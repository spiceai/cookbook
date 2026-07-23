-- Runs automatically on first container startup via /docker-entrypoint-initdb.d.
-- Creates the replication user Spice connects with and seeds the demo table.

-- Spice reads the binlog with the minimum privileges: REPLICATION SLAVE,
-- REPLICATION CLIENT, and SELECT.
CREATE USER 'spice'@'%' IDENTIFIED BY 'spice';
GRANT REPLICATION SLAVE, REPLICATION CLIENT, SELECT ON *.* TO 'spice'@'%';
FLUSH PRIVILEGES;

USE spice_demo;
CREATE TABLE orders (
  id       BIGINT AUTO_INCREMENT PRIMARY KEY,
  customer VARCHAR(255),
  amount   DECIMAL(10,2),
  status   VARCHAR(32)
);
INSERT INTO orders (customer, amount, status) VALUES
  ('Alice',   99.99,  'pending'),
  ('Bob',     149.50, 'pending'),
  ('Charlie', 299.00, 'shipped');
