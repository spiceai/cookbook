# Running GLM Locally: Abliterated Variant

Works with `v2.4+` builds that include the [llama.cpp GGUF engine](https://github.com/spiceai/spiceai/pull/7864); see the [base recipe](../README.md#prerequisites).

This directory is the [GLM recipe](../README.md) with the model swapped for [huihui-ai/Huihui-GLM-4.7-Flash-abliterated](https://huggingface.co/huihui-ai/Huihui-GLM-4.7-Flash-abliterated), a version of GLM-4.7-Flash with its refusal behavior removed by abliteration, in the importance-matrix `i1-Q4_K_M` GGUF (18.1 GB) published by [mradermacher](https://huggingface.co/mradermacher/Huihui-GLM-4.7-Flash-abliterated-i1-GGUF). Everything else is unchanged.

Abliteration removes the "refusal direction" from a model's weights, so the model answers requests the base model would decline. huihui-ai describes its method as a proof-of-concept implementation of [refusal removal](https://github.com/Sumandora/remove-refusals-with-transformers). The result has none of the base model's safety training. Use it for research, red-teaming and controlled experiments, add your own moderation before exposing it to users, and review its outputs. huihui-ai's model card carries its own usage warnings and disclaims responsibility for use.

## Run

```bash
cd models/glm/abliterated
spice run
```

Wait for `Model [glm-4.7-flash-abliterated] deployed, ready for inferencing`, then in a second terminal:

```bash
spice chat
```

The API serves the model as `glm-4.7-flash-abliterated` at `http://localhost:8090/v1/chat/completions`, with the same reasoning behavior as the base model.

## Memory

The mradermacher repository holds `i1-IQ3_M` (13.2 GB, 24 GB Macs), `i1-Q4_K_M` (18.1 GB, the default, 32 GB and up), `i1-Q5_K_M` (21.3 GB, 36 GB and up) and `i1-Q6_K` (24.6 GB, 48 GB and up), and the companion [non-imatrix repository](https://huggingface.co/mradermacher/Huihui-GLM-4.7-Flash-abliterated-GGUF) adds `Q8_0` (31.8 GB, 48 GB and up). These follow the GPU budget described in the base recipe's [Memory](../README.md#memory) section; a 16 GB Mac's 10.7 GiB budget leaves no room for any of them.

## Abliterated GLM-5.3-Flash on a 128 GB MacBook Pro

Two abliterated builds of GLM-5.3-Flash exist. Both need the memory described in the base recipe's [GLM-5.3-Flash section](../README.md#glm-53-flash-on-a-128-gb-macbook-pro).

[huihui-ai/Huihui-GLM-5.3-Flash-abliterated-GGUF](https://huggingface.co/huihui-ai/Huihui-GLM-5.3-Flash-abliterated-GGUF) is Unsloth's quantization ladder with the ablated layers (15 to 35) rewritten in the first shard, so its `UD-IQ2_XXS` build is the same 101.8 GB as the base model's and fits a 128 GB Mac:

```yaml
models:
  - from: huggingface:huggingface.co/huihui-ai/Huihui-GLM-5.3-Flash-abliterated-GGUF
    name: glm-5.3-flash-abliterated
    files:
      - path: UD-IQ2_XXS/GLM-5.3-Flash-UD-IQ2_XXS-00001-of-00004.gguf
      - path: UD-IQ2_XXS/GLM-5.3-Flash-UD-IQ2_XXS-00002-of-00004.gguf
      - path: UD-IQ2_XXS/GLM-5.3-Flash-UD-IQ2_XXS-00003-of-00004.gguf
      - path: UD-IQ2_XXS/GLM-5.3-Flash-UD-IQ2_XXS-00004-of-00004.gguf
    params:
      hf_reasoning_effort: low
```

[orcarouter/GLM-5.3-Flash-Uncensored-GGUF](https://huggingface.co/orcarouter/GLM-5.3-Flash-Uncensored-GGUF) documents its abliteration with measurements (harmful-prompt refusal from about 89% to the low teens, 0% over-refusal, and per-quant perplexity and top-1 agreement), and drops the NextN layer, so it decodes without drafting. Its smallest build, `Q2_K`, is 116.9 GB in three shards, which exceeds the 107 GiB GPU budget of a 128 GB Mac; it is a build for a 192 GB or larger Mac, or for a 128 GB Mac after raising the GPU memory limit with `sudo sysctl iogpu.wired_limit_mb=<MB>` (the setting resets on reboot, and leaves macOS with what remains). The repository is gated: sign in to Hugging Face, accept the model's license on its page, and add `hf_token: ${ secrets:HF_TOKEN }` to `params`, with a read token as `HF_TOKEN` in `.env`.

```yaml
models:
  - from: huggingface:huggingface.co/orcarouter/GLM-5.3-Flash-Uncensored-GGUF
    name: glm-5.3-flash-uncensored
    files:
      - path: Q2_K/GLM-5.3-Flash-Uncensored-Q2_K-00001-of-00003.gguf
      - path: Q2_K/GLM-5.3-Flash-Uncensored-Q2_K-00002-of-00003.gguf
      - path: Q2_K/GLM-5.3-Flash-Uncensored-Q2_K-00003-of-00003.gguf
    params:
      hf_token: ${ secrets:HF_TOKEN }
      hf_reasoning_effort: low
```

## Abliterated GLM-5.2

[huihui-ai/Huihui-GLM-5.2-abliterated-GGUF](https://huggingface.co/huihui-ai/Huihui-GLM-5.2-abliterated-GGUF) is the abliterated GLM-5.2 (753B). Its smallest build, `UD-IQ1_S_MXFP4`, is 216 GB in six shards and its `UD-IQ1_M` 231 GB, so like the base model it is for a 256 GB or larger Mac Studio, not a MacBook Pro. The spicepod shape is the same: list the shards in `files`.

## Clean up

```bash
rm -rf ~/.cache/huggingface/hub/models--mradermacher--Huihui-GLM-4.7-Flash-abliterated-i1-GGUF
```
