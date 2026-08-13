# Omnia Playbook v1 — Owner-Controlled Assurance and Constraint Plane

> **Authoritative architecture sentence**:<br>
> *Omnia constrains.<br>
> Deterministic decision logic evaluates.<br>
> Tribunal reasons and advises.<br>
> Blueshoes represents runtime/network reality and transactional state.<br>
> MBSD executes bounded actions.<br>
> Providers testify.*

No component may silently acquire another component's authority.

## Status: v1, in progress. Semantically complete; physically unproven.

- SPECIFIED: 15 schemas, 21 fixtures, 8 tests (37 safe unit + 8 architecture-boundary tests).
- IMPLEMENTED: schema/fixture validation, repository artifact validation, canonical runtime bundle exporter with reproducible digest.
- DEPLOYED: not physically deployed. All OpenBSD network adapters, Wi-Fi, MediaTek, Beryl = MOCK_TESTED maximum. REAL_HOST_TESTED / BERYL_TESTED = UNKNOWN. Do not claim otherwise.

## What Omnia v1 is

Omnia is an **owner-controlled assurance and constraint plane**. It defines and validates:

- owner intent (declared pre-failure);
- authority ceilings;
- invariants;
- policies;
- typed evidence;
- provenance;
- claims;
- uncertainty;
- contradictory evidence;
- dependency roots and their degraded/offline semantics;
- deterministic decision-kernel inputs and outputs;
- bounded action authorization;
- receipts;
- post-state validation;
- rollback requirements;
- adapter/provider capability declarations.

Omnia **does not** (v1): route, run, replace DNS, replace SCION, replace GNS, process packets in-band, autonomously run LLMs, orchestrate, be Blueshoes, be MBSD, be a kernel.

## What Omnia v1 is NOT (do not remove; these are binding)

- ❌ A router
- ❌ A DNS replacement
- ❌ A SCION implementation
- ❌ A GNS implementation
- ❌ A packet-processing engine
- ❌ An autonomous LLM / autonomous orchestration daemon
- ❌ Blueshoes (representation/runtime) — Blueshoes is the next cell
- ❌ MBSD (physical execution / OpenBSD embodiment) — MBSD is a separate project
- ❌ A "world engine"
- ❌ The production decision kernel (Rheknel is CANDIDATE_UNVALIDATED against current Tribunal corpus)

Remove or correct any documentation that implies otherwise.

## Semantic distinctions (non-negotiable)

```text
Naming ≠ Identity ≠ Service Identity ≠ Location
      ≠ Locator Discovery ≠ Reachability
      ≠ Path Discovery ≠ Path Selection ≠ Multipath
      ≠ Authorization ≠ Execution Authority

Observation ≠ Claim ≠ Evidence ≠ Truth
Trust ≠ Authorization ≠ Mutation Authority
Consensus ≠ Truth
Memory ≠ Truth
Specified ≠ Implemented ≠ Deployed ≠ Locally Observed
```

No adapter/provider becomes an ontology because it currently works. DNS, GNS, SCION, IP, BGP, libp2p, QUIC, MASQUE, RPKI, probes and local caches are **replaceable capability/evidence providers**.

## Repository structure

