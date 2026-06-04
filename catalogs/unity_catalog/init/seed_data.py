"""
Seed a local Unity Catalog instance with realistic sample data via MinIO (S3).

Creates a 'samples' schema in the 'unity' catalog with:
- customers: Customer dimension table (100 rows)
- products: Product catalog dimension table (50 rows)
- orders: Order fact table (500 rows)
- order_items: Order line items fact table (~1500 rows)

Writes Delta Lake tables to MinIO S3 and registers them in Unity Catalog.
"""

import os
import time
import requests
import pyarrow as pa
from deltalake import write_deltalake
from datetime import date
import random

UC_URL = "http://unitycatalog:8081"
CATALOG = "unity"
SCHEMA = "samples"

S3_BUCKET = os.environ.get("S3_BUCKET", "unity-catalog")
AWS_ENDPOINT_URL = os.environ.get("AWS_ENDPOINT_URL", "http://minio:9000")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "minio")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "minio123")

STORAGE_OPTIONS = {
    "AWS_ACCESS_KEY_ID": AWS_ACCESS_KEY_ID,
    "AWS_SECRET_ACCESS_KEY": AWS_SECRET_ACCESS_KEY,
    "AWS_ENDPOINT_URL": AWS_ENDPOINT_URL,
    "AWS_REGION": "us-east-1",
    "AWS_S3_ALLOW_UNSAFE_RENAME": "true",
    "AWS_ALLOW_HTTP": "true",
}


def s3_path(table_name):
    return f"s3://{S3_BUCKET}/samples/{table_name}"


def s3_url_for_uc(table_name):
    """Return the S3 path as UC will store it."""
    return f"s3://{S3_BUCKET}/samples/{table_name}"


def wait_for_uc():
    for i in range(60):
        try:
            r = requests.get(f"{UC_URL}/api/2.1/unity-catalog/catalogs", timeout=5)
            if r.status_code == 200:
                print("Unity Catalog is ready.")
                return
        except Exception:
            pass
        print(f"Waiting for Unity Catalog... ({i+1})")
        time.sleep(2)
    raise RuntimeError("Unity Catalog did not become ready in time.")


def create_schema():
    r = requests.get(f"{UC_URL}/api/2.1/unity-catalog/schemas", params={"catalog_name": CATALOG})
    schemas = [s["name"] for s in r.json().get("schemas", [])]
    if SCHEMA in schemas:
        print(f"Schema '{SCHEMA}' already exists.")
        return
    r = requests.post(
        f"{UC_URL}/api/2.1/unity-catalog/schemas",
        json={"name": SCHEMA, "catalog_name": CATALOG, "comment": "Sample data for demos"},
    )
    r.raise_for_status()
    print(f"Created schema '{SCHEMA}'.")


def register_table(name, columns, storage_location, comment=""):
    r = requests.get(f"{UC_URL}/api/2.1/unity-catalog/tables/{CATALOG}.{SCHEMA}.{name}")
    if r.status_code == 200:
        print(f"Table '{name}' already registered.")
        return
    r = requests.post(
        f"{UC_URL}/api/2.1/unity-catalog/tables",
        json={
            "name": name,
            "catalog_name": CATALOG,
            "schema_name": SCHEMA,
            "table_type": "EXTERNAL",
            "data_source_format": "DELTA",
            "columns": columns,
            "storage_location": storage_location,
            "comment": comment,
        },
    )
    r.raise_for_status()
    print(f"Registered table '{name}'.")


def col(name, type_name, type_text, position, nullable=False, comment=""):
    type_json_type = {
        "INT": "integer", "LONG": "long", "DOUBLE": "double",
        "STRING": "string", "DATE": "date",
    }[type_name]
    return {
        "name": name,
        "type_name": type_name,
        "type_text": type_text,
        "type_json": f'{{"name":"{name}","type":"{type_json_type}","nullable":{str(nullable).lower()},"metadata":{{}}}}',
        "position": position,
        "nullable": nullable,
        "comment": comment,
    }


