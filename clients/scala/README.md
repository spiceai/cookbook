# Scala JDBC Client with Parameterized Queries

This guide demonstrates how to use Scala to query Spice via the Apache Arrow Flight SQL JDBC driver. The example connects to a local Spice OSS runtime, executes a parameterized query, and fetches results.

## Requirements

- Scala 2.13+
- [sbt](https://www.scala-sbt.org/) installed
- [Spice CLI](https://docs.spiceai.org/getting-started) installed and Spice OSS runtime available

## Recipe Steps

### 1. Clone this repository

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/clients/scala
```

### 2. Install dependencies

Ensure you have sbt and Scala installed:

```bash
brew install scala
brew install sbt
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
[info] MessagingServiceAddOn(account123,service456,addon6,type789,{\feature\":\"mms_support\"}",2025-04-06 16:00:00.0,2025-04-07 23:25:00.0)
[info] MessagingServiceAddOn(account123,service456,addon2,type789,{\feature\":\"mms_support\"}",2025-04-02 19:30:00.0,2025-04-03 16:15:00.0)
[info] MessagingServiceAddOn(account123,service456,addon1,type789,{\feature\":\"sms_analytics\"}",2025-04-01 17:00:00.0,2025-04-01 17:00:00.0)
[info] Add-ons by add-on type:
[info] MessagingServiceAddOn(account123,service456,addon1,type789,{\feature\":\"sms_analytics\"}",2025-04-01 17:00:00.0,2025-04-01 17:00:00.0)
[info] MessagingServiceAddOn(account123,service456,addon2,type789,{\feature\":\"mms_support\"}",2025-04-02 19:30:00.0,2025-04-03 16:15:00.0)
[info] MessagingServiceAddOn(account456,service456,addon4,type789,{\feature\":\"sms_analytics\"}",2025-04-04 15:20:00.0,2025-04-05 18:10:00.0)
[info] MessagingServiceAddOn(account123,service456,addon6,type789,{\feature\":\"mms_support\"}",2025-04-06 16:00:00.0,2025-04-07 23:25:00.0)
[info] MessagingServiceAddOn(account789,service456,addon8,type789,{\feature\":\"sms_analytics\"}",2025-04-08 20:15:00.0,2025-04-09 17:40:00.0)
[info] MessagingServiceAddOn(account456,service789,addon10,type789,{\feature\":\"mms_support\"}",2025-04-10 16:45:00.0,2025-04-10 16:45:00.0)
```

## Learn more

- [Spice OSS Documentation](https://docs.spiceai.org/)
- [Apache Arrow Flight SQL JDBC](https://arrow.apache.org/docs/java/reference/org/apache/arrow/flight/sql/FlightSqlClient.html)
