#!/bin/bash

mc alias set minio http://minio:9000 admin password
mc mb minio/hadoop
mc anonymous set public minio/hadoop

wget https://github.com/duckdb/duckdb/releases/download/v1.3.2/duckdb_cli-linux-amd64.zip
unzip duckdb_cli-linux-amd64.zip
./duckdb <<EOF
INSTALL tpch;
LOAD tpch;
CALL dbgen(sf=1);
COPY 'lineitem' TO 'lineitem.csv';
COPY 'customer' TO 'customer.csv';
COPY 'orders' TO 'orders.csv';
COPY 'supplier' TO 'supplier.csv';
COPY 'part' TO 'part.csv';
COPY 'partsupp' TO 'partsupp.csv';
COPY 'nation' TO 'nation.csv';
COPY 'region' TO 'region.csv';
EOF

/opt/spark/bin/spark-shell <<EOF
spark.conf.set("spark.sql.catalog.hadoop", "org.apache.iceberg.spark.SparkCatalog")
spark.conf.set("spark.sql.catalog.hadoop.type", "hadoop")
spark.conf.set("spark.sql.catalog.hadoop.warehouse", "s3a://hadoop")
spark.conf.set("spark.sql.catalog.hadoop.s3.endpoint", "http://minio:9000")
spark.conf.set("spark.sql.defaultCatalog", "hadoop")

spark.sparkContext.hadoopConfiguration.set("fs.s3a.access.key", "admin")
spark.sparkContext.hadoopConfiguration.set("fs.s3a.secret.key", "password")
spark.sparkContext.hadoopConfiguration.set("fs.s3a.endpoint", "http://minio:9000")
spark.sparkContext.hadoopConfiguration.set("fs.s3a.connection.ssl.enabled", "false")
spark.sparkContext.hadoopConfiguration.set("fs.s3a.path.style.access", "true")
spark.sparkContext.hadoopConfiguration.set("fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
spark.sparkContext.hadoopConfiguration.set("fs.s3a.filesystem", "org.apache.hadoop.fs.s3a.S3AFileSystem")

val csv_df = spark.read.option("header", "true").option("inferSchema", "true").csv("./lineitem.csv")
csv_df.writeTo("hadoop.tpch.lineitem").using("iceberg").create()
val csv_df = spark.read.option("header", "true").option("inferSchema", "true").csv("./customer.csv")
csv_df.writeTo("hadoop.tpch.customer").using("iceberg").create()
val csv_df = spark.read.option("header", "true").option("inferSchema", "true").csv("./orders.csv")
csv_df.writeTo("hadoop.tpch.orders").using("iceberg").create()
val csv_df = spark.read.option("header", "true").option("inferSchema", "true").csv("./supplier.csv")
csv_df.writeTo("hadoop.tpch.supplier").using("iceberg").create()
val csv_df = spark.read.option("header", "true").option("inferSchema", "true").csv("./part.csv")
csv_df.writeTo("hadoop.tpch.part").using("iceberg").create()
val csv_df = spark.read.option("header", "true").option("inferSchema", "true").csv("./partsupp.csv")
csv_df.writeTo("hadoop.tpch.partsupp").using("iceberg").create()
val csv_df = spark.read.option("header", "true").option("inferSchema", "true").csv("./nation.csv")
csv_df.writeTo("hadoop.tpch.nation").using("iceberg").create()
val csv_df = spark.read.option("header", "true").option("inferSchema", "true").csv("./region.csv")
csv_df.writeTo("hadoop.tpch.region").using("iceberg").create()
EOF

echo "done" > /opt/setup_done
tail -f /dev/null