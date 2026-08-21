# Cloud Connect on a Development Machine

Works with Spice CLI v2.2 or later.

Use this recipe to link a local Spice instance to Spice Cloud. You will deploy live changes, deliver a secret, and restart the instance.

## Prerequisites

- A Spice Cloud organization where you are an owner or admin
- Docker
- Spice CLI v2.2 or later

Install the Spice CLI:

```shell
curl https://install.spiceai.org | /bin/bash
```

## 1. Link the instance

Clone the cookbook and open this recipe:

```shell
git clone https://github.com/spiceai/cookbook.git
cd cookbook/cloud-connect-dev
```

Sign in to Spice Cloud:

```shell
spice login
```

Create the project. With no `--kind`, this creates a Cloud Connect project — one your own runtime serves, which has no region to choose:

```shell
spice cloud project create cloud-connect-dev
```

If that name is taken in your organization, pick another and use it everywhere below.

`--region`, and the hosted-runtime flags such as `--replicas` and `--memory`, are refused here rather than ignored. They configure a Spice-managed project, which you ask for with `--kind set` or `--kind cluster`.

Link this directory to the project:

```shell
spice cloud link <org>/cloud-connect-dev
```

`spice cloud link` enrolls this directory as an instance and attaches it to the project. It needs an interactive terminal; omit the project to choose one from a list. For an unattended machine, mint an enrollment key in the portal and start the runtime with `spiced --token <enrollment-key>` instead.

```text
✓ Linked the enrolled instance to project <org>/cloud-connect-dev

Start this instance in the current directory with:
  spice run

You can now use commands without specifying --project:
  spice cloud deploy
  spice cloud logs
  spice cloud secrets list
```

Linking adds `.spice/` to `.gitignore`, the directory holding the instance's mTLS private key.

A project with no stored Spicepod is seeded from the local `spicepod.yaml`, so the project now defines the `data` dataset. Later local edits are not synchronized; deploy to change what the instance runs.

Start the instance:

```shell
spice run
```

Leave the runtime open. Open the monitor link in the output.

In a second terminal, check the connection:

```shell
cd cookbook/cloud-connect-dev
spice cloud status
```

The report covers the project, its latest deployment, and the instances serving it, then closes with this directory's own state under `Local enrolled-instance state:`. It reads from Spice Cloud, so it needs the session `spice login` created.

## 2. Deploy a live change

A deployment replaces the Spicepod the instance runs. In the Spice Cloud portal, open the project Spicepod and add this view below the datasets:

```yaml
views:
  - name: recent
    sql: SELECT * FROM data LIMIT 10
```

Deploy the Spicepod. You do not have to restart the instance.

Query the view:

```shell
spice sql
```

```sql
SELECT count(*) FROM recent;
```

## 3. Deliver a secret

Create a password and start PostgreSQL:

```shell
export SPICE_DEMO_PG_PASSWORD="$(openssl rand -hex 16)"
docker compose up -d
```

Confirm that PostgreSQL contains the sample data:

```shell
docker compose exec postgres \
  psql -U spice_reader -d spice_demo \
  -c 'SELECT count(*) FROM public.orders;'
```

In the portal, open the project's **Settings → Secrets** and add:

| Name          | Value                              |
| ------------- | ---------------------------------- |
| `PG_PASSWORD` | Value of `$SPICE_DEMO_PG_PASSWORD` |

Secret names are matched exactly. A Spicepod that references a name the project does not define is rejected when you deploy it, and the portal names the closest match it holds.

Add this dataset to the project Spicepod in the portal — not to the local `spicepod.yaml`:

```yaml
datasets:
  - from: postgres:public.orders
    name: orders
    params:
      pg_host: localhost
      pg_port: "55432"
      pg_db: spice_demo
      pg_user: spice_reader
      pg_pass: ${secrets:PG_PASSWORD}
      pg_sslmode: disable
```

Deploy the Spicepod. Then query the PostgreSQL data:

```shell
spice sql
```

```sql
SELECT customer, total_cents FROM orders ORDER BY id LIMIT 3;
```

The query returns:

```text
+----------+-------------+
| customer | total_cents |
|  varchar |    int32    |
+----------+-------------+
| acme     | 12900       |
| globex   | 4550        |
| initech  | 31875       |
+----------+-------------+
```

Confirm the delivery:

```shell
spice cloud status
```

```text
Local enrolled-instance state:
  secrets:     1 delivered: PG_PASSWORD
```

Status reports secret names. Values stay in the runtime process.

Three properties of a delivered secret:

- The Spicepod declares no `secrets:` section. Delivered secrets are a built-in store, so the same Spicepod runs unchanged as a managed app and on a self-hosted instance.
- A local value wins. The built-in store has the lowest precedence, so an `env` or `.env.local` value for `PG_PASSWORD` overrides the delivered one. Unset it to use the delivered value.
- Only the first delivery applies live. Rotating a secret that a component already resolved requires a restart, like a `runtime` change.

If you deploy the dataset before adding the secret, the runtime names the unresolved reference and that dataset fails to load. Add the secret and deploy again.

## 4. Deploy a change that requires a restart

Add this setting to the project Spicepod:

```yaml
runtime:
  task_history:
    captured_output: truncated
```

Deploy the Spicepod. The runtime names the sections that need a start, in the terminal running the instance:

```text
INFO Spice Cloud Connect: applied the deployed spicepod (1 datasets, 0 models, 0 catalogs, 1 views); runtime takes effect when this instance next starts
```

The project in Spice Cloud reports the same pending sections. The instance continues to serve queries until you restart it.

## 5. Restart and reconnect

In the first terminal, press `Ctrl-C`. Start the instance again from the same directory:

```shell
spice run
```

You do not need to run `spice cloud link` again. The existing identity reconnects the instance.

The instance now serves the deployed `runtime` settings, and the deployment reports nothing pending.

> **Warning:** Spice Cloud invalidates the identity if the instance stays offline for more than 30 days. Link the directory again to reconnect it.

## 6. Validate the recipe

Run the local checks:

```shell
./validate.sh
```

These checks do not connect to Spice Cloud or use credentials.

## 7. Clean up

Stop the runtime first — `spice cloud unlink` refuses while the instance is running. Then detach this directory:

```shell
spice cloud unlink
```

Unlinking releases the enrolled instance, removes its local identity, and uninstalls its service if one is installed. The project keeps its Spicepod, secrets, and deployment history. Delete it when you are finished with it:

```shell
spice cloud project delete <org>/cloud-connect-dev
```

Stop PostgreSQL and delete its volume:

```shell
docker compose down -v
unset SPICE_DEMO_PG_PASSWORD
```

## Run as a service

To keep the instance running after you close the terminal, install a service for this directory:

```shell
spice cloud service install
```

`spice cloud service` also has `start`, `stop`, `restart`, and `uninstall`. Uninstalling keeps the Cloud identity, so `spice run` still reconnects the instance.

Windows does not support the managed service.

See [Cloud Connect as a service](https://spiceai.org/docs/next/deployment/cloud/cloud-connect/service).

## Learn more

- [Cloud Connect](https://spiceai.org/docs/next/deployment/cloud/cloud-connect)
