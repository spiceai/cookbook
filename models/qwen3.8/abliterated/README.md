# Running Qwen3.8 Locally: Abliterated Variant

Works with `v2.4+` builds that include the [llama.cpp GGUF engine](https://github.com/spiceai/spiceai/pull/7864); see the [base recipe](../README.md#prerequisites).

This directory is the [Qwen3.8 recipe](../README.md) with the model swapped for [orcarouter/Qwen3.8-27B-Uncensored-GGUF](https://huggingface.co/orcarouter/Qwen3.8-27B-Uncensored-GGUF), orcarouter's Q4_K_M quantization (16.8 GB) of Qwen3.8-27B with its refusal behavior removed by abliteration. The file embeds the model's multi-token-prediction head, so Spice drafts with it without a separate `mtp-` file. Everything else, the dataset, the tools and the API, is unchanged.

Abliteration orthogonalizes the "refusal direction" out of a model's weights, so the model answers requests the base model would decline. orcarouter's model card reports the effect on the unquantized build: refusal on harmful-prompt benchmarks falls from 64–99% to 0–6%, over-refusal of benign prompts from 5.6% to 0.4%, and MMLU moves from 84.3% to 84.7%. The result has none of the base model's safety training. Use it for research, red-teaming and controlled experiments, add your own moderation before exposing it to users, and review its outputs. The model card carries its own disclaimer. [huihui-ai/Huihui-Qwen3.8-27B-abliterated-GGUF](https://huggingface.co/huihui-ai/Huihui-Qwen3.8-27B-abliterated-GGUF) (`UD-Q4_K_XL`, 17.4 GB, no token needed) is an alternative with the same spicepod shape.

## Prerequisites

The repository is gated: orcarouter asks you to accept the model's license on Hugging Face before it serves the files. Sign in to Hugging Face, open [the model page](https://huggingface.co/orcarouter/Qwen3.8-27B-Uncensored-GGUF), accept the license, create a [read token](https://huggingface.co/settings/tokens), and put the token in `.env`. Without this, the download fails with HTTP 401 or 403.

```bash
cd models/qwen3.8/abliterated
cp .env.example .env   # then edit HF_TOKEN
```

The spicepod reads it as `${ secrets:HF_TOKEN }`:

```yaml
models:
  - from: huggingface:huggingface.co/orcarouter/Qwen3.8-27B-Uncensored-GGUF
    name: qwen3.8-abliterated
    files:
      - path: Qwen3.8-27B-Uncensored-Q4_K_M.gguf
    params:
      hf_token: ${ secrets:HF_TOKEN }
      tools: auto
```

## Run

```bash
spice run
```

Wait for `Model [qwen3.8-abliterated] deployed, ready for inferencing`, then in a second terminal:

```bash
spice chat
```

```console
Using model: qwen3.8-abliterated
chat> How many rows are in the taxi_trips dataset?
```

The API serves the model as `qwen3.8-abliterated` at `http://localhost:8090/v1/chat/completions`, with the same `reasoning_effort` levels as the base model.

## Memory

orcarouter's ladder runs from `IQ2_XXS` (8.9 GB) through `IQ4_XS` (15.3 GB, the card's low-bit pick), `Q4_K_M` (16.8 GB, the default), `Q6_K` (22.4 GB) to `Q8_0` (29.0 GB). Pick by the table in the [base recipe](../README.md#memory).

## Clean up

```bash
rm -rf ~/.cache/huggingface/hub/models--orcarouter--Qwen3.8-27B-Uncensored-GGUF
```
