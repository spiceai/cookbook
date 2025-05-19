# Java JDBC Client with Parameterized Queries

This guide demonstrates how to use Java to query Spice via the Apache Arrow Flight SQL JDBC driver. The example connects to a local Spice OSS runtime, executes a parameterized query, and fetches results.

## Requirements

- Java 11 or newer
- [Maven](https://maven.apache.org/) installed
- [Spice CLI](https://docs.spiceai.org/getting-started) installed and Spice OSS runtime available

## Steps

### 1. Clone this repository

```bash
git clone https://github.com/spiceai/cookbook.git
cd clients/java
```

### 2. Build the project

```bash
mvn clean compile
```

### 3. Start Spice OSS

In a separate terminal, start the Spice OSS runtime:

```bash
spice run
```

### 4. Run the Java client

```bash
mvn exec:java -Dexec.mainClass="MessagingServiceApp"
```

Expected output:

```bash
Add-ons by account and service:
addon1
addon2
addon6

Add-ons by add-on type:
addon1
addon2
addon4
addon6
addon8
addon10
```

## Learn more

- [Spice OSS Documentation](https://docs.spiceai.org/)
- [Apache Arrow Flight SQL JDBC](https://arrow.apache.org/docs/java/reference/org/apache/arrow/flight/sql/FlightSqlClient.html)