```
adapters/                Dumb observation providers. Never decide truth/policy.
  apple/ azure/ google-cloud/ macos/ openbsd/ openwrt/ windows/
checks/                  Read-only YAML observation checks; no mutation.
  dns/ openbsd/
environments/            Estate declaration files.
  bluenikee/ example/ openbsd-sealed-brick/
foundation/              Platform-independent invariant docs only.
  identity.md networking.md dns.md secrets.md storage.md observability.md cicd.md
playbooks/               Operational remediation / diagnostics / recovery / sealed-brick guides.
references/              Source-material notes.
reports/                 Durable gate reports + receipts (allow-listed only).
  SEMANTIC_NEIGHBOURS_MATRIX.md      — 23-family prior-art sweep (blocking gate)
  REUSE_DECISION_REGISTER.md         — reuse / wrap / prior-art / unresolved matrix
  trae-openbsd-sealed-brick.md
schemas/                 15 normative schemas.
  fixtures/valid/        21 passing fixtures
  fixtures/invalid/      21 intentionally failing fixtures
  adapter.schema.json
  causal_experiment.schema.json
  check.schema.json
  disagreement_resolution.schema.json
  environment.schema.json
  evidence_privacy_tier.schema.json        ← new (PUBLIC/PRIVATE/LOCAL_RAW/DERIVED_BOOL)
  invariant.schema.json
  network_model.schema.json
  openbsd_support_tier.schema.json         ← new (honest tiering, no promotion)
  owner_operational_intent.schema.json
  provider_capability.schema.json          ← new (evidence-only boundary, 15 families)
  runtime_bundle.schema.json
  tribunal_advisory_ceiling.schema.json    ← new (advisory only, no FAIL→PASS)
  tribunal_participant_claim.schema.json
  deterministic_decision_kernel.schema.json ← new (PASS/FAIL/UNKNOWN/ERROR/ESCALATE, fail-closed)
scripts/                 validate.sh / diagnose.sh / report.sh / export_runtime_bundle.py / blueshoes_live_test_runner.sh
tests/                   Unit + architecture-boundary tests.
  test_architecture_boundaries.py  ← new (fail-closed, tier honesty, provider/Tribunal ceilings)
  test_multi_interpreter_conformance.py
  test_openbsd_contract.py
  test_repository_artifacts.py
  test_schemas.py
  test_validation_contract.py
  test_zero_history.py
docs/adr/                Architecture decision records (minimal, durable).
.github/workflows/       CI (validate + test, pinned).
```

## Provider model (first-class boundary)

A provider may **report**: identities, names, locators, paths, reachability, routing state, trust assertions, observations, capabilities, failure state.

A provider **must NOT implicitly**: decide Omnia policy, grant itself authority, claim semantic truth, mutate external state. Provider output = typed evidence only.

Conceptual contracts frozen at v1 compatible with: DNS, GNS, SCION, BGP/OpenBGPD, RPKI, LOCAL_OBSERVATION, ACTIVE_PROBE, LIBP2P_LIKE_DISCOVERY, QUIC_PATH_OBSERVATION, MBSD_OPENBSD_OBSERVATION, WIREGUARD_OBSERVATION, MDNS_DNS_SD, ICE_STUN_TURN, MASQUE_TUNNEL, FUTURE_PROVIDER.

Do not implement every provider. Define the boundary that allows implementations to be plugged in later.

## Deterministic decision-kernel boundary

```
typed evidence  +  owner intent  +  policy/invariants  +  authority ceiling
                ↓
        DETERMINISTIC DECISION KERNEL  ← contract, not a single engine yet
                ↓
        PASS / FAIL / UNKNOWN / ERROR / ESCALATE
```

Fail-closed requirements (machine checked in `test_architecture_boundaries.py`):

- unknown policy MUST NOT silently become PASS.
- malformed evidence MUST NOT silently become PASS.
- missing evaluator MUST NOT silently become PASS.
- natural-language payload cannot grant execution authority.
- LLM output cannot override deterministic denial.
- decision I/O must be serializable and deterministically replayable.
- decision receipts must identify policy+evidence+engine+owner-intent versions.

**Rheknel is NOT hard-coded.** It remains `CANDIDATE_UNVALIDATED AGAINST CURRENT TRIBUNAL CORPUS`. The contract independently tests: (1) current deterministic host oracle; (2) future Rheknel; (3) other deterministic engines. Host oracle succeeded in TRIBUNAL-RT-V0; SmolLM2-135M advisory with critical false PASS + prompt injection failures → LLM output = advisory evidence only.

## Tribunal advisory ceiling

Tribunal = `ADVISORY / UNCERTAINTY / HYPOTHESIS / DISAGREEMENT ANALYSIS`.

**Tribunal may**: explain evidence; identify contradictions; request further observations; rank hypotheses; propose a bounded next experiment; recommend escalation; compare interpretations.

**Tribunal may NOT**: grant authority; bypass an invariant; reinterpret untrusted evidence as an instruction; mutate networking directly; merge code; change policy; transform FAIL into PASS.

Machine enforced: `tribunal_advisory_ceiling.schema.json`; `tribunal_participant_claim.schema.json` conformance flags; all tribunal_may_not const=False.

## Evidence / privacy model

