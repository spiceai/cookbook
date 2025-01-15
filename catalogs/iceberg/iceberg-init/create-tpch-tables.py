from pyiceberg.catalog import load_catalog
import pyarrow.parquet as pq
import os

tables = ["customer", "lineitem", "orders", "part", "partsupp", "supplier", "nation", "region"]

# Initialize the REST catalog
catalog = load_catalog(
    "iceberg",
    **{
        "type": "rest",
        "uri": os.getenv("CATALOG_URI"),
        "s3.endpoint": os.getenv("CATALOG_S3_ENDPOINT"),
        "s3.access-key-id": os.getenv("AWS_ACCESS_KEY_ID"),
        "s3.secret-access-key": os.getenv("AWS_SECRET_ACCESS_KEY"),
        "warehouse": os.getenv("CATALOG_WAREHOUSE")
    }
)

catalog.create_namespace("tpch_sf1")

for table in tables:
    df = pq.read_table(f'/home/iceberg/data/tpch_sf1/{table}/{table}.parquet')
    print(f"\n\nReading {table} schema\n\n")
    print(df.schema)

    # Create the table
    table = catalog.create_table(
        f"tpch_sf1.{table}",
        schema=df.schema
    )

    table.append(df)

    print(len(table.scan().to_arrow()))

print("All tables created!")