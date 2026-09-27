# In-Memory Results Caching

Works with `v1.10+`

> Spice.ai OSS supports in-memory caching of query results to improve performance for bursts of requests and non-accelerated results, such as refresh data returned [on zero results](https://docs.spiceai.org/features/data-acceleration/data-refresh#behavior-on-zero-results).
>
> [Spice.ai OSS Docs: Results Caching](https://docs.spiceai.org/features/caching)

This recipe demonstrates using [TPC-H Benchmark Sample Data](https://github.com/spiceai/cookbook/tree/trunk/tpc-h) with in-memory caching to boost query performance.

---

## Step 1: Initialize and Start Spice

Run the following commands to initialize and start the Spice runtime:

```bash
spice init cache-recipe
cd cache-recipe
spice run
```

## Step 2: Add the TPC-H Benchmark Spicepod

In a separate terminal, navigate to the `cache-recipe` directory and add the `spiceai/tpch` Spicepod:

```bash
cd cache-recipe
spice add spiceai/tpch
```

Observe the Spice runtime terminal for cache initialization. Example output:

```bash
2026-08-13T12:05:35.255688Z  INFO runtime::init::caching: Initialized sql results cache; max size: 128.00 MiB, item ttl: 1s, hashing algorithm: XXH3, encoding: none
2026-08-13T12:06:15.025355Z  INFO runtime::init::dataset: Dataset tpch.customer registered (s3://spiceai-demo-datasets/tpch/customer/), acceleration (duckdb), results cache enabled. duration_ms=29
2026-08-13T12:06:16.247663Z  INFO runtime::init::dataset: Dataset tpch.lineitem registered (s3://spiceai-demo-datasets/tpch/lineitem/), acceleration (duckdb), results cache enabled. duration_ms=2
2026-08-13T12:06:17.029597Z  INFO runtime::init::dataset: Dataset tpch.nation registered (s3://spiceai-demo-datasets/tpch/nation/), acceleration (duckdb), results cache enabled. duration_ms=5
2026-08-13T12:06:18.168273Z  INFO runtime::init::dataset: Dataset tpch.orders registered (s3://spiceai-demo-datasets/tpch/orders/), acceleration (duckdb), results cache enabled. duration_ms=2
2026-08-13T12:06:19.339153Z  INFO runtime::init::dataset: Dataset tpch.part registered (s3://spiceai-demo-datasets/tpch/part/), acceleration (duckdb), results cache enabled. duration_ms=2
2026-08-13T12:06:20.452807Z  INFO runtime::init::dataset: Dataset tpch.partsupp registered (s3://spiceai-demo-datasets/tpch/partsupp/), acceleration (duckdb), results cache enabled. duration_ms=2
2026-08-13T12:06:21.209175Z  INFO runtime::init::dataset: Dataset tpch.region registered (s3://spiceai-demo-datasets/tpch/region/), acceleration (duckdb), results cache enabled. duration_ms=1
2026-08-13T12:06:22.259362Z  INFO runtime::init::dataset: Dataset tpch.supplier registered (s3://spiceai-demo-datasets/tpch/supplier/), acceleration (duckdb), results cache enabled. duration_ms=2
```

The `spiceai/tpch` Spicepod registers its datasets under the `tpch` schema (`tpch.lineitem`, `tpch.nation`, …) and accelerates them with DuckDB, which is why each line reports `acceleration (duckdb)`.

Notice the following line confirming the default cache configuration with cached items expiration time of 1 second is loaded.

```bash
2026-08-13T12:05:35.255688Z  INFO runtime::init::caching: Initialized sql results cache; max size: 128.00 MiB, item ttl: 1s, hashing algorithm: XXH3, encoding: none
```

## Step 3: Update Cache Configuration

Stop the Spice runtime using `Ctrl-C`. Open the `spicepod.yaml` file and add a custom cache configuration to increase the cached items' expiration time to 5 minutes.

**Before:**

```yaml
version: v2
kind: Spicepod
name: cache-recipe
dependencies:
  - spiceai/tpch
```

**After:**

```yaml
version: v2
kind: Spicepod
name: cache-recipe

runtime:
  caching:
    sql_results:
      enabled: true
      max_size: 128MiB
      item_ttl: 5m
      eviction_policy: lru

dependencies:
  - spiceai/tpch
```

Restart the Spice runtime:

```bash
spice run
```

Verify the following output is shown in the Spice runtime terminal, confirming that the updated in-memory caching settings (`Initialized sql results cache; max size: 128.00 MiB, item ttl: 300s`) were applied:

```bash
2026-08-13T12:08:09.299303Z  INFO runtime::init::caching: Initialized sql results cache; max size: 128.00 MiB, item ttl: 300s, hashing algorithm: XXH3, encoding: none
2026-08-13T12:08:47.417382Z  INFO runtime::init::dataset: Dataset tpch.region registered (s3://spiceai-demo-datasets/tpch/region/), acceleration (duckdb), results cache enabled. duration_ms=1
2026-08-13T12:08:47.421355Z  INFO runtime::init::dataset: Dataset tpch.nation registered (s3://spiceai-demo-datasets/tpch/nation/), acceleration (duckdb), results cache enabled. duration_ms=5
2026-08-13T12:08:47.422105Z  INFO runtime::init::dataset: Dataset tpch.supplier registered (s3://spiceai-demo-datasets/tpch/supplier/), acceleration (duckdb), results cache enabled. duration_ms=2
2026-08-13T12:08:47.424512Z  INFO runtime::init::dataset: Dataset tpch.orders registered (s3://spiceai-demo-datasets/tpch/orders/), acceleration (duckdb), results cache enabled. duration_ms=2
2026-08-13T12:08:47.426894Z  INFO runtime::init::dataset: Dataset tpch.partsupp registered (s3://spiceai-demo-datasets/tpch/partsupp/), acceleration (duckdb), results cache enabled. duration_ms=2
2026-08-13T12:08:47.556150Z  INFO runtime::init::dataset: Dataset tpch.part registered (s3://spiceai-demo-datasets/tpch/part/), acceleration (duckdb), results cache enabled. duration_ms=2
2026-08-13T12:08:47.595436Z  INFO runtime::init::dataset: Dataset tpch.lineitem registered (s3://spiceai-demo-datasets/tpch/lineitem/), acceleration (duckdb), results cache enabled. duration_ms=2
2026-08-13T12:08:47.734620Z  INFO runtime::init::dataset: Dataset tpch.customer registered (s3://spiceai-demo-datasets/tpch/customer/), acceleration (duckdb), results cache enabled. duration_ms=29
```

## Step 4: Run Queries

Start the Spice SQL REPL in a new terminal:

```bash
spice sql
```

Run the _Pricing Summary Report Query (Q1)_:

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
  tpch.lineitem
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

Observe the query execution time. First run:

```console
+--------------+--------------+---------------+-----------------+-------------------+---------------------+---------------+---------------+---------------+-------------+
| l_returnflag | l_linestatus |    sum_qty    |  sum_base_price |   sum_disc_price  |      sum_charge     |    avg_qty    |   avg_price   |    avg_disc   | count_order |
|    varchar   |    varchar   | decimal(25,2) |  decimal(25,2)  |   decimal(38,4)   |    decimal(38,6)    | decimal(19,6) | decimal(19,6) | decimal(19,6) |    int64    |
+--------------+--------------+---------------+-----------------+-------------------+---------------------+---------------+---------------+---------------+-------------+
| A            | F            | 37734107.00   | 56586554400.73  | 53758257134.8700  | 55909065222.827692  | 25.522006     | 38273.129735  | 0.049985      | 1478493     |
| N            | F            | 991417.00     | 1487504710.38   | 1413082168.0541   | 1469649223.194375   | 25.516472     | 38284.467761  | 0.050093      | 38854       |
| N            | O            | 73416597.00   | 110112303006.41 | 104608220776.3836 | 108796375788.183317 | 25.502438     | 38249.282778  | 0.049996      | 2878807     |
| R            | F            | 37719753.00   | 56568041380.90  | 53741292684.6040  | 55889619119.831932  | 25.505794     | 38250.854626  | 0.050009      | 1478870     |
+--------------+--------------+---------------+-----------------+-------------------+---------------------+---------------+---------------+---------------+-------------+

Time: 0.055311500 seconds. 4 rows.
```

Execute the same query again and observe a significant reduction in query execution time, from **0.055311500** to **0.001090834** seconds, due to the result being retrieved from the in-memory cache. The cached item will expire 5 minutes after the initial query execution. Cached run:

```console
+--------------+--------------+---------------+-----------------+-------------------+---------------------+---------------+---------------+---------------+-------------+
| l_returnflag | l_linestatus |    sum_qty    |  sum_base_price |   sum_disc_price  |      sum_charge     |    avg_qty    |   avg_price   |    avg_disc   | count_order |
|    varchar   |    varchar   | decimal(25,2) |  decimal(25,2)  |   decimal(38,4)   |    decimal(38,6)    | decimal(19,6) | decimal(19,6) | decimal(19,6) |    int64    |
+--------------+--------------+---------------+-----------------+-------------------+---------------------+---------------+---------------+---------------+-------------+
| A            | F            | 37734107.00   | 56586554400.73  | 53758257134.8700  | 55909065222.827692  | 25.522006     | 38273.129735  | 0.049985      | 1478493     |
| N            | F            | 991417.00     | 1487504710.38   | 1413082168.0541   | 1469649223.194375   | 25.516472     | 38284.467761  | 0.050093      | 38854       |
| N            | O            | 73416597.00   | 110112303006.41 | 104608220776.3836 | 108796375788.183317 | 25.502438     | 38249.282778  | 0.049996      | 2878807     |
| R            | F            | 37719753.00   | 56568041380.90  | 53741292684.6040  | 55889619119.831932  | 25.505794     | 38250.854626  | 0.050009      | 1478870     |
+--------------+--------------+---------------+-----------------+-------------------+---------------------+---------------+---------------+---------------+-------------+

Time: 0.001090834 seconds. 4 rows (cached).
```

> **Note:** Because `spiceai/tpch` accelerates its datasets locally with DuckDB, the first (uncached) run already completes in tens of milliseconds. The cached run is still an order of magnitude faster, as the result is returned without planning or executing the query.

The cached result will expire 5 minutes after the initial query execution.

## (Optional) Step 5: Update the hashing algorithm

The hashing algorithm determines how cache keys are hashed before being stored, impacting both lookup speed and protection against potential DOS attacks. The Runtime supports a hashing algorithm of `xxh3` (default), `ahash`, `siphash`, `blake3`, `xxh32`, `xxh64`, or `xxh128`.

Stop the Spice Runtime using `Ctrl-C`. Update the `spicepod.yaml` to specify the `ahash` hashing algorithm in the results cache settings:

```yaml
runtime:
  caching:
    sql_results:
      enabled: true
      max_size: 128MiB
      item_ttl: 5m
      hashing_algorithm: ahash
```

Restart the Spice Runtime:

```bash
spice run
```

Observe the Spice runtime terminal for cache initialization. Example output:

```console
2026-08-13T12:10:12.236524Z  INFO runtime::init::caching: Initialized sql results cache; max size: 128.00 MiB, item ttl: 300s, hashing algorithm: Ahash, encoding: none
2026-08-13T12:10:51.184227Z  INFO runtime::init::dataset: Dataset tpch.customer registered (s3://spiceai-demo-datasets/tpch/customer/), acceleration (duckdb), results cache enabled. duration_ms=29
2026-08-13T12:10:52.402518Z  INFO runtime::init::dataset: Dataset tpch.lineitem registered (s3://spiceai-demo-datasets/tpch/lineitem/), acceleration (duckdb), results cache enabled. duration_ms=2
2026-08-13T12:10:53.188403Z  INFO runtime::init::dataset: Dataset tpch.nation registered (s3://spiceai-demo-datasets/tpch/nation/), acceleration (duckdb), results cache enabled. duration_ms=5
2026-08-13T12:10:54.327196Z  INFO runtime::init::dataset: Dataset tpch.orders registered (s3://spiceai-demo-datasets/tpch/orders/), acceleration (duckdb), results cache enabled. duration_ms=2
2026-08-13T12:10:55.498104Z  INFO runtime::init::dataset: Dataset tpch.part registered (s3://spiceai-demo-datasets/tpch/part/), acceleration (duckdb), results cache enabled. duration_ms=2
2026-08-13T12:10:56.611758Z  INFO runtime::init::dataset: Dataset tpch.partsupp registered (s3://spiceai-demo-datasets/tpch/partsupp/), acceleration (duckdb), results cache enabled. duration_ms=2
2026-08-13T12:10:57.368126Z  INFO runtime::init::dataset: Dataset tpch.region registered (s3://spiceai-demo-datasets/tpch/region/), acceleration (duckdb), results cache enabled. duration_ms=1
2026-08-13T12:10:58.418313Z  INFO runtime::init::dataset: Dataset tpch.supplier registered (s3://spiceai-demo-datasets/tpch/supplier/), acceleration (duckdb), results cache enabled. duration_ms=2
```

For more information about selecting an appropriate hashing algorithm, refer to the [Results Caching Documentation](https://docs.spiceai.org/features/caching)

## (Optional) Step 6: Use stale-while-revalidate caching

Spice supports [Stale-While-Revalidate](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cache-Control) caching behaviours by setting the [`stale_while_revalidate_ttl` property](https://spiceai.org/docs/features/caching#stale-while-revalidate) to a duration. By default, stale-while-revalidate behaviour is disabled.

Stop the Spice Runtime using `Ctrl-C`. Update the `spicepod.yaml` to specify the `stale_while_revalidate_ttl` property and update the `item_ttl` in the results cache settings:

```yaml
runtime:
  caching:
    sql_results:
      enabled: true
      max_size: 128MiB
      item_ttl: 10s
      hashing_algorithm: ahash
      stale_while_revalidate_ttl: 10s
```

Restart the Spice Runtime with verbose logging to view the background refreshes:

```bash
spice run -v
```

Wait until the Spice Runtime is ready, then start the Spice SQL REPL:

```bash
spice sql
```

Perform a simple query, which populates the cache for the first time:

```sql
SELECT COUNT(1) FROM tpch.nation;
```

```console
sql> SELECT COUNT(1) FROM tpch.nation;
+-----------------+
| count(Int64(1)) |
|      int64      |
+-----------------+
| 25              |
+-----------------+

Time: 0.014152333 seconds. 1 rows.
```

Perform the query again before 10 seconds pass, and the result will be returned from cache without a refresh:

```console
sql> SELECT COUNT(1) FROM tpch.nation;
+-----------------+
| count(Int64(1)) |
|      int64      |
+-----------------+
| 25              |
+-----------------+

Time: 0.000771375 seconds. 1 rows (cached).
```

After 10 seconds, but before 20 seconds, the result will still return from cache but the Spice Runtime will produce a debug log that a background refresh occurred:

```console
sql> SELECT COUNT(1) FROM tpch.nation;
+-----------------+
| count(Int64(1)) |
|      int64      |
+-----------------+
| 25              |
+-----------------+

Time: 0.001072708 seconds. 1 rows (cached).
```

```console
2026-08-13T12:11:52.215396Z DEBUG runtime::datafusion::query::cache: Cache entry is stale (beyond TTL), triggering background revalidation for stale-while-revalidate
2026-08-13T12:11:52.216617Z DEBUG runtime::datafusion::query::cache: Starting background revalidation task cache_key=8983958663055006108
2026-08-13T12:11:52.216655Z DEBUG runtime::datafusion::query::cache: Background revalidation: re-executing query with existing plan
2026-08-13T12:11:52.219391Z DEBUG runtime::datafusion::query::cache: Background revalidation completed successfully and cached cache_key=8983958663055006108
2026-08-13T12:11:52.219590Z DEBUG runtime::datafusion::query::cache: Background revalidation task completed cache_key=8983958663055006108
```

For more information about stale-while-revalidate caching, refer to the [Results Caching Documentation](https://spiceai.org/docs/features/caching)

## Additional Resources

- [Results Caching Documentation](https://docs.spiceai.org/features/caching)
