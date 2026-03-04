# GraphQL Data Connector

Follow these steps to get started with GraphQL as a Data Connector.

## Pre-requisites

- The latest version of Spice. [Install Spice](https://docs.spiceai.org/getting-started/installation)
- A GraphQL endpoint with a query that returns data in JSON format.
  - The GitHub GraphQL API (<https://api.github.com/graphql>) is a good example to get started with. [GitHub GraphQL API](https://docs.github.com/en/graphql)

**Step 1 (Optional).** The example uses the GitHub GraphQL API to fetch the `spiceai` stargazers. If you would like to use your own GraphQL endpoint, edit the `spicepod.yaml` file in this directory and replace the `graphql_recipe` dataset parameters with the connection details for your GraphQL instance.

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
INFO Installing Spice.ai runtime v1.11.2 (spiced_models_linux_x86_64.tar.gz)...
```

**Step 3.** Run `spice sql` in a new terminal to start an interactive SQL query session against the Spice runtime.

For more information on using `spice sql`, see the [CLI reference](https://docs.spiceai.org/cli/reference/sql).

**Step 4.** Execute a deterministic query to verify GraphQL data is available:

```sql
select count(*) > 0 as has_rows from stargazers;
```

Example output:

```console
+----------+
| has_rows |
+----------+
| true     |
+----------+
```
