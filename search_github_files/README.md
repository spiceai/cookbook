# Searching GitHub Files

This recipe demonstrates how to create embeddings for GitHub files and perform vector-based searches.

[![Watch the Spice.ai vector search over GitHub files demo](https://img.youtube.com/vi/5y26MveEJ8c/hqdefault.jpg)](https://www.youtube.com/embed/5y26MveEJ8c)

## Prerequisites

- Ensure you have the Spice CLI installed. Follow the [Getting Started](https://docs.spiceai.org/getting-started) if you haven't done so.
- Populate `.env` in the `cookbook/search_github_files` directory.
  - `GITHUB_TOKEN`: With a [personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-personal-access-token-classic).
  - `SPICE_OPENAI_API_KEY`: A valid OpenAI API key (or equivalent).

## SQL Search

1. Start spice runtime:

```shell
git clone https://github.com/spiceai/cookbook # Skip if already cloned
cd cookbook/search_github_files
spice run
```

2. Execute a Basic SQL Query to perform keyword searches within your dataset:

```shell
spice sql
```

Then:

```sql
SELECT COUNT(*) > 0 AS has_matches
FROM spiceai.files
WHERE
    LOWER(content) LIKE '%errors%'
    AND NOT contains(path, 'docs/release_notes');
```


## Utilizing Vector-Based Search

1. In the `spicepod.yaml`, uncomment the `datasets[0].columns[0].embeddings`.
2. Restart the spiced.
3. Wait until vector search is ready:

```shell
for _ in {1..30}; do
    curl -sS --max-time 20 -XPOST http://localhost:8090/v1/search \
        -H "Content-Type: application/json" \
        -d '{"datasets":["spiceai.files"],"text":"testing","where":"not contains(path, '\''docs/release_notes'\'')","limit":1}' >/dev/null 2>&1 && break
    sleep 10
done
```

4. Perform a basic search

```shell
for _ in {1..20}; do
    curl -s --max-time 60 -XPOST http://localhost:8090/v1/search \
            -H "Content-Type: application/json" \
            -d "{
            \"datasets\": [\"spiceai.files\"],
            \"text\": \"testing\",
            \"where\": \"not contains(path, 'docs/release_notes')\",
            \"additional_columns\": [\"download_url\"],
            \"limit\": 1
            }" >/dev/null 2>&1 && break
    sleep 10
done
```

5. Rerun the search, and retrieve the full document by adding `content` column to `additional_columns`).

```shell
curl --retry 10 --retry-delay 5 --retry-all-errors --max-time 180 -XPOST http://localhost:8090/v1/search \
-H 'Content-Type: application/json' \
-d "{
    \"datasets\": [\"spiceai.files\"],
    \"text\": \"errors\",
    \"where\": \"not contains(path, 'docs/release_notes')\",
    \"additional_columns\": [\"download_url\" , \"content\"],
    \"limit\": 1
}"
```

The response includes top matching documents, scores, and the requested `additional_columns`.

## Full Text Search
Spice can build full-text search indexes from dataset columns. Enable full text search at the column level (see `doc.pulls` dataset).

1. In the `spicepod.yaml`, uncomment `datasets[1]` (i.e. `doc.pulls` dataset).
2. Restart the spiced.
3. Warm up full-text search indexing:

```shell
for _ in {1..30}; do
  curl -s --max-time 20 -XPOST http://localhost:8090/v1/search \
      -H "Content-Type: application/json" \
      -d '{"datasets":["doc.pulls"],"text":"Glue data","limit":1}' >/dev/null 2>&1 && break
  sleep 10
done
```

4. Perform a basic search

```shell
for _ in {1..20}; do
  curl -s --max-time 60 -XPOST http://localhost:8090/v1/search \
      -H "Content-Type: application/json" \
      -d '{
          "datasets": ["doc.pulls"],
          "text": "Glue data",
          "limit": 3
      }' && break
  sleep 10
done
```

Note: Only the columns marked `full_text_search.enabled: true` and the table primary keys are stored in the search index.

## Pre-existing embeddings

Spiced can perform vector search on table that already have the required embedding columns. To try this:

1. Run a new `spiced` instance pointing to the currently running `spiced`.

```shell
cd child/
spiced --http 127.0.0.1:8091 --flight 127.0.0.1:50061 --open_telemetry 127.0.0.1:50062
```

2. Rerun the search, this time against the child `spiced` (port `8091`)

```shell
curl --retry 10 --retry-delay 5 --retry-all-errors --max-time 180 -XPOST http://localhost:8091/v1/search \
-H 'Content-Type: application/json' \
-d "{
    \"datasets\": [\"spiceai.files\"],
    \"text\": \"errors\",
    \"where\": \"not contains(path, 'docs/release_notes')\",
    \"additional_columns\": [\"download_url\"],
    \"limit\": 1
}"
```

This request should return a JSON response from the child runtime.
