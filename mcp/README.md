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

For this recipe, set `SPICE_ALLOWED_DIR` to the absolute path of the `cookbook/mcp` directory (for example: `SPICE_ALLOWED_DIR="/full/path/to/cookbook/mcp"`).

3. Start Spice
```bash
spice run
```

Wait for the HTTP tools endpoint to become reachable before continuing:

```bash
until curl -sS http://127.0.0.1:8090/v1/tools >/dev/null; do sleep 2; done
```

4. Show the available tools.
```bash
curl -sS http://127.0.0.1:8090/v1/tools | jq 'type, length'
```
This confirms the endpoint returns a JSON array. The array may be empty while tools are still initializing.

5. List the files from the current directory using the `fs/list_directory` MCP tool.
```bash
curl -sS -XPOST http://127.0.0.1:8090/v1/tools/fs/list_directory \
    -d '{"path": "./"}' | jq -r '.[0].text'
```
This should return directory listing text for the allowed directory.

6. Use the `fs` MCP server from a model.
```bash
spice chat
```

## Connect to Spice over MCP
Spice is an MCP server. It can be connected to like any other MCP server running over HTTP SSE.

Before starting this section, stop the previous `spice run` process from the earlier section to avoid port conflicts.

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
This file should define a `spice_mcp` tool that points to `http://localhost:8090/v1/mcp/sse`.

6. Run the second Spice instance on separate ports.
```bash
spice run --http-endpoint 127.0.0.1:8091 --flight-endpoint 127.0.0.1:50061 --metrics-endpoint 127.0.0.1:9091
```

7.  Show the tools available in the second Spice instance (note the different port).
```bash
curl -sS http://127.0.0.1:8091/v1/tools | jq '.[].name'
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
curl -sS -XPOST http://127.0.0.1:8091/v1/tools/spice_mcp/sql \
    -d '{"query": "SELECT * FROM taxi_trips LIMIT 1"}'
```
The response contains the tool result payload with one row from `taxi_trips`.

9. Similarily to above, Use the `fs` MCP server from a model. In this case, the runtime will call the first spice instance, which subsequently, calls the `fs` MCP server.
```bash
spice chat --http-endpoint http://127.0.0.1:8091
```
