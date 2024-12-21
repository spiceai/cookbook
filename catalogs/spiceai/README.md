# Spice.ai Cloud Platform Catalog Connector

The Spice.ai Cloud Platform Catalog Connector makes querying datasets in the Spice.ai Cloud Platform simple.

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
  - name: spiceai
    from: spice.ai
```

## Step 5. Start the Spice runtime

```bash
spice run
```

## Step 6. Query a dataset

```bash
spice sql
```

```sql
SELECT * FROM spiceai.tpch.lineitem LIMIT 10;
```

## Step 7. Explore the available datasets

Use `show tables;` in the Spice SQL REPL to see the available datasets.

```bash
sql> show tables;
+---------------+--------------+----------------------------------------------------------------+------------+
| table_catalog | table_schema | table_name                                                     | table_type |
+---------------+--------------+----------------------------------------------------------------+------------+
| spiceai       | tpch         | region                                                         | BASE TABLE |
| spiceai       | tpch         | orders                                                         | BASE TABLE |
| spiceai       | tpch         | part                                                           | BASE TABLE |
| spiceai       | tpch         | supplier                                                       | BASE TABLE |
| spiceai       | tpch         | customer                                                       | BASE TABLE |
| spiceai       | tpch         | partsupp                                                       | BASE TABLE |
| spiceai       | tpch         | lineitem                                                       | BASE TABLE |
| spiceai       | tpch         | nation                                                         | BASE TABLE |
| spiceai       | ens          | domains                                                        | BASE TABLE |
| spiceai       | spiceai      | datasets_tpch_partsupp                                         | BASE TABLE |
| spiceai       | spiceai      | datasets_tpch_nation                                           | BASE TABLE |
| spiceai       | spiceai      | datasets_eth_aave_v2_collateral_updates                        | BASE TABLE |
| spiceai       | spiceai      | datasets_eth_sushiswap_pool_stats_detailed                     | BASE TABLE |
| spiceai       | spiceai      | datasets_tpch_orders                                           | BASE TABLE |
... (truncated)
| spiceai       | goerli       | wallet_lst_balances                                            | BASE TABLE |
| spice         | runtime      | task_history                                                   | BASE TABLE |
| spice         | runtime      | metrics                                                        | BASE TABLE |
+---------------+--------------+----------------------------------------------------------------+------------+

Time: 0.007676958 seconds. 249 rows.
```

## Step 8. Filter the included tables with `include`

Specify an `include` filter to limit the tables registered in the catalog.

```yaml
catalogs:
  - name: spiceai
    from: spice.ai
    include:
      - tpch.*
```

```bash
sql> show tables;
+---------------+--------------+---------------+------------+
| table_catalog | table_schema | table_name    | table_type |
+---------------+--------------+---------------+------------+
| spiceai       | tpch         | nation        | BASE TABLE |
| spiceai       | tpch         | orders        | BASE TABLE |
| spiceai       | tpch         | partsupp      | BASE TABLE |
| spiceai       | tpch         | part          | BASE TABLE |
| spiceai       | tpch         | lineitem      | BASE TABLE |
| spiceai       | tpch         | region        | BASE TABLE |
| spiceai       | tpch         | customer      | BASE TABLE |
| spiceai       | tpch         | supplier      | BASE TABLE |
| spice         | runtime      | task_history  | BASE TABLE |
| spice         | runtime      | metrics       | BASE TABLE |
+---------------+--------------+---------------+------------+

Time: 0.001866958 seconds. 9 rows.
```
