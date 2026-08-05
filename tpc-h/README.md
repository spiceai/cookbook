# TPC-H Benchmark Sample Data

Works with `v1.0+`

> TPC-H is a decision support benchmark. It consists of a suite of business-oriented ad hoc queries and concurrent data modifications. The queries and the data populating the database have been chosen to have broad industry-wide relevance. This benchmark illustrates decision support systems that examine large volumes of data, execute queries with a high degree of complexity, and give answers to critical business questions.
>
> - [TPC Benchmark™ H (TPC-H)](https://www.tpc.org/tpch/)

**Step 1.** Initialize and start Spice

```bash
spice init tpch-recipe
```

```bash
cd tpch-recipe
spice run
```

**Step 2.** Add the TPC-H Benchmark pod

```bash
spice add spiceai/tpch
```

The following output is shown in the Spice runtime terminal:

```bash
2026-08-05T12:12:47.811362Z  INFO runtime::init::dataset: Dataset tpch.customer registered (s3://spiceai-demo-datasets/tpch/customer/), acceleration (duckdb), results cache enabled.
2026-08-05T12:12:47.812658Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset tpch.customer
2026-08-05T12:12:49.605443Z  INFO runtime::init::dataset: Dataset tpch.lineitem registered (s3://spiceai-demo-datasets/tpch/lineitem/), acceleration (duckdb), results cache enabled.
2026-08-05T12:12:49.606500Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset tpch.lineitem
2026-08-05T12:12:50.409819Z  INFO runtime::init::dataset: Dataset tpch.nation registered (s3://spiceai-demo-datasets/tpch/nation/), acceleration (duckdb), results cache enabled.
2026-08-05T12:12:50.410648Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset tpch.nation
2026-08-05T12:12:50.524894Z  INFO runtime::accelerated_table::refresh_task: Loaded 150,000 rows (33.76 MiB) for dataset tpch.customer in 2s 712ms.
2026-08-05T12:12:50.970014Z  INFO runtime::accelerated_table::refresh_task: Loaded 25 rows (3.35 kiB) for dataset tpch.nation in 559ms.
2026-08-05T12:12:51.591911Z  INFO runtime::init::dataset: Dataset tpch.orders registered (s3://spiceai-demo-datasets/tpch/orders/), acceleration (duckdb), results cache enabled.
2026-08-05T12:12:51.592095Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset tpch.orders
2026-08-05T12:12:52.822669Z  INFO runtime::init::dataset: Dataset tpch.part registered (s3://spiceai-demo-datasets/tpch/part/), acceleration (duckdb), results cache enabled.
2026-08-05T12:12:52.823043Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset tpch.part
2026-08-05T12:12:53.982557Z  INFO runtime::init::dataset: Dataset tpch.partsupp registered (s3://spiceai-demo-datasets/tpch/partsupp/), acceleration (duckdb), results cache enabled.
2026-08-05T12:12:53.983000Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset tpch.partsupp
2026-08-05T12:12:54.160528Z  INFO runtime::accelerated_table::refresh_task: Loaded 200,000 rows (35.80 MiB) for dataset tpch.part in 1s 337ms.
2026-08-05T12:12:54.829053Z  INFO runtime::init::dataset: Dataset tpch.region registered (s3://spiceai-demo-datasets/tpch/region/), acceleration (duckdb), results cache enabled.
2026-08-05T12:12:54.829967Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset tpch.region
2026-08-05T12:12:55.402071Z  INFO runtime::accelerated_table::refresh_task: Loaded 5 rows (1008.00 B) for dataset tpch.region in 572ms.
2026-08-05T12:12:56.036613Z  INFO runtime::init::dataset: Dataset tpch.supplier registered (s3://spiceai-demo-datasets/tpch/supplier/), acceleration (duckdb), results cache enabled.
2026-08-05T12:12:56.036896Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset tpch.supplier
2026-08-05T12:12:56.397026Z  INFO runtime::accelerated_table::refresh_task: Loaded 800,000 rows (141.48 MiB) for dataset tpch.partsupp in 2s 414ms.
2026-08-05T12:12:57.340627Z  INFO runtime::accelerated_table::refresh_task: Loaded 10,000 rows (1.87 MiB) for dataset tpch.supplier in 1s 303ms.
2026-08-05T12:13:12.771851Z  INFO runtime::accelerated_table::refresh_task: Loaded 6,001,215 rows (1.07 GiB) for dataset tpch.lineitem in 23s 165ms.
2026-08-05T12:13:16.294713Z  INFO runtime::accelerated_table::refresh_task: Loaded 1,500,000 rows (212.28 MiB) for dataset tpch.orders in 24s 702ms.
```

**Step 3.** Run queries against the dataset using the Spice SQL REPL.

In a new terminal, start the Spice SQL REPL.

```bash
spice sql
```

Check that TPC-H tables exist:

```sql
show tables;

+---------------+--------------+--------------+------------+
| table_catalog | table_schema | table_name   | table_type |
+---------------+--------------+--------------+------------+
| spice         | runtime      | task_history | BASE TABLE |
| spice         | tpch         | customer     | BASE TABLE |
| spice         | tpch         | region       | BASE TABLE |
| spice         | tpch         | lineitem     | BASE TABLE |
| spice         | tpch         | partsupp     | BASE TABLE |
| spice         | tpch         | part         | BASE TABLE |
| spice         | tpch         | nation       | BASE TABLE |
| spice         | tpch         | orders       | BASE TABLE |
| spice         | tpch         | supplier     | BASE TABLE |
+---------------+--------------+--------------+------------+

Time: 0.006163958 seconds. 9 rows.
```

Run _Pricing Summary Report Query (Q1)_. More information about TPC-H and all the queries involved can be found in the official [TPC Benchmark H Standard Specification](https://www.tpc.org/tpc_documents_current_versions/pdf/tpc-h_v2.17.1.pdf).

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

```sql
+--------------+--------------+-------------+-----------------+-------------------+---------------------+-----------+--------------+----------+-------------+
| l_returnflag | l_linestatus | sum_qty     | sum_base_price  | sum_disc_price    | sum_charge          | avg_qty   | avg_price    | avg_disc | count_order |
+--------------+--------------+-------------+-----------------+-------------------+---------------------+-----------+--------------+----------+-------------+
| A            | F            | 37734107.00 | 56586554400.73  | 53758257134.8700  | 55909065222.827692  | 25.522006 | 38273.129735 | 0.049985 | 1478493     |
| N            | F            | 991417.00   | 1487504710.38   | 1413082168.0541   | 1469649223.194375   | 25.516472 | 38284.467761 | 0.050093 | 38854       |
| N            | O            | 73416597.00 | 110112303006.41 | 104608220776.3836 | 108796375788.183317 | 25.502438 | 38249.282778 | 0.049996 | 2878807     |
| R            | F            | 37719753.00 | 56568041380.90  | 53741292684.6040  | 55889619119.831932  | 25.505794 | 38250.854626 | 0.050009 | 1478870     |
+--------------+--------------+-------------+-----------------+-------------------+---------------------+-----------+--------------+----------+-------------+

Time: 0.127478459 seconds. 4 rows.
```
