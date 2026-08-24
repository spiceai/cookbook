# Model Context Protocol with Spice

Works with `v2.0+`

## Prerequisties

1.  Spice installed
2.  `jq` installed

## Connect to MCP servers

Spice can run, or connect to MCP servers.

1. Clone the cookbook, and navigate to the MCP recipe.

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/mcp
```

2. Update the `.env` file with the required secrets.

```bash
API_KEY="foobar"
SPICE_OPENAI_API_KEY="{OpenAI API key}"
SPICE_ALLOWED_DIR="{directory the fs MCP tool is allowed to access}"
```

For this recipe, `SPICE_ALLOWED_DIR` should be set to allow access to this cookbook directory - like `SPICE_ALLOWED_DIR="./"`.

3. Start Spice

```bash
spice run
```

4. Show the available tools.

```bash
curl -H 'x-api-key: foobar' http://127.0.0.1:8090/v1/tools | jq '.[].name'
```

```bash
"sql"
"top_n_sample"
"load_memory"
"store_memory"
"random_sample"
"fs__read_file"
"fs__read_multiple_files"
"fs__write_file"
"fs__edit_file"
"fs__create_directory"
"fs__list_directory"
"fs__directory_tree"
"fs__move_file"
"fs__search_files"
"fs__get_file_info"
"fs__list_allowed_directories"
"list_datasets"
"table_schema"
"search"
"get_readiness"
"sample_distinct_columns"
```

This shows both the built in tools (e.g. `sql`) and all the tools listed by the MCP server `fs`.

> **Tool naming (Spice `v2.2+`):** Proxied tools are exposed as `<tool-name>__<upstream-tool-name>`, joined by a **double underscore** — `fs__read_file`, not `fs/read_file`. MCP clients such as Claude and Cursor reject tool names outside `^[a-zA-Z0-9_-]{1,64}$`, and the previous `/` separator made every proxied tool unusable in those clients ([spiceai/spiceai#10894](https://github.com/spiceai/spiceai/issues/10894)). The `<tool-name>` half is the `name` given in the `tools` section of `spicepod.yaml`, so renaming the tool renames every tool it proxies. On `v2.1.x` and earlier, substitute `/` for `__` throughout this recipe.

5. List the files from the current directory using the `fs__list_directory` MCP tool.

```bash
curl -XPOST -H 'x-api-key: foobar' http://127.0.0.1:8090/v1/tools/fs__list_directory \
    -d '{"path": "./"}' | jq -r '.[0].text'
```

```bash
[FILE] .env
[FILE] README.md
[DIR] child
[FILE] spicepod.yaml
```

6. Use the `fs` MCP server from a model.

```bash
spice chat --api-key foobar
```

```bash
>>> spice chat
Spice.ai OSS CLI v1.1.0
Using model: openai-with-spice

chat> Summarize the README.md
The README.md for the Spice.ai OSS Cookbook serves as a comprehensive guide to creating and deploying data and AI applications using Spice.ai. It is structured into various sections, each offering recipes for different use cases and features. Here’s a summary of its contents:

### Overview
- **Spice.ai OSS Cookbook**: A collection of recipes demonstrating how to utilize Spice.ai for data and AI application development.

### Main Sections
- **Guides**: Provides practical instructions, such as the "Real-time Data Access Pattern Analysis" for security analysis.
...
```

7. Make sure the LLM called the MCP tool (and didn't hallucinate)

```bash
>>> spice trace ai_chat --api-key foobar
Spice.ai OSS CLI v2.0.0-unstable (c771b74aa)
 Tree                                   Status  Duration    Span ID
 ai_chat                                OK       9953.36ms  d051f9effec60261
 ai_completion                          OK       9953.06ms  6ccd967faf4dfa1a
 tool_use::fs/list_allowed_directories  OK          1.51ms  0091894899b22e4c
 ai_completion                          OK       9053.25ms  1e9fb1c8408c3ac0
 tool_use::fs/read_text_file            OK          2.96ms  5b3f4b2982e89d0b
 ai_completion                          OK       7731.02ms  9bb53d8608cd4791

```

> **Note:** The trace shows `tool_use::fs/read_text_file` with a `/`, even though the tool is now called `fs__read_text_file`. Task-history labels were missed by the rename, so the two spellings currently coexist depending on how the tool was invoked — tracked in [spiceai/spiceai#13338](https://github.com/spiceai/spiceai/issues/13338).

## Connect to Spice over MCP

Spice is an MCP server. It can be connected to like any other MCP server running over HTTP.

1. Clone the cookbook, and navigate to the MCP recipe.

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/mcp
```

2. Update the `.env` file with the required secrets.

```bash
API_KEY=foobar
SPICE_OPENAI_API_KEY="{OpenAI API key}"
SPICE_ALLOWED_DIR="{directory the fs MCP tool is allowed to access}"
```

For this recipe, `SPICE_ALLOWED_DIR` should be set to allow access to this cookbook directory - like `SPICE_ALLOWED_DIR="./"`.

