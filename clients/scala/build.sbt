name := "jdbi-flight-sql-example"

version := "0.1"

scalaVersion := "2.13.12"

libraryDependencies ++= Seq(
  "org.jdbi" % "jdbi" % "2.78",
  "org.antlr" % "stringtemplate" % "3.2", // Added for StringTemplate support
  "org.apache.arrow" % "flight-sql-jdbc-driver" % "19.0.0",
  "org.slf4j" % "slf4j-simple" % "2.0.16"
)


run / javaOptions += "--add-opens=java.base/java.nio=ALL-UNNAMED"
run / javaOptions += "--add-opens=java.base/java.lang=ALL-UNNAMED"

// Arrow allocates through Netty, and Netty switches off its own sun.misc.Unsafe path
// whenever the JVM reports `sun.misc.unsafe.memory.access` as anything other than `allow`,
// leaving Arrow with no usable allocator. JDK 24 sets that property to `warn` by default
// (JEP 498 phase 2 — the JDK does not itself deny the calls until phase 3, JDK 26 or later).
// The option only exists from JDK 23 on, so it is applied conditionally.
run / javaOptions ++= {
  val jdk = System.getProperty("java.specification.version").toInt
  if (jdk >= 23) Seq("--sun-misc-unsafe-memory-access=allow") else Seq.empty
}
run / fork := true
