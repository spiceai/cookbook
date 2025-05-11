# Model Context Protocol with Spice
## Prerequisties
 1. Spice installed
 2. `jq` installed

## Connect to MCP servers
Spice can run, or connect to MCP servers.

1. Clone the cookbook, and navigate to the MCP recipe.

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/mcp
```

2. Update the `.env` file with the required secrets.

```bash
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
curl http://127.0.0.1:8090/v1/tools | jq '.[].name'
```
```bash
"sql"
"top_n_sample"
"load_memory"
"store_memory"
"random_sample"
"fs/read_file"
"fs/read_multiple_files"
"fs/write_file"
"fs/edit_file"
"fs/create_directory"
"fs/list_directory"
"fs/directory_tree"
"fs/move_file"
"fs/search_files"
"fs/get_file_info"
"fs/list_allowed_directories"
"list_datasets"
"table_schema"
"document_similarity"
"get_readiness"
"sample_distinct_columns"
```
This shows both the built in tools (e.g. `sql`) and all the tools listed by the MCP server `fs`.

5. List the files from the current directory using the `fs/list_directory` MCP tool.
```bash
curl -XPOST http://127.0.0.1:8090/v1/tools/fs/list_directory \
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
spice chat
```
```bash
>>> spice chat
Spice.ai OSS CLI v1.1.0
Using model: openai-with-spice

chat> Summarise the README.md
The README.md for the Spice.ai OSS Cookbook serves as a comprehensive guide to creating and deploying data and AI applications using Spice.ai. It is structured into various sections, each offering recipes for different use cases and features. Here’s a summary of its contents:

### Overview
- **Spice.ai OSS Cookbook**: A collection of recipes demonstrating how to utilize Spice.ai for data and AI application development.

### Main Sections
- **Guides**: Provides practical instructions, such as the "Real-time Data Access Pattern Analysis" for security analysis.
...
```

7. Make sure the LLM called the MCP tool (and didn't hallucinate)
```bash
>>> spice trace ai_chat

TREE                   STATUS DURATION   TASK
d2aea75693c13de3       ✅      8577.00ms ai_chat
  ├── 6b7d17547c4822ab ✅      8575.48ms ai_completion
  ├── 7d669dfe8152ccb4 ✅         2.17ms tool_use::fs/list_allowed_directories
  ├── 234e619826c618f0 ✅      7475.86ms ai_completion
  ├── fdce46ad22f9051e ✅        11.41ms tool_use::fs/read_file
  └── 4f0a4e941f4d0efe ✅      6337.73ms ai_completion
```

## Connect to Spice over MCP
Spice is an MCP server. It can be connected to like any other MCP server running over HTTP SSE.

1. Clone the cookbook, and navigate to the MCP recipe.

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/mcp
```

2. Update the `.env` file with the required secrets.

```bash
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
version: v1beta1
kind: Spicepod

tools:
  - name: spice_mcp
    from: mcp:http://localhost:8090/v1/mcp/sse
```

6. Run the second Spice instance on separate ports.
```bash
spice run --http-endpoint 127.0.0.1:8091 --flight-endpoint 127.0.0.1:50061 --metrics-endpoint 127.0.0.1:9091 -- --open_telemetry 127.0.0.1:50062
```

7.  Show the tools available in the second Spice instance (note the different port).
```bash
curl http://127.0.0.1:8091/v1/tools | jq '.[].name'
```
```bash
"top_n_sample"
"document_similarity"
"store_memory"
"spice_mcp/store_memory"
"spice_mcp/get_readiness"
"spice_mcp/sample_distinct_columns"
"spice_mcp/sql"
"spice_mcp/fs/read_file"
"spice_mcp/fs/read_multiple_files"
"spice_mcp/fs/write_file"
"spice_mcp/fs/edit_file"
"spice_mcp/fs/create_directory"
"spice_mcp/fs/list_directory"
"spice_mcp/fs/directory_tree"
"spice_mcp/fs/move_file"
"spice_mcp/fs/search_files"
"spice_mcp/fs/get_file_info"
"spice_mcp/fs/list_allowed_directories"
"spice_mcp/top_n_sample"
"spice_mcp/random_sample"
"spice_mcp/load_memory"
"spice_mcp/list_datasets"
"spice_mcp/document_similarity"
"spice_mcp/table_schema"
"table_schema"
"sql"
"get_readiness"
"sample_distinct_columns"
"load_memory"
"list_datasets"
"random_sample"
```
Now you will see the following tools:
* Builtin tools within the second spicepod.
* Builtin tools from the first spicepod, over MCP (e.g. `spice_mcp/sql`).
* Tools from the filesystem MCP server, connected to via the first spicepod, over MCP (e.g. `spice_mcp/fs/read_file`).
   ```ascii
   +-------------------------+     +--------------------+     +-----------------+
   | 2nd Spice Instance      |     | 1st Spice Instance |     | `fs` MCP Server |
   +-------------------------+     +--------------------+     +-----------------+
   | sql                     |     |                    |     |                 |
   | spice_mcp/sql-----------|-----|-->sql              |     |                 |
   | spice_mcp/fs/read_file--|-----|-->fs/read_file-----|-----|-->read_file     |
   +-------------------------+     +--------------------+     +-----------------+
   ```

8. Use the SQL tool of the first Spice server, over MCP.
```bash
curl -XPOST http://127.0.0.1:8091/v1/tools/spice_mcp/sql \
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
