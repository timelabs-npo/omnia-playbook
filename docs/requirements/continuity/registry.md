# Monitor and action registry

Requirements draft v0.1, 12 September 2026. This is a registry of requested behavior and candidate data sources, not a list of implemented features. Suggested polling intervals are starting points for measurement. Each adapter must report its actual support and verification status.

Action tiers describe the required control boundary; an entry does not authorize execution:

- **A0:** observe and explain.
- **A1:** take a bounded action on a service owned by the product.
- **A2:** clean an explicitly allowed resource.
- **A3:** change shared network or operating-system configuration under a separate maintenance policy.

`client`, `helper`, and `peer` are generic deployment roles. Endpoint, host, account, and credential references below are opaque identifiers, not values to publish in this repository. See the [technical specification](technical-spec.md) for scope and the [state and data contracts](uml-contracts.md) for operation semantics.

## Resources and service health

| ID / priority | Required observation | Candidate source / method | Interval and limits | Possible action |
|---|---|---|---|---|
| H01 P0 | Host role, OS/build, architecture, RAM, component versions | Native inventory; Windows CIM; WSL version and inventory | On connection, then on change; collector-specific access | A0: explain or reject an incompatible operation |
| H02 P0 | CPU usage, load, owning process, overload duration | Existing product metrics if verified; platform CPU collector | Every 2–5 seconds; process and whole-host CPU percentages use different denominators | A1: reduce the frequency of the product's expensive checks |
| H03 P0 | Memory pressure, swap and their trends; service resident memory | Native macOS metrics; Windows counters; Linux process and pressure information where available | Every 5 seconds; do not add WSL memory to Windows memory as independent usage | A1: defer a scan; no automatic memory purge |
| H04 P0 | Free and available space per volume; log and queue sizes | Filesystem statistics; scoped directory accounting; deep analysis on request | Every 30 seconds; deep scans need a separate I/O budget | A2: rotate the product's closed logs or allowed caches |
| H05 P0 | Disk read/write rate, errors, and the product service's write latency | OS counters and timestamps around the service's writes | Every 5 seconds; SMART is optional; missing data does not mean healthy | A1: stop background scans and report a write-risk event |
| H06 P0 | Thermal state, power source, sleep/wake, low-power mode | Native thermal and power notifications; platform power events | On events; temperature in degrees and fan readings are optional | A1: reduce optional work |
| H07 P1 | GPU state, temperature, fan RPM, battery health | Hardware collectors after checking their capabilities | Every 5–30 seconds; show unsupported fields explicitly | A0; manual fan control is outside P0 |
| H08 P0 | Collector health, errors, polling duration, queue size | Collector heartbeat and health counters | Every cycle, with its own deadline | A1: restart only the collector, not the transport |

Platform sources are candidates until the helper's actual schema and access have been checked. Reference semantics: [Apple thermal state](https://developer.apple.com/documentation/foundation/processinfo/thermalstate-swift.property), [Linux pressure information](https://docs.kernel.org/accounting/psi.html).

## Network and useful delivery

