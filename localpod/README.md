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
2026-08-02T12:24:38.441060Z  INFO spiced: Starting runtime v2.1.2+models
2026-08-02T12:24:38.442600Z  INFO runtime::init::caching: Initialized sql results cache; max size: 128.00 MiB, item ttl: 1s, hashing algorithm: XXH3, encoding: none
2026-08-02T12:24:38.442643Z  INFO runtime::init::caching: Initialized search results cache; max size: 128.00 MiB, item ttl: 1s, engine: Moka
2026-08-02T12:24:38.442658Z  INFO runtime::init::caching: Initialized embeddings cache; max size: 128.00 MiB, item ttl: 1s, engine: Moka
2026-08-02T12:24:38.444400Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2026-08-02T12:24:38.444761Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2026-08-02T12:24:38.452860Z  INFO runtime::init::dataset: Loading datasets: 1 tasks dispatched, 0 skipped at accelerator init (of 2 total; localpod datasets may be chained).
2026-08-02T12:24:38.452891Z  INFO runtime::init::dataset: Dataset local_time_series initializing...
2026-08-02T12:24:38.453637Z  INFO runtime::init::dataset: Dataset time_series registered (file:data.csv), acceleration (arrow, 15s refresh), results cache enabled. duration_ms=0
2026-08-02T12:24:38.454943Z  INFO runtime_table::accelerated::refresh_task: Loading data for dataset time_series
2026-08-02T12:24:38.455886Z  INFO runtime_table::accelerated::refresh_task: Loaded 1 rows for dataset time_series in 0s.
2026-08-02T12:24:38.458522Z  INFO runtime::init::dataset: Dataset local_time_series registered (localpod:time_series), acceleration (duckdb:file, 10s refresh), results cache enabled. duration_ms=3
2026-08-02T12:24:38.459791Z  INFO runtime_table::accelerated::refresh_task: Loading data for dataset local_time_series
2026-08-02T12:24:38.463429Z  INFO runtime_table::accelerated::refresh_task: Loaded 1 rows for dataset local_time_series in 3ms.
2026-08-02T12:24:38.561540Z  INFO runtime: All components are loaded. Spice runtime is ready!
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
2026-08-02T12:25:23.471503Z  INFO runtime_table::accelerated::refresh_task: Loaded 1,000 rows (24.00 B) for dataset time_series in 4ms.
2026-08-02T12:25:28.564207Z  INFO runtime_table::accelerated::refresh_task: Loaded 1,000 rows (24.00 B) for dataset local_time_series in 15ms.
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
