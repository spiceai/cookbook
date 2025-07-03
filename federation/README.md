# Federated SQL Query

Fetch combined data from S3 Parquet, PostgreSQL, and Dremio in a single query.

## Follow these steps to use Spice to federate SQL queries across data sources

**Step 1.** Clone the [github.com/spiceai/cookbook](https://github.com/spiceai/cookbook) repo and navigate to the `federation` directory.

```bash
git clone https://github.com/spiceai/cookbook
cd cookbook/federation
```

**Step 2.** Initialize the Spice app. Use the default name by pressing enter when prompted.

```bash
spice init
name: (federation)?
```

**Step 3.** Log into the demo Dremio instance. Ensure this command is run in the `federation` directory.

```bash
spice login dremio -u demo -p demo1234
```

**Step 4.** Add the `spiceai/fed-demo` Spicepod from [spicerack.org](https://spicerack.org).

```bash
spice add spiceai/fed-demo
```

**Step 5.** Start the Spice runtime.

```bash
spice run
```

```bash
2025/01/27 11:36:41 INFO Checking for latest Spice runtime release...
2025/01/27 11:36:42 INFO Spice.ai runtime starting...
2025-01-27T19:36:43.199530Z  INFO runtime::init::dataset: Initializing dataset dremio_source
2025-01-27T19:36:43.199589Z  INFO runtime::init::dataset: Initializing dataset s3_source
2025-01-27T19:36:43.199709Z  INFO runtime::init::dataset: Initializing dataset dremio_source_accelerated
2025-01-27T19:36:43.199537Z  INFO runtime::init::dataset: Initializing dataset s3_source_accelerated
2025-01-27T19:36:43.201310Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2025-01-27T19:36:43.201625Z  INFO runtime::metrics_server: Spice Runtime Metrics listening on 127.0.0.1:9090
2025-01-27T19:36:43.205435Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2025-01-27T19:36:43.209349Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2025-01-27T19:36:43.401179Z  INFO runtime::init::results_cache: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
2025-01-27T19:36:43.624011Z  INFO runtime::init::dataset: Dataset dremio_source_accelerated registered (dremio:datasets.taxi_trips), acceleration (arrow), results cache enabled.
2025-01-27T19:36:43.625619Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset dremio_source_accelerated
2025-01-27T19:36:43.776300Z  INFO runtime::init::dataset: Dataset dremio_source registered (dremio:datasets.taxi_trips), results cache enabled.
2025-01-27T19:36:44.182533Z  INFO runtime::init::dataset: Dataset s3_source registered (s3://spiceai-demo-datasets/cleaned_sales_data.parquet), results cache enabled.
2025-01-27T19:36:44.203734Z  INFO runtime::init::dataset: Dataset s3_source_accelerated registered (s3://spiceai-demo-datasets/cleaned_sales_data.parquet), acceleration (sqlite), results cache enabled.
2025-01-27T19:36:44.205146Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset s3_source_accelerated
2025-01-27T19:36:45.138393Z  INFO runtime::accelerated_table::refresh_task: Loaded 2,823 rows (1010.18 kiB) for dataset s3_source_accelerated in 933ms.
2025-01-27T19:36:46.313896Z  INFO runtime::accelerated_table::refresh_task: Loaded 100,000 rows (27.91 MiB) for dataset dremio_source_accelerated in 2s 688ms.
```

**Step 6.** In another terminal window, start the Spice SQL REPL and perform the following SQL queries:

```bash
spice sql
```

```sql
-- Query the federated S3 source
select * from s3_source;
```

```output
+--------------+------------------+------------+-------------------+---------+---------------------+---------+---------+-------+------+--------------+------+--------------+--------------------+------------------+-------------------------------+---------------+-------+-------+-------------+---------+-----------+-------------------+--------------------+-----------+
| order_number | quantity_ordered | price_each | order_line_number | sales   | order_date          | status  | quarter | month | year | product_line | msrp | product_code | customer_name      | phone            | address_line1                 | address_line2 | city  | state | postal_code | country | territory | contact_last_name | contact_first_name | deal_size |
+--------------+------------------+------------+-------------------+---------+---------------------+---------+---------+-------+------+--------------+------+--------------+--------------------+------------------+-------------------------------+---------------+-------+-------+-------------+---------+-----------+-------------------+--------------------+-----------+
| 10107        | 30               | 95.7       | 2                 | 2871.0  | 2003-02-24T00:00:00 | Shipped | 1       | 2     | 2003 | Motorcycles  | 95   | S10_1678     | Land of Toys Inc.  | 2125557818       | 897 Long Airport Avenue       |               | NYC   | NY    | 10022       | USA     |           | Yu                | Kwai               | Small     |
| 10121        | 34               | 81.35      | 5                 | 2765.9  | 2003-05-07T00:00:00 | Shipped | 2       | 5     | 2003 | Motorcycles  | 95   | S10_1678     | Reims Collectables | 26.47.1555       | 59 rue de l'Abbaye            |               | Reims |       | 51100       | France  | EMEA      | Henriot           | Paul               | Small     |
| 10134        | 41               | 94.74      | 2                 | 3884.34 | 2003-07-01T00:00:00 | Shipped | 3       | 7     | 2003 | Motorcycles  | 95   | S10_1678     | Lyon Souveniers    | +33 1 46 62 7555 | 27 rue du Colonel Pierre Avia |               | Paris |       | 75508       | France  | EMEA      | Da Cunha          | Daniel             | Medium    |
...
+--------------+------------------+------------+-------------------+---------+---------------------+---------+---------+-------+------+--------------+------+--------------+--------------------+------------------+-------------------------------+---------------+-------+-------+-------------+---------+-----------+-------------------+--------------------+-----------+

Time: 0.876282458 seconds. 500/2823 rows displayed.
```

```sql
-- Query the accelerated S3 source
select * from s3_source_accelerated;
```

Output:

```shell
+--------------+------------------+------------+-------------------+---------+---------------------+---------+---------+-------+------+--------------+------+--------------+--------------------+------------------+-------------------------------+---------------+-------+-------+-------------+---------+-----------+-------------------+--------------------+-----------+
| order_number | quantity_ordered | price_each | order_line_number | sales   | order_date          | status  | quarter | month | year | product_line | msrp | product_code | customer_name      | phone            | address_line1                 | address_line2 | city  | state | postal_code | country | territory | contact_last_name | contact_first_name | deal_size |
+--------------+------------------+------------+-------------------+---------+---------------------+---------+---------+-------+------+--------------+------+--------------+--------------------+------------------+-------------------------------+---------------+-------+-------+-------------+---------+-----------+-------------------+--------------------+-----------+
| 10107        | 30               | 95.7       | 2                 | 2871.0  | 2003-02-24T00:00:00 | Shipped | 1       | 2     | 2003 | Motorcycles  | 95   | S10_1678     | Land of Toys Inc.  | 2125557818       | 897 Long Airport Avenue       |               | NYC   | NY    | 10022       | USA     |           | Yu                | Kwai               | Small     |
| 10121        | 34               | 81.35      | 5                 | 2765.9  | 2003-05-07T00:00:00 | Shipped | 2       | 5     | 2003 | Motorcycles  | 95   | S10_1678     | Reims Collectables | 26.47.1555       | 59 rue de l'Abbaye            |               | Reims |       | 51100       | France  | EMEA      | Henriot           | Paul               | Small     |
| 10134        | 41               | 94.74      | 2                 | 3884.34 | 2003-07-01T00:00:00 | Shipped | 3       | 7     | 2003 | Motorcycles  | 95   | S10_1678     | Lyon Souveniers    | +33 1 46 62 7555 | 27 rue du Colonel Pierre Avia |               | Paris |       | 75508       | France  | EMEA      | Da Cunha          | Daniel             | Medium    |
...
+--------------+------------------+------------+-------------------+---------+---------------------+---------+---------+-------+------+--------------+------+--------------+--------------------+------------------+-------------------------------+---------------+-------+-------+-------------+---------+-----------+-------------------+--------------------+-----------+

Time: 0.024679208 seconds. 500/2823 rows displayed.
```

```sql
-- Query the federated Dremio source
select * from dremio_source;
```

Output:

```shell
+---------------------+-----------------+------------------+-------------+------------+--------------+
| pickup_datetime     | passenger_count | trip_distance_mi | fare_amount | tip_amount | total_amount |
+---------------------+-----------------+------------------+-------------+------------+--------------+
| 2013-08-22T08:24:12 | 1               | 1.1              | 7.5         | 0.0        | 8.0          |
| 2013-08-21T12:40:46 | 1               | 6.1              | 23.0        | 0.0        | 23.5         |
| 2013-08-24T00:40:17 | 2               | 0.6              | 4.5         | 0.0        | 5.5          |
...
+---------------------+-----------------+------------------+-------------+------------+--------------+

Time: 2.671361917 seconds. 500/100000 rows displayed.
```

```sql
-- Query the accelerated Dremio source
select * from dremio_source_accelerated;
```

Output:

```shell
+---------------------+-----------------+------------------+-------------+------------+--------------+
| pickup_datetime     | passenger_count | trip_distance_mi | fare_amount | tip_amount | total_amount |
+---------------------+-----------------+------------------+-------------+------------+--------------+
| 2013-08-22T08:24:12 | 1               | 1.1              | 7.5         | 0.0        | 8.0          |
| 2013-08-21T12:40:46 | 1               | 6.1              | 23.0        | 0.0        | 23.5         |
| 2013-08-24T00:40:17 | 2               | 0.6              | 4.5         | 0.0        | 5.5          |
...
+---------------------+-----------------+------------------+-------------+------------+--------------+

Time: 0.015666208 seconds. 500/100000 rows displayed.
```

```sql
-- Perform an aggregation query that combines data from S3 and Dremio
WITH all_sales AS (
    SELECT sales FROM s3_source_accelerated
    UNION ALL
    select fare_amount+tip_amount as sales from dremio_source_accelerated
)

SELECT SUM(sales) as total_sales,
       COUNT(*) AS total_transactions,
       MAX(sales) AS max_sale,
       AVG(sales) AS avg_sale
FROM all_sales;
```

Output:

```shell
+--------------------+--------------------+----------+--------------------+
| total_sales        | total_transactions | max_sale | avg_sale           |
+--------------------+--------------------+----------+--------------------+
| 11501140.079999998 | 102823             | 14082.8  | 111.85376890384445 |
+--------------------+--------------------+----------+--------------------+

Time: 0.009526666 seconds. 1 rows.
```
