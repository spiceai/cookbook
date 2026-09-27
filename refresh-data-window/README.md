# Refresh Data Window

Works with `v1.0+`

`refresh_data_window` is a duration parameter that filters data refresh source queries for time-series to recent data (duration into past from now).

Requires `time_column` and `time_format` (optional) to also be configured. Only supported for `full` refresh mode datasets.

## Pre-requisites

- Spice is installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation).

## Steps

**Step 1.** Initialize and start Spice

```bash
spice init refresh-data-window-recipe
cd refresh-data-window-recipe
```

**Step 2.** Add a new dataset

```bash
version: v1
kind: Spicepod
name: refresh-data-window-recipe
datasets:
  - from: s3://spiceai-demo-datasets/taxi_trips/2024/
    name: taxi_trips
    time_column: tpep_pickup_datetime
    params:
      file_format: parquet
      s3_auth: public
    acceleration:
      enabled: true
```

**Step 3.** Run spice and check number of rows in `taxi_trips`

```bash
 INFO Spice.ai runtime starting...
2026-09-13T12:09:52.083872Z  INFO spiced: Starting runtime v2.3.0+models.metal
2026-09-13T12:09:52.088606Z  INFO runtime::init::dataset: Dataset taxi_trips initializing...
2026-09-13T12:09:52.288168Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2026-09-13T12:09:52.288514Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2026-09-13T12:09:53.154126Z  INFO runtime::init::dataset: Dataset taxi_trips registered (s3://spiceai-demo-datasets/taxi_trips/2024/), acceleration (arrow), results cache enabled. duration_ms=0
2026-09-13T12:09:53.155485Z  INFO runtime_table::accelerated::refresh_task: Loading data for dataset taxi_trips
2026-09-13T12:09:57.995471Z  INFO runtime_table::accelerated::refresh_task: Loaded 2,964,624 rows (399.38 MiB) for dataset taxi_trips in 4s 839ms.
2026-09-13T12:09:58.030404Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

Run `spice sql` to check the number of rows and the 5 earliest records sorted by `tpep_pickup_datetime`

```shell
spice sql
```

```shell
Welcome to the Spice.ai SQL REPL! Type `help` or `?` for commands.

Examples:
  show tables;              -- list available tables
  describe <table_name>;    -- show column types
  nql <question>            -- natural language to SQL (requires a model)

```

```sql
select count(1) from taxi_trips;
```

```shell
+-----------------+
| count(Int64(1)) |
|      int64      |
+-----------------+
| 2964624         |
+-----------------+

Time: 0.001221792 seconds. 1 rows.
```

```sql
select * from taxi_trips order by tpep_pickup_datetime limit 5;
```

```shell
+----------+----------------------+-----------------------+-----------------+---------------+------------+--------------------+--------------+--------------+--------------+-------------+---------+---------+------------+--------------+-----------------------+--------------+----------------------+-------------+
| VendorID | tpep_pickup_datetime | tpep_dropoff_datetime | passenger_count | trip_distance | RatecodeID | store_and_fwd_flag | PULocationID | DOLocationID | payment_type | fare_amount |  extra  | mta_tax | tip_amount | tolls_amount | improvement_surcharge | total_amount | congestion_surcharge | Airport_fee |
|   int32  |     timestamp[us]    |     timestamp[us]     |      int64      |    float64    |    int64   |       varchar      |     int32    |     int32    |     int64    |   float64   | float64 | float64 |   float64  |    float64   |        float64        |    float64   |        float64       |   float64   |
+----------+----------------------+-----------------------+-----------------+---------------+------------+--------------------+--------------+--------------+--------------+-------------+---------+---------+------------+--------------+-----------------------+--------------+----------------------+-------------+
| 2        | 2002-12-31T22:59:39  | 2002-12-31T23:05:41   | 1               | 0.63          | 1          | N                  | 170          | 170          | 3            | -6.5        | 0.0     | -0.5    | 0.0        | 0.0          | -1.0                  | -10.5        | -2.5                 | 0.0         |
| 2        | 2002-12-31T22:59:39  | 2002-12-31T23:05:41   | 1               | 0.63          | 1          | N                  | 170          | 170          | 3            | 6.5         | 0.0     | 0.5     | 0.0        | 0.0          | 1.0                   | 10.5         | 2.5                  | 0.0         |
| 2        | 2009-01-01T00:24:09  | 2009-01-01T01:13:00   | 2               | 10.88         | 1          | N                  | 138          | 264          | 2            | 50.6        | 9.25    | 0.5     | 0.0        | 6.94         | 1.0                   | 68.29        | 0.0                  | 0.0         |
| 2        | 2009-01-01T23:30:39  | 2009-01-02T00:01:39   | 1               | 10.99         | 1          | N                  | 237          | 264          | 2            | 45.0        | 3.5     | 0.5     | 0.0        | 0.0          | 1.0                   | 50.0         | 0.0                  | 0.0         |
| 2        | 2009-01-01T23:58:40  | 2009-01-02T00:01:40   | 1               | 0.46          | 1          | N                  | 137          | 264          | 2            | 4.4         | 3.5     | 0.5     | 0.0        | 0.0          | 1.0                   | 9.4          | 0.0                  | 0.0         |
+----------+----------------------+-----------------------+-----------------+---------------+------------+--------------------+--------------+--------------+--------------+-------------+---------+---------+------------+--------------+-----------------------+--------------+----------------------+-------------+

