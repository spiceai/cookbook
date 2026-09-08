# Hashed Partitioning with Cayenne

Works with `v1.9.0+`

Accelerate queries on terabyte and petabyte-scale datasets using hashed partitioning, which prunes irrelevant data during filters on categorical columns like IDs.

Hashed partitioning divides data into fixed buckets using a hash expression for even distribution. It can significantly improve query performance for large datasets by reducing the volume of data required when processing a query. It works well for unpredictable categorical data, such as location IDs in geospatial workloads, distinct from range partitioning suited to sequential fields like dates.

This cookbook demonstrates accelerating and querying NYC taxi trip Parquet files from S3 using hashed partitioning with the `bucket` function and Cayenne acceleration.

## Step 1. Clone the repository and navigate to the Hashed Partitioning cookbook

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/hashed_partitioning
```

## Step 2. Spicepod configuration

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
      engine: cayenne
      mode: file
      partition_by:
        - bucket(10, PULocationID)
```

If you know you will be writing queries that filter on the `PULocationID` often, this can improve query times for very large tables by pruning the amount of data required to be read in order to execute the query.

## Step 3: Run Spice

In a terminal window, execute the command:

```bash
spice run
```

## Step 4: Verify partition pruning

You can see, by inspecting the physical plan, that querying without a filter involves scanning all the partitioned files.

In another terminal window, execute `spice sql`. Then at the `sql>` prompt, type:

```sql
EXPLAIN SELECT * FROM taxi_trips;
```

and you'll see the 10 `CayenneAccelerationExec` scans, one for each partition, combined by `PartitionedUnionExec`. The Vortex file paths are abbreviated below for readability.

Each partition directory is named `expr0=<encoded bucket>`, where the segment after `expr0=` is the type-tagged encoding of the bucket value — `v1.i64.v30` through `v1.i64.v39` for buckets 0-9.

