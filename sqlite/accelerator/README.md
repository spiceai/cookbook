# SQLite Data Accelerator

Works with `v1.0+`

> **Deprecated:** The SQLite acceleration engine is deprecated in Spice `v2.4` and will be removed in `v2.5`. New Spicepods should use the default [Cayenne](https://spiceai.org/docs/components/data-accelerators/cayenne) engine, and existing SQLite accelerations must move to Cayenne before upgrading to `v2.5`. See the [migration guide](https://spiceai.org/docs/components/data-accelerators/cayenne/migration) and [Step 4](#step-4-move-to-cayenne).

Follow this recipe to configure dataset acceleration using SQLite.

_Tip: Open and refer to the [SQLite Data Accelerator](https://spiceai.org/docs/components/data-accelerators/sqlite) documentation while completing this recipe._

_Tip: Follow the [Advanced Data Refresh Recipe](../../acceleration/data-refresh/README.md) to learn more about advanced data refresh scenarios, such as programmatically updating `refresh_sql` and triggering data refreshes._

## Step 1. Initialize the Spice app

Ensure the Spice CLI is installed. If not, follow the Spice [Getting Started](https://spiceai.org/docs/getting-started) guide to install.

Clone the Spice samples repository and navigate to the `sqlite` directory:

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/sqlite/accelerator
```

Start the Spice runtime

```bash
spice run
```

Output:

```bash
2024-09-10T06:54:36.185086Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2024-09-10T06:54:36.187305Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2024-09-10T06:54:36.385124Z  INFO runtime::init::caching: Initialized sql results cache; max size: 128.00 MiB, item ttl: 1s, hashing algorithm: XXH3, encoding: none
2024-09-10T06:54:37.020990Z  INFO runtime::init::dataset: Dataset taxi_trips registered (s3://spiceai-demo-datasets/taxi_trips/2024/), results cache enabled.
```

## Step 2. Run query against the dataset using the Spice SQL REPL

In a new terminal, start the Spice SQL REPL.

```bash
spice sql
```

Enter a query to display the longest taxi trips:

```sql
SELECT trip_distance, total_amount FROM taxi_trips ORDER BY trip_distance DESC LIMIT 10;
```

Output:

```bash
+---------------+--------------+
| trip_distance | total_amount |
|    float64    |    float64   |
+---------------+--------------+
| 312722.3      | 22.15        |
| 97793.92      | 36.31        |
| 82015.45      | 21.56        |
| 72975.97      | 20.04        |
| 71752.26      | 49.57        |
| 59282.45      | 33.52        |
| 59076.43      | 23.17        |
| 58298.51      | 18.63        |
| 51619.36      | 24.2         |
| 44018.64      | 52.43        |
+---------------+--------------+

Time: 2.1508365 seconds. 10 rows.
```

## Step3. Enable SQLite Accelerator

Use a text editor to open `spicepod.yaml` and add the `acceleration` block shown below. Save.

Before:

```yaml
version: v1
kind: Spicepod
name: sqlite
datasets:
  - from: s3://spiceai-demo-datasets/taxi_trips/2024/
    name: taxi_trips
    description: taxi trips in s3
    params:
      file_format: parquet
```

After:

```yaml
version: v1
kind: Spicepod
name: sqlite
datasets:
  - from: s3://spiceai-demo-datasets/taxi_trips/2024/
    name: taxi_trips
    description: taxi trips in s3
    params:
      file_format: parquet
    acceleration:
      enabled: true
      engine: sqlite
      mode: file
```

The following output is shown in the Spice runtime terminal confirming new configuration is applied.

```bash
2024-09-10T06:59:21.908667Z  INFO runtime: Unloaded dataset taxi_trips
2024-09-10T06:59:22.524295Z  INFO runtime::init::dataset: Dataset taxi_trips registered (s3://spiceai-demo-datasets/taxi_trips/2024/), acceleration (sqlite:file), results cache enabled.
2024-09-10T06:59:22.525789Z  INFO runtime_table::accelerated::refresh_task: Loading data for dataset taxi_trips
2024-09-10T06:59:39.244473Z  INFO runtime_table::accelerated::refresh_task: Loaded 2,964,624 rows (399.38 MiB) for dataset taxi_trips in 16s 718ms.
```

From `v2.4`, Spice also logs a deprecation warning for the `sqlite` engine:

```bash
2026-10-26T19:34:18.314894Z  WARN runtime::init::pods_watcher: Acceleration engines other than `cayenne` are deprecated and will be removed in v2.5, so these accelerations must move to `cayenne` before upgrading: `sqlite` (dataset 'taxi_trips'). Set `acceleration.engine: cayenne`, or remove `engine` to use the default, which is `cayenne`, then delete the old engine's acceleration files and snapshots. See: https://spiceai.org/docs/components/data-accelerators/cayenne/migration
```

Run query to display the longest taxi trips again:

```sql
SELECT trip_distance, total_amount FROM taxi_trips ORDER BY trip_distance DESC LIMIT 10;
```

Output:

```bash
+---------------+--------------+
| trip_distance | total_amount |
|    float64    |    float64   |
+---------------+--------------+
| 312722.3      | 22.15        |
| 97793.92      | 36.31        |
| 82015.45      | 21.56        |
| 72975.97      | 20.04        |
| 71752.26      | 49.57        |
| 59282.45      | 33.52        |
| 59076.43      | 23.17        |
| 58298.51      | 18.63        |
| 51619.36      | 24.2         |
| 44018.64      | 52.43        |
+---------------+--------------+

Time: 0.193560667 seconds. 10 rows.
```

Observe query execution time decreased from **2.1508365** to **0.193560667** seconds.

## Step 4. Move to Cayenne

Because the SQLite engine is deprecated, switch the dataset to Cayenne. In `spicepod.yaml`, change `engine: sqlite` to `engine: cayenne` (or remove the `engine` line to use the default, which is Cayenne) and save:

```yaml
    acceleration:
      enabled: true
      engine: cayenne
      mode: file
```

Spice reloads the dataset with Cayenne, and the deprecation warning is no longer logged:

```bash
2026-10-26T19:35:14.441222Z  INFO runtime::init::dataset: Dataset taxi_trips registered (s3://spiceai-demo-datasets/taxi_trips/2024/), acceleration (cayenne:file), results cache enabled. duration_ms=316
2026-10-26T19:35:21.224508Z  INFO runtime_table::accelerated::refresh_task: Loaded 2,964,624 rows (398.60 MiB) for dataset taxi_trips in 6s 781ms.
```

Run the query again; it returns the same 10 rows. The SQLite database file (`.spice/data/accelerated_sqlite.db` and its `-wal`/`-shm` files) is no longer used and can be deleted.
