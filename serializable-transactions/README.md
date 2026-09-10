# Serializable Transactions with Durable Write-Back (Balance Transfer)

Works with `v2.2+`

This recipe demonstrates **gated serializable transactions** on Cayenne-accelerated
tables backed by PostgreSQL. You submit a whole `BEGIN … COMMIT` body — a gate plus one
or more writes — as a single request; Spice commits every write **atomically across
tables**, enforces the gate, detects conflicting concurrent writers, and **writes the
result back to PostgreSQL**.

The classic example is a **bank transfer**: move money from `checking` to `savings`,
but only if `checking` has sufficient funds, and never leave the books half-updated.

```sql
BEGIN;
SELECT assert((SELECT balance FROM checking WHERE id = 'alice') >= 200);  -- the gate
UPDATE checking SET balance = balance - 200 WHERE id = 'alice';           -- debit
UPDATE savings  SET balance = balance + 200 WHERE id = 'alice';           -- credit
COMMIT;
```

- **Atomic across tables** — the debit and credit commit together or not at all.
- **Gated** — `assert(<bool>)` aborts (and rolls back) the whole body when its argument is
  false or NULL. Here it prevents an overdraft. "Conditional"-ness is just your choice to
  use `assert()`; the mechanism underneath is a plain serializable transaction.
- **Serializable / conflict-detected** — two transfers that touch the same account are
  ordered; a stale one is rejected with a retryable conflict (HTTP `409`) instead of
  silently losing an update. Transfers on disjoint accounts run concurrently.
- **Durable write-back** — the committed balances are reconciled back to PostgreSQL, so
  the source of record stays in sync.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) is installed
