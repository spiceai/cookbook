#!/usr/bin/env python3
"""
Generate TPC-H data using DuckDB and load it into Microsoft SQL Server with
primary keys, proper types, and foreign key constraints.

Uses DuckDB's built-in TPC-H generator (SF=0.1) — no large file downloads.

Creation order respects FK dependencies:
  region → nation → part, supplier, customer
  supplier + part → partsupp
  customer → orders → lineitem
"""

import time
import duckdb
import pyodbc
import os

MSSQL_HOST     = os.getenv("MSSQL_HOST",     "mssql")
MSSQL_PORT     = int(os.getenv("MSSQL_PORT", "1433"))
MSSQL_DB       = os.getenv("MSSQL_DB",       "tpch")
MSSQL_USER     = os.getenv("MSSQL_USER",     "sa")
MSSQL_PASSWORD = os.getenv("MSSQL_PASSWORD", "SpiceDemo1!")

# Scale factor: 0.1 → ~600K lineitem rows, fast to load
TPCH_SF = float(os.getenv("TPCH_SF", "0.1"))

BATCH_SIZE = 1000

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
    for attempt in range(max_retries):
        try:
            conn = pyodbc.connect(make_conn_str("master"), autocommit=True, timeout=5)
            conn.close()
            print("SQL Server is ready.")
            return
        except Exception:
            print(f"Waiting for SQL Server... ({attempt + 1}/{max_retries})")
            time.sleep(delay)
    raise RuntimeError("SQL Server did not become ready in time.")


def create_database():
    conn = pyodbc.connect(make_conn_str("master"), autocommit=True)
    conn.cursor().execute("IF DB_ID(?) IS NULL CREATE DATABASE tpch", (MSSQL_DB,))
    conn.close()
    print(f"Database '{MSSQL_DB}' ready.")


# ---------------------------------------------------------------------------
# DDL – tables in FK-safe creation order
# ---------------------------------------------------------------------------

DDL_STATEMENTS = [
    """
    IF OBJECT_ID('dbo.region', 'U') IS NULL
    CREATE TABLE dbo.region (
        r_regionkey  INTEGER       NOT NULL,
        r_name       CHAR(25)      NOT NULL,
        r_comment    VARCHAR(152),
        CONSTRAINT pk_region PRIMARY KEY (r_regionkey)
    )
    """,
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

TABLES = ["region", "nation", "part", "supplier", "customer", "partsupp", "orders", "lineitem"]


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_table(duck, mssql_conn, table_name: str):
    result = duck.execute(f"SELECT * FROM {table_name}")
    columns = [desc[0] for desc in result.description]
    rows = result.fetchall()
    num_rows = len(rows)
    print(f"  {num_rows:,} rows")

    placeholders = ", ".join("?" for _ in columns)
    col_list = ", ".join(columns)
    insert_sql = f"INSERT INTO dbo.{table_name} ({col_list}) VALUES ({placeholders})"

    cur = mssql_conn.cursor()
    for i in range(0, len(rows), BATCH_SIZE):
        cur.executemany(insert_sql, rows[i : i + BATCH_SIZE])
    mssql_conn.commit()
    cur.close()
    print(f"  Loaded {num_rows:,} rows into {table_name}.")


def main():
    wait_for_mssql()
    create_database()

    print(f"Generating TPC-H SF={TPCH_SF} with DuckDB ...")
    duck = duckdb.connect()
    duck.execute("INSTALL tpch; LOAD tpch")
    duck.execute(f"CALL dbgen(sf={TPCH_SF})")
    print("TPC-H data generated.")

    mssql_conn = pyodbc.connect(make_conn_str(MSSQL_DB), autocommit=False)

    print("Creating schema ...")
    cur = mssql_conn.cursor()
    for stmt in DDL_STATEMENTS:
        cur.execute(stmt)
    mssql_conn.commit()
    cur.close()
    print("Schema created.")

    for table in TABLES:
        print(f"\nLoading {table} ...")
        load_table(duck, mssql_conn, table)

    duck.close()
    mssql_conn.close()
    print("\nAll TPC-H tables loaded successfully!")


if __name__ == "__main__":
    main()
