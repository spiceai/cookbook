# Searching GitHub Files

This recipe demonstrates how to create embeddings for GitHub files and perform vector-based searches.

[![Watch the Spice.ai vector search over GitHub files demo](https://img.youtube.com/vi/5y26MveEJ8c/hqdefault.jpg)](https://www.youtube.com/embed/5y26MveEJ8c)

## Prerequisites

- Ensure you have the Spice CLI installed. Follow the [Getting Started](https://docs.spiceai.org/getting-started) if you haven't done so.
- Populate `.env` in the `cookbook/search_github_files` directory.
  - `GITHUB_TOKEN`: With a [personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-personal-access-token-classic).
  - `SPICE_OPENAI_API_KEY`: A valid OpenAI API key (or equivalent).

## SQL Search

1. Start spice runtime:

```shell
git clone https://github.com/spiceai/cookbook # Skip if already cloned
cd cookbook/search_github_files
spice run
```

2. Execute a Basic SQL Query to perform keyword searches within your dataset:

```shell
spice sql
```

Then:

```sql
SELECT path
FROM spiceai.files
WHERE
    LOWER(content) LIKE '%errors%'
    AND NOT contains(path, 'docs/release_notes');
```

Result:

```shell
+------------------------------+
| path                         |
+------------------------------+
| docs/criteria/definitions.md |
| docs/dev/error_handling.md   |
| docs/dev/metrics.md          |
| docs/dev/style_guide.md      |
+------------------------------+
```

## Utilizing Vector-Based Search

1. In the `spicepod.yaml`, uncomment the `datasets[0].columns[0].embeddings`.
2. Restart the spiced.
3. Perform a basic search

```shell
curl -XPOST http://localhost:8090/v1/search \
    -H "Content-Type: application/json" \
    -d "{
    \"datasets\": [\"spiceai.files\"],
    \"text\": \"testing\",
    \"where\": \"not contains(path, 'docs/release_notes')\",
    \"additional_columns\": [\"download_url\"],
    \"limit\": 2
    }"
```

Result:

```json
{
  "results": [
    {
      "matches": {
        "content": "\n| Component           | Description                                                                                                                                                                                  | Definition Link                                            |"
      },
      "data": {
        "download_url": "https://raw.githubusercontent.com/spiceai/spiceai/trunk/docs/EXTENSIBILITY.md"
      },
      "primary_key": {
        "path": "docs/EXTENSIBILITY.md"
      },
      "score": 0.9217255119459336,
      "dataset": "spiceai.files"
    },
    {
      "matches": {
        "content": ".\n\n**API Guidelines**: The [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/about.html) are followed for all public interfaces."
      },
      "data": {
        "download_url": "https://raw.githubusercontent.com/spiceai/spiceai/trunk/docs/dev/style_guide.md"
      },
      "primary_key": {
        "path": "docs/dev/style_guide.md"
      },
      "score": 0.8344974606243043,
      "dataset": "spiceai.files"
    }
  ],
  "duration_ms": 86
}
```

4. Rerun the search, and retrieve the full document by adding `content` column to `additional_columns`).

```shell
curl -XPOST http://localhost:8090/v1/search \
-H 'Content-Type: application/json' \
-d "{
    \"datasets\": [\"spiceai.files\"],
    \"text\": \"errors\",
    \"where\": \"not contains(path, 'docs/release_notes')\",
    \"additional_columns\": [\"download_url\" , \"content\"],
    \"limit\": 2
}"
```

Result:

```json
{
  "results": [
    {
      "matches": {
        "content": "\n| Component           | Description                                                                                                                                                                                  | Definition Link                                            |"
      },
      "data": {
        "download_url": "https://raw.githubusercontent.com/spiceai/spiceai/trunk/docs/EXTENSIBILITY.md",
        "content": "# Spice.ai Extensibility\n\nThis document is an overview of all the interfaces and extension points in Spice.ai.\n\n| Component           | Description                                                                                                                                                                                  | Definition Link                                            |\n| ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- |\n| [Data Connector]    | Represents the source of data to the Spice.ai runtime. Specifies how to retrieve data, stream data updates, and write data back.                                                             | [dataconnector.rs](../crates/runtime/src/dataconnector.rs) |\n| [Data Accelerator]  | Used by the runtime to store accelerated data locally. Specify which data accelerator to use via `engine` & `mode` fields.                                                                   | [dataaccelerator.rs](../crates/runtime/src/databackend.rs) |\n| [Catalog Connector] | Catalog Connectors connect to external catalog providers and make their tables available for federated SQL query in Spice. Implemented as an optional function on the `DataConnector` trait. | [dataconnector.rs](../crates/runtime/src/dataconnector.rs) |\n| [Secret Stores]     | A Secret Store is a location where secrets are stored and can be used to store sensitive data, like passwords, tokens, and secret keys.                                                      | [secrets.rs](../crates/runtime/src/secrets.rs)             |\n| [Models]            | A machine-learning (ML) or language model (LLM) to load for inferencing.                                                                                                                     | [modelsource.rs](../crates/model_components/src/model.rs)  |\n| Embeddings          | Embeddings map high-dimensional data to a lower-dimensional vector space.                                                                                                                    | [embeddings.rs](../crates/llms/src/embeddings/mod.rs)      |\n\n[Data Connector]: https://spiceai.org/docs/components/data-connectors\n[Data Accelerator]: https://spiceai.org/docs/components/data-accelerators\n[Catalog Connector]: https://spiceai.org/docs/components/catalogs\n[Secret Stores]: https://spiceai.org/docs/components/secret-stores\n[Models]: https://spiceai.org/docs/components/models\n"
      },
      "primary_key": {
        "path": "docs/EXTENSIBILITY.md"
      },
      "score": 0.9320302128251334,
      "dataset": "spiceai.files"
    },
    {
      "matches": {
        "content": " ] All of the model's error messages follow the [error handling guidelines](../../dev/error_handling.md)\n\n### Documentation\n\n- [ ] All documentation meets alpha criteria.\n- [ ] Documentation includes any exceptions made for Beta quality.\n"
      },
      "data": {
        "download_url": "https://raw.githubusercontent.com/spiceai/spiceai/trunk/docs/criteria/models/beta.md",
        "content": "# Spice.ai OSS Models - Beta Release Criteria\n\nThis document defines the set of criteria that is required before a model is considered to be of Beta quality.\n\nAll criteria must be met for the model to be considered Beta, with exceptions permitted only in some cases.\n\n## Beta Quality Models\n\n|     Model Type          | Beta Quality | DRI Sign-off |\n| ----------------------- | ------------ | ------------ |\n| File                    | ✅           | @Jeadie      |\n| Hugging Face            | ✅           | @Jeadie      |\n| Spice.ai Cloud Platform | ➖           |              |\n| OpenAI                  | ✅            | @ewgenius   |\n| Azure Openai            | ➖           |              |\n| Anthropic               | ➖           |              |\n| xAI (Grok)              | ➖           |              |\n\n## Beta Release Criteria\n\n- [ ] All [Alpha release criteria](./alpha.md) pass.\n- [ ] Supports `v1/chat/completion` with `\"roles\"=\"tool\"` or `.messages[*].tool_calls` for `\"roles\"=\"assistant\"` and `stream=true`.\n- [ ] Loads and runs `params.tools: auto` tools.\n- [ ] Completion requests emit runtime metrics\n- [ ] Completion requests emit runtime tracing, including linkage to parent tasks when used internally.\n- [ ] For both synchronous and streaming APIs, usage numbers are reported.\n- [ ] Can handle consistent requests from several clients without an adverse impact on latency. Resource efficiency (memory, CPU, and I/O usage) is measured.\n  - 8 clients consistently sending requests (i.e. sending another request upon receipt of prior request)\n  - A duration of 5 minutes.\n  - The body must have at least 128 tokens (number of prompt tokens in the templated input string).\n  - An increase in latency is defined as a 10% increase in both the 50th & 95th percentile between the first and last minute.\n\n### UX\n\n- [ ] All of the model's error messages follow the [error handling guidelines](../../dev/error_handling.md)\n\n### Documentation\n\n- [ ] All documentation meets alpha criteria.\n- [ ] Documentation includes any exceptions made for Beta quality.\n"
      },
      "primary_key": {
        "path": "docs/criteria/models/beta.md"
      },
      "score": 0.8549700824464589,
      "dataset": "spiceai.files"
    }
  ],
  "duration_ms": 50
}
```

## Full Text Search
Spice can build full-text search indexes from dataset columns. Enable full text search at the column level (see `doc.pulls` dataset).

1. In the `spicepod.yaml`, uncomment `datasets[1]` (i.e. `doc.pulls` dataset).
2. Restart the spiced.
3. Perform a basic search

```shell
curl -XPOST http://localhost:8090/v1/search \
    -H "Content-Type: application/json" \
    -d '{
        "datasets": ["doc.pulls"],
        "text": "Glue data",
        "limit": 3
    }'
