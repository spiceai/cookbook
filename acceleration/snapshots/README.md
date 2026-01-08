# Accelerated Snapshots

This recipe walks through configuring database snapshots for file-mode accelerations so datasets avoid cold starts and recover quickly after restarts.

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
- Per-pod credentials set through `snapshots.params`.

For this recipe we load credentials from a `.env` file placed beside the pod definition.

Create `.env` in the same directory as `spicepod.yaml`:

```dotenv
S3_SNAPSHOT_KEY=<your-access-key>
S3_SNAPSHOT_SECRET=<your-secret-key>
S3_SNAPSHOT_REGION=<your-region>
```

If you prefer AWS profiles or environment variables set globally, skip the `.env` file and adjust the pod configuration accordingly.

## Step 3. Enable snapshots in the Spicepod

Open the `spicepod.yaml` that `spice init` created and replace its contents with the configuration below, updating the `snapshots.location` prefix to your bucket:

```yaml
version: v1
kind: Spicepod
name: quickstart

snapshots:
  enabled: true
  location: s3://my-snapshots-prod/quickstart/
  bootstrap_on_failure_behavior: fallback  # retry | fallback | warn (default)
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
    acceleration:
      enabled: true
      engine: duckdb
      mode: file
      snapshots: enabled             # enabled | bootstrap_only | create_only | disabled
      params:
        duckdb_file: taxi_trips.db   # Stored on local disk and bootstrapped from snapshots
```

Key settings to note:

- The top-level `snapshots` block defines the shared storage location and failure behavior.
- The dataset opts into snapshots by setting `acceleration.snapshots` to `enabled`.
- Each accelerated dataset must write to its own DuckDB file (`taxi_trips.db`).

## Step 4. Launch Spice and create the first snapshot

Start the runtime:

```bash
spice run
```

On first boot the acceleration file does not exist locally, so Spice loads from S3 and refreshes the dataset. After the initial refresh completes you should see a log similar to:

```bash
2025-10-09T12:53:15.146396Z  INFO runtime_acceleration::snapshot: Snapshot uploaded. dataset=taxi_trips snapshot=quickstart/month=2025-10/day=2025-10-09/dataset=taxi_trips/taxi_trips_20251009T125314Z.db size=2109440
```

Verify the snapshot appeared in your bucket using the AWS CLI or console.

## Step 5. Test snapshot bootstrap

Simulate a cold start by stopping the runtime and removing the local DuckDB file:

```bash
Ctrl+C  # stop spice run
rm taxi_trips.db
spice run
```

This time the startup logs show the snapshot bootstrap:

```bash
2025-10-09T12:50:44.270378Z  INFO runtime_acceleration::snapshot: Downloading snapshot. dataset=taxi_trips snapshot=s3://my-snapshots-prod/quickstart/month=2025-10/day=2025-10-09/dataset=taxi_trips/taxi_trips_20251009T082107Z.db snapshot_id=1
2025-10-09T12:50:44.412962Z  INFO runtime_acceleration::snapshot: Snapshot downloaded to taxi.db. dataset=taxi_trips snapshot=s3://my-snapshots-prod/quickstart/month=2025-10/day=2025-10-09/dataset=taxi_trips/taxi_trips_20251009T082107Z.db size=1847296
```

Spice skips the full refresh and immediately serves queries, dramatically reducing warm-up time.

## Step 6. Explore snapshot modes

Snapshots can be fine-tuned per dataset:

- `bootstrap_only`: download snapshots on startup but never write new ones (useful for read-only staging environments).
- `create_only`: generate snapshots after refreshes without bootstrapping from them.
- `disabled`: opt out for specific datasets even when the pod-wide snapshots block is present.

Try switching `acceleration.snapshots` to `bootstrap_only` and restarting to observe that Spice fetches the existing snapshot but skips writing a new version after refreshes.

## Step 7. Handle bootstrap failures

The top-level `bootstrap_on_failure_behavior` controls what happens if the newest snapshot fails to load:

- `retry`: keep trying the newest file until it succeeds (best when snapshots should never fail).
- `fallback`: automatically attempt older snapshot files.
- `warn`: log a warning and continue with an empty acceleration (default).

Set the value to `warn`, remove the snapshot file from S3, and restart to see how Spice warns and performs a regular refresh when no snapshot is available.

## Summary

You configured DuckDB accelerations to write and consume snapshots, validated fast restarts by deleting the local file, and experimented with snapshot behaviors. Apply the same pattern to additional datasets by pointing each one at its own acceleration file and reusing the shared snapshot location. Remember to manage S3 lifecycle policies so old snapshots expire on the cadence your environment requires.
