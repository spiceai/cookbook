# Cayenne Data Accelerator

Works with `v1.9+`

This recipe will walkthrough how to accelerate a local copy of the taxi trips dataset stored in S3 using Cayenne as the data accelerator engine.

## Requirements

- Spice CLI installed (see [Getting Started](https://docs.spiceai.org/getting-started)).

## Follow these steps

**Step 1.** Initialize a new Spice app.

```bash
spice init cayenne-acceleration-qs
cd cayenne-acceleration-qs
```

**Step 2.** Configure s3 dataset: copy and paste the YAML below to `spicepod.yaml` in the Spice app.

```yaml
version: v1
kind: Spicepod
name: cayenne-acceleration-qs
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
2026-08-24T20:57:43.603253Z  INFO spiced: Starting runtime v2.1.5+models.metal
2026-08-24T20:57:43.687793Z  INFO runtime::init::caching: Initialized sql results cache; max size: 128.00 MiB, item ttl: 1s, hashing algorithm: XXH3, encoding: none
2026-08-24T20:57:43.968078Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2026-08-24T20:57:43.972502Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2026-08-24T20:57:49.910117Z  INFO runtime::init::dataset: Dataset taxi_trips registered (s3://spiceai-demo-datasets/taxi_trips/2024/), results cache enabled. duration_ms=18
2026-08-24T20:57:50.043569Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

**Step 4.** Run queries against the dataset using the Spice SQL REPL.

_In a new terminal_, start the Spice SQL REPL

```bash
spice sql
```

Query the `taxi_trips` dataset, observing the long query time.

```sql
select "VendorID", tpep_pickup_datetime, tpep_dropoff_datetime, passenger_count from taxi_trips limit 10;
```

```
+----------+----------------------+-----------------------+-----------------+
| VendorID | tpep_pickup_datetime | tpep_dropoff_datetime | passenger_count |
|   int32  |     timestamp[us]    |     timestamp[us]     |      int64      |
+----------+----------------------+-----------------------+-----------------+
| 1        | 2024-01-02T18:04:31  | 2024-01-02T18:11:49   | 0               |
| 1        | 2024-01-02T18:13:28  | 2024-01-02T18:34:45   | 0               |
| 1        | 2024-01-02T18:52:21  | 2024-01-02T18:57:43   | 0               |
| 1        | 2024-01-02T18:37:05  | 2024-01-02T18:51:38   | 0               |
| 1        | 2024-01-02T18:46:54  | 2024-01-02T18:53:18   | 0               |
| 1        | 2024-01-02T18:18:22  | 2024-01-02T18:24:30   | 0               |
| 1        | 2024-01-02T18:06:50  | 2024-01-02T18:25:04   | 0               |
| 1        | 2024-01-02T18:45:31  | 2024-01-02T18:58:08   | 0               |
| 1        | 2024-01-02T18:33:29  | 2024-01-02T18:42:09   | 0               |
| 1        | 2024-01-02T18:05:25  | 2024-01-02T18:17:25   | 0               |
+----------+----------------------+-----------------------+-----------------+

Time: 1.256426375 seconds. 10 rows.
```

**Step 5.** Update the `spicepod.yaml` to enable Cayenne acceleration.

```yaml
version: v1
kind: Spicepod
name: cayenne-acceleration-qs
datasets:
  - from: s3://spiceai-demo-datasets/taxi_trips/2024/
    name: taxi_trips
    description: taxi trips in s3
    params:
      file_format: parquet
    acceleration:
      enabled: true
      engine: cayenne
      mode: file
```

**Step 6.** Restart the Spice app and observe the dataset loading and accelerating.

```bash
Spice.ai runtime starting...
2026-08-24T20:58:40.483388Z  INFO spiced: Starting runtime v2.1.5+models.metal
2026-08-24T20:58:40.631669Z  INFO runtime::init::caching: Initialized sql results cache; max size: 128.00 MiB, item ttl: 1s, hashing algorithm: XXH3, encoding: none
2026-08-24T20:58:40.897943Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2026-08-24T20:58:40.905264Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2026-08-24T20:58:43.033807Z  INFO runtime::init::dataset: Dataset taxi_trips registered (s3://spiceai-demo-datasets/taxi_trips/2024/), acceleration (cayenne:file), results cache enabled. duration_ms=477
2026-08-24T20:58:43.035086Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset taxi_trips
2026-08-24T20:58:53.353320Z  INFO runtime::accelerated_table::refresh_task: Loaded 2,964,624 rows (399.38 MiB) for dataset taxi_trips in 10s 302ms.
2026-08-24T20:58:53.400890Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

**Step 7.** Run a query against the `taxi_trips` dataset again, observing the fast query time.

```sql
select "VendorID", tpep_pickup_datetime, tpep_dropoff_datetime, passenger_count from taxi_trips limit 10;
```

```
+----------+----------------------+-----------------------+-----------------+
| VendorID | tpep_pickup_datetime | tpep_dropoff_datetime | passenger_count |
|   int32  |     timestamp[us]    |     timestamp[us]     |      int64      |
+----------+----------------------+-----------------------+-----------------+
| 1        | 2024-01-04T18:01:18  | 2024-01-04T18:11:46   | 1               |
| 1        | 2024-01-04T18:13:06  | 2024-01-04T18:27:17   | 1               |
| 1        | 2024-01-04T18:29:48  | 2024-01-04T18:52:12   | 1               |
| 2        | 2024-01-04T18:19:18  | 2024-01-04T18:49:18   | 1               |
| 2        | 2024-01-04T18:52:38  | 2024-01-04T19:12:11   | 1               |
| 2        | 2024-01-04T18:29:18  | 2024-01-04T18:34:46   | 1               |
| 2        | 2024-01-04T18:36:24  | 2024-01-04T18:55:09   | 1               |
| 2        | 2024-01-04T18:26:17  | 2024-01-04T18:35:32   | 1               |
| 2        | 2024-01-04T18:51:48  | 2024-01-04T19:05:35   | 1               |
| 2        | 2024-01-04T18:06:09  | 2024-01-04T18:30:35   | 1               |
+----------+----------------------+-----------------------+-----------------+

Time: 0.064644125 seconds. 10 rows.
```

## Learn more

- [Cayenne Data Accelerator Documentation](https://docs.spiceai.org/components/data-accelerators/cayenne).

- For using `spice sql`, see the [CLI reference](https://docs.spiceai.org/cli/reference/sql).

- See the [datasets reference](https://docs.spiceai.org/reference/spicepod/datasets) for additional dataset configuration options.
