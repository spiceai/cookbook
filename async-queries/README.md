# Async Queries

Works with `v2.0+`

> **Note:** Async queries require Spice v2.0 or later.

This recipe demonstrates how to use the async queries API to submit long-running SQL queries and retrieve results asynchronously. It shows how to:

- Submit queries via the HTTP API and CLI
- Poll for query completion
- Retrieve paginated results
- Cancel running queries
- Use the interactive `spice query` REPL

Async queries build on top of [distributed query](../distributed/README.md) mode and require cluster mode with a scheduler and at least one executor.

## Prerequisites

- [Spice CLI](https://docs.spiceai.org/getting-started) installed (v2.0+)

## Getting Started

### Step 1: Prepare Working Directory

Clone the cookbook repository and navigate to the `async-queries` directory.

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/async-queries
```

This recipe stores scheduler/job state at the absolute local path `/tmp/spiceai-async-queries/scheduler-state`. To reset local async query state between runs, remove the directory:

```bash
rm -rf /tmp/spiceai-async-queries
```

### Step 2: Generate Development mTLS Certificates

Generate mTLS certificates for the scheduler and executor:

```bash
spice cluster tls init
spice cluster tls add scheduler1
spice cluster tls add executor1
```

### Step 3: Start the Spice Scheduler

Start the scheduler with cluster mode and the absolute `scheduler.state_location` configured in the `spicepod.yaml`:

```bash
~/.spice/bin/spiced --role scheduler \
  --node-bind-address 127.0.0.1:50052 \
  --node-advertise-address 127.0.0.1 \
  --http 127.0.0.1:8090 \
  --flight 127.0.0.1:50051 \
  --node-mtls-ca-certificate-file ~/.spice/pki/ca.crt \
  --node-mtls-certificate-file ~/.spice/pki/scheduler1.crt \
  --node-mtls-key-file ~/.spice/pki/scheduler1.key
```

The scheduler starts and registers the `data` dataset:

```console
2026-03-02T12:00:00.000000Z  INFO spiced: Starting runtime
2026-03-02T12:00:01.000000Z  INFO runtime::cluster: Starting Ballista scheduler on 127.0.0.1:50052 (shuffle_format=arrow_ipc, shuffle_location=disk (temp_directory))
2026-03-02T12:00:01.000000Z  INFO runtime::init::dataset: Dataset data initializing...
2026-03-02T12:00:01.000000Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2026-03-02T12:00:01.000000Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2026-03-02T12:00:03.000000Z  INFO runtime::init::dataset: Dataset data registered (s3://spiceai-public-datasets/hive_partitioned_data/), results cache enabled.
2026-03-02T12:00:03.000000Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

### Step 4: Start the Spice Executor

A scheduler requires at least one executor to run queries. One instance directory serves one
runtime, so give the executor its own with `SPICE_CONFIG_DIR`. In a new terminal:

```bash
SPICE_CONFIG_DIR=~/.spice/executor1 ~/.spice/bin/spiced --role executor \
  --http 127.0.0.1:9090 \
  --scheduler-address 127.0.0.1:50052 \
  --node-mtls-ca-certificate-file ~/.spice/pki/ca.crt \
  --node-mtls-certificate-file ~/.spice/pki/executor1.crt \
  --node-mtls-key-file ~/.spice/pki/executor1.key \
  --node-bind-address 127.0.0.1:50062 \
  --node-advertise-address 127.0.0.1
```

```console
2026-03-02T12:01:00.000000Z  INFO spiced: Starting runtime
2026-03-02T12:01:01.000000Z  INFO ballista_executor::execution_loop: Starting poll work loop with scheduler
2026-03-02T12:01:01.000000Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

### Step 5: Submit an Async Query via HTTP

In a new terminal, submit a query using `curl`:

```bash
curl -s http://127.0.0.1:8090/v1/queries \
  -H "Content-Type: application/json" \
  -d '{"sql": "SELECT * FROM data LIMIT 100"}' | jq .
```

The API returns immediately with a query ID and status URLs:

```json
{
  "query_id": "01ABC-DEF-456-7890AB",
  "status": "PENDING",
  "status_url": "/v1/queries/01ABC-DEF-456-7890AB/status",
  "results_url": "/v1/queries/01ABC-DEF-456-7890AB/results"
}
```

Optional fields are omitted rather than returned as `null`, so an `error` field only
appears when a query actually fails.

### Step 6: Poll for Completion

Use the `status_url` to poll until the query completes:

```bash
curl -s http://127.0.0.1:8090/v1/queries/01ABC-DEF-456-7890AB/status | jq .
```

While still running:

```json
{
  "status": "RUNNING"
}
```

Once completed:

```json
{
  "status": "SUCCEEDED"
}
```

### Step 7: Retrieve Results

Fetch the first chunk of results:

```bash
curl -s http://127.0.0.1:8090/v1/queries/01ABC-DEF-456-7890AB/results | jq .
```

```json
{
  "chunk_index": 0,
  "row_offset": 0,
  "row_count": 50,
  "data_array": [
    { "id": 30, "value": "value_0" },
    { "id": 31, "value": "value_1" }
  ]
}
```

The `data` dataset holds 50 rows, so `LIMIT 100` returns all 50 in a single chunk. Results
are written in chunks of 10,000 rows; because this result fits in one chunk, the
`next_chunk_index` and `next_chunk_url` fields are omitted.

For queries with more than 10,000 rows, follow the `next_chunk_url` to paginate through results:

```bash
curl -s http://127.0.0.1:8090/v1/queries/01ABC-DEF-456-7890AB/results/chunks/1 | jq .
```

## Using the CLI

The `spice query` command provides a convenient CLI wrapper around the async queries API.

### Submit and Wait

```bash
spice query "SELECT * FROM data LIMIT 10;"
```

```console
Submitted query: 01ABC-DEF-456-7890AB (PENDING)
Waiting for completion... (Ctrl+C to stop waiting)
✓ SUCCEEDED (1.5s)
+-------+---------+
|   id  |  value  |
| int64 | varchar |
+-------+---------+
| 0     | value_0 |
| 1     | value_1 |
| 2     | value_2 |
| 3     | value_3 |
| 4     | value_4 |
| 5     | value_5 |
| 6     | value_6 |
| 7     | value_7 |
| 8     | value_8 |
| 9     | value_9 |
+-------+---------+

Time: 1.50488558 seconds. 10 rows.
```

### Submit Without Waiting

```bash
spice query "SELECT * FROM data;" --no-wait
```

```console
Submitted query: 01ABC-DEF-456-7890AB (PENDING)
Check status with: spice query status 01ABC-DEF-456-7890AB
Get results with: spice query results 01ABC-DEF-456-7890AB
```

### List Running Queries

```bash
spice query list --status running
```

```console
 QUERY ID              STATE    CREATED                        SQL PREVIEW
 01ABC-DEF-456-7890AB  RUNNING  2026-03-02T12:00:00.000+00:00  SELECT * FROM data;

Total: 1 queries
```

### Cancel a Query

```bash
spice query cancel 01ABC-DEF-456-7890AB
```

```console
Query 01ABC-DEF-456-7890AB cancelled (status: CANCELLED)
```

## Interactive REPL

Start the REPL for a session-based workflow:

```bash
spice query
```

```console
Welcome to the Spice.ai async query REPL.
Type SQL to submit a query, or .help for commands.

query> SELECT COUNT(*) FROM data;
Submitted query: 01ABC-DEF-456-7890AB (PENDING)
Press Ctrl+C to stop waiting (query continues in background)
✓ SUCCEEDED (1.0s)
+----------+
| count(*) |
|   int64  |
+----------+
| 50       |
+----------+

Time: 1.00419104 seconds. 1 rows.

query> .list
 QUERY ID              STATUS     SUBMITTED  SQL
 01ABC-DEF-456-7890AB  SUCCEEDED  1s ago     SELECT COUNT(*) FROM data;

query> .exit
```

### REPL Commands

| Command             | Description                            |
| ------------------- | -------------------------------------- |
| `.list`             | List tracked queries from this session |
| `.status <id>`      | Show query status                      |
| `.results <id>`     | Fetch and display results              |
| `.wait <id>`        | Resume waiting for a query             |
| `.cancel <id>`      | Cancel a running query                 |
| `.clear`            | Clear tracked queries from local list  |
| `.clear history`    | Clear command history                  |
| `.help`             | Show all commands                      |
| `.exit`, `.quit`, `.q` | Exit the REPL                       |

Partial query IDs are supported — `01ABC` resolves to the full ID if it uniquely matches one tracked query.

## Advanced: Parameterized Queries

Submit queries with bind parameters to safely include dynamic values:

```bash
curl -s http://127.0.0.1:8090/v1/queries \
  -H "Content-Type: application/json" \
  -d '{
    "sql": "SELECT * FROM data WHERE id > $1 LIMIT $2",
    "parameters": [40, 10]
  }' | jq .
```

Fetching the results of that query shows the bound values applied — ids above `40`, capped
at 10 rows:

```json
{
  "chunk_index": 0,
  "row_offset": 0,
  "row_count": 9,
  "data_array": [
    { "id": 41, "value": "value_1" },
    { "id": 42, "value": "value_2" }
  ]
}
```

## Advanced: Timeouts and Size Limits

Set a per-query timeout (the query is automatically cancelled on expiry):

```bash
curl -s http://127.0.0.1:8090/v1/queries \
  -H "Content-Type: application/json" \
  -d '{
    "sql": "SELECT * FROM data",
    "timeout_seconds": 30
  }' | jq .
