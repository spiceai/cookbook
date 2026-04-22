# Elasticsearch Data Connector

Works with `v2.0+`

This recipe demonstrates how to query Elasticsearch indices from Spice using federated SQL. It includes:

- `articles` — a federated dataset queried directly from Elasticsearch
- `all_types` — a federated dataset covering supported Elasticsearch field types

The Elasticsearch connector can also power `vector_search`, `text_search`, and `rrf` for indices that contain the required search fields.

## Prerequisites

- [Spice CLI](https://docs.spiceai.org/getting-started) installed
- Docker installed

## Getting Started

### Step 1: Prepare the recipe directory

Change into the recipe directory:

```bash
cd cookbook/elasticsearch/connector
```

### Step 2: Start Elasticsearch and seed the sample indices

Start the local Elasticsearch service and seed the sample data:

```bash
docker compose up
```

Keep this running while you use the recipe.

### Step 3: Start the Spice runtime

In a new terminal, start the Spice runtime:

```bash
spice run
```

### Step 4: Open the Spice SQL REPL

In another terminal, open the Spice SQL REPL:

```bash
spice sql
```

### Step 5: Run a few example queries

Run a few basic federated SQL queries to verify the Elasticsearch datasets are available.

Query the `articles` index:

```sql
SELECT id, title, category, author
FROM articles
WHERE category = 'machine_learning'
LIMIT 10;
```

Inspect one row from the `all_types` index:

```sql
SELECT *
FROM all_types
LIMIT 1;
```

Filter the `all_types` index on a keyword field:

```sql
SELECT id, field_keyword, field_integer
FROM all_types
WHERE field_keyword = 'category_0';
```

## Notes

- `articles` and `all_types` are queried directly from Elasticsearch.
- The connector maps Elasticsearch index mappings to Arrow schemas so the data can be queried with SQL in Spice.
- For indices with compatible search fields, Spice can route `vector_search`, `text_search`, and `rrf` to Elasticsearch.

## Learn more

- [Elasticsearch Data Connector Documentation](https://spiceai.org/docs/components/data-connectors/elasticsearch)
- [Search Functionality Documentation](https://spiceai.org/docs/features/search)
- [Datasets Reference](https://docs.spiceai.org/reference/spicepod/datasets)
- [Spice SQL CLI Reference](https://docs.spiceai.org/cli/reference/sql)
