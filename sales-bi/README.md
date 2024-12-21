# Sales BI (Apache Superset)

Use [Apache Superset](https://superset.apache.org/) to query and visualize datasets loaded in Spice.

> Apache Superset is a modern, enterprise-ready business intelligence web application. It is fast, lightweight, intuitive, and loaded with options that make it easy for users of all skill sets to explore and visualize their data, from simple pie charts to highly detailed deck.gl geospatial charts.
>
> – [Apache Superset documentation](https://superset.apache.org/docs/intro/)

https://github.com/spiceai/samples/assets/879445/ccc92377-0023-4073-ade1-09bb001ba886

This recipe will show how to configure a BI dashboard (Apache Superset) to use Spice as the data source for sales data. The sales data is stored in a parquet file on Amazon S3.

Spice.ai can be used to accelerate data from connected data sources by keeping an automatically updated copy of the data in an optimized format. This data can be used to power a BI dashboard that refreshes quickly.

## Pre-requisites

This recipe requires [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) to be installed.

## Start Apache Superset with Flight SQL & DataFusion SQL Dialect support

Superset requires a Python [DB API 2](https://peps.python.org/pep-0249/) database driver and a [SQLAlchemy](https://www.sqlalchemy.org/) dialect to be installed for each connected datastore. Spice implements a Flight SQL server that understands the DataFusion SQL Dialect. The [`flightsql-dbapi`](https://pypi.org/project/flightsql-dbapi/) library for Python provides the required DB API 2 driver and SQLAlchemy dialect.

![diagram overview](https://imagedelivery.net/HyTs22ttunfIlvyd6vumhQ/2c99263b-23a2-454f-9fdc-a9cfd67f8d00/public)

This sample consists of a Docker Compose file with the following components:

- A Spice runtime accelerating the data from the parquet file in S3.
- An Apache Superset instance to visualize the data, connected to the Spice instance.

Clone the `spiceai/samples` repository and navigate to the `sales-bi` directory:

```bash
git clone https://github.com/spiceai/samples.git
cd samples/sales-bi
```

Run the following command to start the components in the Docker Compose file:

`make`

This will start the Spice runtime and Apache Superset. The Spice runtime will load two datasets based on the parquet file in S3 - one is accelerated and one is not:

```yaml
version: v1beta1
kind: Spicepod
name: sales-bi

datasets:
  - from: s3://spiceai-demo-datasets/cleaned_sales_data.parquet
    name: cleaned_sales_data_accelerated
    acceleration:
      enabled: true
      refresh_check_interval: 10s
      refresh_mode: full

  - from: s3://spiceai-demo-datasets/cleaned_sales_data.parquet
    name: cleaned_sales_data
```

Queries against `cleaned_sales_data` will always request data from the parquet file in S3, while queries against `cleaned_sales_data_accelerated` will be run against the locally accelerated copy of the parquet file.

The output of the `make` command should look like:

```bash
 ✔ Container superset-sales-bi-demo  Started                                                                                                                                           0.0s
 ✔ Container spiceai-sales-bi-demo   Started                                                                                                                                           0.0s
Connection to localhost port 8088 [tcp/radan-http] succeeded!
Initializing Superset...

Superset is running at http://localhost:8088, login with admin/admin
```

Navigate to [http://localhost:8088](http://localhost:8088) to access the Apache Superset dashboard. The login credentials are `admin/admin`.

Once logged in, navigate to the `Sales Dashboard (Federated)` to view the sales data that is querying against the non-accelerated data.

![sales-bi-Sales-Dashboard-Federated.png](https://imagedelivery.net/HyTs22ttunfIlvyd6vumhQ/0c48f466-cbcc-4672-9df0-e165f90df200/public)

Click on a product line to view the sales data for that product line, i.e. for `Vintage Cars`:

![sales-bi-Sales-Dashboard-Vintage-Cars-Federated.png](https://imagedelivery.net/HyTs22ttunfIlvyd6vumhQ/a580d789-ec8c-445d-0a17-1ead27e85000/public)

Notice that the dashboard takes a few seconds to load the data. This is because the data is being queried from the parquet file in S3.

Navigate to the `Sales Dashboard (Accelerated)` to view the sales data that is querying against the accelerated data. Notice that the dashboard feels much more responsive.

![sales-bi-Sales-Dashboard-Accelerated.png](https://imagedelivery.net/HyTs22ttunfIlvyd6vumhQ/3735c62c-e69a-4aba-5399-5b09a87dbe00/public)

![sales-bi-Sales-Dashboard-Trucks-Buses-Accelerated.png](https://imagedelivery.net/HyTs22ttunfIlvyd6vumhQ/d0d0c14e-d281-46ac-de3c-e5e16a8e0200/public)

In the top navigation bar, hover over the `SQL` menu and click on `SQL Lab` to view a query editor. Explore the data from the Spice.ai runtime by running SQL queries, i.e. `SELECT * FROM cleaned_sales_data LIMIT 10` or `SELECT * FROM cleaned_sales_data_accelerated LIMIT 10`:

![sales-bi-SQL-Lab.png](https://imagedelivery.net/HyTs22ttunfIlvyd6vumhQ/c90376cf-d56e-49a7-09f1-a1e53979b500/public)

View the connection details for the Spice.ai runtime, hover over the `Settings` menu and click on `Database Connections`. Hover over the `Spice.ai` entry and click the pencil icon. The connection details for the Spice.ai runtime are shown:

![sales-bi-DB-Conn.png](https://imagedelivery.net/HyTs22ttunfIlvyd6vumhQ/6ba7b08c-fa78-4613-646d-c07d9cd4ab00/public)

## Spice SQL REPL

In addition to Apache Superset, run queries using the Spice SQL REPL to explore the data in the Spice.ai runtime.

`docker exec -it spiceai-sales-bi-demo spiced --repl`

```bash
Welcome to the interactive Spice.ai SQL Query Utility! Type 'help' for help.

show tables; -- list available tables
sql> show tables;
+---------------+--------------+--------------------------------+------------+
| table_catalog | table_schema | table_name                     | table_type |
+---------------+--------------+--------------------------------+------------+
| spice         | runtime      | task_history                   | BASE TABLE |
| spice         | public       | cleaned_sales_data             | BASE TABLE |
| spice         | public       | cleaned_sales_data_accelerated | BASE TABLE |
+---------------+--------------+--------------------------------+------------+

Time: 0.01025875 seconds. 3 rows.

sql> select * from cleaned_sales_data limit 1;
sql> select order_date, sales from cleaned_sales_data limit 3;
+---------------------+---------+
| order_date          | sales   |
+---------------------+---------+
| 2003-02-24T00:00:00 | 2871.0  |
| 2003-05-07T00:00:00 | 2765.9  |
| 2003-07-01T00:00:00 | 3884.34 |
+---------------------+---------+

Time: 0.610236 seconds. 3 rows.
```

## Clean up

To stop and remove the Docker containers/volumes that were created, run:

`make clean`
