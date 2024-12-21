# Accelerated table data quality with constraint enforcement

This recipe demonstrates how to use Spice to enforce constraints on locally accelerated data. This can be especially useful when you have a `refresh_mode: append` accelerated dataset and the data can be updated in the datasource.

By specifying a `time_column` on the dataset with `refresh_mode: append` on the acceleration, Spice will automatically pull in all changes from the datasource that have occurred after the max timestamp in the accelerated dataset. This can present a problem if the datasource updates the data and it appears as a new row in the accelerated dataset, when it should have updated an existing row.

This sample will have a local Postgres database with a table `users` and a Spice runtime that accelerates the data from the `users` table. A Spicepod will enforce a constraint that the `email` column must be unique. The Spicepod will also specify a `time_column` of `updated_at` to ensure that the Spice runtime only pulls in changes from the datasource that have occurred after the max `updated_at` timestamp in the accelerated dataset. A worker service will update the `users` table in the Postgres database with changes to the `users` table every 5 seconds. This will cause the Spice runtime to pull in the changes and enforce the constraint.

Once you've verified that the constraints are being enforced, try modifying the Spicepod to remove the `on_conflict` clause and observe the behavior. An error should now be given by DuckDB that the constraint is being violated and the data update is rejected.

Another thing to try is to remove the `primary_key` constraint from the Spicepod and observe the behavior. Instead of the rows being updated in place, new rows will be added every time Spice refreshes the data.

## Prerequisites

This recipe requires [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) to be installed.

## How to run

Clone this cookbook repo locally:

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/acceleration/constraints
```

Start the Docker Compose stack:

`make`

Then observe the logs of the Spice runtime and the worker service.

`docker logs -f spiceai-constraint-demo`

`docker logs -f spiceai-constraint-demo-worker`

## Spice SQL REPL

In addition to viewing the logs, run queries using the Spice SQL REPL to explore the data and ensure the constraints are being kept.

`docker exec -it spiceai-constraint-demo spiced --repl`

```bash
Welcome to the interactive Spice.ai SQL Query Utility! Type 'help' for help.

show tables; -- list available tables
sql> show tables;
+---------------+--------------+--------------+------------+
| table_catalog | table_schema | table_name   | table_type |
+---------------+--------------+--------------+------------+
| spice         | public       | users        | BASE TABLE |
| spice         | runtime      | task_history | BASE TABLE |
+---------------+--------------+--------------+------------+

Time: 0.031901631 seconds. 2 rows.
sql> select email, username, items_bought, last_login from users;
+-------------------------+----------+--------------+---------------------+
| email                   | username | items_bought | last_login          |
+-------------------------+----------+--------------+---------------------+
| alice@sample.com        | alice    | 0            | 2023-11-21T19:23:34 |
| bob@umbrellacorp.com    | bob      | 0            | 2024-06-17T12:20:19 |
| clint@bobsumbrellas.com | clint    | 0            | 2024-04-13T08:12:46 |
| dobbie@hogwarts.ac.uk   | dobbie   | 0            | 2024-03-04T03:13:04 |
| eddie@edslawncare.com   | eddie    | 0            | 2024-02-29T23:59:59 |
+-------------------------+----------+--------------+---------------------+

Time: 0.045052253 seconds. 5 rows.
```

## Clean up

To stop and remove the Docker containers/volumes that were created, run:

`make clean`
