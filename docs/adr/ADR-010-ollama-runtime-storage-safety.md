# ADR-010: Ollama Runtime Storage Safety on Shared Production Hosts

## Status
**PROPOSED** — Acceptance requires sign-off from: Infrastructure Owner + AI/Model Engineering lead.
Triggering incident: [INC-20260813-001 — timelabs.ru storage outage](../../reports/INCIDENT_TIMELABS_DISK_20260813.md).

## Date
2026-08-13 (incident date); ADR materialized 2026-08-14.

## Deciders
Infrastructure Engineering; AI/Model Engineering Team; TRAE (reference-architecture materialization).

## Context
A shared-production Plesk node (`timelabs.ru`, 485 GiB single-root partition, hosting ~35 vhosts including `partyglass.ru`, MySQL, Dockerized services, and the Ollama LLM runtime) reached **100% root-filesystem utilization, 0 bytes free** on 2026-08-13. The immediate trigger was two concurrently-initiated large-model pulls through Ollama that:

1. Pre-allocated sparse target blobs of ~90 GiB and ~75 GiB *apparent* size (~70 GiB *physical* blocks) before verifying free-space sufficiency.
2. Aborted mid-stream due to ENOSPC without cleanup hooks on the `*-partial` artifacts.
3. Landed into a partition with only ~20 GiB of headroom against a 163 GiB pre-existing model footprint, ~19 GiB of unbounded logs, and ~19 GiB of duplicated backups — guaranteeing a 0-byte condition.

Post-incident investigation identified **no pre-pull headroom guard, no TTL garbage collector for `*-partial` blobs, no size-limited logrotate policy, and no dedicated AI-model storage volume** as the four compounding architectural causes. This ADR fixes all four.

## Decision

### §1 — Normative Headroom Law (machine-enforceable via `ollama_safe_pull.sh`)
On any host where the Ollama runtime shares a partition with:
- OS binaries or journals (`/`, `/var/log`, `/var/lib/journal`),
- mutable databases (MySQL, PostgreSQL, MariaDB, SQLite),
- web roots / vhost upload directories,
- Docker / containerd storage,

the following inequality **MUST** hold for the filesystem hosting `$OLLAMA_MODELS` **before** any invocation of `ollama pull <tag>` is permitted:

```
FREE_BLOCKS_BYTES  ≥  2.5  ×  MODEL_UNCOMPRESSED_SIZE_BYTES
```

Where the `2.5×` multiplier decomposes into:

| Component | Budget | Rationale |
|---|---:|---|
| Sparse pre-allocation extent | 1.0× | `fallocate()`/`ftruncate()` reserves apparent size before streaming |
| Streaming-in-progress fills | 1.0× | Real extents fill in during download; worst-case both exist |
| Manifest atomic-swap transient | 0.25× | Old + new manifest coexist during rename(2) |
| Co-located workload headroom | 0.25× | DBs / journals / uploads need slack during the pull window |

A ratio of `0` (check bypass) is **NEVER ACCEPTABLE on shared hosts**. On isolated single-purpose AI hosts it may be overridden to `1.5` with explicit Owner sign-off in the environment's `owner_intent` manifest.

### §2 — Mandatory Cleanup Layers on Abort
Every `ollama pull` invocation, whether scripted or interactive, **MUST** be wrapped with two independent cleanup layers that together form defense-in-depth:

1. **In-process trap handler** (signal + error-path): `SIGINT`, `SIGTERM`, `SIGHUP`, `EXIT` with nonzero return code `rm -f` any `*-partial` blob older than 1 minute in `$OLLAMA_MODELS/models/blobs`.
2. **Daily cron TTL sweeper**: `find …/models/blobs -name "*-partial" -mtime +1 -delete`, scheduled at an off-peak hour (e.g. `17 3 * * *` UTC).

Reference implementations:
- Trap layer: [`scripts/ollama_safe_pull.sh`](../../scripts/ollama_safe_pull.sh) §`sweep_partials` trap.
- Cron layer: [`scripts/ollama_cleanup_partials.sh`](../../scripts/ollama_cleanup_partials.sh) (default `MIN_AGE_MINUTES=60` in daily mode, `MIN_AGE_MINUTES=1440` in cron mode).

### §3 — Dedicated Storage Volume for ≥ 70B Parameter / ≥ 40 GiB Models
Any deployment that expects to *ever* pull a model of uncompressed size ≥ 40 GiB (roughly ≥ 70B parameters at Q4 quantization) **MUST NOT** place `$OLLAMA_MODELS` on the same logical volume or partition as OS, DB, vhost, or Docker storage.

Preferred layout (priority order):

