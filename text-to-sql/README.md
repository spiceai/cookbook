# Text-to-SQL

This recipe will walk you through using Spice as a text to SQL interface.

## Prerequisites

- Ensure you have the Spice CLI installed. Follow the [Getting Started](https://docs.spiceai.org/getting-started) if you haven't done so.
- Populate `.env`.
  - `SPICE_OPENAI_API_KEY`: A valid OpenAI API key (or equivalent).
- Install `jq` from [here](https://jqlang.github.io/jq/download/)
  - Or `brew install jq` for MacOS.
  - Or `sudo apt-get install jq` for Linux.

## Steps

Separate from using language models to interact with [runtime tools](https://spiceai.org/docs/components/tools), `spice` has a standalone text to SQL endpoint. This provides more granular control of how SQL generation is done, and is more robust to hallucination and misuse of tools.

1. Start Spice

```bash
spice run
```

2. Call the dedicated text-to-sql endpoint

```shell
curl -XPOST "http://localhost:8090/v1/nsql" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Which vendors have made the most trips in 2024?"
  }'
```

Result:

```json
[
  {
    "VendorID": 2,
    "TripCount": 2234617
  },
  {
    "VendorID": 1,
    "TripCount": 729732
  },
  {
    "VendorID": 6,
    "TripCount": 260
  }
]
```

3. Inspect the tools used.

```shell
spice trace nsql --include-input --truncate=40
```

Result:

```shell
TREE                         STATUS DURATION   SPANID           INPUT
nsql                         ✅      7236.41ms 8d3a62d86a6c79ee Which vendors have made the most trips i... (7 characters omitted)
  ├── tool_use::table_schema ✅         0.30ms 8a015258bd98bf03 {"tables":["spice.public.taxi_trips"],"o... (14 characters omitted)
  ├── tool_use::sample_data  ✅      3960.64ms 88bcd4507f3427dd DistinctColumns({"dataset":"spice.public... (36 characters omitted)
  │ ├── sql_query            ✅       849.41ms 8139fd9e40f24729 SELECT "VendorID" FROM (
                                                                               ... (317 characters omitted)
  │ ├── sql_query            ✅      1288.92ms 66a1c6b44bdce707 SELECT tpep_pickup_datetime FROM (
                                                                     ... (367 characters omitted)
  │ ├── sql_query            ✅      1564.23ms 17cbcc14da32e043 SELECT tpep_dropoff_datetime FROM (
                                                                    ... (372 characters omitted)
  │ ├── sql_query            ✅       923.23ms 3129844549f75e7d SELECT passenger_count FROM (
                                                                          ... (342 characters omitted)
  │ ├── sql_query            ✅      1250.90ms 9592a73b9088d47a SELECT trip_distance FROM (
                                                                            ... (332 characters omitted)
  │ ├── sql_query            ✅       911.91ms 447041cb46bf327b SELECT "RatecodeID" FROM (
                                                                             ... (327 characters omitted)
  │ ├── sql_query            ✅      1124.15ms 50e542d209866a43 SELECT store_and_fwd_flag FROM (
                                                                       ... (357 characters omitted)
  │ ├── sql_query            ✅       974.30ms 9b5ebaf36b8eac90 SELECT "PULocationID" FROM (
                                                                           ... (337 characters omitted)
  │ ├── sql_query            ✅       925.27ms 224caf0373318acb SELECT "DOLocationID" FROM (
                                                                           ... (337 characters omitted)
  │ ├── sql_query            ✅       986.47ms de9cc0bc38f9c0f7 SELECT payment_type FROM (
                                                                             ... (327 characters omitted)
  │ ├── sql_query            ✅       937.38ms ddc3e36fa200f7c8 SELECT fare_amount FROM (
                                                                              ... (322 characters omitted)
  │ ├── sql_query            ✅       953.33ms 02743fa12d7b7cf0 SELECT extra FROM (
                                                                                SELE... (292 characters omitted)
  │ ├── sql_query            ✅       783.41ms 077e32f25486eb55 SELECT mta_tax FROM (
                                                                                SE... (302 characters omitted)
  │ ├── sql_query            ✅       815.82ms 2603f86cb8baaf39 SELECT tip_amount FROM (
                                                                               ... (317 characters omitted)
  │ ├── sql_query            ✅       751.80ms 1959a901c5d318de SELECT tolls_amount FROM (
                                                                             ... (327 characters omitted)
  │ ├── sql_query            ✅       910.21ms 01cf3e43a71848b9 SELECT improvement_surcharge FROM (
                                                                    ... (372 characters omitted)
  │ ├── sql_query            ✅       477.02ms 9f6a60c5c3bb93a3 SELECT total_amount FROM (
                                                                             ... (327 characters omitted)
  │ ├── sql_query            ✅       543.88ms 6f5cd85935ef1e68 SELECT congestion_surcharge FROM (
                                                                     ... (367 characters omitted)
  │ └── sql_query            ✅       547.74ms 91c7107bc1cc5762 SELECT "Airport_fee" FROM (
                                                                            ... (332 characters omitted)
  ├── tool_use::sample_data  ✅        44.97ms 4beb25b66b972a86 RandomSample({"dataset":"spice.public.ta... (21 characters omitted)
  │ └── sql_query            ✅        43.29ms 9ca3f50fb665263d SELECT * FROM spice.public.taxi_trips LI... (5 characters omitted)
  ├── ai_completion          ✅      3095.67ms c8006f436478083b {"messages":[{"role":"system","content":... (8362 characters omitted)
  └── sql_query              ✅       177.09ms 19b611a8e9cffb83 SELECT "VendorID", COUNT(*) AS "trip_cou... (140 characters omitted)
```

From this, you can see that `spice` runs the following [tools](https://spiceai.org/docs/components/tools) to help the model write contextual, correct SQL:

- `table_schema`: To show the table schema of each relevant table.
- Sample data from the relevant table(s), both:
  - `random_sample` to sample rows from each table.
  - `sample_distinct_columns` to sample distinct values from each column in the table.

### Return the SQL Query

The `v1/nsql` endpoint can return the SQL query it used in addition to the results. To do this, specify the `Accept: application/vnd.spiceai.sql.v1+json` header.

```shell
curl -XPOST "http://localhost:8090/v1/nsql" \
  -H "Accept: application/vnd.spiceai.sql.v1+json" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What’s the highest tip any passenger gave?"
  }'
```

Returns:

```json
{
  "row_count": 1,
  "schema": {
    "fields": [
      {
        "name": "highest_tip",
        "data_type": "Float64",
        "nullable": true,
        "dict_id": 0,
        "dict_is_ordered": false,
        "metadata": {}
      }
    ],
    "metadata": {}
  },
  "data": [
    {
      "highest_tip": 428.0
    }
  ],
  "sql": "SELECT MAX(\"tip_amount\") AS \"highest_tip\"\nFROM \"spice\".\"public\".\"taxi_trips\""
}
```

### Disable Sampling

To disable sampling in text-to-SQL:

```shell
curl -XPOST "http://localhost:8090/v1/nsql" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Which vendors have made the most trips in 2024?",
     "sample_data_enabled": false
  }'
```

### Specify Tables

To restrict the tables that `spice` uses for text-to-SQL:

```shell
curl -XPOST "http://localhost:8090/v1/nsql" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Which vendors have made the most trips in 2024?",
    "tables": ["taxi_trips"]
  }'
```

## (Optional) Use a Local Model

### Prerequisites

- Get access to the [Llama-3.2-3B-Instruct model](https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct).
- Populate `.env`: update `SPICE_HF_TOKEN` with your [HuggingFace User Access Token](https://huggingface.co/settings/tokens).

**Step 1.** In the `spicepod.yaml`, uncomment the model `local`.

**Step 2.** Restart the `spiced` server.

**Step 3.** Run the NSQL tool, and select the local model.

```shell
>>> spice nsql
Welcome to the Spice.ai NSQL REPL!
Use the arrow keys to navigate: ↓ ↑ → ←
? Select model:
    nsql
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

**Step 5.** (Optional) Check the underlying query

Run `spice sql` in a separate terminal to check the underlying query

```sql
select start_time, parent_span_id, span_id, task, substr(input, 0, 64) as input, execution_duration_ms from runtime.task_history where trace_id=(select trace_id from runtime.task_history where task='nsql') order by start_time asc;
```

````shell
+----------------------------+------------------+------------------+---------------+-----------------------------------------------------------------+-----------------------+
| start_time                 | parent_span_id   | span_id          | task          | input                                                           | execution_duration_ms |
+----------------------------+------------------+------------------+---------------+-----------------------------------------------------------------+-----------------------+
| 2024-10-14T10:28:46.300138 |                  | 3ca45f3db11636c8 | nsql          | What’s the highest tip any passenger gave?                      | 9138.792000000001     |
| 2024-10-14T10:28:46.300380 | 3ca45f3db11636c8 | 528cbddc53d55c70 | ai_completion | {"messages":[{"role":"system","content":"```SQL\nCREATE TABLE I | 9133.243999999999     |
| 2024-10-14T10:28:55.433665 | 3ca45f3db11636c8 | 2b25cd3f59aa6362 | sql_query     | SELECT MAX(tip_amount) AS highest_tip_amount                    | 5.012                 |
|                            |                  |                  |               | FROM taxi_trips                                                 |                       |
+----------------------------+------------------+------------------+---------------+-----------------------------------------------------------------+-----------------------+
````
