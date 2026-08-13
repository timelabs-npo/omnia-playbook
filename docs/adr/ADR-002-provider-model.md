# ADR-002: Provider Model

## Status
ACCEPTED

## Date
2026-08-13

## Deciders
Timelabs Owner; TRAE materialization

## Context
Network observation comes from diverse sources with wildly different trust characteristics. A unified provider family enum constrains what evidence types may appear and under what authority.

## Decision
Provider families are a closed 15-member enum: DNS, GNS, SCION, BGP_OPENBGPD, RPKI, LOCAL_OBSERVATION, ACTIVE_PROBE, LIBP2P_LIKE_DISCOVERY, QUIC_PATH_OBSERVATION, MBSD_OPENBSD_OBSERVATION, WIREGUARD_OBSERVATION, MDNS_DNS_SD, ICE_STUN_TURN, MASQUE_TUNNEL, FUTURE_PROVIDER. Providers output typed evidence only. Five non-authority constraints: (1) providers never grant decision authority, (2) providers never mutate Omnia constraint state, (3) providers cannot escalate their own evidence tier, (4) provider outputs are signed with their identity key, (5) providers must declare degraded/offline semantics.

## Consequences
Positive: Evidence provenance is structurally traceable; new observation types require explicit enum extension. Negative: Adding a new provider family is a schema-breaking change requiring migration. Binds: schemas/provider.schema.json enum, all provider adapters under adapters/, degraded/offline semantics tests.

## Evidence
- schemas/provider.schema.json: family enum and evidence typing
- schemas/fixtures/valid/: provider fixture set
- tests/provider_family_test.ts: enum exhaustiveness tests
- README.md: Provider Trust Model section
