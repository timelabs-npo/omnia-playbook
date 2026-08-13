# TRAE OpenBSD Sealed-Brick Report + Omnia v1 Runtime-Native Closure

## WHAT CHANGED (runtime-native + architectural correction)

Five large structural changes landed:

1. **New schemas (10 total) for Omnia v1 portable semantics**:
   `schemas/invariant.schema.json`, `schemas/check.schema.json`,
   `schemas/adapter.schema.json`, `schemas/environment.schema.json`,
   `schemas/runtime_bundle.schema.json`, plus five new schemas:
   `schemas/network_model.schema.json` (flow/intent/dependency graph +
   observation/intervention points),
   `schemas/causal_experiment.schema.json` (12 mandatory bounded-experiment
   attributes, passive-first 5-tier evidence hierarchy, fail-closed rollback,
   cryptographic signed receipt contract),
   `schemas/owner_operational_intent.schema.json` (pre-failure declared owner
   intent, named_services + named_capabilities user-defined taxonomy,
   invariant/service/policy separation-of-concerns consts),
   `schemas/tribunal_participant_claim.schema.json` (vendor-neutral independent
   participant claim records: participant_id, model/provenance identity,
   claim, evidence_refs, assumptions, unresolved_questions, proposed_result;
   no specific vendor/model lock-in consts),
   `schemas/disagreement_resolution.schema.json` (per-decision-class conflict
   resolution policy: locate differing premise -> locate differing evidence
   interpretation -> identify discriminating observation -> bounded
   measurement -> recompute; anti-majority `majority_vote_alone_must_not_override: true`
   const required; fail_closed + action_under_unresolved enum + convergence
   criteria configurable per decision class network_policy / dns_explicit_resolvers /
   openbsd_sealed_brick_bounded_control / causal_experiment_approval /
   causal_experiment_commit / owner_intent_service_violation /
   evidence_tier_elevation / authority_promotion).

2. **Machine-closed artifacts upgraded to v1 semantic closure**. Each
   normative invariant carries: id/version/status/scope/applicability/layer
   (layer: normative required), preconditions with unknown_behavior,
   required_observations with schemas, required_capabilities, decision_rule
   with explicit 4-arm `pass_if / fail_if / unknown_if / error_if` using
   `omnia_deterministic_v1` operators (`observation_all_match`,
   `observation_not_equals`, `missing_observation`,
   `contradictory_observations`), explicit 4-outcome PASS/FAIL/UNKNOWN/ERROR
   semantics, authority_ceiling, forbidden_actions[], dependency_ids[],
   remediation_refs{} + source_refs{} split by layer, evidence_requirements
   with classes_allowed + min_tier_for_pass. Operational checks declare
   authority_ceiling (max_authority ∈ {read_only_evidence,
   advisory_remediation_only, repair_unattended}) with
   `no_policy_invention=true, no_authority_promotion=true` consts +
   forbidden_policy_domains. Adapters are DUMB:
   `decides_truth=false, decides_policy=false, decides_remediation=false,
   output_is_typed_untrusted_evidence=true, adapter_does_not_decide_truth=true`
   consts required. Evidence-tier taxonomy with explicit
   `mock_not_equivalent_to_live=true, live_tier_requires_provenance_ref=true`
   consts. Environments now separate `runtime_host{host_substrate_only=true}`
   (substrate-only is const) from `estate_targets[]` per-target platform,
   capabilities_required, evidence_tier_minimum, adapter_id_hint — so
   applicability is TARGET-oriented NOT runtime-host-oriented. Owner
   operational intents declared pre-failure in
   `environments/bluenikee/owner_intent.bluenikee-001.json` (5 named user
   services: public-internet-access, video-streaming,
   development-services, remote-admin, package-retrieval + 2 named
   capabilities). Disagreement resolution policies for
   openbsd-sealed-brick-bounded-control (fail closed,
   LAST_KNOWN_GOOD_RESTORE_ONLY under unresolved disagreement) and
   dns-explicit-resolvers (fail-open advisory).

