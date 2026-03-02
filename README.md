# Spice.ai OSS Cookbook

Welcome to the Spice.ai OSS Cookbook—a comprehensive collection of recipes for building and deploying data & AI applications using Spice.ai. Each recipe is a self-contained example that demonstrates a specific use case, integration, or feature of Spice.ai, helping you accelerate your data and AI projects.

## Recipes

### Guides

- [Real-time Data Access Pattern Analysis](./guides/security-analyzer/README.md) - Use AI to analyze query patterns and detect potential security risks.

### Core scenarios

- [Federated SQL Query](./federation/README.md) - Query data from S3, PostgreSQL, and Dremio in a single query.
- [Cayenne Data Accelerator](./cayenne/README.md)
- [Async Queries](./async-queries/README.md) - Submit long-running SQL queries and retrieve results asynchronously.
- [Hybrid-Search](./search/README.md) - Combine keyword and vector search for improved retrieval.
- [AI SQL Function](./ai/README.md) - Use the `ai()` SQL function to invoke LLMs directly in SQL queries for text generation, sentiment analysis, and data enrichment.

### Sample Applications

- [Command Query Responsibility Segregation (CQRS)](./cqrs/README.md) - Sample application implementing the CQRS pattern with Spice.

### Models & AI - Connect data to hosted or local AI models

- [AI SQL Function](./ai/README.md) - Invoke LLMs directly in SQL queries for text generation and data enrichment.
- [Azure OpenAI Models](./azure_openai/README.md) - Use Azure OpenAI for search and chat.
- [Generative Visualizations](./generative-visualisations/README.md) - Generate SQL queries and visualizations from natural language.
- [Running Llama3 Locally](./llama/README.md) - Run Llama models locally from HuggingFace.
- [OpenAI Models](./models/openai/README.md) - Use OpenAI LLM and embedding models.
- [OpenAI SDK](./openai_sdk/README.md) - Use the OpenAI SDK to connect to models hosted on Spice.
- [LLM Memory](./llm-memory/README.md) - Persistent memory for language models.
- [Text to SQL (Tools)](./text-to-sql/README.md) - Query data with natural language.
- [Nvidia NIM on Kubernetes](./nvidia-nim/kubernetes/README.md) - Deploy Nvidia NIM on Kubernetes with GPUs.
- [Nvidia NIM on AWS EC2](./nvidia-nim/ec2/README.md) - Deploy Nvidia NIM on AWS GPU-optimized EC2 instances.
- [Searching GitHub Files](./search_github_files/README.md) - Search GitHub files with embeddings and vector search.
- [xAI Models](./models/xai/README.md) - Use xAI models such as Grok.
- [DeepSeek Model](./deepseek/README.md) - Use DeepSeek model through Spice.
- [Filesystem Hosted Model](./models/filesystem/README.md) - Use models hosted directly on filesystems.
- [Web Search Tools using Perplexity](./websearch/README.md) - Give LLMs web search access via Perplexity.
- [Language Model Evaluations](./evals/README.md) - Use Spice to evaluate language models.
- [LLM as a Judge](./llm-judge/README.md) - Define LLM judge models to evaluate other models.
- [OpenAI Responses API](./openai-responses-api/README.md) - Use OpenAI's Responses API with Spice
- [Model Context Protocol (MCP)](./mcp/README.md) - Connect to MCP servers and use MCP tools with Spice.

### Data Acceleration - Materializing & accelerating data locally with Data Accelerators

- [Cayenne Data Accelerator](./cayenne/README.md) - Accelerate data using Cayenne.
- [DuckDB Data Accelerator](./duckdb/accelerator/README.md) - Accelerate data using DuckDB.
- [Hashed Partitioning with DuckDB](./hashed_partitioning/README.md) - Prune data with hashed partitioning on categorical columns.
- [PostgreSQL Data Accelerator](./postgres/accelerator/README.md) - Materialize data into an attached PostgreSQL instance.
- [SQLite Data Accelerator](./sqlite/accelerator/README.md) - Accelerate data using SQLite.
- [Database Snapshots](./acceleration/snapshots/README.md) - Bootstrap accelerations from object storage to skip cold starts.
- [Apache Arrow Data Accelerator](./arrow/README.md) - Accelerate data using in-memory Arrow.
- [Accelerated Views](./views/README.md) - Pre-calculate and materialize derived data for faster queries.
- [Dataset Partitioning](./acceleration/partitioning/README.md) - Partition accelerated datasets to improve query performance.

