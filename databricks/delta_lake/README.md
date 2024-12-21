# Spice on Databricks (mode: delta_lake)

Spice can read data straight from a Databricks instance. This recipe will create an app, configure Databricks, load and query a dataset directly from Delta Lake Tables. It assumes:

- Spice is installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation).
- The Databricks instance is running against AWS S3 storage in `us-east-1`.
- Basic AWS authentication is configured (with environment variable credentials `AWS_ACCESS_KEY_ID` & `AWS_SECRET_ACCESS_KEY`).
- A Databricks personal access token is available (as the environment variable `DATABRICKS_TOKEN`).
- A table already exists in Databricks, called `spice_data.public.awesome_table`.

1. Initialize a Spice app

   ```shell
   spice init databricks_demo
   cd databricks_demo
   ```

1. In another terminal, working in the `databricks_demo` directory, configure Spice with the Databricks credentials

   ```shell
   spice login databricks \
       --token $DATABRICKS_TOKEN \
       --aws-access-key-id $AWS_ACCESS_KEY_ID \
       --aws-secret-access-key $AWS_SECRET_ACCESS_KEY \
       --aws-region us-east-1
   ```

   Executing `spice login` and successfully authenticating will create a `.env` file in the `databricks_demo` directory with the Databricks credentials.

1. Start the Spice runtime

   ```shell
   >>> spice run
   2024-03-27T05:27:52.696536Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
   2024-03-27T05:27:52.696543Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
   2024-03-27T05:27:52.696606Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
   ```

1. Configure a Databricks dataset into the spicepod. The table provided must be a reference to a table in the Databricks unity catalog.

   ```shell
   >>> spice dataset configure

   dataset name: (databricks_demo) my_table
   description: My Databricks table
   from: databricks:spice_data.public.awesome_table
   endpoint: https://sp3-07i73ce9d-a654.cloud.databricks.com/
   locally accelerate (y/n)? (y) n
   Saved datasets/my_table/dataset.yaml
   ```

1. Edit the dataset to add `mode: delta_lake` to the `params` section:

   ```yaml
   params:
     mode: delta_lake
     databricks_endpoint: <existing_endpoint>
   ```

1. Confirm that the runtime has registered the new table (in the original terminal)

   ```shell
   2024-03-27T05:27:54.051229Z  INFO runtime: Dataset my_table registered (databricks:spice_data.public.awesome_table), results cache enabled.
   ```

1. Check the table exists from the Spice REPL

   ```shell
   >>> spice sql
   Welcome to the Spice.ai SQL REPL! Type 'help' for help.

   show tables; -- list available tables
   sql> show tables;
   +---------------+--------------+---------------+------------+
   | table_catalog | table_schema | table_name    | table_type |
   +---------------+--------------+---------------+------------+
   | spice         | public       | my_table      | BASE TABLE |
   | spice         | runtime      | task_history  | BASE TABLE |
   | spice         | runtime      | metrics       | BASE TABLE |
   +---------------+--------------+---------------+------------+

   Time: 0.008540708 seconds
   ```

   ```shell
   sql> describe spice.public.my_table;
   +-----------------------+------------------------------+-------------+
   | column_name           | data_type                    | is_nullable |
   +-----------------------+------------------------------+-------------+
   | VendorID              | Int32                        | YES         |
   | tpep_pickup_datetime  | Timestamp(Microsecond, None) | YES         |
   | tpep_dropoff_datetime | Timestamp(Microsecond, None) | YES         |
   | passenger_count       | Int64                        | YES         |
   | trip_distance         | Float64                      | YES         |
   | RatecodeID            | Int64                        | YES         |
   | store_and_fwd_flag    | LargeUtf8                    | YES         |
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
   Time: 0.00507075 seconds
   ```

1. Query against the Databricks table. Since the table isn't accelerated, the spice runtime will make a network call to the object storage service.

   ```shell
   >>> spice sql
   sql> SELECT avg(total_amount), avg(tip_amount), count(1), passenger_count FROM my_table  GROUP BY passenger_count ORDER BY passenger_count ASC;
   +----------------------------+--------------------------+-----------------+-----------------+
   | AVG(my_table.total_amount) | AVG(my_table.tip_amount) | COUNT(Int64(1)) | passenger_count |
   +----------------------------+--------------------------+-----------------+-----------------+
   | 25.327816939456696         | 3.072259971396788        | 31465           | 0               |
   | 26.20523044549061          | 3.3712622884681065       | 2188739         | 1               |
   | 29.5206599309276           | 3.71713021132875         | 405103          | 2               |
   | 29.138309044289365         | 3.5370455392168942       | 91262           | 3               |
   | 30.877266710278            | 3.466037634201754        | 51974           | 4               |
   | 26.26912911120415          | 3.3797078135259517       | 33506           | 5               |
   | 25.801183286359887         | 3.344098778687425        | 22353           | 6               |
   | 57.735                     | 8.37                     | 8               | 7               |
   | 95.66803921568629          | 11.972156862745097       | 51              | 8               |
   | 18.45                      | 3.05                     | 1               | 9               |
   | 25.811736633327225         | 1.5459567500463327       | 140162          |                 |
   +----------------------------+--------------------------+-----------------+-----------------+

   Time: 6.56567 seconds
   ```

## (Optional): Accelerating Databricks

To improve the query performance, the Databricks dataset can be accelerated.

1. Edit the dataset, `my_table`.

   ```shell
   echo """acceleration:
     enabled: true""" >> datasets/my_table/dataset.yaml
   ```

2. The Spice runtime should be updated (i.e. `ACCELERATION=true`)

   ```shell
   >>> spice datasets

   FROM                                       NAME     REPLICATION ACCELERATION DEPENDSON STATUS
   databricks:spice_data.public.awesome_table my_table false       true                   Ready
   ```

3. Rerun the query

   ```shell
   >>> spice sql
   sql> select avg(total_amount), avg(tip_amount), count(1), passenger_count from my_table  group by passenger_count order by passenger_count asc;
   +----------------------------+--------------------------+-----------------+-----------------+
   | AVG(my_table.total_amount) | AVG(my_table.tip_amount) | COUNT(Int64(1)) | passenger_count |
   +----------------------------+--------------------------+-----------------+-----------------+
   | 25.32781693945653          | 3.072259971396793        | 31465           | 0               |
   | 26.205230445474996         | 3.3712622884680052       | 2188739         | 1               |
   | 29.520659930930304         | 3.7171302113290854       | 405103          | 2               |
   | 29.138309044290263         | 3.5370455392167615       | 91262           | 3               |
   | 30.877266710278306         | 3.466037634201712        | 51974           | 4               |
   | 26.269129111203988         | 3.3797078135259317       | 33506           | 5               |
   | 25.801183286359798         | 3.344098778687425        | 22353           | 6               |
   | 57.735                     | 8.37                     | 8               | 7               |
   | 95.66803921568626          | 11.972156862745097       | 51              | 8               |
   | 18.45                      | 3.05                     | 1               | 9               |
   | 25.81173663332435          | 1.545956750046378        | 140162          |                 |
   +----------------------------+--------------------------+-----------------+-----------------+

   Time: 0.0227835 seconds
   ```

Note: A dataset can be accelerated when configured by specifying yes (y) to `locally accelerate (y/n)?`.