def seed_customers():
    random.seed(42)
    first_names = ["James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda",
                   "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
                   "Thomas", "Sarah", "Charles", "Karen", "Emma", "Oliver", "Ava", "Liam", "Sophia"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
                  "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
                  "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White", "Harris"]
    cities = [
        ("New York", "NY", "US"), ("Los Angeles", "CA", "US"), ("Chicago", "IL", "US"),
        ("Houston", "TX", "US"), ("Phoenix", "AZ", "US"), ("London", "", "UK"),
        ("Manchester", "", "UK"), ("Berlin", "", "DE"), ("Munich", "", "DE"),
        ("Paris", "", "FR"), ("Toronto", "ON", "CA"), ("Vancouver", "BC", "CA"),
        ("Sydney", "NSW", "AU"), ("Tokyo", "", "JP"), ("Singapore", "", "SG"),
    ]
    segments = ["Consumer", "Corporate", "Small Business", "Enterprise"]

    customer_ids, fns, lns, emails, segs, city_list, states, countries, dates = [], [], [], [], [], [], [], [], []
    for i in range(1, 101):
        fn = random.choice(first_names)
        ln = random.choice(last_names)
        city, state, country = random.choice(cities)
        customer_ids.append(i)
        fns.append(fn)
        lns.append(ln)
        emails.append(f"{fn.lower()}.{ln.lower()}{i}@example.com")
        segs.append(random.choice(segments))
        city_list.append(city)
        states.append(state if state else None)
        countries.append(country)
        dates.append(date(random.randint(2018, 2023), random.randint(1, 12), random.randint(1, 28)))

    table = pa.table({
        "customer_id": pa.array(customer_ids, type=pa.int32()),
        "first_name": pa.array(fns, type=pa.string()),
        "last_name": pa.array(lns, type=pa.string()),
        "email": pa.array(emails, type=pa.string()),
        "segment": pa.array(segs, type=pa.string()),
        "city": pa.array(city_list, type=pa.string()),
        "state": pa.array(states, type=pa.string()),
        "country": pa.array(countries, type=pa.string()),
        "created_date": pa.array(dates, type=pa.date32()),
    })

    path = s3_path("customers")
    write_deltalake(path, table, mode="overwrite", storage_options=STORAGE_OPTIONS)
    print(f"Wrote 100 rows to customers.")

    register_table("customers", [
        col("customer_id", "INT", "int", 0, comment="Unique customer identifier"),
        col("first_name", "STRING", "string", 1, comment="Customer first name"),
        col("last_name", "STRING", "string", 2, comment="Customer last name"),
        col("email", "STRING", "string", 3, comment="Email address"),
        col("segment", "STRING", "string", 4, comment="Market segment"),
        col("city", "STRING", "string", 5, comment="City"),
        col("state", "STRING", "string", 6, nullable=True, comment="State or province"),
        col("country", "STRING", "string", 7, comment="Country code"),
        col("created_date", "DATE", "date", 8, comment="Account creation date"),
    ], s3_url_for_uc("customers"), "Customer dimension table")


def seed_products():
    random.seed(43)
    categories = {
        "Electronics": ["Laptop", "Smartphone", "Tablet", "Monitor", "Keyboard", "Mouse", "Headphones", "Speaker", "Webcam", "Charger"],
        "Furniture": ["Desk", "Chair", "Bookshelf", "Filing Cabinet", "Standing Desk", "Lamp", "Monitor Stand", "Footrest", "Whiteboard", "Coatrack"],
        "Office Supplies": ["Notebook", "Pen Set", "Stapler", "Paper Ream", "Binder", "Sticky Notes", "Tape Dispenser", "Scissors", "Highlighters", "Envelopes"],
        "Software": ["Productivity Suite", "Antivirus", "Design Tool", "IDE License", "Cloud Storage", "VPN Service", "Backup Tool", "Analytics Platform", "CRM License", "Project Mgmt"],
        "Peripherals": ["USB Hub", "Docking Station", "External SSD", "Ethernet Adapter", "Card Reader", "Printer", "Scanner", "UPS Battery", "Cable Kit", "Surge Protector"],
    }

    pids, names, cats, prices, statuses, stocks = [], [], [], [], [], []
    pid = 1
    for category, products in categories.items():
        for product in products:
            pids.append(pid)
            names.append(product)
            cats.append(category)
            prices.append(round(random.uniform(9.99, 1499.99), 2))
            statuses.append(random.choice(["In Stock", "Low Stock", "Out of Stock"]))
            stocks.append(random.randint(0, 500))
            pid += 1

    table = pa.table({
        "product_id": pa.array(pids, type=pa.int32()),
        "product_name": pa.array(names, type=pa.string()),
        "category": pa.array(cats, type=pa.string()),
        "price": pa.array(prices, type=pa.float64()),
        "status": pa.array(statuses, type=pa.string()),
        "stock_quantity": pa.array(stocks, type=pa.int32()),
    })

    path = s3_path("products")
    write_deltalake(path, table, mode="overwrite", storage_options=STORAGE_OPTIONS)
    print(f"Wrote 50 rows to products.")

    register_table("products", [
        col("product_id", "INT", "int", 0, comment="Unique product identifier"),
        col("product_name", "STRING", "string", 1, comment="Product name"),
        col("category", "STRING", "string", 2, comment="Product category"),
        col("price", "DOUBLE", "double", 3, comment="Unit price in USD"),
        col("status", "STRING", "string", 4, comment="Stock status"),
        col("stock_quantity", "INT", "int", 5, comment="Current stock quantity"),
    ], s3_url_for_uc("products"), "Product catalog dimension table")


