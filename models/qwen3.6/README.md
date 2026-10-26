# Running Qwen3.6 Locally

Works with `v2.4+` builds that include the [llama.cpp GGUF engine](https://github.com/spiceai/spiceai/pull/7864), merged to trunk on 2026-10-24. `v2.4.0-rc.3` and earlier releases refuse this model's `qwen35moe` GGUF architecture; see [Prerequisites](#prerequisites).

[Qwen3.6](https://huggingface.co/collections/Qwen/qwen36) is Alibaba's April 2026 family of hybrid-thinking, multimodal open-weight models under the Apache 2.0 license. This recipe serves **Qwen3.6-35B-A3B**, a 36B mixture-of-experts model that activates 3B parameters per token, on an Apple silicon Mac with Spice's built-in llama.cpp engine and Metal. Three billion active parameters make it several times faster than a dense model of the same memory footprint, which suits a laptop. The recipe grounds the model in a public dataset through Spice's SQL tools. An [abliterated variant](#abliterated-variant) is in [`abliterated/`](./abliterated/).

| Model           | Parameters           | Fits a 36 GB MacBook Pro | GGUF repository                                                                     |
| --------------- | -------------------- | ------------------------ | ----------------------------------------------------------------------------------- |
| Qwen3.6-35B-A3B | 36B MoE, 3B active   | Yes (this recipe)        | [unsloth/Qwen3.6-35B-A3B-GGUF](https://huggingface.co/unsloth/Qwen3.6-35B-A3B-GGUF) |
| Qwen3.6-27B     | 27B dense            | Yes, from 32 GB          | [unsloth/Qwen3.6-27B-GGUF](https://huggingface.co/unsloth/Qwen3.6-27B-GGUF)         |

## Prerequisites

- An Apple silicon Mac with 36 GB or more unified memory for the default file, or 24 GB with the 3-bit file (see [Memory](#memory)). Spice's llama.cpp engine runs the model on the GPU through Metal.
- The [Spice CLI](https://spiceai.org/docs/installation). `spice version` must report a runtime with the `+models.metal` suffix and the llama.cpp GGUF engine. The engine merged to trunk on 2026-10-24, after `v2.4.0-rc.3`; run `spice upgrade` once a release that includes it ships, or use a trunk build in the meantime (see [Using a trunk build](#using-a-trunk-build)).
- 23 GB of free disk for the model, which Spice downloads into the Hugging Face cache at `~/.cache/huggingface/hub`.
- Network access to `huggingface.co` and to the public S3 bucket `spiceai-demo-datasets`. No Hugging Face account is needed.

## Memory

Spice loads the whole GGUF into GPU memory. macOS gives the GPU most of unified memory but not all of it: Metal reports the budget as `recommendedMaxWorkingSetSize` (107 GiB of 128 GiB on an M3 Max). Leave room for the KV cache (under 1 GB at the engine's default 8,192-token context) and for macOS itself.

| Unified memory | File (`files[0].path`)                                        | Size    | Repository                   |
| -------------- | ------------------------------------------------------------- | ------- | ---------------------------- |
| 16 GB          | `Qwen3.6-35B-A3B-UD-IQ2_M.gguf`                               | 11.5 GB | unsloth/Qwen3.6-35B-A3B-GGUF |
| 24 GB to 32 GB | `Qwen3.6-35B-A3B-UD-Q3_K_XL.gguf`                             | 16.8 GB | unsloth/Qwen3.6-35B-A3B-GGUF |
| 36 GB and up   | `Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf` (the default in `spicepod.yaml`) | 22.4 GB | unsloth/Qwen3.6-35B-A3B-GGUF |
| 48 GB and up   | `Qwen3.6-35B-A3B-UD-Q6_K_XL.gguf`                             | 31.8 GB | unsloth/Qwen3.6-35B-A3B-GGUF |
| 64 GB and up   | `Qwen3.6-35B-A3B-Q8_0.gguf` (near-lossless)                   | 36.9 GB | unsloth/Qwen3.6-35B-A3B-GGUF |
| 32 GB and up   | `Qwen3.6-27B-UD-Q4_K_XL.gguf` (dense: slower, slightly more accurate) | 17.6 GB | unsloth/Qwen3.6-27B-GGUF |
| 96 GB and up   | `BF16/Qwen3.6-35B-A3B-BF16-00001-of-00002.gguf` and `-00002-of-00002.gguf` (full precision) | 69.4 GB | unsloth/Qwen3.6-35B-A3B-GGUF |
| 128 GB         | `BF16/Qwen3.6-27B-BF16-00001-of-00002.gguf` and `-00002-of-00002.gguf` (dense, full precision) | 53.8 GB | unsloth/Qwen3.6-27B-GGUF |

To switch, change `from` to the repository and `files` to the file, listing every shard of a split file. The `UD-` files are Unsloth's dynamic quantizations, which keep the layers that matter most at higher precision.

Unsloth also publishes [unsloth/Qwen3.6-35B-A3B-MTP-GGUF](https://huggingface.co/unsloth/Qwen3.6-35B-A3B-MTP-GGUF), the same quantizations with the model's multi-token-prediction (NextN) layer kept in the file. Spice drafts with such a layer automatically, which raises decode speed; budget about 1 GB more memory for it.

## Step 1. Review the Spicepod

`spicepod.yaml` in this directory defines one dataset and one model:

```yaml
version: v2
kind: Spicepod
name: qwen3.6

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
  - from: huggingface:huggingface.co/unsloth/Qwen3.6-35B-A3B-GGUF
    name: qwen3.6
    files:
      - path: Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf
    params:
      tools: auto
```

- `from` names the Hugging Face repository and `files` the GGUF in it. Spice downloads every `.gguf` listed. A repository revision can be pinned with `from: huggingface:huggingface.co/unsloth/Qwen3.6-35B-A3B-GGUF:<commit>`.
- `tools: auto` gives the model Spice's built-in tools, including `list_datasets`, `table_schema` and `sql`, so it can answer questions about `taxi_trips` by writing and running SQL.
- The dataset is 2,964,624 rows of Parquet (400 MB) accelerated into Cayenne on first start.

## Step 2. Start Spice

```bash
cd models/qwen3.6
spice run
```

The first start downloads the model (22.4 GB) and the dataset. Later starts load both from cache in a few seconds.

```console
 INFO Spice.ai runtime starting...
2026-10-26T06:37:28.988962Z  INFO spiced: Starting runtime v2.4.0-unstable+models.metal
...
2026-10-26T06:37:28.995887Z  INFO runtime::init::model: Loading model [qwen3.6] from huggingface:huggingface.co/unsloth/Qwen3.6-35B-A3B-GGUF...
2026-10-26T06:37:29.276811Z  INFO huggingface_hub::snapshot: Downloading 1 file (22.4 GB) for model 'qwen3.6' from Hugging Face repo 'unsloth/Qwen3.6-35B-A3B-GGUF' at commit a483e9e (revision 'main').
2026-10-26T06:37:30.988128Z  INFO runtime::init::dataset: Dataset taxi_trips registered (s3://spiceai-demo-datasets/taxi_trips/2024/), acceleration (cayenne), results cache enabled. duration_ms=329
2026-10-26T06:38:00.310627Z  INFO runtime_table::accelerated::refresh_task: Loaded 2,964,624 rows (398.60 MiB) for dataset taxi_trips in 29s 321ms.
...
2026-10-26T07:27:30.704510Z  INFO huggingface_hub::snapshot: Downloaded model 'qwen3.6' from Hugging Face repo 'unsloth/Qwen3.6-35B-A3B-GGUF' in 50 min 1 s.
2026-10-26T07:27:32.049056Z  INFO runtime::init::model: Model [qwen3.6] deployed, ready for inferencing
2026-10-26T07:27:32.151707Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

The elided lines report settings the runtime derives for this host; the log reports download progress every 30 seconds. Wait for the `deployed, ready for inferencing` line before chatting: `/v1/models` lists the model while it is still downloading.

## Step 3. Chat with the model

In a second terminal, from the same directory:

```bash
spice chat
```

```console
Using model: qwen3.6
chat> How many rows are in the taxi_trips dataset?
There are 2,964,624 rows in the taxi_trips dataset.

chat> What was the largest tip_amount in taxi_trips, and on what date?
The largest tip amount in the taxi_trips dataset was **$428.00**, which occurred on **January 29, 2024**.
```

Qwen3.6 thinks briefly before it answers by default. Behind each answer the model calls `list_datasets`, `table_schema` and `sql` (the first answer took 4.6 seconds end to end on an M3 Max, the second 14 seconds after the model rewrote a query that used `DATE()`, a function Spice's engine does not have). The runtime records every call in `runtime.task_history`, which `spice sql` can query:

```sql
SELECT task, left(input, 80) AS input, round(execution_duration_ms) AS ms
FROM runtime.task_history
WHERE task LIKE 'tool_use::%'
ORDER BY start_time DESC
LIMIT 5;
```

## Step 4. Use the OpenAI-compatible API

Spice serves the model at `http://localhost:8090/v1/chat/completions`, so OpenAI SDKs and clients work unchanged with the model name `qwen3.6`.

```bash
curl -s http://localhost:8090/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3.6",
    "messages": [{"role": "user", "content": "Reply with only the integer 1729."}]
  }'
```

### Reasoning

Qwen3.6 thinks by default and returns the trace in `reasoning_content`, separate from `content`: "Reply with only the integer 1729." took 49 tokens with a 163-character trace. The `reasoning_effort` field controls it per request: `none` turns thinking off for a direct answer (4 tokens), and `low`, `medium` or `high` keep it on (the chat template has one thinking switch, so the three levels are equivalent for this model).

```bash
curl -s http://localhost:8090/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3.6",
    "reasoning_effort": "none",
    "messages": [{"role": "user", "content": "Reply with only the integer 1729."}]
  }'
```

To make direct answers the default for every request, add `hf_reasoning_effort: none` to the model's `params`.

### Speed and context

On an M3 Max, Qwen3.6-35B-A3B at 4-bit decoded about 69 tokens per second and reached its first token in 1.5 seconds on the 1,600-token prompt that `tools: auto` builds: 3B active parameters make it several times faster than the dense 27B models in the Qwen3.8 recipe. The engine uses an 8,192-token context; the dataset tools fit comfortably, and a conversation that outgrows it is cut off with an error that says so.

## Abliterated variant

[`abliterated/`](./abliterated/) is the same recipe with [huihui-ai/Huihui-Qwen3.6-35B-A3B-abliterated](https://huggingface.co/huihui-ai/Huihui-Qwen3.6-35B-A3B-abliterated-MTP-GGUF), a version of Qwen3.6-35B-A3B with its refusal behavior removed by abliteration. It serves the model without the dataset tools, because its stock Qwen chat template trips a runtime bug when `tools: auto` is set ([spiceai/spiceai#15578](https://github.com/spiceai/spiceai/issues/15578)). Read its README before using it: an abliterated model has none of the base model's safety training.

## Troubleshooting

| Symptom                                                                           | Cause and fix                                                                                                      |
| --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `Architecture 'qwen35moe' in <file> is not supported by this Spice release`       | The runtime predates the llama.cpp GGUF engine. Upgrade Spice, or run a trunk build (see below).                   |
| `Unknown GGUF architecture 'qwen35moe'`                                            | A `v2.3.x` or `v2.4.0-rc` runtime, which serves GGUFs with mistral.rs. Same fix.                                   |
| The model never finishes loading, or macOS becomes unresponsive                   | The file does not fit the GPU's share of memory. Choose a smaller file from the [Memory](#memory) table.           |
| `the prompt is N tokens, and the model's context holds 8192`                      | The conversation outgrew the context. Start a new chat.                                                            |
| `spice chat "<question>"` prints nothing for a question that needs the dataset tools | [spiceai/spiceai#15579](https://github.com/spiceai/spiceai/issues/15579): the one-shot form stalls on tool calls. Use the interactive REPL (`spice chat`, then type the question), pipe the question on standard input (`echo "<question>" | spice chat`), or call the API. |
| Slow first start                                                                  | The 22.4 GB download runs at the network's speed; the log reports progress every 30 seconds.                       |

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
rm -rf ~/.cache/huggingface/hub/models--unsloth--Qwen3.6-35B-A3B-GGUF
```

## Learn more

- [Local GGUF models in Spice](https://spiceai.org/docs/components/models#local-gguf-models): engine placement, draft heads, structured output, supported architectures.
- [Hugging Face models](https://spiceai.org/docs/components/models/huggingface) and [reasoning effort for local models](https://spiceai.org/docs/components/models#reasoning-effort-for-local-models).
- [LLM tools](https://spiceai.org/docs/features/large-language-models/tools): the built-in tools behind `tools: auto`.
- [Unsloth's Qwen3.6 guide](https://unsloth.ai/docs/models/qwen3.6): quantization sizes and recommended sampling settings.
