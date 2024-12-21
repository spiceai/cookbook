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
+----------------------------+------------------+------------------+---------------+-----------------------------------------------------------------+-----------------------+
| start_time                 | parent_span_id   | span_id          | task          | input                                                           | execution_duration_ms |
+----------------------------+------------------+------------------+---------------+-----------------------------------------------------------------+-----------------------+
| 2024-10-14T10:18:30.618720 |                  | 3ba34e0b690baf70 | nsql          | How many trips had more than two passengers?                    | 1005.1840000000001    |
| 2024-10-14T10:18:30.621154 | 3ba34e0b690baf70 | c8a36151be8719a8 | ai_completion | {"messages":[{"role":"system","content":"```SQL\nCREATE TABLE I | 996.7589999999999     |
| 2024-10-14T10:18:31.618123 | 3ba34e0b690baf70 | c8fd047ceaf7bc6a | sql_query     | SELECT COUNT(*) AS trip_count                                   | 5.555                 |
|                            |                  |                  |               | FROM taxi_trips                                                 |                       |
|                            |                  |                  |               | WHERE passenger                                                 |                       |
+----------------------------+------------------+------------------+---------------+-----------------------------------------------------------------+-----------------------+

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
