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

// Arrow's Netty allocator uses sun.misc.Unsafe memory access, which JDK 24+ disables by
// default (JEP 498). The flag was only added in JDK 23, so it is applied conditionally.
run / javaOptions ++= {
  val jdk = System.getProperty("java.specification.version").toInt
  if (jdk >= 23) Seq("--sun-misc-unsafe-memory-access=allow") else Seq.empty
}
run / fork := true
