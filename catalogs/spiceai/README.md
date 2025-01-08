# Spice.ai Cloud Platform Catalog Connector

The Spice.ai Cloud Platform Catalog Connector makes querying datasets in the Spice.ai Cloud Platform simple.

This example will show how to connect to public datasets available in the Spice.ai Cloud Platform. Additional public datasets are available in [Spicerack](https://spicerack.org/).

## Prerequisites

- A Spice.ai Cloud Platform account (sign up at <https://spice.ai>)
- Spice is installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation).

## Step 1. Create a Spice.ai Cloud Platform account

Sign up for a Spice.ai Cloud Platform account at <https://spice.ai>.

## Step 2. Create a new directory and initialize a Spicepod

```bash
spice init spice-catalog-demo
cd spice-catalog-demo
```

## Step 3. Login to the Spice.ai Cloud Platform with `spice login`

Working in the `spice-catalog-demo` directory, use the Spice CLI to login to the Spice.ai Cloud Platform. A browser window will open to authenticate when executing the `spice login` command.

```bash
spice login
```

After successfully authenticating, the Spice.ai Cloud Platform API Key and Token will be stored in the `spice-catalog-demo` working directory `.env` file. The Spice runtime reads environment variables set in the local working `.env` file.

## Step 4. Add the Spice.ai Cloud Platform Catalog Connector to `spicepod.yaml`

Add the following configuration to your `spicepod.yaml`:

```yaml
catalogs:
  - from: spice.ai/spiceai/tpch
    name: scp
```

This will register the `scp` catalog to connect to the [`spiceai/tpch`](https://spice.ai/spiceai/tpch) app and load all available tables.

## Step 5. Start the Spice runtime

```bash
spice run
```

## Step 6. Query a dataset

```bash
spice sql
```

```sql
SELECT * FROM scp.tpch.lineitem LIMIT 10;
```

## Step 7. Explore the available datasets

Use `show tables;` in the Spice SQL REPL to see the available datasets.

```bash
sql> show tables;
+---------------+--------------+--------------+------------+
| table_catalog | table_schema | table_name   | table_type |
+---------------+--------------+--------------+------------+
| scp           | tpch         | orders       | BASE TABLE |
| scp           | tpch         | region       | BASE TABLE |
| scp           | tpch         | part         | BASE TABLE |
| scp           | tpch         | supplier     | BASE TABLE |
| scp           | tpch         | lineitem     | BASE TABLE |
| scp           | tpch         | nation       | BASE TABLE |
| scp           | tpch         | customer     | BASE TABLE |
| scp           | tpch         | partsupp     | BASE TABLE |
| spice         | runtime      | task_history | BASE TABLE |
| spice         | runtime      | metrics      | BASE TABLE |
+---------------+--------------+--------------+------------+

Time: 0.005605209 seconds. 10 rows.
```

## Step 8. Filter the included tables with `include`

Specify an `include` filter to limit the tables registered in the catalog.

```yaml
catalogs:
  - from: spice.ai/spiceai/tpch
    name: scp
    include:
      - tpch.part*
      - tpch.supplier
```

```bash
sql> show tables;
+---------------+--------------+---------------+------------+
| table_catalog | table_schema | table_name    | table_type |
+---------------+--------------+---------------+------------+
| spiceai       | tpch         | partsupp      | BASE TABLE |
| spiceai       | tpch         | part          | BASE TABLE |
| spiceai       | tpch         | supplier      | BASE TABLE |
| spice         | runtime      | task_history  | BASE TABLE |
| spice         | runtime      | metrics       | BASE TABLE |
+---------------+--------------+---------------+------------+

Time: 0.001866958 seconds. 9 rows.
```

## Step 9. Add the Quickstart Catalog

Add the Quickstart Catalog to the `spicepod.yaml` file. This demonstrates how to include tables from multiple Spice.ai Cloud Platform apps.

```yaml
catalogs:
  # ... existing catalog ...

  - from: spice.ai/spiceai/quickstart
    name: quickstart
```

```bash
spice sql
sql> show tables;
+---------------+--------------+--------------+------------+
| table_catalog | table_schema | table_name   | table_type |
+---------------+--------------+--------------+------------+
| spiceai       | tpch         | partsupp     | BASE TABLE |
| spiceai       | tpch         | part         | BASE TABLE |
| spiceai       | tpch         | supplier     | BASE TABLE |
| quickstart    | public       | taxi_trips   | BASE TABLE |
| spice         | runtime      | task_history | BASE TABLE |
| spice         | runtime      | metrics      | BASE TABLE |
+---------------+--------------+--------------+------------+

Time: 0.011640125 seconds. 6 rows.

sql> SELECT passenger_count, fare_amount FROM quickstart.public.taxi_trips LIMIT 10;
+-----------------+-------------+
| passenger_count | fare_amount |
+-----------------+-------------+
| 2               | 8.6         |
| 2               | 70.0        |
| 2               | 5.8         |
| 2               | 7.2         |
| 2               | 7.9         |
| 2               | 12.8        |
| 2               | 6.5         |
| 2               | 10.0        |
| 2               | 10.7        |
| 2               | 34.5        |
+-----------------+-------------+

Time: 1.167164208 seconds. 10 rows.
```

## Next Steps

Discover the apps available in [Spicerack](https://spicerack.org/) and use them as catalogs in the Spice.ai Cloud Platform catalog connector.
