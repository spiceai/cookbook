# Running DeepSeek V4 Locally

Works with `v2.4+` builds that include the [llama.cpp GGUF engine](https://github.com/spiceai/spiceai/pull/7864), merged to trunk on 2026-10-24. `v2.4.0-rc.3` and earlier releases refuse this model's `deepseek4` GGUF architecture; see [Prerequisites](#prerequisites).

DeepSeek-V4 is DeepSeek's 2026 generation of open-weight mixture-of-experts models under the MIT license: DeepSeek-V4-Pro (1.6T parameters, 49B active) and DeepSeek-V4-Flash (284B, 13B active), previewed in April 2026, with [DeepSeek-V4-Flash-0731](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731) as the official Flash release on July 31. Both are 1M-context reasoning models with `low`, `high` and `max` reasoning levels.

**No DeepSeek-V4 build fits a 36 GB MacBook Pro.** The smallest GGUF of DeepSeek-V4-Flash is 82.5 GB at 1-bit, and DeepSeek publishes no smaller current-generation model (its last small models were the January 2025 R1 distillations). This recipe therefore targets a **128 GB MacBook Pro** (M3 Max or M4 Max), the smallest Mac that runs the model, and serves DeepSeek-V4-Flash-0731 with Spice's built-in llama.cpp engine and Metal. An [abliterated variant](#abliterated-variant) is in [`abliterated/`](./abliterated/).

| Model                   | Parameters           | Released      | Smallest GGUF | Fits                                        |
| ----------------------- | -------------------- | ------------- | ------------- | ------------------------------------------- |
| DeepSeek-V4-Flash-0731  | 284B MoE, 13B active | July 2026     | 82.5 GB       | A 128 GB Mac (this recipe)                  |
| DeepSeek-V4-Pro-0813    | 1.6T MoE, 49B active | August 2026   | 400 GB-class  | No Mac                                      |
| DeepSeek-V4.1-Flash-1017 | 552B + 196B Engram  | October 2026  | 233 GB        | No MacBook Pro; a recipe is pending runtime support ([spiceai/cookbook#739](https://github.com/spiceai/cookbook/pull/739)) |

## Prerequisites

- An Apple silicon Mac with 128 GB unified memory. Spice's llama.cpp engine runs the model on the GPU through Metal, and Metal reports 107 GiB of a 128 GiB Mac as available to the GPU (`recommendedMaxWorkingSetSize`), which holds the default 90.9 GB file with room for the KV cache.
- The [Spice CLI](https://spiceai.org/docs/installation). `spice version` must report a runtime with the `+models.metal` suffix and the llama.cpp GGUF engine. The engine merged to trunk on 2026-10-24, after `v2.4.0-rc.3`; run `spice upgrade` once a release that includes it ships, or use a trunk build in the meantime (see [Using a trunk build](#using-a-trunk-build)).
- 95 GB of free disk for the model, which Spice downloads into the Hugging Face cache at `~/.cache/huggingface/hub`. The download takes about two hours at 12 MB/s.
- Network access to `huggingface.co`. No Hugging Face account is needed.

## Memory

| Unified memory | File prefix (`UD-<quant>/DeepSeek-V4-Flash-0731-UD-<quant>-0000N-of-0000M.gguf`) | Shards | Size     |
| -------------- | ----------------------------------------------------------------------------------- | ------ | -------- |
| 128 GB         | `UD-IQ1_S`                                                                           | 3      | 82.5 GB  |
| 128 GB         | `UD-IQ1_M`                                                                           | 3      | 86.9 GB  |
| 128 GB         | `UD-IQ2_M` (the default in `spicepod.yaml`)                                          | 3      | 90.9 GB  |
| 128 GB         | `UD-Q2_K_XL`                                                                         | 3      | 96.8 GB  |
| 128 GB, little headroom | `UD-IQ3_XXS`                                                                | 4      | 104.2 GB |
| 192 GB and up  | `UD-Q3_K_XL` (128.2 GB), `UD-IQ4_XS` (136.7 GB), `UD-Q4_K_XL` (155.1 GB)             | 4 to 5 |          |

All files are in [unsloth/DeepSeek-V4-Flash-0731-GGUF](https://huggingface.co/unsloth/DeepSeek-V4-Flash-0731-GGUF); the `UD-` prefix marks Unsloth's dynamic quantizations, which keep the layers that matter most at higher precision. List every shard of the chosen build in `files`. The repository's `dspark-*.gguf` files are DeepSeek's DSpark speculative-decoding head for other engines; Spice reads only draft heads named `mtp-*.gguf`, so leave them out.

## Step 1. Review the Spicepod

`spicepod.yaml` in this directory defines one model:

```yaml
version: v2
kind: Spicepod
name: deepseek-v4

models:
  - from: huggingface:huggingface.co/unsloth/DeepSeek-V4-Flash-0731-GGUF
    name: deepseek-v4-flash
    files:
      - path: UD-IQ2_M/DeepSeek-V4-Flash-0731-UD-IQ2_M-00001-of-00003.gguf
      - path: UD-IQ2_M/DeepSeek-V4-Flash-0731-UD-IQ2_M-00002-of-00003.gguf
      - path: UD-IQ2_M/DeepSeek-V4-Flash-0731-UD-IQ2_M-00003-of-00003.gguf
```

`from` names the Hugging Face repository and `files` the shards of the GGUF. A repository revision can be pinned with `from: huggingface:huggingface.co/<repo>:<commit>`. This recipe does not enable `tools`: DeepSeek's chat template trips a runtime bug when Spice primes the conversation with its `list_datasets` call ([spiceai/spiceai#15578](https://github.com/spiceai/spiceai/issues/15578)).

## Step 2. Start Spice

```bash
cd models/deepseek-v4
spice run
```

The first start downloads the three shards (90.9 GB); later starts load them from cache. Loading 91 GB of weights takes about a minute and a half:

```console
 INFO Spice.ai runtime starting...
2026-10-26T17:02:41.921751Z  INFO spiced: Starting runtime v2.4.0-unstable-build.ec36a7cc5e+models.cuda
...
2026-10-26T17:02:42.150683Z  INFO runtime::init::model: Loading model [deepseek-v4-flash] from file...
2026-10-26T17:04:06.882623Z  INFO runtime::init::model: Model [deepseek-v4-flash] deployed, ready for inferencing
2026-10-26T17:04:06.985227Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

These lines are from a run of this recipe's three shards on an NVIDIA DGX Spark (128 GB of unified memory, the same memory class as a 128 GB MacBook Pro) with the same llama.cpp engine built for CUDA; on a Mac the runtime reports `+models.metal` and the download lines of the `huggingface:` spicepod precede them. Wait for the `deployed, ready for inferencing` line before chatting: `/v1/models` lists the model while it is still downloading. With the model loaded, 9 GB of the 121 GB the machine reports remained free.

## Step 3. Chat with the model

In a second terminal, from the same directory:

```bash
spice chat
```

```console
Using model: deepseek-v4-flash
chat> Explain, in three sentences, why a mixture-of-experts model decodes faster than a dense model of the same size.
A mixture-of-experts (MoE) model decodes faster than a dense model of the same size because it only activates a small subset of its total parameters for each token, rather than computing through all of them. This sparsity reduces the per-token floating-point operations (FLOPs) and memory bandwidth required, leading to lower latency during generation. Meanwhile, the model retains the capacity of a much larger network by routing inputs to specialized experts, achieving comparable quality with significantly less computational cost.
```

## Step 4. Use the OpenAI-compatible API

Spice serves the model at `http://localhost:8090/v1/chat/completions`, so OpenAI SDKs and clients work unchanged with the model name `deepseek-v4-flash`.

```bash
curl -s http://localhost:8090/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-v4-flash",
    "messages": [{"role": "user", "content": "Reply with only the integer 1729."}]
  }'
```

With Unsloth's chat template, DeepSeek-V4-Flash answers directly unless a request asks it to think. "Reply with only the integer 1729." came back in 2 tokens with nothing set and with `reasoning_effort: none`; `low` and `medium` each gave an 88-token answer with a 318-character trace, and `high` a 13-token answer with a short one. The trace arrives in `reasoning_content`, separate from `content`. The field takes the OpenAI levels only (`none`, `minimal`, `low`, `medium`, `high`, `xhigh`). DeepSeek's own "max" is not one of them: the request is refused with HTTP 422 and `reasoning_effort: unknown variant `max``, before it reaches the model. To set a default for every request, add `hf_reasoning_effort: <level>` to the model's `params`. DeepSeek recommends temperature 1.0 and top-p 1.0 (0.95 for agentic use). On the DGX Spark the model decoded about 21 tokens per second; a 128 GB MacBook Pro has comparable memory bandwidth. The engine uses an 8,192-token context, and a conversation that outgrows it is cut off with an error that says so.

## Abliterated variant

[`abliterated/`](./abliterated/) is the same recipe with [huihui-ai/Huihui-DeepSeek-V4-Flash-0731-abliterated](https://huggingface.co/huihui-ai/Huihui-DeepSeek-V4-Flash-0731-abliterated-GGUF), a version of DeepSeek-V4-Flash-0731 with its refusal behavior removed by abliteration, as a single 86.7 GB 2-bit GGUF. Read its README before using it: an abliterated model has none of the base model's safety training.

## Troubleshooting

| Symptom                                                                       | Cause and fix                                                                                                                 |
| ----------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `Architecture 'deepseek4' in <file> is not supported by this Spice release`   | The runtime predates the llama.cpp GGUF engine. Upgrade Spice, or run a trunk build (see below).                              |
| `GGUF architecture deepseek4 (DeepSeek-V4) is recognized but not implemented` | A `v2.3.x` or `v2.4.0-rc` runtime, which serves GGUFs with mistral.rs. Same fix.                                              |
| Adding `tools: auto` makes every request fail with `cannot convert value into pairs` | This model's chat template iterates tool-call arguments, and the `list_datasets` call Spice primes the conversation with has empty arguments ([spiceai/spiceai#15578](https://github.com/spiceai/spiceai/issues/15578)). Leave tools off until it is fixed. |
| The model never finishes loading, or macOS becomes unresponsive               | The build does not fit the GPU's share of memory. Choose a smaller build from the [Memory](#memory) table, or close other apps. |
| A `dspark-*.gguf` file listed in `files` fails the load                         | It is not a shard of the model. Remove it.                                                                                     |
| `the prompt is N tokens, and the model's context holds 8192`                  | The conversation outgrew the context. Start a new chat.                                                                        |

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
rm -rf ~/.cache/huggingface/hub/models--unsloth--DeepSeek-V4-Flash-0731-GGUF
```

## Learn more

- [Local GGUF models in Spice](https://spiceai.org/docs/components/models#local-gguf-models): engine placement, draft heads, structured output, supported architectures.
- [Hugging Face models](https://spiceai.org/docs/components/models/huggingface) and [reasoning effort for local models](https://spiceai.org/docs/components/models#reasoning-effort-for-local-models).
- [Unsloth's DeepSeek-V4 guide](https://unsloth.ai/docs/models/deepseek-v4): quantization sizes and recommended sampling settings.
