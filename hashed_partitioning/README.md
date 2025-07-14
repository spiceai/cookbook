# Hashed Partitioning with DuckDB

This cookbook demonstrates how to use the Spice OSS runtime to accelerate a dataset into multiple partitioned DuckDB files.

## Step 1. Clone the repository and navigate to the Hashed Partitioning cookbook

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/hashed_partitioning
```

## Step 2. Run Spice
The `spicepod.yaml` configuration will accelerate and partition the `taxi_trips` dataset by hashing the `PULocationID` column and placing the data into one of 10 buckets using the `partition_by` parameter.

```yaml
version: v1
kind: Spicepod
name: hashed-partitioning

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
      partition_by:
        - bucket(10, PULocationID)
```

If you know you will be writing queries that filter on the `PULocationID` often, this can improve query times for very large tables by pruning the amount of data required to be read in order to execute the query.

You can see by inspecting the physical plan, that querying without a filter involves scanning all the partitioned files.

Using `spice sql`, run:

```sql
EXPLAIN SELECT * FROM taxi_trips;
```

and you'll see the 10 `DuckSqlExec` plans for each partition scan.

```shell
+---------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| plan_type     | plan                                                                                                                                                                                                                                                                                                                                                                                   |
+---------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| logical_plan  | BytesProcessedNode                                                                                                                                                                                                                                                                                                                                                                     |
|               |   TableScan: taxi_trips projection=[VendorID, tpep_pickup_datetime, tpep_dropoff_datetime, passenger_count, trip_distance, RatecodeID, store_and_fwd_flag, PULocationID, DOLocationID, payment_type, fare_amount, extra, mta_tax, tip_amount, tolls_amount, improvement_surcharge, total_amount, congestion_surcharge, Airport_fee]                                                    |
| physical_plan | BytesProcessedExec                                                                                                                                                                                                                                                                                                                                                                     |
|               |   SchemaCastScanExec                                                                                                                                                                                                                                                                                                                                                                   |
|               |     RepartitionExec: partitioning=RoundRobinBatch(16), input_partitions=10                                                                                                                                                                                                                                                                                                             |
|               |       UnionExec                                                                                                                                                                                                                                                                                                                                                                        |
|               |         DuckSqlExec sql= SELECT "VendorID", "tpep_pickup_datetime", "tpep_dropoff_datetime", "passenger_count", "trip_distance", "RatecodeID", "store_and_fwd_flag", "PULocationID", "DOLocationID", "payment_type", "fare_amount", "extra", "mta_tax", "tip_amount", "tolls_amount", "improvement_surcharge", "total_amount", "congestion_surcharge", "Airport_fee" FROM taxi_trips   |
|               |         DuckSqlExec sql= SELECT "VendorID", "tpep_pickup_datetime", "tpep_dropoff_datetime", "passenger_count", "trip_distance", "RatecodeID", "store_and_fwd_flag", "PULocationID", "DOLocationID", "payment_type", "fare_amount", "extra", "mta_tax", "tip_amount", "tolls_amount", "improvement_surcharge", "total_amount", "congestion_surcharge", "Airport_fee" FROM taxi_trips   |
|               |         DuckSqlExec sql= SELECT "VendorID", "tpep_pickup_datetime", "tpep_dropoff_datetime", "passenger_count", "trip_distance", "RatecodeID", "store_and_fwd_flag", "PULocationID", "DOLocationID", "payment_type", "fare_amount", "extra", "mta_tax", "tip_amount", "tolls_amount", "improvement_surcharge", "total_amount", "congestion_surcharge", "Airport_fee" FROM taxi_trips   |
|               |         DuckSqlExec sql= SELECT "VendorID", "tpep_pickup_datetime", "tpep_dropoff_datetime", "passenger_count", "trip_distance", "RatecodeID", "store_and_fwd_flag", "PULocationID", "DOLocationID", "payment_type", "fare_amount", "extra", "mta_tax", "tip_amount", "tolls_amount", "improvement_surcharge", "total_amount", "congestion_surcharge", "Airport_fee" FROM taxi_trips   |
|               |         DuckSqlExec sql= SELECT "VendorID", "tpep_pickup_datetime", "tpep_dropoff_datetime", "passenger_count", "trip_distance", "RatecodeID", "store_and_fwd_flag", "PULocationID", "DOLocationID", "payment_type", "fare_amount", "extra", "mta_tax", "tip_amount", "tolls_amount", "improvement_surcharge", "total_amount", "congestion_surcharge", "Airport_fee" FROM taxi_trips   |
|               |         DuckSqlExec sql= SELECT "VendorID", "tpep_pickup_datetime", "tpep_dropoff_datetime", "passenger_count", "trip_distance", "RatecodeID", "store_and_fwd_flag", "PULocationID", "DOLocationID", "payment_type", "fare_amount", "extra", "mta_tax", "tip_amount", "tolls_amount", "improvement_surcharge", "total_amount", "congestion_surcharge", "Airport_fee" FROM taxi_trips   |
|               |         DuckSqlExec sql= SELECT "VendorID", "tpep_pickup_datetime", "tpep_dropoff_datetime", "passenger_count", "trip_distance", "RatecodeID", "store_and_fwd_flag", "PULocationID", "DOLocationID", "payment_type", "fare_amount", "extra", "mta_tax", "tip_amount", "tolls_amount", "improvement_surcharge", "total_amount", "congestion_surcharge", "Airport_fee" FROM taxi_trips   |
|               |         DuckSqlExec sql= SELECT "VendorID", "tpep_pickup_datetime", "tpep_dropoff_datetime", "passenger_count", "trip_distance", "RatecodeID", "store_and_fwd_flag", "PULocationID", "DOLocationID", "payment_type", "fare_amount", "extra", "mta_tax", "tip_amount", "tolls_amount", "improvement_surcharge", "total_amount", "congestion_surcharge", "Airport_fee" FROM taxi_trips   |
|               |         DuckSqlExec sql= SELECT "VendorID", "tpep_pickup_datetime", "tpep_dropoff_datetime", "passenger_count", "trip_distance", "RatecodeID", "store_and_fwd_flag", "PULocationID", "DOLocationID", "payment_type", "fare_amount", "extra", "mta_tax", "tip_amount", "tolls_amount", "improvement_surcharge", "total_amount", "congestion_surcharge", "Airport_fee" FROM taxi_trips   |
|               |         DuckSqlExec sql= SELECT "VendorID", "tpep_pickup_datetime", "tpep_dropoff_datetime", "passenger_count", "trip_distance", "RatecodeID", "store_and_fwd_flag", "PULocationID", "DOLocationID", "payment_type", "fare_amount", "extra", "mta_tax", "tip_amount", "tolls_amount", "improvement_surcharge", "total_amount", "congestion_surcharge", "Airport_fee" FROM taxi_trips   |
|               |                                                                                                                                                                                                                                                                                                                                                                                        |
+---------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
```

If you add a filter on the partitioned column,

```sql
EXPLAIN SELECT * FROM taxi_trips WHERE PULocationId = 221;
```

In this case, only one partitioned file is relevant for scanning and remains in the scan plan while all other partitions were pruned from the plan.

```shell
+---------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| plan_type     | plan                                                                                                                                                                                                                                                                                                                                                                                                           |
+---------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| logical_plan  | BytesProcessedNode                                                                                                                                                                                                                                                                                                                                                                                             |
|               |   TableScan: taxi_trips projection=[VendorID, tpep_pickup_datetime, tpep_dropoff_datetime, passenger_count, trip_distance, RatecodeID, store_and_fwd_flag, PULocationID, DOLocationID, payment_type, fare_amount, extra, mta_tax, tip_amount, tolls_amount, improvement_surcharge, total_amount, congestion_surcharge, Airport_fee], full_filters=[taxi_trips.PULocationID = Int32(221)]                       |
| physical_plan | BytesProcessedExec                                                                                                                                                                                                                                                                                                                                                                                             |
|               |   SchemaCastScanExec                                                                                                                                                                                                                                                                                                                                                                                           |
|               |     RepartitionExec: partitioning=RoundRobinBatch(16), input_partitions=1                                                                                                                                                                                                                                                                                                                                      |
|               |       DuckSqlExec sql= SELECT "VendorID", "tpep_pickup_datetime", "tpep_dropoff_datetime", "passenger_count", "trip_distance", "RatecodeID", "store_and_fwd_flag", "PULocationID", "DOLocationID", "payment_type", "fare_amount", "extra", "mta_tax", "tip_amount", "tolls_amount", "improvement_surcharge", "total_amount", "congestion_surcharge", "Airport_fee" FROM taxi_trips WHERE (PULocationID = 221)  |
|               |                                                                                                                                                                                                                                                                                                                                                                                                                |
+---------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
```

## Learn more

[DuckDB Partitioning Documentation](https://spiceai.org/docs/components/data-accelerators/duckdb#partitioning)
[Data Acceleration](https://spiceai.org/docs/features/data-acceleration)
