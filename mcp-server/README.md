# Spice as MCP Server

Works with `v2.0+`

Run Spice as an MCP server and connect your AI assistant (Claude Desktop, Cursor, VS Code, or any MCP client) to it. This recipe loads GitHub issues, pull requests, and commits as accelerated, in-memory datasets and exposes the [GitHub MCP server](https://github.com/modelcontextprotocol/servers-archived/tree/main/src/github) through a single unified endpoint at `/v1/mcp`.

> **Note:** This recipe proxies the reference `@modelcontextprotocol/server-github` package, which has been moved to [`modelcontextprotocol/servers-archived`](https://github.com/modelcontextprotocol/servers-archived/tree/main/src/github) and is marked deprecated on npm. It still installs and runs via `npx`, so the recipe works as written. For new work, GitHub now maintains [`github/github-mcp-server`](https://github.com/github/github-mcp-server) as the supported replacement.

Your AI assistant gets one connection point that gives it:

| Tool | What it does |
|------|-------------|
| `sql` | Sub-millisecond SQL over accelerated GitHub data |
| `github/*` | Write tools — create issues, comment on PRs, search code |
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
    │  github/*  ── stdio ──► npx @mcp/server-github  │
    │                                                 │
    │  datasets (Arrow, in-memory)                    │
    │    github_issues   ◄── GitHub API               │
    │    github_pulls    ◄── GitHub API               │
    │    github_commits  ◄── GitHub API               │
    └─────────────────────────────────────────────────┘
```

> **Want to add Jira?** Uncomment the `jira` tool block in `spicepod.yaml` and add your Jira credentials to `.env`. See [Adding Jira](#optional-adding-jira) below.

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
2025-05-21T10:00:01Z  INFO runtime: Spice runtime is ready
2025-05-21T10:00:01Z  INFO runtime::init::dataset: Dataset github_issues registered (github:...), acceleration (arrow)
2025-05-21T10:00:01Z  INFO runtime::init::dataset: Dataset github_pulls registered (github:...), acceleration (arrow)
2025-05-21T10:00:01Z  INFO runtime::init::dataset: Dataset github_commits registered (github:...), acceleration (arrow)
2025-05-21T10:00:01Z  INFO runtime::init::tool: Tool github registered (mcp:npx)
```

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
"github/create_issue"
"github/list_issues"
"github/get_pull_request"
"github/list_pull_requests"
"github/search_code"
"github/search_repositories"
...
```

Built-in tools (`sql`, `list_datasets`, ...) and proxied GitHub MCP tools (`github/*`) appear together in one catalog.

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
spice: http://localhost:8090/v1/mcp (http)
```

Claude Code will now have access to the full Spice tool catalog — `sql`, `github/*`, `list_datasets`, and the rest — in every conversation.

## Example queries

Once connected, ask your AI assistant questions like:

- *"Show me the 10 most recently merged PRs."*
- *"Who are the top 5 contributors by number of commits in the last 30 days?"*
- *"What issues were opened this week and are still unassigned?"*

### SQL against the accelerated data (direct API)

Count issues by state:

```bash
curl -s -XPOST http://127.0.0.1:8090/v1/tools/sql \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: foo" \
  -d '{"query": "SELECT state, COUNT(*) AS n FROM github_issues GROUP BY state ORDER BY n DESC"}'
```

```json
[{"type":"text","text":"[{\"state\":\"OPEN\",\"n\":1},{\"state\":\"CLOSED\",\"n\":1}]"}]
```

Top contributors by commits:

```bash
curl -s -XPOST http://127.0.0.1:8090/v1/tools/sql \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: foo" \
  -d '{"query": "SELECT author_name, COUNT(*) AS commits FROM github_commits GROUP BY author_name ORDER BY commits DESC LIMIT 5"}'
```

```json
[{"type":"text","text":"[{\"author_name\":\"Sergei Grebnov\",\"commits\":74},{\"author_name\":\"Luke Kim\",\"commits\":45},..."}]
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
curl -s -XPOST http://127.0.0.1:8090/v1/tools/github/search_code \
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

Uncomment the `jira` tool block in `spicepod.yaml`:

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
["jira/get_issue", "jira/search_issues", "jira/create_issue", "jira/list_projects", ...]
```

Your AI assistant can now cross-reference GitHub PRs with Jira tickets through a single MCP connection.
