# OpenAI Models

This recipe demonstrates how to use OpenAI models in Spice.ai.

## Prerequisites

- Ensure you have the Spice CLI installed. Follow the [Getting Started](https://docs.spiceai.org/getting-started) guide if you haven't done so yet.

## Populate `.env` and Configure Spicepod

Populate `.env` with the following:

- `GITHUB_TOKEN`: A [personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-personal-access-token-classic).
- `OPENAI_API_KEY`: A valid OpenAI API key.

Verify that the `spicepod.yaml` is configured as follows:

```yaml
datasets:
  - from: github:github.com/spiceai/spiceai/files/trunk
    name: spiceai.docs
    description: Spice.ai project documentation (github.com/spiceai/spiceai)
    params:
      github_token: ${secrets:GITHUB_TOKEN}
      include: 'docs/**/*.md'
    acceleration:
      enabled: true
    columns:
      - name: content
        embeddings:
          - from: embeddings-model
            row_id:
              - path
            chunking:
              enabled: false
              target_chunk_size: 256
              overlap_size: 64
              file_format: md

embeddings:
  - from: openai:text-embedding-3-small
    name: embeddings-model

models:
  - from: openai:gpt-4o
    name: chat-model
    params:
      tools: auto
      system_prompt: |
        You are a helpful Spice.ai Docs assistant.
```

## Run Spice

```shell
spice run
```

Result:

```shell
2025/01/21 01:19:43 INFO Checking for latest Spice runtime release...
2025/01/21 01:19:44 INFO Spice.ai runtime starting...
2025-01-20T16:19:45.056778Z  INFO runtime::metrics_server: Spice Runtime Metrics listening on 127.0.0.1:9090
2025-01-20T16:19:45.057495Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2025-01-20T16:19:45.057562Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2025-01-20T16:19:45.061178Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2025-01-20T16:19:45.544466Z  INFO runtime::init::embedding: Embedding [embeddings-model] ready to embed
2025-01-20T16:19:45.544649Z  INFO runtime::init::dataset: Initializing dataset spiceai.docs
2025-01-20T16:19:45.544669Z  INFO runtime::init::results_cache: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
2025-01-20T16:19:45.544761Z  INFO runtime::init::model: Loading model [chat-model] from openai:gpt-4o...
2025-01-20T16:19:46.164600Z  INFO runtime::init::dataset: Dataset spiceai.docs registered (github:github.com/spiceai/spiceai/files/trunk), acceleration (arrow), results cache enabled.
2025-01-20T16:19:46.165929Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset spiceai.docs
2025-01-20T16:19:46.534044Z  INFO runtime::init::model: Model [chat-model] deployed, ready for inferencing
2025-01-20T16:19:49.394003Z  INFO runtime::accelerated_table::refresh_task: Loaded 93 rows (1.28 MiB) for dataset spiceai.docs in 3s 228ms.
```

## SQL Search

1. Execute a Basic SQL Query to perform keyword searches within the dataset:

```shell
spice sql
```

Then:

```sql
SELECT path
FROM spiceai.docs
WHERE
    LOWER(content) LIKE '%errors%'
    AND NOT contains(path, 'docs/release_notes');
```

Result:

```shell
+------------------------------+
| path                         |
+------------------------------+
| docs/criteria/definitions.md |
| docs/dev/error_handling.md   |
| docs/dev/metrics.md          |
| docs/dev/style_guide.md      |
+------------------------------+

Time: 0.006798 seconds. 4 rows.
```

## Utilizing Vector-Based Search

```shell
  curl -XPOST http://localhost:8090/v1/search \
    -H "Content-Type: application/json" \
    -d "{
      \"datasets\": [\"spiceai.docs\"],
      \"text\": \"TEL metrics naming\",
      \"where\": \"not contains(path, 'docs/release_notes')\",
      \"additional_columns\": [\"download_url\"],
      \"limit\": 2
    }"
```

Result

```json
{
  "matches": [
    {
      "value": "# Metrics Naming\n\n## TL;DR\n\n**Metric Naming Guide**: Prioritize Developer Experience (DX) with intuitive, ...",
      "score": 0.7941223368131454,
      "dataset": "spiceai.docs",
      "metadata": {
        "download_url": "https://raw.githubusercontent.com/spiceai/spiceai/trunk/docs/dev/metrics.md"
      }
    },
    {
      "value": "# Criteria Definitions\n\n## RC\n\nAcronym for \"Release Candidate\". Identifies a version that is eligible for ...",
      "score": 0.7145749783070606,
      "dataset": "spiceai.docs",
      "metadata": {
        "download_url": "https://raw.githubusercontent.com/spiceai/spiceai/trunk/docs/criteria/definitions.md"
      }
    }
  ],
  "duration_ms": 745
}
```

## Utilizing a natural language query

Use `spice chat` CLI command to query information using natural language

```shell
spice chat
Using model: chat-model
```

Perform test queries:

```shell
chat> what datasets you have access to
I have access to the following dataset:

- **Dataset Name:** spice.spiceai.docs
  - **Description:** Spice.ai project documentation (github.com/spiceai/spiceai)
  - **Can Search Documents:** Yes

This dataset contains documentation related to the Spice.ai project.
```

```shell
chat> how many records in taxi trips dataset
There are a total of 2,964,624 records in the taxi trips dataset.
```

```shell
chat> what is the longest taxi trip distance recorded
The longest taxi trip distance recorded is approximately 312,722.3 meters.
```

```shell
chat> What are release criterias?
The release criteria for Spice.ai components, such as models, data accelerators, and catalog connectors, are divided into stages, including Release Candidate (RC) and Stable release criteria. Here are the details for RC Criteria:

### RC Release Criteria
- **Beta Criteria**: All beta release criteria must pass.
- **Performance and Latency**: The model or component must handle consistent requests from several clients without adverse impacts on latency.
  - Example: 8 clients sending consistent requests for 60 minutes.
  ...
```
