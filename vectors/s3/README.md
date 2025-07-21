# S3 Vector Engine

Spice can use vector engines to store embeddings for datasets and provide efficient search functionality to the runtime.

In this cookbook, Spice will create a simple vector search system over Github issues.

## Prerequisites

- Ensure you have the Spice CLI installed. Follow the [Getting Started](https://docs.spiceai.org/getting-started) if you haven't done so.
- Populate `.env`:
  - `GITHUB_TOKEN`: With a [personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-personal-access-token-classic).
  - `SPICE_OPENAI_API_KEY`: A valid OpenAI API key (or equivalent).
  - `S3_VECTORS_AWS_ACCESS_KEY_ID`, `S3_VECTORS_AWS_SECRET_ACCESS_KEY` (and `S3_VECTORS_AWS_SESSION_TOKEN` if needed): Access credentials for an AWS account.
    - For alternative AWS authentication methods, see Spice's [S3 vectors](https://spiceai.org/docs/components/vectors/s3_vectors) documentation.

## Search with SQL

1. Using a vector search UDTF, search for recent updates to Spice.
```sql
SELECT
    url,
    title,
    score -- this is a computed value (i.e. not in `describe issues;`).
FROM vector_search(pulls, 'bugs in DuckDB')
ORDER BY score DESC
LIMIT 4;
```

```shell
+----------------------------------------------+----------------------------------------------------------------------+---------------------+
| url                                          | title                                                                | score               |
+----------------------------------------------+----------------------------------------------------------------------+---------------------+
| https://github.com/spiceai/spiceai/pull/6496 | Update spiceai/duckdb-rs -> DuckDB 1.3.2 + index fix                 | 0.6213145852088928  |
| https://github.com/spiceai/spiceai/pull/6491 | Use top-level table in full-text search `JOIN ON`                    | 0.35408276319503784 |
| https://github.com/spiceai/spiceai/pull/6463 | Add integration tests for partitioning                               | 0.3499426245689392  |
| https://github.com/spiceai/spiceai/pull/6499 | Add periodic tracing of data loading progress during dataset refresh | 0.3494341969490051  |
+----------------------------------------------+----------------------------------------------------------------------+---------------------+
```

2. Notice how the above query is returning additional fields that are not in the S3 vector index (i.e. `title`, `url`). Spice is doing the necessary JOINs under the hood (the important lines are `HashJoinExec`, `S3VectorsQueryExec` and `DataSourceExec`).
```sql
EXPLAIN SELECT url, title, score FROM vector_search(pulls, 'bugs in DuckDB') ORDER BY score DESC LIMIT 4;
```
```shell
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
|               |                             S3VectorsQueryExec: limit=100                                                             |
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

3. If there is a column (e.g `title` or `url`) that we might either want to retrieve or filter on frequently when performing vector search, we can add it as a metadata column to the index. Uncomment the following lines in `spicepod.yaml`.
```yaml
columns:
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
4. Restart `spice`
```shell
spice run
```

5. Now, with the same `EXPLAIN` plan, we have a single physical scan to `S3VectorsQueryExec` (i.e. no `HashJoinExec` or `DataSourceExec`).
```sql
EXPLAIN SELECT url, title, score FROM vector_search(pulls, 'bugs in DuckDB') ORDER BY score DESC LIMIT 4;
```

```
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
|               |               S3VectorsQueryExec: limit=100                                            |
|               |                                                                                        |
+---------------+----------------------------------------------------------------------------------------+
```

6. Similarly, some filter patterns can be pushed down to S3 vectors (see `S3VectorsQueryExec` below).
```sql
EXPLAIN
  SELECT
    url,
    title,
    score
  FROM vector_search(pulls, 'bugs in DuckDB')
  WHERE state='OPEN'
  ORDER BY score DESC
  LIMIT 4;
```
```markdown
+---------------+----------------------------------------------------------------------------------------------------------------------+
| plan_type     | plan                                                                                                                 |
+---------------+----------------------------------------------------------------------------------------------------------------------+
| logical_plan  | Sort: vector_search().score DESC NULLS FIRST, fetch=4                                                                |
|               |   Projection: vector_search().url, vector_search().title, vector_search().score                                      |
|               |     BytesProcessedNode                                                                                               |
|               |       TableScan: vector_search() projection=[title, url, score], full_filters=[vector_search().state = Utf8("OPEN")] |
| physical_plan | SortPreservingMergeExec: [score@2 DESC], fetch=4                                                                     |
|               |   SortExec: TopK(fetch=4), expr=[score@2 DESC], preserve_partitioning=[true]                                         |
|               |     ProjectionExec: expr=[url@1 as url, title@0 as title, score@2 as score]                                          |
|               |       BytesProcessedExec                                                                                             |
|               |         ProjectionExec: expr=[title@0 as title, url@1 as url, 1 - distance@2 as score]                               |
|               |           RepartitionExec: partitioning=RoundRobinBatch(10), input_partitions=1                                      |
|               |             BytesProcessedExec                                                                                       |
|               |               S3VectorsQueryExec: filter={state:{$eq:"OPEN"}} limit=100                                              |
|               |                                                                                                                      |
+---------------+----------------------------------------------------------------------------------------------------------------------+
```

## Search via HTTP

Instead of using a vector search UDTF, search can be performed over HTTP.
```shell
curl  -XPOST http://localhost:8090/v1/search \
  -H "Content-Type: application/json" \
  --data @<(cat <<EOF
{
    "datasets": ["pulls"],
    "text": "bugs in DuckDB",
    "additional_columns": ["url", "title"],
    "where": "state='OPEN'",
    "limit": 4
}
EOF
)
```
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
                "body": "## 📝 Summary\r\n\r\n<!-- What does this PR change? Why is it necessary? Keep it concise. -->\r\n\r\n## 🔗 Related\r\n\r\n<!-- Link to relevant issues, discussions, or other PRs. Use \"Closes #123\" to auto-close issues. Omit if none. -->\r\n\r\n## 🚨 Breaking Changes\r\n\r\n<!-- Describe breaking changes if any, or delete this section. -->\r\n<!-- If breaking, make sure the \"breaking change\" label is added. -->\r\n\r\n## 📚 Docs\r\n\r\n<!-- Note any required updates to docs, recipes, or guides. Omit if not applicable. -->\r\n\r\n## 👀 Notes for Reviewers\r\n\r\n<!-- Any areas needing special attention or questions for reviewers? Omit if none. -->\r\n"
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
