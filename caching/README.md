# In-Memory Results Caching

> Spice.ai OSS supports in-memory caching of query results.
> Results caching can help improve performance for bursts of requests and for non-accelerated results such as refresh data returned [on zero results](https://docs.spiceai.org/data-accelerators/data-refresh#behavior-on-zero-results).
>
> [Spice.ai OSS Docs: Results Caching](https://docs.spiceai.org/features/caching)

The recipe will use [TPC-H Benchmark Sample Data](https://github.com/spiceai/cookbook/tree/trunk/tpc-h), but instead of using local acceleration, we will leverage in-memory caching to boost query performance.

**Step 1.** Initialize and start Spice

```bash
spice init cache-recipe
```

```bash
cd cache-recipe
spice run
```

**Step 2.** Add the TPC-H Benchmark Spicepod

In a separate terminal, using the same directory, add the TPC-H Benchmark Spicepod to the project.

```bash
cd cache-recipe
spice add spiceai/tpch
```

The following output is shown in the Spice runtime terminal:

```bash
2024-08-05T05:25:10.627005Z  INFO runtime::metrics_server: Spice Runtime Metrics listening on 127.0.0.1:9090
2024-08-05T05:25:10.628875Z  INFO runtime: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
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
2024-08-05T05:25:10.628875Z  INFO runtime: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
```

**Step 3.** Increase the cached items' expiration time

Using `Ctrl-C`, stop Spice and use a text editor to open the `spicepod.yaml` file. Add a custom in-memory caching configuration below to increase the cached items' duration to `5 minutes`. Read [Spice.ai OSS Docs: Results Caching](https://docs.spiceai.org/features/caching) to learn more about the available configuration parameters.

Before:

```yaml
version: v1beta1
kind: Spicepod
name: cache-recipe
dependencies:
- spiceai/tpch
```

After:

```yaml
version: v1beta1
kind: Spicepod
name: cache-recipe

runtime:
  results_cache:
    enabled: true
    cache_max_size: 128MiB
    eviction_policy: lru 
    item_ttl: 5m

dependencies:
- spiceai/tpch
```

Run Spice

```bash
spice run
```

The following output is shown in the Spice runtime terminal, confirming the updated in-memory caching settings (`300s`):

```bash
2024-08-05T05:29:06.876281Z  INFO runtime::metrics_server: Spice Runtime Metrics listening on 127.0.0.1:9090
2024-08-05T05:29:06.876579Z  INFO runtime: Initialized results cache; max size: 128.00 MiB, item ttl: 300s
2024-08-05T05:29:08.395163Z  INFO runtime: Dataset region registered (s3://spiceai-demo-datasets/tpch/region/), results cache enabled.
2024-08-05T05:29:08.399137Z  INFO runtime: Dataset nation registered (s3://spiceai-demo-datasets/tpch/nation/), results cache enabled.
2024-08-05T05:29:08.399887Z  INFO runtime: Dataset supplier registered (s3://spiceai-demo-datasets/tpch/supplier/), results cache enabled.
2024-08-05T05:29:08.402294Z  INFO runtime: Dataset orders registered (s3://spiceai-demo-datasets/tpch/orders/), results cache enabled.
2024-08-05T05:29:08.404676Z  INFO runtime: Dataset partsupp registered (s3://spiceai-demo-datasets/tpch/partsupp/), results cache enabled.
2024-08-05T05:29:08.533932Z  INFO runtime: Dataset part registered (s3://spiceai-demo-datasets/tpch/part/), results cache enabled.
2024-08-05T05:29:08.573218Z  INFO runtime: Dataset lineitem registered (s3://spiceai-demo-datasets/tpch/lineitem/), results cache enabled.
2024-08-05T05:29:08.712402Z  INFO runtime: Dataset customer registered (s3://spiceai-demo-datasets/tpch/customer/), results cache enabled.
```

**Step 3.** Run queries against the dataset using the Spice SQL REPL.

In a new terminal, start the Spice SQL REPL.

```bash
spice sql
```

Run *Pricing Summary Report Query (Q1)*. More information about TPC-H and all the queries involved can be found in the official [TPC Benchmark H Standard Specification](https://www.tpc.org/tpc_documents_current_versions/pdf/tpc-h_v2.17.1.pdf).

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
  lineitem
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

Output:

```sql
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

Execute the same query again and observe a significant reduction in query execution time, from **4.178523666** to **0.004944792** seconds, due to the result being retrieved from the in-memory cache. The cached item will expire 5 minutes after the initial query execution.

```sql
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
