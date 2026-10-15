# DuckDB Data Accelerator

Works with `v2.0+`

This recipe will walkthrough how to accelerate a local copy of the taxi trips dataset stored in S3 using DuckDB as the data accelerator engine.

[![Watch the Spice.ai local Llama demo](https://img.youtube.com/vi/e1PtA3Hr8x8/hqdefault.jpg)](https://www.youtube.com/embed/e1PtA3Hr8x8)

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
version: v2
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
2024-09-16T21:25:43.306009Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2024-09-16T21:25:43.309474Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2024-09-16T21:25:43.507974Z  INFO runtime::init::caching: Initialized sql results cache; max size: 128.00 MiB, item ttl: 1s, hashing algorithm: XXH3, encoding: none
2024-09-16T21:25:44.101055Z  INFO runtime::init::dataset: Dataset taxi_trips registered (s3://spiceai-demo-datasets/taxi_trips/2024/), results cache enabled.
```

**Step 4.** Run queries against the dataset using the Spice SQL REPL.

_In a new terminal_, start the Spice SQL REPL

```bash
spice sql
```

Query the `taxi_trips` dataset, observing the long query time.

```sql
select "VendorID", tpep_pickup_datetime, tpep_dropoff_datetime, passenger_count from taxi_trips order by tpep_pickup_datetime, tpep_dropoff_datetime, "VendorID", passenger_count limit 10;
```

```
+----------+----------------------+-----------------------+-----------------+
| VendorID | tpep_pickup_datetime | tpep_dropoff_datetime | passenger_count |
|   int32  |     timestamp[us]    |     timestamp[us]     |      int64      |
+----------+----------------------+-----------------------+-----------------+
| 2        | 2002-12-31T22:59:39  | 2002-12-31T23:05:41   | 1               |
| 2        | 2002-12-31T22:59:39  | 2002-12-31T23:05:41   | 1               |
| 2        | 2009-01-01T00:24:09  | 2009-01-01T01:13:00   | 2               |
| 2        | 2009-01-01T23:30:39  | 2009-01-02T00:01:39   | 1               |
| 2        | 2009-01-01T23:58:40  | 2009-01-02T00:01:40   | 1               |
| 2        | 2023-12-31T23:39:17  | 2023-12-31T23:42:00   | 2               |
| 2        | 2023-12-31T23:41:02  | 2023-12-31T23:48:03   | 1               |
| 2        | 2023-12-31T23:47:28  | 2023-12-31T23:57:07   | 2               |
| 2        | 2023-12-31T23:49:12  | 2024-01-01T00:04:32   | 1               |
| 2        | 2023-12-31T23:54:27  | 2024-01-01T00:13:12   | 1               |
+----------+----------------------+-----------------------+-----------------+

Time: 5.518708875 seconds. 10 rows.
```

**Step 5.** Update the `spicepod.yaml` to enable DuckDB acceleration.

```yaml
version: v2
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
2024-09-12T23:08:53.965420Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2024-09-12T23:08:53.965471Z  INFO runtime::init::caching: Initialized sql results cache; max size: 128.00 MiB, item ttl: 1s, hashing algorithm: XXH3, encoding: none
2024-09-12T23:08:55.308963Z  INFO runtime::init::dataset: Dataset taxi_trips registered (s3://spiceai-demo-datasets/taxi_trips/2024/), acceleration (duckdb:file), results cache enabled.
2024-09-12T23:08:55.310382Z  INFO runtime_table::accelerated::refresh_task: Loading data for dataset taxi_trips
2024-09-12T23:09:11.477553Z  INFO runtime_table::accelerated::refresh_task: Loaded 2,964,624 rows (399.38 MiB) for dataset taxi_trips in 16s 167ms.
```

At startup, Spice can also log a `WARN` that it capped the DuckDB memory limit to fit the memory available to the process. This message is expected when `duckdb_memory_limit` is not set, and you can ignore it for this recipe.

**Step 7.** Run a query against the `taxi_trips` dataset again, observing the fast query time.

```sql
select "VendorID", tpep_pickup_datetime, tpep_dropoff_datetime, passenger_count from taxi_trips order by tpep_pickup_datetime, tpep_dropoff_datetime, "VendorID", passenger_count limit 10;
```

```
+----------+----------------------+-----------------------+-----------------+
| VendorID | tpep_pickup_datetime | tpep_dropoff_datetime | passenger_count |
|   int32  |     timestamp[us]    |     timestamp[us]     |      int64      |
+----------+----------------------+-----------------------+-----------------+
| 2        | 2002-12-31T22:59:39  | 2002-12-31T23:05:41   | 1               |
| 2        | 2002-12-31T22:59:39  | 2002-12-31T23:05:41   | 1               |
| 2        | 2009-01-01T00:24:09  | 2009-01-01T01:13:00   | 2               |
| 2        | 2009-01-01T23:30:39  | 2009-01-02T00:01:39   | 1               |
| 2        | 2009-01-01T23:58:40  | 2009-01-02T00:01:40   | 1               |
| 2        | 2023-12-31T23:39:17  | 2023-12-31T23:42:00   | 2               |
| 2        | 2023-12-31T23:41:02  | 2023-12-31T23:48:03   | 1               |
| 2        | 2023-12-31T23:47:28  | 2023-12-31T23:57:07   | 2               |
| 2        | 2023-12-31T23:49:12  | 2024-01-01T00:04:32   | 1               |
| 2        | 2023-12-31T23:54:27  | 2024-01-01T00:13:12   | 1               |
+----------+----------------------+-----------------------+-----------------+

Time: 0.020399 seconds. 10 rows.
```

## Learn more

- [DuckDB Data Accelerator Documentation](https://docs.spiceai.org/components/data-accelerators/duckdb).

- For using `spice sql`, see the [CLI reference](https://docs.spiceai.org/cli/reference/sql).

- See the [datasets reference](https://docs.spiceai.org/reference/spicepod/datasets) for additional dataset configuration options.
