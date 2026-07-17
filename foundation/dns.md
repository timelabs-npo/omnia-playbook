# DNS Invariant (Vendor-Neutral)

## Invariant

Developer machines must use explicitly configured, observable DNS resolvers rather than silently inheriting an unknown resolver configuration.

## Decision

The invariant definition is platform-independent. Platform commands are implemented as adapters/checks and remain read-only.
