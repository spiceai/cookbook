# Accelerated Dataset Retention Policy

This recipe demonstrates how to configure a retention policy for an accelerated dataset to evict data that is older than a specified duration.

## Pre-requisites

- Spice is installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation).

## Steps

**Step 1.** Initialize and start Spice

```bash
spice init retention-recipe
cd retention-recipe
```

**Step 2.** Add a dataset without a acceleration retention policy by editing spicepod.yaml

```yaml
version: v1
kind: Spicepod
name: retention-recipe
datasets:
  - from: s3://spiceai-demo-datasets/taxi_trips/2024/
    name: taxi_trips
    time_column: tpep_pickup_datetime
    params:
      file_format: parquet
    acceleration:
      enabled: true
```

**Step 3.** Run spice and see the dataset loaded

When dataset is being accelerated, there's no retention policy applied to the dataset.

```bash
2024-08-26T22:58:35.727218Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2024-08-26T22:58:35.727245Z  INFO runtime::metrics_server: Spice Runtime Metrics listening on 127.0.0.1:9090
2024-08-26T22:58:35.729973Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2024-08-26T22:58:35.732064Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2024-08-26T22:58:35.929371Z  INFO runtime: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
2024-08-26T22:58:36.532031Z  INFO runtime: Dataset taxi_trips registered (s3://spiceai-demo-datasets/taxi_trips/2024/), acceleration (arrow, 10m refresh, 60s retention), results cache enabled.
2024-08-26T22:58:36.533166Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset taxi_trips
2024-08-26T22:58:43.217885Z  INFO runtime::accelerated_table::refresh_task: Loaded 2,964,624 rows (421.71 MiB) for dataset taxi_trips in 6s 684ms.
```

**Step 4.** Run queries against the dataset using the Spice SQL REPL after the dataset is loaded.

```bash
spice sql

Welcome to the Spice.ai SQL REPL! Type 'help' for help.

show tables; -- list available tables
sql> select count(1) from taxi_trips;
+-----------------+
| COUNT(Int64(1)) |
+-----------------+
| 2964624         |
+-----------------+

Time: 0.012826375 seconds. 1 rows.
sql> select * from taxi_trips order by tpep_pickup_datetime limit 5;
+----------+----------------------+-----------------------+-----------------+---------------+------------+--------------------+--------------+--------------+--------------+-------------+-------+---------+------------+--------------+-----------------------+--------------+----------------------+-------------+
| VendorID | tpep_pickup_datetime | tpep_dropoff_datetime | passenger_count | trip_distance | RatecodeID | store_and_fwd_flag | PULocationID | DOLocationID | payment_type | fare_amount | extra | mta_tax | tip_amount | tolls_amount | improvement_surcharge | total_amount | congestion_surcharge | Airport_fee |
+----------+----------------------+-----------------------+-----------------+---------------+------------+--------------------+--------------+--------------+--------------+-------------+-------+---------+------------+--------------+-----------------------+--------------+----------------------+-------------+
| 2        | 2002-12-31T22:59:39  | 2002-12-31T23:05:41   | 1               | 0.63          | 1          | N                  | 170          | 170          | 3            | 6.5         | 0.0   | 0.5     | 0.0        | 0.0          | 1.0                   | 10.5         | 2.5                  | 0.0         |
| 2        | 2002-12-31T22:59:39  | 2002-12-31T23:05:41   | 1               | 0.63          | 1          | N                  | 170          | 170          | 3            | -6.5        | 0.0   | -0.5    | 0.0        | 0.0          | -1.0                  | -10.5        | -2.5                 | 0.0         |
| 2        | 2009-01-01T00:24:09  | 2009-01-01T01:13:00   | 2               | 10.88         | 1          | N                  | 138          | 264          | 2            | 50.6        | 9.25  | 0.5     | 0.0        | 6.94         | 1.0                   | 68.29        | 0.0                  | 0.0         |
| 2        | 2009-01-01T23:30:39  | 2009-01-02T00:01:39   | 1               | 10.99         | 1          | N                  | 237          | 264          | 2            | 45.0        | 3.5   | 0.5     | 0.0        | 0.0          | 1.0                   | 50.0         | 0.0                  | 0.0         |
| 2        | 2009-01-01T23:58:40  | 2009-01-02T00:01:40   | 1               | 0.46          | 1          | N                  | 137          | 264          | 2            | 4.4         | 3.5   | 0.5     | 0.0        | 0.0          | 1.0                   | 9.4          | 0.0                  | 0.0         |
+----------+----------------------+-----------------------+-----------------+---------------+------------+--------------------+--------------+--------------+--------------+-------------+-------+---------+------------+--------------+-----------------------+--------------+----------------------+-------------+

Time: 0.053698917 seconds. 5 rows.
```

**Step 6.** Stop spice runtime by pressing (ctrl + c), update the spicepod config to include a retention configuration that will exclude 5 rows of data from the dataset.

