# MySQL CDC (Binlog Replication)

Works with `v2.2.0+`

This recipe demonstrates how to stream real-time changes from a MySQL table into Spice using native Change Data Capture (CDC) over the MySQL [binary log](https://dev.mysql.com/doc/refman/8.0/en/binary-log.html). Inserts, updates, and deletes propagate automatically to the Spice accelerator — no Debezium or Kafka required.

Spice reads the binlog directly and applies row-level changes by primary key. The resume position is checkpointed in a client-side sidecar table so streaming resumes from where it left off after a restart. When the source runs with `gtid_mode = ON`, Spice automatically positions the stream by [GTID](https://dev.mysql.com/doc/refman/8.0/en/replication-gtids-concepts.html) — a globally unique transaction identity that survives a source failover — so a managed-MySQL promotion or switchover resumes losslessly instead of forcing a full re-snapshot.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) is installed
- Spice is installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation)

> **Note:** MySQL CDC requires row-based binary logging (`log_bin=ON`, `binlog_format=ROW`, `binlog_row_image=FULL`), all defaults on MySQL 8.0+. This recipe also sets `gtid_mode=ON` for failover-safe GTID positioning — automatic, no spicepod config.

---

## Step 1. Start MySQL

`docker compose up -d` starts MySQL with binary logging enabled and, on first startup, runs [`init/init.sql`](./init/init.sql) to create the replication user Spice connects with and seed the `orders` table.

```bash
docker compose up -d
```

The Compose service enables row-based binary logging and GTIDs via server flags, and `init.sql` grants the `spice` user the minimum privileges to read the binlog (`REPLICATION SLAVE`, `REPLICATION CLIENT`, `SELECT`).

Wait for the container to become healthy (`docker compose ps` shows `healthy`), then confirm binary logging and GTIDs are active (`log_bin` should be `ON`, `binlog_format` should be `ROW`, and `gtid_mode` should be `ON`):

```bash
docker exec mysql-cdc mysql -uroot -pspice --table \
  -e "SHOW VARIABLES WHERE Variable_name IN ('log_bin','binlog_format','binlog_row_image','gtid_mode');"
```

```console
+------------------+-------+
| Variable_name    | Value |
+------------------+-------+
| binlog_format    | ROW   |
| binlog_row_image | FULL  |
| gtid_mode        | ON    |
| log_bin          | ON    |
+------------------+-------+
```

---

## Step 2. Start the Spice runtime

```bash
spice run
```

You should see the dataset bootstrap from a consistent snapshot and then transition to live binlog streaming:

```
2026-07-23T01:40:37.317523Z  INFO runtime::init::dataset: Dataset orders initializing...
2026-07-23T01:40:37.392667Z  INFO runtime::init::dataset: Dataset orders registered (mysql:spice_demo.orders), acceleration (duckdb:file, changes), results cache enabled. duration_ms=5
2026-07-23T01:40:37.396202Z  INFO data_components::mysql_replication::shared: MySQL replication: GTID auto-positioning active. dataset=orders source_table=spice_demo.orders
2026-07-23T01:40:37.397269Z  INFO data_components::mysql_replication::shared: dataset joined shared mysql binlog group dataset=orders connection=localhost:3308 snapshot=true rejoining=false members=1
2026-07-23T01:40:37.397719Z  INFO data_components::mysql_replication::bootstrap: mysql replication: starting initial snapshot dataset=orders
2026-07-23T01:40:37.397936Z  INFO runtime_table::accelerated::refresh_task::changes: Processing TRUNCATE for orders
2026-07-23T01:40:37.404727Z  INFO data_components::mysql_replication::bootstrap: mysql replication: initial snapshot complete dataset=orders rows=3
2026-07-23T01:40:37.491325Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2026-07-23T01:40:37.492029Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2026-07-23T01:40:40.042282Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

---

## Step 3. Query the initial snapshot

In a new terminal, open the Spice SQL REPL:

```bash
spice sql
```

```sql
SELECT * FROM orders;
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

## Step 4. Insert a record and see it stream

```bash
docker exec mysql-cdc mysql -uroot -pspice -e \
  "INSERT INTO spice_demo.orders (customer, amount, status) VALUES ('Diana', 74.00, 'pending');"
```

Query again in the SQL REPL:

```sql
SELECT * FROM orders;
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

## Step 5. Update a record and see the change

```bash
docker exec mysql-cdc mysql -uroot -pspice -e \
  "UPDATE spice_demo.orders SET status = 'shipped' WHERE customer = 'Alice';"
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

## Step 6. Delete a record and see it removed

```bash
docker exec mysql-cdc mysql -uroot -pspice -e \
  "DELETE FROM spice_demo.orders WHERE customer = 'Bob';"
```

```sql
SELECT * FROM orders;
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

## Step 7. Cleanup

```bash
docker compose down -v
```

---

## Additional Resources

- [MySQL Data Connector documentation](https://docs.spiceai.org/components/data-connectors/mysql)
- [MySQL Data Connector cookbook](../connector/README.md)
