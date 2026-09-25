# Iceberg Catalog Connector

Works with `v1.0+`

The Iceberg Catalog Connector enables Spice to query and write to Iceberg tables in an Iceberg catalog.

> **Note:** The local Iceberg catalog in this recipe stores its data in [RustFS](https://github.com/rustfs/rustfs), an S3-compatible object store. Earlier versions used MinIO, whose open-source server and client are archived: the `minio/minio` and `minio/mc` images can no longer be pulled.

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
    # access: read_write
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
 INFO Spice.ai runtime starting...
2025-01-27T19:08:37.494155Z  INFO runtime: No datasets or catalogs were configured. If this is unexpected, check the Spicepod configuration.
2025-01-27T19:08:37.494905Z  INFO runtime::init::catalog: Registering catalog 'ice' for iceberg
2025-01-27T19:08:37.499174Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2025-01-27T19:08:37.500689Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2025-01-27T19:08:37.696469Z  INFO runtime::init::caching: Initialized sql results cache; max size: 128.00 MiB, item ttl: 1s, hashing algorithm: XXH3, encoding: none
2025-01-27T19:08:37.697178Z  INFO runtime::init::catalog: Registered catalog 'ice' with 1 schema and 8 tables
```

## Step 5. Query the Iceberg catalog

```bash
spice sql
sql> show tables;
+---------------+--------------+--------------+------------+
| table_catalog | table_schema |  table_name  | table_type |
|    varchar    |    varchar   |    varchar   |   varchar  |
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
+--------------+--------------+------------+--------------------+--------------------+--------------------+--------------------+--------------------+----------------------+-------------+
| l_returnflag | l_linestatus |   sum_qty  |   sum_base_price   |   sum_disc_price   |     sum_charge     |       avg_qty      |      avg_price     |       avg_disc       | count_order |
|    varchar   |    varchar   |   float64  |       float64      |       float64      |       float64      |       float64      |       float64      |        float64       |    int64    |
+--------------+--------------+------------+--------------------+--------------------+--------------------+--------------------+--------------------+----------------------+-------------+
| A            | F            | 37734107.0 | 56586554400.72999  | 53758257134.86979  | 55909065222.82766  | 25.522005853257337 | 38273.12973462167  | 0.049985295838460536 | 1478493     |
| N            | F            | 991417.0   | 1487504710.3799992 | 1413082168.0540988 | 1469649223.1943753 | 25.516471920522985 | 38284.46776084828  | 0.050093426674216755 | 38854       |
| N            | O            | 73416597.0 | 110112303006.41022 | 104608220776.38258 | 108796375788.18262 | 25.50243798906978  | 38249.282778043205 | 0.049996474234010685 | 2878807     |
| R            | F            | 37719753.0 | 56568041380.90029  | 53741292684.60385  | 55889619119.83172  | 25.50579361269077  | 38250.854626099856 | 0.050009405830189806 | 1478870     |
+--------------+--------------+------------+--------------------+--------------------+--------------------+--------------------+--------------------+----------------------+-------------+

Time: 0.4264595 seconds. 4 rows.
```

## Step 6. Write to Iceberg tables

To enable write operations to Iceberg tables, uncomment the `access: read_write` configuration and restart Spice

### 6.1. Update the Spicepod configuration

Edit the `spicepod.yaml` file to uncomment the access line:

```yaml
catalogs:
  - from: iceberg:http://localhost:8181/v1/namespaces
    access: read_write # Uncomment this line
    name: ice
    params:
      iceberg_s3_endpoint: http://localhost:9000
      iceberg_s3_access_key_id: admin
      iceberg_s3_secret_access_key: password
      iceberg_s3_region: us-east-1
```

### 6.2. Restart Spice

Stop the current Spice instance (Ctrl+C) and restart it:

```bash
spice run
```

### 6.3. Insert data into Iceberg tables

Now you can write data to the Iceberg tables using SQL [INSERT statements](https://spiceai.org/docs/reference/sql/dml#insert):

```bash
spice sql
```

Example: Insert a new region into the region table:

```sql
INSERT INTO ice.tpch_sf1.region (r_regionkey, r_name, r_comment)
VALUES (5, 'ANTARCTICA', 'A cold and remote region');
```

```bash
+--------+
|  count |
| uint64 |
+--------+
| 1      |
+--------+
```

Example: Insert a new nation into the nation table:

```sql
INSERT INTO ice.tpch_sf1.nation (n_nationkey, n_name, n_regionkey, n_comment)
VALUES (25, 'PENGUINIA', 5, 'A vibrant home for brave penguins in Antarctica');
```

```bash
+--------+
|  count |
| uint64 |
+--------+
| 1      |
+--------+
```

Verify the inserts by querying the tables:

```sql
SELECT * FROM ice.tpch_sf1.region WHERE r_regionkey = 5;
SELECT * FROM ice.tpch_sf1.nation WHERE n_nationkey = 25;
```

## Step 7. View the Iceberg tables in RustFS

Navigate to [http://localhost:9001/rustfs/console/](http://localhost:9001/rustfs/console/) and log in with `admin` and `password`. View the `iceberg` bucket to see the created Iceberg tables.

## Step 8. Clean up

```bash
docker compose down --volumes --rmi local
```
