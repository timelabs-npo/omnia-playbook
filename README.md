<p align="center">
  <img src="docs/readme/hero.svg" alt="Omnia Playbook — Dance the checks before you touch reality" width="100%" />
</p>

<h1 align="center">OMNIA PLAYBOOK</h1>
<p align="center"><strong>THE KOURETES PROTOCOL FOR INFRASTRUCTURE.</strong></p>
<p align="center"><em>Dance the checks before you touch reality.</em></p>

<p align="center">
  <a href="https://blueshoes.space/rhea/">Rhea Pantheon</a> ·
  <a href="foundation/">Invariants</a> ·
  <a href="checks/">Checks</a> ·
  <a href="playbooks/">Playbooks</a>
</p>

---

Infrastructure fails twice: first in reality, then in the story we tell ourselves about reality.

**Omnia Playbook is the layer that refuses the second failure.** It is a vendor-neutral operational corpus that separates **invariants**, **platform adapters**, **read-only checks**, **remediation procedures**, and **evidence** so an operator—or a future qualified executor—can know what is true *before* changing anything.

```text
     invariant
        │
        ▼
   ┌─────────┐
   │ adapter │   Apple / Google / Azure / OpenWrt / macOS / Windows / …
   └────┬────┘
        │
        ▼
     CHECK  ───────────────► evidence
        │                       │
        │ no mutation           │
        ▼                       ▼
     PLAYBOOK ───────► explicit human / qualified executor
```

## Why the Kouretes?

In the Cretan myth of Rhea, the **Kouretes** drown out the infant Zeus's cries with a ritual shield-dance so Cronus cannot find him. Here the metaphor is less mystical and more useful: **coordination under hostile noise**.

The playbook is the choreography. The checks are the shields. The invariant is what must survive the noise.

> **ΚΡΟΝΟΣ ≠ ΧΡΟΝΟΣ.** Cronus is not Chronos. Ambiguity is a bug.

We keep the cultural reference deliberately precise: Rhea is a Titaness, daughter of Gaia and Uranus and mother of the Olympian generation; the familiar association of her name with Greek *rheō*, “to flow,” is attractive wordplay, not a premise this project needs to pretend is settled etymology.

## The contract

| Layer | Owns | Must not pretend to own |
|---|---|---|
| `foundation/` | platform-independent invariants and rationale | vendor commands |
| `adapters/` | vendor/platform mappings | universal truth |
| `checks/` | executable **read-only** diagnostics | remediation authority |
| `playbooks/` | operational procedures | proof that a procedure ran |
| `references/` | source notes | executable policy |
| `reports/` | generated evidence | canonical source state |

### Current truth receipt

**Implemented now:**

- JSON schemas for invariants, checks, and environments, with valid/invalid fixtures;
- structural validation, YAML/JSON validation, schema checks, shell linting, and Markdown-link checks;
- host-supported read-only diagnostics;
- timestamped Markdown + JSON reports;
- vendor/platform adapter structure.

**Explicitly not implemented by the current commands:** mutation of DNS, networking, credentials, packages, firewall, or system configuration.

That constraint is a feature. A diagnostic corpus that quietly edits the machine is not a diagnostic corpus; it is an executor wearing a fake moustache.

## Run the dance

```bash
make validate
make diagnose
make report
```

- `validate` — prove the corpus is structurally coherent.
- `diagnose` — observe supported host invariants without mutation.
- `report` — emit a timestamped receipt into `reports/`.

## Task genome

A useful operational contribution should be appendable without rewriting the mythology of everything before it:

```text
OBSERVATION
   ↓
INVARIANT
   ↓
ADAPTER
   ↓
READ-ONLY CHECK
   ↓
EVIDENCE
   ↓
REMEDIATION PLAYBOOK
   ↓
EXECUTION RECEIPT      ← only when some separate authority actually executes
```

That is the direction toward an **append-only operational memory**: not an infinite bag of prompts, but a register of claims with types, provenance, and reproducible checks. The repository is not yet a universal append-only database, and the README does not claim otherwise.

## Add a new move

1. Define or amend the invariant in `foundation/`.
2. Map it under `adapters/<platform>/` without leaking vendor semantics into the invariant.
3. Add a machine-readable check under `checks/`.
4. Add remediation under the relevant `playbooks/` area.
5. Update schemas/fixtures if the contract changes.
6. Run:

```bash
make validate && make diagnose && make report
```

## The Rhea family

| Project | Mythic role | Engineering role |
|---|---|---|
| **Rhea Project** | Rhea / succession | staged architecture + authority boundaries |
| **Rheknel** | the stone Cronus cannot digest | deterministic invariant gate |
| **Omnia Vault** | the Cretan cave | immutable-first state preservation |
| **Omnia Playbook** | the Kouretes' choreography | operational invariants + checks + procedures |
| **Blueshoes** | escape into open terrain | mutable network flows + Flow Surgery |

Explore the family surface at **https://blueshoes.space/rhea/**.

## License

BSD 3-Clause. Open infrastructure research by **Timelabs Non-Profit Corp**.

---

<p align="center"><strong>CHECK FIRST. MUTATE LATER. KEEP THE RECEIPT.</strong></p>
