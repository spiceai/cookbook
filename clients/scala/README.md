# Scala JDBC Client with Parameterized Queries

Works with `v1.0+`

This guide demonstrates how to use Scala to query Spice via the Apache Arrow Flight SQL JDBC driver. The example connects to a local Spice OSS runtime, executes a parameterized query, and fetches results.

## Requirements

- JDK 17 or newer
- [sbt](https://www.scala-sbt.org/) installed
- [Spice CLI](https://docs.spiceai.org/getting-started) installed and Spice OSS runtime available

## Recipe Steps

### 1. Clone this repository

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/clients/scala
```

### 2. Install dependencies

Install sbt and JDK 17:

```bash
brew install openjdk@17
brew install sbt
export JAVA_HOME="$(brew --prefix openjdk@17)/libexec/openjdk.jdk/Contents/Home"
export PATH="$JAVA_HOME/bin:$PATH"
```

### 3. Start Spice OSS

In a separate terminal, start the Spice OSS runtime:

```bash
spice run
```

### 4. Run the Scala client

```bash
sbt clean compile
sbt run
```

Expected output:

```
[info] Add-ons by account and service:
[info] addon6
[info] addon2
[info] addon1
[info] Add-ons by add-on type:
[info] addon1
[info] addon2
[info] addon4
[info] addon6
[info] addon8
[info] addon10
```

## Learn more

- [Spice OSS Documentation](https://docs.spiceai.org/)
- [Apache Arrow Flight SQL JDBC](https://arrow.apache.org/java/current/flight_sql_jdbc_driver.html)
