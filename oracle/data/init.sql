-- TPCH Sample Data for Oracle Demo
-- This script runs as SYSTEM user and creates tables in the SCOTT schema

-- Connect to the pluggable database
ALTER SESSION SET CONTAINER = FREEPDB1;

-- Create the SCOTT user if it doesn't exist (fallback, should be created by container)
-- Using IDENTIFIED BY to ensure the user exists with the correct password
BEGIN
    EXECUTE IMMEDIATE 'CREATE USER scott IDENTIFIED BY tiger';
EXCEPTION
    WHEN OTHERS THEN
        IF SQLCODE != -1920 THEN -- -1920 = user already exists
            RAISE;
        END IF;
END;
/

-- Grant necessary privileges to SCOTT
GRANT CONNECT, RESOURCE TO scott;
GRANT CREATE SESSION TO scott;
GRANT CREATE TABLE TO scott;
GRANT CREATE VIEW TO scott;
GRANT CREATE SEQUENCE TO scott;
GRANT CREATE PROCEDURE TO scott;
GRANT UNLIMITED TABLESPACE TO scott;

-- Now connect as SCOTT user to create tables in SCOTT schema
CONNECT scott/tiger@localhost:1521/FREEPDB1;

-- Create TPCH lineitem table
CREATE TABLE lineitem (
    L_ORDERKEY      NUMBER(10,0) NOT NULL,
    L_PARTKEY       NUMBER(10,0) NOT NULL,
    L_SUPPKEY       NUMBER(10,0) NOT NULL,
    L_LINENUMBER    NUMBER(10,0) NOT NULL,
    L_QUANTITY      NUMBER(15,2) NOT NULL,
    L_EXTENDEDPRICE NUMBER(15,2) NOT NULL,
    L_DISCOUNT      NUMBER(15,2) NOT NULL,
    L_TAX           NUMBER(15,2) NOT NULL,
    L_RETURNFLAG    CHAR(1) NOT NULL,
    L_LINESTATUS    CHAR(1) NOT NULL,
    L_SHIPDATE      DATE NOT NULL,
    L_COMMITDATE    DATE NOT NULL,
    L_RECEIPTDATE   DATE NOT NULL,
    L_SHIPINSTRUCT  CHAR(25) NOT NULL,
    L_SHIPMODE      CHAR(10) NOT NULL,
    L_COMMENT       VARCHAR2(44) NOT NULL
);

