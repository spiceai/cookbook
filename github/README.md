# GitHub Data Connector

Works with `v1.6+`

This recipe will use the [spiceai/spiceai](https://github.com/spiceai/spiceai) repo for a demo.

## Pre-requisites

- Spice is installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation).
- GitHub personal access token, [Learn more](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-personal-access-token-classic) how to create one.

  Grant the token both of these scopes:

  - `repo` — for the `files`, `issues`, `pulls`, and `commits` datasets.
  - `read:user` (or `user:email`) — the `stargazers` and `members` datasets select
    the user `email` field, which GitHub only returns for tokens with one of these
    scopes. Without it those two datasets fail to load with `Your token has not
    been granted the required scopes to execute this query`.

  [![Watch the Spice.ai local GitHub connector demo](https://img.youtube.com/vi/mxwt0HEF1VQ/hqdefault.jpg)](https://www.youtube.com/embed/mxwt0HEF1VQ)

**Step 0.** Clone the repository if not already cloned.

```bash
git clone https://github.com/spiceai/cookbook # Skip if already cloned
cd cookbook/github
```

**Step 1.** Copy the `.env` file into a new `.env.local` file in this directory, and set the `GITHUB_TOKEN` environment variable to your personal access token.

```env
GITHUB_TOKEN=<your_github_token>
```

**Step 2.** Run the Spice runtime with `spice run` from the directory with the `spicepod.yaml` file.

```bash
spice run
```

```console
 INFO Spice.ai runtime starting...
2025-07-16T15:17:13.713677Z  INFO runtime::init::caching: Initialized sql results cache; max size: 128.00 MiB, item ttl: 1s, hashing algorithm: XXH3, encoding: none
2025-07-16T15:17:13.713846Z  INFO runtime::init::caching: Initialized search results cache; max size: 128.00 MiB, item ttl: 1s, engine: Moka
2025-07-16T15:17:14.160281Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2025-07-16T15:17:14.162142Z  INFO runtime::init::dataset: Dataset spiceai.issues initializing...
2025-07-16T15:17:14.162164Z  INFO runtime::init::dataset: Dataset spiceai.pulls initializing...
2025-07-16T15:17:14.162231Z  INFO runtime::init::dataset: Dataset spiceai.commits initializing...
2025-07-16T15:17:14.162161Z  INFO runtime::init::dataset: Dataset apache.members initializing...
2025-07-16T15:17:14.162218Z  INFO runtime::init::dataset: Dataset spiceai.stargazers initializing...
2025-07-16T15:17:14.162515Z  INFO runtime::init::dataset: Dataset spiceai.files initializing...
2025-07-16T15:17:14.166935Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2025-07-16T15:17:15.311687Z  INFO runtime::init::dataset: Dataset spiceai.commits registered (github:github.com/spiceai/spiceai/commits), acceleration (arrow), results cache enabled.
2025-07-16T15:17:15.313347Z  INFO runtime_table::accelerated::refresh_task: Loading data for dataset spiceai.commits
2025-07-16T15:17:15.507378Z  INFO runtime::init::dataset: Dataset spiceai.stargazers registered (github:github.com/spiceai/spiceai/stargazers), acceleration (arrow), results cache enabled.
2025-07-16T15:17:15.508684Z  INFO runtime_table::accelerated::refresh_task: Loading data for dataset spiceai.stargazers
2025-07-16T15:17:16.406635Z  INFO runtime::init::dataset: Dataset spiceai.files registered (github:github.com/spiceai/spiceai/files/trunk), acceleration (arrow), results cache enabled.
2025-07-16T15:17:16.407961Z  INFO runtime_table::accelerated::refresh_task: Loading data for dataset spiceai.files
2025-07-16T15:17:16.772995Z  INFO runtime::init::dataset: Dataset spiceai.issues registered (github:github.com/spiceai/spiceai/issues), acceleration (arrow), results cache enabled.
2025-07-16T15:17:16.774218Z  INFO runtime_table::accelerated::refresh_task: Loading data for dataset spiceai.issues
2025-07-16T15:17:17.447103Z  INFO runtime::init::dataset: Dataset apache.members registered (github:github.com/apache/members), acceleration (arrow), results cache enabled.
2025-07-16T15:17:17.448839Z  INFO runtime_table::accelerated::refresh_task: Loading data for dataset apache.members
```

Wait until all datasets are loaded:

```console
2025-07-16T15:17:18.240151Z  INFO runtime_table::accelerated::refresh_task: Loaded 52 rows (184.75 kiB) for dataset spiceai.issues in 1s 465ms.
2025-07-16T15:17:19.861151Z  INFO runtime_table::accelerated::refresh_task: Loaded 300 rows (617.12 kiB) for dataset spiceai.stargazers in 4s 352ms.
2025-07-16T15:17:19.965102Z  INFO runtime_table::accelerated::refresh_task: Loaded 300 rows (618.50 kiB) for dataset apache.members in 2s 516ms.
2025-07-16T15:17:23.204760Z  INFO runtime_table::accelerated::refresh_task: Loaded 140 rows (1.20 MiB) for dataset spiceai.files in 6s 796ms.
2025-07-16T15:17:26.329481Z  INFO runtime_table::accelerated::refresh_task: Loaded 49 rows (149.97 kiB) for dataset spiceai.pulls in 3s 203ms.
2025-07-16T15:17:26.419725Z  INFO runtime_table::accelerated::refresh_task: Loaded 300 rows (908.66 kiB) for dataset spiceai.commits in 11s 106ms.
```

**Step 3.** Run `spice sql` in a new terminal to start an interactive SQL query session against the Spice runtime.

The datasets track live repositories — `spiceai.issues` and `spiceai.pulls` are additionally
limited to a 7-day `refresh_data_window` — so the rows below are a snapshot, not a fixed
expectation. Column names and types are what to compare against.

Get the 10 most recently updated issues:

```sql
select number, title, state, labels, updated_at from spiceai.issues order by updated_at desc limit 10;
```

```console
+--------+-----------------------------------------------------------------------------------------------------------------------------------------------------+---------+-------------------------------------------+---------------------+
| number |                                                                        title                                                                        |  state  |                   labels                  |      updated_at     |
|  int64 |                                                                       varchar                                                                       | varchar |                 varchar[]                 |    timestamp[ms]    |
+--------+-----------------------------------------------------------------------------------------------------------------------------------------------------+---------+-------------------------------------------+---------------------+
| 14058  | Enhancement: Cloud Connect GetDatasets command so spice cloud datasets works for self-hosted instances                                              | OPEN    | [kind/enhancement, area/api]              | 2026-09-12T09:34:27 |
| 14057  | Cayenne: a partition_by expression whose function semantics change across an upgrade has no compatibility guard, so pruning can silently drop rows  | OPEN    | [kind/bug, area/cayenne]                  | 2026-09-12T09:34:26 |
| 14056  | BigQuery: federate date_part('dow', …) as EXTRACT(DAYOFWEEK …) - 1 now that both weekday spellings agree locally (follow-up to #13920)              | OPEN    | [kind/enhancement, area/data-connectors]  | 2026-09-12T09:34:25 |
| 14018  | `Dataset load summary` counts 4 datasets for a Spicepod that declares 2                                                                             | OPEN    | [kind/bug, area/runtime]                  | 2026-09-12T09:34:24 |
| 14008  | A projection above a LIMIT keeps qualifiers naming the relation the derived table now encloses, so the remote engine cannot bind them               | OPEN    | [kind/bug, area/sql]                      | 2026-09-12T09:34:23 |
| 13961  | A chunked index's upsert and pruning are two inner-index operations, so concurrent compute_index calls for one key can prune a newer write's chunks | OPEN    | [kind/bug, area/search]                   | 2026-09-12T09:34:21 |
| 13949  | No test covers Arrow hash-index activation under `refresh_mode: caching`                                                                            | OPEN    | [kind/bug]                                | 2026-09-12T09:34:20 |
| 13937  | GraphQL page-size shrink does not trigger on GitHub's 'Resource limits for this query exceeded'                                                     | OPEN    | [kind/bug, area/data-connectors]          | 2026-09-12T09:34:19 |
| 13927  | A plan cached by an in-flight planner survives the invalidation that should have dropped it                                                         | OPEN    | [kind/bug]                                | 2026-09-12T09:34:19 |
| 13916  | A logical plan built before a hot reload repopulates the plan cache after clear_cached_plans and is served stale                                    | OPEN    | [kind/bug, area/datafusion, area/caching] | 2026-09-12T09:34:18 |
+--------+-----------------------------------------------------------------------------------------------------------------------------------------------------+---------+-------------------------------------------+---------------------+

Time: 0.001630834 seconds. 10 rows.
```

Get the 10 most recently merged pull requests:

```sql
select number, title, state, merged_at from spiceai.pulls where state = 'MERGED' order by merged_at desc limit 10;
```

```console
+--------+-----------------------------------------------------------------------------------------------------+---------+---------------------+
| number |                                                title                                                |  state  |      merged_at      |
|  int64 |                                               varchar                                               | varchar |    timestamp[ms]    |
+--------+-----------------------------------------------------------------------------------------------------+---------+---------------------+
| 14049  | fix(deps): bump arrow-rs fork pin for Decimal->Float rounding fix                                   | MERGED  | 2026-09-11T19:52:55 |
| 14047  | fix(cayenne): make DELETE, UPDATE and INSERT work on a `mode: memory` acceleration (fixes #12008)   | MERGED  | 2026-09-11T19:52:55 |
| 14040  | fix: clarify OpenDAL S3 retry warnings                                                              | MERGED  | 2026-09-11T19:52:55 |
| 14022  | Fix subqueries with use_source acceleration                                                         | MERGED  | 2026-09-11T19:52:55 |
| 14031  | endgame: include spiceai/skills versioned release                                                   | MERGED  | 2026-09-11T05:46:52 |
| 14021  | fix(caching): partition doomed entries at the survivor cutoff so eviction converges (closes #13994) | MERGED  | 2026-09-11T05:46:52 |
| 14035  | perf(vortex): defer projection setup on filtered scans until the filter resolves                    | MERGED  | 2026-09-11T05:05:28 |
| 14009  | Reduce Cayenne allocations during primary-key validation and filtering                              | MERGED  | 2026-09-10T20:46:24 |
| 14012  | fix(deps): bump arrow-rs to correctly-rounded Decimal→Float cast (closes #13978)                    | MERGED  | 2026-09-10T20:46:24 |
| 13996  | test(forks): guard seven fork patches that had no repo-side test                                    | MERGED  | 2026-09-10T20:46:24 |
+--------+-----------------------------------------------------------------------------------------------------+---------+---------------------+

Time: 0.001864792 seconds. 10 rows.
```

Query the review comments on a pull request:

```sql
WITH review_comments AS (
  SELECT
    number,
    UNNEST(review_comments) AS comment
  FROM
    spiceai.pulls
)

SELECT
  comment.author,
  comment.created_at,
  comment.body
FROM
  review_comments
LIMIT 1;
```

```console
+---------------------------------+-------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| review_comments.comment[author] | review_comments.comment[created_at] |                                                                                                                                                                                                                                                                                                                                review_comments.comment[body]                                                                                                                                                                                                                                                                                                                               |
|             varchar             |            timestamp[ms]            |                                                                                                                                                                                                                                                                                                                                           varchar                                                                                                                                                                                                                                                                                                                                          |
+---------------------------------+-------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| copilot-pull-request-reviewer   | 2026-09-11T19:55:24                 | This pin bump invalidates the ledger's repo-side guard for the balanced `list_contains` patch. The linked Vortex change sends primitive lists with at least four elements through `hash_probe_contains`, while `test_large_in_list_filter_pushdown_stays_evaluable` uses an 8,192-element `INT` list; that test therefore no longer constructs the balanced OR tree whose loss it is meant to catch. Update the guard to force the unsupported-probe fallback (for example, a large decimal list) and revise its stale explanation. Unverified by execution here because the review container cannot build the fork dependency; this follows the new dispatch and the existing test input. |
+---------------------------------+-------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

Time: 0.003752708 seconds. 1 rows.
```

Query the discussion on a pull request:

```sql
WITH discussion AS (
  SELECT
    number,
    UNNEST(discussion) AS comment
  FROM
    spiceai.pulls
)

SELECT
  comment.author,
  comment.created_at,
  comment.body
FROM
  discussion
LIMIT 1;
```

```console
+----------------------------+--------------------------------+-------------------------------------------------------------+
| discussion.comment[author] | discussion.comment[created_at] |                   discussion.comment[body]                  |
|           varchar          |          timestamp[ms]         |                           varchar                           |
+----------------------------+--------------------------------+-------------------------------------------------------------+
| github-actions             | 2026-09-11T19:49:44            | ## ✅ Pull with Spice Passed                                |
|                            |                                |                                                             |
|                            |                                | ### Passing checks:                                         |
|                            |                                |                                                             |
|                            |                                | - ✅ Title meets minimum length requirement (10 characters) |
|                            |                                | - ✅ No banned labels detected                              |
|                            |                                | - ✅ Has a label from required category `kind/`             |
|                            |                                | - ✅ Has a label from required category `area/`             |
|                            |                                | - ✅ Has at least one assignee: `bjchambers`                |
|                            |                                |                                                             |
|                            |                                |                                                             |
+----------------------------+--------------------------------+-------------------------------------------------------------+

Time: 0.001584416 seconds. 1 rows.
```

Get the 10 most recent commits:

```sql
select message_head_line, author_name, sha from spiceai.commits order by committed_date desc limit 10;
```

```console
+------------------------------------------------------------------------+-----------------+------------------------------------------+
|                            message_head_line                           |   author_name   |                    sha                   |
|                                 varchar                                |     varchar     |                  varchar                 |
+------------------------------------------------------------------------+-----------------+------------------------------------------+
| fix: clarify OpenDAL S3 retry warnings (#14040)                        | Luke Kim        | ecd92a5122415ecf2a7b4a976c4ce31c64b69f00 |
| fix(cayenne): make DELETE, UPDATE and INSERT work on a `mode: memory`… | Ben Chambers    | 9b9c4fae1239d30ae800df89cef8d0fd56e569d3 |
| Fix subqueries with use_source acceleration (#14022)                   | Phillip LeBlanc | 48f47f6b9dcd8f93d6bce8b7637e02f7af1ba15a |
| fix(deps): bump arrow-rs fork pin for Decimal->Float rounding fix (#1… | Jack Eadie      | eba6c527fdbb1c725a49132f09a9422441de20c0 |
| fix(caching): partition doomed entries at the survivor cutoff so evic… | Jack Eadie      | 4c7b254d6c17ee7124618d37553dc0f5aa852e90 |
| endgame: include spiceai/skills versioned release (#14031)             | Luke Kim        | 3cccd7ccc900f7925a61c0063503ab3046eaf522 |
| perf(vortex): defer projection setup on filtered scans until the filt… | Ben Chambers    | e8dd9d2bf9f4bfc8afc6d8dd97f5474501be64c8 |
| fix(deps): bump arrow-rs to correctly-rounded Decimal→Float cast (clo… | Jack Eadie      | 9972f4a6d455517099c1ca604bbc6a8c8c26f80f |
| test(forks): guard seven fork patches that had no repo-side test (#13… | Viktor Yershov  | 919a66c54554664f667d512f9c45c9516f541ddd |
| Reduce Cayenne allocations during primary-key validation and filterin… | Luke Kim        | 94e6ab6bf2a2ef26070c9549627d14ef8bd6ab59 |
+------------------------------------------------------------------------+-----------------+------------------------------------------+

Time: 0.002161167 seconds. 10 rows.
```

Get the 10 most recent stargazers of the spiceai repository

```sql
select starred_at, login from spiceai.stargazers order by starred_at DESC limit 10;
```

```console
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

List 10 members of the Apache GitHub Organization

```sql
select created_at, username from apache.members limit 10;
```

```console
+---------------------+----------+
| created_at          | username |
+---------------------+----------+
| 2008-02-17T05:48:58 | vic      |
| 2008-02-21T16:56:47 | amoeba   |
| 2008-02-27T23:16:48 | brianm   |
| 2008-03-03T16:49:29 | ruphy    |
| 2008-03-05T18:57:18 | infil00p |
| 2008-03-05T20:21:24 | jthomas  |
| 2008-03-05T23:10:37 | mjwall   |
| 2008-03-27T12:56:22 | mrkn     |
| 2008-04-02T18:39:35 | ryw      |
| 2008-04-03T23:53:41 | rubys    |
+---------------------+----------+

Time: 0.027337792 seconds. 10 rows.
```

List beta release notes files:

```sql
select name, path, download_url from spiceai.files where path like 'docs/release_notes/%-beta.md';
```

```console
+-----------------+-----------------------------------------+-------------------------------------------------------------------------------------------------+
|       name      |                   path                  |                                           download_url                                          |
|     varchar     |                 varchar                 |                                             varchar                                             |
+-----------------+-----------------------------------------+-------------------------------------------------------------------------------------------------+
| v0.17.0-beta.md | docs/release_notes/beta/v0.17.0-beta.md | https://raw.githubusercontent.com/spiceai/spiceai/trunk/docs/release_notes/beta/v0.17.0-beta.md |
| v0.17.1-beta.md | docs/release_notes/beta/v0.17.1-beta.md | https://raw.githubusercontent.com/spiceai/spiceai/trunk/docs/release_notes/beta/v0.17.1-beta.md |
| v0.17.2-beta.md | docs/release_notes/beta/v0.17.2-beta.md | https://raw.githubusercontent.com/spiceai/spiceai/trunk/docs/release_notes/beta/v0.17.2-beta.md |
| v0.17.3-beta.md | docs/release_notes/beta/v0.17.3-beta.md | https://raw.githubusercontent.com/spiceai/spiceai/trunk/docs/release_notes/beta/v0.17.3-beta.md |
| v0.17.4-beta.md | docs/release_notes/beta/v0.17.4-beta.md | https://raw.githubusercontent.com/spiceai/spiceai/trunk/docs/release_notes/beta/v0.17.4-beta.md |
| v0.18.0-beta.md | docs/release_notes/beta/v0.18.0-beta.md | https://raw.githubusercontent.com/spiceai/spiceai/trunk/docs/release_notes/beta/v0.18.0-beta.md |
| v0.18.1-beta.md | docs/release_notes/beta/v0.18.1-beta.md | https://raw.githubusercontent.com/spiceai/spiceai/trunk/docs/release_notes/beta/v0.18.1-beta.md |
| v0.18.2-beta.md | docs/release_notes/beta/v0.18.2-beta.md | https://raw.githubusercontent.com/spiceai/spiceai/trunk/docs/release_notes/beta/v0.18.2-beta.md |
| v0.18.3-beta.md | docs/release_notes/beta/v0.18.3-beta.md | https://raw.githubusercontent.com/spiceai/spiceai/trunk/docs/release_notes/beta/v0.18.3-beta.md |
| v0.19.0-beta.md | docs/release_notes/beta/v0.19.0-beta.md | https://raw.githubusercontent.com/spiceai/spiceai/trunk/docs/release_notes/beta/v0.19.0-beta.md |
| v0.19.1-beta.md | docs/release_notes/beta/v0.19.1-beta.md | https://raw.githubusercontent.com/spiceai/spiceai/trunk/docs/release_notes/beta/v0.19.1-beta.md |
| v0.19.2-beta.md | docs/release_notes/beta/v0.19.2-beta.md | https://raw.githubusercontent.com/spiceai/spiceai/trunk/docs/release_notes/beta/v0.19.2-beta.md |
| v0.19.3-beta.md | docs/release_notes/beta/v0.19.3-beta.md | https://raw.githubusercontent.com/spiceai/spiceai/trunk/docs/release_notes/beta/v0.19.3-beta.md |
| v0.19.4-beta.md | docs/release_notes/beta/v0.19.4-beta.md | https://raw.githubusercontent.com/spiceai/spiceai/trunk/docs/release_notes/beta/v0.19.4-beta.md |
| v0.20.0-beta.md | docs/release_notes/beta/v0.20.0-beta.md | https://raw.githubusercontent.com/spiceai/spiceai/trunk/docs/release_notes/beta/v0.20.0-beta.md |
+-----------------+-----------------------------------------+-------------------------------------------------------------------------------------------------+

Time: 0.001074959 seconds. 15 rows.
```

Read release notes of Spice `v0.17.2-beta` release

```sql
select content from spiceai.files where name = 'v0.17.2-beta.md';
```

````console
+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                                                                                                                                                                       content                                                                                                                                                                       |
|                                                                                                                                                                       varchar                                                                                                                                                                       |
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

Time: 0.000985458 seconds. 1 rows.
````
