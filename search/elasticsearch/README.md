# Elasticsearch Full-Text and Vector Search

Works with `v2.0+`

This recipe demonstrates using Elasticsearch as a unified backend for both **full-text (BM25) search** and **vector (semantic) search** in Spice.ai, configured directly on each dataset and column. It shows how to:

- Run Elasticsearch locally with Docker Compose
- Generate a sample articles dataset
- Configure Elasticsearch engines directly on datasets and columns using YAML anchors
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
ELASTIC_USER=elastic
ELASTIC_PASS=<your-elasticsearch-password>
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

1. Resolves the Elasticsearch engine configured directly on the dataset's `vectors:` and `full_text_search:` blocks
2. Creates the `vector_index` Elasticsearch index with a `dense_vector` mapping for embeddings
3. Creates the `fts_index` Elasticsearch index with an `english` analyzer for full-text search
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
+-----+---------------------------------------------------------------------+----------------+-----------+
|  id |                                title                                |    category    |   _score  |
|int32|                               varchar                               |     varchar    |  float64  |
+-----+---------------------------------------------------------------------+----------------+-----------+
| 7   | Hybrid Search with Elasticsearch and pgvector                       | search_engines | 27.13612  |
| 1   | Vector Search Inside PostgreSQL with pgvector                       | databases      | 11.930085 |
| 164 | How Embedding Models Powers Modern Search                           | search_engines | 10.111884 |
| 295 | Full-Text Search Under the Hood: Architecture and Trade-offs        | search_engines | 10.098769 |
| 78  | Comparing Sparse Retrieval Approaches in 2025                       | search_engines | 10.047134 |
| 148 | Why evaluating Sparse Retrieval: Metrics That Matter                | search_engines | 10.047134 |
| 264 | Reciprocal Rank Fusion Under the Hood: Architecture and Trade-offs  | search_engines | 10.03161  |
| 139 | How to Use cross-Encoder Reranking at Scale: Lessons from the Field | search_engines | 9.900897  |
| 336 | A Developer's Guide to Embedding Models                             | search_engines | 9.7990885 |
| 281 | Comparing Hnsw Graphs Approaches in 2025                            | search_engines | 9.631344  |
+-----+---------------------------------------------------------------------+----------------+-----------+

Time: 0.067911779 seconds. 10 rows.
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

```
+-----+--------------------------------------------------------------------+----------------------+------------+
|  id |                                title                               |       category       |   _score   |
|int32|                               varchar                              |        varchar       |   float64  |
+-----+--------------------------------------------------------------------+----------------------+------------+
| 6   | Cost-Aware AutoML on Kubernetes                                    | machine_learning     | 10.5090885 |
| 117 | Benchmarking Automl Across Popular Frameworks                      | machine_learning     | 5.863331   |
| 147 | How Automl Is Transforming AI Applications                         | machine_learning     | 5.5187984  |
| 310 | Security Considerations for Kubernetes Orchestration               | cloud_infrastructure | 4.645757   |
| 2   | Running Elasticsearch on Kubernetes: Lessons Learned               | cloud_infrastructure | 4.3727703  |
| 171 | Automating Kubernetes Orchestration with Modern Tooling            | cloud_infrastructure | 4.3727703  |
| 105 | Building Self-Service Infrastructure with Kubernetes Orchestration | cloud_infrastructure | 4.130084   |
| 408 | Why kubernetes Orchestration in Practice: Real-World Patterns      | cloud_infrastructure | 3.9129195  |
| 193 | When to Use kubernetes Orchestration for Platform Engineers        | cloud_infrastructure | 3.9129195  |
| 19  | How We Cut Costs by Optimising Kubernetes Orchestration            | cloud_infrastructure | 3.9129195  |
+-----+--------------------------------------------------------------------+----------------------+------------+

Time: 0.032008497 seconds. 10 rows.
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
| 1   | Vector Search Inside PostgreSQL with pgvector                        | databases      | 0.84424317 |
| 7   | Hybrid Search with Elasticsearch and pgvector                        | search_engines | 0.82845736 |
| 211 | How Vector Databases Impacts Query Performance                       | databases      | 0.78835374 |
| 26  | When to Use choosing Between Sql Query Optimisation and Alternatives | databases      | 0.7725092  |
| 290 | Write-Ahead Logging for High-Throughput Applications                 | databases      | 0.7686081  |
| 83  | Why debugging Slow Queries with In-Memory Databases                  | databases      | 0.76624966 |
+-----+----------------------------------------------------------------------+----------------+------------+

Time: 0.573422185 seconds. 6 rows.
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
| 6   | Cost-Aware AutoML on Kubernetes                            | machine_learning | 0.8782172  |
| 208 | Benchmarking Transformer Models Across Popular Frameworks  | machine_learning | 0.80589664 |
| 106 | Implementing Generative Adversarial Networks Without a PhD | machine_learning | 0.80570924 |
+-----+------------------------------------------------------------+------------------+------------+

Time: 0.274407607 seconds. 3 rows.
```

