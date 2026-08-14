# DuckDB Data Connector

Works with `v1.0+`

This recipe will walkthrough how to connect to a DuckDB database in Spice with sample TPCH data.

## Requirements

- [DuckDB CLI](https://duckdb.org/docs/installation/?version=stable&environment=cli&platform=macos&download_method=package_manager) installed.
- Spice CLI installed (see [Getting Started](https://docs.spiceai.org/getting-started)).

## Follow these steps

**Step 1.** Initialize a new Spice app.

```bash
spice init duckdb-qs
cd duckdb-qs
```

**Step 2.** Create a DuckDB database with TPCH sample data.

```bash
duckdb ./tpch.db
```

Using the DuckDB CLI execute the following commands to generate TPC-H data with DuckDB's [TPCH extension](https://duckdb.org/docs/extensions/tpch.html).

```SQL
INSTALL tpch;
LOAD tpch;
CALL dbgen(sf = 1);
```

Output:

```SQL
100% ▕████████████████████████████████████████████████████████████▏
┌─────────┐
│ Success │
│ boolean │
├─────────┤
│ 0 rows  │
└─────────┘
```

Show the TPCH tables were correctly generated.

```SQL
SHOW TABLES;
```

Output:

```SQL
┌──────────┐
│   name   │
│ varchar  │
├──────────┤
│ customer │
│ lineitem │
│ nation   │
│ orders   │
│ part     │
│ partsupp │
│ region   │
│ supplier │
└──────────┘
```

Quit the DuckDB CLI by executing `.exit`.

**Step 3.** Configure the dataset to use the DuckDB database file. Copy and paste the YAML below to `duckdb-qs/spicepod.yaml`.

```yaml
version: v1
kind: Spicepod
name: duckdb-qs
datasets:
  - from: duckdb:customer
    name: tpch_customer
    params:
      duckdb_open: ./tpch.db
```

**Step 4.** Start the Spice runtime.

```bash
spice run
```

Confirm in the terminal output the `tpch_customer` dataset has been registered:

```bash
Spice.ai runtime starting...
2026-08-12T12:08:20.649413Z  INFO spiced: Starting runtime v2.1.4+models.metal
2026-08-12T12:08:20.651520Z  INFO runtime::init::dataset: Dataset tpch_customer initializing...
2026-08-12T12:08:20.660420Z  INFO runtime::init::dataset: Dataset tpch_customer registered (duckdb:customer), results cache enabled. duration_ms=0
2026-08-12T12:08:20.764115Z  INFO runtime: All components are loaded. Spice runtime is ready!
2026-08-12T12:08:20.851410Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2026-08-12T12:08:20.851788Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
```

**Step 5.** Run queries against the dataset using the Spice SQL REPL.

_In a new terminal_, start the Spice SQL REPL

```bash
spice sql
```

Query the `tpch_customer` dataset.

```sql
select c_name, c_address, c_acctbal, c_mktsegment from tpch_customer limit 10;
```

```sql
+--------------------+---------------------------------------+---------------+--------------+
|       c_name       |               c_address               |   c_acctbal   | c_mktsegment |
|       varchar      |                varchar                | decimal(15,2) |    varchar   |
+--------------------+---------------------------------------+---------------+--------------+
| Customer#000000001 | j5JsirBM9PsCy0O1m                     | 711.56        | BUILDING     |
| Customer#000000002 | 487LW1dovn6Q4dMVymKwwLE9OKf3QG        | 121.65        | AUTOMOBILE   |
| Customer#000000003 | fkRGN8nY4pkE                          | 7498.12       | AUTOMOBILE   |
| Customer#000000004 | 4u58h fqkyE                           | 2866.83       | MACHINERY    |
| Customer#000000005 | hwBtxkoBF qSW4KrIk5U 2B1AU7H          | 794.47        | HOUSEHOLD    |
| Customer#000000006 |  g1s,pzDenUEBW3O,2 pxu0f9n2g64rJrt5E  | 7638.57       | AUTOMOBILE   |
| Customer#000000007 | 8OkMVLQ1dK6Mbu6WG9 w4pLGQ n7MQ        | 9561.95       | AUTOMOBILE   |
| Customer#000000008 | j,pZ,Qp,qtFEo0r0c 92qobZtlhSuOqbE4JGV | 6819.74       | BUILDING     |
| Customer#000000009 | vgIql8H6zoyuLMFNdAMLyE7 H9            | 8324.07       | FURNITURE    |
| Customer#000000010 | Vf mQ6Ug9Ucf5OKGYq fsaX AtfsO7,rwY    | 2753.54       | HOUSEHOLD    |
+--------------------+---------------------------------------+---------------+--------------+

Time: 0.004229833 seconds. 10 rows.
```

## Learn more

- [DuckDB Data Connector Documentation](https://spiceai.org/docs/components/data-connectors/duckdb).

- For using `spice sql`, see the [CLI reference](https://docs.spiceai.org/cli/reference/sql).

- See the [datasets reference](https://docs.spiceai.org/reference/spicepod/datasets) for additional dataset configuration options.
