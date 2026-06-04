# MongoDB Change Streams

Works with `v2.0+`

This recipe demonstrates how to stream real-time changes from a MongoDB collection into Spice using [MongoDB Change Streams](https://www.mongodb.com/docs/manual/changeStreams/). Inserts, updates, and deletes propagate automatically to the Spice accelerator — no Debezium or Kafka required.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) is installed
- Spice is installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation)

> **Note:** MongoDB Change Streams require a replica set or sharded cluster — a standalone `mongod` instance does not support them. This recipe runs a single-node replica set in Docker without authentication, which is suitable for local development.

---

## Step 1. Start a MongoDB replica set

```bash
docker run -d --name mongodb-streams \
  -p 27019:27017 \
  mongo:7.0 mongod --replSet rs0 --bind_ip_all
```

Wait a few seconds for MongoDB to start, then initiate the replica set:

```bash
docker exec mongodb-streams mongosh \
  --eval "rs.initiate({_id:'rs0',members:[{_id:0,host:'localhost:27017'}]})"
```

Confirm it became `PRIMARY` (should print `1`):

```bash
docker exec mongodb-streams mongosh --eval "rs.status().myState"
```

---

## Step 2. Seed the collection

```bash
docker exec -i mongodb-streams mongosh <<'EOF'
use spice_demo;
db.orders.insertMany([
  { customer: "Alice",   amount: 99.99,  status: "pending"   },
  { customer: "Bob",     amount: 149.50, status: "pending"   },
  { customer: "Charlie", amount: 299.00, status: "shipped"   },
]);
print("Seeded", db.orders.countDocuments(), "orders");
EOF
```

---

## Step 3. Configure the connection string

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

The default `.env` connects to the Docker instance started above:

```env
MONGODB_CONNECTION_STRING=mongodb://localhost:27019/spice_demo?directConnection=true&replicaSet=rs0&tls=false
```

---

## Step 4. Start the Spice runtime

```bash
spice run
```

You should see the dataset bootstrap and then transition to live streaming:

```
2025-01-13T12:00:00Z  INFO runtime::init::dataset: Initializing dataset orders
2025-01-13T12:00:00Z  INFO runtime::init::dataset: Dataset orders registered (mongodb:orders), acceleration (duckdb:file, changes).
2025-01-13T12:00:00Z  INFO runtime::dataconnector::mongodb: Bootstrapping MongoDB collection orders, records=3
2025-01-13T12:00:00Z  INFO runtime::dataconnector::mongodb: Bootstrap complete for orders. Streaming live changes.
2025-01-13T12:00:00Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

---

## Step 5. Query the initial snapshot

In a new terminal, open the Spice SQL REPL:

```bash
spice sql
```

```sql
SELECT * FROM orders;
```

```console
+------------------------+-----------+--------+---------+
| _id                    | customer  | amount | status  |
+------------------------+-----------+--------+---------+
| 6823a1b2c3d4e5f6a7b8c9 | Alice     | 99.99  | pending |
| 6823a1b2c3d4e5f6a7b8ca | Bob       | 149.5  | pending |
| 6823a1b2c3d4e5f6a7b8cb | Charlie   | 299.0  | shipped |
+------------------------+-----------+--------+---------+

Time: 0.008 seconds. 3 rows.
```

---

## Step 6. Insert a record and see it stream

```bash
docker exec mongodb-streams mongosh \
  --eval 'db.getSiblingDB("spice_demo").orders.insertOne({customer:"Diana",amount:74.00,status:"pending"})'
```

Query again in the SQL REPL:

```sql
SELECT * FROM orders;
```

```console
+------------------------+-----------+--------+---------+
| _id                    | customer  | amount | status  |
+------------------------+-----------+--------+---------+
| 6823a1b2c3d4e5f6a7b8c9 | Alice     | 99.99  | pending |
| 6823a1b2c3d4e5f6a7b8ca | Bob       | 149.5  | pending |
| 6823a1b2c3d4e5f6a7b8cb | Charlie   | 299.0  | shipped |
| 6823a1b2c3d4e5f6a7b8cc | Diana     | 74.0   | pending |
+------------------------+-----------+--------+---------+

Time: 0.006 seconds. 4 rows.
```

---

## Step 7. Update a record and see the change

```bash
docker exec mongodb-streams mongosh \
  --eval 'db.getSiblingDB("spice_demo").orders.updateOne({customer:"Alice"},{$set:{status:"shipped"}})'
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

## Step 8. Delete a record and see it removed

```bash
docker exec mongodb-streams mongosh \
  --eval 'db.getSiblingDB("spice_demo").orders.deleteOne({customer:"Bob"})'
```

```sql
SELECT * FROM orders;
```

```console
+------------------------+-----------+--------+---------+
| _id                    | customer  | amount | status  |
+------------------------+-----------+--------+---------+
| 6823a1b2c3d4e5f6a7b8c9 | Alice     | 99.99  | shipped |
| 6823a1b2c3d4e5f6a7b8cb | Charlie   | 299.0  | shipped |
| 6823a1b2c3d4e5f6a7b8cc | Diana     | 74.0   | pending |
+------------------------+-----------+--------+---------+

Time: 0.006 seconds. 3 rows.
```

---

## Step 9. Cleanup

```bash
docker rm -f mongodb-streams
```

---

## Additional Resources

- [MongoDB Change Streams documentation](https://docs.spiceai.org/components/data-connectors/mongodb#using-mongodb-change-streams)
- [MongoDB Data Connector cookbook](../connector/README.md)
