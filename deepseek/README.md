# DeepSeek Model

This recipe demonstrates how to use DeepSeek model in Spice.ai.

## Prerequisites

- Ensure you have the Spice CLI installed. Follow the [Getting Started](https://docs.spiceai.org/getting-started) guide if you haven't done so yet.

## Populate `.env` and Configure Spicepod

Clone this cookbook repo locally:

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/deepseek
```

Populate `.env` with the following:

- `DEEPSEEK_API_KEY`: A valid DeepSeek API key.

Verify that the `spicepod.yaml` is configured as follows:

```yaml
datasets:
  - from: s3://spiceai-demo-datasets/taxi_trips/2024/
    name: taxi_trips
    description: taxi trips in s3
    params:
      file_format: parquet
    acceleration:
      enabled: true

models:
  - from: openai:deepseek-chat
    name: deepseek
    params:
      tools: auto
      endpoint: https://api.deepseek.com
      openai_api_key: ${secrets:DEEPSEEK_API_KEY}
```

## Run Spice

```shell
spice run
```

Result:

```shell
2025/01/21 14:48:39 INFO Checking for latest Spice runtime release...
2025/01/21 14:48:40 INFO Spice.ai runtime starting...
2025-01-21T22:48:40.569250Z  INFO runtime::init::dataset: Initializing dataset taxi_trips
2025-01-21T22:48:40.569580Z  INFO runtime::init::model: Loading model [deepseek] from openai:deepseek-chat...
2025-01-21T22:48:40.569646Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2025-01-21T22:48:40.569701Z  INFO runtime::metrics_server: Spice Runtime Metrics listening on 127.0.0.1:9090
2025-01-21T22:48:40.570139Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2025-01-21T22:48:40.572365Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2025-01-21T22:48:40.769265Z  INFO runtime::init::results_cache: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
2025-01-21T22:48:41.380306Z  INFO runtime::init::dataset: Dataset taxi_trips registered (s3://spiceai-demo-datasets/taxi_trips/2024/), acceleration (arrow), results cache enabled.
2025-01-21T22:48:41.381620Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset taxi_trips
2025-01-21T22:48:44.001483Z  INFO runtime::init::model: Model [deepseek] deployed, ready for inferencing
```

## Utilizing a natural language query

Use `spice chat` CLI command to query information using natural language

```shell
>> spice chat
Using model: deepseek
```

Perform test queries:

```shell
chat> what datasets you have access to
Currently, I have access to the following dataset:

- **Dataset Name**: `spice.public.taxi_trips`
- **Description**: taxi trips in s3
- **Can Search Documents**: No

This dataset contains information about taxi trips stored in S3. If you need more details or want to perform specific queries on this dataset, feel free to ask!

Time: 5.58s (first token 1.09s). Tokens: 1532. Prompt: 1517. Completion: 15 (3.34/s).
```

```shell
chat> how many records in taxi trips dataset
The `taxi_trips` dataset contains **2,964,624** records.

Time: 9.13s (first token 0.93s). Tokens: 1545. Prompt: 1518. Completion: 27 (3.29/s).
```

```shell
The longest taxi trip distance recorded in the dataset is **312,722.3 miles**.

Time: 5.44s (first token 0.90s). Tokens: 1584. Prompt: 1548. Completion: 36 (7.93/s).
```
