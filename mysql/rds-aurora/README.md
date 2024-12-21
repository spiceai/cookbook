# AWS RDS Aurora (MySQL Data Connector)

Follow these steps to get started with federated SQL query against AWS RDS Aurora (MySQL Compatible).

## Pre-requisites

- AWS RDS Aurora (MySQL Compatible) instance.
- Spice is installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation).

## Steps

**Step 1.** Navigate to your AWS RDS Aurora instance in the AWS Management Console.

> Note: Ensure that inbound connections are enabled in the associated security group.

**Step 2.** Look for "Reader" endpoint name and port.

![Screenshot](./aws-rds-aurora-mysql.png)

**Step 3.** Depending on chosen credentials management option (AWS Secrets Manager, or Self managed) retrieve `username` and `password`.

**Step 4.** Edit the `spicepod.yaml` file in this working directory and replace `[remote_table_path]` with the path to the remote table to be accelerated, `[local_table_name]` with the desired name for the locally accelerated table, and the `[mysql_host]` and `[mysql_tcp_port]` params with the connection parameters for the AWS RDS instance. The `[mysql_user]` should be set to the username for the RDS instance. The `[mysql_db]` should be set to the name of the database in the RDS instance. The `MYSQL_PASS` environment variable should be set to the password for the RDS instance. Environment variables can be specified on the command line when running the Spice runtime or in a `.env` file in the same directory as `spicepod.yaml`.

```bash
echo "MYSQL_PASS=<password>" > .env
```

See the [datasets reference](https://docs.spiceai.org/reference/spicepod/datasets) for more dataset configuration options and [MySQL Data Connector](https://docs.spiceai.org/components/data-connectors/mysql) for more options on configuring a MySQL Data Connector.

To securely store your RDS password, see [Secret Stores](https://docs.spiceai.org/components/secret-stores)

**Step 5.** Run the Spice runtime with `spice run` from this directory.

Follow the [getting started guide](https://docs.spiceai.org/getting-started) to get started with the Spice runtime.

**Step 6.** Run `spice sql` in a new terminal to start an interactive SQL query session against the Spice runtime.

For more information on using `spice sql`, see the [CLI reference](https://docs.spiceai.org/cli/reference/sql).

**Step 7.** Execute the query `select * from [local_table_name];` to see the AWS RDS table accelerated locally.
