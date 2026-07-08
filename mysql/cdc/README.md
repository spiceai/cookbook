# MySQL CDC (Binlog Replication)

Works with `v2.2.0+`

This recipe demonstrates how to stream real-time changes from a MySQL table into Spice using native Change Data Capture (CDC) over the MySQL [binary log](https://dev.mysql.com/doc/refman/8.0/en/binary-log.html). Inserts, updates, and deletes propagate automatically to the Spice accelerator — no Debezium or Kafka required.

Spice reads the binlog directly and applies row-level changes by primary key. The current binlog file and position are checkpointed in a client-side sidecar table so streaming resumes from where it left off after a restart.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) is installed
- Spice is installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation)

> **Note:** MySQL CDC requires the server to be running with row-based binary logging enabled (`log_bin=ON`, `binlog_format=ROW`, `binlog_row_image=FULL`). MySQL 8.0+ enables `log_bin` and `binlog_format=ROW` by default; this recipe passes the flags explicitly so the requirement is clear. GTID-based positioning is not required.

---

## Step 1. Start MySQL with binary logging enabled

```bash
docker run -d --name mysql-cdc \
  -e MYSQL_ROOT_PASSWORD=spice \
  -e MYSQL_DATABASE=spice_demo \
  -p 3308:3306 \
  mysql:8.0 \
  --server-id=1 \
  --log-bin=mysql-bin \
  --binlog-format=ROW \
  --binlog-row-image=FULL
```

Wait a few seconds for MySQL to finish initializing, then confirm binary logging is active (`log_bin` should be `ON` and `binlog_format` should be `ROW`):

```bash
docker exec mysql-cdc mysql -uroot -pspice \
  -e "SHOW VARIABLES WHERE Variable_name IN ('log_bin','binlog_format','binlog_row_image');"
```

```console
+-------------------+-------+
| Variable_name     | Value |
+-------------------+-------+
| binlog_format     | ROW   |
| binlog_row_image  | FULL  |
| log_bin           | ON    |
+-------------------+-------+
```

---

## Step 2. Create a replication user and seed the table

Spice connects with a user that can read the binlog. The minimum privileges are `REPLICATION SLAVE`, `REPLICATION CLIENT`, and `SELECT`.

```bash
docker exec -i mysql-cdc mysql -uroot -pspice <<'EOF'
CREATE USER 'spice'@'%' IDENTIFIED BY 'spice';
GRANT REPLICATION SLAVE, REPLICATION CLIENT, SELECT ON *.* TO 'spice'@'%';
FLUSH PRIVILEGES;

USE spice_demo;
CREATE TABLE orders (
  id       BIGINT AUTO_INCREMENT PRIMARY KEY,
  customer VARCHAR(255),
  amount   DECIMAL(10,2),
  status   VARCHAR(32)
);
INSERT INTO orders (customer, amount, status) VALUES
  ('Alice',   99.99,  'pending'),
  ('Bob',     149.50, 'pending'),
  ('Charlie', 299.00, 'shipped');
SELECT CONCAT('Seeded ', COUNT(*), ' orders') AS result FROM orders;
EOF
```

---

## Step 3. Start the Spice runtime

```bash
spice run
```

You should see the dataset bootstrap from a consistent snapshot and then transition to live binlog streaming:

```
2025-01-13T12:00:00Z  INFO runtime::init::dataset: Initializing dataset orders
2025-01-13T12:00:00Z  INFO runtime::init::dataset: Dataset orders registered (mysql:spice_demo.orders), acceleration (duckdb:file, changes).
2025-01-13T12:00:00Z  INFO runtime::dataconnector::mysql: Bootstrapping MySQL table orders, records=3
2025-01-13T12:00:00Z  INFO runtime::dataconnector::mysql: Bootstrap complete for orders. Streaming binlog changes.
2025-01-13T12:00:00Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

---

## Step 4. Query the initial snapshot

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

## Step 5. Insert a record and see it stream

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

## Step 6. Update a record and see the change

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

## Step 7. Delete a record and see it removed

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

## Step 8. Cleanup

```bash
docker rm -f mysql-cdc
```

---

## Additional Resources

- [MySQL Data Connector documentation](https://docs.spiceai.org/components/data-connectors/mysql)
- [MySQL Data Connector cookbook](../connector/README.md)
- [MongoDB Change Streams cookbook](../../mongodb/change-streams/README.md)
