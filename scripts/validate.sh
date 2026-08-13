#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODE="${1:-}"
export ROOT_DIR

usage() {
  cat <<'EOF'
Usage: ./scripts/validate.sh [--links-only|--structure-only|--artifacts-only]

With no option, run the complete repository validation.
  --links-only      Check internal Markdown links only.
  --structure-only  Check the required current repository structure only.
  --artifacts-only  Check repository artifact cross-references and adapter taxonomy rules only.
EOF
}

case "${MODE}" in
  ""|--links-only|--structure-only|--artifacts-only)
    ;;
  -h|--help)
    usage
    exit 0
    ;;
  *)
    echo "Unknown option: ${MODE}" >&2
    usage >&2
    exit 2
    ;;
esac

require_paths() {
  local required=(
    README.md LICENSE CONTRIBUTING.md SECURITY.md Makefile requirements-dev.txt .editorconfig .gitignore
    .github/workflows/validate.yml .github/workflows/docs.yml .github/pull_request_template.md
    foundation/identity.md foundation/networking.md foundation/dns.md foundation/secrets.md foundation/storage.md foundation/observability.md foundation/cicd.md
    adapters/apple adapters/google-cloud adapters/azure adapters/openwrt adapters/macos adapters/windows adapters/openbsd
    adapters/apple/adapter.json adapters/google-cloud/adapter.json adapters/azure/adapter.json
    adapters/openwrt/adapter.json adapters/macos/adapter.json adapters/windows/adapter.json adapters/openbsd/adapter.json
    checks/dns checks/openbsd
    playbooks/bootstrap playbooks/diagnostics playbooks/recovery playbooks/migration playbooks/openbsd-sealed-brick
    schemas/adapter.schema.json schemas/invariant.schema.json schemas/check.schema.json schemas/environment.schema.json schemas/runtime_bundle.schema.json
    schemas/network_model.schema.json schemas/causal_experiment.schema.json schemas/owner_operational_intent.schema.json
    schemas/tribunal_participant_claim.schema.json schemas/disagreement_resolution.schema.json
    environments/example environments/bluenikee environments/openbsd-sealed-brick
    scripts/validate.sh scripts/diagnose.sh scripts/report.sh scripts/export_runtime_bundle.py
    reports/.gitkeep reports/trae-openbsd-sealed-brick.md reports/SEMANTIC_NEIGHBOURS_MATRIX.md reports/REUSE_DECISION_REGISTER.md reports/RECONCILIATION_MAIN_TRAE_CODEX_COPILOT.md
    references/apple references/google references/microsoft references/openbsd
    schemas/deterministic_decision_kernel.schema.json schemas/provider_capability.schema.json
    schemas/evidence_privacy_tier.schema.json schemas/openbsd_support_tier.schema.json schemas/tribunal_advisory_ceiling.schema.json
    docs/adr/ADR-001-concern-separation.md docs/adr/ADR-002-provider-model.md docs/adr/ADR-003-deterministic-decision-boundary.md
    docs/adr/ADR-004-tribunal-advisory-ceiling.md docs/adr/ADR-005-openbsd-platform-policy.md docs/adr/ADR-006-evidence-and-privacy-model.md
    docs/adr/ADR-007-degraded-and-offline-semantics.md docs/adr/ADR-008-cross-cell-boundaries.md docs/adr/ADR-009-blueshoes-representation-handoff.md
    scripts/blueshoes_live_test_runner.sh
  )
  local missing=0
  for item in "${required[@]}"; do
    if [ ! -e "${ROOT_DIR}/${item}" ]; then
      echo "Missing required path: ${item}" >&2
      missing=1
    fi
  done
  if [ "${missing}" -ne 0 ]; then
    return 1
  fi
}

require_command() {
  local command_name="$1"
  local install_hint="$2"
  if ! command -v "${command_name}" >/dev/null 2>&1; then
    echo "Missing required command: ${command_name}. ${install_hint}" >&2
    return 1
  fi
}

