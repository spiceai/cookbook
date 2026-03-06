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

Wait until the runtime reports it is ready before continuing.

## Step 2: Add the TPC-H Benchmark Spicepod

In a separate terminal, in the `accelerated-views` directory, add the `spiceai/tpch` Spicepod:

```bash
spice add spiceai/tpch
```

Wait for `spice add` to complete successfully before continuing.

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

Wait for the view registration and initial refresh to complete before querying.

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
SELECT * FROM supplier_order_waits WHERE nation = 'SAUDI ARABIA' LIMIT 10;
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

```

Now query the same data using the created view and observe reduced latency due to pre-calculated results.

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

Observe periodic refresh log entries for the view.

## Additional Resources

- [Views Documentation](https://spiceai.org/docs/components/views)
