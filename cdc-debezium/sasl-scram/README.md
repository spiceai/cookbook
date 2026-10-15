# Streaming changes in real-time with Debezium CDC and SASL/SCRAM authentication

Works with `v1.0+`

This recipe is identical to the [cdc-debezium](../README.md) recipe, but using SASL/SCRAM over TLS (`SASL_SSL` with `SCRAM-SHA-512`) authentication for Kafka instead of `SASL_PLAINTEXT` (`SCRAM-SHA-256`), and from a MySQL database.

## Prerequisites

This recipe requires [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) to be installed.

Also ensure that you have the `spice` CLI installed. You can find instructions on how to install it [here](https://docs.spiceai.org/getting-started).

You will also need `mysql` or another Database client (i.e. DBeaver) to connect to the MySQL database.

`curl` is required to register the Debezium MySQL connector.

## How to run

Clone this cookbook repo locally and navigate to the `cdc-debezium/sasl-scram` directory:

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/cdc-debezium/sasl-scram
```

Start the Docker Compose stack, which includes a MySQL database, a Kafka broker, Zookeeper, and a Debezium connector:

```bash
docker compose up -d
```

Navigate to <http://localhost:8080> to see the Kafka console. Notice that no topics are created by Debezium yet. We need to tell Debezium to connect to the MySQL database and create the topics.

Register the Debezium connector:

```bash
curl -i -X POST -H "Accept:application/json" -H  "Content-Type:application/json" http://localhost:8083/connectors/ -d @register-connector.json
```

or using `make`:

```bash
make register-connector
```

Now the Debezium connector is registered and will start capturing changes from the `customer_addresses` table in the MySQL database.

This `spicepod.yaml` shows the config needed to configure Spice to connect to the Kafka topic and consume the Debezium changes with SASL/SCRAM authentication over TLS:

```yaml
version: v1
kind: Spicepod
name: cdc-debezium-sasl-scram

datasets:
  - from: debezium:cdc.inventory.customer_addresses
    name: cdc
    params:
      debezium_transport: kafka
      debezium_message_format: json
      kafka_bootstrap_servers: localhost:19092
      kafka_security_protocol: SASL_SSL
      kafka_sasl_mechanism: SCRAM-SHA-512
      kafka_sasl_username: kafka
      kafka_sasl_password: kafka_password
      kafka_ssl_ca_location: ./certs/kafka_ca_cert.pem
      kafka_enable_ssl_certificate_verification: true
    acceleration:
      enabled: true
      engine: sqlite
      mode: file
      refresh_mode: changes
```

Spice runtime is already configured to run with the debug level of information, with environment variable configured in `cdc-debezium/sasl-scram/.env`

```bash
SPICED_LOG="spiced=DEBUG,runtime=DEBUG,data_components=DEBUG,cache=DEBUG"
```

Ensure the current directory is `cdc-debezium/sasl-scram`, and start the spice runtime with the following command

```bash
spice run
```

Observe that the dataset is registered. It should look like:

```bash
2026-10-15T06:09:03.857564Z  INFO runtime::init::dataset: Dataset cdc registered (debezium:cdc.inventory.customer_addresses), acceleration (sqlite:file, changes), results cache enabled. duration_ms=4
2026-10-15T06:09:08.640159Z  INFO runtime: All components are loaded. Spice runtime is ready!
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

Time: 0.002061542 seconds. 1 rows.
```

Now let's make some changes to the MySQL database and observe that Spice consumes the changes.

Stop the Spice SQL REPL or open a third terminal and connect to the MySQL database with `mysql`:

```bash
mysql -h 127.0.0.1 -u root -pdebezium inventory -P 3306
```

```sql
INSERT INTO inventory.customer_addresses (id, first_name, last_name, email)
VALUES
(100, 'John', 'Doe', 'john@doe.com');
```

Query the data again from the `spice sql` REPL. After a few seconds, the new record is in the accelerated dataset:

```sql
SELECT * FROM cdc WHERE id = 100;
```

```bash
+-------+------------+-----------+--------------+-------------+--------------+---------+---------+---------+---------+
|   id  | first_name | last_name |     email    | res_address | work_address | country |  State  | phone_1 | phone_2 |
| int64 |   varchar  |  varchar  |    varchar   |   varchar   |    varchar   | varchar | varchar | varchar | varchar |
+-------+------------+-----------+--------------+-------------+--------------+---------+---------+---------+---------+
| 100   | John       | Doe       | john@doe.com |             |              |         |         |         |         |
+-------+------------+-----------+--------------+-------------+--------------+---------+---------+---------+---------+

Time: 0.002631125 seconds. 1 rows.
```

`SELECT count(*) FROM cdc;` now returns `52`.

Now let's see what happens when we stop Spice and restart it. The data should still be there and it should not replay all of the changes from the beginning.

Stop spice with `Ctrl+C`

Restart Spice with `spice run`

Observe that it doesn't replay the changes and the data is still there. Spice continues from the Kafka offsets that it saved, and only new changes will be consumed. It can take up to a minute before the runtime is ready:

```bash
2026-10-15T06:10:02.401191Z  INFO runtime::init::dataset: Dataset cdc registered (debezium:cdc.inventory.customer_addresses), acceleration (sqlite:file, changes), results cache enabled. duration_ms=3
2026-10-15T06:10:52.545508Z  INFO data_components::kafka: Restored Kafka consumer offsets from sidecar
2026-10-15T06:10:53.688576Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

Run `SELECT count(*) FROM cdc;` again in `spice sql`. It returns `52`, the same number of rows as before the restart.

## Clean up

To stop and remove the Docker containers/volumes that were created, run:

`make clean`

If you don't have the `make` command available, you can run the following commands:

```bash
docker compose down -v
rm -r .spice || true
rm -r certs || true
```
