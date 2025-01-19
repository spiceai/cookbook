# Delta Lake Data Connector

Spice supports reading data directly from Delta Lake tables. This recipe will create an app that loads and queries a dataset from a Delta Lake table in AWS S3. It assumes:

- Spice is installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation).
- A Delta Lake table is configured and available in AWS S3.
- Basic AWS authentication is configured (with environment variable credentials `AWS_ACCESS_KEY_ID` & `AWS_SECRET_ACCESS_KEY`).

1. Initialize a Spice app

   ```shell
   spice init delta_lake_demo
   cd delta_lake_demo
   ```

2. Run the following command to set AWS secrets to access the Delta Lake table in S3.

   ```bash
   export AWS_ACCESS_KEY_ID=<your-aws-access-key-id>
   export AWS_SECRET_ACCESS_KEY=<your-aws-secret-access-key>
   ```

3. Configure the `spicepod.yaml` as following, replacing the `<s3://my_bucket/path/to/s3/delta/table/>` with the Delta Lake table path in S3.

   ```yaml
   version: v1
   kind: Spicepod
   name: delta_lake_demo
   datasets:
     - from: delta_lake:<s3://my_bucket/path/to/s3/delta/table/>
       name: delta_lake_table
       params:
         delta_lake_aws_access_key_id: ${secrets:AWS_ACCESS_KEY_ID}
         delta_lake_aws_secret_access_key: ${secrets:AWS_SECRET_ACCESS_KEY}
   ```

4. Start the Spice runtime, and the `delta_lake_table` dataset has been registered:

   ```shell
   >>> spice run
   2025/01/17 16:30:47 INFO Checking for latest Spice runtime release...
   2025/01/17 16:30:47 INFO Spice.ai runtime starting...
   2025-01-18T00:30:48.557502Z  INFO runtime::init::dataset: Initializing dataset delta_lake_table
   2025-01-18T00:30:48.561170Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
   2025-01-18T00:30:48.561514Z  INFO runtime::metrics_server: Spice Runtime Metrics listening on 127.0.0.1:9090
   2025-01-18T00:30:48.569153Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
   2025-01-18T00:30:48.574811Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
   2025-01-18T00:30:48.758689Z  INFO runtime::init::results_cache: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
   2025-01-18T00:30:49.116731Z  INFO runtime::init::dataset: Dataset delta_lake_table registered (delta_lake:s3:<s3://my_bucket/path/to/s3/delta/table/>), results cache enabled.
   ```

5. In another terminal window, run `spice sql` and check the `delta_lake_table` dataset exists from the Spice REPL:

    ```sql
    show tables;
    ```

   ```shell
   >>> spice sql
    Welcome to the Spice.ai SQL REPL! Type 'help' for help.

    show tables; -- list available tables
    sql> show tables;
    +---------------+--------------+------------------+------------+
    | table_catalog | table_schema | table_name       | table_type |
    +---------------+--------------+------------------+------------+
    | spice         | runtime      | task_history     | BASE TABLE |
    | spice         | runtime      | metrics          | BASE TABLE |
    | spice         | public       | delta_lake_table | BASE TABLE |
    +---------------+--------------+------------------+------------+

    Time: 0.004799292 seconds. 3 rows.
   ```

6. Query against the Delta Lake table.

   ```sql
    select * from delta_lake_table limit 10;
   ```

   ```shell
   sql> select * from delta_lake_table limit 10;
   +-----------+--------------------+---------------------------------------+-------------+-----------------+-----------+--------------+-------------------------------------------------------------------------------------------------------------------+
   | c_custkey | c_name             | c_address                             | c_nationkey | c_phone         | c_acctbal | c_mktsegment | c_comment                                                                                                         |
   +-----------+--------------------+---------------------------------------+-------------+-----------------+-----------+--------------+-------------------------------------------------------------------------------------------------------------------+
   | 1         | Customer#000000001 | j5JsirBM9PsCy0O1m                     | 15          | 25-989-741-2988 | 711.56    | BUILDING     | y final requests wake slyly quickly special accounts. blithely                                                    |
   | 2         | Customer#000000002 | 487LW1dovn6Q4dMVymKwwLE9OKf3QG        | 13          | 23-768-687-3665 | 121.65    | AUTOMOBILE   | y carefully regular foxes. slyly regular requests about the bli                                                   |
   | 3         | Customer#000000003 | fkRGN8nY4pkE                          | 1           | 11-719-748-3364 | 7498.12   | AUTOMOBILE   | fully. carefully silent instructions sleep alongside of the slyly regular asymptotes. quickly regular             |
   | 4         | Customer#000000004 | 4u58h fqkyE                           | 4           | 14-128-190-5944 | 2866.83   | MACHINERY    |  sublate. fluffily even instructions are about th                                                                 |
   | 5         | Customer#000000005 | hwBtxkoBF qSW4KrIk5U 2B1AU7H          | 3           | 13-750-942-6364 | 794.47    | HOUSEHOLD    | equests haggle furiously against the pending packa                                                                |
   | 6         | Customer#000000006 |  g1s,pzDenUEBW3O,2 pxu0f9n2g64rJrt5E  | 20          | 30-114-968-4951 | 7638.57   | AUTOMOBILE   |  quickly silent asymptotes are slyly regular excuses. instructions wake furiously? quickly bold courts p          |
   | 7         | Customer#000000007 | 8OkMVLQ1dK6Mbu6WG9 w4pLGQ n7MQ        | 18          | 28-190-982-9759 | 9561.95   | AUTOMOBILE   | ounts. ironic, regular accounts sleep. final requests haggle quickly after the                                    |
   | 8         | Customer#000000008 | j,pZ,Qp,qtFEo0r0c 92qobZtlhSuOqbE4JGV | 17          | 27-147-574-9335 | 6819.74   | BUILDING     | riously final excuses sublate quickly among the fluffily even foxes. quickly final packages haggle furiously furi |
   | 9         | Customer#000000009 | vgIql8H6zoyuLMFNdAMLyE7 H9            | 8           | 18-338-906-3675 | 8324.07   | FURNITURE    | ss pinto beans believe slyly quiet deposits-- doggedly bold packages boost. quickly ironic de                     |
   | 10        | Customer#000000010 | Vf mQ6Ug9Ucf5OKGYq fsaX AtfsO7,rwY    | 5           | 15-741-346-9870 | 2753.54   | HOUSEHOLD    | g quickly after the evenly bold                                                                                   |
   +-----------+--------------------+---------------------------------------+-------------+-----------------+-----------+--------------+-------------------------------------------------------------------------------------------------------------------+
   Time: 1.899808833 seconds. 10 rows.
   ```
