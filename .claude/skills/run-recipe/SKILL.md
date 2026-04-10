---
name: run-recipe
description: |
  Run a Spice.ai cookbook recipe to completion by following its README instructions.
  Use this skill whenever the user wants to test, run, verify, or execute a cookbook
  recipe — e.g., "run the kafka recipe", "test the localpod recipe", "try out the
  ai recipe", "does the duckdb connector recipe work?". Also trigger when the user
  asks to validate, smoke-test, or QA any recipe in this repository, run all recipes,
  or check which recipes are locally runnable.
allowed-tools:
  - Bash
  - Read
  - Glob
  - Grep
  - Agent
  - AskUserQuestion
---

# Run Cookbook Recipe

You are executing a Spice.ai cookbook recipe end-to-end by following its README.

## Overview

Each recipe in this cookbook is a self-contained demo in its own directory with a
`spicepod.yaml` (Spice config) and `README.md` (step-by-step instructions). Your
job is to follow the README exactly, verify each step produces the expected output,
and report the result.

## Step 1: Identify the recipe

Determine which recipe to run. The user will name it or you can find it:

```
# List all recipes
find . -name spicepod.yaml -maxdepth 3 | sort
```

If the recipe name is ambiguous, ask the user to clarify.

### Batch runs: identifying locally runnable recipes

When asked to run "all recipes" or "all locally runnable recipes", triage by
checking each recipe directory for:

- **Docker dependency**: `compose.yaml`, `docker-compose.yml`, or `Makefile` with
  docker commands. Skip if Docker is not running.
- **API keys / secrets**: `${secrets:...}` in `spicepod.yaml` or `.env.example`
  files. Skip unless a `.env` with the required keys already exists.
- **External databases**: `from:` URIs like `postgres:`, `mysql:`, `mongodb:`,
  `clickhouse:`, `mssql:`, `dynamodb:` etc. require running database servers.
- **Complex infrastructure**: Distributed mode (scheduler/executor), mTLS setup,
  or multi-service architectures. Skip these.

Recipes that use only these data sources are locally runnable:
- `file:` or `file://` (local files)
- `s3://spiceai-public-datasets/` or `s3://spiceai-demo-datasets/` (public S3)
- `duckdb:` with a local `.db` file
- `localpod:` (references another local dataset)
- `https://` public APIs (e.g., TVMaze)

Run locally runnable recipes sequentially, cleaning up between each one. Use tasks
to track progress and report a summary table at the end.

## Step 2: Read and understand the README

Read the recipe's `README.md` in full. Before executing anything, identify:

- **Prerequisites**: Docker, external CLIs (e.g., `duckdb`), API keys
- **Infrastructure**: Does it need `docker compose up` or `make`? Check for
  `compose.yaml`, `docker-compose.yml`, or `Makefile` in the recipe directory.
- **Secrets**: Does it reference `.env` files or API keys? Check for `.env.example`.
- **Steps**: The ordered list of commands and expected outputs.

## Step 3: Check prerequisites

Before running anything:

1. **Spice CLI** -- verify `spice` is installed: `spice version`. If not, install:
   ```bash
   curl https://install.spiceai.org | /bin/bash
   ```

2. **Docker** -- if the recipe has a `compose.yaml` / `docker-compose.yml` / `Makefile`,
   verify Docker is running: `docker info > /dev/null 2>&1`

3. **Secrets** -- if the recipe needs API keys (check `.env.example` or README for
   `SPICE_OPENAI_API_KEY`, `OPENAI_API_KEY`, `GITHUB_TOKEN`, etc.), check if a `.env`
   file already exists in the recipe directory. If not, ask the user to provide the
   required keys before proceeding. Do NOT skip steps that need secrets without
   telling the user.

4. **External tools** -- if the README requires tools like `duckdb`, `psql`, `mysql`,
   etc., verify they're installed.

5. **Port conflicts** -- check if Spice's ports are free:
   ```bash
   lsof -i :50051 -i :8090 -i :9090 2>/dev/null | grep LISTEN
   ```
   If port 8090 is occupied (common with VS Code, dev servers, etc.), don't try to
   kill the process. Instead, use `spiced` directly with an alternate HTTP port
   (see "Starting Spice runtime" below). Ports 50051 (Flight) and 9090 (metrics)
   are less commonly conflicted.

6. **Clean stale acceleration data** -- previous runs may have left DuckDB/SQLite
   files in nested `.spice/` subdirectories that cause schema mismatch errors.
   Clean them recursively (the glob `*.db` misses nested paths like
   `.spice/data/accelerated_duckdb.db`):
   ```bash
   find .spice -name '*.db' -delete 2>/dev/null
   ```

## Step 4: Execute the recipe

Follow the README instructions in order. Key patterns:

### Starting infrastructure (if needed)
```bash
cd <recipe-dir>
docker compose up -d   # or: make
```
Wait for services to be healthy before proceeding.

### Starting Spice runtime

**If port 8090 is free**, use the standard approach:
```bash
cd <recipe-dir>
spice run &>/tmp/spice_<recipe>.log &
```

