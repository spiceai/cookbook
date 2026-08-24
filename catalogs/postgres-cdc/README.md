# PostgreSQL Catalog CDC Acceleration

Works with `v2.2.0+`

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

> **Alpha.** Catalog-level CDC acceleration is Alpha in `v2.2.0`; the
> configuration may still change. See [Known limitations](#known-limitations).

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
| Requires a replication slot on the source | ❌ | ✅ (one per catalog) |
| Each accelerated table needs a usable `REPLICA IDENTITY` (primary key or unique index); others are skipped | ❌ | ✅ |
| Views and materialized views appear in the catalog | ✅ | ❌ (not CDC-accelerable) |

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed
- Spice installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation)
- **PostgreSQL 13 or newer.** Catalog CDC creates its publication
  `WITH (publish_via_partition_root = true)` so that a partitioned table's
  changes are published under the parent relation; that publication option was
  introduced in PostgreSQL 13.

The `compose.yaml` in this recipe already satisfies what CDC requires of the
source. Pointing the catalog at your own PostgreSQL instead means ensuring:

- `wal_level = logical`
- the connecting role can start replication (`REPLICATION`, or superuser)
- at least one free replication slot (`max_replication_slots`)

Spice checks all three before it touches any table and fails fast with a
specific error if one is missing — see [Troubleshooting](#troubleshooting).

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

```console
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
block. At its smallest, that is one line:

```yaml
    acceleration:
      refresh_mode: changes
```

This recipe adds a file mode so the acceleration survives a restart
(see [Step 8](#step-8-restart-and-resume-without-re-snapshotting)):

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
      mode: file
      params:
        cayenne_file_path: .spice/data/pg-catalog
```

The `acceleration` block takes four keys, all applied uniformly to every table
the catalog accelerates:

| Key | Required | Meaning |
|---|---|---|
| `refresh_mode` | ✅ | The only supported value is `changes` (CDC). There is no catalog-level `full` mode, and no default — an `acceleration` block without it is a configuration error. |
| `engine` | | The accelerator engine. Defaults to `cayenne`, currently the only supported value. |
| `mode` | | Storage mode, same meaning as a dataset's `acceleration.mode`. Defaults to `memory`. |
| `params` | | Engine parameters, same meaning as a dataset's `acceleration.params` (e.g. `cayenne_file_path`). |

> **`mode` decides whether a restart re-snapshots.** The default `memory` holds
> the acceleration only in RAM: nothing is written to disk, so it starts empty
> on every run and each table re-runs its initial snapshot from the source.
> Spice warns once at startup when the configured mode is not durable. A file
> `mode` with `params.cayenne_file_path` persists it, and each table gets its
> own subdirectory under that path. If the goal is RAM-speed CDC writes rather
> than discarding them, keep a file `mode` and add
> `params.cayenne_cdc_durability: memory`, which buffers in RAM but still drains
> to durable storage.

> **Per-table acceleration settings are not configurable here.** `primary_key`,
> `on_conflict`, `indexes` and other per-dataset overrides remain exclusively on
> an individual dataset's own `acceleration` block. Each table's CDC key is
> resolved from its `REPLICA IDENTITY`: a primary key (`DEFAULT`) or a unique
> index (`USING INDEX`) becomes the key, and `REPLICA IDENTITY FULL` works too
> **as long as the table also has a primary key** (it is heavier — the full
> old-row image is written to the WAL on every change). `FULL` alone is **not**
> enough: it still needs a primary key (or a `USING INDEX` key) to route
> upserts, so a `FULL` table with no key is **still skipped**, just like
> `NOTHING` and a keyless `DEFAULT`. A skipped table gets a warning and is left
> out of the catalog rather than failing catalog setup. Use `include`/`exclude`
> to scope out tables (or whole schemas) you don't want accelerated, which also
> silences the skip warning for known-ineligible tables.

## Step 5. Start the Spice runtime

```bash
spice run
```

Spice discovers all tables, snapshots each into Cayenne, and opens a single
shared replication slot to keep them live:

```console
INFO runtime::catalogconnector::postgres_accelerated: Catalog 'pg': accelerating 8 table(s) via CDC (8 via primary key, 0 via REPLICA IDENTITY USING INDEX, 0 via REPLICA IDENTITY FULL; shared replication slot 'spice_catalog_pg_f0da15'); 0 table(s) excluded by include/exclude filters; 0 table(s) skipped (no usable replica identity -- see warnings); tables added to these schema(s) later are picked up on the periodic catalog refresh; schema changes to existing tables, and renamed or dropped tables, are not tracked.
INFO runtime::init::catalog: Registered catalog 'pg' with 1 schema and 8 tables
INFO runtime::init::dataset: Dataset __catalog_accel_pg__public__customer registered (postgres:public.customer), acceleration (cayenne:file, changes), results cache enabled. duration_ms=664
INFO data_components::postgres_replication::slot: Created new replication slot slot=spice_catalog_pg_f0da15 publication=spice_catalog_pg_f0da15_pub consistent_lsn=0/94F12180 snapshot=0/94F12180
INFO data_components::postgres_replication::shared: dataset joined shared replication slot dataset=__catalog_accel_pg__public__customer table=public.customer slot=spice_catalog_pg_f0da15 publication=spice_catalog_pg_f0da15_pub snapshot=true rejoining=false members=5
INFO data_components::postgres_replication::bootstrap: initial snapshot bootstrap complete dataset=__catalog_accel_pg__public__customer rows=150000 expected=Some(150000)
INFO data_components::postgres_replication::bootstrap: initial snapshot bootstrap complete dataset=__catalog_accel_pg__public__lineitem rows=6001215 expected=Some(6001215)
INFO runtime: All components are loaded. Spice runtime is ready!
```

Spice also logs, once, what the slot costs the source:

```console
INFO data_components::postgres_replication::slot: Replication slot `spice_catalog_pg_f0da15` retains WAL on the source for as long as it exists, so the source's disk grows whenever Spice is not consuming it. Nothing removes it: Spice reuses it across restarts and never drops it, and this server is too old to retire idle slots itself (PostgreSQL 18 added idle_replication_slot_timeout), so removing Spice leaves it retaining WAL until you drop it with `SELECT pg_drop_replication_slot('spice_catalog_pg_f0da15');`. Until then, max_slot_wal_keep_size is the only bound on what it retains.
```

`docker compose down --volumes` in [Step 9](#step-9-clean-up) discards this
recipe's database entirely, so there is nothing to drop here — but against your
own PostgreSQL, dropping the slot is a manual step when you stop using Spice.

All 8 tables share **one** replication slot and **one** publication — a
multi-table catalog opens a single replication connection, not one per table:

```bash
docker exec tpch-cdc-postgres psql -U postgres -d tpch \
  -c "SELECT slot_name, plugin, slot_type, active FROM pg_replication_slots;" \
  -c "SELECT pubname FROM pg_publication;"
```

```console
        slot_name        |  plugin  | slot_type | active
-------------------------+----------+-----------+--------
 spice_catalog_pg_f0da15 | pgoutput | logical   | t
(1 row)

           pubname
-----------------------------
 spice_catalog_pg_f0da15_pub
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

```console
+-----------+--------------------+--------------+---------------+
| c_custkey |       c_name       | c_mktsegment |   c_acctbal   |
|   int32   |       varchar      |    varchar   | decimal(15,2) |
+-----------+--------------------+--------------+---------------+
| 1         | Customer#000000001 | BUILDING     | 711.56        |
| 2         | Customer#000000002 | AUTOMOBILE   | 121.65        |
| 3         | Customer#000000003 | AUTOMOBILE   | 7498.12       |
| 4         | Customer#000000004 | MACHINERY    | 2866.83       |
| 5         | Customer#000000005 | HOUSEHOLD    | 794.47        |
+-----------+--------------------+--------------+---------------+

Time: 0.018687291 seconds. 5 rows.
```

> A table that is still bootstrapping is reported as not-yet-present rather
> than being served from PostgreSQL — queries never transparently fall back to
> the un-accelerated source. On a large catalog, a table queried during startup
> can therefore be "not found" until its snapshot completes.

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

```console
+-----------+---------------------+--------------+---------------+
| c_custkey |        c_name       | c_mktsegment |   c_acctbal   |
|   int32   |       varchar       |    varchar   | decimal(15,2) |
+-----------+---------------------+--------------+---------------+
| 9999999   | Customer#CDC-DEMO   | BUILDING     | 100.00        |
+-----------+---------------------+--------------+---------------+

Time: 0.003589333 seconds. 1 rows.
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

```console
+-----------+---------------------+---------------+
| c_custkey |        c_name       |   c_acctbal   |
|   int32   |       varchar       | decimal(15,2) |
+-----------+---------------------+---------------+
| 9999999   | Customer#CDC-DEMO   | 999999.99     |
+-----------+---------------------+---------------+

Time: 0.003188542 seconds. 1 rows.
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

```console
+-------+
|   n   |
| int64 |
+-------+
| 0     |
+-------+

Time: 0.015511666 seconds. 1 rows.
```

No refresh, no restart — the accelerated catalog stays in lock-step with the
source through the WAL.

## Step 8. Restart and resume without re-snapshotting

Because this recipe uses a file `mode`, the acceleration is on disk and the
replication slot persists on the PostgreSQL server. A restart resumes from the
slot's position and replays only the WAL that accumulated while Spice was down.

Stop the runtime with `Ctrl+C`, then change the source while it is down:

```bash
docker exec -i tpch-cdc-postgres psql -U postgres -d tpch -c \
  "INSERT INTO customer (c_custkey, c_name, c_address, c_nationkey, c_phone, c_acctbal, c_mktsegment, c_comment) VALUES (8888888, 'Customer#WHILE-DOWN', '2 Offline Ave', 0, '00-000-000-0000', 42.00, 'BUILDING', 'inserted while spice was down');"
```

Start it again:

```bash
spice run
```

Every table rejoins the existing slot with `snapshot=false`, and there is **no**
`initial snapshot bootstrap complete` line — nothing is re-read from the source:

```console
INFO data_components::postgres_replication::slot: Resuming from existing replication slot slot=spice_catalog_pg_f0da15 publication=spice_catalog_pg_f0da15_pub confirmed_flush_lsn=0/9562E930
INFO data_components::postgres_replication::shared: dataset joined shared replication slot dataset=__catalog_accel_pg__public__customer table=public.customer slot=spice_catalog_pg_f0da15 publication=spice_catalog_pg_f0da15_pub snapshot=false rejoining=false members=6
INFO runtime: All components are loaded. Spice runtime is ready!
```

The row inserted while Spice was down is caught up from the WAL:

```sql
SELECT c_custkey, c_name, c_acctbal
FROM pg.public.customer
WHERE c_custkey = 8888888;
```

```console
+-----------+---------------------+---------------+
| c_custkey |        c_name       |   c_acctbal   |
|   int32   |       varchar       | decimal(15,2) |
+-----------+---------------------+---------------+
| 8888888   | Customer#WHILE-DOWN | 42.00         |
+-----------+---------------------+---------------+

Time: 0.003789458 seconds. 1 rows.
```

With the default `mode: memory`, this same restart re-snapshots all eight
tables instead.

## Step 9. Clean up

```bash
docker compose down --volumes --rmi local
```

## How it works: slots, publications, and restarts

**One slot and one publication per catalog.** All eligible tables in a catalog
share a single replication slot and a single publication, so a multi-table
catalog decodes the WAL once and opens one replication connection — not one per
table. The slot is named `spice_catalog_{catalog_name}_{hash}` (the `pg` catalog
above gives `spice_catalog_pg_f0da15`), and the publication is that name plus
`_pub`. The `spice_catalog_` prefix keeps it distinct from the per-dataset
`spice_` slots, and the trailing hash keeps two long catalog names that share a
truncated prefix distinct within PostgreSQL's 63-byte identifier limit.

**The publication lists only the eligible tables.** Spice builds the publication
explicitly with `FOR TABLE ... ` / `ADD TABLE ...` over the tables it
accelerates — never `FOR ALL TABLES`. This means:

- Tables with no usable `REPLICA IDENTITY` (keyless, `NOTHING`), views,
  materialized views, and foreign tables are **never** publication members, so
  the source never has to log changes Spice would only discard.
- Views, materialized views, and foreign tables are not CDC-accelerable (they
  have no replica identity). Each one is reported with a "not replicated"
  warning and left out of the accelerated catalog — it is not an error, and it
  does not stop the eligible tables from replicating. This is the one way an
  accelerated catalog's namespace differs from an un-accelerated one's.
- Discovery re-runs on the catalog's periodic refresh (once a minute), so a
  table added to a selected schema **after** startup is picked up and
  accelerated on the next refresh. Schema changes to existing tables, and
  renamed or dropped tables, are not tracked.

**The slot outlives Spice.** A replication slot retains WAL on the source for as
long as it exists, so the source's disk grows whenever Spice is not consuming
it. Spice reuses its slot across restarts and never drops it, so removing Spice
leaves the slot retaining WAL until it is dropped manually. Every slot Spice
creates is named `spice_…`:

```sql
SELECT slot_name, active, wal_status,
       pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS retained
FROM pg_replication_slots WHERE slot_name LIKE 'spice_%';
```

```sql
SELECT pg_drop_replication_slot('spice_catalog_pg_f0da15');
```

PostgreSQL 18 added `idle_replication_slot_timeout` to retire idle slots
automatically; on older servers `max_slot_wal_keep_size` is the only bound.

**Restart vs. re-snapshot.** The slot name is a pure function of the catalog
`name` — it carries no instance, host, or process component — so a restart, or a
reschedule onto a different node, recomputes the identical name and reuses the
existing slot. Whether that avoids a re-snapshot depends on `acceleration.mode`:

- **A file mode** (this recipe) persists the acceleration, so the restart
  resumes from the slot's position and replays only the WAL accumulated while
  Spice was down.
- **`mode: memory`** (the default) keeps nothing on disk, so the acceleration
  starts empty and every table re-runs its initial snapshot from the source —
  the slot is still reused, but there is no local state for it to continue from.

**One Spice instance per accelerated catalog.** Because the slot name is
instance-independent, two instances configured with the same catalog `name`
resolve to the *same* slot, and PostgreSQL permits only one consumer per slot.
Before it starts streaming, Spice checks whether the slot is already **actively**
held: an absent slot is created, a present-but-inactive slot is reused, and an
actively-held one fails the catalog to load with an error naming the slot and
the consumer. A slot can also read as active immediately after the runtime's own
ungraceful exit — PostgreSQL keeps the walsender marked active until
`wal_sender_timeout` elapses — so Spice waits for it to free (the server's
`wal_sender_timeout` plus a 5-second grace, polled once a second; a 90-second
budget when `wal_sender_timeout` is disabled) before concluding another consumer
owns it. Making slot identity independent of the deployment, and cleaning up
slots that are no longer used, is tracked by the slot-lifecycle enhancement
([#12018](https://github.com/spiceai/spiceai/issues/12018)).

## Observability

Each catalog refresh records how every discovered relation was resolved, as
gauges (they can rise or fall, since each refresh re-plans the whole namespace).
Start the runtime with a metrics endpoint to see them:

```bash
spice run --metrics-endpoint 127.0.0.1:9090
```

```bash
curl -s http://127.0.0.1:9090/metrics | grep catalog_acceleration
```

```console
catalog_acceleration_accelerated_tables{catalog="pg",kind="full"} 0
catalog_acceleration_accelerated_tables{catalog="pg",kind="primary_key"} 8
catalog_acceleration_accelerated_tables{catalog="pg",kind="unique_index"} 0
catalog_acceleration_tables{catalog="pg",category="accelerated"} 8
catalog_acceleration_tables{catalog="pg",category="excluded"} 0
catalog_acceleration_tables{catalog="pg",category="skipped"} 0
catalog_acceleration_tables{catalog="pg",category="views_not_replicated"} 0
```

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

**`Cannot start CDC catalog acceleration: PostgreSQL wal_level is 'replica', but 'logical' is required.`**

Logical decoding is off on the source. Run
`ALTER SYSTEM SET wal_level = 'logical';` and restart PostgreSQL. This recipe's
`compose.yaml` already passes `-c wal_level=logical`, so this only comes up
against your own database.

**`Cannot start CDC catalog acceleration: PostgreSQL role '<role>' is not permitted to start replication.`**

The connecting role can read the tables but cannot open a replication
connection. Grant it with `ALTER ROLE "<role>" REPLICATION;`, or connect as a
superuser. On managed PostgreSQL the equivalent is provider-specific (for
example, Amazon RDS grants `rds_replication`).

**`Cannot start CDC catalog acceleration: PostgreSQL has no free replication slots ...`**

The server is at `max_replication_slots` and the catalog's slot does not exist
yet. Drop an unused slot, or raise the limit and restart PostgreSQL:

```sql
SELECT slot_name, active FROM pg_replication_slots;
SELECT pg_drop_replication_slot('<slot_name>');
```

The check is skipped when the catalog's slot **already** exists, since reusing
it consumes no additional capacity — so a restart still succeeds on a server
whose slots are otherwise full.

**`Catalog 'pg': replication slot '...' is already in use by PID <n> ...`**

Another Spice instance (or process) is already streaming this catalog's
changes. Run only one instance per accelerated catalog, or stop the other
consumer. Spice already waits out a shutting-down predecessor before reporting
this, so a genuine restart or rolling deploy does not trip it.

**`... 0 of N discovered table(s) are eligible for CDC acceleration ...`**

The catalog matched no CDC-eligible tables, so it fails to load rather than
registering an empty catalog. The error reports how many of the discovered
tables were skipped for lacking a usable `REPLICA IDENTITY` and how many were
excluded by `include`/`exclude`. Common causes: an `include`/`exclude` pattern
that matches nothing (it is matched against `schema.table`, e.g. `public.*`), or
a database whose tables have no primary key and no `REPLICA IDENTITY USING
INDEX`/`FULL`. Fix the patterns, or give the tables a usable replica identity (a
primary key, or a `UNIQUE NOT NULL` index set via `ALTER TABLE ... REPLICA
IDENTITY USING INDEX ...`), then restart — a catalog that discovers zero
eligible tables fails to load, so it won't pick them up until Spice is
restarted.

**A table or view is missing from the catalog.**

Every TPC-H table in this recipe is eligible, so its startup summary reports 8
accelerated and 0 skipped. Against a database with keyless tables or views, the
same catalog logs one warning per relation it left out, and the summary counts
them:

```console
WARN runtime::catalogconnector::postgres_accelerated: Catalog 'pg': skipping table public.events_no_pk: no primary key (REPLICA IDENTITY DEFAULT) -- add a primary key, or a unique NOT NULL index with REPLICA IDENTITY USING INDEX. Exclude it via the catalog's `include`/`exclude` patterns to suppress this warning. Docs: https://spiceai.org/docs/components/data-connectors/postgres
WARN runtime::catalogconnector::postgres_accelerated: Catalog 'pg': view public.customer_summary is not replicated -- views cannot be CDC-accelerated (no REPLICA IDENTITY). It is absent from the accelerated catalog; query it through a non-accelerated catalog or dataset instead. Exclude it via the catalog's `include`/`exclude` patterns to suppress this warning. Docs: https://spiceai.org/docs/components/data-connectors/postgres
INFO runtime::catalogconnector::postgres_accelerated: Catalog 'pg': accelerating 8 table(s) via CDC (...); 0 table(s) excluded by include/exclude filters; 1 table(s) skipped (no usable replica identity -- see warnings); 2 view(s)/materialized view(s)/foreign table(s) not replicated (see warnings); ...
```

Give the table a usable replica identity, exclude it to silence the warning, or
reach those relations through a second, un-accelerated catalog.

## Known limitations

- **Alpha.** Catalog-level CDC acceleration is Alpha in `v2.2.0` and its
  configuration may change. Feedback is welcome in
  [#11850](https://github.com/spiceai/spiceai/issues/11850).
- **Views and materialized views are not replicated** and are absent from the
  accelerated catalog ([#11911](https://github.com/spiceai/spiceai/issues/11911)).
- **A table dropped and recreated in the source** can serve rows captured before
  it was recreated ([#12110](https://github.com/spiceai/spiceai/issues/12110)).
- **Schema changes are not tracked.** Discovery picks up newly added tables on
  the periodic refresh, but column changes to existing tables, and renamed or
  dropped tables, are not.
- **`include`/`exclude` filter tables, not schemas.** Both are matched against
  `schema.table`.
- **Catalog tables are read-only**, and per-table `acceleration` blocks cannot
  be set on individually discovered tables.

## References

- [Catalog-Level CDC Acceleration documentation](https://docs.spiceai.org/components/catalogs/postgres#catalog-level-cdc-acceleration)
- [Spice.ai PostgreSQL Catalog Connector documentation](https://docs.spiceai.org/components/catalogs/postgres)
- [Cayenne Data Accelerator documentation](https://docs.spiceai.org/components/data-accelerators/cayenne)
- [TPC-H Benchmark Specification](https://www.tpc.org/tpc_documents_current_versions/pdf/tpc-h_v2.17.1.pdf)
- [Spice SQL CLI reference](https://docs.spiceai.org/cli/reference/sql)
