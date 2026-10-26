# Running GLM Locally

Works with `v2.4+` builds that include the [llama.cpp GGUF engine](https://github.com/spiceai/spiceai/pull/7864), merged to trunk on 2026-10-24. `v2.4.0-rc.3` and earlier releases refuse the `glm4moe` and `glm5-next` GGUF architectures; see [Prerequisites](#prerequisites).

Z.ai publishes its GLM models as open weights under the MIT license. The current flagships are [GLM-5.3](https://huggingface.co/zai-org/GLM-5.3) (744B parameters, 40B active) and [GLM-5.3-Flash](https://huggingface.co/zai-org/GLM-5.3-Flash) (320B, 18B active), both released in August 2026. Neither fits a standard MacBook Pro: the smallest GLM-5.3-Flash build is 93 GB, a 128 GB Mac at the least. The GLM that runs on a 36 GB MacBook Pro is [GLM-4.7-Flash](https://huggingface.co/zai-org/GLM-4.7-Flash), Z.ai's January 2026 30B mixture-of-experts reasoning model with about 3.6B active parameters and a 200K context.

This recipe serves **GLM-4.7-Flash** on an Apple silicon Mac with Spice's built-in llama.cpp engine and Metal, and shows how to run **GLM-5.3-Flash** on a 128 GB MacBook Pro by swapping the model block. Abliterated variants of both are in [`abliterated/`](./abliterated/).

GLM-5.2 (June 2026) and GLM-5.3 are the 744B-class flagships: their smallest GGUFs are 217 GB and 223 GB, for a 256 GB or larger Mac Studio rather than a MacBook Pro. Their `glm-dsa` GGUF architecture is one Spice serves, so the same spicepod shape works there, with the shards of [unsloth/GLM-5.2-GGUF](https://huggingface.co/unsloth/GLM-5.2-GGUF) or [unsloth/GLM-5.3-GGUF](https://huggingface.co/unsloth/GLM-5.3-GGUF) listed in `files`.

| Model         | Parameters            | Released     | Fits a 36 GB MacBook Pro          | GGUF repository                                                                     |
| ------------- | --------------------- | ------------ | --------------------------------- | ----------------------------------------------------------------------------------- |
| GLM-4.7-Flash | 30B MoE, ~3.6B active | January 2026 | Yes, from 32 GB; 24 GB at 3-bit (this recipe) | [unsloth/GLM-4.7-Flash-GGUF](https://huggingface.co/unsloth/GLM-4.7-Flash-GGUF)     |
| GLM-5.3-Flash | 320B MoE, 18B active  | August 2026  | No: 93 GB at 1-bit; a 128 GB Mac  | [unsloth/GLM-5.3-Flash-GGUF](https://huggingface.co/unsloth/GLM-5.3-Flash-GGUF)     |
| GLM-5.3       | 744B MoE, 40B active  | August 2026  | No: 223 GB at 1-bit               | unsloth/GLM-5.3-GGUF                                                                |
| GLM-5.2       | 753B MoE, 8 of 256 experts active | June 2026 | No: 217 GB at 1-bit          | [unsloth/GLM-5.2-GGUF](https://huggingface.co/unsloth/GLM-5.2-GGUF)                 |

## Prerequisites

- An Apple silicon Mac with 32 GB or more unified memory for the default file, or 24 GB with the 3-bit file (see [Memory](#memory)). Spice's llama.cpp engine runs the model on the GPU through Metal.
- The [Spice CLI](https://spiceai.org/docs/installation). `spice version` must report a runtime with the `+models.metal` suffix and the llama.cpp GGUF engine. The engine merged to trunk on 2026-10-24, after `v2.4.0-rc.3`; run `spice upgrade` once a release that includes it ships, or use a trunk build in the meantime (see [Using a trunk build](#using-a-trunk-build)).
- 18 GB of free disk for the model, which Spice downloads into the Hugging Face cache at `~/.cache/huggingface/hub`.
- Network access to `huggingface.co`. No Hugging Face account is needed.

## Memory

Spice loads the whole GGUF into GPU memory. macOS gives the GPU most of unified memory but not all of it: Metal reports the budget as `recommendedMaxWorkingSetSize`, which has been two-thirds of unified memory on Macs below 64 GB and three-quarters from 64 GB up (10.7 GiB on a 16 GB Mac, 16 GiB on 24 GB, 24 GiB on 36 GB, 48 GiB on 64 GB); macOS 27 on a 128 GB M3 Max reports more, 107 GiB (84%). The rows below are sized by the smaller figure and leave at least 2 GB under it for the KV cache (under 1 GB at the engine's default 8,192-token context) and the compute buffers. A file larger than the budget fails to load or pages, so when in doubt take the row below yours. A 16 GB Mac is under the minimum for this model: its 10.7 GiB budget leaves no room for even the 2-bit files (10.5 GB and up).

| Unified memory | Model         | File                                                                  | Size     |
| -------------- | ------------- | --------------------------------------------------------------------- | -------- |
| 24 GB          | GLM-4.7-Flash | `GLM-4.7-Flash-UD-Q3_K_XL.gguf`                                       | 13.8 GB  |
| 32 GB          | GLM-4.7-Flash | `GLM-4.7-Flash-UD-Q4_K_XL.gguf` (the default in `spicepod.yaml`)      | 17.5 GB  |
| 36 GB          | GLM-4.7-Flash | `GLM-4.7-Flash-UD-Q5_K_XL.gguf` (or the default)                      | 21.7 GB  |
| 48 GB to 64 GB | GLM-4.7-Flash | `GLM-4.7-Flash-Q8_0.gguf` (near-lossless; `UD-Q6_K_XL`, 26.2 GB, leaves more room) | 31.8 GB  |
| 96 GB and up   | GLM-4.7-Flash | `BF16/GLM-4.7-Flash-BF16-00001-of-00002.gguf` and `-00002-of-00002.gguf` (full precision; over a 64 GB Mac's 48 GiB budget) | 59.9 GB |
| 128 GB         | GLM-5.3-Flash | `UD-IQ2_XXS/GLM-5.3-Flash-UD-IQ2_XXS-00001-of-00004.gguf` … `-00004-of-00004.gguf` (needs the 107 GiB budget of macOS 27; see [GLM-5.3-Flash on a 128 GB MacBook Pro](#glm-53-flash-on-a-128-gb-macbook-pro)) | 101.8 GB |

The GLM-4.7-Flash files are in [unsloth/GLM-4.7-Flash-GGUF](https://huggingface.co/unsloth/GLM-4.7-Flash-GGUF); the `UD-` files are Unsloth's dynamic quantizations, which keep the layers that matter most at higher precision. To switch, change `files[0].path`, listing every shard of a split file.

## Step 1. Review the Spicepod

`spicepod.yaml` in this directory defines one model:

```yaml
version: v2
kind: Spicepod
name: glm

models:
  - from: huggingface:huggingface.co/unsloth/GLM-4.7-Flash-GGUF
    name: glm-4.7-flash
    files:
      - path: GLM-4.7-Flash-UD-Q4_K_XL.gguf
```

`from` names the Hugging Face repository and `files` the GGUF in it. A repository revision can be pinned with `from: huggingface:huggingface.co/<repo>:<commit>`. This recipe does not enable `tools`: GLM's chat template trips a runtime bug when Spice primes the conversation with its `list_datasets` call ([spiceai/spiceai#15578](https://github.com/spiceai/spiceai/issues/15578)), and GLM's tool-call format is not one Spice's parser reads.

## Step 2. Start Spice

```bash
cd models/glm
spice run
```

The first start downloads the model (17.5 GB); later starts load it from cache in a few seconds.

```console
 INFO Spice.ai runtime starting...
2026-10-26T04:06:19.714295Z  INFO spiced: Starting runtime v2.4.0-unstable+models.metal
...
2026-10-26T04:06:19.720337Z  INFO runtime::init::model: Loading model [glm-4.7-flash] from huggingface:huggingface.co/unsloth/GLM-4.7-Flash-GGUF...
2026-10-26T04:06:20.282539Z  INFO huggingface_hub::snapshot: Downloading 1 file (17.5 GB) for model 'glm-4.7-flash' from Hugging Face repo 'unsloth/GLM-4.7-Flash-GGUF' at commit 0d32489 (revision 'main').
...
2026-10-26T05:40:58.497345Z  INFO huggingface_hub::snapshot: Downloaded model 'glm-4.7-flash' from Hugging Face repo 'unsloth/GLM-4.7-Flash-GGUF' in 1 h 34 min.
2026-10-26T05:40:59.701471Z  INFO runtime::init::model: Model [glm-4.7-flash] deployed, ready for inferencing
2026-10-26T05:40:59.803827Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

The elided lines report settings the runtime derives for this host. The download ran on a slow, shared link; the log reports progress every 30 seconds. Wait for the `deployed, ready for inferencing` line before chatting: `/v1/models` lists the model while it is still downloading.

## Step 3. Chat with the model

In a second terminal, from the same directory:

```bash
spice chat
```

```console
Using model: glm-4.7-flash
chat> Explain, in three sentences, what a mixture-of-experts model is.
Mixture-of-Experts models are neural networks composed of multiple specialized sub-networks called experts. A gating mechanism selects which experts to activate for a given input, allowing the model to handle diverse tasks efficiently. This architecture enables the creation of massive models that remain computationally efficient by only processing a small portion of parameters per input.
```

## Step 4. Use the OpenAI-compatible API

Spice serves the model at `http://localhost:8090/v1/chat/completions`, so OpenAI SDKs and clients work unchanged with the model name `glm-4.7-flash`.

```bash
curl -s http://localhost:8090/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "glm-4.7-flash",
    "messages": [{"role": "user", "content": "Reply with only the integer 1729."}]
  }'
```

GLM-4.7-Flash is a reasoning model: it thinks before it answers and returns the trace in `reasoning_content`, separate from `content`. Asked to "Reply with only the integer 1729", it spent 122 tokens (a 477-character trace) before answering; with `reasoning_effort: none` on the request it answered in 2 tokens. To make direct answers the default for every request, add `hf_reasoning_effort: none` to the model's `params`. On an M3 Max the model decodes about 75 tokens per second: 3.6B active parameters make it one of the fastest models of its quality on a laptop. The engine uses an 8,192-token context, and a conversation that outgrows it is cut off with an error that says so.

## GLM-5.3-Flash on a 128 GB MacBook Pro

GLM-5.3-Flash is Z.ai's 320B multimodal mixture of experts with 18B active parameters and a 1M-token context, in the `glm5-next` GGUF architecture. Its 2-bit build is 101.8 GB in four shards and fits the 107 GiB GPU budget that macOS 27 reports on a 128 GB M3 Max, with room for the KV cache; an older macOS that budgets 96 GiB (103 GB) needs the `UD-IQ1_M` or `UD-IQ1_S` build listed below. The GGUF carries GLM's own multi-token-prediction (NextN) layer, and Spice drafts with it automatically: on an NVIDIA DGX Spark, drafting lifted decode speed from 17.5 to 27.1 tokens per second ([spiceai/spiceai#7864](https://github.com/spiceai/spiceai/pull/7864)).

Replace the `models` entry with:

```yaml
models:
  - from: huggingface:huggingface.co/unsloth/GLM-5.3-Flash-GGUF
    name: glm-5.3-flash
    files:
      - path: UD-IQ2_XXS/GLM-5.3-Flash-UD-IQ2_XXS-00001-of-00004.gguf
      - path: UD-IQ2_XXS/GLM-5.3-Flash-UD-IQ2_XXS-00002-of-00004.gguf
      - path: UD-IQ2_XXS/GLM-5.3-Flash-UD-IQ2_XXS-00003-of-00004.gguf
      - path: UD-IQ2_XXS/GLM-5.3-Flash-UD-IQ2_XXS-00004-of-00004.gguf
    params:
      hf_reasoning_effort: low
```

- The download is 102 GB: about two and a half hours at 12 MB/s. The smaller `UD-IQ1_M` (97.6 GB, three shards) and `UD-IQ1_S` (93.1 GB, three shards) builds trade fidelity for headroom; `UD-Q2_K_XL` (108.7 GB, four shards) is the largest that fits, with little room to spare. Unsloth measured top-1 agreement with the full model at 71% for `UD-IQ1_S`, 76% for `UD-IQ2_XXS` and 78% for `UD-Q2_K_XL`.
- GLM-5.3-Flash always reasons; its chat template takes `reasoning_effort` `low` or `high`, and reasons at its maximum when nothing is set. `hf_reasoning_effort: low` makes short reasoning the default, which suits a laptop. A request for `none` or `medium` is refused with HTTP 400 and a message that names the levels the model takes.
- Vision input and GLM's tool-call format are not used by this recipe.

## Abliterated variant

[`abliterated/`](./abliterated/) is the same recipe with [huihui-ai/Huihui-GLM-4.7-Flash-abliterated](https://huggingface.co/huihui-ai/Huihui-GLM-4.7-Flash-abliterated), a version of GLM-4.7-Flash with its refusal behavior removed by abliteration, in the importance-matrix GGUF quantization by mradermacher. Its README also names the abliterated GLM-5.3-Flash builds for a 128 GB Mac. Read it before using either: an abliterated model has none of the base model's safety training.

## Troubleshooting

| Symptom                                                                                  | Cause and fix                                                                                                      |
| ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `Architecture 'glm4moe' in <file> is not supported by this Spice release` (or `glm5-next`) | The runtime predates the llama.cpp GGUF engine. Upgrade Spice, or run a trunk build (see below).                 |
| `Unknown GGUF architecture 'glm4moe'`                                                     | A `v2.3.x` or `v2.4.0-rc` runtime, which serves GGUFs with mistral.rs. Same fix.                                   |
| `Model 'glm-5.3-flash' always reasons, so reasoning_effort: none can't turn reasoning off` | GLM-5.3-Flash's template has no off switch. Use `low` for the least reasoning.                                     |
| Adding `tools: auto` makes every request fail with `cannot convert value into pairs` | This model's chat template iterates tool-call arguments, and the `list_datasets` call Spice primes the conversation with has empty arguments ([spiceai/spiceai#15578](https://github.com/spiceai/spiceai/issues/15578)). Leave tools off until it is fixed. |
| The model never finishes loading, or macOS becomes unresponsive                          | The file does not fit the GPU's share of memory. Choose a smaller file from the [Memory](#memory) table.           |
| `the prompt is N tokens, and the model's context holds 8192`                             | The conversation outgrew the context. Start a new chat.                                                            |

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
rm -rf ~/.cache/huggingface/hub/models--unsloth--GLM-4.7-Flash-GGUF
rm -rf ~/.cache/huggingface/hub/models--unsloth--GLM-5.3-Flash-GGUF
```

## Learn more

- [Local GGUF models in Spice](https://spiceai.org/docs/components/models#local-gguf-models): engine placement, draft heads, structured output, supported architectures.
- [Hugging Face models](https://spiceai.org/docs/components/models/huggingface) and [reasoning effort for local models](https://spiceai.org/docs/components/models#reasoning-effort-for-local-models).
- Unsloth's guides to [GLM-4.7-Flash](https://unsloth.ai/docs/models/glm-4.7-flash) and [GLM-5.3-Flash](https://unsloth.ai/docs/models/glm-5.3-flash): quantization sizes and recommended sampling settings.