```

Note: Only the columns marked `full_text_search.enabled: true` and the table primary keys are stored in the search index.

## Pre-existing embeddings

Spiced can perform vector search on table that already have the required embedding columns. To try this:

1. Run a new `spiced` instance pointing to the currently running `spiced`.

```shell
cd child/
spiced --http 127.0.0.1:8091 --flight 127.0.0.1:50061 --open_telemetry 127.0.0.1:50062
```

2. Rerun the search, this time against the child `spiced` (port `8091`)

```shell
curl -XPOST http://localhost:8091/v1/search \
-H 'Content-Type: application/json' \
-d "{
    \"datasets\": [\"spiceai.files\"],
    \"text\": \"errors\",
    \"where\": \"not contains(path, 'docs/release_notes')\",
    \"additional_columns\": [\"download_url\"],
    \"limit\": 2
}"
```

Result:

```json
{
  "results": [
    {
      "matches": {
        "content": "\n| Component           | Description                                                                                                                                                                                  | Definition Link                                            |"
      },
      "data": {
        "download_url": "https://raw.githubusercontent.com/spiceai/spiceai/trunk/docs/EXTENSIBILITY.md"
      },
      "primary_key": {
        "path": "docs/EXTENSIBILITY.md"
      },
      "score": 0.9320302128251334,
      "dataset": "spiceai.files"
    },
    {
      "matches": {
        "content": " ] All of the model's error messages follow the [error handling guidelines](../../dev/error_handling.md)\n\n### Documentation\n\n- [ ] All documentation meets alpha criteria.\n- [ ] Documentation includes any exceptions made for Beta quality.\n"
      },
      "data": {
        "download_url": "https://raw.githubusercontent.com/spiceai/spiceai/trunk/docs/criteria/models/beta.md"
      },
      "primary_key": {
        "path": "docs/criteria/models/beta.md"
      },
      "score": 0.8549700824464589,
      "dataset": "spiceai.files"
    }
  ],
  "duration_ms": 45
}
```
