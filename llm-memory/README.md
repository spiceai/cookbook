# LLM Memory Recipe

Spice can provide persistent memory capabilities for language models, allowing them to remember important details from conversations across sessions.

## Requirements

- [Spice CLI](https://docs.spiceai.org/getting-started) installed.
- The following environment variables set:
  - `SPICE_OPENAI_API_KEY`

## Using LLM Memory

**Step 1.** Run Spice runtime

```shell
spice run
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

### Using Memory Tools Directly

**Step 1.** Store a memory directly

```shell
curl -XPOST http://127.0.0.1:8090/v1/tool/store_memory -d '{"thoughts": ["Alice deserves a promotion"]}'
```

**Step 2.** Load stored memories

```shell
curl -XPOST http://127.0.0.1:8090/v1/tool/load_memory -d '{"last": "10m"}'
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
