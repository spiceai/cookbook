# Dual-Dataset Registration

Works with `v1.0+`

Serve queries instantly while a large table accelerates in the background by registering the same source as two datasets: one federated and one accelerated.

_Tip: Keep the [Data Acceleration documentation](https://docs.spiceai.org/components/data-accelerators) handy while following this guide._

## When to use this pattern

Use dual-dataset registration when **all** of the following apply:

- The table is large (hundreds of millions of rows or more) and the initial acceleration load takes minutes to hours.
- Queries against the federated source during the loading window are **too slow** for your application to tolerate (high latency, timeouts, or expensive per-query costs on the source).
- You need **deterministic control** over when your application switches from the federated path to the accelerated path (for example, a blue-green cutover, or gating behind a feature flag).

### When NOT to use this pattern

| Scenario                                                                                | Better alternative                                                                                                                                                                 |
| --------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The table loads in seconds or a few minutes and brief federation latency is acceptable. | Use a single dataset with `ready_state: on_registration`. Queries fall back to the federated source automatically until acceleration finishes. No application-side routing needed. |
| You never need to query the table before acceleration completes.                        | Use a single accelerated dataset with the default `ready_state: on_load`. The runtime will report the dataset as ready only after loading is done.                                 |
| You want fast restarts but already have a prior acceleration file.                      | Use [acceleration snapshots](../snapshots/README.md) to bootstrap from a pre-built file. The dataset is ready in seconds.                                                          |

### Trade-offs

- **Two table names.** Your application must be aware of both `<table>` and `<table>_accelerated` and include logic to switch between them when the accelerated copy is ready.
- **Double registration overhead.** The runtime registers two datasets against the same source. This is lightweight (metadata only for the federated entry), but it adds entries to the dataset catalog.
- **Source queried twice during load.** Until the acceleration finishes, the federated dataset still routes to the source. If the source charges per query or per byte scanned, plan accordingly.

## Prerequisites

- [Spice CLI](https://docs.spiceai.org/getting-started) installed.

## Step 1. Create a Spice workspace

```bash
spice init dual-dataset-registration
cd dual-dataset-registration
```

## Step 2. Configure the dual datasets

Replace the generated `spicepod.yaml` with the following configuration. It registers the public NYC taxi-trips Parquet dataset twice — once as a plain federated table and once with DuckDB file-mode acceleration.

```yaml
version: v1
kind: Spicepod
name: dual-dataset-registration

datasets:
  # Federated table — available immediately at startup
  - from: s3://spiceai-demo-datasets/taxi_trips/2024/
    name: taxi_trips
    params:
      file_format: parquet

  # Accelerated copy — loads in the background
  - from: s3://spiceai-demo-datasets/taxi_trips/2024/
    name: taxi_trips_accelerated
    params:
      file_format: parquet
    ready_state: on_registration # Required for runtime to be ready while loading
    acceleration:
      enabled: true
      engine: duckdb
      mode: file
      refresh_check_interval: 30m
```

Key points:

- `taxi_trips` is a federated dataset with no acceleration. It is ready the moment the runtime starts.
- `taxi_trips_accelerated` points to the same source but has `acceleration.enabled: true`. The runtime begins loading data into a local DuckDB file as soon as it starts.
- `ready_state: on_registration` is required on the accelerated dataset so the runtime becomes ready immediately. Without it the runtime waits for the acceleration to finish loading before marking itself ready, which blocks the federated dataset from serving queries.
- `mode: file` writes the accelerated data to disk instead of memory, avoiding out-of-memory crashes for large tables.
- `refresh_check_interval: 30m` re-checks the source every 30 minutes after the initial load.

## Step 3. Start the Spice runtime

```bash
spice run
```

Shortly after startup you will see both datasets register. The federated table is ready immediately, while the accelerated copy begins loading:

```bash
2025-03-24T10:00:01.123456Z  INFO runtime::init::dataset: Dataset taxi_trips registered (s3://spiceai-demo-datasets/taxi_trips/2024/), results cache enabled.
2025-03-24T10:00:01.234567Z  INFO runtime::init::dataset: Dataset taxi_trips_accelerated registered (s3://spiceai-demo-datasets/taxi_trips/2024/), acceleration (duckdb:file), results cache enabled.
2025-03-24T10:00:01.234890Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset taxi_trips_accelerated
```

## Step 4. Query the federated table immediately

In a new terminal, open the Spice SQL REPL:

```bash
spice sql
```

Run a query against the federated table. It hits the S3 source directly, so it works right away — even while the acceleration is still loading:

```sql
SELECT COUNT(*) AS total_trips FROM taxi_trips;
```

```output
+-------------+
| total_trips |
+-------------+
| 2964624     |
+-------------+
```

Queries against the federated table work but have higher latency since every query reads from the remote source.

## Step 5. Check acceleration readiness

Use the datasets status API to determine when the accelerated copy is ready:

```bash
curl "http://localhost:8090/v1/datasets?status=true" | jq
```

While still loading:

```json
[
  {
    "from": "s3://spiceai-demo-datasets/taxi_trips/2024/",
    "name": "taxi_trips",
    "status": "Ready"
  },
  {
    "from": "s3://spiceai-demo-datasets/taxi_trips/2024/",
    "name": "taxi_trips_accelerated",
    "status": "Refreshing"
  }
]
```

When the acceleration finishes:

```json
[
  {
    "from": "s3://spiceai-demo-datasets/taxi_trips/2024/",
    "name": "taxi_trips",
    "status": "Ready"
  },
  {
    "from": "s3://spiceai-demo-datasets/taxi_trips/2024/",
    "name": "taxi_trips_accelerated",
    "status": "Ready"
  }
]
```

The Spice runtime logs also confirm when the load completes:

```bash
2025-03-24T10:03:45.678901Z  INFO runtime::accelerated_table::refresh_task: Loaded 2,964,624 rows () for dataset taxi_trips_accelerated in 3m 44s.
```

## Step 6. Switch to the accelerated table

Once `taxi_trips_accelerated` reports `Ready`, run the same query against the accelerated copy:

```sql
SELECT COUNT(*) AS total_trips FROM taxi_trips_accelerated;
```

```output
+-------------+
| total_trips |
+-------------+
| 2964624     |
+-------------+
```

The result is the same, but the query runs against local DuckDB storage and is significantly faster — especially for analytical queries scanning many rows.

## Step 7. Implement application-side routing (optional)

In your application, poll the status endpoint and route queries accordingly. A minimal example:

```bash
#!/bin/bash
# Poll until the accelerated table is ready, then switch.
TABLE="taxi_trips"
while true; do
  STATUS=$(curl -s "http://localhost:8090/v1/datasets?status=true" \
    | jq -r '.[] | select(.name == "taxi_trips_accelerated") | .status')
  if [ "$STATUS" = "Ready" ]; then
    TABLE="taxi_trips_accelerated"
    echo "Switched to accelerated table."
    break
  fi
  sleep 5
done

# Use $TABLE for subsequent queries.
```

In production, implement this check in your application's startup or health-check loop rather than a shell script.

## Summary

You registered the same S3 source as two datasets — a federated table for immediate queries and an accelerated table for fast local reads once loaded. This dual-dataset pattern keeps your application responsive during cold starts while still delivering the full performance benefits of local acceleration for large tables.

For tables that load quickly or where brief federation latency is acceptable, prefer the simpler `ready_state: on_registration` approach on a single dataset instead.
