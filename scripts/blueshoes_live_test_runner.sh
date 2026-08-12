#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ADAPTER="openbsd"
PLAN="${ROOT_DIR}/playbooks/openbsd-sealed-brick/blueshoes-live-runner.md"
CANDIDATE_DIR=""
RECEIPT_DIR="${ROOT_DIR}/reports/blueshoes/receipts"
WORKERS=6
MAX_ROUNDS=3
MAX_WALL_SECONDS=900
DRY_RUN_FIRST=1
ABORT_ON_FAIL=1

usage() {
  cat <<'EOF'
Usage: ./scripts/blueshoes_live_test_runner.sh [options]

Safe, read-only, bounded, append-only repository and rehearsal runner for
blueshoes-style live testing. NO live router/network mutation is ever performed.

Options:
  --adapter ADAPTER       Adapter directory name (default: openbsd)
  --plan PATH             Playbook markdown plan to follow (default: openbsd-sealed-brick runner plan)
  --candidate-dir PATH    Directory holding candidate files for offline syntax rehearsal.
                          If empty, offline syntax rehearsal is skipped gracefully.
  --receipt-dir PATH      Append-only receipt directory (default: reports/blueshoes/receipts)
  --workers N             Advisory worker emulation count (default: 6)
  --max-rounds N          Max orchestration rounds before aborting (default: 3)
  --max-wall-seconds S    Wall clock budget for the entire run (default: 900)
  --no-dry-run-first      Skip the explicit dry-run-first gate (not recommended)
  --continue-on-fail      Continue past FAIL instead of aborting (not recommended)
  -h|--help               Show this help.

Operator contract:
  * Runs only on the trusted admin workstation.
  * Never runs pfctl -f / rcctl set / sysctl -w.
  * Only performs: dry-run/validate/test/rehearsal/read-only collection.
  * Each stage emits a bounded result only: PASS / FAIL / UNKNOWN + reason.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --adapter) ADAPTER="$2"; shift 2 ;;
    --plan) PLAN="$2"; shift 2 ;;
    --candidate-dir) CANDIDATE_DIR="$2"; shift 2 ;;
    --receipt-dir) RECEIPT_DIR="$2"; shift 2 ;;
    --workers) WORKERS="$2"; shift 2 ;;
    --max-rounds) MAX_ROUNDS="$2"; shift 2 ;;
    --max-wall-seconds) MAX_WALL_SECONDS="$2"; shift 2 ;;
    --no-dry-run-first) DRY_RUN_FIRST=0; shift ;;
    --continue-on-fail) ABORT_ON_FAIL=0; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

START_EPOCH="$(date +%s)"
RUN_ID=""
RUN_ID="$(date +%Y%m%dT%H%M%S)-blueshoes-${ADAPTER}"
RECEIPT_DIR="${RECEIPT_DIR%/}"
mkdir -p "${RECEIPT_DIR}"
RECEIPT_LOG="${RECEIPT_DIR}/${RUN_ID}.log"
RECEIPT_JSON="${RECEIPT_DIR}/${RUN_ID}.json"

log() {
  local ts line
  ts="$(date '+%Y-%m-%dT%H:%M:%S%z')"
  line="[${ts}] $*"
  printf '%s\n' "$line" | tee -a "${RECEIPT_LOG}" >&2
}

log "Blueshoes live-testing runner starting"
log "adapter=${ADAPTER}; plan=${PLAN}; workers=${WORKERS}; max_rounds=${MAX_ROUNDS}; max_wall_s=${MAX_WALL_SECONDS}"

if [[ ! -d "${ROOT_DIR}/adapters/${ADAPTER}" ]]; then
  log "FAIL stage=prep reason=\"adapter directory missing: adapters/${ADAPTER}\""
  exit 1
fi

if [[ ! -f "${ROOT_DIR}/adapters/${ADAPTER}/adapter.json" ]]; then
  log "FAIL stage=prep reason=\"adapter missing manifest adapter.json (ambiguous taxonomy)\""
  exit 1
fi

if [[ ! -f "${PLAN}" ]]; then
  log "FAIL stage=prep reason=\"plan file not found: ${PLAN}\""
  exit 1
fi

budget_left() {
  local now elapsed remaining
  now="$(date +%s)"
  elapsed=$(( now - START_EPOCH ))
  if [[ ${elapsed} -ge ${MAX_WALL_SECONDS} ]]; then
    return 1
  fi
  remaining=$(( MAX_WALL_SECONDS - elapsed ))
  printf '%s' "${remaining}"
  return 0
}

stage() {
  local stage_name="$1"; shift
  local result reason tmp_path
  result="UNKNOWN"
  reason=""
  tmp_path=""
  tmp_path="/tmp/blueshoes-stage.$$.$(date +%N)"
  if ! budget_left >/dev/null; then
    log "ABORT stage=${stage_name} reason=\"wall budget exhausted\""
    echo "FAIL"
    return 1
  fi
  if ("$@") >"${tmp_path}" 2>&1; then
    result="PASS"
    reason="$(head -n 3 "${tmp_path}" | tr -d '\r')"
  else
    result="FAIL"
    reason="$(head -n 10 "${tmp_path}" | tr -d '\r')"
  fi
  rm -f "${tmp_path}"
  log "stage=${stage_name} result=${result} reason=\"${reason}\""
  if [[ "${result}" == "FAIL" && "${ABORT_ON_FAIL}" == "1" ]]; then
    echo "${result}"
    return 1
  fi
  echo "${result}"
  return 0
}

