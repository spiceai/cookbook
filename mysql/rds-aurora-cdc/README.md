# Aurora MySQL CDC (Binlog Replication, AWS Hosted)

Works with `v2.2.0+`

This recipe demonstrates how to stream real-time changes from an AWS-hosted **Amazon Aurora MySQL-Compatible** cluster into Spice using native Change Data Capture (CDC) over the MySQL [binary log](https://spiceai.org/docs/next/features/cdc/mysql-replication). Inserts, updates, and deletes propagate automatically to the Spice accelerator — no Debezium or Kafka required.

Spice reads the binlog directly and applies row-level changes by primary key. The current binlog file and position are checkpointed in a client-side sidecar table so streaming resumes from where it left off after a restart.

> **Note:** Aurora only produces a binary log on the **writer** instance. Spice must connect to the cluster's **writer (cluster) endpoint**, not the reader endpoint — the reader endpoint routes to Aurora Replicas, which serve reads from shared storage and do not expose their own binlog stream.

## Prerequisites

- An AWS account
- AWS CLI installed ([installation guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html))
- IAM permissions to create/delete CloudFormation stacks and the underlying VPC, RDS, and EC2 security group resources
- [Docker](https://docs.docker.com/get-docker/) is installed (used to run a `mysql` client against the cluster — see note below)
- Spice is installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation)

> **Why Docker for the `mysql` client?** Aurora MySQL's master user authenticates with the `mysql_native_password` plugin by default. Recent MySQL client builds (9.x, including current Homebrew formulas) dropped that plugin and fail with `Authentication plugin 'mysql_native_password' cannot be loaded`. Running the client via the `mysql:8.0` image sidesteps whatever client version happens to be installed locally.

> **Cost note:** this recipe provisions a real `db.t3.medium` Aurora instance, which is billed by AWS. Remember to complete the cleanup step when you're done.

---

## Step 1. Clone this cookbook repo locally

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/mysql/rds-aurora-cdc
```

## Step 2. Define AWS_REGION

```bash
export AWS_REGION=<your-region>
```

---

## Step 3. Deploy an Aurora MySQL cluster with binlog enabled

The included CloudFormation template provisions a VPC, a publicly-reachable Aurora MySQL cluster, and a custom **DB cluster parameter group** with `binlog_format=ROW` and `binlog_row_image=FULL` — the settings binlog CDC requires. Binlog format is a cluster-level parameter on Aurora MySQL, so it must be set before the cluster starts serving traffic.

```bash
aws cloudformation create-stack \
  --stack-name aurora-cdc-cookbook \
  --template-body file://aurora-mysql-cdc-cluster.yaml \
  --region $AWS_REGION
```

Wait for the cluster to finish provisioning (this typically takes 10-15 minutes):

```bash
aws cloudformation wait stack-create-complete \
  --stack-name aurora-cdc-cookbook \
  --region $AWS_REGION
```

> Ensure your IP (or `0.0.0.0/0` for testing) is allowed by passing `--parameters ParameterKey=AllowedCIDR,ParameterValue=<your-cidr>` if you don't want the default open ingress rule.

## Step 4. Fetch the writer endpoint and master credentials

```bash
export AURORA_WRITER_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name aurora-cdc-cookbook \
  --region $AWS_REGION \
  --query "Stacks[0].Outputs[?OutputKey=='WriterEndpoint'].OutputValue" \
  --output text)

echo $AURORA_WRITER_ENDPOINT
```

The default master username is `admin` and the default master password is `TestPassword123!` (set via the `MasterUsername`/`MasterPassword` template parameters — change these for anything beyond local testing).

## Step 5. Confirm binlog is active

```bash
docker run --rm -e MYSQL_PWD=TestPassword123! mysql:8.0 mysql -h $AURORA_WRITER_ENDPOINT -u admin \
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

Aurora purges binlogs on its own retention schedule, which by default can be shorter than a standalone MySQL server's. Give Spice enough headroom to survive a restart by explicitly setting the retention window:

```bash
docker run --rm -e MYSQL_PWD=TestPassword123! mysql:8.0 mysql -h $AURORA_WRITER_ENDPOINT -u admin \
  -e "CALL mysql.rds_set_configuration('binlog retention hours', 24);"
```

---

## Step 6. Create a replication user and seed the table

Spice connects with a user that can read the binlog. The minimum privileges are `REPLICATION SLAVE`, `REPLICATION CLIENT`, and `SELECT`.

```bash
docker run --rm -i -e MYSQL_PWD=TestPassword123! mysql:8.0 mysql -h $AURORA_WRITER_ENDPOINT -u admin <<'EOF'
CREATE USER 'spice'@'%' IDENTIFIED BY 'spice';
GRANT REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'spice'@'%';
GRANT SELECT ON spicedemo.* TO 'spice'@'%';
FLUSH PRIVILEGES;

USE spicedemo;
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

## Step 7. Configure Spice with the Aurora connection details

```bash
echo "AURORA_WRITER_ENDPOINT=$AURORA_WRITER_ENDPOINT
MYSQL_PASS=spice" > .env
```

## Step 8. Start the Spice runtime

```bash
spice run
```

You should see the dataset bootstrap from a consistent snapshot and then transition to live binlog streaming:

```
2025-01-13T12:00:00Z  INFO runtime::init::dataset: Initializing dataset orders
2025-01-13T12:00:00Z  INFO runtime::init::dataset: Dataset orders registered (mysql:spicedemo.orders), acceleration (duckdb:file, changes).
2025-01-13T12:00:00Z  INFO runtime::dataconnector::mysql: Bootstrapping MySQL table orders, records=3
2025-01-13T12:00:00Z  INFO runtime::dataconnector::mysql: Bootstrap complete for orders. Streaming binlog changes.
2025-01-13T12:00:00Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

---

## Step 9. Query the initial snapshot

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

## Step 10. Insert a record and see it stream

```bash
docker run --rm -e MYSQL_PWD=TestPassword123! mysql:8.0 mysql -h $AURORA_WRITER_ENDPOINT -u admin -e \
  "INSERT INTO spicedemo.orders (customer, amount, status) VALUES ('Diana', 74.00, 'pending');"
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

## Step 11. Update a record and see the change

```bash
docker run --rm -e MYSQL_PWD=TestPassword123! mysql:8.0 mysql -h $AURORA_WRITER_ENDPOINT -u admin -e \
  "UPDATE spicedemo.orders SET status = 'shipped' WHERE customer = 'Alice';"
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

## Step 12. Delete a record and see it removed

```bash
docker run --rm -e MYSQL_PWD=TestPassword123! mysql:8.0 mysql -h $AURORA_WRITER_ENDPOINT -u admin -e \
  "DELETE FROM spicedemo.orders WHERE customer = 'Bob';"
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

## Step 13. Cleanup

Tear down the Aurora cluster and all associated resources:

```bash
aws cloudformation delete-stack --stack-name aurora-cdc-cookbook --region $AWS_REGION
aws cloudformation wait stack-delete-complete --stack-name aurora-cdc-cookbook --region $AWS_REGION
```

---

## Additional Resources

- [MySQL Data Connector documentation](https://spiceai.org/docs/next/components/data-connectors/mysql)
- [MySQL Binlog Replication documentation](https://spiceai.org/docs/next/features/cdc/mysql-replication)
- [MySQL CDC (Docker) cookbook](../cdc/README.md)
- [AWS RDS Aurora (MySQL) connector cookbook](../rds-aurora/README.md)
