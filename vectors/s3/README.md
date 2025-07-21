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
FROM vector_search(issues, 'new software releases')
ORDER BY score DESC
LIMIT 4;
```

```shell
+------------------------------------------------+----------------------------------------------------------------+--------------------+
| url                                            | title                                                          | score              |
+------------------------------------------------+----------------------------------------------------------------+--------------------+
| https://github.com/spiceai/spiceai/issues/6493 | v1.5.0 Endgame                                                 | 0.3843652009963989 |
| https://github.com/spiceai/spiceai/issues/6400 | v1.5.0-rc.2 Endgame                                            | 0.3777492642402649 |
| https://github.com/spiceai/spiceai/issues/6476 | v1.5.0-rc.3 Endgame                                            | 0.3593345880508423 |
| https://github.com/spiceai/spiceai/issues/4035 | Enhancement: Spice.ai Cloud Platform Data Connector 1.0 Stable | 0.3318648338317871 |
+------------------------------------------------+----------------------------------------------------------------+--------------------+
```

2. Notice how the above query is returning additional fields that are not in the S3 vector index (i.e. `title`, `url`). Spice is doing the necessary JOINs under the hood (the important lines are `HashJoinExec`, `S3VectorsQueryExec` and `DataSourceExec`).
```sql
EXPLAIN SELECT url, title, score FROM vector_search(issues, 'new software releases') ORDER BY score DESC LIMIT 4;
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
|               |                           ProjectionExec: expr=[id@0 as id, title@2 as title, url@3 as url]                           |
|               |                             DataSourceExec: partitions=1, partition_sizes=[10]                                        |
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
EXPLAIN SELECT url, title, score FROM vector_search(issues, 'new software releases') ORDER BY score DESC LIMIT 4;
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
  FROM vector_search(issues, 'new software releases')
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
curl -XPOST http://localhost:8090/v1/search \
  -H "Content-Type: application/json" \
  -d '{
      "datasets": ["issues"],
      "text": "new software releases",
      "additional_columns": ["url", "title"]
      "where": "state='OPEN'",
      "limit": 4
  }'
```
```json
```
