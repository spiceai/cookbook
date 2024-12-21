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

Separate from using language models to interact with [runtime tools](https://docs.spiceai.org/features/ai-gateway/runtime_tools), `spice` has a standalone text to SQL endpoint. This provides more granular control of how SQL generation is done, and is more robust to hallucination and misuse of tools.

1. Start Spice

  ```bash
  spice run
  ```

2. Call the dedicated text-to-sql endpoint

  ```shell
  curl -XPOST "http://localhost:8090/v1/nsql" \
    -H "Content-Type: application/json" \
    -d '{
      "query": "Which vendors have made the most trips this year?"
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
  curl -X POST "http://localhost:8090/v1/sql" \
    --data "
      SELECT input
      FROM runtime.task_history
      WHERE trace_id = (
        SELECT trace_id
        FROM runtime.task_history
        WHERE task = 'nsql'
        LIMIT 1
      )
      AND task = 'ai_completion';
    " \
    | jq -cr '.[0].input' \
    | jq '.'
  ```

  Result:

  ```json
  {
    "messages": [
      {
        "role": "system",
        "content": "Task: Write a SQL query to answer this question: _\\\"Which vendors have made the most trips this year?\\\"_. Instruction: Return only valid SQL code, nothing additional. Columns with capitals must be quoted. For tables with schemas and catalogs '\"catalog\".\"schema\".\"table\"' not '\"catalog.schema.table\"'."
      },
      {
        "role": "assistant",
        "tool_calls": [
          {
            "id": "schemas-nsql",
            "type": "function",
            "function": {
              "name": "table_schema",
              "arguments": "{\"tables\":[\"spice.public.taxi_trips\"]}"
            }
          }
        ]
      },
      {
        "role": "tool",
        "content": "[{\"schema\":{\"fields\":[{\"data_type\":\"Int32\",\"dict_id\":0,\"dict_is_ordered\":false,\"metadata\":{},\"name\":\"VendorID\",\"nullable\":true},{\"data_type\":{\"Timestamp\":[\"Microsecond\",null]},\"dict_id\":0,\"dict_is_ordered\":false,\"metadata\":{},\"name\":\"tpep_pickup_datetime\",\"nullable\":true},{\"data_type\":{\"Timestamp\":[\"Microsecond\",null]},\"dict_id\":0,\"dict_is_ordered\":false,\"metadata\":{},\"name\":\"tpep_dropoff_datetime\",\"nullable\":true},{\"data_type\":\"Int64\",\"dict_id\":0,\"dict_is_ordered\":false,\"metadata\":{},\"name\":\"passenger_count\",\"nullable\":true},{\"data_type\":\"Float64\",\"dict_id\":0,\"dict_is_ordered\":false,\"metadata\":{},\"name\":\"trip_distance\",\"nullable\":true},{\"data_type\":\"Int64\",\"dict_id\":0,\"dict_is_ordered\":false,\"metadata\":{},\"name\":\"RatecodeID\",\"nullable\":true},{\"data_type\":\"Utf8\",\"dict_id\":0,\"dict_is_ordered\":false,\"metadata\":{},\"name\":\"store_and_fwd_flag\",\"nullable\":true},{\"data_type\":\"Int32\",\"dict_id\":0,\"dict_is_ordered\":false,\"metadata\":{},\"name\":\"PULocationID\",\"nullable\":true},{\"data_type\":\"Int32\",\"dict_id\":0,\"dict_is_ordered\":false,\"metadata\":{},\"name\":\"DOLocationID\",\"nullable\":true},{\"data_type\":\"Int64\",\"dict_id\":0,\"dict_is_ordered\":false,\"metadata\":{},\"name\":\"payment_type\",\"nullable\":true},{\"data_type\":\"Float64\",\"dict_id\":0,\"dict_is_ordered\":false,\"metadata\":{},\"name\":\"fare_amount\",\"nullable\":true},{\"data_type\":\"Float64\",\"dict_id\":0,\"dict_is_ordered\":false,\"metadata\":{},\"name\":\"extra\",\"nullable\":true},{\"data_type\":\"Float64\",\"dict_id\":0,\"dict_is_ordered\":false,\"metadata\":{},\"name\":\"mta_tax\",\"nullable\":true},{\"data_type\":\"Float64\",\"dict_id\":0,\"dict_is_ordered\":false,\"metadata\":{},\"name\":\"tip_amount\",\"nullable\":true},{\"data_type\":\"Float64\",\"dict_id\":0,\"dict_is_ordered\":false,\"metadata\":{},\"name\":\"tolls_amount\",\"nullable\":true},{\"data_type\":\"Float64\",\"dict_id\":0,\"dict_is_ordered\":false,\"metadata\":{},\"name\":\"improvement_surcharge\",\"nullable\":true},{\"data_type\":\"Float64\",\"dict_id\":0,\"dict_is_ordered\":false,\"metadata\":{},\"name\":\"total_amount\",\"nullable\":true},{\"data_type\":\"Float64\",\"dict_id\":0,\"dict_is_ordered\":false,\"metadata\":{},\"name\":\"congestion_surcharge\",\"nullable\":true},{\"data_type\":\"Float64\",\"dict_id\":0,\"dict_is_ordered\":false,\"metadata\":{},\"name\":\"Airport_fee\",\"nullable\":true}],\"metadata\":{}},\"table\":\"spice.public.taxi_trips\"}]",
        "tool_call_id": "schemas-nsql"
      },
      {
        "role": "assistant",
        "tool_calls": [
          {
            "id": "distinct-spice.public.taxi_trips-nsql",
            "type": "function",
            "function": {
              "name": "sample_data",
              "arguments": "{\"dataset\":\"spice.public.taxi_trips\",\"limit\":3,\"cols\":null}"
            }
          }
        ]
      },
      {
        "role": "tool",
        "content": "\"+----------+----------------------+-----------------------+-----------------+---------------+------------+--------------------+--------------+--------------+--------------+-------------+-------+---------+------------+--------------+-----------------------+--------------+----------------------+-------------+\\n| VendorID | tpep_pickup_datetime | tpep_dropoff_datetime | passenger_count | trip_distance | RatecodeID | store_and_fwd_flag | PULocationID | DOLocationID | payment_type | fare_amount | extra | mta_tax | tip_amount | tolls_amount | improvement_surcharge | total_amount | congestion_surcharge | Airport_fee |\\n+----------+----------------------+-----------------------+-----------------+---------------+------------+--------------------+--------------+--------------+--------------+-------------+-------+---------+------------+--------------+-----------------------+--------------+----------------------+-------------+\\n| 1        | 2002-12-31T22:59:39  | 2002-12-31T23:05:41   | 0               | 0.0           | 1          | N                  | 1            | 1            | 0            | -899.0      | -7.5  | -0.5    | -80.0      | -80.0        | -1.0                  | -900.0       | -2.5                 | -1.75       |\\n| 2        | 2009-01-01T00:24:09  | 2009-01-01T01:13:00   | 1               | 0.01          | 2          | Y                  | 2            | 2            | 1            | -800.0      | -6.0  | 0.0     | -66.02     | -60.0        | -0.3                  | -801.0       | -0.75                | 0.0         |\\n| 6        | 2009-01-01T23:30:39  | 2009-01-02T00:01:39   | 2               | 0.02          | 3          |                    | 3            | 3            | 2            | -744.3      | -5.0  | 0.5     | -65.1      | -56.64       | 0.0                   | -753.74      | 0.0                  | 1.75        |\\n+----------+----------------------+-----------------------+-----------------+---------------+------------+--------------------+--------------+--------------+--------------+-------------+-------+---------+------------+--------------+-----------------------+--------------+----------------------+-------------+\"",
        "tool_call_id": "distinct-spice.public.taxi_trips-nsql"
      },
      {
        "role": "assistant",
        "tool_calls": [
          {
            "id": "distinct-spice.public.taxi_trips-nsql",
            "type": "function",
            "function": {
              "name": "sample_data",
              "arguments": "{\"dataset\":\"spice.public.taxi_trips\",\"limit\":3}"
            }
          }
        ]
      },
      {
        "role": "tool",
        "content": "\"+----------+----------------------+-----------------------+-----------------+---------------+------------+--------------------+--------------+--------------+--------------+-------------+-------+---------+------------+--------------+-----------------------+--------------+----------------------+-------------+\\n| VendorID | tpep_pickup_datetime | tpep_dropoff_datetime | passenger_count | trip_distance | RatecodeID | store_and_fwd_flag | PULocationID | DOLocationID | payment_type | fare_amount | extra | mta_tax | tip_amount | tolls_amount | improvement_surcharge | total_amount | congestion_surcharge | Airport_fee |\\n+----------+----------------------+-----------------------+-----------------+---------------+------------+--------------------+--------------+--------------+--------------+-------------+-------+---------+------------+--------------+-----------------------+--------------+----------------------+-------------+\\n| 2        | 2024-01-23T15:35:31  | 2024-01-23T16:26:51   | 2               | 21.06         | 2          | N                  | 132          | 87           | 1            | 70.0        | 0.0   | 0.5     | 20.23      | 6.94         | 1.0                   | 102.92       | 2.5                  | 1.75        |\\n| 2        | 2024-01-23T15:23:18  | 2024-01-23T15:46:22   | 2               | 1.57          | 1          | N                  | 142          | 186          | 2            | 19.8        | 0.0   | 0.5     | 0.0        | 0.0          | 1.0                   | 23.8         | 2.5                  | 0.0         |\\n| 2        | 2024-01-23T15:52:48  | 2024-01-23T15:56:39   | 2               | 0.66          | 1          | N                  | 142          | 239          | 2            | 5.8         | 0.0   | 0.5     | 0.0        | 0.0          | 1.0                   | 9.8          | 2.5                  | 0.0         |\\n+----------+----------------------+-----------------------+-----------------+---------------+------------+--------------------+--------------+--------------+--------------+-------------+-------+---------+------------+--------------+-----------------------+--------------+----------------------+-------------+\"",
        "tool_call_id": "distinct-spice.public.taxi_trips-nsql"
      }
    ],
    "model": "nql",
    "response_format": {
      "type": "json_schema",
      "json_schema": {
        "name": "sql_mode",
        "schema": {
          "$schema": "http://json-schema.org/draft-07/schema#",
          "additionalProperties": false,
          "properties": {
            "sql": {
              "type": "string"
            }
          },
          "required": [
            "sql"
          ],
          "title": "StructuredNsqlOutput",
          "type": "object"
        },
        "strict": true
      }
    }
  }
  ```

From this, you can see that `spice` runs the following [tools](https://docs.spiceai.org/features/ai-gateway/runtime_tools) to help the model write contextual, correct SQL:

- `table_schema`: To show the table schema of each relevant table.
- Sample data from the relevant table(s), both:
  - `random_sample` to sample rows from each table.
  - `sample_distinct_columns` to sample distinct values from each column in the table.

### Disable Sampling

To disable sampling in text-to-SQL:

```shell
curl -XPOST "http://localhost:8090/v1/nsql" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Which vendors have made the most trips this year?",
     "sample_data_enabled": false
  }'
```

### Specify Tables

To restrict the tables that `spice` uses for text-to-SQL:

```shell
curl -XPOST "http://localhost:8090/v1/nsql" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Which vendors have made the most trips this year?",
    "tables": ["taxi_trips"]
  }'
```
