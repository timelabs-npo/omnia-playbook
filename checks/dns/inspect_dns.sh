#!/usr/bin/env bash
set -euo pipefail

platform="$(uname -s 2>/dev/null || echo unknown)"
case "${platform}" in
  Darwin)
    if command -v scutil >/dev/null 2>&1; then
      scutil --dns
    else
      echo "scutil unavailable"
      exit 1
    fi
    ;;
  Linux)
    if [ -r /etc/resolv.conf ]; then
      cat /etc/resolv.conf
    else
      echo "/etc/resolv.conf unavailable"
      exit 1
    fi
    ;;
  MINGW*|MSYS*|CYGWIN*|Windows_NT)
    if command -v powershell >/dev/null 2>&1; then
      powershell -NoProfile -Command "Get-DnsClientServerAddress | Format-List"
    else
      echo "powershell unavailable"
      exit 1
    fi
    ;;
  *)
    echo "Unsupported platform: ${platform}"
    exit 2
    ;;
esac
