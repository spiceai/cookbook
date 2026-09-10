# Caching Accelerator

Works with `v1.10+`

This recipe demonstrates the **caching accelerator** (`refresh_mode: caching`), which provides intelligent caching for HTTP-based datasets with Stale-While-Revalidate (SWR) support.

## Overview

The caching accelerator is designed for scenarios that require:

- Caching HTTP API responses to reduce latency and API costs
- Serving stale data immediately while refreshing in the background (SWR pattern)
- Persisting cached data to disk for fast cold starts

This recipe includes a small Rust-based time server that helps illustrate and experiment with caching behavior.

## Prerequisites

- [Spice CLI](https://docs.spiceai.org/getting-started) installed
- Docker (for running the time server)

## Time Server

The included time server (`time_server/`) serves the current UTC time on `http://localhost:7400/time` and provides interactive controls to simulate various caching scenarios. A pre-built Docker image is available at `ghcr.io/spiceai/cookbook-time-server:latest`.

| Key | Action                                                |
| --- | ----------------------------------------------------- |
| `s` | Toggle error mode (returns 500 Internal Server Error) |
| `+` | Increase response delay by 100ms                      |
| `-` | Decrease response delay by 100ms                      |
| `q` | Quit the server                                       |

The server also displays:

- Current response status (OK or 500 error)
- Current response delay (default: 1000ms)
- Recent requests with timestamps and status codes
- Seconds since the last request

The server supports any path under `/time`, enabling testing of multiple cache keys:

- `/time` - Base time endpoint
- `/time/1`, `/time/2`, etc. - Additional endpoints for testing multiple cache entries

## Getting Started

### Step 1: Start the Time Server

Run the time server using Docker:

```bash
docker run -it --rm -p 7400:7400 ghcr.io/spiceai/cookbook-time-server:latest
```

The server will start and display an interactive control panel.

### Step 2: Start Spice Runtime

In a separate terminal, start the Spice runtime:

```bash
cd caching/accelerator
spice run
```

### Step 3: Query the Cached Data

Open another terminal and use the Spice SQL REPL:

```bash
spice sql
```

Run a query to fetch the current time through the cache:

```sql
SELECT request_path, content, _fetched_at FROM time WHERE request_path = '/time';
```

> **Version note:** The fetch-timestamp column is named `_fetched_at` (leading underscore) on Spice `v2.0+`. On `v1.x` it is `fetched_at` (no underscore) — use that name if you are running a `v1.x` release.

## Understanding the Configuration

The `spicepod.yaml` configures the caching accelerator:

```yaml
datasets:
  - from: http://localhost:7400
    name: time
    params:
      request_query_filters: enabled
      request_body_filters: enabled
      allowed_request_paths: /**/**
    acceleration:
      enabled: true
      engine: duckdb
      refresh_mode: caching
      params:
        caching_ttl: 10s
        caching_stale_while_revalidate_ttl: 10s
        caching_stale_if_error: enabled
        caching_max_size: 256MiB
        caching_max_items: 10000
```

### Key Configuration Options

| Parameter                            | Value     | Description                                                    |
| ------------------------------------ | --------- | -------------------------------------------------------------- |
| `refresh_mode`                       | `caching` | Enables the caching accelerator with SWR support               |
| `engine`                             | `duckdb`  | Uses DuckDB for cache storage                                  |
| `caching_ttl`                        | `10s`     | Cache entries are considered fresh for 10 seconds              |
| `caching_stale_while_revalidate_ttl` | `10s`     | Serve stale data for 10 seconds while refreshing in background |
| `caching_stale_if_error`             | `enabled` | Return cached data if the upstream server returns an error     |
| `caching_max_size`                   | `256MiB`  | Byte budget for the stored cache (`v2.3.0+`)                   |
| `caching_max_items`                  | `10000`   | Row budget for the stored cache (`v2.3.0+`)                    |

### What Bounds the Cache

`caching_ttl` and `caching_stale_while_revalidate_ttl` bound how long an entry is
*served*, not how long it is *stored*. With `caching_stale_if_error: enabled` an
expired entry is deliberately kept, because it is the copy served when the origin
fails — so those two TTLs evict nothing, and the accelerator grows with every
distinct request it serves.

`caching_max_size` and `caching_max_items` (`v2.3.0+`) are what bound it. Eviction is
entry-granular: a cached response can span several rows, so the runtime ranks entries
by their oldest page and removes all of an entry's rows together. Without a budget,
`v2.3.0+` warns at startup:

```console
WARN runtime_table::accelerated::caching_eviction: Dataset 'time' sets `caching_stale_if_error: enabled` with no `caching_max_size` or `caching_max_items`, so no cached entry is ever evicted and the acceleration will grow without bound - expired entries are deliberately kept as fallback for a failing origin. Set a budget to bound it.
```

A time-based bound is a separate mechanism, and the runtime warns separately when
none is running. To add one, either set `caching_stale_if_error: disabled` — which
evicts at `caching_ttl` + `caching_stale_while_revalidate_ttl`, giving up the
stale-if-error fallback this recipe demonstrates — or declare a retention policy with
all four of `retention_check_enabled: true`, `retention_period`,
`retention_check_interval`, and the dataset's `time_column`. A policy missing any one
of those starts nothing.

> **Note:** This recipe's DuckDB accelerator is in-memory (no `mode: file`), so the
> cache starts empty on every `spice run`. Add `mode: file` under `acceleration` to
> persist it across restarts.

## Experimenting with Caching Behavior

### Observing SWR in Action

1. **First Query (Cache Miss)**: Run the query - it will take ~1 second (the server's default delay)

   ```sql
   SELECT request_path, content, _fetched_at FROM time WHERE request_path = '/time';
   ```

2. **Immediate Repeat (Cache Hit)**: Run the same query again - it returns instantly from cache

3. **Wait for Staleness**: Wait 10+ seconds (past `caching_ttl`), then query again:
   - The stale cached data returns immediately
   - A background refresh is triggered
   - The time server shows the new request

4. **Observe Refresh**: Query again after the background refresh completes to see updated data

### Testing Error Handling

1. Press `s` on the time server to enable error mode (500 responses)
2. Query the cache - with `caching_stale_if_error: enabled`, cached data is still returned even though the server is returning errors
3. Press `s` again to disable error mode

### Testing Multiple Cache Keys

Query different paths to create separate cache entries:

```sql
-- These create separate cache entries
SELECT request_path, content, _fetched_at FROM time WHERE request_path = '/time/1';
SELECT request_path, content, _fetched_at FROM time WHERE request_path = '/time/2';
SELECT request_path, content, _fetched_at FROM time WHERE request_path = '/time/3';

-- View all cached entries
SELECT request_path, content, _fetched_at FROM time ORDER BY _fetched_at DESC;
```

### Testing Response Delays

The `+` and `-` keys on the time server adjust response delay:

1. Increase delay to 2000ms with `+` (press multiple times)
2. Clear the cache by restarting Spice
3. Query and observe the longer initial fetch time
4. Subsequent queries still return instantly from cache

## Cache Schema

The cached table carries the request and response metadata alongside the content — `describe time` lists all eight columns:

| Field              | Type            | Description                                                    |
| ------------------ | --------------- | -------------------------------------------------------------- |
| `request_path`     | `Utf8`          | The URL path used for the request                              |
| `request_query`    | `Utf8`          | Query parameters from the request                              |
| `request_body`     | `Utf8`          | Request body (for POST requests)                               |
| `request_headers`  | `Utf8`          | Headers sent with the request                                  |
| `content`          | `Utf8`          | The response content                                           |
| `response_status`  | `UInt16`        | HTTP status code returned by the upstream server               |
| `response_headers` | `Map`           | Response headers, as a map of string keys to string values     |
| `_fetched_at`      | `Timestamp(ns)` | When the data was fetched (named `fetched_at` on Spice `v1.x`) |

## Use Cases

The caching accelerator is ideal for:

- **API Response Caching**: Reduce latency and costs when fetching from external APIs
- **Rate Limit Management**: Cache responses to stay within API rate limits
- **Offline Resilience**: Serve cached data when upstream services are unavailable
- **Search Result Caching**: Cache search API responses where queries may return different results over time

## Learn More

- [Caching Accelerator Documentation](https://docs.spiceai.org/features/data-acceleration/refresh-modes/caching)
- [HTTPS Connector Documentation](https://docs.spiceai.org/components/data-connectors/https)
