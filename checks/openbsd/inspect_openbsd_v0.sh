#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: ./checks/openbsd/inspect_openbsd_v0.sh [--contract|--collect]

  --contract  Print the bounded read-only v0 contract.
  --collect   Run the bounded read-only OpenBSD collection.
EOF
}

print_contract() {
  cat <<'EOF'
contract_version=v0
platform=openbsd
read_only=true
collection_boundary=allowlisted
policy_gate=deterministic
unknown_is_not_pass=true
fail_or_error_abort=true
unbounded_retry=false
allowlisted_commands=uname,ifconfig,route,pfctl,rcctl,sysctl,cat
EOF
}

MODE="${1:---contract}"

case "${MODE}" in
  --contract)
    print_contract
    exit 0
    ;;
  --collect)
    ;;
  -h|--help)
    usage
    exit 0
    ;;
  *)
    echo "Unknown option: ${MODE}" >&2
    usage >&2
    exit 2
    ;;
esac

platform="$(uname -s 2>/dev/null || echo unknown)"
if [ "${platform}" != "OpenBSD" ]; then
  echo "Unsupported platform: ${platform}" >&2
  exit 2
fi

missing=0
for command_name in uname ifconfig route pfctl rcctl sysctl cat; do
  if ! command -v "${command_name}" >/dev/null 2>&1; then
    echo "missing_command=${command_name}" >&2
    missing=1
  fi
done

if [ "${missing}" -ne 0 ]; then
  echo "result=ERROR"
  exit 1
fi

print_contract

printf '== uname ==\n'
uname -srm
printf '== ifconfig ==\n'
ifconfig -A
printf '== route ==\n'
route -n show
printf '== pf info ==\n'
pfctl -s info
printf '== pf rules ==\n'
pfctl -sr
printf '== pf nat ==\n'
pfctl -sn
printf '== rcctl ==\n'
rcctl ls on
printf '== sysctl ==\n'
sysctl net.inet.ip.forwarding
printf '== resolv.conf ==\n'
if [ -r /etc/resolv.conf ]; then
  cat /etc/resolv.conf
else
  echo "unavailable"
fi

echo "result=PASS"
