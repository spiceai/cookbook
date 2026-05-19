#!/usr/bin/env python3
"""
Load TPC-H SF1 parquet files into Microsoft SQL Server with
primary keys, proper types, and foreign key constraints.

Creation order respects FK dependencies:
  region → nation → part, supplier, customer
  supplier + part → partsupp
  customer → orders → lineitem
"""

import time
import pyarrow.parquet as pq
import pyarrow as pa
import pyodbc
import os

MSSQL_HOST     = os.getenv("MSSQL_HOST",     "mssql")
MSSQL_PORT     = int(os.getenv("MSSQL_PORT", "1433"))
MSSQL_DB       = os.getenv("MSSQL_DB",       "tpch")
MSSQL_USER     = os.getenv("MSSQL_USER",     "sa")
MSSQL_PASSWORD = os.getenv("MSSQL_PASSWORD", "SpiceDemo1!")

DATA_DIR = "/data/tpch_sf1"

BATCH_SIZE = 500

# ---------------------------------------------------------------------------
# Connection helpers
# ---------------------------------------------------------------------------

def make_conn_str(database: str) -> str:
    return (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={MSSQL_HOST},{MSSQL_PORT};"
        f"DATABASE={database};"
        f"UID={MSSQL_USER};"
        f"PWD={MSSQL_PASSWORD};"
        f"TrustServerCertificate=yes"
    )


def wait_for_mssql(max_retries: int = 30, delay: int = 2):
    """Retry until SQL Server is accepting connections."""
    for attempt in range(max_retries):
        try:
            conn = pyodbc.connect(make_conn_str("master"), autocommit=True)
            conn.close()
            print("SQL Server is ready.")
            return
        except pyodbc.OperationalError:
            print(f"Waiting for SQL Server... ({attempt + 1}/{max_retries})")
            time.sleep(delay)
    raise RuntimeError("SQL Server did not become ready in time.")


def create_database():
    """Create the tpch database if it does not already exist."""
    conn = pyodbc.connect(make_conn_str("master"), autocommit=True)
    cur = conn.cursor()
    cur.execute(
        "IF DB_ID(?) IS NULL CREATE DATABASE tpch",
        (MSSQL_DB,),
    )
    cur.close()
    conn.close()
    print(f"Database '{MSSQL_DB}' ready.")


# ---------------------------------------------------------------------------
# DDL – tables in FK-safe creation order
# ---------------------------------------------------------------------------

