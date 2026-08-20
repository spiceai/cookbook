# AWS RDS Aurora (MySQL Data Connector)

Works with `v1.0+`

This recipe demonstrates federated SQL query against an AWS-hosted **Amazon Aurora MySQL-Compatible** cluster, with the queried table locally accelerated using a periodic full-refresh (`refresh_mode: full`). Spice queries the cluster's **reader endpoint**, matching how a read-heavy application would talk to Aurora.

> Looking for real-time change propagation instead of periodic full refreshes? See the [Aurora MySQL CDC cookbook](../rds-aurora-cdc/README.md), which streams inserts/updates/deletes over the binlog.

## Prerequisites

- An AWS account
- AWS CLI installed ([installation guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html))
- [`jq`](https://jqlang.org/download/) installed (used to parse the Secrets Manager response below)
- IAM permissions to create/delete CloudFormation stacks, the underlying VPC/RDS/EC2 security group resources, and to read the cluster's generated Secrets Manager secret (`secretsmanager:GetSecretValue`)
- [Docker](https://docs.docker.com/get-docker/) is installed (used to run a `mysql` client against the cluster — see note below)
- Spice is installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation)

> **Why Docker for the `mysql` client?** Aurora MySQL's master user authenticates with the `mysql_native_password` plugin by default. Recent MySQL client builds (9.x, including current Homebrew formulas) dropped that plugin and fail with `Authentication plugin 'mysql_native_password' cannot be loaded`. Running the client via the `mysql:8.0` image sidesteps whatever client version happens to be installed locally.

> **Cost note:** this recipe provisions a real `db.t3.medium` Aurora instance, which is billed by AWS. Remember to complete the cleanup step when you're done.

---

## Step 1. Clone this cookbook repo locally

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/mysql/rds-aurora
```

## Step 2. Define AWS_REGION

```bash
export AWS_REGION=<your-region>
```

---

## Step 3. Deploy an Aurora MySQL cluster

The included CloudFormation template provisions a VPC, a publicly-reachable Aurora MySQL cluster, and its security group. The master password is not a template parameter — the cluster is created with `ManageMasterUserPassword: true`, so Aurora generates it and stores it in AWS Secrets Manager rather than it ever being typed, hardcoded, or read from a console.

```bash
aws cloudformation create-stack \
  --stack-name aurora-cookbook \
  --template-body file://aurora-test-cluster.yaml \
  --region $AWS_REGION
```

Wait for the cluster to finish provisioning (this typically takes 10-15 minutes):

```bash
aws cloudformation wait stack-create-complete \
  --stack-name aurora-cookbook \
  --region $AWS_REGION
```

## Step 4. Fetch the endpoints and master credentials

```bash
export AURORA_WRITER_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name aurora-cookbook \
  --region $AWS_REGION \
  --query "Stacks[0].Outputs[?OutputKey=='WriterEndpoint'].OutputValue" \
  --output text)

export AURORA_READER_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name aurora-cookbook \
  --region $AWS_REGION \
  --query "Stacks[0].Outputs[?OutputKey=='ReaderEndpoint'].OutputValue" \
  --output text)

echo $AURORA_WRITER_ENDPOINT
echo $AURORA_READER_ENDPOINT
```

Retrieve the generated master password from Secrets Manager:

```bash
export AURORA_SECRET_ARN=$(aws cloudformation describe-stacks \
  --stack-name aurora-cookbook \
  --region $AWS_REGION \
  --query "Stacks[0].Outputs[?OutputKey=='MasterUserSecretArn'].OutputValue" \
  --output text)

export MYSQL_PASS=$(aws secretsmanager get-secret-value \
  --secret-id $AURORA_SECRET_ARN \
  --region $AWS_REGION \
  --query 'SecretString' --output text | jq -r '.password')