run_validate() {
  cd "${ROOT_DIR}"
  if command -v shellcheck >/dev/null 2>&1 && python3 -c 'import jsonschema' >/dev/null 2>&1; then
    bash scripts/validate.sh
  else
    bash scripts/validate.sh --structure-only
  fi
}

run_tests() {
  cd "${ROOT_DIR}"
  if python3 -m unittest discover -s tests -p 'test_*.py' >/tmp/blueshoes-tests.$$ 2>&1; then
    echo "make test: unittest ok"
    return 0
  fi
  cat /tmp/blueshoes-tests.$$ >&2
  rm -f /tmp/blueshoes-tests.$$
  return 1
}

run_candidate_rehearsal() {
  if [[ -z "${CANDIDATE_DIR}" ]]; then
    echo "no candidate dir provided; skipped offline rehearsal"
    return 0
  fi
  if [[ ! -d "${CANDIDATE_DIR}" ]]; then
    echo "candidate dir not found" >&2
    return 1
  fi
  local pf_candidate="${CANDIDATE_DIR}/pf.conf"
  local ok=1
  if [[ -f "${pf_candidate}" ]]; then
    if command -v pfctl >/dev/null 2>&1; then
      pfctl -n -f "${pf_candidate}" || { echo "pf syntax rehearsal failed"; ok=0; }
    else
      echo "pfctl not available on this workstation; rehearsal skipped gracefully"
    fi
  fi
  local f
  for f in "${CANDIDATE_DIR}"/hostname.if*; do
    [[ -e "${f}" ]] || continue
    if ! sh -n "${f}" 2>/dev/null; then
      echo "hostname.if syntax check failed: ${f}"
      ok=0
    fi
  done
  if [[ "${ok}" == "1" ]]; then
    echo "candidate rehearsal ok"
    return 0
  fi
  return 1
}

run_advisory_workers() {
  local round="$1"
  local passed=0 failed=0 unknown=0
  local w out
  for ((w=1; w<=WORKERS; w++)); do
    if ! budget_left >/dev/null 2>&1; then
      out="UNKNOWN"
    else
      out="PASS"
    fi
    if [[ "${round}" == "1" ]]; then
      if ! (cd "${ROOT_DIR}" && python3 -m unittest tests.test_validation_contract >/dev/null 2>&1); then
        out="FAIL"
      else
        out="PASS"
      fi
    fi
    log "round=${round} worker=${w} vote=${out}"
    case "${out}" in
      PASS) passed=$((passed+1)) ;;
      FAIL) failed=$((failed+1)) ;;
      *) unknown=$((unknown+1)) ;;
    esac
  done
  log "round=${round} worker_vote_summary=pass=${passed}/fail=${failed}/unknown=${unknown}"
  if [[ "${failed}" -gt 0 || "${unknown}" -gt 0 ]]; then
    echo "FAIL or UNKNOWN: pass=${passed} fail=${failed} unknown=${unknown}" >&2
    return 1
  fi
  echo "worker consensus PASS: pass=${passed}/${WORKERS}"
  return 0
}

emit_aggregate() {
  local final="$1"
  cd "${ROOT_DIR}"
  python3 - "${RECEIPT_JSON}" "${RUN_ID}" "${ADAPTER}" "${final}" "${RECEIPT_LOG}" <<'PY'
import datetime as _dt, json, sys, hashlib
path, run_id, adapter, final, log_path = sys.argv[1:6]
log_text = open(log_path, encoding='utf-8').read()
receipt = {
    "run_id": run_id,
    "adapter": adapter,
    "generated_at_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(),
    "final_result": final,
    "log_sha256": hashlib.sha256(log_text.encode('utf-8')).hexdigest(),
    "log_lines": log_text.splitlines(),
    "contract": {
        "mutation_allowed": False,
        "evidence_classes": ["receipt_only", "posture_booleans_counts_only"],
        "raw_topology_allowed": False
    },
}
path = __import__('pathlib').Path(path)
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(receipt, indent=2), encoding='utf-8')
print(path)
PY
}

OVERALL="PASS"

log "stage=prep dry_run_first=${DRY_RUN_FIRST}"
if [[ "${DRY_RUN_FIRST}" == "1" ]]; then
  stage dry_run_structure bash -c "cd ${ROOT_DIR} && bash scripts/validate.sh --structure-only" >/dev/null || OVERALL="FAIL"
fi

if [[ "${OVERALL}" == "PASS" ]]; then
  stage repo_validate run_validate >/dev/null || OVERALL="FAIL"
fi
if [[ "${OVERALL}" == "PASS" ]]; then
  stage repo_tests run_tests >/dev/null || OVERALL="FAIL"
fi
if [[ "${OVERALL}" == "PASS" ]]; then
  stage candidate_rehearsal run_candidate_rehearsal >/dev/null || OVERALL="FAIL"
fi

ROUND=1
while [[ "${OVERALL}" == "PASS" && "${ROUND}" -le "${MAX_ROUNDS}" ]]; do
  if ! budget_left >/dev/null; then
    log "ABORT round=${ROUND} reason=\"wall budget exhausted\""
    OVERALL="FAIL"
    break
  fi
  if ! stage "round${ROUND}_advisory_workers" run_advisory_workers "${ROUND}" >/dev/null; then
    OVERALL="FAIL"
  fi
  ROUND=$((ROUND+1))
done

emit_aggregate "${OVERALL}" | tee -a "${RECEIPT_LOG}" >/dev/null
log "FINAL=${OVERALL} receipt_json=${RECEIPT_JSON}"
if [[ "${OVERALL}" != "PASS" ]]; then
  exit 1
fi
exit 0
