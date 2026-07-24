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
- `PATH="/tmp/omnia-playbook-venv/bin:$PATH" python3 -m unittest tests.test_openbsd_contract -v`
- `PATH="/tmp/omnia-playbook-venv/bin:$PATH" make validate`
- `PATH="/tmp/omnia-playbook-venv/bin:$PATH" make test`
- `git commit -m "TRAE: minimize OpenBSD public collection output"`
- `git push`

## Results

- Internal Markdown links passed.
- Full repository validation passed, including schema fixtures, repository artifact validation, and shell linting.
- `make test` now passes with 18 tests.
- The OpenBSD read-only collection script is executable, contract-tested off-host, and its public `--collect` mode now emits minimized posture booleans and counts only.
- Raw native state is reserved for the explicit `--inspect-private` path with the `LOCAL SENSITIVE OUTPUT` / `DO NOT UPLOAD OR APPEND TO LOG.0` warning.
- Commit `628d289` was created on `trae/a0l-audit` for the public-output minimization fix.
- Branch publish succeeded to `origin/trae/a0l-audit`.
- OpenBSD-specific schema-valid environment, invariant, and check fixtures now pass under the existing schemas and are exercised by `make validate` and `make test`.

## Known Thin Places

- The OpenBSD collection script is contract-tested off-host with mocked native outputs, but the minimized posture summary still needs one real OpenBSD run for end-to-end confirmation.
- The repository models the evidence path and deterministic gate contract, but does not yet implement the future signed policy gate.
- The `--inspect-private` path is intentionally local and sensitive; it is not suitable for append-only evidence until a separate redaction gate exists.
- The playbook is deliberately documentation-first; it does not automate rollback on live hardware.

## Next Smallest Hardware Experiment

Boot a single OpenBSD appliance on isolated lab hardware or a serial-console-capable VM, load the last-known-good network and `pf` files, and run `./checks/openbsd/inspect_openbsd_v0.sh --collect` to confirm the bounded collection contract before any broader management workflow is attempted.
