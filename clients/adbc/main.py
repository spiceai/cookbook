from adbc_driver_flightsql import DatabaseOptions
from adbc_driver_flightsql.dbapi import connect

with connect(
    "grpc://127.0.0.1:50051",
) as conn:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT AccountId,ServiceId,AddOnSid,AddOnTypeSid,AddOnJson,DateCreated,DateUpdated
            FROM addons
            WHERE ServiceId LIKE $1
            LIMIT $2
            """, parameters=("s%9", 3))
        table = cur.fetch_arrow_table()
        print(table)

        cur.execute("""
            SELECT AccountId,ServiceId,AddOnSid,AddOnTypeSid,AddOnJson,DateCreated,DateUpdated
            FROM addons
            WHERE ServiceId=:id_pattern
            LIMIT :batchSize
            """, parameters={"id_pattern": "service123"}) # "batchSize": 5}) # "id_pattern": "s%9",   WHERE ServiceId LIKE :id_pattern
        table = cur.fetch_arrow_table()
        print(table)

    conn.close()
