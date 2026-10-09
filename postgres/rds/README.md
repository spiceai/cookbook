# AWS RDS for PostgreSQL

Works with `v1.0+`

Follow these steps to get started with federated SQL query against an AWS-hosted **Amazon RDS for PostgreSQL** instance, with the queried table locally accelerated using a periodic full-refresh (`refresh_mode: full`).

## Prerequisites

- An AWS account
- AWS CLI installed ([installation guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html))
- [`jq`](https://jqlang.org/download/) installed (used to parse the Secrets Manager response below)
- IAM permissions to create/delete CloudFormation stacks, the underlying VPC/RDS/EC2 security group resources, and to read the instance's generated Secrets Manager secret (`secretsmanager:GetSecretValue`)
- [Docker](https://docs.docker.com/get-docker/) is installed (used to run a `psql` client against the instance, so no local PostgreSQL client is needed)
- Spice is installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation)

> **Cost note:** this recipe provisions a real `db.t4g.micro` RDS instance, which is billed by AWS. Remember to complete the cleanup step when you're done.

---

## Step 1. Clone this cookbook repo locally

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/postgres/rds
```

## Step 2. Define AWS_REGION

```bash
export AWS_REGION=<your-region>
```

---

## Step 3. Deploy an RDS for PostgreSQL instance

The included CloudFormation template provisions a VPC, a publicly-reachable RDS for PostgreSQL instance, and its security group. The master password is not a template parameter — the instance is created with `ManageMasterUserPassword: true`, so RDS generates it and stores it in AWS Secrets Manager rather than it ever being typed, hardcoded, or read from a console.

```bash
aws cloudformation create-stack \
  --stack-name rds-postgres-cookbook \
  --template-body file://rds-postgres.yaml \
  --region $AWS_REGION
```

By default the security group admits PostgreSQL connections from any address. To admit only your own, add `--parameters ParameterKey=AllowedCIDR,ParameterValue=<your-public-ip>/32` to the command above. On a network that sends traffic out through more than one public IP, connections from the other addresses time out.

Wait for the instance to finish provisioning (this typically takes about 5 minutes):

```bash
aws cloudformation wait stack-create-complete \
  --stack-name rds-postgres-cookbook \
  --region $AWS_REGION
```

## Step 4. Fetch the endpoint and master credentials

```bash
export RDS_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name rds-postgres-cookbook \
  --region $AWS_REGION \
  --query "Stacks[0].Outputs[?OutputKey=='Endpoint'].OutputValue" \
  --output text)

echo $RDS_ENDPOINT
```

Retrieve the generated master password from Secrets Manager:

```bash
export RDS_SECRET_ARN=$(aws cloudformation describe-stacks \
  --stack-name rds-postgres-cookbook \
  --region $AWS_REGION \
  --query "Stacks[0].Outputs[?OutputKey=='MasterUserSecretArn'].OutputValue" \
  --output text)

export PG_PASS=$(aws secretsmanager get-secret-value \
  --secret-id $RDS_SECRET_ARN \
  --region $AWS_REGION \
  --query 'SecretString' --output text | jq -r '.password')
```

The master username is `postgres` and the database is `testdb` (the `MasterUsername` and `DatabaseName` template parameters).

---

## Step 5. Create a demo table and seed it

```bash
docker run --rm -i -e PGPASSWORD=$PG_PASS postgres:18-alpine \
  psql -h $RDS_ENDPOINT -U postgres -d testdb <<'EOF'
CREATE TABLE customers (
  id    BIGSERIAL PRIMARY KEY,
  name  TEXT,
  email TEXT,
  tier  TEXT
);
INSERT INTO customers (name, email, tier) VALUES
  ('Alice',   'alice@example.com',   'gold'),
  ('Bob',     'bob@example.com',     'silver'),
  ('Charlie', 'charlie@example.com', 'silver');
SELECT 'Seeded ' || COUNT(*) || ' customers' AS result FROM customers;
EOF
```

```console
CREATE TABLE
INSERT 0 3
       result
