# Clickhouse Data Connector Recipe

Follow these steps to get started with Clickhouse as a Data Connector.

## Preparation

- Install the [Spice.ai CLI](https://docs.spiceai.org/getting-started/installation)
- Install [Clickhouse](https://clickhouse.com/docs/en/install#quick-install)
  - `curl https://clickhouse.com/ | sh`
- Start a Clickhouse instance (`clickhouse server`)

  ```bash
  ./clickhouse server
  ```
  
- Create a database and table, for example:

  ```bash
  ./clickhouse client 
  ```

  ```sql
  CREATE TABLE my_first_table
  (
      user_id UInt32,
      message String,
      timestamp DateTime,
      metric Float32
  )
  ENGINE = MergeTree
  PRIMARY KEY (user_id, timestamp);

  INSERT INTO my_first_table (user_id, message, timestamp, metric) VALUES
    (101, 'Hello, ClickHouse!',                                 now(),       -1.0    ),
    (102, 'Insert a lot of rows per batch',                     yesterday(), 1.41421 ),
    (102, 'Sort your data based on your commonly-used queries', today(),     2.718   ),
    (101, 'Granules are the smallest chunks of data read',      now() + 5,   3.14159 );
  ```

## Quickstart

**Step 1.** Edit the `spicepod.yaml` file in this directory and replace the params in the `clickhouse_quickstart` dataset with the connection parameters for your Clickhouse instance, where `[local_table_name]` is your desired name for the federated table and `[remote_table_path]` is the name of the table in your Clickhouse instance.

Follow the [quickstart guide](https://docs.spiceai.org/getting-started) to get started with the Spice.ai runtime.

See the [datasets reference](https://docs.spiceai.org/reference/spicepod/datasets) for more dataset configuration options.

Set the environment variable `CLICKHOUSE_PASS` to the Clickhouse instance password. Environment variables can be specified on the command line when running the Spice runtime or in a `.env` file in the same directory as `spicepod.yaml`. The password is not required if the Clickhouse instance does not have a password set.

i.e. to set the password in a `.env` file:

```bash
echo "CLICKHOUSE_PASS=<password>" > .env
```

A `.env` file is created in the project directory with the following content:

```bash
CLICKHOUSE_PASS=<password>
```

If you followed the above [preparation](#preparation) to generate a Clickhouse server use this:

```yaml
version: v1beta1
kind: Spicepod
name: clickhouse_quickstart
datasets:
  - from: clickhouse:my_first_table
    name: my_first_table
    params:
      clickhouse_host: localhost
      clickhouse_db: default
      clickhouse_user: default
      clickhouse_tcp_port: 9000
      clickhouse_secure: false
    acceleration:
      enabled: true
      refresh_mode: full
      refresh_check_interval: 10s
```

**Step 2.** Run the Spice runtime with `spice run` from this directory.

**Step 3.** Run `spice sql` in a new terminal to start an interactive SQL query session against the Spice runtime.

For more information on using `spice sql`, see the [CLI reference](https://docs.spiceai.org/cli/reference/sql).

**Step 4.** Execute the query `select * from [local_table_name];` to see the Clickhouse table accelerated locally.

```console
$ spice sql
Welcome to the Spice.ai SQL REPL! Type 'help' for help.

show tables; -- list available tables
sql> select * from my_first_table;
+---------+----------------------------------------------------+---------------------+---------+
| user_id | message                                            | timestamp           | metric  |
+---------+----------------------------------------------------+---------------------+---------+
| 101     | Hello, ClickHouse!                                 | 2024-09-02T05:53:24 | -1.0    |
| 101     | Granules are the smallest chunks of data read      | 2024-09-02T05:53:29 | 3.14159 |
| 102     | Insert a lot of rows per batch                     | 2024-08-31T15:00:00 | 1.41421 |
| 102     | Sort your data based on your commonly-used queries | 2024-09-01T15:00:00 | 2.718   |
+---------+----------------------------------------------------+---------------------+---------+

Time: 0.004758125 seconds. 4 rows.
```
