# Fail-fast policy machine

## Purpose

Manual approval of every event preserves nominal control but destroys
throughput and encourages rubber-stamping. Omnia instead separates authority
from attention:

- the Owner sets and signs a narrow policy;
- deterministic machinery handles the normal case;
- only critical or ambiguous deviations consume human attention.

This is delegated automation, not autonomous authority.

## State machine

```text
Schema / Contract
  ├─ invalid ───────────────→ REJECT → receipt
  └─ valid
       ↓
Bounded collection
       ↓
Deterministic checks
  ├─ FAIL / ERROR ──────────→ ABORT + NOTIFY → receipt
  ├─ UNKNOWN ───────────────→ QUARANTINE
  │                            └→ bounded recollection or manual adjudication
  └─ PASS
       ↓
Policy gate
  ├─ outside / critical ────→ OWNER
  └─ within signed scope
       ↓
Automatic execution
       ↓
Verify
  ├─ stable ────────────────→ CLOSE → receipt
  └─ unstable
       ↓
Retry budget N
  ├─ available ─────────────→ Bounded collection
  └─ exhausted ─────────────→ EMERGENCY STOP → receipt
```

No terminal path erases evidence. “Abort” and “reject” stop effects, then append
a minimized receipt to `log.0`.

## Contract ingress

Collection begins only after a versioned input contract accepts the request.
The contract identifies:

- schema and operation version;
- target and scope;
- source class and required provenance;
- allowed data categories and redaction policy;
- resource and time budgets;
- declared risk class.

Malformed or unknown versions fail before discovery or network activity.

## Signed policy

A policy is data, not free-form prose. At minimum it binds:

- policy ID, version, issuer, signature, and validity interval;
- permitted contract versions;
- permitted target selectors and operation registry IDs;
- maximum risk and resource budgets;
- required check IDs and accepted result (`PASS` only);
- required before-state and reversal support;
- retry ceiling and emergency-stop behavior;
- notification and receipt destinations.

AI output, Tribunal agreement, inferred user preference, and previous
successful execution cannot widen this envelope.

## `UNKNOWN`

`UNKNOWN` is not a weaker `PASS` and is not a self-training signal. Quarantine
may request a bounded additional observation or await manual adjudication. The
new evidence starts a new evaluation tick; it does not mutate the earlier
result.

## Retry

Retry is a policy counter, not a loop in the UI. The receipt records attempt
number, maximum attempts, prior result, backoff rule, and the exact evidence
range. A timeout, repeated non-progress, policy expiry, or budget exhaustion
enters emergency stop.

## v0 boundary

The repository currently implements record framing, verification, and local
view reconstruction. It does not yet implement policy signatures, an operation
registry, an executor, notifications, quarantine workers, or emergency-stop
integration. The state machine is the contract those components must satisfy
before mutation is introduced.
