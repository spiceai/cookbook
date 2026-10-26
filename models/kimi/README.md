# Running Kimi Locally

Works with `v2.4+` builds that include the [llama.cpp GGUF engine](https://github.com/spiceai/spiceai/pull/7864), merged to trunk on 2026-10-24. `v2.4.0-rc.3` and earlier releases refuse this model's `kimi-linear` GGUF architecture; see [Prerequisites](#prerequisites).

Moonshot AI's Kimi models are open weights, but the flagship ones are trillion-parameter mixtures of experts: Kimi K2.6 (1T parameters) is 340 GB at 2-bit, and Kimi K3 (2.8T parameters, June 2026) is 466 GB even in Unsloth's 1-bit `UD-Q1_0` build, so neither fits a MacBook Pro (a 512 GB Mac Studio could hold K2.6 at 2-bit, which this recipe does not test); they are served from multi-GPU servers, or tensor-parallel across several machines with Spice Enterprise's `distributed_backend: ring`. The Kimi model that runs on a laptop is **Kimi-Linear-48B-A3B-Instruct**, Moonshot's 48B mixture-of-experts model with 3B active parameters, built on Kimi Delta Attention, a hybrid linear-attention design that keeps the KV cache small at long context. This recipe serves it on an Apple silicon Mac with Spice's built-in llama.cpp engine and Metal. An [abliterated variant](#abliterated-variant) is in [`abliterated/`](./abliterated/).

| Model                        | Parameters              | Released     | Fits a 36 GB MacBook Pro       | GGUF repository                                                                                                           |
| ---------------------------- | ----------------------- | ------------ | ------------------------------ | ------------------------------------------------------------------------------------------------------------------------- |
| Kimi-Linear-48B-A3B-Instruct | 48B MoE, 3B active      | October 2025 | Yes (this recipe)              | [bartowski/moonshotai_Kimi-Linear-48B-A3B-Instruct-GGUF](https://huggingface.co/bartowski/moonshotai_Kimi-Linear-48B-A3B-Instruct-GGUF) |
| Kimi K2.6                    | 1T MoE, 32B active      | April 2026   | No: 340 GB at 2-bit            | unsloth/Kimi-K2.6-GGUF                                                                                                    |
| Kimi K2.7-Code               | 1T MoE                  | June 2026    | No                             | unsloth/Kimi-K2.7-Code-GGUF                                                                                               |
| Kimi K3                      | 2.8T MoE, 896 experts   | June 2026    | No: 466 GB at 1-bit, 861 GB at 2-bit | [unsloth/Kimi-K3-GGUF](https://huggingface.co/unsloth/Kimi-K3-GGUF)                                                 |

Moonshot publishes Kimi-Linear under the MIT license. The GGUF quantizations are by bartowski, a maintainer of community llama.cpp quantizations, since neither Moonshot nor Unsloth publishes one.

## Prerequisites

- An Apple silicon Mac with 36 GB or more unified memory for the default file, or 24 GB with the 2-bit file (see [Memory](#memory)). Spice's llama.cpp engine runs the model on the GPU through Metal.
- The [Spice CLI](https://spiceai.org/docs/installation). `spice version` must report a runtime with the `+models.metal` suffix and the llama.cpp GGUF engine. The engine merged to trunk on 2026-10-24, after `v2.4.0-rc.3`; run `spice upgrade` once a release that includes it ships, or use a trunk build in the meantime (see [Using a trunk build](#using-a-trunk-build)).
- 23 GB of free disk for the model, which Spice downloads into the Hugging Face cache at `~/.cache/huggingface/hub`.
- Network access to `huggingface.co`. No Hugging Face account is needed.

## Memory

Spice loads the whole GGUF into GPU memory. macOS gives the GPU most of unified memory but not all of it: Metal reports the budget as `recommendedMaxWorkingSetSize` (107 GiB of 128 GiB on an M3 Max). Leave room for the KV cache, which Kimi Delta Attention keeps small, and for macOS itself.

| Unified memory | File (`files[0].path`)                                                        | Size    |
| -------------- | ----------------------------------------------------------------------------- | ------- |
| 24 GB          | `moonshotai_Kimi-Linear-48B-A3B-Instruct-IQ2_M.gguf`                          | 15.8 GB |
| 32 GB          | `moonshotai_Kimi-Linear-48B-A3B-Instruct-IQ3_XXS.gguf`                        | 19.7 GB |
| 36 GB and up   | `moonshotai_Kimi-Linear-48B-A3B-Instruct-IQ3_M.gguf` (the default in `spicepod.yaml`) | 22.7 GB |
| 48 GB and up   | `moonshotai_Kimi-Linear-48B-A3B-Instruct-Q4_K_M.gguf`                         | 30.1 GB |
| 64 GB and up   | `moonshotai_Kimi-Linear-48B-A3B-Instruct-Q6_K.gguf`                           | 40.5 GB |
| 96 GB and up   | `moonshotai_Kimi-Linear-48B-A3B-Instruct-Q8_0/moonshotai_Kimi-Linear-48B-A3B-Instruct-Q8_0-00001-of-00002.gguf` and `-00002-of-00002.gguf` (near-lossless) | 52.2 GB |
| 128 GB         | `moonshotai_Kimi-Linear-48B-A3B-Instruct-bf16/moonshotai_Kimi-Linear-48B-A3B-Instruct-bf16-00001-of-00003.gguf` and its two sibling shards (full precision) | 98.3 GB |

The `IQ` files are importance-matrix quantizations, which keep more of the model's quality at the same size than the plain `Q` files. List every shard of a split file in `files`. Kimi K2.6 stays out of reach: its 2-bit build is 340 GB.

## Step 1. Review the Spicepod

`spicepod.yaml` in this directory defines one model:

```yaml
version: v2
kind: Spicepod
name: kimi

models:
  - from: huggingface:huggingface.co/bartowski/moonshotai_Kimi-Linear-48B-A3B-Instruct-GGUF
    name: kimi-linear
    files:
      - path: moonshotai_Kimi-Linear-48B-A3B-Instruct-IQ3_M.gguf
```

`from` names the Hugging Face repository and `files` the GGUF in it. A repository revision can be pinned with `from: huggingface:huggingface.co/<repo>:<commit>`. Kimi-Linear's tool-call format is not one Spice's parser reads, so this recipe does not enable `tools`.

## Step 2. Start Spice

```bash
cd models/kimi
spice run
```

The first start downloads the model (22.7 GB); later starts load it from cache in a few seconds.

```console
 INFO Spice.ai runtime starting...
2026-10-26T05:41:57.483463Z  INFO spiced: Starting runtime v2.4.0-unstable+models.metal
...
2026-10-26T05:41:57.491583Z  INFO runtime::init::model: Loading model [kimi-linear] from huggingface:huggingface.co/bartowski/moonshotai_Kimi-Linear-48B-A3B-Instruct-GGUF...
2026-10-26T05:41:57.893767Z  INFO huggingface_hub::snapshot: Downloading 1 file (22.7 GB) for model 'kimi-linear' from Hugging Face repo 'bartowski/moonshotai_Kimi-Linear-48B-A3B-Instruct-GGUF' at commit 228dbe4 (revision 'main').
...
2026-10-26T06:36:54.084353Z  INFO huggingface_hub::snapshot: Downloaded model 'kimi-linear' from Hugging Face repo 'bartowski/moonshotai_Kimi-Linear-48B-A3B-Instruct-GGUF' in 54 min 56 s.
2026-10-26T06:36:55.557496Z  INFO runtime::init::model: Model [kimi-linear] deployed, ready for inferencing
2026-10-26T06:36:55.660328Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

The elided lines report settings the runtime derives for this host; the log reports download progress every 30 seconds. Wait for the `deployed, ready for inferencing` line before chatting: `/v1/models` lists the model while it is still downloading.

## Step 3. Chat with the model

In a second terminal, from the same directory:

```bash
spice chat
```

```console
Using model: kimi-linear
chat> Explain, in three sentences, what a mixture-of-experts model is.
A mixture-of-experts (MoE) model splits its parameters into multiple “expert” sub-networks and adds a lightweight “gating” network that learns to route each input to a subset of experts, so only those selected sub-networks are actually evaluated. This sparsely-activated structure lets the overall model behave like an ensemble of specialized sub-models while keeping the total number of active parameters small, yielding large capacity with modest compute cost.
```

## Step 4. Use the OpenAI-compatible API

Spice serves the model at `http://localhost:8090/v1/chat/completions`, so OpenAI SDKs and clients work unchanged with the model name `kimi-linear`.

```bash
curl -s http://localhost:8090/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "kimi-linear",
    "messages": [{"role": "user", "content": "Reply with only the integer 1729."}]
  }'
```

Kimi-Linear is an instruct model without a thinking mode: it answered "Reply with only the integer 1729." in 2 tokens, and `reasoning_effort` changes nothing. With 3B active parameters it is fast: about 85 tokens per second on an M3 Max, the fastest of the models in these recipes. The engine uses an 8,192-token context; the model itself supports up to 1M tokens, and a conversation that outgrows the context is cut off with an error that says so.

## Abliterated variant

[`abliterated/`](./abliterated/) is the same recipe with [huihui-ai/Huihui-Kimi-Linear-48B-A3B-Instruct-abliterated](https://huggingface.co/mradermacher/Huihui-Kimi-Linear-48B-A3B-Instruct-abliterated-i1-GGUF), a version of Kimi-Linear with its refusal behavior removed by abliteration, in the importance-matrix GGUF quantization by mradermacher. Read its README before using it: an abliterated model has none of the base model's safety training.

## Troubleshooting

| Symptom                                                                           | Cause and fix                                                                                                      |
| --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `Architecture 'kimi-linear' in <file> is not supported by this Spice release`     | The runtime predates the llama.cpp GGUF engine. Upgrade Spice, or run a trunk build (see below).                   |
| `Unknown GGUF architecture 'kimi-linear'`                                          | A `v2.3.x` or `v2.4.0-rc` runtime, which serves GGUFs with mistral.rs. Same fix.                                   |
| The model never finishes loading, or macOS becomes unresponsive                   | The file does not fit the GPU's share of memory. Choose a smaller file from the [Memory](#memory) table.           |
| `the prompt is N tokens, and the model's context holds 8192`                      | The conversation outgrew the context. Start a new chat.                                                            |

## Using a trunk build

Until a release includes the llama.cpp GGUF engine, download the latest trunk build of the runtime and point the CLI at it. The CLI's `spice run`, `spice chat` and `spice sql` work unchanged. The download needs the [GitHub CLI](https://cli.github.com) signed in to a GitHub account (`brew install gh`, then `gh auth login`), because Actions artifacts are only served to authenticated users.

```bash
RUN_ID=$(gh run list -R spiceai/spiceai --workflow build_and_release --branch trunk --status success --limit 1 --json databaseId -q '.[0].databaseId')
gh run download "$RUN_ID" -R spiceai/spiceai -n spiced_metal_darwin_aarch64 -D spiced-trunk
tar -xzf spiced-trunk/spiced_metal_darwin_aarch64.tar.gz -C spiced-trunk && chmod +x spiced-trunk/spiced
SPICED_PATH="$PWD/spiced-trunk/spiced" spice run
```

## Clean up

Stop Spice with `Ctrl+C`. The model stays in the Hugging Face cache for the next start; remove it with:

```bash
rm -rf ~/.cache/huggingface/hub/models--bartowski--moonshotai_Kimi-Linear-48B-A3B-Instruct-GGUF
```

## Learn more

- [Local GGUF models in Spice](https://spiceai.org/docs/components/models#local-gguf-models): engine placement, draft heads, structured output, supported architectures.
- [Hugging Face models](https://spiceai.org/docs/components/models/huggingface).
- [Kimi-Linear-48B-A3B-Instruct](https://huggingface.co/moonshotai/Kimi-Linear-48B-A3B-Instruct) and the [Kimi Linear paper](https://huggingface.co/papers/2510.26692).
