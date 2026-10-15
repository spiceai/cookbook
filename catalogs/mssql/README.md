# Microsoft SQL Server Catalog Connector

Works with `v2.0+`

The Microsoft SQL Server Catalog Connector enables Spice to automatically discover and query all schemas and tables in an MSSQL database. This recipe demonstrates the connector using the standard TPC-H benchmark dataset (Scale Factor 0.1) with full foreign key constraints defined between tables.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed
- Spice installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation)

## Step 1. Start the SQL Server database

Clone the cookbook repository and start the database using Docker Compose. The `mssql-init` container generates TPC-H data at Scale Factor 0.1 using DuckDB's built-in generator and loads it into SQL Server with primary keys and foreign keys.

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/catalogs/mssql
docker compose up -d
```

Wait for the init container to finish (usually 2–5 minutes):

```bash
docker compose logs -f mssql-init
```

You should see:

```
tpch-mssql-init  | SQL Server is ready.
tpch-mssql-init  | Database 'tpch' ready.
tpch-mssql-init  | Generating TPC-H SF=0.1 with DuckDB ...
tpch-mssql-init  | TPC-H data generated.
tpch-mssql-init  | Creating schema ...
tpch-mssql-init  | Schema created.
tpch-mssql-init  |
tpch-mssql-init  | Loading region ...
tpch-mssql-init  |   5 rows
tpch-mssql-init  |   Loaded 5 rows into region.
...
tpch-mssql-init  | All TPC-H tables loaded successfully!
```

The TPC-H schema includes the following foreign key relationships:

| Table      | Foreign Key Column(s)          | References                         |
|------------|--------------------------------|------------------------------------|
| `nation`   | `n_regionkey`                  | `region(r_regionkey)`              |
| `supplier` | `s_nationkey`                  | `nation(n_nationkey)`              |
| `customer` | `c_nationkey`                  | `nation(n_nationkey)`              |
| `partsupp` | `ps_partkey`                   | `part(p_partkey)`                  |
| `partsupp` | `ps_suppkey`                   | `supplier(s_suppkey)`              |
| `orders`   | `o_custkey`                    | `customer(c_custkey)`              |
| `lineitem` | `l_orderkey`                   | `orders(o_orderkey)`               |
| `lineitem` | `(l_partkey, l_suppkey)`       | `partsupp(ps_partkey, ps_suppkey)` |

## Step 2. Go to the Spicepod directory

The `mssql-catalog-recipe` directory already contains the `spicepod.yaml` file (shown in Step 4) and a `.env.example` file. Do not run `spice init`.

```bash
cd mssql-catalog-recipe
```

## Step 3. Configure credentials

Create a `.env` file with the database credentials:

```bash
cp .env.example .env
```

Or set them directly:

```bash
echo "MSSQL_USERNAME=sa" > .env
echo "MSSQL_PASSWORD=SpiceDemo1!" >> .env
```

## Step 4. Review the Microsoft SQL Server Catalog Connector in `spicepod.yaml`

```yaml
version: v1
kind: Spicepod
name: mssql-catalog-recipe

catalogs:
  - from: mssql
    name: ms
    params:
      mssql_host: localhost
      mssql_port: 1433
      mssql_database: tpch
      mssql_username: ${secrets:MSSQL_USERNAME}
      mssql_password: ${secrets:MSSQL_PASSWORD}
      mssql_encrypt: disable
      mssql_trust_server_certificate: "true"