require_toolchain() {
  local missing=0

  require_command python3 "Install Python 3.11 or newer." || missing=1
  require_command ruby "Install Ruby with the standard yaml library." || missing=1
  require_command jq "Install jq 1.6 or newer." || missing=1
  require_command shellcheck "Install the dependencies from requirements-dev.txt in the active Python environment." || missing=1

  if command -v python3 >/dev/null 2>&1; then
    if ! python3 -c 'import jsonschema' >/dev/null 2>&1; then
      echo "Missing required Python module: jsonschema. Install the dependencies from requirements-dev.txt." >&2
      missing=1
    fi
  fi

  if command -v ruby >/dev/null 2>&1; then
    if ! ruby -e 'require "yaml"' >/dev/null 2>&1; then
      echo "Ruby is present but its standard yaml library is unavailable." >&2
      missing=1
    fi
  fi

  if [ "${missing}" -ne 0 ]; then
    return 1
  fi
}

validate_yaml_syntax() {
  while IFS= read -r file; do
    ruby -e 'require "yaml"; YAML.safe_load(File.read(ARGV[0]), aliases: false)' "$file" >/dev/null
  done < <(find "${ROOT_DIR}" -type f \( -name '*.yml' -o -name '*.yaml' \) | sort)
}

validate_json_syntax() {
  while IFS= read -r file; do
    jq -e . "$file" >/dev/null
  done < <(find "${ROOT_DIR}" -type f -name '*.json' | sort)
}

validate_schemas_and_fixtures() {
  python3 - <<'PY'
import json
import os
from pathlib import Path
from jsonschema import Draft202012Validator

root = Path(os.environ['ROOT_DIR'])

schema_map = {
    "invariant": root / "schemas/invariant.schema.json",
    "check": root / "schemas/check.schema.json",
    "environment": root / "schemas/environment.schema.json",
    "adapter": root / "schemas/adapter.schema.json",
    "runtime_bundle": root / "schemas/runtime_bundle.schema.json",
    "network_model": root / "schemas/network_model.schema.json",
    "causal_experiment": root / "schemas/causal_experiment.schema.json",
    "owner_intent": root / "schemas/owner_operational_intent.schema.json",
    "tribunal_participant_claim": root / "schemas/tribunal_participant_claim.schema.json",
    "disagreement_resolution": root / "schemas/disagreement_resolution.schema.json",
    "deterministic_decision_kernel": root / "schemas/deterministic_decision_kernel.schema.json",
    "provider_capability": root / "schemas/provider_capability.schema.json",
    "evidence_privacy_tier": root / "schemas/evidence_privacy_tier.schema.json",
    "openbsd_support_tier": root / "schemas/openbsd_support_tier.schema.json",
    "tribunal_advisory_ceiling": root / "schemas/tribunal_advisory_ceiling.schema.json",
}

for name, schema_path in schema_map.items():
    schema = json.loads(schema_path.read_text())
    validator = Draft202012Validator(schema)

    valid_paths = sorted((root / "schemas" / "fixtures" / "valid").glob(f"{name}*.valid.json"))
    invalid_paths = sorted((root / "schemas" / "fixtures" / "invalid").glob(f"{name}*.invalid.json"))

    if not valid_paths:
        raise SystemExit(f"No valid fixtures found for schema: {name}")
    if not invalid_paths:
        raise SystemExit(f"No invalid fixtures found for schema: {name}")

    for valid_path in valid_paths:
        valid_doc = json.loads(valid_path.read_text())
        valid_errors = sorted(validator.iter_errors(valid_doc), key=lambda e: e.path)
        if valid_errors:
            raise SystemExit(f"{valid_path.relative_to(root)} failed schema validation: {valid_errors[0].message}")

    for invalid_path in invalid_paths:
        invalid_doc = json.loads(invalid_path.read_text())
        invalid_errors = sorted(validator.iter_errors(invalid_doc), key=lambda e: e.path)
        if not invalid_errors:
            raise SystemExit(f"{invalid_path.relative_to(root)} unexpectedly passed schema validation")

print("Schema/fixture validation passed")
PY
}

