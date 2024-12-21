# GitHub Data Connector

This recipe will use the [spiceai/spiceai](https://github.com/spiceai/spiceai) repo for a demo.

## Pre-requisites

- Spice is installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation).
- GitHub personal access token, [Learn more](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-personal-access-token-classic) how to create one.

**Step 1.** Copy the `.env` file into a new `.env.local` file in this directory, and set the `GITHUB_TOKEN` environment variable to your personal access token.

```env
GITHUB_TOKEN=<your_github_token>
```

**Setp 2.** Run the Spice runtime with `spice run` from the directory with the `spicepod.yaml` file.

```console
cd <path/to/cookbook/github>

spice run
Checking for latest Spice runtime release...
Spice.ai runtime starting...
2024-09-16T03:58:04.013601Z  INFO runtime::metrics_server: Spice Runtime Metrics listening on 127.0.0.1:9090
2024-09-16T03:58:04.013775Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2024-09-16T03:58:04.014420Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2024-09-16T03:58:04.025747Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2024-09-16T03:58:04.213793Z  INFO runtime: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
2024-09-16T03:58:04.514613Z  INFO runtime: Dataset spiceai.files registered (github:github.com/spiceai/spiceai/files/trunk), acceleration (arrow), results cache enabled.
2024-09-16T03:58:04.516007Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset spiceai.files
2024-09-16T03:58:04.697364Z  INFO runtime: Dataset spiceai.commits registered (github:github.com/spiceai/spiceai/commits), acceleration (arrow), results cache enabled.
2024-09-16T03:58:04.698871Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset spiceai.commits
2024-09-16T03:58:04.871658Z  INFO runtime::accelerated_table::refresh_task: Loaded 69 rows (380.35 kiB) for dataset spiceai.files in 355ms.
2024-09-16T03:58:05.178247Z  INFO runtime: Dataset spiceai.stargazers registered (github:github.com/spiceai/spiceai/stargazers), acceleration (arrow), results cache enabled.
2024-09-16T03:58:05.179671Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset spiceai.stargazers
2024-09-16T03:58:05.504365Z  INFO runtime: Dataset spiceai.issues registered (github:github.com/spiceai/spiceai/issues), acceleration (arrow), results cache enabled.
2024-09-16T03:58:05.505534Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset spiceai.issues
2024-09-16T03:58:06.563660Z  INFO runtime: Dataset spiceai.pulls registered (github:github.com/spiceai/spiceai/pulls), acceleration (arrow), results cache enabled.
2024-09-16T03:58:06.564929Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset spiceai.pulls
```

Wait until all datasets are loaded:

```console
2024-09-16T03:58:18.641091Z  INFO runtime::accelerated_table::refresh_task: Loaded 300 rows (641.44 kiB) for dataset spiceai.issues in 13s 135ms.
2024-09-16T03:58:20.553513Z  INFO runtime::accelerated_table::refresh_task: Loaded 300 rows (59.55 kiB) for dataset spiceai.stargazers in 15s 373ms.
2024-09-16T03:58:24.953706Z  INFO runtime::accelerated_table::refresh_task: Loaded 300 rows (204.38 kiB) for dataset spiceai.commits in 20s 254ms.
2024-09-16T03:58:48.900296Z  INFO runtime::accelerated_table::refresh_task: Loaded 300 rows (948.54 kiB) for dataset spiceai.pulls in 42s 335ms.
```

**Step 3.** Run `spice sql` in a new terminal to start an interactive SQL query session against the Spice runtime.

Get the 10 most recently updated issues:

