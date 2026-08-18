#!/usr/bin/env bash
# Deterministic local checks for the cloud-connect-dev recipe.
#
# Everything here runs without a Spice Cloud account, without a login, and
# without network access to the control plane. It never creates, stores, or
# reads a credential. The cloud-side steps of the README (enrollment, project
# creation, deployment) are not covered — they need an account.
set -uo pipefail

cd "$(dirname "$0")" || exit 1

pass=0
fail=0

ok() {
  printf '  ok   %s\n' "$1"
  pass=$((pass + 1))
}

no() {
  printf '  FAIL %s\n' "$1"
  [ $# -gt 1 ] && printf '       %s\n' "$2"
  fail=$((fail + 1))
}

need() {
  command -v "$1" >/dev/null 2>&1 || {
    printf 'TEST FAILED: %s is required\n' "$1"
    exit 1
  }
}

need spice

echo "cloud-connect-dev validation"
echo

# The checks are ordered so that the ones needing no CLI run first and always
# report. An older CLI stops the flow-specific assertions below, but it says
# nothing about whether this recipe's files agree with each other — and those
# are exactly the checks CI can enforce before the release ships.

# --- The project-name default comes from this directory, not from a random
# --- fallback. The suggestion is the directory's final component, slugified.
echo "Project naming"
dir_name="$(basename "$PWD")"
if [ "$dir_name" = "cloud-connect-dev" ]; then
  ok "recipe directory is 'cloud-connect-dev'"
else
  no "recipe directory is '$dir_name'" "run this from the cloud-connect-dev directory"
fi
# Same contract the CLI validates a project name against: 4-38 characters of
# lowercase letters, digits, and dashes, not starting or ending with a dash.
len=${#dir_name}
if [ "$len" -ge 4 ] && [ "$len" -le 38 ] &&
  printf '%s' "$dir_name" | grep -Eq '^[a-z0-9]([a-z0-9-]*[a-z0-9])?$'; then
  ok "'$dir_name' is a valid project name, so no <adjective>-spice fallback is used"
else
  no "'$dir_name' is not a valid project name" "the CLI would fall back to a generated suggestion"
fi
echo

# --- Nothing secret and nothing generated is staged for commit. -------------
echo "Secrets"
if grep -q '^\.spice/$' .gitignore 2>/dev/null; then
  ok ".spice/ is gitignored"
else
  no ".spice/ is not gitignored" "the issued identity would be committable"
fi
if [ -d .spice ] && git check-ignore -q .spice 2>/dev/null; then
  ok "the local .spice directory is ignored by git"
elif [ ! -d .spice ]; then
  ok "no .spice directory present"
else
  no "a .spice directory exists and git does not ignore it"
fi
tracked="$(git ls-files . 2>/dev/null)"
case "$tracked" in
*.spice/*) no "files under .spice/ are tracked by git" ;;
*) ok "no .spice/ file is tracked by git" ;;
esac

# The recipe's own files must not carry a key, a token, or an identity. Scan
# what git tracks; outside a git checkout, scan the recipe directory instead,
# so the check is never vacuously true.
# This script is excluded: it is the one file in the recipe whose content is
# credential *patterns*, which would match themselves.
scan_files="$(printf '%s\n' "$tracked" | grep -v '^validate\.sh$')"
scan_source="tracked"
if [ -z "$tracked" ]; then
  scan_files="$(find . -type f -not -path './.spice/*' -not -name validate.sh 2>/dev/null)"
  scan_source="recipe"
fi
# An enrollment key is long and opaque. Requiring both length and a letter is
# what separates a real key from the documented `spice-enroll-…` placeholder
# and from the all-digit value used above to prove positional refusal.
key_shaped='spice-enroll-[A-Za-z0-9]{16,}'
has_letter='spice-enroll-[0-9]*[A-Za-z]'
if [ -n "$scan_files" ] &&
  printf '%s\n' "$scan_files" |
  xargs grep -h -o -E "$key_shaped" 2>/dev/null |
  grep -q -E "$has_letter"; then
  no "a $scan_source file contains an enrollment-key-shaped value"
else
  ok "no $scan_source file contains an enrollment-key-shaped value"
fi
if [ -n "$scan_files" ] &&
  printf '%s\n' "$scan_files" |
  xargs grep -l -E '"private_key_pem"|"identity_cert_pem"|BEGIN [A-Z ]*PRIVATE KEY|BEGIN CERTIFICATE' 2>/dev/null |
  grep -q .; then
  no "a $scan_source file contains an identity or private key"
else
  ok "no $scan_source file contains an identity or private key"
fi
echo

# --- The secrets step is internally consistent and carries no credential. ---
#
# None of this needs Spice Cloud: it checks that the recipe asks for the
# password from a delivered secret rather than a literal, that the container
# refuses to start without one, and that the three places naming the database
# agree with each other.
echo "Secrets sync"
if grep -q '\${secrets:pg_password}' README.md; then
  ok "the deployed Spicepod resolves the password from \${secrets:pg_password}"
else
  no "the README's Spicepod does not use \${secrets:pg_password}"
fi
if grep -q 'secrets:' spicepod.yaml; then
  no "the local spicepod declares a secrets: section" "delivered secrets are a built-in store; declaring one makes the Spicepod unportable"
else
  ok "no secrets: section is declared — the delivered store is built in"
fi
if grep -qE 'POSTGRES_PASSWORD: \$\{SPICE_DEMO_PG_PASSWORD:\?' docker-compose.yml; then
  ok "compose reads the password from the environment and fails loudly without it"
else
  no "compose does not read POSTGRES_PASSWORD from the environment with a :? guard"
fi
if grep -q 'CREATE TABLE public.orders' init/01-orders.sql; then
  ok "the seed creates the table the README queries"
else
  no "init/01-orders.sql does not create public.orders"
fi

# The published port, the Spicepod's pg_port, and the psql examples must agree,
# or the reader follows three different databases.
# Quote-agnostic: a formatter may normalise '55432' to "55432", and a check that
# reads only one spelling reports a mismatch that does not exist.
compose_port="$(grep -oE '[0-9]{4,5}:5432' docker-compose.yml | head -1 | cut -d: -f1)"
readme_port="$(grep -oE 'pg_port: .?[0-9]{4,5}' README.md | head -1 | grep -oE '[0-9]{4,5}')"
if [ -n "$compose_port" ] && [ "$compose_port" = "$readme_port" ]; then
  ok "compose publishes $compose_port and the Spicepod connects to it"
else
  no "port mismatch: compose publishes '${compose_port:-?}', the README uses '${readme_port:-?}'"
fi

if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
  if SPICE_DEMO_PG_PASSWORD=validate-only docker compose config >/dev/null 2>&1; then
    ok "docker-compose.yml parses"
  else
    no "docker-compose.yml does not parse" "$(SPICE_DEMO_PG_PASSWORD=validate-only docker compose config 2>&1 | head -3)"
  fi
  # The guard is the point: an unset password must stop the command, not start
  # a database that accepts an empty one.
  if (unset SPICE_DEMO_PG_PASSWORD; docker compose config >/dev/null 2>&1); then
    no "compose accepts an unset SPICE_DEMO_PG_PASSWORD"
  else
    ok "compose refuses to run with SPICE_DEMO_PG_PASSWORD unset"
  fi
else
  printf '  skip docker not available; compose file not parsed\n'
fi
echo

# --- The CLI is new enough to have the flow this recipe documents. ----------
#
# An older CLI still has a `spice connect` command, but it is the superseded
# one: every assertion below would fail for the same single reason. Report that
# reason once and stop, with exit code 2 so a caller can tell "not validated
# here" from "validated and broken".
echo "CLI"
version="$(spice version 2>/dev/null | sed -n 's/^CLI version: *//p' | head -1)"
if [ -z "$version" ]; then
  printf '  FAIL spice version reports no CLI version\n\nTEST FAILED\n'
  exit 1
fi
read -r cli_major cli_minor <<EOF
$(printf '%s' "$version" | sed -n 's/^v\{0,1\}\([0-9]\{1,\}\)\.\([0-9]\{1,\}\).*/\1 \2/p')
EOF
if [ -z "${cli_major:-}" ] || [ -z "${cli_minor:-}" ]; then
  printf '  FAIL could not read a version number from "%s"\n\nTEST FAILED\n' "$version"
  exit 1
fi
if [ "$cli_major" -lt 2 ] || { [ "$cli_major" -eq 2 ] && [ "$cli_minor" -lt 2 ]; }; then
  printf '  skip CLI is %s; this recipe needs v2.2 or later\n' "$version"
  printf '\n%d passed, %d failed before the CLI-dependent checks\n' "$pass" "$fail"
  if [ "$fail" -gt 0 ]; then
    printf 'TEST FAILED\n'
    exit 1
  fi
  printf 'Not validated beyond the file checks: install Spice CLI v2.2+ and re-run.\nTEST SKIPPED\n'
  exit 2
fi
ok "CLI is $version (v2.2+)"

help="$(spice connect --help 2>&1)"
case "$help" in
*'spice connect service install'*) ok "'spice connect service' is the documented service group" ;;
*) no "'spice connect --help' does not describe the service group" ;;
esac
case "$help" in
*'spiced --token'*) ok "help points unattended enrollment at 'spiced --token'" ;;
*) no "help does not mention 'spiced --token' for unattended enrollment" ;;
esac
echo

