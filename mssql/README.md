# MSSQL (Microsoft SQL Server) Connector

This recipe is meant to get you up and running with Spice's MSSQL data connector. It runs two instances of MSSQL server: 2019 and 2022. Both
instances are accessible from within Spice to demonstrate that you can query across multiple servers.

## Pre-requisites

- Spice is installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation).
- Docker running on your system

## Steps

1. Clone the Spice cookbook repository and navigate to the `mssql` directory:

    ```shell
    git clone https://github.com/spiceai/cookbook.git
    cd cookbook/mssql
    ```

2. Start the MSSQL instances using `docker compose up -d`. In a production scenario you'd want to use [secrets](https://docs.spiceai.org/components/secret-stores) to protect your secrets
3. Start up Spice using `spice run`

    ```shell
    Checking for latest Spice runtime release...
    Spice.ai runtime starting...
    2024-09-23T19:43:29.074453Z  INFO runtime::metrics_server: Spice Runtime Metrics listening on 127.0.0.1:9090
    2024-09-23T19:43:29.074284Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
    2024-09-23T19:43:29.075193Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
    2024-09-23T19:43:29.091737Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
    2024-09-23T19:43:29.274085Z  INFO runtime: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
    2024-09-23T19:43:29.280949Z  WARN tiberius::client::tls_stream::rustls_tls_stream: Trusting the server certificate without validation.
    2024-09-23T19:43:29.281023Z  WARN tiberius::client::tls_stream::rustls_tls_stream: Trusting the server certificate without validation.
    2024-09-23T19:43:29.281987Z  WARN tiberius::client::tls_stream::rustls_tls_stream: Trusting the server certificate without validation.
    2024-09-23T19:43:29.296410Z  INFO runtime: Dataset sales.customer registered (mssql:Sales.Customer), acceleration (arrow), results cache enabled.
    2024-09-23T19:43:29.296456Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset sales.customer
    2024-09-23T19:43:29.298284Z  INFO runtime: Dataset sales.customer2022 registered (mssql:Sales.Customer), acceleration (arrow), results cache enabled.
    2024-09-23T19:43:29.298383Z  INFO runtime: Dataset sales.salesorderheader registered (mssql:Sales.SalesOrderHeader), acceleration (arrow), results cache enabled.
    2024-09-23T19:43:29.299097Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset sales.salesorderheader
    2024-09-23T19:43:29.299104Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset sales.customer2022
    2024-09-23T19:43:29.374935Z  INFO runtime::accelerated_table::refresh_task: Loaded 19,820 rows (2.20 MiB) for dataset sales.customer in 78ms.
    2024-09-23T19:43:29.387697Z  INFO runtime::accelerated_table::refresh_task: Loaded 19,820 rows (2.20 MiB) for dataset sales.customer2022 in 88ms.
    2024-09-23T19:43:29.394271Z  INFO runtime::accelerated_table::refresh_task: Loaded 31,465 rows (7.19 MiB) for dataset sales.salesorderheader in 95ms.
    ```

4. In another shell, fire up the Spice SQL REPL using `spice sql`

    ```shell
    Welcome to the Spice.ai SQL REPL! Type 'help' for help.

    show tables; -- list available tables
    ```

## Example Queries

### Verify that the row counts in the 2019 server matches the 2022 server

```sql
SELECT
    count_2019,
    count_2022,
    count_2019=count_2022 AS equal
FROM (
    SELECT
        COUNT(*) AS count_2019,
        MAX(count_2022) AS count_2022
    FROM Sales.Customer
    JOIN (
        SELECT
            COUNT(*) AS count_2022
        FROM Sales.Customer2022
    ) ON 1=1
);
```

Output:

```shell
+------------+------------+-------+
| count_2019 | count_2022 | equal |
+------------+------------+-------+
| 19820      | 19820      | true  |
+------------+------------+-------+
```

### Order information per customer

```sql
SELECT c."CustomerID",
    MAX(CAST("OrderDate" AS DATE)) AS LatestOrderDate,
    ROUND(AVG("TotalDue"), 2) AS AverageOrderValue,
    COUNT("SalesOrderID") AS TotalNumberOfOrders
FROM Sales.Customer c
LEFT OUTER JOIN Sales.SalesOrderHeader soh
    ON c."CustomerID" = soh."CustomerID"
GROUP BY c."CustomerID"
ORDER BY TotalNumberOfOrders DESC
LIMIT 10;
```

Output:

```shell
+------------+-----------------+-------------------+---------------------+
| CustomerID | latestorderdate | averageordervalue | totalnumberoforders |
+------------+-----------------+-------------------+---------------------+
| 11176      | 2014-06-29      | 52.09             | 28                  |
| 11091      | 2014-06-10      | 46.94             | 28                  |
| 11330      | 2014-06-24      | 46.51             | 27                  |
| 11300      | 2014-06-02      | 61.41             | 27                  |
| 11711      | 2014-06-28      | 45.17             | 27                  |
| 11331      | 2014-06-26      | 54.4              | 27                  |
| 11287      | 2014-06-30      | 47.76             | 27                  |
| 11185      | 2014-06-28      | 66.15             | 27                  |
| 11276      | 2014-06-24      | 40.45             | 27                  |
| 11200      | 2014-06-22      | 59.89             | 27                  |
+------------+-----------------+-------------------+---------------------+
```
