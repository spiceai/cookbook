# Azure OpenAI Models

Works with `v1.0+`

This recipe demonstrates how to use Azure OpenAI models for vector-based search and chat functionalities with structured (taxi trips) and unstructured GitHub data.

To reduce GitHub API requests and Azure embedding usage, the sample accelerates at most **10 closed issues** and **16 Markdown files** from `docs/dev/`. The `refresh_sql` limits in `spicepod.yaml` bound the embedded rows, and the file connector's `include` pattern restricts downloads to developer documentation. Increase these limits or broaden the pattern only when your API quotas allow it.

## Prerequisites

- Ensure you have the Spice CLI installed. Follow the [Getting Started](https://docs.spiceai.org/getting-started) guide if you haven't done so yet.

## Deploy Test Models

Navigate to the [Azure OpenAI Model Deployment](https://ai.azure.com/resource/deployments) page and deploy the following base models:

- `text-embedding-3-small`: Model for embeddings creation for vector similarity search.
- `gpt-4o-mini`: LLM chat model.

Note: Other models can be used if available. Update `spicepod.yaml` to match the model name.

## Clone cookbook repo, populate `.env` and Configure Spicepod

Clone this cookbook repo locally:

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/azure_openai/
```

Populate `.env` with the following:

- `GITHUB_TOKEN`: A [personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-personal-access-token-classic).
- `SPICE_AZURE_API_KEY`: An Azure OpenAI API key from the Models Deployment page.
- `SPICE_AZURE_AI_ENDPOINT`: The Azure OpenAI resource endpoint used for models, for example, `https://resource-name.openai.azure.com`. This can be found on the Models Deployment page.

Verify that the `spicepod.yaml` configuration (`azure_deployment_name`, `azure_api_version`, etc.) matches the information on the [Azure OpenAI Model Deployment](https://ai.azure.com/resource/deployments) page.

```yaml
embeddings:
  - name: embeddings-model
    from: azure:text-embedding-3-small
    params:
      endpoint: ${ secrets:SPICE_AZURE_AI_ENDPOINT }
      azure_deployment_name: text-embedding-3-small
      azure_api_version: 2023-05-15
      azure_api_key: ${ secrets:SPICE_AZURE_API_KEY }

models:
  - from: azure:gpt-4o-mini
    name: chat-model
    params:
      tools: auto
      endpoint: ${ secrets:SPICE_AZURE_AI_ENDPOINT }
      azure_api_version: 2024-08-01-preview
      azure_deployment_name: gpt-4o-mini
      azure_api_key: ${ secrets:SPICE_AZURE_API_KEY }
```

## Run Spice

```shell
spice run
```

At startup the runtime logs `WARN runtime_parameters: Ignoring parameter
'file_format': not supported for connector github.` — this is expected and
harmless. The GitHub connector has no `file_format` parameter, but the chunker
reads the dataset's `file_format` directly and uses it to pick the Markdown-aware
splitter, which is what the setting is for here. Removing it falls back to the
plain text splitter.

Wait for the datasets to finish loading, then check their sizes in `spice sql`:

```sql
SELECT 'issues' AS dataset, COUNT(*) AS row_count FROM spiceai.issues
UNION ALL
SELECT 'files' AS dataset, COUNT(*) AS row_count FROM spiceai.files;
```

The issue and file counts are capped at 10 and 16 respectively. Fewer rows are
possible if the repository has fewer matching issues or files. Search results
and scores depend on the contents of this sample.

## SQL Search

1. Execute a Basic SQL Query to perform keyword searches within the dataset:

```shell
spice sql
```

Then:

```sql
SELECT path
FROM spiceai.files
WHERE
    LOWER(content) LIKE '%errors%'
    AND NOT contains(path, 'docs/release_notes')
ORDER BY path;
```

Example result:

```text
+--------------------------------+
| path                           |
|            varchar             |
+--------------------------------+
| docs/dev/cloud-login.md        |
| docs/dev/cloud-multi-org.md    |
| docs/dev/cosmosdb.md           |
| docs/dev/error_handling.md     |
| docs/dev/fork_patches.md       |
| docs/dev/metrics.md            |
| docs/dev/refresh_pipelining.md |
| docs/dev/style_guide.md        |
+--------------------------------+
```

## Utilizing Vector-Based Search

```shell
  curl -XPOST http://localhost:8090/v1/search \
    -H "Content-Type: application/json" \
    -d "{
      \"datasets\": [\"spiceai.files\"],
      \"text\": \"TEL metrics naming\",
      \"where\": \"not contains(path, 'docs/release_notes')\",
      \"additional_columns\": [\"download_url\"],
      \"limit\": 2
    }"
```

Example response:

```json
{
  "results": [
    {
      "matches": {
        "content": [
          "# Metrics Naming\n\n## TL;DR\n\n**Metric Naming Guide**: Prioritize Developer Experience (DX) with intuitive, readable names that follow consistent conventions. Start with a domain prefix, use snake_case, avoid plurals in names (except counters), include units where relevant, and use labels for variations. Align with Prometheus and OpenTelemetry standards, and adhere to UCUM for units.\n\n"
        ]
      },
      "data": {
        "download_url": "https://raw.githubusercontent.com/spiceai/spiceai/trunk/docs/dev/metrics.md"
      },
      "primary_key": {
        "path": "docs/dev/metrics.md"
      },
      "_score": 0.8277048428639362,
      "dataset": "spiceai.files"
    },
    {
      "matches": {
        "content": [
          "## Guidelines\n\nThese guidelines were created based on the First Principle of Developer Experience First and Align to Industry Standard. No direct industry standards exist, but \"best practices\" are available. Loosely inspired by error handling material from:\n\n* [Error Messages in Windows 7](https://learn.microsoft.com/en-us/windows/win32/uxguide/mess-error)\n* [Cypress](https://docs.cypress.io/app/references/error-messages)\n\nRelated reading:\n\n* [Microcopy: A complete guide](https://www.microcopybook.com/)\n\n"
        ]
      },
      "data": {
        "download_url": "https://raw.githubusercontent.com/spiceai/spiceai/trunk/docs/dev/error_handling.md"
      },
      "primary_key": {
        "path": "docs/dev/error_handling.md"
      },
      "_score": 0.6896097040436964,
      "dataset": "spiceai.files"
    }
  ],
  "duration_ms": 381
}
```

> **Version note:** The relevance score is returned in the `_score` field (leading underscore) on Spice `v2.0+`. On `v1.x` it was returned as `score` (no underscore).

Vector-based search could also be performed using `spice search` CLI command:

```shell
spice search
```

At the search prompt, enter `TEL metrics naming`. Results come from the sampled
developer documentation; release notes and other documentation directories are
outside this recipe's `include` pattern.

## Vector Search on multiple columns

Notice on the `name: spiceai.issues` dataset, there are embeddings on both the `body` & `title`. When performing vector search on this table, it will search across both these columns, and return results based on combined relevance.

```shell
  curl -XPOST http://localhost:8090/v1/search \
    -H "Content-Type: application/json" \
    -d "{
      \"datasets\": [\"spiceai.issues\"],
      \"text\": \"AI\",
      \"where\": \"state='CLOSED'\",
      \"additional_columns\": [\"url\"],
      \"limit\": 3
    }"
```

## Utilizing a natural language query

Use `spice chat` CLI command to query information using natural language

```shell
spice chat
Using model: chat-model
```

Perform test queries:

```shell
chat> what datasets you have access to
I have access to the following datasets:

1. **Taxi Trips Dataset**
   - **Description**: Taxi trips in S3
   - **Can Search Documents**: No

2. **Spice.ai Project Documentation**
   - **Description**: Spice.ai project documentation (github.com/spiceai/spiceai)
   - **Can Search Documents**: Yes
```

```shell
chat> how many records in taxi trips dataset
There are a total of 2,964,624 records in the taxi trips dataset.
```

```shell
chat> what is the longest taxi trip distance recorded
The longest taxi trip distance recorded is approximately 312,722.3 meters.
```
