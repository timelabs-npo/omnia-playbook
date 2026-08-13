#!/usr/bin/env bash
set -euo pipefail

RATIO="2.5"
BLOBS_DIR_DEFAULT="/usr/share/ollama/.ollama/models/blobs"
MODEL_NAME=""
OVERRIDE_SIZE_BYTES=""

usage() {
  cat <<'USAGE'
ollama_safe_pull.sh — drop-in "ollama pull" with disk headroom guard + cleanup trap.

Implements the Omnia ADR-010 / INC-20260813-001 rule:
    FREE_SPACE_REQUIRED  >=  RATIO  ×  MODEL_UNCOMPRESSED_SIZE

Default RATIO = 2.5.  Override with --ratio=N.N
If you know the model size ahead of time (recommended for very large pulls),
pass --expect-bytes=BYTES to skip the "ollama show" heuristic and enforce a
floor.

USAGE:
  ollama_safe_pull.sh [--ratio=2.5] [--expect-bytes=N] <model:tag>
  ollama_safe_pull.sh --help

ENVIRONMENT (all optional):
  OLLAMA_BLOBS_DIR   override blob directory (default: /usr/share/ollama/.ollama/models/blobs)
  OLLAMA_BIN         path to ollama binary     (default: $(which ollama))

EXIT CODES:
   0  pull succeeded
   1  usage / argument error
   2  headroom check FAILED — free space < ratio × model size
   3  ollama binary missing or not executable
   4  actual `ollama pull` returned nonzero
   5  trap handler could not sweep partials (informational; original rc preserved)
USAGE
}

log()  { printf '[%s] %s\n' "$(date -u +%H:%M:%SZ)" "$*"; }
warn() { printf '[%s] WARN: %s\n' "$(date -u +%H:%M:%SZ)" "$*" >&2; }
die()  { printf '[%s] FATAL: %s\n' "$(date -u +%H:%M:%SZ)" "$*" >&2; exit "${2:-1}"; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --ratio=*)       RATIO="${1#--ratio=}" ;;
    --expect-bytes=*) OVERRIDE_SIZE_BYTES="${1#--expect-bytes=}" ;;
    -h|--help)       usage; exit 0 ;;
    --)              shift; break ;;
    -*)              die "Unknown option: $1" 1 ;;
    *)               if [[ -z "$MODEL_NAME" ]]; then MODEL_NAME="$1"; else die "Unexpected extra argument: $1" 1; fi ;;
  esac
  shift
done

if [[ -z "$MODEL_NAME" ]]; then
  usage
  exit 1
fi

if ! [[ "$RATIO" =~ ^[0-9]+(\.[0-9]+)?$ ]]; then
  die "--ratio must be a non-negative number, got: $RATIO" 1
fi

OLLAMA_BIN="${OLLAMA_BIN:-$(command -v ollama || true)}"
if [[ -z "$OLLAMA_BIN" || ! -x "$OLLAMA_BIN" ]]; then
  die "ollama binary not found or not executable (OLLAMA_BIN=$OLLAMA_BIN). Install ollama first." 3
fi

BLOBS_DIR="${OLLAMA_BLOBS_DIR:-$BLOBS_DIR_DEFAULT}"
if [[ ! -d "$BLOBS_DIR" ]]; then
  warn "Blobs dir $BLOBS_DIR does not exist yet — will create on first pull"
fi

human_bytes() {
  awk -v b="$1" 'BEGIN {
    split("B KiB MiB GiB TiB PiB", u, " ");
    i = 1;
    while (b >= 1024 && i < 6) { b /= 1024; i++; }
    printf "%.2f %s", b, u[i];
  }'
}

estimate_model_size_bytes() {
  local model="$1"
  local size_line size_val size_unit bytes

  if [[ -n "$OVERRIDE_SIZE_BYTES" ]]; then
    printf '%s' "$OVERRIDE_SIZE_BYTES"
    return 0
  fi

  size_line="$($OLLAMA_BIN show "$model" --modelfile 2>/dev/null || true)"
  size_line="$($OLLAMA_BIN list 2>/dev/null | awk -v m="$model" '$1 == m {print $3, $4; exit}')"
  if [[ -z "$size_line" ]]; then
    warn "Could not look up size for $model via 'ollama list'.  Falling back to 0 — this BYPASSES the headroom check."
    warn "Re-run with --expect-bytes=<bytes> to enforce a proper floor."
    printf '0'
    return 0
  fi

  size_val="$(awk '{print $1}' <<<"$size_line")"
  size_unit="$(awk '{print $2}' <<<"$size_line")"
  bytes="$(awk -v v="$size_val" -v u="$size_unit" 'BEGIN {
    u = toupper(u);
    mul = 1;
    if (u ~ /^KB?$/) mul = 1024;
    else if (u ~ /^MB?$/) mul = 1024*1024;
    else if (u ~ /^GB?$/) mul = 1024*1024*1024;
    else if (u ~ /^TB?$/) mul = 1024*1024*1024*1024;
    printf "%d", v * mul;
  }')"
  printf '%s' "$bytes"
}

