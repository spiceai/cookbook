# Running Qwen3.5 Locally

Works with `v2.4+` builds that include the [llama.cpp GGUF engine](https://github.com/spiceai/spiceai/pull/7864), merged to trunk on 2026-10-24. `v2.4.0-rc.3` and earlier releases refuse this model's `qwen35` GGUF architecture; see [Prerequisites](#prerequisites).

[Qwen3.5](https://huggingface.co/collections/Qwen/qwen35) is Alibaba's February 2026 family of hybrid-thinking, multimodal open-weight models under the Apache 2.0 license. This recipe serves **Qwen3.5-9B** on an Apple silicon Mac with Spice's built-in llama.cpp engine and Metal, grounds it in a public dataset through Spice's SQL tools, and shows how to turn its reasoning on and off per request. An [abliterated variant](#abliterated-variant) of the same model is in [`abliterated/`](./abliterated/).

The 9B model is the member of the family that runs on every MacBook Pro, including 16 GB configurations. The table in [Memory](#memory) names the files for larger Macs, up to Qwen3.5-35B-A3B on a 36 GB MacBook Pro.

| Model             | Parameters        | Fits a 36 GB MacBook Pro | GGUF repository                                                                 |
| ----------------- | ----------------- | ------------------------ | ------------------------------------------------------------------------------- |
| Qwen3.5-9B        | 9B dense          | Yes, from 16 GB          | [unsloth/Qwen3.5-9B-GGUF](https://huggingface.co/unsloth/Qwen3.5-9B-GGUF)       |
| Qwen3.5-27B       | 27B dense         | Yes, from 32 GB          | [unsloth/Qwen3.5-27B-GGUF](https://huggingface.co/unsloth/Qwen3.5-27B-GGUF)     |
| Qwen3.5-35B-A3B   | 36B MoE, 3B active | Yes, from 36 GB         | [unsloth/Qwen3.5-35B-A3B-GGUF](https://huggingface.co/unsloth/Qwen3.5-35B-A3B-GGUF) |
| Qwen3.5-122B-A10B | 122B MoE, 10B active | No: 77 GB at 4-bit; a 128 GB Mac | [unsloth/Qwen3.5-122B-A10B-GGUF](https://huggingface.co/unsloth/Qwen3.5-122B-A10B-GGUF) |
| Qwen3.5-397B-A17B | 397B MoE, 17B active | No: a 256 GB Mac Studio and up | unsloth/Qwen3.5-397B-A17B-GGUF                                             |

The 0.8B, 2B and 4B models also fit, with the same spicepod shape and Unsloth repositories.

## Prerequisites

- An Apple silicon Mac with 16 GB or more unified memory. Spice's llama.cpp engine runs the model on the GPU through Metal.
- The [Spice CLI](https://spiceai.org/docs/installation). `spice version` must report a runtime with the `+models.metal` suffix and the llama.cpp GGUF engine. Spice installs the Metal build on Apple silicon by default. The engine merged to trunk on 2026-10-24, after `v2.4.0-rc.3`; run `spice upgrade` once a release that includes it ships, or use a trunk build in the meantime (see [Using a trunk build](#using-a-trunk-build)).
- 7 GB of free disk for the model, which Spice downloads into the Hugging Face cache at `~/.cache/huggingface/hub`.
- Network access to `huggingface.co` and to the public S3 bucket `spiceai-demo-datasets`. No Hugging Face account is needed.

## Memory

Spice loads the whole GGUF into GPU memory. macOS gives the GPU most of unified memory but not all of it: Metal reports the budget as `recommendedMaxWorkingSetSize` (107 GiB of 128 GiB on an M3 Max). Leave room for the KV cache (a few hundred MB at the engine's default 8,192-token context) and for macOS itself. Pick the file for the Mac:

| Unified memory | File (`files[0].path`)                                               | Size    | Repository                   |
| -------------- | -------------------------------------------------------------------- | ------- | ---------------------------- |
| 16 GB and up   | `Qwen3.5-9B-UD-Q4_K_XL.gguf` (the default in `spicepod.yaml`)        | 6.0 GB  | unsloth/Qwen3.5-9B-GGUF      |
| 16 GB and up   | `Qwen3.5-9B-UD-Q6_K_XL.gguf`                                         | 8.8 GB  | unsloth/Qwen3.5-9B-GGUF      |
| 24 GB and up   | `Qwen3.5-9B-Q8_0.gguf` (near-lossless)                               | 9.5 GB  | unsloth/Qwen3.5-9B-GGUF      |
| 32 GB and up   | `Qwen3.5-27B-UD-Q4_K_XL.gguf`                                        | 17.6 GB | unsloth/Qwen3.5-27B-GGUF     |
| 36 GB and up   | `Qwen3.5-35B-A3B-UD-Q4_K_XL.gguf` (3B active: several times faster)  | 22.2 GB | unsloth/Qwen3.5-35B-A3B-GGUF |
| 48 GB and up   | `Qwen3.5-35B-A3B-UD-Q6_K_XL.gguf`                                    | 32.1 GB | unsloth/Qwen3.5-35B-A3B-GGUF |
| 64 GB and up   | `Qwen3.5-122B-A10B-UD-IQ3_XXS.gguf` (122B MoE, 10B active)           | 44.7 GB | unsloth/Qwen3.5-122B-A10B-GGUF |
| 96 GB and up   | `UD-Q3_K_XL/Qwen3.5-122B-A10B-UD-Q3_K_XL-00001-of-00003.gguf` and its two sibling shards | 57.0 GB | unsloth/Qwen3.5-122B-A10B-GGUF |
| 128 GB         | `UD-Q4_K_XL/Qwen3.5-122B-A10B-UD-Q4_K_XL-00001-of-00003.gguf` and its two sibling shards | 77.0 GB | unsloth/Qwen3.5-122B-A10B-GGUF |

To switch, change `from` to the repository and `files` to the file, listing every shard of a split file. The `UD-` files are Unsloth's dynamic quantizations, which keep the layers that matter most at higher precision.

## Step 1. Review the Spicepod

`spicepod.yaml` in this directory defines one dataset and one model:

```yaml
version: v2
kind: Spicepod
name: qwen3.5

datasets:
  - from: s3://spiceai-demo-datasets/taxi_trips/2024/
    name: taxi_trips
    description: NYC yellow taxi trips, 2024
    params:
      file_format: parquet
      s3_auth: public
    acceleration:
      enabled: true

models:
  - from: huggingface:huggingface.co/unsloth/Qwen3.5-9B-GGUF
    name: qwen3.5
    files:
      - path: Qwen3.5-9B-UD-Q4_K_XL.gguf
    params:
      tools: auto
```

- `from` names the Hugging Face repository and `files` the GGUF in it. Spice downloads every `.gguf` listed, so a model split into shards lists each shard. A repository revision can be pinned with `from: huggingface:huggingface.co/unsloth/Qwen3.5-9B-GGUF:<commit>`.
- `tools: auto` gives the model Spice's built-in tools, including `list_datasets`, `table_schema` and `sql`, so it can answer questions about `taxi_trips` by writing and running SQL.
- The dataset is 2,964,624 rows of Parquet (400 MB) accelerated into Cayenne on first start.

## Step 2. Start Spice

```bash
cd models/qwen3.5
spice run
```

The first start downloads the model (6.0 GB) into the Hugging Face cache and reads the dataset (399 MB) from S3. Later starts load the model from the cache; the dataset is read from S3 again on every start, since the acceleration is in memory (about a second on a fast connection).

```console
 INFO Spice.ai runtime starting...
2026-10-26T02:30:27.427419Z  INFO spiced: Starting runtime v2.4.0-unstable+models.metal
...
2026-10-26T02:30:27.604524Z  INFO runtime::init::model: Loading model [qwen3.5] from huggingface:huggingface.co/unsloth/Qwen3.5-9B-GGUF...
2026-10-26T02:30:27.823909Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2026-10-26T02:30:27.829546Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2026-10-26T02:30:28.877965Z  INFO huggingface_hub::snapshot: Downloading 1 file (6.0 GB) for model 'qwen3.5' from Hugging Face repo 'unsloth/Qwen3.5-9B-GGUF' at commit 3885219 (revision 'main').
2026-10-26T02:30:58.879869Z  INFO huggingface_hub::snapshot: Downloading model 'qwen3.5': 0.1 of 6.0 GB (1%) at 3.5 MB/s, about 28 min left.
...
2026-10-26T02:45:15.066497Z  INFO huggingface_hub::snapshot: Downloaded model 'qwen3.5' from Hugging Face repo 'unsloth/Qwen3.5-9B-GGUF' in 14 min 46 s.
2026-10-26T02:45:19.045839Z  INFO runtime::init::model: Model [qwen3.5] deployed, ready for inferencing
2026-10-26T02:47:20.273463Z  INFO runtime::init::dataset: Dataset taxi_trips registered (s3://spiceai-demo-datasets/taxi_trips/2024/), acceleration (cayenne), results cache enabled. duration_ms=345
2026-10-26T02:47:20.274611Z  INFO runtime_table::accelerated::refresh_task: Loading data for dataset taxi_trips
2026-10-26T02:47:37.399751Z  INFO runtime_table::accelerated::refresh_task: Loaded 2,964,624 rows (398.60 MiB) for dataset taxi_trips in 17s 125ms.
2026-10-26T02:47:37.400000Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

The elided lines report settings the runtime derives for this host, and their values differ from machine to machine. The download rate is the network's: this run was on a slow link.

## Step 3. Chat with the model

In a second terminal, from the same directory:

```bash
spice chat
```

```console
Using model: qwen3.5
chat> How many rows are in the taxi_trips dataset?
There are 2,964,624 rows in the `taxi_trips` dataset.

chat> What was the largest tip_amount in taxi_trips, and on what date?
The largest tip amount in the `taxi_trips` dataset was **$428.00**.

This trip occurred on **January 29, 2024** (specifically at 13:30:58).
```

Behind each answer the model called `list_datasets`, then `table_schema`, then `sql`. The runtime records every call in `runtime.task_history`; `spice sql` shows them:

```sql
SELECT task, left(input, 80) AS input, round(execution_duration_ms) AS ms
FROM runtime.task_history
WHERE task LIKE 'tool_use::%'
ORDER BY start_time DESC
LIMIT 5;
```

A model this size sometimes writes a SQL function Spice's engine does not have, such as `DATE()`. The tool returns the planner's error, and the model rewrites the query; the answer takes a few seconds longer.

## Step 4. Use the OpenAI-compatible API

Spice serves the model at `http://localhost:8090/v1/chat/completions`, so OpenAI SDKs and clients work unchanged with the model name `qwen3.5`.

```bash
curl -s http://localhost:8090/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3.5",
    "messages": [{"role": "user", "content": "Reply with only the integer 1729."}]
  }'
```

```json
{"id":"qwen3.5-792fnpdMVt-4","choices":[{"index":0,"message":{"content":"1729","role":"assistant"},"finish_reason":"stop"}],"model":"qwen3.5","object":"chat.completion","usage":{"prompt_tokens":23,"completion_tokens":4,"total_tokens":27}}
```

### Reasoning

Qwen3.5's small models (0.8B to 9B) answer directly unless asked to think; the 27B and 35B-A3B models think by default. The `reasoning_effort` field controls it per request: `none` turns thinking off, and `low`, `medium` or `high` turn it on. The thinking trace comes back in `reasoning_content`, separate from `content`.

```bash
curl -s http://localhost:8090/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3.5",
    "reasoning_effort": "high",
    "messages": [{"role": "user", "content": "Reply with only the integer 1729."}]
  }'
```

```json
{"choices":[{"message":{"content":"\n\n1729","reasoning_content":"Thinking Process:\n\n1.  **Analyze the Request:**\n    *   Input: \"Reply with only the integer 1729.\"\n ...","role":"assistant"},"finish_reason":"stop"}],"usage":{"prompt_tokens":21,"completion_tokens":204,"total_tokens":225}}
```

To set a default for every request, add `hf_reasoning_effort: <level>` to the model's `params`. Qwen3.5's chat template has one thinking switch, so `low`, `medium` and `high` all mean "think" for this model.

### Speed and context

On an M3 Max, Qwen3.5-9B at 4-bit decodes about 43 tokens per second with a 1,600-token prompt. The engine uses an 8,192-token context; the dataset tools fit comfortably, and a longer conversation is cut off with an error that says so.

## Abliterated variant

[`abliterated/`](./abliterated/) is the same recipe with [huihui-ai/Huihui-Qwen3.5-9B-abliterated](https://huggingface.co/huihui-ai/Huihui-Qwen3.5-9B-abliterated), a version of Qwen3.5-9B with its refusal behavior removed by abliteration, in the GGUF quantization by [mradermacher](https://huggingface.co/mradermacher/Huihui-Qwen3.5-9B-abliterated-GGUF). It serves the model without the dataset tools, because its stock Qwen chat template trips a runtime bug when `tools: auto` is set ([spiceai/spiceai#15578](https://github.com/spiceai/spiceai/issues/15578)). Read its README before using it: an abliterated model has none of the base model's safety training.

## Troubleshooting

| Symptom                                                                                              | Cause and fix                                                                                                                                                            |
| ---------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `Architecture 'qwen35' in <file> is not supported by this Spice release`                             | The runtime predates the llama.cpp GGUF engine. Upgrade Spice, or run a trunk build (see below).                                                                         |
| `Unknown GGUF architecture 'qwen35'`                                                                  | A `v2.3.x` or `v2.4.0-rc` runtime, which serves GGUFs with mistral.rs. Same fix.                                                                                         |
| The model never finishes loading, or macOS becomes unresponsive                                      | The file does not fit the GPU's share of memory. Choose a smaller file from the [Memory](#memory) table.                                                                 |
| `the prompt is N tokens, and the model's context holds 8192`                                         | The conversation outgrew the context. Start a new chat.                                                                                                                  |
| `spice chat "<question>"` prints nothing for a question that needs the dataset tools | [spiceai/spiceai#15579](https://github.com/spiceai/spiceai/issues/15579): the one-shot form stalls on tool calls. Use the interactive REPL (`spice chat`, then type the question), pipe the question on standard input (`echo "<question>" | spice chat`), or call the API. |
| Slow first start                                                                                     | The 6.0 GB download runs at the network's speed; the log reports progress every 30 seconds. Later starts read the cache.                                                 |

## Using a trunk build

Until a release includes the llama.cpp GGUF engine, download the latest trunk build of the runtime and point the CLI at it. The CLI's `spice run`, `spice chat` and `spice sql` work unchanged.

```bash
RUN_ID=$(gh run list -R spiceai/spiceai --workflow build_and_release --branch trunk --status success --limit 1 --json databaseId -q '.[0].databaseId')
gh run download "$RUN_ID" -R spiceai/spiceai -n spiced_metal_darwin_aarch64 -D spiced-trunk
tar -xzf spiced-trunk/spiced_metal_darwin_aarch64.tar.gz -C spiced-trunk && chmod +x spiced-trunk/spiced
SPICED_PATH="$PWD/spiced-trunk/spiced" spice run
```

## Clean up

Stop Spice with `Ctrl+C`. The model stays in the Hugging Face cache for the next start; remove it with:

```bash
rm -rf ~/.cache/huggingface/hub/models--unsloth--Qwen3.5-9B-GGUF
```

## Learn more

- [Local GGUF models in Spice](https://spiceai.org/docs/components/models#local-gguf-models): engine placement, draft heads, structured output, supported architectures.
- [Hugging Face models](https://spiceai.org/docs/components/models/huggingface) and [reasoning effort for local models](https://spiceai.org/docs/components/models#reasoning-effort-for-local-models).
- [LLM tools](https://spiceai.org/docs/features/large-language-models/tools): the built-in tools behind `tools: auto`.
- [Unsloth's Qwen3.5 guide](https://unsloth.ai/docs/models/qwen3.5): quantization sizes and recommended sampling settings.
