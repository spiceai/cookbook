# MySQL Data Connector

This recipe will use a demo instance of MySQL with a dataset generated using SQL stored procedure. Follow the recipe to create MySQL instance and get started with MySQL as a Data Connector.

## Prerequisites

- Install [MySQL](https://dev.mysql.com/doc/refman/8.0/en/installing.html).
- Spice is installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation).

## Steps

**Step 1.** Create a sample MySQL database and generate a testing table using stored procedure.

Invoke MySQL in the prompt.

```bash
mysql -u USERNAME -pPASSWORD
```

Using the MySQL console, create a sample database named `spice_demo`.

```SQL
CREATE DATABASE spice_demo;
USE spice_demo;
```

Create a sample table named `sample_data`.

```SQL
CREATE TABLE `sample_data`
(
  `id`             bigint(20) NOT NULL AUTO_INCREMENT,
  `datetime`       timestamp  NULL DEFAULT CURRENT_TIMESTAMP,
  `name`           varchar(255) DEFAULT NULL,
  `phone`          varchar(20) DEFAULT NULL,
  `email`          varchar(255) DEFAULT NULL,
  `street_address` varchar(255) DEFAULT NULL,
  `zip_code`       varchar(10) DEFAULT NULL,
  `region`         varchar(100) DEFAULT NULL,
  `latitude`       decimal(9,6) DEFAULT NULL,
  `longitude`      decimal(9,6) DEFAULT NULL,

  PRIMARY KEY (`id`)
);
```

Create a stored procedure for generating data in `sample_data`.

```SQL
DELIMITER $$
CREATE PROCEDURE sample_data_gen()
BEGIN
  DECLARE i INT DEFAULT 0;
  WHILE i < 20000 DO
    INSERT INTO `sample_data` (
      `datetime`, `name`, `phone`, `email`, `street_address`, `zip_code`, `region`, `latitude`, `longitude`
    ) VALUES (
      FROM_UNIXTIME(UNIX_TIMESTAMP('2024-01-01 01:00:00') + FLOOR(RAND() * 31536000)),
      CONCAT('Name', FLOOR(RAND() * 100)),
      CONCAT('555-', LPAD(FLOOR(RAND() * 10000), 4, '0')),
      CONCAT('user', FLOOR(RAND() * 100), '@example.com'),
      CONCAT('Street', FLOOR(RAND() * 100), ' Avenue'),
      LPAD(FLOOR(RAND() * 100000), 5, '0'),
      CONCAT('Region', FLOOR(RAND() * 10)),
      ROUND(-90 + (180 * RAND()), 6),
      ROUND(-180 + (360 * RAND()), 6)
    );
    SET i = i + 1;
  END WHILE;
END$$
DELIMITER ;
```

Call the stored procedure to generate data in `sample_data`.

```SQL
CALL sample_data_gen();
```

```bash
Query OK, 1 row affected (1.92 sec)
```

Drop the stored procedure.

```SQL
DROP PROCEDURE sample_data_gen;
```

Check the sample data generated in the `sample_data` table.

```SQL
SELECT * FROM sample_data LIMIT 10;
```

```bash
+----+---------------------+--------+----------+--------------------+-----------------+----------+---------+------------+-------------+
| id | datetime            | name   | phone    | email              | street_address  | zip_code | region  | latitude   | longitude   |
+----+---------------------+--------+----------+--------------------+-----------------+----------+---------+------------+-------------+
|  1 | 2024-04-21 17:26:52 | Name49 | 555-5584 | user30@example.com | Street85 Avenue | 36728    | Region2 | -50.484340 |  -70.260682 |
|  2 | 2024-11-11 23:19:51 | Name41 | 555-4699 | user10@example.com | Street13 Avenue | 36252    | Region3 |  72.269701 |  -66.940222 |
|  3 | 2024-11-12 01:13:48 | Name38 | 555-3363 | user52@example.com | Street59 Avenue | 42688    | Region3 | -14.786284 | -154.742840 |
|  4 | 2024-02-05 12:45:07 | Name27 | 555-0867 | user60@example.com | Street77 Avenue | 04347    | Region8 | -23.942890 | -130.868949 |
|  5 | 2024-07-31 07:16:24 | Name49 | 555-7441 | user22@example.com | Street90 Avenue | 85108    | Region5 | -68.518797 |  177.533816 |
|  6 | 2024-08-09 21:41:31 | Name5  | 555-4727 | user18@example.com | Street51 Avenue | 00585    | Region4 | -11.677234 |   73.445000 |
|  7 | 2024-03-19 10:41:05 | Name96 | 555-1629 | user93@example.com | Street16 Avenue | 02943    | Region6 | -56.949324 |  163.769050 |
|  8 | 2024-03-22 17:50:09 | Name25 | 555-5982 | user22@example.com | Street35 Avenue | 07752    | Region3 | -16.818093 | -162.236694 |
|  9 | 2024-01-10 21:38:38 | Name98 | 555-8541 | user30@example.com | Street98 Avenue | 00167    | Region0 | -46.053884 | -154.358929 |
| 10 | 2024-08-15 17:31:51 | Name90 | 555-6528 | user54@example.com | Street79 Avenue | 30242    | Region1 |  53.699951 |   24.584954 |
+----+---------------------+--------+----------+--------------------+-----------------+----------+---------+------------+-------------+
10 rows in set (0.00 sec)
```

