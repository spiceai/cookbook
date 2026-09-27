# GraphQL Data Connector

Works with `v1.0+`

Follow these steps to get started with GraphQL as a Data Connector.

## Pre-requisites

- The latest version of Spice. [Install Spice](https://docs.spiceai.org/getting-started)
- A GraphQL endpoint with a query that returns data in JSON format.
  - The GitHub GraphQL API (<https://api.github.com/graphql>) is a good example to get started with. [GitHub GraphQL API](https://docs.github.com/en/graphql)

**Step 1 (Optional).** The example uses the GitHub GraphQL API to fetch the `spiceai` stargazers. If you would like to use your own GraphQL endpoint, edit the `spicepod.yaml` file in this directory and replace the `stargazers` dataset parameters with the connection details for your GraphQL instance.

- `name`: The desired name for the federated table within Spice
- `from: graphql:<URL>`: The URL to your GraphQL endpoint
- `graphql_query`: The query to execute
- `json_pointer`: The JSON pointer to the data in the GraphQL response

For authentication options see [GraphQL Data Connector docs](https://docs.spiceai.org/components/data-connectors/graphql#configuration)

To connect to the GitHub GraphQL API and fetch the stargazers of the `spiceai` repository:

```yaml
datasets:
  - from: graphql:https://api.github.com/graphql
    name: stargazers
    params:
      graphql_auth_token: ${env:GH_TOKEN}
      json_pointer: /data/repository/stargazers/edges
      graphql_query: |
        {
          repository(name: "spiceai", owner: "spiceai") {
            id
            name
            stargazers(first: 100) {
              edges {
                starredAt
                node {
                  id
                  name
                  login
                }
              }
              pageInfo {
                hasNextPage
                endCursor
              }
            }
          }
        }
```

See the [GraphQL data connector docs](https://docs.spiceai.org/components/data-connectors/graphql) for more configuration options.

To securely store GraphQL auth params, see [Secret Stores](https://docs.spiceai.org/components/secret-stores).

Create `.env` file with the following environment variable:

```bash
GH_TOKEN=<your GitHub token>
```

**Step 2.** Run the Spice runtime with `spice run` from the directory with the `spicepod.yaml` file.

```bash
cd path/to/graphql
spice run
```

Example output:

```console
 INFO Spice.ai runtime starting...
2026-09-09T12:17:19.539074Z  INFO spiced: Starting runtime v2.2.1+models.metal
2026-09-09T12:17:19.541962Z  INFO runtime::init::caching: Initialized sql results cache; max size: 128.00 MiB, item ttl: 1s, hashing algorithm: XXH3, encoding: none
2026-09-09T12:17:19.541988Z  INFO runtime::init::caching: Initialized search results cache; max size: 128.00 MiB, item ttl: 1s, engine: Moka
2026-09-09T12:17:19.541998Z  INFO runtime::init::caching: Initialized embeddings cache; max size: 128.00 MiB, item ttl: 1s, engine: Moka
2026-09-09T12:17:19.543875Z  INFO runtime::secrets_preflight: Secrets: all 1 secret reference(s) resolved.
2026-09-09T12:17:19.544699Z  INFO runtime::init::dataset: Dataset stargazers initializing...
2026-09-09T12:17:19.743259Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2026-09-09T12:17:19.743556Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2026-09-09T12:17:23.168435Z  INFO runtime::init::dataset: Dataset stargazers registered (graphql:https://api.github.com/graphql), acceleration (arrow), results cache enabled. duration_ms=4
2026-09-09T12:17:23.170112Z  INFO runtime_table::accelerated::refresh_task: Loading data for dataset stargazers
2026-09-09T12:17:34.037609Z  INFO runtime_table::accelerated::refresh_task: Dataset stargazers received 301 records (200.33 kiB uncompressed) in 10s, 18.44 kiB/s
2026-09-09T12:17:44.977917Z  INFO runtime_table::accelerated::refresh_task: Dataset stargazers received 801 records (535.35 kiB uncompressed) in 21s, 24.55 kiB/s
2026-09-09T12:17:49.547223Z  INFO runtime::init::dataset: Dataset load summary (after 30s): 2/2 ready, 0 unhealthy, 0 still initializing.
2026-09-09T12:17:55.464375Z  INFO runtime_table::accelerated::refresh_task: Dataset stargazers received 1,201 records (801.57 kiB uncompressed) in 32s, 24.82 kiB/s
2026-09-09T12:18:05.663061Z  INFO runtime_table::accelerated::refresh_task: Dataset stargazers received 1,601 records (1.04 MiB uncompressed) in 42s, 25.14 kiB/s
2026-09-09T12:18:16.571801Z  INFO runtime_table::accelerated::refresh_task: Dataset stargazers received 2,101 records (1.37 MiB uncompressed) in 53s, 26.26 kiB/s
2026-09-09T12:18:28.345213Z  INFO runtime_table::accelerated::refresh_task: Dataset stargazers received 2,601 records (1.70 MiB uncompressed) in 65s, 26.66 kiB/s
2026-09-09T12:18:36.363019Z  INFO runtime_table::accelerated::refresh_task: Loaded 3,079 rows (2.01 MiB) for dataset stargazers in 1m 13s 192ms.
2026-09-09T12:18:36.389381Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

The `pageInfo` block in the query lets the connector follow GitHub's cursor
pagination, so the first load walks the full stargazer list 100 at a time and
takes about a minute. The row count grows as the repository gains stars.

**Step 3.** Run `spice sql` in a new terminal to start an interactive SQL query session against the Spice runtime.

For more information on using `spice sql`, see the [CLI reference](https://docs.spiceai.org/cli/reference/sql).

**Step 4.** Execute the query to see GraphQL response accelerated locally:

```sql
select * from stargazers limit 10;
```

Example output:

```console
+----------------------+--------------------------------------------------------------------------+
|       starredAt      |                                   node                                   |
|        varchar       |                                  struct                                  |
+----------------------+--------------------------------------------------------------------------+
| 2021-08-13T10:40:54Z | {id: MDQ6VXNlcjIyOTIwOQ==, name: Andrew Armstrong, login: Plasma}        |
| 2021-09-07T06:18:49Z | {id: MDQ6VXNlcjg3OTQ0NQ==, name: Phillip LeBlanc, login: phillipleblanc} |
| 2021-09-07T19:57:24Z | {id: MDQ6VXNlcjcwNzIw, name: Thomas Dohmke, login: ashtom}               |
| 2021-09-07T20:06:11Z | {id: MDQ6VXNlcjEzODk4ODM=, name: Lane Harris, login: haardvark}          |
| 2021-09-07T20:16:06Z | {id: MDQ6VXNlcjgzMjM0, name: Txus, login: txus}                          |
| 2021-09-07T20:16:13Z | {id: MDQ6VXNlcjY4OTI4NDM4, name: godelcomplete, login: iblameandrew}     |
| 2021-09-07T20:26:53Z | {id: MDQ6VXNlcjE2Mjk1Mjgz, name: Yaron Schneider, login: yaron2}         |
| 2021-09-07T20:28:28Z | {id: MDQ6VXNlcjY4Njg5NjY=, name: , login: nightlyworker}                 |
| 2021-09-07T21:10:56Z | {id: MDQ6VXNlcjMxNDU3, name: Nate Todd, login: ntodd}                    |
| 2021-09-07T21:15:22Z | {id: MDQ6VXNlcjMwNjUyNA==, name: Felix Chan, login: felixchan}           |
+----------------------+--------------------------------------------------------------------------+

Time: 0.004832417 seconds. 10 rows.
```