-- Insert sample TPCH lineitem data
INSERT INTO lineitem VALUES (1, 15519, 785, 1, 17.00, 21168.23, 0.04, 0.02, 'N', 'O', DATE '1996-03-13', DATE '1996-02-12', DATE '1996-03-22', 'DELIVER IN PERSON', 'TRUCK', 'egular courts above the');
INSERT INTO lineitem VALUES (1, 67310, 7311, 2, 36.00, 45983.16, 0.09, 0.06, 'N', 'O', DATE '1996-04-12', DATE '1996-02-28', DATE '1996-04-20', 'TAKE BACK RETURN', 'MAIL', 'ly final dependencies: slyly bold');
INSERT INTO lineitem VALUES (1, 63700, 3701, 3, 8.00, 13309.60, 0.10, 0.02, 'N', 'O', DATE '1996-01-29', DATE '1996-12-31', DATE '1996-01-31', 'TAKE BACK RETURN', 'REG AIR', 'riously. regular, express dep');
INSERT INTO lineitem VALUES (1, 2132, 4633, 4, 28.00, 28955.64, 0.09, 0.06, 'N', 'O', DATE '1996-04-21', DATE '1996-03-30', DATE '1996-05-16', 'NONE', 'AIR', 'lites. fluffily even de');
INSERT INTO lineitem VALUES (1, 24027, 1534, 5, 24.00, 22824.48, 0.10, 0.04, 'N', 'O', DATE '1996-03-30', DATE '1996-03-14', DATE '1996-04-01', 'NONE', 'FOB', ' pending foxes. slyly re');
INSERT INTO lineitem VALUES (1, 15635, 638, 6, 32.00, 49620.16, 0.07, 0.02, 'N', 'O', DATE '1996-01-30', DATE '1996-02-07', DATE '1996-02-03', 'DELIVER IN PERSON', 'MAIL', 'arefully slyly ex');
INSERT INTO lineitem VALUES (2, 106170, 1191, 1, 38.00, 44694.46, 0.00, 0.05, 'N', 'O', DATE '1997-01-28', DATE '1997-01-14', DATE '1997-02-02', 'TAKE BACK RETURN', 'RAIL', 'ven requests. deposits breach a');
INSERT INTO lineitem VALUES (3, 4297, 1798, 1, 45.00, 54058.05, 0.06, 0.00, 'R', 'F', DATE '1994-02-02', DATE '1994-01-04', DATE '1994-02-23', 'NONE', 'AIR', 'ongside of the furiously express');
INSERT INTO lineitem VALUES (3, 19036, 6540, 2, 49.00, 46796.47, 0.10, 0.00, 'R', 'F', DATE '1993-11-09', DATE '1993-12-20', DATE '1993-11-20', 'TAKE BACK RETURN', 'RAIL', ' unusual accounts. eve');
INSERT INTO lineitem VALUES (3, 128449, 3474, 3, 27.00, 39890.88, 0.06, 0.07, 'A', 'F', DATE '1994-01-16', DATE '1993-11-22', DATE '1994-01-23', 'DELIVER IN PERSON', 'SHIP', 'nal foxes wake quickly');
INSERT INTO lineitem VALUES (3, 29380, 1883, 4, 2.00, 2618.76, 0.01, 0.06, 'A', 'F', DATE '1993-12-04', DATE '1994-01-07', DATE '1994-01-01', 'NONE', 'TRUCK', 'y. fluffily pending d');
INSERT INTO lineitem VALUES (3, 183095, 650, 5, 28.00, 32986.52, 0.04, 0.00, 'R', 'F', DATE '1993-12-14', DATE '1994-01-10', DATE '1994-01-01', 'NONE', 'FOB', 'ar deposits. blithely final');
INSERT INTO lineitem VALUES (3, 62143, 9158, 6, 26.00, 28733.64, 0.10, 0.02, 'A', 'F', DATE '1993-10-29', DATE '1993-12-18', DATE '1993-11-04', 'TAKE BACK RETURN', 'RAIL', 'sleep quickly. req');
INSERT INTO lineitem VALUES (4, 88035, 5560, 1, 30.00, 28681.50, 0.03, 0.08, 'N', 'O', DATE '1996-01-10', DATE '1995-12-14', DATE '1996-01-18', 'DELIVER IN PERSON', 'REG AIR', '- quickly regular packages sleep');
INSERT INTO lineitem VALUES (4, 5794, 8295, 2, 4.00, 4846.16, 0.09, 0.08, 'N', 'O', DATE '1996-12-28', DATE '1996-12-09', DATE '1997-01-14', 'TAKE BACK RETURN', 'AIR', 'eep blithely bold accou');
INSERT INTO lineitem VALUES (4, 169544, 4556, 3, 11.00, 15904.94, 0.10, 0.03, 'N', 'O', DATE '1996-10-21', DATE '1996-11-17', DATE '1996-10-30', 'NONE', 'REG AIR', 'ar accounts detect slyly');
INSERT INTO lineitem VALUES (5, 108570, 8571, 1, 15.00, 19754.55, 0.02, 0.04, 'R', 'F', DATE '1994-08-08', DATE '1994-10-13', DATE '1994-08-25', 'DELIVER IN PERSON', 'AIR', 'eep blithely bold accou');
INSERT INTO lineitem VALUES (5, 123927, 3928, 2, 26.00, 32281.92, 0.07, 0.08, 'R', 'F', DATE '1994-10-16', DATE '1994-09-25', DATE '1994-10-19', 'NONE', 'FOB', 'ests wake carefully ca');
INSERT INTO lineitem VALUES (5, 37531, 7532, 3, 50.00, 77101.50, 0.08, 0.03, 'A', 'F', DATE '1994-08-13', DATE '1994-10-30', DATE '1994-08-25', 'DELIVER IN PERSON', 'SHIP', 'y pending requests integrate');
INSERT INTO lineitem VALUES (6, 139636, 2150, 1, 37.00, 42560.31, 0.08, 0.03, 'A', 'F', DATE '1992-04-27', DATE '1992-05-15', DATE '1992-05-02', 'TAKE BACK RETURN', 'TRUCK', 'p furiously special foxes');
INSERT INTO lineitem VALUES (7, 182052, 9607, 1, 12.00, 14202.60, 0.07, 0.03, 'N', 'O', DATE '1996-05-07', DATE '1996-03-13', DATE '1996-06-03', 'NONE', 'FOB', ' haggle. carefully express');
INSERT INTO lineitem VALUES (7, 145243, 7750, 2, 9.00, 11804.16, 0.08, 0.08, 'N', 'O', DATE '1996-02-01', DATE '1996-03-02', DATE '1996-02-19', 'TAKE BACK RETURN', 'SHIP', 'y agreements. slyly bold');
INSERT INTO lineitem VALUES (7, 94780, 2290, 3, 46.00, 43645.88, 0.10, 0.07, 'N', 'O', DATE '1996-01-15', DATE '1996-03-27', DATE '1996-02-03', 'COLLECT COD', 'MAIL', ' unusual, regular acco');
INSERT INTO lineitem VALUES (7, 163073, 3074, 4, 28.00, 32293.96, 0.03, 0.04, 'N', 'O', DATE '1996-03-21', DATE '1996-04-08', DATE '1996-04-16', 'NONE', 'FOB', 'ly special requests ');
INSERT INTO lineitem VALUES (7, 156323, 8838, 5, 38.00, 54700.16, 0.05, 0.08, 'N', 'O', DATE '1996-02-11', DATE '1996-02-24', DATE '1996-02-26', 'DELIVER IN PERSON', 'TRUCK', 'ns haggle carefully ironic deposits');
INSERT INTO lineitem VALUES (7, 40921, 922, 6, 35.00, 33482.20, 0.06, 0.03, 'N', 'O', DATE '1996-01-16', DATE '1996-02-23', DATE '1996-01-22', 'TAKE BACK RETURN', 'FOB', 'jole. excuses wake carefully');
INSERT INTO lineitem VALUES (7, 21636, 1637, 7, 5.00, 4650.15, 0.04, 0.02, 'N', 'O', DATE '1996-02-10', DATE '1996-03-26', DATE '1996-02-11', 'NONE', 'MAIL', 'ithely regula');

