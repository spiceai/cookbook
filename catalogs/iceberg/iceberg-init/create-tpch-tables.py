from pyiceberg.catalog import load_catalog
import pyarrow.parquet as pq
import pyarrow as pa
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

for table_name in tables:
    print(f"\n\nProcessing table: {table_name}")

    # Read the parquet file
    df = pq.read_table(f'/home/iceberg/data/tpch_sf1/{table_name}/{table_name}.parquet')
    print(f"Reading {table_name} schema:")
    print(df.schema)

    # Process the schema to handle decimal types
    modified_schema = pa.schema([])
    decimal_fields = []

    for field in df.schema:
        if pa.types.is_decimal(field.type):
            print(f"Converting decimal field: {field.name}")
            # Convert decimal fields to double
            decimal_fields.append(field.name)
            # Keep the same field but with type converted to float64
            modified_schema = modified_schema.append(pa.field(field.name, pa.float64()))
        else:
            modified_schema = modified_schema.append(field)

    # Create a new table with the modified schema
    modified_df = df

    # Convert decimal fields to double
    if decimal_fields:
        print(f"Converting decimal fields to double: {decimal_fields}")
        for field in decimal_fields:
            # Convert the decimal column to double
            array = df[field].cast(pa.float64())
            modified_df = modified_df.set_column(
                modified_df.schema.get_field_index(field),
                field,
                array
            )

    print(f"Modified schema:")
    print(modified_df.schema)

    # Create the table
    iceberg_table = catalog.create_table(
        f"tpch_sf1.{table_name}",
        schema=modified_df.schema
    )

    # Append data
    iceberg_table.append(modified_df)

    # Verify data was added
    row_count = len(iceberg_table.scan().to_arrow())
    print(f"Table {table_name} created with {row_count} rows")

print("All tables created!")
