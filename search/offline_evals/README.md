# Offline Search Evals

Works with `v2.5+`.

Spice provides [search within SQL](https://spice.ai/learn/hybrid-search), executed natively in the query engine. Search indexes are defined atop datasets and views in the `spicepod.yaml` and search pipelines run directly in SQL. See the [hybrid search cookbook](../hybrid/README.md) for details.

This cookbook focuses on evaluating search configurations offline. 

## Prerequisites

- Spice CLI `v2.5+`. Follow [Getting Started](https://spiceai.org/docs/getting-started).
- An OpenAI API key, and a TypeSafe API key for step 5.

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/search/offline_evals
cp .env.example .env   # then set OPENAI_API_KEY and TYPESAFE_API_KEY
```

## Step 1. Search a dataset
The root `spicepod.yaml` loads the [MTEB SciFact](https://huggingface.co/datasets/mteb/scifact) corpus, with a full text search index.

```bash
spice run
```

In a second terminal, run a full-text search:

```bash
spice sql
```

```sql
SELECT _id, title, _score FROM text_search(corpus, 'vitamin D deficiency', text, limit => 5);
```

```text
+----------+--------------------------------------------------------------------------------------------------------------------+--------------------+
|    _id   |                                                        title                                                       |       _score       |
+----------+--------------------------------------------------------------------------------------------------------------------+--------------------+
| 23267371 | Vitamin D: The "sunshine" vitamin.                                                                                 | 19.45318603515625  |
| 30720103 | Vitamin D status: measurement, interpretation, and clinical application.                                           | 19.203651428222656 |
| 275294   | Environmental factors that influence the cutaneous production of vitamin D                                         | 18.27470588684082  |
| 21553394 | Vitamin D and obesity: current perspectives and future directions.                                                 | 17.69023323059082  |
| 13312471 | Vitamin D insufficiency and the blunted PTH response in established osteoporosis: the role of magnesium deficiency | 17.42413330078125  |
+----------+--------------------------------------------------------------------------------------------------------------------+--------------------+
```


## Step 2. Add a search pipeline

Keep `spice run` running. In `spicepod.yaml`, uncomment `dependencies:` and `llm_rerank`:

**Before**
```yaml
# dependencies:
#   - llm_rerank
#   - offline_eval
```

**After**
```yaml
dependencies:
  - llm_rerank
#   - offline_eval
```

The spice runtime will load these new components. 
```text
INFO runtime::datafusion::udf: Registered user table function name=search_pipeline from=sql
INFO runtime::init::model: Model [luna] deployed, ready for inferencing
```

Call the pipeline like any table:

```sql
SELECT _id, title, _score FROM search_pipeline('vitamin D deficiency') limit 5;
```

```text
+----------+---------------------------------------------------------------------------------------------------------------------+--------------------+
| _id      | title                                                                                                               | _score             |
+----------+---------------------------------------------------------------------------------------------------------------------+--------------------+
| 21557614 | Pleiotropic effects of statins.                                                                                     | 1.0                |
| 22420524 | Statin use and risk of gallstone disease followed by cholecystectomy.                                               | 0.9900000095367432 |
| 7552215  | Long term pharmacotherapy for obesity and overweight: updated meta-analysis.                                        | 0.9900000095367432 |
| 4687948  | HMG-CoA reductase inhibitors and the risk of hip fractures in elderly patients.                                     | 0.9800000190734863 |
| 13774178 | Metabolomics study of the therapeutic mechanism of Schisandra Chinensis lignans in diet-induced hyperlipidemia mice | 0.9700000286102295 |
+----------+---------------------------------------------------------------------------------------------------------------------+--------------------+
```

## Step 3. Add the offline evaluation

The dataset we have been search upon, is apart of a well known, open source benchmark [MTEB](https://huggingface.co/mteb). Because of this, there are search queries with predefined, correct answers. We can use these questions to measure the impact of adding a reranker model, upgrading the underlying model, or changing rerankers entirely. 

In `spicepod.yaml`, uncomment `offline_eval`:

**Before**
```yaml
dependencies:
  - llm_rerank
#   - offline_eval
```

**After**
```yaml
dependencies:
  - llm_rerank
  - offline_eval
```

This reload will take more time. It will load the MTEB questions and correct answers, then run each question against our `search_pipeline(query)`, and calculating the statistical accuracy of our results. 

The important log line will look similar to (`search_results` completes running, then dependent tables `query_metrics` and `retrieval_metrics` register):
```text
2026-11-28T01:03:58.779514Z  INFO runtime_table::accelerated::refresh_task: Loaded 200 rows (8.66 kiB) for view search_results in 8s 888ms.
2026-11-28T01:03:58.859689Z  INFO runtime::datafusion: View query_metrics registered.
2026-11-28T01:03:59.225252Z  INFO runtime::datafusion: Dependent table query_metrics for view retrieval_metrics found
2026-11-28T01:03:59.228387Z  INFO runtime::datafusion: View retrieval_metrics registered.
```

200 rows is 20 queries, which for each `search_pipeline(query)` produces 10 rows. 

## Step 4. Explore the results
Because the `search_results` are evaluated once, we can explore the results without rerunning any `search_pipeline` requests. 



```sql
SELECT k, ROUND(ndcg, 4) AS ndcg, ROUND(recall, 4) AS recall, ROUND(mrr, 4) AS mrr, ROUND(precision, 4) AS precision
FROM retrieval_metrics
WHERE k IN (1, 3, 5, 10)
ORDER BY k;
```
```
+-------+---------+---------+---------+-----------+
|   k   |   ndcg  |  recall |   mrr   | precision |
| int64 | float64 | float64 | float64 |  float64  |
+-------+---------+---------+---------+-----------+
| 1     | 0.7     | 0.6333  | 0.7     | 0.7       |
| 3     | 0.7396  | 0.7667  | 0.75    | 0.3       |
| 5     | 0.7396  | 0.7667  | 0.75    | 0.18      |
| 10    | 0.7396  | 0.7667  | 0.75    | 0.09      |
+-------+---------+---------+---------+-----------+
```

A mean can hide a lot. How are the queries spread?

```sql
SELECT CASE WHEN ndcg = 1 THEN 'perfect'
            WHEN ndcg >= 0.5 THEN 'good (>= 0.5)'
            WHEN ndcg > 0 THEN 'poor (< 0.5)'
            ELSE 'miss (0)' END AS bucket,
       COUNT(*) AS queries
FROM query_metrics
WHERE k = 10
GROUP BY 1
ORDER BY 2 DESC;
```
```
+---------------+---------+
|     bucket    | queries |
|    varchar    |  int64  |
+---------------+---------+
| perfect       | 12      |
| miss (0)      | 4       |
| good (>= 0.5) | 4       |
+---------------+---------+
```

Which queries find no relevant document in the top 10?

```sql
SELECT m.query_id, q.text AS query
FROM query_metrics m
JOIN eval_queries q ON q.query_id = m.query_id
WHERE m.k = 10 AND m.ndcg = 0
ORDER BY m.query_id;
```
```
+----------+------------------------------------------------------------------------------------------------------+
| query_id |                                                 query                                                |
|  varchar |                                                varchar                                               |
+----------+------------------------------------------------------------------------------------------------------+
| 1        | 0-dimensional biomaterials show inductive properties.                                                |
| 1041     | Replacement of histone H2A with H2A.Z slows gene activation in yeasts by stabilizing +1 nucleosomes. |
+----------+------------------------------------------------------------------------------------------------------+
```

For one query, compare what the search returned with what a person judged relevant (we will use `query_id=1` from above):

```sql
SELECT 'expected' AS kind, CAST(NULL AS BIGINT) AS rank, c.title
FROM relevance_judgments j JOIN corpus c ON c._id = j.corpus_id
WHERE j.query_id = '1'
UNION ALL
SELECT 'returned', r.rank, c.title
FROM search_results r JOIN corpus c ON c._id = r.corpus_id
WHERE r.query_id = '1' AND r.rank <= 3
ORDER BY kind, rank;
```
```
+----------+-------+-------------------------------------------------------------------------------------------------------------------------------------------------+
|   kind   |  rank |                                                                      title                                                                      |
|  varchar | int64 |                                                                     varchar                                                                     |
+----------+-------+-------------------------------------------------------------------------------------------------------------------------------------------------+
| expected |       | New opportunities: the use of nanotechnologies to manipulate and track stem cells.                                                              |
| returned | 1     | A graphene-based platform for induced pluripotent stem cells culture and differentiation.                                                       |
| returned | 2     | In situ regulation of DC subsets and T cells mediates tumor regression in mice.                                                                 |
| returned | 3     | The carboxyl terminus of human cytomegalovirus-encoded 7 transmembrane receptor US28 camouflages agonism by mediating constitutive endocytosis. |
+----------+-------+-------------------------------------------------------------------------------------------------------------------------------------------------+
```

### Task History
The above data exploration solely considers the quality of the search result. There are also non-functional factors an engineer will care about. For example, adding a reranker will increase latency of a search result, and some rerankers more than others.

The `runtime.task_history` table records the history of all the search results we 
Task history records the evaluation: one `acceleration_refresh` task for `search_results`, and one `rerank` task for each query. With `captured_context: full`, a `rerank` task keeps its input (the query), and `captured_output` keeps the reranked rows.

```sql
SELECT task, input, start_time, ROUND(execution_duration_ms) AS duration_ms
FROM runtime.task_history
WHERE trace_id = (
    -- Find the trace assocaited with refreshing the 'search_results' table.
    SELECT trace_id FROM runtime.task_history
    WHERE task = 'acceleration_refresh' AND input = 'search_results'
    ORDER BY start_time DESC LIMIT 1
)
ORDER BY start_time;
```
```
+----------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------+-------------+
|         task         |                                                                            input                                                                            |          start_time         | duration_ms |
|        varchar       |                                                                           varchar                                                                           |     timestamp[ns] (UTC)     |   float64   |
+----------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------+-------------+
| acceleration_refresh | search_results                                                                                                                                              | 2026-11-28T01:03:54.335106Z | 4444.0      |
| rerank               | 0-dimensional biomaterials show inductive properties.                                                                                                       | 2026-11-28T01:03:54.345418Z | 670.0       |
| rerank               | All hematopoietic stem cells segregate their chromosomes randomly.                                                                                          | 2026-11-28T01:03:55.040523Z | 337.0       |
| rerank               | Radioiodine treatment of non-toxic multinodular goitre reduces thyroid volume.                                                                              | 2026-11-28T01:03:55.402249Z | 645.0       |
| rerank               | Rapamycin decreases the concentration of triacylglycerols in fruit flies.                                                                                   | 2026-11-28T01:03:56.074465Z | 626.0       |
| rerank               | Rapid phosphotransfer rates govern fidelity in two component systems                                                                                        | 2026-11-28T01:03:56.725495Z | 422.0       |
| rerank               | Rapid up-regulation and higher basal expression of interferon-induced genes increase survival of granule cell neurons that are infected by West Nile virus. | 2026-11-28T01:03:57.173128Z | 182.0       |
| rerank               | Rapid up-regulation and higher basal expression of interferon-induced genes reduce survival of granule cell neurons that are infected by West Nile virus.   | 2026-11-28T01:03:57.377029Z | 263.0       |
| rerank               | Recurrent mutations occur frequently within CTCF anchor sites adjacent to oncogenes.                                                                        | 2026-11-28T01:03:57.662747Z | 361.0       |

...
```

## Step 5. Change the search pipeline

Lets try a different reranker. 
**Before**
```yaml
dependencies:
  - llm_rerank
  - offline_eval
```

**After**
```yaml
dependencies:
  - jev_rerank
  - offline_eval
```

Because `search_results` are stored in a file-based acceleration, they will not immediately rerun. Rerun them by refreshing the table. 

```bash
spice refresh search_results
```
```
2026-11-28T01:30:07.502919Z  INFO runtime_table::accelerated::refresh_task: Loading data for view search_results
2026-11-28T01:30:10.404736Z  INFO runtime_table::accelerated::refresh_task: Loaded 200 rows (8.66 kiB) for view search_results in 3s 901ms.
```

## Step 7. Compare the results

```sql
SELECT k, ROUND(ndcg, 4) AS ndcg, ROUND(recall, 4) AS recall, ROUND(mrr, 4) AS mrr, ROUND(precision, 4) AS precision
FROM retrieval_metrics
WHERE k IN (1, 3, 5, 10)
ORDER BY k;
```
```
+-------+---------+---------+---------+-----------+
|   k   |   ndcg  |  recall |   mrr   | precision |
| int64 | float64 | float64 | float64 |  float64  |
+-------+---------+---------+---------+-----------+
| 1     | 0.8     | 0.7333  | 0.8     | 0.8       |
| 3     | 0.7765  | 0.7667  | 0.8     | 0.3       |
| 5     | 0.7765  | 0.7667  | 0.8     | 0.18      |
| 10    | 0.7765  | 0.7667  | 0.8     | 0.09      |
+-------+---------+---------+---------+-----------+
```
Compared to above, TypeSafe's model produces higher quality answers

| Metric | Jev    | OpenAI | Diff     | % Change |
|--------|--------|--------|----------|----------|
| NDCG   | 0.7824 | 0.7297 | +0.0527  | +7.22%   |
| Recall | 0.7584 | 0.7333 | +0.0251  | +3.42%   |
| MRR    | 0.8000 | 0.7375 | +0.0625  | +8.47%   |
| Precision | 0.3425 | 0.3175 | +0.0250 | +7.87% |

Similar, we can compare latencies:

```sql
SELECT task, input, start_time, ROUND(execution_duration_ms) AS duration_ms
FROM runtime.task_history
WHERE trace_id = (
    SELECT trace_id FROM runtime.task_history
    WHERE task = 'acceleration_refresh' AND input = 'search_results'
    ORDER BY start_time DESC LIMIT 1
)
ORDER BY start_time;
```
```
+----------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------+-------------+
|         task         |                                                                            input                                                                            |          start_time         | duration_ms |
|        varchar       |                                                                           varchar                                                                           |     timestamp[ns] (UTC)     |   float64   |
+----------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------+-------------+
| acceleration_refresh | search_results                                                                                                                                              | 2026-11-28T01:30:07.502876Z | 2902.0      |
| rerank               | 0-dimensional biomaterials show inductive properties.                                                                                                       | 2026-11-28T01:30:07.567667Z | 233.0       |
| rerank               | All hematopoietic stem cells segregate their chromosomes randomly.                                                                                          | 2026-11-28T01:30:07.819270Z | 217.0       |
| rerank               | Radioiodine treatment of non-toxic multinodular goitre reduces thyroid volume.                                                                              | 2026-11-28T01:30:08.052541Z | 257.0       |
| rerank               | Rapamycin decreases the concentration of triacylglycerols in fruit flies.                                                                                   | 2026-11-28T01:30:08.330879Z | 226.0       |
| rerank               | Rapid phosphotransfer rates govern fidelity in two component systems                                                                                        | 2026-11-28T01:30:08.577551Z | 275.0       |
| rerank               | Rapid up-regulation and higher basal expression of interferon-induced genes increase survival of granule cell neurons that are infected by West Nile virus. | 2026-11-28T01:30:08.872816Z | 341.0       |
| rerank               | Rapid up-regulation and higher basal expression of interferon-induced genes reduce survival of granule cell neurons that are infected by West Nile virus.   | 2026-11-28T01:30:09.221242Z | 225.0       |
| rerank               | Recurrent mutations occur frequently within CTCF anchor sites adjacent to oncogenes.                                                                        | 2026-11-28T01:30:09.471800Z | 274.0       |


... 
```

The new, TypeSafe pipeline takes 263.5 ms on average, compared to OpenAI's 486.0 ms.

## Clean up

Stop `spice run` with `Ctrl+C`. Delete the local data, and restore `spicepod.yaml` to the base spicepod:

```bash
rm -rf .spice
git checkout spicepod.yaml
```

## Learn more

- [Search](https://spiceai.org/docs/features/search)
- [Rerank](https://spiceai.org/docs/features/search/rerank)
- [Decisions](https://spiceai.org/docs/features/large-language-models/decisions)
- [Data acceleration](https://spiceai.org/docs/features/data-acceleration)
