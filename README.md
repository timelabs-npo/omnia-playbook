# Omnia Playbook

Vendor-neutral developer infrastructure playbook scaffold for Apple, Google Cloud, Azure, OpenWrt, macOS, and Windows.

## Architectural decisions

1. `foundation/` stores platform-independent invariants and rationale only.
2. `adapters/` stores vendor/platform mappings only.
3. `checks/` contains executable read-only diagnostics.
4. `playbooks/` contains remediation and operational procedures.
5. `references/` contains source documentation notes.
6. `reports/` stores generated output and is excluded from Git except `.gitkeep`.

## Core models

The data model fields are defined via JSON Schemas:

- `schemas/invariant.schema.json`
- `schemas/check.schema.json`
- `schemas/environment.schema.json`

Each schema includes one valid and one intentionally invalid fixture in `schemas/fixtures/`.

## Rheknel bus

`tools/compile_omnia_bus.py` compiles selected machine-readable invariant/check documents plus explicit assurance, freshness, evidence, and provenance metadata into the exact-version `OMNA` ABI 1.0 binary consumed by Rheknel. The compiler is deterministic, rejects unsupported or lossy values, and preserves repository boundaries: Omnia produces data; Rheknel evaluates it.

The normative wire contract and loss guarantees are in [`docs/OMNIA_RHEKNEL_ABI.md`](docs/OMNIA_RHEKNEL_ABI.md). Reproducible positive and adversarial fixtures are under [`artifacts/omnia-bus-v1/`](artifacts/omnia-bus-v1/README.md).

## Commands

```bash
make validate
make diagnose
make report
make compile-bus
make verify-bus
```

- `validate`: checks structure, YAML/JSON syntax, schema/fixture validation, shell linting, and internal Markdown links.
- `diagnose`: runs read-only host-supported checks (currently DNS invariant inspection).
- `report`: writes timestamped Markdown + JSON diagnostic reports to `reports/`.
- `compile-bus`: rebuilds the committed compact fixtures and SHA-256 manifest.
- `verify-bus`: proves a byte-identical rebuild and runs the codec/adversarial tests.

No command mutates DNS, networking, credentials, packages, firewall, or system configuration.

## Extending the playbook (agent workflow)

1. Add or update invariant documentation in `foundation/`.
2. Add adapter details under the matching `adapters/<vendor-or-platform>/` directory.
3. Add a machine-readable check definition under `checks/<domain>/`.
4. Add remediation documentation in `playbooks/recovery/` or the relevant playbook area.
5. Update schemas/fixtures if the model changes.
6. Run `make validate && make diagnose && make report`.
