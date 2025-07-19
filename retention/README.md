# Accelerated Dataset Retention Policy

This recipe shows how to set up a [retention policy](https://spiceai.org/docs/features/data-acceleration/data-refresh#retention-policy) for an accelerated dataset to evict data older than a specified duration.

## Pre-requisites

This recipe requires [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) to be installed.

## How to run

Clone this cookbook repo locally:

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/retention
```

Start the Docker Compose stack:

`make`

Then observe the logs the worker service.

`docker logs -f spiceai-retention-demo-worker`

```console
Inserted new user user_1743059111919094138@example.com with username user_1743059111919131971
Inserted new user user_1743059116946543113@example.com with username user_1743059116946571113
Inserted new user user_1743059121968650335@example.com with username user_1743059121968694585
Inserted new user user_1743059126987340233@example.com with username user_1743059126987350733
Inserted new user user_1743059131996107498@example.com with username user_1743059131996143414
Inserted new user user_1743059137019737701@example.com with username user_1743059137019748826
Inserted new user user_1743059142033727592@example.com with username user_1743059142033752467
Inserted new user user_1743059147049323917@example.com with username user_1743059147049330500
Inserted new user user_1743059152063665845@example.com with username user_1743059152063694678
```

Run `docker logs -f spiceai-retention-demo` and Wait for the next retention check interval and see the retention policy evict data:

```console
2025-03-27T07:08:50.616347Z  INFO runtime::accelerated_table::refresh_task: Loaded 1 rows (34.64 kiB) for dataset users in 16ms.
2025-03-27T07:08:54.291596Z  INFO runtime::accelerated_table: [retention] Evicting data for users where updated_at < 2025-03-27T07:08:24+00:00...
2025-03-27T07:08:54.299160Z  INFO runtime::accelerated_table: [retention] Evicted 2 records for users
2025-03-27T07:08:55.634074Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset users
2025-03-27T07:08:55.650633Z  INFO runtime::accelerated_table::refresh_task: Loaded 1 rows (34.64 kiB) for dataset users in 31ms.
2025-03-27T07:09:00.660625Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset users
2025-03-27T07:09:00.673057Z  INFO runtime::accelerated_table::refresh_task: Loaded 1 rows (34.64 kiB) for dataset users in 20ms.
2025-03-27T07:09:04.293654Z  INFO runtime::accelerated_table: [retention] Evicting data for users where updated_at < 2025-03-27T07:08:34+00:00...
2025-03-27T07:09:04.302727Z  INFO runtime::accelerated_table: [retention] Evicted 2 records for users
2025-03-27T07:09:05.689919Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset users
2025-03-27T07:09:05.697891Z  INFO runtime::accelerated_table::refresh_task: Loaded 1 rows (34.64 kiB) for dataset users in 23ms.
2025-03-27T07:09:10.712582Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset users
2025-03-27T07:09:10.729119Z  INFO runtime::accelerated_table::refresh_task: Loaded 1 rows (34.64 kiB) for dataset users in 25ms.
```

In addition to viewing the logs, run queries with the Spice SQL REPL to explore the data and confirm that only recently added users are in the dataset.

`docker exec -it spiceai-retention-demo spiced --repl`

```console
Welcome to the Spice.ai SQL REPL! Type 'help' for help.

show tables; -- list available tables
sql> show tables;
+---------------+--------------+--------------+------------+
| table_catalog | table_schema | table_name   | table_type |
+---------------+--------------+--------------+------------+
| spice         | public       | users        | BASE TABLE |
| spice         | runtime      | task_history | BASE TABLE |
+---------------+--------------+--------------+------------+

Time: 0.014326448 seconds. 2 rows.
sql> select email, username, created_at from users;
+--------------------------------------+--------------------------+----------------------------+
| email                                | username                 | created_at                 |
+--------------------------------------+--------------------------+----------------------------+
| user_1743059257413535768@example.com | user_1743059257413551018 | 2025-03-27T07:07:37.414097 |
| user_1743059262422040686@example.com | user_1743059262422063394 | 2025-03-27T07:07:42.423914 |
| user_1743059267444354559@example.com | user_1743059267444361351 | 2025-03-27T07:07:47.444588 |
| user_1743059272460513902@example.com | user_1743059272460540943 | 2025-03-27T07:07:52.462135 |
| user_1743059277474480320@example.com | user_1743059277474485236 | 2025-03-27T07:07:57.474682 |
| user_1743059282485177704@example.com | user_1743059282485198954 | 2025-03-27T07:08:02.485777 |
+--------------------------------------+--------------------------+----------------------------+

Time: 0.00946948 seconds. 6 rows.
```

## Clean up

In another terminal, execute the following command to clean up the containers.

```bash
make clean
```
