from pyspark.sql import SparkSession

# Create SparkSession if not already exists
spark = SparkSession.builder.getOrCreate()

spark.sql("CREATE DATABASE IF NOT EXISTS nyc")
spark.sql("DROP TABLE IF EXISTS nyc.taxis")

df = spark.read.parquet("/home/iceberg/data/yellow_tripdata_2021-04.parquet")
df.write.saveAsTable("nyc.taxis")

spark.sql("SELECT * FROM nyc.taxis LIMIT 10").show()