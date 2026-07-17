#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPORT_DIR="${ROOT_DIR}/reports"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
JSON_PATH="${REPORT_DIR}/diagnose-${TIMESTAMP}.json"
MD_PATH="${REPORT_DIR}/diagnose-${TIMESTAMP}.md"

mkdir -p "${REPORT_DIR}"

"${ROOT_DIR}/scripts/diagnose.sh" --json-output "${JSON_PATH}" > "/tmp/diagnose-${TIMESTAMP}.txt"

python3 - <<'PY' "${JSON_PATH}" "${MD_PATH}"
import json
import pathlib
import sys

json_path = pathlib.Path(sys.argv[1])
md_path = pathlib.Path(sys.argv[2])
payload = json.loads(json_path.read_text(encoding='utf-8'))

md = [
    f"# Omnia Playbook Diagnostic Report ({payload['timestamp']})",
    "",
    f"- Invariant: `{payload['invariant_id']}`",
    f"- Platform: `{payload['platform']}`",
    f"- Status: `{payload['status']}`",
    f"- Reason: {payload['reason']}",
    f"- Read-only check: `{str(payload['read_only']).lower()}`",
    "",
    "## Observed resolvers",
]
if payload['observed_resolvers']:
    md.extend([f"- `{resolver}`" for resolver in payload['observed_resolvers']])
else:
    md.append("- none detected")

md.extend([
    "",
    "## Raw output",
    "```text",
    payload['raw_output'] or "(no output)",
    "```",
    ""
])

md_path.write_text("\n".join(md), encoding='utf-8')
PY

echo "Wrote ${MD_PATH}"
echo "Wrote ${JSON_PATH}"
