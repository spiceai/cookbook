# Streaming changes in real-time with Debezium CDC

Works with `v1.0+`

Change Data Capture (CDC) is a technique to capture changed rows from a database's transaction log and deliver to consumers with low latency. Leveraging this technique allows Spice to keep locally accelerated datasets up-to-date in real-time with the source data, and is highly efficient by only transferring the changed rows instead of re-fetching the entire dataset on refresh.

In this recipe we will have a local Postgres database with a table `customer_addresses` and a Spice runtime that accelerates the data from the `customer_addresses` table. A Debezium connector will capture changes from the `customer_addresses` table and publish them to a Kafka topic called `cdc.public.customer_addresses`. The Spice runtime will consume the changes from the Kafka topic and keep an accelerated dataset updated with the changes, including the initial state.

## Prerequisites

This recipe requires [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) to be installed.

Also ensure that you have the `spice` CLI installed. You can find instructions on how to install it [here](https://docs.spiceai.org/getting-started).

You will also need `psql` or another Database client (i.e. DBeaver) to connect to the Postgres database.

`curl` is required to register the Debezium Postgres connector.

## How to run

Clone this cookbook repo locally and navigate to the `cdc-debezium` directory:

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/cdc-debezium
```

Start the Docker Compose stack, which includes a Postgres database, a Kafka broker (via Redpanda), and a Debezium connector:

```shell
docker compose up -d
```

Navigate to <http://localhost:8080> to see the Redpanda console. Notice that no topics are created by Debezium yet. We need to tell Debezium to connect to the Postgres database and create the topics.

```shell
curl -i -X POST -H "Accept:application/json" -H  "Content-Type:application/json" http://localhost:8083/connectors/ -d @register-connector.json
```

Now the Debezium connector is registered and will start capturing changes from the `customer_addresses` table in the Postgres database. Open http://<localhost:8080/topics> and see the topic `cdc.public.customer_addresses` created.

This spicepod.yaml shows the config needed to configure Spice to connect to the Kafka topic and consume the Debezium changes:

```yaml
version: v1
kind: Spicepod
name: cdc-debezium

datasets:
  - from: debezium:cdc.public.customer_addresses
    name: cdc
    params:
      debezium_transport: kafka
      debezium_message_format: json
      kafka_bootstrap_servers: localhost:19092
      kafka_security_protocol: SASL_PLAINTEXT
      kafka_sasl_mechanism: SCRAM-SHA-256
      kafka_sasl_username: ${secrets:KAFKA_USERNAME}
      kafka_sasl_password: ${secrets:KAFKA_PASSWORD}
    acceleration:
      enabled: true
      engine: sqlite
      mode: file
      refresh_mode: changes
```

Ensure the current directory is `cdc-debezium`, and start the spice runtime with the following command

```bash
spice run
```

Observe that the dataset is registered. It should look like:

```bash
2026-10-15T06:03:39.185035Z  INFO runtime::init::dataset: Dataset cdc registered (debezium:cdc.public.customer_addresses), acceleration (sqlite:file, changes), results cache enabled. duration_ms=4
2026-10-15T06:03:40.817926Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

If Debezium has not created the Kafka topic yet, Spice can log a `WARN` that it failed to load the dataset `cdc`. Spice tries again and loads the dataset when the topic is available.

Spice does not log each change that it applies. Use SQL to make sure that Spice consumed the changes. Run `spice sql` in a separate terminal to query the data

```sql
SELECT * FROM cdc;
```

Count the rows. The initial state of the `customer_addresses` table has 51 rows:

```sql
SELECT count(*) FROM cdc;
```

```bash
+----------+
| count(*) |
|   int64  |
+----------+
| 51       |
+----------+

Time: 0.002231875 seconds. 1 rows.
```

Now let's make some changes to the Postgres database and observe that Spice consumes the changes.

Stop the Spice SQL REPL or open a third terminal and connect to the Postgres database with `psql`:

```bash
PGPASSWORD="postgres" psql -h localhost -U postgres -d postgres -p 15432
```

```sql
INSERT INTO public.customer_addresses (id, first_name, last_name, email)
VALUES
(100, 'John', 'Doe', 'john@doe.com');
```

Query the data again from the `spice sql` REPL. After a few seconds, the new record is in the accelerated dataset:

```sql
SELECT * FROM cdc WHERE id = 100;
```

```bash
+-------+------------+-----------+--------------+-------------+--------------+---------+---------+---------+---------+
|   id  | first_name | last_name |     email    | res_address | work_address | country |  state  | phone_1 | phone_2 |
| int32 |   varchar  |  varchar  |    varchar   |   varchar   |    varchar   | varchar | varchar | varchar | varchar |
+-------+------------+-----------+--------------+-------------+--------------+---------+---------+---------+---------+
| 100   | John       | Doe       | john@doe.com |             |              |         |         |         |         |
+-------+------------+-----------+--------------+-------------+--------------+---------+---------+---------+---------+

Time: 0.003222416 seconds. 1 rows.
```

`SELECT count(*) FROM cdc;` now returns `52`.

Now let's see what happens when we stop Spice and restart it. The data should still be there and it should not replay all of the changes from the beginning.

Stop spice with `Ctrl+C`

Restart Spice with `spice run`

Observe that it doesn't replay the changes and the data is still there. Spice continues from the Kafka offsets that it saved, and only new changes will be consumed. It can take up to a minute before the runtime is ready:

```bash
2026-10-15T06:04:07.790425Z  INFO runtime::init::dataset: Dataset cdc registered (debezium:cdc.public.customer_addresses), acceleration (sqlite:file, changes), results cache enabled. duration_ms=3
2026-10-15T06:04:48.902137Z  INFO data_components::kafka: Restored Kafka consumer offsets from sidecar
2026-10-15T06:04:49.995292Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

Run `SELECT count(*) FROM cdc;` again in `spice sql`. It returns the same number of rows as before the restart, plus any rows that you inserted while Spice was stopped.

## Clean up

To stop and remove the Docker containers/volumes that were created, run:

`make clean`

If you don't have the `make` command available, you can run the following commands:

```bash
docker compose down -v
```