--------------------
 Seeded 3 customers
(1 row)
```

---

## Step 6. Configure Spice with the RDS connection details

Write the endpoint and password to a `.env` file in this directory. The password is single-quoted so it is read literally; RDS master passwords never contain `'`.

```bash
printf "RDS_ENDPOINT=%s\nPG_PASS='%s'\n" "$RDS_ENDPOINT" "$PG_PASS" > .env
```

The `spicepod.yaml` connects with `pg_sslmode: require`, which encrypts the connection without verifying the server certificate.

See the [datasets reference](https://docs.spiceai.org/reference/spicepod/datasets) for more dataset configuration options, the [PostgreSQL Data Connector](https://docs.spiceai.org/components/data-connectors/postgres) docs for connector params, and [Secret Stores](https://docs.spiceai.org/components/secret-stores) for alternatives to a local `.env` file.

## Step 7. Start the Spice runtime

```bash
spice run
```

You should see the dataset load and the accelerator perform its first full refresh:

```console
2026-10-09T01:51:05.396717Z  INFO runtime::init::dataset: Dataset customers initializing...
2026-10-09T01:51:06.007501Z  INFO runtime::init::dataset: Dataset customers registered (postgres:public.customers), acceleration (cayenne, 10s refresh), results cache enabled. duration_ms=125
2026-10-09T01:51:06.007752Z  INFO runtime_table::accelerated::refresh_task: Loading data for dataset customers
2026-10-09T01:51:06.044864Z  INFO runtime_table::accelerated::refresh_task: Loaded 3 rows (154.00 B) for dataset customers in 37ms.
2026-10-09T01:51:06.109989Z  INFO runtime: All components are loaded. Spice runtime is ready!
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
+-------+---------+---------------------+---------+
|   id  |   name  |        email        |   tier  |
| int64 | varchar |       varchar       | varchar |
+-------+---------+---------------------+---------+
| 1     | Alice   | alice@example.com   | gold    |
| 2     | Bob     | bob@example.com     | silver  |
| 3     | Charlie | charlie@example.com | silver  |
+-------+---------+---------------------+---------+

Time: 0.005426416 seconds. 3 rows.
```

---

## Step 9. Insert a record on RDS and see it appear on the next refresh

In the terminal where `RDS_ENDPOINT` and `PG_PASS` are set:

```bash
docker run --rm -e PGPASSWORD=$PG_PASS postgres:18-alpine \
  psql -h $RDS_ENDPOINT -U postgres -d testdb -c \
  "INSERT INTO customers (name, email, tier) VALUES ('Diana', 'diana@example.com', 'gold');"
```

`refresh_check_interval` is set to `10s`, so wait a few seconds and query again in the SQL REPL:

```sql
SELECT * FROM customers;
```

```console
+-------+---------+---------------------+---------+
|   id  |   name  |        email        |   tier  |
| int64 | varchar |       varchar       | varchar |
+-------+---------+---------------------+---------+
| 1     | Alice   | alice@example.com   | gold    |
| 2     | Bob     | bob@example.com     | silver  |
| 3     | Charlie | charlie@example.com | silver  |
| 4     | Diana   | diana@example.com   | gold    |
+-------+---------+---------------------+---------+

Time: 0.003633125 seconds. 4 rows.
```

---

## Step 10. Cleanup

Tear down the RDS instance and all associated resources:

```bash
aws cloudformation delete-stack --stack-name rds-postgres-cookbook --region $AWS_REGION
aws cloudformation wait stack-delete-complete --stack-name rds-postgres-cookbook --region $AWS_REGION
```

---

## Additional Resources

- [PostgreSQL Data Connector documentation](https://docs.spiceai.org/components/data-connectors/postgres)
- [Datasets reference](https://docs.spiceai.org/reference/spicepod/datasets)
- [Secret Stores](https://docs.spiceai.org/components/secret-stores)
- [AWS Secrets Manager Secret Store](https://spiceai.org/docs/components/secret-stores/aws-secrets-manager)
