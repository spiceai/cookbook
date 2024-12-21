# Supabase (PostgreSQL Data Connector)

Follow these steps to get started with Supabase using the PostgreSQL Data Connector.

## Pre-requisites

- Supabase project.
- Spice is installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation).

## Steps

**Step 1.** From a Supabase project select `Project Settings` from the sidebar navigation.

**Step 2.** Navigate to `Database` under `Configuration`.

**Step 3.** Find the `Connection parameters` section.
![Connection parameters](https://imagedelivery.net/HyTs22ttunfIlvyd6vumhQ/02a30c41-072c-49cc-cba3-e29f35ca6800/public)

**Step 4.** Edit the `spicepod.yaml` file in this directory and replace `[remote_table_path]` with the path to the Supabase table to be accelerated, `[local_table_name]` with your desired name for the locally accelerated table, and the params section with the connection parameters from the Supabase project.

See the [datasets reference](https://docs.spiceai.org/reference/spicepod/datasets) for more dataset configuration options and [PostgreSQL Data Connector](https://docs.spiceai.org/data-connectors/postgres) for more options on configuring a PostgreSQL Data Connector.

Ensure the `PG_PASS` environment variable is set to the password for your Supabase instance. Environment variables can be specified on the command line when running the Spice runtime, or in a `.env` file in the same directory as `spicepod.yaml`.

```bash
echo "PG_PASS=<password>" > .env
```

To securely store the Supabase password, see [Secret Stores](https://docs.spiceai.org/components/secret-stores)

**Step 5.** Run the Spice runtime with `spice run` from this directory.

Follow the [getting started guide](https://docs.spiceai.org/getting-started) to get started with the Spice runtime.

**Step 6.** Run `spice sql` in a new terminal to start an interactive SQL query session against the Spice runtime.

For more information on using `spice sql`, see the [CLI reference](https://docs.spiceai.org/cli/reference/sql).

**Step 7.** Execute the query `select * from [local_table_name];` to see the Supabase table accelerated locally.
