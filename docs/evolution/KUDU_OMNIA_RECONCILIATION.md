# Kudu → Omnia semantic reconciliation

Status: proposed cross-platform red-team contract. No runtime gate is promoted by this document.

Upstream source: `AdventDevInc/kudu@92dbc52336ad9c9eb2968a180d22c72670de3b45`.

## Why reconcile here

Kudu supplies platform-specific maintenance rules and product behaviors. Omnia supplies the state/receipt architecture. `omnia-playbook` is the reconciliation layer between those domains: it converts source-specific maintenance dialects into one typed semantic proposal and subjects that proposal to independent adversarial validation.

The playbook is not an execution engine.

## Normalization pipeline

`upstream rule -> source adapter -> MaintenanceCapabilityProposalV1 -> invariant checks -> platform adapter contract -> Omnia proposal intake -> host policy/state transition -> execution receipt`

No stage before host policy/state transition may claim that a destructive operation is authorized or complete.

## Initial Kudu mapping

| Kudu concept | Normalized meaning | Initial disposition |
|---|---|---|
| cleaner path/rule match | cleanup candidate observation | adopt as proposal-only |
| `needsAdmin` | elevation requirement metadata | adopt; never authority |
| `minAgeDays` | age precondition | adopt |
| `deepRecencyCheck` | freshness/revalidation precondition | adopt |
| browser/app cache definitions | target discovery dialect | adopt behind translator |
| disk analysis | read-only analysis | adopt |
| startup/service inventory | read-only observation | adopt |
| `cacheReset` | optional maintenance hint | defer execution; proposal metadata only |
| cleanup action / command-like behavior | platform execution primitive | reject from normal form; requires explicit adapter contract |
| Kudu Cloud remote commands | remote control plane | exclude from this integration |
| secure delete / malware deletion / registry mutation / debloat / updater execution | destructive product actions | defer until separate invariants and recovery evidence exist |

## Cross-platform semantic equivalence

A semantic operation is identified by intent and evidence obligations, not by an OS command.

For example, `discover_cleanup_candidate` has the same semantic contract on macOS, Windows and Linux:

1. resolve the candidate inside an allowed scope;
2. identify what object is actually being referred to;
3. obtain a fresh observation;
4. evaluate age/recency conditions when present;
5. preserve uncertainty and user-data risk;
6. emit a proposal with `authority = proposal_only`.

The platform adapter may use File Provider metadata, Win32/CFAPI/NTFS primitives, POSIX paths, service managers or other native facilities, but those details do not alter the semantic intent.

## Required independent red-team families

### RT-A — semantic authority
- imported source claims `safe=true`;
- `needsAdmin=true`;
- model unanimous agreement;
- UI marks item reclaimable;
- transport returns success.

Oracle: none may change `proposal_only` into execution authority.

### RT-B — identity and scope
- symlink replacement;
- Windows reparse/junction substitution;
- sibling-prefix path confusion;
- case/normalization differences;
- environment-variable expansion changes;
- path exists at scan time but resolves differently at action time.

Oracle: proposal must not silently rebind to a different target.

### RT-C — platform equivalence
Feed semantically equivalent darwin/win32/linux fixtures through their translators.

Oracle: normalized intent/effect/risk/evidence obligations remain equivalent; only adapter-specific fields differ.

### RT-D — stale provenance
- upstream Kudu commit changes;
- rule content changes under same display name;
- source rule disappears;
- schema version changes.

Oracle: provenance drift is visible and requires revalidation.

### RT-E — recovery truth
A cleanup candidate has no demonstrated restore/recreate path.

Oracle: lack of recovery evidence remains explicit and may block later destructive authorization.

### RT-F — arbitrary action escape
Source rule contains shell syntax, cleanup command identifiers or other executable content.

Oracle: normalization rejects or quarantines it; executable content is never passed through the proposal schema as authority.

## Evidence status model

Every cross-platform check result must be one of `PASS`, `FAIL`, `SKIP`, or `NOT_EXECUTED`, and must bind:

- contract/schema version;
- source revision;
- target platform/adapter version;
- fixture identity;
- actual observed result.

A missing platform runner or unavailable privilege/tooling is not PASS.

## Current next step

Implement three translators (`darwin`, `win32`, `linux`) that consume source dialects and emit only `MaintenanceCapabilityProposalV1`. Validate them against independent fixtures before wiring any proposal into destructive Omnia operations.
