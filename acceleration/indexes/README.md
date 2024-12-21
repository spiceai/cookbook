# Indexes on Accelerated Data

Indexes can be created on accelerated datasets (for supported engines) to improve query performance. This recipe will demonstrate how to create an index and compare the performance on the same accelerated dataset without an index.

Clone the Spice cookbook repository and navigate to the `indexes` directory:

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/acceleration/indexes
```

**Step 1.** Download the large test dataset locally

Indexes only make a difference on large datasets. This dataset is 1.5GB bytes, decompressed into 7+GB in-memory.

```bash
wget https://public-data.spiceai.org/large_eth_traces.parquet
```

**Step 2.** Start Spice

Spice will start and load the dataset into sqlite. **This may take several minutes.**

```bash
spice run
```

```console
2024-09-30T18:04:26.070605Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2024-09-30T18:04:26.070827Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2024-09-30T18:04:26.070596Z  INFO runtime::metrics_server: Spice Runtime Metrics listening on 127.0.0.1:9090
2024-09-30T18:04:26.078670Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2024-09-30T18:04:26.270747Z  INFO runtime: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
2024-09-30T18:04:26.286500Z  INFO runtime: Dataset traces registered (file:large_eth_traces.parquet), acceleration (duckdb:file), results cache enabled.
2024-09-30T18:04:26.287326Z  INFO runtime: Dataset traces_no_index registered (file:large_eth_traces.parquet), acceleration (duckdb:file), results cache enabled.
2024-09-30T18:04:26.287668Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset traces
2024-09-30T18:04:26.288332Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset traces_no_index
2024-09-30T18:05:00.532792Z  INFO runtime::accelerated_table::refresh_task: Loaded 7,595,994 rows (7.04 GiB) for dataset traces in 34s 245ms.
2024-09-30T18:05:00.683737Z  INFO runtime::accelerated_table::refresh_task: Loaded 7,595,994 rows (7.04 GiB) for dataset traces_no_index in 34s 395ms.
```

**Step 3.** Run a query on the dataset without an index

Once the datasets have loaded, run the following query in the SQL REPL via `spice sql` to get a single row:

```sql
SELECT * FROM traces_no_index WHERE trace_id = 'call_0x22ba49176f15ec5524434d87c47fc9dbff6ef8f584889ab4f0fa830d76a678d4_7_3_2_0_0_0_0_0';
```

> Time: 0.118341417 seconds. 1 rows.

**Step 4.** Run a query on the dataset with an index

Repeat the query, but this time against the dataset with the index configured:

```sql
SELECT * FROM traces WHERE trace_id = 'call_0x22ba49176f15ec5524434d87c47fc9dbff6ef8f584889ab4f0fa830d76a678d4_7_3_2_0_0_0_0_0';
```

> Time: 0.003471583 seconds. 1 rows.

Much faster! Try exploring with indexes in different acceleration engines to get a sense of how they behave.
