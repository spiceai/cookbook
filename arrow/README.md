# In-Memory Arrow Data Accelerator

Works with `v1.0+`

Create a connector instance using sample data and accelerate it using In-Memory Arrow Data Accelerator.

## Requirements

- Spice CLI installed (see [Getting Started](https://docs.spiceai.org/getting-started)).

## Follow these steps

**Step 1.** Initialize a new Spice app.

```bash
spice init arrow-acceleration-qs
cd arrow-acceleration-qs
```

**Step 2.** Configure s3 dataset: copy and paste the YAML below to `spicepod.yaml` in the Spice app.

```yaml
version: v1
kind: Spicepod
name: arrow-acceleration-qs
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

Confirm in the terminal output the `taxi_trips` dataset has been registered:

```bash
2026/08/13 12:18:39 INFO Checking for latest Spice runtime release...
2026/08/13 12:18:39 INFO Spice.ai runtime starting...
2026-08-13T12:18:39.774775Z  INFO spiced: Starting runtime v2.1.5+models.metal
2026-08-13T12:18:39.775655Z  INFO runtime::init::caching: Initialized sql results cache; max size: 128.00 MiB, item ttl: 1s, hashing algorithm: XXH3, encoding: none
2026-08-13T12:18:39.775701Z  INFO runtime::init::caching: Initialized search results cache; max size: 128.00 MiB, item ttl: 1s, engine: Moka
2026-08-13T12:18:39.775720Z  INFO runtime::init::caching: Initialized embeddings cache; max size: 128.00 MiB, item ttl: 1s, engine: Moka
2026-08-13T12:18:39.776955Z  INFO runtime::init::dataset: Dataset taxi_trips initializing...
2026-08-13T12:18:39.777562Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2026-08-13T12:18:39.777944Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2026-08-13T12:18:40.981333Z  INFO runtime::init::dataset: Dataset taxi_trips registered (s3://spiceai-demo-datasets/taxi_trips/2024/), results cache enabled. duration_ms=0
2026-08-13T12:18:41.084720Z  INFO runtime: All components are loaded. Spice runtime is ready!
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

```console
+----------+----------------------+-----------------------+-----------------+
| VendorID | tpep_pickup_datetime | tpep_dropoff_datetime | passenger_count |
|   int32  |     timestamp[us]    |     timestamp[us]     |      int64      |
+----------+----------------------+-----------------------+-----------------+
| 2        | 2024-01-25T09:27:43  | 2024-01-25T09:37:09   | 1               |
| 2        | 2024-01-25T09:41:18  | 2024-01-25T09:56:19   | 1               |
| 1        | 2024-01-25T09:24:36  | 2024-01-25T10:03:59   | 1               |
| 2        | 2024-01-25T09:04:15  | 2024-01-25T09:16:53   | 1               |
| 2        | 2024-01-25T09:26:17  | 2024-01-25T09:42:50   | 1               |
| 2        | 2024-01-25T09:50:27  | 2024-01-25T10:09:28   | 1               |
| 1        | 2024-01-25T09:29:58  | 2024-01-25T09:37:14   | 1               |
| 1        | 2024-01-25T09:53:55  | 2024-01-25T10:25:37   | 1               |
| 1        | 2024-01-25T09:18:38  | 2024-01-25T09:43:35   | 1               |
| 1        | 2024-01-25T09:55:55  | 2024-01-25T10:05:55   | 1               |
+----------+----------------------+-----------------------+-----------------+

Time: 1.072190667 seconds. 10 rows.
```

> **Note:** The query has no `ORDER BY`, so which ten rows come back varies between runs — expect different trips than shown here.

**Step 5.** Update the `spicepod.yaml` to enable In-Memory Arrow acceleration.

```yaml
version: v1
kind: Spicepod
name: arrow-acceleration-qs
datasets:
  - from: s3://spiceai-demo-datasets/taxi_trips/2024/
    name: taxi_trips
    description: taxi trips in s3
    params:
      file_format: parquet
    acceleration:
      enabled: true
```

**Step 6.** Save the changes in Spice app and observe the dataset updating and accelerating.

```bash
2026-08-13T12:19:22.038848Z  INFO runtime::init::dataset: Accelerated Dataset taxi_trips updating...
2026-08-13T12:19:23.118534Z  INFO runtime_table::accelerated::refresh_task: Loading data for dataset taxi_trips
2026-08-13T12:19:25.902457Z  INFO runtime_table::accelerated::refresh_task: Loaded 2,964,624 rows (399.38 MiB) for dataset taxi_trips in 2s 783ms.
2026-08-13T12:19:26.977420Z  INFO runtime::init::dataset: Dataset taxi_trips registered (s3://spiceai-demo-datasets/taxi_trips/2024/), acceleration (arrow), results cache enabled. duration_ms=0
```

**Step 7.** Run a query against the `taxi_trips` dataset again, observing the fast query time.

```sql
select "VendorID", tpep_pickup_datetime, tpep_dropoff_datetime, passenger_count from taxi_trips limit 10;
```

```console
+----------+----------------------+-----------------------+-----------------+
| VendorID | tpep_pickup_datetime | tpep_dropoff_datetime | passenger_count |
|   int32  |     timestamp[us]    |     timestamp[us]     |      int64      |
+----------+----------------------+-----------------------+-----------------+
| 1        | 2024-01-03T10:42:24  | 2024-01-03T10:53:32   | 2               |
| 2        | 2024-01-03T10:53:30  | 2024-01-03T11:12:09   | 2               |
| 2        | 2024-01-03T10:56:10  | 2024-01-03T11:07:08   | 2               |
| 1        | 2024-01-03T10:49:00  | 2024-01-03T11:08:07   | 2               |
| 2        | 2024-01-03T10:08:43  | 2024-01-03T10:18:24   | 2               |
| 2        | 2024-01-03T10:30:50  | 2024-01-03T10:37:26   | 2               |
| 2        | 2024-01-03T10:58:54  | 2024-01-03T11:07:38   | 2               |
| 2        | 2024-01-03T10:17:19  | 2024-01-03T10:41:15   | 2               |
| 2        | 2024-01-03T10:03:09  | 2024-01-03T10:07:16   | 2               |
| 2        | 2024-01-03T10:39:29  | 2024-01-03T10:57:56   | 2               |
+----------+----------------------+-----------------------+-----------------+

Time: 0.003522625 seconds. 10 rows.
```

## Learn more

- [In-Memory Arrow Data Accelerator Documentation](https://docs.spiceai.org/components/data-accelerators/arrow).

- For using `spice sql`, see the [CLI reference](https://docs.spiceai.org/cli/reference/sql).

- See the [datasets reference](https://docs.spiceai.org/reference/spicepod/datasets) for additional dataset configuration options.