SWEEP_RAN=0
sweep_partials() {
  local orig_rc=$?
  local sweep_rc=0
  if [[ $SWEEP_RAN -eq 0 && -d "$BLOBS_DIR" ]]; then
    SWEEP_RAN=1
    log "trap: sweeping *-partial blobs older than 1 minute in $BLOBS_DIR"
    find "$BLOBS_DIR" -type f -name "*-partial" -mmin +1 -print -delete 2>/dev/null || sweep_rc=1
    if [[ $sweep_rc -ne 0 ]]; then
      warn "trap: partial-blob sweep reported errors"
    fi
  fi
  if [[ $orig_rc -ne 0 ]]; then
    exit $orig_rc
  fi
}
trap sweep_partials EXIT INT TERM HUP

FREE_BYTES="$(stat -f -c '%a*%S' "$BLOBS_DIR" 2>/dev/null | bc || true)"
if [[ -z "$FREE_BYTES" ]]; then
  FREE_BYTES="$(df -P -B1 "$BLOBS_DIR" 2>/dev/null | awk 'NR==2 {print $4}')"
fi
if [[ -z "$FREE_BYTES" || ! "$FREE_BYTES" =~ ^[0-9]+$ ]]; then
  die "Could not determine free bytes for $BLOBS_DIR (tried stat -f + df -B1)." 2
fi

MODEL_BYTES="$(estimate_model_size_bytes "$MODEL_NAME")"
REQUIRED_BYTES="$(awk -v f="$FREE_BYTES" -v m="$MODEL_BYTES" -v r="$RATIO" 'BEGIN { printf "%d", m * r }')"

log "MODEL       : $MODEL_NAME"
log "MODEL_SIZE  : $(human_bytes "$MODEL_BYTES") ($MODEL_BYTES B)"
log "HEADROOM_R  : $RATIO x"
log "FREE_BYTES  : $(human_bytes "$FREE_BYTES") ($FREE_BYTES B)"
log "REQUIRED    : $(human_bytes "$REQUIRED_BYTES") ($REQUIRED_BYTES B)"

if [[ "$MODEL_BYTES" -eq 0 ]]; then
  warn "Model size could not be determined -> headroom gate BYPASSED.  Use --expect-bytes=BYTES."
elif [[ "$FREE_BYTES" -lt "$REQUIRED_BYTES" ]]; then
  SHORTFALL="$(awk -v r="$REQUIRED_BYTES" -v f="$FREE_BYTES" 'BEGIN { printf "%d", r - f }')"
  echo ""
  cat <<EOM
================================================================================
  HEADROOM CHECK FAILED  (ADR-010 / INC-20260813-001 §6.1)
  Required headroom not present before pull of $MODEL_NAME.

    Required : $(human_bytes "$REQUIRED_BYTES")   ($RATIO × model)
    Free     : $(human_bytes "$FREE_BYTES")
    Shortfall: $(human_bytes "$SHORTFALL")

  Options (do one, then re-run):
    1. Prune unused models      :  ollama rm <dormant_tag>
    2. Relocate blob dir to dedicated volume :
         mount /mnt/ai-models + export OLLAMA_MODELS=/mnt/ai-models/ollama
    3. Clean unrelated cruft    :  apt-get clean; journalctl --vacuum-size=500M
    4. (unsafe) Override check  :  --ratio=0  (NOT on shared hosts)
================================================================================
EOM
  exit 2
fi

log "HEADROOM OK — proceeding with 'ollama pull $MODEL_NAME'"
log "  (trap handler will sweep partials on interrupt/exit for $BLOBS_DIR)"
echo ""

set +e
$OLLAMA_BIN pull "$MODEL_NAME"
PULL_RC=$?
set -e

if [[ $PULL_RC -ne 0 ]]; then
  die "'ollama pull $MODEL_NAME' exited with rc=$PULL_RC" 4
fi

log "PULL OK — final sweep pass"
sweep_partials
log "Done. $MODEL_NAME safely landed."
exit 0
