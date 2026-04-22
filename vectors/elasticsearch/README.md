# Elasticsearch Vector Engine

Works with `v2.0+`

This recipe demonstrates how to use Elasticsearch as a vector engine in Spice.ai. It shows how to:

- Run Elasticsearch locally with Docker Compose
- Generate a sample articles dataset
- Start Spice and automatically write embeddings into Elasticsearch
- Run vector and hybrid search queries that match the generated article titles and content

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
3. Computes embeddings locally using `all-MiniLM-L6-v2`
4. Bulk indexes the vectors into Elasticsearch

When startup completes, the `articles` dataset is ready for vector and hybrid search queries.
Use search prompts that mirror the generated article topics, such as `pgvector`, `Kubernetes`, `AutoML`, and `hybrid search`.

### Step 3: Open the Spice SQL REPL

In a new terminal, start the SQL REPL:

```bash
spice sql
```

## Run Queries

Run semantic similarity search over the indexed embeddings:

```sql
SELECT id, title, category, _score
FROM vector_search(articles, 'pgvector vector databases sql query optimisation', 10)
ORDER BY _score DESC;
```

Run vector search with a post-filter:

```sql
SELECT id, title, category, _score
FROM vector_search(articles, 'kubernetes cost optimisation automl', 10)
WHERE category = 'machine_learning'
ORDER BY _score DESC;
```

Fuse vector and keyword results with [Reciprocal Rank Fusion (RRF)](https://spiceai.org/docs/next/features/search#hybrid-search-with-rrf):

```sql
SELECT id, title, category, fused_score
FROM rrf(
    vector_search(articles, 'hybrid search elasticsearch pgvector'),
    text_search(articles, 'hybrid search elasticsearch pgvector', content),
    join_key => 'id'
)
ORDER BY fused_score DESC
LIMIT 10;
```

## Notes

- The Elasticsearch index is created automatically. No manual mapping step is required.
- Embeddings are generated during the initial dataset refresh.

## Learn more

- [Elasticsearch Vector Engine Documentation](https://spiceai.org/docs/components/vectors/elasticsearch)
- [Vector Search Documentation](https://spiceai.org/docs/features/search/vector-search)
- [Datasets Reference](https://spiceai.org/docs/reference/spicepod/datasets)
