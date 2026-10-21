# Decisions on Unstructured Data with Typed Questions

Works with `v2.4.0-rc.2+`

This recipe uses `POST /v1/decisions` to make decisions about a support message with [TypeSafe Jev](https://typesafe.ai). One request checks whether the message is urgent, selects a support team, and scores the tone of the message.

The endpoint is compatible with [OpenAI's Decisions API](https://developers.openai.com/api/docs/guides/decisions). A request has an `input` (a string, or user messages with text parts) and an array of `questions`. Each question has one of three types:

| Type | Use | Answer |
| --- | --- | --- |
| `predicate` | Ask how likely a statement is true. | `probability`: the probability of yes, from 0 to 1. |
| `choice` | Select from a list of `choices`. | `choice`: the most probable option, with each option's `probabilities` and a `confidence`. |
| `score` | Place the input on 2–10 ordered `levels`, lowest first. | `score`: the probability-weighted 0-based level index, with each level's `probabilities` and a `confidence`. |

Any model in the Spicepod can answer. Jev is a TypeSafe decision model with calibrated probabilities. The second example sends the same questions to OpenAI GPT-6 Luna, which answers through OpenAI's native Decisions API; its probabilities are the model's estimates. See [Decisions with GPT-6 Luna](#decisions-with-gpt-6-luna).

## Prerequisites

- Spice v2.4.0-rc.2 or later with model support installed ([Getting Started](https://spiceai.org/docs/getting-started)).
- A TypeSafe API key and an OpenAI API key.
- `curl` installed.

## How to run

Clone the cookbook repository and navigate to the `decisions` directory:

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/decisions
```

Copy the example environment file:

```console
cp .env.example .env
```

Set both API keys in `.env`:

```dotenv
TYPESAFE_API_KEY=your_typesafe_api_key
OPENAI_API_KEY=your_openai_api_key
```

The included `spicepod.yaml` defines both models:

```yaml
version: v1
kind: Spicepod
name: decisions

models:
  - from: typesafe:jev
    name: jev
    params:
      typesafe_api_key: ${secrets:TYPESAFE_API_KEY}

  - from: openai:gpt-6-luna
    name: gpt-6-luna
    params:
      openai_api_key: ${secrets:OPENAI_API_KEY}
```

Start the Spice runtime:

```console
spice run
```

Keep this terminal open. Once both models are ready, open a second terminal to send the request below.

## Decisions about a support message with Jev

The request's `model` is the name defined in the Spicepod. The question names (`is_urgent`, `team`, and `tone`) are optional identifiers you choose; each answer echoes its question's `name`.

```console
curl --fail-with-body -sS http://localhost:8090/v1/decisions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "jev",
    "input": "Help! My payouts have been failing for 3 days.",
    "questions": [
      {
        "type": "predicate",
        "name": "is_urgent",
        "instructions": "Does this convey urgency?"
      },
      {
        "type": "choice",
        "name": "team",
        "instructions": "Which team should handle this?",
        "choices": [
          { "value": "billing", "description": "Payments and payouts" },
          { "value": "technical", "description": "Bugs and outages" }
        ]
      },
      {
        "type": "score",
        "name": "tone",
        "instructions": "How frustrated is the customer?",
        "levels": [{ "label": "Calm" }, { "label": "Concerned" }, { "label": "Frustrated" }]
      }
    ]
  }'
```

A successful request returns HTTP 200 with one entry in `answers` for each question, in question order. The following response is from Spice v2.4.0-rc.2. Numerical values vary between runs and model versions:

```json
{
  "model": "jev",
  "answers": [
    { "type": "predicate", "name": "is_urgent", "probability": 0.95 },
    {
      "type": "choice",
      "name": "team",
      "choice": "billing",
      "probabilities": [
        { "value": "billing", "probability": 0.98 },
        { "value": "technical", "probability": 0.02 }
      ],
      "confidence": 0.96
    },
    {
      "type": "score",
      "name": "tone",
      "score": 1.95,
      "probabilities": [
        { "value": 0, "label": "Calm", "probability": 0.0 },
        { "value": 1, "label": "Concerned", "probability": 0.05 },
        { "value": 2, "label": "Frustrated", "probability": 0.95 }
      ],
      "confidence": 0.93
    }
  ],
  "usage": {
    "input_tokens": 378,
    "input_tokens_details": { "cached_tokens": 0, "cache_write_tokens": 0 },
    "output_tokens": 70,
    "output_tokens_details": { "reasoning_tokens": 0 },
    "total_tokens": 448
  }
}
```

In this response:

- `model` is the model name from the request.
- `is_urgent.probability` is the probability that the message conveys urgency.
- `team.choice` is `billing`, the option with the highest probability.
- `tone.score` is the probability-weighted average of the 0-based level indexes: `0 × 0.0 + 1 × 0.05 + 2 × 0.95 = 1.95`. Each entry in `probabilities` gives the level's index (`value`) and `label`.
- `confidence` shows how concentrated a choice or score distribution is: 0 for uniform and 1 for certain.
- `usage` shows the tokens the request used. It is omitted when the model does not report token counts.

## Decisions with GPT-6 Luna

GPT-6 Luna is an OpenAI decision model, and the same Spicepod already loads it. Spice sends its decision requests to OpenAI's native Decisions API. Send the same questions with `"model": "gpt-6-luna"`:

```console
curl --fail-with-body -sS http://localhost:8090/v1/decisions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "gpt-6-luna",
    "input": "Help! My payouts have been failing for 3 days.",
    "questions": [
      {
        "type": "predicate",
        "name": "is_urgent",
        "instructions": "Does this convey urgency?"
      },
      {
        "type": "choice",
        "name": "team",
        "instructions": "Which team should handle this?",
        "choices": [
          { "value": "billing", "description": "Payments and payouts" },
          { "value": "technical", "description": "Bugs and outages" }
        ]
      },
      {
        "type": "score",
        "name": "tone",
        "instructions": "How frustrated is the customer?",
        "levels": [{ "label": "Calm" }, { "label": "Concerned" }, { "label": "Frustrated" }]
      }
    ]
  }'
```

The response has the same structure and reports `"model": "gpt-6-luna"`. Its values differ from Jev's. For example, one Spice v2.4.0-rc.2 run returned these `answers`:

```json
[
  { "type": "predicate", "name": "is_urgent", "probability": 0.98 },
  {
    "type": "choice",
    "name": "team",
    "choice": "billing",
    "probabilities": [
      { "value": "billing", "probability": 1.0 },
      { "value": "technical", "probability": 0.0 }
    ],
    "confidence": 1.0
  },
  {
    "type": "score",
    "name": "tone",
    "score": 1.41,
    "probabilities": [
      { "value": 0, "label": "Calm", "probability": 0.0 },
      { "value": 1, "label": "Concerned", "probability": 0.59 },
      { "value": 2, "label": "Frustrated", "probability": 0.41 }
    ],
    "confidence": 0.39
  }
]
```

GPT-6 Luna's probabilities are the model's estimates and are not calibrated. OpenAI recommends that you set decision thresholds from your own labeled examples.

Any other chat model in the Spicepod, such as `openai:gpt-4o-mini`, can also answer `/v1/decisions` requests through chat completions. Its probabilities are also its own estimates.

## Learn More

- [Decisions](https://github.com/spiceai/spiceai/blob/trunk/docs/features/models/decisions.md)
- [TypeSafe model configuration](https://github.com/spiceai/spiceai/blob/trunk/docs/features/models/typesafe.md)
- [OpenAI Decisions API](https://developers.openai.com/api/docs/guides/decisions)
- [OpenAI Models](../models/openai/README.md)
