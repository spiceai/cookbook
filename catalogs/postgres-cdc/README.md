# PostgreSQL Catalog CDC Acceleration

Works with `v2.2+`

The PostgreSQL Catalog Connector can automatically discover every table in a
database _and_ keep a local, always-fresh copy of each one using Change Data
Capture (CDC). Adding `acceleration: { refresh_mode: changes }` to the catalog
tells Spice to, with zero per-table configuration:

1. **Bootstrap** every discovered table by snapshotting it into the
   [Cayenne](https://docs.spiceai.org/components/data-accelerators/cayenne) accelerator, and
2. **Keep it live** by streaming inserts, updates, and deletes from the
   PostgreSQL write-ahead log (WAL) through a single shared replication slot.

Queries are then served from the local accelerated copy, and source mutations
show up automatically — no polling, no per-table `refresh_sql`, no manual
dataset definitions.

This recipe uses the standard TPC-H benchmark dataset (Scale Factor 1). Every
TPC-H table has a primary key, which catalog-level CDC acceleration requires.

## How it differs from the [PostgreSQL Catalog Connector](../postgres) recipe

| | `catalogs/postgres` | This recipe |
|---|---|---|
| Discovers all tables | ✅ | ✅ |
| Query path | Federated (each query hits PostgreSQL) | Local accelerated copy (Cayenne) |
| Freshness | Live (source is queried directly) | Live via CDC from the WAL |
| Requires `wal_level=logical` | ❌ | ✅ |
| Requires a primary key on every included table | ❌ | ✅ |

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed
- Spice installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation)

## Step 1. Start the PostgreSQL database

The database is started with `wal_level=logical` and replication slots enabled,
which is what lets Spice stream changes from the WAL. The `postgres-init`
container downloads the TPC-H SF1 parquet files and loads them into PostgreSQL,
creating all tables with primary keys and foreign keys.

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/catalogs/postgres-cdc
docker compose up -d
```

Wait for the init container to finish loading data (it downloads ~700 MB of
parquet files on first build):

```bash
docker compose logs -f postgres-init
```

You should see:

```
tpch-cdc-postgres-init  | PostgreSQL is ready.
tpch-cdc-postgres-init  | Creating schema ...
tpch-cdc-postgres-init  | Schema created.
...
tpch-cdc-postgres-init  | All TPC-H tables loaded successfully!
```

## Step 2. Create a new directory and initialize a Spicepod

```bash
mkdir postgres-cdc-catalog-recipe
cd postgres-cdc-catalog-recipe
spice init
```

## Step 3. Configure credentials

Create a `.env` file with the database credentials. Catalog-level CDC
acceleration opens a replication connection, which authenticates with a
password, so both `PG_USER` and `PG_PASS` are required:

```bash
printf 'PG_USER=postgres\nPG_PASS=postgres\n' > .env
```

## Step 4. Add the accelerated PostgreSQL catalog to `spicepod.yaml`

The only difference from the plain catalog connector is the `acceleration`
block:

```yaml
version: v1
kind: Spicepod
name: postgres-cdc-catalog-recipe

catalogs:
  - from: pg
    name: pg
    include:
      - 'public.*'
    params:
      pg_host: localhost
      pg_port: 5432
      pg_db: tpch
      pg_user: ${secrets:PG_USER}
      pg_pass: ${secrets:PG_PASS}
      pg_sslmode: disable
    acceleration:
      refresh_mode: changes
```

> `refresh_mode: changes` is the only supported catalog-level acceleration mode,
> and the engine defaults to `cayenne`. Every included table must have a primary
> key; catalog setup fails and names any table that doesn't. Use
> `include`/`exclude` to scope out tables (or whole schemas) you don't want
> accelerated.

## Step 5. Start the Spice runtime

```bash
spice run
```

Spice discovers all tables, snapshots each into Cayenne, and opens a single
shared replication slot to keep them live:

```
INFO runtime::catalogconnector::postgres_accelerated: Catalog 'pg': accelerating 8 tables via CDC (shared replication slot 'spice_pg_f0da15_3f484bfe'); 0 tables excluded by include/exclude filters.
INFO runtime::init::catalog: Registered catalog 'pg' with 1 schema and 8 tables
INFO data_components::postgres_replication::slot: Created new replication slot slot=spice_pg_f0da15_3f484bfe publication=spice_pg_f0da15_3f484bfe_pub
INFO data_components::postgres_replication::shared: dataset joined shared replication slot table=public.customer slot=spice_pg_f0da15_3f484bfe members=2
INFO data_components::postgres_replication::bootstrap: initial snapshot bootstrap complete dataset=...customer rows=150000 expected=Some(150000)
INFO data_components::postgres_replication::bootstrap: initial snapshot bootstrap complete dataset=...lineitem rows=6001215 expected=Some(6001101)
INFO runtime: All components are loaded. Spice runtime is ready!
```

All 8 tables share **one** replication slot and **one** publication — a
multi-table catalog opens a single replication connection, not one per table:

```bash
docker exec tpch-cdc-postgres psql -U postgres -d tpch \
  -c "SELECT slot_name, plugin, slot_type, active FROM pg_replication_slots;"
