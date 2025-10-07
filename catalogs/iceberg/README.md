# Iceberg Catalog Connector

The Iceberg Catalog Connector enables Spice to query Iceberg tables in an Iceberg catalog.

[![Watch the Spice.ai OSS Iceberg Catalog connector demo](https://img.youtube.com/vi/Akq39ml8LO0/hqdefault.jpg)](https://www.youtube.com/embed/Akq39ml8LO0)

## Prerequisites

- Access to an Iceberg catalog, or Docker to run an Iceberg catalog locally.
- Spice is installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation).

## Step 1. Create a new directory and initialize a Spicepod

```bash
mkdir iceberg-catalog-recipe
cd iceberg-catalog-recipe
spice init
```

## Step 2. Run the Docker container for the Iceberg catalog

In a separate terminal, clone the cookbook repository and run the Docker container for the Iceberg catalog.

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/catalogs/iceberg
docker compose up -d
```

## Step 3. Add the Iceberg Catalog Connector to your Spicepod

`spicepod.yaml`

```yaml
catalogs:
  - from: iceberg:http://localhost:8181/v1/namespaces
    name: ice
    params:
      iceberg_s3_endpoint: http://localhost:9000
      iceberg_s3_access_key_id: admin
      iceberg_s3_secret_access_key: password
      iceberg_s3_region: us-east-1
```

## Step 4. Run Spice

```bash
spice run
```

```bash
2025/01/27 11:08:36 INFO Checking for latest Spice runtime release...
2025/01/27 11:08:37 INFO Spice.ai runtime starting...
2025-01-27T19:08:37.494155Z  INFO runtime::init::dataset: No datasets were configured. If this is unexpected, check the Spicepod configuration.
2025-01-27T19:08:37.494905Z  INFO runtime::init::catalog: Registering catalog 'ice' for iceberg
2025-01-27T19:08:37.499162Z  INFO runtime::metrics_server: Spice Runtime Metrics listening on 127.0.0.1:9090
2025-01-27T19:08:37.499174Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2025-01-27T19:08:37.500689Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2025-01-27T19:08:37.503376Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2025-01-27T19:08:37.696469Z  INFO runtime::init::results_cache: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
2025-01-27T19:08:37.697178Z  INFO runtime::init::catalog: Registered catalog 'ice' with 1 schema and 8 tables
```

## Step 5. Query the Iceberg catalog

```bash
spice sql
sql> show tables;
+---------------+--------------+--------------+------------+
| table_catalog | table_schema | table_name   | table_type |
+---------------+--------------+--------------+------------+
| ice           | tpch_sf1     | lineitem     | BASE TABLE |
| ice           | tpch_sf1     | nation       | BASE TABLE |
| ice           | tpch_sf1     | orders       | BASE TABLE |
| ice           | tpch_sf1     | supplier     | BASE TABLE |
| ice           | tpch_sf1     | customer     | BASE TABLE |
| ice           | tpch_sf1     | partsupp     | BASE TABLE |
| ice           | tpch_sf1     | region       | BASE TABLE |
| ice           | tpch_sf1     | part         | BASE TABLE |
| spice         | runtime      | task_history | BASE TABLE |
| spice         | runtime      | metrics      | BASE TABLE |
+---------------+--------------+--------------+------------+
```

Run _Pricing Summary Report Query (Q1)_. More information about TPC-H and all the queries involved can be found in the official [TPC Benchmark H Standard Specification](https://www.tpc.org/tpc_documents_current_versions/pdf/tpc-h_v2.17.1.pdf).

```sql
select
  l_returnflag,
  l_linestatus,
  sum(l_quantity) as sum_qty,
  sum(l_extendedprice) as sum_base_price,
  sum(l_extendedprice * (1 - l_discount)) as sum_disc_price,
  sum(l_extendedprice * (1 - l_discount) * (1 + l_tax)) as sum_charge,
  avg(l_quantity) as avg_qty,
  avg(l_extendedprice) as avg_price,
  avg(l_discount) as avg_disc,
  count(*) as count_order
from
  ice.tpch_sf1.lineitem
where
  l_shipdate <= date '1998-12-01' - interval '110' day
group by
  l_returnflag,
  l_linestatus
order by
  l_returnflag,
  l_linestatus
;
```

Output:

```bash
+--------------+--------------+-------------+-----------------+-------------------+---------------------+-----------+--------------+----------+-------------+
| l_returnflag | l_linestatus | sum_qty     | sum_base_price  | sum_disc_price    | sum_charge          | avg_qty   | avg_price    | avg_disc | count_order |
+--------------+--------------+-------------+-----------------+-------------------+---------------------+-----------+--------------+----------+-------------+
| A            | F            | 37734107.00 | 56586554400.73  | 53758257134.8700  | 55909065222.827692  | 25.522005 | 38273.129734 | 0.049985 | 1478493     |
| N            | F            | 991417.00   | 1487504710.38   | 1413082168.0541   | 1469649223.194375   | 25.516471 | 38284.467760 | 0.050093 | 38854       |
| N            | O            | 73416597.00 | 110112303006.41 | 104608220776.3836 | 108796375788.183317 | 25.502437 | 38249.282778 | 0.049996 | 2878807     |
| R            | F            | 37719753.00 | 56568041380.90  | 53741292684.6040  | 55889619119.831932  | 25.505793 | 38250.854626 | 0.050009 | 1478870     |
+--------------+--------------+-------------+-----------------+-------------------+---------------------+-----------+--------------+----------+-------------+

Time: 0.186233833 seconds. 10 rows.
```

## Step 6. View the Iceberg tables in MinIO

Navigate to [http://localhost:9001](http://localhost:9001) and login with `admin` and `password`. View the `iceberg` bucket to see the created Iceberg tables.

## Step 7. Clean up

```bash
docker compose down --volumes --rmi local
```
