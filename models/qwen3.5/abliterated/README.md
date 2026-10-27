# Running Qwen3.5 Locally: Abliterated Variant

Works with `v2.4+` builds that include the [llama.cpp GGUF engine](https://github.com/spiceai/spiceai/pull/7864); see the [base recipe](../README.md#prerequisites).

This directory is the [Qwen3.5 recipe](../README.md) with the model swapped for [huihui-ai/Huihui-Qwen3.5-9B-abliterated](https://huggingface.co/huihui-ai/Huihui-Qwen3.5-9B-abliterated), a version of Qwen3.5-9B with its refusal behavior removed by abliteration, in the Q4_K_M GGUF quantization published by [mradermacher](https://huggingface.co/mradermacher/Huihui-Qwen3.5-9B-abliterated-GGUF) (5.6 GB). It serves the model and its API; it does not load the dataset or enable tools, for the reason in [Why no dataset tools](#why-no-dataset-tools).

Abliteration removes the "refusal direction" from a model's weights, so the model answers requests the base model would decline. huihui-ai describes its method as a proof-of-concept implementation of [refusal removal](https://github.com/Sumandora/remove-refusals-with-transformers). The result has none of the base model's safety training. Use it for research, red-teaming and controlled experiments, add your own moderation before exposing it to users, and review its outputs. huihui-ai's model card carries its own usage warnings and disclaims responsibility for use.

## Spicepod

```yaml
version: v2
kind: Spicepod
name: qwen3.5-abliterated

models:
  - from: huggingface:huggingface.co/mradermacher/Huihui-Qwen3.5-9B-abliterated-GGUF
    name: qwen3.5-abliterated
    files:
      - path: Huihui-Qwen3.5-9B-abliterated.Q4_K_M.gguf
```

## Run

```bash
cd models/qwen3.5/abliterated
spice run
```

```console
2026-10-26T03:06:11.534220Z  INFO runtime::init::model: Loading model [qwen3.5-abliterated] from huggingface:huggingface.co/mradermacher/Huihui-Qwen3.5-9B-abliterated-GGUF...
2026-10-26T03:06:12.064035Z  INFO huggingface_hub::snapshot: Downloading 1 file (5.6 GB) for model 'qwen3.5-abliterated' from Hugging Face repo 'mradermacher/Huihui-Qwen3.5-9B-abliterated-GGUF' at commit 9f646d7 (revision 'main').
...
2026-10-26T03:34:57.217610Z  INFO huggingface_hub::snapshot: Downloaded model 'qwen3.5-abliterated' from Hugging Face repo 'mradermacher/Huihui-Qwen3.5-9B-abliterated-GGUF' in 28 min 45 s.
2026-10-26T03:34:57.748131Z  INFO runtime::init::model: Model [qwen3.5-abliterated] deployed, ready for inferencing
2026-10-26T03:34:57.850555Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

Then, in a second terminal:

```bash
spice chat
```

```console
Using model: qwen3.5-abliterated
chat> In one sentence, what is a lighthouse for?
```

The API serves the model as `qwen3.5-abliterated` at `http://localhost:8090/v1/chat/completions`:

```bash
curl -s http://localhost:8090/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3.5-abliterated",
    "reasoning_effort": "none",
    "messages": [{"role": "user", "content": "Reply with only the integer 1729."}]
  }'
```

Unlike the Unsloth build of Qwen3.5-9B, this GGUF's chat template turns thinking on by default: the same question answered in 4 tokens with `reasoning_effort: none` and in 302 tokens (a 966-character trace in `reasoning_content`) without it. On an M3 Max it decodes about 52 tokens per second.

## Why no dataset tools

This GGUF carries Qwen's stock chat template, which renders a tool call's arguments with `tool_call.arguments|items`. When `tools: auto` is set, Spice primes the conversation with a `list_datasets` call whose arguments are an empty string, and the stock template fails to render it: every request returns HTTP 400 `Failed to render the chat template: invalid operation: cannot convert value into pairs`. Unsloth's templates guard that loop, which is why the base recipe's tools work. A `chat_template` override does not help, because a GGUF's own template takes precedence. The runtime bug is [spiceai/spiceai#15578](https://github.com/spiceai/spiceai/issues/15578); once it is fixed, add the base recipe's `datasets` block and `params: { tools: auto }` to this spicepod.

## Memory

The mradermacher repository holds the same quantization ladder as the base model: `Q4_K_M` (5.6 GB, the default), `Q6_K` (7.4 GB) and `Q8_0` (9.5 GB) for 16 GB and 24 GB Macs. For larger Macs, [mradermacher/Huihui-Qwen3.5-35B-A3B-abliterated-GGUF](https://huggingface.co/mradermacher/Huihui-Qwen3.5-35B-A3B-abliterated-GGUF) (`Q4_K_M`, 21.2 GB) is the abliterated Qwen3.5-35B-A3B for a 36 GB MacBook Pro, with the same template caveat.

## Clean up

```bash
rm -rf ~/.cache/huggingface/hub/models--mradermacher--Huihui-Qwen3.5-9B-abliterated-GGUF
```