| ID / priority | Required observation | Candidate source / method | Interval and limits | Possible action |
|---|---|---|---|---|
| N01 P0 | Physical and virtual interfaces, IPv4/IPv6 addresses, MTU, route to the selected receiver | Native network APIs or CLI; Windows adapter inventory; WSL structured interface and route output | On change and every 10 seconds; include tunnel and bridge interfaces | A0: explain the selected route |
| N02 P0 | Bytes, packets, errors, and discards for each interface | Platform interface counters; Windows adapter statistics; WSL structured link counters | Every 2–5 seconds; handle resets and avoid counting the same traffic twice across boundaries | A0: locate degradation |
| N03 P0 | DNS, proxy, and tunnel configuration separately from request success | Platform configuration plus a probe scoped to a configured target | Every 30 seconds and on events; active probes only to configured targets | A3: change configuration only under the separate policy |
| N04 P0 | Client-to-helper sends, receives, matched responses, timeouts | Unique request ID, sequence number, and receiver response; capture on request | Lab default: every 5 seconds, 2-second deadline; UDP port is configuration data | A0: repeat diagnostics; no response alone does not prove firewall blocking |
| N05 P0 | Effective Windows and Hyper-V firewall policy; last point where a packet was observed | Windows helper and PowerShell; bounded platform packet captures | Rules on request or change; captures have time/size limits and required access | A3: a specific policy change only; never disable filtering automatically |
| N06 P0 | SCION presence/version, components, daemon availability, paths, stock end-to-end test results | Version-pinned SCION tools, configuration, logs, and native metrics where available | Health every 5 seconds; full tests on request | A1: manage an owned service under policy; preserve the stock data plane |
| N07 P0 | GNS3 endpoint, API version, project ID, nodes, links, runtime state | API of the installed GNS3 version | Every 10 seconds; endpoint from the registry; errors must not appear as zero projects | A1: act on one identified lab node after checking preconditions |
| N08 P0 | Flow-control availability, desired state, observed state, command result | Adapter for the existing TCP commands, with typed responses | Every 5 seconds and after a command; timeout and action ID required | A1: open or close according to the active-flow policy |
| N09 P0 | Useful delivery for the selected scenario | Receiver receipt, commit, or stream counters correlated with a flow ID | On events; freshness and success semantics depend on the data type | A1: resume/retry only when supported and verified |
| N10 P0 | Delivery queue bytes/count, oldest age, retry rate, acknowledgement/commit lag | Product-service instrumentation, if a queue exists | Every 2–5 seconds; missing instrumentation means unknown | A1: limit new jobs/retries and preserve already accepted work |
| N11 P0 | Incidents and state changes across boundaries | Correlated events with host, boot, and configuration IDs; source and receive times | Event stream with local quota and retention | A0/A1: a concise explanation and bounded recovery |