-- Create additional sample tables for a more complete demonstration
CREATE TABLE orders (
    O_ORDERKEY      NUMBER(10,0) NOT NULL,
    O_CUSTKEY       NUMBER(10,0) NOT NULL,
    O_ORDERSTATUS   CHAR(1) NOT NULL,
    O_TOTALPRICE    NUMBER(15,2) NOT NULL,
    O_ORDERDATE     DATE NOT NULL,
    O_ORDERPRIORITY CHAR(15) NOT NULL,
    O_CLERK         CHAR(15) NOT NULL,
    O_SHIPPRIORITY  NUMBER(10,0) NOT NULL,
    O_COMMENT       VARCHAR2(79) NOT NULL
);

INSERT INTO orders VALUES (1, 370, 'O', 172799.49, DATE '1996-01-02', '5-LOW', 'Clerk#000000951', 0, 'nstructions sleep furiously among');
INSERT INTO orders VALUES (2, 781, 'O', 38426.09, DATE '1996-12-01', '1-URGENT', 'Clerk#000000880', 0, ' foxes. pending, express requests');
INSERT INTO orders VALUES (3, 1234, 'F', 205654.30, DATE '1993-10-14', '5-LOW', 'Clerk#000000955', 0, 'sly final accounts boost. careful');
INSERT INTO orders VALUES (4, 1369, 'O', 56000.91, DATE '1995-10-11', '5-LOW', 'Clerk#000000124', 0, 'sits. slyly regular packages');
INSERT INTO orders VALUES (5, 445, 'F', 144659.20, DATE '1994-07-30', '5-LOW', 'Clerk#000000925', 0, 'quickly. bold deposits sleep slyly');
INSERT INTO orders VALUES (6, 557, 'F', 58749.59, DATE '1992-02-21', '4-NOT SPECIFIED', 'Clerk#000000058', 0, 'ggle. special, final requests');
INSERT INTO orders VALUES (7, 392, 'O', 252004.18, DATE '1996-01-10', '2-HIGH', 'Clerk#000000470', 0, 'ly special requests');

