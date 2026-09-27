#!/usr/bin/env python3
"""
Download TPC-H SF1 parquet files and load them into MySQL with
primary keys, proper types, and foreign key constraints.

Creation order respects FK dependencies:
  region → nation → part, supplier, customer
  supplier + part → partsupp
  customer → orders → lineitem
"""

import time
import pyarrow.parquet as pq
import pyarrow as pa
import mysql.connector
import os

MYSQL_HOST = os.getenv("MYSQL_HOST", "mysql")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_DB   = os.getenv("MYSQL_DB",   "tpch")
MYSQL_USER = os.getenv("MYSQL_USER", "root")

DATA_DIR = "/data/tpch_sf1"

# ---------------------------------------------------------------------------
# DDL – tables in FK-safe creation order
# ---------------------------------------------------------------------------

DDL_STATEMENTS = [
    """
CREATE TABLE IF NOT EXISTS region (
    r_regionkey  INTEGER      NOT NULL,
    r_name       CHAR(25)     NOT NULL,
    r_comment    VARCHAR(152),
    PRIMARY KEY (r_regionkey)
) ENGINE=InnoDB
""",
    """
CREATE TABLE IF NOT EXISTS nation (
    n_nationkey  INTEGER      NOT NULL,
    n_name       CHAR(25)     NOT NULL,
    n_regionkey  INTEGER      NOT NULL,
    n_comment    VARCHAR(152),
    PRIMARY KEY (n_nationkey),
    CONSTRAINT fk_nation_region
        FOREIGN KEY (n_regionkey) REFERENCES region (r_regionkey)
) ENGINE=InnoDB
""",
    """
CREATE TABLE IF NOT EXISTS part (
    p_partkey     INTEGER       NOT NULL,
    p_name        VARCHAR(55)   NOT NULL,
    p_mfgr        CHAR(25)      NOT NULL,
    p_brand       CHAR(10)      NOT NULL,
    p_type        VARCHAR(25)   NOT NULL,
    p_size        INTEGER       NOT NULL,
    p_container   CHAR(10)      NOT NULL,
    p_retailprice DECIMAL(15,2) NOT NULL,
    p_comment     VARCHAR(23)   NOT NULL,
    PRIMARY KEY (p_partkey)
) ENGINE=InnoDB
""",
    """
CREATE TABLE IF NOT EXISTS supplier (
    s_suppkey    INTEGER       NOT NULL,
    s_name       CHAR(25)      NOT NULL,
    s_address    VARCHAR(40)   NOT NULL,
    s_nationkey  INTEGER       NOT NULL,
    s_phone      CHAR(15)      NOT NULL,
    s_acctbal    DECIMAL(15,2) NOT NULL,
    s_comment    VARCHAR(101)  NOT NULL,
    PRIMARY KEY (s_suppkey),
    CONSTRAINT fk_supplier_nation
        FOREIGN KEY (s_nationkey) REFERENCES nation (n_nationkey)
) ENGINE=InnoDB
""",
    """
CREATE TABLE IF NOT EXISTS customer (
    c_custkey    INTEGER       NOT NULL,
    c_name       VARCHAR(25)   NOT NULL,
    c_address    VARCHAR(40)   NOT NULL,
    c_nationkey  INTEGER       NOT NULL,
    c_phone      CHAR(15)      NOT NULL,
    c_acctbal    DECIMAL(15,2) NOT NULL,
    c_mktsegment CHAR(10)      NOT NULL,
    c_comment    VARCHAR(117)  NOT NULL,
    PRIMARY KEY (c_custkey),
    CONSTRAINT fk_customer_nation
        FOREIGN KEY (c_nationkey) REFERENCES nation (n_nationkey)
) ENGINE=InnoDB
""",
    """
CREATE TABLE IF NOT EXISTS partsupp (
    ps_partkey    INTEGER       NOT NULL,
    ps_suppkey    INTEGER       NOT NULL,
    ps_availqty   INTEGER       NOT NULL,
    ps_supplycost DECIMAL(15,2) NOT NULL,
    ps_comment    VARCHAR(199)  NOT NULL,
    PRIMARY KEY (ps_partkey, ps_suppkey),
    CONSTRAINT fk_partsupp_part
        FOREIGN KEY (ps_partkey) REFERENCES part (p_partkey),
    CONSTRAINT fk_partsupp_supplier
        FOREIGN KEY (ps_suppkey) REFERENCES supplier (s_suppkey)
) ENGINE=InnoDB
""",
    """
CREATE TABLE IF NOT EXISTS orders (
    o_orderkey      INTEGER       NOT NULL,
    o_custkey       INTEGER       NOT NULL,
    o_orderstatus   CHAR(1)       NOT NULL,
    o_totalprice    DECIMAL(15,2) NOT NULL,
    o_orderdate     DATE          NOT NULL,
    o_orderpriority CHAR(15)      NOT NULL,
    o_clerk         CHAR(15)      NOT NULL,
    o_shippriority  INTEGER       NOT NULL,
    o_comment       VARCHAR(79)   NOT NULL,
    PRIMARY KEY (o_orderkey),
    CONSTRAINT fk_orders_customer
        FOREIGN KEY (o_custkey) REFERENCES customer (c_custkey)
) ENGINE=InnoDB
""",
    """
CREATE TABLE IF NOT EXISTS lineitem (
    l_orderkey      INTEGER       NOT NULL,
    l_partkey       INTEGER       NOT NULL,
    l_suppkey       INTEGER       NOT NULL,
    l_linenumber    INTEGER       NOT NULL,
    l_quantity      DECIMAL(15,2) NOT NULL,
    l_extendedprice DECIMAL(15,2) NOT NULL,
    l_discount      DECIMAL(15,2) NOT NULL,
    l_tax           DECIMAL(15,2) NOT NULL,
    l_returnflag    CHAR(1)       NOT NULL,
    l_linestatus    CHAR(1)       NOT NULL,
    l_shipdate      DATE          NOT NULL,
    l_commitdate    DATE          NOT NULL,
    l_receiptdate   DATE          NOT NULL,
    l_shipinstruct  CHAR(25)      NOT NULL,
    l_shipmode      CHAR(10)      NOT NULL,
    l_comment       VARCHAR(44)   NOT NULL,
    PRIMARY KEY (l_orderkey, l_linenumber),
    CONSTRAINT fk_lineitem_orders
        FOREIGN KEY (l_orderkey) REFERENCES orders (o_orderkey),
    CONSTRAINT fk_lineitem_partsupp
        FOREIGN KEY (l_partkey, l_suppkey) REFERENCES partsupp (ps_partkey, ps_suppkey)
) ENGINE=InnoDB
""",
]

