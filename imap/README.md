# IMAP Data Connector

Follow these steps to get started with the IMAP Data Connector, connecting to an IMAP server with a plain username and password.

For connecting to a hosted email service like Outlook, see the [Connecting to an Outlook mailbox recipe](./outlook.md)

## Pre-requisites

- The latest version of Spice. [Install Spice](https://docs.spiceai.org/getting-started/installation).
- An IMAP server with configured mailboxes, to login using a username (email) and password.

## Steps

### 1. Spicepod setup

Edit the `spicepod.yaml` file in this directory, and replace the `<IMAP_EMAIL>` and `<IMAP_HOST>` with the connection details to connect to your IMAP server. The password for the IMAP connection will be supplied using a secret, via an environment variable.

For example:

```yaml
version: v1
kind: Spicepod
name: imap_email
datasets:
  - from: imap:awesome@example.com
    name: awesome_mailbox
    params:
      imap_password: ${secrets:IMAP_PASSWORD}
      imap_host: imap.example.com
```

### 2. Start Spice

Start Spice, supplying `IMAP_PASSWORD` as an environment variable.

For example, in an `.env` file:

```bash
IMAP_PASSWORD=my_password
```

Once started, the mailbox should be registered in the Spice Runtime logs:

```console
2025-02-02T23:25:23.876322Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2025-02-02T23:25:23.876386Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2025-02-02T23:25:23.877307Z  INFO runtime::init::dataset: Initializing dataset awesome_mailbox
2025-02-02T23:25:23.877477Z  INFO runtime::init::results_cache: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
2025-02-02T23:25:23.878156Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2025-02-02T23:25:23.887277Z  INFO runtime::init::dataset: Dataset awesome_mailbox registered (imap:awesome@example.com), results cache enabled.
```

### 3. Query your mail

Once the Spice Runtime is running, run `spice sql` to launch the Spice REPL and start querying your mail:

```sql
SELECT * FROM awesome_mailbox
```

```console
+-------------------------+------------+----------------+----------------------+----+-----+----------------+------------+-------------+
| date                    | subject    | from           | to                   | cc | bcc | reply_to       | message_id | in_reply_to |
+-------------------------+------------+----------------+----------------------+----+-----+----------------+------------+-------------+
| 1970-01-21T02:46:04.919 | Test Email | [ubuntu@localhost] | [awesome@example.com] |    |     | [ubuntu@localhost] |            |             |
+-------------------------+------------+----------------+----------------------+----+-----+----------------+------------+-------------+
```
