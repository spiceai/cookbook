# Elasticsearch Vector Engine

Works with `v2.0+`

This recipe demonstrates how to use Elasticsearch as a vector engine in Spice.ai. It shows how to:

- Run Elasticsearch locally with Docker Compose
- Generate a sample articles dataset
- Start Spice and automatically write OpenAI embeddings into Elasticsearch
- Run vector and hybrid search queries using meaningful phrases and natural-language questions

## Prerequisites

- [Spice CLI](https://docs.spiceai.org/getting-started) installed
- Docker and Docker Compose installed
- Python 3 installed

## Getting Started

### Step 1: Start Elasticsearch and generate the sample data

From this recipe directory, start Elasticsearch:

```bash
docker compose up
```

In a new terminal, install the Python dependencies and generate the sample dataset:

```bash
pip install pandas pyarrow faker
python generate_data.py --rows 500 --out articles.parquet
```

This creates an `articles.parquet` file used by the recipe.

### Step 2: Start the Spice runtime

Start Spice from this directory:

```bash
spice run
```

On startup, Spice automatically:

1. Creates the `articles_search_engine` Elasticsearch index with a `dense_vector` mapping
2. Loads the article records
3. Computes embeddings using OpenAI `text-embedding-3-small`
4. Bulk indexes the vectors into Elasticsearch

When startup completes, the `articles` dataset is ready for vector and hybrid search queries.
Use phrase-based prompts and natural-language questions that mirror the generated article topics, such as `pgvector`, `Kubernetes`, `AutoML`, and `hybrid search`.

This avoids `dense_vector` mapping conflicts when the embedding dimensions change, such as `384` vs `1536`.

### Step 3: Open the Spice SQL REPL

In a new terminal, start the SQL REPL:

```bash
spice sql
```

## Run Queries

Run semantic similarity search over the indexed embeddings using a phrase-based prompt:

```sql
SELECT id, title, category, _score
FROM vector_search(
    articles,
    'How does pgvector improve SQL query optimisation for vector search?',
    10
)
ORDER BY _score DESC;
```

```
+-----+----------------------------------------------------------------------+----------------+------------+
|  id |                                 title                                |    category    |   _score   |
|int32|                                varchar                               |     varchar    |   float64  |
+-----+----------------------------------------------------------------------+----------------+------------+
| 1   | Vector Search Inside PostgreSQL with pgvector                        | databases      | 0.8442027  |
| 7   | Hybrid Search with Elasticsearch and pgvector                        | search_engines | 0.82845736 |
| 211 | How Vector Databases Impacts Query Performance                       | databases      | 0.78836733 |
| 26  | When to Use choosing Between Sql Query Optimisation and Alternatives | databases      | 0.7725092  |
| 290 | Write-Ahead Logging for High-Throughput Applications                 | databases      | 0.7686081  |
| 83  | Why debugging Slow Queries with In-Memory Databases                  | databases      | 0.76624966 |
+-----+----------------------------------------------------------------------+----------------+------------+

Time: 0.491752584 seconds. 6 rows.
```

Run vector search with a post-filter using a natural-language question:

```sql
SELECT id, title, category, _score
FROM vector_search(
    articles,
    'What are the trade-offs of cost-aware AutoML on Kubernetes?',
    10
)
WHERE category = 'machine_learning'
ORDER BY _score DESC;
```

```
+-----+------------------------------------------------------------+------------------+------------+
|  id |                            title                           |     category     |   _score   |
|int32|                           varchar                          |      varchar     |   float64  |
+-----+------------------------------------------------------------+------------------+------------+
| 6   | Cost-Aware AutoML on Kubernetes                            | machine_learning | 0.8782016  |
| 208 | Benchmarking Transformer Models Across Popular Frameworks  | machine_learning | 0.80589664 |
| 106 | Implementing Generative Adversarial Networks Without a PhD | machine_learning | 0.80574334 |
+-----+------------------------------------------------------------+------------------+------------+

Time: 0.246288086 seconds. 3 rows.
```

Fuse vector and keyword results with [Reciprocal Rank Fusion (RRF)](https://spiceai.org/docs/next/features/search#hybrid-search-with-rrf):

```sql
SELECT id, title, category, fused_score
FROM rrf(
    vector_search(
        articles,
        'How can hybrid search combine Elasticsearch and pgvector effectively?'
    ),
    text_search(
        articles,
        'How can hybrid search combine Elasticsearch and pgvector effectively?',
        content
    ),
    join_key => 'id'
)
ORDER BY fused_score DESC
LIMIT 10;
```

```
+-----+---------------------------------------------------------------------+----------------+----------------------+
|  id |                                title                                |    category    |      fused_score     |
|int32|                               varchar                               |     varchar    |        float64       |
+-----+---------------------------------------------------------------------+----------------+----------------------+
| 7   | Hybrid Search with Elasticsearch and pgvector                       | search_engines | 0.03278688524590164  |
| 1   | Vector Search Inside PostgreSQL with pgvector                       | databases      | 0.03225806451612903  |
| 164 | How Embedding Models Powers Modern Search                           | search_engines | 0.031746031746031744 |
| 148 | Why evaluating Sparse Retrieval: Metrics That Matter                | search_engines | 0.030776515151515152 |
| 21  | Comparing Bi-Encoder Retrieval Approaches in 2025                   | search_engines | 0.02804284323271665  |
| 295 | Full-Text Search Under the Hood: Architecture and Trade-offs        | search_engines | 0.015625             |
| 78  | Comparing Sparse Retrieval Approaches in 2025                       | search_engines | 0.015384615384615385 |
| 264 | Reciprocal Rank Fusion Under the Hood: Architecture and Trade-offs  | search_engines | 0.014925373134328358 |
| 139 | How to Use cross-Encoder Reranking at Scale: Lessons from the Field | search_engines | 0.014705882352941176 |
| 336 | A Developer's Guide to Embedding Models                             | search_engines | 0.014492753623188406 |
+-----+---------------------------------------------------------------------+----------------+----------------------+
```

## Learn more

- [Elasticsearch Vector Engine Documentation](https://spiceai.org/docs/components/vectors/elasticsearch)
- [Vector Search Documentation](https://spiceai.org/docs/features/search/vector-search)
- [Datasets Reference](https://spiceai.org/docs/reference/spicepod/datasets)
