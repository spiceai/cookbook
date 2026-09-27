# Spice as MCP Server

Works with `v2.0+`

Run Spice as an MCP server and connect your AI assistant (Claude Desktop, Cursor, VS Code, or any MCP client) to it. This recipe loads GitHub issues, pull requests, and commits as accelerated, in-memory datasets and exposes the [GitHub MCP server](https://github.com/modelcontextprotocol/servers-archived/tree/main/src/github) through a single unified endpoint at `/v1/mcp`.

> **Note:** This recipe proxies the reference `@modelcontextprotocol/server-github` package, which has been moved to [`modelcontextprotocol/servers-archived`](https://github.com/modelcontextprotocol/servers-archived/tree/main/src/github) and is marked deprecated on npm. It still installs and runs via `npx`, so the recipe works as written. For new work, GitHub now maintains [`github/github-mcp-server`](https://github.com/github/github-mcp-server) as the supported replacement.

Your AI assistant gets one connection point that gives it:

| Tool | What it does |
|------|-------------|
| `sql` | Sub-millisecond SQL over accelerated GitHub data |
| `github__*` | Write tools — create issues, comment on PRs, search code |
| `list_datasets`, `table_schema` | Schema discovery |
| `search`, `top_n_sample`, `sample_distinct_columns` | Data exploration |

```
  Claude Desktop / Cursor / any MCP client
              │
              │  Streamable HTTP  http://localhost:8090/v1/mcp
              ▼
    ┌─────────────────────────────────────────────────┐
    │                    SPICE                        │
    │                                                 │
    │  built-in tools                                 │
    │    sql, list_datasets, table_schema,            │
    │    search, top_n_sample, ...                    │
    │                                                 │
    │  github__*  ── stdio ──► npx @mcp/server-github │
    │                                                 │
    │  datasets (Arrow, in-memory)                    │
    │    github_issues   ◄── GitHub API               │
    │    github_pulls    ◄── GitHub API               │
    │    github_commits  ◄── GitHub API               │
    └─────────────────────────────────────────────────┘
```

> **Tool naming (Spice `v2.2+`):** Proxied tools are exposed as `<tool-name>__<upstream-tool-name>`, joined by a **double underscore** — `github__search_code`, not `github/search_code`. MCP clients such as Claude and Cursor reject tool names outside `^[a-zA-Z0-9_-]{1,64}$`, and the previous `/` separator made every proxied tool unusable in those clients ([spiceai/spiceai#10894](https://github.com/spiceai/spiceai/issues/10894)). The `<tool-name>` half is the `name` given in the `tools` section of `spicepod.yaml`, so renaming the tool renames every tool it proxies. On `v2.1.x` and earlier, substitute `/` for `__` throughout this recipe.

> **Want to add Jira?** Add a `jira` tool block to `spicepod.yaml` and add your Jira credentials to `.env`. See [Adding Jira](#optional-adding-jira) below.

## Prerequisites

- [Spice CLI](https://docs.spiceai.org/getting-started) installed
- [Node.js](https://nodejs.org) — for `npx` to launch the GitHub MCP server
- A [GitHub personal access token](https://github.com/settings/tokens) with `repo` scope

## Setup

**Step 1.** Clone the cookbook and navigate to this recipe:

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/mcp-server
```

**Step 2.** Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and set your GitHub token:

```env
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_...
```

> The same token is used by both the GitHub dataset connector and the GitHub MCP server subprocess. Spice injects it via the `env:` block in `spicepod.yaml`.

**Step 3.** Start Spice:

```bash
spice run
```

Spice loads GitHub data into memory and launches the GitHub MCP server subprocess. Expect the initial load to take 20–60 seconds.

```console
2026-09-12T12:04:46.677499Z  INFO spiced: Starting runtime v2.3.0+models.metal
2026-09-12T12:04:46.999770Z  INFO runtime::http::routes: Enabled API key authentication on HTTP routes
2026-09-12T12:04:47.000953Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
GitHub MCP Server running on stdio
2026-09-12T12:04:48.422999Z  INFO runtime::init::dataset: Dataset github_issues registered (github:github.com/spiceai/cookbook/issues), acceleration (arrow, 300s refresh), results cache enabled. duration_ms=4
2026-09-12T12:04:49.065134Z  INFO runtime_table::accelerated::refresh_task: Loaded 4 rows (1.53 MiB) for dataset github_issues in 640ms.
2026-09-12T12:04:50.436538Z  INFO runtime::init::dataset: Dataset github_pulls registered (github:github.com/spiceai/cookbook/pulls), acceleration (arrow, 300s refresh), results cache enabled. duration_ms=0
2026-09-12T12:04:50.660468Z  INFO runtime::init::dataset: Dataset github_commits registered (github:github.com/spiceai/cookbook/commits), acceleration (arrow), results cache enabled. duration_ms=6
2026-09-12T12:05:08.156863Z  INFO runtime_table::accelerated::refresh_task: Loaded 500 rows (1.51 MiB) for dataset github_commits in 17s 494ms.
2026-09-12T12:05:09.750891Z  INFO runtime_table::accelerated::refresh_task: Loaded 69 rows (7.37 MiB) for dataset github_pulls in 19s 312ms.
2026-09-12T12:05:09.757459Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

The GitHub MCP server subprocess announces itself on stdout (`GitHub MCP Server running on stdio`); tool loading itself is logged at `DEBUG`, so no `Tool github registered` line appears at the default log level.

**Step 4.** Confirm the unified tool catalog is available (in a new terminal):

```bash
curl -s http://127.0.0.1:8090/v1/tools -H "X-API-KEY: foo" | jq '.[].name'
```

```
"sql"
"list_datasets"
"table_schema"
"search"
"top_n_sample"
"random_sample"
"sample_distinct_columns"
"get_readiness"
"load_memory"
"store_memory"
"github__create_issue"
"github__list_issues"
"github__get_pull_request"
"github__list_pull_requests"
"github__search_code"
"github__search_repositories"
...
```

Built-in tools (`sql`, `list_datasets`, ...) and proxied GitHub MCP tools (`github__*`) appear together in one catalog.

## Connect Claude Code

Run this once to register Spice as an MCP server in Claude Code:

```bash
claude mcp add --transport http spice http://localhost:8090/v1/mcp --header "X-API-KEY: foo"
```

Verify it was added:

```bash
claude mcp list
```

```
Checking MCP server health…

spice: http://localhost:8090/v1/mcp (HTTP) - ✔ Connected
```

Claude Code will now have access to the full Spice tool catalog — `sql`, `github__*`, `list_datasets`, and the rest — in every conversation.

## Example queries

Once connected, ask your AI assistant questions like:

- *"Show me the 10 most recently merged PRs."*
- *"Who are the top 5 contributors by number of commits in the last 30 days?"*
- *"What issues were opened this week and are still unassigned?"*

### SQL against the accelerated data (direct API)

The `/v1/tools/sql` endpoint returns a JSON string containing the serialized row
array. Pipe the response through `jq 'fromjson'` to decode it into a JSON array.
The examples below show the raw response; row counts depend on the GitHub data.

Count issues by state:

```bash
curl -s -XPOST http://127.0.0.1:8090/v1/tools/sql \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: foo" \
  -d '{"query": "SELECT state, COUNT(*) AS n FROM github_issues GROUP BY state ORDER BY n DESC"}'
```

```json
"[{\"state\":\"OPEN\",\"n\":1},{\"state\":\"CLOSED\",\"n\":1}]"
```

Top contributors by commits (example response shown for two contributors):

```bash
curl -s -XPOST http://127.0.0.1:8090/v1/tools/sql \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: foo" \
  -d '{"query": "SELECT author_name, COUNT(*) AS commits FROM github_commits GROUP BY author_name ORDER BY commits DESC LIMIT 5"}'
```

```json
"[{\"author_name\":\"Sergei Grebnov\",\"commits\":74},{\"author_name\":\"Luke Kim\",\"commits\":45}]"
```

PRs merged in the last 7 days:

```bash
curl -s -XPOST http://127.0.0.1:8090/v1/tools/sql \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: foo" \
  -d '{"query": "SELECT number, title, merged_at FROM github_pulls WHERE state = '\''MERGED'\'' AND merged_at >= now() - INTERVAL '\''7 days'\'' ORDER BY merged_at DESC"}'
```

### GitHub MCP tools (direct API)

Search code across the repository:

```bash
curl -s -XPOST http://127.0.0.1:8090/v1/tools/github__search_code \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: foo" \
  -d '{"q": "java repo:spiceai/cookbook"}'
```

## Optional: Adding Jira

To expose Jira and Confluence tools through the same MCP endpoint, add credentials to `.env`:

```env
JIRA_URL=https://your-org.atlassian.net
JIRA_USERNAME=your@email.com
JIRA_API_TOKEN=...
```

Add a `jira` tool block to the `tools` section of `spicepod.yaml`:

```yaml
  - name: jira
    from: mcp:uvx
    description: Jira and Confluence tools — query tickets, update status, search projects
    params:
      mcp_args: mcp-atlassian
    env:
      JIRA_URL: ${secrets:JIRA_URL}
      JIRA_USERNAME: ${secrets:JIRA_USERNAME}
      JIRA_API_TOKEN: ${secrets:JIRA_API_TOKEN}
```

Restart Spice. Jira tools appear in the same catalog alongside GitHub and SQL:

```bash
curl -s http://127.0.0.1:8090/v1/tools -H "X-API-KEY: foo" | jq '[.[].name | select(startswith("jira"))]'
```

```json
["jira__jira_get_issue", "jira__jira_search", "jira__jira_create_issue", "jira__jira_get_all_projects", ...]
```

The `jira_` prefix appears twice because `mcp-atlassian` already namespaces its own tools: it exposes `jira_get_issue`, and the tool named `jira` prefixes that again. This is expected.

Your AI assistant can now cross-reference GitHub PRs with Jira tickets through a single MCP connection.
