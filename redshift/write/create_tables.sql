-- TPC-H tables for the write spicepod. Column types match the source Parquet files.
CREATE TABLE IF NOT EXISTS customer (
  c_custkey    INTEGER,
  c_name       VARCHAR(256),
  c_address    VARCHAR(256),
  c_nationkey  INTEGER,
  c_phone      VARCHAR(256),
  c_acctbal    NUMERIC(15,2),
  c_mktsegment VARCHAR(256),
  c_comment    VARCHAR(256)
);

CREATE TABLE IF NOT EXISTS lineitem (
  l_orderkey      INTEGER,
  l_partkey       INTEGER,
  l_suppkey       INTEGER,
  l_linenumber    INTEGER,
  l_quantity      NUMERIC(15,2),
  l_extendedprice NUMERIC(15,2),
  l_discount      NUMERIC(15,2),
  l_tax           NUMERIC(15,2),
  l_returnflag    VARCHAR(256),
  l_linestatus    VARCHAR(256),
  l_shipdate      DATE,
  l_commitdate    DATE,
  l_receiptdate   DATE,
  l_shipinstruct  VARCHAR(256),
  l_shipmode      VARCHAR(256),
  l_comment       VARCHAR(256)
);

CREATE TABLE IF NOT EXISTS nation (
  n_nationkey INTEGER,
  n_name      VARCHAR(256),
  n_regionkey INTEGER,
  n_comment   VARCHAR(256)
);

CREATE TABLE IF NOT EXISTS orders (
  o_orderkey      INTEGER,
  o_custkey       INTEGER,
  o_orderstatus   VARCHAR(256),
  o_totalprice    NUMERIC(15,2),
  o_orderdate     DATE,
  o_orderpriority VARCHAR(256),
  o_clerk         VARCHAR(256),
  o_shippriority  INTEGER,
  o_comment       VARCHAR(256)
);

CREATE TABLE IF NOT EXISTS part (
  p_partkey     INTEGER,
  p_name        VARCHAR(256),
  p_mfgr        VARCHAR(256),
  p_brand       VARCHAR(256),
  p_type        VARCHAR(256),
  p_size        INTEGER,
  p_container   VARCHAR(256),
  p_retailprice NUMERIC(15,2),
  p_comment     VARCHAR(256)
);

CREATE TABLE IF NOT EXISTS partsupp (
  ps_partkey    INTEGER,
  ps_suppkey    INTEGER,
  ps_availqty   INTEGER,
  ps_supplycost NUMERIC(15,2),
  ps_comment    VARCHAR(256)
);

CREATE TABLE IF NOT EXISTS region (
  r_regionkey INTEGER,
  r_name      VARCHAR(256),
  r_comment   VARCHAR(256)
);

CREATE TABLE IF NOT EXISTS supplier (
  s_suppkey   INTEGER,
  s_name      VARCHAR(256),
  s_address   VARCHAR(256),
  s_nationkey INTEGER,
  s_phone     VARCHAR(256),
  s_acctbal   NUMERIC(15,2),
  s_comment   VARCHAR(256)
);
