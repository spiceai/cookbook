# Postgres Data Connector

This recipe will use a demo instance of Postgres with a dataset generated using SQL stored procedure. Follow the recipe to create Postgres instance and get started with Postgres as a Data Connector.

## Pre-requisites

- Install [PostgresSQL](https://www.postgresql.org/download/). Once downloaded and installed, run the following commands:

```bash
createdb --help
psql --help
```

- Spice is installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation).

## Steps

**Step 1.** Create a sample Postgres database and generate a testing table using stored procedure.

- Start postgres server (note: this is an insecure postgres, only use for testing).

```bash
docker run --name postgres -e POSTGRES_HOST_AUTH_METHOD=trust  -d -p 5432:5432 postgres
```

- Configure postgres settings

```bash
export PGHOST=localhost
export PGPORT=5432
export PGUSER=postgres
```

Create an empty database `spice_demo` in local Postgres.

```bash
createdb spice_demo
```

Verify the creation of `spice_demo` by openning it with psql CLI.

```bash
psql spice_demo
```

Create a sample table named `sample_data`.

```SQL
CREATE TABLE sample_data (
  id BIGSERIAL PRIMARY KEY,
  datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  name VARCHAR(255) DEFAULT NULL,
  phone VARCHAR(20) DEFAULT NULL,
  email VARCHAR(255) DEFAULT NULL,
  street_address VARCHAR(255) DEFAULT NULL,
  zip_code VARCHAR(10) DEFAULT NULL,
  region VARCHAR(100) DEFAULT NULL,
  latitude DECIMAL(9,6) DEFAULT NULL,
  longitude DECIMAL(9,6) DEFAULT NULL
);
```

Create a stored procedure for generating data in `sample_data`.

```SQL
CREATE PROCEDURE sample_data_gen()
LANGUAGE plpgsql
AS $$
DECLARE
  i INT := 0;
BEGIN
  WHILE i < 20000 LOOP
    INSERT INTO sample_data (
      datetime, name, phone, email, street_address, zip_code, region, latitude, longitude
    ) VALUES (
      TIMESTAMP '2024-01-01 01:00:00' + INTERVAL '1 second' * FLOOR(RANDOM() * 31536000),
      'Name' || FLOOR(RANDOM() * 100),
      '555-' || LPAD(FLOOR(RANDOM() * 10000)::TEXT, 4, '0'),
      'user' || FLOOR(RANDOM() * 100) || '@example.com',
      'Street' || FLOOR(RANDOM() * 100) || ' Avenue',
      LPAD(FLOOR(RANDOM() * 100000)::TEXT, 5, '0'),
      'Region' || FLOOR(RANDOM() * 10),
      ROUND(CAST(-90 + (180 * RANDOM()) AS NUMERIC), 6),
      ROUND(CAST(-180 + (360 * RANDOM()) AS NUMERIC), 6)
    );
    i := i + 1;
  END LOOP;
END $$;
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
DROP PROCEDURE sample_data_gen();
```

Check the sample data generated in the `sample_data` table.

```SQL
SELECT * FROM sample_data LIMIT 10;
```

```bash
 id |      datetime       |  name  |  phone   |       email        | street_address  | zip_code | region  |  latitude  |  longitude
----+---------------------+--------+----------+--------------------+-----------------+----------+---------+------------+-------------
  1 | 2024-03-24 15:32:29 | Name86 | 555-7511 | user61@example.com | Street28 Avenue | 99036    | Region1 |  37.401720 |   98.195050
  2 | 2024-03-13 23:26:47 | Name51 | 555-7673 | user14@example.com | Street50 Avenue | 56498    | Region9 | -48.121413 |   24.399114
  3 | 2024-03-14 04:48:57 | Name18 | 555-4908 | user5@example.com  | Street94 Avenue | 90463    | Region7 | -43.850714 | -133.347619
  4 | 2024-04-28 07:05:48 | Name58 | 555-4262 | user90@example.com | Street38 Avenue | 38997    | Region9 | -64.336487 | -169.703826
  5 | 2024-12-05 01:13:01 | Name62 | 555-2014 | user21@example.com | Street22 Avenue | 24267    | Region9 |  -0.871213 | -136.917815
  6 | 2024-06-11 09:33:40 | Name60 | 555-2465 | user80@example.com | Street87 Avenue | 57574    | Region4 | -16.725530 |  -48.126485
  7 | 2024-11-06 02:22:00 | Name51 | 555-9568 | user5@example.com  | Street72 Avenue | 66055    | Region4 |  85.865851 |  -73.635508
  8 | 2024-05-31 18:15:45 | Name13 | 555-8721 | user55@example.com | Street21 Avenue | 96491    | Region8 |  49.269070 | -158.880790
  9 | 2024-04-30 06:13:46 | Name67 | 555-1919 | user74@example.com | Street49 Avenue | 90063    | Region6 | -59.289773 |  -86.577233
 10 | 2024-02-29 03:27:14 | Name12 | 555-2194 | user47@example.com | Street47 Avenue | 35029    | Region1 |   6.813841 |   52.001473
(10 rows)
```

