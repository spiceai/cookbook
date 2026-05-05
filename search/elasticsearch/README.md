# Elasticsearch Full-Text and Vector Search

Works with `v2.0+`

This recipe demonstrates using Elasticsearch as a unified backend for both **full-text (BM25) search** and **vector (semantic) search** in Spice.ai, wired through the new top-level `search_engines:` configuration. It shows how to:

- Run Elasticsearch locally with Docker Compose
- Generate a sample articles dataset
- Configure a single named `elastic` search engine for both `vector` and `text` kinds
- Automatically write OpenAI embeddings and build text indexes in Elasticsearch on startup
- Run text search, vector search, and hybrid (RRF) queries

## Prerequisites

- [Spice CLI](https://docs.spiceai.org/getting-started) installed
- Docker and Docker Compose installed
- Python 3 installed
- OpenAI API key

## Getting Started

### Step 1: Configure secrets

Create a `.env.local` file in this directory:

```bash
OPENAI_API_KEY=<your-openai-api-key>
```

### Step 2: Start Elasticsearch and generate the sample data

From this recipe directory, start Elasticsearch:

```bash
docker compose up -d
```

In a new terminal, install the Python dependencies and generate the sample dataset:

```bash
pip install pandas pyarrow faker
python generate_data.py --rows 500 --out articles.parquet
```

This creates an `articles.parquet` file used by the recipe.

### Step 3: Start the Spice runtime

Start Spice from this directory:

```bash
spice run
```

On startup, Spice automatically:

1. Resolves the `elastic` search engine defined under `search_engines:` (supports both `vector` and `text` kinds)
2. Creates the `articles_vectors` Elasticsearch index with a `dense_vector` mapping for embeddings
3. Creates the `articles_text` Elasticsearch index with an `english` analyzer for full-text search
4. Loads the article records
5. Computes embeddings using OpenAI `text-embedding-3-small`
6. Bulk indexes vectors and text into Elasticsearch

When startup completes, the `articles` dataset is ready for full-text, vector, and hybrid search queries.

### Step 4: Open the Spice SQL REPL

In a new terminal, start the SQL REPL:

```bash
spice sql
```

## Run Queries

### Text Search (BM25)

Run keyword-based full-text search against the Elasticsearch BM25 index:

```sql
SELECT id, title, category, _score
FROM text_search(
    articles,
    'hybrid search Elasticsearch pgvector',
    content
)
ORDER BY _score DESC
LIMIT 10;
```

```
+-----+----------------------------------------------------------------------+----------------+-----------+
|  id |                                 title                                |    category    |  _score   |
|int32|                                varchar                               |     varchar    |  float64  |
+-----+----------------------------------------------------------------------+----------------+-----------+
| 7   | Hybrid Search with Elasticsearch and pgvector                        | search_engines | 12.853201 |
| 1   | Vector Search Inside PostgreSQL with pgvector                        | databases      |  9.412034 |
| 295 | Full-Text Search Under the Hood: Architecture and Trade-offs         | search_engines |  8.901122 |
+-----+----------------------------------------------------------------------+----------------+-----------+

Time: 0.312451234 seconds. 3 rows.
```

Search by title field:

```sql
SELECT id, title, category, _score
FROM text_search(
    articles,
    'AutoML Kubernetes',
    title
)
ORDER BY _score DESC
LIMIT 10;
```

### Vector Search (Semantic)

Run semantic similarity search over the indexed embeddings:

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
+-----+----------------------------------------------------------------------+----------------+------------+

Time: 0.491752584 seconds. 3 rows.
```

Vector search with a post-filter:

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

### Hybrid Search with RRF

Fuse BM25 and vector results with [Reciprocal Rank Fusion (RRF)](https://spiceai.org/docs/next/features/search#hybrid-search-with-rrf) for the best of both search modes:

```sql
SELECT id, title, category, _fused_score
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
ORDER BY _fused_score DESC
LIMIT 10;
```

```
+-----+---------------------------------------------------------------------+----------------+----------------------+
|  id |                                title                                |    category    |     _fused_score     |
|int32|                               varchar                               |     varchar    |        float64       |
+-----+---------------------------------------------------------------------+----------------+----------------------+
| 7   | Hybrid Search with Elasticsearch and pgvector                       | search_engines | 0.03278688524590164  |
| 1   | Vector Search Inside PostgreSQL with pgvector                       | databases      | 0.03225806451612903  |
| 164 | How Embedding Models Powers Modern Search                           | search_engines | 0.031746031746031744 |
| 295 | Full-Text Search Under the Hood: Architecture and Trade-offs        | search_engines | 0.015625             |
| 78  | Comparing Sparse Retrieval Approaches in 2025                       | search_engines | 0.015384615384615385 |
+-----+---------------------------------------------------------------------+----------------+----------------------+

Time: 0.523841234 seconds. 5 rows.
```

Hybrid search with recency boosting using exponential decay:

```sql
SELECT id, title, category, _fused_score
FROM rrf(
    text_search(articles, 'database performance optimization', content),
    vector_search(articles, 'improving database query speed'),
    join_key => 'id',
    k => 20.0
)
ORDER BY _fused_score DESC
LIMIT 10;
```

## How It Works

The `search_engines:` top-level block defines a named, reusable engine:

```yaml
search_engines:
  - name: elastic
    from: elasticsearch
    kind:
      - vector
      - text
    params:
      endpoint: http://localhost:9200
      user: elastic
      pass: spiceai
```

Datasets reference it by name in `columns[].vectors.engine` and `columns[].full_text_search.engine`:

```yaml
datasets:
  - from: file:./articles.parquet
    name: articles
    params:
      file_format: parquet
    acceleration:
      enabled: true
      engine: arrow
    columns:
      - name: content
        embeddings:
          - from: openai_embeddings
            row_id: id
            chunking:
              enabled: true
              target_chunk_size: 256
              overlap_size: 64
        vectors:
          enabled: true
          engine: elastic         # vector_search() → Elasticsearch kNN
        full_text_search:
          enabled: true
          engine: elastic         # text_search() → Elasticsearch BM25
          row_id:
            - id
      - name: title
        full_text_search:
          enabled: true
          engine: elastic
          row_id:
            - id
```

This means a single Elasticsearch cluster serves all search modalities, keeping infrastructure simple while enabling powerful hybrid queries.

## Learn more

- [Elasticsearch Documentation](https://spiceai.org/docs/components/vectors/elasticsearch)
- [Search Engines Configuration](https://spiceai.org/docs/reference/spicepod/search-engines)
- [Full-Text Search Documentation](https://spiceai.org/docs/features/search/full-text-search)
- [Vector Search Documentation](https://spiceai.org/docs/features/search/vector-search)
- [Hybrid Search with RRF](https://spiceai.org/docs/features/search#hybrid-search-with-rrf)
- [Datasets Reference](https://spiceai.org/docs/reference/spicepod/datasets)
