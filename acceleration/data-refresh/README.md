# Advanced Data Refresh

Works with `v1.0+`

Data refresh for accelerated datasets can be configured and tuned for specific scenarios.

Follow this recipe to dynamically refresh specific data at runtime by programmatically updating `refresh_sql` and triggering data refreshes.

_Tip: Open and refer to the [Data Refresh](https://spiceai.org/docs/features/data-acceleration/data-refresh) documentation while completing this recipe._

## Step 1. Initialize the Spice app

First ensure the Spice CLI is installed. If not, follow the Spice [Getting Started](https://docs.spiceai.org/getting-started) guide to install.

```bash
mkdir spice-data-refresh
cd spice-data-refresh

# Add the spiceai/quickstart Spicepod
spice add spiceai/quickstart

# Start the Spice runtime
spice run
```

The Spice runtime will start and the `taxi_trips` dataset included in the `spiceai/quickstart` Spicepod will be loaded.

```bash
Spice.ai runtime starting...
2026-08-05T12:06:14.195427Z  INFO runtime::init::caching: Initialized sql results cache; max size: 128.00 MiB, item ttl: 1s, hashing algorithm: XXH3, encoding: none
2026-08-05T12:06:14.412746Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2026-08-05T12:06:14.415936Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2026-08-05T12:06:19.784484Z  INFO runtime::init::dataset: Dataset taxi_trips registered (s3://spiceai-demo-datasets/taxi_trips/2024/), acceleration (arrow), results cache enabled.
2026-08-05T12:06:19.785986Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset taxi_trips
2026-08-05T12:06:23.126886Z  INFO runtime::accelerated_table::refresh_task: Loaded 2,964,624 rows (399.38 MiB) for dataset taxi_trips in 3s 340ms.
```

**In a new terminal window**, run `spice sql` to start the Spice SQL REPL.

In the REPL, enter:

```sql
select avg(passenger_count) from taxi_trips;
```

Note the output is:

```bash
+---------------------------------+
| avg(taxi_trips.passenger_count) |
|             float64             |
+---------------------------------+
| 1.3392808966805005              |
+---------------------------------+
```

## Step 2. Filter the refresh data

In a code or text editor, open `spicepods/spiceai/quickstart/spicepod.yaml`.

In the `acceleration` section:

1. Add `refresh_mode: full`.
2. Add a `refresh_sql` below it to filter the dataset to a passenger_count of two.

The `spiceai/quickstart` Spicepod does not set `refresh_check_interval`, so the dataset only refreshes when the configuration changes or a refresh is triggered — there are no automated refreshes to disable.

The `spicepod.yaml` should be as below:

```yaml
version: v1
kind: Spicepod
name: quickstart
datasets:
  - from: s3://spiceai-demo-datasets/taxi_trips/2024/
    name: taxi_trips
    description: taxi trips in s3
    params:
      file_format: parquet
    acceleration:
      enabled: true
      refresh_mode: full
      refresh_sql: select * from taxi_trips where passenger_count = 2
```

Save the file and note that the dataset has been updated:

```console
2026-08-05T12:07:15.397249Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset taxi_trips
2026-08-05T12:07:17.674699Z  INFO runtime::accelerated_table::refresh_task: Loaded 405,103 rows (55.13 MiB) for dataset taxi_trips in 2s 277ms.
2026-08-05T12:07:18.827981Z  INFO runtime::init::dataset: Dataset taxi_trips registered (s3://spiceai-demo-datasets/taxi_trips/2024/), acceleration (arrow), results cache enabled.
```

Swap to the Spice SQL REPL and enter:

```sql
select avg(passenger_count) from taxi_trips;
```

Note, the output is now:

```bash
+---------------------------------+
| avg(taxi_trips.passenger_count) |
|             float64             |
+---------------------------------+
| 2.0                             |
+---------------------------------+
```

The dataset was refreshed with data filtered to trips with a passenger count of 2.

## Step 3. Programmatically update the refresh SQL

In addition to editing the `spicepod.yaml` directly, the Refresh SQL can be updated by API.

Run the following cURL command to update it:

```bash
curl -i -X PATCH \
     -H "Content-Type: application/json" \
     -d '{
           "refresh_sql": "SELECT * FROM taxi_trips WHERE passenger_count = 3"
         }' \
     localhost:8090/v1/datasets/taxi_trips/acceleration
```

```bash
2026-08-05T12:07:57.314898Z  INFO runtime::accelerated_table: [refresh] Updated refresh SQL for taxi_trips to SELECT * FROM taxi_trips WHERE passenger_count = 3
```

The updated `refresh_sql` will be applied on the _next_ refresh. With no `refresh_check_interval` configured, that refresh has to be triggered.

Make an additional call to trigger a refresh now:

```bash
curl -i -H "Content-Type: application/json" -X POST localhost:8090/v1/datasets/taxi_trips/acceleration/refresh --data "{}"
```

```bash
2026-08-05T12:07:57.325903Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset taxi_trips
2026-08-05T12:07:59.150212Z  INFO runtime::accelerated_table::refresh_task: Loaded 91,262 rows (13.19 MiB) for dataset taxi_trips in 1s 824ms.
```

Swap to the Spice SQL REPL and enter:

```sql
select avg(passenger_count) from taxi_trips;
```

Note, the output is now:

```bash
+---------------------------------+
| avg(taxi_trips.passenger_count) |
|             float64             |
+---------------------------------+
| 3.0                             |
+---------------------------------+
```

## Summary

This recipe demonstrated how to dynamically refresh specific data at runtime by updating the `refresh_sql` in `spicepod.yaml` and programmatically via API calls. This provides control over what data is queried and fetched from remote data sources and when it happens.