### Hybrid Search with RRF

Fuse BM25 and vector results with [Reciprocal Rank Fusion (RRF)](https://spiceai.org/docs/features/search#hybrid-search-with-rrf) for the best of both search modes:

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
| 148 | Why evaluating Sparse Retrieval: Metrics That Matter                | search_engines | 0.030776515151515152 |
| 21  | Comparing Bi-Encoder Retrieval Approaches in 2025                   | search_engines | 0.02804284323271665  |
| 295 | Full-Text Search Under the Hood: Architecture and Trade-offs        | search_engines | 0.015625             |
| 78  | Comparing Sparse Retrieval Approaches in 2025                       | search_engines | 0.015384615384615385 |
| 264 | Reciprocal Rank Fusion Under the Hood: Architecture and Trade-offs  | search_engines | 0.014925373134328358 |
| 139 | How to Use cross-Encoder Reranking at Scale: Lessons from the Field | search_engines | 0.014705882352941176 |
| 336 | A Developer's Guide to Embedding Models                             | search_engines | 0.014492753623188406 |
+-----+---------------------------------------------------------------------+----------------+----------------------+

Time: 0.452906543 seconds. 10 rows.
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

```
+-----+--------------------------------------------------------------+-----------+----------------------+
|  id |                             title                            |  category |     _fused_score     |
|int32|                            varchar                           |  varchar  |        float64       |
+-----+--------------------------------------------------------------+-----------+----------------------+
| 397 | How to Use choosing Between Foundationdb and Alternatives    | databases | 0.08051529790660225  |
| 240 | Debugging Slow Queries with B-Tree Indexes                   | databases | 0.07670454545454546  |
| 266 | Database Connection Pooling for High-Throughput Applications | databases | 0.07261904761904761  |
| 276 | How B-Tree Indexes Impacts Query Performance                 | databases | 0.06666666666666667  |
| 435 | How Lsm-Tree Storage Impacts Query Performance               | databases | 0.06325581395348837  |
| 53  | How Distributed Databases Impacts Query Performance          | databases | 0.06285178236397748  |
| 83  | Why debugging Slow Queries with In-Memory Databases          | databases | 0.052655677655677656 |
| 15  | How to Use time-Series Databases Internals Explained         | databases | 0.047619047619047616 |
| 186 | Columnar Databases for High-Throughput Applications          | databases | 0.046102932785575715 |
| 380 | Production Lessons from Running Newsql at Scale              | databases | 0.045454545454545456 |
+-----+--------------------------------------------------------------+-----------+----------------------+

Time: 0.351917263 seconds. 10 rows.
```

## Elasticsearch Ingestion Tuning

Spice exposes a set of Elasticsearch-specific parameters that control how data is written to the index during acceleration. These are useful for optimising bulk-load throughput on large datasets.

| Parameter | Description |
|---|---|
| `number_of_shards` | Number of primary shards created with the index. Only applied at index creation time. More shards allow parallel writes but increase overhead. |
| `number_of_replicas` | Number of replica shards. Setting to `0` during initial load eliminates replication overhead; restore after load for resilience. |
| `refresh_interval` | How often Elasticsearch refreshes the index to make new documents searchable. Only applied at index creation time. Use larger values (e.g. `30s`) to trade search freshness for write throughput. |
| `bulk_load_refresh_interval` | Temporarily overrides `refresh_interval` for the duration of a Spice acceleration write (full or append). Set to `-1` to disable refresh entirely during the write, then restore after. This is the most impactful single tuning for bulk-load speed. |
| `force_merge_after_write` | When `true`, triggers an Elasticsearch `_forcemerge` after each acceleration write completes. Reduces segment count, improving query performance at the cost of extra CPU/IO post-write. |
| `force_merge_segments` | Target number of segments after force-merge. Defaults to `1` when `force_merge_after_write` is `true`. Fewer segments = faster queries. |
| `batch_write_rows` | Number of documents sent per bulk request to Elasticsearch. Larger batches reduce HTTP overhead; too large may hit memory limits. Default: `1000`. |
| `index_settings` | Arbitrary index settings as a JSON string, applied at index creation time. Use for advanced settings such as `codec`, `similarity`, or custom analyzers. |

### Testing ingestion tuning

The `spicepod.yaml` in this recipe includes a ready-to-use `x-elasticsearch-fts-tuned` anchor that enables all ingestion controls. To test it, replace the `&elasticsearch_fts` anchor reference with `&elasticsearch_fts_tuned` for the dataset-level and column-level `full_text_search:` entries.

First, add this anchor to your `spicepod.yaml` alongside the existing ones:

```yaml
x-elasticsearch-fts-tuned: &elasticsearch_fts_tuned
  enabled: true
  engine: elasticsearch
  params:
    elasticsearch_endpoint: http://localhost:9200
    elasticsearch_user: ${secrets:ELASTIC_USER}
    elasticsearch_pass: ${secrets:ELASTIC_PASS}
    elasticsearch_index: fts_index_tuned   # separate index to avoid conflicts
    number_of_shards: 2
    number_of_replicas: 0
    refresh_interval: 1s
    bulk_load_refresh_interval: "-1"       # disable refresh during bulk load
    force_merge_after_write: true
    force_merge_segments: 1
    batch_write_rows: 500
    index_settings: '{"index":{"codec":"best_compression"}}'
```

Then switch the dataset and columns to use the tuned anchor:

```yaml
    full_text_search:
      <<: *elasticsearch_fts_tuned          # was: *elasticsearch_fts

    columns:
      - name: content
        full_text_search:
          <<: *elasticsearch_fts_tuned      # was: *elasticsearch_fts
          row_id:
            - id

      - name: title
        full_text_search:
          <<: *elasticsearch_fts_tuned      # was: *elasticsearch_fts
          row_id:
            - id
```

Restart Spice to apply the new index configuration:

```bash
spice run
```

Spice will create a fresh `fts_index_tuned` index using the tuned settings and bulk-index all documents. Once ready, run the same text search queries as before — results should be identical, with faster indexing observed in the startup logs:

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

## How It Works

Engines are configured directly on each dataset and column. YAML anchors (`&elasticsearch_fts`, `&elasticsearch_vectors`) are used to define reusable engine configs and avoid repetition:

```yaml
x-elasticsearch-fts: &elasticsearch_fts
  enabled: true
  engine: elasticsearch
  params:
    elasticsearch_endpoint: http://localhost:9200
    elasticsearch_user: ${secrets:ELASTIC_USER}
    elasticsearch_pass: ${secrets:ELASTIC_PASS}
    elasticsearch_index: fts_index

x-elasticsearch-vectors: &elasticsearch_vectors
  enabled: true
  engine: elasticsearch
  params:
    elasticsearch_endpoint: http://localhost:9200
    elasticsearch_user: ${secrets:ELASTIC_USER}
    elasticsearch_pass: ${secrets:ELASTIC_PASS}
    elasticsearch_index: vector_index
    elasticsearch_vector_field: content_embedding
```

Datasets reference these anchors directly in `vectors:` and `full_text_search:` blocks. Because all params — including credentials — are defined in the anchors, each usage site is a simple reference with no repetition:

```yaml
datasets:
  - from: file:./articles.parquet
    name: articles
    params:
      file_format: parquet
    acceleration:
      enabled: true
      engine: arrow

    vectors: *elasticsearch_vectors

    columns:
      - name: content
        embeddings:
          - from: openai_embeddings
            row_id:
              - id
            chunking:
              enabled: true
              target_chunk_size: 256
              overlap_size: 64
        full_text_search:
          <<: *elasticsearch_fts
          row_id:
            - id

      - name: title
        full_text_search:
          <<: *elasticsearch_fts
          row_id:
            - id
```

This means a single Elasticsearch cluster serves all search modalities, keeping infrastructure simple while enabling powerful hybrid queries.

## Learn more

- [Elasticsearch Documentation](https://spiceai.org/docs/components/vectors/elasticsearch)

- [Full-Text Search Documentation](https://spiceai.org/docs/features/search/full-text)
- [Vector Search Documentation](https://spiceai.org/docs/features/search/vector-search)
- [Hybrid Search with RRF](https://spiceai.org/docs/features/search#hybrid-search-with-rrf)
- [Datasets Reference](https://spiceai.org/docs/reference/spicepod/datasets)
