# Apache Spark Data Connector

Spice can read data from a Spark instance. This guide will start Spark isntance with sample data, create an app, load and query a dataset.

## Prerequisites

This recipe requires [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) to be installed.

Also ensure that you have the `spice` CLI installed. You can find instructions on how to install it [here](https://docs.spiceai.org/getting-started).

## How to run

Clone this cookbook repo locally and navigate to the `spark` directory:

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/spark
```

### Spark 3.5

1. Navigate to `spark-3.5` folder and start the Docker Compose stack, which includes a Spark 3.5.6 instance and init notebook to load the NYC taxi trip parquet data:

  ```shell
  docker compose up -d
  ```

  It will take about about 30 seconds to start the Spark instance and load the sample dataset.
  Check service logs to see when the Spark instance is ready:

  ```shell
  docker compose logs -f spark
  ```
  ```shell
  spark  | 25/01/14 14:11:12 INFO CodeGenerator: Code generated in 14.890809 ms
  spark  | +--------+--------------------+---------------------+---------------+-------------+----------+------------------+------------+------------+------------+-----------+-----+-------+----------+------------+---------------------+------------+--------------------+-----------+
  spark  | |VendorID|tpep_pickup_datetime|tpep_dropoff_datetime|passenger_count|trip_distance|RatecodeID|store_and_fwd_flag|PULocationID|DOLocationID|payment_type|fare_amount|extra|mta_tax|tip_amount|tolls_amount|improvement_surcharge|total_amount|congestion_surcharge|airport_fee|
  spark  | +--------+--------------------+---------------------+---------------+-------------+----------+------------------+------------+------------+------------+-----------+-----+-------+----------+------------+---------------------+------------+--------------------+-----------+
  spark  | |       1| 2022-03-01 00:13:08|  2022-03-01 00:24:35|            1.0|          2.4|       1.0|                 N|          90|         209|           2|       10.0|  3.0|    0.5|       0.0|         0.0|                  0.3|        13.8|                 2.5|        0.0|
  spark  | |       1| 2022-03-01 00:47:52|  2022-03-01 01:00:08|            1.0|          2.2|       1.0|                 N|         148|         234|           2|       10.5|  3.0|    0.5|       0.0|         0.0|                  0.3|        14.3|                 2.5|        0.0|
  spark  | |       2| 2022-03-01 00:02:46|  2022-03-01 00:46:43|            1.0|        19.78|       2.0|                 N|         132|         249|           1|       52.0|  0.0|    0.5|     11.06|         0.0|                  0.3|       67.61|                 2.5|       1.25|
  spark  | |       2| 2022-03-01 00:52:43|  2022-03-01 01:03:40|            2.0|         2.94|       1.0|                 N|         211|          66|           1|       11.0|  0.5|    0.5|      4.44|         0.0|                  0.3|       19.24|                 2.5|        0.0|
  spark  | |       2| 2022-03-01 00:15:35|  2022-03-01 00:34:13|            1.0|         8.57|       1.0|                 N|         138|         197|           1|       25.0|  0.5|    0.5|      5.51|         0.0|                  0.3|       33.06|                 0.0|       1.25|
  spark  | |       1| 2022-03-01 00:11:57|  2022-03-01 00:53:05|            2.0|         14.0|       1.0|                 N|         132|          33|           1|       43.5| 1.75|    0.5|       9.2|         0.0|                  0.3|       55.25|                 0.0|       1.25|
  spark  | |       2| 2022-03-01 00:05:11|  2022-03-01 00:08:22|            1.0|         0.61|       1.0|                 N|         166|         151|           1|        4.5|  0.5|    0.5|       1.0|         0.0|                  0.3|         6.8|                 0.0|        0.0|
  spark  | |       2| 2022-03-01 00:30:56|  2022-03-01 00:46:21|            1.0|         2.83|       1.0|                 N|          74|         238|           1|       13.0|  0.5|    0.5|       3.7|         0.0|                  0.3|        18.0|                 0.0|        0.0|
  spark  | |       2| 2022-03-01 00:30:28|  2022-03-01 00:30:36|            1.0|          0.1|       1.0|                 N|         145|         145|           3|       -2.5| -0.5|   -0.5|       0.0|         0.0|                 -0.3|        -3.8|                 0.0|        0.0|
  spark  | |       2| 2022-03-01 00:30:28|  2022-03-01 00:30:36|            1.0|          0.1|       1.0|                 N|         145|         145|           2|        2.5|  0.5|    0.5|       0.0|         0.0|                  0.3|         3.8|                 0.0|        0.0|
  spark  | +--------+--------------------+---------------------+---------------+-------------+----------+------------------+------------+------------+------------+-----------+-----+-------+----------+------------+---------------------+------------+--------------------+-----------+
  spark  |
  spark  | 25/01/14 14:11:12 INFO SparkContext: Invoking stop() from shutdown hook
  spark  | 25/01/14 14:11:12 INFO SparkContext: SparkContext is stopping with exitCode 0.
  spark  | 25/01/14 14:11:12 INFO SparkUI: Stopped Spark web UI at http://2556af46dcb0:4040
  spark  | 25/01/14 14:11:12 INFO StandaloneSchedulerBackend: Shutting down all executors
  spark  | 25/01/14 14:11:12 INFO StandaloneSchedulerBackend$StandaloneDriverEndpoint: Asking each executor to shut down
  spark  | 25/01/14 14:11:12 INFO MapOutputTrackerMasterEndpoint: MapOutputTrackerMasterEndpoint stopped!
  spark  | 25/01/14 14:11:12 INFO MemoryStore: MemoryStore cleared
  spark  | 25/01/14 14:11:12 INFO BlockManager: BlockManager stopped
  spark  | 25/01/14 14:11:12 INFO BlockManagerMaster: BlockManagerMaster stopped
  spark  | 25/01/14 14:11:12 INFO OutputCommitCoordinator$OutputCommitCoordinatorEndpoint: OutputCommitCoordinator stopped!
  spark  | 25/01/14 14:11:12 INFO SparkContext: Successfully stopped SparkContext
  spark  | 25/01/14 14:11:12 INFO ShutdownHookManager: Shutdown hook called
  spark  | 25/01/14 14:11:12 INFO ShutdownHookManager: Deleting directory /tmp/spark-e026e8e3-f302-4adf-bdf3-de083138fa40
  spark  | 25/01/14 14:11:12 INFO ShutdownHookManager: Deleting directory /tmp/spark-314a37cb-843b-4e6a-a4a2-8e71944f85bf
  spark  | 25/01/14 14:11:12 INFO ShutdownHookManager: Deleting directory /tmp/spark-314a37cb-843b-4e6a-a4a2-8e71944f85bf/pyspark-ffa34bfd-aa50-4a7a-80f5-4b6dc6e0b0fb
  spark  | Spark services started! ✅
  ```

2. Initialize a Spice app

  ```shell
  spice init spark_demo
  cd spark_demo
  ```

3. Start the Spice runtime

  ```shell
  spice run
  ```
  ```shell
  2025/01/14 02:52:58 INFO Checking for latest Spice runtime release...
  2025/01/14 02:52:59 INFO Spice.ai runtime starting...
  2025-01-13T17:53:00.171638Z  INFO runtime::init::dataset: No datasets were configured. If this is unexpected, check the Spicepod configuration.
  2025-01-13T17:53:00.181202Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
  2025-01-13T17:53:00.181420Z  INFO runtime::metrics_server: Spice Runtime Metrics listening on 127.0.0.1:9090
  2025-01-13T17:53:00.185632Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
  2025-01-13T17:53:00.185712Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
  2025-01-13T17:53:00.196585Z  INFO runtime::init::results_cache: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
  ```

4. Configure a Spark dataset into the spicepod. Copy and paste the following `spicepod.yaml` configuration into your Spicepod.

  ```yaml
  version: v1
  kind: Spicepod
  name: spark_demo

  datasets:
    - from: spark:nyc_taxis
      name: nyc_taxis
      params:
          spark_remote: sc://localhost:15002
  ```

5. Confirm that the runtime has loaded the new table (in the original terminal)

  ```shell
  2025-01-13T17:54:33.672161Z  INFO runtime::init::dataset: Dataset nyc_taxis registered (spark:nyc_taxis), results cache enabled.
  ```

6. Check the table exists from the Spice REPL

  ```shell
  spice sql
  ```
  ```
  Welcome to the Spice.ai SQL REPL! Type 'help' for help.

  show tables; -- list available tables
  ```
  ```shell
  sql> show tables;
  +---------------+--------------+--------------+------------+
  | table_catalog | table_schema | table_name   | table_type |
  +---------------+--------------+--------------+------------+
  | spice         | runtime      | task_history | BASE TABLE |
  | spice         | runtime      | metrics      | BASE TABLE |
  | spice         | public       | nyc_taxis    | BASE TABLE |
  +---------------+--------------+--------------+------------+

  Time: 0.031211 seconds. 3 rows.
  ```

7. Check the table structure of `nyc_taxis`.
  ```sql
  describe nyc_taxis;
  ```
  ```shell
  +-----------------------+-----------------------------------------+-------------+
  | column_name           | data_type                               | is_nullable |
  +-----------------------+-----------------------------------------+-------------+
  | VendorID              | Int64                                   | YES         |
  | tpep_pickup_datetime  | Timestamp(Microsecond, Some("Etc/UTC")) | YES         |
  | tpep_dropoff_datetime | Timestamp(Microsecond, Some("Etc/UTC")) | YES         |
  | passenger_count       | Float64                                 | YES         |
  | trip_distance         | Float64                                 | YES         |
  | RatecodeID            | Float64                                 | YES         |
  | store_and_fwd_flag    | Utf8                                    | YES         |
  | PULocationID          | Int64                                   | YES         |
  | DOLocationID          | Int64                                   | YES         |
  | payment_type          | Int64                                   | YES         |
  | fare_amount           | Float64                                 | YES         |
  | extra                 | Float64                                 | YES         |
  | mta_tax               | Float64                                 | YES         |
  | tip_amount            | Float64                                 | YES         |
  | tolls_amount          | Float64                                 | YES         |
  | improvement_surcharge | Float64                                 | YES         |
  | total_amount          | Float64                                 | YES         |
  | congestion_surcharge  | Float64                                 | YES         |
  | airport_fee           | Float64                                 | YES         |
  +-----------------------+-----------------------------------------+-------------+

  Time: 0.006024208 seconds. 19 rows.
  ```

8. Query against the Spark table. The spice runtime will make a network call to the Spark instance.

  ```sql
  SELECT * FROM nyc_taxis LIMIT 10;
  ```
  ```shell
  +----------+----------------------+-----------------------+-----------------+---------------+------------+--------------------+--------------+--------------+--------------+-------------+-------+---------+------------+--------------+-----------------------+--------------+----------------------+-------------+
  | VendorID | tpep_pickup_datetime | tpep_dropoff_datetime | passenger_count | trip_distance | RatecodeID | store_and_fwd_flag | PULocationID | DOLocationID | payment_type | fare_amount | extra | mta_tax | tip_amount | tolls_amount | improvement_surcharge | total_amount | congestion_surcharge | airport_fee |
  +----------+----------------------+-----------------------+-----------------+---------------+------------+--------------------+--------------+--------------+--------------+-------------+-------+---------+------------+--------------+-----------------------+--------------+----------------------+-------------+
  | 1        | 2022-03-01T00:13:08Z | 2022-03-01T00:24:35Z  | 1.0             | 2.4           | 1.0        | N                  | 90           | 209          | 2            | 10.0        | 3.0   | 0.5     | 0.0        | 0.0          | 0.3                   | 13.8         | 2.5                  | 0.0         |
  | 1        | 2022-03-01T00:47:52Z | 2022-03-01T01:00:08Z  | 1.0             | 2.2           | 1.0        | N                  | 148          | 234          | 2            | 10.5        | 3.0   | 0.5     | 0.0        | 0.0          | 0.3                   | 14.3         | 2.5                  | 0.0         |
  | 2        | 2022-03-01T00:02:46Z | 2022-03-01T00:46:43Z  | 1.0             | 19.78         | 2.0        | N                  | 132          | 249          | 1            | 52.0        | 0.0   | 0.5     | 11.06      | 0.0          | 0.3                   | 67.61        | 2.5                  | 1.25        |
  | 2        | 2022-03-01T00:52:43Z | 2022-03-01T01:03:40Z  | 2.0             | 2.94          | 1.0        | N                  | 211          | 66           | 1            | 11.0        | 0.5   | 0.5     | 4.44       | 0.0          | 0.3                   | 19.24        | 2.5                  | 0.0         |
  | 2        | 2022-03-01T00:15:35Z | 2022-03-01T00:34:13Z  | 1.0             | 8.57          | 1.0        | N                  | 138          | 197          | 1            | 25.0        | 0.5   | 0.5     | 5.51       | 0.0          | 0.3                   | 33.06        | 0.0                  | 1.25        |
  | 1        | 2022-03-01T00:11:57Z | 2022-03-01T00:53:05Z  | 2.0             | 14.0          | 1.0        | N                  | 132          | 33           | 1            | 43.5        | 1.75  | 0.5     | 9.2        | 0.0          | 0.3                   | 55.25        | 0.0                  | 1.25        |
  | 2        | 2022-03-01T00:05:11Z | 2022-03-01T00:08:22Z  | 1.0             | 0.61          | 1.0        | N                  | 166          | 151          | 1            | 4.5         | 0.5   | 0.5     | 1.0        | 0.0          | 0.3                   | 6.8          | 0.0                  | 0.0         |
  | 2        | 2022-03-01T00:30:56Z | 2022-03-01T00:46:21Z  | 1.0             | 2.83          | 1.0        | N                  | 74           | 238          | 1            | 13.0        | 0.5   | 0.5     | 3.7        | 0.0          | 0.3                   | 18.0         | 0.0                  | 0.0         |
  | 2        | 2022-03-01T00:30:28Z | 2022-03-01T00:30:36Z  | 1.0             | 0.1           | 1.0        | N                  | 145          | 145          | 3            | -2.5        | -0.5  | -0.5    | 0.0        | 0.0          | -0.3                  | -3.8         | 0.0                  | 0.0         |
  | 2        | 2022-03-01T00:30:28Z | 2022-03-01T00:30:36Z  | 1.0             | 0.1           | 1.0        | N                  | 145          | 145          | 2            | 2.5         | 0.5   | 0.5     | 0.0        | 0.0          | 0.3                   | 3.8          | 0.0                  | 0.0         |
  +----------+----------------------+-----------------------+-----------------+---------------+------------+--------------------+--------------+--------------+--------------+-------------+-------+---------+------------+--------------+-----------------------+--------------+----------------------+-------------+

  Time: 1.139626792 seconds. 10 rows.
  ```

9. Stop the Spark instance and cleanup

  ```shell
  docker compose down --volumes --rmi local
  ```

### Spark 4

1. Navigate to `spark-4` folder and start the Docker Compose stack, which includes a Spark 4.0.0 instance and init notebook to load the NYC taxi trip parquet data:

  ```shell
  docker compose up -d
  ```

  It will take about about 30 seconds to start the Spark instance and load the sample dataset.
  Check service logs to see when the Spark instance is ready:

  ```shell
  docker compose logs -f spark
  ```

  ```shell
  ...
  Spark services started! ✅
  ```

2. Restart spice runtime in spark_demo app

  ```shell
  spice run
  ```

  ```console
  Spice.ai OSS CLI v1.4.0-unstable-build.8eee8ad4b
  2025/06/10 10:46:32 INFO Checking for latest Spice runtime release...
  2025/06/10 10:46:32 INFO Spice.ai runtime starting...
  2025-06-10T01:46:32.725076Z  INFO spiced: Starting runtime v1.4.0-unstable-build.8eee8ad4b+models
  2025-06-10T01:46:32.742491Z  INFO runtime::init::caching: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
  2025-06-10T01:46:32.744098Z  INFO runtime::init::caching: Initialized search results cache;
  2025-06-10T01:46:33.592583Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
  2025-06-10T01:46:33.592555Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
  2025-06-10T01:46:33.599924Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
  2025-06-10T01:46:33.602360Z  INFO runtime::init::dataset: Initializing dataset nyc_taxis
  2025-06-10T01:46:36.494592Z  INFO runtime::init::dataset: Dataset nyc_taxis registered (spark:nyc_taxis), results cache enabled.
  2025-06-10T01:46:36.596578Z  INFO runtime: All components are loaded. Spice runtime is ready!
  ```

3. Query against the Spark table.

  ```sql
  SELECT * FROM nyc_taxis LIMIT 10;
  ```

  ```
  +----------+----------------------+-----------------------+-----------------+---------------+------------+--------------------+--------------+--------------+--------------+-------------+-------+---------+------------+--------------+-----------------------+--------------+----------------------+-------------+
  | VendorID | tpep_pickup_datetime | tpep_dropoff_datetime | passenger_count | trip_distance | RatecodeID | store_and_fwd_flag | PULocationID | DOLocationID | payment_type | fare_amount | extra | mta_tax | tip_amount | tolls_amount | improvement_surcharge | total_amount | congestion_surcharge | airport_fee |
  +----------+----------------------+-----------------------+-----------------+---------------+------------+--------------------+--------------+--------------+--------------+-------------+-------+---------+------------+--------------+-----------------------+--------------+----------------------+-------------+
  | 1        | 2022-03-01T00:13:08Z | 2022-03-01T00:24:35Z  | 1.0             | 2.4           | 1.0        | N                  | 90           | 209          | 2            | 10.0        | 3.0   | 0.5     | 0.0        | 0.0          | 0.3                   | 13.8         | 2.5                  | 0.0         |
  | 1        | 2022-03-01T00:47:52Z | 2022-03-01T01:00:08Z  | 1.0             | 2.2           | 1.0        | N                  | 148          | 234          | 2            | 10.5        | 3.0   | 0.5     | 0.0        | 0.0          | 0.3                   | 14.3         | 2.5                  | 0.0         |
  | 2        | 2022-03-01T00:02:46Z | 2022-03-01T00:46:43Z  | 1.0             | 19.78         | 2.0        | N                  | 132          | 249          | 1            | 52.0        | 0.0   | 0.5     | 11.06      | 0.0          | 0.3                   | 67.61        | 2.5                  | 1.25        |
  | 2        | 2022-03-01T00:52:43Z | 2022-03-01T01:03:40Z  | 2.0             | 2.94          | 1.0        | N                  | 211          | 66           | 1            | 11.0        | 0.5   | 0.5     | 4.44       | 0.0          | 0.3                   | 19.24        | 2.5                  | 0.0         |
  | 2        | 2022-03-01T00:15:35Z | 2022-03-01T00:34:13Z  | 1.0             | 8.57          | 1.0        | N                  | 138          | 197          | 1            | 25.0        | 0.5   | 0.5     | 5.51       | 0.0          | 0.3                   | 33.06        | 0.0                  | 1.25        |
  | 1        | 2022-03-01T00:11:57Z | 2022-03-01T00:53:05Z  | 2.0             | 14.0          | 1.0        | N                  | 132          | 33           | 1            | 43.5        | 1.75  | 0.5     | 9.2        | 0.0          | 0.3                   | 55.25        | 0.0                  | 1.25        |
  | 2        | 2022-03-01T00:05:11Z | 2022-03-01T00:08:22Z  | 1.0             | 0.61          | 1.0        | N                  | 166          | 151          | 1            | 4.5         | 0.5   | 0.5     | 1.0        | 0.0          | 0.3                   | 6.8          | 0.0                  | 0.0         |
  | 2        | 2022-03-01T00:30:56Z | 2022-03-01T00:46:21Z  | 1.0             | 2.83          | 1.0        | N                  | 74           | 238          | 1            | 13.0        | 0.5   | 0.5     | 3.7        | 0.0          | 0.3                   | 18.0         | 0.0                  | 0.0         |
  | 2        | 2022-03-01T00:30:28Z | 2022-03-01T00:30:36Z  | 1.0             | 0.1           | 1.0        | N                  | 145          | 145          | 3            | -2.5        | -0.5  | -0.5    | 0.0        | 0.0          | -0.3                  | -3.8         | 0.0                  | 0.0         |
  | 2        | 2022-03-01T00:30:28Z | 2022-03-01T00:30:36Z  | 1.0             | 0.1           | 1.0        | N                  | 145          | 145          | 2            | 2.5         | 0.5   | 0.5     | 0.0        | 0.0          | 0.3                   | 3.8          | 0.0                  | 0.0         |
  +----------+----------------------+-----------------------+-----------------+---------------+------------+--------------------+--------------+--------------+--------------+-------------+-------+---------+------------+--------------+-----------------------+--------------+----------------------+-------------+

  Time: 0.658063792 seconds. 10 rows.
  ```

4. Stop the Spark instance and cleanup

  ```shell
  docker compose down --volumes --rmi local
  ```
