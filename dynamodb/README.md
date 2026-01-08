# DynamoDB Data Connector (AWS Hosted)

This recipe demonstrates how to configure a Spice dataset to connect to an AWS-hosted DynamoDB table and query data from it.

## Prerequisites

- An AWS account
- AWS CLI installed ([installation guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html))
- IAM user or role with `dynamodb:ListTables`, `dynamodb:DescribeTable`, `dynamodb:Scan`, `dynamodb:GetItem`, and `dynamodb:Query` permissions
- Spice.ai runtime ([Getting Started](https://docs.spiceai.org/getting-started))

---

## Step 1. Clone this cookbook repo locally

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/dynamodb
```

## Step 2. Define AWS_REGION
```bash
export AWS_REGION=<your-region>
```

---

## Step 3. Create a DynamoDB Table and Load Sample Data

You can create a table and load a few demo items via the AWS CLI:

```bash
aws dynamodb create-table \
  --table-name sample_data \
  --attribute-definitions AttributeName=id,AttributeType=S \
  --key-schema AttributeName=id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region $AWS_REGION
```

Add demo items using `put-item`:

```bash
aws dynamodb put-item --table-name sample_data --item \
  '{"id": {"S": "1"}, "name": {"S": "Name1"}, "phone": {"S": "555-0001"}, "email": {"S": "user1@example.com"}, "region": {"S": "Region1"}, "location": {"M": {"lat": {"N": "12.345"}, "lon": {"N": "-34.567"}}}}' \
  --region $AWS_REGION

aws dynamodb put-item --table-name sample_data --item \
  '{"id": {"S": "2"}, "name": {"S": "Name2"}, "phone": {"S": "555-0002"}, "email": {"S": "user2@example.com"}, "region": {"S": "Region2"}, "location": {"M": {"lat": {"N": "-41.789"}, "lon": {"N": "77.123"}}}}' \
  --region $AWS_REGION

---

## Step 4. Configure Spice to Use DynamoDB Credentials

Update `.env` file to use your AWS credentials

```env
SPICE_DYNAMODB_KEY=<aws_access_key_id>
SPICE_DYNAMODB_SECRET=<aws_secret_access_key>
```

---

## Step 5. Start the Spice Runtime (if not already running)

```bash
spice run
```

If your credentials and region are correct, the dataset will load and logs output to terminal:

```bash
INFO runtime::init::dataset: Dataset sample_data initializing...
INFO runtime::init::dataset: Dataset sample_data registered (dynamodb:sample_data), acceleration (arrow), results cache enabled.
INFO runtime::accelerated_table::refresh_task: Loading data for dataset sample_data
INFO runtime::accelerated_table::refresh_task: Loaded 2 rows (3.25 kiB) for dataset sample_data in 34ms.
```

---

## Step 6. Query the DynamoDB Table with the Spice SQL REPL

```bash
spice sql
```

To show tables:

```sql
show tables;
```

To query your sample data:

```sql
select * from sample_data limit 10;
```

Sample output:

```console
+----+-------+----------+---------+-------------------+--------------+--------------+
| id | name  | phone    | region  | email             | location.lat | location.lon |
+----+-------+----------+---------+-------------------+--------------+--------------+
| 1  | Name1 | 555-0001 | Region1 | user1@example.com | 12.345       | -34.567      |
| 2  | Name2 | 555-0002 | Region2 | user2@example.com | -41.789      | 77.123       |
+----+-------+----------+---------+-------------------+--------------+--------------+
```

---

## Step 7. Cleanup

To delete the DynamoDB table:

```bash
aws dynamodb delete-table --table-name sample_data --region $AWS_REGION
```

## Additional Resources

For more information, see the [DynamoDB Connector documentation](https://spiceai.org/docs/components/data-connectors/dynamodb).