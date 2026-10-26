# Running DeepSeek V4 Locally: Abliterated Variant

Works with `v2.4+` builds that include the [llama.cpp GGUF engine](https://github.com/spiceai/spiceai/pull/7864); see the [base recipe](../README.md#prerequisites).

This directory is the [DeepSeek V4 recipe](../README.md) with the model swapped for [huihui-ai/Huihui-DeepSeek-V4-Flash-0731-abliterated-GGUF](https://huggingface.co/huihui-ai/Huihui-DeepSeek-V4-Flash-0731-abliterated-GGUF), huihui-ai's 2-bit GGUF (`DeepSeek-V4-Flash-Q2-0731.gguf`, 86.7 GB, one file) of DeepSeek-V4-Flash-0731 with its refusal behavior removed by abliteration. It needs the same 128 GB Mac as the base recipe. Everything else is unchanged.

Abliteration removes the "refusal direction" from a model's weights, so the model answers requests the base model would decline. huihui-ai describes its method as a proof-of-concept implementation of [refusal removal](https://github.com/Sumandora/remove-refusals-with-transformers) that left the expert modules untouched. The result has none of the base model's safety training. Use it for research, red-teaming and controlled experiments, add your own moderation before exposing it to users, and review its outputs. huihui-ai's model card carries its own usage warnings and disclaims responsibility for use.

## Run

```bash
cd models/deepseek-v4/abliterated
spice run
```

Wait for `Model [deepseek-v4-flash-abliterated] deployed, ready for inferencing`, then in a second terminal:

```bash
spice chat
```

The API serves the model as `deepseek-v4-flash-abliterated` at `http://localhost:8090/v1/chat/completions`, with the same reasoning behavior as the base model. Run on the same DGX Spark and engine build as the base recipe's Step 2 (the file named by path after a checksum), it loaded in 72 seconds with 87 GB resident, answered "Reply with only the integer 1729." in 2 tokens by default and with `reasoning_effort: none`, gave a 22-token answer with a short trace at `low`, `medium` and `high`, and decoded at about 19 tokens per second.

## Memory

The repository holds two text builds: `DeepSeek-V4-Flash-Q2-0731.gguf` (86.7 GB, the default) and `DeepSeek-V4-Flash-Q2_K-0731.gguf` (97.6 GB), both for a 128 GB Mac, and a 4-bit `MXFP4` build (156 GB) for 192 GB and larger machines. Its `dspark-*.gguf` files are DeepSeek's DSpark speculative-decoding head for other engines; Spice reads only draft heads named `mtp-*.gguf`, so leave them out.

[orcarouter/DeepSeek-V4-Flash-Vision-Uncensored-GGUF](https://huggingface.co/orcarouter/DeepSeek-V4-Flash-Vision-Uncensored-GGUF) is a measured and documented abliteration of a different checkpoint, DeepSeek-V4-Flash-Vision-Exp (August 2026), packaged without quantization as a 156 GB MXFP4 set; it is a build for a 192 GB or larger Mac, and a gated repository: accept the model's license on its Hugging Face page while signed in, and pass a read token as `hf_token: ${ secrets:HF_TOKEN }`.

## Clean up

```bash
rm -rf ~/.cache/huggingface/hub/models--huihui-ai--Huihui-DeepSeek-V4-Flash-0731-abliterated-GGUF
```
