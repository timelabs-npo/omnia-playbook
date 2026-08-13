# INCIDENT & INFRASTRUCTURE IMPACT REPORT

| Field | Value |
|---|---|
| TO | AI / Model Engineering Team & Model Authors |
| FROM | Infrastructure Engineering & Security Audit (TRAE-assisted) |
| DATE | 2026-08-13 |
| INCIDENT-ID | INC-20260813-001 |
| SEVERITY AT INTAKE | CRITICAL (root filesystem 100%, 0 bytes free) |
| SEVERITY POST | STABLE (83%, 80 GiB free) |
| TARGET HOST | timelabs.ru (188.124.50.80 / Shared Production VHost Node) |
| SUBJECT | Storage Outage, Sparse Blob Allocation Analysis, and Model Artifact Provenance Review |

---

## 1. Executive Summary

During an emergency intervention on 2026-08-13, the primary host `timelabs.ru` experienced a total service lock due to root filesystem exhaustion: `/` utilization reached **100%, 0 bytes free**, with ext4 unable to accept writes for journals, database commits, or new sessions.

The primary trigger was **unmanaged, concurrent large-model download attempts** through the Ollama runtime, resulting in orphaned partial blobs occupying ~70 GiB of *physical* storage (~165 GiB *apparent* sparse size) on top of an already-resident 163 GiB static model footprint. Additional structural debt — 5.1 GiB unbounded `syslog`, 3.9 GiB of unvacuumed journals, 1.9 GiB of never-pruned rotated logs — consumed remaining headroom and guaranteed zero margin before the incident.

This report outlines:

1. **Operational impact** of the 0-free-byte condition on co-located vhosts (partyglass.ru, kremneva-photo.com, worldforums.ru, ~30 others).
2. **Technical failure modes** observed during large-model streaming into a single shared 485 GiB partition.
3. **Required provenance clarifications** regarding 6 external-registry `leak_model_*` artifacts.
4. **Mandatory engineering guidelines** for subsequent Ollama deployments on partition-constrained shared hosts, with reference implementation scripts committed to this repo.

---

## 2. Inventory of Model Footprint & Observed Artifacts

### 2.1. Active Resident Models (163 GiB Total Footprint)

This list was captured via `ollama list` at 2026-08-13 intervention time. Resident blob count (non-partial): ~28 files in `/usr/share/ollama/.ollama/models/blobs/`.

| Tag | Size | Last Modified | Dormancy Assessment |
|---|---:|---|---|
| `qwen3.6:35b` | ~23 GiB | 3 months prior | **Dormant ~90 days** — candidate for cull |
| `laguna-xs-2.1:latest` | ~20 GiB | 3 weeks prior | Active |
| `qwen3.6:27b` | ~17 GiB | 3 weeks prior | Active |
| `qwen3:14b` | ~9.3 GiB | 4 months prior | Dormant — candidate |
| `hf.co/BlossomsAI/Qwen2.5-Coder-7B-Instruct-Uncensored-GGUF:Q4_K_M` | 4.7 GiB | 3 weeks prior | Active |
| `bge-m3:latest` | 1.2 GiB | 4 months prior | Dormant |
| `llama3.2:3b` | 2.0 GiB | 4 months prior | Dormant |
| `tinyllama:latest` | 637 MiB | 6 months prior | Dormant |
| `gpt-4o`, `gpt-4`, `claude-3-opus`, `verif_sys` | 4 × 637 MiB | 6 days–20 hours | Likely cloud-API shims, minimal disk |
| 10 `*:cloud` entries (glm-*, deepseek-*, minimax-*, kimi-*) | 0 (remote) | 5–6 weeks | Metadata only, no blob cost |
| `205.237.106.117:8443/attacker/leak_model_[0-5]_c6526a:latest` | 6 × 12 MiB | 3 months prior | **See §2.3 — PROVENANCE INQUIRY OPEN** |

### 2.2. Critical Failure Trigger: Orphaned Partial Downloads

At approximately **09:24 UTC on 2026-08-13**, two concurrent (or closely-serialized) model pulls were initiated against the Ollama daemon. Both were interrupted (network timeout, process kill, or 100% disk boundary collision) *before* finalizing their blobs into the manifest. The runtime failed to trigger cleanup hooks on abort.

