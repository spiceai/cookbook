# PostgreSQL CDC (Logical Replication)

Works with `v2.0+`

This recipe demonstrates how to stream real-time changes from a PostgreSQL table into Spice using native Change Data Capture (CDC) over [logical replication](https://www.postgresql.org/docs/current/logical-replication.html) (WAL streaming). Inserts, updates, and deletes propagate automatically to the Spice accelerator — no Debezium or Kafka required.

Through a replication slot, PostgreSQL streams decoded WAL changes to Spice, which applies them by primary key. The dataset first bootstraps from a consistent snapshot, then follows the slot so replication resumes from where it left off after a restart.

> **Note:** Each replication slot runs a dedicated `walsender` process on the PostgreSQL server and holds back WAL until Spice has consumed it, so every streamed dataset adds some load on the source. Keep this in mind when streaming many tables from one server.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) is installed
- Spice is installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation)

> **Note:** PostgreSQL CDC requires the server to run with `wal_level=logical`, and the connecting role must have the `REPLICATION` attribute. The default `postgres` superuser already has it. This recipe runs a single Postgres instance in Docker without TLS, which is suitable for local development.

---

## Step 1. Start PostgreSQL with logical replication enabled

```bash
docker run -d --name postgres-cdc \
  -e POSTGRES_PASSWORD=spice \
  -e POSTGRES_DB=spice_demo \
  -p 5434:5432 \
  postgres:16 -c wal_level=logical
```

Wait a few seconds for Postgres to finish initializing, then confirm logical WAL is active (should print `logical`):

```bash
docker exec postgres-cdc psql -U postgres -d spice_demo -c "SHOW wal_level;"
```

```console
 wal_level
-----------
 logical
(1 row)
```

---

## Step 2. Seed the table

```bash
docker exec -i postgres-cdc psql -U postgres -d spice_demo <<'EOF'
CREATE TABLE orders (
  id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  customer TEXT,
  amount   NUMERIC(10,2),
  status   TEXT
);
INSERT INTO orders (customer, amount, status) VALUES
  ('Alice',   99.99,  'pending'),
  ('Bob',     149.50, 'pending'),
  ('Charlie', 299.00, 'shipped');
SELECT 'Seeded ' || COUNT(*) || ' orders' AS result FROM orders;
EOF
```

> The `orders` table has a primary key, so its default `REPLICA IDENTITY` covers `UPDATE` and `DELETE` events. A table without a primary key would need `ALTER TABLE ... REPLICA IDENTITY FULL` before it can be streamed.

---

## Step 3. Start the Spice runtime

```bash
spice run
```

You should see the dataset bootstrap from a consistent snapshot and then transition to live WAL streaming:

```
2025-01-13T12:00:00Z  INFO runtime::init::dataset: Dataset orders initializing...
2025-01-13T12:00:00Z  INFO runtime::init::dataset: Dataset orders registered (postgres:orders), acceleration (duckdb:file, changes).
2025-01-13T12:00:00Z  INFO data_components::postgres_replication::slot: Created new replication slot slot=spice_orders publication=spice_orders_pub consistent_lsn=0/1A2B3C48 snapshot=0/1A2B3C48
2025-01-13T12:00:00Z  INFO data_components::postgres_replication::bootstrap: initial snapshot bootstrap complete dataset=orders rows=3 expected=Some(3)
2025-01-13T12:00:00Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

---

## Step 4. Query the initial snapshot

In a new terminal, open the Spice SQL REPL:

```bash
spice sql
```

```sql
SELECT * FROM orders ORDER BY id;
```

```console
+----+-----------+--------+---------+
| id | customer  | amount | status  |
+----+-----------+--------+---------+
| 1  | Alice     | 99.99  | pending |
| 2  | Bob       | 149.50 | pending |
| 3  | Charlie   | 299.00 | shipped |
+----+-----------+--------+---------+

Time: 0.008 seconds. 3 rows.
```

---

## Step 5. Insert a record and see it stream

```bash
docker exec postgres-cdc psql -U postgres -d spice_demo -c \
  "INSERT INTO orders (customer, amount, status) VALUES ('Diana', 74.00, 'pending');"
```

Query again in the SQL REPL:

```sql
SELECT * FROM orders ORDER BY id;
```

```console
+----+-----------+--------+---------+
| id | customer  | amount | status  |
+----+-----------+--------+---------+
| 1  | Alice     | 99.99  | pending |
| 2  | Bob       | 149.50 | pending |
| 3  | Charlie   | 299.00 | shipped |
| 4  | Diana     | 74.00  | pending |
+----+-----------+--------+---------+

Time: 0.006 seconds. 4 rows.
```

---

## Step 6. Update a record and see the change

```bash
docker exec postgres-cdc psql -U postgres -d spice_demo -c \
  "UPDATE orders SET status = 'shipped' WHERE customer = 'Alice';"
```

```sql
SELECT customer, status FROM orders WHERE customer = 'Alice';
```

```console
+----------+---------+
| customer | status  |
+----------+---------+
| Alice    | shipped |
+----------+---------+

Time: 0.005 seconds. 1 rows.
```

---

## Step 7. Delete a record and see it removed

```bash
docker exec postgres-cdc psql -U postgres -d spice_demo -c \
  "DELETE FROM orders WHERE customer = 'Bob';"
```

```sql
SELECT * FROM orders ORDER BY id;
```

```console
+----+-----------+--------+---------+
| id | customer  | amount | status  |
+----+-----------+--------+---------+
| 1  | Alice     | 99.99  | shipped |
| 3  | Charlie   | 299.00 | shipped |
| 4  | Diana     | 74.00  | pending |
+----+-----------+--------+---------+

Time: 0.006 seconds. 3 rows.
```

---

## Step 8. Cleanup

```bash
docker rm -f postgres-cdc
```

Dropping the container removes the replication slot with it. If you instead point this recipe at a long-lived Postgres server, drop the slot manually so it stops retaining WAL:

```sql
SELECT pg_drop_replication_slot('spice_orders');
```

---

## Additional Resources

- [PostgreSQL Data Connector documentation](https://docs.spiceai.org/components/data-connectors/postgres)
- [PostgreSQL Data Connector cookbook](../connector/README.md)
- [MongoDB Change Streams cookbook](../../mongodb/change-streams/README.md)
