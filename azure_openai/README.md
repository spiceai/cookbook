# Azure OpenAI Models Recipe

This recipe demonstrates how to use Azure OpenAI models for vector-based search and chat functionalities with structured (taxi trips) and unstructured (GitHub files) data.

## Prerequisites

- Ensure you have the Spice CLI installed. Follow the [Getting Started](https://docs.spiceai.org/getting-started) guide if you haven't done so yet.

## Deploy Test Models

Navigate to the [Azure OpenAI Model Deployment](https://ai.azure.com/resource/deployments) page and deploy the following base models:

- `text-embedding-3-small`: Model for embeddings creation for vector similarity search.
- `gpt-4o-mini`: LLM chat model.

Note: Other models can be used if available. Update `spicepod.yaml` to match the model name.

## Populate `.env` and Configure Spicepod

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
      spice_tools: auto
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
  "matches": [
    {
      "value": "# Metrics Naming\n\n## TL;DR\n\n**Metric Naming Guide**: Prioritize Developer Experience (DX) with intuitive, readable names that ...",
      "score": 0.7572349075959143,
      "dataset": "spiceai.files",
      "metadata": {
        "download_url": "https://raw.githubusercontent.com/spiceai/spiceai/trunk/docs/dev/metrics.md"
      }
    },
    {
      "value": "# Criteria Definitions\n\n## RC\n\nAcronym for \"Release Candidate\". Identifies a version that is eligible for general/stable release ....",
      "score": 0.6719117129814338,
      "dataset": "spiceai.files",
      "metadata": {
        "download_url": "https://raw.githubusercontent.com/spiceai/spiceai/trunk/docs/criteria/definitions.md"
      }
    }
  ],
  "duration_ms": 535
}
```

Vector-based search could also be performed using `spice search` CLI command:

```shell
spice search
```

Result:

```shell
search> OTEL metrics naming

Rank 1, Score: 75.7, Datasets [spice.spiceai.files]
# Metrics Naming

## TL;DR

**Metric Naming Guide**: Prioritize Developer Experience (DX) with intuitive, readable names that follow consistent conventions. Start with a domain prefix, use snake_case, avoid plurals in names (except counters), include units where relevant, and use labels for variations. Align with Prometheus and OpenTelemetry standards, and adhere to UCUM for units.

## Definitions

- Metric: is a measurement used to track the state and behavior of a system component. Metrics represent the current status (e.g., readiness or availability) or describe specific operations (e.g., request counts, cache hits, latencies, failures) to provide insight into system health, performance, and workload.
...
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
