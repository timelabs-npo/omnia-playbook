# Omnia Playbook

> **Status: experimental / not a compliance certification.**
>
> Omnia is an owner-controlled, local-first assurance prototype. It records
> bounded observations, produces deterministic findings, and prepares
> reviewable plans. It does not establish legal compliance, prove that an
> observation is true, or authorize a system change.

Vendor-neutral developer infrastructure playbook scaffold for Apple, Google
Cloud, Azure, OpenWrt, macOS, and Windows.

## Architectural decisions

1. `foundation/` stores platform-independent invariants and rationale only.
2. `adapters/` stores vendor/platform mappings only.
3. `checks/` contains executable read-only diagnostics.
4. `playbooks/` contains remediation and operational procedures.
5. `references/` contains source documentation notes.
6. `reports/` stores generated output and is excluded from Git except `.gitkeep`.
7. `log.0` is the append-only source record; SQLite files are disposable,
   rebuildable read models.
8. Runtime remains local and dependency-light. Provider tools can supply
   bounded input through adapters, but are not part of Omnia's authority root.

## Core models

The data model fields are defined via JSON Schemas:

- `schemas/invariant.schema.json`
- `schemas/check.schema.json`
- `schemas/environment.schema.json`
- `schemas/log-event.schema.json`

Each schema includes one valid and one intentionally invalid fixture in `schemas/fixtures/`.

The event and projection design is described in
[`docs/architecture/log0-multi-nqlite.md`](docs/architecture/log0-multi-nqlite.md).
Here, **multi-NQLite** is a project-local name for three named,
SQLite-compatible read models: `catalog`, `assurance`, and `workflow`. It is
not a distributed database, consensus protocol, or third-party service.

The writer-assigned `sequence` is the v0 Deterministic Time System (DTS) tick:
it orders committed records independently of wall-clock timestamps. With one
writer this is a central logical sequence, not a claim of distributed
causality, CRDT convergence, or cross-host consensus.

The future automation boundary is specified as a
[`fail-fast policy machine`](docs/architecture/fail-fast-policy.md): the Owner
signs bounded policy rather than approving every event; only `PASS` may enter
that policy gate, while `FAIL`/`ERROR` abort and `UNKNOWN` quarantines. The
current repository does not contain a mutating executor.

Unusual or failure-prone work belongs in the
[`experimental lane`](docs/experiments/README.md). Its first machine-readable
feature is a Projection Honesty Contract: every derived view declares what it
preserves, drops, can answer, and must refuse.

## Development setup

The supported validation baseline is:

- Bash 3.2 or newer;
- Python 3.11 or newer;
- Ruby with its standard `yaml` library;
- `jq` 1.6 or newer.

Create an isolated environment and install the pinned validation dependencies:

```bash
python3 -m venv /tmp/omnia-playbook-venv
source /tmp/omnia-playbook-venv/bin/activate
python3 -m pip install -r requirements-dev.txt
```

The dependency file supplies both the `jsonschema` Python module and the `shellcheck` command used by validation.

## Commands

```bash
make validate
make test
make diagnose
make report
```

- `validate`: checks structure, YAML/JSON syntax, schema/fixture validation, shell linting, and internal Markdown links.
- `test`: runs the safe unit and validation-contract tests.
- `diagnose`: runs read-only host-supported checks (currently DNS invariant inspection).
- `report`: writes timestamped Markdown + JSON diagnostic reports to `reports/`.

No command mutates DNS, networking, credentials, packages, firewall, or system configuration.

`diagnose` inspects live host DNS state. `report` additionally writes local
artifacts. Neither command is a legal or security assessment. Raw resolver
output is not retained by the default report path.

Before sharing any repository or report outside the owner-controlled
environment, apply the [`publication gate`](docs/publication-gate.md).

## Extending the playbook (agent workflow)

1. Add or update invariant documentation in `foundation/`.
2. Add adapter details under the matching `adapters/<vendor-or-platform>/` directory.
3. Add a machine-readable check definition under `checks/<domain>/`.
4. Add remediation documentation in `playbooks/recovery/` or the relevant playbook area.
5. Update schemas/fixtures if the model changes.
6. Run `make validate` and `make test`.

Live diagnostics and report generation are separate, explicitly approved operations.