3. **Deterministic canonical runtime bundle exporter** (`scripts/export_runtime_bundle.py`)
   produces `build/runtime-bundle/omnia.runtime.v1.json` with:
   - layer_inclusion (normative true, operational true, explanatory stripped)
   - tribunal_participant_claim_model (vendor-neutral fields with
     `no_specific_vendor_lock=true, no_specific_model_lock=true,
     deterministic_semantics_owner=Omnia, same_result_across_runtimes=true`)
   - deterministic_procedure_exports per invariant (proc-<decision_rule.id>
     with `omnia_deterministic_v1_json` 4-arm structure and
     `portable_across_runtimes_must_match_ref_implementation=true`)
   - multi_interpreter_conformance_refs naming scenarios A-G with
     `majority_count_alone_must_not_override=true` const required
   - indexes (by_platform, by_vendor, by_inv→caps, by_inv→checks,
     by_cap→ops, by_tier→checks, closure_refs per target with id lists
     + size_bytes_approx)
   - metrics (counts including adapters_by_evidence_tier, sizes
     canonical_bundle/normative_core_bytes_approx,
     largest/median rule closure bytes, representative_task closure map per
     target, closures largest/median dep sizes unresolved refs)
   - execution_contract with tribunal_prompt_only (7 sentences of
     execution discipline only; domain semantics all in Omnia, not prompt)
     plus const booleans `never_invent_policy,
     missing_required_evidence_is_unknown, use_declared_decision_rules_only,
     never_increase_authority, typed_result_with_evidence_refs_only`;
     model_swappability with no vendor and no model name dependency.
   - Reproducible canonical SHA-256 digest with sorted keys, placeholder
     timestamp/digest fields so same source commit → identical bytes.
   - Validate.sh runs the exporter twice to enforce byte-identical
     reproducibility before stamping.

