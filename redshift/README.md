# Amazon Redshift

Works with `v2.4+`

This guide demonstrates how to use Spice to read and write TPC-H data with Amazon Redshift, a PostgreSQL-compatible columnar OLAP database.

> TPC-H is a decision support benchmark. It consists of a suite of business-oriented ad hoc queries and concurrent data modifications. The queries and the data populating the database have been chosen to have broad industry-wide relevance. This benchmark illustrates decision support systems that examine large volumes of data, execute queries with a high degree of complexity, and give answers to critical business questions.
>
> - [TPC Benchmark™ H (TPC-H)](https://www.tpc.org/tpch/)

## **Step 1.** Create a Redshift cluster

A Redshift cluster can be deployed using the AWS console or CLI. The following example demonstrates deployment using the AWS CLI:

```bash
aws cloudformation create-stack \
  --stack-name redshift-tpc \
  --template-body file://cloudformation.yaml \
  --capabilities CAPABILITY_IAM \
  --parameters ParameterKey=MasterUsername,ParameterValue=admin \
               ParameterKey=MasterUserPassword,ParameterValue=Hellothere123 \
               ParameterKey=DatabaseName,ParameterValue=dev
```

> Avoid `$` in the password: the shell expands `$$` to its process ID.

## Step 2: Configure connection credentials

Wait for the cluster to finish provisioning (this can take several minutes), then retrieve its endpoint address:

```bash
aws cloudformation describe-stacks --stack-name redshift-tpc \
  --query "Stacks[0].Outputs[?OutputKey=='RedshiftClusterEndpoint'].OutputValue" \
  --output text
```

Update the `.env` file in **both** the `write/` and `read/` directories with the endpoint and the master credentials you set in Step 1:

```env
PG_HOST=<your-cluster-endpoint>
PG_USER=admin
PG_PASS=Hellothere123
```

> The spicepods resolve these values via `${secrets:PG_HOST}`, `${secrets:PG_USER}`, and `${secrets:PG_PASS}`; the database (`dev`) and port (`5439`) are already set in `spicepod.yaml`. The committed `.env` files ship with placeholder values (`foo`/`bar`/`baz`) that must be replaced before running Spice.

## Step 3: Writing Data into Redshift

The `write` spicepod samples 1,000 rows of each TPC-H table from S3 into [Spice Cayenne](https://spiceai.org/docs/components/data-accelerators/cayenne) (`<table>_source`) and writes them into Redshift through the [PostgreSQL data connector](https://spiceai.org/docs/components/data-connectors/postgres#write-support) (`<table>`, `access: read_write`).

> **Note:** Writing through the PostgreSQL data connector is in preview. The connector writes into existing tables, so the tables are created with `psql` first.

To write data into Redshift, navigate to the `write` directory, create the tables, and start Spice using the following commands:

```bash
cd write
psql -h <your-cluster-endpoint> -p 5439 -U admin -d dev -f create_tables.sql
spice run
```

You should see this output in your terminal window:

```bash
2026-10-26T20:35:23.575727Z  INFO runtime::init::dataset: Dataset orders_source initializing...
2026-10-26T20:35:23.575719Z  INFO runtime::init::dataset: Dataset part_source initializing...
2026-10-26T20:35:23.575851Z  INFO runtime::init::dataset: Dataset partsupp initializing...
2026-10-26T20:35:23.575966Z  INFO runtime::init::dataset: Dataset lineitem initializing...
2026-10-26T20:35:23.576000Z  INFO runtime::init::dataset: Dataset supplier initializing...
2026-10-26T20:35:23.576023Z  INFO runtime::init::dataset: Dataset supplier_source initializing...
2026-10-26T20:35:23.575890Z  INFO runtime::init::dataset: Dataset nation initializing...
2026-10-26T20:35:23.575927Z  INFO runtime::init::dataset: Dataset region initializing...
2026-10-26T20:35:23.576114Z  INFO runtime::init::dataset: Dataset customer initializing...
2026-10-26T20:35:23.575945Z  INFO runtime::init::dataset: Dataset nation_source initializing...
2026-10-26T20:35:23.575858Z  INFO runtime::init::dataset: Dataset region_source initializing...
2026-10-26T20:35:23.576188Z  INFO runtime::init::dataset: Dataset partsupp_source initializing...
2026-10-26T20:35:23.575934Z  INFO runtime::init::dataset: Dataset orders initializing...
2026-10-26T20:35:23.576231Z  INFO runtime::init::dataset: Dataset customer_source initializing...
2026-10-26T20:35:23.575940Z  INFO runtime::init::dataset: Dataset part initializing...
2026-10-26T20:35:23.575953Z  INFO runtime::init::dataset: Dataset lineitem_source initializing...
2026-10-26T20:35:23.774880Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2026-10-26T20:35:23.775332Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2026-10-26T20:35:25.611292Z  INFO runtime::init::dataset: Dataset region_source registered (s3://spiceai-demo-datasets/tpch/region/), acceleration (cayenne), results cache enabled. duration_ms=1
2026-10-26T20:35:25.627062Z  INFO runtime::init::dataset: Dataset nation_source registered (s3://spiceai-demo-datasets/tpch/nation/), acceleration (cayenne), results cache enabled. duration_ms=37
2026-10-26T20:35:25.723737Z  INFO runtime::init::dataset: Dataset supplier_source registered (s3://spiceai-demo-datasets/tpch/supplier/), acceleration (cayenne), results cache enabled. duration_ms=1
2026-10-26T20:35:25.780844Z  INFO runtime::init::dataset: Dataset partsupp_source registered (s3://spiceai-demo-datasets/tpch/partsupp/), acceleration (cayenne), results cache enabled. duration_ms=1
2026-10-26T20:35:25.822167Z  INFO runtime::init::dataset: Dataset part_source registered (s3://spiceai-demo-datasets/tpch/part/), acceleration (cayenne), results cache enabled. duration_ms=1
2026-10-26T20:35:25.823810Z  INFO runtime::init::dataset: Dataset orders_source registered (s3://spiceai-demo-datasets/tpch/orders/), acceleration (cayenne), results cache enabled. duration_ms=1
2026-10-26T20:35:25.883286Z  INFO runtime::init::dataset: Dataset lineitem_source registered (s3://spiceai-demo-datasets/tpch/lineitem/), acceleration (cayenne), results cache enabled. duration_ms=1
2026-10-26T20:35:25.900755Z  INFO runtime::init::dataset: Dataset customer_source registered (s3://spiceai-demo-datasets/tpch/customer/), acceleration (cayenne), results cache enabled. duration_ms=1
2026-10-26T20:35:26.154340Z  INFO runtime::init::dataset: Dataset lineitem registered (postgres:public.lineitem), results cache enabled. duration_ms=638
2026-10-26T20:35:26.160558Z  INFO runtime::init::dataset: Dataset part registered (postgres:public.part), results cache enabled. duration_ms=631
2026-10-26T20:35:26.168165Z  INFO runtime::init::dataset: Dataset partsupp registered (postgres:public.partsupp), results cache enabled. duration_ms=635
2026-10-26T20:35:26.210134Z  INFO runtime::init::dataset: Dataset customer registered (postgres:public.customer), results cache enabled. duration_ms=660
2026-10-26T20:35:26.210549Z  INFO runtime::init::dataset: Dataset orders registered (postgres:public.orders), results cache enabled. duration_ms=665
2026-10-26T20:35:26.215687Z  INFO runtime::init::dataset: Dataset nation registered (postgres:public.nation), results cache enabled. duration_ms=637
2026-10-26T20:35:26.220651Z  INFO runtime::init::dataset: Dataset region registered (postgres:public.region), results cache enabled. duration_ms=630
2026-10-26T20:35:26.244279Z  INFO runtime::init::dataset: Dataset supplier registered (postgres:public.supplier), results cache enabled. duration_ms=629
2026-10-26T20:35:26.365571Z  INFO runtime_table::accelerated::refresh_task: Loaded 25 rows (2.59 kiB) for dataset nation_source in 737ms.
2026-10-26T20:35:26.373254Z  INFO runtime_table::accelerated::refresh_task: Loaded 5 rows (480.00 B) for dataset region_source in 760ms.
2026-10-26T20:35:26.845375Z  INFO runtime_table::accelerated::refresh_task: Loaded 1,000 rows (172.15 kiB) for dataset supplier_source in 1s 120ms.
2026-10-26T20:35:27.817000Z  INFO runtime_table::accelerated::refresh_task: Loaded 1,000 rows (164.50 kiB) for dataset part_source in 1s 994ms.
2026-10-26T20:35:28.146453Z  INFO runtime_table::accelerated::refresh_task: Loaded 1,000 rows (198.82 kiB) for dataset customer_source in 2s 244ms.
2026-10-26T20:35:29.132961Z  INFO runtime_table::accelerated::refresh_task: Loaded 1,000 rows (133.15 kiB) for dataset orders_source in 3s 308ms.
2026-10-26T20:35:36.516235Z  INFO runtime_table::accelerated::refresh_task: Loaded 1,000 rows (155.32 kiB) for dataset partsupp_source in 10s 734ms.
2026-10-26T20:35:36.640820Z  INFO runtime_table::accelerated::refresh_task: Loaded 1,000 rows (173.81 kiB) for dataset lineitem_source in 10s 756ms.
2026-10-26T20:35:36.659067Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

The `read_write` preview and `Failed to query PostgreSQL comments` warnings for each Redshift table can be ignored.

Once Spice is ready, write the samples into Redshift from another terminal in the `write` directory:

```bash
spice sql < insert.sql
```

```bash
+--------+
|  count |
| uint64 |
+--------+
| 1000   |
+--------+

Time: 1.394963875 seconds. 1 rows.
```

Each `INSERT` returns the number of rows written: 1,000 per table, 25 for `nation`, and 5 for `region`.

> `INSERT INTO` appends rows. Truncate the Redshift tables before running it again.

Validate that the correct tables have been made in PostgreSQL using the `psql` command-line utility:

```sql
$ psql -h host -p5439 -Uadmin dev
dev=# \dt
         List of relations
 schema |   name   | type  | owner
--------+----------+-------+-------
 public | customer | table | admin
 public | lineitem | table | admin
 public | nation   | table | admin
 public | orders   | table | admin
 public | part     | table | admin
 public | partsupp | table | admin
 public | region   | table | admin
 public | supplier | table | admin
(8 rows)
```

To validate the schema of a table, query `pg_table_def` (`\d+` fails against Redshift with `psql` 17). For example:

```sql
dev=# select "column", type from pg_table_def where tablename = 'lineitem';
     column      |          type
-----------------+------------------------
 l_orderkey      | integer
 l_partkey       | integer
 l_suppkey       | integer
 l_linenumber    | integer
 l_quantity      | numeric(15,2)
 l_extendedprice | numeric(15,2)
 l_discount      | numeric(15,2)
 l_tax           | numeric(15,2)
 l_returnflag    | character varying(256)
 l_linestatus    | character varying(256)
 l_shipdate      | date
 l_commitdate    | date
 l_receiptdate   | date
 l_shipinstruct  | character varying(256)
 l_shipmode      | character varying(256)
 l_comment       | character varying(256)
(16 rows)
```

Run the _Pricing Summary Report Query (Q1)_ to validate data. Q1 is defined in the
[TPC Benchmark H Standard Specification](https://www.tpc.org/tpc_documents_current_versions/pdf/tpc-h_v2.17.1.pdf).

> **Your numbers will differ.** The `write` spicepod samples the source with
> `refresh_sql: select * from lineitem_source limit 1000`. That `LIMIT` has no `ORDER BY`, so
> which 1,000 rows are loaded is arbitrary and changes from run to run — two successive
> runs here loaded completely disjoint samples. The aggregates below are therefore one
> run's result, not a fixed expected answer, and not the TPC-H specification's answer
> (those are defined over the full SF1 dataset). Add an `ORDER BY` to `refresh_sql` if
> you want a reproducible sample.

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
        "lineitem"
where
        l_shipdate <= date '1998-12-01' - interval '110' day
group by
        l_returnflag,
        l_linestatus
order by
        l_returnflag,
        l_linestatus
limit 2
;
```

```sql
-[ RECORD 1 ]--+---------------
l_returnflag   | A
l_linestatus   | F
sum_qty        | 6536.00
sum_base_price | 9904741.27
sum_disc_price | 9384409.9342
sum_charge     | 9772788.631818
avg_qty        | 25.33
avg_price      | 38390.47
avg_disc       | 0.05
count_order    | 258
-[ RECORD 2 ]--+---------------
l_returnflag   | N
l_linestatus   | F
sum_qty        | 299.00
sum_base_price | 433668.79
sum_disc_price | 418425.9970
sum_charge     | 433583.312504
avg_qty        | 29.90
avg_price      | 43366.87
avg_disc       | 0.03
count_order    | 10
```

Stop Spice with `Ctrl+C` before starting the `read` spicepod.

## Step 4: Reading Data from Redshift

To read data from Redshift, navigate to the `read` directory and start Spice:

```bash
cd read
spice run
```

You should see this output in your terminal window:

```bash
2026-10-26T20:37:07.924540Z  INFO runtime::init::dataset: Dataset customer initializing...
2026-10-26T20:37:07.924560Z  INFO runtime::init::dataset: Dataset partsupp initializing...
2026-10-26T20:37:07.924572Z  INFO runtime::init::dataset: Dataset nation initializing...
2026-10-26T20:37:07.924551Z  INFO runtime::init::dataset: Dataset region initializing...
2026-10-26T20:37:07.924556Z  INFO runtime::init::dataset: Dataset lineitem initializing...
2026-10-26T20:37:07.924563Z  INFO runtime::init::dataset: Dataset supplier initializing...
2026-10-26T20:37:07.924545Z  INFO runtime::init::dataset: Dataset orders initializing...
2026-10-26T20:37:07.924532Z  INFO runtime::init::dataset: Dataset part initializing...
2026-10-26T20:37:08.123802Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2026-10-26T20:37:08.124160Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2026-10-26T20:37:09.985445Z  INFO runtime::init::dataset: Dataset region registered (postgres:public.region), acceleration (cayenne), results cache enabled. duration_ms=96
2026-10-26T20:37:09.986546Z  INFO runtime::init::dataset: Dataset orders registered (postgres:public.orders), acceleration (cayenne), results cache enabled. duration_ms=90
2026-10-26T20:37:09.986667Z  INFO runtime::init::dataset: Dataset part registered (postgres:public.part), acceleration (cayenne), results cache enabled. duration_ms=59
2026-10-26T20:37:09.987825Z  INFO runtime::init::dataset: Dataset nation registered (postgres:public.nation), acceleration (cayenne), results cache enabled. duration_ms=87
2026-10-26T20:37:09.987880Z  INFO runtime::init::dataset: Dataset lineitem registered (postgres:public.lineitem), acceleration (cayenne), results cache enabled. duration_ms=85
2026-10-26T20:37:09.989027Z  INFO runtime::init::dataset: Dataset supplier registered (postgres:public.supplier), acceleration (cayenne), results cache enabled. duration_ms=92
2026-10-26T20:37:09.990408Z  INFO runtime::init::dataset: Dataset partsupp registered (postgres:public.partsupp), acceleration (cayenne), results cache enabled. duration_ms=108
2026-10-26T20:37:10.014557Z  INFO runtime::init::dataset: Dataset customer registered (postgres:public.customer), acceleration (cayenne), results cache enabled. duration_ms=87
2026-10-26T20:37:10.251586Z  INFO runtime_table::accelerated::refresh_task: Loaded 25 rows (2.38 kiB) for dataset nation in 262ms.
2026-10-26T20:37:10.257129Z  INFO runtime_table::accelerated::refresh_task: Loaded 5 rows (432.00 B) for dataset region in 270ms.
2026-10-26T20:37:10.392412Z  INFO runtime_table::accelerated::refresh_task: Loaded 1,000 rows (117.51 kiB) for dataset orders in 404ms.
2026-10-26T20:37:10.403624Z  INFO runtime_table::accelerated::refresh_task: Loaded 1,000 rows (151.41 kiB) for dataset partsupp in 412ms.
2026-10-26T20:37:10.422216Z  INFO runtime_table::accelerated::refresh_task: Loaded 1,000 rows (179.27 kiB) for dataset customer in 406ms.
2026-10-26T20:37:10.423121Z  INFO runtime_table::accelerated::refresh_task: Loaded 1,000 rows (154.26 kiB) for dataset lineitem in 434ms.
2026-10-26T20:37:10.458880Z  INFO runtime_table::accelerated::refresh_task: Loaded 1,000 rows (141.04 kiB) for dataset part in 471ms.
2026-10-26T20:37:10.643631Z  INFO runtime_table::accelerated::refresh_task: Loaded 1,000 rows (156.51 kiB) for dataset supplier in 653ms.
2026-10-26T20:37:10.725435Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

The `Failed to query PostgreSQL comments` warning for each table can be ignored.

Validate that the correct tables have been made:

```sql
spice sql
sql> show tables;
+---------------+--------------+--------------+------------+
| table_catalog | table_schema |  table_name  | table_type |
|    varchar    |    varchar   |    varchar   |   varchar  |
+---------------+--------------+--------------+------------+
| spice         | runtime      | task_history | BASE TABLE |
| spice         | public       | part         | BASE TABLE |
| spice         | public       | lineitem     | BASE TABLE |
| spice         | public       | orders       | BASE TABLE |
| spice         | public       | nation       | BASE TABLE |
| spice         | public       | region       | BASE TABLE |
| spice         | public       | customer     | BASE TABLE |
| spice         | public       | supplier     | BASE TABLE |
| spice         | public       | partsupp     | BASE TABLE |
+---------------+--------------+--------------+------------+
```

`show tables` on v2.2.0 also lists the `information_schema` views (`tables`, `views`,
`columns`, `df_settings`, `schemata`, `routines`, `parameters`) alongside the rows above.

To validate the schema of `lineitem`, use the `describe` command:

```sql
sql> describe lineitem;
+--------------+-----------------+-------------------+-------------+
| table_schema |   column_name   |     data_type     | is_nullable |
|    varchar   |     varchar     |      varchar      |   varchar   |
+--------------+-----------------+-------------------+-------------+
| public       | l_orderkey      | Int32             | YES         |
| public       | l_partkey       | Int32             | YES         |
| public       | l_suppkey       | Int32             | YES         |
| public       | l_linenumber    | Int32             | YES         |
| public       | l_quantity      | Decimal128(15, 2) | YES         |
| public       | l_extendedprice | Decimal128(15, 2) | YES         |
| public       | l_discount      | Decimal128(15, 2) | YES         |
| public       | l_tax           | Decimal128(15, 2) | YES         |
| public       | l_returnflag    | Utf8              | YES         |
| public       | l_linestatus    | Utf8              | YES         |
| public       | l_shipdate      | Date32            | YES         |
| public       | l_commitdate    | Date32            | YES         |
| public       | l_receiptdate   | Date32            | YES         |
| public       | l_shipinstruct  | Utf8              | YES         |
| public       | l_shipmode      | Utf8              | YES         |
| public       | l_comment       | Utf8              | YES         |
+--------------+-----------------+-------------------+-------------+
```

Run the _Pricing Summary Report Query (Q1)_ to validate data. Q1 is defined in the
[TPC Benchmark H Standard Specification](https://www.tpc.org/tpc_documents_current_versions/pdf/tpc-h_v2.17.1.pdf).

> The `read` spicepod reads the rows written in Step 3, so the results match Step 3. Redshift rounds `avg()` of a
> `NUMERIC(15,2)` column to two decimal places.

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
        "lineitem"
where
        l_shipdate <= date '1998-12-01' - interval '110' day
group by
        l_returnflag,
        l_linestatus
order by
        l_returnflag,
        l_linestatus
limit 2
;
```

```sql
+--------------+--------------+---------------+----------------+----------------+----------------+---------------+---------------+---------------+-------------+
| l_returnflag | l_linestatus |    sum_qty    | sum_base_price | sum_disc_price |   sum_charge   |    avg_qty    |   avg_price   |    avg_disc   | count_order |
|    varchar   |    varchar   | decimal(25,2) |  decimal(25,2) |  decimal(38,4) |  decimal(38,6) | decimal(19,6) | decimal(19,6) | decimal(19,6) |    int64    |
+--------------+--------------+---------------+----------------+----------------+----------------+---------------+---------------+---------------+-------------+
| A            | F            | 6536.00       | 9904741.27     | 9384409.9342   | 9772788.631818 | 25.333333     | 38390.470038  | 0.050736      | 258         |
| N            | F            | 299.00        | 433668.79      | 418425.9970    | 433583.312504  | 29.900000     | 43366.879000  | 0.037000      | 10          |
+--------------+--------------+---------------+----------------+----------------+----------------+---------------+---------------+---------------+-------------+
```

## Step 5: Tearing Down Infrastructure

To delete the Redshift instance, use the same stack name provided during setup:

```bash
aws cloudformation delete-stack --stack-name redshift-tpc
```