# Tables in load order (parent tables before child tables)
TABLES = ["region", "nation", "part", "supplier", "customer", "partsupp", "orders", "lineitem"]

BATCH_SIZE = 1000


def wait_for_mysql(max_retries=30, delay=2):
    """Retry until MySQL is accepting connections."""
    for attempt in range(max_retries):
        try:
            conn = mysql.connector.connect(
                host=MYSQL_HOST, port=MYSQL_PORT, database=MYSQL_DB, user=MYSQL_USER
            )
            conn.close()
            print("MySQL is ready.")
            return
        except mysql.connector.Error:
            print(f"Waiting for MySQL... ({attempt + 1}/{max_retries})")
            time.sleep(delay)
    raise RuntimeError("MySQL did not become ready in time.")


def load_table(conn, table_name: str):
    path = f"{DATA_DIR}/{table_name}.parquet"
    print(f"  Reading {path} ...")
    arrow_table = pq.read_table(path)
    print(f"  {arrow_table.num_rows:,} rows, schema: {arrow_table.schema}")

    # Cast decimal columns to float64 and date columns to Python date strings
    arrays = []
    col_names = arrow_table.schema.names
    for field in arrow_table.schema:
        col = arrow_table.column(field.name)
        if pa.types.is_decimal(field.type):
            col = col.cast(pa.float64())
        arrays.append(col)
    arrow_table = pa.table(dict(zip(col_names, arrays)))

    # Convert to list of tuples for executemany
    rows = arrow_table.to_pydict()
    num_rows = arrow_table.num_rows
    columns = arrow_table.schema.names

    placeholders = ", ".join(["%s"] * len(columns))
    col_list = ", ".join(columns)
    insert_sql = f"INSERT INTO {table_name} ({col_list}) VALUES ({placeholders})"

    cursor = conn.cursor()
    batch = []
    for i in range(num_rows):
        row = tuple(rows[col][i] for col in columns)
        batch.append(row)
        if len(batch) >= BATCH_SIZE:
            cursor.executemany(insert_sql, batch)
            conn.commit()
            batch = []
    if batch:
        cursor.executemany(insert_sql, batch)
        conn.commit()
    cursor.close()

    print(f"  Loaded {num_rows:,} rows into {table_name}.")


def main():
    wait_for_mysql()

    conn = mysql.connector.connect(
        host=MYSQL_HOST, port=MYSQL_PORT, database=MYSQL_DB, user=MYSQL_USER
    )

    print("Creating schema ...")
    cursor = conn.cursor()
    for stmt in DDL_STATEMENTS:
        cursor.execute(stmt)
    conn.commit()
    cursor.close()
    print("Schema created.")

    # Disable FK checks during bulk load for performance, re-enable after
    cursor = conn.cursor()
    cursor.execute("SET FOREIGN_KEY_CHECKS=0")
    cursor.close()

    for table in TABLES:
        print(f"\nLoading {table} ...")
        load_table(conn, table)

    cursor = conn.cursor()
    cursor.execute("SET FOREIGN_KEY_CHECKS=1")
    cursor.close()
    conn.commit()

    conn.close()
    print("\nAll TPC-H tables loaded successfully!")


if __name__ == "__main__":
    main()
