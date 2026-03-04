# Accelerated Views

This recipe demonstrates how to use accelerated [Views](https://spiceai.org/docs/components/views) to pre-calculate and materialize data derived from one or more underlying datasets. By defining views that aggregate, join, or transform source data in advance, you can significantly improve the performance of analytical queries. In this recipe, we will create a locally accelerated view for the [TPC-H Q21 - Suppliers Who Kept Orders Waiting](https://github.com/spiceai/cookbook/tree/trunk/tpc-h) report.

---

## Step 1: Initialize and Start Spice

Run the following commands to initialize and start the Spice runtime:

```bash
spice init accelerated-views
cd accelerated-views
spice run
```

Example output:

```bash
2025-05-18T19:55:04.208627Z  INFO spiced: Starting runtime v1.2.2+models.metal
2025-05-18T19:55:04.720993Z  INFO runtime::init::results_cache: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
2025-05-18T19:55:04.721098Z  INFO runtime::init::dataset: No datasets were configured. If this is unexpected, check the Spicepod configuration.
2025-05-18T19:55:04.721210Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2025-05-18T19:55:04.721306Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2025-05-18T19:55:04.721346Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2025-05-18T19:55:04.823688Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

## Step 2: Add the TPC-H Benchmark Spicepod

In a separate terminal, in the `accelerated-views` directory, add the `spiceai/tpch` Spicepod:

```bash
spice add spiceai/tpch
```

Example output:

```bash
2025-05-18T20:17:42.674632Z  INFO runtime::init::dataset: Dataset tpch.customer registered (s3://spiceai-demo-datasets/tpch/customer/), acceleration (duckdb), results cache enabled.
2025-05-18T20:17:42.677295Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset tpch.customer
2025-05-18T20:17:43.689020Z  INFO runtime::init::dataset: Dataset tpch.lineitem registered (s3://spiceai-demo-datasets/tpch/lineitem/), acceleration (duckdb), results cache enabled.
2025-05-18T20:17:43.691802Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset tpch.lineitem
2025-05-18T20:17:44.573390Z  INFO runtime::init::dataset: Dataset tpch.nation registered (s3://spiceai-demo-datasets/tpch/nation/), acceleration (duckdb), results cache enabled.
2025-05-18T20:17:44.575014Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset tpch.nation
2025-05-18T20:17:45.012944Z  INFO runtime::accelerated_table::refresh_task: Loaded 150,000 rows (33.72 MiB) for dataset tpch.customer in 2s 335ms.
2025-05-18T20:17:45.465199Z  INFO runtime::accelerated_table::refresh_task: Loaded 25 rows (3.35 kiB) for dataset tpch.nation in 890ms.
2025-05-18T20:17:45.579670Z  INFO runtime::init::dataset: Dataset tpch.orders registered (s3://spiceai-demo-datasets/tpch/orders/), acceleration (duckdb), results cache enabled.
2025-05-18T20:17:45.584503Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset tpch.orders
2025-05-18T20:17:46.861509Z  INFO runtime::init::dataset: Dataset tpch.part registered (s3://spiceai-demo-datasets/tpch/part/), acceleration (duckdb), results cache enabled.
2025-05-18T20:17:46.863911Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset tpch.part
2025-05-18T20:17:47.979505Z  INFO runtime::init::dataset: Dataset tpch.partsupp registered (s3://spiceai-demo-datasets/tpch/partsupp/), acceleration (duckdb), results cache enabled.
2025-05-18T20:17:47.981985Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset tpch.partsupp
2025-05-18T20:17:48.661190Z  INFO runtime::accelerated_table::refresh_task: Loaded 200,000 rows (35.76 MiB) for dataset tpch.part in 1s 797ms.
2025-05-18T20:17:48.947079Z  INFO runtime::init::dataset: Dataset tpch.region registered (s3://spiceai-demo-datasets/tpch/region/), acceleration (duckdb), results cache enabled.
2025-05-18T20:17:48.949633Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset tpch.region
2025-05-18T20:17:49.863619Z  INFO runtime::accelerated_table::refresh_task: Loaded 5 rows (1008.00 B) for dataset tpch.region in 913ms.
2025-05-18T20:17:49.979310Z  INFO runtime::init::dataset: Dataset tpch.supplier registered (s3://spiceai-demo-datasets/tpch/supplier/), acceleration (duckdb), results cache enabled.
2025-05-18T20:17:49.980156Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset tpch.supplier
2025-05-18T20:17:51.387183Z  INFO runtime::accelerated_table::refresh_task: Loaded 10,000 rows (1.83 MiB) for dataset tpch.supplier in 1s 407ms.
2025-05-18T20:17:52.873917Z  INFO runtime::accelerated_table::refresh_task: Loaded 800,000 rows (141.47 MiB) for dataset tpch.partsupp in 4s 891ms.
2025-05-18T20:18:01.715009Z  INFO runtime::accelerated_table::refresh_task: Loaded 6,001,215 rows (1.07 GiB) for dataset tpch.lineitem in 18s 23ms.
2025-05-18T20:18:01.862647Z  INFO runtime::accelerated_table::refresh_task: Loaded 1,500,000 rows (212.25 MiB) for dataset tpch.orders in 16s 278ms
```

## Step 3: Create View

Add a view definition representing _TPC-H Q21 - Suppliers Who Kept Orders Waiting_. We enable local acceleration for the view so it stores a locally materialized version of the query results:

```shell
cat <<'EOF' >> spicepod.yaml

views:
  - name: supplier_order_waits
    acceleration: 
      enabled: true
      refresh_check_interval: 1h
      engine: duckdb

    sql: |
      SELECT
          s_name,
          n_name AS nation,
          COUNT(*) AS numwait
      FROM
          tpch.supplier,
          tpch.lineitem l1,
          tpch.orders,
          tpch.nation
      WHERE
          s_suppkey = l1.l_suppkey
          AND o_orderkey = l1.l_orderkey
          AND o_orderstatus = 'F'
          AND l1.l_receiptdate > l1.l_commitdate
          AND EXISTS (
              SELECT
                  *
              FROM
                  tpch.lineitem l2
              WHERE
                  l2.l_orderkey = l1.l_orderkey
                  AND l2.l_suppkey <> l1.l_suppkey
          )
          AND NOT EXISTS (
              SELECT
                  *
              FROM
                  tpch.lineitem l3
              WHERE
                  l3.l_orderkey = l1.l_orderkey
                  AND l3.l_suppkey <> l1.l_suppkey
                  AND l3.l_receiptdate > l3.l_commitdate
          )
          AND s_nationkey = n_nationkey
      GROUP BY
          s_name,
          n_name
      ORDER BY
          numwait DESC,
          s_name;
EOF
```

Example output:

```bash
2025-05-18T20:20:11.150665Z  INFO runtime::datafusion: View supplier_order_waits registered, acceleration (duckdb, 3600s refresh).
2025-05-18T20:20:11.151971Z  INFO runtime::accelerated_table::refresh_task: Loading data for view supplier_order_waits
2025-05-18T20:20:12.414223Z  INFO runtime::accelerated_table::refresh_task: Loaded 10,000 rows (481.43 kiB) for view supplier_order_waits in 1s 262ms.
```

## Step 4: Run Queries

Start the Spice SQL REPL:

```bash
spice sql
```

Review view content:

```sql
SELECT * FROM supplier_order_waits LIMIT 5;
```

```console
+--------------------+------------+---------+
| s_name             | nation     | numwait |
+--------------------+------------+---------+
| Supplier#000002340 | INDIA      | 25      |
| Supplier#000003591 | JAPAN      | 24      |
| Supplier#000000014 | MOROCCO    | 23      |
| Supplier#000001915 | JORDAN     | 23      |
| Supplier#000007754 | MOZAMBIQUE | 23      |
+--------------------+------------+---------+
```

Run the _Suppliers Who Kept Orders Waiting Query (Q21)_ directly:

```sql
SELECT
    s_name,
    n_name AS nation,
    COUNT(*) AS numwait
FROM
    tpch.supplier,
    tpch.lineitem l1,
    tpch.orders,
    tpch.nation
WHERE
    s_suppkey = l1.l_suppkey
    AND o_orderkey = l1.l_orderkey
    AND o_orderstatus = 'F'
    AND l1.l_receiptdate > l1.l_commitdate
    AND EXISTS (
        SELECT
            *
        FROM
            tpch.lineitem l2
        WHERE
            l2.l_orderkey = l1.l_orderkey
            AND l2.l_suppkey <> l1.l_suppkey
    )
    AND NOT EXISTS (
        SELECT
            *
        FROM
            tpch.lineitem l3
        WHERE
            l3.l_orderkey = l1.l_orderkey
            AND l3.l_suppkey <> l1.l_suppkey
            AND l3.l_receiptdate > l3.l_commitdate
    )
    AND s_nationkey = n_nationkey
    AND n_name = 'SAUDI ARABIA'
GROUP BY
    s_name,
    n_name
ORDER BY
    numwait DESC,
    s_name
LIMIT 10;
```

Observe the query execution time.

```console
+--------------------+--------------+---------+
| s_name             | nation       | numwait |
+--------------------+--------------+---------+
| Supplier#000002829 | SAUDI ARABIA | 20      |
| Supplier#000005808 | SAUDI ARABIA | 18      |
| Supplier#000000262 | SAUDI ARABIA | 17      |
| Supplier#000000496 | SAUDI ARABIA | 17      |
| Supplier#000002160 | SAUDI ARABIA | 17      |
| Supplier#000002301 | SAUDI ARABIA | 17      |
| Supplier#000002540 | SAUDI ARABIA | 17      |
| Supplier#000003063 | SAUDI ARABIA | 17      |
| Supplier#000005178 | SAUDI ARABIA | 17      |
| Supplier#000008331 | SAUDI ARABIA | 17      |
+--------------------+--------------+---------+

Time: 0.259203917 seconds. 10 rows.
```

Now query the same data using the created view and observe a significant reduction in query execution time, from **0.259203917** to **0.005394292** seconds, due to the result being retrieved from pre-calculated data.

```sql
SELECT * FROM supplier_order_waits WHERE nation = 'SAUDI ARABIA' LIMIT 10;
```

```console
+--------------------+--------------+---------+
| s_name             | nation       | numwait |
+--------------------+--------------+---------+
| Supplier#000002829 | SAUDI ARABIA | 20      |
| Supplier#000005808 | SAUDI ARABIA | 18      |
| Supplier#000000262 | SAUDI ARABIA | 17      |
| Supplier#000000496 | SAUDI ARABIA | 17      |
| Supplier#000002160 | SAUDI ARABIA | 17      |
| Supplier#000002301 | SAUDI ARABIA | 17      |
| Supplier#000002540 | SAUDI ARABIA | 17      |
| Supplier#000003063 | SAUDI ARABIA | 17      |
| Supplier#000005178 | SAUDI ARABIA | 17      |
| Supplier#000008331 | SAUDI ARABIA | 17      |
+--------------------+--------------+---------+

Time: 0.005394292 seconds. 10 rows.
```

## Step 5 (optional): Refresh on a defined schedule

Accelerated views support refreshing on a cron schedule.

Stop the Spice Runtime, then update the spicepod to remove the `acceleration.refresh_check_interval` from the view.

Define a new `acceleration.refresh_cron` for the view with a value of `* * * * *` to refresh every minute.

Example view spicepod:

```yaml
views:
  - name: supplier_order_waits
    acceleration: 
      enabled: true
      refresh_cron: "* * * * *"
      engine: duckdb

    sql: |
    ...
```

Start the Spice Runtime, and observe scheduled refreshes:

```bash
spice run
```

Example output:

```bash
2025-05-18T20:20:11.150665Z  INFO runtime::datafusion: View supplier_order_waits registered, acceleration (duckdb, 3600s refresh).
2025-05-18T20:20:11.151971Z  INFO runtime::accelerated_table::refresh_task: Loading data for view supplier_order_waits
2025-05-18T20:20:12.414223Z  INFO runtime::accelerated_table::refresh_task: Loaded 10,000 rows (481.43 kiB) for view supplier_order_waits in 1s 262ms.
2025-05-18T20:21:00.151971Z  INFO runtime::accelerated_table::refresh_task: Loading data for view supplier_order_waits
2025-05-18T20:21:01.414223Z  INFO runtime::accelerated_table::refresh_task: Loaded 10,000 rows (481.43 kiB) for view supplier_order_waits in 1s 262ms.
```

## Additional Resources

- [Views Documentation](https://spiceai.org/docs/components/views)