**If port 8090 is occupied**, use `spiced` directly with an alternate HTTP port.
This is the most reliable approach and avoids port conflicts entirely:
```bash
cd <recipe-dir>
~/.spice/bin/spiced --http 127.0.0.1:8091 &>/tmp/spice_<recipe>.log &
```

Always redirect output to a log file so you can inspect it. Wait for readiness by
checking the log for key markers:
- `Spice Runtime Flight listening on 127.0.0.1:50051` -- Flight endpoint ready
- `Dataset <name> registered` -- datasets being configured
- `Loaded N rows` -- acceleration data loaded
- `All components are loaded. Spice runtime is ready!` -- fully ready

Give it 5-10 seconds for simple recipes, longer for recipes that load large datasets
from S3 (millions of rows can take 10-60+ seconds).

**Note:** Hot-reload of `spicepod.yaml` only works with `spice run`, not with
`spiced` directly. If a recipe requires editing `spicepod.yaml` mid-run (like
`sqlite/accelerator`), either use `spice run` or restart `spiced` after the edit.

### Monitoring data loads

For recipes that accelerate large datasets, monitor loading progress rather than
blindly sleeping:
```bash
# Check the log for completion
grep "Loaded\|All components\|Failed" /tmp/spice_<recipe>.log
```

For long-running loads (S3 datasets with millions of rows), use the Monitor tool
or check the log periodically. Typical load times:
- Local files (CSV, parquet): 1-5 seconds
- Public S3 datasets (~3M rows): 8-20 seconds
- Large S3 datasets with acceleration: 30-120 seconds
- GitHub API with comments: 1-3 minutes (rate-limited)

### Running SQL queries

Pipe queries directly rather than using the interactive REPL:
```bash
echo "SELECT COUNT(*) FROM my_table;" | spice sql
```
This avoids interactive mode issues and captures output cleanly.

If the recipe uses API key authentication, pass the key:
```bash
echo "SELECT 1;" | spice sql --api-key <key>
```

### Running helper scripts
Some recipes have `generate_data.sh` or similar scripts. Run them as documented.

### Comparing output

The README shows expected output for each step. How to compare:

- **Column names and types**: Must match exactly.
- **Row counts for local/static data**: Should match exactly (e.g., 8 products
  from a local CSV, 15 release notes files).
- **Row counts for dynamic/remote data**: May differ from README if the source
  data has changed since the README was written. This is expected -- verify the
  query works and returns reasonable results rather than demanding exact counts.
  Note the variance in your report (e.g., "README says 1.5M rows, got 100 --
  public S3 dataset has changed").
- **Timestamps**: Approximate differences are OK.
- **LLM-generated text**: Will vary -- just verify it returned something reasonable.
- **Query performance**: Accelerated queries should be noticeably faster than
  federated queries. Exact times will vary by machine.

### Handling transient API errors

External data sources (especially GitHub, S3) may return transient errors like
502 Bad Gateway or rate limit warnings. The Spice runtime automatically retries
these. Wait for the retry rather than reporting immediate failure. Only report
failure if the dataset never loads after 2-3 minutes of retries.

GitHub-specific: rate limit warnings during comment fetching are normal and
expected. The `pulls` dataset with `github_include_comments` can take 1-3 minutes
to load due to per-PR comment fetching with rate limits.

## Step 5: Clean up

After the recipe completes (pass or fail):

1. Stop the Spice runtime: `pkill -f spiced`
2. Stop Docker infrastructure if started: `docker compose down` (from recipe dir)
3. Remove any generated `.env` files you created (not ones that already existed)
4. If the recipe asked you to edit `spicepod.yaml`, restore the original content.

## Step 6: Report the result

Summarize what happened:

- **PASSED**: All README steps executed successfully and output matched expectations.
  List the key verifications (e.g., "queried 1000 rows from time_series",
  "AI function returned sentiment analysis").

- **FAILED**: Describe exactly which step failed, what the expected output was,
  and what actually happened. Include the error message or unexpected output.

- **SKIPPED**: If a prerequisite was missing (e.g., no Docker, no API key) and
  the user chose not to provide it, note which steps were skipped and why.

For batch runs, report a summary table:
```
| Recipe | Status | Key Verification |
|--------|--------|-----------------|
| localpod | PASSED | Both datasets loaded 1000 rows |
| github | FAILED | 401 Unauthorized - token expired |
```

## Important guidelines

- **Follow the README literally.** Don't improvise or fix issues silently. If a
  documented command fails, that's a real finding -- report it.
- **Don't modify recipe files** unless the README explicitly instructs you to
  (e.g., "create a .env file with..."). Restore any edits after the run.
- **Timeout awareness.** If `spice run` hangs or a query takes more than 60
  seconds, that's likely a failure. Exception: large dataset loads from S3 can
  legitimately take 1-2 minutes.
- **Multiple recipes.** If asked to run several recipes, run them sequentially,
  cleaning up between each one. Always `pkill -f spiced` between recipes to
  avoid port conflicts.
