# Full-Text Search with Spice

Works with `v2.0+`

Full-text search uses BM25 scoring to retrieve records matching keywords in indexed columns. This cookbook demonstrates how to configure and query full-text search indexes on markdown files from the Spice cookbook repository.

## Prerequisites

- Install Spice CLI: Follow [Getting Started](https://docs.spiceai.org/getting-started).
- Create a `.env` file in this directory with:
  - `GITHUB_TOKEN`: GitHub personal access token ([guide](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-personal-access-token-classic)).

```bash
echo "GITHUB_TOKEN=your_token_here" > .env
```

## Configuration

The `spicepod.yaml` in this directory configures a dataset of markdown files from the Spice cookbook with full-text search enabled on the `content` column:

```yaml
datasets:
  - from: github:github.com/spiceai/cookbook/files/trunk
    name: cookbook_files
    params:
      github_token: ${secrets:GITHUB_TOKEN}
      include: "**/*.md"
    acceleration:
      enabled: true
    columns:
      - name: content
        full_text_search:
          enabled: true
          row_id:
            - path
```

Key configuration options:

- **`acceleration: enabled: true`**: Required for full-text search. The index is built on the accelerated data.
- **`full_text_search.enabled`**: Enables BM25 indexing on the column.
- **`full_text_search.row_id`**: Specifies the unique identifier column(s) for referencing results. Only needed on one column per dataset.

## Run Spice

Start the Spice runtime:

```shell
spice run
```

Wait for the dataset to load and index:

```shell
2026-01-21T01:00:00.000000Z  INFO runtime::init::dataset: Dataset cookbook_files registered (github:github.com/spiceai/cookbook/files/trunk), acceleration (arrow), results cache enabled.
2026-01-21T01:00:05.000000Z  INFO runtime::accelerated_table::refresh_task: Loaded 104 rows (1.13 MiB) for dataset cookbook_files in 4s.
2026-01-21T01:00:05.100000Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

## Search with SQL

Start the Spice SQL REPL:

```shell
spice sql
```

Verify the dataset is loaded:

```sql
show tables;
```

```
+---------------+--------------+----------------+------------+
| table_catalog | table_schema | table_name     | table_type |
+---------------+--------------+----------------+------------+
| spice         | public       | cookbook_files | BASE TABLE |
| spice         | runtime      | task_history   | BASE TABLE |
+---------------+--------------+----------------+------------+
```

### Basic Full-Text Search

Search for files containing specific keywords:

```sql
SELECT path, _score
FROM text_search(cookbook_files, 'vector search', content)
ORDER BY _score DESC
LIMIT 5;
```

Results (scores may vary):

```
+-------------------------------+--------------------+
| path                          | _score              |
+-------------------------------+--------------------+
| vectors/README.md             | 6.82               |
| search/README.md              | 6.51               |
| search_github_files/README.md | 6.47               |
+-------------------------------+--------------------+
```

### Search for Specific Topics

Find all cookbooks mentioning a particular technology:

```sql
SELECT path, _score
FROM text_search(cookbook_files, 'DuckDB acceleration', content)
ORDER BY _score DESC
LIMIT 5;
```

### Combine with SQL Filters

Full-text search results can be filtered using standard SQL:

```sql
SELECT path, _score
FROM text_search(cookbook_files, 'kubernetes', content)
WHERE path LIKE 'kubernetes/%'
ORDER BY _score DESC
LIMIT 10;
```

### Function Signature

The `text_search()` function:

```sql
text_search(
  table IDENTIFIER,          -- Dataset name (required, unquoted)
  query STRING,              -- Keyword or phrase to search (required)
  col IDENTIFIER,            -- Column name to search (required if multiple indexed columns, unquoted)
  limit INTEGER,             -- Maximum results returned (optional, defaults to 1000)
  include_score BOOLEAN      -- Include relevance scores in results (optional, defaults to TRUE)
)
RETURNS TABLE                -- Original table columns plus a FLOAT column `_score`
```

## Search with HTTP API

Query the `/v1/search` endpoint:

```shell
curl -X POST http://localhost:8090/v1/search \
  -H 'Content-Type: application/json' \
  -d '{
    "datasets": ["cookbook_files"],
    "text": "getting started",
    "additional_columns": ["path"],
    "limit": 5
  }'
```

Response (truncated):

```json
{
  "results": [
    {
      "matches": {
        "content": "... Follow these steps to get started with ..."
      },
      "data": {
        "path": "postgres/rds/README.md"
      },
      "primary_key": {
        "path": "postgres/rds/README.md"
      },
      "_score": 1.41,
      "dataset": "cookbook_files"
    }
  ],
  "duration_ms": 12
}
```

## When to Use Full-Text Search

Full-text search is optimal for:

- **Keyword-based queries**: Users searching for specific terms or phrases
- **Exact matching**: When precise keyword matching matters more than semantic similarity
- **Structured text fields**: Searching titles, tags, names, or other well-defined text

For semantic similarity (finding related content even with different wording), use [vector search](https://docs.spiceai.org/features/search/vector-search). For best results, combine both using [hybrid search with RRF](https://docs.spiceai.org/reference/sql/search#reciprocal-rank-fusion-rrf).

## References

- [Full-Text Search documentation](https://docs.spiceai.org/features/search/full-text)
- [Search SQL Reference](https://docs.spiceai.org/reference/sql/search)
- [Search API Reference](https://docs.spiceai.org/api/HTTP/post-search)
