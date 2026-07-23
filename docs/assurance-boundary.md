# Assurance boundary

## What Omnia can establish

Omnia can establish that:

- a named collector produced a bounded observation at a recorded time;
- the observation passed a declared minimization policy before persistence;
- a deterministic evaluator produced a declared result from a declared input;
- an append-only digest chain is internally consistent;
- a read model can be rebuilt from the retained event sequence;
- a proposed action was or was not bound to an explicit owner approval.

## What Omnia cannot establish by itself

Omnia cannot establish that:

- an observed system told the truth;
- an observation represents the entire target environment;
- a digest is an identity, signature, timestamp authority, or proof of truth;
- agreement among AI systems makes a claim correct;
- a technical control satisfies a law, regulation, contract, or council policy;
- a documented reversal is possible on every target;
- a third-party adapter is safe merely because it is read-only.

These distinctions are part of the public interface, not optional caveats.

## Authority model

The Owner is the root authority, but must not become a per-event bottleneck.
The Owner delegates a bounded operation class through a signed, versioned
policy. A future executor may act automatically only when the input contract,
deterministic check, target, operation, risk class, retry budget, and reversal
requirements all fall inside that policy.

Critical deviation, policy ambiguity, or a request outside the delegated scope
leaves the automatic path. Optional AI components may summarize, challenge, or
dissent; neither they nor a Tribunal can expand policy or authorize execution.

Mutation fails fast:

- `PASS` may proceed to the policy gate;
- `FAIL` and `ERROR` abort the execution path and emit a receipt;
- `UNKNOWN` enters quarantine for bounded recollection or manual adjudication;
- failed verification may retry only within an explicit budget;
- exhausted retries enter emergency stop.

Recovery is independently Owner-authenticated and does not depend on an AI
gate. Omnia v0 records these states but contains no mutating executor.

## Dependency boundary

The runtime source of record and its projectors use platform facilities and the
language standard library. Large external applications are not embedded in the
trust base. A provider or desktop tool may emit input through a narrow adapter,
but the adapter output is treated as an untrusted observation until Omnia
normalizes and records it.