DDL_STATEMENTS = [
    # region
    """
    IF OBJECT_ID('dbo.region', 'U') IS NULL
    CREATE TABLE dbo.region (
        r_regionkey  INTEGER       NOT NULL,
        r_name       CHAR(25)      NOT NULL,
        r_comment    VARCHAR(152),
        CONSTRAINT pk_region PRIMARY KEY (r_regionkey)
    )
    """,

    # nation
    """
    IF OBJECT_ID('dbo.nation', 'U') IS NULL
    CREATE TABLE dbo.nation (
        n_nationkey  INTEGER       NOT NULL,
        n_name       CHAR(25)      NOT NULL,
        n_regionkey  INTEGER       NOT NULL,
        n_comment    VARCHAR(152),
        CONSTRAINT pk_nation PRIMARY KEY (n_nationkey),
        CONSTRAINT fk_nation_region
            FOREIGN KEY (n_regionkey) REFERENCES dbo.region (r_regionkey)
    )
    """,

    # part
    """
    IF OBJECT_ID('dbo.part', 'U') IS NULL
    CREATE TABLE dbo.part (
        p_partkey     INTEGER        NOT NULL,
        p_name        VARCHAR(55)    NOT NULL,
        p_mfgr        CHAR(25)       NOT NULL,
        p_brand       CHAR(10)       NOT NULL,
        p_type        VARCHAR(25)    NOT NULL,
        p_size        INTEGER        NOT NULL,
        p_container   CHAR(10)       NOT NULL,
        p_retailprice DECIMAL(15,2)  NOT NULL,
        p_comment     VARCHAR(23)    NOT NULL,
        CONSTRAINT pk_part PRIMARY KEY (p_partkey)
    )
    """,

    # supplier
    """
    IF OBJECT_ID('dbo.supplier', 'U') IS NULL
    CREATE TABLE dbo.supplier (
        s_suppkey    INTEGER        NOT NULL,
        s_name       CHAR(25)       NOT NULL,
        s_address    VARCHAR(40)    NOT NULL,
        s_nationkey  INTEGER        NOT NULL,
        s_phone      CHAR(15)       NOT NULL,
        s_acctbal    DECIMAL(15,2)  NOT NULL,
        s_comment    VARCHAR(101)   NOT NULL,
        CONSTRAINT pk_supplier PRIMARY KEY (s_suppkey),
        CONSTRAINT fk_supplier_nation
            FOREIGN KEY (s_nationkey) REFERENCES dbo.nation (n_nationkey)
    )
    """,

    # customer
    """
    IF OBJECT_ID('dbo.customer', 'U') IS NULL
    CREATE TABLE dbo.customer (
        c_custkey    INTEGER        NOT NULL,
        c_name       VARCHAR(25)    NOT NULL,
        c_address    VARCHAR(40)    NOT NULL,
        c_nationkey  INTEGER        NOT NULL,
        c_phone      CHAR(15)       NOT NULL,
        c_acctbal    DECIMAL(15,2)  NOT NULL,
        c_mktsegment CHAR(10)       NOT NULL,
        c_comment    VARCHAR(117)   NOT NULL,
        CONSTRAINT pk_customer PRIMARY KEY (c_custkey),
        CONSTRAINT fk_customer_nation
            FOREIGN KEY (c_nationkey) REFERENCES dbo.nation (n_nationkey)
    )
    """,

    # partsupp
    """
    IF OBJECT_ID('dbo.partsupp', 'U') IS NULL
    CREATE TABLE dbo.partsupp (
        ps_partkey    INTEGER        NOT NULL,
        ps_suppkey    INTEGER        NOT NULL,
        ps_availqty   INTEGER        NOT NULL,
        ps_supplycost DECIMAL(15,2)  NOT NULL,
        ps_comment    VARCHAR(199)   NOT NULL,
        CONSTRAINT pk_partsupp PRIMARY KEY (ps_partkey, ps_suppkey),
        CONSTRAINT fk_partsupp_part
            FOREIGN KEY (ps_partkey) REFERENCES dbo.part (p_partkey),
        CONSTRAINT fk_partsupp_supplier
            FOREIGN KEY (ps_suppkey) REFERENCES dbo.supplier (s_suppkey)
    )
    """,

    # orders
    """
    IF OBJECT_ID('dbo.orders', 'U') IS NULL
    CREATE TABLE dbo.orders (
        o_orderkey      INTEGER        NOT NULL,
        o_custkey       INTEGER        NOT NULL,
        o_orderstatus   CHAR(1)        NOT NULL,
        o_totalprice    DECIMAL(15,2)  NOT NULL,
        o_orderdate     DATE           NOT NULL,
        o_orderpriority CHAR(15)       NOT NULL,
        o_clerk         CHAR(15)       NOT NULL,
        o_shippriority  INTEGER        NOT NULL,
        o_comment       VARCHAR(79)    NOT NULL,
        CONSTRAINT pk_orders PRIMARY KEY (o_orderkey),
        CONSTRAINT fk_orders_customer
            FOREIGN KEY (o_custkey) REFERENCES dbo.customer (c_custkey)
    )
    """,

    # lineitem
    """
    IF OBJECT_ID('dbo.lineitem', 'U') IS NULL
    CREATE TABLE dbo.lineitem (
        l_orderkey      INTEGER        NOT NULL,
        l_partkey       INTEGER        NOT NULL,
        l_suppkey       INTEGER        NOT NULL,
        l_linenumber    INTEGER        NOT NULL,
        l_quantity      DECIMAL(15,2)  NOT NULL,
        l_extendedprice DECIMAL(15,2)  NOT NULL,
        l_discount      DECIMAL(15,2)  NOT NULL,
        l_tax           DECIMAL(15,2)  NOT NULL,
        l_returnflag    CHAR(1)        NOT NULL,
        l_linestatus    CHAR(1)        NOT NULL,
        l_shipdate      DATE           NOT NULL,
        l_commitdate    DATE           NOT NULL,
        l_receiptdate   DATE           NOT NULL,
        l_shipinstruct  CHAR(25)       NOT NULL,
        l_shipmode      CHAR(10)       NOT NULL,
        l_comment       VARCHAR(44)    NOT NULL,
        CONSTRAINT pk_lineitem PRIMARY KEY (l_orderkey, l_linenumber),
        CONSTRAINT fk_lineitem_orders
            FOREIGN KEY (l_orderkey) REFERENCES dbo.orders (o_orderkey),
        CONSTRAINT fk_lineitem_partsupp
            FOREIGN KEY (l_partkey, l_suppkey) REFERENCES dbo.partsupp (ps_partkey, ps_suppkey)
    )
    """,
]

# Tables in load order (parent tables before child tables)
TABLES = ["region", "nation", "part", "supplier", "customer", "partsupp", "orders", "lineitem"]


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_table(conn, table_name: str):
    path = f"{DATA_DIR}/{table_name}.parquet"
    print(f"  Reading {path} ...")
    arrow_table = pq.read_table(path)
    print(f"  {arrow_table.num_rows:,} rows, schema: {arrow_table.schema}")

    # Cast decimal columns to float64; pyodbc will insert them as floats and
    # SQL Server will coerce back to DECIMAL via the table DDL.
    arrays = []
    for field in arrow_table.schema:
        col = arrow_table.column(field.name)
        if pa.types.is_decimal(field.type):
            col = col.cast(pa.float64())
        arrays.append(col)
    arrow_table = pa.table(dict(zip(arrow_table.schema.names, arrays)))

    columns = arrow_table.schema.names
    placeholders = ", ".join("?" for _ in columns)
    col_list = ", ".join(columns)
    insert_sql = f"INSERT INTO dbo.{table_name} ({col_list}) VALUES ({placeholders})"

    # Convert arrow table to list of Python tuples
    rows = list(zip(*[arrow_table.column(c).to_pylist() for c in columns]))

    cur = conn.cursor()
    for i in range(0, len(rows), BATCH_SIZE):
        cur.executemany(insert_sql, rows[i : i + BATCH_SIZE])
    conn.commit()
    cur.close()
    print(f"  Loaded {arrow_table.num_rows:,} rows into {table_name}.")


def main():
    wait_for_mssql()
    create_database()

    conn = pyodbc.connect(make_conn_str(MSSQL_DB), autocommit=False)

    print("Creating schema ...")
    cur = conn.cursor()
    for stmt in DDL_STATEMENTS:
        cur.execute(stmt)
    conn.commit()
    cur.close()
    print("Schema created.")

    for table in TABLES:
        print(f"\nLoading {table} ...")
        load_table(conn, table)

    conn.close()
    print("\nAll TPC-H tables loaded successfully!")


if __name__ == "__main__":
    main()
