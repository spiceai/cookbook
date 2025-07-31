# redshift-tpch-roundtrip

Round-trip TPCH through Redshift with Spice

#### Create Redshift Cluster

Use either the AWS console or the CLI to deploy Redshift:

```bash
$ aws cloudformation create-stack \
  --stack-name redshift-tpc \
  --template-body file://cloudformation.yaml \
  --capabilities CAPABILITY_IAM \
  --parameters ParameterKey=MasterUsername,ParameterValue=admin \
               ParameterKey=MasterUserPassword,ParameterValue=hGG3ellothere$$$$ \
               ParameterKey=DatabaseName,ParameterValue=dev
```

#### Write data into Redshift as accelerator target

Start Spice:

```bash
$ cd write
$ spiced
```

Validate that the correct tables have been made, look at the schema of one or two:

```
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

dev=# \x
Expanded display is on.

dev=# select * from "partsupp" limit 2;
-[ RECORD 1 ]-+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
ps_partkey    | 1
ps_suppkey    | 2
ps_availqty   | 3325
ps_supplycost | 771.64
ps_comment    | blithely regular theodolites sleep slyly across the sometimes bold dependencies. even accounts among the slyly final sauternes cajole quickly about the doggedly even platelets. carefully final
-[ RECORD 2 ]-+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
ps_partkey    | 1
ps_suppkey    | 2502
ps_availqty   | 8076
ps_supplycost | 993.49
ps_comment    | ts boost carefully ironic, regular accounts. final theodolites cajole slyly. final

dev=# select
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

#### Read data from Redshift via PostgreSQL connector

Start Spice:

```bash
$ pushd read
$ spiced
```

Validate that the correct tables have been made, look at the schema of one or two:
```bash
$ spiced --repl
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

Time: 0.011231625 seconds. 16 rows.
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

Run a TPCH query:

```
Time: 0.010364958 seconds. 16 rows.
sql> select
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
+--------------+--------------+---------+----------------+----------------+----------------+-----------+--------------+----------+-------------+
| l_returnflag | l_linestatus | sum_qty | sum_base_price | sum_disc_price | sum_charge     | avg_qty   | avg_price    | avg_disc | count_order |
+--------------+--------------+---------+----------------+----------------+----------------+-----------+--------------+----------+-------------+
| A            | F            | 6124.00 | 9141994.30     | 8710508.2481   | 9038832.715152 | 24.693548 | 36862.880241 | 0.048145 | 248         |
| N            | F            | 138.00  | 201910.19      | 189721.4555    | 197237.694662  | 23.000000 | 33651.698333 | 0.055000 | 6           |
+--------------+--------------+---------+----------------+----------------+----------------+-----------+--------------+----------+-------------+
```

#### Tear down Amazon infrastructure

Using the same stack name from earlier, delete the Redshift instance you set up.

```bash
$ aws cloudformation delete-stack --stack-name redshift-tpc
```
