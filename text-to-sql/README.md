# Text-to-SQL (NSQL)

This recipe demonstrates how to use Spice.ai as an intelligent text-to-SQL interface, so you can query your data using natural language instead of writing SQL manually.

## What You'll Learn

- How to use Spice's natural language SQL generation
- Two methods to interact with the text-to-SQL endpoint (CLI and API)
- How to inspect the AI reasoning process
- Advanced options for customizing SQL generation
- (Optional) Running with a local AI model

## Prerequisites

**Required:**

1. **Install Spice CLI** - Follow the [Getting Started guide](https://docs.spiceai.org/getting-started) if you haven't already.

2. **Clone this repository:**

   ```bash
   git clone https://github.com/spiceai/cookbook.git  # Skip if already cloned
   cd cookbook/text-to-sql
   ```

3. **Configure your environment:**
   - Create/update a `.env` file in this directory
   - Add your OpenAI API key:

```env
SPICE_OPENAI_API_KEY=your_openai_api_key_here
```

- Get an API key from [OpenAI Platform](https://platform.openai.com/api-keys)

**Optional (for advanced examples):**

- **Install `jq`** (for pretty-printing JSON):
  - macOS: `brew install jq`
  - Ubuntu/Debian: `sudo apt-get install jq`
  - Fedora: `sudo dnf install jq`
  - Other platforms: [jqlang.github.io/jq/download](https://jqlang.github.io/jq/download/)

## Background

Spice provides a dedicated text-to-SQL endpoint that offers more control and reliability than generic LLM tool use. The system:

- Automatically analyzes your database schema
- Samples data to understand content and patterns
- Generates contextually accurate SQL queries
- Is more robust against hallucinations and errors

This is separate from Spice's [runtime tools](https://spiceai.org/docs/components/tools) feature and provides specialized text-to-SQL capabilities.

## Tutorial

### Step 1: Start the Spice Runtime

Start the Spice runtime in your terminal:

```bash
spice run
```

You should see output indicating that Spice is loading datasets and models. Wait for the message showing the runtime is ready (typically takes 10-30 seconds on first run).

The runtime will:

- Load the NYC taxi trips dataset
- Initialize the text-to-SQL AI model
- Start the API server on `http://localhost:8090`

**Tip:** Keep this terminal window open. Open a new terminal for the following steps.

### Step 2: Query Using Natural Language

You can interact with your data using natural language in two ways:

#### Method 1: Interactive CLI (Recommended for Exploration)

The CLI provides an interactive REPL (Read-Eval-Print Loop) for asking questions:

```shell
spice nsql
```

You'll see a welcome message and can start asking questions:

```shell
nsql> Which vendors have made the most trips in 2024?
+----------+------------+
| VendorID | trip_count |
+----------+------------+
| 2        | 2234617    |
| 1        | 729732     |
| 6        | 260        |
+----------+------------+

Time: 1.824840 seconds. 3 rows.
```

**Try these example queries:**

- `What's the average trip distance?`
- `Show me the top 5 most popular pickup locations`
- `What was the highest tip amount?`

Press `Ctrl+C` to exit the REPL.

#### Method 2: HTTP API (Recommended for Applications)

For programmatic access or integration into applications, use the HTTP API:

```shell
curl -XPOST "http://localhost:8090/v1/nsql" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Which vendors have made the most trips in 2024?"
  }' | jq
```

**Response:**

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

The API returns results as JSON, making it easy to integrate into web applications, scripts, or data pipelines.

### Step 3: Understand How It Works (Observability)

Spice provides powerful observability tools to see exactly how it converts your natural language into SQL.

**View the execution trace:**

```shell
spice trace nsql --include-input --truncate=40
```

**Result:**

```shell
TREE                         STATUS DURATION   SPANID           INPUT
nsql                         ✅      1824.15ms 12f07906aaf5da28 Which vendors have made the most trips i... (7 characters omitted)
  ├── tool_use::table_schema ✅         0.17ms ccd6c135f476b667 {"tables":["spice.public.taxi_trips"],"o... (14 characters omitted)
  ├── tool_use::sample_data  ✅        59.85ms ed37435e258ca21a DistinctColumns({"dataset":"spice.public... (36 characters omitted)
  │ ├── sql_query            ✅        20.64ms d2e7e3164690c7a8 SELECT "VendorID" FROM (
                                                                               ... (317 characters omitted)
  │ ├── sql_query            ✅        29.04ms 13c911276c86bf00 SELECT tpep_pickup_datetime FROM (
                                                                     ... (367 characters omitted)
  │ ├── sql_query            ✅        28.99ms 9d46a93ff038b8da SELECT tpep_dropoff_datetime FROM (
                                                                    ... (372 characters omitted)
  │ ├── sql_query            ✅        16.05ms 5b7cd9fe77fe9b2a SELECT passenger_count FROM (
                                                                          ... (342 characters omitted)
  │ ├── sql_query            ✅        13.48ms 3681e7f855a7fe37 SELECT trip_distance FROM (
                                                                            ... (332 characters omitted)
  │ ├── sql_query            ✅         8.34ms 297ec1b7e1459834 SELECT "RatecodeID" FROM (
                                                                             ... (327 characters omitted)
  │ ├── sql_query            ✅         8.56ms 72784b4e2e5558b6 SELECT store_and_fwd_flag FROM (
                                                                       ... (357 characters omitted)
  │ ├── sql_query            ✅         9.85ms 90df43952c18ef05 SELECT "PULocationID" FROM (
                                                                           ... (337 characters omitted)
  │ ├── sql_query            ✅         7.97ms 2712e68354273151 SELECT "DOLocationID" FROM (
                                                                           ... (337 characters omitted)
  │ ├── sql_query            ✅         3.85ms 1bf083de2fc8cb6b SELECT payment_type FROM (
                                                                             ... (327 characters omitted)
  │ ├── sql_query            ✅         4.98ms b005cf6b9ad59b97 SELECT fare_amount FROM (
                                                                              ... (322 characters omitted)
  │ ├── sql_query            ✅         9.29ms 0e5d432e33d78842 SELECT extra FROM (
                                                                                SELE... (292 characters omitted)
  │ ├── sql_query            ✅         6.51ms 4fdec9d696879881 SELECT mta_tax FROM (
                                                                                SE... (302 characters omitted)
  │ ├── sql_query            ✅         9.66ms 839e94d954ed47ae SELECT tip_amount FROM (
                                                                               ... (317 characters omitted)
  │ ├── sql_query            ✅         8.11ms d8f10a738e0d9f5b SELECT tolls_amount FROM (
                                                                             ... (327 characters omitted)
  │ ├── sql_query            ✅         5.80ms 49f029f6589b0a81 SELECT improvement_surcharge FROM (
                                                                    ... (372 characters omitted)
  │ ├── sql_query            ✅         4.02ms 3cd2bf1818a6f2c8 SELECT total_amount FROM (
                                                                             ... (327 characters omitted)
  │ ├── sql_query            ✅         3.04ms 5323aea0774302a1 SELECT congestion_surcharge FROM (
                                                                     ... (367 characters omitted)
  │ └── sql_query            ✅         2.38ms fcd8e6da9bbbd069 SELECT "Airport_fee" FROM (
                                                                            ... (332 characters omitted)
  ├── tool_use::sample_data  ✅         9.90ms 1ff95d7d9c447640 RandomSample({"dataset":"spice.public.ta... (21 characters omitted)
  │ └── sql_query            ✅        11.09ms 360a4251c2a21af0 SELECT * FROM spice.public.taxi_trips LI... (5 characters omitted)
  ├── ai_completion          ✅      1756.85ms 09e7b05de4071457 {"messages":[{"role":"system","content":... (6934 characters omitted)
  └── sql_query              ✅         6.40ms ea2f648224bbd773 SELECT "VendorID", COUNT(*) AS "trip_cou... (140 characters omitted)
```

**What's happening here:**

The trace shows Spice's AI agent using [tools](https://spiceai.org/docs/components/tools) to gather context before generating SQL:

1. **`table_schema`** - Fetches the schema (column names, types) of relevant tables
2. **`sample_data`** - Gathers sample data in two ways:
   - **`sample_distinct_columns`** - Gets unique values from each column (helps understand categorical data like VendorID)
   - **`random_sample`** - Fetches random rows to understand data patterns
3. **`ai_completion`** - The LLM generates SQL based on the schema and samples
4. **`sql_query`** - Executes the generated SQL and returns results

This multi-step process ensures the AI generates accurate, context-aware SQL queries.

## Advanced Usage

### See the Generated SQL

Sometimes you want to see the actual SQL query that was generated:

```shell
curl -XPOST "http://localhost:8090/v1/nsql" \
  -H "Accept: application/vnd.spiceai.sql.v1+json" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the highest tip any passenger gave?"
  }' | jq
```

**Response includes the SQL:**

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

**Use case:** This is helpful for:

- Learning SQL by seeing how natural language maps to queries
- Debugging unexpected results
- Validating the AI's interpretation of your question
- Copying SQL for use in other tools

### Disable Data Sampling

For faster queries or when working with well-documented schemas, you can skip data sampling:

```shell
curl -XPOST "http://localhost:8090/v1/nsql" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Which vendors have made the most trips in 2024?",
    "sample_data_enabled": false
  }'
```

**Trade-off:** Faster execution but potentially less accurate SQL for complex queries.

### Restrict to Specific Tables

For better performance and accuracy in multi-table databases, specify which tables to query:

```shell
curl -XPOST "http://localhost:8090/v1/nsql" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Which vendors have made the most trips in 2024?",
    "tables": ["taxi_trips"]
  }'
```

**Use case:** Essential when:

- Your database has many tables
- You know which tables contain relevant data
- You want to avoid the AI considering irrelevant tables

## (Optional) Using a Local AI Model

Want to run everything locally without API costs? You can use a local Llama model.

### Prerequisites

1. **Get model access:**
   - Visit [Llama-3.2-3B-Instruct on HuggingFace](https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct)
   - Accept the license agreement

2. **Get your HuggingFace token:**
   - Go to [HuggingFace Settings → Tokens](https://huggingface.co/settings/tokens)
   - Create a token with read access
   - Add to your `.env` file:

```env
SPICE_HF_TOKEN=your_huggingface_token_here
```

### Steps

**1. Enable the local model:**

Edit `spicepod.yaml` and uncomment the `local` model section (look for commented YAML blocks).

**2. Restart Spice:**

Stop the existing `spice run` process (Ctrl+C) and start it again:

```bash
spice run
```

The first run will download the model (~2GB), which may take a few minutes.

**3. Use the local model:**

When you start the NSQL CLI, you'll now see a model selection menu:

```shell
spice nsql
```

```console
Welcome to the Spice.ai NSQL REPL!
Use the arrow keys to navigate: ↓ ↑ → ←
? Select model:
    nsql
  ▸ local
```

Select `local` and ask your question:

```shell
nsql> What's the highest tip any passenger gave?
+--------------------+
| highest_tip_amount |
+--------------------+
| 428.0              |
+--------------------+

Time: 9.141290 seconds. 1 rows.
```

**Note:** Local models are slower but provide:

- Complete privacy (no data sent to external APIs)
- No API costs
- Full control over model selection and parameters

**4. (Optional) Inspect the local model's work:**

You can trace the local model's execution similarly:

```sql
spice sql
```

Then run:

```sql
SELECT
  start_time,
  parent_span_id,
  span_id,
  task,
  substr(input, 0, 64) as input,
  execution_duration_ms
FROM runtime.task_history
WHERE trace_id = (
  SELECT trace_id
  FROM runtime.task_history
  WHERE task = 'nsql'
  ORDER BY start_time DESC
  LIMIT 1
)
ORDER BY start_time ASC;
```

## Next Steps

Now that you understand text-to-SQL with Spice, explore:

- **[Other cookbook recipes](https://github.com/spiceai/cookbook)** - More Spice.ai examples
- **[Spice documentation](https://docs.spiceai.org)** - Comprehensive guides
- **[Connect your own data](https://docs.spiceai.org/components/data-connectors)** - Use Spice with your databases
- **[Custom AI models](https://docs.spiceai.org/components/models)** - Configure different LLMs

## Troubleshooting

**"Model not found" errors:**

- Ensure your `.env` file has valid API keys
- Check that `spice run` shows models loading successfully

**Slow queries:**

- Try disabling data sampling with `"sample_data_enabled": false`
- Specify tables explicitly with the `"tables"` parameter
- Use a more powerful model (e.g., GPT-4 instead of GPT-3.5)

**Inaccurate SQL generation:**

- Enable data sampling (it's on by default)
- Make your natural language queries more specific
- Inspect the generated SQL and refine your question

**Connection errors:**

- Verify Spice is running (`spice run` in another terminal)
- Check that port 8090 is not in use by another application
- Ensure you're in the correct directory (`cookbook/text-to-sql`)
