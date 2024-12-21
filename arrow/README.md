# In-Memory Arrow Data Accelerator

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
version: v1beta1
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

Confirm in the terminal output the `taxi_trips` dataset has been loaded:

```bash
2024/10/22 12:27:07 INFO Checking for latest Spice runtime release...
2024/10/22 12:27:07 INFO Spice.ai runtime starting...
2024-10-22T19:27:08.372600Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2024-10-22T19:27:08.372667Z  INFO runtime::metrics_server: Spice Runtime Metrics listening on 127.0.0.1:9090
2024-10-22T19:27:08.372790Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2024-10-22T19:27:08.373723Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2024-10-22T19:27:08.572674Z  INFO runtime: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
2024-10-22T19:27:08.582201Z  INFO runtime: Tool [document_similarity] ready to use
2024-10-22T19:27:08.582226Z  INFO runtime: Tool [table_schema] ready to use
2024-10-22T19:27:08.582231Z  INFO runtime: Tool [sql] ready to use
2024-10-22T19:27:08.582236Z  INFO runtime: Tool [list_datasets] ready to use
2024-10-22T19:27:08.582242Z  INFO runtime: Tool [random_sample] ready to use
2024-10-22T19:27:08.582245Z  INFO runtime: Tool [sample_distinct_columns] ready to use
2024-10-22T19:27:08.582251Z  INFO runtime: Tool [top_n_sample] ready to use
2024-10-22T19:27:09.991363Z  INFO runtime: Dataset taxi_trips registered (s3://spiceai-demo-datasets/taxi_trips/2024/), results cache enabled.
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
| 2        | 2024-01-29T19:28:41  | 2024-01-29T19:36:46   | 2               |
| 1        | 2024-01-29T19:22:21  | 2024-01-29T19:28:45   | 2               |
| 1        | 2024-01-29T19:50:24  | 2024-01-29T20:09:21   | 2               |
| 1        | 2024-01-29T19:43:52  | 2024-01-29T20:01:40   | 2               |
| 1        | 2024-01-29T19:09:57  | 2024-01-29T19:55:36   | 2               |
| 1        | 2024-01-29T19:51:28  | 2024-01-29T20:09:16   | 2               |
| 1        | 2024-01-29T19:23:46  | 2024-01-29T19:31:06   | 2               |
| 2        | 2024-01-29T19:01:27  | 2024-01-29T19:09:07   | 2               |
| 1        | 2024-01-29T19:13:53  | 2024-01-29T19:23:09   | 2               |
| 1        | 2024-01-29T19:53:55  | 2024-01-29T20:06:56   | 2               |
+----------+----------------------+-----------------------+-----------------+

Time: 4.291336125 seconds. 10 rows.
```

**Step 5.** Update the `spicepod.yaml` to enable In-Memory Arrow acceleration.

```yaml
version: v1beta1
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
2024-10-22T19:28:24.204608Z  INFO runtime: Updating accelerated dataset taxi_trips...
2024-10-22T19:28:25.202828Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset taxi_trips
2024-10-22T19:29:07.729346Z  INFO runtime::accelerated_table::refresh_task: Loaded 2,964,624 rows (398.86 MiB) for dataset taxi_trips in 42s 525ms.
2024-10-22T19:29:09.217425Z  INFO runtime: Dataset taxi_trips registered (s3://spiceai-demo-datasets/taxi_trips/2024/), acceleration (arrow), results cache enabled.
```

**Step 7.** Run a query against the `taxi_trips` dataset again, observing the fast query time.

```sql
select "VendorID", tpep_pickup_datetime, tpep_dropoff_datetime, passenger_count from taxi_trips limit 10;
+----------+----------------------+-----------------------+-----------------+
| VendorID | tpep_pickup_datetime | tpep_dropoff_datetime | passenger_count |
+----------+----------------------+-----------------------+-----------------+
| 1        | 2024-01-12T19:14:53  | 2024-01-12T19:28:34   | 2               |
| 2        | 2024-01-12T19:03:12  | 2024-01-12T19:17:19   | 2               |
| 2        | 2024-01-12T19:34:22  | 2024-01-12T19:38:11   | 2               |
| 2        | 2024-01-12T19:44:51  | 2024-01-12T19:49:40   | 2               |
| 1        | 2024-01-12T19:31:54  | 2024-01-12T19:38:43   | 2               |
| 2        | 2024-01-12T19:54:37  | 2024-01-12T19:59:55   | 2               |
| 1        | 2024-01-12T19:02:32  | 2024-01-12T19:12:25   | 2               |
| 1        | 2024-01-12T19:22:38  | 2024-01-12T19:37:30   | 2               |
| 2        | 2024-01-12T19:34:30  | 2024-01-12T20:31:18   | 2               |
| 2        | 2024-01-12T19:54:06  | 2024-01-12T20:07:29   | 2               |
+----------+----------------------+-----------------------+-----------------+

Time: 0.013083584 seconds. 10 rows.
```

## Learn more

- [In-Memory Arrow Data Accelerator Documentation](https://docs.spiceai.org/components/data-accelerators/arrow).

- For using `spice sql`, see the [CLI reference](https://docs.spiceai.org/cli/reference/sql).

- See the [datasets reference](https://docs.spiceai.org/reference/spicepod/datasets) for additional dataset configuration options.
