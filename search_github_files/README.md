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


For vector and full-text search options, see the repository's dedicated search and vectors recipes.

