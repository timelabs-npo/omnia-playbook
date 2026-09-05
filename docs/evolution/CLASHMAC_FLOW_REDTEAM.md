# ClashMac-inspired Flow Observation semantic red-team plan

Status: clean-room semantic contract; no ClashMac code import and no mutation authority.

Reference source: `666OS/ClashMac@6bd4eee77ac3face93d6ba38fdc505e15a4e376e`.

## Scope

ClashMac is used only as a behavioral/product reference for native flow visibility, topology UX, traffic analytics, rule intent UX, TUN/system proxy controls, and privileged-helper deployment patterns.

Because ClashMac is proprietary/closed-source, this playbook forbids implementation reuse. The target is an independent normal form plus adversarial checks that can be implemented by darwin, win32, linux, openbsd, and netbsd adapters.

## Semantic pipeline

`native observation -> adapter -> FlowObservationV1 -> invariant checks -> Blueshoes Flow Graph -> UI projection`

Future mutations follow a separate pipeline:

`operator intent -> typed Flow Surgery proposal -> semantic validation -> host policy -> native adapter -> execution receipt`

Observation never implies mutation authority.

## Initial red-team families

### NF-A — authority escalation
Attack examples:
- UI says "disconnect" and expects immediate socket kill;
- helper process is privileged;
- model consensus recommends a route;
- proxy engine reports a successful rule change.

Oracle: `FlowObservationV1.authority` remains `observation_only`; no observation object can authorize effect.

### NF-B — flow identity rebinding
Attack examples:
- PID reused between observation and action;
- tuple reused after connection close;
- process identity missing or stale;
- route/interface changes under the same display row;
- NAT/proxy translation causes endpoint ambiguity.

Oracle: uncertainty remains explicit; a later mutation proposal must bind a fresh target identity and cannot rely solely on a stale table row.

### NF-C — cross-platform equivalence
Feed equivalent darwin/win32/linux/openbsd fixtures through their adapters.

Oracle: semantic fields retain equivalent meaning; only adapter-specific provenance and unavailable observations may differ. Missing data becomes `partial`/`unknown`, never fabricated.

### NF-D — stale telemetry
Attack examples:
- delayed counter sample;
- UI reconnect after daemon restart;
- cached route state;
- closed flow still visible.

Oracle: `freshness` is explicit and stale observations cannot be silently promoted to fresh.

### NF-E — display truth contamination
Attack examples:
- geographic origin intentionally masked;
- synthetic topology edge for visual layout;
- inferred hostname shown as observed DNS truth;
- route animation interpolated between actual nodes.

Oracle: display-only derivations are labeled (`real`, `derived`, `masked`, `unknown`) and never overwrite source evidence.

### NF-F — rule intent escape
Attack examples:
- one-click rule UI emits raw shell/config mutation;
- arbitrary engine command embedded in a policy proposal;
- helper accepts opaque command strings.

Oracle: executable content is rejected from semantic proposal objects. Rule intent must normalize to typed capabilities before host policy.

### NF-G — privileged helper sovereignty
Attack examples:
- helper auto-installs/updates engine;
- helper changes proxy/TUN mode on startup;
- helper retries a failed mutation after policy denial.

Oracle: helper is an adapter only. It cannot manufacture policy grants or durable success receipts.

## Evidence statuses

Each platform check reports exactly one of:

- `PASS`
- `FAIL`
- `SKIP`
- `NOT_EXECUTED`

A missing platform runner is never PASS.

## First implementation sequence

1. fixture-only `FlowObservationV1` validation;
2. adapter contracts for darwin/win32/linux/openbsd;
3. semantic equivalence fixtures;
4. Blueshoes read-only Flow Graph projection;
5. independent stale/identity/display-truth negative controls;
6. only then introduce one typed mutation, preferably `TerminateFlow`, behind host policy and receipts.
