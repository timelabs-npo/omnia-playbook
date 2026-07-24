# TRAE OpenBSD Sealed-Brick Report

## Changed Paths

- `.gitignore`
- `README.md`
- `adapters/openbsd/README.md`
- `checks/openbsd/chk-openbsd-v0-collection-boundary.yaml`
- `checks/openbsd/inspect_openbsd_v0.sh`
- `checks/openbsd/invariant-openbsd-sealed-brick.yaml`
- `environments/openbsd-sealed-brick/environment.json`
- `playbooks/openbsd-sealed-brick/README.md`
- `references/openbsd/README.md`
- `reports/trae-openbsd-sealed-brick.md`
- `schemas/fixtures/valid/check.openbsd-sealed-brick.valid.json`
- `schemas/fixtures/valid/environment.openbsd-sealed-brick.valid.json`
- `schemas/fixtures/valid/invariant.openbsd-sealed-brick.valid.json`
- `scripts/validate.sh`
- `tests/test_schemas.py`
- `tests/test_openbsd_contract.py`
- `tests/test_repository_artifacts.py`
- `tests/test_validation_contract.py`

## Commands Run

- `python3 -m venv /tmp/omnia-playbook-venv`
- `/tmp/omnia-playbook-venv/bin/python -m pip install -r requirements-dev.txt`
- `PATH="/tmp/omnia-playbook-venv/bin:$PATH" ./scripts/validate.sh --links-only`
- `PATH="/tmp/omnia-playbook-venv/bin:$PATH" make validate`
- `PATH="/tmp/omnia-playbook-venv/bin:$PATH" make test`
- `chmod +x checks/openbsd/inspect_openbsd_v0.sh`
- `git commit -m "TRAE: add OpenBSD sealed-brick playbook and checks"`
- `git push -u origin trae/a0l-audit`
- `PATH="/tmp/omnia-playbook-venv/bin:$PATH" make validate`
- `PATH="/tmp/omnia-playbook-venv/bin:$PATH" make test`

## Results

- Internal Markdown links passed.
- Full repository validation passed, including schema fixtures, repository artifact validation, and shell linting.
- `make test` passed with 15 tests.
- The OpenBSD read-only collection script is executable and contract-tested off-host.
- Commit `0832e50` was created on `trae/a0l-audit`.
- Branch publish succeeded to `origin/trae/a0l-audit`.
- OpenBSD-specific schema-valid environment, invariant, and check fixtures now pass under the existing schemas and are exercised by `make validate` and `make test`.

## Known Thin Places

- The OpenBSD collection script is contract-tested on non-OpenBSD hosts, but full `--collect` execution still needs a real OpenBSD target.
- The repository models the evidence path and deterministic gate contract, but does not yet implement the future signed policy gate.
- The playbook is deliberately documentation-first; it does not automate rollback on live hardware.

## Next Smallest Hardware Experiment

Boot a single OpenBSD appliance on isolated lab hardware or a serial-console-capable VM, load the last-known-good network and `pf` files, and run `./checks/openbsd/inspect_openbsd_v0.sh --collect` to confirm the bounded collection contract before any broader management workflow is attempted.
