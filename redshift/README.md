# Amazon Redshift

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
               ParameterKey=MasterUserPassword,ParameterValue=hGG3ellothere$$$$ \
               ParameterKey=DatabaseName,ParameterValue=dev
```

## Step 2: Writing Data into Redshift

To write data into Redshift, navigate to the `write` directory and start Spice using the following command:

```bash
cd write
spice run
```

You should see this output in your terminal window:

```bash
2025-08-01T01:15:06.019931Z  INFO spiced: Starting runtime v1.6.0-unstable-build.184ebb772
2025-08-01T01:15:06.022725Z  INFO runtime::init::caching: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
2025-08-01T01:15:06.022949Z  INFO runtime::init::caching: Initialized search results cache;
2025-08-01T01:15:06.438166Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2025-08-01T01:15:06.438359Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2025-08-01T01:15:06.441831Z  INFO runtime::init::dataset: Dataset region initializing...
2025-08-01T01:15:06.441851Z  INFO runtime::init::dataset: Dataset orders initializing...
2025-08-01T01:15:06.441912Z  INFO runtime::init::dataset: Dataset supplier initializing...
2025-08-01T01:15:06.441970Z  INFO runtime::init::dataset: Dataset lineitem initializing...
2025-08-01T01:15:06.441990Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2025-08-01T01:15:06.442066Z  INFO runtime::init::dataset: Dataset partsupp initializing...
2025-08-01T01:15:06.442084Z  INFO runtime::init::dataset: Dataset customer initializing...
2025-08-01T01:15:06.442089Z  INFO runtime::init::dataset: Dataset part initializing...
2025-08-01T01:15:06.442117Z  INFO runtime::init::dataset: Dataset nation initializing...
2025-08-01T01:15:07.411919Z  INFO runtime::init::dataset: Dataset region registered (s3://spiceai-demo-datasets/tpch/region/), acceleration (postgres), results cache enabled.
2025-08-01T01:15:07.413277Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset region
2025-08-01T01:15:07.702387Z  INFO runtime::init::dataset: Dataset supplier registered (s3://spiceai-demo-datasets/tpch/supplier/), acceleration (postgres), results cache enabled.
2025-08-01T01:15:07.702858Z  INFO runtime::init::dataset: Dataset part registered (s3://spiceai-demo-datasets/tpch/part/), acceleration (postgres), results cache enabled.
2025-08-01T01:15:07.702864Z  INFO runtime::init::dataset: Dataset orders registered (s3://spiceai-demo-datasets/tpch/orders/), acceleration (postgres), results cache enabled.
2025-08-01T01:15:07.703431Z  INFO runtime::init::dataset: Dataset customer registered (s3://spiceai-demo-datasets/tpch/customer/), acceleration (postgres), results cache enabled.
2025-08-01T01:15:07.703558Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset supplier
2025-08-01T01:15:07.703580Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset orders
2025-08-01T01:15:07.703617Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset part
2025-08-01T01:15:07.703894Z  INFO runtime::init::dataset: Dataset nation registered (s3://spiceai-demo-datasets/tpch/nation/), acceleration (postgres), results cache enabled.
2025-08-01T01:15:07.703941Z  INFO runtime::init::dataset: Dataset partsupp registered (s3://spiceai-demo-datasets/tpch/partsupp/), acceleration (postgres), results cache enabled.
2025-08-01T01:15:07.704752Z  INFO runtime::init::dataset: Dataset lineitem registered (s3://spiceai-demo-datasets/tpch/lineitem/), acceleration (postgres), results cache enabled.
2025-08-01T01:15:07.704832Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset nation
2025-08-01T01:15:07.704859Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset partsupp
2025-08-01T01:15:07.704871Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset customer
2025-08-01T01:15:07.706200Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset lineitem
2025-08-01T01:15:08.814196Z  INFO runtime::accelerated_table::refresh_task: Loaded 5 rows (1008.00 B) for dataset region in 1s 400ms.
2025-08-01T01:15:09.264442Z  INFO runtime::accelerated_table::refresh_task: Loaded 1,000 rows (190.69 kiB) for dataset supplier in 1s 560ms.
2025-08-01T01:15:09.608490Z  INFO runtime::accelerated_table::refresh_task: Loaded 25 rows (3.35 kiB) for dataset nation in 1s 903ms.
2025-08-01T01:15:10.603145Z  INFO runtime::accelerated_table::refresh_task: Loaded 1,000 rows (277.68 kiB) for dataset customer in 2s 898ms.
2025-08-01T01:15:12.128351Z  INFO runtime::accelerated_table::refresh_task: Loaded 1,000 rows (158.19 kiB) for dataset orders in 4s 424ms.
2025-08-01T01:15:12.846856Z  INFO runtime::accelerated_table::refresh_task: Loaded 1,000 rows (190.84 kiB) for dataset lineitem in 5s 140ms.
2025-08-01T01:15:13.375356Z  INFO runtime::accelerated_table::refresh_task: Loaded 1,000 rows (180.17 kiB) for dataset part in 5s 671ms.
2025-08-01T01:15:14.029083Z  INFO runtime::accelerated_table::refresh_task: Loaded 1,000 rows (227.71 kiB) for dataset partsupp in 6s 324ms.
2025-08-01T01:15:14.091465Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

Validate that the correct tables have been made in PostgreSQL using the `psql` command-line utility:

```sql
$ psql -h host -p5439 -Uadmin dev
dev=# \d
                   List of relations
 schema |             name             | type  | owner
--------+------------------------------+-------+-------
 public | spice_sys_dataset_checkpoint | table | admin
 public | customer                | table | admin
 public | lineitem                | table | admin
 public | nation                  | table | admin
 public | orders                  | table | admin
 public | part                    | table | admin
 public | partsupp                | table | admin
 public | region                  | table | admin
 public | supplier                | table | admin
```

To validate the schema of a table, use the `\d+` command. For example:

```sql
dev=# \d+ "lineitem"
                                           Table "public.lineitem"
     Column      |          Type          | Collation | Nullable | Default | Storage  | Stats target | Description
-----------------+------------------------+-----------+----------+---------+----------+--------------+-------------
 l_orderkey      | integer                |           |          |         | plain    |              |
 l_partkey       | integer                |           |          |         | plain    |              |
 l_suppkey       | integer                |           |          |         | plain    |              |
 l_linenumber    | integer                |           |          |         | plain    |              |
 l_quantity      | numeric(15,2)          |           |          |         | main     |              |
 l_extendedprice | numeric(15,2)          |           |          |         | main     |              |
 l_discount      | numeric(15,2)          |           |          |         | main     |              |
 l_tax           | numeric(15,2)          |           |          |         | main     |              |
 l_returnflag    | character varying(256) |           |          |         | extended |              |
 l_linestatus    | character varying(256) |           |          |         | extended |              |
 l_shipdate      | date                   |           |          |         | plain    |              |
 l_commitdate    | date                   |           |          |         | plain    |              |
 l_receiptdate   | date                   |           |          |         | plain    |              |
 l_shipinstruct  | character varying(256) |           |          |         | extended |              |
 l_shipmode      | character varying(256) |           |          |         | extended |              |
 l_comment       | character varying(256) |           |          |         | extended |              |
Has OIDs: yes
```

Run the _Pricing Summary Report Query (Q1)_ to validate data. The query and its expected output are detailed in the [TPC Benchmark H Standard Specification](https://www.tpc.org/tpc_documents_current_versions/pdf/tpc-h_v2.17.1.pdf):

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

## Step 3: Reading Data from Redshift

To read data from Redshift, navigate to the `read` directory and start Spice:

```bash
cd read
spice run
```

You should see this output in your terminal window:

```bash
2025-08-01T01:15:40.066625Z  INFO spiced: Starting runtime v1.6.0-unstable-build.184ebb772
2025-08-01T01:15:40.069247Z  INFO runtime::init::caching: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
2025-08-01T01:15:40.069468Z  INFO runtime::init::caching: Initialized search results cache;
2025-08-01T01:15:40.306607Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2025-08-01T01:15:40.306719Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2025-08-01T01:15:40.308188Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2025-08-01T01:15:40.308507Z  INFO runtime::init::dataset: Dataset orders initializing...
2025-08-01T01:15:40.308511Z  INFO runtime::init::dataset: Dataset region initializing...
2025-08-01T01:15:40.308587Z  INFO runtime::init::dataset: Dataset part initializing...
2025-08-01T01:15:40.308563Z  INFO runtime::init::dataset: Dataset nation initializing...
2025-08-01T01:15:40.308584Z  INFO runtime::init::dataset: Dataset customer initializing...
2025-08-01T01:15:40.308603Z  INFO runtime::init::dataset: Dataset supplier initializing...
2025-08-01T01:15:40.308684Z  INFO runtime::init::dataset: Dataset partsupp initializing...
2025-08-01T01:15:40.308770Z  INFO runtime::init::dataset: Dataset lineitem initializing...
2025-08-01T01:15:40.995606Z  INFO runtime::init::dataset: Dataset orders registered (postgres:public.orders), acceleration (arrow), results cache enabled.
2025-08-01T01:15:40.996460Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset orders
2025-08-01T01:15:41.374001Z  INFO runtime::accelerated_table::refresh_task: Loaded 1,000 rows (146.19 kiB) for dataset orders in 377ms.
2025-08-01T01:15:41.481632Z  INFO runtime::init::dataset: Dataset region registered (postgres:public.region), acceleration (arrow), results cache enabled.
2025-08-01T01:15:41.482800Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset region
2025-08-01T01:15:41.563571Z  INFO runtime::accelerated_table::refresh_task: Loaded 5 rows (14.45 kiB) for dataset region in 80ms.
2025-08-01T01:15:41.798712Z  INFO runtime::init::dataset: Dataset part registered (postgres:public.part), acceleration (arrow), results cacheenabled.
2025-08-01T01:15:41.799995Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset part
2025-08-01T01:15:41.926069Z  INFO runtime::accelerated_table::refresh_task: Loaded 1,000 rows (161.36 kiB) for dataset part in 126ms.
2025-08-01T01:15:42.142538Z  INFO runtime::init::dataset: Dataset nation registered (postgres:public.nation), acceleration (arrow), results cache enabled.
2025-08-01T01:15:42.143810Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset nation
2025-08-01T01:15:42.219842Z  INFO runtime::accelerated_table::refresh_task: Loaded 25 rows (19.55 kiB) for dataset nation in 76ms.
2025-08-01T01:15:42.480982Z  INFO runtime::init::dataset: Dataset customer registered (postgres:public.customer), acceleration (arrow), results cache enabled.
2025-08-01T01:15:42.482235Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset customer
2025-08-01T01:15:42.826813Z  INFO runtime::accelerated_table::refresh_task: Loaded 1,000 rows (269.18 kiB) for dataset customer in 344ms.
2025-08-01T01:15:42.886263Z  INFO runtime::init::dataset: Dataset supplier registered (postgres:public.supplier), acceleration (arrow), results cache enabled.
2025-08-01T01:15:42.887628Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset supplier
2025-08-01T01:15:43.250965Z  INFO runtime::accelerated_table::refresh_task: Loaded 1,000 rows (185.00 kiB) for dataset supplier in 363ms.
2025-08-01T01:15:43.386852Z  INFO runtime::init::dataset: Dataset partsupp registered (postgres:public.partsupp), acceleration (arrow), results cache enabled.
2025-08-01T01:15:43.388171Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset partsupp
2025-08-01T01:15:43.830328Z  INFO runtime::init::dataset: Dataset lineitem registered (postgres:public.lineitem), acceleration (arrow), results cache enabled.
2025-08-01T01:15:43.831713Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset lineitem
2025-08-01T01:15:43.898640Z  INFO runtime::accelerated_table::refresh_task: Loaded 1,000 rows (160.55 kiB) for dataset partsupp in 510ms.
2025-08-01T01:15:44.157564Z  INFO runtime::accelerated_table::refresh_task: Loaded 1,000 rows (171.93 kiB) for dataset lineitem in 325ms.
2025-08-01T01:15:44.239953Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

Validate that the correct tables have been made:

```sql
spice sql
sql> show tables;
+---------------+--------------+--------------+------------+
| table_catalog | table_schema | table_name   | table_type |
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

To validate the schema of `lineitem`, use the `describe` command:

```sql
sql> describe lineitem;
+-----------------+-------------------+-------------+
| column_name     | data_type         | is_nullable |
+-----------------+-------------------+-------------+
| l_orderkey      | Int32             | YES         |
| l_partkey       | Int32             | YES         |
| l_suppkey       | Int32             | YES         |
| l_linenumber    | Int32             | YES         |
| l_quantity      | Decimal128(15, 2) | YES         |
| l_extendedprice | Decimal128(15, 2) | YES         |
| l_discount      | Decimal128(15, 2) | YES         |
| l_tax           | Decimal128(15, 2) | YES         |
| l_returnflag    | Utf8              | YES         |
| l_linestatus    | Utf8              | YES         |
| l_shipdate      | Date32            | YES         |
| l_commitdate    | Date32            | YES         |
| l_receiptdate   | Date32            | YES         |
| l_shipinstruct  | Utf8              | YES         |
| l_shipmode      | Utf8              | YES         |
| l_comment       | Utf8              | YES         |
+-----------------+-------------------+-------------+
```

Run the _Pricing Summary Report Query (Q1)_ to validate data. The query and its expected output are detailed in the [TPC Benchmark H Standard Specification](https://www.tpc.org/tpc_documents_current_versions/pdf/tpc-h_v2.17.1.pdf):

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
+--------------+--------------+---------+----------------+----------------+----------------+-----------+--------------+----------+-------------+
| l_returnflag | l_linestatus | sum_qty | sum_base_price | sum_disc_price | sum_charge     | avg_qty   | avg_price    | avg_disc | count_order |
+--------------+--------------+---------+----------------+----------------+----------------+-----------+--------------+----------+-------------+
| A            | F            | 6124.00 | 9141994.30     | 8710508.2481   | 9038832.715152 | 24.693548 | 36862.880241 | 0.048145 | 248         |
| N            | F            | 138.00  | 201910.19      | 189721.4555    | 197237.694662  | 23.000000 | 33651.698333 | 0.055000 | 6           |
+--------------+--------------+---------+----------------+----------------+----------------+-----------+--------------+----------+-------------+
```

## Step 4: Tearing Down Infrastructure

To delete the Redshift instance, use the same stack name provided during setup:

```bash
aws cloudformation delete-stack --stack-name redshift-tpc
```