- Spice is installed (see [Getting Started](https://docs.spiceai.org/getting-started))

> PostgreSQL write-back over CDC requires the server to run with `wal_level=logical`, and
> the connecting role must have the `REPLICATION` attribute (the default `postgres`
> superuser has it). This recipe runs a single Postgres in Docker without TLS, suitable
> for local development.

---

## Step 1. Start PostgreSQL with logical replication enabled

```bash
docker run -d --name spice-bank \
  -e POSTGRES_PASSWORD=spice \
  -e POSTGRES_DB=spice_demo \
  -p 5432:5432 \
  postgres:16 -c wal_level=logical
```

Confirm logical WAL is active (should print `logical`):

```bash
docker exec spice-bank psql -U postgres -d spice_demo -c "SHOW wal_level;"
```

---

## Step 2. Create and seed the accounts

Two tables, each with a single-column primary key — required so `UPDATE` replicates and
so write-back can address rows by key. (A `DELETE` through Spice is refused on a
write-back dataset; see [What write-back refuses](#what-write-back-refuses).) Alice
starts with 1000 in checking, 0 in savings.

```bash
docker exec -i spice-bank psql -U postgres -d spice_demo <<'EOF'
CREATE TABLE checking (id TEXT PRIMARY KEY, balance BIGINT NOT NULL);
CREATE TABLE savings  (id TEXT PRIMARY KEY, balance BIGINT NOT NULL);
INSERT INTO checking (id, balance) VALUES ('alice', 1000), ('bob', 500);
INSERT INTO savings  (id, balance) VALUES ('alice', 0),    ('bob', 0);
SELECT 'seeded' AS status;
EOF
```

---

## Step 3. Configure the datasets

Copy [`spicepod.yaml`](./spicepod.yaml) and [`.env`](./.env) into your Spice app. Both
tables are accelerated by Cayenne with `write_mode: write_back` and share the default
Cayenne metastore, so a transaction spanning both commits atomically. See the file for
the full annotated configuration.

---

## Step 4. Start the Spice runtime

```bash
spice run
```

You should see both datasets bootstrap from a snapshot and begin streaming WAL:

```
INFO runtime::init::dataset: Dataset checking registered (postgres:checking), acceleration (cayenne:file, changes).
INFO runtime::init::dataset: Dataset savings registered (postgres:savings), acceleration (cayenne:file, changes).
INFO runtime: All components are loaded. Spice runtime is ready!
```

---

## Step 5. Check the opening balances

```bash
curl -s -XPOST http://localhost:8090/v1/sql -d \
  "SELECT 'checking' AS acct, id, balance FROM checking
   UNION ALL SELECT 'savings', id, balance FROM savings ORDER BY id, acct;"
```

```json
[{"acct":"checking","id":"alice","balance":1000},
 {"acct":"savings","id":"alice","balance":0},
 {"acct":"checking","id":"bob","balance":500},
 {"acct":"savings","id":"bob","balance":0}]
```

---

## Step 6. Make a gated, atomic transfer

Move 200 from Alice's checking to her savings — as one transaction. The gate asserts she
has at least 200 before either row changes.

```bash
curl -s -XPOST http://localhost:8090/v1/sql -d "
BEGIN;
SELECT assert((SELECT balance FROM checking WHERE id = 'alice') >= 200);
UPDATE checking SET balance = balance - 200 WHERE id = 'alice';
UPDATE savings  SET balance = balance + 200 WHERE id = 'alice';
COMMIT;"
```

Both balances moved together — checking 800, savings 200:

```bash
curl -s -XPOST http://localhost:8090/v1/sql -d \
  "SELECT balance FROM checking WHERE id='alice';"   # -> 800
curl -s -XPOST http://localhost:8090/v1/sql -d \
  "SELECT balance FROM savings WHERE id='alice';"    # -> 200
```

---

## Step 7. Confirm it was written back to PostgreSQL

The transaction committed to the accelerator; the write-back worker reconciles it to the
source. Query Postgres **directly** — the money moved there too:

```bash
docker exec spice-bank psql -U postgres -d spice_demo -c \
  "SELECT 'checking' t, id, balance FROM checking WHERE id='alice'
   UNION ALL SELECT 'savings', id, balance FROM savings WHERE id='alice';"
```

```console
    t     |  id   | balance
----------+-------+---------
 checking | alice |     800
 savings  | alice |     200
```

> Write-back is asynchronous — it may lag a commit by a moment under load. The commit to
> the accelerator is durable immediately; the source converges shortly after.

---

## Step 8. Overdraft protection (the gate rolls back everything)

Try to transfer 5000 — more than Alice's 800 checking balance. The `assert` fails, so the
**entire** body rolls back; neither table changes.

```bash
curl -s -XPOST http://localhost:8090/v1/sql -d "
BEGIN;
SELECT assert((SELECT balance FROM checking WHERE id = 'alice') >= 5000);
UPDATE checking SET balance = balance - 5000 WHERE id = 'alice';
UPDATE savings  SET balance = balance + 5000 WHERE id = 'alice';
COMMIT;"
```

```json
{"code":400,"message":"assertion failed: gate expression was false or NULL"}
```

Balances are unchanged (checking still 800, savings still 200) — the debit that was staged
before the gate never published:

```bash
curl -s -XPOST http://localhost:8090/v1/sql -d \
  "SELECT balance FROM checking WHERE id='alice';"   # -> 800 (unchanged)
```

---

## Step 9. Concurrency: conflicting transfers are serialized

If two transactions read-modify-write the **same** account concurrently, one commits and
the stale one is rejected with a retryable conflict (HTTP `409`) — never a lost update.
Transfers on **different** accounts (e.g. Alice vs Bob) commit concurrently without
contention. Retry a `409` and it succeeds against the new balance.

---

## Step 10. Cleanup

```bash
docker rm -f spice-bank
```

Dropping the container removes the replication slots with it. Against a long-lived server,
drop them manually:

```sql
SELECT pg_drop_replication_slot('spice_checking');
SELECT pg_drop_replication_slot('spice_savings');
```

---

## How it works

- Every statement runs through the normal query path, so authorization, masking, and
  logging apply. Atomicity comes from a **transaction-aware sink**: inside a `BEGIN … COMMIT`
  body the writes **stage** into an invisible snapshot instead of publishing.
- At `COMMIT`, Spice re-checks **per-key optimistic concurrency** — each committed write
  stamps a sequence onto the primary keys it touched; if a key your transaction read or
  wrote advanced since it began, the commit aborts with a retryable `409`.
- Tables sharing one Cayenne metastore commit in a **single metastore transaction**, so a
  multi-table transfer is all-or-nothing.
- For `write_mode: write_back`, the commit records the touched primary keys in a marker
  table **in the same commit transaction**; a per-table worker then reconciles them to
  PostgreSQL idempotently (delete-by-key, then insert the current rows).

## What write-back refuses

> **Version note:** Both refusals below were added in `v2.3.0`. On `v2.2.x` these
> statements were accepted, and a `DELETE` could diverge the accelerator from
> PostgreSQL without recording anything for delivery.

`write_mode: write_back` only accepts writes it can record for delivery to PostgreSQL,
so two shapes are refused outright rather than silently diverging from the source:

- **Writes outside a transaction.** An `INSERT` or `UPDATE` that is not inside a
  `BEGIN … COMMIT` body is refused. Every write in this recipe is submitted as one
  `BEGIN; … COMMIT;` request, which is why they succeed.
- **`DELETE` in any form, and `TRUNCATE`.** A delete cannot be recorded for delivery,
  so it is refused:

  ```console
  Failed to delete from dataset 'checking': DELETE is not supported while
  'acceleration.write_mode: write_back' is enabled, because a delete cannot be
  recorded for delivery to the federated source.
  ```

  To remove rows at the source, stop writing to the dataset and wait for its
  `dataset_acceleration_write_back_pending_keys` metric to reach zero *while write-back
  is still enabled* — the delivery worker is what drains it, and taking the dataset out
  of write-back stops that worker and clears the gauge without delivering anything. Once
  it reads zero, take the dataset out of write-back, delete at the source, and let the
  change stream refresh the accelerator.

The runtime also refuses a write-back configuration it cannot uphold, which is why each
dataset here sets `mode: file`, declares a single-column `primary_key`, and sets no
retention.

## Additional Resources

- [Cayenne accelerator cookbook](../cayenne/README.md)
- [PostgreSQL CDC cookbook](../postgres/cdc/README.md)
- [Data Accelerators documentation](https://docs.spiceai.org/components/data-accelerators)
