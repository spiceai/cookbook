# Use official sbt image with OpenJDK 11 and sbt 1.10.11
FROM sbtscala/scala-sbt:eclipse-temurin-23.0.2_7_1.10.11_3.6.4

WORKDIR /app

# Copy the project files
COPY . .

# Cache dependencies
RUN sbt clean compile

ENV JAVA_OPTS="--add-opens=java.base/java.lang=ALL-UNNAMED --add-opens=java.base/java.nio=org.apache.arrow.memory.core,ALL-UNNAMED"

# Run the application
CMD ["sbt", "run"] 