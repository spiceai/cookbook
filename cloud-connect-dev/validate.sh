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

# --- The CLI is new enough to have the flow this recipe documents. ----------
echo "CLI"
version="$(spice version 2>/dev/null | sed -n 's/^CLI version: *//p' | head -1)"
if [ -z "$version" ]; then
  no "spice version reports a CLI version"
else
  major_minor="$(printf '%s' "$version" | sed -n 's/^v\{0,1\}\([0-9]\{1,\}\)\.\([0-9]\{1,\}\).*/\1 \2/p')"
  set -- $major_minor
  if [ $# -eq 2 ] && { [ "$1" -gt 2 ] || { [ "$1" -eq 2 ] && [ "$2" -ge 2 ]; }; }; then
    ok "CLI is $version (v2.2+)"
  else
    no "CLI is $version; this recipe needs v2.2 or later"
  fi
fi

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
# The recipe's own files must not carry a key, a token, or an identity.
if [ -n "$tracked" ] &&
  printf '%s\n' "$tracked" | xargs grep -l -E 'spice-enroll-[A-Za-z0-9]|"private_key"|BEGIN [A-Z ]*PRIVATE KEY' 2>/dev/null | grep -q .; then
  no "a tracked recipe file contains credential-shaped material"
else
  ok "no tracked recipe file contains credential-shaped material"
fi
echo

printf '%d passed, %d failed\n' "$pass" "$fail"
if [ "$fail" -eq 0 ]; then
  echo "TEST PASSED"
  exit 0
fi
echo "TEST FAILED"
exit 1