```console
sql> select number, title, state, labels, updated_at from spiceai.issues order by updated_at desc limit 10;
+--------+------------------------------------------------------------------------+--------+--------------------+----------------------+
| number | title                                                                  | state  | labels             | updated_at           |
+--------+------------------------------------------------------------------------+--------+--------------------+----------------------+
| 2455   | v0.17.3-beta endgame                                                   | OPEN   | [endgame]          | 2024-09-02T15:49:21Z |
| 2147   | Enhancement: Native schema inference for Data Connectors               | OPEN   | [kind/enhancement] | 2024-09-02T12:40:31Z |
| 2460   | Clickhouse Native Schema Inference                                     | CLOSED | [kind/task]        | 2024-09-02T12:40:30Z |
| 2464   | ODBC Native Scheme Inference                                           | CLOSED | [kind/task]        | 2024-09-02T12:39:51Z |
| 2465   | Snowflake Native Schema Inference                                      | OPEN   | [kind/task]        | 2024-09-02T07:21:02Z |
| 2463   | Sqlite Native Schema Inference                                         | OPEN   | [kind/task]        | 2024-09-02T07:20:28Z |
| 2462   | PostgreSQL Native Schema Inference                                     | OPEN   | [kind/task]        | 2024-09-02T07:20:11Z |
| 2461   | DuckDB Native Schema Inference                                         | OPEN   | [kind/task]        | 2024-09-02T07:19:59Z |
| 1852   | Warn if `endpoint` param for `s3` data connector ends in `/`           | CLOSED | [kind/bug]         | 2024-09-02T07:12:29Z |
| 2349   | Accelerator queries with date ranges in where clause return no columns | CLOSED | [kind/bug]         | 2024-09-02T06:50:56Z |
+--------+------------------------------------------------------------------------+--------+--------------------+----------------------+

Time: 0.017607167 seconds. 10 rows.
```

Get the 10 most recently merged pull requests:

```console
sql> select number, title, state, merged_at from spiceai.pulls where state = 'MERGED' order by merged_at desc limit 10;
+--------+--------------------------------------------------------------------------------+--------+----------------------+
| number | title                                                                          | state  | merged_at            |
+--------+--------------------------------------------------------------------------------+--------+----------------------+
| 2475   | Remove non existing updated_at from github.pulls dataset                       | MERGED | 2024-09-02T16:40:15Z |
| 2474   | Fix LLMs health check; Add `updatedAt` field to GitHub connector               | MERGED | 2024-09-02T15:34:50Z |
| 2468   | List GitHub connector in readme                                                | MERGED | 2024-09-02T12:55:25Z |
| 2466   | Native clickhouse schema inference                                             | MERGED | 2024-09-02T12:40:29Z |
| 2467   | Add `assignees` and `labels` fields to github issues and github pulls datasets | MERGED | 2024-09-02T11:45:52Z |
| 2459   | Add `accelerated_refresh` to `task_history` table                              | MERGED | 2024-09-02T08:07:49Z |
| 2458   | Trim trailing `/` for S3 data connector                                        | MERGED | 2024-09-02T07:12:28Z |
| 2456   | Bump `datafusion` version to the latest                                        | MERGED | 2024-09-02T06:50:55Z |
| 2452   | GitHub connector: convert `labels` and `hashes` to primitive arrays            | MERGED | 2024-09-02T06:12:25Z |
| 2457   | task: Disable and update federation                                            | MERGED | 2024-09-02T05:33:34Z |
+--------+--------------------------------------------------------------------------------+--------+----------------------+

Time: 0.010307125 seconds. 10 rows.
```

Get the 10 most recent commits:

```console
sql> select message_head_line, author_name, sha from spiceai.commits order by committed_date desc limit 10;
+--------------------------------------------------------------------------+------------------+------------------------------------------+
| message_head_line                                                        | author_name      | sha                                      |
+--------------------------------------------------------------------------+------------------+------------------------------------------+
| Remove non existing updated_at from github.pulls dataset (#2475)         | Evgenii Khramkov | eeb94605ce737d779ae99e4617329164ce95c357 |
| Fix LLMs health check; Add `updatedAt` field to GitHub connector (#2474) | Evgenii Khramkov | e63fecb86657b97352d772247a12c357cde354c4 |
| List GitHub connector in readme (#2468)                                  | Evgenii Khramkov | 4fa914c95185290d6cbc20e108d575a22d33119b |
| Native clickhouse schema inference (#2466)                               | Phillip LeBlanc  | 2d8d9b573213d10bbd39c90e786b086d61166dae |
| Add `assignees` and `labels` fields to github issues and github pulls…   | Evgenii Khramkov | 582e702c53320975143b83330f3ae9cae3fc7241 |
| Add `accelerated_refresh` to `task_history` table (#2459)                | Phillip LeBlanc  | 2187f711364ddc3cd0ab635e414c682643347109 |
| Trim trailing `/` for S3 data connector (#2458)                          | Phillip LeBlanc  | 81260ed4583ec11547bac43a331cc46037f16bce |
| Bump datafusion to the latest (#2456)                                    | Sergei Grebnov   | 2e9db2b33154992c30603d46d5949ba456f9b2f6 |
| GitHub connector: convert `labels` and `hashes` to primitive arrays (…   | Sergei Grebnov   | 4f6ffb8728a2a9293ae120f384e19f61aba187b8 |
| task: Disable and update federation (#2457)                              | peasee           | 0358a11dd1c2ce4c15b949c7265cd70e2351d615 |
+--------------------------------------------------------------------------+------------------+------------------------------------------+

Time: 0.009864666 seconds. 10 rows.
```

