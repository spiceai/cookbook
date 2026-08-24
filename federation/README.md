# Federated SQL Query

Works with `v1.0+`

Fetch combined data from S3 Parquet and Dremio in a single query.

Dremio runs locally in Docker as part of this recipe, so no external Dremio instance, account, or credentials are required.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) is installed and running, with at least 4 GB of memory available to it.
- Spice is installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation).

## Follow these steps to use Spice to federate SQL queries across data sources

**Step 1.** Clone the [github.com/spiceai/cookbook](https://github.com/spiceai/cookbook) repo and navigate to the `federation` directory.

```bash
git clone https://github.com/spiceai/cookbook
cd cookbook/federation
```

**Step 2.** Start the local Dremio instance and load the sample dataset.

```bash
make
```

The first run pulls the `dremio/dremio-oss` image (~1.1 GB), so it takes a few minutes; subsequent runs start in seconds.

This runs `docker compose up` followed by `./setup-dremio.sh`, which:

1. Creates the first (admin) Dremio user, `demo` / `demo1234`.
2. Adds the cookbook `data` directory (mounted into the container at `/opt/dremio/datasets`) as a Dremio NAS source named `datasets`.
3. Promotes `data/taxi_trips` to the physical dataset `datasets.taxi_trips` — 100,000 NYC yellow taxi trips from January 2024.

```bash
Starting Dremio container...
 Container federation-dremio-1  Started
Waiting for Dremio at http://localhost:9047 (first start takes 1-2 minutes)...
Creating the first user 'demo'...
Adding the 'datasets' NAS source...
Promoting datasets.taxi_trips to a physical dataset...

Dremio is ready:
  UI:           http://localhost:9047 (demo / demo1234)
  Arrow Flight: grpc://localhost:32010
  Dataset:      datasets.taxi_trips
```

**Step 3.** Log into the local Dremio instance. Ensure this command is run in the `federation` directory.

```bash
spice login dremio -u demo -p demo1234
```

This writes `SPICE_DREMIO_USERNAME` and `SPICE_DREMIO_PASSWORD` to a local `.env` file, which the runtime reads on startup.

**Step 4.** Review `spicepod.yaml`. It defines four datasets — the same Dremio dataset and the same public S3 Parquet file, each both federated and locally accelerated:

```yaml
version: v1
kind: Spicepod
name: federation

datasets:
  # Federated to the local Dremio instance on every query.
  - from: dremio:datasets.taxi_trips
    name: dremio_source
    description: taxi trips in the local Dremio instance
    params:
      dremio_endpoint: grpc://localhost:32010

  # The same Dremio dataset, accelerated locally with Arrow.
  - from: dremio:datasets.taxi_trips
    name: dremio_source_accelerated
    description: taxi trips in the local Dremio instance, locally accelerated
    params:
      dremio_endpoint: grpc://localhost:32010
    acceleration:
      enabled: true

  # Federated to S3 on every query.
  - from: s3://spiceai-demo-datasets/cleaned_sales_data.parquet
    name: s3_source
    description: sales data in a public S3 bucket

  # The same S3 dataset, accelerated locally with SQLite.
  - from: s3://spiceai-demo-datasets/cleaned_sales_data.parquet
    name: s3_source_accelerated
    description: sales data in a public S3 bucket, locally accelerated
    acceleration:
      enabled: true
      engine: sqlite
```

**Step 5.** Start the Spice runtime.

```bash
spice run
```

```bash
2026-08-21T16:39:30.535480Z  INFO runtime::init::dataset: Loading datasets: 4 tasks dispatched, 0 skipped at accelerator init (of 4 total; localpod datasets may be chained).
2026-08-21T16:39:30.535492Z  INFO runtime::init::dataset: Dataset s3_source_accelerated initializing...
2026-08-21T16:39:30.535504Z  INFO runtime::init::dataset: Dataset s3_source initializing...
2026-08-21T16:39:30.535485Z  INFO runtime::init::dataset: Dataset dremio_source initializing...
2026-08-21T16:39:30.535537Z  INFO runtime::init::dataset: Dataset dremio_source_accelerated initializing...
2026-08-21T16:39:30.734622Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2026-08-21T16:39:30.734882Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2026-08-21T16:39:30.868087Z  INFO runtime::init::dataset: Dataset dremio_source registered (dremio:datasets.taxi_trips), results cache enabled. duration_ms=0
2026-08-21T16:39:30.868362Z  INFO runtime::init::dataset: Dataset dremio_source_accelerated registered (dremio:datasets.taxi_trips), acceleration (arrow), results cache enabled. duration_ms=0
2026-08-21T16:39:30.869566Z  INFO runtime_table::accelerated::refresh_task: Loading data for dataset dremio_source_accelerated
2026-08-21T16:39:31.274951Z  INFO runtime_table::accelerated::refresh_task: Loaded 100,000 rows (27.91 MiB) for dataset dremio_source_accelerated in 405ms.
2026-08-21T16:39:33.633663Z  INFO runtime::init::dataset: Dataset s3_source registered (s3://spiceai-demo-datasets/cleaned_sales_data.parquet), results cache enabled. duration_ms=0
2026-08-21T16:39:33.646948Z  INFO runtime::init::dataset: Dataset s3_source_accelerated registered (s3://spiceai-demo-datasets/cleaned_sales_data.parquet), acceleration (sqlite), results cache enabled. duration_ms=13
2026-08-21T16:39:33.736240Z  INFO runtime_table::accelerated::refresh_task: Loading data for dataset s3_source_accelerated
2026-08-21T16:39:34.425952Z  INFO runtime_table::accelerated::refresh_task: Loaded 2,823 rows (1010.18 kiB) for dataset s3_source_accelerated in 689ms.
2026-08-21T16:39:34.463210Z  INFO runtime: All components are loaded. Spice runtime is ready!
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
+--------------+------------------+------------+-------------------+---------+---------------------+------------+---------+-------+-------+------------------+-------+--------------+--------------------+-------------------+--------------------------------------------+---------------+----------------+---------------+-------------+-------------+-----------+-------------------+--------------------+-----------+
| order_number | quantity_ordered | price_each | order_line_number |  sales  |      order_date     |   status   | quarter | month |  year |   product_line   |  msrp | product_code |    customer_name   |       phone       |                address_line1               | address_line2 |      city      |     state     | postal_code |   country   | territory | contact_last_name | contact_first_name | deal_size |
|     int64    |       int64      |   float64  |       int64       | float64 |    timestamp[us]    |   varchar  |  int64  | int64 | int64 |      varchar     | int64 |    varchar   |       varchar      |      varchar      |                   varchar                  |    varchar    |     varchar    |    varchar    |   varchar   |   varchar   |  varchar  |      varchar      |       varchar      |  varchar  |
+--------------+------------------+------------+-------------------+---------+---------------------+------------+---------+-------+-------+------------------+-------+--------------+--------------------+-------------------+--------------------------------------------+---------------+----------------+---------------+-------------+-------------+-----------+-------------------+--------------------+-----------+
| 10107        | 30               | 95.7       | 2                 | 2871.0  | 2003-02-24T00:00:00 | Shipped    | 1       | 2     | 2003  | Motorcycles      | 95    | S10_1678     | Land of Toys Inc.  | 2125557818        | 897 Long Airport Avenue                    |               | NYC            | NY            | 10022       | USA         |           | Yu                | Kwai               | Small     |
| 10121        | 34               | 81.35      | 5                 | 2765.9  | 2003-05-07T00:00:00 | Shipped    | 2       | 5     | 2003  | Motorcycles      | 95    | S10_1678     | Reims Collectables | 26.47.1555        | 59 rue de l'Abbaye                         |               | Reims          |               | 51100       | France      | EMEA      | Henriot           | Paul               | Small     |
...
+--------------+------------------+------------+-------------------+---------+---------------------+------------+---------+-------+-------+------------------+-------+--------------+--------------------+-------------------+--------------------------------------------+---------------+----------------+---------------+-------------+-------------+-----------+-------------------+--------------------+-----------+

Time: 0.63591475 seconds. 500/2823 rows displayed.
```

```sql
-- Query the accelerated S3 source
select * from s3_source_accelerated;
```

The same rows are returned, served from the local SQLite acceleration:

```output
Time: 0.010731209 seconds. 500/2823 rows displayed.
```

```sql
-- Query the federated Dremio source
select * from dremio_source;
```

Output:

```output
+---------------------+-----------------+------------------+-------------+------------+--------------+
|   pickup_datetime   | passenger_count | trip_distance_mi | fare_amount | tip_amount | total_amount |
|    timestamp[ms]    |      int64      |      float64     |   float64   |   float64  |    float64   |
+---------------------+-----------------+------------------+-------------+------------+--------------+
| 2024-01-01T00:01:39 | 1               | 2.59             | 47.1        | 0.0        | 52.1         |
| 2024-01-01T00:02:35 | 1               | 1.36             | 10.0        | 3.0        | 18.0         |
...
+---------------------+-----------------+------------------+-------------+------------+--------------+

Time: 0.198277334 seconds. 500/100000 rows displayed.
```

```sql
-- Query the accelerated Dremio source
select * from dremio_source_accelerated;
```

Output:

```output
+---------------------+-----------------+------------------+-------------+------------+--------------+
|   pickup_datetime   | passenger_count | trip_distance_mi | fare_amount | tip_amount | total_amount |
|    timestamp[ms]    |      int64      |      float64     |   float64   |   float64  |    float64   |
+---------------------+-----------------+------------------+-------------+------------+--------------+
| 2024-01-20T22:01:01 | 1               | 2.45             | 14.9        | 4.97       | 24.87        |
| 2024-01-20T22:01:18 | 1               | 3.36             | 19.8        | 4.96       | 29.76        |
...
+---------------------+-----------------+------------------+-------------+------------+--------------+

Time: 0.003680042 seconds. 500/100000 rows displayed.
```

Rows are returned in a different order than `dremio_source` because the accelerated copy is scanned locally; add an `ORDER BY` for a deterministic order.

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

```output
+--------------------+--------------------+----------+--------------------+
|     total_sales    | total_transactions | max_sale |      avg_sale      |
|       float64      |        int64       |  float64 |       float64      |
+--------------------+--------------------+----------+--------------------+
| 12228778.539999995 | 102823             | 14082.8  | 118.93038075138826 |
+--------------------+--------------------+----------+--------------------+

Time: 0.016817 seconds. 1 rows.
```

The trailing digits of `total_sales` and `avg_sale` can vary between runs — floating-point aggregation depends on the order partitions are combined in.

**Step 7.** Stop Dremio and remove its container and volume.

```bash
make clean
```

**Next Steps**

Add another data source to `spicepod.yaml` — for example a [PostgreSQL](https://docs.spiceai.org/components/data-connectors/postgres) table or a [MySQL](https://docs.spiceai.org/components/data-connectors/mysql) table — and join it with `dremio_source` and `s3_source` in a single query. See [Data Connectors](https://docs.spiceai.org/components/data-connectors) for the full list.