### Consuming and visualizing data with clients

- [Sales BI (Apache Superset)](./sales-bi/README.md) - Visualize data in Spice with Apache Superset.
- [Grafana Datasource](./grafana-datasource/README.md) - Add Spice as a Grafana datasource.
- [Python ADBC Client](./clients/adbc/README.md) - Query Spice using ADBC with Python.
- [Java JDBC Client](./clients/java/README.md) - Query Spice using JDBC with Java.
- [Scala JDBC Client](./clients/scala/README.md) - Query Spice using JDBC with Scala.

### Connecting to Data Sources with Data Connectors

- [Postgres Data Connector](./postgres/connector/README.md)
  - [AWS RDS PostgreSQL](./postgres/rds/README.md)
  - [Supabase](./postgres/supabase/README.md)
- [MySQL Data Connector](./mysql/connector/README.md)
  - [AWS RDS Aurora (MySQL Compatible)](./mysql/rds-aurora/README.md)
  - [PlanetScale](./mysql/planetscale/README.md)
- [Clickhouse Data Connector](./clickhouse/README.md) - Connect to ClickHouse as a data source.
- [Databricks Connector](./databricks/README.md) - Delta Lake and Spark Connect.
- [Delta Lake Connector](./delta-lake/README.md) - Query data from Delta Lake tables.
- [Debezium CDC Data Connector](./cdc-debezium/README.md) - Stream changes from Postgres to Spice.
  - [Debezium CDC SASL/SCRAM from MySQL](./cdc-debezium/sasl-scram/README.md) - Stream changes from MySQL using SASL/SCRAM.
- [DynamoDB Data Connector](./dynamodb/README.md) - Query data from an AWS-hosted DynamoDB table.
  - [DynamoDB Streams](./dynamodb/streams/README.md) - Stream real-time changes from DynamoDB tables.
- [Dremio Data Connector](./dremio/README.md) - Connect to a Dremio instance.
- [DuckDB Data Connector](./duckdb/connector/README.md) - Use a DuckDB database with sample TPCH data.
- [File Data Connector](./file/README.md) - Query data from local files.
- [FTP Data Connector](./ftp/README.md) - Query data from an FTP server.
- [Glue Data Connector](./glue/README.md) - Query tables in an AWS Glue Data Catalog.
- [GitHub Data Connector](./github/README.md) - Query GitHub repository data.
- [GraphQL Data Connector](./graphql/README.md) - Connect to GraphQL endpoints.
- [HTTP Data Connector](./http/README.md) - Query data from HTTP(s) endpoints like REST APIs.
- [MongoDB Data Connector](./mongodb/connector/README.md) - Connect to MongoDB as a data source.
- [MSSQL (Microsoft SQL Server) Data Connector](./mssql/README.md) - Query across multiple SQL Server instances.
- [ODBC Data Connector](./odbc/README.md) - Connect to databases via ODBC.
- [Amazon Redshift](./redshift/README.md) - Read and write TPC-H data with Amazon Redshift.
- [Oracle Data Connector](./oracle/README.md) - Connect to and accelerate data from Oracle.
- [S3 Data Connector](./s3/README.md) - Query data from an S3 bucket.
- [ScyllaDB Data Connector](./scylladb/README.md) - Query data from ScyllaDB clusters using federated SQL.
- [SharePoint/OneDrive for Business Data Connector](./sharepoint/README.md) - Query documents in SharePoint.
- [SMB Data Connector](./smb/README.md) - Query data files from SMB/CIFS network shares.
- [Snowflake Data Connector](./snowflake/README.md) - Access a Snowflake database.
- [Spice.ai Cloud Platform Data Connector](./spiceai/README.md) - Connect to Spice.ai Cloud Platform datasets.
- [Apache Spark Data Connector](./spark/README.md) - Read data from an Apache Spark instance.
- [Apache Kafka Data Connector](./kafka/README.md) - Stream data from Kafka with federated queries.
- [IMAP Data Connector](./imap/README.md) - Connect to an IMAP email server.
  - [Connecting to an Outlook mailbox](./imap/outlook.md)