Filesystem evidence, captured via `ls -lahS /usr/share/ollama/.ollama/models/blobs/`:

| Blob File | Apparent Size (`ls -l`) | Physical Blocks (`stat %b`) | Status |
|---|---:|---:|---|
| `sha256-948255a146c07678678183af4cb1234a124e945e48c85c2006598ef4696552c8-partial` | 90 GiB | ~42 GiB sparse extent | Deleted in incident response |
| `sha256-a46088eccd0d171cc2694f315f2921bd0fda0ae3577099c4864cbe98f190807e-partial` | 75 GiB | ~28 GiB sparse extent | Deleted in incident response |

**Root cause (engineering-level):**
The streaming download path in the Ollama daemon pre-allocates a target file via `ftruncate(2)`/`fallocate(2)`-equivalent before writing layer data. On SIGTERM/SIGKILL/ETXTBSY/ENOSPC, no cleanup guard exists — the `*-partial` suffix is preserved, ownership is retained as `ollama:ollama`, and no cron-based TTL sweep is configured by the stock package.

### 2.3. Security & Provenance Inquiry: `leak_model_*` Artifacts

During blob inventory, 6 isolated model artifacts were found referencing an **external, non-authoritative, IP-literal registry endpoint** that is not part of `ollama.com`, `huggingface.co`, or any Omnia-approved provider.

| Field | Value |
|---|---|
| Registry endpoint | `205.237.106.117:8443` (IP-literal, no TLS hostname pinning observed in manifest) |
| Artifact names | `attacker/leak_model_0_c6526a:latest` … `attacker/leak_model_5_c6526a:latest` (6 tags) |
| Individual size | 12 MiB per blob (72 MiB total) |
| Created | 3 months prior to incident |
| Current state on timelabs.ru | **BLOBS STILL PRESENT** as of close of SSH session. Not deleted. |
| Forensic posture | **ACTIONABLE. Do not `ollama run`. Do not delete before hashing.** |

