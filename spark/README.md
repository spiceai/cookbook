# Apache Spark Data Connector

Spice can read data from a Spark instance. This guide will create an app, configure Spark to run locally, load and query a dataset. It assumes:

- Spice is installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation).
- Apache Spark package newer than v3.4.0 is downloaded (see the [Download Apache Spark](https://spark.apache.org/downloads.html) to download Apache Spark package )
- Spark is configured with enough spark driver memory before starting the Spark Connect Server. Add the following configuration to the `./conf/spark-defaults.conf` in apache spark package.

```shell
spark.driver.memory 6g
```

- Spark Connect Server is running locally (refer to the [Quickstart: Spark Connect](https://spark.apache.org/docs/latest/api/python/getting_started/quickstart_connect.html) to launch spark server with spark connect)
- Install [Spark dependencies](https://spark.apache.org/docs/latest/api/python/getting_started/install.html#dependencies) in a dedicated python virtual environment.

1. Initialise a Spice app

   ```shell
   spice init spark_demo
   cd spark_demo
   ```

2. Start the Spice runtime

   ```shell
   >>> spice run
   Spice.ai runtime starting...
   2024-05-20T23:54:42.323695Z  INFO spiced: Metrics listening on 127.0.0.1:9090
   2024-05-20T23:54:42.325278Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
   2024-05-20T23:54:42.327243Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
   2024-05-20T23:54:42.327255Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
   ```

3. Create the Sample Dataset in Spark

   This Quickstarts use NYC taxi trip parquet data from [TLC Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page) to create a sample table in Spark.

   Download the NYC taxi trip parquet file using the following command

   ```shell
   wget https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet
   ```

   Change the `parquet_file_path` in python script to the absolute file path where `yellow_tripdata_2024-01.parquet` is located. Run the following python script in the python virtual environment that already have [Spark dependencies](https://spark.apache.org/docs/latest/api/python/getting_started/install.html#dependencies) downloaded.

   ```python
   from pyspark.sql import SparkSession
   from pyspark.sql import Row

   SparkSession.builder.master("local[*]").getOrCreate().stop()
   spark = SparkSession.builder.remote("sc://localhost:15002").getOrCreate()

   parquet_table_name = "nyc_taxi_trip"
   parquet_file_path = "/absolute/path/to/yellow_tripdata_2024-01.parquet"

   df = spark.read.format('parquet').options(header=True,inferSchema=True).load(parquet_file_path)
   df.write.option("path", f"./{parquet_table_name}").mode("overwrite").saveAsTable(parquet_table_name)
   ```

   Execute the following python code to confirm the creation of `nyc_taxi_trip` table

   ```python
   spark.sql("SHOW TABLES").show()

   +---------+-------------+-----------+
   |namespace|    tableName|isTemporary|
   +---------+-------------+-----------+
   |  default|nyc_taxi_trip|      false|
   +---------+-------------+-----------+
   ```

4. Configure a Spark dataset into the spicepod. Copy and paste the following `spicepod.yaml` configuration into your Spicepod.

   ```yaml
   version: v1beta1
   kind: Spicepod
   name: spark_demo
   datasets:
   - from: spark:nyc_taxi_trip
      name: nyc_taxi_trip
      params:
         spark_remote: sc://localhost:15002
   ```

5. Confirm that the runtime has loaded the new table (in the original terminal)

   ```shell
   2024-05-21T01:51:11.688868Z  INFO runtime: Registered dataset nyc_taxi_trip
   ```

6. Check the table exists from the Spice REPL

   ```shell
   >>> spice sql
   Welcome to the Spice.ai SQL REPL! Type 'help' for help.

   show tables; -- list available tables
   sql> show tables
   +---------------+------------+
   | table_name    | table_type |
   +---------------+------------+
   | nyc_taxi_trip | BASE TABLE |
   +---------------+------------+

   Time: 0.013910458 seconds. 1 rows.
   ```

   ```shell
   sql> describe nyc_taxi_trip
   +-----------------------+------------------------------+-------------+
   | column_name           | data_type                    | is_nullable |
   +-----------------------+------------------------------+-------------+
   | VendorID              | Int32                        | YES         |
   | tpep_pickup_datetime  | Timestamp(Microsecond, None) | YES         |
   | tpep_dropoff_datetime | Timestamp(Microsecond, None) | YES         |
   | passenger_count       | Int64                        | YES         |
   | trip_distance         | Float64                      | YES         |
   | RatecodeID            | Int64                        | YES         |
   | store_and_fwd_flag    | Utf8                         | YES         |
   | PULocationID          | Int32                        | YES         |
   | DOLocationID          | Int32                        | YES         |
   | payment_type          | Int64                        | YES         |
   | fare_amount           | Float64                      | YES         |
   | extra                 | Float64                      | YES         |
   | mta_tax               | Float64                      | YES         |
   | tip_amount            | Float64                      | YES         |
   | tolls_amount          | Float64                      | YES         |
   | improvement_surcharge | Float64                      | YES         |
   | total_amount          | Float64                      | YES         |
   | congestion_surcharge  | Float64                      | YES         |
   | Airport_fee           | Float64                      | YES         |
   +-----------------------+------------------------------+-------------+
   Time: 0.00544475 seconds. 19 rows.
   ```

7. Query against the Spark table. The spice runtime will make a network call to the Spark instance.

   ```shell
   >>> spice sql
   sql> SELECT avg(total_amount), avg(tip_amount), count(1), passenger_count FROM nyc_taxi_trip GROUP BY passenger_count ORDER BY passenger_count ASC;
   +---------------------------------+-------------------------------+-----------------+-----------------+
   | AVG(nyc_taxi_trip.total_amount) | AVG(nyc_taxi_trip.tip_amount) | COUNT(Int64(1)) | passenger_count |
   +---------------------------------+-------------------------------+-----------------+-----------------+
   | 25.327816939455595              | 3.0722599713968206            | 31465           | 0               |
   | 26.20523044547389               | 3.3712622884691075            | 2188739         | 1               |
   | 29.520659930934283              | 3.717130211328188             | 405103          | 2               |
   | 29.138309044288356              | 3.537045539216639             | 91262           | 3               |
   | 30.87726671027726               | 3.466037634201733             | 51974           | 4               |
   | 26.26912911120369               | 3.379707813526131             | 33506           | 5               |
   | 25.801183286359812              | 3.3440987786874916            | 22353           | 6               |
   | 57.735                          | 8.37                          | 8               | 7               |
   | 95.66803921568625               | 11.972156862745098            | 51              | 8               |
   | 18.45                           | 3.05                          | 1               | 9               |
   | 25.811736633327225              | 1.5459567500463327            | 140162          |                 |
   +---------------------------------+-------------------------------+-----------------+-----------------+

   Time: 0.522384708 seconds. 11 rows.
   ```
