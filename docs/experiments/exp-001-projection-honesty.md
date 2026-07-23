# EXP-001: Projection Honesty Contract

## Hypothesis

Every view lies by omission. The dangerous part is not loss; it is loss that
has no declared boundary.

A view should therefore ship with a machine-readable contract stating:

- what source relations it preserves;
- what it intentionally drops;
- which aggregations destroy detail;
- which questions it can answer;
- which questions it must refuse;
- which anomaly probes should be visible, partial, or invisible;
- its exact replay invariant.

The initial schema is
[`schemas/projection-honesty.schema.json`](../../schemas/projection-honesty.schema.json).

## Why this is non-typical

Most dashboards advertise features. This contract advertises blindness.

Averages, search indexes, Tribunal summaries, risk scores, and 3D rigs become
comparable by the information they destroy, not by visual polish. A council or
operator can inspect a view's refusal surface before trusting it.

## Smallest falsifiable artifact

Take one fixed `log.0` containing:

1. a short high-amplitude transient;
2. a slow baseline drift;
3. a field change excluded by the projector;
4. reordered wall-clock timestamps with stable DTS sequence.

Project it through:

- a five-minute mean dashboard;
- an event table;
- the Deterministic Lens;
- a Tribunal summary.

For every view, compare observed detectability with the declared probes.

## Kill criterion

Kill or redesign the contract if independent implementers cannot predict a
view's blind spots better with it than without it, or if teams routinely fill
it with generic disclaimers that do not correspond to executable probes.

## Isolation

The contract is descriptive and testable. It grants no execution permission,
does not alter `log.0`, and cannot turn `UNKNOWN` into `PASS`.

## Promotion evidence

- two independently implemented views;
- at least ten anomaly probes;
- declared invisibility matching observed invisibility;
- a failing CI check for a false `lossless` claim;
- a semantic replay digest for each view.