```yaml
version: v1
kind: Spicepod
name: retention-recipe
datasets:
  - from: s3://spiceai-demo-datasets/taxi_trips/2024/
    name: taxi_trips
    time_column: tpep_pickup_datetime
    params:
      file_format: parquet
    acceleration:
      enabled: true
      refresh_check_interval: 10m
      retention_check_enabled: true
      retention_check_interval: 60s
      retention_period: 35040h # 4 years, this will exclude 5 rows of data from the dataset
```

**Step 7.** Start the spice runtime by running `spice run`

Observe that the log shows that 0 records evicted for the dataset, and the loaded dataset include 5 less rows. This is because the retention policy is filtered out during the initial data loading.

```bash
2025-03-27T03:34:34.371144Z  INFO spiced: Starting runtime v1.0.7-build.7f8f25179+models.metal
2025-03-27T03:34:35.713104Z  INFO runtime::init::results_cache: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
2025-03-27T03:34:35.713340Z  INFO runtime::init::dataset: Initializing dataset taxi_trips
2025-03-27T03:34:35.715105Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2025-03-27T03:34:35.715138Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2025-03-27T03:34:35.715406Z  INFO runtime::metrics_server: Spice Runtime Metrics listening on 127.0.0.1:9090
2025-03-27T03:34:35.716024Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2025-03-27T03:34:39.220352Z  INFO runtime::init::dataset: Dataset taxi_trips registered (s3://spiceai-demo-datasets/taxi_trips/2024/), acceleration (arrow, 600s refresh, 180s retention), results cache enabled.
2025-03-27T03:34:39.221986Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset taxi_trips
2025-03-27T03:34:39.222061Z  INFO runtime::accelerated_table: [retention] Evicting data for taxi_trips where tpep_pickup_datetime < 2021-03-28T03:34:39+00:00...
2025-03-27T03:34:39.226484Z  INFO runtime::accelerated_table: [retention] Evicted 0 records for taxi_trips
2025-03-27T03:35:25.610069Z  INFO runtime::accelerated_table::refresh_task: Loaded 2,964,619 rows (400.10 MiB) for dataset taxi_trips in 46s 388ms.
```

**Step 6.** Run queries against the dataset using the Spice SQL REPL again to check the outdated data is no longer within the dataset.

```bash
sql> select count(1) from taxi_trips;
+-----------------+
| COUNT(Int64(1)) |
+-----------------+
| 2964619         |
+-----------------+

Time: 0.008739667 seconds. 1 rows.
sql> select * from taxi_trips order by tpep_pickup_datetime limit 5;
+----------+----------------------+-----------------------+-----------------+---------------+------------+--------------------+--------------+--------------+--------------+-------------+-------+---------+------------+--------------+-----------------------+--------------+----------------------+-------------+
| VendorID | tpep_pickup_datetime | tpep_dropoff_datetime | passenger_count | trip_distance | RatecodeID | store_and_fwd_flag | PULocationID | DOLocationID | payment_type | fare_amount | extra | mta_tax | tip_amount | tolls_amount | improvement_surcharge | total_amount | congestion_surcharge | Airport_fee |
+----------+----------------------+-----------------------+-----------------+---------------+------------+--------------------+--------------+--------------+--------------+-------------+-------+---------+------------+--------------+-----------------------+--------------+----------------------+-------------+
| 2        | 2023-12-31T23:39:17  | 2023-12-31T23:42:00   | 2               | 0.47          | 1          | N                  | 90           | 68           | 1            | 5.1         | 1.0   | 0.5     | 0.0        | 0.0          | 1.0                   | 10.1         | 2.5                  | 0.0         |
| 2        | 2023-12-31T23:41:02  | 2023-12-31T23:48:03   | 1               | 0.4           | 1          | N                  | 246          | 246          | 2            | 7.2         | 1.0   | 0.5     | 0.0        | 0.0          | 1.0                   | 12.2         | 2.5                  | 0.0         |
| 2        | 2023-12-31T23:47:28  | 2023-12-31T23:57:07   | 2               | 1.44          | 1          | N                  | 68           | 137          | 1            | 10.7        | 1.0   | 0.5     | 3.14       | 0.0          | 1.0                   | 18.84        | 2.5                  | 0.0         |
| 2        | 2023-12-31T23:49:12  | 2024-01-01T00:04:32   | 1               | 3.14          | 1          | N                  | 234          | 237          | 1            | 17.0        | 1.0   | 0.5     | 6.6        | 0.0          | 1.0                   | 28.6         | 2.5                  | 0.0         |
| 2        | 2023-12-31T23:54:27  | 2024-01-01T00:13:12   | 1               | 7.7           | 1          | N                  | 229          | 244          | 1            | 33.1        | 1.0   | 0.5     | 7.62       | 0.0          | 1.0                   | 45.72        | 2.5                  | 0.0         |
+----------+----------------------+-----------------------+-----------------+---------------+------------+--------------------+--------------+--------------+--------------+-------------+-------+---------+------------+--------------+-----------------------+--------------+----------------------+-------------+

Time: 0.050874208 seconds. 5 rows.
```