validate_repository_artifacts() {
  python3 - <<'PY'
import json
import os
import subprocess
import sys
from pathlib import Path
from jsonschema import Draft202012Validator

root = Path(os.environ['ROOT_DIR'])


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def load_yaml(path: Path):
    result = subprocess.run(
        [
            "ruby",
            "-e",
            'require "yaml"; require "json"; puts JSON.generate(YAML.safe_load(File.read(ARGV[0]), aliases: false))',
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


EVIDENCE_TIERS = [
    "declared_only",
    "implemented",
    "validated_mock",
    "validated_live_target",
]

schemas = {
    "environment": load_json(root / "schemas/environment.schema.json"),
    "invariant": load_json(root / "schemas/invariant.schema.json"),
    "check": load_json(root / "schemas/check.schema.json"),
    "adapter": load_json(root / "schemas/adapter.schema.json"),
    "runtime_bundle": load_json(root / "schemas/runtime_bundle.schema.json"),
    "network_model": load_json(root / "schemas/network_model.schema.json"),
    "causal_experiment": load_json(root / "schemas/causal_experiment.schema.json"),
    "owner_intent": load_json(root / "schemas/owner_operational_intent.schema.json"),
    "tribunal_claim": load_json(root / "schemas/tribunal_participant_claim.schema.json"),
    "disagreement": load_json(root / "schemas/disagreement_resolution.schema.json"),
}
validators = {k: Draft202012Validator(s) for k, s in schemas.items()}

environment_files = sorted((root / "environments").rglob("environment.json"))
owner_intent_files = sorted((root / "environments").rglob("owner_intent.*.json"))
disagreement_files = sorted((root / "environments").rglob("disagree.*.json"))
invariant_files = sorted((root / "checks").rglob("invariant-*.yaml"))
check_files = sorted((root / "checks").rglob("chk-*.yaml"))
adapter_files = sorted((root / "adapters").rglob("adapter.json"))
causal_files = sorted((root / "playbooks").rglob("causal-experiment-*.json"))
network_model_files = sorted((root / "playbooks").rglob("network-model-*.json"))

for label, files in [
    ("environment", environment_files),
    ("invariant", invariant_files),
    ("check", check_files),
    ("adapter", adapter_files),
]:
    if not files:
        raise SystemExit(f"No {label} files found")

adapter_dirs = sorted({path.parent.name for path in adapter_files})
adapter_dirs_direct = sorted(p.name for p in (root / "adapters").iterdir() if p.is_dir())
for adapter_dir in adapter_dirs_direct:
    if adapter_dir not in adapter_dirs:
        raise SystemExit(f"Adapter directory missing manifest adapter.json: adapters/{adapter_dir}")

adapter_docs: dict = {}
for path in adapter_files:
    doc = load_json(path)
    errors = sorted(validators["adapter"].iter_errors(doc), key=lambda e: e.path)
    if errors:
        raise SystemExit(f"{path.relative_to(root)} failed adapter schema validation: {errors[0].message}")
    manifest_dir = path.parent.name
    if not doc["id"].startswith(f"adapter-{manifest_dir}"):
        raise SystemExit(f"Ambiguous taxonomy: {path.relative_to(root)} id='{doc['id']}' must match directory adapters/{manifest_dir} prefix 'adapter-{manifest_dir}'")
    if doc["id"] in adapter_docs:
        raise SystemExit(f"Duplicate adapter manifest id: {doc['id']}")

    auth = doc.get("authority_ceiling", {})
    if auth.get("decides_truth") or auth.get("decides_policy") or auth.get("decides_remediation"):
        raise SystemExit(f"{path.relative_to(root)} dumb adapter doctrine violated: adapter must not decide truth/policy/remediation")
    if not auth.get("output_is_typed_untrusted_evidence"):
        raise SystemExit(f"{path.relative_to(root)} adapter missing output_is_typed_untrusted_evidence=true")
    if not doc.get("evidence_tier_claims", {}).get("adapter_does_not_decide_truth"):
        raise SystemExit(f"{path.relative_to(root)} adapter missing adapter_does_not_decide_truth=true")
    if not doc.get("evidence_tier_support", {}).get("mock_not_equivalent_to_live"):
        raise SystemExit(f"{path.relative_to(root)} adapter missing mock_not_equivalent_to_live=true")

    declared_cap_ids = {c["id"] for c in doc.get("declared_capabilities", [])}
    valid_status = {"proposed", "implemented", "validated_mock", "validated_live_target", "VALIDATED", "MAPPED"}
    status = doc.get("status", "")
    validated = doc.get("validated_capability_ids", []) or []
    if doc.get("support_tier") == "supported":
        if not validated:
            raise SystemExit(
                f"{path.relative_to(root)} adapter support_tier=supported requires non-empty "
                f"validated_capability_ids (and requires status=VALIDATED or equivalent). "
                f"Ambiguous taxonomy: directory presence alone is never support proof."
            )
        # Status must at least be VALIDATED-equivalent.
        if status not in {"implemented", "validated_mock", "validated_live_target", "VALIDATED", "MAPPED"}:
            raise SystemExit(
                f"{path.relative_to(root)} adapter support_tier=supported requires status=VALIDATED (or "
                f"validated_mock/validated_live_target/implemented/MAPPED). Directory alone is "
                f"insufficient evidence. Got status={status!r}."
            )
    for validated_id in validated:
        if validated_id not in declared_cap_ids:
            raise SystemExit(f"{path.relative_to(root)} validated_capability_ids references undeclared capability {validated_id}")
        cap = next(c for c in doc["declared_capabilities"] if c["id"] == validated_id)
        cap_tier = cap.get("evidence_tier", "declared_only")
        if cap_tier == "declared_only":
            raise SystemExit(f"{path.relative_to(root)} validated_capability_ids requires capability evidence_tier>=implemented, got {cap_tier}")
    adapter_docs[doc["id"]] = (path, doc)

capability_index = {}
for _id, (_, adoc) in adapter_docs.items():
    for cap in adoc.get("declared_capabilities", []):
        capability_index[cap["id"]] = {
            "adapter_id": adoc["id"],
            "evidence_tier": cap.get("evidence_tier", "declared_only"),
            "operation": cap.get("operation", ""),
            "observation_ids": {o["id"] for o in cap.get("observation_contract", {}).get("observations", [])},
        }

observation_index: dict = {}
for cid, meta in capability_index.items():
    for oid in meta["observation_ids"]:
        observation_index.setdefault(oid, []).append(cid)

check_docs: dict = {}
for path in check_files:
    doc = load_yaml(path)
    errors = sorted(validators["check"].iter_errors(doc), key=lambda e: e.path)
    if errors:
        raise SystemExit(f"{path.relative_to(root)} failed check schema validation: {errors[0].message}")
    if doc["id"] in check_docs:
        raise SystemExit(f"Duplicate check id: {doc['id']}")
    check_docs[doc["id"]] = (path, doc)

    ac = doc.get("authority_ceiling", {})
    if not ac.get("no_policy_invention") or not ac.get("no_authority_promotion"):
        raise SystemExit(f"{path.relative_to(root)} check missing no_policy_invention / no_authority_promotion")
    max_auth = ac.get("max_authority")
    if max_auth not in {"read_only_evidence", "advisory_remediation_only"}:
        raise SystemExit(f"{path.relative_to(root)} check max_authority={max_auth} not in allowed closed ceilings")
    claim = doc.get("evidence_tier_claim")
    support = doc.get("evidence_tier_support", {})
    if claim == "validated_live_target" and not support.get("live_target_provenance_ref_present"):
        raise SystemExit(f"{path.relative_to(root)} evidence_tier_claim=validated_live_target requires live_target_provenance_ref_present=true")
    if claim and EVIDENCE_TIERS.index(claim) > EVIDENCE_TIERS.index(next(
        (t for t in reversed(EVIDENCE_TIERS) if support.get(t, False)), "declared_only"
    )):
        raise SystemExit(f"{path.relative_to(root)} evidence_tier_claim={claim} exceeds evidence_tier_support booleans")
    rem = doc.get("remediation_ref")
    if rem:
        rem_path = root / rem
        if not rem_path.exists():
            raise SystemExit(f"{path.relative_to(root)} references missing remediation: {rem}")

invariant_docs: dict = {}
for path in invariant_files:
    doc = load_yaml(path)
    errors = sorted(validators["invariant"].iter_errors(doc), key=lambda e: e.path)
    if errors:
        raise SystemExit(f"{path.relative_to(root)} failed invariant schema validation: {errors[0].message}")
    if doc["id"] in invariant_docs:
        raise SystemExit(f"Duplicate invariant id: {doc['id']}")
    invariant_docs[doc["id"]] = (path, doc)

    for cid in doc.get("required_capabilities", []):
        if cid not in capability_index:
            raise SystemExit(f"{path.relative_to(root)} required_capabilities references undeclared capability {cid}")
    for obs in doc.get("required_observations", []):
        oid = obs["id"]
        if oid not in observation_index:
            raise SystemExit(f"{path.relative_to(root)} required_observation {oid} is not provided by any adapter capability observation_contract")
    inv_min_tier = doc.get("applicability", {}).get("evidence_tier_minimum")
    if inv_min_tier:
        matched = [c for c in check_docs.values() if c[1].get("invariant_ref") == doc["id"]]
        if matched:
            max_claim = max((EVIDENCE_TIERS.index(c[1].get("evidence_tier_claim", "declared_only")) for c in matched), default=-1)
            if max_claim < EVIDENCE_TIERS.index(inv_min_tier):
                raise SystemExit(
                    f"{path.relative_to(root)} evidence_tier_minimum={inv_min_tier} but checks claim at most {EVIDENCE_TIERS[max_claim]}"
                )
    unknown_sem = doc.get("preconditions", {}).get("unknown_behavior")
    if not unknown_sem:
        raise SystemExit(f"{path.relative_to(root)} invariant missing preconditions.unknown_behavior")
    for dep in doc.get("dependency_ids", []):
        if dep not in invariant_docs and dep != doc["id"]:
            pass

for _id, (path, doc) in check_docs.items():
    inv_ref = doc.get("invariant_ref")
    if inv_ref and inv_ref not in invariant_docs:
        raise SystemExit(f"{path.relative_to(root)} references missing invariant_ref {inv_ref}")

for path in owner_intent_files:
    doc = load_json(path)
    errors = sorted(validators["owner_intent"].iter_errors(doc), key=lambda e: e.path)
    if errors:
        raise SystemExit(f"{path.relative_to(root)} failed owner_intent schema: {errors[0].message}")
    if not doc.get("declared_before_failure"):
        raise SystemExit(f"{path.relative_to(root)} owner_intent missing declared_before_failure=true")
    for inv_refs in [s.get("invariant_refs_required_if_fail", []) for s in doc.get("named_services", [])]:
        for inv_id in inv_refs:
            if inv_id not in invariant_docs:
                raise SystemExit(f"{path.relative_to(root)} owner_intent references missing invariant {inv_id}")

for path in disagreement_files:
    doc = load_json(path)
    errors = sorted(validators["disagreement"].iter_errors(doc), key=lambda e: e.path)
    if errors:
        raise SystemExit(f"{path.relative_to(root)} failed disagreement schema: {errors[0].message}")
    if "fail_closed" not in doc:
        raise SystemExit(f"{path.relative_to(root)} disagreement missing fail_closed field")
    if not doc.get("majority_vote_alone_must_not_override"):
        raise SystemExit(f"{path.relative_to(root)} disagreement missing majority_vote_alone_must_not_override=true")
    steps = doc.get("recompute_workflow", [])
    expected_steps = [
        "locate_differing_premise",
        "locate_differing_evidence_interpretation",
        "identify_discriminating_observation",
        "perform_bounded_measurement_if_authorized",
        "recompute_result_from_omnia_rules",
    ]
    if steps != expected_steps:
        raise SystemExit(f"{path.relative_to(root)} disagreement recompute_workflow must equal the required 5 steps exactly")

for path in causal_files:
    doc = load_json(path)
    errors = sorted(validators["causal_experiment"].iter_errors(doc), key=lambda e: e.path)
    if errors:
        raise SystemExit(f"{path.relative_to(root)} failed causal_experiment schema: {errors[0].message}")
    if "time_bound_seconds" not in doc or not isinstance(doc["time_bound_seconds"], int) or doc["time_bound_seconds"] <= 0:
        raise SystemExit(f"{path.relative_to(root)} causal_experiment missing positive time_bound_seconds")
    if not doc.get("evidence_method_hierarchy_used", {}).get("tribunal_must_propose_from_registered_only"):
        raise SystemExit(f"{path.relative_to(root)} causal_experiment must have tribunal_must_propose_from_registered_only=true")
    if not doc.get("fail_closed_condition", {}).get("triggers_immediate_rollback_on_anomalous_impact"):
        raise SystemExit(f"{path.relative_to(root)} causal_experiment fail_closed_condition.triggers_immediate_rollback_on_anomalous_impact required true")
    auth = doc.get("authority_required", {})
    if not auth.get("never_invent_policy") or not auth.get("unvetted_mutation_prohibited"):
        raise SystemExit(f"{path.relative_to(root)} causal_experiment must have never_invent_policy and unvetted_mutation_prohibited both true")
    hierarchy = doc.get("evidence_method_hierarchy_used", {}).get("hierarchy_order", [])
    expected_hierarchy_options = [
        [
            "passive_observational_evidence_no_modification",
            "safe_active_probes_minimal_risk",
            "bounded_fully_reversible_mutations_blast_radius_controlled",
            "controlled_causal_observations_during_approved_experiment",
            "formal_rollback_or_commit_only_upon_completion_or_failure",
        ],
        [
            "passive_observational_evidence_no_modification",
            "safe_active_probes_minimal_risk",
            "bounded_fully_reversible_mutations_blast_radius_contained",
            "controlled_causal_observations_during_approved_experiment",
            "formal_rollback_or_commit_only_upon_completion_or_failure",
        ],
    ]
    if not any(hierarchy == expected for expected in expected_hierarchy_options):
        raise SystemExit(f"{path.relative_to(root)} causal_experiment evidence_method_hierarchy_used must match required 5 tiers")

environment_docs = {}
for path in environment_files:
    doc = load_json(path)
    errors = sorted(validators["environment"].iter_errors(doc), key=lambda e: e.path)
    if errors:
        raise SystemExit(f"{path.relative_to(root)} failed environment schema: {errors[0].message}")
    if not doc.get("runtime_host", {}).get("host_substrate_only"):
        raise SystemExit(f"{path.relative_to(root)} environment missing runtime_host.host_substrate_only=true (target-oriented vs host-substrate rule)")
    for target in doc.get("estate_targets", []):
        adp_id = target.get("adapter_id_hint")
        if adp_id and adp_id not in adapter_docs:
            raise SystemExit(f"{path.relative_to(root)} estate target {target['target_id']} adapter_id_hint={adp_id} not a registered adapter id")
        for cap in target.get("capabilities_required", []):
            if cap not in capability_index:
                raise SystemExit(f"{path.relative_to(root)} estate target {target['target_id']} capability_required={cap} not declared")
    environment_docs[doc["id"]] = (path, doc)

# Run canonical runtime bundle exporter.
exporter_path = root / "scripts" / "export_runtime_bundle.py"
if not exporter_path.exists():
    raise SystemExit(f"Missing exporter script: scripts/export_runtime_bundle.py")
bundle_out = root / "build" / "runtime-bundle" / "omnia.runtime.v1.json"
bundle_out.parent.mkdir(parents=True, exist_ok=True)
res = subprocess.run(
    [
        sys.executable,
        str(exporter_path),
        "--root",
        str(root),
        "--output",
        str(bundle_out),
    ],
    capture_output=True,
    text=True,
)
if res.returncode != 0:
    raise SystemExit(f"Runtime bundle exporter failed (exit {res.returncode}):\n{res.stderr}")

# Validate produced bundle against runtime_bundle.schema.json.
bundle_doc = load_json(bundle_out)
bundle_errors = sorted(validators["runtime_bundle"].iter_errors(bundle_doc), key=lambda e: e.path)
if bundle_errors:
    raise SystemExit(f"Exported runtime bundle failed schema validation: {bundle_errors[0].message}")

# Bundle digest reproducibility: run twice, digests must match.
res2 = subprocess.run(
    [sys.executable, str(exporter_path), "--root", str(root), "--print-digest"],
    capture_output=True,
    text=True,
)
res3 = subprocess.run(
    [sys.executable, str(exporter_path), "--root", str(root), "--print-digest"],
    capture_output=True,
    text=True,
)
if res2.returncode != 0 or res3.returncode != 0:
    raise SystemExit("Runtime bundle digest runs failed: " + res2.stderr + res3.stderr)
if res2.stdout.strip() != res3.stdout.strip():
    raise SystemExit(f"Runtime bundle digest not reproducible between runs: {res2.stdout.strip()} vs {res3.stdout.strip()}")

# Broken reference detection invariants by dependency_ids - no cycles.
from collections import defaultdict, deque
graph = defaultdict(list)
for inv_id, (_, inv_doc) in invariant_docs.items():
    graph[inv_id] = list(inv_doc.get("dependency_ids", []))
color = {k: 0 for k in graph}
WHITE, GRAY, BLACK = 0, 1, 2
for start in list(graph):
    if color[start] != WHITE:
        continue
    stack = [(start, iter(graph[start]))]
    color[start] = GRAY
    while stack:
        node, it = stack[-1]
        found = False
        for nxt in it:
            if nxt not in graph:
                continue
            c = color.get(nxt, WHITE)
            if c == GRAY:
                raise SystemExit(f"Circular semantic dependency in invariants: {nxt} reachable from {start}")
            if c == WHITE:
                color[nxt] = GRAY
                stack.append((nxt, iter(graph[nxt])))
                found = True
                break
        if not found:
            color[node] = BLACK
            stack.pop()

# Runtime readiness: for normative invariants, fail if any required field is prose-only or missing.
for inv_id, (path, inv_doc) in invariant_docs.items():
    layer = inv_doc.get("layer")
    if layer != "normative":
        continue
    required_runtime = [
        "id", "version", "status", "scope", "applicability",
        "preconditions", "required_observations", "required_capabilities",
        "decision_rule", "outcomes",
    ]
    missing = [f for f in required_runtime if not inv_doc.get(f)]
    if missing:
        raise SystemExit(f"{path.relative_to(root)} normative invariant runtime-readiness missing fields: {missing}")
    outcomes = inv_doc.get("outcomes", {})
    has_uppercase = all(k in outcomes for k in ["PASS", "FAIL", "UNKNOWN", "ERROR"])
    has_snake = all(k in outcomes for k in ["pass_semantics", "fail_semantics", "unknown_semantics", "error_semantics"])
    if not (has_uppercase or has_snake):
        raise SystemExit(f"{path.relative_to(root)} normative invariant missing explicit PASS/FAIL/UNKNOWN/ERROR semantics")
    dr = inv_doc.get("decision_rule", {})
    logic = dr.get("logic", {})
    if "unknown_if" not in dr and "unknown_if" not in logic:
        raise SystemExit(f"{path.relative_to(root)} normative invariant missing explicit decision_rule.unknown_if")
    if not inv_doc.get("authority_ceiling"):
        raise SystemExit(f"{path.relative_to(root)} normative invariant missing machine-readable authority_ceiling")

print("Repository artifact validation passed")
print(f"Runtime bundle produced: {bundle_out.relative_to(root)}")
print(f"Canonical digest: {bundle_doc.get('canonical_digest_sha256')}")
PY
}

lint_shell_scripts() {
  while IFS= read -r file; do
    shellcheck -S warning "$file"
  done < <(find "${ROOT_DIR}/scripts" "${ROOT_DIR}/checks" -type f -name '*.sh' | sort)
}

check_internal_markdown_links() {
  python3 - <<'PY'
import os
import re
from pathlib import Path

root = Path(os.environ['ROOT_DIR'])
pattern = re.compile(r'\[[^\]]+\]\(([^)]+)\)')
errors = []

for md_file in root.rglob('*.md'):
    text = md_file.read_text(encoding='utf-8')
    for link in pattern.findall(text):
        if link.startswith(('http://', 'https://', 'mailto:', '#')):
            continue
        target = link.split('#', 1)[0]
        if not target:
            continue
        target_path = (md_file.parent / target).resolve()
        if not target_path.exists():
            errors.append(f"{md_file.relative_to(root)} -> {link}")

if errors:
    raise SystemExit("Broken internal markdown links:\n" + "\n".join(errors))

print("Internal markdown links passed")
PY
}

cd "${ROOT_DIR}"

if [ "${MODE}" = "--links-only" ]; then
  require_command python3 "Install Python 3.11 or newer."
  check_internal_markdown_links
  exit 0
fi

require_paths
if [ "${MODE}" = "--structure-only" ]; then
  echo "Required repository structure passed"
  exit 0
fi

require_toolchain
if [ "${MODE}" = "--artifacts-only" ]; then
  validate_json_syntax
  validate_repository_artifacts
  exit 0
fi

check_internal_markdown_links
validate_yaml_syntax
validate_json_syntax
validate_schemas_and_fixtures
validate_repository_artifacts
lint_shell_scripts
echo "Repository validation passed"
