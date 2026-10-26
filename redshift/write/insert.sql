INSERT INTO customer SELECT * FROM customer_source;
INSERT INTO lineitem SELECT * FROM lineitem_source;
INSERT INTO nation SELECT * FROM nation_source;
INSERT INTO orders SELECT * FROM orders_source;
INSERT INTO part SELECT * FROM part_source;
INSERT INTO partsupp SELECT * FROM partsupp_source;
INSERT INTO region SELECT * FROM region_source;
INSERT INTO supplier SELECT * FROM supplier_source;