CREATE TABLE customer (
    C_CUSTKEY       NUMBER(10,0) NOT NULL,
    C_NAME          VARCHAR2(25) NOT NULL,
    C_ADDRESS       VARCHAR2(40) NOT NULL,
    C_NATIONKEY     NUMBER(10,0) NOT NULL,
    C_PHONE         CHAR(15) NOT NULL,
    C_ACCTBAL       NUMBER(15,2) NOT NULL,
    C_MKTSEGMENT    CHAR(10) NOT NULL,
    C_COMMENT       VARCHAR2(117) NOT NULL
);

INSERT INTO customer VALUES (370, 'Customer#000000370', 'ynhwmJwzBsL9LWLm', 12, '22-895-641-3466', 1414.29, 'BUILDING', 'ully regular requests. final, regular');
INSERT INTO customer VALUES (781, 'Customer#000000781', 'mZzPbk9A6hXhxXq', 17, '27-329-829-2043', 9506.60, 'AUTOMOBILE', 'ular excuses wake slyly');
INSERT INTO customer VALUES (1234, 'Customer#000001234', 'QxCzH8wuenFOaTC', 8, '18-999-999-9999', 7895.12, 'HOUSEHOLD', 'accounts sleep furiously');
INSERT INTO customer VALUES (1369, 'Customer#000001369', 'TyaxLMoKjibF40h', 18, '28-555-555-5555', 4536.89, 'MACHINERY', 'blithely pending packages');
INSERT INTO customer VALUES (445, 'Customer#000000445', 'GzEzNm4UjFv6BXl', 7, '17-777-777-7777', 2345.67, 'FURNITURE', 'special packages wake');
INSERT INTO customer VALUES (557, 'Customer#000000557', 'OzMwqcDnH4BxSJe', 23, '33-333-333-3333', 6789.01, 'BUILDING', 'carefully final requests');
INSERT INTO customer VALUES (392, 'Customer#000000392', 'GhJyNmJdYs2xHVe', 2, '12-222-222-2222', 8901.23, 'AUTOMOBILE', 'special, express packages');

-- Create primary keys for better performance
ALTER TABLE lineitem ADD CONSTRAINT pk_lineitem PRIMARY KEY (L_ORDERKEY, L_LINENUMBER);
ALTER TABLE orders ADD CONSTRAINT pk_orders PRIMARY KEY (O_ORDERKEY);
ALTER TABLE customer ADD CONSTRAINT pk_customer PRIMARY KEY (C_CUSTKEY);

-- Create foreign keys for referential integrity
ALTER TABLE lineitem ADD CONSTRAINT fk_lineitem_order FOREIGN KEY (L_ORDERKEY) REFERENCES orders(O_ORDERKEY);
ALTER TABLE orders ADD CONSTRAINT fk_orders_customer FOREIGN KEY (O_CUSTKEY) REFERENCES customer(C_CUSTKEY);

COMMIT;
