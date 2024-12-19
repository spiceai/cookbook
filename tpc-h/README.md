# Recipe for TPC-H Benchmark Sample Data

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
Spice.ai runtime starting...
2024/11/27 12:59:01 INFO Checking for latest Spice runtime release...
2024/11/27 12:59:01 INFO Spice.ai runtime starting...
2024-11-27T20:59:02.364766Z  INFO runtime::init::dataset: No datasets were configured. If this is unexpected, check the Spicepod configuration.
2024-11-27T20:59:02.366771Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2024-11-27T20:59:02.366928Z  INFO runtime::metrics_server: Spice Runtime Metrics listening on 127.0.0.1:9090
2024-11-27T20:59:02.366986Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2024-11-27T20:59:02.374354Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2024-11-27T20:59:02.564753Z  INFO runtime::init::results_cache: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
2024-11-27T20:59:47.749619Z  INFO runtime::init::dataset: Dataset customer registered (s3://spiceai-demo-datasets/tpch/customer/), results cache enabled.
2024-11-27T20:59:48.540821Z  INFO runtime::init::dataset: Dataset lineitem registered (s3://spiceai-demo-datasets/tpch/lineitem/), results cache enabled.
2024-11-27T20:59:49.279920Z  INFO runtime::init::dataset: Dataset nation registered (s3://spiceai-demo-datasets/tpch/nation/), results cache enabled.
2024-11-27T20:59:50.096551Z  INFO runtime::init::dataset: Dataset orders registered (s3://spiceai-demo-datasets/tpch/orders/), results cache enabled.
2024-11-27T20:59:50.928929Z  INFO runtime::init::dataset: Dataset part registered (s3://spiceai-demo-datasets/tpch/part/), results cache enabled.
2024-11-27T20:59:51.717123Z  INFO runtime::init::dataset: Dataset partsupp registered (s3://spiceai-demo-datasets/tpch/partsupp/), results cache enabled.
2024-11-27T20:59:52.464457Z  INFO runtime::init::dataset: Dataset region registered (s3://spiceai-demo-datasets/tpch/region/), results cache enabled.
2024-11-27T20:59:53.264263Z  INFO runtime::init::dataset: Dataset supplier registered (s3://spiceai-demo-datasets/tpch/supplier/), results cache enabled.
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

**Step4 (Optional)** Enable [Data Acceleration](https://docs.spiceai.org/data-accelerators) for TPC-H Benchmark Sample Data

Use text editor to open `./spicepods/spiceai/tpch/spicepod.yaml` file and enable `acceleration` flags for each table. Save.

Before:

```yaml
  - from: s3://spiceai-demo-datasets/tpch/customer/
    name: customer
    acceleration:
      enabled: false
```

After:

```yaml
  - from: s3://spiceai-demo-datasets/tpch/customer/
    name: customer
    acceleration:
      enabled: true
```

The following output is shown in the Spice runtime terminal confirming new configuration is applied.

```bash
2024-07-23T00:49:40.552646Z  INFO runtime: Updating accelerated dataset customer...
2024-07-23T00:49:41.286410Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset customer
2024-07-23T00:49:44.029108Z  INFO runtime::accelerated_table::refresh_task: Loaded 150,000 rows (32.10 MiB) for dataset customer in 2s 742ms.
2024-07-23T00:49:44.717176Z  INFO runtime: Dataset customer registered (s3://spiceai-demo-datasets/tpch/customer/), acceleration (arrow), results cache enabled.
2024-07-23T00:49:44.717224Z  INFO runtime: Updating accelerated dataset lineitem...
2024-07-23T00:49:45.352376Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset lineitem
2024-07-23T00:49:57.824329Z  INFO runtime::accelerated_table::refresh_task: Loaded 6,001,215 rows (1.05 GiB) for dataset lineitem in 12s 471ms.
2024-07-23T00:49:58.476041Z  INFO runtime: Dataset lineitem registered (s3://spiceai-demo-datasets/tpch/lineitem/), acceleration (arrow), results cache enabled.
2024-07-23T00:49:58.476107Z  INFO runtime: Updating accelerated dataset nation...
2024-07-23T00:49:59.092162Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset nation
2024-07-23T00:50:00.028890Z  INFO runtime::accelerated_table::refresh_task: Loaded 25 rows (3.10 kiB) for dataset nation in 936ms.
2024-07-23T00:50:00.632540Z  INFO runtime: Dataset nation registered (s3://spiceai-demo-datasets/tpch/nation/), acceleration (arrow), results cache enabled.
2024-07-23T00:50:00.632589Z  INFO runtime: Updating accelerated dataset orders...
2024-07-23T00:50:01.319494Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset orders
2024-07-23T00:50:06.117615Z  INFO runtime::accelerated_table::refresh_task: Loaded 1,500,000 rows (206.69 MiB) for dataset orders in 4s 798ms.
2024-07-23T00:50:06.758589Z  INFO runtime: Dataset orders registered (s3://spiceai-demo-datasets/tpch/orders/), acceleration (arrow), results cache enabled.
2024-07-23T00:50:06.758635Z  INFO runtime: Updating accelerated dataset part...
2024-07-23T00:50:07.474957Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset part
2024-07-23T00:50:09.480938Z  INFO runtime::accelerated_table::refresh_task: Loaded 200,000 rows (34.61 MiB) for dataset part in 2s 5ms.
2024-07-23T00:50:10.099495Z  INFO runtime: Dataset part registered (s3://spiceai-demo-datasets/tpch/part/), acceleration (arrow), results cache enabled.
2024-07-23T00:50:10.099526Z  INFO runtime: Updating accelerated dataset partsupp...
2024-07-23T00:50:10.788284Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset partsupp
2024-07-23T00:50:19.160679Z  INFO runtime::accelerated_table::refresh_task: Loaded 800,000 rows (138.95 MiB) for dataset partsupp in 8s 372ms.
2024-07-23T00:50:19.849290Z  INFO runtime: Dataset partsupp registered (s3://spiceai-demo-datasets/tpch/partsupp/), acceleration (arrow), results cache enabled.
2024-07-23T00:50:19.849380Z  INFO runtime: Updating accelerated dataset region...
2024-07-23T00:50:20.438604Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset region
2024-07-23T00:50:21.347679Z  INFO runtime::accelerated_table::refresh_task: Loaded 5 rows (944.00 B) for dataset region in 909ms.
2024-07-23T00:50:21.958690Z  INFO runtime: Dataset region registered (s3://spiceai-demo-datasets/tpch/region/), acceleration (arrow), results cache enabled.
2024-07-23T00:50:21.958735Z  INFO runtime: Updating accelerated dataset supplier...
2024-07-23T00:50:22.692098Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset supplier
2024-07-23T00:50:24.212649Z  INFO runtime::accelerated_table::refresh_task: Loaded 10,000 rows (1.80 MiB) for dataset supplier in 1s 520ms.
2024-07-23T00:50:24.832568Z  INFO runtime: Dataset supplier registered (s3://spiceai-demo-datasets/tpch/supplier/), acceleration (arrow), results cache enabled.
```

Run *Pricing Summary Report Query* using the Spice SQL REPL.

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
+--------------+--------------+-------------+-----------------+-------------------+---------------------+-----------+--------------+----------+-------------+
| l_returnflag | l_linestatus | sum_qty     | sum_base_price  | sum_disc_price    | sum_charge          | avg_qty   | avg_price    | avg_disc | count_order |
+--------------+--------------+-------------+-----------------+-------------------+---------------------+-----------+--------------+----------+-------------+
| A            | F            | 37734107.00 | 56586554400.73  | 53758257134.8700  | 55909065222.827692  | 25.522005 | 38273.129734 | 0.049985 | 1478493     |
| N            | F            | 991417.00   | 1487504710.38   | 1413082168.0541   | 1469649223.194375   | 25.516471 | 38284.467760 | 0.050093 | 38854       |
| N            | O            | 73416597.00 | 110112303006.41 | 104608220776.3836 | 108796375788.183317 | 25.502437 | 38249.282778 | 0.049996 | 2878807     |
| R            | F            | 37719753.00 | 56568041380.90  | 53741292684.6040  | 55889619119.831932  | 25.505793 | 38250.854626 | 0.050009 | 1478870     |
+--------------+--------------+-------------+-----------------+-------------------+---------------------+-----------+--------------+----------+-------------+

Time: 0.108190459 seconds. 4 rows.
```

Observe query execution time decreased from **4.178523666** to **0.108190459** seconds.
