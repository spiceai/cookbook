# DuckLake Catalog Connector

> **Note:** The DuckLake connector is available in Spice v2.0 or later.

The DuckLake Catalog Connector enables Spice to automatically discover and query all schemas and tables in a [DuckLake](https://ducklake.select/) catalog — an open lakehouse format that stores metadata in a SQLite-compatible database and data in Parquet files.

## Prerequisites

- [DuckDB CLI](https://duckdb.org/docs/installation/) v1.3.0–v1.4.4 installed (to create a DuckLake catalog). DuckDB v1.5.x is **not** currently supported. Install the LTS version:
  ```bash
  curl https://install.duckdb.org | DUCKDB_VERSION=1.4.4 sh
  ```
- Spice v2.0 or later is installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation).

## Step 1. Create a new directory and initialize a Spicepod

```bash
mkdir ducklake-catalog-recipe
cd ducklake-catalog-recipe
spice init
```

## Step 2. Create a DuckLake catalog with sample data

Open DuckDB and create a DuckLake catalog with TPC-H sample data:

```bash
duckdb
```

```bash
SELECT version();
```

```bash
┌─────────────┐
│ "version"() │
│   varchar   │
├─────────────┤
│ v1.4.4      │
└─────────────┘
```

Install and load the DuckLake and TPC-H extensions, then create a catalog and populate it:

```sql
INSTALL ducklake;
LOAD ducklake;
INSTALL tpch;
LOAD tpch;

-- Generate TPC-H data in-memory (scale factor 0.01 for a quick demo)
CALL dbgen(sf = 0.01);

-- Create a DuckLake catalog with local metadata storage
ATTACH 'ducklake:metadata.ducklake' AS my_lakehouse;

-- Copy tables into DuckLake
CREATE TABLE my_lakehouse.main.customer AS SELECT * FROM customer;
CREATE TABLE my_lakehouse.main.lineitem AS SELECT * FROM lineitem;
CREATE TABLE my_lakehouse.main.nation AS SELECT * FROM nation;
CREATE TABLE my_lakehouse.main.orders AS SELECT * FROM orders;
CREATE TABLE my_lakehouse.main.part AS SELECT * FROM part;
CREATE TABLE my_lakehouse.main.partsupp AS SELECT * FROM partsupp;
CREATE TABLE my_lakehouse.main.region AS SELECT * FROM region;
CREATE TABLE my_lakehouse.main.supplier AS SELECT * FROM supplier;
```

Verify the tables were created:

```sql
SHOW ALL TABLES;
```

```text
┌──────────────┬─────────┬──────────┬──────────────────┬───────────────────────────────────────────────────────────────┬───────────┐
│   database   │ schema  │   name   │ column_names     │ column_types                                                │ temporary │
│   varchar    │ varchar │ varchar  │    varchar[]      │             varchar[]                                       │  boolean  │
├──────────────┼─────────┼──────────┼──────────────────┼───────────────────────────────────────────────────────────────┤───────────┤
│ my_lakehouse │ main    │ customer │ [c_custkey, ...]  │ [INTEGER, VARCHAR, ...]                                     │ false     │
│ my_lakehouse │ main    │ lineitem │ [l_orderkey, ...] │ [INTEGER, INTEGER, ...]                                     │ false     │
│ my_lakehouse │ main    │ nation   │ [n_nationkey, ...]│ [INTEGER, VARCHAR, ...]                                     │ false     │
│ my_lakehouse │ main    │ orders   │ [o_orderkey, ...] │ [INTEGER, INTEGER, ...]                                     │ false     │
│ my_lakehouse │ main    │ part     │ [p_partkey, ...]  │ [INTEGER, VARCHAR, ...]                                     │ false     │
│ my_lakehouse │ main    │ partsupp │ [ps_partkey, ...] │ [INTEGER, INTEGER, ...]                                     │ false     │
│ my_lakehouse │ main    │ region   │ [r_regionkey, ...]│ [INTEGER, VARCHAR, ...]                                     │ false     │
│ my_lakehouse │ main    │ supplier │ [s_suppkey, ...]  │ [INTEGER, VARCHAR, ...]                                     │ false     │
└──────────────┴─────────┴──────────┴──────────────────┴───────────────────────────────────────────────────────────────┴───────────┘
```

Exit DuckDB:

```sql
.exit
```

## Step 3. Configure the DuckLake Catalog Connector in your Spicepod

Edit `spicepod.yaml` to add the DuckLake catalog:

```yaml
version: v1
kind: Spicepod
name: ducklake-catalog-recipe

catalogs:
  - from: ducklake:metadata.ducklake
    name: my_lakehouse
```

## Step 4. Start the Spice runtime

```bash
spice run
```

Observe that Spice discovers all schemas and tables:

```bash
2026-03-02T10:00:00.000000Z  INFO runtime::init::catalog: Registering catalog 'my_lakehouse' for ducklake
2026-03-02T10:00:00.500000Z  INFO runtime::init::catalog: Registered catalog 'my_lakehouse' with 1 schema and 8 tables
```

## Step 5. Query the DuckLake catalog

In a new terminal, start the Spice SQL REPL:

```bash
spice sql
```

List all discovered tables:

```sql
SHOW TABLES;
```

```text
+---------------+--------------+------------+------------+
| table_catalog | table_schema | table_name | table_type |
+---------------+--------------+------------+------------+
| my_lakehouse  | main         | customer   | BASE TABLE |
| my_lakehouse  | main         | lineitem   | BASE TABLE |
| my_lakehouse  | main         | nation     | BASE TABLE |
| my_lakehouse  | main         | orders     | BASE TABLE |
| my_lakehouse  | main         | part       | BASE TABLE |
| my_lakehouse  | main         | partsupp   | BASE TABLE |
| my_lakehouse  | main         | region     | BASE TABLE |
| my_lakehouse  | main         | supplier   | BASE TABLE |
| spice         | runtime      | task_history | BASE TABLE |
| spice         | runtime      | metrics    | BASE TABLE |
+---------------+--------------+------------+------------+
```

Query the customer table:

```sql
SELECT c_custkey, c_name, c_mktsegment, c_acctbal
FROM my_lakehouse.main.customer
LIMIT 5;
```

```text
+-----------+--------------------+--------------+-----------+
| c_custkey |       c_name       | c_mktsegment | c_acctbal |
|   int64   |       varchar      |    varchar   |decimal(15,2)|
+-----------+--------------------+--------------+-----------+
| 1         | Customer#000000001 | BUILDING     | 711.56    |
| 2         | Customer#000000002 | AUTOMOBILE   | 121.65    |
| 3         | Customer#000000003 | AUTOMOBILE   | 7498.12   |
| 4         | Customer#000000004 | MACHINERY    | 2866.83   |
| 5         | Customer#000000005 | HOUSEHOLD    | 794.47    |
+-----------+--------------------+--------------+-----------+
```

Run a cross-table query:

```sql
SELECT n.n_name AS nation, COUNT(*) AS num_customers, ROUND(AVG(c.c_acctbal), 2) AS avg_balance
FROM my_lakehouse.main.customer c
JOIN my_lakehouse.main.nation n ON c.c_nationkey = n.n_nationkey
GROUP BY n.n_name
ORDER BY num_customers DESC
LIMIT 5;
```

```text
+---------+---------------+-------------+
|  nation | num_customers | avg_balance |
| varchar |     int64     |   float64   |
+---------+---------------+-------------+
| MOROCCO | 72            | 5484.47     |
| IRAN    | 72            | 4206.76     |
| CANADA  | 69            | 4116.12     |
| BRAZIL  | 68            | 3635.3      |
| JAPAN   | 67            | 4962.46     |
+---------+---------------+-------------+
```

## Step 6. Enable read-write access (optional)

To enable write operations, update the catalog configuration with `access: read_write`:

```yaml
version: v1
kind: Spicepod
name: ducklake-catalog-recipe

catalogs:
  - from: ducklake:metadata.ducklake
    name: my_lakehouse
    access: read_write
```

Restart Spice and insert data:

```bash
spice run
```

```bash
spice sql
```

```sql
INSERT INTO my_lakehouse.main.region (r_regionkey, r_name, r_comment)
VALUES (5, 'ANTARCTICA', 'A cold and remote region');
```

```text
+-------+
| count |
+-------+
| 1     |
+-------+
```

Verify the insert:

```sql
SELECT * FROM my_lakehouse.main.region ORDER BY r_regionkey;
```

## Using the DuckLake Data Connector

Instead of the catalog connector (which auto-discovers all tables), you can connect to specific tables using the DuckLake data connector:

```yaml
version: v1
kind: Spicepod
name: ducklake-data-connector-recipe

datasets:
  - from: ducklake:customer
    name: customer
    params:
      ducklake_connection_string: metadata.ducklake
  - from: ducklake:orders
    name: orders
    params:
      ducklake_connection_string: metadata.ducklake
```

This is useful when you only need specific tables or want to configure each dataset independently (e.g., with different acceleration settings).

## Using with Cloud Storage (S3)

DuckLake supports storing metadata and data on cloud storage. To use S3:

1. Ensure AWS credentials are available via environment variables, `~/.aws/credentials`, or an IAM instance profile.

2. Create a DuckLake catalog on S3 (via DuckDB CLI):

```sql
ATTACH 'ducklake:s3://my-bucket/lakehouse/metadata.ducklake' AS cloud_lakehouse;
```

3. Configure the Spice catalog:

```yaml
catalogs:
  - from: ducklake:s3://my-bucket/lakehouse/metadata.ducklake
    name: cloud_lakehouse
```

## Learn more

- [DuckLake website](https://ducklake.select/)
- [DuckLake Catalog Connector documentation](https://spiceai.org/docs/components/catalogs/ducklake)
- [DuckLake Data Connector documentation](https://spiceai.org/docs/components/data-connectors/ducklake)
- For using `spice sql`, see the [CLI reference](https://docs.spiceai.org/cli/reference/sql).
