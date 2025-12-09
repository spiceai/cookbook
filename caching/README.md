# In-Memory Results Caching

> Spice.ai OSS supports in-memory caching of query results to improve performance for bursts of requests and non-accelerated results, such as refresh data returned [on zero results](https://docs.spiceai.org/data-accelerators/data-refresh#behavior-on-zero-results).
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
2024-08-05T05:25:10.627005Z  INFO runtime::metrics_server: Spice Runtime Metrics listening on 127.0.0.1:9090
2024-08-05T05:25:10.628875Z  INFO runtime: Initialized results cache; max size: 128.00 MiB, item ttl: 1s, hashing algorithm: XXH3, encoding: none
2024-08-05T05:26:50.262092Z  INFO runtime: Dataset customer registered (s3://spiceai-demo-datasets/tpch/customer/), results cache enabled.
2024-08-05T05:26:51.569841Z  INFO runtime: Dataset lineitem registered (s3://spiceai-demo-datasets/tpch/lineitem/), results cache enabled.
2024-08-05T05:26:52.871013Z  INFO runtime: Dataset nation registered (s3://spiceai-demo-datasets/tpch/nation/), results cache enabled.
2024-08-05T05:26:54.201229Z  INFO runtime: Dataset orders registered (s3://spiceai-demo-datasets/tpch/orders/), results cache enabled.
2024-08-05T05:26:55.583954Z  INFO runtime: Dataset part registered (s3://spiceai-demo-datasets/tpch/part/), results cache enabled.
2024-08-05T05:26:56.933827Z  INFO runtime: Dataset partsupp registered (s3://spiceai-demo-datasets/tpch/partsupp/), results cache enabled.
2024-08-05T05:26:58.182547Z  INFO runtime: Dataset region registered (s3://spiceai-demo-datasets/tpch/region/), results cache enabled.
2024-08-05T05:26:59.501475Z  INFO runtime: Dataset supplier registered (s3://spiceai-demo-datasets/tpch/supplier/), results cache enabled.
```

Notice the following line confirming the default cache configuration with cached items expiration time of 1 second is loaded.

```bash
2024-08-05T05:25:10.628875Z  INFO runtime: Initialized results cache; max size: 128.00 MiB, item ttl: 1s, hashing algorithm: XXH3, encoding: none
```

## Step 3: Update Cache Configuration

Stop the Spice runtime using `Ctrl-C`. Open the `spicepod.yaml` file and add a custom cache configuration to increase the cached items' expiration time to 5 minutes.

**Before:**

```yaml
version: v1
kind: Spicepod
name: cache-recipe
dependencies:
  - spiceai/tpch
```

**After:**

```yaml
version: v1
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

Verify the following output is shown in the Spice runtime terminal, confirming that the updated in-memory caching settings (`Initialized results cache; max size: 128.00 MiB, item ttl: 300s`) were applied:

```bash
2024-08-05T05:29:06.876281Z  INFO runtime::metrics_server: Spice Runtime Metrics listening on 127.0.0.1:9090
2024-08-05T05:29:06.876579Z  INFO runtime: Initialized results cache; max size: 128.00 MiB, item ttl: 300s, hashing algorithm: XXH3, encoding: none
2024-08-05T05:29:08.395163Z  INFO runtime: Dataset region registered (s3://spiceai-demo-datasets/tpch/region/), results cache enabled.
2024-08-05T05:29:08.399137Z  INFO runtime: Dataset nation registered (s3://spiceai-demo-datasets/tpch/nation/), results cache enabled.
2024-08-05T05:29:08.399887Z  INFO runtime: Dataset supplier registered (s3://spiceai-demo-datasets/tpch/supplier/), results cache enabled.
2024-08-05T05:29:08.402294Z  INFO runtime: Dataset orders registered (s3://spiceai-demo-datasets/tpch/orders/), results cache enabled.
2024-08-05T05:29:08.404676Z  INFO runtime: Dataset partsupp registered (s3://spiceai-demo-datasets/tpch/partsupp/), results cache enabled.
2024-08-05T05:29:08.533932Z  INFO runtime: Dataset part registered (s3://spiceai-demo-datasets/tpch/part/), results cache enabled.
2024-08-05T05:29:08.573218Z  INFO runtime: Dataset lineitem registered (s3://spiceai-demo-datasets/tpch/lineitem/), results cache enabled.
2024-08-05T05:29:08.712402Z  INFO runtime: Dataset customer registered (s3://spiceai-demo-datasets/tpch/customer/), results cache enabled.
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
+--------------+--------------+-------------+-----------------+-------------------+---------------------+-----------+--------------+----------+-------------+
| l_returnflag | l_linestatus | sum_qty     | sum_base_price  | sum_disc_price    | sum_charge          | avg_qty   | avg_price    | avg_disc | count_order |
+--------------+--------------+-------------+-----------------+-------------------+---------------------+-----------+--------------+----------+-------------+
| A            | F            | 37734107.00 | 56586554400.73  | 53758257134.8700  | 55909065222.827692  | 25.522005 | 38273.129734 | 0.049985 | 1478493     |
| N            | F            | 991417.00   | 1487504710.38   | 1413082168.0541   | 1469649223.194375   | 25.516471 | 38284.467760 | 0.050093 | 38854       |
| N            | O            | 73416597.00 | 110112303006.41 | 104608220776.3836 | 108796375788.183317 | 25.502437 | 38249.282778 | 0.049996 | 2878807     |
| R            | F            | 37719753.00 | 56568041380.90  | 53741292684.6040  | 55889619119.831932  | 25.505793 | 38250.854626 | 0.050009 | 1478870     |
+--------------+--------------+-------------+-----------------+-------------------+---------------------+-----------+--------------+----------+-------------+

Time: 4.178523666 seconds. 4 rows.
```

Execute the same query again and observe a significant reduction in query execution time, from **4.178523666** to **0.004944792** seconds, due to the result being retrieved from the in-memory cache. The cached item will expire 5 minutes after the initial query execution. Cached run:

```console
+--------------+--------------+-------------+-----------------+-------------------+---------------------+-----------+--------------+----------+-------------+
| l_returnflag | l_linestatus | sum_qty     | sum_base_price  | sum_disc_price    | sum_charge          | avg_qty   | avg_price    | avg_disc | count_order |
+--------------+--------------+-------------+-----------------+-------------------+---------------------+-----------+--------------+----------+-------------+
| A            | F            | 37734107.00 | 56586554400.73  | 53758257134.8700  | 55909065222.827692  | 25.522005 | 38273.129734 | 0.049985 | 1478493     |
| N            | F            | 991417.00   | 1487504710.38   | 1413082168.0541   | 1469649223.194375   | 25.516471 | 38284.467760 | 0.050093 | 38854       |
| N            | O            | 73416597.00 | 110112303006.41 | 104608220776.3836 | 108796375788.183317 | 25.502437 | 38249.282778 | 0.049996 | 2878807     |
| R            | F            | 37719753.00 | 56568041380.90  | 53741292684.6040  | 55889619119.831932  | 25.505793 | 38250.854626 | 0.050009 | 1478870     |
+--------------+--------------+-------------+-----------------+-------------------+---------------------+-----------+--------------+----------+-------------+

Time: 0.004944792 seconds. 4 rows (cached).
```

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
2024-08-05T05:25:10.627005Z  INFO runtime::metrics_server: Spice Runtime Metrics listening on 127.0.0.1:9090
2024-08-05T05:25:10.628875Z  INFO runtime: Initialized results cache; max size: 128.00 MiB, item ttl: 300s, hashing algorithm: Ahash, encoding: none
2024-08-05T05:26:50.262092Z  INFO runtime: Dataset customer registered (s3://spiceai-demo-datasets/tpch/customer/), results cache enabled.
2024-08-05T05:26:51.569841Z  INFO runtime: Dataset lineitem registered (s3://spiceai-demo-datasets/tpch/lineitem/), results cache enabled.
2024-08-05T05:26:52.871013Z  INFO runtime: Dataset nation registered (s3://spiceai-demo-datasets/tpch/nation/), results cache enabled.
2024-08-05T05:26:54.201229Z  INFO runtime: Dataset orders registered (s3://spiceai-demo-datasets/tpch/orders/), results cache enabled.
2024-08-05T05:26:55.583954Z  INFO runtime: Dataset part registered (s3://spiceai-demo-datasets/tpch/part/), results cache enabled.
2024-08-05T05:26:56.933827Z  INFO runtime: Dataset partsupp registered (s3://spiceai-demo-datasets/tpch/partsupp/), results cache enabled.
2024-08-05T05:26:58.182547Z  INFO runtime: Dataset region registered (s3://spiceai-demo-datasets/tpch/region/), results cache enabled.
2024-08-05T05:26:59.501475Z  INFO runtime: Dataset supplier registered (s3://spiceai-demo-datasets/tpch/supplier/), results cache enabled.
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
+-----------------+
| 25              |
+-----------------+

Time: 0.010650365 seconds. 1 rows.
```

Perform the query again before 10 seconds pass, and the result will be returned from cache without a refresh:

```console
sql> SELECT COUNT(1) FROM tpch.nation;
+-----------------+
| count(Int64(1)) |
+-----------------+
| 25              |
+-----------------+

Time: 0.002846184 seconds. 1 rows (cached).
```

After 10 seconds, but before 20 seconds, the result will still return from cache but the Spice Runtime will produce a debug log that a background refresh occurred:

```console
sql> SELECT COUNT(1) FROM tpch.nation;
+-----------------+
| count(Int64(1)) |
+-----------------+
| 25              |
+-----------------+

Time: 0.002767147 seconds. 1 rows (cached).
```

```console
2025-12-09T04:15:33.356304Z DEBUG runtime::datafusion::query::cache: Cache entry is stale (beyond TTL), triggering background revalidation for stale-while-revalidate
2025-12-09T04:15:33.356535Z DEBUG runtime::datafusion::query::cache: Starting background revalidation task cache_key=4682376472860759847
2025-12-09T04:15:33.356546Z DEBUG runtime::datafusion::query::cache: Background revalidation: re-executing query with existing plan
2025-12-09T04:15:33.356946Z DEBUG datafusion_optimizer::analyzer: Analyzer took 0 ms
2025-12-09T04:15:33.356978Z DEBUG datafusion_optimizer::analyzer: Analyzer took 0 ms
2025-12-09T04:15:33.357554Z DEBUG datafusion_table_providers::sql::db_connection_pool::duckdbpool: DuckDB connection setup: SET order_by_non_integer_literal = true
2025-12-09T04:15:33.357941Z DEBUG datafusion_table_providers::sql::db_connection_pool::duckdbpool: DuckDB connection setup: SET TimeZone = UTC
2025-12-09T04:15:33.359580Z DEBUG runtime::datafusion::query::cache: Background query execution succeeded, collecting batches cache_key=4682376472860759847
2025-12-09T04:15:33.365280Z DEBUG runtime::datafusion::query::cache: Collected batches, now caching cache_key=4682376472860759847 num_batches=1
2025-12-09T04:15:33.365303Z DEBUG runtime::datafusion::query::cache: Background revalidation completed successfully and cached cache_key=4682376472860759847
2025-12-09T04:15:33.365310Z DEBUG runtime::datafusion::query::cache: Background revalidation task completed cache_key=4682376472860759847
```

For more information about stale-while-revalidate caching, refer to the [Results Caching Documentation](https://spiceai.org/docs/features/caching)

## Additional Resources

- [Results Caching Documentation](https://docs.spiceai.org/features/caching)
