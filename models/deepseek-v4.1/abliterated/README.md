# Running DeepSeek V4.1 Locally: Abliterated Variant

Works with `v2.4+` builds that include the [llama.cpp GGUF engine](https://github.com/spiceai/spiceai/pull/7864) once its llama.cpp supports the `deepseek41` architecture; see the base recipe's [Runtime support](../README.md#runtime-support).

This directory is the [DeepSeek V4.1 recipe](../README.md) with the model swapped for [orcarouter/DeepSeek-V4.1-Flash-1017-abliterated-GGUF](https://huggingface.co/orcarouter/DeepSeek-V4.1-Flash-1017-abliterated-GGUF), orcarouter's abliteration of DeepSeek-V4.1-Flash-1017. The default is its `Mix-256G` build: 346.5 GB in seven shards, of which 236 GB of weights sit in GPU memory and the 110.6 GB Engram table is read from disk, for a 256 GB or larger Mac Studio. Everything else is unchanged.

Abliteration orthogonalizes the "refusal direction" out of a model's weights, so the model answers requests the base model would decline. orcarouter's model card reports, for the unquantized checkpoint, harmful-prompt refusal falling from 87% to 7%, over-refusal of benign prompts from 7% to 0.6%, and MMLU unchanged at about 0.91, and for `Mix-256G` a 93.7% next-token agreement with the original. The result has none of the base model's safety training. Use it for research, red-teaming and controlled experiments, add your own moderation before exposing it to users, and review its outputs. The model card carries its own disclaimer.

## Prerequisites

The repository is gated: orcarouter asks you to accept the model's license on Hugging Face before it serves the files. Sign in to Hugging Face, open [the model page](https://huggingface.co/orcarouter/DeepSeek-V4.1-Flash-1017-abliterated-GGUF), accept the license, create a [read token](https://huggingface.co/settings/tokens), and put the token in `.env`. Without this, the download fails with HTTP 401 or 403.

```bash
cd models/deepseek-v4.1/abliterated
cp .env.example .env   # then edit HF_TOKEN
```

The spicepod reads it as `${ secrets:HF_TOKEN }`:

```yaml
models:
  - from: huggingface:huggingface.co/orcarouter/DeepSeek-V4.1-Flash-1017-abliterated-GGUF
    name: deepseek-v4.1-flash-abliterated
    files:
      - path: Mix-256G/DeepSeek-V4.1-Flash-1017-abliterated-Mix-256G-00001-of-00007.gguf
      - path: Mix-256G/DeepSeek-V4.1-Flash-1017-abliterated-Mix-256G-00002-of-00007.gguf
      - path: Mix-256G/DeepSeek-V4.1-Flash-1017-abliterated-Mix-256G-00003-of-00007.gguf
      - path: Mix-256G/DeepSeek-V4.1-Flash-1017-abliterated-Mix-256G-00004-of-00007.gguf
      - path: Mix-256G/DeepSeek-V4.1-Flash-1017-abliterated-Mix-256G-00005-of-00007.gguf
      - path: Mix-256G/DeepSeek-V4.1-Flash-1017-abliterated-Mix-256G-00006-of-00007.gguf
      - path: Mix-256G/DeepSeek-V4.1-Flash-1017-abliterated-Mix-256G-00007-of-00007.gguf
    params:
      hf_token: ${ secrets:HF_TOKEN }
```

## Run

```bash
spice run
```

Wait for `Model [deepseek-v4.1-flash-abliterated] deployed, ready for inferencing`, then in a second terminal:

```bash
spice chat
```

The API serves the model as `deepseek-v4.1-flash-abliterated` at `http://localhost:8090/v1/chat/completions`. The model card recommends a system prompt, since the model sometimes misnames itself while thinking.

## Memory

The repository also holds `Mix-128G` (225 GB in five shards, 114 GB of weights in memory). orcarouter built it for a 128 GB machine, but its card calls it heavily degraded (78.5% next-token agreement, perplexity up 55%) and "not a substitute" for `Mix-256G`; on a 128 GB Mac its 114 GB of weights also leave almost nothing of the 107 GiB GPU budget for the KV cache. The builds are text-only: the vision projector and the DSpark speculative head were left out.

## Clean up

```bash
rm -rf ~/.cache/huggingface/hub/models--orcarouter--DeepSeek-V4.1-Flash-1017-abliterated-GGUF
```
