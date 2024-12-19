# Searching GitHub Files Recipe

This recipe demonstrates how to create embeddings for GitHub files and perform vector-based searches.

## Prerequisites

- Ensure you have the Spice CLI installed. Follow the [Getting Started](https://docs.spiceai.org/getting-started) if you haven't done so.
- Populate `.env`.
  - `GITHUB_TOKEN`: With a [personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-personal-access-token-classic).
  - `SPICE_OPENAI_API_KEY`: A valid OpenAI API key (or equivalent).

## SQL Search

1. Execute a Basic SQL Query to perform keyword searches within your dataset:

```shell
spice sql
```

Then:

```sql
SELECT path
FROM spiceai.files
WHERE
    LOWER(content) LIKE '%errors%'
    AND NOT contains(path, 'docs/release_notes');
```

Result:

```shell
+------------------------------+
| path                         |
+------------------------------+
| docs/criteria/definitions.md |
| docs/dev/error_handling.md   |
| docs/dev/style_guide.md      |
+------------------------------+
```

## Utilizing Vector-Based Search

1. In the `spicepod.yaml`, uncomment the `datasets[0].columns[0].embeddings`.
2. Restart the spiced.
3. Perform a basic search

    ```shell
    curl -XPOST http://localhost:8090/v1/search \
        -H "Content-Type: application/json" \
        -d "{
        \"datasets\": [\"spiceai.files\"],
        \"text\": \"testing\",
        \"where\": \"not contains(path, 'docs/release_notes')\",
        \"additional_columns\": [\"download_url\"],
        \"limit\": 2
        }"
    ```

    Result:

    ```json
    {
        "matches": [
            {
                "value": "# Criteria Definitions\n\n## RC\n\nAcronym for \"Release Candidate\". Identifies a version that is eligible for general/stable release.\n\n## Major Bug\n\nA major bug...",
                "score": 0.8142404969373118,
                "dataset": "spiceai.files",
                "primary_key": {
                    "path": "docs/criteria/definitions.md"
                },
                "metadata": {
                    "download_url": "https://raw.githubusercontent.com/spiceai/spiceai/trunk/docs/criteria/definitions.md"
                }
            },
            {
                "value": "# Spice.ai Project Docs\n\nThe project docs for contributors and community. For user documentation of the Spice.ai...",
                "score": 0.8001740819999499,
                "dataset": "spiceai.files",
                "primary_key": {
                    "path": "docs/README.md"
                },
                "metadata": {
                    "download_url": "https://raw.githubusercontent.com/spiceai/spiceai/trunk/docs/README.md"
                }
            }
        ],
        "duration_ms": 48
    }
    ```

### Additional Configuration - Chunking

1. Update the spicepod `datasets[0].columns[0].embeddings.chunking.enabled: true`.
2. Restart the spiced.
3. Rerun the search

    ```shell
    curl -XPOST http://localhost:8090/v1/search \
    -H 'Content-Type: application/json' \
    -d "{
        \"datasets\": [\"spiceai.files\"],
        \"text\": \"errors\",
        \"where\": \"not contains(path, 'docs/release_notes')\",
        \"additional_columns\": [\"download_url\"],
        \"limit\": 2
    }"
    ```

    Result:

    ```json
    {
        "matches": [
            {
                "value": "# Spice.ai Extensibility\n\nThis document is an overview of all the interfaces and extension points in Spice.ai.\n\n| Component       | Description                                                                                                                                | Definition Link                                            |\n| --------------- | -----------------------------",
                "score": 0.7811596783985292,
                "dataset": "spiceai.files",
                "primary_key": {
                    "path": "docs/EXTENSIBILITY.md"
                },
                "metadata": {
                    "download_url": "https://raw.githubusercontent.com/spiceai/spiceai/trunk/docs/EXTENSIBILITY.md"
                }
            },
            {
                "value": "# Guidelines for error handlling\n\n## Rust Error Traits\n\nIn Rust, the Error trait implements both the Debug and Display traits. All user-facing errors should use the Display trait, not the Debug trait.\n\ni.e.\n\nGood (uses Display trait)\n```rust\nif let Err(user_facing_err) = upload_data(datasource) {\n    tracing::error!(\"Unable to upload data to {datasource}: {user_facing_err}\");\n}\n``",
                "score": 0.8009972672322939,
                "dataset": "spiceai.files",
                "primary_key": {
                    "path": "docs/dev/error_handling.md"
                },
                "metadata": {
                    "download_url": "https://raw.githubusercontent.com/spiceai/spiceai/trunk/docs/dev/error_handling.md"
                }
            }
        ],
        "duration_ms": 48
    }
    ```

4. Rerun the search, and retrieve the full document (as an entry in `additional_coluumns`).

    ```shell
    curl -XPOST http://localhost:8090/v1/search \
    -H 'Content-Type: application/json' \
    -d "{
        \"datasets\": [\"spiceai.files\"],
        \"text\": \"errors\",
        \"where\": \"not contains(path, 'docs/release_notes')\",
        \"additional_columns\": [\"download_url\" , \"content\"],
        \"limit\": 2
    }"
    ```

    Result:

    ```json
    {
        "matches": [
            {
                "value": "# Guidelines for error handlling\n\n## Rust Error Traits\n\nIn Rust, the Error trait implements both the Debug and Display traits. All user-facing errors should use the Display trait, not the Debug trait.\n\ni.e.\n\nGood (uses Display trait)\n```rust\nif let Err(user_facing_err) = upload_data(datasource) {\n    tracing::error!(\"Unable to upload data to {datasource}: {user_facing_err}\");\n}\n``",
                "score": 0.8009972672322939,
                "dataset": "spiceai.files",
                "primary_key": {
                    "path": "docs/dev/error_handling.md"
                },
                "metadata": {
                    "content": "# Guidelines for error handlling\n\n## Rust Error Traits\n\nIn Rust, the Error trait implements both the Debug and Display traits. All user-facing errors should use the Display trait, not the Debug trait.\n\ni.e.\n\nGood (uses Display trait)\n```rust\nif let Err(user_facing_err) = upload_data(datasource) {\n    tracing::error!(\"Unable to upload data to {datasource}: {user_facing_err}\");\n}\n```\n\nBad (uses Debug trait `:?`)\n```rust\nif let Err(user_facing_err) = upload_data(datasource) {\n    tracing::error!(\"Unable to upload data to {datasource}: {user_facing_err:?}\");\n}\n```\n\n## Displaying errors to the user\n\n1. **Specific and Actionable**: The error message should be specific enough to help the user understand what went wrong and how to fix it.\n\n> Example:\n> `Cannot connect to postgres. Authentication failed. Ensure that the username and password are correctly configured in the spicepod.` is better than `Error connecting to postgres`.\n\n1. **Avoid Debugging Information**: The error message should not contain any debugging information. This includes stack traces, Rust debug representations, or any other technical information that the user cannot act on.\n  - It can be helpful for developers to access this, but it should be gated behind a debug mode/log level/log file, etc and not shown by default.\n1. **Internal/Unknown Errors**: If the error is internal to the application or unknown, the error message should be generic and not expose any internal details. The error message should indicate how to report the error to the developers.\n  - Strive to have as few of these as possible.\n\n## Data Connector Errors\n\n`dataconnector` module provides common bucket of errors with predefined messages. Each data connector implementation should use these to provide consistent error messages to the user.\n\nhttps://github.com/spiceai/spiceai/blob/2a9fab7905737e1af182e17f40aecc5c4b5dd236/crates/runtime/src/dataconnector.rs#L113-L169\n\nExample: postgres connector catches erros from underlying postgres crate and maps them to `DataConnectorError::...`.\n\nhttps://github.com/spiceai/spiceai/blob/2a9fab7905737e1af182e17f40aecc5c4b5dd236/crates/runtime/src/dataconnector/postgres.rs#L54-L76\n\nIf a new error is needed, it should be added to the `DataConnectorError` enum and the error message should be specific and actionable.\n\nIf it is not possible to provide a specific error message, use common  `DataConnectorError::InvalidConfiguration` to wrap the error.\n",
                    "download_url": "https://raw.githubusercontent.com/spiceai/spiceai/trunk/docs/dev/error_handling.md"
                }
            },
            {
                "value": "# Spice.ai Extensibility\n\nThis document is an overview of all the interfaces and extension points in Spice.ai.\n\n| Component       | Description                                                                                                                                | Definition Link                                            |\n| --------------- | -----------------------------",
                "score": 0.7811596783985292,
                "dataset": "spiceai.files",
                "primary_key": {
                    "path": "docs/EXTENSIBILITY.md"
                },
                "metadata": {
                    "content": "# Spice.ai Extensibility\n\nThis document is an overview of all the interfaces and extension points in Spice.ai.\n\n| Component       | Description                                                                                                                                | Definition Link                                            |\n| --------------- | ------------------------------------------------------------------------------------------------------------------------------------       | ------------------------------------------------------     |\n| [Data Connector]   | Represents the source of data to the Spice.ai runtime. Specifies how to retrieve data, stream data updates, and write data back.           | [dataconnector.rs](../crates/runtime/src/dataconnector.rs) |\n| [Data Accelerator]     | Used by the runtime to store accelerated data locally. Specify which data accelerator to use via `engine` & `mode` fields.                   | [dataaccelerator.rs](../crates/runtime/src/databackend.rs)     |\n| [Catalog Connector]     | Catalog Connectors connect to external catalog providers and make their tables available for federated SQL query in Spice. Implemented as an optional function on the `DataConnector` trait.                                                                                                  | [dataconnector.rs](../crates/runtime/src/dataconnector.rs)     |\n| [Secret Stores]    | A Secret Store is a location where secrets are stored and can be used to store sensitive data, like passwords, tokens, and secret keys.                               | [secrets.rs](../crates/runtime/src/secrets.rs)   |\n| [Models]     | A machine-learning (ML) or language model (LLM) to load for inferencing.          | [modelsource.rs](../crates/model_components/src/model.rs)     |\n| Embeddings    | Embeddings map high-dimensional data to a lower-dimensional vector space.         | [embeddings.rs](../crates/llms/src/embeddings/mod.rs)     |\n\n[Data Connector]: https://docs.spiceai.org/components/data-connectors\n[Data Accelerator]: https://docs.spiceai.org/components/data-accelerators\n[Catalog Connector]: https://docs.spiceai.org/components/catalogs\n[Secret Stores]: https://docs.spiceai.org/components/secret-stores\n[Models]: https://docs.spiceai.org/components/models",
                    "download_url": "https://raw.githubusercontent.com/spiceai/spiceai/trunk/docs/EXTENSIBILITY.md"
                }
            }
        ],
        "duration_ms": 45
    }
    ```

## Pre-existing embeddings

Spiced can perform vector search on table that already have the required embedding columns. To try this:

1. Run a new `spiced` instance pointing to the currently running `spiced`.

    ```shell
    cd child/
    spiced --http 127.0.0.1:8091 --flight 127.0.0.1:50061 --open_telemetry 127.0.0.1:50062
    ```

2. Rerun the search, this time against the child `spiced` (port `8091`)

    ```shell
    curl -XPOST http://localhost:8091/v1/search \
    -H 'Content-Type: application/json' \
    -d "{
        \"datasets\": [\"spiceai.files\"],
        \"text\": \"errors\",
        \"where\": \"not contains(path, 'docs/release_notes')\",
        \"additional_columns\": [\"download_url\"],
        \"limit\": 2
    }"
    ```

    Result:

    ```json
    {
        "matches": [
            {
                "value": "# Spice.ai Extensibility\n\nThis document is an overview of all the interfaces and extension points in Spice.ai.\n\n| Component       | Description                                                                                                                                | Definition Link                                            |\n| --------------- | -----------------------------",
                "score": 0.7811596783985292,
                "dataset": "spiceai.files",
                "primary_key": {
                    "path": "docs/EXTENSIBILITY.md"
                },
                "metadata": {
                    "download_url": "https://raw.githubusercontent.com/spiceai/spiceai/trunk/docs/EXTENSIBILITY.md"
                }
            },
            {
                "value": "# Guidelines for error handlling\n\n## Rust Error Traits\n\nIn Rust, the Error trait implements both the Debug and Display traits. All user-facing errors should use the Display trait, not the Debug trait.\n\ni.e.\n\nGood (uses Display trait)\n```rust\nif let Err(user_facing_err) = upload_data(datasource) {\n    tracing::error!(\"Unable to upload data to {datasource}: {user_facing_err}\");\n}\n``",
                "score": 0.8009972672322939,
                "dataset": "spiceai.files",
                "primary_key": {
                    "path": "docs/dev/error_handling.md"
                },
                "metadata": {
                    "download_url": "https://raw.githubusercontent.com/spiceai/spiceai/trunk/docs/dev/error_handling.md"
                }
            }
        ],
        "duration_ms": 48
    }
    ```
