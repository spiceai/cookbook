# Dataset Partitioning

This recipe demonstrates how to partition accelerated datasets to improve query performance by enabling partition pruning for queries. Partitioning groups rows into separate files based on an expression, allowing Spice to skip reading unnecessary partitions during queries.

## Requirements

- Spice CLI installed (see [Getting Started](https://docs.spiceai.org/getting-started)).

## Follow these steps

**Step 1.** Initialize a new Spice app.

```bash
spice init partitioning-qs
cd partitioning-qs
```

**Step 2.** Configure the taxi trips dataset: copy and paste the YAML below to `spicepod.yaml` in the Spice app.

```yaml
version: v1
kind: Spicepod
name: partitioning-qs
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

**Step 3.** Start the Spice runtime.

```bash
spice run
```

Confirm in the terminal output the `taxi_trips` dataset has been loaded and accelerated:

```bash
Spice.ai runtime starting...
2024-09-16T21:25:43.305988Z  INFO runtime::metrics_server: Spice Runtime Metrics listening on 127.0.0.1:9090
2024-09-16T21:25:43.306009Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2024-09-16T21:25:43.309474Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2024-09-16T21:25:43.311587Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2024-09-16T21:25:43.507974Z  INFO runtime: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
2024-09-16T21:25:44.101055Z  INFO runtime: Dataset taxi_trips registered (s3://spiceai-demo-datasets/taxi_trips/2024/), acceleration (cayenne:file), results cache enabled.
2024-09-16T21:25:45.310382Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset taxi_trips
2024-09-16T21:26:01.477553Z  INFO runtime::accelerated_table::refresh_task: Loaded 2,964,624 rows (421.71 MiB) for dataset taxi_trips in 4s 167ms.
```

**Step 4.** Run queries against the dataset using the Spice SQL REPL.

_In a new terminal_, start the Spice SQL REPL

```bash
spice sql
```

Query the `taxi_trips` dataset to check how many unique pickup locations exist:

```sql
SELECT COUNT(DISTINCT PULocationID) as unique_locations FROM taxi_trips;
```

```
+------------------+
| unique_locations |
+------------------+
| 260              |
+------------------+

Time: 0.088840307 seconds. 1 rows
```

Now run a query filtering by a specific pickup location:

```sql
SELECT COUNT(*) FROM taxi_trips WHERE PULocationID = 161;
```

```
+----------+
| count(*) |
+----------+
| 143471   |
+----------+

Time: 0.041479883 seconds. 1 rows.
```

Notice that without partitioning, Spice must scan the entire dataset for this query.

**Step 5.** Update the `spicepod.yaml` to enable partitioning by pickup location.

Add the `partition_by` parameter to partition the dataset into 50 buckets based on the `PULocationID` column:

```yaml
version: v1
kind: Spicepod
name: partitioning-qs
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
      partition_by:
        - bucket(50, PULocationID)
```

The `bucket(50, PULocationID)` function hashes the `PULocationID` column and distributes rows into 50 partition files. This enables partition pruning for queries that filter on `PULocationID`.

**Step 6.** Restart the Spice app and observe the dataset being loaded with partitioning.

```bash
2024-09-12T23:08:53.964728Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2024-09-12T23:08:53.964845Z  INFO runtime::metrics_server: Spice Runtime Metrics listening on 127.0.0.1:9090
2024-09-12T23:08:53.965420Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2024-09-12T23:08:53.965471Z  INFO runtime: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
2024-09-12T23:08:53.966168Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2024-09-12T23:08:55.308963Z  INFO runtime: Dataset taxi_trips registered (s3://spiceai-demo-datasets/taxi_trips/2024/), acceleration (cayenne:file), results cache enabled.
2024-09-12T23:08:55.310382Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset taxi_trips
2024-09-12T23:09:11.477553Z  INFO runtime::accelerated_table::refresh_task: Loaded 2,964,624 rows (421.71 MiB) for dataset taxi_trips in 24s 380ms.
```

**Step 7.** Run the same query again to see the performance improvement from partition pruning.

```sql
SELECT COUNT(*) FROM taxi_trips WHERE PULocationID = 161;
```

```
+----------+
| count(*) |
+----------+
| 143471   |
+----------+

Time: 0.028580917 seconds. 1 rows.
```

The query is now significantly faster because Spice only reads the partition(s) containing `PULocationID = 161`, rather than scanning the entire dataset.

## Partitioning Functions

The `partition_by` parameter supports several expressions:

- **`bucket(n, column)`**: Hashes the column value and distributes rows into `n` partitions
  ```yaml
  partition_by:
    - bucket(50, PULocationID)
  ```

- **Direct column reference**: Partitions by the column's actual values
  ```yaml
  partition_by:
    - PULocationID
  ```

- **Other expressions**: Any scalar expression that references exactly one column
  ```yaml
  partition_by:
    - YEAR(tpep_pickup_datetime)
  ```

## Learn more

- [Dataset Partitioning Documentation](https://docs.spiceai.org/features/data-acceleration/partitioning)

- [Cayenne Data Accelerator Documentation](https://docs.spiceai.org/components/data-accelerators/cayenne)

- For using `spice sql`, see the [CLI reference](https://docs.spiceai.org/cli/reference/sql)

- See the [datasets reference](https://docs.spiceai.org/reference/spicepod/datasets) for additional dataset configuration options

