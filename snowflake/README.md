# Snowflake Data Connector Recipe

>[Snowflake](https://www.snowflake.com/) is a leading cloud-based data warehousing service that enables users to store, compute, and analyze vast amounts of data in real-time.

The guide demonstrates how to configure [Spice with Snowflake Data Connector](https://docs.spiceai.org/data-connectors/snowflake) to access a Snowflake database.

The guide requires a Snowflake account. Start [free trial](https://signup.snowflake.com/) if needed.

**Step 1.** Create [Snowflake TPC-H Sample Dataset](https://docs.snowflake.com/en/user-guide/sample-data-tpch)

1. **Sign in** to [Snowflake](https://app.snowflake.com/)
1. Select **Projects** » **Worksheets**
1. Execute the following SQL statements with the **ACCOUNTADMIN role** active. Refer to [Using the Sample Database](https://docs.snowflake.com/en/user-guide/sample-data-using) for more details.

```sql
-- Create a database from the share.
CREATE DATABASE IF NOT EXISTS SNOWFLAKE_SAMPLE_DATA FROM SHARE SFC_SAMPLES.SAMPLE_DATA;

-- Grant the PUBLIC role access to the database.
-- Optionally change the role name to restrict access to a subset of users.
GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE_SAMPLE_DATA TO ROLE PUBLIC;
```

**Step 2.** Initialize a new Spicepod

```bash
spice init snowflake-app
cd snowflake-app
```

**Step 3.** Configure Spice Snowflake access

1. Get [Snowflake account identifier](https://docs.snowflake.com/en/user-guide/admin-account-identifier#finding-the-organization-and-account-name-for-an-account)

1. Run `spice login snowflake -a <account-identifier> -u <username> -p <password>`

The CLI command will create a `.env` file in the current directory with the Snowflake account details. The `.env` file should look like this:

```bash
SPICE_SNOWFLAKE_ACCOUNT=<account-identifier>
SPICE_SNOWFLAKE_PASSWORD=<password>
SPICE_SNOWFLAKE_USERNAME=<username>
```

**Step 4.** Start the Spice runtime

```bash
spice run
```

The following output is shown in the Spice runtime terminal:

```bash
Spice.ai runtime starting...
2024-07-23T00:20:01.012063Z  INFO spiced: Metrics listening on 127.0.0.1:9090
2024-07-23T00:20:01.044050Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2024-07-23T00:20:01.044108Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2024-07-23T00:20:01.045430Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2024-07-23T00:20:01.047970Z  INFO runtime: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
```

**Step 5.** Configure Snowflake Dataset

Use text editor add **snowflake_sample_data.tpch_sf1** dataset to `spicepod.yaml`. Modify the `params` section to specify desired warehouse or role to use.

```yaml
version: v1beta1
kind: Spicepod
name: snowflake-app
datasets:
- from: snowflake:SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.LINEITEM
  name: lineitem
  params: 
    snowflake_role: accountadmin
    snowflake_warehouse: COMPUTE_WH
```

The following output is shown in the Spice runtime terminal:

```bash
2024-07-23T00:20:53.116572Z  INFO runtime: Dataset lineitem registered (snowflake:SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.LINEITEM), results cache enabled.
```

**Step 6.** Run queries against the dataset using the Spice SQL REPL.

In a new terminal, start the Spice SQL REPL.

```bash
spice sql
```

Check that TPC-H lineitem tables exist:

```sql
show tables;

sql> show tables;
+---------------+--------------+---------------+------------+
| table_catalog | table_schema | table_name    | table_type |
+---------------+--------------+---------------+------------+
| spice         | public       | lineitem      | BASE TABLE |
| spice         | runtime      | task_history  | BASE TABLE |
| spice         | runtime      | metrics       | BASE TABLE |
+---------------+--------------+---------------+------------+

Time: 0.032075708 seconds. 2 rows.
```

Run *Pricing Summary Report Query (Q1)*. More information about TPC-H and all the queries involved can be found in the official [TPC Benchmark H Standard Specification](https://www.tpc.org/tpc_documents_current_versions/pdf/tpc-h_v2.17.1.pdf).

```sql
SELECT
       "L_RETURNFLAG",
       "L_LINESTATUS",
       SUM("L_QUANTITY") AS "SUM_QTY",
       SUM("L_EXTENDEDPRICE") AS "SUM_BASE_PRICE",
       SUM("L_EXTENDEDPRICE" * (1-"L_DISCOUNT")) AS "SUM_DISC_PRICE",
       SUM("L_EXTENDEDPRICE" * (1-"L_DISCOUNT") * (1+"L_TAX")) AS "SUM_CHARGE",
       AVG("L_QUANTITY") AS "AVG_QTY",
       AVG("L_EXTENDEDPRICE") AS "AVG_PRICE",
       AVG("L_DISCOUNT") AS "AVG_DISC",
       COUNT(*) AS "COUNT_ORDER"
FROM
       lineitem
WHERE
       "L_SHIPDATE" <= DATE '1998-12-01'
GROUP BY
       "L_RETURNFLAG",
       "L_LINESTATUS"
ORDER BY
       "L_RETURNFLAG",
       "L_LINESTATUS";
;
```

Output:

```bash
+--------------+--------------+-------------+-----------------+-------------------+---------------------+-----------+--------------+----------+-------------+
| L_RETURNFLAG | L_LINESTATUS | SUM_QTY     | SUM_BASE_PRICE  | SUM_DISC_PRICE    | SUM_CHARGE          | AVG_QTY   | AVG_PRICE    | AVG_DISC | COUNT_ORDER |
+--------------+--------------+-------------+-----------------+-------------------+---------------------+-----------+--------------+----------+-------------+
| N            | F            | 991417.00   | 1487504710.38   | 1413082168.0541   | 1469649223.194375   | 25.516472 | 38284.467761 | 0.050093 | 38854       |
| A            | F            | 37734107.00 | 56586554400.73  | 53758257134.8700  | 55909065222.827692  | 25.522006 | 38273.129735 | 0.049985 | 1478493     |
| N            | O            | 76633518.00 | 114935210409.19 | 109189591897.4720 | 113561024263.013782 | 25.502020 | 38248.015609 | 0.050000 | 3004998     |
| R            | F            | 37719753.00 | 56568041380.90  | 53741292684.6040  | 55889619119.831932  | 25.505794 | 38250.854626 | 0.050009 | 1478870     |
+--------------+--------------+-------------+-----------------+-------------------+---------------------+-----------+--------------+----------+-------------+

Time: 1.398187833 seconds. 4 rows.
```

**Step 7. (Optional)** Enable [Data Acceleration](https://docs.spiceai.org/data-accelerators)

Use text editor to update `spicepod.yaml`

Before:

```yaml
version: v1beta1
kind: Spicepod
name: snowflake-app
datasets:
- from: snowflake:snowflake_sample_data.tpch_sf1.lineitem
  name: lineitem
  params: 
    snowflake_role: accountadmin
    snowflake_warehouse: COMPUTE_WH
```

After:

```yaml
version: v1beta1
kind: Spicepod
name: test
datasets:
- from: snowflake:snowflake_sample_data.tpch_sf1.lineitem
  name: lineitem
  params: 
    snowflake_role: accountadmin
    snowflake_warehouse: COMPUTE_WH
  acceleration:
    enabled: true
    refresh_sql: |
      SELECT * FROM lineitem WHERE "L_SHIPDATE" <= DATE '1998-12-01'
```

Note: we use `refresh_sql` parameter in this example to specify exact data we require local (specific date interval).

The following output is shown in the Spice runtime terminal confirming new configuration is applied.

```bash
2024-07-23T00:23:29.327942Z  INFO runtime: Updating accelerated dataset lineitem...
2024-07-23T00:23:29.657023Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset lineitem
2024-07-23T00:23:52.413596Z  INFO runtime::accelerated_table::refresh_task: Loaded 6,001,215 rows (9.46 GiB) for dataset lineitem in 22s 756ms.
2024-07-23T00:23:52.553037Z  INFO runtime: Dataset lineitem registered (snowflake:snowflake_sample_data.tpch_sf1.lineitem), acceleration (arrow), results cache enabled.
```

Run *Pricing Summary Report Query* using the Spice SQL REPL.

```sql
SELECT
       "L_RETURNFLAG",
       "L_LINESTATUS",
       SUM("L_QUANTITY") AS "SUM_QTY",
       SUM("L_EXTENDEDPRICE") AS "SUM_BASE_PRICE",
       SUM("L_EXTENDEDPRICE" * (1-"L_DISCOUNT")) AS "SUM_DISC_PRICE",
       SUM("L_EXTENDEDPRICE" * (1-"L_DISCOUNT") * (1+"L_TAX")) AS "SUM_CHARGE",
       AVG("L_QUANTITY") AS "AVG_QTY",
       AVG("L_EXTENDEDPRICE") AS "AVG_PRICE",
       AVG("L_DISCOUNT") AS "AVG_DISC",
       COUNT(*) AS "COUNT_ORDER"
FROM
       lineitem
WHERE
       "L_SHIPDATE" <= DATE '1998-12-01'
GROUP BY
       "L_RETURNFLAG",
       "L_LINESTATUS"
ORDER BY
       "L_RETURNFLAG",
       "L_LINESTATUS";
;
```

Output:

```bash
+--------------+--------------+-------------+-----------------+-------------------+---------------------+-----------+--------------+----------+-------------+
| L_RETURNFLAG | L_LINESTATUS | SUM_QTY     | SUM_BASE_PRICE  | SUM_DISC_PRICE    | SUM_CHARGE          | AVG_QTY   | AVG_PRICE    | AVG_DISC | COUNT_ORDER |
+--------------+--------------+-------------+-----------------+-------------------+---------------------+-----------+--------------+----------+-------------+
| A            | F            | 37734107.00 | 56586554400.73  | 53758257134.8700  | 55909065222.827692  | 25.522005 | 38273.129734 | 0.049985 | 1478493     |
| N            | F            | 991417.00   | 1487504710.38   | 1413082168.0541   | 1469649223.194375   | 25.516471 | 38284.467760 | 0.050093 | 38854       |
| N            | O            | 76633518.00 | 114935210409.19 | 109189591897.4720 | 113561024263.013782 | 25.502019 | 38248.015609 | 0.050000 | 3004998     |
| R            | F            | 37719753.00 | 56568041380.90  | 53741292684.6040  | 55889619119.831932  | 25.505793 | 38250.854626 | 0.050009 | 1478870     |
+--------------+--------------+-------------+-----------------+-------------------+---------------------+-----------+--------------+----------+-------------+

Time: 0.080415458 seconds. 4 rows.
```

Observe query execution time decreased from **1.398187833** to **0.080415458** seconds using local acceleration.