```shell
+---------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|   plan_type   |                                                                                                                                                                                                                                                                                                                                                                                         plan                                          |
|    varchar    |                                                                                                                                                                                                                                                                                                                                                                                      varchar                                          |
+---------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| logical_plan  | TableScan: taxi_trips projection=[VendorID, tpep_pickup_datetime, tpep_dropoff_datetime, passenger_count, trip_distance, RatecodeID, store_and_fwd_flag, PULocationID, DOLocationID, payment_type, fare_amount, extra, mta_tax, tip_amount, tolls_amount, improvement_surcharge, total_amount, congestion_surcharge, Airport_fee]                                                                                                     |
| physical_plan | SchemaCastScanExec                                                                                                                                                                                                                                                                                                                                                                                                                    |
|               |   PartitionedUnionExec                                                                                                                                                                                                                                                                                                                                                                                                                |
|               |     CayenneAccelerationExec: snapshots_scanned=1, files_scanned=1                                                                                                                                                                                                                                                                                                                                                                     |
|               |       BytesProcessedExec                                                                                                                                                                                                                                                                                                                                                                                                              |
|               |         DataSourceExec: file_groups={1 group: [[.spice/data/taxi_trips/expr0=v1.i64.v33/.../..._00000.vortex]]}, projection=[VendorID, tpep_pickup_datetime, tpep_dropoff_datetime, passenger_count, trip_distance, RatecodeID, store_and_fwd_flag, PULocationID, DOLocationID, payment_type, fare_amount, extra, mta_tax, tip_amount, tolls_amount, improvement_surcharge, total_amount, congestion_surcharge, Airport_fee], file_type=vortex |
|               |     CayenneAccelerationExec: snapshots_scanned=1, files_scanned=1                                                                                                                                                                                                                                                                                                                                                                     |
|               |       BytesProcessedExec                                                                                                                                                                                                                                                                                                                                                                                                              |
|               |         DataSourceExec: file_groups={1 group: [[.spice/data/taxi_trips/expr0=v1.i64.v38/.../..._00000.vortex]]}, projection=[VendorID, tpep_pickup_datetime, tpep_dropoff_datetime, passenger_count, trip_distance, RatecodeID, store_and_fwd_flag, PULocationID, DOLocationID, payment_type, fare_amount, extra, mta_tax, tip_amount, tolls_amount, improvement_surcharge, total_amount, congestion_surcharge, Airport_fee], file_type=vortex |
|               |     CayenneAccelerationExec: snapshots_scanned=1, files_scanned=1                                                                                                                                                                                                                                                                                                                                                                     |
|               |       BytesProcessedExec                                                                                                                                                                                                                                                                                                                                                                                                              |
|               |         DataSourceExec: file_groups={1 group: [[.spice/data/taxi_trips/expr0=v1.i64.v30/.../..._00000.vortex]]}, projection=[VendorID, tpep_pickup_datetime, tpep_dropoff_datetime, passenger_count, trip_distance, RatecodeID, store_and_fwd_flag, PULocationID, DOLocationID, payment_type, fare_amount, extra, mta_tax, tip_amount, tolls_amount, improvement_surcharge, total_amount, congestion_surcharge, Airport_fee], file_type=vortex |
|               |     CayenneAccelerationExec: snapshots_scanned=1, files_scanned=1                                                                                                                                                                                                                                                                                                                                                                     |
|               |       BytesProcessedExec                                                                                                                                                                                                                                                                                                                                                                                                              |
|               |         DataSourceExec: file_groups={1 group: [[.spice/data/taxi_trips/expr0=v1.i64.v37/.../..._00000.vortex]]}, projection=[VendorID, tpep_pickup_datetime, tpep_dropoff_datetime, passenger_count, trip_distance, RatecodeID, store_and_fwd_flag, PULocationID, DOLocationID, payment_type, fare_amount, extra, mta_tax, tip_amount, tolls_amount, improvement_surcharge, total_amount, congestion_surcharge, Airport_fee], file_type=vortex |
|               |     CayenneAccelerationExec: snapshots_scanned=1, files_scanned=1                                                                                                                                                                                                                                                                                                                                                                     |
|               |       BytesProcessedExec                                                                                                                                                                                                                                                                                                                                                                                                              |
|               |         DataSourceExec: file_groups={1 group: [[.spice/data/taxi_trips/expr0=v1.i64.v31/.../..._00000.vortex]]}, projection=[VendorID, tpep_pickup_datetime, tpep_dropoff_datetime, passenger_count, trip_distance, RatecodeID, store_and_fwd_flag, PULocationID, DOLocationID, payment_type, fare_amount, extra, mta_tax, tip_amount, tolls_amount, improvement_surcharge, total_amount, congestion_surcharge, Airport_fee], file_type=vortex |
|               |     CayenneAccelerationExec: snapshots_scanned=1, files_scanned=1                                                                                                                                                                                                                                                                                                                                                                     |
|               |       BytesProcessedExec                                                                                                                                                                                                                                                                                                                                                                                                              |
|               |         DataSourceExec: file_groups={1 group: [[.spice/data/taxi_trips/expr0=v1.i64.v39/.../..._00000.vortex]]}, projection=[VendorID, tpep_pickup_datetime, tpep_dropoff_datetime, passenger_count, trip_distance, RatecodeID, store_and_fwd_flag, PULocationID, DOLocationID, payment_type, fare_amount, extra, mta_tax, tip_amount, tolls_amount, improvement_surcharge, total_amount, congestion_surcharge, Airport_fee], file_type=vortex |
|               |     CayenneAccelerationExec: snapshots_scanned=1, files_scanned=1                                                                                                                                                                                                                                                                                                                                                                     |
|               |       BytesProcessedExec                                                                                                                                                                                                                                                                                                                                                                                                              |
|               |         DataSourceExec: file_groups={1 group: [[.spice/data/taxi_trips/expr0=v1.i64.v34/.../..._00000.vortex]]}, projection=[VendorID, tpep_pickup_datetime, tpep_dropoff_datetime, passenger_count, trip_distance, RatecodeID, store_and_fwd_flag, PULocationID, DOLocationID, payment_type, fare_amount, extra, mta_tax, tip_amount, tolls_amount, improvement_surcharge, total_amount, congestion_surcharge, Airport_fee], file_type=vortex |
|               |     CayenneAccelerationExec: snapshots_scanned=1, files_scanned=1                                                                                                                                                                                                                                                                                                                                                                     |
|               |       BytesProcessedExec                                                                                                                                                                                                                                                                                                                                                                                                              |
|               |         DataSourceExec: file_groups={1 group: [[.spice/data/taxi_trips/expr0=v1.i64.v32/.../..._00000.vortex]]}, projection=[VendorID, tpep_pickup_datetime, tpep_dropoff_datetime, passenger_count, trip_distance, RatecodeID, store_and_fwd_flag, PULocationID, DOLocationID, payment_type, fare_amount, extra, mta_tax, tip_amount, tolls_amount, improvement_surcharge, total_amount, congestion_surcharge, Airport_fee], file_type=vortex |
|               |     CayenneAccelerationExec: snapshots_scanned=1, files_scanned=1                                                                                                                                                                                                                                                                                                                                                                     |
|               |       BytesProcessedExec                                                                                                                                                                                                                                                                                                                                                                                                              |
|               |         DataSourceExec: file_groups={1 group: [[.spice/data/taxi_trips/expr0=v1.i64.v35/.../..._00000.vortex]]}, projection=[VendorID, tpep_pickup_datetime, tpep_dropoff_datetime, passenger_count, trip_distance, RatecodeID, store_and_fwd_flag, PULocationID, DOLocationID, payment_type, fare_amount, extra, mta_tax, tip_amount, tolls_amount, improvement_surcharge, total_amount, congestion_surcharge, Airport_fee], file_type=vortex |
|               |     CayenneAccelerationExec: snapshots_scanned=1, files_scanned=1                                                                                                                                                                                                                                                                                                                                                                     |
|               |       BytesProcessedExec                                                                                                                                                                                                                                                                                                                                                                                                              |
|               |         DataSourceExec: file_groups={1 group: [[.spice/data/taxi_trips/expr0=v1.i64.v36/.../..._00000.vortex]]}, projection=[VendorID, tpep_pickup_datetime, tpep_dropoff_datetime, passenger_count, trip_distance, RatecodeID, store_and_fwd_flag, PULocationID, DOLocationID, payment_type, fare_amount, extra, mta_tax, tip_amount, tolls_amount, improvement_surcharge, total_amount, congestion_surcharge, Airport_fee], file_type=vortex |
|               |                                                                                                                                                                                                                                                                                                                                                                                                                                       |
+---------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

Time: 0.0146875 seconds. 2 rows.
```

