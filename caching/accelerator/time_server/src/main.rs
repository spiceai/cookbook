use std::{
    collections::VecDeque,
    io::{Write, stdout},
    net::SocketAddr,
    sync::{
        Arc, Mutex,
        atomic::{AtomicBool, AtomicU64, Ordering},
    },
    time::Duration,
};

use anyhow::Result;
use axum::{
    Router,
    extract::{OriginalUri, State},
    http::{HeaderValue, StatusCode, header::DATE},
    response::IntoResponse,
    routing::get,
};
use chrono::{SecondsFormat, Utc};
use crossterm::{
    cursor::{MoveTo, Show},
    event::{self, Event, KeyCode, KeyEventKind, KeyModifiers},
    execute,
    style::Print,
    terminal::{Clear, ClearType, disable_raw_mode, enable_raw_mode},
};
use tokio::{signal, sync::broadcast, task, time::sleep};

#[derive(Clone)]
struct AppState {
    error_mode: Arc<AtomicBool>,
    request_log: Arc<Mutex<VecDeque<RequestEntry>>>,
    delay_ms: Arc<AtomicU64>,
    last_request_ts: Arc<AtomicU64>,
}

#[tokio::main]
async fn main() -> Result<()> {
    let error_mode = Arc::new(AtomicBool::new(false));
    let request_log = Arc::new(Mutex::new(VecDeque::with_capacity(10)));
    let delay_ms = Arc::new(AtomicU64::new(1000));
    let last_request_ts = Arc::new(AtomicU64::new(Utc::now().timestamp() as u64));
    let (shutdown_tx, mut shutdown_rx_server) = broadcast::channel::<()>(1);

    let app_state = AppState {
        error_mode: Arc::clone(&error_mode),
        request_log: Arc::clone(&request_log),
        delay_ms: Arc::clone(&delay_ms),
        last_request_ts: Arc::clone(&last_request_ts),
    };

    let app = Router::new()
        .route("/time", get(time_handler))
        .route("/time/*rest", get(time_handler))
        .with_state(app_state);

    let addr = SocketAddr::from(([0, 0, 0, 0], 7400));
    println!("Time server listening on http://{addr}");
    println!("Press 'q' or Ctrl+C to quit, 's' for 500 mode, '+'/'-' to adjust delay.");

    let listener = tokio::net::TcpListener::bind(addr).await?;
    let server = axum::serve(listener, app).with_graceful_shutdown(async move {
        let _ = shutdown_rx_server.recv().await;
    });

    let mut ui_handle = task::spawn_blocking({
        let error_mode = Arc::clone(&error_mode);
        let request_log = Arc::clone(&request_log);
        let delay_ms = Arc::clone(&delay_ms);
        let last_request_ts = Arc::clone(&last_request_ts);
        let shutdown_tx = shutdown_tx.clone();
        move || {
            let shutdown_rx = shutdown_tx.subscribe();
            run_ui(
                error_mode,
                request_log,
                delay_ms,
                last_request_ts,
                shutdown_tx,
                shutdown_rx,
            )
        }
    });

    let mut server_handle = tokio::spawn(async move { server.await });

    tokio::select! {
        _ = signal::ctrl_c() => {
            let _ = shutdown_tx.send(());
        }
        res = &mut ui_handle => {
            res??;
            let _ = shutdown_tx.send(());
        }
        res = &mut server_handle => {
            res??;
        }
    }

    let _ = shutdown_tx.send(());

    if !server_handle.is_finished() {
        server_handle.await??;
    }
    if !ui_handle.is_finished() {
        ui_handle.await??;
    }

    Ok(())
}