def seed_orders():
    random.seed(44)
    statuses = ["Pending", "Processing", "Shipped", "Delivered", "Cancelled", "Returned"]
    status_weights = [0.05, 0.1, 0.15, 0.55, 0.1, 0.05]
    payments = ["Credit Card", "Debit Card", "Wire Transfer", "PayPal", "Invoice"]

    oids, cids, odates, sts, totals, pms = [], [], [], [], [], []
    for i in range(1, 501):
        oids.append(i)
        cids.append(random.randint(1, 100))
        odates.append(date(random.randint(2022, 2024), random.randint(1, 12), random.randint(1, 28)))
        sts.append(random.choices(statuses, weights=status_weights, k=1)[0])
        totals.append(round(random.uniform(15.0, 5000.0), 2))
        pms.append(random.choice(payments))

    table = pa.table({
        "order_id": pa.array(oids, type=pa.int32()),
        "customer_id": pa.array(cids, type=pa.int32()),
        "order_date": pa.array(odates, type=pa.date32()),
        "status": pa.array(sts, type=pa.string()),
        "total_amount": pa.array(totals, type=pa.float64()),
        "payment_method": pa.array(pms, type=pa.string()),
    })

    path = s3_path("orders")
    write_deltalake(path, table, mode="overwrite", storage_options=STORAGE_OPTIONS)
    print(f"Wrote 500 rows to orders.")

    register_table("orders", [
        col("order_id", "INT", "int", 0, comment="Unique order identifier"),
        col("customer_id", "INT", "int", 1, comment="FK to customers"),
        col("order_date", "DATE", "date", 2, comment="Date order was placed"),
        col("status", "STRING", "string", 3, comment="Order status"),
        col("total_amount", "DOUBLE", "double", 4, comment="Order total in USD"),
        col("payment_method", "STRING", "string", 5, comment="Payment method used"),
    ], s3_url_for_uc("orders"), "Order fact table")


def seed_order_items():
    random.seed(45)

    iids, oids, pids, qtys, uprices, discounts = [], [], [], [], [], []
    item_id = 1
    for order_id in range(1, 501):
        n_items = random.randint(1, 5)
        for _ in range(n_items):
            iids.append(item_id)
            oids.append(order_id)
            pids.append(random.randint(1, 50))
            qtys.append(random.randint(1, 10))
            uprices.append(round(random.uniform(9.99, 1499.99), 2))
            discounts.append(random.choice([0.0, 0.0, 0.0, 0.05, 0.1, 0.15, 0.2]))
            item_id += 1

    table = pa.table({
        "item_id": pa.array(iids, type=pa.int32()),
        "order_id": pa.array(oids, type=pa.int32()),
        "product_id": pa.array(pids, type=pa.int32()),
        "quantity": pa.array(qtys, type=pa.int32()),
        "unit_price": pa.array(uprices, type=pa.float64()),
        "discount": pa.array(discounts, type=pa.float64()),
    })

    path = s3_path("order_items")
    write_deltalake(path, table, mode="overwrite", storage_options=STORAGE_OPTIONS)
    print(f"Wrote {len(iids)} rows to order_items.")

    register_table("order_items", [
        col("item_id", "INT", "int", 0, comment="Unique line item identifier"),
        col("order_id", "INT", "int", 1, comment="FK to orders"),
        col("product_id", "INT", "int", 2, comment="FK to products"),
        col("quantity", "INT", "int", 3, comment="Quantity ordered"),
        col("unit_price", "DOUBLE", "double", 4, comment="Price per unit at time of order"),
        col("discount", "DOUBLE", "double", 5, comment="Discount percentage applied"),
    ], s3_url_for_uc("order_items"), "Order line items fact table")


if __name__ == "__main__":
    print("=== Unity Catalog Data Seeder ===")
    wait_for_uc()
    create_schema()
    seed_customers()
    seed_products()
    seed_orders()
    seed_order_items()
    print("\n=== Seeding complete! ===")
    print("Tables created in unity.samples:")
    print("  - customers (100 rows)")
    print("  - products (50 rows)")
    print("  - orders (500 rows)")
    print("  - order_items (~1500 rows)")
