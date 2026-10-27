# Running Qwen3.6 Locally: Abliterated Variant

Works with `v2.4+` builds that include the [llama.cpp GGUF engine](https://github.com/spiceai/spiceai/pull/7864); see the [base recipe](../README.md#prerequisites).

This directory is the [Qwen3.6 recipe](../README.md) with the model swapped for [huihui-ai/Huihui-Qwen3.6-35B-A3B-abliterated](https://huggingface.co/huihui-ai/Huihui-Qwen3.6-35B-A3B-abliterated-MTP-GGUF), huihui-ai's own Q4_K GGUF (21.7 GB) of Qwen3.6-35B-A3B with its refusal behavior removed by abliteration. The file keeps the model's multi-token-prediction (NextN) layer, so Spice drafts with it automatically. It serves the model and its API; it does not load the dataset or enable tools, for the reason in [Why no dataset tools](#why-no-dataset-tools).

Abliteration removes the "refusal direction" from a model's weights, so the model answers requests the base model would decline. huihui-ai describes its method as a proof-of-concept implementation of [refusal removal](https://github.com/Sumandora/remove-refusals-with-transformers). The result has none of the base model's safety training. Use it for research, red-teaming and controlled experiments, add your own moderation before exposing it to users, and review its outputs. huihui-ai's model card carries its own usage warnings and disclaims responsibility for use.

## Spicepod

```yaml
version: v2
kind: Spicepod
name: qwen3.6-abliterated

models:
  - from: huggingface:huggingface.co/huihui-ai/Huihui-Qwen3.6-35B-A3B-abliterated-MTP-GGUF
    name: qwen3.6-abliterated
    files:
      - path: Huihui-Qwen3.6-35B-A3B-abliterated-ggml-model-Q4_K.gguf
```

## Run

```bash
cd models/qwen3.6/abliterated
spice run
```

Wait for `Model [qwen3.6-abliterated] deployed, ready for inferencing`, then in a second terminal:

```bash
spice chat
```

The API serves the model as `qwen3.6-abliterated` at `http://localhost:8090/v1/chat/completions`, with the same `reasoning_effort` behavior as the base model (`none` for a direct answer).

## Why no dataset tools

This GGUF carries Qwen's stock chat template, which renders a tool call's arguments with `tool_call.arguments|items`. When `tools: auto` is set, Spice primes the conversation with a `list_datasets` call whose arguments are an empty string, and the stock template fails to render it: every request returns HTTP 400 `Failed to render the chat template: invalid operation: cannot convert value into pairs`. Unsloth's templates guard that loop, which is why the base recipe's tools work. A `chat_template` override does not help, because a GGUF's own template takes precedence. The runtime bug is [spiceai/spiceai#15578](https://github.com/spiceai/spiceai/issues/15578); once it is fixed, add the base recipe's `datasets` block and `params: { tools: auto }` to this spicepod.

## Memory

The repository holds `Q2_K` (13.2 GB, 16 GB Macs), `Q3_K` (17.2 GB, 24 GB to 32 GB), `Q4_K` (21.7 GB, the default, 36 GB and up), `Q5_K` (25.3 GB), `Q6_K` (29.2 GB, 48 GB and up) and `Q8_0` (37.8 GB, 64 GB and up), all with the NextN layer. For the dense 27B model, [huihui-ai/Huihui-Qwen3.6-27B-abliterated-MTP-GGUF](https://huggingface.co/huihui-ai/Huihui-Qwen3.6-27B-abliterated-MTP-GGUF) has the same ladder (`Q4_K`, 16.8 GB).

## Clean up

```bash
rm -rf ~/.cache/huggingface/hub/models--huihui-ai--Huihui-Qwen3.6-35B-A3B-abliterated-MTP-GGUF
```
