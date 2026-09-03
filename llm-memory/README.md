# LLM Memory: Persistent Memory for Language Models with Spice

Works with `v1.0+`

Spice provides persistent memory capabilities for language models, enabling them to retain key information from conversations across sessions. This feature supports building more context-aware and intelligent applications by maintaining memory continuity.

[![Watch the Spice.ai LLM memory demo](https://img.youtube.com/vi/NikPkLZJy7w/hqdefault.jpg)](https://www.youtube.com/embed/NikPkLZJy7w)

## Prerequisites

Ensure the following before starting:

- [Spice CLI](https://docs.spiceai.org/getting-started) installed.
- Working directory is `llm-memory`:
  ```bash
  git clone https://github.com/spiceai/cookbook.git
  cd cookbook/llm-memory
  ```
- The following environment variables set in `.env`:
  - `SPICE_OPENAI_API_KEY`

## Using LLM Memory

**Step 1.** Run Spice runtime

```shell
spice run
```

```shell
2025/01/27 11:29:49 INFO Checking for latest Spice runtime release...
2025/01/27 11:29:50 INFO Spice.ai runtime starting...
2025-01-27T19:29:50.856594Z  INFO runtime::init::dataset: Dataset llm_memory initializing...
2025-01-27T19:29:50.857758Z  INFO runtime::init::model: Loading model [chat_model] from openai:gpt-4o...
2025-01-27T19:29:50.858938Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2025-01-27T19:29:50.859210Z  INFO runtime::init::dataset: Dataset llm_memory registered (memory:store).
2025-01-27T19:29:50.865516Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2025-01-27T19:29:51.058851Z  INFO runtime::init::caching: Initialized sql results cache; max size: 128.00 MiB, item ttl: 1s, hashing algorithm: XXH3, encoding: none
2025-01-27T19:29:52.248966Z  INFO runtime::init::model: Model [chat_model] deployed, ready for inferencing
```

**Step 3.** Start a chat session

```shell
spice chat
```

**Step 4.** Interact with the model

```shell
>>> spice chat

chat> Hi, my name is Alice and I work as a software engineer
Hi Alice! It's nice to meet you. How can I assist you today?

chat>  I live in Seattle. Tell me a joke about it
Sure, here's a Seattle-themed joke for you:

Why don't Seattle folks get lost in the woods?

Because they always follow the trail of coffee cups back home! ☕🌲

Hope that gives you a chuckle! Let me know if there's anything else you'd like to know or chat about.
```

Press Ctrl-C to exit the chat.

**Step 5.** Check stored memories

```shell
spice sql
```

Then:

```sql
SELECT id, value FROM llm_memory;
```

Output:

```shell
+--------------------------------------+-------------------------------------+
| id                                   | value                               |
+--------------------------------------+-------------------------------------+
| 019319e4-ca14-7a12-a91a-f2c73528d304 | User's name is Alice                |
| 019319e4-ca14-7a12-a91a-f2d52fb70fba | Alice is a software engineer        |
| 019319e4-ca14-7a12-a91a-f2e2656ff222 | Alice lives in Seattle              |
+--------------------------------------+-------------------------------------+
```

**Step 6.** Re-run spice chat and ask "Who am I?"

```shell
spice chat
```

Then:

```shell
chat> Who am I?
You are Alice, and you work as a software engineer.
```

### Using Memory Tools Directly

> **Note (Spice `v2.0+`):** Tool-invocation endpoints (`/v1/tools/*`) require an authentication provider to be configured on the runtime. Without `runtime.auth` these routes return `401 Unauthorized`. To call them, add an API-key provider to `spicepod.yml`:
>
> ```yaml
> runtime:
>   auth:
>     api-key:
>       enabled: true
>       keys:
>         - ${ secrets:SPICE_API_KEY }
> ```
>
> and pass the key as an `x-api-key` header (shown below). Enabling `runtime.auth` applies to all endpoints, so the earlier `spice chat` step then also needs credentials (`spice chat --api-key <key>`). See the [api_key recipe](https://github.com/spiceai/cookbook/tree/trunk/api_key) for the full flow.

**Step 1.** Store a memory directly

```shell
curl -XPOST http://127.0.0.1:8090/v1/tools/store_memory -H "x-api-key: $SPICE_API_KEY" -d '{"thoughts": ["Alice deserves a promotion"]}'
```

**Step 2.** Load stored memories

```shell
curl -XPOST http://127.0.0.1:8090/v1/tools/load_memory -H "x-api-key: $SPICE_API_KEY" -d '{"last": "10m"}'
```

Output:

```json
[
  "Users name is Alice",
  "Alice is a software engineer",
  "Alice lives in Seattle",
  "Alice thinks she deserves a promotion"
]
```
