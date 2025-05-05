name := "jdbi-flight-sql-example"

version := "0.1"

scalaVersion := "2.13.12"

libraryDependencies ++= Seq(
  "org.jdbi" % "jdbi" % "2.78",
  "org.antlr" % "stringtemplate" % "3.2", // Added for StringTemplate support
  "org.apache.arrow" % "flight-sql-jdbc-driver" % "18.1.0",
  "org.slf4j" % "slf4j-simple" % "2.0.16"
)


run / javaOptions += "--add-opens=java.base/java.nio=org.apache.arrow.memory.core,ALL-UNNAMED"
run / javaOptions += "--add-opens=java.base/java.lang=ALL-UNNAMED"
run / fork := true
