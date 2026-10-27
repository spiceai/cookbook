# Running DeepSeek V4.1 Locally

Works with `v2.4+` builds that include the [llama.cpp GGUF engine](https://github.com/spiceai/spiceai/pull/7864) once that engine's llama.cpp supports the `deepseek41` GGUF architecture; see [Runtime support](#runtime-support).

[DeepSeek-V4.1-Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash) (September 2026) and its [1017 update](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017) (October 17, 2026) are DeepSeek's newest open-weight models, under the MIT license: a 552B-parameter mixture-of-experts backbone with a 196B-parameter Engram memory table, a 1M-token context, and a `reasoning_effort` that takes `low`, `medium`, `high`, `max` or an integer from 1 to 100. The 1017 update raised coding and agentic scores (Terminal-Bench 4.0 from 31.2 to 42.3) and shortened its outputs.

**No MacBook Pro runs DeepSeek-V4.1-Flash.** The smallest GGUF, Unsloth's 1-bit `UD-IQ1_S`, is 233 GB, of which about 122 GB of weights must sit in GPU memory; the Engram table (110.6 GB in that build) is read one row per token and can be paged from SSD. The default in this recipe, `UD-IQ1_M`, keeps 140 GB of weights in memory and needs a **256 GB Mac Studio**; the 2-bit builds need 512 GB. This recipe exists so that the spicepod is ready for that hardware and for the runtime support described below. For a DeepSeek model that a 128 GB MacBook Pro can serve today, see the [DeepSeek V4 recipe](../deepseek-v4/README.md). An [abliterated variant](#abliterated-variant) is in [`abliterated/`](./abliterated/).

## Runtime support

Spice serves single-node GGUF models with llama.cpp. The llama.cpp release that Spice pins, `b11803`, does not include the `deepseek41` architecture. Upstream llama.cpp added it in [ggml-org/llama.cpp#31086](https://github.com/ggml-org/llama.cpp/pull/31086), merged on October 25, 2026, after `b11803` (it replaced [ggml-org/llama.cpp#30817](https://github.com/ggml-org/llama.cpp/pull/30817), now closed). So upstream support exists; what is still missing is a Spice release that moves its llama.cpp pin past that change. Until then, the load fails with:

```text
Architecture 'deepseek41' in DeepSeek-V4.1-Flash-1017-UD-IQ1_M-00001-of-00005.gguf is not supported by this Spice release. Upgrade Spice, or use a GGUF of a supported architecture: https://spiceai.org/docs/components/models#gguf-architectures
```

That is the message the engine gave on 2026-10-26 (build `ec36a7cc`, the llama.cpp engine at `b11803`) when handed a DeepSeek-V4.1-Flash-1017 GGUF on an NVIDIA DGX Spark, before allocating any memory:

```console
2026-10-26T16:50:00.211547Z  INFO runtime::init::model: Loading model [deepseek-v4.1-flash] from file...
2026-10-26T16:50:00.624562Z  WARN runtime::init::model: Failed to load LLM: deepseek-v4.1-flash. Failed to initialize LLM model: Architecture 'deepseek41' in DeepSeek-V4.1-Flash-1017-Q2_K-00001-of-00010.gguf is not supported by this Spice release. Upgrade Spice, or use a GGUF of a supported architecture: https://spiceai.org/docs/components/models#gguf-architectures
```

Spice's mistral.rs engine has a `deepseek41` graph, but uses it only for GGUF models with `distributed_backend: ring` (Spice Enterprise, tensor-parallel across several machines such as a ring of NVIDIA DGX Sparks).

## Memory

| Build        | Shards | Total download | Weights in GPU memory | Hardware                                   |
| ------------ | ------ | -------------- | --------------------- | ------------------------------------------ |
| `UD-IQ1_S`   | 5      | 233.0 GB       | 122 GB                | 256 GB Mac Studio, Engram table on SSD     |
| `UD-IQ1_M` (the default in `spicepod.yaml`) | 5 | 250.4 GB | 140 GB     | 256 GB Mac Studio, Engram table on SSD     |
| `UD-IQ2_XXS` | 6      | 300.5 GB       | 165 GB                | 256 GB Mac Studio (table on SSD) or 512 GB |
| `UD-Q2_K_XL` | 7      | 334.8 GB       | 200 GB                | 512 GB Mac Studio                          |
| `UD-IQ3_XXS` | 7      | 394.7 GB       | 234 GB                | 512 GB Mac Studio                          |

All builds are in [unsloth/DeepSeek-V4.1-Flash-1017-GGUF](https://huggingface.co/unsloth/DeepSeek-V4.1-Flash-1017-GGUF), with the Engram table as the last shard of each. Unsloth measured 88% top-1 agreement with the full model for `UD-IQ1_M`. The repository's `dspark-*.gguf` files are DeepSeek's DSpark speculative-decoding head for other engines; Spice reads only draft heads named `mtp-*.gguf`, so leave them out.

## Step 1. Review the Spicepod

`spicepod.yaml` in this directory defines one model:

```yaml
version: v2
kind: Spicepod
name: deepseek-v4.1

models:
  - from: huggingface:huggingface.co/unsloth/DeepSeek-V4.1-Flash-1017-GGUF
    name: deepseek-v4.1-flash
    files:
      - path: UD-IQ1_M/DeepSeek-V4.1-Flash-1017-UD-IQ1_M-00001-of-00005.gguf
      - path: UD-IQ1_M/DeepSeek-V4.1-Flash-1017-UD-IQ1_M-00002-of-00005.gguf
      - path: UD-IQ1_M/DeepSeek-V4.1-Flash-1017-UD-IQ1_M-00003-of-00005.gguf
      - path: UD-IQ1_M/DeepSeek-V4.1-Flash-1017-UD-IQ1_M-00004-of-00005.gguf
      - path: UD-IQ1_M/DeepSeek-V4.1-Flash-1017-UD-IQ1_M-00005-of-00005.gguf
```

`from` names the Hugging Face repository and `files` the five shards of the GGUF. A repository revision can be pinned with `from: huggingface:huggingface.co/<repo>:<commit>`. This recipe does not enable `tools`: DeepSeek's chat template trips a runtime bug when Spice primes the conversation with its `list_datasets` call ([spiceai/spiceai#15578](https://github.com/spiceai/spiceai/issues/15578)).

## Step 2. Start Spice

```bash
cd models/deepseek-v4.1
spice run
```

The first start downloads the five shards (250 GB, about six hours at 12 MB/s). Wait for `Model [deepseek-v4.1-flash] deployed, ready for inferencing` and `All components are loaded. Spice runtime is ready!` before chatting.

## Step 3. Chat with the model

In a second terminal, from the same directory:

```bash
spice chat
```

```console
Using model: deepseek-v4.1-flash
chat> Explain, in three sentences, what an Engram memory table adds to a transformer.
```

## Step 4. Use the OpenAI-compatible API

Spice serves the model at `http://localhost:8090/v1/chat/completions`, so OpenAI SDKs and clients work unchanged with the model name `deepseek-v4.1-flash`.

```bash
curl -s http://localhost:8090/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-v4.1-flash",
    "reasoning_effort": "high",
    "messages": [{"role": "user", "content": "Reply with only the integer 1729."}]
  }'
```

Set `reasoning_effort` explicitly: `none` for a direct answer, or `low`, `medium`, `high` or `xhigh` for a thinking trace in `reasoning_content`. The field takes those OpenAI levels only; DeepSeek's own "max" is refused with HTTP 422 before it reaches the model. Which levels the V4.1 template honors could not be checked, since no Spice build loads the model yet (see Runtime support). DeepSeek recommends temperature 1.0 and top-p 1.0, and a generous `max_tokens` for the longer levels. To set a default for every request, add `hf_reasoning_effort: <level>` to the model's `params`. The engine uses an 8,192-token context, and a conversation that outgrows it is cut off with an error that says so.

## Abliterated variant

[`abliterated/`](./abliterated/) is the same recipe with [orcarouter/DeepSeek-V4.1-Flash-1017-abliterated](https://huggingface.co/orcarouter/DeepSeek-V4.1-Flash-1017-abliterated-GGUF), a version of DeepSeek-V4.1-Flash-1017 with its refusal behavior removed by abliteration, documented with before-and-after measurements. Read its README before using it: an abliterated model has none of the base model's safety training, the repository is gated behind a Hugging Face token, and its default build needs a 512 GB Mac Studio.

## Troubleshooting

| Symptom                                                                          | Cause and fix                                                                                                                      |
| -------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `Architecture 'deepseek41' in <file> is not supported by this Spice release`     | The runtime's llama.cpp predates `deepseek41` support; see [Runtime support](#runtime-support).                                    |
| `Unknown GGUF architecture 'deepseek41'`                                          | A `v2.3.x` or `v2.4.0-rc` runtime. Same fix.                                                                                       |
| Adding `tools: auto` makes every request fail with `cannot convert value into pairs` | This model's chat template iterates tool-call arguments, and the `list_datasets` call Spice primes the conversation with has empty arguments ([spiceai/spiceai#15578](https://github.com/spiceai/spiceai/issues/15578)). Leave tools off until it is fixed. |
| The model never finishes loading, or macOS becomes unresponsive                  | The weights do not fit the GPU's share of memory. This model needs a 256 GB or larger Mac; see [Memory](#memory).                  |
| A `dspark-*.gguf` file listed in `files` fails the load                            | It is not a shard of the model. Remove it.                                                                                         |

## Clean up

```bash
rm -rf ~/.cache/huggingface/hub/models--unsloth--DeepSeek-V4.1-Flash-1017-GGUF
```

## Learn more

- [Local GGUF models in Spice](https://spiceai.org/docs/components/models#local-gguf-models): engine placement, draft heads, structured output, supported architectures.
- [Hugging Face models](https://spiceai.org/docs/components/models/huggingface) and [reasoning effort for local models](https://spiceai.org/docs/components/models#reasoning-effort-for-local-models).
- [Unsloth's DeepSeek-V4.1-Flash guide](https://unsloth.ai/docs/models/deepseek-v4.1-flash): quantization sizes, the Engram table, and recommended sampling settings.
