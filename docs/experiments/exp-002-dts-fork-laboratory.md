# EXP-002: DTS Fork Laboratory

## Hypothesis

A central `last + 1` sequence is sufficient for deterministic replay but
insufficient for honest causal claims across intermittently connected devices.

## Experiment

Simulate three devices with:

- skewed and jumping wall clocks;
- independent producer counters;
- offline work and delayed delivery;
- duplicate delivery and lost acknowledgement;
- a device reset that reuses an old local counter;
- two concurrent events with no causal relation.

Compare:

1. server-arrival sequence;
2. producer Lamport merge;
3. parent-edge topological order with deterministic tie-breaking.

The output is not “which algorithm wins.” It is a set of minimal
counterexamples showing what each ordering can and cannot claim.

## Kill criterion

Stop if the added causal metadata cannot change a real consumer decision, or
if its operational complexity is larger than the class of offline workflows
Omnia actually needs.

## Isolation

Synthetic events only. No live device control, remote execution, network
capture, or production database.

## Promotion evidence

- frozen counterexample fixtures;
- a normative clock/identity/reset protocol;
- duplicate and fork detection;
- Windows, macOS, and OpenWrt test vectors;
- an explicit statement of unresolved multi-host failure modes.
