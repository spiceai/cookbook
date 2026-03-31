---
name: run-recipe
description: |
  Run a Spice.ai cookbook recipe to completion by following its README instructions.
  Use this skill whenever the user wants to test, run, verify, or execute a cookbook
  recipe — e.g., "run the kafka recipe", "test the localpod recipe", "try out the
  ai recipe", "does the duckdb connector recipe work?". Also trigger when the user
  asks to validate, smoke-test, or QA any recipe in this repository.
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

## Step 2: Read and understand the README

Read the recipe's `README.md` in full. Before executing anything, identify:

- **Prerequisites**: Docker, external CLIs (e.g., `duckdb`), API keys
- **Infrastructure**: Does it need `docker compose up` or `make`? Check for
  `compose.yaml`, `docker-compose.yml`, or `Makefile` in the recipe directory.
- **Secrets**: Does it reference `.env` files or API keys? Check for `.env.example`.
- **Steps**: The ordered list of commands and expected outputs.

## Step 3: Check prerequisites

Before running anything:

1. **Spice CLI** — verify `spice` is installed: `spice version`. If not, install it:
   ```bash
   curl https://install.spiceai.org | /bin/bash
   ```

2. **Docker** — if the recipe has a `compose.yaml` / `docker-compose.yml` / `Makefile`,
   verify Docker is running: `docker info > /dev/null 2>&1`

3. **Secrets** — if the recipe needs API keys (check `.env.example` or README for
   `SPICE_OPENAI_API_KEY`, `OPENAI_API_KEY`, etc.), check if a `.env` file already
   exists in the recipe directory. If not, ask the user to provide the required keys
   before proceeding. Do NOT skip steps that need secrets without telling the user.

4. **External tools** — if the README requires tools like `duckdb`, `psql`, `mysql`,
   etc., verify they're installed.

## Step 4: Execute the recipe

Follow the README instructions in order. Key patterns:

### Starting infrastructure (if needed)
```bash
cd <recipe-dir>
docker compose up -d   # or: make
```
Wait for services to be healthy before proceeding.

### Starting Spice runtime
```bash
cd <recipe-dir>
spice run &
```
Run `spice run` in the background. Wait for the runtime to be ready — look for
log lines like `Spice Runtime Flight listening on 127.0.0.1:50051` and dataset
registration messages. Give it up to 30 seconds.

### Running SQL queries
The README will show queries to run via `spice sql`. Rather than using the
interactive REPL, pipe queries directly:
```bash
echo "SELECT COUNT(*) FROM my_table;" | spice sql
```
This avoids interactive mode issues and captures output cleanly.

### Running helper scripts
Some recipes have `generate_data.sh` or similar scripts. Run them as documented.

### Comparing output
The README shows expected output for each step. Compare actual output to expected.
Exact row counts matter. Column names and types matter. Approximate timestamp
differences are OK. LLM-generated text content will vary — just verify it returned
something reasonable.

## Step 5: Clean up

After the recipe completes (pass or fail):

1. Stop the Spice runtime: `pkill -f spiced` or `kill %1`
2. Stop Docker infrastructure if started: `docker compose down` (from recipe dir)
3. Remove any generated `.env` files you created (not ones that already existed)

## Step 6: Report the result

Summarize what happened:

- **PASSED**: All README steps executed successfully and output matched expectations.
  List the key verifications (e.g., "queried 1000 rows from time_series",
  "AI function returned sentiment analysis").

- **FAILED**: Describe exactly which step failed, what the expected output was,
  and what actually happened. Include the error message or unexpected output.

- **SKIPPED**: If a prerequisite was missing (e.g., no Docker, no API key) and
  the user chose not to provide it, note which steps were skipped and why.

## Important guidelines

- **Follow the README literally.** Don't improvise or fix issues silently. If a
  documented command fails, that's a real finding — report it.
- **Don't modify recipe files** unless the README explicitly instructs you to
  (e.g., "create a .env file with...").
- **Timeout awareness.** If `spice run` hangs or a query takes more than 60
  seconds, that's likely a failure. Don't wait forever.
- **Port conflicts.** Spice uses ports 50051, 8090, 9090. If something is already
  using them, stop it first or report the conflict.
- **Multiple recipes.** If asked to run several recipes, run them sequentially,
  cleaning up between each one. Report results for each.
