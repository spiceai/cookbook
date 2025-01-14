from pyspark.sql import SparkSession

# Create SparkSession if not already exists
spark = SparkSession.builder \
    .appName("NYC Taxi Data") \
    .config("spark.sql.warehouse.dir", "/home/spark/warehouse") \
    .config("spark.sql.catalogImplementation", "hive") \
    .getOrCreate()

# Read the data to get the schema
df = spark.read.parquet("/home/spark/data/yellow_tripdata_2022-04.parquet")

# Create external table with explicit schema
spark.sql("""
    CREATE EXTERNAL TABLE IF NOT EXISTS nyc_taxis (
        VendorID BIGINT,
        tpep_pickup_datetime TIMESTAMP,
        tpep_dropoff_datetime TIMESTAMP,
        passenger_count DOUBLE,
        trip_distance DOUBLE,
        RatecodeID DOUBLE,
        store_and_fwd_flag STRING,
        PULocationID BIGINT,
        DOLocationID BIGINT,
        payment_type BIGINT,
        fare_amount DOUBLE,
        extra DOUBLE,
        mta_tax DOUBLE,
        tip_amount DOUBLE,
        tolls_amount DOUBLE,
        improvement_surcharge DOUBLE,
        total_amount DOUBLE,
        congestion_surcharge DOUBLE,
        airport_fee DOUBLE
    )
    STORED AS PARQUET
    LOCATION '/home/spark/data'
""")

spark.sql("SELECT * FROM nyc_taxis LIMIT 10").show()