async fn time_handler(
    State(state): State<AppState>,
    OriginalUri(uri): OriginalUri,
) -> impl IntoResponse {
    let now = Utc::now();
    let timestamp = now.to_rfc3339_opts(SecondsFormat::Secs, true);
    let date_header =
        HeaderValue::from_str(&timestamp).expect("timestamp should be valid header value");
    state
        .last_request_ts
        .store(now.timestamp() as u64, Ordering::Relaxed);
    let delay = state.delay_ms.load(Ordering::Relaxed);
    let path = uri.path().to_string();

    if state.error_mode.load(Ordering::Relaxed) {
        if delay > 0 {
            sleep(Duration::from_millis(delay)).await;
        }
        record_request(
            &state.request_log,
            RequestEntry::new(
                timestamp.clone(),
                path.clone(),
                StatusCode::INTERNAL_SERVER_ERROR,
            ),
        );
        return (
            StatusCode::INTERNAL_SERVER_ERROR,
            [(DATE, date_header)],
            "Internal Server Error".to_string(),
        );
    }

    if delay > 0 {
        sleep(Duration::from_millis(delay)).await;
    }

    record_request(
        &state.request_log,
        RequestEntry::new(timestamp.clone(), path, StatusCode::OK),
    );
    (StatusCode::OK, [(DATE, date_header)], timestamp)
}

fn run_ui(
    error_mode: Arc<AtomicBool>,
    request_log: Arc<Mutex<VecDeque<RequestEntry>>>,
    delay_ms: Arc<AtomicU64>,
    last_request_ts: Arc<AtomicU64>,
    shutdown_tx: broadcast::Sender<()>,
    mut shutdown_rx: broadcast::Receiver<()>,
) -> Result<()> {
    let _raw_mode_guard = RawModeGuard::new()?;
    let mut stdout = stdout();

    render_status(
        &mut stdout,
        error_mode.load(Ordering::Relaxed),
        &request_log,
        Utc::now().to_rfc3339_opts(SecondsFormat::Secs, true),
        delay_ms.load(Ordering::Relaxed),
        seconds_since_last_request(&last_request_ts),
    )?;

    loop {
        match shutdown_rx.try_recv() {
            Ok(_) | Err(broadcast::error::TryRecvError::Closed) => break,
            Err(broadcast::error::TryRecvError::Empty) => {}
            Err(broadcast::error::TryRecvError::Lagged(_)) => {}
        }

        if event::poll(Duration::from_millis(200))? {
            if let Event::Key(key_event) = event::read()? {
                match key_event.code {
                    KeyCode::Char('q') if key_event.kind == KeyEventKind::Press => {
                        let _ = shutdown_tx.send(());
                        break;
                    }
                    KeyCode::Char('c')
                        if key_event.kind == KeyEventKind::Press
                            && key_event.modifiers.contains(KeyModifiers::CONTROL) =>
                    {
                        let _ = shutdown_tx.send(());
                        break;
                    }
                    KeyCode::Char('s') if key_event.kind == KeyEventKind::Press => {
                        error_mode.fetch_xor(true, Ordering::SeqCst);
                        render_status(
                            &mut stdout,
                            error_mode.load(Ordering::Relaxed),
                            &request_log,
                            Utc::now().to_rfc3339_opts(SecondsFormat::Secs, true),
                            delay_ms.load(Ordering::Relaxed),
                            seconds_since_last_request(&last_request_ts),
                        )?;
                    }
                    KeyCode::Char('+') if key_event.kind == KeyEventKind::Press => {
                        let new = delay_ms.fetch_add(100, Ordering::SeqCst) + 100;
                        render_status(
                            &mut stdout,
                            error_mode.load(Ordering::Relaxed),
                            &request_log,
                            Utc::now().to_rfc3339_opts(SecondsFormat::Secs, true),
                            new,
                            seconds_since_last_request(&last_request_ts),
                        )?;
                    }
                    KeyCode::Char('-') if key_event.kind == KeyEventKind::Press => {
                        delay_ms
                            .fetch_update(Ordering::SeqCst, Ordering::SeqCst, |d| {
                                Some(d.saturating_sub(100))
                            })
                            .ok();
                        let new = delay_ms.load(Ordering::SeqCst);
                        render_status(
                            &mut stdout,
                            error_mode.load(Ordering::Relaxed),
                            &request_log,
                            Utc::now().to_rfc3339_opts(SecondsFormat::Secs, true),
                            new,
                            seconds_since_last_request(&last_request_ts),
                        )?;
                    }
                    _ => {}
                }
            }
        }

        render_status(
            &mut stdout,
            error_mode.load(Ordering::Relaxed),
            &request_log,
            Utc::now().to_rfc3339_opts(SecondsFormat::Secs, true),
            delay_ms.load(Ordering::Relaxed),
            seconds_since_last_request(&last_request_ts),
        )?;
    }

    render_exit_message(&mut stdout)?;
    Ok(())
}

