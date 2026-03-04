# ScyllaDB Data Connector

This recipe demonstrates how to configure a Spice dataset to connect to a ScyllaDB cluster and query data using federated SQL queries.

## Prerequisites

- A ScyllaDB cluster (self-hosted or ScyllaDB Cloud)
- ScyllaDB CQL native transport accessible (default port 9042)
- User credentials with read access to the target keyspace/tables
- Spice.ai runtime ([Getting Started](https://docs.spiceai.org/getting-started))

---

## Step 1. Clone this cookbook repo locally

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/scylladb
```

---

## Step 2. Set Up a ScyllaDB Cluster (Optional)

If you don't have an existing ScyllaDB cluster, you can start one locally using Docker:

```bash
docker rm -f scylladb >/dev/null 2>&1 || true
docker run --name scylladb -d \
  -p 9042:9042 \
  scylladb/scylla:latest \
  --smp 1 --memory 750M
```

Wait for ScyllaDB to be ready (about 30 seconds):

```bash
until docker exec scylladb nodetool status >/dev/null 2>&1; do sleep 5; done
docker exec scylladb nodetool status
```

---

## Step 3. Create a Keyspace and Table with Sample Data

Connect to the ScyllaDB CQL shell:

```bash
docker exec -it scylladb cqlsh
```

Create a keyspace and table with sample data:

```sql
-- Create keyspace
CREATE KEYSPACE IF NOT EXISTS demo
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

-- Use the keyspace
USE demo;

-- Create a sample users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    name TEXT,
    email TEXT,
    age INT,
    created_at TIMESTAMP
);

-- Insert sample data
INSERT INTO users (id, name, email, age, created_at)
VALUES (uuid(), 'Alice Smith', 'alice@example.com', 30, toTimestamp(now()));

INSERT INTO users (id, name, email, age, created_at)
VALUES (uuid(), 'Bob Johnson', 'bob@example.com', 25, toTimestamp(now()));

INSERT INTO users (id, name, email, age, created_at)
VALUES (uuid(), 'Charlie Brown', 'charlie@example.com', 35, toTimestamp(now()));

-- Verify data
SELECT * FROM users;
```

Exit the CQL shell:

```sql
EXIT;
```

---

## Step 4. Configure Spice Credentials (Optional)

If your ScyllaDB cluster requires authentication, update the `.env` file:

```env
SCYLLADB_USER=<your_username>
SCYLLADB_PASS=<your_password>
```

---

## Step 5. Start the Spice Runtime

```bash
spice run
```

If the configuration is correct, you should see output similar to:

The runtime should start and register the `users` dataset.

---

## Step 6. Query the ScyllaDB Table with the Spice SQL REPL

```bash
spice sql
```

To show tables:

```sql
SHOW TABLES;
```

To query your sample data:

```sql
SELECT name, email, age FROM users ORDER BY name;
```

Sample output:

```console
+---------------+---------------------+-----+
| name          | email               | age |
+---------------+---------------------+-----+
| Alice Smith   | alice@example.com   | 30  |
| Bob Johnson   | bob@example.com     | 25  |
| Charlie Brown | charlie@example.com | 35  |
+---------------+---------------------+-----+
```

---

## Using Acceleration for Better Performance

Since ScyllaDB queries fetch all data for processing (filter pushdown is not supported), enabling acceleration is recommended for frequently queried tables:

```yaml
datasets:
  - from: scylladb:users
    name: users
    params:
      scylladb_host: localhost
      scylladb_keyspace: demo
    acceleration:
      enabled: true
      engine: duckdb
      refresh_check_interval: 1h
```

---

## Configuration Options

### Connection Parameters

| Parameter             | Description                                                        | Required | Default |
| --------------------- | ------------------------------------------------------------------ | -------- | ------- |
| `scylladb_host`       | Hostname(s) of ScyllaDB nodes. Comma-separated for multiple nodes. | Yes      | -       |
| `scylladb_hosts`      | Alternative to `scylladb_host`. Comma-separated list of hostnames. | No       | -       |
| `scylladb_port`       | ScyllaDB CQL native transport port.                                | No       | `9042`  |
| `scylladb_keyspace`   | The keyspace to use for queries.                                   | Yes      | -       |
| `scylladb_user`       | Username for authentication.                                       | No       | -       |
| `scylladb_pass`       | Password for authentication.                                       | No       | -       |
| `scylladb_datacenter` | Preferred datacenter for connection routing.                       | No       | -       |
| `scylladb_ssl`        | Enable SSL/TLS for connections.                                    | No       | `false` |
| `connection_timeout`  | Connection timeout in milliseconds.                                | No       | `10000` |

### Multi-Node Cluster Example

```yaml
datasets:
  - from: scylladb:events
    name: events
    params:
      scylladb_hosts: node1.scylla.local,node2.scylla.local,node3.scylla.local
      scylladb_keyspace: analytics
      scylladb_datacenter: us-west-2
```

---

## Supported CQL Types

| CQL Type    | Arrow Type          | Notes                                 |
| ----------- | ------------------- | ------------------------------------- |
| `boolean`   | `Boolean`           |                                       |
| `tinyint`   | `Int8`              |                                       |
| `smallint`  | `Int16`             |                                       |
| `int`       | `Int32`             |                                       |
| `bigint`    | `Int64`             |                                       |
| `counter`   | `Int64`             | Cassandra counter type                |
| `float`     | `Float32`           |                                       |
| `double`    | `Float64`           |                                       |
| `decimal`   | `Decimal128(38, 2)` | Arbitrary precision → fixed precision |
| `blob`      | `Binary`            |                                       |
| `date`      | `Date32`            | Days since epoch                      |
| `text`      | `Utf8`              |                                       |
| `varchar`   | `Utf8`              |                                       |
| `uuid`      | `Utf8`              |                                       |
| `timeuuid`  | `Utf8`              |                                       |
| `timestamp` | `Timestamp`         |                                       |

---

## Limitations

### CQL Limitations

The following SQL operations cannot be pushed down to ScyllaDB and are performed locally:

- **JOINs**: All joins are performed locally by DataFusion
- **Aggregations**: COUNT, SUM, AVG, etc. are computed locally
- **Subqueries**: Nested queries are not supported in CQL
- **Window functions**: RANK, ROW_NUMBER, etc. not supported
- **Complex WHERE clauses**: CQL requires partition key in WHERE; Spice fetches all data
- **ORDER BY**: Sorting is done locally

### Connector Limitations

- **Read-only**: The connector does not support INSERT, UPDATE, or DELETE operations
- **Decimal precision**: Fixed at precision=38, scale=2; may not suit all use cases
- **Collection types**: Lists, sets, and maps are converted to JSON string representation
- **Large tables**: Without acceleration, large tables cause significant data transfer

---

## Step 7. Cleanup

First stop the running Spice runtime (in the terminal where `spice run` is active) with `Ctrl+C`.

Then stop and remove the ScyllaDB container:

```bash
docker stop scylladb
docker rm scylladb
```

---

## Additional Resources

- [ScyllaDB Data Connector Documentation](https://docs.spiceai.org/components/data-connectors/scylladb)
- [ScyllaDB Official Documentation](https://docs.scylladb.com/)
- [Data Acceleration](https://docs.spiceai.org/features/data-acceleration)