```

The master username is `admin` (the `MasterUsername` template parameter — change it for anything beyond local testing).

---

## Step 5. Create a demo table and seed it

Writes must go through the **writer endpoint** — the reader endpoint is read-only.

```bash
docker run --rm -i -e MYSQL_PWD=$MYSQL_PASS mysql:8.0 mysql -h $AURORA_WRITER_ENDPOINT -u admin <<'EOF'
CREATE TABLE testdb.customers (
  id    BIGINT AUTO_INCREMENT PRIMARY KEY,
  name  VARCHAR(255),
  email VARCHAR(255),
  tier  VARCHAR(32)
);
INSERT INTO testdb.customers (name, email, tier) VALUES
  ('Alice',   'alice@example.com',   'gold'),
  ('Bob',     'bob@example.com',     'silver'),
  ('Charlie', 'charlie@example.com', 'silver');
SELECT CONCAT('Seeded ', COUNT(*), ' customers') AS result FROM testdb.customers;
EOF
```

---

## Step 6. Configure Spice with the Aurora connection details

```bash
echo "AURORA_READER_ENDPOINT=$AURORA_READER_ENDPOINT
MYSQL_PASS=$MYSQL_PASS" > .env
```

See the [datasets reference](https://docs.spiceai.org/reference/spicepod/datasets) for more dataset configuration options, the [MySQL Data Connector](https://docs.spiceai.org/components/data-connectors/mysql) docs for connector params, and [Secret Stores](https://docs.spiceai.org/components/secret-stores) for alternatives to a local `.env` file.

## Step 7. Start the Spice runtime

```bash
spice run
```

You should see the dataset load and the accelerator perform its first full refresh:

```
2025-01-13T12:00:00Z  INFO runtime::init::dataset: Initializing dataset customers
2025-01-13T12:00:00Z  INFO runtime::init::dataset: Dataset customers registered (mysql:testdb.customers), acceleration (arrow, full).
2025-01-13T12:00:00Z  INFO runtime::accelerated_table::refresh_task: Refreshing dataset customers
2025-01-13T12:00:00Z  INFO runtime::accelerated_table::refresh_task: Loaded 3 rows for dataset customers
2025-01-13T12:00:00Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

---

## Step 8. Query the accelerated table

In a new terminal, open the Spice SQL REPL:

```bash
spice sql
```

```sql
SELECT * FROM customers;
```

```console
+----+-----------+-----------------------+--------+
| id | name      | email                 | tier   |
+----+-----------+-----------------------+--------+
| 1  | Alice     | alice@example.com     | gold   |
| 2  | Bob       | bob@example.com       | silver |
| 3  | Charlie   | charlie@example.com   | silver |
+----+-----------+-----------------------+--------+

Time: 0.008 seconds. 3 rows.
```

---

## Step 9. Insert a record on Aurora and see it appear on the next refresh

```bash
docker run --rm -e MYSQL_PWD=$MYSQL_PASS mysql:8.0 mysql -h $AURORA_WRITER_ENDPOINT -u admin -e \
  "INSERT INTO testdb.customers (name, email, tier) VALUES ('Diana', 'diana@example.com', 'gold');"
```

`refresh_check_interval` is set to `10s`, so wait a few seconds and query again in the SQL REPL:

```sql
SELECT * FROM customers;
```

```console
+----+-----------+-----------------------+--------+
| id | name      | email                 | tier   |
+----+-----------+-----------------------+--------+
| 1  | Alice     | alice@example.com     | gold   |
| 2  | Bob       | bob@example.com       | silver |
| 3  | Charlie   | charlie@example.com   | silver |
| 4  | Diana     | diana@example.com     | gold   |
+----+-----------+-----------------------+--------+

Time: 0.006 seconds. 4 rows.
```

---

## Step 10. Cleanup

Tear down the Aurora cluster and all associated resources:

```bash
aws cloudformation delete-stack --stack-name aurora-cookbook --region $AWS_REGION
aws cloudformation wait stack-delete-complete --stack-name aurora-cookbook --region $AWS_REGION
```

---

## Additional Resources

- [MySQL Data Connector documentation](https://docs.spiceai.org/components/data-connectors/mysql)
- [Datasets reference](https://docs.spiceai.org/reference/spicepod/datasets)
- [Secret Stores](https://docs.spiceai.org/components/secret-stores)
- [Aurora MySQL CDC (binlog replication) cookbook](../rds-aurora-cdc/README.md)
