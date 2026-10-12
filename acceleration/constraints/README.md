# Accelerated table data quality with primary keys

Works with `v2.4+`

This recipe demonstrates how a `primary_key` keeps one row per key in a Cayenne acceleration, and how a `time_column` decides which version of a key is kept. This is especially useful for a `refresh_mode: append` dataset whose source updates rows in place or keeps a history of every change.

With `refresh_mode: append`, Spice fetches the rows whose `time_column` is later than the newest one already accelerated. An updated row arrives again as a new row, and Cayenne applies one rule to it, with nothing else to configure:

| `primary_key` | `time_column` | A key that appears more than once |
| ------------- | ------------- | --------------------------------- |
| not set       | any           | Every row is kept.                |
| set           | not set       | One row per key: the version that arrived last. |
| set           | set           | One row per key: the newest by `time_column`. |

This sample runs a local Postgres database with two tables, and a Spice runtime that accelerates both:

- `users` holds one row per user. A worker service increments a random user's `items_bought` every 4 seconds, and a trigger sets `updated_at`. The `users` dataset keeps exactly one row per `email`, updated in place.
- `user_plan_changes` is a history table: every plan change is a new row, and the rows were inserted out of time order. The `user_plans` dataset reads it with `primary_key: email` and `time_column: changed_at`, so it keeps each user's current plan. A late row with an older `changed_at` never replaces a newer one, even when `refresh_append_overlap` re-reads it.

The `on_conflict` setting is deprecated and will be removed in Spice 3.0. This recipe does not use it: with the `cayenne` engine, `primary_key` and `time_column` decide which row is kept.

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

Then observe the logs of the worker service.

`docker logs -f spiceai-constraint-demo-worker`

## Spice Runtime

Start the Spice runtime in the same directory as the `spicepod.yaml` file:

```bash
cd cookbook/acceleration/constraints
spice run
```

At startup, Spice states the rule it inferred for each dataset:

```console
INFO runtime::init::dataset: Dataset 'users' keeps one row per 'email': the newest by 'updated_at', or the version that arrived last when times are equal.
INFO runtime::init::dataset: Dataset 'user_plans' keeps one row per 'email': the newest by 'changed_at', or the version that arrived last when times are equal.
```

## One row per key, updated in place

In another terminal, open the Spice SQL REPL:

```bash
spice sql
```

The worker updates `users` every 4 seconds, and each update arrives as a new row on the next refresh. The `primary_key` replaces the stored row instead of adding another one, so there is still one row per email. The `items_bought` values depend on how long the worker has been running:

```sql
select email, username, items_bought from users order by email;
```

```console
+-------------------------+----------+--------------+
|          email          | username | items_bought |
|         varchar         |  varchar |     int64    |
+-------------------------+----------+--------------+
| alice@sample.com        | alice    | 0            |
| bob@umbrellacorp.com    | bob      | 1            |
| clint@bobsumbrellas.com | clint    | 1            |
| dobbie@hogwarts.ac.uk   | dobbie   | 2            |
| eddie@edslawncare.com   | eddie    | 0            |
+-------------------------+----------+--------------+

Time: 0.001509375 seconds. 5 rows.
```

```sql
select count(*) as rows, count(distinct email) as emails from users;
```

```console
+-------+--------+
|  rows | emails |
| int64 |  int64 |
+-------+--------+
| 5     | 5      |
+-------+--------+

Time: 0.001392042 seconds. 1 rows.
```

## The newest version by time

`user_plan_changes` holds three versions for `alice@sample.com`: `free` at 10:00, `enterprise` at 12:00 and `pro` at 11:00, inserted in that order. The newest by `changed_at` is kept, not the last one inserted:

```sql
select email, plan, changed_at from user_plans order by email;
```

```console
+----------------------+------------+---------------------+
|         email        |    plan    |      changed_at     |
|        varchar       |   varchar  |    timestamp[ns]    |
+----------------------+------------+---------------------+
| alice@sample.com     | enterprise | 2024-06-01T12:00:00 |
| bob@umbrellacorp.com | pro        | 2024-06-01T09:00:00 |
+----------------------+------------+---------------------+

Time: 0.000935333 seconds. 2 rows.
```

Now insert a late row: a change for Alice at 11:30, older than the `enterprise` version already loaded. Run this in a third terminal:

```bash
docker exec constraints-postgres-1 psql -U postgres -c \
  "INSERT INTO user_plan_changes VALUES ('alice@sample.com', 'free', '2024-06-01 11:30:00');"
```

`refresh_append_overlap: 1d` makes each refresh re-read rows up to a day older than the newest loaded one, so the late row is fetched. It is older than the stored version, so Alice stays on `enterprise`. Wait a few seconds for a refresh, then query again:

```sql
select email, plan, changed_at from user_plans order by email;
```

```console
+----------------------+------------+---------------------+
|         email        |    plan    |      changed_at     |
|        varchar       |   varchar  |    timestamp[ns]    |
+----------------------+------------+---------------------+
| alice@sample.com     | enterprise | 2024-06-01T12:00:00 |
| bob@umbrellacorp.com | pro        | 2024-06-01T09:00:00 |
+----------------------+------------+---------------------+

Time: 0.00092075 seconds. 2 rows.
```

A newer change does replace the stored version:

```bash
docker exec constraints-postgres-1 psql -U postgres -c \
  "INSERT INTO user_plan_changes VALUES ('bob@umbrellacorp.com', 'enterprise', '2024-06-01 13:00:00');"
```

```sql
select email, plan, changed_at from user_plans order by email;
```

```console
+----------------------+------------+---------------------+
|         email        |    plan    |      changed_at     |
|        varchar       |   varchar  |    timestamp[ns]    |
+----------------------+------------+---------------------+
| alice@sample.com     | enterprise | 2024-06-01T12:00:00 |
| bob@umbrellacorp.com | enterprise | 2024-06-01T13:00:00 |
+----------------------+------------+---------------------+

Time: 0.000904834 seconds. 2 rows.
```

Exit the Spice SQL REPL with `exit`.

## Things to try

- Remove `time_column` from the `user_plans` dataset. Spice then keeps the version that arrived last, which can differ between refreshes, and logs that at startup. Because `refresh_mode: append` needs a `time_column` to know which rows are new, also set `refresh_mode: full`.
- Remove `primary_key` from a dataset. Every row is kept, so `user_plans` returns every plan change instead of one row per user.

## Clean up

To stop and remove the Docker containers/volumes that were created, run:

`make clean`
