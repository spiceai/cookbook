# Language Model Evaluations

Spice can be used to both run language models but also to evaluate their performance on specific tasks.

This recipe demonstrates how to measure the performance of a language model, configured entirely in the spice runtime.


## Prerequisites

- Ensure you have the Spice CLI installed. Follow the [Getting Started](https://docs.spiceai.org/getting-started) if you haven't done so.
- Populate `.env`.
  - `SPICE_OPENAI_API_KEY`: A valid OpenAI API key (or equivalent).

## Steps

1. Start spice, and wait for the components to load
```shell
spice run
```

2. Run an evaluation against `my_model`. This will take a moment to complete.
```shell
curl -XPOST "http://localhost:8090/v1/evals/tetris" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "my_model"
  }'
```
```json
[
    {
        "id": "15b8c5351cff98d96db28b8c76ad19dc",
        "created_at": "2024-12-30T06:14:54",
        "dataset": "small_tetris",
        "model": "my_model",
        "status": "Completed",
        "scorers": [
            "match"
        ],
        "metrics": {
            "match/mean": 0.375
        }
    }
]
```

3. Inspect the results
```shell
curlie -XPOST http://localhost:8090/v1/sql \
  --data "SELECT
    json_get_str(json_get_json(input, 1), 'content') as input,
    expected,
    actual
  FROM eval.results
  WHERE run_id='15b8c5351cff98d96db28b8c76ad19dc' AND value=0.0
  LIMIT 5"
```
```json

[
    {
        "input": "Imagine this being a Tetris block:\nx\nx\nxx\nWhen you rotate that block clockwise, it would look like this:\nxxx\nx\nWhen you rotate it one more time it would look like this:\nxx\n x\n x\nYour Task is to rotate it again. \nDo not output any explanation. Only show the resulting rotation.",
        "expected": "```\n  x\nxxx\n```",
        "actual": "  x\nxxx"
    },
    {
        "input": "Imagine this being a Tetris block:\nx\nx\nxx\nWhen you rotate that block counterclockwise, it would look like this:\n  x\nxxx\nWhen you rotate it one more time it would look like this:\nxx\n x\n x\nYour Task is to rotate it again. \nDo not output any explanation. Only show the resulting rotation.",
        "expected": "xx\nxx",
        "actual": "xxx\nx"
    }
    // Omit all for brevity
]
```

4. Update the spicepod with a better model.
```diff
-    from: openai:gpt-4o-mini
+     params:
+       openai_api_key: ${ secrets:SPICE_OPENAI_API_KEY }
+       system_prompt: |
+         You love to play Tetris. You are playing a game of Tetris and you are trying to rotate a block. Here is an example:
+
+         Input:
+         ```
+         Imagine this being a Tetris block:\nx\nx\nxx\nWhen you rotate that block clockwise, it would look like this:\nxxx\nx\nWhen you rotate it one more time it would look like this:\nxx\n x\n x\nYour Task is to rotate it again. \nDo not output any explanation. Only show the resulting rotation."
+         ```
+
+         Expected: "  x\nxxx"
```
5. Restart `spiced` and re-run the evaluation (steps 1 & 2 from above). Result
```json
[
    {
        "id": "8dd8667b06be388b460459e26cc99105",
        "created_at": "2024-12-30T06:24:25",
        "dataset": "small_tetris",
        "model": "my_model",
        "status": "Completed",
        "scorers": [
            "match"
        ],
        "metrics": {
            "match/mean": 0.4375
        }
    }
]
```

A little better.
