# Filesystem Hosted Model

This recipe demonstrates how to use models hosted on filesystems.

## Prerequisites

- Ensure you have the Spice CLI installed. Follow the [Getting Started](https://docs.spiceai.org/getting-started) guide if you haven't done so yet.

Clone this cookbook repo locally:

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/models/filesystem
```

## Download model to the filesystem

The [Phi-3-mini-4k-instruct model](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct) size is `7.66 GB`, the **download might take several minutes**.

```shell
mkdir -p phi-3-mini && BASE_URL="https://huggingface.co/microsoft/Phi-3-mini-4k-instruct/resolve/main" \
&& wget -q --show-progress -P phi-3-mini \
  "$BASE_URL/config.json" \
  "$BASE_URL/generation_config.json" \
  "$BASE_URL/model-00001-of-00002.safetensors" \
  "$BASE_URL/model-00002-of-00002.safetensors" \
  "$BASE_URL/tokenizer.json" \
  "$BASE_URL/tokenizer.model" \
  "$BASE_URL/tokenizer_config.json"
```

```shell
config.json                      100%[=========================================================>]     967  --.-KB/s    in 0s      
generation_config.json           100%[=========================================================>]     181  --.-KB/s    in 0s      
model-00001-of-00002.safetensors 100%[=========================================================>]   4.63G  40.0MB/s    in 1m 58s  
model-00002-of-00002.safetensors 100%[=========================================================>]   2.49G  40.7MB/s    in 63s     
tokenizer.json                   100%[=========================================================>]   1.85M  9.40MB/s    in 0.2s    
tokenizer.model                  100%[=========================================================>] 488.01K  --.-KB/s    in 0.07s   
tokenizer_config.json            100%[=========================================================>]   3.36K  --.-KB/s    in 0s  
```

## Run Spice

Spice is configured to load the model from the `phi-3-mini` folder (downloaded in the previous step).

```yaml
models:
  - from: file:phi-3-mini
    name: local_model
    params:
      model_type: phi3
```

Run Spice

```shell
spice run
```

```shell
2025/01/30 23:53:11 INFO Checking for latest Spice runtime release...
2025/01/30 23:53:11 INFO Spice.ai runtime starting...
2025-01-31T07:53:12.600614Z  INFO runtime::init::dataset: No datasets were configured. If this is unexpected, check the Spicepod configuration.
2025-01-31T07:53:12.600965Z  INFO runtime::init::results_cache: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
2025-01-31T07:53:12.601384Z  INFO runtime::init::model: Loading model [local_model] from file:phi-3-mini...
2025-01-31T07:53:12.601668Z  INFO runtime::metrics_server: Spice Runtime Metrics listening on 127.0.0.1:9090
2025-01-31T07:53:12.601718Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2025-01-31T07:53:12.604584Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2025-01-31T07:53:12.610797Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2025-01-31T07:53:20.388313Z  INFO runtime::init::model: Model [local_model] deployed, ready for inferencing
```

## Chat with the model

Use the `spice chat` CLI command to interact with the model.

```shell
Using model: local_model
chat> If Alice is older than Bob, and Bob is older than Charlie, who is the youngest? Explain your answer
Based on the given information, Charlie is the youngest among Alice, Bob, and himself. Here's the explanation:

1. We know that Alice is older than Bob. This means the age order between Alice and Bob is Alice > Bob.
2. We also know that Bob is older than Charlie. Similarly, the age order between Bob and Charlie is Bob > Charlie.
3. When we combine these two age relationships, we get Alice > Bob > Charlie.
4. From this combined relationship, it's evident that Charlie is the youngest person since there are no other comparisons made placing him at an equal or greater age level than Alice and Bob.

Therefore, Charlie is the youngest.

Time: 6.91s (first token 0.31s). Tokens: 178. Prompt: 27. Completion: 151 (22.89/s).
```

## Further Reading

[Filesytem Hosted Models Documentation](https://spiceai.org/docs/components/models/filesystem)
