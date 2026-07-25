# Snowflake DML — HTTP API Ingestion Pipeline

Works with `v2.0+`

> This recipe demonstrates how to build a mini ingestion pipeline with Spice: fetch data from a public HTTP API ([TVMaze](https://www.tvmaze.com/api)), transform it with SQL, and write it into a writable Snowflake table using **Snowflake DML** (`INSERT`).

## Pre-requisites

- Spice `v2.0+` — [Install Spice](https://docs.spiceai.org/getting-started)
- [A Snowflake account](https://signup.snowflake.com/)

## Step 1. Create the destination table in Snowflake

Sign in to your Snowflake account, open a worksheet, and run:

```sql
CREATE DATABASE IF NOT EXISTS SPICE_DEMO;
USE DATABASE SPICE_DEMO;
USE SCHEMA PUBLIC;

CREATE TABLE IF NOT EXISTS TV_SHOWS (
    id              INTEGER       NOT NULL,
    name            VARCHAR(255),
    type            VARCHAR(100),
    language        VARCHAR(100),
    status          VARCHAR(100),
    runtime         INTEGER,
    premiered       DATE,
    ended           DATE,
    rating_average  FLOAT,
    PRIMARY KEY (id)
);
```

> **No worksheet UI access?** You can run the same DDL from the command line using [`snowflake-connector-python`](https://pypi.org/project/snowflake-connector-python/). Note the account identifier must use the dash form (`<org>-<account>`) for this driver, even though the Spice connector accepts the dot form (`<org>.<account>`):
>
> ```bash
> pip install snowflake-connector-python
> python -c "
> import snowflake.connector
> ddl = '''
> CREATE DATABASE IF NOT EXISTS SPICE_DEMO;
> CREATE TABLE IF NOT EXISTS SPICE_DEMO.PUBLIC.TV_SHOWS (
>     id INTEGER NOT NULL, name VARCHAR(255), type VARCHAR(100),
>     language VARCHAR(100), status VARCHAR(100), runtime INTEGER,
>     premiered DATE, ended DATE, rating_average FLOAT, PRIMARY KEY (id)
> );
> '''
> with snowflake.connector.connect(account='<org>-<account>', user='<username>', password='<password>') as cn:
>     for stmt in filter(None, (s.strip() for s in ddl.split(';'))):
>         cn.cursor().execute(stmt)
> "
> ```

## Step 2. Configure Snowflake credentials

```bash
spice login snowflake -a <account-identifier> -u <username> -p <password>
```

This creates a `.env` file:

```bash
SPICE_SNOWFLAKE_ACCOUNT=<account-identifier>
SPICE_SNOWFLAKE_USERNAME=<username>
SPICE_SNOWFLAKE_PASSWORD=<password>
```

## Step 3. Start Spice

```bash
spice run
```

Expected output:

```
Spice.ai runtime starting...
...
2026-05-10T22:03:07.236786Z  INFO runtime::init::dataset: Dataset tv_shows initializing...
2026-05-10T22:03:07.236915Z  INFO runtime::init::dataset: Dataset tvmaze_shows_raw initializing...
2026-05-10T22:03:07.237083Z  INFO runtime::init::worker: Loading worker [ingest_tvmaze_shows]...
2026-05-10T22:03:07.237202Z  INFO runtime::init::worker: Worker [ingest_tvmaze_shows] loaded, ready for use
2026-05-10T22:03:07.237660Z  INFO runtime::init::worker: Scheduler for worker [ingest_tvmaze_shows] created successfully
2026-05-10T22:03:07.246890Z  INFO runtime::init::dataset: Dataset tvmaze_shows_raw registered (https://api.tvmaze.com/shows), results cache enabled. duration_ms=0
2026-05-10T22:03:07.250581Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2026-05-10T22:03:11.936902Z  INFO runtime::init::dataset: Dataset tv_shows registered (snowflake:SPICE_DEMO.PUBLIC."TV_SHOWS"), results cache enabled. duration_ms=1865
2026-05-10T22:03:12.039156Z  INFO runtime: All components are loaded. Spice runtime is ready!
2026-05-10T22:03:37.238925Z  INFO runtime::init::dataset: Dataset load summary (after 30s): 2/2 ready, 0 unhealthy, 0 still initializing.
```

## Step 4. Wait for the ingestion worker to run

The `ingest_tvmaze_shows` worker runs automatically on the cron schedule. You can inspect its run history in the SQL REPL:

```bash
spice sql
```

```sql
SELECT task, start_time, end_time, error_message
FROM runtime.task_history
WHERE task = 'scheduled_worker'
ORDER BY start_time DESC
LIMIT 5;
```

```
+------------------+--------------------------------+--------------------------------+
|       task       |           start_time           |            end_time            |
|      varchar     |       timestamp[ns] (UTC)      |       timestamp[ns] (UTC)      |
+------------------+--------------------------------+--------------------------------+
| scheduled_worker | 2026-05-10T22:02:00.776514814Z | 2026-05-10T22:02:01.188614794Z |
| scheduled_worker | 2026-05-10T22:01:00.410603700Z | 2026-05-10T22:01:00.776281757Z |
| scheduled_worker | 2026-05-10T22:00:00.002615777Z | 2026-05-10T22:00:02.409577328Z |
+------------------+--------------------------------+--------------------------------+

Time: 0.014705856 seconds. 3 rows.
```

## Step 5. Query the data

Verify rows landed in Snowflake:

```sql
SELECT count(*) FROM tv_shows;
```

```
+----------+
| count(*) |
|   int64  |
+----------+
| 240      |
+----------+

Time: 0.582791267 seconds. 1 rows.
```

> On subsequent runs, the worker only inserts shows not already present in Snowflake, so the count grows incrementally as TVMaze adds new shows.

Top-rated shows:

```sql
SELECT "NAME" AS show_name, "STATUS" AS status, "LANGUAGE" AS language, "RATING_AVERAGE" AS rating_average
FROM tv_shows
WHERE "RATING_AVERAGE" IS NOT NULL
ORDER BY "RATING_AVERAGE" DESC
LIMIT 10;
```

```
+----------------------+---------+----------+----------------+
|       show_name      |  status | language | rating_average |
|        varchar       | varchar |  varchar |     float64    |
+----------------------+---------+----------+----------------+
| Breaking Bad         | Ended   | English  | 9.2            |
| Game of Thrones      | Ended   | English  | 8.9            |
| Firefly              | Ended   | English  | 8.9            |
| The Wire             | Ended   | English  | 8.9            |
| Stargate Atlantis    | Ended   | English  | 8.8            |
| Death Note           | Ended   | Japanese | 8.8            |
| Stargate SG·1        | Ended   | English  | 8.8            |
| Rick and Morty       | Running | English  | 8.8            |
| Person of Interest   | Ended   | English  | 8.8            |
| Battlestar Galactica | Ended   | English  | 8.7            |
+----------------------+---------+----------+----------------+

Time: 0.678913675 seconds. 10 rows.
```

## Learn More

- [Snowflake Data Connector](https://spiceai.org/docs/components/data-connectors/snowflake)
- [HTTP(s) Data Connector](https://docs.spiceai.org/components/data-connectors/https)
- [Spice Workers](https://docs.spiceai.org/features/workers)
- [TVMaze API](https://www.tvmaze.com/api)
