# SharePoint Data Connector Recipe

Use the SharePoint Data Connector to query documents stored in SharePoint from Spice.

## Requirements

- [Spice CLI](https://docs.spiceai.org/getting-started) installed.
- Access to a SharePoint instance, and know the associated tenant ID.
  - (Optional) Upload relevant documents to the user's root sharepoint directory

## Follow these steps

**Step 1.** Login in Sharepoint via Spice CLI.

```bash
export TENANT_ID=<YOUR_TENANT_ID>
spice login sharepoint --tenant-id $TENANT_ID --client-id f2b3116e-b4c4-464f-80ec-73cd9d9886b4
```

**Step 2.** Start the Spice runtime.

```bash
spice run
```

Confirm in the terminal output that the `important_documents` dataset has been loaded:

```bash
Spice.ai runtime starting...
2024-09-16T12:34:56.789012Z  INFO spiced: Metrics listening on 127.0.0.1:9090
2024-09-16T12:34:56.789012Z  INFO runtime: Loaded dataset: important_documents
```

**Step 3.** Run queries against the dataset using the Spice SQL REPL.

_In a new terminal_, start the Spice SQL REPL:

```bash
spice sql
```

Query the `important_documents` dataset.

```sql
SELECT web_url FROM important_documents;
```

## Learn more

- [SharePoint Data Connector Documentation](https://docs.spiceai.org/components/data-connectors/sharepoint).
- [Spice CLI Reference](https://docs.spiceai.org/cli/reference/sql) for SQL queries.
- [Datasets Reference](https://docs.spiceai.org/reference/spicepod/datasets) for more configuration options.