If you add a filter on the partitioned column to the query,

```sql
EXPLAIN SELECT COUNT(*) FROM taxi_trips WHERE PULocationID = 221;
```

In this case, only one partitioned file is relevant for scanning and remains in the scan plan while all other partitions are pruned from the plan — a single `CayenneAccelerationExec` reading the `expr0=v1.i64.v37` partition.

```shell
+---------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|   plan_type   |                                                                                                                                                                                                                             plan  |
|    varchar    |                                                                                                                                                                                                                           varchar |
+---------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| logical_plan  | Projection: count(Int64(1)) AS count(*)                                                                                                                                                                                           |
|               |   Aggregate: groupBy=[[]], aggr=[[count(Int64(1))]]                                                                                                                                                                               |
|               |     Projection:                                                                                                                                                                                                                   |
|               |       Filter: taxi_trips.PULocationID = Int32(221)                                                                                                                                                                                |
|               |         TableScan: taxi_trips projection=[PULocationID], partial_filters=[taxi_trips.PULocationID = Int32(221)]                                                                                                                   |
| physical_plan | ProjectionExec: expr=[count(Int64(1))@0 as count(*)]                                                                                                                                                                              |
|               |   AggregateExec: mode=Final, gby=[], aggr=[count(Int64(1))]                                                                                                                                                                       |
|               |     CoalescePartitionsExec                                                                                                                                                                                                        |
|               |       AggregateExec: mode=Partial, gby=[], aggr=[count(Int64(1))]                                                                                                                                                                 |
|               |         RepartitionExec: partitioning=RoundRobinBatch(8), input_partitions=1                                                                                                                                                      |
|               |           ProjectionExec: expr=[]                                                                                                                                                                                                 |
|               |             SchemaCastScanExec                                                                                                                                                                                                    |
|               |               CayenneAccelerationExec: snapshots_scanned=1, files_scanned=1                                                                                                                                                       |
|               |                 BytesProcessedExec                                                                                                                                                                                                |
|               |                   DataSourceExec: file_groups={1 group: [[.spice/data/taxi_trips/expr0=v1.i64.v37/.../..._00000.vortex]]}, projection=[PULocationID], file_type=vortex, predicate: PULocationID@7 = 221                                    |
|               |                                                                                                                                                                                                                                   |
+---------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

Time: 0.012550625 seconds. 2 rows.
```

## Learn more

[Cayenne Partitioning Documentation](https://spiceai.org/docs/components/data-accelerators/cayenne)
[Data Acceleration](https://spiceai.org/docs/features/data-acceleration)