fn render_status(
    stdout: &mut std::io::Stdout,
    error_mode: bool,
    request_log: &Arc<Mutex<VecDeque<RequestEntry>>>,
    current_time: String,
    delay_ms: u64,
    since_last_request_secs: u64,
) -> Result<()> {
    let status_text = if error_mode {
        "Responding with 500 Internal Server Error"
    } else {
        "Responding with current UTC time"
    };

    let log_snapshot = {
        let log = request_log.lock().unwrap();
        log.iter()
            .rev()
            .map(|entry| format!("{} {} -> {}", entry.timestamp, entry.path, entry.status))
            .collect::<Vec<_>>()
    };

    let mut display = String::new();
    display.push_str("Time Server Controls\r\n");
    display.push_str("q: quit server\r\n");
    display.push_str("s: toggle 500 mode\r\n");
    display.push_str("+: increase delay by 100ms\r\n");
    display.push_str("-: decrease delay by 100ms\r\n");
    display.push_str("ctrl+c: quit server\r\n");
    display.push_str("\r\n");
    display.push_str("Status:\r\n");
    display.push_str(status_text);
    display.push_str("\r\n");
    display.push_str(&format!("Current delay: {} ms\r\n", delay_ms));
    display.push_str("Listening on: http://0.0.0.0:7400/time\r\n");
    display.push_str("\r\n");
    display.push_str("Current time:\r\n");
    display.push_str("  ");
    display.push_str(&current_time);
    display.push_str("\r\n");
    display.push_str("Seconds since last request:\r\n");
    display.push_str("  ");
    display.push_str(&since_last_request_secs.to_string());
    display.push_str(" seconds\r\n");
    display.push_str("\r\n\r\n");
    display.push_str("Recent requests (newest first):\r\n");

    if log_snapshot.is_empty() {
        display.push_str("  (none yet)\r\n");
    } else {
        for line in log_snapshot {
            display.push_str("  ");
            display.push_str(&line);
            display.push_str("\r\n");
        }
    }

    execute!(stdout, Clear(ClearType::All), MoveTo(0, 0), Print(display),)?;
    stdout.flush()?;
    Ok(())
}

fn render_exit_message(stdout: &mut std::io::Stdout) -> Result<()> {
    execute!(
        stdout,
        Clear(ClearType::All),
        MoveTo(0, 0),
        Print("Shutting down server...\r\n"),
        Show,
    )?;
    stdout.flush()?;
    Ok(())
}

fn seconds_since_last_request(last_request_ts: &Arc<AtomicU64>) -> u64 {
    let now = Utc::now().timestamp() as u64;
    let last = last_request_ts.load(Ordering::Relaxed);
    now.saturating_sub(last)
}

fn record_request(log: &Arc<Mutex<VecDeque<RequestEntry>>>, entry: RequestEntry) {
    let mut log = log.lock().unwrap();
    if log.len() == 10 {
        log.pop_front();
    }
    log.push_back(entry);
}

#[derive(Clone)]
struct RequestEntry {
    timestamp: String,
    path: String,
    status: u16,
}

impl RequestEntry {
    fn new(timestamp: String, path: String, status: StatusCode) -> Self {
        Self {
            timestamp,
            path,
            status: status.as_u16(),
        }
    }
}

struct RawModeGuard;

impl RawModeGuard {
    fn new() -> Result<Self> {
        enable_raw_mode()?;
        execute!(stdout(), crossterm::cursor::Hide)?;
        Ok(Self)
    }
}

impl Drop for RawModeGuard {
    fn drop(&mut self) {
        let _ = disable_raw_mode();
        let _ = execute!(stdout(), Show);
    }
}
