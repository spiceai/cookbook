# Hugging Face Data Connector

Works with `v2.4+`

The Hugging Face data connector queries and accelerates datasets on the [Hugging Face Hub](https://huggingface.co/datasets) with SQL. It reads the Parquet, CSV, TSV, JSON, JSONL, and ORC files of public, gated, and private datasets. A public dataset needs no account, no token, and no parameters.

This recipe queries three public datasets, joins files in two formats, pins a dataset to a commit, and accelerates a dataset locally with Cayenne:

| Dataset                                                              | Contents                                                                         | Files      |
| -------------------------------------------------------------------- | -------------------------------------------------------------------------------- | ---------- |
| [stanfordnlp/imdb](https://huggingface.co/datasets/stanfordnlp/imdb) | 100,000 movie reviews labeled by sentiment                                       | Parquet    |
| [mteb/scifact](https://huggingface.co/datasets/mteb/scifact)         | Scientific claims, paper abstracts, and the relevance judgments that link them   | JSONL, TSV |
| [openai/gsm8k](https://huggingface.co/datasets/openai/gsm8k)         | Grade-school math word problems                                                  | Parquet    |

## Prerequisites

- Spice v2.4 or later. See [Installation](https://spiceai.org/docs/installation).
- Network access to `huggingface.co`. Steps 1–6 need no Hugging Face account.

## Step 1. Review the Spicepod

`spicepod.yaml` in this directory defines five datasets:

```yaml
version: v2
kind: Spicepod
name: huggingface

datasets:
  # A folder of Parquet files. No parameters: the connector infers the format from the
  # files in the folder. `_location` adds a column with each row's source file and commit.
  - from: hf://datasets/stanfordnlp/imdb/plain_text/
    name: imdb
    description: IMDB movie reviews labeled by sentiment
    metadata:
      _location: enabled

  # SciFact, from the MTEB retrieval benchmark: claims (JSONL), paper abstracts (JSONL),
  # and the relevance judgments that link them (TSV).
  - from: hf://datasets/mteb/scifact/queries.jsonl
    name: scifact_queries
    description: SciFact scientific claims
  - from: hf://datasets/mteb/scifact/corpus.jsonl
    name: scifact_corpus
    description: SciFact paper abstracts
  - from: hf://datasets/mteb/scifact/qrels/test.tsv
    name: scifact_qrels
    description: SciFact test-split relevance judgments (claim id, abstract id, score)

  # One file of GSM8K, pinned to a commit so that its contents never change.
  - from: hf://datasets/openai/gsm8k@740312add88f781978c0658806c59bc2815b9866/main/test-00000-of-00001.parquet
    name: gsm8k
    description: GSM8K grade-school math word problems, test split
```

Each `from` uses the location syntax that the Hugging Face `HfFileSystem`, DuckDB, and Polars share, so a path copied from a dataset card or a DuckDB query works unchanged:

```text
hf://datasets/<owner>/<dataset>[@<revision>][/<path>]
```

| Part                | Description                                                                                     |
| ------------------- | ----------------------------------------------------------------------------------------------- |
| `<owner>/<dataset>` | The dataset repository, for example `stanfordnlp/imdb`.                                         |
| `@<revision>`       | Optional. A branch, tag, or commit. Defaults to `main`.                                         |
| `<path>`            | Optional. A file, a folder (ending in `/`), or a glob such as `plain_text/train-*.parquet`.     |

No dataset sets `file_format`: the connector takes the format from the file extension or, for a folder, from the files in it.

## Step 2. Start Spice

From the cookbook root:

```bash
cd huggingface
spice run
```

```console
 INFO Spice.ai runtime starting...
2026-10-08T22:21:51.204307Z  INFO spiced: Starting runtime v2.4.0-unstable+models.metal
...
2026-10-08T22:21:51.209304Z  INFO runtime::init::dataset: Loading datasets: 5 tasks dispatched, 0 skipped at accelerator init (of 5 total; localpod datasets may be chained).
2026-10-08T22:21:51.209314Z  INFO runtime::init::dataset: Dataset scifact_corpus initializing...
2026-10-08T22:21:51.209329Z  INFO runtime::init::dataset: Dataset imdb initializing...
2026-10-08T22:21:51.209320Z  INFO runtime::init::dataset: Dataset scifact_queries initializing...
2026-10-08T22:21:51.209323Z  INFO runtime::init::dataset: Dataset gsm8k initializing...
2026-10-08T22:21:51.209344Z  INFO runtime::init::dataset: Dataset scifact_qrels initializing...
2026-10-08T22:21:51.408818Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2026-10-08T22:21:51.409340Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2026-10-08T22:21:51.706359Z  INFO runtime::init::dataset: Dataset scifact_queries registered (hf://datasets/mteb/scifact/queries.jsonl), results cache enabled. duration_ms=0
2026-10-08T22:21:51.780396Z  INFO runtime::init::dataset: Dataset scifact_corpus registered (hf://datasets/mteb/scifact/corpus.jsonl), results cache enabled. duration_ms=0
2026-10-08T22:21:51.811864Z  INFO runtime::init::dataset: Dataset scifact_qrels registered (hf://datasets/mteb/scifact/qrels/test.tsv), results cache enabled. duration_ms=0
2026-10-08T22:21:51.998455Z  INFO runtime::init::dataset: Dataset gsm8k registered (hf://datasets/openai/gsm8k@740312add88f781978c0658806c59bc2815b9866/main/test-00000-of-00001.parquet), results cache enabled. duration_ms=0
2026-10-08T22:21:52.372654Z  INFO runtime::init::dataset: Dataset imdb registered (hf://datasets/stanfordnlp/imdb/plain_text/), results cache enabled. duration_ms=0
2026-10-08T22:21:52.474036Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

The elided lines report settings the runtime derives for this host, such as its CPU budget and cache sizes, so their values differ from machine to machine.

Registering a dataset lists its files and infers its schema. These datasets are federated: no local copy is made, and each query reads the files it needs from the Hub.

## Step 3. Query a public dataset

In a new terminal, start the Spice SQL REPL:

```bash
spice sql
```

List the datasets:

```sql
show tables;
```

```console
+---------------+--------------+-----------------+------------+
| table_catalog | table_schema |    table_name   | table_type |
|    varchar    |    varchar   |     varchar     |   varchar  |
+---------------+--------------+-----------------+------------+
| spice         | public       | gsm8k           | BASE TABLE |
| spice         | public       | scifact_corpus  | BASE TABLE |
| spice         | public       | scifact_qrels   | BASE TABLE |
| spice         | public       | imdb            | BASE TABLE |
| spice         | public       | scifact_queries | BASE TABLE |
| spice         | runtime      | task_history    | BASE TABLE |
+---------------+--------------+-----------------+------------+

Time: 0.000991583 seconds. 6 rows.
```

Count the IMDB reviews by label:

```sql
SELECT label, count(*) AS reviews FROM imdb GROUP BY label ORDER BY label;
```

```console
+-------+---------+
| label | reviews |
| int64 |  int64  |
+-------+---------+
| -1    | 50000   |
| 0     | 25000   |
| 1     | 25000   |
+-------+---------+

Time: 1.5393500420000001 seconds. 3 rows.
```

The `plain_text/` folder holds three splits: `train` and `test`, labeled `0` (negative) or `1` (positive), and `unsupervised`, labeled `-1`. The query reads the files from the Hub, so its time depends on your connection. Spice reads Parquet files in byte ranges, so this query downloads only the `label` column and the files' metadata: about 1.5 MiB of the folder's 80 MiB.

Now see which file, at which commit, each row comes from:

```sql
SELECT _location, count(*) AS reviews FROM imdb GROUP BY _location ORDER BY _location;
```

```console
+------------------------------------------------------------------------------------------------------------------------+---------+
|                                                        _location                                                       | reviews |
|                                                         varchar                                                        |  int64  |
+------------------------------------------------------------------------------------------------------------------------+---------+
| hf://datasets/stanfordnlp/imdb@e6281661ce1c48d982bc483cf8a173c1bbeb5d31/plain_text/test-00000-of-00001.parquet         | 25000   |
| hf://datasets/stanfordnlp/imdb@e6281661ce1c48d982bc483cf8a173c1bbeb5d31/plain_text/train-00000-of-00001.parquet        | 25000   |
| hf://datasets/stanfordnlp/imdb@e6281661ce1c48d982bc483cf8a173c1bbeb5d31/plain_text/unsupervised-00000-of-00001.parquet | 50000   |
+------------------------------------------------------------------------------------------------------------------------+---------+

Time: 0.002303666 seconds. 3 rows.
```

The `from` of `imdb` names no revision, so the dataset follows the `main` branch. Each query first resolves `main` to a commit, then lists and reads only that commit's files, so a query never mixes two versions of a dataset, even if the dataset changes while the query runs. For a public dataset read without a token, each `_location` is an `hf://` path that DuckDB and `HfFileSystem` can read as is.

## Step 4. Join JSONL and TSV files

SciFact is a retrieval benchmark: `scifact_queries` holds claims, `scifact_corpus` holds paper abstracts, and `scifact_qrels` links each claim in the test split to the abstracts that hold its evidence. Join the three files to see claims next to the titles of their evidence:

```sql
SELECT q.text AS claim, c.title AS evidence
FROM scifact_qrels r
JOIN scifact_queries q ON q._id = CAST(r."query-id" AS VARCHAR)
JOIN scifact_corpus c ON c._id = CAST(r."corpus-id" AS VARCHAR)
ORDER BY r."query-id", r."corpus-id"
LIMIT 5;
```

```console
+------------------------------------------------------------------------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------+
|                                                                         claim                                                                        |                                                             evidence                                                             |
|                                                                        varchar                                                                       |                                                              varchar                                                             |
+------------------------------------------------------------------------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------+
| 0-dimensional biomaterials show inductive properties.                                                                                                | New opportunities: the use of nanotechnologies to manipulate and track stem cells.                                               |
| 1,000 genomes project enables mapping of genetic sequence variation consisting of rare variants with larger penetrance effects than common variants. | Rare Variants Create Synthetic Genome-Wide Associations                                                                          |
| 1/2000 in UK have abnormal PrP positivity.                                                                                                           | Prevalent abnormal prion protein in human appendixes after bovine spongiform encephalopathy epizootic: large scale survey        |
| 5% of perinatal mortality is due to low birth weight.                                                                                                | Estimates of global prevalence of childhood underweight in 1990 and 2015.                                                        |
| A deficiency of vitamin B12 increases blood levels of homocysteine.                                                                                  | Folic acid improves endothelial function in coronary artery disease via mechanisms largely independent of homocysteine lowering. |
+------------------------------------------------------------------------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------+

Time: 0.49875125 seconds. 5 rows.
```

The JSONL files store ids as strings, and the ids in the TSV file are read as integers, so the join casts them. Run `describe scifact_qrels;` to see the types the connector inferred.

## Step 5. Pin a dataset to a commit

`gsm8k` names a commit after `@`, so its rows never change, even if the dataset's maintainers update `main`. Pin evaluation sets and benchmarks this way to keep results reproducible. Each GSM8K answer ends with `####` and the final number:

```sql
SELECT split_part(answer, '#### ', 2) AS final_answer, question FROM gsm8k LIMIT 3;
```

```console
+--------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| final_answer |                                                                                                                                         question                                                                                                                                         |
|    varchar   |                                                                                                                                          varchar                                                                                                                                         |
+--------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 18           | Janet’s ducks lay 16 eggs per day. She eats three for breakfast every morning and bakes muffins for her friends every day with four. She sells the remainder at the farmers' market daily for $2 per fresh duck egg. How much in dollars does she make every day at the farmers' market? |
| 3            | A robe takes 2 bolts of blue fiber and half that much white fiber.  How many bolts in total does it take?                                                                                                                                                                                |
| 70000        | Josh decides to try flipping a house.  He buys a house for $80,000 and then puts in $50,000 in repairs.  This increased the value of the house by 150%.  How much profit did he make?                                                                                                    |
+--------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

Time: 0.510906916 seconds. 3 rows.
```

The revision and the path together select exactly the files a dataset reads:

| `from`                                                                                  | Reads                                                                                                                                                                                      |
| --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `hf://datasets/stanfordnlp/imdb/plain_text/`                                            | The `main` branch, the default.                                                                                                                                                            |
| `hf://datasets/stanfordnlp/imdb@main/plain_text/`                                       | A named branch or tag, here `main`.                                                                                                                                                        |
| `hf://datasets/stanfordnlp/imdb@e6281661ce1c48d982bc483cf8a173c1bbeb5d31/plain_text/`   | One commit, such as a commit that `_location` showed in Step 3.                                                                                                                            |
| `hf://datasets/stanfordnlp/imdb/plain_text/train-*.parquet`                             | The files a glob selects, here only the `train` split.                                                                                                                                     |
| `hf://datasets/mteb/scifact@~parquet/corpus/corpus/`                                    | The Hub's automatic Parquet conversion of a dataset (the `refs/convert/parquet` branch), in one folder per configuration and split. Use it for datasets whose own files aren't tables, such as images in a zip archive. |

## Step 6. Accelerate a dataset with Cayenne

A federated query that needs the review text downloads all 80 MiB of the IMDB folder, so its time depends on your connection:

```sql
SELECT label, round(avg(character_length(text))) AS avg_chars FROM imdb GROUP BY label ORDER BY label;
```

```console
+-------+-----------+
| label | avg_chars |
| int64 |  float64  |
+-------+-----------+
| -1    | 1330.0    |
| 0     | 1294.0    |
| 1     | 1325.0    |
+-------+-----------+

Time: 7.895663417 seconds. 3 rows.
```

To load the dataset into Spice instead, add an `acceleration` block to the `imdb` dataset in `spicepod.yaml`:

```yaml
  - from: hf://datasets/stanfordnlp/imdb/plain_text/
    name: imdb
    description: IMDB movie reviews labeled by sentiment
    metadata:
      _location: enabled
    acceleration:
      enabled: true
      engine: cayenne
```

Save the file. `spice run` reloads the Spicepod and loads the dataset into [Cayenne](https://spiceai.org/docs/components/data-accelerators/cayenne). The load time depends on your connection:

```console
2026-10-08T22:24:35.374866Z  INFO runtime::init::dataset: Accelerated Dataset imdb updating...
...
2026-10-08T22:24:36.275313Z  INFO runtime_table::accelerated::refresh_task: Loading data for dataset imdb
2026-10-08T22:24:47.913343Z  INFO runtime_table::accelerated::refresh_task: Loaded 100,000 rows (138.68 MiB) for dataset imdb in 11s 638ms.
2026-10-08T22:24:48.369388Z  INFO runtime::init::dataset: Dataset imdb registered (hf://datasets/stanfordnlp/imdb/plain_text/), acceleration (cayenne), results cache enabled. duration_ms=0
```

On this first reload, `spice run` may also log `` WARN runtime::init::pods_watcher: `runtime.task_history` changed, but it is applied when spiced starts ... Restart spiced to apply it. `` The edit doesn't change `runtime.task_history`, so no restart is needed. See [spiceai/spiceai#14001](https://github.com/spiceai/spiceai/issues/14001).

Cayenne holds this copy in memory. To store it on disk instead, in `.spice/data/`, add `mode: file` under `acceleration`.

Run the same query again. It now reads the accelerated copy:

```sql
SELECT label, round(avg(character_length(text))) AS avg_chars FROM imdb GROUP BY label ORDER BY label;
```

```console
+-------+-----------+
| label | avg_chars |
| int64 |  float64  |
+-------+-----------+
| -1    | 1330.0    |
| 0     | 1294.0    |
| 1     | 1325.0    |
+-------+-----------+

Time: 0.003760083 seconds. 3 rows.
```

With the reviews accelerated, full-text exploration is interactive. For example, how do the reviews that mention a "masterpiece" split by label?

```sql
SELECT label, count(*) AS reviews FROM imdb WHERE text ILIKE '%masterpiece%' GROUP BY label ORDER BY label;
```

```console
+-------+---------+
| label | reviews |
| int64 |  int64  |
+-------+---------+
| -1    | 1263    |
| 0     | 379     |
| 1     | 942     |
+-------+---------+

Time: 0.005317708 seconds. 3 rows.
```

An accelerated dataset is read from the Hub once per refresh, not once per query, and each refresh reads the latest commit of the branch in `from`. To pick up changes to the dataset, run `spice refresh imdb` in another terminal; the runtime logs `Loaded 100,000 rows ...` when the refresh finishes. To refresh on a schedule, see [Data Refresh](https://spiceai.org/docs/features/data-acceleration/data-refresh).

## Private and gated datasets

Private datasets, and gated datasets whose access conditions you must accept first, need a Hugging Face [User Access Token](https://huggingface.co/settings/tokens) of an account that can read them. A token with the `Read` role is enough.

1. For a gated dataset, open the dataset's page on the Hub and accept its access conditions with your account.

2. Add the token to `.env.local` in this directory, which the cookbook's `.gitignore` keeps out of Git. Open the file in an editor rather than using `echo`, so the token stays out of your shell history, and add this line:

   ```text
   HF_TOKEN=<your-hugging-face-token>
   ```

3. Add the dataset to `spicepod.yaml`:

   ```yaml
     - from: hf://datasets/<owner>/<dataset>/
       name: my_dataset
       params:
         hf_token: ${secrets:HF_TOKEN}
   ```

   Setting `hf_token` is optional. When a dataset doesn't set it, the connector loads the token from the `hf_token` secret, which the default `env` secret store reads from `HF_TOKEN` in `.env.local` or in the environment. A token in `.env.local` therefore applies to every Hugging Face dataset in the Spicepod. Authenticated requests also get higher Hub rate limits.

4. Stop `spice run` with `Ctrl+C` and start it again, so that it loads the token from `.env.local`.

Without access, a dataset fails to load, and `spice datasets` reports why. For example, this is the gated [meta-llama/Llama-3.1-8B-evals](https://huggingface.co/datasets/meta-llama/Llama-3.1-8B-evals) dataset, read without a token:

```console
 NAME           FROM                                                                                      REPLICATION  ACCELERATION  STATUS  ERROR
 gated_metrics  hf://datasets/meta-llama/Llama-3.1-8B-evals@~parquet/Llama-3.1-8B-evals__metrics/latest/  false        false         Error   Insufficient permissions to access the dataset gated_metrics (hf). Hugging Face dataset 'meta-llama/Llama-3.1-8B-evals' is gated and no `hf_token` is set: accept its access conditions at https://huggingface.co/datasets/meta-llama/Llama-3.1-8B-evals with the account `hf_token` belongs to. See: https://github.com/spiceai/spiceai/blob/trunk/docs/features/huggingface-connector.md
```

When `hf_token` is set but can't read the dataset, the message reads `... is gated: accept its access conditions at ...` instead.

## Troubleshooting

When a dataset doesn't load, run `spice datasets` in another terminal: its `ERROR` column holds the reason, even when the runtime log doesn't show it.

| Error                                                                                  | Fix                                                                                                                                                         |
| -------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `'qrels' in dataset 'mteb/scifact' holds files of more than one format (.jsonl, .tsv)` | The folder in `from` holds more than one data format. Narrow `from` to a file or a glob, such as `hf://datasets/mteb/scifact/qrels/*.tsv`, or set `file_format` (for example `file_format: tsv`) under the dataset's `params`. |
| `Insufficient permissions ... is gated and no hf_token is set`                         | Set a token, as in [Private and gated datasets](#private-and-gated-datasets).                                                                              |
| `Insufficient permissions ... is gated: accept its access conditions`                  | Check that the token is valid, and accept the dataset's access conditions on the Hub with the account the token belongs to.                                  |

## Clean up

Stop `spice run` with `Ctrl+C`. The accelerated copy of IMDB is in memory, so stopping Spice removes it. If you added `mode: file`, delete the `.spice/` directory to remove the copy on disk. To restore the original `spicepod.yaml`, run `git checkout -- spicepod.yaml`.

## Learn more

- [Hugging Face Data Connector documentation](https://spiceai.org/docs/components/data-connectors/huggingface)
- [Cayenne Data Accelerator documentation](https://spiceai.org/docs/components/data-accelerators/cayenne)
- [Datasets reference](https://spiceai.org/docs/reference/spicepod/datasets), including the `_location`, `_last_modified`, and `_size` metadata columns
- [Hugging Face Hub datasets](https://huggingface.co/datasets)
