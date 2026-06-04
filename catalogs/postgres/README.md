# PostgreSQL Catalog Connector

Works with `v1.0+`

The PostgreSQL Catalog Connector enables Spice to automatically discover and query all schemas and tables in a PostgreSQL database. This recipe demonstrates the connector using the standard TPC-H benchmark dataset (Scale Factor 1) with full foreign key constraints defined between tables.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed
- Spice installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation)

## Step 1. Start the PostgreSQL database

Clone the cookbook repository and start the database using Docker Compose. The `postgres-init` container downloads the TPC-H SF1 parquet files and loads them into PostgreSQL, creating all tables with primary keys and foreign keys.

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/catalogs/postgres
docker compose up -d
```

Wait for the init container to finish loading data (it downloads ~700 MB of parquet files on first build):

```bash
docker compose logs -f postgres-init
```

You should see:

```
tpch-postgres-init  | PostgreSQL is ready.
tpch-postgres-init  | Creating schema ...
tpch-postgres-init  | Schema created.
tpch-postgres-init  |
tpch-postgres-init  | Loading region ...
tpch-postgres-init  |   Reading /data/tpch_sf1/region.parquet ...
tpch-postgres-init  |   5 rows, schema: ...
tpch-postgres-init  |   Loaded 5 rows into region.
...
tpch-postgres-init  | All TPC-H tables loaded successfully!
```

The TPC-H schema includes the following foreign key relationships:

| Table      | Foreign Key Column(s)          | References                      |
|------------|--------------------------------|---------------------------------|
| `nation`   | `n_regionkey`                  | `region(r_regionkey)`           |
| `supplier` | `s_nationkey`                  | `nation(n_nationkey)`           |
| `customer` | `c_nationkey`                  | `nation(n_nationkey)`           |
| `partsupp` | `ps_partkey`                   | `part(p_partkey)`               |
| `partsupp` | `ps_suppkey`                   | `supplier(s_suppkey)`           |
| `orders`   | `o_custkey`                    | `customer(c_custkey)`           |
| `lineitem` | `l_orderkey`                   | `orders(o_orderkey)`            |
| `lineitem` | `(l_partkey, l_suppkey)`       | `partsupp(ps_partkey, ps_suppkey)` |

## Step 2. Create a new directory and initialize a Spicepod

```bash
mkdir postgres-catalog-recipe
cd postgres-catalog-recipe
spice init
```

## Step 3. Configure credentials

Create a `.env` file with the database credentials:

```bash
echo "PG_USER=postgres" > .env
```

## Step 4. Add the PostgreSQL Catalog Connector to `spicepod.yaml`

```yaml
version: v1
kind: Spicepod
name: postgres-catalog-recipe

catalogs:
  - from: pg
    name: pg
    params:
      pg_host: localhost
      pg_port: 5432
      pg_db: tpch
      pg_user: ${secrets:PG_USER}
      pg_sslmode: disable
```

## Step 5. Start the Spice runtime

```bash
spice run
```

Observe that Spice discovers all schemas and tables in the `tpch` database:

```bash
2025-05-19T10:00:00.000000Z  INFO runtime::init::catalog: Registering catalog 'pg' for pg
2025-05-19T10:00:00.500000Z  INFO runtime::init::catalog: Registered catalog 'pg' with 1 schema and 8 tables
```

## Step 6. Query the PostgreSQL catalog

In a new terminal, start the Spice SQL REPL:

```bash
spice sql
```

List all discovered tables:

```sql
SHOW TABLES;
```

```
+---------------+--------------+--------------+------------+
| table_catalog | table_schema | table_name   | table_type |
+---------------+--------------+--------------+------------+
| spice         | runtime      | task_history | BASE TABLE |
| pg            | public       | part         | BASE TABLE |
| pg            | public       | customer     | BASE TABLE |
| pg            | public       | orders       | BASE TABLE |
| pg            | public       | region       | BASE TABLE |
| pg            | public       | supplier     | BASE TABLE |
| pg            | public       | nation       | BASE TABLE |
| pg            | public       | partsupp     | BASE TABLE |
| pg            | public       | lineitem     | BASE TABLE |
+---------------+--------------+--------------+------------+
```

Query a table using the three-part `catalog.schema.table` name:

```sql
SELECT c_custkey, c_name, c_mktsegment, c_acctbal
FROM pg.public.customer
LIMIT 5;
```

```
+-----------+--------------------+--------------+-----------+
| c_custkey | c_name             | c_mktsegment | c_acctbal |
+-----------+--------------------+--------------+-----------+
| 1         | Customer#000000001 | BUILDING     | 711.56    |
| 2         | Customer#000000002 | AUTOMOBILE   | 121.65    |
| 3         | Customer#000000003 | AUTOMOBILE   | 7498.12   |
| 4         | Customer#000000004 | MACHINERY    | 2866.83   |
| 5         | Customer#000000005 | HOUSEHOLD    | 794.47    |
+-----------+--------------------+--------------+-----------+
```

Run the TPC-H _Pricing Summary Report (Q1)_:

```sql
SELECT
  l_returnflag,
  l_linestatus,
  sum(l_quantity)                                       AS sum_qty,
  sum(l_extendedprice)                                  AS sum_base_price,
  sum(l_extendedprice * (1 - l_discount))               AS sum_disc_price,
  sum(l_extendedprice * (1 - l_discount) * (1 + l_tax)) AS sum_charge,
  avg(l_quantity)                                       AS avg_qty,
  avg(l_extendedprice)                                  AS avg_price,
  avg(l_discount)                                       AS avg_disc,
  count(*)                                              AS count_order
