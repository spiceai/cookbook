# Local dataset replication (Localpod) recipe

The [Localpod](https://docs.spiceai.org/components/data-connectors/localpod) Data Connector allows you to link datasets in a parent/child relationship within the current Spicepod. This helps you set up multiple levels of data acceleration for a single dataset and ensures the data is downloaded only once from the remote source.

```yaml
version: v1beta1
kind: Spicepod
name: localpod

datasets:
    - from: file:data.csv
      name: time_series
      description: taxi trips in s3
      params:
        file_format: parquet
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

```

:::note

The parent dataset must have `refresh_mode` set to `full` in order for the `localpod` data connector to function. See [here](https://docs.spiceai.org/components/data-connectors/localpod#synchronized-refreshes) for more information

:::

## Running this recipe

In a new terminal, start `spice` with `spice run`.

You should see terminal output like so:

```shell
$ spice run
2024/10/29 18:31:38 INFO Checking for latest Spice runtime release...
2024/10/29 18:31:38 INFO Spice.ai runtime starting...
2024-10-30T01:31:38.912802Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2024-10-30T01:31:38.913151Z  INFO runtime::metrics_server: Spice Runtime Metrics listening on 127.0.0.1:9090
2024-10-30T01:31:38.913247Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2024-10-30T01:31:38.921580Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2024-10-30T01:31:39.112883Z  INFO runtime: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
2024-10-30T01:31:39.123137Z  INFO runtime: Tool [document_similarity] ready to use
2024-10-30T01:31:39.123166Z  INFO runtime: Tool [table_schema] ready to use
2024-10-30T01:31:39.123172Z  INFO runtime: Tool [sql] ready to use
2024-10-30T01:31:39.123180Z  INFO runtime: Tool [list_datasets] ready to use
2024-10-30T01:31:39.123183Z  INFO runtime: Tool [get_readiness] ready to use
2024-10-30T01:31:39.123187Z  INFO runtime: Tool [random_sample] ready to use
2024-10-30T01:31:39.123193Z  INFO runtime: Tool [sample_distinct_columns] ready to use
2024-10-30T01:31:39.123197Z  INFO runtime: Tool [top_n_sample] ready to use
2024-10-30T01:31:39.125295Z  INFO runtime: Dataset time_series registered (file:data.csv), acceleration (arrow, 15s refresh), results cache enabled.
2024-10-30T01:31:39.126352Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset time_series
2024-10-30T01:31:39.128337Z  INFO runtime::accelerated_table::refresh_task: Loaded 0 rows for dataset time_series in 1ms.
2024-10-30T01:31:39.136703Z  INFO runtime::datafusion: Localpod dataset local_time_series synchronizing refreshes with parent table time_series
2024-10-30T01:31:39.136764Z  INFO runtime: Dataset local_time_series registered (localpod:time_series), acceleration (duckdb:file, 10s refresh), results cache enabled.
2024-10-30T01:31:39.137955Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset local_time_series
2024-10-30T01:31:39.139139Z  INFO runtime::accelerated_table::refresh_task: Loaded 0 rows for dataset local_time_series in 1ms.
```

### Querying the `localpod`

In a new terminal, start `spice sql` and run these two queries to validate that both datasets contain the same number of rows:

```shell
$ spice sql

sql> SELECT COUNT(*) FROM time_series;
+----------+
| count(*) |
+----------+
| 0        |
+----------+

Time: 0.004800375 seconds. 1 rows.
sql> SELECT COUNT(*) FROM local_time_series;
+----------+
| count(*) |
+----------+
| 0        |
+----------+


Time: 0.005054417 seconds. 1 rows.
```

### Updating the parent dataset

Let's insert new data into the parent dataset and see the `localpod` update. In a new terminal, navigate to this sample directory and run the following:

```shell
./generate_data.sh
```

In the terminal where `spice run` is running, you should see a message indicating the new data is loaded:

```shell
2024-10-30T01:37:24.266411Z  INFO runtime::accelerated_table::refresh_task: Loaded 1,000 rows (48.16 kiB) for dataset time_series in 3ms.
2024-10-30T01:37:24.266422Z  INFO runtime::accelerated_table::refresh_task: Loaded 1,000 rows (48.16 kiB) for dataset local_time_series in 3ms.
```

And the same SQL queries as above will give updated results:

```shell
sql> SELECT COUNT(*) FROM time_series;
+----------+
| count(*) |
+----------+
| 1000     |
+----------+

Time: 0.006115708 seconds. 1 rows.
sql> SELECT COUNT(*) FROM local_time_series;
+----------+
| count(*) |
+----------+
| 1000     |
+----------+

Time: 0.005385625 seconds. 1 rows.
```

The `local_time_series` dataset is faster because it's accelerated locally using [DuckDB](https://docs.spiceai.org/components/data-accelerators/duckdb)
