# Azure OpenAI Models

This recipe demonstrates how to use Azure OpenAI models for vector-based search and chat functionalities with structured (taxi trips) and unstructured GitHub data.

## Prerequisites

- Ensure you have the Spice CLI installed. Follow the [Getting Started](https://docs.spiceai.org/getting-started) guide if you haven't done so yet.

## Deploy Test Models

Navigate to the [Azure OpenAI Model Deployment](https://ai.azure.com/resource/deployments) page and deploy the following base models:

- `text-embedding-3-small`: Model for embeddings creation for vector similarity search.
- `gpt-4o-mini`: LLM chat model.

Note: Other models can be used if available. Update `spicepod.yaml` to match the model name.

## Clone cookbook repo, populate `.env` and Configure Spicepod

Clone this cookbook repo locally:

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/azure_openai/
```

Populate `.env` with the following:

- `GITHUB_TOKEN`: A [personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-personal-access-token-classic).
- `SPICE_AZURE_API_KEY`: An Azure OpenAI API key from the Models Deployment page.
- `SPICE_AZURE_AI_ENDPOINT`: The Azure OpenAI resource endpoint used for models, for example, `https://resource-name.openai.azure.com`. This can be found on the Models Deployment page.

Verify that the `spicepod.yaml` configuration (`azure_deployment_name`, `azure_api_version`, etc.) matches the information on the [Azure OpenAI Model Deployment](https://ai.azure.com/resource/deployments) page.

```yaml
embeddings:
  - name: embeddings-model
    from: azure:text-embedding-3-small
    params:
      endpoint: ${ secrets:SPICE_AZURE_AI_ENDPOINT }
      azure_deployment_name: text-embedding-3-small
      azure_api_version: 2023-05-15
      azure_api_key: ${ secrets:SPICE_AZURE_API_KEY }

models:
  - from: azure:gpt-4o-mini
    name: chat-model
    params:
      tools: auto
      endpoint: ${ secrets:SPICE_AZURE_AI_ENDPOINT }
      azure_api_version: 2024-08-01-preview
      azure_deployment_name: gpt-4o-mini
      azure_api_key: ${ secrets:SPICE_AZURE_API_KEY }
```

## Run Spice

```shell
spice run
```

Result:

```shell
2024/12/12 14:10:00 INFO Checking for latest Spice runtime release...
2024/12/12 14:10:00 INFO Spice.ai runtime starting...
2024-12-12T22:10:00.770177Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2024-12-12T22:10:00.770235Z  INFO runtime::metrics_server: Spice Runtime Metrics listening on 127.0.0.1:9090
2024-12-12T22:10:00.770385Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2024-12-12T22:10:00.771411Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2024-12-12T22:10:01.248755Z  INFO runtime::init::embedding: Embedding [embeddings-model] ready to embed
2024-12-12T22:10:01.248915Z  INFO runtime::init::dataset: Initializing dataset spiceai.files
2024-12-12T22:10:01.248921Z  INFO runtime::init::dataset: Initializing dataset taxi_trips
2024-12-12T22:10:01.248962Z  INFO runtime::init::model: Loading model [chat-model] from azure:gpt-4o-mini...
2024-12-12T22:10:01.448894Z  INFO runtime::init::results_cache: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
2024-12-12T22:10:01.640572Z  INFO runtime::init::dataset: Dataset spiceai.files registered (github:github.com/spiceai/spiceai/files/trunk), acceleration (arrow), results cache enabled.
2024-12-12T22:10:01.641876Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset spiceai.files
2024-12-12T22:10:01.920208Z  INFO runtime::init::model: Model [chat-model] deployed, ready for inferencing
2024-12-12T22:10:02.221149Z  INFO runtime::init::dataset: Dataset taxi_trips registered (s3://spiceai-demo-datasets/taxi_trips/2024/), acceleration (arrow), results cache enabled.
2024-12-12T22:10:02.222425Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset taxi_trips
2024-12-12T22:10:06.212606Z  INFO runtime::accelerated_table::refresh_task: Loaded 74 rows (1.06 MiB) for dataset spiceai.files in 4s 570ms.
2024-12-12T22:10:10.896203Z  INFO runtime::accelerated_table::refresh_task: Loaded 2,964,624 rows (419.31 MiB) for dataset taxi_trips in 8s 673ms.

```

## SQL Search

1. Execute a Basic SQL Query to perform keyword searches within the dataset:

```shell
spice sql
```

Then:

```sql
SELECT path
FROM spiceai.files
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

Time: 0.018795833 seconds. 4 rows.
```

## Utilizing Vector-Based Search

```shell
  curl -XPOST http://localhost:8090/v1/search \
    -H "Content-Type: application/json" \
    -d "{
      \"datasets\": [\"spiceai.files\"],
      \"text\": \"TEL metrics naming\",
      \"where\": \"not contains(path, 'docs/release_notes')\",
      \"additional_columns\": [\"download_url\"],
      \"limit\": 2
    }"
```

Result:

```json
{
  "results": [
    {
      "matches": {        "content": ".\n\n## Definitions\n\n- Metric: is a measurement used to track the state and behavior of a system component. Metrics represent the current status ..."
      },
      "data": {
        "download_url": "https://raw.githubusercontent.com/spiceai/spiceai/trunk/docs/dev/metrics.md"
      },
      "primary_key": {
        "path": "docs/dev/metrics.md"
      },
      "score": 0.7269563689871208,
      "dataset": "spiceai.files"
    },
    {
      "matches": {
        "content": "6\n\n## Core Connector Data Types\n\nCore Connector Data Types depend on the specific connector, but in general can be abstracted as (non-exhaustive) types like: ..."
      },
      "data": {
        "download_url": "https://raw.githubusercontent.com/spiceai/spiceai/trunk/docs/criteria/definitions.md"
      },
      "primary_key": {
        "path": "docs/criteria/definitions.md"
      },
      "score": 0.6737559856782607,
      "dataset": "spiceai.files"
    }
  ],
  "duration_ms": 1043
}
```

Vector-based search could also be performed using `spice search` CLI command:

```shell
spice search
```

Result:

```shell
search> OTEL metrics naming
+------+-------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+---------------------+
| Rank |                Key (path)                 |                                                                                                                                                                                                                                                                                                                   Match                                                                                                                                                                                                                                                                                                                   | Score  |     Dataset(s)      |
+------+-------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+---------------------+
| 1    | docs/dev/metrics.md                       | .                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | 0.7456 | spice.spiceai.files |
|      |                                           |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |        |                     |
|      |                                           | ## Definitions                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |        |                     |
| 2    | docs/release_notes/beta/v0.19.3-beta.md   | 5                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | 0.6989 | spice.spiceai.files |
|      |                                           | - Upgrade OTEL to v0.26 and make seconds based metrics reported precisely by @sgrebnov in https://github.com/spiceai/spiceai/pull/3203                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |        |                     |
|      |                                           | - use `text_embedding_inference::Infer` for more complete embedding solution by @Jeadie in https://github.com/spiceai/spiceai/pull/3199                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |        |                     |
| 3    | docs/release_notes/rc/v1.0.0-rc.1.md      |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | 0.6730 | spice.spiceai.files |
|      |                                           | | **Before**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | **v1.0-rc.1**                                                           | |        |                     |
|      |                                           | | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- | |        |                     |
| 4    | docs/release_notes/v1.8.1.md              | .                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | 0.6684 | spice.spiceai.files |
|      |                                           |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |        |                     |
|      |                                           | - **Acceleration Snapshot Metrics**: The following metrics are now available for Acceleration Snapshots:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |        |                     |
| 5    | docs/release_notes/v1.1/v1.1.1.md         | # Spice v1.1.1 (Apr 7, 2025)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | 0.6561 | spice.spiceai.files |
|      |                                           |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |        |                     |
|      |                                           | Spice v1.1.1 introduces several key updates, including a new Component Metrics System, improved Delta Data Connector performance, improved MCP tool descriptions, and expanded runtime results caching options. This release also adds detailed MySQL connection pool metrics for better observability. Component Metrics are Prometheus-compatible and accessible via the metrics endpoint.                                                                                                                                                                                                                                              |        |                     |
| 6    | docs/criteria/accelerators/stable.md      |  end-to-end [Throughput Test](../definitions.md) is performed on the accelerator using the TPC-DS dataset at scale factor 1 in all [Access Modes](../definitions.md).                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | 0.6550 | spice.spiceai.files |
|      |                                           |   - [ ] End-to-end tests should perform [Throughput Tests](../definitions.md) at the required [parallel query count](../definitions.md)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |        |                     |
|      |                                           |   - [ ] [Throughput Metric](../definitions.md) is calculated and reported as a metric with a parallel query count of 1 to serve as a baseline metric.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |        |                     |
| 7    | docs/release_notes/v1.9.0.md              | ocation' as primary key for document tables by [@Jeadie](https://github.com/Jeadie) in [#7567](https://github.com/spiceai/spiceai/pull/7567)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | 0.6530 | spice.spiceai.files |
|      |                                           | - Extend query-related metrics by [@krinart](https://github.com/krinart) in [#7571](https://github.com/spiceai/spiceai/pull/7571)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |        |                     |
|      |                                           | - Enabling acceleration refresh metrics by using `runtime.metrics` config by [@krinart](https://github.com/krinart) in [#7583](https://github.com/spiceai/spiceai/pull/7583)                                                                                                                                                                                                                                                                                                                                                                                                                                                              |        |                     |
| 8    | docs/criteria/models/beta.md              | # Spice.ai OSS Models - Beta Release Criteria                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | 0.6495 | spice.spiceai.files |
|      |                                           |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |        |                     |
|      |                                           | This document defines the set of criteria that is required before a model is considered to be of Beta quality.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |        |                     |
| 9    | docs/release_notes/v1.7/v1.7.1.md         | .                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | 0.6488 | spice.spiceai.files |
|      |                                           |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |        |                     |
|      |                                           | Example usage:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |        |                     |
| 10   | docs/release_notes/alpha/v0.14.0-alpha.md | 2                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | 0.6488 | spice.spiceai.files |
|      |                                           | - Rename metrics column `labels` to `properties` and make it nullable by @ewgenius in https://github.com/spiceai/spiceai/pull/1686                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |        |                     |
|      |                                           | - Fix federation_optimizer_rule schema error for `tpch_q7`, `tpch_q8`, `tpch_q9`, `tpch_q14` by @sgrebnov in https://github.com/spiceai/spiceai/pull/1683                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |        |                     |
+------+-------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+---------------------+

Time: 650ms. 10 results.
```

## Vector Search on multiple columns
Notice on the `name: spiceai.issues` dataset, there are embeddings on both the `body` & `title`. When performing vector search on this table, it will search across both these columns, and return results based on combined relevance.

```shell
  curl -XPOST http://localhost:8090/v1/search \
    -H "Content-Type: application/json" \
    -d "{
      \"datasets\": [\"spiceai.issues\"],
      \"text\": \"AI\",
      \"where\": \"state='CLOSED'\",
      \"additional_columns\": [\"url\"],
      \"limit\": 3
    }"
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
I have access to the following datasets:

1. **Taxi Trips Dataset**
   - **Description**: Taxi trips in S3
   - **Can Search Documents**: No

2. **Spice.ai Project Documentation**
   - **Description**: Spice.ai project documentation (github.com/spiceai/spiceai)
   - **Can Search Documents**: Yes
```

```shell
chat> how many records in taxi trips dataset
There are a total of 2,964,624 records in the taxi trips dataset.
```

```shell
chat> what is the longest taxi trip distance recorded
The longest taxi trip distance recorded is approximately 312,722.3 meters.
```
