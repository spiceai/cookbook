# AGENTS.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is the **Spice.ai OSS Cookbook** — a collection of self-contained "recipes" demonstrating how to use [Spice.ai](https://spiceai.org) for data and AI applications. Each top-level directory is an independent recipe (e.g., `ai/`, `kafka/`, `postgres/`, `cqrs/`).

## Recipe Structure

Every recipe follows the same pattern:

- `spicepod.yaml` — Spice.ai configuration file defining datasets, models, views, and acceleration settings
- `README.md` — Step-by-step instructions to run the recipe
- Optional: `docker-compose.yml` / `compose.yaml`, `Makefile`, `.env.example`, data files, helper scripts

Recipes are **not interdependent** — each can be run in isolation from its own directory.

## Key Concepts in spicepod.yaml

- **Datasets** (`datasets:`): Data sources with a `from:` URI (e.g., `postgres:`, `s3://`, `file:`, `duckdb:`) and optional `acceleration:` block for local materialization
- **Models** (`models:`): LLM configurations (e.g., `from: openai:gpt-4o-mini`) with API key references via `${secrets:KEY_NAME}`
- **Views** (`views:`): SQL-defined virtual tables
- **Catalogs** (`catalogs:`): Connectors to external catalog systems (Databricks Unity, Iceberg, Glue)
- Secrets are loaded from `.env` files using `${secrets:VAR_NAME}` or `${env:VAR_NAME}` syntax

## Running a Recipe

```bash
# Install Spice CLI
curl https://install.spiceai.org | /bin/bash

# Run any recipe
cd <recipe-dir>
spice run          # starts the Spice runtime (spiced)
spice sql          # opens interactive SQL REPL against the running instance
```

Some recipes require Docker infrastructure — check for `Makefile`, `docker-compose.yml`, or `compose.yaml`:

```bash
make              # or docker compose up -d
spice run
```

Spice runtime listens on:

- **50051** — Arrow Flight (primary query protocol)
- **8090** — HTTP API
- **9090** — OpenTelemetry metrics

## CI / Testing

Tests use a reusable GitHub Actions workflow (`.github/workflows/codex-test-reusable.yml`) that:

1. Installs the Spice CLI
2. Uses Codex CLI to execute each recipe's README instructions verbatim
3. Parses output for `TEST PASSED` / `TEST FAILED`

To add a new testable recipe:

1. Create `.github/workflows/codex-test-<name>.yml` calling the reusable workflow
2. Register it in `.github/workflows/spice-qa.yml` under the appropriate matrix (`trigger-simple-recipes` for no secrets, `trigger-secrets-recipes` for API-key-dependent recipes)

The `spice-qa.yml` orchestrator runs weekly and can be triggered manually with version and secrets options.

## Shared Data

The `data/` directory contains CSV files (e.g., `taxi_zone_lookup.csv`, `customer_feedback.csv`) referenced by multiple recipes via relative paths like `file:../data/filename.csv`.

## When Adding or Modifying Recipes

- Each recipe must be self-contained with its own `spicepod.yaml` and `README.md`
- READMEs should include exact CLI commands and expected output — they serve as both documentation and test scripts
- Use `.env.example` to document required secrets; actual `.env` files are gitignored
- The `spicepod.yaml` format is `version: v1`, `kind: Spicepod`
- Prefer public datasets (e.g., `s3://spiceai-public-datasets/`) for recipes that don't require external credentials
- Write for new users, as described in [Writing for New Users](#writing-for-new-users)

## Writing for New Users

The cookbook is where new users, many of them junior engineers, first learn Spice. Write every README, spicepod comment, script, and `.env.example` for a reader who has not read the Spice source or its pull requests.

- Name the release a reader needs, such as `Works with v2.4+`. Do not reference pull requests, commits, merge dates, or `trunk` in recipe text unless a step cannot be followed without one. A reader can install a release, not a pull request.
- Describe what the latest release does, and leave out behavior that exists only on `trunk` until a release ships it. When a recipe cannot work without an unreleased feature, say that no release includes it yet, give the steps to get a build that does, and change the note to the release version once one ships.
- For a known bug the reader will hit, describe the symptom and the workaround in plain words, and link the open issue as the place to follow the fix. When a release fixes the bug, name that release or remove the note.
- Put the evidence for a change (the pull request that changed a behavior, a link to source code, the release notes) in the pull request description, where reviewers read it, not in the recipe.
- Leave references that are data as they are: GitHub URLs in a recipe that queries GitHub, a pinned model or dataset revision, and log lines in captured output.
- Define a term a newcomer would not know where it first appears, or link the docs page that explains it. Keep internal names, such as crate names, code paths, and the library behind a feature, out of the text unless the reader acts on them.
- Title a pull request by what a reader of the recipe saw, for example `Fix huggingface recipe: v2.4.1 ignores HUGGING_FACE_HUB_TOKEN`, not by the pull request that caused it.

For example, write "No Spice release includes the llama.cpp GGUF engine yet; until one does, follow the build steps under Prerequisites" instead of "Works with builds that include spiceai/spiceai#7864, merged to trunk on 2026-10-24."
