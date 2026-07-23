# The Deterministic Lens

## Position

Dashboards compress a system into averages, bins, and delayed summaries. That
compression is useful, but it can erase short transients, hide ordering, and
make an anomaly look ordinary.

The Deterministic Lens is a different projection: a versioned stream of
minimized events drives a three-dimensional rig through a deterministic state
machine. The rig is not a pet and not an oracle. It is an instrument whose pose
can be replayed from the same source record.

## Hardcore pitch

**Dashboards flatten the event stream. The Deterministic Lens gives it a
replayable body.**

We map bounded telemetry vectors into the discrete state and joint targets of a
3D rig. There is no model in the decision path and no pre-baked alert
animation. Every authoritative pose is derived from:

```text
log.0 + event schema + projector version + calibration digest
```

Stable input produces a stable equilibrium pose. A declared change detector
can move the rig through `NOMINAL → WATCH → STORM`. In `STORM`, the pose snaps
to a rigid, unmistakable configuration. The event range, thresholds, state
transition, and joint targets remain inspectable.

The claim is deliberately falsifiable:

```text
same canonical inputs ⇒ same discrete rig state
```

If replay produces a different state, the projector failed.

This is not a claim that a dragon knows the truth. It is a loss-aware,
replayable projection that makes selected anomalies spatially difficult to
ignore.

## Mathematical contract

For each event tick `t`, the typed feature vector is:

```text
x_t = [s_t, v_t, n_t, …]
```

where every component has an explicit unit, window, normalization, missing-data
rule, and saturation range. “Strength,” “variability,” “novelty,” and
“entropy” are not accepted as free-form labels.

The state machine and pose projector are:

```text
q_t     = FSM(q_(t-1), x_t; thresholds, hysteresis, persistence)
theta_t = Q(A[q_t] · x_t + b[q_t])
```

- `q_t` is a finite state such as `NOMINAL`, `WATCH`, or `STORM`;
- `A` and `b` come from a versioned calibration profile;
- `Q` is an explicit fixed-point quantizer;
- `theta_t` is the authoritative joint-target vector.

For an exact replay:

```text
D_replay = max_t ||theta_t(live) - theta_t(replay)||_∞
target: D_replay = 0
```

The target is realistic only when event ordering, arithmetic, calibration,
projector code, and platform test vectors are fixed. Floating-point IK,
wall-clock reads, unordered iteration, hidden smoothing, model calls, and
network lookups are excluded from the authoritative projector.

## What `STORM` means

`STORM` is not a universal fact about a network. It is a declared transition
under one calibration profile.

A valid profile records:

- feature definitions and units;
- baseline and window boundaries;
- thresholds;
- hysteresis;
- minimum persistence;
- missing and late event behavior;
- saturation behavior;
- exact pose targets;
- calibration digest.

The “wings lock at +22°” pose may be a useful visual invariant, but `22°` is a
profile value, not a law of nature.

## Provenance path

```text
bounded source
    ↓
normalize → minimize / redact → append to log.0
    ↓
deterministic feature projector
    ↓
finite state transition
    ↓
fixed-point joint targets
    ↓
visual rig + replay receipt
```

Every rendered audit state identifies the contributing event range, last event
digest, projector version, calibration digest, state, and target-pose digest.

## Non-claims

The Deterministic Lens does not claim that:

- the source cannot be spoofed;
- the visual mapping preserves all source information;
- a digest proves truth or identity;
- a detected change is malicious;
- a 3D pose replaces logs, traces, or raw evidence;
- the system is “un-falsifiable”;
- a state transition is legal or scientific proof.

Those non-claims make the instrument harder to dismiss, not less ambitious.

## Relation to the “invisible 97%” concept

The creative film is the visual thesis: familiar surfaces become populated by
otherwise invisible actors and fields. The engineering form of that thesis is
stricter. We expose a declared, measurable subset of an invisible system and
preserve the exact transformation that made it visible.

The product line is:

> **Create the invisible. Then make every transformation reviewable.**
