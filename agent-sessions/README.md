# Coding Agent Sessions

Works with `v2.4+`

Query your local [Claude Code](https://docs.claude.com/en/docs/claude-code/overview) and [Codex](https://developers.openai.com/codex/cli) history with SQL. Each coding agent writes its sessions to JSONL files in your home directory. These Spicepods load the files with the [File Data Connector](https://spiceai.org/docs/components/data-connectors/file), parse them into views (sessions, turns, tool calls, shell commands, token usage), and add a [full-text search](https://spiceai.org/docs/features/search/full-text-search) index on the messages.

| Spicepod                                       | Reads        | Main views                                                                                |
| ---------------------------------------------- | ------------ | ----------------------------------------------------------------------------------------- |
| [`claude-code/spicepod.yaml`](./claude-code/spicepod.yaml) | `~/.claude/` | `sessions`, `turns`, `tool_runs`, `commands`, `files_touched`, `interruptions`, `messages`, `memories` |
| [`claude-code/snapshot-reader.yaml`](./claude-code/snapshot-reader.yaml) | S3 snapshots of `claude-code/spicepod.yaml` ([Enterprise](#optional-read-your-sessions-from-s3)) | Same as `claude-code/spicepod.yaml` |
| [`codex/spicepod.yaml`](./codex/spicepod.yaml)             | `~/.codex/`  | `sessions`, `threads`, `turns`, `tool_runs`, `commands`, `files_touched`, `token_usage`, `rate_limits`, `messages`, `thread_state`, `memories` |

Each view has a comment in its Spicepod that tells what its rows are. The Claude Code views are in the [`claude-code-views`](./claude-code/spicepods/claude-code-views/spicepod.yaml) Spicepod. Both Claude Code Spicepods load it as a dependency, so they serve the same views.

A background or forked session starts with a copy of its parent's history. The views mark these copied rows with `is_fork_copy`. To count each tool call or command one time, add `NOT is_fork_copy`, as the queries below do.

## Prerequisites

- Spice.ai CLI installed (see [Getting Started](https://spiceai.org/docs/getting-started)).
- This cookbook cloned to your computer.
- Claude Code or Codex used on this computer, so that `~/.claude/projects/` or `~/.codex/sessions/` has session files.

### Optional Codex files

The Codex Spicepod also reads the files below. Codex creates each file only when you use the feature that writes it. Most views, including `sessions`, `threads`, `turns` and `messages`, read only `~/.codex/sessions/`.

| File                         | Views that need it | Codex creates it when                               |
| ---------------------------- | ------------------ | --------------------------------------------------- |
| `~/.codex/history.jsonl`       | `prompt_history`   | You send a prompt, if prompt history is on.         |
| `~/.codex/session_index.jsonl` | `thread_names`     | A thread gets a name (a rename or an automatic title). |
| `~/.codex/rules/default.rules` | `exec_rules`       | You approve a command with "always allow".          |
| `~/.codex/state_5.sqlite`      | `thread_state`     | Codex starts. If you set `sqlite_home` or `CODEX_SQLITE_HOME`, the file is in that directory. |
| `~/.codex/memories_1.sqlite`   | `memories`         | You use Codex memories.                             |

If a file is missing, Spice logs a warning for its dataset, does not create the views that need it, and does not report ready. The log does not show `Spice runtime is ready!`, and `/v1/ready` returns `503`. All other views work. To remove the warnings, delete the dataset of the missing file from `codex/spicepod.yaml`.

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
SELECT tool, count(*) AS calls FROM tool_calls WHERE NOT is_fork_copy GROUP BY tool ORDER BY calls DESC LIMIT 5;
```

The number of sessions, their total cost in USD, and the number of tool calls that failed:

```sql
SELECT count(*) AS sessions, round(sum(total_cost_usd), 2) AS cost_usd, sum(tool_errors) AS tool_errors FROM sessions;
```

Shell commands that failed, and the number of sessions they occurred in:

```sql
SELECT count(*) AS failed, count(DISTINCT session_id) AS sessions FROM commands WHERE exit_code <> 0 AND NOT is_fork_copy;
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

### Optional: Save your sessions to S3

> **Note:** Acceleration snapshots require [Spice Enterprise](https://spice.ai) or a Spice OSS build compiled with the `snapshots` feature flag. A standard OSS build logs `Acceleration Snapshots are included in the Enterprise distribution of Spice.ai` and does not write snapshots.

Claude Code deletes old transcripts (by default, after 30 days). To keep your sessions after Claude Code deletes them, and to keep a copy in S3, use [acceleration snapshots](https://spiceai.org/docs/features/data-acceleration/snapshots). Spice then stores the `transcripts` and `memory_files` datasets in [Cayenne](https://spiceai.org/docs/components/data-accelerators/cayenne) files on your computer, and uploads a copy of each file to S3.

```text
~/.claude/projects/*.jsonl  ──append──> transcripts  (Cayenne) ──every 10m──> s3://<bucket>/agent-sessions/snapshots/
~/.claude/projects/*/memory ──────────> memory_files (Cayenne) ──every 10m──┘
                                              │                    ▲
                                          all views                └── on start, if the local files are missing
```

1. Add a `runtime` section to `claude-code/spicepod.yaml`, below `name: claude_sessions`. Replace `<bucket>` and `<region>` with your values:

   ```yaml
   runtime:
     state:
       location: s3://<bucket>/agent-sessions/
       params:
         s3_region: <region>
   ```

2. Replace the `acceleration` section of the `transcripts` dataset with:

   ```yaml
       acceleration:
         enabled: true
         engine: cayenne
         mode: file
         refresh_mode: append
         primary_key: "(_location, column_1)"
         snapshots: enabled
         snapshots_trigger: time_interval
         snapshots_trigger_threshold: 10m
         params:
           file_watcher: enabled
           cayenne_file_path: .spice/agent-sessions/
   ```

   `refresh_mode: append` adds new lines and does not remove the lines of deleted files. With the default refresh mode (`full`), the next change to a transcript removes the rows of all deleted files. The primary key (file and line) prevents duplicate rows when Spice reads a file again. It also keeps one copy of a line that occurs two times in the same file. Claude Code writes some metadata lines (for example `ai-title` and `mode`) two times.

3. Replace the `acceleration` section of the `memory_files` dataset with:

   ```yaml
       acceleration:
         enabled: true
         engine: cayenne
         mode: file
         refresh_check_interval: 60s
         snapshots: enabled
         snapshots_trigger: time_interval
         snapshots_trigger_threshold: 10m
         params:
           cayenne_file_path: .spice/agent-sessions/
   ```

   Memory files keep the default refresh mode (`full`), so the data shows edits and deletes that you make to your memories. Both datasets use the same `cayenne_file_path`. Spice puts each dataset in its own folder below it.

4. Start Spice as in [Step 1](#step-1-start-spice). Spice gets AWS credentials from the default AWS credential chain, for example `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`.

When the data loads, the log shows `Snapshot created dataset=transcripts` and `Snapshot created dataset=memory_files`. After that, Spice uploads a new snapshot every 10 minutes, but only if the data changed.

If the local Cayenne files are missing (for example, on a new computer), Spice downloads the newest snapshots when it starts, and the log shows `Snapshot restored`. Spice then adds the lines from `~/.claude/projects/`.

Each snapshot is a full copy of the data, not only the changes since the last snapshot. Spice keeps snapshots for 28 days, and always keeps the newest snapshot. Use a different `location` for each computer, because only one Spice runtime at a time can write snapshots to a location. If you change the `acceleration` section after Spice writes a snapshot, also change the `location`: Spice cannot load a snapshot that has a different primary key.

### Optional: Read your sessions from S3

[`claude-code/snapshot-reader.yaml`](./claude-code/snapshot-reader.yaml) serves the same views from the snapshots that the previous section writes. Use it on a different computer, or after you delete `~/.claude/`. It reads only S3, and it never writes to S3. It requires the same Spice build as the publisher (see the note in the previous section).

```text
publisher (claude-code/spicepod.yaml)            reader (claude-code/snapshot-reader.yaml)
~/.claude/projects ──> transcripts  ──snapshot──> s3://<bucket>/agent-sessions/snapshots/ ──> transcripts
                       memory_files                                                          memory_files
                           │                                                                    │
                    claude-code-views                                                    claude-code-views
```

1. In `claude-code/snapshot-reader.yaml`, replace `<bucket>` and `<region>` with the values of the publisher's `runtime.state` section. The reader reads the `snapshots/` folder below the publisher's `location`.

2. Start Spice. If the publisher runs on the same computer, stop it first. The reader uses the same ports, and its own directory for its local copy:

   ```shell
   POD="$PWD/agent-sessions/claude-code/snapshot-reader.yaml"
   mkdir -p ~/claude-sessions-reader && cd ~/claude-sessions-reader && spice run "$POD"
   ```

   Spice downloads the newest snapshot of each dataset, and the log shows `Snapshot restored` two times. Every minute (`refresh_check_interval`), Spice looks for a newer snapshot and loads it.

3. Query the views as in [Step 2](#step-2-query-your-sessions).

The snapshots contain only the `transcripts` and `memory_files` datasets. The reader computes the views itself, and builds its own full-text index for `messages`. The reader does not have the full-text index on memory content (`memory_files.content`), because a snapshot reader cannot have a full-text index on its datasets.

## Codex

### Step 1: Start Spice

If the Claude Code Spicepod is running, stop it first. From the root of this cookbook, run:

```shell
POD="$PWD/agent-sessions/codex/spicepod.yaml"
cd ~ && spice run "$POD"
```

On the first run, DuckDB downloads its `sqlite` extension to read the Codex databases. If one of the [optional Codex files](#optional-codex-files) is missing, Spice does not show `Spice runtime is ready!`. Wait until the log shows `Dataset load summary`, then continue.

### Step 2: Query your sessions

In a new terminal, start the SQL REPL:

```shell
spice sql
```

The tools that Codex calls most. Codex runs most work through `exec`, a script that calls shell and patch tools:

```sql
SELECT tool, count(*) AS calls FROM tool_runs WHERE NOT is_fork_copy GROUP BY tool ORDER BY calls DESC LIMIT 5;
```

Turns and tokens for each model. Only newer Codex versions record tokens for each turn:

```sql
SELECT model, count(*) AS turns, sum(tokens) AS tokens FROM turns GROUP BY model ORDER BY turns DESC LIMIT 5;
```

Shell commands that failed, and the number of sessions they occurred in:

```sql
SELECT count(*) AS failed, count(DISTINCT session_id) AS sessions FROM commands WHERE exit_code <> 0 AND NOT is_fork_copy;
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
