# TPC-H Benchmark Sample Data

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
2024/12/31 09:36:45 INFO Checking for latest Spice runtime release...
2024/12/31 09:36:45 INFO Spice.ai runtime starting...
2024-12-31T00:36:46.690599Z  INFO runtime::init::dataset: No datasets were configured. If this is unexpected, check the Spicepod configuration.
2024-12-31T00:36:46.690681Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2024-12-31T00:36:46.690713Z  INFO runtime::metrics_server: Spice Runtime Metrics listening on 127.0.0.1:9090
2024-12-31T00:36:46.691410Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2024-12-31T00:36:46.692600Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2024-12-31T00:36:46.887621Z  INFO runtime::init::results_cache: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
2024-12-31T00:36:59.368743Z  INFO runtime::init::dataset: Dataset tpch.customer registered (s3://spiceai-demo-datasets/tpch/customer/), acceleration (arrow), results cache enabled.
2024-12-31T00:36:59.373278Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset tpch.customer
2024-12-31T00:37:01.613375Z  INFO runtime::init::dataset: Dataset tpch.lineitem registered (s3://spiceai-demo-datasets/tpch/lineitem/), acceleration (arrow), results cache enabled.
2024-12-31T00:37:01.616682Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset tpch.lineitem
2024-12-31T00:37:03.657908Z  INFO runtime::init::dataset: Dataset tpch.nation registered (s3://spiceai-demo-datasets/tpch/nation/), acceleration (arrow), results cache enabled.
2024-12-31T00:37:03.661211Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset tpch.nation
2024-12-31T00:37:04.555006Z  INFO runtime::accelerated_table::refresh_task: Loaded 150,000 rows (102.50 MiB) for dataset tpch.customer in 5s 181ms.
2024-12-31T00:37:05.550729Z  INFO runtime::accelerated_table::refresh_task: Loaded 25 rows (3.80 kiB) for dataset tpch.nation in 1s 889ms.
2024-12-31T00:37:05.986097Z  INFO runtime::init::dataset: Dataset tpch.orders registered (s3://spiceai-demo-datasets/tpch/orders/), acceleration (arrow), results cache enabled.
2024-12-31T00:37:05.988902Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset tpch.orders
2024-12-31T00:37:08.124169Z  INFO runtime::init::dataset: Dataset tpch.part registered (s3://spiceai-demo-datasets/tpch/part/), acceleration (arrow), results cache enabled.
2024-12-31T00:37:08.125948Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset tpch.part
2024-12-31T00:37:10.331999Z  INFO runtime::init::dataset: Dataset tpch.partsupp registered (s3://spiceai-demo-datasets/tpch/partsupp/), acceleration (arrow), results cache enabled.
2024-12-31T00:37:10.333913Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset tpch.partsupp
2024-12-31T00:37:12.375223Z  INFO runtime::init::dataset: Dataset tpch.region registered (s3://spiceai-demo-datasets/tpch/region/), acceleration (arrow), results cache enabled.
2024-12-31T00:37:12.377626Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset tpch.region
2024-12-31T00:37:12.526294Z  INFO runtime::accelerated_table::refresh_task: Loaded 200,000 rows (76.59 MiB) for dataset tpch.part in 4s 400ms.
2024-12-31T00:37:14.225651Z  INFO runtime::accelerated_table::refresh_task: Loaded 5 rows (1016.00 B) for dataset tpch.region in 1s 848ms.
2024-12-31T00:37:14.598651Z  INFO runtime::init::dataset: Dataset tpch.supplier registered (s3://spiceai-demo-datasets/tpch/supplier/), acceleration (arrow), results cache enabled.
2024-12-31T00:37:14.599904Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset tpch.supplier
2024-12-31T00:37:17.423852Z  INFO runtime::accelerated_table::refresh_task: Loaded 10,000 rows (3.46 MiB) for dataset tpch.supplier in 2s 823ms.
2024-12-31T00:37:20.287682Z  INFO runtime::accelerated_table::refresh_task: Loaded 800,000 rows (227.25 MiB) for dataset tpch.partsupp in 9s 953ms.
2024-12-31T00:37:26.427600Z  INFO runtime::accelerated_table::refresh_task: Loaded 1,500,000 rows (366.86 MiB) for dataset tpch.orders in 20s 438ms.
2024-12-31T00:37:32.034745Z  INFO runtime::accelerated_table::refresh_task: Loaded 6,001,215 rows (1.83 GiB) for dataset tpch.lineitem in 30s 418ms.
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
| spice         | runtime      | metrics      | BASE TABLE |
| spice         | public       | customer     | BASE TABLE |
| spice         | public       | region       | BASE TABLE |
| spice         | public       | lineitem     | BASE TABLE |
| spice         | public       | partsupp     | BASE TABLE |
| spice         | public       | part         | BASE TABLE |
| spice         | public       | nation       | BASE TABLE |
| spice         | public       | orders       | BASE TABLE |
| spice         | public       | supplier     | BASE TABLE |
+---------------+--------------+--------------+------------+

Time: 0.006163958 seconds. 9 rows.
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
| A            | F            | 37734107.00 | 56586554400.73  | 53758257134.8700  | 55909065222.827692  | 25.522005 | 38273.129734 | 0.049985 | 1478493     |
| N            | F            | 991417.00   | 1487504710.38   | 1413082168.0541   | 1469649223.194375   | 25.516471 | 38284.467760 | 0.050093 | 38854       |
| N            | O            | 73416597.00 | 110112303006.41 | 104608220776.3836 | 108796375788.183317 | 25.502437 | 38249.282778 | 0.049996 | 2878807     |
| R            | F            | 37719753.00 | 56568041380.90  | 53741292684.6040  | 55889619119.831932  | 25.505793 | 38250.854626 | 0.050009 | 1478870     |
+--------------+--------------+-------------+-----------------+-------------------+---------------------+-----------+--------------+----------+-------------+

Time: 0.127478459 seconds. 4 rows.
```
