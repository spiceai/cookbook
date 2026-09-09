# MySQL Catalog Connector

Works with `v2.0+`

The MySQL Catalog Connector enables Spice to automatically discover and query all databases and tables in a MySQL server. This recipe demonstrates the connector using the standard TPC-H benchmark dataset (Scale Factor 1) with full foreign key constraints defined between tables.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed
- Spice installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation)

## Step 1. Start the MySQL database

Clone the cookbook repository and start the database using Docker Compose. The `mysql-init` container downloads the TPC-H SF1 parquet files and loads them into MySQL, creating all tables with primary keys and foreign keys.

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/catalogs/mysql
docker compose up -d
```

Wait for the init container to finish loading data (it downloads ~700 MB of parquet files on first build):

```bash
docker compose logs -f mysql-init
```

You should see:

```
tpch-mysql-init  | MySQL is ready.
tpch-mysql-init  | Creating schema ...
tpch-mysql-init  | Schema created.
tpch-mysql-init  |
tpch-mysql-init  | Loading region ...
tpch-mysql-init  |   Reading /data/tpch_sf1/region.parquet ...
tpch-mysql-init  |   5 rows, schema: ...
tpch-mysql-init  |   Loaded 5 rows into region.
...
tpch-mysql-init  | All TPC-H tables loaded successfully!
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
mkdir mysql-catalog-recipe
cd mysql-catalog-recipe
spice init
```

## Step 3. Configure credentials

Create a `.env` file with the database credentials:

```bash
echo "MYSQL_USER=root" > .env
```

## Step 4. Add the MySQL Catalog Connector to `spicepod.yaml`

```yaml
version: v1
kind: Spicepod
name: mysql-catalog-recipe

catalogs:
  - from: mysql
    name: my
    params:
      mysql_host: localhost
      mysql_tcp_port: 3306
      mysql_db: tpch
      mysql_user: ${secrets:MYSQL_USER}
      mysql_sslmode: disabled
```

## Step 5. Start the Spice runtime

```bash
spice run
```

Observe that Spice discovers all databases and tables in the MySQL server:

```bash
2025-05-19T10:00:00.000000Z  INFO runtime::init::catalog: Registering catalog 'my' for mysql
2025-05-19T10:00:00.500000Z  INFO runtime::init::catalog: Registered catalog 'my' with 1 schema and 8 tables
```

## Step 6. Query the MySQL catalog

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
| my            | tpch         | region       | BASE TABLE |
| my            | tpch         | nation       | BASE TABLE |
| my            | tpch         | part         | BASE TABLE |
| my            | tpch         | supplier     | BASE TABLE |
| my            | tpch         | customer     | BASE TABLE |
| my            | tpch         | partsupp     | BASE TABLE |
| my            | tpch         | orders       | BASE TABLE |
| my            | tpch         | lineitem     | BASE TABLE |
| spice         | runtime      | task_history | BASE TABLE |
+---------------+--------------+--------------+------------+
```

Query a table using the three-part `catalog.database.table` name:

```sql
SELECT c_custkey, c_name, c_mktsegment, c_acctbal
FROM my.tpch.customer
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
FROM my.tpch.lineitem
WHERE l_shipdate <= date '1998-12-01' - interval '110' day
GROUP BY l_returnflag, l_linestatus
ORDER BY l_returnflag, l_linestatus;
```

