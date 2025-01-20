# Federated SQL Query

Fetch combined data from S3 Parquet, PostgreSQL, and Dremio in a single query.

## Follow these steps to use Spice to federate SQL queries across data sources

**Step 1.** Clone the [github.com/spiceai/cookbook](https://github.com/spiceai/cookbook) repo and navigate to the `federation` directory.

```bash
git clone https://github.com/spiceai/cookbook
cd cookbook/federation
```

**Step 2.** Initialize the Spice app. Use the default name by pressing enter when prompted.

```bash
spice init
name: (federation)?
```

**Step 3.** Log into the demo Dremio instance. Ensure this command is run in the `federation` directory.

```bash
spice login dremio -u demo -p demo1234
```

**Step 4.** Add the `spiceai/fed-demo` Spicepod from [spicerack.org](https://spicerack.org).

```bash
spice add spiceai/fed-demo
```

**Step 5.** Start the Spice runtime.

```bash
spice run
```

**Step 6.** In another terminal window, start the Spice SQL REPL and perform the following SQL queries:

```bash
spice sql
```

```sql
-- Query the federated S3 source
select * from s3_source;

-- Query the accelerated S3 source
select * from s3_source_accelerated;

-- Query the federated Dremio source
select * from dremio_source;

-- Query the accelerated Dremio source
select * from dremio_source_accelerated;

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
