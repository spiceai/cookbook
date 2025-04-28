from adbc_driver_flightsql import DatabaseOptions
from adbc_driver_flightsql.dbapi import connect

with connect(
    "grpc://127.0.0.1:50051",
) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT $1 + 1 AS the_answer", parameters=(41,))
        table = cur.fetch_arrow_table()
        print(table)

        cur.execute("SELECT 1 AS one")
        table = cur.fetch_arrow_table()
        print(table)

    conn.close()