**Step 2.** Inside MySQL, check the users in the local MySQL instance. Use any of the users from your query result in the later configuration of `mysql_user` in spicepod.yaml.

```SQL
SELECT user FROM mysql.user;
+------------------+
| user             |
+------------------+
| mysql.infoschema |
| mysql.session    |
| mysql.sys        |
| root             |
+------------------+
4 rows in set (0.00 sec)
```

**Step 3.** Initialize a Spice app.

```bash
spice init mysql-demo
cd mysql-demo
```

**Step 4.** Configure the dataset to connect to MySQL. Copy and paste the configuration below to `spicepod.yaml` in the Spice app.

```yaml
version: v1beta1
kind: Spicepod
name: mysql-demo
datasets:
  - from: mysql:spice_demo.sample_data
    name: sample_data
    params:
      mysql_host: localhost
      mysql_tcp_port: 3306
      mysql_db: spice_demo
      mysql_sslmode: disabled
      mysql_user: root
      mysql_pass: ${env:MYSQL_PASS}
```

Ensure the `MYSQL_PASS` environment variable is set to the password for your MySQL instance. Environment variables can be specified on the command line when running the Spice runtime or in a `.env` file in the same directory as `spicepod.yaml`.

```bash
echo "MYSQL_PASS=<password>" > .env
```

**Step 5.** Start the Spice runtime

```bash
spice run
```

Follow the [getting started guide](https://docs.spiceai.org/getting-started) to get started with the Spice.ai runtime.

See the [datasets reference](https://docs.spiceai.org/reference/spicepod/datasets) for more dataset configuration options.

**Step 6.** Run queries against the dataset using the Spice SQL REPL.

In a new terminal, start the Spice SQL REPL

```bash
spice sql
```

You can now now query `sample_data` in the runtime.

```sql
select * from sample_data limit 10;
+----+---------------------+--------+----------+--------------------+-----------------+----------+---------+------------+-------------+
| id | datetime            | name   | phone    | email              | street_address  | zip_code | region  | latitude   | longitude   |
+----+---------------------+--------+----------+--------------------+-----------------+----------+---------+------------+-------------+
| 1  | 2024-12-22T13:15:47 | Name54 | 555-7824 | user28@example.com | Street7 Avenue  | 52178    | Region3 | -26.288629 | 42.540805   |
| 2  | 2024-01-11T14:56:16 | Name29 | 555-3652 | user95@example.com | Street67 Avenue | 52628    | Region5 | -16.801736 | -92.886831  |
| 3  | 2024-12-27T08:49:21 | Name22 | 555-1488 | user7@example.com  | Street91 Avenue | 37329    | Region1 | -11.593564 | 124.084618  |
| 4  | 2024-11-30T14:37:20 | Name4  | 555-4955 | user33@example.com | Street16 Avenue | 83573    | Region6 | 72.989369  | -7.251897   |
| 5  | 2024-09-06T07:14:17 | Name97 | 555-8235 | user19@example.com | Street50 Avenue | 92686    | Region1 | 64.729577  | 149.010004  |
| 6  | 2024-12-27T16:01:57 | Name21 | 555-0879 | user80@example.com | Street75 Avenue | 35681    | Region5 | 8.764192   | -118.093257 |
| 7  | 2024-03-19T02:24:54 | Name55 | 555-1229 | user95@example.com | Street41 Avenue | 19421    | Region7 | -74.996777 | -101.823089 |
| 8  | 2024-11-01T03:03:14 | Name52 | 555-1288 | user6@example.com  | Street92 Avenue | 44372    | Region4 | 66.192141  | -173.042407 |
| 9  | 2024-06-29T04:27:17 | Name40 | 555-5655 | user60@example.com | Street30 Avenue | 72462    | Region7 | -24.397028 | 71.749364   |
| 10 | 2024-05-27T05:28:20 | Name91 | 555-3794 | user14@example.com | Street58 Avenue | 47381    | Region6 | 37.356779  | 57.708228   |
+----+---------------------+--------+----------+--------------------+-----------------+----------+---------+------------+-------------+

Time: 0.011687958 seconds. 10 rows.
```

For more information on using `spice sql`, see the [CLI reference](https://docs.spiceai.org/cli/reference/sql).
