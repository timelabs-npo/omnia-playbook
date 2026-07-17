#!/usr/bin/env bash
set -euo pipefail

JSON_OUTPUT=""
if [ "${1:-}" = "--json-output" ] && [ -n "${2:-}" ]; then
  JSON_OUTPUT="$2"
fi

platform="$(uname -s 2>/dev/null || echo unknown)"
resolver_output=""
status="unsupported"
reason="No supported resolver inspection command for this host"

collect_macos() {
  if command -v scutil >/dev/null 2>&1; then
    scutil --dns
  else
    return 1
  fi
}

collect_linux_openwrt() {
  if [ -r /etc/resolv.conf ]; then
    cat /etc/resolv.conf
  else
    return 1
  fi
}

collect_windows() {
  if command -v powershell >/dev/null 2>&1; then
    powershell -NoProfile -Command "Get-DnsClientServerAddress | Format-List"
  else
    return 1
  fi
}

case "${platform}" in
  Darwin)
    if resolver_output="$(collect_macos 2>/dev/null)"; then
      reason="Read-only macOS resolver inspection via scutil"
      if echo "${resolver_output}" | grep -qi 'nameserver'; then
        status="pass"
      else
        status="fail"
      fi
    else
      status="fail"
      reason="Unable to run scutil --dns"
    fi
    ;;
  Linux)
    if resolver_output="$(collect_linux_openwrt 2>/dev/null)"; then
      reason="Read-only Linux/OpenWrt resolver inspection via /etc/resolv.conf"
      if echo "${resolver_output}" | grep -Eq '^nameserver[[:space:]]+'; then
        status="pass"
      else
        status="fail"
      fi
    else
      status="fail"
      reason="Unable to read /etc/resolv.conf"
    fi
    ;;
  MINGW*|MSYS*|CYGWIN*|Windows_NT)
    if resolver_output="$(collect_windows 2>/dev/null)"; then
      reason="Read-only Windows resolver inspection via Get-DnsClientServerAddress"
      if echo "${resolver_output}" | grep -qi 'ServerAddresses'; then
        status="pass"
      else
        status="fail"
      fi
    else
      status="fail"
      reason="Unable to run PowerShell DNS inspection"
    fi
    ;;
esac

resolvers="$(printf '%s\n' "${resolver_output}" | awk '/^nameserver[[:space:]]+/ {print $2}' | paste -sd ',' -)"

printf 'DNS invariant: inv-dns-explicit-observable-resolvers\n'
printf 'Platform: %s\n' "${platform}"
printf 'Status: %s\n' "${status}"
printf 'Reason: %s\n' "${reason}"
printf 'Observed resolvers: %s\n' "${resolvers:-n/a}"

if [ -n "${JSON_OUTPUT}" ]; then
  python3 - <<'PY' "${JSON_OUTPUT}" "${platform}" "${status}" "${reason}" "${resolvers}" "${resolver_output}"
import json
import sys
from datetime import datetime, timezone

output_path, platform, status, reason, resolvers_csv, raw = sys.argv[1:7]
resolvers = [r for r in resolvers_csv.split(',') if r]
payload = {
    "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
    "invariant_id": "inv-dns-explicit-observable-resolvers",
    "platform": platform,
    "status": status,
    "reason": reason,
    "observed_resolvers": resolvers,
    "raw_output": raw.strip(),
    "read_only": True,
}
with open(output_path, 'w', encoding='utf-8') as fh:
    json.dump(payload, fh, indent=2, sort_keys=True)
    fh.write('\n')
PY
fi
