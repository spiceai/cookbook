# DynamoDB Streams Data Connector (AWS Hosted)

Works with `v2.2.0+`

This recipe demonstrates how to configure a Spice dataset to stream real-time changes from an AWS-hosted DynamoDB table using DynamoDB Streams. You'll see how inserts, updates, and deletes automatically flow into Spice.

## Prerequisites

- An AWS account
- AWS CLI installed ([installation guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html))
- IAM user or role with DynamoDB permissions: `dynamodb:ListTables`, `dynamodb:DescribeTable`, `dynamodb:Scan`, `dynamodb:GetItem`, `dynamodb:Query`, `dynamodb:DescribeStream`, `dynamodb:GetShardIterator`, and `dynamodb:GetRecords`
- Spice.ai runtime ([Getting Started](https://docs.spiceai.org/getting-started))

---

## Step 1. Clone this cookbook repo locally

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/dynamodb/streams
```

## Step 2. Define AWS_REGION

```bash
export AWS_REGION=<your-region>
```

## Step 3. Create a DynamoDB Table with Streams Enabled and Insert a Record

Create a simple table with DynamoDB Streams enabled to capture all changes:

```bash
aws dynamodb create-table \
  --table-name orders \
  --attribute-definitions AttributeName=id,AttributeType=S \
  --key-schema AttributeName=id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --stream-specification StreamEnabled=true,StreamViewType=NEW_AND_OLD_IMAGES \
  --region $AWS_REGION

aws dynamodb put-item --table-name orders --item \
  '{"id": {"S": "order-001"}, "customer": {"S": "Alice"}, "amount": {"N": "99.99"}, "status": {"S": "pending"}}' \
  --region $AWS_REGION
```

---

## Step 4. Configure Spice to Use DynamoDB Credentials

Update the `.env` file with your AWS credentials:

```env
SPICE_DYNAMODB_KEY=<aws_access_key_id>
SPICE_DYNAMODB_SECRET=<aws_secret_access_key>
```

---

## Step 5. Start the Spice Runtime and Watch Table Bootstrapping

```bash
spice run
```

You should see the dataset initialize and begin streaming:

```bash
INFO runtime::init::dataset: Dataset orders_stream registered (dynamodb:orders), acceleration (duckdb:file, changes), results cache enabled.
INFO connector_dynamodb::connector: No existing checkpoint found for DynamoDB Streams table, starting initialization. Table will be marked as Ready once lag threshold is reached dataset=orders_stream ready_lag=1h
INFO runtime: All components are loaded. Spice runtime is ready!
```

---

## Step 6. Query the Streamed Record

In the Spice SQL REPL (run `spice sql` in another terminal), query the table:

```sql
SELECT * FROM orders_stream;
```

You should see the new record:

```console
+-----------+----------+--------+---------+
| id        | customer | amount | status  |
+-----------+----------+--------+---------+
| order-001 | Alice    | 99.99  | pending |
+-----------+----------+--------+---------+
```

---

## Step 7. Insert Another Record and See the Change

Insert a second order — it will stream into the table:

```bash
aws dynamodb put-item --table-name orders --item \
  '{"id": {"S": "order-002"}, "customer": {"S": "Bob"}, "amount": {"N": "149.99"}, "status": {"S": "pending"}}' \
  --region $AWS_REGION
```

Query again in the SQL REPL:

```sql
SELECT * FROM orders_stream;
```

The new record should now appear:

```console
+-----------+----------+---------+---------+
| id        | customer | amount  | status  |
+-----------+----------+---------+---------+
| order-001 | Alice    | 99.99   | pending |
| order-002 | Bob      | 149.99  | pending |
+-----------+----------+---------+---------+
```

---

## Step 8. Cleanup

To delete the DynamoDB table:

```bash
aws dynamodb delete-table --table-name orders --region $AWS_REGION
```

---

## Additional Resources

For more information, see the [DynamoDB Streams documentation](https://spiceai.org/docs/components/data-connectors/dynamodb#streams).
