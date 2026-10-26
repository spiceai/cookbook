# Indexes on Accelerated Data

Works with `v2.3.2+`

Indexes can be created on accelerated datasets (for supported engines) to improve query performance. This recipe will demonstrate how to create an index and compare the performance on the same accelerated dataset without an index.

Clone the Spice cookbook repository and navigate to the `indexes` directory:

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/acceleration/indexes
```

**Step 1.** Download the large test dataset locally

Indexes only make a difference on large datasets. This dataset is 1.5GB bytes, decompressed into 5+GB in-memory.

```bash
curl -O https://public-data.spiceai.org/large_eth_traces.parquet
```

**Step 2.** Start Spice

Spice will start and load the dataset into Cayenne. **This may take several minutes.**

```bash
spice run
```

```console
2026-10-26T20:18:27.232560Z  INFO runtime::init::caching: Initialized sql results cache; max size: 128.00 MiB, item ttl: 1s, hashing algorithm: XXH3, encoding: none
2026-10-26T20:18:27.433771Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2026-10-26T20:18:27.434150Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2026-10-26T20:18:27.670034Z  INFO cayenne::provider::lookup_index: Dataset 'traces' (cayenne): maintaining secondary indexes on trace_id table=traces
2026-10-26T20:18:27.672906Z  INFO runtime::init::dataset: Dataset traces registered (file:large_eth_traces.parquet), acceleration (cayenne:file), results cache enabled. duration_ms=422
2026-10-26T20:18:27.674032Z  INFO runtime_table::accelerated::refresh_task: Loading data for dataset traces
2026-10-26T20:18:27.698118Z  INFO runtime::init::dataset: Dataset traces_no_index registered (file:large_eth_traces.parquet), acceleration (cayenne:file), results cache enabled. duration_ms=447
2026-10-26T20:18:27.699381Z  INFO runtime_table::accelerated::refresh_task: Loading data for dataset traces_no_index
2026-10-26T20:18:34.457660Z  INFO runtime_table::accelerated::refresh_task: Loaded 7,595,994 rows (5.58 GiB) for dataset traces_no_index in 6s 758ms.
2026-10-26T20:18:34.552711Z  INFO cayenne::provider::lookup_index: Dataset 'traces' (cayenne): indexed 7595994 rows in 12 files for its secondary index table=traces
2026-10-26T20:18:34.598767Z  INFO runtime_table::accelerated::refresh_task: Loaded 7,595,994 rows (5.58 GiB) for dataset traces in 6s 924ms.
2026-10-26T20:18:34.698990Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

**Step 3.** Run a query on the dataset without an index

Once the datasets have loaded, run the following query in the SQL REPL via `spice sql` to get a single row:

```sql
SELECT * FROM traces_no_index WHERE trace_id = 'call_0x22ba49176f15ec5524434d87c47fc9dbff6ef8f584889ab4f0fa830d76a678d4_7_3_2_0_0_0_0_0';
```

> Time: 0.027245208 seconds. 1 rows.

**Step 4.** Run a query on the dataset with an index

Repeat the query, but this time against the dataset with the index configured:

```sql
SELECT * FROM traces WHERE trace_id = 'call_0x22ba49176f15ec5524434d87c47fc9dbff6ef8f584889ab4f0fa830d76a678d4_7_3_2_0_0_0_0_0';
```

> Time: 0.004053708 seconds. 1 rows.

Much faster!

**Step 5.** See what each query reads

Prefix each query with `EXPLAIN ANALYZE` to see how much data it reads:

```sql
EXPLAIN ANALYZE SELECT * FROM traces_no_index WHERE trace_id = 'call_0x22ba49176f15ec5524434d87c47fc9dbff6ef8f584889ab4f0fa830d76a678d4_7_3_2_0_0_0_0_0';
EXPLAIN ANALYZE SELECT * FROM traces WHERE trace_id = 'call_0x22ba49176f15ec5524434d87c47fc9dbff6ef8f584889ab4f0fa830d76a678d4_7_3_2_0_0_0_0_0';
```

In the plans, the `CayenneAccelerationExec` line shows the difference:

```console
-- traces_no_index
CayenneAccelerationExec: snapshots_scanned=1, files_scanned=27, ...
-- traces
CayenneAccelerationExec: snapshots_scanned=1, files_scanned=1, lookup_index=trace_id, candidate_files=1, uncovered_files=0, candidate_rows=1, ...
```

Without an index, Cayenne skips a file only when its min/max statistics rule the value out. For this lookup they don't, so the query opens all 27 files. With the index, it reads only the file that holds the row.

Cayenne uses an index when the query pins every column of that index to literal values, with `=`, `IN`, or an `OR` of equalities. See [Secondary indexes](https://spiceai.org/docs/components/data-accelerators/cayenne#secondary-indexes) for how Cayenne builds and maintains them.

## Learn more

- [Data Acceleration Indexes Documentation](https://spiceai.org/docs/features/data-acceleration/indexes)
- [Spice Cayenne Secondary Indexes](https://spiceai.org/docs/components/data-accelerators/cayenne#secondary-indexes)