```

Set a maximum result size (the query fails if results exceed it):

```bash
curl -s http://127.0.0.1:8090/v1/queries \
  -H "Content-Type: application/json" \
  -d '{
    "sql": "SELECT * FROM data",
    "maximum_size": 10485760
  }' | jq .
```

## How It Works

1. **Submit**: A `POST /v1/queries` request creates a job in the scheduler's object store (configured via `scheduler.state_location`) and spawns a background task.
2. **Execute**: The background task submits the query to the Ballista distributed scheduler, which distributes execution across connected executors.
3. **Stream**: As result batches arrive from the executors, they are written to the object store in chunks of 10,000 rows.
4. **Complete**: The job is marked as `SUCCEEDED` with result metadata (schema, row count, chunk count).
5. **Retrieve**: Clients fetch results by chunk index. Results are available for 12 hours after completion.
6. **Cleanup**: Expired job results are periodically cleaned up from the object store.

## Learn More

- [Distributed Query — Async Queries API](https://spiceai.org/docs/features/distributed-query#async-queries-api) — Full HTTP and Flight API reference
- [Distributed Query](https://spiceai.org/docs/features/distributed-query) — Distributed multi-node SQL execution overview
- [Distributed Query Recipe](../distributed/README.md) — Setting up a distributed Spice cluster
- [`spice query` CLI](https://spiceai.org/docs/features/distributed-query#cli) — CLI command and REPL documentation