3. Start Spice.

```bash
spice run
```

4. In a new terminal, change to the `child` directory.

```bash
cd child
```

5. Inspect the spicepod.

```bash
cat spicepod.yaml
```

```yaml
name: spicepod
version: v1
kind: Spicepod

tools:
  - name: spice_mcp
    from: mcp:http://localhost:8090/v1/mcp
    params:
      mcp_headers: "x-api-key: foobar"
```

6. Run the second Spice instance on separate ports.

```bash
spice run --http-endpoint 127.0.0.1:8091 --flight-endpoint 127.0.0.1:50061 --metrics-endpoint 127.0.0.1:9091
```

7.  Show the tools available in the second Spice instance (note the different port).

```bash
curl -H 'x-api-key: foobar' http://127.0.0.1:8091/v1/tools | jq '.[].name'
```

```bash
"top_n_sample"
"search"
"store_memory"
"spice_mcp__store_memory"
"spice_mcp__get_readiness"
"spice_mcp__sample_distinct_columns"
"spice_mcp__sql"
"spice_mcp__fs_-_read_file"
"spice_mcp__fs_-_read_multiple_files"
"spice_mcp__fs_-_write_file"
"spice_mcp__fs_-_edit_file"
"spice_mcp__fs_-_create_directory"
"spice_mcp__fs_-_list_directory"
"spice_mcp__fs_-_directory_tree"
"spice_mcp__fs_-_move_file"
"spice_mcp__fs_-_search_files"
"spice_mcp__fs_-_get_file_info"
"spice_mcp__fs_-_list_allowed_directories"
"spice_mcp__top_n_sample"
"spice_mcp__random_sample"
"spice_mcp__load_memory"
"spice_mcp__list_datasets"
"spice_mcp__search"
"spice_mcp__table_schema"
"table_schema"
"sql"
"get_readiness"
"sample_distinct_columns"
"load_memory"
"list_datasets"
"random_sample"
```

Now you will see the following tools:

- Builtin tools within the second spicepod.
- Builtin tools from the first spicepod, over MCP (e.g. `spice_mcp__sql`).
- Tools from the filesystem MCP server, connected to via the first spicepod, over MCP (e.g. `spice_mcp__fs_-_read_file`).

  Chaining two hops escapes the inner separator: the first instance already exposes the tool as `fs__read_file`, and prefixing it again would produce an ambiguous `spice_mcp__fs__read_file`. So the inner `__` is rewritten to `_-_`, giving `spice_mcp__fs_-_read_file`, which decodes back to catalog `spice_mcp` and tool `fs__read_file`.

  ```ascii
  +----------------------------+     +--------------------+     +-----------------+
  | 2nd Spice Instance         |     | 1st Spice Instance |     | `fs` MCP Server |
  +----------------------------+     +--------------------+     +-----------------+
  | sql                        |     |                    |     |                 |
  | spice_mcp__sql-------------|-----|-->sql              |     |                 |
  | spice_mcp__fs_-_read_file--|-----|-->fs__read_file----|-----|-->read_file     |
  +----------------------------+     +--------------------+     +-----------------+
  ```

8. Use the SQL tool of the first Spice server, over MCP.

```bash
curl -H 'x-api-key: foobar' -XPOST http://127.0.0.1:8091/v1/tools/spice_mcp__sql \
    -d '{"query": "SELECT * FROM taxi_trips LIMIT 1"}'
```

```bash
[
  {
    "type": "text",
    "text": "\"[{\\\"VendorID\\\":1,\\\"tpep_pickup_datetime\\\":\\\"2024-01-29T12:51:51\\\",\\\"tpep_dropoff_datetime\\\":\\\"2024-01-29T13:00:42\\\",\\\"passenger_count\\\":1,\\\"trip_distance\\\":0.9,\\\"RatecodeID\\\":1,\\\"store_and_fwd_flag\\\":\\\"N\\\",\\\"PULocationID\\\":230,\\\"DOLocationID\\\":161,\\\"payment_type\\\":2,\\\"fare_amount\\\":8.6,\\\"extra\\\":2.5,\\\"mta_tax\\\":0.5,\\\"tip_amount\\\":0.0,\\\"tolls_amount\\\":0.0,\\\"improvement_surcharge\\\":1.0,\\\"total_amount\\\":12.6,\\\"congestion_surcharge\\\":2.5,\\\"Airport_fee\\\":0.0}\""
  }
]
```

9. Similarily to above, Use the `fs` MCP server from a model. In this case, the runtime will call the first spice instance, which subsequently, calls the `fs` MCP server.

```bash
spice chat --api-key foobar --http-endpoint http://127.0.0.1:8091
```

```bash
Using model: openai-with-spice
chat> Summarize the README.md

The README.md for the Spice.ai Model Context Protocol (MCP) details a comprehensive setup guide for using Spice with MCP servers. Here's a summary of its contents:

### Overview
- **Spice.ai OSS Cookbook**: A collection of recipes aimed at utilizing Spice.ai for developing data and AI applications.
...
```
