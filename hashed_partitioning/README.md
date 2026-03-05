# Hashed Partitioning with DuckDB

Accelerate queries on terabyte and petabyte-scale datasets using hashed partitioning, which prunes irrelevant data during filters on categorical columns like IDs.

Hashed partitioning divides data into fixed buckets using a hash expression for even distribution. It can significantly improve query performance for large datasets by reducing the volume of data required when processing a query. It works well for unpredictable categorical data, such as location IDs in geospatial workloads, distinct from range partitioning suited to sequential fields like dates.

This cookbook demonstrates accelerating and querying NYC taxi trip Parquet files from S3 using hashed partitioning with the `bucket` function and DuckDB acceleration.

## Step 1. Clone the repository and navigate to the Hashed Partitioning cookbook

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/hashed_partitioning
```

## Step 2. Spicepod configuration
Review `spicepod.yaml` in this directory. It configures `taxi_trips` acceleration with hashed partitioning on `PULocationID` using `partition_by` and `bucket(10, PULocationID)`.

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

and you'll see a plan shape where `logical_plan` begins with `TableScan` and `physical_plan` includes `PartitionedUnionExec` and `CooperativeExec` over partitioned scans.

```shell
logical_plan
  TableScan: taxi_trips projection=[VendorID, tpep_pickup_datetime, tpep_dropoff_datetime, passenger_count, trip_distance, RatecodeID, store_and_fwd_flag, PULocationID, DOLocationID, payment_type, fare_amount, extra, mta_tax, tip_amount, tolls_amount, improvement_surcharge, total_amount, congestion_surcharge, Airport_fee]

physical_plan
  PartitionedUnionExec
    CooperativeExec
      ... partition scans ...
```

If you add a filter on the partitioned column to the query,

```sql
EXPLAIN SELECT * FROM taxi_trips WHERE PULocationID = 221;
```

In this case, the explain output should show pruning for the partition filter, with the `PULocationID = 221` predicate applied and fewer partition scans than the unfiltered query.

## Learn more

[DuckDB Partitioning Documentation](https://spiceai.org/docs/components/data-accelerators/duckdb#partitioning)
[Data Acceleration](https://spiceai.org/docs/features/data-acceleration)
