# Running Qwen3.8 Locally

Works with `v2.4+` builds that include the [llama.cpp GGUF engine](https://github.com/spiceai/spiceai/pull/7864), merged to trunk on 2026-10-24. `v2.4.0-rc.3` and earlier releases refuse this model's `qwen35` GGUF architecture; see [Prerequisites](#prerequisites).

[Qwen3.8](https://huggingface.co/collections/Qwen/qwen38) is Alibaba's August 2026 generation of open-weight models. This recipe serves **Qwen3.8-27B**, the dense 27B model released under the Apache 2.0 license, on an Apple silicon Mac with Spice's built-in llama.cpp engine and Metal, grounds the model in a public dataset through Spice's SQL tools, and shows the four reasoning levels the model offers. The model's multi-token-prediction (MTP) draft head is one line away in the spicepod. An [abliterated variant](#abliterated-variant) is in [`abliterated/`](./abliterated/).

| Model               | Parameters                    | Fits a 36 GB MacBook Pro | GGUF repository                                                                           |
| ------------------- | ----------------------------- | ------------------------ | ----------------------------------------------------------------------------------------- |
| Qwen3.8-27B         | 27B dense                     | Yes (this recipe)        | [unsloth/Qwen3.8-27B-GGUF](https://huggingface.co/unsloth/Qwen3.8-27B-GGUF)               |
| Qwen3.8-Flash-Next  | 180B MoE, 10 of 512 experts   | No: 79 GB at 2-bit; a 128 GB Mac (see [Qwen3.8-Flash-Next on a 128 GB Mac](#qwen38-flash-next-on-a-128-gb-mac)) | [unsloth/Qwen3.8-Flash-Next-GGUF](https://huggingface.co/unsloth/Qwen3.8-Flash-Next-GGUF) |
| Qwen3.8-2.4T-A95B   | 2.4T MoE, 95B active          | No: 397 GB at 1-bit      | unsloth/Qwen3.8-2.4T-A95B-GGUF                                                            |

## Prerequisites

- An Apple silicon Mac with 32 GB or more unified memory for the default file, or 16 GB to 24 GB with a smaller file (see [Memory](#memory)). Spice's llama.cpp engine runs the model on the GPU through Metal.
- The [Spice CLI](https://spiceai.org/docs/installation). `spice version` must report a runtime with the `+models.metal` suffix and the llama.cpp GGUF engine. The engine merged to trunk on 2026-10-24, after `v2.4.0-rc.3`; run `spice upgrade` once a release that includes it ships, or use a trunk build in the meantime (see [Using a trunk build](#using-a-trunk-build)).
- 18 GB of free disk for the model (20 GB with the optional draft head), which Spice downloads into the Hugging Face cache at `~/.cache/huggingface/hub`.
- Network access to `huggingface.co` and to the public S3 bucket `spiceai-demo-datasets`. No Hugging Face account is needed.

## Memory

Spice loads the whole GGUF into GPU memory. macOS gives the GPU most of unified memory but not all of it: Metal reports the budget as `recommendedMaxWorkingSetSize` (107 GiB of 128 GiB on an M3 Max). Leave room for the KV cache (under 1 GB at the engine's default 8,192-token context), the optional draft head (1.4 GB) and macOS itself.

| Unified memory | File (`files[0].path`)                                           | Size    |
| -------------- | ---------------------------------------------------------------- | ------- |
| 16 GB          | `Qwen3.8-27B-UD-IQ3_XXS.gguf`                                    | 10.9 GB |
| 24 GB          | `Qwen3.8-27B-UD-IQ4_XS.gguf`                                     | 14.3 GB |
| 32 GB and up   | `Qwen3.8-27B-UD-Q4_K_XL.gguf` (the default in `spicepod.yaml`)   | 17.6 GB |
| 48 GB and up   | `Qwen3.8-27B-UD-Q6_K_XL.gguf`                                    | 25.3 GB |
| 64 GB and up   | `Qwen3.8-27B-Q8_0.gguf` (near-lossless)                          | 29.0 GB |
| 96 GB and up   | `BF16/Qwen3.8-27B-BF16-00001-of-00002.gguf` and `-00002-of-00002.gguf` (full precision) | 54.7 GB |
| 128 GB         | Qwen3.8-Flash-Next at 3-bit, 82 GB (see [Qwen3.8-Flash-Next on a 128 GB Mac](#qwen38-flash-next-on-a-128-gb-mac)) | 82.0 GB |

All files are in [unsloth/Qwen3.8-27B-GGUF](https://huggingface.co/unsloth/Qwen3.8-27B-GGUF); the `UD-` files are Unsloth's dynamic quantizations, which keep the layers that matter most at higher precision. The draft head `MTP/mtp-Qwen3.8-27B-Q4_0.gguf` works with any of them.

## Step 1. Review the Spicepod

`spicepod.yaml` in this directory defines one dataset and one model:

```yaml
version: v2
kind: Spicepod
name: qwen3.8

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
  - from: huggingface:huggingface.co/unsloth/Qwen3.8-27B-GGUF
    name: qwen3.8
    files:
      - path: Qwen3.8-27B-UD-Q4_K_XL.gguf
      # Optional: the model's 1.4 GB multi-token-prediction draft head. Spice drafts with any
      # `mtp-` file listed here. It did not change decode speed measurably on an M3 Max (README.md).
      # - path: MTP/mtp-Qwen3.8-27B-Q4_0.gguf
    params:
      tools: auto
```

- `from` names the Hugging Face repository and `files` the GGUFs in it. Spice downloads every `.gguf` listed. A file whose name starts with `mtp-` is a multi-token-prediction draft head: the head proposes the next tokens and one pass of the model verifies them, so decoding can yield more than one token per pass. Uncomment the line to try it; see [Speed and context](#speed-and-context) for what it measured here.
- `tools: auto` gives the model Spice's built-in tools, including `list_datasets`, `table_schema` and `sql`, so it can answer questions about `taxi_trips` by writing and running SQL.
- The dataset is 2,964,624 rows of Parquet (400 MB) accelerated into Cayenne on first start.

## Step 2. Start Spice

```bash
cd models/qwen3.8
spice run
```

The first start downloads the model (17.6 GB) and the dataset. Later starts load both from cache in a few seconds.

```console
 INFO Spice.ai runtime starting...
2026-10-26T04:03:04.805678Z  INFO runtime::init::model: Loading model [qwen3.8] from huggingface:huggingface.co/unsloth/Qwen3.8-27B-GGUF...
2026-10-26T04:03:05.421390Z  INFO huggingface_hub::snapshot: Downloading 3 files (18.9 GB) for model 'qwen3.8' from Hugging Face repo 'unsloth/Qwen3.8-27B-GGUF' at commit 4ca7207 (revision 'main').
...
2026-10-26T05:44:11.108543Z  INFO huggingface_hub::snapshot: Downloaded model 'qwen3.8' from Hugging Face repo 'unsloth/Qwen3.8-27B-GGUF' in 1 h 41 min.
2026-10-26T05:44:13.109617Z  INFO runtime::init::model: Model [qwen3.8] deployed, ready for inferencing
2026-10-26T05:44:13.133050Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

This run also fetched the optional draft head, hence three files and 18.9 GB; the download ran on a slow, shared link. Wait for the `deployed, ready for inferencing` line before chatting: `/v1/models` lists the model while it is still downloading.

## Step 3. Chat with the model

In a second terminal, from the same directory:

```bash
spice chat
```

```console
Using model: qwen3.8
chat> How many rows are in the taxi_trips dataset?
The **taxi_trips** dataset (NYC taxi trips in 2024) contains **2,964,624 rows**.

chat> What was the largest tip_amount in taxi_trips, and on what date?
The largest tip in `taxi_trips` was **$428.00**, from a trip picked up on **January 29, 2024** (13:30:58).

For context, the next highest tips were $422.70 (Jan 11) and $303.00 (Jan 8).
```

Behind each answer the model calls `list_datasets`, `table_schema` and `sql` (the first answer took 31 seconds end to end on an M3 Max, the second 58 seconds: the tool definitions and results make prompts of 3,000 to 6,000 tokens, and a 27B dense model reads them at a laptop's pace). The runtime records every call in `runtime.task_history`, which `spice sql` can query:

```sql
SELECT task, left(input, 80) AS input, round(execution_duration_ms) AS ms
FROM runtime.task_history
WHERE task LIKE 'tool_use::%'
ORDER BY start_time DESC
LIMIT 5;
```

## Step 4. Use the OpenAI-compatible API

Spice serves the model at `http://localhost:8090/v1/chat/completions`, so OpenAI SDKs and clients work unchanged with the model name `qwen3.8`.

```bash
curl -s http://localhost:8090/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3.8",
    "messages": [{"role": "user", "content": "Reply with only the integer 1729."}]
  }'
```

### Reasoning

Qwen3.8-27B reasons at `xhigh` by default and also takes `medium`, `low` and `none`. The `reasoning_effort` field sets the level per request; the thinking trace comes back in `reasoning_content`, separate from `content`. On "Reply with only the integer 1729." the default spent 41 tokens (a 116-character trace), `low` 42, and `none` answered in 4 tokens; `none` is the fastest setting for tool calls over the dataset.

```bash
curl -s http://localhost:8090/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3.8",
    "reasoning_effort": "low",
    "messages": [{"role": "user", "content": "Reply with only the integer 1729."}]
  }'
```

A level the chat template does not name is refused with HTTP 400 and a message that lists the levels it takes. To set a default for every request, add `hf_reasoning_effort: <level>` to the model's `params`.

### Speed and context

On an M3 Max (128 GB) that was also running other work, Qwen3.8-27B at 4-bit decoded 11 to 14 tokens per second and took 10 to 15 seconds to the first token on the 1,600-token prompt that `tools: auto` builds. The optional `mtp-` draft head changed neither figure measurably in that run (13.6 and 11.1 tokens per second with it, 13.2 and 12.9 without), so the spicepod leaves it commented out; a draft head never changes which tokens are likely, only how many a pass yields, so trying it is free. For a snappier laptop experience at this size, the Qwen3.6 recipe's 35B-A3B model (3B active) decodes several times faster. The engine uses an 8,192-token context; the dataset tools fit comfortably, and a conversation that outgrows it is cut off with an error that says so.

## Qwen3.8-Flash-Next on a 128 GB Mac

Qwen3.8-Flash-Next is the family's 180B mixture-of-experts model (`qwen4exp` architecture). At 3-bit it is 82 GB, which fits a 128 GB Mac. Replace the `models` entry with the one below; the separate `mtp-` file is its draft head. Flash-Next takes `reasoning_effort` `xhigh` (the default), `medium`, `low` and `none`.

```yaml
models:
  - from: huggingface:huggingface.co/unsloth/Qwen3.8-Flash-Next-GGUF
    name: qwen3.8-flash-next
    files:
      - path: UD-IQ3_XXS/Qwen3.8-Flash-Next-UD-IQ3_XXS-00001-of-00003.gguf
      - path: UD-IQ3_XXS/Qwen3.8-Flash-Next-UD-IQ3_XXS-00002-of-00003.gguf
      - path: UD-IQ3_XXS/Qwen3.8-Flash-Next-UD-IQ3_XXS-00003-of-00003.gguf
      - path: MTP/mtp-Qwen3.8-Flash-Next-Q8_0.gguf
    params:
      tools: auto
```

## Abliterated variant

[`abliterated/`](./abliterated/) is the same recipe with [orcarouter/Qwen3.8-27B-Uncensored](https://huggingface.co/orcarouter/Qwen3.8-27B-Uncensored-GGUF), a version of Qwen3.8-27B with its refusal behavior removed by abliteration and documented with before-and-after refusal and benchmark measurements. Read its README before using it: an abliterated model has none of the base model's safety training, and the repository is gated behind a Hugging Face token.

## Troubleshooting

| Symptom                                                                        | Cause and fix                                                                                                      |
| ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------ |
| `Architecture 'qwen35' in <file> is not supported by this Spice release`       | The runtime predates the llama.cpp GGUF engine. Upgrade Spice, or run a trunk build (see below).                   |
| `Unknown GGUF architecture 'qwen35'`                                            | A `v2.3.x` or `v2.4.0-rc` runtime, which serves GGUFs with mistral.rs. Same fix.                                   |
| `Model 'qwen3.8' takes reasoning_effort ... and ignores 'high'` (HTTP 400)      | Qwen3.8's template names `xhigh`, `medium`, `low` and `none`. Use one of those.                                    |
| The model never finishes loading, or macOS becomes unresponsive                | The file does not fit the GPU's share of memory. Choose a smaller file from the [Memory](#memory) table.           |
| `spice chat "<question>"` prints nothing for a question that needs the dataset tools | [spiceai/spiceai#15579](https://github.com/spiceai/spiceai/issues/15579): the one-shot form stalls on tool calls. Use the interactive REPL (`spice chat`, then type the question), pipe the question on standard input (`echo "<question>" | spice chat`), or call the API. |
| `the prompt is N tokens, and the model's context holds 8192`                   | The conversation outgrew the context. Start a new chat.                                                            |

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
rm -rf ~/.cache/huggingface/hub/models--unsloth--Qwen3.8-27B-GGUF
```

## Learn more

- [Local GGUF models in Spice](https://spiceai.org/docs/components/models#local-gguf-models): engine placement, draft heads, structured output, supported architectures.
- [Hugging Face models](https://spiceai.org/docs/components/models/huggingface) and [reasoning effort for local models](https://spiceai.org/docs/components/models#reasoning-effort-for-local-models).
- [LLM tools](https://spiceai.org/docs/features/large-language-models/tools): the built-in tools behind `tools: auto`.
- [Unsloth's Qwen3.8 guide](https://unsloth.ai/docs/models/qwen3.8): quantization sizes and recommended sampling settings.