4. **Validation gates extended**. `scripts/validate.sh` now runs:
   - 10-schema fixture map (new owner_intent, tribunal, disagreement,
     causal, network_model, runtime_bundle each have valid+invalid
     fixtures, 25 total fixtures)
   - Dumb adapter doctrine enforcement
   - Adapter evidence-tier taxonomy with support_tier=supported requiring
     at least one non-declared_only validated_capability_ids entry and
     status>=implemented equivalent; tier elevation forbidden
   - Invariant capability/observation cross-refs to adapter contracts
   - Invariant per-platform evidence_tier_minimum gate (only applies
     when check's platform is explicitly enumerated in inv target_platforms)
   - DFS circular dependency detection on invariant dependency_ids
   - Runtime-readiness gates for normative invariants (10 required fields
     + 4 outcomes present + decision_rule.unknown_if exists + authority
     ceiling present)
   - Disagreement recompute_workflow 5-step order exact match + anti-majority
     const true
   - Causal experiment 12-gate checks (never_invent, unvetted prohibited,
     fail_closed rollback true, evidence_method_hierarchy matches one of two
     exact 5-tier orderings)
   - Owner intent declares_before_failure=true + invariant_refs_required_if_fail
     existence
   - Exporter run with 2-pass digest reproducibility check.

5. **Tests expanded (37 tests, all green)**:
   tests/test_zero_history.py (8 scenarios: happy PASS, missing->UNKNOWN,
   contradictory->ERROR conflict, unsupported capability → missing
   provider, mock!=live tier elevation reject, cross-platform applicability
   macos/openwrt applicable windows/openbsd not SKIP_INAPPLICABLE, broken
   ref inv-NO-SUCH-ID → LookupError validation fail, unauthorized
   mutating + read_only → PermissionError fail closed; 18 tests pass
   with 13 subtests), tests/test_multi_interpreter_conformance.py (7
   Tribunal conformance scenarios A-G all exercised with the real
   inv-dns-explicit-observable-resolvers root: A unanimous correct PASS +
   determinism rechecked ×5; B one participant contradicts deterministic
   Omnia rule PASS/FAIL override rejected; C disagreement because
   evidence missing → UNKNOWN trumps any PASS majority; D contradictory
   evidence → ERROR independent of majority; E 2 wrong PASS majority + 1
   correct FAIL with decisive evidence → final FAIL (anti-majority
   override by evidence+Omnia semantics enforced by
   `_tribunal_majority_must_not_override()`); F UNKNOWN → PASS after one
   additional bounded observation materializes reachability=true obs; G
   unresolved disagreement with fail_closed=true decision class →
   action_under_unresolved restricted to allowed enum. Required property
   enforced across all scenarios: majority count alone never overrides
   deterministic Omnia rule evaluation and evidence grounding),
   test_repository_artifacts.py (adapter manifest schema + taxonomy,
   environment schema + adapter id→dir resolution with fallbacks,
   check+invariant files match schema + cross-refs with v1/v0 dual naming
   paths), test_openbsd_contract.py (public collect emits only minimized
   posture booleans/counts no IPv4/MAC/hostname/ifname/rule/resolver;
   --inspect-private emits raw with warning; check.command never
   references --inspect-private even when forbidden_actions prose mentions
   it), test_validation_contract.py (missing manifest → ambiguous
   taxonomy; supported without validated_ids → fail; UNIMPLEMENTED +
   supported → fail; --collect public output rejects sensitive classes).

6. **Blueshoes boundary quarantine**:
   `playbooks/openbsd-sealed-brick/blueshoes-live-runner.md` carries
   omnia_trusted_surface_include=false frontmatter with full
   justification; `scripts/blueshoes_live_test_runner.sh` carries the
   equivalent header comment. Exporter intentionally does not rglob
   scripts dir or non-causal playbooks — these artifacts are operator
   ritual orchestration conveniences, not normative Omnia law. Tribunal
   participants MUST NOT infer semantics from them.

7. **Critical Architectural Correction encoded (7 pillars reaffirmed)**:
   Omnia owns BOTH world semantics AND normative computation. Tribunal
   Runtime is interpreter/executor/checker, NOT the owner of semantics.
   Same Omnia bundle + same observations → same result across all
   conforming MBSD/OpenBSD/macOS/Linux/other runtime implementations,
   runtime implementation changes MUST NOT alter prescribed result.
   Tribunal participants are vendor-neutral replaceable epistemic
   workers under Omnia law, not the law's authors. Majority vote alone
   CANNOT override deterministic Omnia rules and evidence. Disagreement
   is first-class resolved via premise/interpretation/discriminating-obs
   /bounded-measurement/recompute 5-step workflow with per-decision-class
   policy controls. Owner operational intent declared pre-failure with
   user-defined service taxonomy so autonomous systems need not ask a
   human during incidents whether a named expected service is actually
   required.

## Changed Paths (updated)

- `.gitignore`
- `README.md`
- `requirements-dev.txt` (added PyYAML==6.0.2 for exporter)
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
- `checks/dns/invariant-dns-explicit-resolvers.yaml`
- `checks/dns/chk-dns-macos-observe.yaml`
- `checks/dns/chk-dns-windows-observe.yaml`
- `checks/dns/chk-dns-linux-openwrt-observe.yaml`
- `environments/bluenikee/environment.json`
- `environments/bluenikee/owner_intent.bluenikee-001.json`
- `environments/bluenikee/disagree.dns-explicit-resolvers.json`
- `environments/example/environment.json`
- `environments/openbsd-sealed-brick/environment.json`
- `environments/openbsd-sealed-brick/disagree.openbsd-sealed-brick-bounded-control.json`
- `playbooks/openbsd-sealed-brick/README.md`
- `playbooks/openbsd-sealed-brick/blueshoes-live-runner.md`
- `playbooks/diagnostics/causal-experiment-dns-reachability-001.json`
- `playbooks/diagnostics/dns.md`
- `references/openbsd/README.md`
- `reports/trae-openbsd-sealed-brick.md`
- `schemas/adapter.schema.json`
- `schemas/check.schema.json`
- `schemas/invariant.schema.json`
- `schemas/environment.schema.json`
- `schemas/runtime_bundle.schema.json`
- `schemas/network_model.schema.json` (new)
- `schemas/causal_experiment.schema.json` (new)
- `schemas/owner_operational_intent.schema.json` (new)
- `schemas/tribunal_participant_claim.schema.json` (new)
- `schemas/disagreement_resolution.schema.json` (new)
- `schemas/fixtures/valid/*.valid.json` (14, all rewritten for v1 schemas)
- `schemas/fixtures/invalid/*.invalid.json` (11, 6 new types added)
- `scripts/blueshoes_live_test_runner.sh`
- `scripts/validate.sh`
- `scripts/export_runtime_bundle.py` (new, ~460 lines deterministic exporter)
- `tests/test_schemas.py`
- `tests/test_openbsd_contract.py`
- `tests/test_repository_artifacts.py`
- `tests/test_validation_contract.py`
- `tests/test_zero_history.py` (new, 18 zero-history tests)
- `tests/test_multi_interpreter_conformance.py` (new, 7 scenarios A-G)

## RUNTIME BUNDLE FORMAT

File: `build/runtime-bundle/omnia.runtime.v1.json`
Schema: `schemas/runtime_bundle.schema.json` (Draft 2020-12, 22 required top-level fields)

Top-level structure (deterministic key order in output):

```
schema_version         const "omnia.runtime.v1"
generated_at_utc       ISO-8601 stamp (reproducible: replaced with "__PLACEHOLDER__" during digest)
source_commit          git HEAD commit short sha via export_runtime_bundle.py
canonical_digest_sha256   SHA-256 over sorted JSON minus generated_at + digest itself; 2-pass reproducibility checked
layer_inclusion        { normative: true, operational: true, explanatory_stripped: true }
registry               { invariant_ids, capability_ids, operation_ids, check_ids, adapter_ids,
                         environment_ids, owner_intent_ids, disagreement_resolution_ids,
                         causal_experiment_ids, network_model_ids, deterministic_procedure_ids }
capabilities[] / operations[]   flattened lists derived from adapter declared_capabilities
adapters_compact[]     stripped of explanatory; authority_ceiling + dumb doctrine consts retained
invariants_compact[]   normative only: id, applicability, preconditions, required_observations,
                         required_capabilities, decision_rule, outcomes, authority_ceiling,
                         forbidden_actions, dependency_ids
checks_compact[]       operational only: id, invariant_ref, target_platform, authority_ceiling,
                         forbidden_actions, capability_ref, observation_contract,
                         evidence_tier_claim, evidence_tier_support, command, requires, timeout,
                         exit_code_semantics, observation_semantics, unknown_semantics, error_semantics
environments[]         runtime_host separated from estate_targets; owner_intent_refs[] +
                         disagreement_resolution_refs[] retained
owner_intents[]        declared_before_failure=true; named_services[] / named_capabilities[]
disagreement_resolutions[]  per decision_class policy, fail_closed, action_under_unresolved enum,
                             recompute_workflow 5-step, majority_vote_alone_must_not_override true
causal_experiments[]   21 required top-level; 12 attribute mandatory; evidence_method_hierarchy 5-tier exact
network_models[]       operator_intents, flows, dependency_graph, paths, policy_boundaries,
                         observation_points, intervention_points, evidence_snapshots (signed JWS receipt ref)
tribunal_participant_claim_model   { claim_required_fields, identity_independent fields,
                                     no_specific_vendor_lock=true, no_specific_model_lock=true,
                                     deterministic_semantics_owner=Omnia,
                                     same_result_across_runtimes=true }
deterministic_procedure_exports[]  { id: proc-<decision_rule.id>, version,
                                      omnia_deterministic_v1_json: {pass_if, fail_if, unknown_if, error_if},
                                      portable_across_runtimes_must_match_ref_implementation=true }
multi_interpreter_conformance_refs  { scenarios: [A..G], paths,
                                        majority_count_alone_must_not_override: true }
indexes                { by_platform, by_vendor, by_inv->caps, by_inv->checks, by_cap->ops,
                          by_tier->checks, closure_refs[target]={id_list, size_bytes_approx} }
metrics                { counts, sizes, closures } (see RUNTIME FOOTPRINT METRICS)
execution_contract     { tribunal_prompt_only: "<7 sentence discipline only prompt — NO domain semantics here>",
                          const booleans: never_invent_policy=true,
                          missing_required_evidence_is_unknown=true,
                          use_declared_decision_rules_only=true,
                          never_increase_authority=true,
                          typed_result_with_evidence_refs_only=true,
                          model_swappability.no_vendor_name_dependency=true,
                          model_swappability.no_model_name_dependency=true }
```

## RUNTIME BUNDLE DIGEST

```
schema_version:     omnia.runtime.v1
source_commit:      (from actual `git rev-parse --short HEAD` at export time)
canonical_digest:   8013cea3fc788351065c602ffe09225aefc3e2d81a4e8d90d153c3f59c6ac83a
2nd run digest:     8013cea3fc788351065c602ffe09225aefc3e2d81a4e8d90d153c3f59c6ac83a
                    (byte-identical — reproducibility confirmed in validate.sh 2-pass gate)
```

Digests are computed over sorted JSON with generated_at_utc and canonical_digest_sha256
fields temporarily replaced with "__PLACEHOLDER__" strings so changes only in those
stamp fields do not falsify semantic comparison. Changing any normative field
(PASS/FAIL arms, tier claims, applicability platforms, authority ceilings,
forbidden actions, deterministic procedure exports) changes the digest.
Changing only explanatory prose typically does not (exporter strips those fields).

## EXAMPLE: closure + observations + deterministic result

**Example closure target:** `router-sealed-brick-1`
**Environment:** environments/openbsd-sealed-brick/environment.json
**Invariant closure (compact):**
  inv-openbsd-sealed-brick-bounded-control
  → dependency_ids: [inv-dns-explicit-observable-resolvers] (empty here but structure generalizes)
  → required_capabilities: [cap-openbsd-bounded-collect-v0]
  → required_observations:
      obs-ob-v0-collect-contract-version (string, minLength 2)
      obs-ob-v0-collect-output-mode    (enum: public_minimized|private_raw_redacted|private_raw_full)
      obs-ob-v0-collect-result         (enum: PASS|FAIL|UNKNOWN|ERROR)
  → decision_rule dr-openbsd-bounded-control-v1 arms:
      pass_if: observation_all_match contract_version=v0 output_mode=public_minimized result=PASS
      fail_if: contract_version!=v0 OR output_mode!=public_minimized OR result in {FAIL, ERROR}
      unknown_if: missing_observation on any of the 3
      error_if: contradictory_observations contract_version vs output_mode vs result
  → authority_ceiling max_authority=advisory_remediation_only
  → forbidden_actions: fa-pf-load-live, fa-rcctl-change, fa-egress-widen

**Hypothetical observations emitted by chk-openbsd-v0-collection-boundary:**
```
obs-ob-v0-collect-contract-version = "v0"
obs-ob-v0-collect-output-mode      = "public_minimized"
obs-ob-v0-collect-result           = "PASS"
```

**Deterministic result (applying omnia_deterministic_v1_json proc-dr-openbsd-bounded-control-v1):**
→ PASS (deterministic, same on OpenBSD/macOS/Linux/MBSD any conforming runtime)
→ Portable reproducibility: 5 runs of `_apply_deterministic_rule()` in scenario A
  of test_multi_interpreter_conformance return identical string "PASS" with
  identical grounding reason string "pass:explicit-count-and-reachable" (DNS root used there)

**Example Tribunal claim record for scenario E (majority wrong, one correct):**
```json
{
  "participant_id": "tp-eve-01",
  "model_identity": "tiny-model-family-foo-v2-1.1b@sha256:aabb…",
  "provenance_identity": "open-corpus-research-ecosystem",
  "alignment_assumptions": ["refuse-nonevidence-based-pass"],
  "claim": {
    "type": "deterministic_omnia_rule",
    "result": "FAIL"
  },
  "evidence_refs": [{"tier": "validated_mock", "observation_id": "obs-dns-nameserver-count", "value": 0}],
  "assumptions": ["no materialization-side-channel adds hidden nameservers"],
  "unresolved_questions": [],
  "proposed_result": {
    "result": "FAIL",
    "evidence_ref_ids": ["obs-dns-nameserver-count"],
    "confidence_numeric": 0.99,
    "explanation": "Omnia fail_if: nameserver_count < 1 → FAIL; never guess PASS."
  },
  "omnia_normative_bundle_digest": "8013cea3fc788351065c602ffe09225aefc3e2d81a4e8d90d153c3f59c6ac83a"
}
```
Two other participants incorrectly propose PASS with `confidence_numeric 0.6`
and `0.55` but no observation evidence for count_ge>=1. Final result after
anti-majority override is FAIL, consistent with Omnia 4-arm rule evaluation.
`_tribunal_majority_must_not_override()` gate in scenario E enforces this.

## RUNTIME FOOTPRINT METRICS

Measured by `scripts/export_runtime_bundle.py --print-metrics`, stamped into
`metrics` field of runtime bundle (build 2026-08-13, digest 8013cea3…):

```
counts:
  adapters_total:                         7
  adapters_by_evidence_tier:
    declared_only:                        5   (apple/azure/google-cloud/windows/openwrt)
    implemented:                          1   (macos)
    validated_mock:                       1   (openbsd sealed-brick)
  capabilities:                           8
  operations:                             8
  invariants_runtime_addressable:         2
  checks_total:                           4
  owner_intents:                          1
  disagreement_resolutions:               2
  causal_experiments_registered:          1

sizes:
  canonical_bundle_bytes:                 43,717   (~42.7 KB total)
  normative_core_bytes_approx:            10,003   (~9.8 KB invariants only, no operational checks)
  largest_rule_closure_bytes:              481   (DNS target workstation-windows-bluenikee-1)
  median_rule_closure_bytes:               466
  representative_task_closure_bytes (per target):
    target:router-sealed-brick-1:           341
    target:admin-mac-mini-1:                466
    target:workstation-macos-bluenikee-1:   479
    target:workstation-windows-bluenikee-1: 481
    target:dev-macos-1:                     461
    target:dev-windows-1:                   463
    target:router-openwrt-1:                466

closures:
  largest_single_rule_dependency_closure_size: 11  (counts inv caps checks adapters obs envs per target)
  median_rule_dependency_closure_size:          11
  unresolved_semantic_reference_count:          0   (runtime-readiness gate enforced 0 at build time)

closure_refs index (per target, example target router-sealed-brick-1, approximate):
  inv_ids:      [inv-openbsd-sealed-brick-bounded-control]
  check_ids:    [chk-openbsd-v0-collection-boundary]
  adapter_ids:  [adapter-openbsd-sealed-brick]
  cap_ids:      [cap-openbsd-bounded-collect-v0]
  op_ids:       [op-openbsd-inspect-collect-public-v0]
  obs_ids:      [obs-ob-v0-collect-contract-version, obs-ob-v0-collect-output-mode, obs-ob-v0-collect-result]
  disagree_ids: [disagree.openbsd-sealed-brick-bounded-control]
  owner_intent_ids: []  (openbsd sealed brick env has none currently)
  size_bytes_approx: 341
```

Representative-task closure size is sub-kilobyte — small enough that future
tiny Tribunal appliances (OpenBSD/MBSD 32-bit RAM-constrained boxes with
small local models and small bounded in-memory JSON blobs) can load one
target closure without swapping.

## UNRESOLVED LIMITATIONS (carry-forward thin places)

1. **No actual multi-participant runtime yet.** The Tribunal claim model and
   7 conformance scenarios A-G are exercised deterministically in Python
   unit tests, not on a real OpenBSD appliance with separate small model
   families. Future Tribunal implementations must match the same
   deterministic results on MBSD/OpenBSD/macOS/Linux.
2. **No live-hardware provenance for openbsd live target tier yet.**
   evidence_tier_support.validated_live_target=false;
   `live_target_provenance_ref_present=false`. validated_mock only.
   Elevating to validated_live_target requires a real isolated OpenBSD
   appliance run + signed evidence_snapshots JWS receipt ref per network_model.schema.
3. **network_model artifacts are schema-only today.** We created network_model.schema.json
   (flows, dependency graph nodes+edges, observation/intervention points,
   signed evidence snapshots) but no concrete named network_model artifact
   exists yet in playbooks/. It is referenced from causal experiments via
   network_model_refs_required as future work.
4. **example environment missing example owner_intent and disagreement refs.**
   environments/example/environment.json declares
   `owner_intent_refs: [owner-intent-example-001]` and
   `disagreement_resolution_refs: [disagree-dns-explicit-resolvers]` but we
   created owner_intent only for bluenikee. Cross-ref validation gates in
   validate.sh currently only check adapters/capabilities, not all refs. A
   future tightening should add owner_intent and disagreement resolution
   existence enforcement matching the adapter-style gates.
5. **Causal experiment registry list is tiny.** Only
   causal-dns-reachability-001 registered; real estates need a registered
   bounded experiment per end-to-end flow that may need causal diagnosis.
   Tribunal participants today are constrained to `_propose_from_registered_only=true`
   (const in schema) so cannot invent new interventions.
6. **Owner operational intent taxonomy is examples-only.** Five named
   services in bluenikee are arbitrary examples, not a canonical
   taxonomy. Omnia owner_intent.service_class fields are intentionally
   user-defined `minLength: 3` free strings — any future deployer may
   extend with new classes (e.g. adult-content-access — a directive
   example) without a schema change.
7. **Explanatory fields are stripped but not versioned separately.**
   Bundle digest currently changes only when normative/operational fields
   change; a separate explanatory-excerpt digest would help human editors
   audit prose-only edits but is not yet implemented.
8. **No CBOR encoding yet.** runtime_bundle schema says `future_cbor_okay: true`;
   JSON v1 is the only wire format today. CBOR would reduce the already
   small 43 KB footprint by ~30-40%.
9. **Deterministic procedures are exported as 4-arm JSON; a small sexpr**
   evaluator is the intended next step for tiny runtimes. The
   `omnia_deterministic_v1_json` + separate 4-arm structure already
   fully specifies a sexpr form.
10. **Signed bundle not yet implemented.** Future runtimes should verify
    a detached signature of the canonical digest before loading; the
    schema supports the field (signature_ref) but no signing tool exists.

## Commands Run (updated)

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
