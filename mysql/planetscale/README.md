# Planetscale (MySQL Data Connector) Recipe

Follow these steps to get started with federated SQL query against [Planetscale](https://planetscale.com/) using the MySQL Data Connector.

**Step 1.** Navigate to your Planetscale account and select your database, then click `Connect`.

![Screenshot](./img/planetscale-1-connect.png)

**Step 2.** Select the branch, set the password name, and specify the role. Read-only access will be sufficient for spice.

![Screenshot](./img/planetscale-2-create-password.png)

**Step 3.** Select "Other" for the framework option and copy the generated credentials.

![Screenshot](./img/planetscale-3-configure.png)

**Step 4.** Edit the `spicepod.yaml` file in this directory and replace the following parameters:

- `[remote_table_path]` with the path to the Planetscale table to be accelerated.
- `[local_table_name]` with your desired name for the locally accelerated table.
- `[mysql_host]` with the host from Planetscale configuration.
- `[mysql_user]` with the username from the generated credentials in step 3.
- `[mysql_db]` with the name of your Planetscale database.

See the [datasets reference](https://docs.spiceai.org/reference/spicepod/datasets) for more dataset configuration options and [MySQL Data Connector](https://docs.spiceai.org/data-connectors/mysql) for more options on configuring a MySQL Data Connector.

Ensure the `MYSQL_PASS` environment variable is set to the password for your Planetscale instance. Environment variables can be specified on the command line when running the Spice runtime, or in a `.env` file in the same directory as `spicepod.yaml`.

```bash
echo "MYSQL_PASS=<password>" > .env
```

**Step 5.** Run the Spice runtime with `spice run` from this directory.

Follow the [getting started guide](https://docs.spiceai.org/getting-started) to get started with the Spice runtime.

**Step 6.** Run `spice sql` in a new terminal to start an interactive SQL query session against the Spice runtime.

For more information on using `spice sql`, see the [CLI reference](https://docs.spiceai.org/cli/reference/sql).

**Step 7.** Execute the query `select * from [local_table_name];` to see the Planetscale table accelerated locally.
