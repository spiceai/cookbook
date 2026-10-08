# Evaluate Unstructured Data with Typed Questions

Works with `v2.4.0-rc.1+`

This recipe uses `POST /v1/evaluate` to evaluate a support message with an OpenAI chat model. Any chat model configured in a Spicepod can use the same endpoint without additional evaluation configuration. One request checks whether the message is urgent, selects a support team, and scores its tone against a rubric.

The endpoint accepts a `state` string, object, or array and a map of questions. Each question has one of three types:

| Type | Use | Answer |
| --- | --- | --- |
| `noul` | Ask a yes/no question. | The probability of yes, from 0 to 1. |
| `choice` | Select from named options. | The selected option, each option's probability, and confidence. |
| `score` | Evaluate against an ordered rubric of 2–10 levels. | A probability-weighted score, the rubric legend, each level's probability, and confidence. |

Chat-model probabilities are the model's own estimates and are not calibrated. You can also use [TypeSafe Jev](https://typesafe.ai), a System One evaluation model with calibrated probabilities; see [Using TypeSafe Jev](#using-typesafe-jev).

## Prerequisites

- Spice v2.4.0-rc.1 or later with model support installed ([Getting Started](https://spiceai.org/docs/getting-started)).
- An OpenAI API key.
- `curl` installed.

## How to run

Clone the cookbook repository and navigate to the `evaluate` directory:

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/evaluate
```

Copy the example environment file:

```console
cp .env.example .env
```

Set `OPENAI_API_KEY` in `.env` to your OpenAI API key:

```dotenv
OPENAI_API_KEY=your_openai_api_key
```

The included `spicepod.yaml` defines the model:

```yaml
version: v1
kind: Spicepod
name: evaluate

models:
  - from: openai:gpt-4o-mini
    name: judge
    params:
      openai_api_key: ${secrets:OPENAI_API_KEY}
```

Start the Spice runtime:

```console
spice run
```

Keep this terminal open. Once the model is ready, open a second terminal to send the request below.

## Evaluate a support message

The request's `model` is the name defined in the Spicepod. The question names (`is_urgent`, `team`, and `tone`) are identifiers you choose; the response uses the same names.

```console
curl --fail-with-body -sS http://localhost:8090/v1/evaluate \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "judge",
    "state": "Help! My payouts have been failing for 3 days.",
    "questions": {
      "is_urgent": {
        "type": "noul",
        "instructions": "Does this convey urgency?"
      },
      "team": {
        "type": "choice",
        "instructions": "Which team should handle this?",
        "criteria": {
          "billing": "Payments and payouts",
          "technical": "Bugs and outages"
        }
      },
      "tone": {
        "type": "score",
        "instructions": "How frustrated is the customer?",
        "criteria": ["Calm", "Concerned", "Frustrated"]
      }
    }
  }'
```

A successful request returns HTTP 200 with an `answers` entry for each question. The following response is illustrative; numerical values vary:

```json
{
  "model": "judge",
  "answers": {
    "is_urgent": {
      "type": "noul",
      "noul": 0.9
    },
    "team": {
      "type": "choice",
      "choice": "billing",
      "probabilities": { "billing": 0.8, "technical": 0.2 },
      "confidence": 0.6
    },
    "tone": {
      "type": "score",
      "score": 1.7,
      "legend": { "0": "Calm", "1": "Concerned", "2": "Frustrated" },
      "probabilities": { "0": 0.1, "1": 0.1, "2": 0.8 },
      "confidence": 0.55
    }
  }
}
```

In this example:

- `is_urgent.noul` is the probability that the message conveys urgency.
- `team.choice` selects `billing`, the option with the highest probability.
- `tone.score` is a weighted average of the rubric levels, starting at zero. The example score is `0 × 0.1 + 1 × 0.1 + 2 × 0.8 = 1.7`.
- `confidence` describes how concentrated a choice or score distribution is: 0 for uniform and 1 for certain.

The response may also include `usage` with `input_tokens` and `output_tokens` when the provider reports token counts.

## Using TypeSafe Jev

To use TypeSafe Jev instead of a chat model, replace the `models` section in `spicepod.yaml` with:

```yaml
models:
  - from: typesafe:jev
    name: jev
    params:
      typesafe_api_key: ${secrets:TYPESAFE_API_KEY}
```

Set `TYPESAFE_API_KEY` in `.env` to your TypeSafe API key:

```dotenv
TYPESAFE_API_KEY=your_typesafe_api_key
```

Stop the runtime with `Ctrl+C` and start it again with `spice run`. Send the same evaluation request with `"model": "jev"`. The answer structure is the same, with calibrated probabilities and a provider-reported model version in the response.

Jev uses `/v1/evaluate` and does not support `/v1/chat/completions` or `spice chat`.

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| `curl` cannot connect | Keep `spice run` running and check that the HTTP API is listening on port 8090. |
| HTTP 404 | Check that the request's `model` matches the Spicepod model name and that the model loaded successfully. Use Spice v2.4.0-rc.1 or later for `/v1/evaluate`. |
| HTTP 401 or 403 | Check the API key in `.env` and your provider account's access to the model. Restart Spice after updating the key. |
| HTTP 429 | Wait before retrying and check the provider's request limits. |
| HTTP 500 with a chat model | Read the response body and runtime logs. A chat model that repeatedly returns malformed evaluation answers causes the request to fail. |

## Learn More

- [Evaluate API](https://github.com/spiceai/spiceai/blob/trunk/docs/features/models/evaluate.md)
- [TypeSafe model configuration](https://github.com/spiceai/spiceai/blob/trunk/docs/features/models/typesafe.md)
- [OpenAI Models](../models/openai/README.md)
