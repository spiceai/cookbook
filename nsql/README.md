# Text to SQL (NSQL)

Spice can provide an end to end system for users to ask natural language questions of their datasets.

## Prerequisites

- [Spice CLI](https://docs.spiceai.org/getting-started) installed.
- The following environment variables set:
  - `SPICE_OPENAI_API_KEY`

## Using a Hosted Model

**Step 1.** Run Spice runtime

```shell
spice run
```

**Step 2.** Run the NSQL tool

```shell
spice nsql
```

**Step 3.** Ask a question of the dataset (`taxi_trips`).

```shell
>>> spice nsql
Welcome to the Spice.ai NSQL REPL!
Using model:
 oai

Enter a query in natural language.
nsql> How many trips had more than two passengers?
+------------+
| trip_count |
+------------+
| 199155     |
+------------+

Time: 1.006369 seconds. 1 rows.
```

**Step 4.** Check the underlying query

```shell
spice sql 
```

Then:

```sql
SELECT start_time, parent_span_id, span_id, task, substr(input, 0, 64) AS input, execution_duration_ms FROM runtime.task_history WHERE trace_id=(SELECT trace_id FROM runtime.task_history WHERE task='nsql') ORDER BY start_time ASC;
```

```shell
+----------------------------+------------------+------------------+------------------------+-----------------------------------------------------------------+-----------------------+
| start_time                 | parent_span_id   | span_id          | task                   | input                                                           | execution_duration_ms |
+----------------------------+------------------+------------------+------------------------+-----------------------------------------------------------------+-----------------------+
| 2024-12-31T01:27:07.602167 |                  | 064f2ab4a7b4b2fb | nsql                   | How many trips had more than two passengers?                    | 1326.028              |
| 2024-12-31T01:27:07.602244 | 064f2ab4a7b4b2fb | 80d5fb34c641513b | tool_use::table_schema | {"tables":["spice.public.taxi_trips"],"output":"full"}          | 0.13799999999999998   |
| 2024-12-31T01:27:07.602555 | 064f2ab4a7b4b2fb | 8ff5f010ec707dfe | tool_use::sample_data  | DistinctColumns({"dataset":"spice.public.taxi_trips","limit":3, | 276.22400000000005    |
| 2024-12-31T01:27:07.602601 | 8ff5f010ec707dfe | dccfb0bb2ae23fc0 | sql_query              | SELECT "VendorID" FROM (                                        | 18.211000000000002    |
|                            |                  |                  |                        |                 SELECT "VendorID", 1 a                          |                       |
| 2024-12-31T01:27:07.620847 | 8ff5f010ec707dfe | 23b0be962838a09c | sql_query              | SELECT tpep_pickup_datetime FROM (                              | 36.894999999999996    |
|                            |                  |                  |                        |                 SELECT tpep_                                    |                       |
| 2024-12-31T01:27:07.657776 | 8ff5f010ec707dfe | a34a235e2f3a2faf | sql_query              | SELECT tpep_dropoff_datetime FROM (                             | 34.202999999999996    |
|                            |                  |                  |                        |                 SELECT tpep                                     |                       |
| 2024-12-31T01:27:07.691994 | 8ff5f010ec707dfe | 29ab980be6ba5dd6 | sql_query              | SELECT passenger_count FROM (                                   | 8.267999999999999     |
|                            |                  |                  |                        |                 SELECT passenger_                               |                       |
| 2024-12-31T01:27:07.700280 | 8ff5f010ec707dfe | 0585805f332cb6eb | sql_query              | SELECT trip_distance FROM (                                     | 17.111                |
|                            |                  |                  |                        |                 SELECT trip_distanc                             |                       |
| 2024-12-31T01:27:07.717418 | 8ff5f010ec707dfe | 9ccdb35a36bee57d | sql_query              | SELECT "RatecodeID" FROM (                                      | 18.592000000000002    |
|                            |                  |                  |                        |                 SELECT "RatecodeID",                            |                       |
| 2024-12-31T01:27:07.736024 | 8ff5f010ec707dfe | 2cea0a431b726880 | sql_query              | SELECT store_and_fwd_flag FROM (                                | 24.061                |
|                            |                  |                  |                        |                 SELECT store_a                                  |                       |
| 2024-12-31T01:27:07.760102 | 8ff5f010ec707dfe | a4af137da79af8fb | sql_query              | SELECT "PULocationID" FROM (                                    | 8.123                 |
|                            |                  |                  |                        |                 SELECT "PULocation                              |                       |
| 2024-12-31T01:27:07.768240 | 8ff5f010ec707dfe | dc4f1476a1df9eac | sql_query              | SELECT "DOLocationID" FROM (                                    | 9.456000000000001     |
|                            |                  |                  |                        |                 SELECT "DOLocation                              |                       |
| 2024-12-31T01:27:07.777714 | 8ff5f010ec707dfe | fb479f85bd865335 | sql_query              | SELECT payment_type FROM (                                      | 17.267                |
|                            |                  |                  |                        |                 SELECT payment_type,                            |                       |
| 2024-12-31T01:27:07.794998 | 8ff5f010ec707dfe | 1f0e835a7bed38c6 | sql_query              | SELECT fare_amount FROM (                                       | 15.381                |
|                            |                  |                  |                        |                 SELECT fare_amount, 1                           |                       |
| 2024-12-31T01:27:07.810393 | 8ff5f010ec707dfe | a617589b82f71ea4 | sql_query              | SELECT extra FROM (                                             | 8.113                 |
|                            |                  |                  |                        |                 SELECT extra, 1 as priority                     |                       |
| 2024-12-31T01:27:07.818521 | 8ff5f010ec707dfe | 17864cff3e482452 | sql_query              | SELECT mta_tax FROM (                                           | 8.722000000000001     |
|                            |                  |                  |                        |                 SELECT mta_tax, 1 as prio                       |                       |
| 2024-12-31T01:27:07.827257 | 8ff5f010ec707dfe | 62f7203c8b28d458 | sql_query              | SELECT tip_amount FROM (                                        | 9.355                 |
|                            |                  |                  |                        |                 SELECT tip_amount, 1 a                          |                       |
| 2024-12-31T01:27:07.836631 | 8ff5f010ec707dfe | 9f312f011d06d6c9 | sql_query              | SELECT tolls_amount FROM (                                      | 8.026                 |
|                            |                  |                  |                        |                 SELECT tolls_amount,                            |                       |
| 2024-12-31T01:27:07.844674 | 8ff5f010ec707dfe | 39d91a0327de8506 | sql_query              | SELECT improvement_surcharge FROM (                             | 8.066                 |
|                            |                  |                  |                        |                 SELECT impr                                     |                       |
| 2024-12-31T01:27:07.852756 | 8ff5f010ec707dfe | ae6ed37e57d00fb5 | sql_query              | SELECT total_amount FROM (                                      | 9.456000000000001     |
|                            |                  |                  |                        |                 SELECT total_amount,                            |                       |
| 2024-12-31T01:27:07.862236 | 8ff5f010ec707dfe | bc1f149cef3857a7 | sql_query              | SELECT congestion_surcharge FROM (                              | 7.875                 |
|                            |                  |                  |                        |                 SELECT conge                                    |                       |
| 2024-12-31T01:27:07.870127 | 8ff5f010ec707dfe | 06033de33f9b6118 | sql_query              | SELECT "Airport_fee" FROM (                                     | 8.503                 |
|                            |                  |                  |                        |                 SELECT "Airport_fee                             |                       |
| 2024-12-31T01:27:07.878795 | 064f2ab4a7b4b2fb | ef051a38ee72fc36 | tool_use::sample_data  | RandomSample({"dataset":"spice.public.taxi_trips","limit":3})   | 1.0430000000000001    |
| 2024-12-31T01:27:07.878806 | ef051a38ee72fc36 | be84c5f1a9ceab97 | sql_query              | SELECT * FROM spice.public.taxi_trips LIMIT 3                   | 0.955                 |
| 2024-12-31T01:27:07.880187 | 064f2ab4a7b4b2fb | d76c89046ffebfcd | ai_completion          | {"messages":[{"role":"system","content":"Task: Write a SQL quer | 1039.372              |
+----------------------------+------------------+------------------+------------------------+-----------------------------------------------------------------+-----------------------+
Time: 0.01162825 seconds. 3 rows.
```

### (Optional) Use a Local Model

**Step 1.** In the `spicepod.yaml`, uncomment the model `local`.

**Step 2.** Restart the `spiced` server.

**Step 3.** Run the NSQL tool, and select the local model.

```shell
>>> ~/.spice/bin/spice nsql
Welcome to the Spice.ai NSQL REPL!
Use the arrow keys to navigate: ↓ ↑ → ←
? Select model:
    oai
  ▸ local
```

**Step 4.** Ask a question

```shell
nsql> What’s the highest tip any passenger gave?
+--------------------+
| highest_tip_amount |
+--------------------+
| 428.0              |
+--------------------+

Time: 9.141290 seconds. 1 rows.
```

Step 5.** (Optional) Check the underlying query

```sql
select start_time, parent_span_id, span_id, task, substr(input, 0, 64) as input, execution_duration_ms from runtime.task_history where trace_id=(select trace_id from runtime.task_history where task='nsql') order by start_time asc;
```

```shell
+----------------------------+------------------+------------------+---------------+-----------------------------------------------------------------+-----------------------+
| start_time                 | parent_span_id   | span_id          | task          | input                                                           | execution_duration_ms |
+----------------------------+------------------+------------------+---------------+-----------------------------------------------------------------+-----------------------+
| 2024-10-14T10:28:46.300138 |                  | 3ca45f3db11636c8 | nsql          | What’s the highest tip any passenger gave?                      | 9138.792000000001     |
| 2024-10-14T10:28:46.300380 | 3ca45f3db11636c8 | 528cbddc53d55c70 | ai_completion | {"messages":[{"role":"system","content":"```SQL\nCREATE TABLE I | 9133.243999999999     |
| 2024-10-14T10:28:55.433665 | 3ca45f3db11636c8 | 2b25cd3f59aa6362 | sql_query     | SELECT MAX(tip_amount) AS highest_tip_amount                    | 5.012                 |
|                            |                  |                  |               | FROM taxi_trips                                                 |                       |
+----------------------------+------------------+------------------+---------------+-----------------------------------------------------------------+-----------------------+
```
