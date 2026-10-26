# Running Kimi Locally: Abliterated Variant

Works with `v2.4+` builds that include the [llama.cpp GGUF engine](https://github.com/spiceai/spiceai/pull/7864); see the [base recipe](../README.md#prerequisites).

This directory is the [Kimi recipe](../README.md) with the model swapped for [huihui-ai/Huihui-Kimi-Linear-48B-A3B-Instruct-abliterated](https://huggingface.co/huihui-ai/Huihui-Kimi-Linear-48B-A3B-Instruct-abliterated), a version of Kimi-Linear-48B-A3B-Instruct with its refusal behavior removed by abliteration, in the importance-matrix `i1-IQ3_M` GGUF (21.5 GB) published by [mradermacher](https://huggingface.co/mradermacher/Huihui-Kimi-Linear-48B-A3B-Instruct-abliterated-i1-GGUF). Everything else is unchanged.

Abliteration removes the "refusal direction" from a model's weights, so the model answers requests the base model would decline. huihui-ai describes its method as a proof-of-concept implementation of [refusal removal](https://github.com/Sumandora/remove-refusals-with-transformers). The result has none of the base model's safety training. Use it for research, red-teaming and controlled experiments, add your own moderation before exposing it to users, and review its outputs. huihui-ai's model card carries its own usage warnings and disclaims responsibility for use.

## Run

```bash
cd models/kimi/abliterated
spice run
```

Wait for `Model [kimi-linear-abliterated] deployed, ready for inferencing`, then in a second terminal:

```bash
spice chat
```

The API serves the model as `kimi-linear-abliterated` at `http://localhost:8090/v1/chat/completions`.

## Memory

The mradermacher repository holds `i1-IQ2_M` (16.1 GB, 24 GB Macs), `i1-IQ3_XXS` (19.0 GB, 32 GB), `i1-IQ3_M` (21.5 GB, the default, 36 GB and up), `i1-IQ4_XS` (26.3 GB) and `i1-Q4_K_M` (29.7 GB, 48 GB and up), and `i1-Q6_K` (40.4 GB, 64 GB and up).

## Clean up

```bash
rm -rf ~/.cache/huggingface/hub/models--mradermacher--Huihui-Kimi-Linear-48B-A3B-Instruct-abliterated-i1-GGUF
```
