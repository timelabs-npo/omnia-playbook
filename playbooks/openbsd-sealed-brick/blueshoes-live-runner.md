---
omnia_quarantine: "blueshoes orchestration plan — NOT part of the Omnia v1 normative or trusted semantic closure"
omnia_trusted_surface_include: false
omnia_category: "external_orchestration_operator_documentation"
justification: |
  Blueshoes is an operator-facing live-testing orchestration harness, NOT a
  runtime-level semantic primitive of Omnia v1. Omnia defines contracts
  (invariants, checks, adapter capabilities, owner operational intent,
  disagreement resolution, causal experiment registries, portable
  deterministic decision procedures). Blueshoes is merely ONE possible
  downstream ritual that an operator may choose to run, on a specific
  workstation, to exercise those contracts through repeated advisory worker
  rounds. Blueshoes decisions are evidence, NOT law. A Tribunal Runtime MUST
  NOT infer any additional semantic, default, or policy from the presence
  of this file or of scripts/blueshoes_live_test_runner.sh.
---

# blueshoes live-testing runner (openbsd sealed brick)

Read-only, bounded, append-only live-testing orchestration plan for blueshoes
sessions on this repository. The runner itself is
`scripts/blueshoes_live_test_runner.sh`. This document is the operator-facing
runbook. It is quarantined from the Omnia v1 normative trusted surface (see
YAML frontmatter above).

## Operator hard contract (no exceptions)

- Run this plan **only on the trusted admin workstation**. Never directly on
  the appliance. No `ssh root@router`, no `doas`, no `sudo` against any live
  box from the runner.
- This runner **never mutates** any live infrastructure. Specifically it must
  never run `pfctl -f`, `rcctl set`, `rcctl start/stop/restart`, `sysctl -w`,
  `route change/add`, `ifconfig ... up/down`, or any other config-changing
  command.
- The runner is dry-run-first. If `--no-dry-run-first` is passed the operator
  acknowledges they are skipping a recommended safety gate.
- Worker "disagreements" are recorded but **never auto-promoted** to a PASS.
  Any single `FAIL` or `ERROR` from a worker, and any `UNKNOWN`, must be
  resolved by an operator decision outside the runner before a subsequent
  blueshoes live round.
- Evidence stored under `reports/blueshoes/receipts/` is append-only and
  receipt-only. It can include: repository validation result summaries,
  offline syntax-rehearsal booleans/counts, worker votes with reason text,
  bounded collect posture booleans/counts. It MUST NOT include raw topology:
  no MAC addresses, no IPv4/IPv6 addresses, no interface names, no pf rule
  bodies, no route entries, no resolver values, no hostnames.

## Stages

1. `prep / owner approval gate`
   - Operator confirms candidate directory path (if any) is isolated, read-only,
     and does not contain real production credentials.
   - Runner confirms `adapters/openbsd/adapter.json` exists, passes schema,
     declares ontology, and is `support_tier=supported` with at least one
     validated capability mapping.
2. `dry-run-structure` (explicit unless `--no-dry-run-first` was set)
   - `bash scripts/validate.sh --structure-only`
3. `repo-validate`
   - Full `make validate` (links, schema fixtures, artifact cross-refs,
     adapter taxonomy, shell lint) using the workstation Python venv and
     shellcheck.
4. `repo-tests`
   - Full `make test` (unit tests for repository artifacts, validation
     contracts, and OpenBSD posture `--collect` / `--inspect-private`
     boundaries using mocked native commands).
5. `candidate rehearsal` (only if `--candidate-dir PATH` was supplied)
   - `pfctl -n -f candidates/.../pf.conf` — offline syntax only, no load.
   - `sh -n` on `hostname.if*` files in the candidate directory — syntax only.
   - Future `iked -n`, `unbound-checkconf`, `bgpd -n`, `relayd -n` may be
     added in a strictly additive commit; they must be `* -n` or equivalent
     offline-syntax forms.
6. `round {1..max-rounds}: six-advisory-worker vote`
   - Each round runs 6 separate deterministic advisory worker invocations.
   - Each worker returns only `PASS | FAIL | UNKNOWN` plus a short reason
     string. Raw stdout/stderr of workers is NOT written into the receipt
     JSON except as bounded digest lines under the worker's reason text.
   - Round consensus: FAIL if any worker returns FAIL or UNKNOWN. Operator
     must decide whether to re-run (e.g. after fixing a receipt-visible
     reason) or escalate.
7. `aggregate`
   - Append-only receipt JSON + markdown appended under
     `reports/blueshoes/receipts/<run-id>.*`.
   - Receipt JSON includes a sha256 of its companion log, a `contract`
     block restating mutation/evidence rules, and the FINAL `PASS|FAIL`.

## Recommended invocation

```bash
cd <repo root>
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

Repeat the invocation, possibly with an updated candidate directory and an
updated `trae/a0l-audit` checkout, after each operator decision. Each run
writes a fresh append-only receipt. Old receipts are never deleted or
overwritten by the runner.

## Suggestion: how to run *the assistant* until blueshoes live work is done

Because "live blueshoes" is operator-facing, slow, and gated on real
hardware, the assistant's recommended loop is bounded and receipt-driven.
On the trusted admin workstation, in an isolated terminal inside this repo:

1. Start from the current branch (`trae/a0l-audit`) with a clean `git status`
   (stash unrelated changes).
2. Create a local `candidates/openbsd-lab-01/` directory populated only with
   sanitized, offline-rehearsable config candidates (no real secrets).
3. Run the runner once with the recommended invocation above. Save the
   receipt id.
4. If the runner returns `FINAL=PASS`, record that receipt id as "assistant
   gate passed for round N" and proceed to operator-owned live-hardware
   steps outside this repo runner.
5. If the runner returns `FINAL=FAIL`, attach the assistant to the *receipt*
   (not to a live shell on the router): point the assistant at
   `reports/blueshoes/receipts/<run-id>.json` + `.log` and ask for the
   smallest safe repository-only change that addresses the first failing
   stage; then repeat step 3 with the same candidate dir (or an updated one
   if the failure was a syntax rehearsal issue), `--max-rounds` reset to a
   fresh value, and a new receipt id.
6. Bound the assistant's iterations with explicit
   `--max-rounds=N --max-wall-seconds=S` on every assistant-orchestrated
   invocation, and abort the loop if:
   - `MAX_WALL_SECONDS` is exceeded, or
   - a stage fails twice in a row with the same reason, or
   - the receipt's first failing stage is in the candidate rehearsal AND the
     workstation is missing the relevant offline tool (e.g. no `pfctl` on a
     non-OpenBSD admin workstation), in which case operator-visible
     "blueshoes-on-real-brick" step is required without the assistant
     fabricating evidence.

That cycle (runner receipt -> assistant repo-only change -> rerun -> new
receipt) is the assistant's bounded live-testing harness. It never takes
control of live hardware.
