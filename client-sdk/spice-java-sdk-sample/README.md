# Spice with Java SDK

Use [Spice.ai Java SDK](https://github.com/spiceai/spice-java) to query [Spice.ai](https://github.com/spiceai/spiceai) from Java.

## Clone this sample

```shell
git clone https://github.com/spiceai/cookbook.git
cd cookbook/client-sdk/spice-java-sdk-sample
```

## Start spice runtime

[Install Spice.ai OSS](https://docs.spiceai.org/getting-started) and start Spice runtime:

```shell
spice run
```

```shell
Spice.ai runtime starting...
2024-07-16T19:16:34.192387Z  INFO spiced: Metrics listening on 127.0.0.1:9090
2024-07-16T19:16:34.195177Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2024-07-16T19:16:34.197072Z  INFO runtime: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
2024-07-16T19:16:34.197759Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2024-07-16T19:16:34.197770Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2024-07-16T19:16:34.885084Z  INFO runtime: Dataset taxi_trips registered (s3://spiceai-demo-datasets/taxi_trips/2024/), acceleration (arrow, 10s refresh), results cache enabled.
2024-07-16T19:16:34.886257Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset taxi_trips
2024-07-16T19:16:40.494038Z  INFO runtime::accelerated_table::refresh_task: Loaded 2,964,624 rows (421.71 MiB) for dataset taxi_trips in 5s 607ms.
```

## Maven Users

### Prerequisites

1. A Java Development Kit (JDK), version 17 or higher - for example [OracleJDK](https://www.oracle.com/java/technologies/downloads/). Installed version can be verified with `java -version`.
1. [Maven](https://maven.apache.org/install.html). Verify the Maven installation with: `mvn -version`

### Build sample

```shell
mvn clean compile
```

```shell
[INFO] Scanning for projects...
[INFO] 
[INFO] ------------------< ai.spice.example:taxi-trips-app >-------------------
[INFO] Building taxi-trips-app 1.0-SNAPSHOT
[INFO]   from pom.xml
[INFO] --------------------------------[ jar ]---------------------------------
[INFO] 
[INFO] --- clean:3.2.0:clean (default-clean) @ taxi-trips-app ---
[INFO] Deleting /Users/sg/spice/samples/client-sdk/spice-java-sdk-sample/target
[INFO] 
[INFO] --- resources:3.3.1:resources (default-resources) @ taxi-trips-app ---
[WARNING] Using platform encoding (UTF-8 actually) to copy filtered resources, i.e. build is platform dependent!
[INFO] skip non existing resourceDirectory /Users/sg/spice/samples/client-sdk/spice-java-sdk-sample/src/main/resources
[INFO] 
[INFO] --- compiler:3.13.0:compile (default-compile) @ taxi-trips-app ---
[INFO] Recompiling the module because of changed source code.
[WARNING] File encoding has not been set, using platform encoding UTF-8, i.e. build is platform dependent!
[INFO] Compiling 1 source file with javac [debug target 1.8] to target/classes
[WARNING] bootstrap class path is not set in conjunction with -source 8
  not setting the bootstrap class path may lead to class files that cannot run on JDK 8
    --release 8 is recommended instead of -source 8 -target 1.8 because it sets the bootstrap class path automatically
[WARNING] source value 8 is obsolete and will be removed in a future release
[WARNING] target value 8 is obsolete and will be removed in a future release
[WARNING] To suppress warnings about obsolete options, use -Xlint:-options.
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Total time:  0.712 s
[INFO] Finished at: 2024-07-16T12:43:33-07:00
[INFO] ------------------------------------------------------------------------

```

### Run sample

> **IMPORTANT:** The Spice SDK uses the Apache Arrow Flight library, which requires the `--add-opens=java.base/java.nio=ALL-UNNAMED` parameter to operate.
>
> Read [Apache Arrow Java Compatibility](https://arrow.apache.org/docs/java/install.html#java-compatibility) for more details.

```shell
_JAVA_OPTIONS="--add-opens=java.base/java.nio=ALL-UNNAMED" mvn exec:java -Dexec.mainClass="ai.spice.example.App"
```

```shell
Picked up _JAVA_OPTIONS: --add-opens=java.base/java.nio=ALL-UNNAMED
[INFO] Scanning for projects...
[INFO] 
[INFO] ------------------< ai.spice.example:taxi-trips-app >-------------------
[INFO] Building taxi-trips-app 1.0-SNAPSHOT
[INFO]   from pom.xml
[INFO] --------------------------------[ jar ]---------------------------------
[INFO] 
[INFO] --- exec:3.3.0:java (default-cli) @ taxi-trips-app ---
[ai.spice.example.App.main()] INFO org.apache.arrow.memory.BaseAllocator - Debug mode disabled. Enable with the VM option -Darrow.memory.debug.allocator=true.
[ai.spice.example.App.main()] INFO org.apache.arrow.memory.DefaultAllocationManagerOption - allocation manager type not specified, using netty as the default type
[ai.spice.example.App.main()] INFO org.apache.arrow.memory.CheckAllocator - Using DefaultAllocationManager at memory-netty/16.1.0/arrow-memory-netty-16.1.0.jar!/org/apache/arrow/memory/netty/DefaultAllocationManagerFactory.class
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

## Gradle Users

### Prerequisites

1. A Java Development Kit (JDK), version 17 or higher - for example [OracleJDK](https://www.oracle.com/java/technologies/downloads/). Installed version can be verified with `java -version`.
1. [Gradle Build Tools version 7.0 or later](https://gradle.org/install/). Installed version can be verified with `gradle -v`.

### Init gradle wrapper

```shell
gradle wrapper
```

```shell
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

### Build recipe

```shell
./gradlew clean build
```

```shell
Downloading https://services.gradle.org/distributions/gradle-8.9-bin.zip
............10%.............20%.............30%.............40%.............50%.............60%.............70%.............80%.............90%.............100%
Starting a Gradle Daemon, 1 incompatible Daemon could not be reused, use --status for details

BUILD SUCCESSFUL in 40s
6 actionable tasks: 5 executed, 1 up-to-date
```

### Run recipe

`./gradlew run`

```shell
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
