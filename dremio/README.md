# Dremio Data Connector Recipe

Works with `v1.0+`

This recipe runs a self-hosted [Dremio Community Edition](https://hub.docker.com/r/dremio/dremio-oss) instance in Docker, exposes the cookbook's sample NYC taxi trips dataset through it, and queries it with Spice. It is fully self-contained — no external Dremio instance, account, or credentials are required. The same steps work against any Dremio instance by changing the `dremio_endpoint` parameter.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) is installed and running, with at least 4 GB of memory available to it.
- Spice is installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation).

**Step 1.** Clone the [github.com/spiceai/cookbook](https://github.com/spiceai/cookbook) repo and navigate to the `dremio` directory.

```bash
git clone https://github.com/spiceai/cookbook
cd cookbook/dremio
```

**Step 2.** Start Dremio and load the sample dataset.

```bash
make
```

The first run pulls the `dremio/dremio-oss` image (~1.1 GB), so it takes a few minutes; subsequent runs start in seconds.

This runs `docker compose up` followed by `./setup-dremio.sh`, which:

1. Creates the first (admin) Dremio user, `demo` / `demo1234`.
2. Adds the cookbook `data` directory (mounted into the container at `/opt/dremio/datasets`) as a Dremio NAS source named `datasets`.
3. Promotes `data/taxi_trips` to the physical dataset `datasets.taxi_trips` — 100,000 NYC yellow taxi trips from January 2024.

```bash
Starting Dremio container...
 Container dremio-dremio-1  Started
Waiting for Dremio at http://localhost:9047 (first start takes 1-2 minutes)...
Creating the first user 'demo'...
Adding the 'datasets' NAS source...
Promoting datasets.taxi_trips to a physical dataset...

Dremio is ready:
  UI:           http://localhost:9047 (demo / demo1234)
  Arrow Flight: grpc://localhost:32010
  Dataset:      datasets.taxi_trips
```

Dremio's web UI is now available at [http://localhost:9047](http://localhost:9047), and the Arrow Flight endpoint that Spice connects to is `grpc://localhost:32010`.

**Step 3.** Set the login credentials that the Spice runtime will use when accessing Dremio. Ensure this command is run in the `dremio` directory.

```bash
spice login dremio -u demo -p demo1234
```

This writes `SPICE_DREMIO_USERNAME` and `SPICE_DREMIO_PASSWORD` to a local `.env` file, which the runtime reads on startup.

**Step 4.** Review `spicepod.yaml`, which configures the Dremio dataset:

```yaml
version: v1
kind: Spicepod
name: dremio-demo

datasets:
  - from: dremio:datasets.taxi_trips
    name: taxi_trips
    description: taxi trips data in the local Dremio instance
    params:
      dremio_endpoint: grpc://localhost:32010
    acceleration:
      enabled: true
```

To connect to a different Dremio instance instead, point `dremio_endpoint` at its Arrow Flight endpoint and change `from:` to the path of a dataset in that instance.

**Step 5.** Start the runtime.

```bash
spice run
```

```bash
2026-08-21T16:37:22.944424Z  INFO runtime::init::dataset: Dataset taxi_trips initializing...
2026-08-21T16:37:23.143965Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2026-08-21T16:37:23.144245Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2026-08-21T16:37:23.289412Z  INFO runtime::init::dataset: Dataset taxi_trips registered (dremio:datasets.taxi_trips), acceleration (arrow), results cache enabled. duration_ms=0
2026-08-21T16:37:23.290602Z  INFO runtime_table::accelerated::refresh_task: Loading data for dataset taxi_trips
2026-08-21T16:37:23.803270Z  INFO runtime_table::accelerated::refresh_task: Loaded 100,000 rows (27.91 MiB) for dataset taxi_trips in 512ms.
2026-08-21T16:37:23.898677Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

**Step 6.** Run queries against the dataset using the Spice SQL REPL.

In a new terminal, start the Spice SQL REPL.

```bash
spice sql
```

Now query `taxi_trips`:

```sql
select avg(total_amount), avg(tip_amount), count(1), passenger_count from taxi_trips group by passenger_count order by passenger_count asc;
```

```bash
+------------------------------+----------------------------+-----------------+-----------------+
| avg(taxi_trips.total_amount) | avg(taxi_trips.tip_amount) | count(Int64(1)) | passenger_count |
|            float64           |           float64          |      int64      |      int64      |
+------------------------------+----------------------------+-----------------+-----------------+
| 26.854220471636765           | 3.4209324208725356         | 78323           | 1               |
| 30.00704346023626            | 3.7304525668486166         | 14473           | 2               |
| 29.522078564800488           | 3.5187256418187443         | 3233            | 3               |
| 31.041041110517895           | 3.581195942338495          | 1873            | 4               |
| 26.925718750000005           | 3.52340625                 | 1280            | 5               |
| 25.43750611246944            | 3.3346943765281174         | 818             | 6               |
+------------------------------+----------------------------+-----------------+-----------------+

Time: 0.003632416 seconds. 6 rows.
```

> **Note:** the group counts are stable, but the `avg(...)` values are float64 sums whose result depends on
> how many partitions the query ran with, so the last few digits will differ from the output above on a
> machine with a different core count. Compare the counts and the leading digits, not the full mantissa.

The trailing digits of the averages can vary between runs — floating-point aggregation depends on the order partitions are combined in.

**Step 7.** Stop Dremio and remove its container and volume.

```bash
make clean
```

**Next Steps**

This recipe accelerates query performance using [Spice Data Accelerators](https://docs.spiceai.org/components/data-accelerators). Experiment with different acceleration options by editing `spicepod.yaml` — for example, add `refresh_check_interval: 10s` to refresh the local copy on a schedule, or remove the `acceleration` block altogether to have the Spice runtime federate every query to Dremio directly.

To add more data, drop Parquet or CSV files into the cookbook `data` directory and promote them in the Dremio UI, or extend `setup-dremio.sh` to promote them automatically.
