#!/usr/bin/env bash
set -euo pipefail

usage() {
  /bin/cat <<'EOF'
Usage: ./checks/openbsd/inspect_openbsd_v0.sh [--contract|--collect|--inspect-private]

  --contract  Print the bounded read-only v0 contract.
  --collect   Emit minimized posture booleans and counts only.
  --inspect-private  Print raw native OpenBSD state with a local sensitive warning.
EOF
}

print_contract() {
  /bin/cat <<'EOF'
contract_version=v0
platform=openbsd
read_only=true
collection_boundary=allowlisted
policy_gate=deterministic
unknown_is_not_pass=true
fail_or_error_abort=true
unbounded_retry=false
allowlisted_commands=uname,ifconfig,route,pfctl,rcctl,sysctl,cat
public_output=minimized_posture_only
private_inspection=explicit_only
EOF
}

print_sensitive_warning() {
  /bin/cat <<'EOF'
LOCAL SENSITIVE OUTPUT
DO NOT UPLOAD OR APPEND TO LOG.0
EOF
}

bool_from_zero() {
  if [ "${1}" -gt 0 ]; then
    echo true
  else
    echo false
  fi
}

run_capture() {
  "$@" 2>/dev/null
}

capture_native_state() {
  raw_uname="$(run_capture uname -srm)" || return 1
  raw_ifconfig="$(run_capture ifconfig -A)" || return 1
  raw_route="$(run_capture route -n show)" || return 1
  raw_pf_info="$(run_capture pfctl -s info)" || return 1
  raw_pf_rules="$(run_capture pfctl -sr)" || return 1
  raw_pf_nat="$(run_capture pfctl -sn)" || return 1
  raw_rcctl="$(run_capture rcctl ls on)" || return 1
  raw_sysctl="$(run_capture sysctl net.inet.ip.forwarding)" || return 1
  if [ -r /etc/resolv.conf ]; then
    raw_resolv="$(run_capture cat /etc/resolv.conf)" || return 1
  else
    raw_resolv=""
  fi
}

print_public_collect() {
  local interface_count pf_rule_count pf_nat_rule_count service_enabled_count resolver_entry_count
  local forwarding_enabled default_route_present pf_enabled resolver_config_present resolver_search_domain_present

  interface_count="$(printf '%s\n' "${raw_ifconfig}" | awk '/flags=/{count++} END{print count+0}')"
  pf_rule_count="$(printf '%s\n' "${raw_pf_rules}" | awk 'NF{count++} END{print count+0}')"
  pf_nat_rule_count="$(printf '%s\n' "${raw_pf_nat}" | awk 'NF{count++} END{print count+0}')"
  service_enabled_count="$(printf '%s\n' "${raw_rcctl}" | awk 'NF{count++} END{print count+0}')"
  resolver_entry_count="$(printf '%s\n' "${raw_resolv}" | awk '/^[[:space:]]*nameserver[[:space:]]+/ {count++} END{print count+0}')"

  forwarding_enabled=false
  if printf '%s\n' "${raw_sysctl}" | grep -Eq '[=:][[:space:]]*1([[:space:]]|$)'; then
    forwarding_enabled=true
  fi

  default_route_present=false
  if printf '%s\n' "${raw_route}" | grep -Eq '(^|[[:space:]])default([[:space:]:]|$)'; then
    default_route_present=true
  fi

  pf_enabled=false
  if printf '%s\n' "${raw_pf_info}" | grep -Eq 'Status:[[:space:]]+Enabled'; then
    pf_enabled=true
  fi

  resolver_config_present="$(bool_from_zero "${resolver_entry_count}")"

  resolver_search_domain_present=false
  if printf '%s\n' "${raw_resolv}" | grep -Eq '^[[:space:]]*(search|domain)[[:space:]]+'; then
    resolver_search_domain_present=true
  fi

  print_contract
  /bin/cat <<EOF
output_mode=public_minimized
kernel_forwarding_enabled=${forwarding_enabled}
default_route_present=${default_route_present}
pf_enabled=${pf_enabled}
interface_count=${interface_count}
pf_rule_count=${pf_rule_count}
pf_nat_rule_count=${pf_nat_rule_count}
service_enabled_count=${service_enabled_count}
resolver_config_present=${resolver_config_present}
resolver_entry_count=${resolver_entry_count}
resolver_search_domain_present=${resolver_search_domain_present}
result=PASS
EOF
}

print_private_inspect() {
  print_sensitive_warning
  print_contract

  printf '== uname ==\n%s\n' "${raw_uname}"
  printf '== ifconfig ==\n%s\n' "${raw_ifconfig}"
  printf '== route ==\n%s\n' "${raw_route}"
  printf '== pf info ==\n%s\n' "${raw_pf_info}"
  printf '== pf rules ==\n%s\n' "${raw_pf_rules}"
  printf '== pf nat ==\n%s\n' "${raw_pf_nat}"
  printf '== rcctl ==\n%s\n' "${raw_rcctl}"
  printf '== sysctl ==\n%s\n' "${raw_sysctl}"
  printf '== resolv.conf ==\n%s\n' "${raw_resolv:-unavailable}"
  echo "result=PASS"
}

MODE="${1:---contract}"

case "${MODE}" in
  --contract)
    print_contract
    exit 0
    ;;
  --collect)
    ;;
  --inspect-private)
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

platform="${OPENBSD_V0_FORCE_PLATFORM:-$(uname -s 2>/dev/null || echo unknown)}"
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

if ! capture_native_state; then
  echo "result=ERROR"
  exit 1
fi

case "${MODE}" in
  --collect)
    print_public_collect
    ;;
  --inspect-private)
    print_private_inspect
    ;;
esac
