# Caching Accelerator

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

| Key | Action |
|-----|--------|
| `s` | Toggle error mode (returns 500 Internal Server Error) |
| `+` | Increase response delay by 100ms |
| `-` | Decrease response delay by 100ms |
| `q` | Quit the server |

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
SELECT request_path, content, fetched_at FROM time WHERE request_path = '/time';
```

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
```

### Key Configuration Options

| Parameter | Value | Description |
|-----------|-------|-------------|
| `refresh_mode` | `caching` | Enables the caching accelerator with SWR support |
| `engine` | `duckdb` | Uses DuckDB for cache storage |
| `caching_ttl` | `10s` | Cache entries are considered fresh for 10 seconds |
| `caching_stale_while_revalidate_ttl` | `10s` | Serve stale data for 10 seconds while refreshing in background |
| `caching_stale_if_error` | `enabled` | Return cached data if the upstream server returns an error |

## Experimenting with Caching Behavior

### Observing SWR in Action

1. **First Query (Cache Miss)**: Run the query - it will take ~1 second (the server's default delay)

   ```sql
   SELECT request_path, content, fetched_at FROM time WHERE request_path = '/time';
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
SELECT request_path, content, fetched_at FROM time WHERE request_path = '/time/1';
SELECT request_path, content, fetched_at FROM time WHERE request_path = '/time/2';
SELECT request_path, content, fetched_at FROM time WHERE request_path = '/time/3';

-- View all cached entries
SELECT request_path, content, fetched_at FROM time ORDER BY fetched_at DESC;
```

### Testing Response Delays

The `+` and `-` keys on the time server adjust response delay:

1. Increase delay to 2000ms with `+` (press multiple times)
2. Clear the cache by restarting Spice
3. Query and observe the longer initial fetch time
4. Subsequent queries still return instantly from cache

## Cache Schema

The caching accelerator automatically adds metadata fields to cached data:

| Field | Type | Description |
|-------|------|-------------|
| `request_path` | String | The URL path used for the request |
| `request_query` | String | Query parameters from the request |
| `request_body` | String | Request body (for POST requests) |
| `content` | String | The response content |
| `fetched_at` | Timestamp | When the data was fetched |

## Use Cases

The caching accelerator is ideal for:

- **API Response Caching**: Reduce latency and costs when fetching from external APIs
- **Rate Limit Management**: Cache responses to stay within API rate limits
- **Offline Resilience**: Serve cached data when upstream services are unavailable
- **Search Result Caching**: Cache search API responses where queries may return different results over time

## Learn More

- [Caching Accelerator Documentation](https://docs.spiceai.org/features/data-accelerators/refresh-modes/caching)
- [HTTPS Connector Documentation](https://docs.spiceai.org/components/data-connectors/https)