References: [Windows adapter counters](https://learn.microsoft.com/en-us/powershell/module/netadapter/get-netadapterstatistics?view=windowsserver2025-ps), [WSL networking](https://learn.microsoft.com/en-us/windows/wsl/networking), [Hyper-V firewall](https://learn.microsoft.com/en-us/windows/security/operating-system-security/network-security/windows-firewall/hyper-v-firewall), [stock SCION local tests](https://docs.scion.org/en/v0.15.1/dev/run.html), [GNS3 architecture](https://docs.gns3.com/docs/using-gns3/design/architecture). Keep existing lab results with their original scope and provenance. Adding this registry neither passes new gates nor invalidates previously reported results.

## NDI: research reference, outside beta scope

An NDI integration is not required. M01–M07 preserve reference capabilities for comparison; they are not implementation tasks. GUI, SDK, and service APIs have separate capability and platform limits.

| ID / priority | Reference observation or control | Documented candidate | Limit |
|---|---|---|---|
| M01 REF-NDI | Sources, receivers, and their relationships | Discovery GUI, SDK discovery, Discovery Service API | Visibility depends on groups, configuration, and endpoint participation |
| M02 REF-NDI | Format, FPS/timecodes, arrival intervals, data volume | Windows Analysis CLI; local SDK receiver; Advanced events | Arrival jitter is not end-to-end latency |
| M03 REF-NDI | Received/dropped frames and queue depth | `NDIlib_recv_get_performance`, `NDIlib_recv_get_queue` | Local receiver measurements; application drops are not UDP/IP loss |
| M04 REF-NDI | Useful output: video preview, audio presence/meters | macOS Video Monitor; Windows Studio Monitor; SDK consumer | A visible source does not prove correct output |
| M05 REF-NDI | Source/output selection and connection readback | Router; opted-in Discovery receivers; Advanced control | GUI, SDK, and REST need separate adapters; check versions and permissions |
| M06 REF-NDI | Bridge peer/session/stream state and configuration changes | Windows Bridge Service REST plus WebSocket/webhooks | Separate service product; not the ordinary Bridge GUI or a promised WSL build |
| M07 REF-NDI | Repeatable load and diagnostic chain | Test Patterns, Monitor, Analysis | Start a test generator on request and account for its load |

Consult the [official NDI documentation](https://docs.ndi.video/) for the installed edition, SDK, and tool versions. These reference capabilities do not provide a general operating-system reliability guarantee or a ready-made SCION integration.

## Maintenance and execution control

| ID / priority | Requested tool | Preconditions and required result |
|---|---|---|
| A01 P0 | Owned-service lifecycle | Name the component and establish dependencies/activity; set a deadline; allow at most one automatic attempt per incident; perform a functional check afterward |
| A02 P0 | Rotate owned logs | Use closed segments, quota, and retention; preserve active-incident evidence; measure actual free space afterward |
| A03 P1 | Clean allowed regenerable caches | Maintain owner and resource references; reject busy/unknown resources; dry-run and recheck before deletion; establish how regeneration works. A broad system-cleanup command is not this operation |
| A04 P0 | Diagnostic scheduler | Cancellable tasks; bounded concurrency, CPU, and I/O; reduce frequency under pressure; monitoring must not become another heavy workload |
| A05 P0 | Client-to-helper commands | Identification/authentication; bounded actions and targets; request ID, result, and readback; reconcile an uncertain outcome before any retry |
| A06 P0 | Export a report | Include version/configuration manifest, checks, observations, actions, and postchecks; exclude secrets and payload by default |

## Required contract before implementation

Every entry must define:

`id, host_id, component/version, capability, source, units, scope, permissions, interval, deadline, freshness_ttl, cost_budget, required_dependencies, action_policy, preconditions, action_id, reversibility, postcondition, evidence`.

Do not substitute zero for unknown. Label measured and inferred values separately. Define normal values, thresholds, freshness, and permissions per feature. One combined health score must not replace the state of a critical transfer.

## Synchronization and private archive

Requested mode: bidirectional synchronization of selected folders, preserving conflicting versions. Provider scope includes iCloud Drive, Google Drive, OneDrive, S3/MinIO, macOS/Windows folders, and NAS. Preserve this scope while verifying each adapter separately. NDI remains a reference only. Detailed invariants belong to the [technical specification](technical-spec.md) and [operation contracts](uml-contracts.md).

| ID / priority | Requested monitor / tool | Required data | Control and limit |
|---|---|---|---|
| S01 P0 | Endpoint inventory | Provider/account/container/root references, capabilities, access, API version | Connect/disconnect one endpoint and safely preserve pending work |
| S02 P0 | Mapping registry | Source and destination, filters, configuration revision, selected policy | Preview, validate, enable; separate pause/resume, conflict, deletion, and retention settings |
| S03 P0 | Change discovery | Cursor/checkpoint, full/partial scan status, last confirmed revision | Refresh/reconcile; incomplete scans must not create deletions |
| S04 P0 | Transfer queue | Pending objects/bytes, oldest age, stage, retry/backoff, confirmed progress | Durable enqueue, bounded retry, version-checked resume; cancel with regard to the actual outcome |
| S05 P0 | Conflict manager | Baseline, local, and remote versions; reason | Preserve both versions; resolve through a separate decision; use a deterministic conflict ID |
| S06 P0 | Integrity and commit | Checksum algorithm/scope, provider revision, verification result | Reverify; never assume every ETag is an MD5 digest |
| S07 P0 | Hydration and offline availability | Placeholder/available/dirty/pinned state; verified remote version | Hydrate/evict only through a supported mechanism; do not remove unverified copies |
| S08 P0 | Deletion and retention | Tombstones, trash/version availability, oldest offline peer | Propagate deletion only under an explicit policy; restore an available version |
| S09 P0 | Quotas and cost | Remaining local/cloud capacity, API throttling, storage/egress estimates and their freshness | Limit concurrency/bandwidth; pause new jobs at a limit |
| S10 P0 | Archive classifier | All user files; separate stash/untracked/artifact classes; exclusions, origin, resource reference, reason | Apply the agreed broad scope and exclusions; show missing access; exclude raw credentials and the archive's own output |
| S11 P0 | Private archive | Encrypted snapshot/manifest/object references, upload/verification status, retention | Create, upload, verify, restore; do not delete the source before accepting the archive policy and verifying its result |
| S12 P0 | Keys and recovery | Selected default profile, credential/key references, locked/unlocked state, restore-drill date | Unlock, rotate, and recover through the selected key scheme; never place keys in shared Git |

**Implementation of S01–S12 has not been established.** These are requirements, not confirmed capabilities of an existing command-line controller.

An existing product supervisor's metrics and scan endpoints are candidates to reuse for H02–H04, subject to checking its actual runtime, schema, scope, and cost. This document does not require replacing that service or adding a new monitoring process.