| Option | Path | Mount Options | When to use |
|---|---|---|---|
| **(A)** Dedicated block volume | `/mnt/ai-models` | `xfs noatime,nodiratime,inode64,logbsize=256k` | All production shared hosts with ≥ 1 ≥ 40 GiB model |
| **(B)** Bind-mount under /usr | `/usr/share/ollama` → `/mnt/ai-models/ollama` | Same as (A); package default path preserved |
| **(C)** Loopback file on /opt (fallback only) | `/opt/ai-models.img` → `/mnt/ai-models` loop | Development / lab only; never production |
| **(D)** No volume / rootfs-native | `/usr/share/ollama` on `/` | **FORBIDDEN** if any model ≥ 20 GiB resident |

The dedicated volume **MUST** have its own `df`-monitored alerting thresholds (WARN ≥ 80%, CRIT ≥ 92%) separate from the root `/` volume alerting.

### §4 — Daemon Listening Scope
The Ollama daemon (`ollama serve`) **MUST** bind to `127.0.0.1:11434` on any multi-tenant, shared, or production host. Exposures:

- `OLLAMA_HOST=0.0.0.0` or any routable non-loopback address → **FORBIDDEN** without an explicit `owner_intent` manifest + reverse-proxy authentication layer (mTLS or HMAC header).
- If remote API access is required, the only approved pattern is a localhost-bound `ollama serve` fronted by an authenticating nginx/caddy/relayd reverse proxy with mTLS client cert enforcement.

### §5 — Dormant-Model Cull Cadence
A quarterly model-retention review **MUST** be performed. Any local-weight model with:
- 90+ days of zero invocations in the Ollama request log (`~/.ollama/logs/server.log` count per tag), OR
- No downstream `environment.json` / `owner_intent` reference,

is a candidate for `ollama rm` and removal unless the Model Author provides an explicit 90-day retention justification.

### §6 — Logging Guardrails (Causal Co-requisite)
On any host covered by this ADR, the following logging caps are **REQUIRED within 72 hours of adoption**:

- `systemd-journald` (`/etc/systemd/journald.conf`): `SystemMaxUse=500M`, `SystemKeepFree=1G`, `MaxRetentionSec=14day`.
- `logrotate.d/rsyslog`: `size 100M; maxsize 500M; rotate 14; compress; delaycompress` on `syslog`, `auth.log`.
- `btmp`/`wtmp`: `monthly; rotate 12` with `create` directive to prevent unbounded growth.

## Consequences

### Positive
- **Definite**: A repeat of INC-20260813-001 (0-byte root disk) on a shared host through a large Ollama pull is structurally eliminated; the worst case becomes an early-abort `ollama_safe_pull.sh` with a 2 KiB error message instead of a site-wide outage.
- **Operational**: Both cleanup layers (trap + cron) mean a partial blob can at most occupy disk for ~25 hours even if both puller error-path and the Ollama daemon's internal cleanup all fail — compared to unbounded duration in the status quo.
- **Security**: §3 removes the largest single write-workload from the database/vhost volume; §4 eliminates a DoS + intel-gathering vector from port 11434 exposure.
- **Cost clarity**: A dedicated volume (§3) produces accurate AI-workload storage accounting in shared-host billing / attribution contexts.

### Negative
- **Process friction**: `ollama pull <tag>` without the `ollama_safe_pull.sh` wrapper becomes a non-compliant action on shared hosts; wrapper adoption requires muscle-memory change or shell aliasing.
- **Volume planning cost**: §3 requires capacity forecasting for AI models distinct from DB/web — a planning activity that did not previously exist for any host in the current fleet.
- **False rejects**: The 2.5× ratio is conservative; hosts with ~2.1× headroom will be rejected by the guard even though the pull technically fits. This is an intentional design choice (fail closed over fail open); override per §1 final paragraph.

### Binds / Artifacts
| Bound Artifact | Path |
|---|---|
| Incident record | [`INCIDENT_TIMELABS_DISK_20260813.md`](../../reports/INCIDENT_TIMELABS_DISK_20260813.md) |
| Safe pull wrapper (§1 + §2 trap) | [`ollama_safe_pull.sh`](../../scripts/ollama_safe_pull.sh) |
| Cron sweeper (§2 cron) | [`ollama_cleanup_partials.sh`](../../scripts/ollama_cleanup_partials.sh) |
| Future env validation | A future `check.ollama-storage-safety.valid.json` fixture should verify headroom ratio via the Decision Kernel enum |

## Evidence
- timelabs.ru intake `df -h /`: `/dev/sda1  485G  465G  0  100%  /` (2026-08-13 incident intake).
- timelabs.ru post-op `df -h /`: `/dev/sda1  485G  385G  80G  83%  /` (after §1-level manual cleanup of 2 partials).
- `ollama list` inventory: 163 GiB resident across ~28 tags, including 6 × `attacker/leak_model_*_c6526a:latest` artifacts of unconfirmed provenance (see INC §2.3).
- Blob dir listing at incident: two `*-partial` files with apparent sizes 90 GiB and 75 GiB, mtime 2026-08-13 09:24 UTC.
- `find /var/log -name "*.gz" -o -name "*.[0-9]" | wc -l` at incident = 1,466 files totaling 1.9 GiB; `syslog` single-file size 5.1 GiB with no size cap in logrotate.
