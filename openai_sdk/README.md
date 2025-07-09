# Spice with the OpenAI SDK

One of Spice's best features is to act in place of the OpenAI API. Even better, you don't even have to be running OpenAI behind Spice! You can run OpenAI, Anthropic or HuggingFace models over your data and use existing tools that are compatible with the OpenAI API.

## Prerequisites

1. Python >= 3.10
2. Python package manager (`pip` or `uv`)
3. Spice [installed](https://docs.spiceai.org/getting-started)
4. OpenAI API Key

## Starting Spice

The first step is to get the Spice instance up and running.

```bash
git clone https://github.com/spiceai/cookbook # Skip if already cloned
cd cookbook/openai_sdk
# Add your OpenAI API key to the .env.local file
echo "SPICE_OPENAI_API_KEY=your_openai_api_key" > .env.local
# Start Spice
spice run
```

Output:

```bash
2025/01/13 13:27:41 INFO Spice.ai runtime starting...
2025-01-13T21:27:41.702275Z  INFO runtime::init::dataset: Initializing dataset taxi_trips
2025-01-13T21:27:41.703569Z  INFO runtime::metrics_server: Spice Runtime Metrics listening on 127.0.0.1:9090
2025-01-13T21:27:41.704347Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2025-01-13T21:27:41.704514Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2025-01-13T21:27:41.703575Z  INFO runtime::init::model: Loading model [openai] from openai:gpt-4o...
2025-01-13T21:27:41.713543Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2025-01-13T21:27:41.902271Z  INFO runtime::init::results_cache: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
2025-01-13T21:27:42.242310Z  INFO runtime::init::model: Model [openai] deployed, ready for inferencing
2025-01-13T21:27:42.576976Z  INFO runtime::init::dataset: Dataset taxi_trips registered (s3://spiceai-demo-datasets/taxi_trips/2024/), acceleration (arrow, 10s refresh), results cache enabled.
2025-01-13T21:27:42.578442Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset taxi_trips
2025-01-13T21:27:53.260052Z  INFO runtime::accelerated_table::refresh_task: Loaded 2,964,624 rows (399.41 MiB) for dataset taxi_trips in 10s 681ms.
```

Spice will use your OpenAI API key to communicate with OpenAI on your client code's behalf.

## Client prerequisites

These steps only need to be done once. Use a Python `virtualenv` to keep projects isolated.

### Using pip

1. Create the virtual environment: `python -m venv .venv`
2. Activate the virtual environment: `source .venv/bin/activate`
3. Install the required packages: `pip install openai python-dotenv`

Run the client: `python spice_openai_sdk.py` and observe the model's response to the `What datasets do I have access to?` question:

```bash
You have access to the following dataset:

- **taxi_trips**: This dataset contains data about taxi trips in s3.
```

### Using uv

1. Use `uv venv` to create the virtual environment
2. Activate the virtual environment: `source .venv/bin/activate`
3. Ensure the packages are installed: `uv pip install openai python-dotenv`

Run the client: `uv run spice_openai_sdk.py` and observe the model's response to the `What datasets do I have access to?` question:

```bash
You have access to the following dataset:

- **taxi_trips**: This dataset contains data about taxi trips in s3.
```

## About the client

The client is fairly simple, but it demonstrates how to integrate existing tooling with Spice's AI Gateway.

First, construct the client:

```python
client = Client(api_key="anything", base_url="http://localhost:8090/v1")
```

Notice that we can use any string we want for the `api_key`, because it's Spice that's responsible for communicating with the OpenAI API, not our client code, meaning less secrets to have to store and manage for your client application.

```python
chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "What datasets do I have access to?",
        }
    ],
    model="openai",
)
```

Here we're using the chat completions API to ask a question. Notice that we're asking a question about our Datasets. This is a question that only Spice can answer, and that's exactly what it does:

```python
print(chat_completion.choices[0].message.content)
```

```shell
You have access to the following dataset:

- **Table Name:** taxi_trips
  - **Description:** Taxi trips data stored in S3.

This dataset is available in the SQL database.
```
