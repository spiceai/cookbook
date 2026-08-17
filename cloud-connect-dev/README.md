# Cloud Connect on a Development Machine

Works with `v2.2+`

Connect this directory to Spice Cloud with one command, watch a deployment apply to the running instance without a restart, stop it, and reconnect.

The recipe is deliberately minimal: one public dataset, no infrastructure, no credentials on disk. What it demonstrates is the [Cloud Connect](https://spiceai.org/docs/deployment/cloud-connect) lifecycle on the machine you develop on.

You will:

1. Connect this directory and get a running instance attached to a new Spice Cloud project.
2. Deploy a change that applies live, with no restart and no serving gap.
3. Deploy a change that needs a restart, and see exactly which settings are pending.
4. Stop with `Ctrl-C` and reconnect with `spice run` — the identity survives.
5. Release the instance and delete its project.

## Prerequisites

- The Spice CLI, `v2.2.0` or later:

  ```bash
  curl https://install.spiceai.org | /bin/bash
  ```

- A Spice Cloud account with the **owner** or **admin** role in at least one organization. Those roles may enroll an instance and create a project; `member` may not.
- Outbound HTTPS to `api.spice.ai` and to the Cloud Connect gateway.

No `spice login` beforehand — `spice connect` runs login inline if needed.

**Cost:** a Spice Cloud project on the free tier. Step 6 deletes it.

## 1. Connect

Clone the cookbook and enter this recipe. The directory name is the project-name default, so run from `cloud-connect-dev` exactly:

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/cloud-connect-dev
spice connect
```

With no saved login, `spice connect` offers two choices rather than failing:

```console
? Connect this directory to Spice Cloud ›
❯ Log in to Spice Cloud (recommended)
  Use an enrollment key
```

Choose **Log in to Spice Cloud**. Login runs in the same process and the connect flow continues — there is no second command.

Next the organization. If your login is owner or admin in exactly one, it is named and used:

```console
Organization: <org> (owner)
```

If several are eligible, pick one. Then the project name, defaulted from this directory:

```console
? Project name › cloud-connect-dev
```

Press Enter to accept it. If the name is already taken in that organization, the CLI explains and re-prompts with an editable `cloud-connect-dev-2`; accept whatever it offers and use that name for the rest of the recipe.

The runtime then starts in your terminal:

```console
Starting the Spice runtime. Press Ctrl-C to stop it.
...
INFO Spice Cloud Connect: connected to <org> / cloud-connect-dev
INFO Monitor: https://spice.ai/<org>/cloud-connect-dev/monitor
```

Leave it running. Open the monitor link — the instance appears online, with the `data` dataset from `spicepod.yaml`.

Confirm from a second terminal, in the same directory:

```bash
cd cookbook/cloud-connect-dev
spice connect status
```

```console
Spice Cloud Connect: connected — <org> / cloud-connect-dev
  instance:    inst_<id>
  identity:    <path>/cloud-connect-dev/.spice/identity.json
  gateway:     connect.aws.spiceai.io:443
  expiry:      unix=<seconds> (expired=false)
  service:     not_installed
  starts:      not started automatically
  logs:        not configured by this service definition
  deployment:  none yet — this instance runs its local spicepod until an app is deployed
  secrets:     none delivered yet — deploy the app to deliver them
  monitor:     https://spice.ai/<org>/cloud-connect-dev/monitor
No service is installed for this directory. Run `spice connect service install` to keep this instance running across reboots.
```

Note the PID of the running runtime — nothing below changes it:

```bash
pgrep -f 'spiced' | head -1
```

## 2. Deploy a change that applies live

In the portal, edit the project's Spicepod and add a view, then deploy. Anything under `datasets`, `views`, `models`, `functions`, or an added `catalog` is reconciled into the running process:

```yaml
views:
  - name: recent
    sql: SELECT * FROM data LIMIT 10
```

The foreground terminal reports the deployment. There is no restart and no gap in serving:

```console
INFO Spice Cloud Connect: applied the deployed spicepod (1 datasets, 0 models, 0 catalogs, 1 views)
```

Check the PID again — it is unchanged — and query the new view while the same process serves it:

```bash
spice sql
```

```sql
SELECT count(*) FROM recent;
```

`spice connect status` now names the deployed Spicepod and reports no pending restart:

```console
  deployment:  <path>/cloud-connect-dev/.spice/spicepod-cloud-managed.yml
  secrets:     none (the last deployment delivered no secrets)
```

## 3. Deploy a change that needs a restart

Some sections are read only when the runtime starts. Add one in the portal — for example a `runtime` setting — and deploy again:

```yaml
runtime:
  task_history:
    captured_output: truncated
```

The instance keeps serving its current configuration. The deployment is persisted as desired state and the affected sections are named:

```console
INFO Spice Cloud Connect: applied the deployed spicepod (1 datasets, 0 models, 0 catalogs, 1 views); runtime takes effect when this instance next starts
```

The pending list is sticky and readable from three places, all backed by the same state:

```bash
spice connect status
```

```console
  restart:     required for runtime
```

```bash
spice connect status --output json | jq .deployment.restart_required
```

```console
[
  "runtime"
]
```

```bash
curl -s http://127.0.0.1:8090/v1/cloud-connect/status | jq
```

```console
{
  "instance_id": "inst_<id>",
  "restart_required": [
    "runtime"
  ]
}
```

The PID is still unchanged, and queries still work. In the foreground there is no supervisor to restart the instance — that is step 4.

## 4. Stop and reconnect

In the foreground terminal, press `Ctrl-C`. The runtime stops. The Cloud identity is **not** released: the instance shows as offline in the portal and `.spice/identity.json` is still on disk.

```bash
spice connect status
```

```console
Spice Cloud Connect: connected — <org> / cloud-connect-dev
```

Start it again from the same directory. No Cloud Connect flag is needed — the identity reconnects it:

```bash
spice run
```

```console
INFO Spice Cloud Connect: connected to <org> / cloud-connect-dev
INFO Monitor: https://spice.ai/<org>/cloud-connect-dev/monitor
```

This start activates the desired configuration, so the pending list clears:

```bash
spice connect status
```

The `restart:` line is gone.

`spice connect` from this directory does the same thing. It never enrolls a second instance — an existing identity always wins.

## 5. Validate locally

`validate.sh` checks the parts of this recipe that need no Spice Cloud account and no credentials. Run it any time:

```bash
./validate.sh
```

It asserts that the CLI is new enough, that the project-name default derives from this directory with no random fallback, that `spice connect status` reports a coherent snapshot in both output formats, that a non-interactive `spice connect` refuses instead of hanging, and that no credential or generated identity is staged for commit.

## 6. Clean up

Stop the runtime first — removal refuses while `spiced` is running — then release the instance:

```bash
spice connect remove
```

```console
This will delete this instance's project in Spice Cloud and remove the instance from this host:
  directory: <path>/cloud-connect-dev
  identity:  <path>/cloud-connect-dev/.spice/identity.json (deleted)
? Continue? › yes
Deleted project cloud-connect-dev in Spice Cloud.
Spice Cloud Connect identity cleared. To re-enroll this directory, mint a new enrollment key in the Spice Cloud portal and start the runtime with `spiced --token <enrollment-key>`.
```

The project is deleted with your logged-in user session, so stay logged in to the same organization. Confirm the directory is clear:

```bash
spice connect status
```

```console
Spice Cloud Connect: not connected (<path>/cloud-connect-dev)
```

## Notes

- **Nothing is committed.** `.spice/` is gitignored: the issued identity, the cloud-managed Spicepod, and the delivered-secrets cache all live there. `validate.sh` checks it.
- **`spice connect` needs a terminal.** It is interactive; on a non-interactive stdin it exits and points at `spiced --token <enrollment-key>` for [headless enrollment](https://spiceai.org/docs/deployment/cloud-connect/headless).
- **Cancelling is safe.** `Esc` or `Ctrl-C` at any prompt is a clean exit. An interrupted enrollment resumes on the next run rather than creating a duplicate instance or project.
- **This recipe is foreground only.** To keep the instance running across reboots on Linux, see [Cloud Connect as a persistent service](https://spiceai.org/docs/deployment/cloud-connect/service). The managed service lifecycle does not yet support macOS or Windows; there, the foreground flow in this recipe is the development story.

## Learn more

- [Cloud Connect](https://spiceai.org/docs/deployment/cloud-connect)
- [`spice connect` reference](https://spiceai.org/docs/cli/reference/connect)
