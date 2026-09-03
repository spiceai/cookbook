# ScyllaDB Data Connector

Works with `v1.11+`

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
docker run --name scylladb -d \
  -p 9042:9042 \
  scylladb/scylla:latest \
  --smp 1 --memory 750M
```

Wait for ScyllaDB to be ready (about 30 seconds):

```bash
docker exec -it scylladb nodetool status
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
WITH replication = {'class': 'NetworkTopologyStrategy', 'replication_factor': 1};

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

```console
INFO runtime::init::dataset: Dataset users initializing...
INFO runtime::init::dataset: Dataset users registered (scylladb:users), acceleration (none), results cache enabled.
```

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
SELECT * FROM users;
```

Sample output:

```console
+--------------------------------------+---------------+---------------------+-----+-------------------------+
| id                                   | name          | email               | age | created_at              |
+--------------------------------------+---------------+---------------------+-----+-------------------------+
| a1b2c3d4-e5f6-7890-abcd-ef1234567890 | Alice Smith   | alice@example.com   | 30  | 2025-01-19T12:00:00.000 |
| b2c3d4e5-f6a7-8901-bcde-f12345678901 | Bob Johnson   | bob@example.com     | 25  | 2025-01-19T12:00:01.000 |
| c3d4e5f6-a7b8-9012-cdef-123456789012 | Charlie Brown | charlie@example.com | 35  | 2025-01-19T12:00:02.000 |
+--------------------------------------+---------------+---------------------+-----+-------------------------+
```

---

## Using Acceleration for Better Performance

ScyllaDB can push down partition-key equality filters (and clustering-key comparisons when a partition-key filter is also present). Unaccelerated queries remain subject to ScyllaDB's CQL restrictions, so enable acceleration when you need unrestricted SQL filtering or sorting:

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
- **WHERE clauses without a partition key**: Unsupported predicates are normally evaluated locally, but pushdown behavior depends on the complete query
- **UUID partition-key predicates in v2.2**: A predicate such as `WHERE id = '<uuid>'` can be sent to CQL as a string literal and rejected as an invalid UUID constant; use acceleration or another predicate until the runtime issue is fixed
- **ORDER BY**: Unaccelerated queries are subject to ScyllaDB's rule that the partition key must be restricted by `EQ` or `IN`; enable acceleration for unrestricted sorting

### Connector Limitations

- **Read-only**: The connector does not support INSERT, UPDATE, or DELETE operations
- **Decimal precision**: Fixed at precision=38, scale=2; may not suit all use cases
- **Collection types**: Lists, sets, and maps are converted to JSON string representation
- **Large tables**: Without acceleration, large tables cause significant data transfer

---

## Step 7. Cleanup

To stop and remove the ScyllaDB container:

```bash
docker stop scylladb
docker rm scylladb
```

---

## Additional Resources

- [ScyllaDB Data Connector Documentation](https://docs.spiceai.org/components/data-connectors/scylladb)
- [ScyllaDB Official Documentation](https://docs.scylladb.com/)
- [Data Acceleration](https://docs.spiceai.org/features/data-acceleration)