FROM pg.public.lineitem
WHERE l_shipdate <= date '1998-12-01' - interval '110' day
GROUP BY l_returnflag, l_linestatus
ORDER BY l_returnflag, l_linestatus;
```

```
+--------------+--------------+-------------+-----------------+-------------------+---------------------+-----------+--------------+----------+-------------+
| l_returnflag | l_linestatus | sum_qty     | sum_base_price  | sum_disc_price    | sum_charge          | avg_qty   | avg_price    | avg_disc | count_order |
+--------------+--------------+-------------+-----------------+-------------------+---------------------+-----------+--------------+----------+-------------+
| A            | F            | 37734107.00 | 56586554400.73  | 53758257134.87    | 55909065222.83      | 25.522005 | 38273.129734 | 0.049985 | 1478493     |
| N            | F            | 991417.00   | 1487504710.38   | 1413082168.05     | 1469649223.19       | 25.516471 | 38284.467760 | 0.050093 | 38854       |
| N            | O            | 73416597.00 | 110112303006.41 | 104608220776.38   | 108796375788.18     | 25.502437 | 38249.282778 | 0.049996 | 2878807     |
| R            | F            | 37719753.00 | 56568041380.90  | 53741292684.60    | 55889619119.83      | 25.505793 | 38250.854626 | 0.050009 | 1478870     |
+--------------+--------------+-------------+-----------------+-------------------+---------------------+-----------+--------------+----------+-------------+

Time: 0.812 seconds. 4 rows.
```

Run a cross-table join using the foreign key relationships:

```sql
SELECT
  r.r_name                        AS region,
  n.n_name                        AS nation,
  COUNT(DISTINCT c.c_custkey)     AS num_customers,
  ROUND(AVG(c.c_acctbal), 2)      AS avg_balance
FROM pg.public.customer c
JOIN pg.public.nation   n ON c.c_nationkey = n.n_nationkey
JOIN pg.public.region   r ON n.n_regionkey = r.r_regionkey
GROUP BY r.r_name, n.n_name
ORDER BY r.r_name, num_customers DESC;
```

```
+-------------+----------------+---------------+-------------+
| region      | nation         | num_customers | avg_balance |
+-------------+----------------+---------------+-------------+
| AFRICA      | MOZAMBIQUE     | 1102          | 4571.98     |
| AFRICA      | ETHIOPIA       | 1098          | 4627.11     |
...
| MIDDLE EAST | SAUDI ARABIA   | 1067          | 4540.05     |
+-------------+----------------+---------------+-------------+

Time: 0.045 seconds. 25 rows.
```

## Step 7. Clean up

```bash
docker compose down --volumes --rmi local
```

## References

- [Spice.ai PostgreSQL Catalog Connector documentation](https://docs.spiceai.org/components/catalogs/postgres)
- [TPC-H Benchmark Specification](https://www.tpc.org/tpc_documents_current_versions/pdf/tpc-h_v2.17.1.pdf)
- [Spice SQL CLI reference](https://docs.spiceai.org/cli/reference/sql)