Separate: `PUBLIC_EVIDENCE` / `PRIVATE_EVIDENCE` / `LOCAL_ONLY_RAW_OBSERVATION` / `DERIVED_BOOLEAN_POSTURE`.

Leakage audit required for 12 channels: values, nested structures, alternative keys, serialized blobs, hostnames, resolver data, addresses, interface names, topology, routing state, timing, identifiers.

Public output exposes the minimum evidence required for the claim. Provenance is still recorded in private.

**Privacy is NOT comprehensively proven unless actually tested.** Do not claim otherwise.

Tier non-promotion: LOCAL_RAW → PUBLIC requires explicit owner approval.

## OpenBSD platform policy (no tier promotion)

Tier order: UNKNOWN → OPENBSD_BASE_AVAILABLE → OPENBSD_PORT_AVAILABLE → MOCK_TESTED → VM_TESTED → REAL_HOST_TESTED → BERYL_TESTED.

- MOCK must not claim REAL_HOST or BERYL.
- VM must not claim BERYL.
- REAL_HOST must not claim BERYL without BERYL observation.
- Wi-Fi and MediaTek success must be locally observed before claiming.
- No kernel modification claim unless src has actually been patched.
- No production mutation claim without observed boundary.

Current honest status: bgpd(8)/wg(4)/iked(8)/rpki-client(8) OPENBSD_BASE_AVAILABLE + MOCK_TESTED via fixtures. All network adapters, Wi-Fi, MediaTek, BERYL_TESTED physical = UNKNOWN. Do not promote.

## Dependency degraded/offline semantics

Every dependency root (DNS, cloud, external model, identity authority, rendezvous, remote control plane, any external provider) must have explicitly declared degraded/offline semantics. Offline behavior must never be silently PASS. Machine checkable.

## Cross-cell boundaries (strict)

```text
Omnia ≠ Blueshoes ≠ MBSD ≠ HME ≠ Rheknel
```

Integration is through typed contracts and evidence only. No Blueshoes runtime code in Omnia. No MBSD platform code in Omnia. No HME representation logic in Omnia. No Rheknel embedded as production kernel in Omnia before independent validation.

## How to validate

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements-dev.txt

make validate      # structure, links, YAML/JSON syntax, schemas+fixtures, artifacts,
                   # shell lint, canonical runtime bundle + digest reproducibility
make test          # safe unit tests + architecture boundary tests
make diagnose      # read-only host-supported checks
make report        # writes timestamped reports/ (Git-ignored except allow-listed gates)
```

## CI (reproducible)

`.github/workflows/validate.yml` runs on `pull_request` + push to `main`: `make validate` then `make test`. Ubuntu-latest; Python 3.11; pinned actions/checkout@v4 + setup-python@v5; no `latest` floats for packages.

## Prior-art gate (blocking) — already closed

See:
- [SEMANTIC_NEIGHBOURS_MATRIX.md](reports/SEMANTIC_NEIGHBOURS_MATRIX.md) — 23-family sweep
- [REUSE_DECISION_REGISTER.md](reports/REUSE_DECISION_REGISTER.md) — reuse / wrap / prior-art-only / unresolved matrix

Gate verdict: **ACCEPTED**. Networking primitives post-gate proceed only in order: (1) REUSE_DIRECTLY; (2) WRAP_AS_PROVIDER; (3) PRIOR_ART; (4) UNRESOLVED_UNDER_CURRENT_BOUNDED_INVENTORY normative designs only.

## Known unknowns (do not falsely resolve)

- Physical OpenBSD target testing: not observed.
- Beryl router / MediaTek Wi-Fi: not observed.
- Production mutation boundaries: unproven.
- Rheknel as production decision kernel: CANDIDATE_UNVALIDATED.
- Any unresolved semantic-neighbour contradictions between Trae / Codex / Copilot lanes: recorded in `docs/adr/reconciliation.md`.

## Next frontier: Blueshoes → Representation

After Omnia v1 is published, the next unsolved representational problem is cleanly transferred to **Blueshoes Representation v0**. Central question:

> How do heterogeneous observations of actual network reality become a canonical, replayable, typed representation without prematurely deciding truth, policy, or action?

See `docs/adr/blueshoes-handoff.md`.

## License

Timelabs NPO. See [LICENSE](LICENSE). See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md).
