# EXP-003: Tiny Tribunal Capsule

## Hypothesis

A very small adversarial capsule can improve a review by producing one useful
counterexample or missing assumption without pretending to vote on truth.

## Capsule boundary

Input:

- one minimized claim;
- its evidence references;
- the applicable Projection Honesty Contract;
- a strict token, time, and model-call budget.

Output:

- strongest counterexample;
- missing evidence;
- ambiguous term;
- proposed falsification test;
- `NO_USEFUL_DISSENT` when it finds nothing.

The capsule emits no confidence score, consensus score, approval, plan
authorization, or execution request.

## Non-typical rule

Success is not “the models agree.” Success is one of:

- the capsule finds a counterexample that changes a deterministic test;
- it exposes a view's undeclared blind spot;
- it admits `NO_USEFUL_DISSENT`.

## Kill criterion

Kill the capsule if its output does not change a test, schema, evidence request,
or refusal boundary often enough to justify its cost—or if reviewers begin
treating fluent dissent as evidence.

## Isolation

Private experimental feature. Provider adapters are replaceable. Raw prompts
and personal data are not appended to the public record. The capsule cannot
reach the executor or policy gate.

## Promotion evidence

- preregistered adversarial fixtures;
- comparison with a no-Tribunal baseline;
- false-positive and cost measurements;
- demonstrated `NO_USEFUL_DISSENT`;
- no path from capsule output to execution authority.
