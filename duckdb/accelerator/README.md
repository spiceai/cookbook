# DuckDB Data Accelerator Recipe

This recipe will walkthrough how to accelerate a local copy of the taxi trips dataset stored in S3 using DuckDB as the data accelerator engine.

## Requirements

- Spice CLI installed (see [Getting Started](https://docs.spiceai.org/getting-started)).

## Follow these steps

**Step 1.** Initialize a new Spice app.

```bash
spice init duckdb-acceleration-qs
cd duckdb-acceleration-qs
```

**Step 2.** Configure s3 dataset: copy and paste the YAML below to `spicepod.yaml` in the Spice app.

```yaml
version: v1beta1
kind: Spicepod
name: duckdb-acceleration-qs
datasets:
- from: s3://spiceai-demo-datasets/taxi_trips/2024/
  name: taxi_trips
  description: taxi trips in s3
  params:
    file_format: parquet
```

**Step 3.** Start the Spice runtime.

```bash
spice run
```

Confirm in the terminal output the `taxi_trips` dataset has been loaded:

```bash
Spice.ai runtime starting...
2024-09-16T21:25:43.305988Z  INFO runtime::metrics_server: Spice Runtime Metrics listening on 127.0.0.1:9090
2024-09-16T21:25:43.306009Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2024-09-16T21:25:43.309474Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2024-09-16T21:25:43.311587Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2024-09-16T21:25:43.507974Z  INFO runtime: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
2024-09-16T21:25:44.101055Z  INFO runtime: Dataset taxi_trips registered (s3://spiceai-demo-datasets/taxi_trips/2024/), results cache enabled.
```

**Step 4.** Run queries against the dataset using the Spice SQL REPL.

_In a new terminal_, start the Spice SQL REPL

```bash
spice sql
```

Query the `taxi_trips` dataset, observing the long query time.

```sql
select "VendorID", tpep_pickup_datetime, tpep_dropoff_datetime, passenger_count from taxi_trips limit 10;
+----------+----------------------+-----------------------+-----------------+
| VendorID | tpep_pickup_datetime | tpep_dropoff_datetime | passenger_count |
+----------+----------------------+-----------------------+-----------------+
| 2        | 2024-01-13T03:18:09  | 2024-01-13T03:24:37   | 1               |
| 2        | 2024-01-13T03:52:58  | 2024-01-13T04:01:18   | 1               |
| 2        | 2024-01-13T03:26:02  | 2024-01-13T03:34:43   | 1               |
| 2        | 2024-01-13T03:53:44  | 2024-01-13T04:10:56   | 1               |
| 2        | 2024-01-13T02:58:28  | 2024-01-13T03:14:33   | 1               |
| 2        | 2024-01-13T03:54:24  | 2024-01-13T04:03:58   | 1               |
| 2        | 2024-01-13T03:06:55  | 2024-01-13T03:50:08   | 3               |
| 2        | 2024-01-13T03:22:26  | 2024-01-13T03:30:50   | 2               |
| 2        | 2024-01-13T03:21:19  | 2024-01-13T03:46:54   | 1               |
| 1        | 2024-01-13T03:13:35  | 2024-01-13T03:40:25   | 1               |
+----------+----------------------+-----------------------+-----------------+

Time: 4.684086261 seconds. 10 rows.
```

**Step 5.** Update the `spicepod.yaml` to enable DuckDB acceleration.

```yaml
version: v1beta1
kind: Spicepod
name: duckdb-acceleration-qs
datasets:
- from: s3://spiceai-demo-datasets/taxi_trips/2024/
  name: taxi_trips
  description: taxi trips in s3
  params:
    file_format: parquet
  acceleration:
    enabled: true
    engine: duckdb
    mode: file
```

**Step 6.** Restart the Spice app and observe the dataset loading and accelerating.

```bash
2024-09-12T23:08:53.964728Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2024-09-12T23:08:53.964845Z  INFO runtime::metrics_server: Spice Runtime Metrics listening on 127.0.0.1:9090
2024-09-12T23:08:53.965420Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2024-09-12T23:08:53.965471Z  INFO runtime: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
2024-09-12T23:08:53.966168Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2024-09-12T23:08:55.308963Z  INFO runtime: Dataset taxi_trips registered (s3://spiceai-demo-datasets/taxi_trips/2024/), acceleration (duckdb:file), results cache enabled.
2024-09-12T23:08:55.310382Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset taxi_trips
2024-09-12T23:09:11.477553Z  INFO runtime::accelerated_table::refresh_task: Loaded 2,964,624 rows (421.71 MiB) for dataset taxi_trips in 16s 167ms.
```

**Step 7.** Run a query against the `taxi_trips` dataset again, observing the fast query time.

```sql
select "VendorID", tpep_pickup_datetime, tpep_dropoff_datetime, passenger_count from taxi_trips limit 10;
+----------+----------------------+-----------------------+-----------------+
| VendorID | tpep_pickup_datetime | tpep_dropoff_datetime | passenger_count |
+----------+----------------------+-----------------------+-----------------+
| 2        | 2024-01-13T03:18:09  | 2024-01-13T03:24:37   | 1               |
| 2        | 2024-01-13T03:52:58  | 2024-01-13T04:01:18   | 1               |
| 2        | 2024-01-13T03:26:02  | 2024-01-13T03:34:43   | 1               |
| 2        | 2024-01-13T03:53:44  | 2024-01-13T04:10:56   | 1               |
| 2        | 2024-01-13T02:58:28  | 2024-01-13T03:14:33   | 1               |
| 2        | 2024-01-13T03:54:24  | 2024-01-13T04:03:58   | 1               |
| 2        | 2024-01-13T03:06:55  | 2024-01-13T03:50:08   | 3               |
| 2        | 2024-01-13T03:22:26  | 2024-01-13T03:30:50   | 2               |
| 2        | 2024-01-13T03:21:19  | 2024-01-13T03:46:54   | 1               |
| 1        | 2024-01-13T03:13:35  | 2024-01-13T03:40:25   | 1               |
+----------+----------------------+-----------------------+-----------------+

Time: 0.015658908 seconds. 10 rows.
```

## Learn more

- [DuckDB Data Accelerator Documentation](https://docs.spiceai.org/components/data-accelerators/duckdb).

- For using `spice sql`, see the [CLI reference](https://docs.spiceai.org/cli/reference/sql).

- See the [datasets reference](https://docs.spiceai.org/reference/spicepod/datasets) for additional dataset configuration options.