Get the 10 most recent stargazers of the spiceai repository

```console
sql> select starred_at, login from spiceai.stargazers order by starred_at DESC limit 10;
+----------------------+----------------------+
| starred_at           | login                |
+----------------------+----------------------+
| 2024-09-15T13:22:09Z | cisen                |
| 2024-09-14T18:04:22Z | tyan-boot            |
| 2024-09-13T10:38:01Z | yofriadi             |
| 2024-09-13T10:01:33Z | FourSpaces           |
| 2024-09-13T04:02:11Z | d4x1                 |
| 2024-09-11T18:10:28Z | stephenakearns-insta |
| 2024-09-09T22:17:42Z | Lrs121               |
| 2024-09-09T19:56:26Z | jonathanfinley       |
| 2024-09-09T07:02:10Z | leookun              |
| 2024-09-09T03:04:27Z | royswale             |
+----------------------+----------------------+

Time: 0.0088075 seconds. 10 rows.
```

List beta release notes files:

```console
sql> select name, path, download_url, content from spiceai.files where path like 'docs/release_notes/%-beta.md';
+-----------------+------------------------------------+---------------------------------------------------------------------------------------------------+
| name            | path                               | download_url                                                                                      |
+-----------------+------------------------------------+---------------------------------------------------------------------------------------------------+
| v0.17.0-beta.md | docs/release_notes/v0.17.0-beta.md | https://raw.githubusercontent.com/spiceai/spiceai/v0.17.2-beta/docs/release_notes/v0.17.0-beta.md |
| v0.17.1-beta.md | docs/release_notes/v0.17.1-beta.md | https://raw.githubusercontent.com/spiceai/spiceai/v0.17.2-beta/docs/release_notes/v0.17.1-beta.md |
| v0.17.2-beta.md | docs/release_notes/v0.17.2-beta.md | https://raw.githubusercontent.com/spiceai/spiceai/v0.17.2-beta/docs/release_notes/v0.17.2-beta.md |
+-----------------+------------------------------------+---------------------------------------------------------------------------------------------------+
```

Read release notes of Spice `v0.17.2-beta` release

