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
TPC-H table has a primary key, so all eight are eligible for CDC acceleration.
You can point a catalog at any PostgreSQL database, though: each table is
accelerated according to its `REPLICA IDENTITY` — a primary key, or a unique
index via `REPLICA IDENTITY USING INDEX` — and any table with no usable replica
identity is skipped with a warning rather than failing the whole catalog.

## How it differs from the [PostgreSQL Catalog Connector](../postgres) recipe

| | `catalogs/postgres` | This recipe |
|---|---|---|
| Discovers all tables | ✅ | ✅ |
| Query path | Federated (each query hits PostgreSQL) | Local accelerated copy (Cayenne) |
| Freshness | Live (source is queried directly) | Live via CDC from the WAL |
| Requires `wal_level=logical` | ❌ | ✅ |
| Each accelerated table needs a usable `REPLICA IDENTITY` (primary key or unique index); others are skipped | ❌ | ✅ |

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed
- Spice installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation)
- **PostgreSQL 13 or newer.** Catalog CDC creates its publication
  `WITH (publish_via_partition_root = true)` so that a partitioned table's
  changes are published under the parent relation; that publication option was
  introduced in PostgreSQL 13.

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

Create a `.env` file with the database credentials:

```bash
echo "PG_USER=postgres" > .env
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
      pg_sslmode: disable
    acceleration:
      refresh_mode: changes
```

> `refresh_mode: changes` is the only supported catalog-level acceleration mode,
> and the engine defaults to `cayenne`. Each discovered table is accelerated
> according to its PostgreSQL `REPLICA IDENTITY`: a primary key (`DEFAULT`) or a
> unique index (`USING INDEX`) becomes the CDC key, and `REPLICA IDENTITY FULL`
> works too **as long as the table also has a primary key** (it is heavier — the
> full old-row image is written to the WAL on every change). Note that `FULL`
> alone is **not** enough: `FULL` still needs a primary key (or a `USING INDEX`
> key) to route upserts, so a `FULL` table with no key is **still skipped**, just
> like `NOTHING` and a keyless `DEFAULT`. A skipped table gets a warning and is
> left out of the catalog rather than failing catalog setup. Use `include`/`exclude`
> to scope out tables (or whole schemas) you don't want accelerated, which also
> silences the skip warning for
> known-ineligible tables.

## Step 5. Start the Spice runtime

```bash
spice run
```

Spice discovers all tables, snapshots each into Cayenne, and opens a single
shared replication slot to keep them live:

```
INFO runtime::catalogconnector::postgres_accelerated: Catalog 'pg': accelerating 8 table(s) via CDC (8 via primary key, 0 via REPLICA IDENTITY USING INDEX, 0 via REPLICA IDENTITY FULL; shared replication slot 'spice_pg_f0da15_3f484bfe'); 0 table(s) excluded by include/exclude filters; 0 table(s) skipped (no usable replica identity -- see warnings); tables added to these schema(s) later are picked up on the periodic catalog refresh; schema changes to existing tables, and renamed or dropped tables, are not tracked.
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

## How it works: slots, publications, and restarts

**One slot and one publication per catalog.** All eligible tables in a catalog
share a single replication slot and a single publication, so a multi-table
catalog decodes the WAL once and opens one replication connection — not one per
table. The names are derived deterministically from the catalog (e.g.
`spice_pg_f0da15_3f484bfe` above).

**The publication lists only the eligible tables.** Spice builds the publication
explicitly with `FOR TABLE ... ` / `ADD TABLE ...` over the tables it
accelerates — never `FOR ALL TABLES`. This means:

- Tables with no usable `REPLICA IDENTITY` (keyless, `NOTHING`), views,
  materialized views, and foreign tables are **never** publication members, so
  the source never has to log changes Spice would only discard.
- Views and materialized views are not CDC-accelerable (they have no replica
  identity). Each one is reported with a "not replicated" warning and left out
  of the accelerated catalog — it is not an error, and it does not stop the
  eligible tables from replicating.
- Discovery re-runs on the catalog's periodic refresh, so a table added to a
  selected schema **after** startup is picked up and accelerated on the next
  refresh. Schema changes to existing tables, and renamed or dropped tables, are
  not tracked.

**Restart vs. re-snapshot.** The replication slot persists on the PostgreSQL
server across a Spice restart. When the same Spice instance restarts, it resumes
from the slot's `restart_lsn` and replays only the WAL accumulated while it was
down — it does **not** re-snapshot tables from scratch. The slot name is
deterministic for a given instance, which is what lets it find and reuse its own
slot on restart.

**Multiple Spice instances.** Two instances pointed at the same catalog get
distinct slot names, so they do not fight over one physical slot (PostgreSQL
permits a single consumer per slot). Rescheduling the same logical service onto a
different node is a distinct concern tracked by the slot-lifecycle enhancement
([#12018](https://github.com/spiceai/spiceai/issues/12018)), which covers making
the slot identity independent of the host and cleaning up slots that are no
longer used.

## Troubleshooting

**`Failed to setup the catalog pg (pg). PostgreSQL connection failed.`**

Another PostgreSQL is already listening on `localhost:5432` — commonly a
host-local install (Homebrew `postgresql@16`, Postgres.app, or another
container). Because it binds the loopback address directly, it shadows this
recipe's Docker container for connections from the host, so Spice connects to
the wrong server (which has no `tpch` database) and fails.

Confirm what's on the port:

```bash
lsof -nP -iTCP:5432 -sTCP:LISTEN
```

Then either free the port — e.g. `brew services stop postgresql@16`, or stop
the other container — **or** run this recipe on a different port by changing
the published port in `compose.yaml` (e.g. `"5433:5432"`) and `pg_port` in
`spicepod.yaml` to match.

**`... 0 of N discovered table(s) are eligible for CDC acceleration ...`**

The catalog matched no CDC-eligible tables, so it fails to load rather than
registering an empty catalog. The error reports how many of the discovered
tables were skipped for lacking a usable `REPLICA IDENTITY` and how many were
excluded by `include`/`exclude`. Common causes: an `include`/`exclude` pattern
that matches nothing (it
is matched against `schema.table`, e.g. `public.*`), or a database whose tables
have no primary key and no `REPLICA IDENTITY USING INDEX`/`FULL`. Fix the
patterns, or give the tables a usable replica identity (a primary key, or a
`UNIQUE NOT NULL` index set via `ALTER TABLE ... REPLICA IDENTITY USING INDEX
...`), then restart — a catalog that discovers zero eligible tables fails to
load, so it won't pick them up until Spice is restarted.

## References

- [Spice.ai PostgreSQL Catalog Connector documentation](https://docs.spiceai.org/components/catalogs/postgres)
- [Cayenne Data Accelerator documentation](https://docs.spiceai.org/components/data-accelerators/cayenne)
- [TPC-H Benchmark Specification](https://www.tpc.org/tpc_documents_current_versions/pdf/tpc-h_v2.17.1.pdf)
- [Spice SQL CLI reference](https://docs.spiceai.org/cli/reference/sql)
