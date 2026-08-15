# Spice with Java SDK

Works with `v1.0+`

Use the [Spice Java SDK](https://github.com/spiceai/spice-java) to query Spice from Java.

## What This Sample Includes

- `App.java`: Query a local Spice runtime.
- `Cloud.java`: Query Spice.ai Cloud with inline replacement values.

## Prerequisites

- JDK 17+
- [Maven](https://maven.apache.org/install.html)
- [Spice CLI](https://docs.spiceai.org/getting-started) for local mode

## Local Quick Start (Maven)

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/client-sdk/spice-java-sdk-sample
```

Start Spice runtime in one terminal:

```bash
spice run
```

Sample runtime logs:

```text
Spice.ai runtime starting...
2024-07-16T19:16:34.197072Z  INFO runtime::init::caching: Initialized sql results cache; max size: 128.00 MiB, item ttl: 1s, hashing algorithm: XXH3, encoding: none
2024-07-16T19:16:34.197759Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2024-07-16T19:16:34.197770Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2024-07-16T19:16:34.885084Z  INFO runtime::init::dataset: Dataset taxi_trips registered (s3://spiceai-demo-datasets/taxi_trips/2024/), acceleration (arrow, 10s refresh), results cache enabled.
2024-07-16T19:16:34.886257Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset taxi_trips
2024-07-16T19:16:40.494038Z  INFO runtime::accelerated_table::refresh_task: Loaded 2,964,624 rows (421.71 MiB) for dataset taxi_trips in 5s 607ms.
```

In another terminal, compile and run:

```bash
mvn clean compile exec:exec
```

Sample output:

```text
VendorID        tpep_pickup_datetime    fare_amount
2       2024-01-14T08:32:55     70.0
1       2024-01-14T08:13:28     70.0
2       2024-01-14T08:31:56     6.5
1       2024-01-14T08:15:17     16.3
1       2024-01-14T08:49:57     10.7
2       2024-01-14T08:28:37     14.2
2       2024-01-14T08:42:59     12.0
2       2024-01-14T08:49:26     7.2
1       2024-01-14T08:10:31     7.2
1       2024-01-14T08:17:35     5.1
```

## Spice.ai Cloud Quick Start

Set your API key for the commands in this README:

```bash
export SPICE_API_KEY="your_api_key"
```

The cloud snippet keeps an inline API key placeholder by design. Replace the API key placeholder in `src/main/java/ai/spice/example/Cloud.java` with `${SPICE_API_KEY}`, then run:

```bash
mvn exec:exec -Dexec.mainClass="ai.spice.example.Cloud"
```

## Advanced: Gradle Workflow

This sample also supports Gradle.

### Gradle Prerequisites

1. JDK 17 or higher.
2. [Gradle](https://gradle.org/install/) 7.0 or later.

### Initialize Gradle Wrapper

```bash
gradle wrapper
```

Sample output:

```text
Welcome to Gradle 8.9!

Here are the highlights of this release:
 - Enhanced Error and Warning Messages
 - IDE Integration Improvements
 - Daemon JVM Information

For more details see https://docs.gradle.org/8.9/release-notes.html

Starting a Gradle Daemon (subsequent builds will be faster)

BUILD SUCCESSFUL in 2s
1 actionable task: 1 executed
```

### Build with Gradle

```bash
./gradlew clean build
```

Sample output:

```text
Downloading https://services.gradle.org/distributions/gradle-8.9-bin.zip
............10%.............20%.............30%.............40%.............50%.............60%.............70%.............80%.............90%.............100%
Starting a Gradle Daemon, 1 incompatible Daemon could not be reused, use --status for details

BUILD SUCCESSFUL in 40s
6 actionable tasks: 5 executed, 1 up-to-date
```

### Run with Gradle

```bash
./gradlew run
```

Sample output:

```text
> Task :run
[main] INFO org.apache.arrow.memory.BaseAllocator - Debug mode disabled. Enable with the VM option -Darrow.memory.debug.allocator=true.
[main] INFO org.apache.arrow.memory.DefaultAllocationManagerOption - allocation manager type not specified, using netty as the default type
[main] INFO org.apache.arrow.memory.CheckAllocator - Using DefaultAllocationManager at memory-netty/16.1.0/c608dab8b8e59d4dc1609a645340f83fa4a145ed/arrow-memory-netty-16.1.0.jar!/org/apache/arrow/memory/netty/DefaultAllocationManagerFactory.class
VendorID        tpep_pickup_datetime    fare_amount
2       2024-01-02T14:54:44     56.9
1       2024-01-02T14:58:35     25.5
1       2024-01-02T14:21:32     12.1
1       2024-01-02T14:36:26     10.0
2       2024-01-02T14:25:25     38.0
2       2024-01-02T14:41:57     44.3
2       2024-01-02T14:47:52     66.0
2       2024-01-02T14:01:17     21.9
2       2024-01-02T14:27:29     44.3
2       2024-01-02T14:54:39     8.6
```

## Links

- [Spice Java SDK](https://github.com/spiceai/spice-java)
- [Maven Central](https://central.sonatype.com/artifact/ai.spice/spice)
- [Spice.ai Cloud](https://spice.ai)
- [Spice.ai documentation](https://docs.spiceai.org)
