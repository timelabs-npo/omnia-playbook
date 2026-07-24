# Omnia Playbook

Vendor-neutral developer infrastructure playbook scaffold for Apple, Google Cloud, Azure, OpenWrt, macOS, Windows, and OpenBSD.

## Architectural decisions

1. `foundation/` stores platform-independent invariants and rationale only.
2. `adapters/` stores vendor/platform mappings only.
3. `checks/` contains executable read-only diagnostics.
4. `playbooks/` contains remediation and operational procedures.
5. `references/` contains source documentation notes.
6. `reports/` stores generated output and is excluded from Git except `.gitkeep`.

Current recovery coverage includes:

- [DNS explicit resolver recovery](playbooks/recovery/dns-explicit-resolvers.md)
- [OpenBSD sealed-brick architecture and recovery](playbooks/openbsd-sealed-brick/README.md)

## Core models

The data model fields are defined via JSON Schemas:

- `schemas/invariant.schema.json`
- `schemas/check.schema.json`
- `schemas/environment.schema.json`

Each schema includes one valid and one intentionally invalid fixture in `schemas/fixtures/`.

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

`diagnose` and `report` inspect live host DNS state. The current prototype retains raw resolver output in local, Git-ignored report files, so do not run those commands with sensitive topology until the redaction/provenance work is complete or a separate evidence procedure is approved.

## Extending the playbook (agent workflow)

1. Add or update invariant documentation in `foundation/`.
2. Add adapter details under the matching `adapters/<vendor-or-platform>/` directory.
3. Add a machine-readable check definition under `checks/<domain>/`.
4. Add remediation documentation in `playbooks/recovery/` or the relevant playbook area.
5. Update schemas/fixtures if the model changes.
6. Run `make validate` and `make test`.

Live diagnostics and report generation are separate, explicitly approved operations.