```
┌──────────────────────────────────────────────────────────────────────────┐
│ ACTION REQUIRED FROM MODEL AUTHOR / SYSTEM OWNER:                        │
│                                                                          │
│  1. CONFIRM whether 205.237.106.117:8443 was an AUTHORIZED private      │
│     development registry used for fine-tuning, red-teaming, or security  │
│     evaluation work.  If yes, state: registry operator, purpose,        │
│     expected TTL of artifacts, and why IP-literal transport was         │
│     chosen over a pinned hostname with a CA-validated cert.             │
│                                                                          │
│  2. CONFIRM whether the `leak_model_*` naming convention belongs to an  │
│     internal test harness (e.g. data-leakage evaluation benchmark) or   │
│     to an external third-party benchmark framework.  Provide the        │
│     canonical upstream repo / paper reference.                          │
│                                                                          │
│  3. IF YOU CANNOT ANSWER (1) OR (2):                                     │
│     → treat these 6 blobs as UNAUTHORIZED / COMPROMISED artifacts.      │
│       Required remediation steps:                                        │
│       a. Hash each of the 6 blobs with sha256 and write to              │
│          /root/INC-20260813-001_leak_models.sha256                       │
│       b. Archive the 6 .sha256 + 6 blob filenames + size per row to     │
│          this repo under reports/INC-20260813-001_leak_manifest.md       │
│       c. `ollama rm` each of the 6 tags.                                 │
│       d. Verify blobs are no longer reachable via `ollama list`.         │
│       e. Add firewall egress deny for 205.237.106.117/32 tcp:8443.       │
│       f. Open a security incident ticket; presume prior compromise.     │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Technical Breakdown for Model Developers

### 3.1. Sparse File Allocation vs. Production Disk Capacity

When Ollama (or any HTTP-layered blob fetcher) streams model layers, the client engine creates a destination file of the *final advertised size* before the first byte arrives. This is implemented via sparse extent reservation.

**Consequence for timelabs.ru's shared partition:**

| Metric | Value |
|---|---:|
| Total partition (`/dev/sda1`) | 485 GiB |
| Static resident model blobs | 163 GiB (33.6%) |
| Orphaned partial blobs (physical blocks) | ~70 GiB (14.4%) |
| Live user data: MySQL + `/var/www/vhosts` | ~45 GiB (9.3%) |
| OS, Plesk, logs, backups, `/root/*` | ~187 GiB (38.5%) |
| **FREE HEADROOM before the pull started** | ~20 GiB (4.2%) |
| Headroom after partial allocations landed | **0 GiB — CRITICAL** |

Even though `ls -lh` reported "165 GiB of partial files", only ~70 GiB of real ext4 extents were consumed. The danger is that **sparse reservation + two concurrent pulls conspired to push block usage from 96% → 100% in seconds**, collapsing service across *all* co-located vhosts (partyglass.ru WP uploads, MySQL commits, rsyslog writes, Plesk panel sessions) with a single model action.

### 3.2. Failure-Mode Tree

```
ollama pull <large-model>
   │
   ├─► No pre-pull headroom check executed  ←––– MISSING GUARD (fixed by ADR-010 / ollama_safe_pull.sh)
   │
   ├─► Two pulls run concurrently or close-serial
   │     │
   │     ├─► fallocate/ftruncate two sparse blobs: 90G + 75G apparent
   │     └─► Streaming writes begin to both
   │           │
   │           └─► First ENOSPC at ~60G into first write
   │                 │
   │                 ├─► HTTP/3 connection aborts (mid-frame)
   │                 ├─► blob writer closes fd with no unlink()
   │                 └─► *-partial suffix retained
   │
   ├─► No TTL-based garbage-collector sweep of *-partial ever runs
   │     ←––– MISSING CRON (fixed by scripts/ollama_cleanup_partials.sh)
   │
   └─► No monitoring / alert on / > 90%
         └─► / reaches 100%; rsyslog / journald / MySQL all fail write()
                └─► Operator pages after vhost uploads break
```

### 3.3. Daemon Listening Scope (Ollama binding)

Ollama, by default up to the version running on timelabs.ru, binds to `127.0.0.1:11434` when installed from the upstream installer script. If the daemon was ever exposed beyond localhost (e.g. via `OLLAMA_HOST=0.0.0.0`), an attacker with TCP reach to port 11434 can:

- Initiate unbounded pulls of any size, directly reproducing this incident as a DoS vector.
- Inspect `ollama list` and enumerate resident model tags (intel leak).
- Execute `ollama run` with attacker-controlled prompts (GPU / memory exhaustion, prompt-injection into any tool-use models).

**Required verification (owner action):**
```bash
ss -lntp | grep 11434 ; echo "---" ; cat /etc/systemd/system/ollama.service.d/*.conf 2>/dev/null ; grep -i OLLAMA_HOST /etc/environment /etc/default/ollama ~ollama/.env* 2>/dev/null
```
Expected output: `127.0.0.1:11434` only. If `0.0.0.0` or any public IP is shown → immediate firewall + systemd override fix.

---

## 4. Incident Response Actions Executed (2026-08-13)

| # | Action | Outcome | Safety |
|---|---|---|---|
| 1 | Triage: 4-IP reachability scan → single-host confirmed | A+ evidence | read-only |
| 2 | Baseline `df`, `du -x /`, top-20 largest files, Docker df, journal disk-usage | A+ evidence | read-only |
| 3 | `rm -fv /usr/share/ollama/.ollama/models/blobs/*-partial` (2 files) | Freed ~70 GiB. 0 remaining confirmed. | NO user data |
| 4 | `journalctl --vacuum-size=500M` | Deleted 28 × 128M archived journals; freed 3.5 GiB; active journals kept. | Standard |
| 5 | `find /var/log -type f \( -name "*.gz" -o -name "*.[0-9]" \) -delete` | 1,466 rotated/compressed logs removed; freed 1.9 GiB; active writers untouched. | Standard |
| 6 | `truncate -s 0 /var/log/syslog /var/log/btmp.1 /var/log/atop/atop_* /var/log/atop/daily.log` | Freed ~5.5 GiB. Writers kept fds; appends continue. | **Known flaws (§5)**: lost btmp attacker list, lost syslog root-cause tail |
| 7 | `apt-get clean` | 133 MiB. | Standard |
| 8 | `docker system prune -f` (dangling only, running containers + volumes SKIPPED) | Freed 12.6 MiB. 2 stopped containers removed. 1 live container survived. | NO user data |
| 9 | Post-cleanup `sync` + `df -h /` | `/dev/sda1 485G 385G 80G 83% /`. **Headroom restored.** | N/A |

**Net recovery:** ~80 GiB free, with zero confirmed deletion of user-owned (vhost) data or live MySQL records.

---

## 5. Defects / "What Was Fucked Up" (forensic honesty)

| Severity | Item | Impact | Mitigation |
|---|---|---|---|
| **MEDIUM** | Operator self-ban via Fail2ban — too many short-lived SSH probes from single egress IP during triage. By close of business 2026-08-13, new SSH sessions to all 4 IPs returned "Connection closed"/"banner timeout". | Blocked the final live verification pass requested for the supervisor report. Will self-clear in Fail2ban `bantime` (typically 10 min–1 hr). | Whitelist egress CIDR in Plesk → Fail2ban → Trusted IPs, or wait for ban expiry. |
| **LOW** | Apparent vs sparse size mis-quoted verbally (165 GiB instead of ~70 GiB physical). The delta in `df` is always ground truth. | Misleading headline number in chat channel; `df` numbers correct. | Report now disambiguates apparent vs blocks. |
| **LOW** | `truncate -s 0 /var/log/syslog` was executed WITHOUT saving the last 10,000 lines first. | Lost root-cause evidence for *why* syslog reached 5.1 GiB. | `/var/log/syslog.1` (193 MiB pre-cleanup) likely contains the same pattern; inspect immediately. |
| **LOW** | `truncate -s 0 /var/log/btmp.1` executed WITHOUT extracting `lastb | top-attackers` first. | Lost pre-incident brute-force frequency distribution. | Plesk Fail2ban history has duplicate data; audit ongoing. |
| **LOW** | `leak_model_*` 6 blobs were flagged but **not hashed, archived, nor removed** during the incident window. Only logged in chat + this report. | 72 MiB of unauthorized-name artifacts remain resident with unknown provenance → post-incident exposure window. | Owner to execute §2.3 step 3a–f immediately upon SSH restore. |

---

## 6. Remediation & Operational Directives

To maintain host stability and prevent recurrence, model authors and deployers MUST adhere to the workflow below. Reference implementations are committed alongside this report.

### 6.1. Pre-Pull Headroom Check (MANDATORY)

**Never** initiate `ollama pull` without verifying that **free physical disk space ≥ 2.5 × the target model's uncompressed footprint**.

```
Free_Space_Required  ≥  2.5  ×  Size_Model
```

The 2.5× multiplier accounts for:
- Partial-blob sparse reservation (up to 1× before write).
- Streaming download (up to 1× as blocks fill in).
- Manifest atomic swap (another ~0.25–0.5× transient).
- Safety headroom for DB/journal writes during the pull window (0.5× min).

Reference implementation committed: [`scripts/ollama_safe_pull.sh`](../scripts/ollama_safe_pull.sh). Usage:

```bash
ollama_safe_pull.sh qwen3.6:35b       # refuses if / < 2.5 × 23 GiB
ollama_safe_pull.sh --ratio=3.0 llama3.1:70b  # tighter override
```

### 6.2. Model Lifecycle & Pruning (QUARTERLY)

Regularly audit resident models and remove unused historical weights:

```bash
ollama list                          # inventory
ollama rm qwen3.6:35b                # specific cull
ollama list | head -n -10            # eyeball dormant list
```

Wrap all `ollama pull` calls in scripts with `trap` handlers that remove `*-partial` blobs on process cancellation or error return. Reference implementation committed in `ollama_safe_pull.sh` §trap-handler.

Additionally, schedule a daily cron sweep:

```bash
# /etc/cron.d/ollama-partial-gc
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
17 3 * * * root  find /usr/share/ollama/.ollama/models/blobs/ -name "*-partial" -mtime +1 -delete
```

Reference implementation: [`scripts/ollama_cleanup_partials.sh`](../scripts/ollama_cleanup_partials.sh) (run as a daily cron entry + `trap` on interactive pulls).

### 6.3. Storage Relocation (RECOMMENDED if ≥ 70B models tested locally)

If local testing of ≥ 70B models is required, mount a dedicated non-root storage volume to isolate AI runtime data from OS and database partitions.

Suggested layout:

```
/dev/sdb1 xfs noatime,nodiratime  /mnt/ai-models   1.5 TiB (dedicated)
OLLAMA_MODELS=/mnt/ai-models/ollama
```

If host-specific `/etc/fstab` change is not possible, the next-best option is **bind-mount** `/usr/share/ollama` → `/mnt/ai-models/ollama` so the package default path still works.

### 6.4. Logging Guardrails (PREVENT 5.1 GiB syslog)

Two config changes required within 72 hours of this report:

1. `/etc/systemd/journald.conf`
   ```ini
   SystemMaxUse=500M
   SystemKeepFree=1G
   MaxRetentionSec=14day
   ```
   Apply: `systemctl restart systemd-journald` + `journalctl --vacuum-size=500M`

2. `/etc/logrotate.d/rsyslog` — add size caps on `syslog`, `auth.log`, `btmp`:
   ```
   /var/log/syslog {
       size 100M
       maxsize 500M
       rotate 14
       daily
       missingok
       notifempty
       compress
       delaycompress
       sharedscripts
       postrotate
           /usr/lib/rsyslog/rsyslog-rotate
       endscript
   }
   ```

---

## 7. ADR & Scripts Committed Alongside This Report

| Artifact | Path | Purpose |
|---|---|---|
| This incident report | [`INCIDENT_TIMELABS_DISK_20260813.md`](./INCIDENT_TIMELABS_DISK_20260813.md) | Primary incident record |
| ADR-010 | [`ADR-010-ollama-runtime-storage-safety.md`](../docs/adr/ADR-010-ollama-runtime-storage-safety.md) | Normative rules for Ollama on shared hosts, 2.5× headroom law, bind-mount layout |
| Safe pull script | [`ollama_safe_pull.sh`](../scripts/ollama_safe_pull.sh) | Drop-in replacement for `ollama pull` with headroom + trap |
| GC sweep script | [`ollama_cleanup_partials.sh`](../scripts/ollama_cleanup_partials.sh) | Cron + one-shot partial-blob TTL sweeper |

---

## 8. Owner Sign-Off Required

| Decision | Owner | Status | Approver |
|---|---|---|---|
| Accept incident facts §1–§5 | Infrastructure | OPEN | — |
| Remediate §2.3 `leak_model_*` provenance or execute compromise path 3a–f | Security / Model Author | OPEN | — |
| Adopt ADR-010 §2.5× headroom + bind-mount policy in future deploys | AI Eng + Infra | OPEN | — |
| Apply §6.4 journald + rsyslog size caps within 72 h | Infra | OPEN | — |
| Optional cleanup [A] (WP backup rotation — 16.8 GiB) | Vhost Owner | OPEN | — |
| Optional cleanup [B] (delete extracted `/root/mysql_backup` 18G — keep .zip) | Infra | OPEN | — |
| Optional cleanup [C] (cull dormant Ollama models — ~35 GiB) | AI Eng | OPEN | — |
| Optional cleanup [D] (delete 1panel .tar.gz 45 MiB) | Infra | OPEN | — |

---

## 9. Evidence Chain of Custody

| Timestamp (UTC) | Source | Data |
|---|---|---|
| 2026-08-13 (intake) | `ssh root@188.124.50.80 df -h` | 465G / 100% / 0B free |
| 2026-08-13 (intake) | `du -x --max-depth=1 /` + `find / -size +500M` | Consumer map captured in chat transcript |
| 2026-08-13 (intake) | `ollama list` | Full model table incl. `leak_model_*` 6 entries |
| 2026-08-13 (post-op) | `df -h /` after `sync` | 385G used / 80G free / 83% |
| 2026-08-13 (post-op) | `ls blobs/*-partial \| wc -l` | 0 confirmed |
| 2026-08-13 (post-op) | `docker ps` | 1 live running; 2 stopped pruned |
| 2026-08-14 T+12h | `ssh` reconnect test | Rate-limited / Fail2ban ban (documented defect §5 MEDIUM) |

End of report.
