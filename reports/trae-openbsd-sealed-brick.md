# TRAE OpenBSD Sealed-Brick Report

## Changed Paths

- `.gitignore`
- `README.md`
- `adapters/apple/README.md`
- `adapters/apple/adapter.json`
- `adapters/azure/README.md`
- `adapters/azure/adapter.json`
- `adapters/google-cloud/README.md`
- `adapters/google-cloud/adapter.json`
- `adapters/macos/README.md`
- `adapters/macos/adapter.json`
- `adapters/openbsd/README.md`
- `adapters/openbsd/adapter.json`
- `adapters/openwrt/README.md`
- `adapters/openwrt/adapter.json`
- `adapters/windows/README.md`
- `adapters/windows/adapter.json`
- `checks/openbsd/chk-openbsd-v0-collection-boundary.yaml`
- `checks/openbsd/inspect_openbsd_v0.sh`
- `checks/openbsd/invariant-openbsd-sealed-brick.yaml`
- `environments/bluenikee/environment.json`
- `environments/example/environment.json`
- `environments/openbsd-sealed-brick/environment.json`
- `playbooks/openbsd-sealed-brick/README.md`
- `playbooks/openbsd-sealed-brick/blueshoes-live-runner.md`
- `references/openbsd/README.md`
- `reports/trae-openbsd-sealed-brick.md`
- `schemas/adapter.schema.json`
- `schemas/fixtures/valid/adapter.openbsd-sealed-brick.valid.json`
- `schemas/fixtures/valid/adapter.valid.json`
- `schemas/fixtures/invalid/adapter.placeholder-invalid.json`
- `schemas/fixtures/invalid/adapter.invalid.json`
- `schemas/fixtures/valid/check.openbsd-sealed-brick.valid.json`
- `schemas/fixtures/valid/environment.openbsd-sealed-brick.valid.json`
- `schemas/fixtures/valid/invariant.openbsd-sealed-brick.valid.json`
- `scripts/blueshoes_live_test_runner.sh`
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
- `PATH="/tmp/omnia-playbook-venv/bin:$PATH" ./scripts/validate.sh --structure-only`
- `PATH="/tmp/omnia-playbook-venv/bin:$PATH" ./scripts/validate.sh --artifacts-only`
- `PATH="/tmp/omnia-playbook-venv/bin:$PATH" ./scripts/validate.sh --help`
- `PATH="/tmp/omnia-playbook-venv/bin:$PATH" bash scripts/blueshoes_live_test_runner.sh --help`
- `PATH="/tmp/omnia-playbook-venv/bin:$PATH" bash scripts/blueshoes_live_test_runner.sh --adapter openbsd --plan playbooks/openbsd-sealed-brick/blueshoes-live-runner.md --workers 6 --max-rounds 2 --max-wall-seconds 600 --receipt-dir reports/blueshoes/receipts`
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
- `make test` now passes with 22 tests.
- The OpenBSD read-only collection script is executable, contract-tested off-host, and its public `--collect` mode now emits minimized posture booleans and counts only.
- Raw native state is reserved for the explicit `--inspect-private` path with the `LOCAL SENSITIVE OUTPUT` / `DO NOT UPLOAD OR APPEND TO LOG.0` warning.
- Adapter directory presence alone no longer implies "supported" status; every adapter now declares its ontology/type through a required `adapters/<name>/adapter.json` manifest.
- Ambiguous taxonomy is a validation failure:
  - missing `adapters/<name>/adapter.json` fails structure-only and artifacts-only checks,
  - `support_tier=supported` without at least one validated capability mapping fails,
  - `status=VALIDATED` is only allowed when `support_tier=supported`,
  - `status=UNIMPLEMENTED` cannot be combined with `support_tier=supported`,
  - environment files must only reference adapters whose manifest says `support_tier=supported`.
- Placeholder-only adapters (`apple`, `google-cloud`, `azure`) explicitly declare `status=UNIMPLEMENTED`, `support_tier=unsupported`, and `validated_capability_ids=[]`; environment files that reference them now fail validation.
- The new adapter schema supports `validated_capability_ids` cross-checks against declared capabilities and evidence references/source path resolution.
- Blueshoes live-testing runner (`scripts/blueshoes_live_test_runner.sh`) runs read-only, bounded, append-only, and produces a final receipt JSON + log in `reports/blueshoes/receipts/`; the runner is exercised by `--adapter openbsd --max-rounds 2` and returns `FINAL=PASS` for the current tree.
- OpenBSD-specific schema-valid environment, invariant, and check fixtures now pass under the existing schemas and are exercised by `make validate` and `make test`.

## Known Thin Places

- The OpenBSD collection script is contract-tested off-host with mocked native outputs, but the minimized posture summary still needs one real OpenBSD run for end-to-end confirmation.
- The repository models the evidence path and deterministic gate contract, but does not yet implement the future signed policy gate.
- The `--inspect-private` path is intentionally local and sensitive; it is not suitable for append-only evidence until a separate redaction gate exists.
- The playbook is deliberately documentation-first; it does not automate rollback on live hardware.
- Blueshoes offline rehearsal for `pfctl -n -f` and `hostname.if` syntax checks is gated on the operator providing `--candidate-dir`; without real candidate files it skips gracefully.
- Advisory worker emulation in the runner is deterministic for round 1 (runs `tests.test_validation_contract`) and bounded consensus for subsequent rounds; for real blueshoes live sessions operators still must reconcile any non-PASS vote manually.

## Next Smallest Blueshoes Experiment (Suggested Runner Workflow)

Use `scripts/blueshoes_live_test_runner.sh` on the trusted admin workstation only. No appliance access is required for the repository/rehearsal gate:

```bash
. .venv/bin/activate
bash scripts/blueshoes_live_test_runner.sh \
  --adapter openbsd \
  --plan playbooks/openbsd-sealed-brick/blueshoes-live-runner.md \
  --candidate-dir ./candidates/openbsd-lab-01 \
  --workers 6 \
  --max-rounds 3 \
  --max-wall-seconds 900 \
  --receipt-dir reports/blueshoes/receipts
```

How to keep the assistant running *until blueshoes live work is done* (receipt-driven loop):

1. Run the runner once to obtain the first `FINAL` receipt.
2. If `FINAL=FAIL`, pass the assistant the failing receipt (`reports/blueshoes/receipts/<run-id>.json` and `.log`) and ask for the smallest repository-only change that resolves the first failing stage.
3. Re-run the runner and inspect the new receipt.
4. Repeat with bounded parameters (`--max-rounds`, `--max-wall-seconds`). Abort if the same stage fails twice in a row with the same reason, or if the first failing stage needs real hardware confirmation (e.g. an offline `pfctl -n -f` rehearsal that cannot be completed without actual `pfctl` on the admin box).
5. After `FINAL=PASS`, proceed to the operator-owned live-hardware step: boot one isolated OpenBSD appliance, load last-known-good configs, run `./checks/openbsd/inspect_openbsd_v0.sh --collect`, and compare the resulting bounded posture summary against the check fixture expectations before any broader management workflow.
