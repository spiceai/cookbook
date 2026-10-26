# Accelerated Snapshots

Works with `v2.4+`

This recipe walks through configuring database snapshots for file-mode accelerations so datasets avoid cold starts and recover quickly after restarts.

> **Note:** Acceleration Snapshots require either [Spice Enterprise](https://spice.ai) or a Spice OSS build compiled with the `snapshots` feature flag. Running this recipe against a standard OSS binary will produce warnings and the snapshot functionality will be inactive.

_Tip: Keep the [Snapshots documentation](https://spiceai.org/docs/features/data-acceleration/snapshots) handy while following this guide._

## Step 1. Prepare a Spice workspace

Install the Spice CLI if needed, then create a new project and initialize a fresh pod:

```bash
spice init spice-db-snapshots
cd spice-db-snapshots
```

The `spice init` command creates a top-level `spicepod.yaml` that we will customize in later steps.

## Step 2. Configure snapshot storage

Snapshots need a writable location, typically an S3 bucket/prefix that only the Spice runtime uses. Pick or create a bucket and prefix such as `s3://my-snapshots-prod/taxi-trips/`.

Spice supports the standard AWS credential flows:

- `AWS_PROFILE` pointing to an AWS CLI profile (SSO or static keys).
- Standard `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` environment variables.
- Per-pod credentials set through `runtime.state.params`.

For this recipe we load credentials from a `.env` file placed beside the pod definition.

Create `.env` in the same directory as `spicepod.yaml`:

```dotenv
S3_SNAPSHOT_KEY=<your-access-key>
S3_SNAPSHOT_SECRET=<your-secret-key>
S3_SNAPSHOT_REGION=<your-region>
```

If you prefer AWS profiles or environment variables set globally, skip the `.env` file and adjust the pod configuration accordingly.

## Step 3. Enable snapshots in the Spicepod

Open the `spicepod.yaml` that `spice init` created and replace its contents with the configuration below, updating the `runtime.state.location` prefix to your bucket:

```yaml
version: v1
kind: Spicepod
name: quickstart

runtime:
  state:
    location: s3://my-snapshots-prod/quickstart/
    params:
      s3_auth: key
      s3_key: ${ env:S3_SNAPSHOT_KEY }
      s3_secret: ${ env:S3_SNAPSHOT_SECRET }
      s3_region: ${ env:S3_SNAPSHOT_REGION }

datasets:
  - from: s3://spiceai-public-datasets/taxi_trips/
    name: taxi_trips
    description: NYC TLC trips sample
    params:
      file_format: parquet
      s3_auth: public
    acceleration:
      enabled: true
      engine: cayenne
      mode: file
      snapshots: enabled # enabled | bootstrap_only | create_only | disabled
      snapshots_bootstrap_on_failure_behavior: fallback # retry | fallback | warn (default)
      params:
        cayenne_file_path: cayenne_data # Stored on local disk and bootstrapped from snapshots
```

Key settings to note:

- The `runtime.state` block defines the shared storage location. Snapshots are written to its `snapshots/` folder.
- The dataset opts into snapshots by setting `acceleration.snapshots` to `enabled`.
- The dataset sets its failure behavior with `acceleration.snapshots_bootstrap_on_failure_behavior`.
- Each accelerated dataset writes to its own Cayenne folder (`cayenne_data/taxi_trips/`), next to the shared Cayenne catalog (`cayenne_data/metadata/`).

The top-level `snapshots` section used by earlier versions of this recipe is deprecated in v2.4. See [Migrate from the top-level `snapshots` section](https://spiceai.org/docs/features/data-acceleration/snapshots#migrate-from-the-top-level-snapshots-section).

## Step 4. Launch Spice and create the first snapshot

Start the runtime:

```bash
spice run
```

On first boot the acceleration file does not exist locally, so Spice loads from S3 and refreshes the dataset. After the initial refresh completes you should see a log similar to:

```bash
2026-10-26T20:53:39.415062Z  INFO runtime_acceleration::snapshot: Snapshot created dataset=taxi_trips snapshot=quickstart/snapshots/month=2026-10/day=2026-10-26/dataset=taxi_trips/taxi_trips_20261026T205338Z_01a179fd7e6e7b03ae698e0cc2bfe78f.cayenne size_bytes=72192 duration_ms=872.4 sha=3e1c62451a408815ba098db06711fb51b6d68310003309df2745969da4fbb315
```

Each snapshot object is named `<dataset>_<UTC timestamp>_<UUIDv7>.<engine extension>`, so Cayenne snapshots end in `.cayenne`.

Verify the snapshot appeared in your bucket using the AWS CLI or console.

## Step 5. Test snapshot bootstrap

Simulate a cold start by stopping the runtime and removing the local Cayenne data:

```bash
Ctrl+C  # stop spice run
rm -rf cayenne_data
spice run
```

This time the startup logs show the snapshot bootstrap:

```bash
2026-10-26T20:53:44.481627Z  INFO runtime_acceleration::snapshot: Snapshot restored to cayenne_data/metadata dataset=taxi_trips snapshot=s3://my-snapshots-prod/quickstart/snapshots/month=2026-10/day=2026-10-26/dataset=taxi_trips/taxi_trips_20261026T205338Z_01a179fd7e6e7b03ae698e0cc2bfe78f.cayenne size_bytes=72192 sha=3e1c62451a408815ba098db06711fb51b6d68310003309df2745969da4fbb315
```

Spice skips the full refresh and immediately serves queries, dramatically reducing warm-up time.

## Step 6. Explore snapshot modes

Snapshots can be fine-tuned per dataset:

- `bootstrap_only`: download snapshots on startup but never write new ones (useful for read-only staging environments).
- `create_only`: generate snapshots after refreshes without bootstrapping from them.
- `disabled`: opt out for specific datasets even when the pod sets `runtime.state`.

Spice downloads a snapshot only when the local acceleration file does not exist. Try switching `acceleration.snapshots` to `bootstrap_only`, stopping Spice, removing `cayenne_data`, and restarting to observe that Spice restores the existing snapshot but skips writing a new version after refreshes.

## Step 7. Handle bootstrap failures

The dataset's `acceleration.snapshots_bootstrap_on_failure_behavior` controls what happens if the newest snapshot fails to load:

- `retry`: keep trying the newest file until it succeeds (best when snapshots should never fail).
- `fallback`: automatically attempt older snapshot files.
- `warn`: log a warning and continue with an empty acceleration (default).

Set the value to `warn`, stop Spice, remove the snapshot file from S3 and the local `cayenne_data`, and restart to see how Spice warns and performs a regular refresh when no snapshot is available:

```bash
WARN runtime_acceleration::snapshot: Failed to bootstrap snapshot; continuing without a downloaded snapshot. dataset=taxi_trips location=quickstart/snapshots error=Snapshot 1 of dataset 'taxi_trips' has no file at ...
```

## Summary

You configured Cayenne accelerations to write and consume snapshots, validated fast restarts by deleting the local file, and experimented with snapshot behaviors. Apply the same pattern to additional datasets by pointing each one at the same `cayenne_file_path`, where each gets its own folder, and reusing the shared snapshot location. Spice keeps 28 days of snapshots and deletes older snapshot files itself, so an S3 lifecycle policy is optional; if you add one, expire snapshots after more than 28 days.
