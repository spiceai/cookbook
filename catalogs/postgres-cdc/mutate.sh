#!/usr/bin/env bash
#
# Mutate the *source* PostgreSQL database while Spice is running, so you can
# watch catalog-level CDC acceleration reflect each change. Every statement
# below runs directly against PostgreSQL (never against Spice) -- Spice picks
# the changes up from the write-ahead log through its shared replication slot.
#
# Each step prints the exact command it runs against PostgreSQL before running
# it, so it's clear what the source mutation is.
#
# After each step, re-run the matching query from the Spice SQL REPL:
#
#     SELECT c_custkey, c_name, c_mktsegment, c_acctbal
#     FROM pg.public.customer
#     WHERE c_custkey = 9999999;
#
# Usage: ./mutate.sh [insert|update|delete|all]

set -euo pipefail

PSQL=(docker exec -i tpch-cdc-postgres psql -U postgres -d tpch -v ON_ERROR_STOP=1)

# Print the exact PostgreSQL command, then run it against the source database.
run_sql() {
  local label=$1 sql=$2
  echo "==> ${label}"
  echo "    \$ docker exec -i tpch-cdc-postgres psql -U postgres -d tpch -c \"${sql}\""
  "${PSQL[@]}" -c "${sql}"
}

insert() {
  run_sql "INSERT customer 9999999 into PostgreSQL" \
    "INSERT INTO customer (c_custkey, c_name, c_address, c_nationkey, c_phone, c_acctbal, c_mktsegment, c_comment) VALUES (9999999, 'Customer#CDC-DEMO', '1 Change Data Capture Way', 0, '00-000-000-0000', 100.00, 'BUILDING', 'inserted via CDC demo');"
}

update() {
  run_sql "UPDATE customer 9999999 acctbal in PostgreSQL" \
    "UPDATE customer SET c_acctbal = 999999.99 WHERE c_custkey = 9999999;"
}

delete() {
  run_sql "DELETE customer 9999999 from PostgreSQL" \
    "DELETE FROM customer WHERE c_custkey = 9999999;"
}

case "${1:-all}" in
  insert) insert ;;
  update) update ;;
  delete) delete ;;
  all)
    insert
    echo "   -> query Spice; you should see 1 row with acctbal 100.00"; echo
    update
    echo "   -> query Spice; acctbal should become 999999.99"; echo
    delete
    echo "   -> query Spice; the row should be gone (0 rows)"; echo
    ;;
  *)
    echo "Usage: $0 [insert|update|delete|all]" >&2
    exit 1
    ;;
esac