### Connecting to Data Sources with Catalog Connectors

- [Spice.ai Cloud Platform Catalog Connector](./catalogs/spiceai/README.md) - Query datasets in Spice.ai Cloud Platform.
- [Databricks Unity Catalog Connector](./catalogs/databricks/README.md) - Query Databricks Unity Catalog tables.
- [Unity Catalog Connector](./catalogs/unity_catalog/README.md) - Query an open-source Unity Catalog instance.
- [Iceberg Catalog Connector](./catalogs/iceberg/README.md) - Query and write to Iceberg tables.
- [Iceberg Hadoop Catalog Connector](./catalogs/iceberg-hadoop/README.md) - Connect to Hadoop catalogs on S3-compatible storage.
- [Glue Catalog Connector](./catalogs/glue/README.md) - Query tables in an AWS Glue Data Catalog.

### Using Vector Engines

- [Amazon S3 Vectors](./vectors/s3-vectors/README.md) - Use S3 as a vector engine for embeddings and similarity search.

## Search

- [Hybrid-Search](./search/README.md) - Combine keyword and vector search for improved retrieval.
- [Full-Text Search](./full-text-search/README.md) - Retrieve records matching keywords using BM25 scoring.

### Deployment and Installation

- [Deploying to Kubernetes](./kubernetes/README.md)
- [Running in Docker](./docker/README.md)
- [Sidecar Deployment Architecture](./architectures/sidecar/README.md)
- [Microservice Deployment Architecture](./architectures/microservice/README.md)

### Performance

- [TPC-H Benchmarking](./tpc-h/README.md) - Run TPC-H benchmark queries.
- [SQL Results Caching](./caching/sql_results/README.md) - Cache query results in memory for faster repeated queries.
- [Caching Accelerator](./caching/accelerator/README.md) - HTTP response caching with SWR support.
- [Indexes on Accelerated Data](./acceleration/indexes/README.md) - Create indexes to improve query performance.

### Acceleration Data Configuration

- [Data Retention Policy](./retention/README.md) - Evict data older than a specified duration.
- [Refresh Data Window](./refresh-data-window/README.md) - Filter data refresh to only recent data.
- [Advanced Data Refresh](./acceleration/data-refresh/README.md) - Configure and tune data refresh for accelerated datasets.
- [Data Quality with Constraints](./acceleration/constraints/README.md) - Enforce data quality constraints on accelerated datasets.

## Client SDKs - Recipes for querying data from Spice with language-specific SDKs

- [Rust SDK](client-sdk/spice-rs-sdk-sample/README.md)
- [Python SDK](client-sdk/spicepy-sdk-sample/README.md)
- [Go SDK](client-sdk/gospice-sdk-sample/README.md)
- [JavaScript SDK (Node.js)](client-sdk/spice.js-sdk-sample/README.md) - Query data using the `@spiceai/spice` npm package.
- [Java SDK](client-sdk/spice-java-sdk-sample/README.md)

### Security

- [Encryption in transit using TLS](./tls/README.md)
- [API Key Authentication](./api_key/README.md)

### Advanced Topics

- [Local dataset replication](./localpod/README.md) - Link datasets in a parent/child relationship.
- [Distributed Query](./distributed/README.md) - Run queries distributed across multiple nodes.
- [JSON Strings](./json_strings/README.md) - Work with JSON strings using JSON functions.
