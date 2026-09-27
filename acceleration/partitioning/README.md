# Dataset Partitioning

Works with `v1.11.0+`

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
2026-08-15T12:09:50.445159Z  INFO runtime::init::caching: Initialized sql results cache; max size: 128.00 MiB, item ttl: 1s, hashing algorithm: XXH3, encoding: none
2026-08-15T12:09:50.465737Z  INFO runtime::init::dataset: Dataset taxi_trips initializing...
2026-08-15T12:09:50.646429Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2026-08-15T12:09:50.646776Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2026-08-15T12:09:51.818849Z  INFO runtime::init::dataset: Dataset taxi_trips registered (s3://spiceai-demo-datasets/taxi_trips/2024/), acceleration (cayenne:file), results cache enabled. duration_ms=101
2026-08-15T12:09:51.820118Z  INFO runtime_table::accelerated::refresh_task: Loading data for dataset taxi_trips
2026-08-15T12:10:02.183762Z  INFO runtime_table::accelerated::refresh_task: Loaded 2,964,624 rows (399.38 MiB) for dataset taxi_trips in 10s 363ms.
2026-08-15T12:10:02.265750Z  INFO runtime: All components are loaded. Spice runtime is ready!
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
|       int64      |
+------------------+
| 260              |
+------------------+

Time: 0.031309 seconds. 1 rows.
```

Now run a query filtering by a specific pickup location:

```sql
SELECT COUNT(*) FROM taxi_trips WHERE PULocationID = 161;
```

```
+----------+
| count(*) |
|   int64  |
+----------+
| 143471   |
+----------+

Time: 0.007991375 seconds. 1 rows.
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
2026-08-15T12:11:09.653803Z  INFO runtime::init::caching: Initialized sql results cache; max size: 128.00 MiB, item ttl: 1s, hashing algorithm: XXH3, encoding: none
2026-08-15T12:11:09.655711Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2026-08-15T12:11:09.656053Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2026-08-15T12:11:09.664397Z  INFO runtime::init::dataset: Dataset taxi_trips initializing...
2026-08-15T12:11:15.122630Z  INFO runtime::init::dataset: Dataset taxi_trips registered (s3://spiceai-demo-datasets/taxi_trips/2024/), acceleration (cayenne:file), results cache enabled. duration_ms=76
2026-08-15T12:11:15.123765Z  INFO runtime_table::accelerated::refresh_task: Loading data for dataset taxi_trips
2026-08-15T12:11:23.519321Z  INFO runtime_table::accelerated::refresh_task: Loaded 2,964,624 rows (399.38 MiB) for dataset taxi_trips in 8s 395ms.
2026-08-15T12:11:23.604755Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

**Step 7.** Run the same query again to see the performance improvement from partition pruning.

```sql
SELECT COUNT(*) FROM taxi_trips WHERE PULocationID = 161;
```

```
+----------+
| count(*) |
|   int64  |
+----------+
| 143471   |
+----------+

Time: 0.00751475 seconds. 1 rows.
```

The same count is returned, but Spice now only reads the partition containing `PULocationID = 161` rather than scanning the entire dataset. The partition files are visible under `.spice/data/taxi_trips/` as `expr0=<bucket>` directories.

The speedup grows with the size of the dataset and the selectivity of the filter — on this 2.9M-row sample both queries already complete in single-digit milliseconds, so the benefit is most visible at terabyte scale.

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
