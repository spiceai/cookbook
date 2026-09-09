# Searching GitHub Files

Works with `v1.0+`

This recipe demonstrates how to create embeddings for GitHub files and perform vector-based searches.

[![Watch the Spice.ai vector search over GitHub files demo](https://img.youtube.com/vi/5y26MveEJ8c/hqdefault.jpg)](https://www.youtube.com/embed/5y26MveEJ8c)

## Prerequisites

- Ensure you have the Spice CLI installed. Follow the [Getting Started](https://docs.spiceai.org/getting-started) if you haven't done so.
- Populate `.env` in the `cookbook/search_github_files` directory.
  - `GITHUB_TOKEN`: With a [personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-personal-access-token-classic).
    A classic token with no scopes selected is enough for the public repositories
    this recipe reads.

No model provider key is needed. Embeddings are produced locally by the
`sentence-transformers/all-MiniLM-L6-v2` model that the Spicepod downloads from
Hugging Face on first run.

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
+--------------------------------------------------+
|                       path                       |
|                      varchar                     |
+--------------------------------------------------+
| docs/PRINCIPLES.md                               |
| docs/cayenne/cayenne.md                          |
| docs/criteria/connectors/rc.md                   |
| docs/criteria/definitions.md                     |
| docs/criteria/features/alpha.md                  |
| docs/decisions/008-vendored-vortex-datafusion.md |
| docs/dev/cloud-login.md                          |
| docs/dev/cloud-multi-org.md                      |
| docs/dev/cosmosdb.md                             |
| docs/dev/error_handling.md                       |
| docs/dev/fork_patches.md                         |
| docs/dev/metrics.md                              |
| docs/dev/refresh_pipelining.md                   |
| docs/dev/style_guide.md                          |
| docs/examples/http_refresh_sql_example.md        |
| docs/features/databricks-resilience.md           |
| docs/features/gcs-connector.md                   |
| docs/features/git-connector.md                   |
| docs/features/mysql-binlog-replication.md        |
| docs/features/postgres-replication.md            |
| docs/threat_models/v1.9.2.md                     |
| docs/threat_models/v2.0.0.md                     |
+--------------------------------------------------+

Time: 0.009444042 seconds. 22 rows.
```

The dataset tracks `spiceai/spiceai` at `trunk`, so the exact rows and every
search result below change as the repository's `docs/` directory changes.

## Utilizing Vector-Based Search

1. In the `spicepod.yaml`, uncomment the `datasets[0].columns[0].embeddings`
   block and the `file_format: md` parameter.
2. Restart the spiced.

   The runtime logs `WARN runtime_parameters: Ignoring parameter 'file_format':
   not supported for connector github.` — this is expected and harmless. The
   GitHub connector has no `file_format` parameter, but the chunker reads the
   dataset's `file_format` directly and uses it to pick the Markdown-aware
   splitter, which is what the setting is for here.

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
        "content": [
          "### Test Coverage\n\nStable quality accelerators should be able to run test packages derived from the following:\n\n- [TPC-H](https://www.tpc.org/TPC-H/)\n- [TPC-DS](https://www.tpc.org/TPC-DS/)\n- [ClickBench](https://github.com/ClickHouse/ClickBench)\n- [SpiceBench](https://github.com/spiceai/spicebench)\n\nIndexes are not required for test coverage, but can be introduced if required for tests to pass (e.g. due to performance characteristics, etc).\n\n"
        ]
      },
      "data": {
        "download_url": "https://raw.githubusercontent.com/spiceai/spiceai/trunk/docs/criteria/accelerators/stable.md"
      },
      "primary_key": {
        "path": "docs/criteria/accelerators/stable.md"
      },
      "_score": 0.7255329489486705,
      "dataset": "spiceai.files"
    },
    {
      "matches": {
        "content": [
          "### Test Coverage\n\nBeta quality accelerators should be able to run test packages derived from the following:\n\n- [TPC-H](https://www.tpc.org/TPC-H/)\n- [TPC-DS](https://www.tpc.org/TPC-DS/)\n- [ClickBench](https://github.com/ClickHouse/ClickBench)\n\nIndexes are not required for test coverage, but can be introduced if required for tests to pass (e.g. due to performance characteristics, etc).\n\n#### General\n\n- [ ] Integration tests to cover accelerating data from S3 parquet, MySQL, Postgres with the [Core Arrow Data Types](../definitions.md)\n- [ ] Integration tests to cover \"On Conflict\" behaviors.\n- [ ] An integration or benchmark test validating the maximum column count use case is added.\n\n"
        ]
      },
      "data": {
        "download_url": "https://raw.githubusercontent.com/spiceai/spiceai/trunk/docs/criteria/accelerators/beta.md"
      },
      "primary_key": {
        "path": "docs/criteria/accelerators/beta.md"
      },
      "_score": 0.7108545813115704,
      "dataset": "spiceai.files"
    }
  ],
  "duration_ms": 59
}
```

> **Version note:** The relevance score is returned in the `_score` field (leading underscore) on Spice `v2.0+`. On `v1.x` it was returned as `score` (no underscore).

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
        "content": [
          "### Errors and resilience\n\n"
        ]
      },
      "data": {
        "download_url": "https://raw.githubusercontent.com/spiceai/spiceai/trunk/docs/features/postgres-replication.md",
        "content": "# PostgreSQL Logical Replication\n\n... full document text, elided here ...\n"
      },
      "primary_key": {
        "path": "docs/features/postgres-replication.md"
      },
      "_score": 0.7487837074615193,
      "dataset": "spiceai.files"
    },
    {
      "matches": {
        "content": [
          "### UX\n\n- [ ] User-facing error messages are clear, actionable, and non-technical where appropriate\n- [ ] Configuration experience is consistent with other features\n"
        ]
      },
      "data": {
        "download_url": "https://raw.githubusercontent.com/spiceai/spiceai/trunk/docs/criteria/features/beta.md",
        "content": "# Spice.ai OSS Features - Beta Release Criteria\n\n... full document text, elided here ...\n"
      },
      "primary_key": {
        "path": "docs/criteria/features/beta.md"
      },
      "_score": 0.746478348538512,
      "dataset": "spiceai.files"
    }
  ],
  "duration_ms": 7
}
```

`data.content` holds the entire file, so the real response for these two
documents is about 40 KB — it is elided above.

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

Result:

```json
{
  "results": [
    {
      "matches": {
        "body": [
          "Adds benefits, consideration, limits on data ingestion"
        ],
        "title": [
          "Data ingestion doc"
        ]
      },
      "primary_key": {
        "id": "PR_kwDOF38K0s5q_Qqv"
      },
      "_score": 0.03252247488101534,
      "dataset": "doc.pulls"
    },
    {
      "matches": {
        "title": [
          "Rename `refresh_data_period` to `refresh_data_window`"
        ],
        "body": [
          "Renames `refresh_data_period` to `refresh_data_window` to be clearer and also open the possibility of different windows other than pure lookback."
        ]
      },
      "primary_key": {
        "id": "PR_kwDOF38K0s5uEvw0"
      },
      "_score": 0.03200204813108039,
      "dataset": "doc.pulls"
    }
  ]
}
```

Note: Only the columns marked `full_text_search.enabled: true` and the table primary keys are stored in the search index.

## Pre-existing embeddings

Spiced can perform vector search on table that already have the required embedding columns. To try this:

1. Run a new `spiced` instance pointing to the currently running `spiced`.

```shell
cd child/
spiced --http 127.0.0.1:8091 --flight 127.0.0.1:50061
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
        "content": [
          "### Errors and resilience\n\n"
        ]
      },
      "data": {
        "download_url": "https://raw.githubusercontent.com/spiceai/spiceai/trunk/docs/features/postgres-replication.md"
      },
      "primary_key": {
        "path": "docs/features/postgres-replication.md"
      },
      "_score": 0.7487837074615193,
      "dataset": "spiceai.files"
    },
    {
      "matches": {
        "content": [
          "### UX\n\n- [ ] User-facing error messages are clear, actionable, and non-technical where appropriate\n- [ ] Configuration experience is consistent with other features\n"
        ]
      },
      "data": {
        "download_url": "https://raw.githubusercontent.com/spiceai/spiceai/trunk/docs/criteria/features/beta.md"
      },
      "primary_key": {
        "path": "docs/criteria/features/beta.md"
      },
      "_score": 0.746478348538512,
      "dataset": "spiceai.files"
    }
  ],
  "duration_ms": 37
}
```

The scores match the parent runtime's — the child re-uses the embeddings that
are already stored on the table rather than recomputing them.
