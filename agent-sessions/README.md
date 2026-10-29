# Coding Agent Sessions

Works with `v2.4+`

Query your local [Claude Code](https://docs.claude.com/en/docs/claude-code/overview) and [Codex](https://developers.openai.com/codex/cli) history with SQL. Each coding agent writes its sessions to JSONL files in your home directory. These Spicepods load the files with the [File Data Connector](https://spiceai.org/docs/components/data-connectors/file), parse them into views (sessions, turns, tool calls, shell commands, token usage), and add a [full-text search](https://spiceai.org/docs/features/search/full-text-search) index on the messages.

| Spicepod                                       | Reads        | Main views                                                                                |
| ---------------------------------------------- | ------------ | ----------------------------------------------------------------------------------------- |
| [`claude-code/spicepod.yaml`](./claude-code/spicepod.yaml) | `~/.claude/` | `sessions`, `turns`, `tool_runs`, `commands`, `files_touched`, `interruptions`, `messages`, `memories` |
| [`codex/spicepod.yaml`](./codex/spicepod.yaml)             | `~/.codex/`  | `sessions`, `threads`, `turns`, `tool_runs`, `commands`, `files_touched`, `token_usage`, `rate_limits`, `messages`, `memories` |

Each view has a comment in its Spicepod that tells what its rows are.

## Prerequisites

- Spice.ai CLI installed (see [Getting Started](https://spiceai.org/docs/getting-started)).
- This cookbook cloned to your computer.
- Claude Code or Codex used on this computer, so that `~/.claude/projects/` or `~/.codex/sessions/` has session files.

## Run Spice from your home directory

The Spicepods use paths relative to your home directory (for example `file:.claude/projects/`). Spice does not expand `~` in a `from:` path, and resolves a relative path from the directory where Spice starts. Thus, you must start Spice from `~`.

Spice runs one runtime per directory. Thus, you can run only one of these Spicepods at a time.

The views read your session files and do not change them. The Codex Spicepod opens two Codex SQLite databases through DuckDB, which creates `-wal` and `-shm` files next to each database. This is safe while Codex runs.

## Claude Code

### Step 1: Start Spice

From the root of this cookbook, run:

```shell
POD="$PWD/agent-sessions/claude-code/spicepod.yaml"
cd ~ && spice run "$POD"
```

Spice loads your transcripts into memory. When it is ready, the log shows `All components are loaded. Spice runtime is ready!`. Spice watches `~/.claude/projects/`, so new messages show in queries while you work.

### Step 2: Query your sessions

In a new terminal, start the SQL REPL:

```shell
spice sql
```

The tools that Claude Code calls most:

```sql
SELECT tool, count(*) AS calls FROM tool_calls GROUP BY tool ORDER BY calls DESC LIMIT 5;
```

The number of sessions, their total cost in USD, and the number of tool calls that failed:

```sql
SELECT count(*) AS sessions, round(sum(total_cost_usd), 2) AS cost_usd, sum(tool_errors) AS tool_errors FROM sessions;
```

Shell commands that failed, and the number of sessions they occurred in:

```sql
SELECT count(*) AS failed, count(DISTINCT session_id) AS sessions FROM commands WHERE exit_code > 0;
```

Search your prompts and Claude's replies:

```sql
SELECT role, ts, substr(text, 1, 80) AS text FROM text_search(messages, 'flaky test', 5);
```

Your auto-memory files, with their frontmatter parsed:

```sql
SELECT name, type, description FROM memories WHERE name IS NOT NULL LIMIT 5;
```

### Step 3: Stop Spice

Stop the Spice runtime with `Ctrl+C`. Spice keeps the data in memory, so there is nothing to clean up.

## Codex

### Step 1: Start Spice

If the Claude Code Spicepod is running, stop it first. From the root of this cookbook, run:

```shell
POD="$PWD/agent-sessions/codex/spicepod.yaml"
cd ~ && spice run "$POD"
```

On the first run, DuckDB downloads its `sqlite` extension to read the Codex databases.

### Step 2: Query your sessions

In a new terminal, start the SQL REPL:

```shell
spice sql
```

The tools that Codex calls most. Codex runs most work through `exec`, a script that calls shell and patch tools:

```sql
SELECT tool, count(*) AS calls FROM tool_runs GROUP BY tool ORDER BY calls DESC LIMIT 5;
```

Turns and tokens for each model. Only newer Codex versions record tokens for each turn:

```sql
SELECT model, count(*) AS turns, sum(tokens) AS tokens FROM turns GROUP BY model ORDER BY turns DESC LIMIT 5;
```

Shell commands that failed, and the number of sessions they occurred in:

```sql
SELECT count(*) AS failed, count(DISTINCT session_id) AS sessions FROM commands WHERE exit_code <> 0;
```

Your most recent plan usage for each limit. `window_minutes` is `300` for the 5-hour limit and `10080` for the weekly limit. The view is empty if you use Codex with an API key:

```sql
SELECT window_minutes, last_value(used_percent ORDER BY ts) AS used_percent, last_value(resets_at ORDER BY ts) AS resets_at FROM rate_limits GROUP BY window_minutes;
```

Search your prompts and Codex's replies:

```sql
SELECT role, ts, substr(text, 1, 80) AS text FROM text_search(messages, 'flaky test', 5);
```

### Step 3: Stop Spice

Stop the Spice runtime with `Ctrl+C`. Spice keeps the data in memory, so there is nothing to clean up.
