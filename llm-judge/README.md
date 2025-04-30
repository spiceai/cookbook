# LLM as a Judge

Spice can be used to run language models but also to evaluate their performance on specific tasks. Sometimes it's useful to use another language model to judge the performance of former. This is often called an [LLM judge](https://spiceai.org/docs/features/large-language-models/evals#llm-judge).

This recipe demonstrates how to evaluate a language model in Spice, and how to use an LLM judge to evaluate their performance.


## Prerequisites

- Ensure you have the Spice CLI installed. Follow the [Getting Started](https://docs.spiceai.org/getting-started) if you haven't done so.
- Populate `.env`.
  - `SPICE_OPENAI_API_KEY`: A valid OpenAI API key (or equivalent).