```console
sql> select content from spiceai.files where name = 'v0.17.0-beta.md';
+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| content                                                                                                                                                                                                                                                                                                                                             |
+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| # Spice v0.17.2-beta (Aug 26, 2024)                                                                                                                                                                                                                                                                                                                 |
|                                                                                                                                                                                                                                                                                                                                                     |
| The v0.17.2-beta release focuses on improving data accelerator compatibility, stability, and performance. Expanded data type support for DuckDB, SQLite, and PostgreSQL data accelerators (and data connectors) enables significantly more data types to be accelerated. Error handling and logging has also been improved along with several bugs. |
|                                                                                                                                                                                                                                                                                                                                                     |
| ## Highlights in v0.17.2-beta                                                                                                                                                                                                                                                                                                                       |
|                                                                                                                                                                                                                                                                                                                                                     |
| **Expanded Data Type Support for Data Accelerators:** DuckDB, SQLite, and PostgreSQL Data Accelerators now support a wider range of data types, enabling acceleration of more diverse datasets.                                                                                                                                                     |
|                                                                                                                                                                                                                                                                                                                                                     |
| **Enhanced Error Handling and Logging:** Improvements have been made to aid in troubleshooting and debugging.                                                                                                                                                                                                                                       |
|                                                                                                                                                                                                                                                                                                                                                     |
| **Anonymous Usage Telemetry:** Optional, anonymous, aggregated telemetry has been added to help improve Spice. This feature can be disabled. For details about collected data, see the [telemetry documentation](https://docs.spiceai.org/getting-started/telemetry).                                                                               |
|                                                                                                                                                                                                                                                                                                                                                     |
| To opt out of telemetry:                                                                                                                                                                                                                                                                                                                            |
|                                                                                                                                                                                                                                                                                                                                                     |
| 1. Using the CLI flag:                                                                                                                                                                                                                                                                                                                              |
|                                                                                                                                                                                                                                                                                                                                                     |
|    ```bash                                                                                                                                                                                                                                                                                                                                          |
|    spice run -- --telemetry-enabled false                                                                                                                                                                                                                                                                                                           |
|    ```                                                                                                                                                                                                                                                                                                                                              |
|                                                                                                                                                                                                                                                                                                                                                     |
| 2. Add configuration to `spicepod.yaml`:                                                                                                                                                                                                                                                                                                            |
|                                                                                                                                                                                                                                                                                                                                                     |
|    ```yaml                                                                                                                                                                                                                                                                                                                                          |
|    runtime:                                                                                                                                                                                                                                                                                                                                         |
|      telemetry:                                                                                                                                                                                                                                                                                                                                     |
|        enabled: false                                                                                                                                                                                                                                                                                                                               |
|    ```                                                                                                                                                                                                                                                                                                                                              |
|                                                                                                                                                                                                                                                                                                                                                     |
| **Improved Benchmarking:** A suite of performance benchmarking tests have been added to the project, helping to maintain and improve runtime performance; a top priority for the project.                                                                                                                                                           |
|                                                                                                                                                                                                                                                                                                                                                     |
| ## Breaking Changes                                                                                                                                                                                                                                                                                                                                 |
|                                                                                                                                                                                                                                                                                                                                                     |
| None.                                                                                                                                                                                                                                                                                                                                               |
|                                                                                                                                                                                                                                                                                                                                                     |
| ## Contributors                                                                                                                                                                                                                                                                                                                                     |
|                                                                                                                                                                                                                                                                                                                                                     |
| - @Jeadie                                                                                                                                                                                                                                                                                                                                           |
| - @y-f-u                                                                                                                                                                                                                                                                                                                                            |
| - @phillipleblanc                                                                                                                                                                                                                                                                                                                                   |
| - @sgrebnov                                                                                                                                                                                                                                                                                                                                         |
| - @Sevenannn                                                                                                                                                                                                                                                                                                                                        |
| - @peasee                                                                                                                                                                                                                                                                                                                                           |
| - @ewgenius                                                                                                                                                                                                                                                                                                                                         |
|                                                                                                                                                                                                                                                                                                                                                     |
| ## What's Changed                                                                                                                                                                                                                                                                                                                                   |
|                                                                                                                                                                                                                                                                                                                                                     |
| ### Dependencies                                                                                                                                                                                                                                                                                                                                    |
|                                                                                                                                                                                                                                                                                                                                                     |
| - **[DataFusion:](<(https://datafusion.apache.org/)>)** Upgraded from v40 to v41                                                                                                                                                                                                                                                                    |
|                                                                                                                                                                                                                                                                                                                                                     |
| ### Commits                                                                                                                                                                                                                                                                                                                                         |
|                                                                                                                                                                                                                                                                                                                                                     |
| - Pin actions/upload-artifact to v4.3.4 by @phillipleblanc in <https://github.com/spiceai/spiceai/pull/2200>                                                                                                                                                                                                                                        |
| - Update spicepod.schema.json by @github-actions in <https://github.com/spiceai/spiceai/pull/2202>                                                                                                                                                                                                                                                  |
| - Update to next release version, `v0.17.2-beta` by @phillipleblanc in <https://github.com/spiceai/spiceai/pull/2203>                                                                                                                                                                                                                               |
| - add accelerator beta criteria by @y-f-u in <https://github.com/spiceai/spiceai/pull/2201>                                                                                                                                                                                                                                                         |
| - update helm chart to 0.17.1-beta by @Sevenannn in <https://github.com/spiceai/spiceai/pull/2205>                                                                                                                                                                                                                                                  |
| - add dockerignore to avoid copy target and test folder by @y-f-u in <https://github.com/spiceai/spiceai/pull/2206>                                                                                                                                                                                                                                 |
| - add client timeout for deltalake connector by @y-f-u in <https://github.com/spiceai/spiceai/pull/2208>                                                                                                                                                                                                                                            |
| - Upgrade tonic and opentelemetry-proto by @phillipleblanc in <https://github.com/spiceai/spiceai/pull/2223>                                                                                                                                                                                                                                        |
| - Add index and resource tuning for postgres ghcr image to support postgres benchmark in sf1 by @Sevenannn in <https://github.com/spiceai/spiceai/pull/2196>                                                                                                                                                                                        |
| - Remove embedding columns from `retrieved_primary_keys` in v1/search by @Jeadie in <https://github.com/spiceai/spiceai/pull/2176>                                                                                                                                                                                                                  |
| - use file as db_path_param as the param prefix is trimmed by @y-f-u in <https://github.com/spiceai/spiceai/pull/2230>                                                                                                                                                                                                                              |
| - use file for sqlite db path param by @y-f-u in <https://github.com/spiceai/spiceai/pull/2231>                                                                                                                                                                                                                                                     |
| - docs: Clarify the global requirement for local_infile when loading TPCH by @peasee in <https://github.com/spiceai/spiceai/pull/2228>                                                                                                                                                                                                              |
| - Revert pinning actions/upload-artifact@v4 by @phillipleblanc in <https://github.com/spiceai/spiceai/pull/2232>                                                                                                                                                                                                                                    |
| - Runtime tools to chat models by @Jeadie in <https://github.com/spiceai/spiceai/pull/2207>                                                                                                                                                                                                                                                         |
| - Create `runtime.task_history` table for queries, and embeddings by @Jeadie in <https://github.com/spiceai/spiceai/pull/2191>                                                                                                                                                                                                                      |
| - chore: Update Databricks ODBC Bench to use TPCH SF1 by @peasee in <https://github.com/spiceai/spiceai/pull/2238>                                                                                                                                                                                                                                  |
| - Replace `metrics-rs` with OpenTelemetry Metrics by @phillipleblanc in <https://github.com/spiceai/spiceai/pull/2240>                                                                                                                                                                                                                              |
| - fix: Remove dead code by @peasee in <https://github.com/spiceai/spiceai/pull/2249>                                                                                                                                                                                                                                                                |
| - Improve tool quality and add vector search tool by @Jeadie in <https://github.com/spiceai/spiceai/pull/2250>                                                                                                                                                                                                                                      |
| - fix missing partition cols in delta lake by @y-f-u in <https://github.com/spiceai/spiceai/pull/2253>                                                                                                                                                                                                                                              |
| - download file from remote for delta testing by @y-f-u in <https://github.com/spiceai/spiceai/pull/2254>                                                                                                                                                                                                                                           |
| - feat: Set SQLite DB path to .spice/data by @peasee in <https://github.com/spiceai/spiceai/pull/2242>                                                                                                                                                                                                                                              |
| - Support tools for chat completions in streaming mode by @ewgenius in <https://github.com/spiceai/spiceai/pull/2255>                                                                                                                                                                                                                               |
| - Load component `description` field from spicepod.yaml and include in LLM context by @ewgenius in <https://github.com/spiceai/spiceai/pull/2261>                                                                                                                                                                                                   |
| - Add parameter for `connection_pool_size` in the Postgres Data Connector by @phillipleblanc in <https://github.com/spiceai/spiceai/pull/2251>                                                                                                                                                                                                      |
| - Add primary keys to response of `DocumentSimilarityTool` by @Jeadie in <https://github.com/spiceai/spiceai/pull/2263>                                                                                                                                                                                                                             |
| - run queries bash script by @y-f-u in <https://github.com/spiceai/spiceai/pull/2262>                                                                                                                                                                                                                                                               |
| - Run benchmark test on schedule by @Sevenannn in <https://github.com/spiceai/spiceai/pull/2277>                                                                                                                                                                                                                                                    |
| - feat: Add a reference to originating App for a Dataset by @peasee in <https://github.com/spiceai/spiceai/pull/2283>                                                                                                                                                                                                                               |
| - Tool use & telemetry productionisation. by @Jeadie in <https://github.com/spiceai/spiceai/pull/2286>                                                                                                                                                                                                                                              |
| - Fix cron in benchmarks.yml by @Sevenannn in <https://github.com/spiceai/spiceai/pull/2288>                                                                                                                                                                                                                                                        |
| - Upgrade to DataFusion v41 by @phillipleblanc in <https://github.com/spiceai/spiceai/pull/2290>                                                                                                                                                                                                                                                    |
| - Chat completions adjustments and fixes by @ewgenius in <https://github.com/spiceai/spiceai/pull/2292>                                                                                                                                                                                                                                             |
| - Define the new metrics Arrow schema based on Open Telemetry by @phillipleblanc in <https://github.com/spiceai/spiceai/pull/2295>                                                                                                                                                                                                                  |
| - OpenTelemetry Metrics Arrow exporter to `runtime.metrics` table by @phillipleblanc in <https://github.com/spiceai/spiceai/pull/2296>                                                                                                                                                                                                              |
| - Calculate summary metrics from histograms for Prometheus endpoint by @phillipleblanc in <https://github.com/spiceai/spiceai/pull/2302>                                                                                                                                                                                                            |
| - Add back Spice DF runtime_env during SessionContext construction by @phillipleblanc in <https://github.com/spiceai/spiceai/pull/2304>                                                                                                                                                                                                             |
| - Add integration test for S3 data connector by @phillipleblanc in <https://github.com/spiceai/spiceai/pull/2305>                                                                                                                                                                                                                                   |
| - Fix `secrets.inject_secrets` when secret not found. by @Jeadie in <https://github.com/spiceai/spiceai/pull/2306>                                                                                                                                                                                                                                  |
| - Intra-table federation query on duckdb accelerated table by @y-f-u in <https://github.com/spiceai/spiceai/pull/2299>                                                                                                                                                                                                                              |
| - Postgres federation on acceleration by @y-f-u in <https://github.com/spiceai/spiceai/pull/2309>                                                                                                                                                                                                                                                   |
| - sqlite intra table federation on acceleration by @y-f-u in <https://github.com/spiceai/spiceai/pull/2308>                                                                                                                                                                                                                                         |
| - feat: Add `DataAccelerator::init()` for SQLite acceleration federation by @peasee in <https://github.com/spiceai/spiceai/pull/2293>                                                                                                                                                                                                               |
| - Initial framework for collecting anonymous usage telemetry by @phillipleblanc in <https://github.com/spiceai/spiceai/pull/2310>                                                                                                                                                                                                                   |
| - Add gRPC action to trigger accelerated dataset refresh by @sgrebnov in <https://github.com/spiceai/spiceai/pull/2316>                                                                                                                                                                                                                             |
| - add `disable_query_push_down` option to acceleration settings by @y-f-u in <https://github.com/spiceai/spiceai/pull/2327>                                                                                                                                                                                                                         |
| - Remove `v1/assist` by @Jeadie in <https://github.com/spiceai/spiceai/pull/2312>                                                                                                                                                                                                                                                                   |
| - bump table provider version to set the correct dialect for postgres writer by @y-f-u in <https://github.com/spiceai/spiceai/pull/2329>                                                                                                                                                                                                            |
| - Send telemetry on startup by @phillipleblanc in <https://github.com/spiceai/spiceai/pull/2331>                                                                                                                                                                                                                                                    |
| - Calculate resource IDs for telemetry by @phillipleblanc in <https://github.com/spiceai/spiceai/pull/2332>                                                                                                                                                                                                                                         |
| - Refactor `v1/search`: include WHERE condition, allow extra columns in projection. by @Jeadie in <https://github.com/spiceai/spiceai/pull/2328>                                                                                                                                                                                                    |
| - Add integration test for gRPC dataset refresh action by @sgrebnov in <https://github.com/spiceai/spiceai/pull/2330>                                                                                                                                                                                                                               |
| - Propagate errors through all `task_history` nested spans by @phillipleblanc in <https://github.com/spiceai/spiceai/pull/2337>                                                                                                                                                                                                                     |
| - Improve tools by @Jeadie in <https://github.com/spiceai/spiceai/pull/2338>                                                                                                                                                                                                                                                                        |
| - update duckdb rs version to support more types: interval/duration/etc by @y-f-u in <https://github.com/spiceai/spiceai/pull/2336>                                                                                                                                                                                                                 |
| - feat: Add DuckDB accelerator init, attach databases for federation by @peasee in <https://github.com/spiceai/spiceai/pull/2335>                                                                                                                                                                                                                   |
| - Add query telemetry metrics by @phillipleblanc in <https://github.com/spiceai/spiceai/pull/2333>                                                                                                                                                                                                                                                  |
| - Add system prompts for LLMs; system prompts for tool using models. by @Jeadie in <https://github.com/spiceai/spiceai/pull/2342>                                                                                                                                                                                                                   |
| - Fix benchmark test to keep running when there's failed queries by @Sevenannn in <https://github.com/spiceai/spiceai/pull/2347>                                                                                                                                                                                                                    |
| - Tools as a spicepod first class citizen. by @Jeadie in <https://github.com/spiceai/spiceai/pull/2344>                                                                                                                                                                                                                                             |
| - Add `bytes_processed` telemetry metric by @phillipleblanc in <https://github.com/spiceai/spiceai/pull/2343>                                                                                                                                                                                                                                       |
| - fix misaligned columns from delta lake by @y-f-u in <https://github.com/spiceai/spiceai/pull/2356>                                                                                                                                                                                                                                                |
| - Emit telemetry metrics to `runtime.metrics`/Prometheus as well by @phillipleblanc in <https://github.com/spiceai/spiceai/pull/2352>                                                                                                                                                                                                               |
| - Use UTC timezone for telemetry timestamps by @phillipleblanc in <https://github.com/spiceai/spiceai/pull/2354>                                                                                                                                                                                                                                    |
| - Fix MetricType deserialization by @phillipleblanc in <https://github.com/spiceai/spiceai/pull/2358>                                                                                                                                                                                                                                               |
| - Add dataset details to tool using LLMs; early check tables in vector search by @Jeadie in <https://github.com/spiceai/spiceai/pull/2353>                                                                                                                                                                                                          |
| - Bump datafusion-federation/datafusion-table-providers dependencies by @phillipleblanc in <https://github.com/spiceai/spiceai/pull/2360>                                                                                                                                                                                                           |
| - Update spicepod.schema.json by @github-actions in <https://github.com/spiceai/spiceai/pull/2362>                                                                                                                                                                                                                                                  |
| - fix: Disable DuckDB and SQLite federation by @peasee in <https://github.com/spiceai/spiceai/pull/2371>                                                                                                                                                                                                                                            |
| - Fix system prompt in ToolUsingChat, fix builtin registration by @Jeadie in <https://github.com/spiceai/spiceai/pull/2367>                                                                                                                                                                                                                         |
| - fix: Use --profile release for benchmarks by @peasee in <https://github.com/spiceai/spiceai/pull/2372>                                                                                                                                                                                                                                            |
| - nql parameter 'use' -> 'model' by @Jeadie in <https://github.com/spiceai/spiceai/pull/2366>                                                                                                                                                                                                                                                       |
|                                                                                                                                                                                                                                                                                                                                                     |
| **Full Changelog**: <https://github.com/spiceai/spiceai/compare/v0.17.1-beta...v0.17.2-beta>                                                                                                                                                                                                                                                        |
|                                                                                                                                                                                                                                                                                                                                                     |
+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

Time: 0.008751208 seconds. 1 rows.
```