**Step 2.** Initialize a Spice app.

```bash
spice init postgres-connector-demo
cd postgres-connector-demo
```

**Step 3.** Configure the dataset to connect to Postgres. Copy and paste the configuration below to `spicepod.yaml` in the Spice app.

```yaml
version: v1beta1
kind: Spicepod
name: postgres-connector-demo
datasets:
  - from: postgres:sample_data
    name: sample_data
    params:
      pg_host: localhost
      pg_port: 5432
      pg_db: spice_demo
      pg_sslmode: disable
      pg_user: postgres
```

Ensure that the `pg_pass` connctor parameter is only set when `pg_user` used in spicepod requires a password.

**Step 4.** Start the Spice runtime

```bash
spice run
```

Follow the [getting started guide](https://docs.spiceai.org/getting-started) to get started with the Spice.ai runtime.

See the [datasets reference](https://docs.spiceai.org/reference/spicepod/datasets) for more dataset configuration options.

**Step 5.** Run queries against the dataset using the Spice SQL REPL.

In a new terminal, start the Spice SQL REPL

```bash
spice sql
```

List available datasets in spice runtime.

```sql
sql> show tables;
+---------------+--------------+---------------+------------+
| table_catalog | table_schema | table_name    | table_type |
+---------------+--------------+---------------+------------+
| spice         | public       | sample_data   | BASE TABLE |
| spice         | runtime      | task_history  | BASE TABLE |
| spice         | runtime      | metrics       | BASE TABLE |
+---------------+--------------+---------------+------------+

Time: 0.028967208 seconds. 4 rows.
```

You can now now query `sample_data` in the runtime.

```sql
sql> select * from sample_data limit 10;
+----+---------------------+--------+----------+--------------------+-----------------+----------+---------+------------+-------------+
| id | datetime            | name   | phone    | email              | street_address  | zip_code | region  | latitude   | longitude   |
+----+---------------------+--------+----------+--------------------+-----------------+----------+---------+------------+-------------+
| 1  | 2024-03-24T15:32:29 | Name86 | 555-7511 | user61@example.com | Street28 Avenue | 99036    | Region1 | 37.401720  | 98.195050   |
| 2  | 2024-03-13T23:26:47 | Name51 | 555-7673 | user14@example.com | Street50 Avenue | 56498    | Region9 | -48.121413 | 24.399114   |
| 3  | 2024-03-14T04:48:57 | Name18 | 555-4908 | user5@example.com  | Street94 Avenue | 90463    | Region7 | -43.850714 | -133.347619 |
| 4  | 2024-04-28T07:05:48 | Name58 | 555-4262 | user90@example.com | Street38 Avenue | 38997    | Region9 | -64.336487 | -169.703826 |
| 5  | 2024-12-05T01:13:01 | Name62 | 555-2014 | user21@example.com | Street22 Avenue | 24267    | Region9 | -0.871213  | -136.917815 |
| 6  | 2024-06-11T09:33:40 | Name60 | 555-2465 | user80@example.com | Street87 Avenue | 57574    | Region4 | -16.725530 | -48.126485  |
| 7  | 2024-11-06T02:22:00 | Name51 | 555-9568 | user5@example.com  | Street72 Avenue | 66055    | Region4 | 85.865851  | -73.635508  |
| 8  | 2024-05-31T18:15:45 | Name13 | 555-8721 | user55@example.com | Street21 Avenue | 96491    | Region8 | 49.269070  | -158.880790 |
| 9  | 2024-04-30T06:13:46 | Name67 | 555-1919 | user74@example.com | Street49 Avenue | 90063    | Region6 | -59.289773 | -86.577233  |
| 10 | 2024-02-29T03:27:14 | Name12 | 555-2194 | user47@example.com | Street47 Avenue | 35029    | Region1 | 6.813841   | 52.001473   |
+----+---------------------+--------+----------+--------------------+-----------------+----------+---------+------------+-------------+

Time: 0.017579583 seconds. 10 rows.
```

For more information on using `spice sql`, see the [CLI reference](https://docs.spiceai.org/cli/reference/sql).