```
+--------------+--------------+---------------+-----------------+-------------------+---------------------+---------------+---------------+---------------+-------------+
| l_returnflag | l_linestatus |    sum_qty    |  sum_base_price |   sum_disc_price  |      sum_charge     |    avg_qty    |   avg_price   |    avg_disc   | count_order |
|    varchar   |    varchar   | decimal(25,2) |  decimal(25,2)  |   decimal(38,4)   |    decimal(38,6)    | decimal(19,6) | decimal(19,6) | decimal(19,6) |    int64    |
+--------------+--------------+---------------+-----------------+-------------------+---------------------+---------------+---------------+---------------+-------------+
| A            | F            | 37734107.00   | 56586554400.73  | 53758257134.8700  | 55909065222.827692  | 25.522006     | 38273.129735  | 0.049985      | 1478493     |
| N            | F            | 991417.00     | 1487504710.38   | 1413082168.0541   | 1469649223.194375   | 25.516472     | 38284.467761  | 0.050093      | 38854       |
| N            | O            | 73416597.00   | 110112303006.41 | 104608220776.3836 | 108796375788.183317 | 25.502438     | 38249.282778  | 0.049996      | 2878807     |
| R            | F            | 37719753.00   | 56568041380.90  | 53741292684.6040  | 55889619119.831932  | 25.505794     | 38250.854626  | 0.050009      | 1478870     |
+--------------+--------------+---------------+-----------------+-------------------+---------------------+---------------+---------------+---------------+-------------+

Time: 0.877365833 seconds. 4 rows.
```

Run a cross-table join using the foreign key relationships:

```sql
SELECT
  r.r_name                        AS region,
  n.n_name                        AS nation,
  COUNT(DISTINCT c.c_custkey)     AS num_customers,
  ROUND(AVG(c.c_acctbal), 2)      AS avg_balance
FROM my.tpch.customer c
JOIN my.tpch.nation   n ON c.c_nationkey = n.n_nationkey
JOIN my.tpch.region   r ON n.n_regionkey = r.r_regionkey
GROUP BY r.r_name, n.n_name
ORDER BY r.r_name, num_customers DESC, nation;
```

```
+-------------+----------------+---------------+---------------+
|   region    |     nation     | num_customers |  avg_balance  |
|   varchar   |    varchar     |     int64     | decimal(19,6) |
+-------------+----------------+---------------+---------------+
| AFRICA      | KENYA          | 5992          | 4573.860000   |
| AFRICA      | MOZAMBIQUE     | 5974          | 4523.420000   |
| AFRICA      | ETHIOPIA       | 5952          | 4467.370000   |
| AFRICA      | ALGERIA        | 5925          | 4442.700000   |
| AFRICA      | MOROCCO        | 5921          | 4496.790000   |
| AMERICA     | CANADA         | 6020          | 4489.260000   |
| AMERICA     | BRAZIL         | 5999          | 4471.020000   |
| AMERICA     | UNITED STATES  | 5983          | 4565.650000   |
| AMERICA     | ARGENTINA      | 5975          | 4485.000000   |
| AMERICA     | PERU           | 5975          | 4444.570000   |
| ASIA        | INDONESIA      | 6161          | 4533.430000   |
| ASIA        | INDIA          | 6042          | 4517.320000   |
| ASIA        | CHINA          | 6024          | 4438.950000   |
| ASIA        | VIETNAM        | 6008          | 4507.660000   |
| ASIA        | JAPAN          | 5948          | 4522.270000   |
| EUROPE      | FRANCE         | 6100          | 4436.010000   |
| EUROPE      | ROMANIA        | 6100          | 4544.850000   |
| EUROPE      | RUSSIA         | 6078          | 4517.580000   |
| EUROPE      | UNITED KINGDOM | 6011          | 4514.660000   |
| EUROPE      | GERMANY        | 5908          | 4452.740000   |
| MIDDLE EAST | JORDAN         | 6033          | 4457.380000   |
| MIDDLE EAST | IRAN           | 6009          | 4467.340000   |
| MIDDLE EAST | EGYPT          | 5995          | 4520.490000   |
| MIDDLE EAST | IRAQ           | 5963          | 4514.440000   |
| MIDDLE EAST | SAUDI ARABIA   | 5904          | 4480.980000   |
+-------------+----------------+---------------+---------------+

Time: 0.102868 seconds. 25 rows.
```

## Step 7. Clean up

```bash
docker compose down --volumes --rmi local
```

## References

- [Spice.ai MySQL Catalog Connector documentation](https://docs.spiceai.org/components/catalogs/mysql)
- [TPC-H Benchmark Specification](https://www.tpc.org/tpc_documents_current_versions/pdf/tpc-h_v2.17.1.pdf)
- [Spice SQL CLI reference](https://docs.spiceai.org/cli/reference/sql)