Time: 0.002656291 seconds. 5 rows.
```

**Step 4.** Edit spicepod.yaml to add `refresh_data_window`

```bash
version: v1
kind: Spicepod
name: refresh-data-window-recipe
datasets:
  - from: s3://spiceai-demo-datasets/taxi_trips/2024/
    name: taxi_trips
    time_column: tpep_pickup_datetime
    params:
      file_format: parquet
      s3_auth: public
    acceleration:
      enabled: true
      refresh_data_window: 35040h # 4 years, this will evict 5 rows of data from the dataset
```

Check if dataset has been reloaded

```bash
2026-09-13T12:10:02.904824Z  INFO runtime::init::dataset: Accelerated Dataset taxi_trips updating...
2026-09-13T12:10:03.991227Z  INFO runtime_table::accelerated::refresh_task: Loading data for dataset taxi_trips
2026-09-13T12:10:12.436828Z  INFO runtime_table::accelerated::refresh_task: Loaded 2,964,619 rows (399.38 MiB) for dataset taxi_trips in 8s 445ms.
2026-09-13T12:10:13.551412Z  INFO runtime::init::dataset: Dataset taxi_trips registered (s3://spiceai-demo-datasets/taxi_trips/2024/), acceleration (arrow), results cache enabled. duration_ms=0

```

Check the number of rows again, and it shows 5 rows difference. The previous 5 earliest records are excluded after reloading.

```sql
select count(1) from taxi_trips;
```

```shell
+-----------------+
| count(Int64(1)) |
|      int64      |
+-----------------+
| 2964619         |
+-----------------+

Time: 0.001739 seconds. 1 rows.
```

```sql
select * from taxi_trips order by tpep_pickup_datetime limit 1;
```

```shell
+----------+----------------------+-----------------------+-----------------+---------------+------------+--------------------+--------------+--------------+--------------+-------------+---------+---------+------------+--------------+-----------------------+--------------+----------------------+-------------+
| VendorID | tpep_pickup_datetime | tpep_dropoff_datetime | passenger_count | trip_distance | RatecodeID | store_and_fwd_flag | PULocationID | DOLocationID | payment_type | fare_amount |  extra  | mta_tax | tip_amount | tolls_amount | improvement_surcharge | total_amount | congestion_surcharge | Airport_fee |
|   int32  |     timestamp[us]    |     timestamp[us]     |      int64      |    float64    |    int64   |       varchar      |     int32    |     int32    |     int64    |   float64   | float64 | float64 |   float64  |    float64   |        float64        |    float64   |        float64       |   float64   |
+----------+----------------------+-----------------------+-----------------+---------------+------------+--------------------+--------------+--------------+--------------+-------------+---------+---------+------------+--------------+-----------------------+--------------+----------------------+-------------+
| 2        | 2023-12-31T23:39:17  | 2023-12-31T23:42:00   | 2               | 0.47          | 1          | N                  | 90           | 68           | 1            | 5.1         | 1.0     | 0.5     | 0.0        | 0.0          | 1.0                   | 10.1         | 2.5                  | 0.0         |
+----------+----------------------+-----------------------+-----------------+---------------+------------+--------------------+--------------+--------------+--------------+-------------+---------+---------+------------+--------------+-----------------------+--------------+----------------------+-------------+

Time: 0.003305417 seconds. 1 rows.
```
