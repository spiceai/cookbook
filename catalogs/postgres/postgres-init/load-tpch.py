#!/usr/bin/env python3
"""
Download TPC-H SF1 parquet files and load them into PostgreSQL with
primary keys, proper types, foreign key constraints, and the standard
TPC-H secondary indexes.

Creation order respects FK dependencies:
  region → nation → part, supplier, customer
  supplier + part → partsupp
  customer → orders → lineitem

Secondary indexes are created after the bulk load (faster than maintaining
them during COPY). Without the composite lineitem(l_partkey, l_suppkey) index,
correlated-subquery queries such as TPC-H Q20 fall back to full 6M-row scans
and are effectively unrunnable.
"""

import time
import pyarrow.parquet as pq
import pyarrow as pa
import psycopg2
from psycopg2 import sql
import io
import os

PG_HOST = os.getenv("PG_HOST", "postgres")
PG_PORT = int(os.getenv("PG_PORT", "5432"))
PG_DB   = os.getenv("PG_DB",   "tpch")
PG_USER = os.getenv("PG_USER", "postgres")

DATA_DIR = "/data/tpch_sf1"

# ---------------------------------------------------------------------------
# DDL – tables in FK-safe creation order
# ---------------------------------------------------------------------------

DDL = """
CREATE TABLE IF NOT EXISTS region (
    r_regionkey  INTEGER      NOT NULL,
    r_name       CHAR(25)     NOT NULL,
    r_comment    VARCHAR(152),
    PRIMARY KEY (r_regionkey)
);

CREATE TABLE IF NOT EXISTS nation (
    n_nationkey  INTEGER      NOT NULL,
    n_name       CHAR(25)     NOT NULL,
    n_regionkey  INTEGER      NOT NULL,
    n_comment    VARCHAR(152),
    PRIMARY KEY (n_nationkey),
    CONSTRAINT fk_nation_region
        FOREIGN KEY (n_regionkey) REFERENCES region (r_regionkey)
);

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
);

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
);

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
);

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
);

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
);

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
);
"""

# ---------------------------------------------------------------------------
# Secondary indexes – created after the bulk load. These mirror the standard
# TPC-H index set; the lineitem(l_partkey)/l_suppkey indexes in particular are
# required for correlated-subquery queries like Q20 to run in reasonable time.
# ---------------------------------------------------------------------------

INDEXES = """
CREATE INDEX IF NOT EXISTS idx_region_name               ON region(r_name);
CREATE INDEX IF NOT EXISTS idx_nation_region             ON nation(n_regionkey);
CREATE INDEX IF NOT EXISTS idx_supplier_nation           ON supplier(s_nationkey);
CREATE INDEX IF NOT EXISTS idx_customer_nation           ON customer(c_nationkey);
CREATE INDEX IF NOT EXISTS idx_orders_custkey_orderdate  ON orders(o_custkey, o_orderdate);
-- Composite (l_partkey, l_suppkey): required for the Q20 correlated subquery to
-- resolve via an index lookup instead of a full lineitem scan. Also serves
-- l_partkey-prefix lookups, so a standalone l_partkey index is unnecessary. A
-- single-column l_partkey index alone leaves Q20 effectively unrunnable
-- (observed ~1h49m vs ~0.1s with the composite) on a modestly-resourced host.
CREATE INDEX IF NOT EXISTS idx_lineitem_partkey_suppkey  ON lineitem(l_partkey, l_suppkey);
CREATE INDEX IF NOT EXISTS idx_lineitem_suppkey          ON lineitem(l_suppkey);
CREATE INDEX IF NOT EXISTS idx_lineitem_orderkey         ON lineitem(l_orderkey);
CREATE INDEX IF NOT EXISTS idx_partsupp_part             ON partsupp(ps_partkey);
CREATE INDEX IF NOT EXISTS idx_partsupp_supplier         ON partsupp(ps_suppkey);
CREATE INDEX IF NOT EXISTS idx_part_brand_container      ON part(p_brand, p_container);
"""

# Tables in load order (parent tables before child tables)
TABLES = ["region", "nation", "part", "supplier", "customer", "partsupp", "orders", "lineitem"]


def wait_for_postgres(max_retries=30, delay=2):
    """Retry until postgres is accepting connections."""
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(host=PG_HOST, port=PG_PORT, dbname=PG_DB,
                                    user=PG_USER)
            conn.close()
            print("PostgreSQL is ready.")
            return
        except psycopg2.OperationalError:
            print(f"Waiting for PostgreSQL... ({attempt + 1}/{max_retries})")
            time.sleep(delay)
    raise RuntimeError("PostgreSQL did not become ready in time.")


def arrow_to_csv_bytes(table: pa.Table) -> bytes:
    """Serialise an Arrow table to CSV bytes for COPY FROM."""
    buf = io.BytesIO()
    import pyarrow.csv as pa_csv
    pa_csv.write_csv(table, buf)
    buf.seek(0)
    return buf.read()


def load_table(conn, table_name: str):
    path = f"{DATA_DIR}/{table_name}.parquet"
    print(f"  Reading {path} ...")
    arrow_table = pq.read_table(path)
    print(f"  {arrow_table.num_rows:,} rows, schema: {arrow_table.schema}")

    # Cast any decimal columns to float64 for parquet compatibility,
    # then postgres COPY will coerce back to DECIMAL via the table DDL.
    casts = []
    for field in arrow_table.schema:
        if pa.types.is_decimal(field.type):
            casts.append((field.name, pa.float64()))
        elif pa.types.is_date(field.type):
            # keep as-is; CSV export renders as YYYY-MM-DD which postgres accepts
            casts.append((field.name, field.type))
        else:
            casts.append((field.name, field.type))

    new_schema = pa.schema([pa.field(name, typ) for name, typ in casts])
    arrays = []
    for field in arrow_table.schema:
        col = arrow_table.column(field.name)
        if pa.types.is_decimal(field.type):
            col = col.cast(pa.float64())
        arrays.append(col)
    arrow_table = pa.table(dict(zip(arrow_table.schema.names, arrays)))

    buf = io.BytesIO()
    import pyarrow.csv as pa_csv
    pa_csv.write_csv(arrow_table, buf)
    buf.seek(0)

    with conn.cursor() as cur:
        cur.copy_expert(
            f"COPY {table_name} FROM STDIN WITH (FORMAT CSV, HEADER TRUE)",
            buf,
        )
    conn.commit()
    print(f"  Loaded {arrow_table.num_rows:,} rows into {table_name}.")


def main():
    wait_for_postgres()

    conn = psycopg2.connect(host=PG_HOST, port=PG_PORT, dbname=PG_DB, user=PG_USER)
    conn.autocommit = False

    print("Creating schema ...")
    with conn.cursor() as cur:
        cur.execute(DDL)
    conn.commit()
    print("Schema created.")

    for table in TABLES:
        print(f"\nLoading {table} ...")
        load_table(conn, table)

    print("\nCreating secondary indexes ...")
    with conn.cursor() as cur:
        cur.execute(INDEXES)
    conn.commit()
    print("Secondary indexes created.")

    conn.close()
    print("\nAll TPC-H tables loaded successfully!")


if __name__ == "__main__":
    main()
