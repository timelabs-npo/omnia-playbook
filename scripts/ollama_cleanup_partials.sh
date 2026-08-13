#!/usr/bin/env bash
set -euo pipefail

BLOBS_DIR_DEFAULT="/usr/share/ollama/.ollama/models/blobs"
MIN_AGE_MINUTES="${MIN_AGE_MINUTES:-60}"
DRY_RUN=0
ACTION="report"

usage() {
  cat <<'USAGE'
ollama_cleanup_partials.sh — TTL garbage collector for *-partial Ollama blobs.

Counterpart to ollama_safe_pull.sh (which handles at-exit / at-interrupt).
This script is intended as:
  (a) a daily cron entry (see below),
  (b) a post-incident one-shot reclaimer,
  (c) a --dry-run inventory for dashboards / observability pipelines.

The default MIN_AGE_MINUTES = 60 (1 hour) is a floor intentionally greater than
the longest single-model pull we expect on a 1 Gbit/s link (~20 minutes for a
70B Q4).  Do NOT set MIN_AGE_MINUTES < 10 in production — you will interrupt
in-progress pulls and cause exactly the orphan you are trying to prevent.

USAGE:
  ollama_cleanup_partials.sh [--report]         # default: inventory only
  ollama_cleanup_partials.sh --delete           # actually remove partials >= age
  ollama_cleanup_partials.sh --dry-run --delete # show what would be deleted
  ollama_cleanup_partials.sh --min-age=1440     # 24-hour TTL instead of 1h
  ollama_cleanup_partials.sh --blobs-dir /alt/path

ENVIRONMENT (all optional):
  OLLAMA_BLOBS_DIR   override (default: /usr/share/ollama/.ollama/models/blobs)
  MIN_AGE_MINUTES    override (default: 60)

CRON EXAMPLE (daily 03:17 UTC, delete anything >= 24h old):
  # /etc/cron.d/ollama-partial-gc
  PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
  MAILTO=root
  17 3 * * * root  MIN_AGE_MINUTES=1440 /usr/local/bin/ollama_cleanup_partials.sh --delete

EXIT CODES:
   0  OK (nothing found, or everything cleaned)
   1  usage / argument error
   2  blobs dir does not exist
   3  find(1) or rm(1) reported error during delete
USAGE
}

log()  { printf '[%s] %s\n' "$(date -u +%H:%M:%SZ)" "$*"; }
warn() { printf '[%s] WARN: %s\n' "$(date -u +%H:%M:%SZ)" "$*" >&2; }
die()  { printf '[%s] FATAL: %s\n' "$(date -u +%H:%M:%SZ)" "$*" >&2; exit "${2:-1}"; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --report)         ACTION="report" ;;
    --delete)         ACTION="delete" ;;
    --dry-run)        DRY_RUN=1 ;;
    --min-age=*)      MIN_AGE_MINUTES="${1#--min-age=}" ;;
    --blobs-dir=*)    BLOBS_DIR_OVERRIDE="${1#--blobs-dir=}" ;;
    -h|--help)        usage; exit 0 ;;
    -*)               die "Unknown option: $1" 1 ;;
    *)                die "Unexpected argument: $1" 1 ;;
  esac
  shift
done

if ! [[ "$MIN_AGE_MINUTES" =~ ^[0-9]+$ ]]; then
  die "--min-age must be a non-negative integer, got: $MIN_AGE_MINUTES" 1
fi

if [[ "$MIN_AGE_MINUTES" -lt 10 ]]; then
  warn "MIN_AGE_MINUTES=$MIN_AGE_MINUTES is below the 10-minute safety floor."
  warn "You risk interrupting in-progress pulls.  Continuing ONLY because you explicitly asked."
fi

BLOBS_DIR="${BLOBS_DIR_OVERRIDE:-${OLLAMA_BLOBS_DIR:-$BLOBS_DIR_DEFAULT}}"

if [[ ! -d "$BLOBS_DIR" ]]; then
  die "Blobs directory does not exist: $BLOBS_DIR" 2
fi

human_bytes() {
  awk -v b="$1" 'BEGIN {
    split("B KiB MiB GiB TiB PiB", u, " ");
    i = 1;
    while (b >= 1024 && i < 6) { b /= 1024; i++; }
    printf "%.2f %s", b, u[i];
  }'
}

log "Scanning $BLOBS_DIR for *-partial blobs >= ${MIN_AGE_MINUTES}m old."
log "  mode : $ACTION $([[ $DRY_RUN -eq 1 ]] && echo "(DRY RUN)")"

TMP_LIST="$(mktemp)"
trap 'rm -f "$TMP_LIST"' EXIT INT TERM HUP

find "$BLOBS_DIR" -type f -name "*-partial" -mmin "+$MIN_AGE_MINUTES" -print0 > "$TMP_LIST"

COUNT="$(tr -cd '\0' < "$TMP_LIST" | wc -c | tr -d ' ')"
BYTES="$(xargs -0 -r stat -c '%s' < "$TMP_LIST" 2>/dev/null | awk '{s+=$1} END {printf "%d", s+0}')"

echo ""
echo "Blobs matching criteria : $COUNT"
echo "Total reclaimable size  : $(human_bytes "$BYTES") ($BYTES bytes)"
echo ""

if [[ "$COUNT" -eq 0 ]]; then
  log "Nothing to do. Exiting clean."
  exit 0
fi

echo "--------------------------------------------------------------------------------"
echo " Candidate files (top 20 by size):"
echo "--------------------------------------------------------------------------------"
xargs -0 -r stat -c '%s %n' < "$TMP_LIST" 2>/dev/null \
  | sort -rn \
  | head -n 20 \
  | awk '{
      b=$1; $1=""; sub(/^ /, "");
      split("B KiB MiB GiB TiB PiB", u, " ");
      i = 1; v=b;
      while (v >= 1024 && i < 6) { v /= 1024; i++; }
      printf "  %8.2f %-3s  %s\n", v, u[i], $0;
    }'
[[ "$COUNT" -gt 20 ]] && echo "  (... $((COUNT - 20)) more not shown)"
echo ""

if [[ "$ACTION" == "report" ]]; then
  log "Report mode. Re-run with --delete to remove the files above, or with --dry-run --delete to preview."
  exit 0
fi

if [[ "$DRY_RUN" -eq 1 ]]; then
  log "DRY RUN. Would have deleted $COUNT files reclaiming $(human_bytes "$BYTES")."
  exit 0
fi

log "Deleting $COUNT files (>= ${MIN_AGE_MINUTES}m old) …"
set +e
xargs -0 -r rm -f -- < "$TMP_LIST"
RC=$?
set -e

if [[ "$RC" -ne 0 ]]; then
  die "rm(1) or xargs(1) exited nonzero rc=$RC during partial-blob delete sweep." 3
fi

REMNANT="$(find "$BLOBS_DIR" -type f -name "*-partial" -mmin "+$MIN_AGE_MINUTES" -print0 | tr -cd '\0' | wc -c | tr -d ' ')"
if [[ "$REMNANT" -ne 0 ]]; then
  die "$REMNANT qualifying partials still present after delete sweep — manual intervention required." 3
fi

log "Sweep complete. Reclaimed $(human_bytes "$BYTES") across $COUNT partial blobs."
exit 0
