# Amazon S3 Vectors Engine with Spice.ai

Spice.ai integrates Amazon S3 Vectors, launched in public preview at AWS Summit New York 2025, as a scalable vector index backend for embedding storage and similarity search. This recipe configures a dataset of GitHub pull requests from the `spiceai/spiceai` repository, embeds the `body` column using OpenAI, stores embeddings in S3 Vectors, and demonstrates semantic search via SQL and HTTP. Spice manages index creation, data synchronization, and query execution, enabling sub-second similarity queries on large datasets at ~$0.02/GB, reducing costs by up to 90% versus traditional vector databases.

## Prerequisites

- Install Spice CLI: Follow [Getting Started](https://docs.spiceai.org/getting-started).
- Create `.env` file with:
  - `GITHUB_TOKEN`: GitHub personal access token ([guide](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-personal-access-token-classic)).
  - `SPICE_OPENAI_API_KEY`: OpenAI API key.
  - `S3_VECTORS_AWS_ACCESS_KEY_ID`, `S3_VECTORS_AWS_SECRET_ACCESS_KEY` (and `S3_VECTORS_AWS_SESSION_TOKEN` if using temporary credentials): AWS credentials for S3 Vectors access. For alternatives, see [S3 Vectors documentation](https://spiceai.org/docs/components/vectors/s3_vectors).
- AWS account with an S3 Vectors-enabled bucket (e.g., `spiceai-cookbook` in `us-east-2`).

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
    score -- this is a computed value (i.e. not in `describe pulls;`).
FROM vector_search(pulls, 'bugs in DuckDB', 4)
ORDER BY score DESC
LIMIT 4;
```

Results:

```sql
+----------------------------------------------+----------------------------------------------------------------------+---------------------+
| url                                          | title                                                                | score               |
+----------------------------------------------+----------------------------------------------------------------------+---------------------+
| https://github.com/spiceai/spiceai/pull/6496 | Update spiceai/duckdb-rs -> DuckDB 1.3.2 + index fix                 | 0.6213145852088928  |
| https://github.com/spiceai/spiceai/pull/6491 | Use top-level table in full-text search `JOIN ON`                    | 0.35408276319503784 |
| https://github.com/spiceai/spiceai/pull/6463 | Add integration tests for partitioning                               | 0.3499426245689392  |
| https://github.com/spiceai/spiceai/pull/6499 | Add periodic tracing of data loading progress during dataset refresh | 0.3494341969490051  |
+----------------------------------------------+----------------------------------------------------------------------+---------------------+
```

The `score` column (0-1, higher is more similar) is computed from distances returned by S3 Vectors.

### Query Plan

Examine execution:

```sql
EXPLAIN SELECT url, title, score FROM vector_search(pulls, 'bugs in DuckDB', 4) ORDER BY score DESC LIMIT 4;
```

Plan:

```sql
+---------------+-----------------------------------------------------------------------------------------------------------------------+
| plan_type     | plan                                                                                                                  |
+---------------+-----------------------------------------------------------------------------------------------------------------------+
| logical_plan  | Sort: vector_search().score DESC NULLS FIRST, fetch=4                                                                 |
|               |   Projection: vector_search().url, vector_search().title, vector_search().score                                       |
|               |     BytesProcessedNode                                                                                                |
|               |       TableScan: vector_search() projection=[title, url, score]                                                       |
| physical_plan | SortPreservingMergeExec: [score@2 DESC], fetch=4                                                                      |
|               |   SortExec: TopK(fetch=4), expr=[score@2 DESC], preserve_partitioning=[true]                                          |
|               |     ProjectionExec: expr=[url@1 as url, title@0 as title, score@2 as score]                                           |
|               |       BytesProcessedExec                                                                                              |
|               |         ProjectionExec: expr=[title@1 as title, url@2 as url, score@0 as score]                                       |
|               |           CoalesceBatchesExec: target_batch_size=8192                                                                 |
|               |             CoalesceBatchesExec: target_batch_size=8192                                                               |
|               |               HashJoinExec: mode=Partitioned, join_type=Left, on=[(id@0, id@0)], projection=[score@1, title@3, url@4] |
|               |                 CoalesceBatchesExec: target_batch_size=8192                                                           |
|               |                   RepartitionExec: partitioning=Hash([id@0], 10), input_partitions=10                                 |
|               |                     CoalesceBatchesExec: target_batch_size=8192                                                       |
|               |                       ProjectionExec: expr=[key@0 as id, 1 - distance@1 as score]                                     |
|               |                         RepartitionExec: partitioning=RoundRobinBatch(10), input_partitions=1                         |
|               |                           BytesProcessedExec                                                                          |
|               |                             **S3VectorsQueryExec: limit=4**                                                           |
|               |                 CoalesceBatchesExec: target_batch_size=8192                                                           |
|               |                   RepartitionExec: partitioning=Hash([id@0], 10), input_partitions=10                                 |
|               |                     RepartitionExec: partitioning=RoundRobinBatch(10), input_partitions=1                             |
|               |                       CoalesceBatchesExec: target_batch_size=8192                                                     |
|               |                         BytesProcessedExec                                                                            |
|               |                           SchemaCastScanExec                                                                          |
|               |                             DataSourceExec: partitions=1, partition_sizes=[6]                                         |
|               |                                                                                                                       |
+---------------+-----------------------------------------------------------------------------------------------------------------------+
```

The plan shows `S3VectorsQueryExec` for similarity search, joined via `HashJoinExec` with `DataSourceExec` to fetch fields like `title` and `url`.

### Optimize with Metadata

To avoid joins and push filters, uncomment metadata columns in `spicepod.yaml`:

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

Restart:

```shell
spice run
```

Re-run the `EXPLAIN`:

```sql
EXPLAIN SELECT url, title, score FROM vector_search(pulls, 'bugs in DuckDB', 4) ORDER BY score DESC LIMIT 4;
```

Plan:

```sql
+---------------+----------------------------------------------------------------------------------------+
| plan_type     | plan                                                                                   |
+---------------+----------------------------------------------------------------------------------------+
| logical_plan  | Sort: vector_search().score DESC NULLS FIRST, fetch=4                                  |
|               |   Projection: vector_search().url, vector_search().title, vector_search().score        |
|               |     BytesProcessedNode                                                                 |
|               |       TableScan: vector_search() projection=[title, url, score]                        |
| physical_plan | SortPreservingMergeExec: [score@2 DESC], fetch=4                                       |
|               |   SortExec: TopK(fetch=4), expr=[score@2 DESC], preserve_partitioning=[true]           |
|               |     ProjectionExec: expr=[url@1 as url, title@0 as title, score@2 as score]            |
|               |       BytesProcessedExec                                                               |
|               |         ProjectionExec: expr=[title@0 as title, url@1 as url, 1 - distance@2 as score] |
|               |           RepartitionExec: partitioning=RoundRobinBatch(10), input_partitions=1        |
|               |             BytesProcessedExec                                                         |
|               |               **S3VectorsQueryExec: limit=4**                                          |
|               |                                                                                        |
+---------------+----------------------------------------------------------------------------------------+
```

Now, a single `S3VectorsQueryExec` retrieves all data, avoiding joins.

Filter pushdown example:

```sql
EXPLAIN
SELECT url, title, score
FROM vector_search(pulls, 'bugs in DuckDB', 4)
WHERE state = 'OPEN'
ORDER BY score DESC
LIMIT 4;
```

Plan:

```sql
+---------------+----------------------------------------------------------------------------------------------------------------------+
| plan_type     | plan                                                                                                                  |
+---------------+----------------------------------------------------------------------------------------------------------------------+
| logical_plan  | Sort: vector_search().score DESC NULLS FIRST, fetch=4                                                                 |
|               |   Projection: vector_search().url, vector_search().title, vector_search().score                                       |
|               |     BytesProcessedNode                                                                                                |
|               |       TableScan: vector_search() projection=[title, url, score], full_filters=[vector_search().state = Utf8("OPEN")]  |
| physical_plan | SortPreservingMergeExec: [score@2 DESC], fetch=4                                                                      |
|               |   SortExec: TopK(fetch=4), expr=[score@2 DESC], preserve_partitioning=[true]                                          |
|               |     ProjectionExec: expr=[url@1 as url, title@0 as title, score@2 as score]                                           |
|               |       BytesProcessedExec                                                                                              |
|               |         ProjectionExec: expr=[title@0 as title, url@1 as url, 1 - distance@2 as score]                                |
|               |           RepartitionExec: partitioning=RoundRobinBatch(10), input_partitions=1                                       |
|               |             BytesProcessedExec                                                                                        |
|               |               **S3VectorsQueryExec: filter={state:{$eq:"OPEN"}} limit=4**                                             |
|               |                                                                                                                       |
+---------------+----------------------------------------------------------------------------------------------------------------------+
```

The filter is pushed to `S3VectorsQueryExec`, ensuring accurate top-K results.

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
	"where": "state='\''CLOSED'\''",
	"limit": 4
}'
```

Response:

```json
{
  "results": [
    {
      "matches": {
        "body": "## 📝 Summary\r\n- Update duckdb-rs to point at spiceai duckdb fork: https://github.com/spiceai/duckdb-rs/pull/20\r\n- DuckDB v1.3.2 + [index resolution fix](https://github.com/spiceai/duckdb/compare/v1.3.2...v1.3.2-index-resolution)\r\n"
      },
      "data": {
        "url": "https://github.com/spiceai/spiceai/pull/6496",
        "title": "Update spiceai/duckdb-rs -> DuckDB 1.3.2 + index fix"
      },
      "primary_key": {
        "id": "PR_kwDOF31SUc6fp25h"
      },
      "score": 0.6213145852088928,
      "dataset": "pulls"
    },
    {
      "matches": {
        "body": "## 📝 Summary\r\n\r\n<!-- What does this PR change? Why is it necessary? Keep it concise. -->\r\n\r\n## 🔗 Related\r\n\r\n<!-- Link to relevant issues, discussions, or other PRs. Use \"Closes #123\" to auto-close issues. Omit if none. -->\r\n\r\n## 🚨 Breaking Changes\r\n\r\n<!-- Describe breaking changes if any, or delete this section. -->\r\n<!-- If breaking, make sure the \"breaking change\" label is added. -->\r\n\r\n## 📚 Docs\r\n\r\n<!-- Note any required updates to docs, recipes, or guides. Omit if not applicable. -->\r\n\r\n## 👀 Notes for Reviewers\r\n\r\n<!-- Any areas needing special attention or questions for reviewers? Omitၓ Omit if none. -->\r\n"
      },
      "data": {
        "url": "https://github.com/spiceai/spiceai/pull/6494",
        "title": "v1.5.0 release notes"
      },
      "primary_key": {
        "id": "PR_kwDOF31SUc6fpWVh"
      },
      "score": 0.2575995922088623,
      "dataset": "pulls"
    },
    {
      "matches": {
        "body": "## 📝 Summary\r\n\r\n<!-- What does this PR change? Why is it necessary? Keep it concise. -->\r\n\r\n## 🔗 Related\r\n\r\n<!-- Link to relevant issues, discussions, or other PRs. Use \"Closes #123\" to auto-close issues. Omit if none. -->\r\n\r\n## 🚨 Breaking Changes\r\n\r\n<!-- Describe breaking changes if any, or delete this section. -->\r\n<!-- If breaking, make sure the \"breaking change\" label is added. -->\r\n\r\n## 📚 Docs\r\n\r\n<!-- Note any required updates to docs, recipes, or guides. Omit if not applicable. -->\r\n\r\n## 👀 Notes for Reviewers\r\n\r\n<!-- Any areas needing special attention or questions for reviewers? Omit if none. -->\r\n"
      },
      "data": {
        "url": "https://github.com/spiceai/spiceai/pull/6520",
        "title": "Prepare v1.5.0 release"
      },
      "primary_key": {
        "id": "PR_kwDOF31SUc6fy91T"
      },
      "score": 0.2575995922088623,
      "dataset": "pulls"
    },
    {
      "matches": {
        "body": "## Summary\r\nAdds a new `availability_monitor` configuration option to individual datasets to control whether the dataset availability monitor checks that specific dataset. This provides granular control over which datasets are monitored, preventing unnecessary remote calls that could wake up expensive warehouses.\r\n\r\n- Closes #5676\r\n\r\n## Usage\r\nUsers can now disable availability monitoring for specific datasets that might cause expensive warehouse wake-ups:\r\n\r\n```yaml\r\ndatasets:\r\n  - from: snowflake\r\n    name: expensive_table\r\n    availability_monitor: disabled\r\n  \r\n  - from: file://local_data.csv\r\n    name: local_data\r\n    availability_monitor: default\r\n```\r\n"
      },
      "data": {
        "url": "https://github.com/spiceai/spiceai/pull/6482",
        "title": "Add per-dataset availability monitor configuration"
      },
      "primary_key": {
        "id": "PR_kwDOF31SUc6fT_8S"
      },
      "score": 0.24210351705551147,
      "dataset": "pulls"
    }
  ],
  "duration_ms": 3387
}
```

## Advanced Usage

- **Hybrid Search**: Combine vector and full-text search with `text_search` using Reciprocal Rank Fusion (RRF) in SQL. See [blog post](https://spiceai.org/blog/amazon-s3-vectors-with-spice).
- **Multi-Column Embeddings**: Embed additional fields (e.g., `title`) and weight in queries (e.g., title score \* 2).
- **Re-ranking**: Use keyword search for initial candidates, then vector search for precision.
- **Scaling**: S3 Vectors supports billions of vectors; Spice handles synchronization.
- **Limitations**: ANN provides approximate results; single index per dataset limits multi-embedding columns without ARN.

## References

- [S3 Vectors documentation](https://spiceai.org/docs/components/vectors/s3_vectors)
- [Spice.ai S3 Vectors blog post](https://spiceai.org/blog/amazon-s3-vectors-with-spice)
- [Amazon S3 Vectors](https://aws.amazon.com/s3/vectors/)
