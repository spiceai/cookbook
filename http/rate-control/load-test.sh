#!/usr/bin/env bash
# load-test.sh — Run an oha load test against two Spice instances and report results.
#
# Usage:
#   ./load-test.sh [OPTIONS]
#
# Options:
#   -d, --duration    <duration>   oha test duration (default: 30s)
#   -c, --concurrency <n>          concurrent workers per instance (default: 10)
#   -1, --port1       <port>       HTTP port of first instance  (default: 8091)
#   -2, --port2       <port>       HTTP port of second instance (default: 8092)
#   -q, --query       <sql>        SQL query to send (default: items path query)
#   -h, --help                     Show this help message
#
# Example:
#   ./load-test.sh --duration 60s --concurrency 20

set -euo pipefail

# ── Defaults ──────────────────────────────────────────────────────────────────
DURATION="30s"
CONCURRENCY=10
PORT1=8091
PORT2=8092
QUERY="SELECT * FROM local_items WHERE request_path = '/items'"

# ── Argument parsing ──────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    -d|--duration)    DURATION="$2";    shift 2 ;;
    -c|--concurrency) CONCURRENCY="$2"; shift 2 ;;
    -1|--port1)       PORT1="$2";       shift 2 ;;
    -2|--port2)       PORT2="$2";       shift 2 ;;
    -q|--query)       QUERY="$2";       shift 2 ;;
    -h|--help)
      sed -n '2,/^[^#]/{ /^#/s/^# \{0,1\}//p; /^[^#]/q }' "$0"
      exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

# ── Dependency check ──────────────────────────────────────────────────────────
if ! command -v oha &>/dev/null; then
  echo "Error: 'oha' not found. Install it with: cargo install oha" >&2
  exit 1
fi

# Parse duration number for the summary (strip trailing unit letters)
DURATION_SECS="${DURATION//[^0-9]/}"

OUT1="/tmp/oha-${PORT1}.txt"
OUT2="/tmp/oha-${PORT2}.txt"

echo "Starting load test: duration=${DURATION}, concurrency=${CONCURRENCY}, ports=${PORT1}+${PORT2}"
echo ""

# ── Run both oha instances in parallel ───────────────────────────────────────
oha -z "${DURATION}" -c "${CONCURRENCY}" \
    -m POST \
    -H "Content-Type: text/plain" \
    -d "${QUERY}" \
    --no-tui "http://localhost:${PORT1}/v1/sql" > "${OUT1}" 2>&1 &
PID1=$!

oha -z "${DURATION}" -c "${CONCURRENCY}" \
    -m POST \
    -H "Content-Type: text/plain" \
    -d "${QUERY}" \
    --no-tui "http://localhost:${PORT2}/v1/sql" > "${OUT2}" 2>&1 &
PID2=$!

wait "${PID1}" "${PID2}"

# ── Print raw summaries ───────────────────────────────────────────────────────
echo "=== :${PORT1} ==="
grep -E "Success|Total:|Requests/sec|responses" "${OUT1}" || true

echo ""
echo "=== :${PORT2} ==="
grep -E "Success|Total:|Requests/sec|responses" "${OUT2}" || true

# ── Combined summary ──────────────────────────────────────────────────────────
echo ""
echo "=== COMBINED ==="
python3 - <<EOF
import re, sys

duration = ${DURATION_SECS}
files = [("${OUT1}", ${PORT1}), ("${OUT2}", ${PORT2})]
total = 0

for path, port in files:
    try:
        content = open(path).read()
    except FileNotFoundError:
        print(f":{port} -> output file not found: {path}")
        continue
    m = re.search(r'\[200\] (\d+) responses', content)
    if m:
        n = int(m.group(1))
        total += n
        print(f":{port} -> {n} requests (~{n/duration:.1f} req/sec)")
    else:
        print(f":{port} -> no [200] responses found (check {path})")

if total:
    print(f"Total: {total} in {duration}s = {total/duration:.1f} req/sec")
    print()
    print(f"Baseline (no limit):              ~41.3 req/sec")
    print(f"Expected if shared budget:         ~1.0 req/sec combined (~0.5 each)")
    print(f"Expected if independent budgets:   ~2.0 req/sec combined (~1.0 each)")
EOF
