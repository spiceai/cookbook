# Federated SQL Query

Works with `v1.0+`

Join data from S3 and PostgreSQL in a single SQL query, then accelerate both locally.

This recipe federates two sources:

- **S3**: 2,964,624 NYC yellow taxi trips from January 2024, stored as Parquet in the public `spiceai-demo-datasets` bucket. Each trip records its pickup zone as a numeric ID, `PULocationID`.
- **PostgreSQL**: the NYC TLC taxi zone lookup table, which maps all 265 zone IDs to zone and borough names. PostgreSQL runs locally in Docker as part of this recipe, so no external database, account, or credentials are required.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) is installed and running.
- Spice is installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation).

## Follow these steps to use Spice to federate SQL queries across data sources

**Step 1.** Clone the [github.com/spiceai/cookbook](https://github.com/spiceai/cookbook) repo and navigate to the `federation` directory.

```bash
git clone https://github.com/spiceai/cookbook
cd cookbook/federation
```

**Step 2.** Start the local PostgreSQL instance and load the taxi zones.

```bash
make
```

This runs `docker compose up --detach --wait`, which starts PostgreSQL 18 on host port `15432` (chosen so it doesn't clash with a PostgreSQL server already running on `5432`) and waits until it is ready. On first start, [`init/taxi_zones.sql`](./init/taxi_zones.sql) creates the `taxi_zones` table in the `taxi` database and loads it from the shared [`data/taxi_zone_lookup.csv`](../data/taxi_zone_lookup.csv) file. `make` then prints the row count:

```bash
Starting PostgreSQL container...
...
 Container federation-postgres-1 Healthy
 taxi_zones
------------
        265
(1 row)
```

**Step 3.** Store the PostgreSQL password. Ensure this command is run in the `federation` directory.

```bash
spice login postgres -p postgres
```

```bash
Successfully logged in to Postgres
```

This writes `SPICE_PG_PASS` to a local `.env` file. On startup, the runtime reads it and the PostgreSQL connector uses it as the `pg_pass` parameter.

**Step 4.** Review `spicepod.yaml`. It defines four datasets — the S3 trips and the PostgreSQL zones, each both federated and locally accelerated:

```yaml
version: v1
kind: Spicepod
name: federation

datasets:
  # NYC yellow taxi trips stored as Parquet in a public S3 bucket.
  # Federated to S3 on every query. s3_auth: public skips the AWS credential chain.
  - from: s3://spiceai-demo-datasets/taxi_trips/2024/
    name: taxi_trips
    description: NYC yellow taxi trips from January 2024, stored in S3
    params:
      file_format: parquet
      s3_auth: public

  # The same S3 dataset, accelerated locally in memory with Arrow.
  - from: s3://spiceai-demo-datasets/taxi_trips/2024/
    name: taxi_trips_accelerated
    description: NYC yellow taxi trips from January 2024, stored in S3, locally accelerated
    params:
      file_format: parquet
      s3_auth: public
    acceleration:
      enabled: true

  # NYC taxi zone lookup table in the local PostgreSQL instance.
  # Federated to PostgreSQL on every query. pg_pass is read from SPICE_PG_PASS in .env.
  - from: postgres:taxi_zones
    name: taxi_zones
    description: NYC taxi zones, stored in PostgreSQL
    params:
      pg_host: localhost
      pg_port: 15432
      pg_db: taxi
      pg_user: postgres
      pg_sslmode: disable

  # The same PostgreSQL table, accelerated locally in memory with Arrow.
  - from: postgres:taxi_zones
    name: taxi_zones_accelerated
    description: NYC taxi zones, stored in PostgreSQL, locally accelerated
    params:
      pg_host: localhost
      pg_port: 15432
      pg_db: taxi
      pg_user: postgres
      pg_sslmode: disable
    acceleration:
      enabled: true
```

**Step 5.** Start the Spice runtime.

```bash
spice run
```

The accelerated datasets load a local copy of their source on startup. `taxi_trips_accelerated` downloads the 97 MB Parquet file from S3 and loads all 2,964,624 trips into memory (about 400 MiB), which takes several seconds depending on your network. Wait for `Spice runtime is ready!` before querying.

```bash
2026-10-01T16:44:20.498472Z  INFO runtime::init::dataset: Loading datasets: 4 tasks dispatched, 0 skipped at accelerator init (of 4 total; localpod datasets may be chained).
2026-10-01T16:44:20.498489Z  INFO runtime::init::dataset: Dataset taxi_zones_accelerated initializing...
2026-10-01T16:44:20.498493Z  INFO runtime::init::dataset: Dataset taxi_trips initializing...
2026-10-01T16:44:20.498495Z  INFO runtime::init::dataset: Dataset taxi_zones initializing...
2026-10-01T16:44:20.498504Z  INFO runtime::init::dataset: Dataset taxi_trips_accelerated initializing...
2026-10-01T16:44:20.539682Z  INFO runtime::init::dataset: Dataset taxi_zones registered (postgres:taxi_zones), results cache enabled. duration_ms=0
2026-10-01T16:44:20.540439Z  INFO runtime::init::dataset: Dataset taxi_zones_accelerated registered (postgres:taxi_zones), acceleration (arrow), results cache enabled. duration_ms=0
2026-10-01T16:44:20.541813Z  INFO runtime_table::accelerated::refresh_task: Loading data for dataset taxi_zones_accelerated
2026-10-01T16:44:20.544007Z  INFO runtime_table::accelerated::refresh_task: Loaded 265 rows (30.46 kiB) for dataset taxi_zones_accelerated in 2ms.
2026-10-01T16:44:20.698053Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2026-10-01T16:44:20.698339Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2026-10-01T16:44:21.527428Z  INFO runtime::init::dataset: Dataset taxi_trips registered (s3://spiceai-demo-datasets/taxi_trips/2024/), results cache enabled. duration_ms=0
2026-10-01T16:44:21.535643Z  INFO runtime::init::dataset: Dataset taxi_trips_accelerated registered (s3://spiceai-demo-datasets/taxi_trips/2024/), acceleration (arrow), results cache enabled. duration_ms=0
2026-10-01T16:44:21.536846Z  INFO runtime_table::accelerated::refresh_task: Loading data for dataset taxi_trips_accelerated
2026-10-01T16:44:31.487572Z  INFO runtime_table::accelerated::refresh_task: Loaded 2,964,624 rows (399.38 MiB) for dataset taxi_trips_accelerated in 9s 950ms.
2026-10-01T16:44:31.546775Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

**Step 6.** In another terminal window, start the Spice SQL REPL and perform the following SQL queries:

```bash
spice sql
```

```sql
-- Query the federated PostgreSQL source
SELECT * FROM taxi_zones ORDER BY location_id LIMIT 5;
```

```output
+-------------+---------------+-------------------------+--------------+
| location_id |    borough    |           zone          | service_zone |
|    int32    |    varchar    |         varchar         |    varchar   |
+-------------+---------------+-------------------------+--------------+
| 1           | EWR           | Newark Airport          | EWR          |
| 2           | Queens        | Jamaica Bay             | Boro Zone    |
| 3           | Bronx         | Allerton/Pelham Gardens | Boro Zone    |
| 4           | Manhattan     | Alphabet City           | Yellow Zone  |
| 5           | Staten Island | Arden Heights           | Boro Zone    |
+-------------+---------------+-------------------------+--------------+

Time: 0.002984875 seconds. 5 rows.
```

```sql
-- Query the federated S3 source
SELECT COUNT(*) AS trips, COUNT(DISTINCT "PULocationID") AS pickup_zones FROM taxi_trips;
```

The trip data uses mixed-case column names, so quote them in SQL (`"PULocationID"`).

```output
+---------+--------------+
|  trips  | pickup_zones |
|  int64  |     int64    |
+---------+--------------+
| 2964624 | 260          |
+---------+--------------+

Time: 1.99011925 seconds. 1 rows.
```

```sql
-- Join trips in S3 with zone names in PostgreSQL: the 10 busiest pickup zones
SELECT z.zone,
       z.borough,
       COUNT(*) AS trips,
       ROUND(AVG(t.fare_amount), 2) AS avg_fare,
       ROUND(AVG(t.tip_amount), 2) AS avg_tip
FROM taxi_trips t
JOIN taxi_zones z ON t."PULocationID" = z.location_id
GROUP BY z.zone, z.borough
ORDER BY trips DESC
LIMIT 10;
```

Spice reads the trip columns from S3 and the zones from PostgreSQL, then joins them in a single query. Nothing is copied or loaded ahead of time.

```output
+------------------------------+-----------+--------+----------+---------+
|             zone             |  borough  |  trips | avg_fare | avg_tip |
|            varchar           |  varchar  |  int64 |  float64 | float64 |
+------------------------------+-----------+--------+----------+---------+
| JFK Airport                  | Queens    | 145240 | 59.4     | 8.86    |
| Midtown Center               | Manhattan | 143471 | 15.21    | 3.08    |
| Upper East Side South        | Manhattan | 142708 | 12.18    | 2.59    |
| Upper East Side North        | Manhattan | 136465 | 12.71    | 2.64    |
| Midtown East                 | Manhattan | 106717 | 14.79    | 3.02    |
| Times Sq/Theatre District    | Manhattan | 106324 | 17.54    | 3.3     |
| Penn Station/Madison Sq West | Manhattan | 104523 | 15.79    | 3.09    |
| Lincoln Square East          | Manhattan | 104080 | 13.43    | 2.79    |
| LaGuardia Airport            | Queens    | 89533  | 41.46    | 8.67    |
| Upper West Side South        | Manhattan | 88474  | 13.45    | 2.79    |
+------------------------------+-----------+--------+----------+---------+

Time: 2.705304958 seconds. 10 rows.
```

```sql
-- Run the same join against the locally accelerated datasets
SELECT z.zone,
       z.borough,
       COUNT(*) AS trips,
       ROUND(AVG(t.fare_amount), 2) AS avg_fare,
       ROUND(AVG(t.tip_amount), 2) AS avg_tip
FROM taxi_trips_accelerated t
JOIN taxi_zones_accelerated z ON t."PULocationID" = z.location_id
GROUP BY z.zone, z.borough
ORDER BY trips DESC
LIMIT 10;
```

The same rows are returned, served from the in-memory Arrow copies without contacting S3 or PostgreSQL. The query takes milliseconds instead of seconds:

```output
Time: 0.0255035 seconds. 10 rows.
```

Federated query times depend on network latency to S3, so expect them to vary between runs.

**Step 7.** Stop the Spice runtime with `Ctrl+C`. Then stop PostgreSQL and remove its container and volume.

```bash
make clean
```

**Next Steps**

- Add another data source to `spicepod.yaml` — for example a [MySQL](https://docs.spiceai.org/components/data-connectors/mysql) table or a [DuckDB](https://docs.spiceai.org/components/data-connectors/duckdb) database — and join it with `taxi_trips` and `taxi_zones` in the same query. See [Data Connectors](https://docs.spiceai.org/components/data-connectors) for the full list.
- Choose a different engine for the accelerated datasets, such as `engine: duckdb` or `engine: sqlite`. See [Data Accelerators](https://docs.spiceai.org/components/data-accelerators).
- Learn how Spice pushes queries down to each source in [Query Federation](https://docs.spiceai.org/features/query-federation).
