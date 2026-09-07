# Amazon S3 Vectors Engine with Spice.ai

Works with `v2.0+`

Spice.ai integrates Amazon S3 Vectors, launched in public preview at AWS Summit New York 2025, as a scalable vector index backend for embedding storage and similarity search. This recipe configures a dataset of GitHub pull requests from the `spiceai/cookbook` repository, embeds the `body` column using OpenAI, stores embeddings in S3 Vectors, and demonstrates semantic search via SQL and HTTP. Spice manages index creation, data synchronization, and query execution, enabling sub-second similarity queries on large datasets at ~$0.02/GB, reducing costs by up to 90% versus traditional vector databases.

## Prerequisites

- Install Spice CLI: Follow [Getting Started](https://docs.spiceai.org/getting-started).
- Create `.env` file with:
  - `GITHUB_TOKEN`: GitHub personal access token ([guide](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-personal-access-token-classic)).
  - `SPICE_OPENAI_API_KEY`: OpenAI API key.
  - `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` (and `AWS_SESSION_TOKEN` if using temporary credentials): AWS credentials for S3 Vectors access. For alternatives, see [S3 Vectors documentation](https://spiceai.org/docs/components/vectors/s3_vectors).
- An S3 Vectors bucket in your own AWS account, set as `s3_vectors_bucket` in `spicepod.yaml`. Spice creates the *indexes* inside the bucket automatically, but not the bucket itself:

  ```shell
  aws s3vectors create-vector-bucket --vector-bucket-name <your-bucket> --region us-east-2
  ```

Instead of static keys, `s3_vectors_aws_iam_role_source` uses the AWS credential chain — `auto` (any chain provider, including an SSO profile), `metadata` (IMDS/ECS/EKS only), or `env`:

```yaml
s3_vectors_param: &s3_vectors_param
  s3_vectors_bucket: <your-bucket>
  s3_vectors_aws_region: us-east-2
  s3_vectors_aws_iam_role_source: auto
```

## Configuration

Use the `spicepod.yaml` in this recipe directory. It pulls recent GitHub PRs, accelerates data for the last 7 days, embeds the `body` column, and stores vectors in S3 Vectors. The `row_id` uses `id` as the primary key for vector upsert. On ingestion, Spice embeds each PR's `body` using OpenAI and upserts to S3 Vectors with `id` as key, handling updates/deletions automatically.

## Run Spice

Start the Spice runtime:

```shell
spice run
```

Spice creates the S3 Vectors index if absent, ingests data, and generates embeddings.

## Search with SQL

Use the `vector_search` table-valued function for semantic search. It embeds the query text and queries S3 Vectors for nearest neighbors by cosine similarity.

Start the Spice SQL REPL:

```shell
spice sql
```

### Basic Search

Search for PRs similar to "bugs in DuckDB":

```sql
SELECT
    url,
    title,
    _score -- this is a computed value (i.e. not in `describe pulls;`).
FROM vector_search(pulls, 'bugs in DuckDB', 4)
ORDER BY _score DESC
LIMIT 4;
```

Results:

```sql
+----------------------------------------------+--------------------------------------------------------------------------------+--------------------+
|                     url                      |                                     title                                      |       _score       |
|                   varchar                    |                                    varchar                                     |      float64       |
+----------------------------------------------+--------------------------------------------------------------------------------+--------------------+
| https://github.com/spiceai/cookbook/pull/576 | fix(localpod,duckdb): correct a truncated CSV header and a typo                 | 0.7042624683970505 |
| https://github.com/spiceai/cookbook/pull/581 | Fix caching/sql_results recipe: correct dataset names, log lines, and Q1 output | 0.6822196713980645 |
| https://github.com/spiceai/cookbook/pull/595 | docs: fix v2.2 cookbook validation issues                                      | 0.681723637898489  |
| https://github.com/spiceai/cookbook/pull/590 | Add Mysql-Aurora CDC cookbook                                                  | 0.6804361755080721 |
+----------------------------------------------+--------------------------------------------------------------------------------+--------------------+

4 rows.
```

The `_score` column (0-1, higher is more similar) is computed from cosine distance. Because `refresh_data_window: 7d` only loads the last week of pull requests, the specific rows and scores you see will differ from the output above.

### Query Plan

Examine execution:

```sql
EXPLAIN SELECT url, title, _score FROM vector_search(pulls, 'bugs in DuckDB', 4) ORDER BY _score DESC LIMIT 4;
```

Plan (the 1536-element query vector is elided as `[...]` for readability):

```sql
+---------------+--------------------------------------------------------------------------------------------------------------------------------------------------------+
|   plan_type   |                                                                  plan                                                                  |
|    varchar    |                                                                varchar                                                                 |
+---------------+--------------------------------------------------------------------------------------------------------------------------------------------------------+
| logical_plan  | Sort: vector_search(pulls, Utf8("bugs in DuckDB"), Int64(4))._score DESC NULLS FIRST, fetch=4                                           |
|               |   Projection: vector_search(...).url, vector_search(...).title, vector_search(...)._score                                               |
|               |     TableScan: vector_search(pulls, Utf8("bugs in DuckDB"), Int64(4)) projection=[_score, title, url]                                   |
| physical_plan | SortExec: TopK(fetch=4), expr=[_score@2 DESC], preserve_partitioning=[false]                                                            |
|               |   ProjectionExec: expr=[url@2 as url, title@1 as title, _score@3 as _score]                                                             |
|               |     SortExec: TopK(fetch=4), expr=[_score@3 DESC NULLS LAST, id@0 ASC], preserve_partitioning=[false]                                   |
|               |       ProjectionExec: expr=[id@1 as id, title@2 as title, url@3 as url,                                                                 |
|               |                            1 - cosine_distance([...], body_embedding@0) as _score]                                                      |
|               |         BytesProcessedExec                                                                                                              |
|               |           DataSourceExec: partitions=1, partition_sizes=[18]                                                                            |
+---------------+--------------------------------------------------------------------------------------------------------------------------------------------------------+
```

Because this dataset sets `acceleration: enabled: true`, the embeddings are materialized
locally alongside the rows, and the similarity search is evaluated there — the plan scores
rows with `cosine_distance` over the local `body_embedding` column. S3 Vectors is still the
durable index: Spice creates it, writes every embedding through to it on ingestion, and
serves reads from it when the vectors are not available locally.

Confirm the vectors reached S3:

```shell
aws s3vectors list-vectors \
  --vector-bucket-name <your-bucket> \
  --index-name pulls-body-my-embedding-model \
  --region us-east-2 --query 'length(vectors)'
```

### Metadata Columns

The `spicepod.yaml` in this recipe declares metadata alongside the embedded column:

```yaml
columns:
  - name: body
    embeddings:
      - from: my_embedding_model
        row_id:
          - id
  - name: title
    metadata:
      vectors: filterable
  - name: url
    metadata:
      vectors: non-filterable
  - name: state
    metadata:
      vectors: filterable
```

`filterable` metadata can be used in search predicates; `non-filterable` metadata is stored
and returned but cannot be filtered on. These declarations shape the S3 Vectors index itself,
visible on the created index:

```shell
aws s3vectors get-index \
  --vector-bucket-name <your-bucket> \
  --index-name pulls-body-my-embedding-model \
  --region us-east-2
```

```json
{
  "index": {
    "indexName": "pulls-body-my-embedding-model",
    "dataType": "float32",
    "dimension": 1536,
    "distanceMetric": "cosine",
    "metadataConfiguration": {
      "nonFilterableMetadataKeys": [
        "url"
      ]
    }
  }
}
```

Filtering on a `filterable` column:

```sql
EXPLAIN
SELECT url, title, _score
FROM vector_search(pulls, 'bugs in DuckDB', 4)
WHERE state = 'OPEN'
ORDER BY _score DESC
LIMIT 4;
```

Plan:

```sql
+---------------+--------------------------------------------------------------------------------------------------------------------------------------------------------+
|   plan_type   |                                                                  plan                                                                  |
|    varchar    |                                                                varchar                                                                 |
+---------------+--------------------------------------------------------------------------------------------------------------------------------------------------------+
| physical_plan | SortExec: TopK(fetch=4), expr=[_score@2 DESC], preserve_partitioning=[false]                                                            |
|               |   ProjectionExec: expr=[url@2 as url, title@1 as title, _score@3 as _score]                                                             |
|               |     SortPreservingMergeExec: [_score@3 DESC NULLS LAST, id@0 ASC], fetch=4                                                              |
|               |       SortExec: TopK(fetch=4), expr=[_score@3 DESC NULLS LAST, id@0 ASC], preserve_partitioning=[true]                                  |
|               |         ProjectionExec: expr=[id@1 as id, title@3 as title, url@4 as url,                                                               |
|               |                              1 - cosine_distance([...], body_embedding@0) as _score]                                                    |
|               |           RepartitionExec: partitioning=RoundRobinBatch(18), input_partitions=1                                                          |
|               |             FilterExec: state@2 = OPEN                                                                                                  |
|               |               BytesProcessedExec                                                                                                        |
|               |                 DataSourceExec: partitions=1, partition_sizes=[18]                                                                      |
+---------------+--------------------------------------------------------------------------------------------------------------------------------------------------------+
```

The predicate is applied before scoring, so the top-K is computed over matching rows only
rather than filtered afterward.

## Search via HTTP

Use `/v1/search` for semantic search:

```shell
curl --request POST \
  --url http://localhost:8090/v1/search \
  --header 'Content-Type: application/json' \
  --data '{
	"datasets": [
		"pulls"
	],
	"text": "bugs in DuckDB",
	"additional_columns": [
		"url",
		"title"
	],
	"where": "state='\''MERGED'\''",
	"limit": 4
}'
```

`state` is one of `OPEN`, `MERGED`, or `CLOSED`; a 7-day window on an active repository
typically holds only `OPEN` and `MERGED`, so filtering on `CLOSED` can legitimately return
no results.

Response:

````json
{
  "results": [
    {
      "matches": {
        "body": [
          "## 📝 Summary\r\n- Update duckdb-rs to point at spiceai duckdb fork: https://github.com/spiceai/duckdb-rs/pull/20\r\n- DuckDB v1.3.2 + [index resolution fix](https://github.com/spiceai/duckdb/compare/v1.3.2...v1.3.2-index-resolution)\r\n"
        ]
      },
      "data": {
        "url": "https://github.com/spiceai/spiceai/pull/6496",
        "title": "Update spiceai/duckdb-rs -> DuckDB 1.3.2 + index fix"
      },
      "primary_key": {
        "id": "PR_kwDOF31SUc6fp25h"
      },
      "_score": 0.6213145852088928,
      "dataset": "pulls"
    },
    {
      "matches": {
        "body": [
          "## 📝 Summary\r\n\r\n<!-- What does this PR change? Why is it necessary? Keep it concise. -->\r\n\r\n## 🔗 Related\r\n\r\n<!-- Link to relevant issues, discussions, or other PRs. Use \"Closes #123\" to auto-close issues. Omit if none. -->\r\n\r\n## 🚨 Breaking Changes\r\n\r\n<!-- Describe breaking changes if any, or delete this section. -->\r\n<!-- If breaking, make sure the \"breaking change\" label is added. -->\r\n\r\n## 📚 Docs\r\n\r\n<!-- Note any required updates to docs, recipes, or guides. Omit if not applicable. -->\r\n\r\n## 👀 Notes for Reviewers\r\n\r\n<!-- Any areas needing special attention or questions for reviewers? Omitၓ Omit if none. -->\r\n"
        ]
      },
      "data": {
        "url": "https://github.com/spiceai/spiceai/pull/6494",
        "title": "v1.5.0 release notes"
      },
      "primary_key": {
        "id": "PR_kwDOF31SUc6fpWVh"
      },
      "_score": 0.2575995922088623,
      "dataset": "pulls"
    },
    {
      "matches": {
        "body": [
          "## 📝 Summary\r\n\r\n<!-- What does this PR change? Why is it necessary? Keep it concise. -->\r\n\r\n## 🔗 Related\r\n\r\n<!-- Link to relevant issues, discussions, or other PRs. Use \"Closes #123\" to auto-close issues. Omit if none. -->\r\n\r\n## 🚨 Breaking Changes\r\n\r\n<!-- Describe breaking changes if any, or delete this section. -->\r\n<!-- If breaking, make sure the \"breaking change\" label is added. -->\r\n\r\n## 📚 Docs\r\n\r\n<!-- Note any required updates to docs, recipes, or guides. Omit if not applicable. -->\r\n\r\n## 👀 Notes for Reviewers\r\n\r\n<!-- Any areas needing special attention or questions for reviewers? Omit if none. -->\r\n"
        ]
      },
      "data": {
        "url": "https://github.com/spiceai/spiceai/pull/6520",
        "title": "Prepare v1.5.0 release"
      },
      "primary_key": {
        "id": "PR_kwDOF31SUc6fy91T"
      },
      "_score": 0.2575995922088623,
      "dataset": "pulls"
    },
    {
      "matches": {
        "body": [
          "## Summary\r\nAdds a new `availability_monitor` configuration option to individual datasets to control whether the dataset availability monitor checks that specific dataset. This provides granular control over which datasets are monitored, preventing unnecessary remote calls that could wake up expensive warehouses.\r\n\r\n- Closes #5676\r\n\r\n## Usage\r\nUsers can now disable availability monitoring for specific datasets that might cause expensive warehouse wake-ups:\r\n\r\n```yaml\r\ndatasets:\r\n  - from: snowflake\r\n    name: expensive_table\r\n    availability_monitor: disabled\r\n  \r\n  - from: file://local_data.csv\r\n    name: local_data\r\n    availability_monitor: default\r\n```\r\n"
        ]
      },
      "data": {
        "url": "https://github.com/spiceai/spiceai/pull/6482",
        "title": "Add per-dataset availability monitor configuration"
      },
      "primary_key": {
        "id": "PR_kwDOF31SUc6fT_8S"
      },
      "_score": 0.24210351705551147,
      "dataset": "pulls"
    }
  ],
  "duration_ms": 3387
}
````

## Chunking

The Spice runtime can manage chunking, embedding and reaggregating chunks of datasets with large content. Spice loaded `spiceai.cookbook_readme`: all cookbook READMEs. Search, both HTTP and SQL can be queried as before.

```SQL
SELECT
    path,
    _match, -- The matching chunk within `content`
    length(content) as content_length,
    _score
FROM vector_search(spiceai.cookbook_readme, 'data governance and auditing')
ORDER BY _score DESC
LIMIT 3;
```

````
+------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------------+---------------------+
|                path                |                                                                                           _match                                                                                           | content_length |        _score       |
|               varchar              |                                                                                           varchar                                                                                          |      int32     |       float64       |
+------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------------+---------------------+
| guides/security-analyzer/README.md |                                                                                                                                                                                            | 12688          | 0.4630262851715088  |
|                                    | -- Suspicious: Large data extraction                                                                                                                                                       |                |                     |
|                                    | INSERT INTO query_audit_logs (user_id, query_text, database_name, schema_name, rows_affected, query_type)                                                                                  |                |                     |
|                                    | VALUES                                                                                                                                                                                     |                |                     |
|                                    | ('bob', 'SELECT * FROM employees', 'hr_db', 'public', 5000, 'SELECT');                                                                                                                     |                |                     |
|                                    |                                                                                                                                                                                            |                |                     |
|                                    | -- Suspicious: Cross-schema access                                                                                                                                                         |                |                     |
|                                    | INSERT INTO query_audit_logs (user_id, query_text, database_name, schema_name, rows_affected, query_type)                                                                                  |                |                     |
|                                    | VALUES                                                                                                                                                                                     |                |                     |
|                                    | ('charlie', 'SELECT * FROM finance.salary_data', 'hr_db', 'finance', 100, 'SELECT'),                                                                                                       |                |                     |
|                                    | ('charlie', 'SELECT * FROM hr.employee_reviews', 'hr_db', 'hr', 200, 'SELECT'),                                                                                                            |                |                     |
|                                    | ('charlie', 'SELECT * FROM security.access_logs', 'hr_db', 'security', 300, 'SELECT');                                                                                                     |                |                     |
|                                    |                                                                                                                                                                                            |                |                     |
|                                    | -- Suspicious: Sequential data harvesting                                                                                                                                                  |                |                     |
|                                    | INSERT INTO query_audit_logs (user_id, query_text, database_name, schema_name, rows_affected, query_type)                                                                                  |                |                     |
|                                    | VALUES                                                                                                                                                                                     |                |                     |
|                                    | ('dave', 'SELECT email FROM customers WHERE region = ''West''', 'sales_db', 'public', 50, 'SELECT'),                                                                                       |                |                     |
|                                    | ('dave', 'SELECT phone FROM customers WHERE region = ''East''', 'sales_db', 'public', 50, 'SELECT'),                                                                                       |                |                     |
|                                    | ('dave', 'SELECT address FROM customers WHERE region = ''South''', 'sales_db', 'public', 50, 'SELECT');                                                                                    |                |                     |
|                                    | ```                                                                                                                                                                                        |                |                     |
|                                    |                                                                                                                                                                                            |                |                     |
|                                    | Our AI analysis provides rich context about these patterns:                                                                                                                                |                |                     |
|                                    |                                                                                                                                                                                            |                |                     |
|                                    | ```plaintext                                                                                                                                                                               |                |                     |
|                                    | Based on the recent query patterns, several concerning behaviors have been identified:                                                                                                     |                |                     |
|                                    |                                                                                                                                                                                            |                |                     |
|                                    | 1. Sequential Data Harvesting (High Severity)                                                                                                                                              |                |                     |
|                                    |    User 'dave' is systematically extracting customer PII (email, phone, address) across different regions.                                                                                 |                |                     |
|                                    |    While each query appears legitimate, the pattern suggests a methodical data gathering operation.                                                                                        |                |                     |
|                                    |                                                                                                                                                                                            |                |                     |
|                                    |    Recommendations:                                                                                                                                                                        |                |                     |
|                                    |    - Implement controls to detect cross-region PII access patterns                                                                                                                         |                |                     |
|                                    |    - Review dave's role requirements for customer data access                                                                                                                              |                |                     |
|                                    |    - Consider implementing aggregate-only views for customer data                                                                                                                          |                |                     |
|                                    |                                                                                                                                                                                            |                |                     |
|                                    | 2. Bulk Data Access (Medium Severity)                                                                                                                                                      |                |                     |
|                                    |    User 'bob' extracted 5000 employee records in a single query.                                                                                                                           |                |                     |
|                                    |    This could be legitimate ETL work but requires verification.                                                                                                                            |                |                     |
|                                    |                                                                                                                                                                                            |                |                     |
|                                    |    Recommendations:                                                                                                                                                                        |                |                     |
|                                    |    - Verify if this is a scheduled data export                                                                                                                                             |                |                     |
|                                    |    - Implement row-level security if bulk access isn't required                                                                                                                            |                |                     |
|                                    |    - Add rate limiting for large data retrieval                                                                                                                                            |                |                     |
| vectors/s3/README.md               |    | INSERT INTO query_audit_logs (user_id, query_text, database_name, schema_name, rows_affected, query_type)  |                |                     |                                   | 25486          | 0.44905054569244385 |
|                                    | |                                    | VALUES                                                                                                     |                |                     | |                |                     |
|                                    | |                                    | ('dave', 'SELECT email FROM customers WHERE region = ''West''', 'sales_db', 'public', 50, 'SELECT'),       |                |                     | |                |                     |
|                                    | |                                    | ('dave', 'SELECT phone FROM customers WHERE region = ''East''', 'sales_db', 'public', 50, 'SELECT'),       |                |                     | |                |                     |
...
````

```shell
curl --request POST \
  --url http://localhost:8090/v1/search \
  --header 'Content-Type: application/json' \
  --data '{
	"datasets": [
		"spiceai.cookbook_readme"
	],
	"text": "data governance and auditing",
	"limit": 2
}'
```

````json
{
  "results": [
    {
      "matches": {
        "content": [
          "\n```sql\n-- Normal query - single department access\nINSERT INTO query_audit_logs (user_id, query_text, database_name, schema_name, rows_affected, ..."
        ]
      },
      "primary_key": {
        "path": "guides/security-analyzer/README.md"
      },
      "_score": 0.4742351770401001,
      "dataset": "spiceai.cookbook_readme"
    },
    {
      "matches": {
        "content": [
          "\n```shell\ndrop table <CATALOG_NAME>.<SCHEMA_NAME>.test_table_no_v2checkpoint;\n```\n\n**Verify table removal in Spice**: Observe that the table has beem removed in spice runtime log\n\n```shell\n2025-01-18T00:59:49.121835Z  INFO data_components::unity_catalog::provider: Refreshed schema <CATALOG_NAME>.<SCHEMA_NAME>. Tables removed: test_table_no_v2checkpoint.\n```\n\n## Step 8. Use Databricks Service Principal\n\nCreate a Databricks service ..."
        ]
      },
      "primary_key": {
        "path": "catalogs/databricks/README.md"
      },
      "_score": 0.3918114900588989,
      "dataset": "spiceai.cookbook_readme"
    }
  ],
  "duration_ms": 657
}
````

## Advanced Usage

- **Hybrid Search**: Combine vector and full-text search with `text_search` using Reciprocal Rank Fusion (RRF) in SQL. See [blog post](https://spiceai.org/blog/amazon-s3-vectors-with-spice).
- **Multi-Column Embeddings**: Embed additional fields (e.g., `title`) and weight in queries (e.g., title score \* 2).
- **Re-ranking**: Use keyword search for initial candidates, then vector search for precision.
- **Scaling**: S3 Vectors supports billions of vectors; Spice handles synchronization.
- **Limitations**: ANN provides approximate results; single index per dataset limits multi-embedding columns without ARN.

## References

- [S3 Vectors documentation](https://spiceai.org/docs/components/vectors/s3_vectors)
- [Spice.ai S3 Vectors blog post](https://spiceai.org/blog/amazon-s3-vectors-with-spice)
- [Amazon S3 Vectors](https://aws.amazon.com/s3/features/vectors/)
