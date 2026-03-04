# Local dataset replication (Localpod)

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

Wait until the runtime reports it is ready before opening `spice sql`.

### Querying the `localpod`

In a new terminal, start `spice sql` and run these two queries to validate that both datasets contain the same number of rows:

```shell
$ spice sql

sql> SELECT COUNT(*) FROM time_series;

sql> SELECT COUNT(*) FROM local_time_series;
```

Both queries should return the same count value.


### Updating the parent dataset

Let's insert new data into the parent dataset. In a new terminal, navigate to this sample directory and run the following:

```shell
./generate_data.sh
```

In the terminal where `spice run` is running, wait for refresh logs indicating new data was loaded.

The parent dataset count should now be updated:

```shell
sql> SELECT COUNT(*) FROM time_series;
```