# --- Status reports a coherent snapshot in both output formats. -------------
echo "Status"
table="$(spice connect status 2>&1)"
if [ $? -eq 0 ]; then
  ok "'spice connect status' exits 0"
else
  no "'spice connect status' exited non-zero" "$table"
fi
case "$table" in
*'Spice Cloud Connect:'*) ok "table output reports a connection state" ;;
*) no "table output has no connection state" "$table" ;;
esac

json="$(spice connect status --output json 2>/dev/null)"
if command -v jq >/dev/null 2>&1; then
  if printf '%s' "$json" | jq -e . >/dev/null 2>&1; then
    ok "'--output json' writes JSON and nothing else to stdout"
  else
    no "'--output json' did not write parseable JSON" "$json"
  fi
  for field in .connection.state .service.state .deployment.state .schema_version; do
    if printf '%s' "$json" | jq -e "$field != null" >/dev/null 2>&1; then
      ok "status JSON has $field"
    else
      no "status JSON is missing $field"
    fi
  done
  # The service object is identical in the full and filtered reports, so
  # automation never has to reconcile two schemas.
  svc_full="$(printf '%s' "$json" | jq -Sc .service 2>/dev/null)"
  svc_only="$(spice connect service status --output json 2>/dev/null | jq -Sc .service 2>/dev/null)"
  if [ -n "$svc_full" ] && [ "$svc_full" = "$svc_only" ]; then
    ok "'connect status' and 'connect service status' render the same service object"
  else
    no "the two status commands disagree about the service object"
  fi
else
  printf '  skip jq not installed; JSON assertions skipped\n'
fi
echo

# --- The interactive flow refuses rather than hanging without a terminal. ---
echo "Non-interactive safety"
out="$(spice connect </dev/null 2>&1)"
code=$?
if [ "$code" -ne 0 ]; then
  ok "non-interactive 'spice connect' exits non-zero instead of prompting"
else
  no "non-interactive 'spice connect' exited 0" "$out"
fi
case "$out" in
*'requires a terminal'*) ok "it explains that setup is interactive" ;;
*) no "it does not explain that setup needs a terminal" "$out" ;;
esac
case "$out" in
*'spiced --token'*) ok "it names the unattended alternative" ;;
*) no "it does not name the unattended alternative" "$out" ;;
esac

# An enrollment key must never ride a positional argument.
out="$(spice connect spice-enroll-000000000000 2>&1)"
case "$out" in
*'not accepted as a positional argument'*) ok "an enrollment key is refused as a positional argument" ;;
*) no "an enrollment key was not refused positionally" "$out" ;;
esac
echo

printf '%d passed, %d failed\n' "$pass" "$fail"
if [ "$fail" -eq 0 ]; then
  echo "TEST PASSED"
  exit 0
fi
echo "TEST FAILED"
exit 1
