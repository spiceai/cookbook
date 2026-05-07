# HTTP Rate Control

This recipe demonstrates how Spice's `runtime.rate_control` feature works with the HTTP data connector.

`runtime.rate_control` persists HTTP governor state — the rate-budget token buckets for each origin — to an object-store location (local file, S3, GCS, Azure Blob, etc.). When multiple Spice instances share the same `state_location`, they coordinate their outbound request rates against a common budget, preventing any single origin from being overwhelmed by a fleet of Spice nodes.

## What You'll Learn

- How to configure `runtime.rate_control` in `spicepod.yaml`
- How the HTTP connector enforces the `rate_limit` parameter against a live server
- How persisted rate state survives Spice restarts
- How two Spice instances share the same rate budget

## Recipe Structure

```
.
├── compose.yaml           # Docker Compose file to start the test server
├── load-test.sh           # oha load-test script for the two-instance scenario
├── spicepod.yaml          # Spice configuration with rate_control and HTTP dataset
└── test-server/
    ├── Dockerfile         # Container image for the test server
    ├── main.py            # Python test server (rate-limits at 10 req / 10 s per path)
    └── pyproject.toml     # uv project metadata (stdlib only, no pip installs needed)
```

## Pre-requisites

- [Spice CLI](https://spiceai.org/docs/installation) installed (`spice` on your `$PATH`)
- [Docker](https://docs.docker.com/get-docker/) with Compose plugin **or** Python ≥ 3.11 and [`uv`](https://docs.astral.sh/uv/getting-started/installation/)

## Step 1 — Start the Test Server

The test server is a zero-dependency Python HTTP server that:

- **`GET /items`** — returns a static list of 5 JSON items
- **`GET /status`** — returns cumulative request and rate-limited counters
- Enforces **10 requests per 10 seconds** per path (sliding window)
- Returns `429 Too Many Requests` with `Retry-After` and `X-RateLimit-*` headers when the limit is exceeded

### Option A — Docker Compose (recommended)

```bash
cd cookbook/http/rate-control
docker compose up -d
```

The server starts in the background and listens on `http://localhost:8080`. View its logs with:

```bash
docker compose logs -f test-server
```

### Option B — run directly with uv

```bash
cd cookbook/http/rate-control
uv run test-server/main.py
```

Expected output:

```
Rate-limit test server listening on http://0.0.0.0:8080
  GET /items   — returns 5 sample items
  GET /status  — returns request counters
  Limit: 10 requests / 10s per path (sliding window)
Press Ctrl+C to stop.
```

> **Custom port**: pass a port number as the first argument, e.g. `uv run test-server/main.py 9090`, and update the `from:` URL in `spicepod.yaml` accordingly.

## Step 2 — Start Spice

In a second terminal (same directory):

```bash
cd cookbook/http/rate-control
spice run
```

Spice reads `spicepod.yaml` and registers the `local_items` dataset backed by `http://localhost:8080`. The `runtime.rate_control` block tells Spice to persist governor state to `./.rate_control_state/` on the local filesystem and refresh it every 5 seconds.

Expected startup output (abridged):

```bash
Spice.ai runtime starting...
...
2024-01-15T12:00:00Z INFO runtime: Rate control state loaded from file://./.rate_control_state (refresh: 5s)
2024-01-15T12:00:00Z INFO runtime: Dataset local_items registered (from: http://localhost:8080, rate_limit: 10/10s)
...
Spice.ai runtime ready
```

## Step 3 — Query the Data

Open the Spice SQL REPL in a third terminal:

```bash
spice sql
```

### Query items

```bash
SELECT * FROM local_items.items;
```

Expected output:

```bash
+----+--------+
| id | name   |
+----+--------+
| 1  | item-1 |
| 2  | item-2 |
| 3  | item-3 |
| 4  | item-4 |
| 5  | item-5 |
+----+--------+

Time: 0.042 seconds. 5 rows.
```

### Query server-side counters

```bash
SELECT * FROM local_items.status;
```

Expected output:

```bash
+----------------+--------------+
| requests_total | rate_limited |
+----------------+--------------+
| 2              | 0            |
+----------------+--------------+

Time: 0.018 seconds. 1 rows.
```

## Step 4 — Trigger Rate Limiting

Run more than 5 queries against `/items` within a second to exhaust the `requests_per_second_limit`, or more than 100 within a minute for `requests_per_minute_limit`. In the SQL REPL, loop rapidly:

```bash
SELECT * FROM local_items.items;
SELECT * FROM local_items.items;
-- ... (repeat quickly)
```

Once the budget is exhausted the test server logs `rate_limited=True` and returns `429`. Spice surfaces this as an error in the query response:

```bash
Error: HTTP 429 Too Many Requests — Retry-After: 5s
```

Check the server's running counters:

```bash
SELECT * FROM local_items.status;
```

```bash
+----------------+--------------+
| requests_total | rate_limited |
+----------------+--------------+
| 14             | 4            |
+----------------+--------------+
```

And in the test server terminal you'll see entries like:

```bash
[2024-01-15T12:00:10+00:00] GET /items  | rate_limited=False | remaining=3
[2024-01-15T12:00:10+00:00] GET /items  | rate_limited=False | remaining=2
[2024-01-15T12:00:11+00:00] GET /items  | rate_limited=True  | remaining=0
[2024-01-15T12:00:11+00:00] GET /items  | rate_limited=True  | remaining=0
```

After 10 seconds the sliding window resets and queries succeed again.

## Step 5 — Verify Persisted State

Stop Spice (`Ctrl+C`) and inspect the persisted state directory:

```bash
ls -lh .rate_control_state/
```

You'll find one or more state files keyed by origin. Restart Spice:

```bash
spice run
```

Spice immediately loads the persisted token-bucket state rather than starting fresh. Requests made before the restart count against the current window, so a burst before shutdown cannot be "reset" by restarting the process.

## Step 6 — Two Instances Sharing a Budget (Advanced)

Because the governor state lives at `file://./.rate_control_state` (or any shared object-store URI), two Spice instances pointed at the same location will coordinate their outbound rate.

### Start two Spice instances on different ports

```bash
# Terminal A — first instance
spiced --http 127.0.0.1:8091 --flight 127.0.0.1:50052

# Terminal B — second instance
spiced --http 127.0.0.1:8092 --flight 127.0.0.1:50062
```

Both instances read and write `.rate_control_state/` with a 5-second refresh interval. Together they share the **same 10 req/s budget** for `http://localhost:8080`. Queries issued to either instance consume from the shared pool.

### Load test with `oha`

Install [`oha`](https://github.com/hatoo/oha) if needed (`cargo install oha` or via your package manager), then run the bundled load-test script:

```bash
# Default: 30s duration, 10 concurrent workers, query both instances
./load-test.sh

# Custom options
./load-test.sh --duration 60s --concurrency 20 --port1 8091 --port2 8092
```

Or run `oha` directly:

```bash
oha -z 30s -c 10 -m POST \
    -H "Content-Type: text/plain" \
    -d "SELECT * FROM local_items WHERE request_path = '/items'" \
    --no-tui http://localhost:8091/v1/sql > /tmp/oha-8091.txt 2>&1 &

oha -z 30s -c 10 -m POST \
    -H "Content-Type: text/plain" \
    -d "SELECT * FROM local_items WHERE request_path = '/items'" \
    --no-tui http://localhost:8092/v1/sql > /tmp/oha-8092.txt 2>&1 &

wait && echo "=== :8091 ===" && grep -E "Success|Total:|Requests/sec|responses" /tmp/oha-8091.txt \
     && echo "=== :8092 ===" && grep -E "Success|Total:|Requests/sec|responses" /tmp/oha-8092.txt
```

#### Interpreting the results

| Scenario | Expected combined req/sec |
|---|---|
| No rate limit (baseline) | ~41 req/sec |
| Shared budget (10 req/10s total) | ~1 req/sec combined (~0.5 each) |
| Independent budgets (10 req/10s each) | ~2 req/sec combined (~1 each) |

When both instances share the same `state_location`, the combined throughput should stay near the single-instance limit, confirming coordinated rate control.

> **Production tip**: Replace `file://` with an S3 or GCS URI to share state across nodes in a Kubernetes cluster:
>
> ```yaml
> runtime:
>   rate_control:
>     state_location: s3://my-bucket/spice/rate-control-state/
>     refresh_interval: 5s
> ```

## Configuration Reference

| `spicepod.yaml` key | Description |
|---|---|
| `runtime.rate_control.state_location` | Object-store URI where governor state is persisted. Supports `file://`, `s3://`, `gs://`, `az://`. |
| `runtime.rate_control.refresh_interval` | How often each instance re-reads the shared state from the backing store (e.g. `5s`, `30s`). |
| `datasets[].params.requests_per_second_limit` | Maximum number of HTTP requests per second to the upstream origin. |
| `datasets[].params.requests_per_minute_limit` | Maximum number of HTTP requests per minute to the upstream origin. |
| `datasets[].params.max_concurrent_requests` | Maximum number of concurrent HTTP requests to the upstream origin. |
| `datasets[].params.rate_control_jitter_min` | Minimum random delay added before each request when rate control is active (e.g. `5ms`). |
| `datasets[].params.rate_control_jitter_max` | Maximum random delay added before each request when rate control is active (e.g. `20ms`). |
| `datasets[].params.allowed_request_paths` | Comma-separated URL path prefixes the HTTP connector may request. |
| `datasets[].params.client_timeout` | HTTP request timeout. |

## Cleaning Up

```bash
# Stop Spice and the test server with Ctrl+C, then remove persisted state
rm -rf .rate_control_state/
```

## Learn More

- [HTTP Data Connector docs](https://spiceai.org/docs/components/data-connectors/http)
- [Runtime rate control docs](https://spiceai.org/docs/runtime/rate-control)
- [Spice.ai Cookbook](https://github.com/spiceai/cookbook)
