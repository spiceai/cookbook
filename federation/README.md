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

```bash
2025/01/27 11:36:41 INFO Checking for latest Spice runtime release...
2025/01/27 11:36:42 INFO Spice.ai runtime starting...
2025-01-27T19:36:43.199530Z  INFO runtime::init::dataset: Initializing dataset dremio_source
2025-01-27T19:36:43.199589Z  INFO runtime::init::dataset: Initializing dataset s3_source
2025-01-27T19:36:43.199709Z  INFO runtime::init::dataset: Initializing dataset dremio_source_accelerated
2025-01-27T19:36:43.199537Z  INFO runtime::init::dataset: Initializing dataset s3_source_accelerated
2025-01-27T19:36:43.201310Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2025-01-27T19:36:43.201625Z  INFO runtime::metrics_server: Spice Runtime Metrics listening on 127.0.0.1:9090
2025-01-27T19:36:43.205435Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2025-01-27T19:36:43.209349Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2025-01-27T19:36:43.401179Z  INFO runtime::init::results_cache: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
2025-01-27T19:36:43.624011Z  INFO runtime::init::dataset: Dataset dremio_source_accelerated registered (dremio:datasets.taxi_trips), acceleration (arrow), results cache enabled.
2025-01-27T19:36:43.625619Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset dremio_source_accelerated
2025-01-27T19:36:43.776300Z  INFO runtime::init::dataset: Dataset dremio_source registered (dremio:datasets.taxi_trips), results cache enabled.
2025-01-27T19:36:44.182533Z  INFO runtime::init::dataset: Dataset s3_source registered (s3://spiceai-demo-datasets/cleaned_sales_data.parquet), results cache enabled.
2025-01-27T19:36:44.203734Z  INFO runtime::init::dataset: Dataset s3_source_accelerated registered (s3://spiceai-demo-datasets/cleaned_sales_data.parquet), acceleration (sqlite), results cache enabled.
2025-01-27T19:36:44.205146Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset s3_source_accelerated
2025-01-27T19:36:45.138393Z  INFO runtime::accelerated_table::refresh_task: Loaded 2,823 rows (1010.18 kiB) for dataset s3_source_accelerated in 933ms.
2025-01-27T19:36:46.313896Z  INFO runtime::accelerated_table::refresh_task: Loaded 100,000 rows (27.91 MiB) for dataset dremio_source_accelerated in 2s 688ms.
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