```

## Step 5. Start the Spice runtime

```bash
spice run
```

Observe that Spice discovers all schemas and tables in the `tpch` database:

```bash
2026-10-15T06:18:43.270961Z  INFO runtime::init::catalog: Registering catalog 'ms' for mssql
2026-10-15T06:18:45.186008Z  INFO runtime::init::catalog: Registered catalog 'ms' with 1 schema and 8 tables
```

## Step 6. Query the SQL Server catalog

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
| table_catalog | table_schema |  table_name  | table_type |
|    varchar    |    varchar   |    varchar   |   varchar  |
+---------------+--------------+--------------+------------+
| ms            | dbo          | supplier     | BASE TABLE |
| ms            | dbo          | region       | BASE TABLE |
| ms            | dbo          | customer     | BASE TABLE |
| ms            | dbo          | orders       | BASE TABLE |
| ms            | dbo          | partsupp     | BASE TABLE |
| ms            | dbo          | nation       | BASE TABLE |
| ms            | dbo          | part         | BASE TABLE |
| ms            | dbo          | lineitem     | BASE TABLE |
| spice         | runtime      | task_history | BASE TABLE |
| spice         | runtime      | metrics      | BASE TABLE |
+---------------+--------------+--------------+------------+

Time: 0.001717875 seconds. 10 rows.
```

The order of the tables can be different.

Query a table using the three-part `catalog.schema.table` name:

```sql
SELECT c_custkey, c_name, c_mktsegment, c_acctbal
FROM ms.dbo.customer
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
FROM ms.dbo.lineitem
WHERE l_shipdate <= date '1998-12-01' - interval '110' day
GROUP BY l_returnflag, l_linestatus
ORDER BY l_returnflag, l_linestatus;
```

```
+--------------+--------------+---------------+----------------+-----------------+--------------------+---------------+---------------+---------------+-------------+
| l_returnflag | l_linestatus |    sum_qty    | sum_base_price |  sum_disc_price |     sum_charge     |    avg_qty    |   avg_price   |    avg_disc   | count_order |
+--------------+--------------+---------------+----------------+-----------------+--------------------+---------------+---------------+---------------+-------------+
| A            | F            | 3774200.00    | 5320753880.69  | 5054096266.6828 | 5256751331.449234  | 25.537587     | 36002.123829  | 0.050144      | 147790      |
| N            | F            | 95257.00      | 133737795.84   | 127132372.6512  | 132286291.229445   | 25.300664     | 35521.326916  | 0.049394      | 3765        |
| N            | O            | 7350414.00    | 10358309235.26 | 9839988630.9747 | 10233485783.131724 | 25.546131     | 35999.976489  | 0.050097      | 287731      |
| R            | F            | 3785523.00    | 5337950526.47  | 5071818532.9420 | 5274405503.049367  | 25.525943     | 35994.029214  | 0.049989      | 148301      |
+--------------+--------------+---------------+----------------+-----------------+--------------------+---------------+---------------+---------------+-------------+

Time: 0.784812833 seconds. 4 rows.
```

Run a cross-table join using the foreign key relationships:

```sql
SELECT
  r.r_name                        AS region,
  n.n_name                        AS nation,
  COUNT(DISTINCT c.c_custkey)     AS num_customers,
  ROUND(AVG(c.c_acctbal), 2)      AS avg_balance
FROM ms.dbo.customer c
JOIN ms.dbo.nation   n ON c.c_nationkey = n.n_nationkey
JOIN ms.dbo.region   r ON n.n_regionkey = r.r_regionkey
GROUP BY r.r_name, n.n_name
ORDER BY r.r_name, num_customers DESC;
```

```
+-------------+----------------+---------------+---------------+
|    region   |     nation     | num_customers |  avg_balance  |
+-------------+----------------+---------------+---------------+
| AFRICA      | MOROCCO        | 620           | 4366.45       |
| AFRICA      | ETHIOPIA       | 616           | 4384.92       |
...
| MIDDLE EAST | SAUDI ARABIA   | 543           | 4573.21       |
+-------------+----------------+---------------+---------------+

Time: 0.056650125 seconds. 25 rows.
```

## Step 7. Clean up

```bash
docker compose down --volumes --rmi local
```

## References

- [Spice.ai Microsoft SQL Server Catalog Connector documentation](https://docs.spiceai.org/components/catalogs/mssql)
- [TPC-H Benchmark Specification](https://www.tpc.org/tpc_documents_current_versions/pdf/tpc-h_v2.17.1.pdf)
- [Spice SQL CLI reference](https://docs.spiceai.org/cli/reference/sql)