```

```
        slot_name         |  plugin  | slot_type | active
--------------------------+----------+-----------+--------
 spice_pg_f0da15_3f484bfe | pgoutput | logical   | t
(1 row)
```

## Step 6. Query the accelerated catalog

In a new terminal, start the Spice SQL REPL:

```bash
spice sql
```

Query a table using the three-part `catalog.schema.table` name — this reads
from the local accelerated copy, not from PostgreSQL:

```sql
SELECT c_custkey, c_name, c_mktsegment, c_acctbal
FROM pg.public.customer
WHERE c_custkey <= 5
ORDER BY c_custkey;
```

```
+-----------+--------------------+--------------+-----------+
| c_custkey | c_name             | c_mktsegment | c_acctbal |
+-----------+--------------------+--------------+-----------+
| 1         | Customer#000000001 | BUILDING     | 711.56    |
| 2         | Customer#000000002 | AUTOMOBILE   | 121.65    |
| 3         | Customer#000000003 | AUTOMOBILE   | 7498.12   |
| 4         | Customer#000000004 | MACHINERY    | 2866.83   |
| 5         | Customer#000000005 | HOUSEHOLD    | 794.47    |
+-----------+--------------------+--------------+-----------+

Time: 0.029 seconds. 5 rows.
```

## Step 7. Mutate the source and watch the change propagate

This is the point of CDC acceleration: change the data in PostgreSQL, and the
accelerated copy converges automatically.

The `mutate.sh` helper runs `INSERT`, `UPDATE`, and `DELETE` statements
**directly against PostgreSQL** (never against Spice). Run each step, then
re-run the query in the Spice SQL REPL to watch the change appear.

### Insert

```bash
./mutate.sh insert
```

```sql
SELECT c_custkey, c_name, c_mktsegment, c_acctbal
FROM pg.public.customer
WHERE c_custkey = 9999999;
```

Within about a second, the new row appears in the accelerated catalog:

```
+-----------+-------------------+--------------+-----------+
| c_custkey | c_name            | c_mktsegment | c_acctbal |
+-----------+-------------------+--------------+-----------+
| 9999999   | Customer#CDC-DEMO | BUILDING     | 100.00    |
+-----------+-------------------+--------------+-----------+

Time: 0.011 seconds. 1 rows.
```

### Update

```bash
./mutate.sh update
```

```sql
SELECT c_custkey, c_name, c_acctbal
FROM pg.public.customer
WHERE c_custkey = 9999999;
```

The updated balance propagates:

```
+-----------+-------------------+-----------+
| c_custkey | c_name            | c_acctbal |
+-----------+-------------------+-----------+
| 9999999   | Customer#CDC-DEMO | 999999.99 |
+-----------+-------------------+-----------+

Time: 0.011 seconds. 1 rows.
```

### Delete

```bash
./mutate.sh delete
```

```sql
SELECT count(*) AS n
FROM pg.public.customer
WHERE c_custkey = 9999999;
```

The row is gone:

```
+---+
| n |
+---+
| 0 |
+---+

Time: 0.011 seconds. 1 rows.
```

No refresh, no restart — the accelerated catalog stays in lock-step with the
source through the WAL.

## Step 8. Clean up

```bash
docker compose down --volumes --rmi local
```

## References

- [Spice.ai PostgreSQL Catalog Connector documentation](https://docs.spiceai.org/components/catalogs/postgres)
- [Cayenne Data Accelerator documentation](https://docs.spiceai.org/components/data-accelerators/cayenne)
- [TPC-H Benchmark Specification](https://www.tpc.org/tpc_documents_current_versions/pdf/tpc-h_v2.17.1.pdf)
- [Spice SQL CLI reference](https://docs.spiceai.org/cli/reference/sql)
