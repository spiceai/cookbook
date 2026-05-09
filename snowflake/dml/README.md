# Snowflake DML — HTTP API Ingestion Pipeline

Works with `v2.0+`

> This recipe demonstrates how to build a mini ingestion pipeline with Spice: fetch data from a public HTTP API ([TVMaze](https://www.tvmaze.com/api)), transform it with SQL, and write it into a writable Snowflake table using **Snowflake DML** (`INSERT`).

## Architecture

```
TVMaze HTTP API  ──(HTTP connector)──►  tvmaze_shows_raw  (read-only, in-memory)
                                                │
                                   ingest_tvmaze_shows worker
                                      (cron: every hour)
                                         INSERT new rows
                                                │
                                                ▼
                                      Snowflake: TV_SHOWS  (read_write)
```

The **worker** (`ingest_tvmaze_shows`) runs on a cron schedule, fetches shows from the TVMaze API, and inserts any that are not already in Snowflake. Its execution history is recorded in `runtime.task_history`.

## Pre-requisites

- Spice `v1.0+` — [Install Spice](https://docs.spiceai.org/getting-started/installation)
- A Snowflake account — [free trial](https://signup.snowflake.com/) if needed

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

## Step 2. Configure Snowflake credentials

```bash
spice login snowflake -a <account-identifier> -u <username> -p <password>
```

This creates a `.env` file. Add `SPICE_SNOWFLAKE_ROLE` and `SPICE_SNOWFLAKE_WAREHOUSE`:

```bash
SPICE_SNOWFLAKE_ACCOUNT=<account-identifier>
SPICE_SNOWFLAKE_USERNAME=<username>
SPICE_SNOWFLAKE_PASSWORD=<password>
SPICE_SNOWFLAKE_ROLE=accountadmin
SPICE_SNOWFLAKE_WAREHOUSE=COMPUTE_WH
```

## Step 3. Start Spice

```bash
cd snowflake/dml
spice run
```

Expected output:

```
Spice.ai runtime starting...
...
INFO runtime::init::dataset: Dataset tvmaze_shows_raw registered (https://api.tvmaze.com/shows), results cache enabled.
INFO runtime::init::dataset: Dataset tv_shows registered (snowflake:SPICE_DEMO.PUBLIC.TV_SHOWS), results cache enabled.
INFO runtime: All components are loaded. Spice runtime is ready!
```

## Step 4. Wait for the ingestion worker to run

The `ingest_tvmaze_shows` worker runs automatically on the cron schedule. You can inspect its run history in the SQL REPL:

```bash
spice sql
```

```sql
SELECT task, status, start_time, end_time, error_message
FROM runtime.task_history
WHERE task = 'scheduled_worker'
ORDER BY start_time DESC
LIMIT 5;
```

```
+------------------+---------+---------------------+---------------------+---------------+
| task             | status  | start_time          | end_time            | error_message |
+------------------+---------+---------------------+---------------------+---------------+
| scheduled_worker | success | 2025-01-01 10:00:02 | 2025-01-01 10:00:07 |               |
+------------------+---------+---------------------+---------------------+---------------+
```

## Step 5. Query the data

Verify rows landed in Snowflake:

```sql
SELECT count(*) FROM tv_shows;
```

```
+----------+
| count(*) |
+----------+
| 500      |
+----------+
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
+------------------------+---------+----------+----------------+
| show_name              | status  | language | rating_average |
+------------------------+---------+----------+----------------+
| Breaking Bad           | Ended   | English  | 9.2            |
| The Wire               | Ended   | English  | 9.2            |
| ...                    | ...     | ...      | ...            |
+------------------------+---------+----------+----------------+
```

## Learn More

- [Snowflake Data Connector](https://spiceai.org/docs/components/data-connectors/snowflake)
- [HTTP(s) Data Connector](https://docs.spiceai.org/components/data-connectors/https)
- [Spice Workers](https://docs.spiceai.org/components/workers)
- [TVMaze API](https://www.tvmaze.com/api)
