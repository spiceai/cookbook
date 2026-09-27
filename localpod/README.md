# Local dataset replication (Localpod)

Works with `v1.0+`

The [Localpod](https://docs.spiceai.org/components/data-connectors/localpod) Data Connector allows you to link datasets in a parent/child relationship within the current Spicepod. This helps you set up multiple levels of data acceleration for a single dataset and ensures the data is downloaded only once from the remote source.

```yaml
version: v1
kind: Spicepod
name: localpod

datasets:
  - from: file:data.csv
    name: time_series
    description: taxi trips in s3
    params:
      file_format: csv
    acceleration:
      enabled: true
      refresh_check_interval: 15s
      refresh_mode: full
  - from: localpod:time_series
    name: local_time_series
    acceleration:
      enabled: true
      engine: duckdb
      mode: file
      refresh_check_interval: 10s
```

:::note

The parent dataset must have `refresh_mode` set to `full` in order for the `localpod` data connector to function. See [here](https://docs.spiceai.org/components/data-connectors/localpod#synchronized-refreshes) for more information

The CSV fixture contains one typed seed row so the file connector resolves concrete column types when the runtime starts. A header-only CSV resolves its columns as `Null`, and subsequent full refreshes preserve that initial schema.

:::

## Running this recipe

In a new terminal, start `spice` with `spice run`.

You should see terminal output like so:

```shell
$ spice run
 INFO Spice.ai runtime starting...
2026-09-24T15:46:28.639648Z  INFO spiced: Starting runtime v2.3.2+models.metal
2026-09-24T15:46:28.642754Z  INFO runtime::init::caching: Initialized sql results cache; max size: 128.00 MiB, item ttl: 1s, hashing algorithm: XXH3, encoding: none
2026-09-24T15:46:28.642780Z  INFO runtime::init::caching: Initialized search results cache; max size: 128.00 MiB, item ttl: 1s, engine: Moka
2026-09-24T15:46:28.642793Z  INFO runtime::init::caching: Initialized embeddings cache; max size: 128.00 MiB, item ttl: 1s, engine: Moka
2026-09-24T15:46:28.644686Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2026-09-24T15:46:28.645041Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2026-09-24T15:46:28.652730Z  INFO runtime::init::dataset: Loading datasets: 1 tasks dispatched, 0 skipped at accelerator init (of 2 total; localpod datasets may be chained).
2026-09-24T15:46:28.652776Z  INFO runtime::init::dataset: Dataset local_time_series initializing...
2026-09-24T15:46:28.655274Z  INFO runtime::init::dataset: Dataset time_series registered (file:data.csv), acceleration (arrow, 15s refresh), results cache enabled. duration_ms=0
2026-09-24T15:46:28.656620Z  INFO runtime_table::accelerated::refresh_task: Loading data for dataset time_series
2026-09-24T15:46:28.657844Z  INFO runtime_table::accelerated::refresh_task: Loaded 1 rows (384.00 B) for dataset time_series in 1ms.
2026-09-24T15:46:28.664894Z  INFO runtime::datafusion: Localpod dataset local_time_series synchronizing refreshes with parent table time_series
2026-09-24T15:46:28.665318Z  INFO runtime::init::dataset: Dataset local_time_series registered (localpod:time_series), acceleration (duckdb:file, 10s refresh), results cache enabled. duration_ms=8
2026-09-24T15:46:28.666606Z  INFO runtime_table::accelerated::refresh_task: Loading data for dataset local_time_series
2026-09-24T15:46:28.671346Z  INFO runtime_table::accelerated::refresh_task: Loaded 1 rows (384.00 B) for dataset local_time_series in 4ms.
2026-09-24T15:46:28.767918Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

### Querying the `localpod`

In a new terminal, start `spice sql` and run these two queries to validate that both datasets contain the same number of rows:

```shell
$ spice sql

sql> SELECT COUNT(*) FROM time_series;
+----------+
| count(*) |
|   int64  |
+----------+
| 1        |
+----------+

Time: 0.001709125 seconds. 1 rows.
sql> SELECT COUNT(*) FROM local_time_series;
+----------+
| count(*) |
|   int64  |
+----------+
| 1        |
+----------+

Time: 0.001861500 seconds. 1 rows.
```

### Updating the parent dataset

Replace the seed data with 1,000 generated rows and observe the `localpod` update. In a new terminal, navigate to this sample directory and run the following:

```shell
./generate_data.sh
```

In the terminal where `spice run` is running, you should see a message indicating the new data is loaded:

```shell
2026-09-24T15:46:58.687136Z  INFO runtime_table::accelerated::refresh_task: Loaded 1,000 rows (24.28 kiB) for dataset time_series in 13ms.
2026-09-24T15:46:58.687180Z  INFO runtime_table::accelerated::refresh_task: Loaded 1,000 rows (24.28 kiB) for dataset local_time_series in 13ms.
```

And the same SQL queries as above will give updated results:

```shell
sql> SELECT COUNT(*) FROM time_series;
+----------+
| count(*) |
|   int64  |
+----------+
| 1000     |
+----------+

Time: 0.001220625 seconds. 1 rows.
sql> SELECT COUNT(*) FROM local_time_series;
+----------+
| count(*) |
|   int64  |
+----------+
| 1000     |
+----------+

Time: 0.002321541 seconds. 1 rows.
```

Validate that both datasets contain the generated values, not only the same number of rows:

```console
sql> SELECT 'time_series' dataset, COUNT(*) rows, COUNT(timestamp) timestamp_values,
  COUNT(val1) val1_values, SUM(val1) val1_sum, SUM(val2) val2_sum
  FROM time_series
  UNION ALL
  SELECT 'local_time_series' dataset, COUNT(*) rows, COUNT(timestamp) timestamp_values,
  COUNT(val1) val1_values, SUM(val1) val1_sum, SUM(val2) val2_sum
  FROM local_time_series;
+-------------------+-------+------------------+-------------+----------+----------+
|      dataset      |  rows | timestamp_values | val1_values | val1_sum | val2_sum |
|      varchar      | int64 |       int64      |    int64    |   int64  |   int64  |
+-------------------+-------+------------------+-------------+----------+----------+
| time_series       | 1000  | 1000             | 1000        | 49500    | 49500    |
| local_time_series | 1000  | 1000             | 1000        | 49500    | 49500    |
+-------------------+-------+------------------+-------------+----------+----------+
```

The `local_time_series` dataset is accelerated locally using [DuckDB](https://docs.spiceai.org/components/data-accelerators/duckdb) in file mode.
