#!/usr/bin/env python3
"""Deterministic Omnia v1 runtime-bundle exporter.

Conceptual pipeline (matching directive 2):
  authoritative Omnia sources
    -> validate
    -> resolve references
    -> canonicalize (sort keys, deterministic ordering)
    -> strip explanatory prose
    -> compact runtime knowledge bundle (JSON today; CBOR-safe tomorrow)

Acceptance properties:
  * Same source commit -> same canonical bytes/digest.
  * Changing explanatory prose only SHOULD ideally not change normative digest.
  * Changing normative semantics MUST change the digest.
  * All references resolve mechanically; broken refs -> raise ValidationError.
  * Circular semantic dependencies detected.
  * Computes footprint metrics (sizes, closure fan-out, counts) for the bundle.

Usage:
  export_runtime_bundle.py --root <repo-root> --output <bundle.json> [--print-digest]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set, Tuple

try:
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - CI will install
    print(
        "Missing required Python module: PyYAML. Install requirements-dev.txt or run: pip install PyYAML.",
        file=sys.stderr,
    )
    raise


EVIDENCE_TIER_ORDER: List[str] = [
    "declared_only",
    "implemented",
    "validated_mock",
    "validated_live_target",
]

NORMATIVE_ONLY_FIELDS_BY_TYPE: Dict[str, Set[str]] = {
    "invariant": {
        "rationale", "explanatory_notes",
    },
    "check": set(),
    "adapter": {"notes"},
    "environment": set(),
    "owner_intent": {"notes"},
    "disagreement_resolution": {"explanatory_notes"},
    "causal_experiment": {"explanatory_notes"},
}


@dataclass
class CollectedArtifacts:
    invariants: List[Dict[str, Any]]
    checks: List[Dict[str, Any]]
    adapters: List[Dict[str, Any]]
    environments: List[Dict[str, Any]]
    owner_intents: List[Dict[str, Any]]
    disagreement_resolutions: List[Dict[str, Any]]
    causal_experiments: List[Dict[str, Any]]


class ValidationError(Exception):
    """Raised when semantic closure, ref resolution, or tier elevation fails."""


def load_yaml_or_json(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    if path.suffix in {".yaml", ".yml"}:
        return yaml.safe_load(text)
    return json.loads(text)


def strip_explanatory(obj: Any, artifact_type: str) -> Any:
    """Shallow-strip explanatory fields we've declared non-normative for a given type.

    Deep-scans for top-level keys matching NORMATIVE_ONLY_FIELDS_BY_TYPE[artifact_type].
    Because we remove whole entries, the normative digest remains stable for pure
    explanatory updates. Nested explanatory strings are left alone to keep parser simple;
    truly normative-only updates can come in a future v1.1.
    """
    drop = NORMATIVE_ONLY_FIELDS_BY_TYPE.get(artifact_type, set())
    if isinstance(obj, dict):
        return {k: strip_explanatory(v, artifact_type) for k, v in obj.items() if k not in drop}
    if isinstance(obj, list):
        return [strip_explanatory(i, artifact_type) for i in obj]
    return obj


def collect_artifacts(root: Path) -> CollectedArtifacts:
    invariants, checks, adapters, environments = [], [], [], []
    owner_intents, disagreements, causal_experiments = [], [], []

    checks_dir = root / "checks"
    for path in sorted(checks_dir.rglob("invariant-*.yaml")):
        invariants.append(load_yaml_or_json(path))
    for path in sorted(checks_dir.rglob("chk-*.yaml")):
        checks.append(load_yaml_or_json(path))

    adapters_dir = root / "adapters"
    for path in sorted(adapters_dir.glob("*/adapter.json")):
        adapters.append(json.loads(path.read_text(encoding="utf-8")))

    envs_dir = root / "environments"
    for path in sorted(envs_dir.glob("*/environment.json")):
        environments.append(json.loads(path.read_text(encoding="utf-8")))
    for path in sorted(envs_dir.rglob("owner_intent.*.json")):
        owner_intents.append(json.loads(path.read_text(encoding="utf-8")))
    for path in sorted(envs_dir.rglob("disagree.*.json")):
        disagreements.append(json.loads(path.read_text(encoding="utf-8")))

    playbooks_dir = root / "playbooks"
    for path in sorted(playbooks_dir.rglob("causal-experiment-*.json")):
        causal_experiments.append(json.loads(path.read_text(encoding="utf-8")))

    return CollectedArtifacts(
        invariants=invariants,
        checks=checks,
        adapters=adapters,
        environments=environments,
        owner_intents=owner_intents,
        disagreement_resolutions=disagreements,
        causal_experiments=causal_experiments,
    )


def build_id_indexes(artifacts: CollectedArtifacts) -> Dict[str, Set[str]]:
    indexes: Dict[str, Set[str]] = {
        "invariant_ids": {x["id"] for x in artifacts.invariants},
        "check_ids": {x["id"] for x in artifacts.checks},
        "adapter_ids": {x["id"] for x in artifacts.adapters},
        "environment_ids": {x["id"] for x in artifacts.environments},
        "owner_intent_ids": {x["id"] for x in artifacts.owner_intents},
        "disagreement_ids": {x["id"] for x in artifacts.disagreement_resolutions},
        "causal_ids": {x["id"] for x in artifacts.causal_experiments},
        "capability_ids": set(),
        "operation_ids": set(),
        "observation_ids": set(),
    }
    for a in artifacts.adapters:
        for cap in a.get("declared_capabilities", []):
            indexes["capability_ids"].add(cap["id"])
            indexes["operation_ids"].add(cap.get("operation", ""))
            for obs in cap.get("observation_contract", {}).get("observations", []):
                indexes["observation_ids"].add(obs["id"])
    for inv in artifacts.invariants:
        for obs in inv.get("required_observations", []):
            indexes["observation_ids"].add(obs["id"])
        for cap in inv.get("required_capabilities", []):
            indexes["capability_ids"].add(cap)
    return indexes


def detect_cycles(graph: Dict[str, List[str]], kind: str) -> None:
    """Color-based DFS cycle detection. Raises ValidationError on cycle."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color: Dict[str, int] = {k: WHITE for k in graph}
    for start in graph:
        if color[start] != WHITE:
            continue
        stack: List[Tuple[str, Iterable[str]]] = [(start, iter(graph[start]))]
        color[start] = GRAY
        while stack:
            node, it = stack[-1]
            found_next = False
            for nxt in it:
                if nxt not in graph:
                    continue
                c = color.get(nxt, WHITE)
                if c == GRAY:
                    raise ValidationError(f"Circular {kind} dependency at {nxt} reachable from {start}")
                if c == WHITE:
                    color[nxt] = GRAY
                    stack.append((nxt, iter(graph[nxt])))
                    found_next = True
                    break
            if not found_next:
                color[node] = BLACK
                stack.pop()


def validate_refs_and_tiers(artifacts: CollectedArtifacts, idxs: Dict[str, Set[str]]) -> None:
    broken: List[str] = []
    dep_graph: Dict[str, List[str]] = {inv["id"]: list(inv.get("dependency_ids", [])) for inv in artifacts.invariants}

    # Invariants: required_capabilities; required_observations; check_refs; remediation/source paths.
    for inv in artifacts.invariants:
        for cap in inv.get("required_capabilities", []):
            if cap not in idxs["capability_ids"]:
                broken.append(f"invariant {inv['id']} -> missing capability {cap}")
        for obs in inv.get("required_observations", []):
            oid = obs["id"]
            if oid not in idxs["observation_ids"]:
                broken.append(f"invariant {inv['id']} -> missing observation {oid}")
        for cid in inv.get("check_refs", {}).get("ids", []):
            if cid not in idxs["check_ids"]:
                broken.append(f"invariant {inv['id']} -> missing check_ref {cid}")
        inv_tier_min = inv.get("applicability", {}).get("evidence_tier_minimum")
        inv_platforms = set(inv.get("applicability", {}).get("target_platforms", []) or [])
        if inv_tier_min:
            matching_checks = [c for c in artifacts.checks if c.get("invariant_ref") == inv["id"]]
            for chk in matching_checks:
                claim = chk.get("evidence_tier_claim")
                chk_platform = chk.get("target_platform")
                must_meet_tier = (
                    (not inv_platforms)  # invariant applies to all platforms
                    or (chk_platform and chk_platform in inv_platforms)  # check platform explicitly targeted by inv
                )
                if (
                    must_meet_tier
                    and claim
                    and EVIDENCE_TIER_ORDER.index(claim) < EVIDENCE_TIER_ORDER.index(inv_tier_min)
                ):
                    broken.append(
                        f"invariant {inv['id']} requires evidence_tier_minimum={inv_tier_min} "
                        f"but check {chk['id']} claims evidence_tier={claim}"
                    )
                support = chk.get("evidence_tier_support", {})
                claim_name = chk.get("evidence_tier_claim")
                if claim_name and claim_name not in {"declared_only"} and not support.get(claim_name):
                    broken.append(
                        f"check {chk['id']} evidence_tier_claim={claim_name} not enabled in evidence_tier_support"
                    )
                if claim_name == "validated_live_target" and not support.get("live_target_provenance_ref_present"):
                    broken.append(
                        f"check {chk['id']} claims validated_live_target without live_target_provenance_ref_present"
                    )

    # Checks: invariant_ref; capability_ref.capability_id; adapter_id_hint existence via adapter declared_capability ops match.
    adapter_cap_ids = set()
    for a in artifacts.adapters:
        for c in a.get("declared_capabilities", []):
            adapter_cap_ids.add(c["id"])
    for chk in artifacts.checks:
        if chk.get("invariant_ref") not in idxs["invariant_ids"]:
            broken.append(f"check {chk['id']} -> missing invariant_ref {chk.get('invariant_ref')}")
        cap_ref = chk.get("capability_ref", {}).get("capability_id")
        if cap_ref and cap_ref not in adapter_cap_ids:
            broken.append(f"check {chk['id']} -> missing capability_ref {cap_ref}")
        max_authority = chk.get("authority_ceiling", {}).get("max_authority")
        if max_authority not in {"read_only_evidence", "advisory_remediation_only"}:
            broken.append(f"check {chk['id']} authority_ceiling.max_authority={max_authority} exceeds closed ceilings")
        if not chk.get("authority_ceiling", {}).get("no_policy_invention"):
            broken.append(f"check {chk['id']} missing no_policy_invention=true")
        if not chk.get("authority_ceiling", {}).get("no_authority_promotion"):
            broken.append(f"check {chk['id']} missing no_authority_promotion=true")

    # Environments: estate_targets[*].adapter_id_hint -> adapter_ids exists
    adapter_ids = idxs["adapter_ids"]
    for env in artifacts.environments:
        if not env.get("runtime_host", {}).get("host_substrate_only"):
            broken.append(f"environment {env['id']} runtime_host.host_substrate_only must be true")
        for target in env.get("estate_targets", []):
            adp = target.get("adapter_id_hint")
            if adp and adp not in adapter_ids:
                broken.append(f"environment {env['id']} target {target['target_id']} adapter_id_hint={adp} missing")
            for cap in target.get("capabilities_required", []):
                if cap not in idxs["capability_ids"]:
                    broken.append(f"environment {env['id']} target {target['target_id']} capability_required={cap} missing")
    # Adapters authority ceilings; must declare dumb; never decide truth.
    for a in artifacts.adapters:
        auth = a.get("authority_ceiling", {})
        if auth.get("decides_truth") or auth.get("decides_policy") or auth.get("decides_remediation"):
            broken.append(f"adapter {a['id']} claims policy/truth/remediation authority (dumb adapter doctrine violated)")
        if not auth.get("output_is_typed_untrusted_evidence"):
            broken.append(f"adapter {a['id']} missing output_is_typed_untrusted_evidence=true")

    detect_cycles(dep_graph, "invariant dependency")

    if broken:
        raise ValidationError("\n".join("- " + b for b in broken))


def determine_representative_closure(
    target_id: str,
    target_platform: str,
    artifacts: CollectedArtifacts,
) -> Dict[str, Set[str]]:
    """Given a target id and platform, compute the minimal closure for runtime retrieval."""
    inv_ids: Set[str] = set()
    for inv in artifacts.invariants:
        if target_platform in inv.get("applicability", {}).get("target_platforms", []):
            inv_ids.add(inv["id"])
    cap_ids: Set[str] = set()
    check_ids: Set[str] = set()
    adapter_ids: Set[str] = set()
    operation_ids: Set[str] = set()
    for inv in artifacts.invariants:
        if inv["id"] not in inv_ids:
            continue
        for c in inv.get("required_capabilities", []):
            cap_ids.add(c)
        for cid in inv.get("check_refs", {}).get("ids", []):
            check_ids.add(cid)
    for chk in artifacts.checks:
        if chk["id"] in check_ids:
            cap_ref = chk.get("capability_ref", {}).get("capability_id")
            if cap_ref:
                cap_ids.add(cap_ref)
            adp_hint = chk.get("capability_ref", {}).get("adapter_ref_hint")
            if adp_hint:
                adapter_ids.add(adp_hint)
    for a in artifacts.adapters:
        if a["id"] in adapter_ids:
            for cap in a.get("declared_capabilities", []):
                if cap["id"] in cap_ids:
                    operation_ids.add(cap.get("operation", ""))
    return {
        "target_id": {target_id},
        "invariant_ids": inv_ids,
        "capability_ids": cap_ids,
        "check_ids": check_ids,
        "adapter_ids": adapter_ids,
        "operation_ids": operation_ids,
        "environment_ids": set(),
    }


def build_runtime_bundle(root: Path, artifacts: CollectedArtifacts, idxs: Dict[str, Set[str]]) -> Tuple[Dict[str, Any], str]:
    # 1) strip explanatory for each layer first.
    inv_norm = [strip_explanatory(inv, "invariant") for inv in artifacts.invariants]
    chk_norm = [strip_explanatory(chk, "check") for chk in artifacts.checks]
    adp_norm = [strip_explanatory(a, "adapter") for a in artifacts.adapters]
    env_norm = [strip_explanatory(e, "environment") for e in artifacts.environments]
    own_norm = [strip_explanatory(o, "owner_intent") for o in artifacts.owner_intents]
    dis_norm = [strip_explanatory(d, "disagreement_resolution") for d in artifacts.disagreement_resolutions]
    cau_norm = [strip_explanatory(c, "causal_experiment") for c in artifacts.causal_experiments]

    # 2) Build capabilities/operations flattened registry + deterministic procedure exports.
    capabilities: List[Dict[str, Any]] = []
    operations: List[Dict[str, Any]] = []
    deterministic_procedure_exports: List[Dict[str, Any]] = []
    for a in artifacts.adapters:
        for cap in a.get("declared_capabilities", []):
            capabilities.append({
                "id": cap["id"],
                "version": cap.get("version", "1.0.0"),
                "name": cap.get("name", ""),
                "operation": cap.get("operation", ""),
                "mode": cap.get("mode", ""),
                "support_tier": cap.get("support_tier", ""),
                "status": cap.get("status", ""),
                "evidence_tier": cap.get("evidence_tier", "declared_only"),
                "provenance_refs": cap.get("provenance_refs", []),
                "observation_ids": [o["id"] for o in cap.get("observation_contract", {}).get("observations", [])],
            })
            operations.append({
                "id": cap.get("operation", ""),
                "capability_id": cap["id"],
                "adapter_id_hint": a["id"],
                "command": "",
                "timeout_seconds": 30,
                "observation_schema_refs": [o["id"] for o in cap.get("observation_contract", {}).get("observations", [])],
                "requires": [],
            })
    for inv in artifacts.invariants:
        deterministic_procedure_exports.append({
            "id": "proc-" + inv["decision_rule"]["id"],
            "name": inv["title"],
            "decision_class_ref": inv["id"],
            "invariant_ref": inv["id"],
            "format": "omnia_deterministic_v1_json",
            "encoding": "utf-8",
            "observations_input_refs": [o["id"] for o in inv.get("required_observations", [])],
            "logic_rules": inv.get("decision_rule", {}).get("logic", {}),
            "output_result_schema": {
                "result_enum": ["PASS", "FAIL", "UNKNOWN", "ERROR", "INAPPLICABLE"],
                "result_refs_required": ["evidence_refs", "outcome_semantics"],
            },
            "portable_across_runtimes_must_match_ref_implementation": True,
        })

    # 3) Build compact adapter entries.
    adapters_compact: List[Dict[str, Any]] = []
    for a in adp_norm:
        adapters_compact.append({
            "id": a["id"],
            "version": a.get("version", "1.0.0"),
            "ontology": a.get("ontology", {}),
            "support_tier": a.get("support_tier", ""),
            "status": a.get("status", ""),
            "evidence_tier_highest": a.get("evidence_tier_support", {}).get("highest_tier_for_supported_capability", "declared_only"),
            "primary_platforms": a.get("primary_platforms", []),
            "primary_vendors": a.get("primary_vendors", []),
            "authority_ceiling": a.get("authority_ceiling", {}),
            "capability_ids": [c["id"] for c in a.get("declared_capabilities", [])],
        })

    # 4) Build compact invariants + checks.
    invariants_compact: List[Dict[str, Any]] = []
    for inv in inv_norm:
        invariants_compact.append({
            "id": inv["id"],
            "version": inv["version"],
            "status": inv["status"],
            "severity": inv["severity"],
            "runtime_host_independent": inv["runtime_host_independent"],
            "applicability": inv["applicability"],
            "preconditions": inv["preconditions"],
            "required_observation_ids": [o["id"] for o in inv.get("required_observations", [])],
            "required_capability_ids": list(inv.get("required_capabilities", [])),
            "decision_rule_id": inv["decision_rule"]["id"],
            "decision_rule": inv["decision_rule"],
            "outcomes": inv["outcomes"],
            "evidence_requirements": inv.get("evidence_requirements", {}),
            "remediation_ref": inv.get("remediation_refs", {}).get("playbook", ""),
            "dependency_ids": list(inv.get("dependency_ids", [])),
            "check_ref_ids": list(inv.get("check_refs", {}).get("ids", [])),
            "authority_ceiling": inv["authority_ceiling"],
        })
    checks_compact: List[Dict[str, Any]] = []
    for chk in chk_norm:
        checks_compact.append({
            "id": chk["id"],
            "version": chk.get("version", "1.0.0"),
            "status": chk.get("status", "implemented"),
            "invariant_ref": chk["invariant_ref"],
            "target_platform": chk.get("target_platform", ""),
            "runtime_host_independent": chk.get("runtime_host_independent", True),
            "authority_ceiling": chk.get("authority_ceiling", {}),
            "capability_ref": chk.get("capability_ref", {}),
            "evidence_tier_claim": chk.get("evidence_tier_claim", "declared_only"),
            "evidence_tier_support": chk.get("evidence_tier_support", {}),
            "command": chk.get("command", ""),
            "requires": list(chk.get("requires", [])),
            "timeout_seconds": chk.get("timeout", 30),
            "observation_ids": [o["id"] for o in chk.get("observation_contract", {}).get("observations_emitted", [])],
            "unknown_semantics": chk.get("unknown_semantics", {}),
            "error_semantics": chk.get("error_semantics", {}),
            "remediation_ref": chk.get("remediation_ref", ""),
            "provenance_refs": chk.get("provenance_refs", {}),
        })
    environments_compact: List[Dict[str, Any]] = []
    for env in env_norm:
        environments_compact.append({
            "id": env["id"],
            "version": env.get("version", "1.0.0"),
            "runtime_host": env.get("runtime_host", {}),
            "estate_targets": env.get("estate_targets", []),
        })

    owner_intents_compact: List[Dict[str, Any]] = []
    for oi in own_norm:
        owner_intents_compact.append({
            "id": oi["id"],
            "version": oi.get("version", "1.0.0"),
            "owner_id": oi.get("owner_id", ""),
            "named_service_ids": [s["id"] for s in oi.get("named_services", [])],
            "named_capability_ids": [c["id"] for c in oi.get("named_capabilities", [])],
            "separation_of_concerns": oi.get("separation_of_concerns", {}),
        })

    disagreements_compact: List[Dict[str, Any]] = []
    for d in dis_norm:
        disagreements_compact.append({
            "id": d["id"],
            "decision_class": d.get("decision_class", ""),
            "disagreement_allowed": d.get("disagreement_policy", {}).get("disagreement_allowed", False),
            "resolution_refs": d.get("resolution_evidence", {}),
            "fail_closed": d.get("fail_closed", True),
            "action_under_unresolved": d.get("action_under_unresolved", "HUMAN_ESCALATION_REQUIRED"),
            "convergence": d.get("convergence_criteria", {}),
            "majority_vote_alone_must_not_override": d.get("majority_vote_alone_must_not_override", True),
        })

    causal_compact: List[Dict[str, Any]] = []
    for c in cau_norm:
        causal_compact.append({
            "id": c["id"],
            "hypothesis_ids": [h["id"] for h in c.get("competing_hypotheses", [])],
            "target_flow_ids": [f["flow_id"] for f in c.get("target_flows", [])],
            "baseline_metric_ids": c.get("baseline_metrics", {}).get("required_metric_ids", []),
            "authority_required_level": c.get("authority_required", {}).get("least_privilege_level", "safe_active_probe"),
            "mutation_id": c.get("mutation_spec", {}).get("temporary_mutation_id", ""),
            "blast_radius_max_flows": c.get("blast_radius", {}).get("max_flows_impacted", 0),
            "time_bound_seconds": c.get("time_bound_seconds", 60),
            "rollback_idempotent_command_ref": c.get("rollback_procedure_ref", {}).get("id", ""),
            "commit_condition_id": c.get("commit_condition", {}).get("id", ""),
            "fail_closed_condition_id": c.get("fail_closed_condition", {}).get("id", ""),
            "evidence_receipt_contract_ref": c.get("evidence_receipt_contract", {}).get("id", ""),
            "evidence_method_hierarchy": c.get("evidence_method_hierarchy_used", {}).get("hierarchy_order", []),
            "network_model_refs": c.get("network_model_refs_required", {}),
        })
    # Placeholder network model registry. Future work will serialize full network_model artifacts.
    network_models_compact: List[Dict[str, Any]] = [
        {
            "id": "netmodel-bluenikee-001",
            "operator_intent_ids": [x["id"] for x in owner_intents_compact],
            "flow_ids": [f["flow_id"] for c in cau_norm for f in c.get("target_flows", [])],
            "dependency_graph_id": "depgraph-lan-dns-001",
            "path_ids": ["path-admin-lan-target-to-resolver"],
            "policy_boundary_ids": ["pb-admin-lan-only"],
            "observation_point_ids": sorted(list(idxs["observation_ids"]))[:16],
            "intervention_point_ids": ["ip-dns-lan-safe-probe"],
            "snapshot_before_ids": ["snap-before-dns-001"],
            "snapshot_after_ids": ["snap-after-dns-001"],
            "causal_experiment_ref_ids": [c["id"] for c in causal_compact],
        }
    ]

    tribunal_participant_claim_model: Dict[str, Any] = {
        "claim_required_fields": [
            "claim_id",
            "participant.participant_id",
            "participant.model_identity",
            "participant.provenance_identity",
            "participant.vendor_identity",
            "claim.result",
            "evidence_refs",
            "assumptions",
            "unresolved_questions",
            "proposed_result.result",
            "omnia_normative_bundle_digest",
        ],
        "participant_identity_independent_fields": [
            "participant.participant_id",
            "participant.model_identity",
            "participant.provenance_identity",
            "participant.vendor_identity",
            "participant.architecture_identity",
            "participant.alignment_assumptions",
            "participant.language_support",
        ],
        "no_specific_vendor_lock": True,
        "no_specific_model_lock": True,
        "deterministic_omnia_semantics_owner_is_omnia_not_participant": True,
        "result_must_be_same_across_runtimes_for_deterministic": True,
    }

    # 5) Indexes.
    by_platform: Dict[str, List[str]] = {}
    by_vendor: Dict[str, List[str]] = {}
    by_inv_to_caps: Dict[str, List[str]] = {}
    by_inv_to_checks: Dict[str, List[str]] = {}
    by_cap_to_ops: Dict[str, List[str]] = {}
    by_tier_to_checks: Dict[str, List[str]] = {}
    for inv in artifacts.invariants:
        by_inv_to_caps[inv["id"]] = list(inv.get("required_capabilities", []))
        by_inv_to_checks[inv["id"]] = list(inv.get("check_refs", {}).get("ids", []))
        for plat in inv.get("applicability", {}).get("target_platforms", []):
            by_platform.setdefault(plat, []).append(inv["id"])
        for v in inv.get("applicability", {}).get("target_vendors", []):
            by_vendor.setdefault(v, []).append(inv["id"])
    for op in operations:
        by_cap_to_ops.setdefault(op["capability_id"], []).append(op["id"])
    for chk in checks_compact:
        tier = chk.get("evidence_tier_claim", "declared_only")
        by_tier_to_checks.setdefault(tier, []).append(chk["id"])

    closure_refs: Dict[str, Dict[str, Any]] = {}
    # Representative closures: one from each env estate target.
    for env in artifacts.environments:
        for t in env.get("estate_targets", []):
            closure = determine_representative_closure(t["target_id"], t["platform"], artifacts)
            closure_json = json.dumps({k: sorted(v) for k, v in closure.items()}, sort_keys=True)
            size_bytes_approx = len(closure_json.encode("utf-8"))
            closure_refs[f"target:{t['target_id']}"] = {
                "invariant_ids": sorted(closure["invariant_ids"]),
                "capability_ids": sorted(closure["capability_ids"]),
                "check_ids": sorted(closure["check_ids"]),
                "adapter_ids": sorted(closure["adapter_ids"]),
                "operation_ids": sorted(closure["operation_ids"]),
                "environment_ids": sorted({env["id"]}),
                "size_bytes_approx": size_bytes_approx,
            }

    # 6) Metrics.
    adapters_by_tier: Dict[str, int] = {}
    for a in artifacts.adapters:
        tier = a.get("evidence_tier_support", {}).get("highest_tier_for_supported_capability", "declared_only")
        adapters_by_tier[tier] = adapters_by_tier.get(tier, 0) + 1

    closure_sizes = [c["size_bytes_approx"] for c in closure_refs.values()]
    if closure_sizes:
        largest_closure_bytes = max(closure_sizes)
        median_closure_bytes = sorted(closure_sizes)[len(closure_sizes) // 2]
    else:
        largest_closure_bytes = median_closure_bytes = 0

    largest_closure_count = max((len(c["invariant_ids"]) + len(c["check_ids"]) + len(c["capability_ids"]) + len(c["adapter_ids"]) + len(c["operation_ids"]) for c in closure_refs.values()), default=0)
    median_closure_count = sorted(
        [len(c["invariant_ids"]) + len(c["check_ids"]) + len(c["capability_ids"]) + len(c["adapter_ids"]) + len(c["operation_ids"]) for c in closure_refs.values()]
    )[len(closure_refs) // 2] if closure_refs else 0

    # Pre-determine bundle (before timestamp and digest).
    now_utc = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    try:
        source_commit = os.popen("git -C " + sh_quote(str(root)) + " rev-parse HEAD 2>/dev/null").read().strip() or "unknown-commit"
    except Exception:
        source_commit = "unknown-commit"
    if len(source_commit) < 7:
        source_commit = source_commit + "0" * (7 - len(source_commit))

    bundle_unsigned = {
        "schema_version": "omnia.runtime.v1",
        "generated_at_utc": "DETERMINISTIC_PLACEHOLDER",
        "source_commit": source_commit,
        "canonical_digest_sha256": "DETERMINISTIC_PLACEHOLDER",
        "layer_inclusion": {
            "normative": True,
            "operational": True,
            "explanatory_stripped": True,
        },
        "registry": {
            "invariant_ids": sorted([inv["id"] for inv in invariants_compact]),
            "capability_ids": sorted(list(idxs["capability_ids"])),
            "operation_ids": sorted([op["id"] for op in operations]),
            "check_ids": sorted([chk["id"] for chk in checks_compact]),
            "adapter_ids": sorted([a["id"] for a in adapters_compact]),
            "environment_ids": sorted([e["id"] for e in environments_compact]),
            "owner_intent_ids": sorted([o["id"] for o in owner_intents_compact]),
            "disagreement_resolution_ids": sorted([d["id"] for d in disagreements_compact]),
            "causal_experiment_ids": sorted([c["id"] for c in causal_compact]),
            "network_model_ids": sorted([n["id"] for n in network_models_compact]),
            "deterministic_procedure_ids": sorted([p["id"] for p in deterministic_procedure_exports]),
        },
        "capabilities": sorted(capabilities, key=lambda x: x["id"]),
        "operations": sorted(operations, key=lambda x: (x["id"], x["capability_id"])),
        "adapters": sorted(adapters_compact, key=lambda x: x["id"]),
        "invariants": sorted(invariants_compact, key=lambda x: x["id"]),
        "checks": sorted(checks_compact, key=lambda x: x["id"]),
        "environments": sorted(environments_compact, key=lambda x: x["id"]),
        "owner_intents": sorted(owner_intents_compact, key=lambda x: x["id"]),
        "disagreement_resolutions": sorted(disagreements_compact, key=lambda x: x["id"]),
        "causal_experiments": sorted(causal_compact, key=lambda x: x["id"]),
        "network_models": sorted(network_models_compact, key=lambda x: x["id"]),
        "tribunal_participant_claim_model": tribunal_participant_claim_model,
        "deterministic_procedure_exports": sorted(deterministic_procedure_exports, key=lambda x: x["id"]),
        "multi_interpreter_conformance_refs": {
            "scenario_a_unanimous": "tests/test_multi_interpreter_conformance.py::test_scenario_a_unanimous_correct_result",
            "scenario_b_contradicts_deterministic": "tests/test_multi_interpreter_conformance.py::test_scenario_b_one_contradicts_deterministic",
            "scenario_c_disagree_missing_evidence": "tests/test_multi_interpreter_conformance.py::test_scenario_c_disagree_because_missing_evidence",
            "scenario_d_contradictory_evidence": "tests/test_multi_interpreter_conformance.py::test_scenario_d_contradictory_evidence",
            "scenario_e_majority_wrong_one_identifies": "tests/test_multi_interpreter_conformance.py::test_scenario_e_majority_wrong_one_has_decisive_evidence",
            "scenario_f_resolved_by_one_bounded_obs": "tests/test_multi_interpreter_conformance.py::test_scenario_f_resolved_by_one_bounded_observation",
            "scenario_g_unresolved_fail_closed": "tests/test_multi_interpreter_conformance.py::test_scenario_g_unresolved_fail_closed",
            "majority_count_alone_must_not_override": True,
        },
        "indexes": {
            "by_target_platform_to_invariant_ids": {k: sorted(v) for k, v in by_platform.items()},
            "by_target_vendor_to_invariant_ids": {k: sorted(v) for k, v in by_vendor.items()},
            "by_invariant_to_required_capability_ids": {k: sorted(v) for k, v in by_inv_to_caps.items()},
            "by_invariant_to_check_ids": {k: sorted(v) for k, v in by_inv_to_checks.items()},
            "by_capability_id_to_operation_ids": {k: sorted(v) for k, v in by_cap_to_ops.items()},
            "by_evidence_tier_to_check_ids": {k: sorted(v) for k, v in by_tier_to_checks.items()},
            "closure_refs": {k: closure_refs[k] for k in sorted(closure_refs.keys())},
        },
        "metrics": {
            "counts": {
                "invariants_runtime_addressable": len(invariants_compact),
                "capabilities": len(capabilities),
                "operations": len(operations),
                "adapters_total": len(adapters_compact),
                "adapters_by_evidence_tier": adapters_by_tier,
                "checks_total": len(checks_compact),
            },
            "sizes": {
                "canonical_bundle_bytes": 0,
                "normative_core_bytes_approx": len(json.dumps(invariants_compact + owner_intents_compact + disagreements_compact, sort_keys=True).encode("utf-8")),
                "largest_rule_closure_bytes": largest_closure_bytes,
                "median_rule_closure_bytes": median_closure_bytes,
                "representative_task_closure_bytes": {
                    k: v["size_bytes_approx"] for k, v in closure_refs.items()
                },
            },
            "closures": {
                "largest_single_rule_dependency_closure_size": largest_closure_count,
                "median_rule_dependency_closure_size": median_closure_count,
                "unresolved_semantic_reference_count": 0,
            },
        },
        "execution_contract": {
            "tribunal_prompt_only": (
                "You are an Omnia executor. Never invent policy. Resolve applicable invariant IDs. "
                "Request only required evidence. Treat missing required evidence as UNKNOWN. "
                "Use declared decision rules. Never increase your authority. "
                "Return typed result + evidence references."
            ),
            "never_invent_policy": True,
            "missing_required_evidence_is_unknown": True,
            "use_declared_decision_rules_only": True,
            "never_increase_authority": True,
            "return_typed_result_plus_evidence_refs": True,
            "model_swappability": {
                "no_model_name_dependency": True,
                "no_vendor_lock": True,
            },
        },
    }
    # Compute digest AFTER replacing placeholder timestamp with DETERMINISTIC_PLACEHOLDER
    # so same commit -> same bytes. Then stamp timestamp and digest afterwards.
    canonical_sorted_str = json.dumps(bundle_unsigned, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical_sorted_str.encode("utf-8")).hexdigest()

    # Finalize bundle.
    bundle_unsigned["generated_at_utc"] = now_utc
    bundle_unsigned["canonical_digest_sha256"] = digest
    bundle_unsigned["metrics"]["sizes"]["canonical_bundle_bytes"] = len(json.dumps(bundle_unsigned, sort_keys=True, separators=(",", ":")).encode("utf-8"))

    return bundle_unsigned, digest


def sh_quote(s: str) -> str:
    return "'" + s.replace("'", "'\\''") + "'"


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    ap.add_argument("--output", default=None, help="Path to write runtime bundle JSON.")
    ap.add_argument("--print-digest", action="store_true", help="Print canonical digest SHA256 to stdout.")
    ap.add_argument("--print-metrics", action="store_true", help="Print runtime footprint metrics to stdout.")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    try:
        artifacts = collect_artifacts(root)
        idxs = build_id_indexes(artifacts)
        validate_refs_and_tiers(artifacts, idxs)
        bundle, digest = build_runtime_bundle(root, artifacts, idxs)
    except ValidationError as e:
        print("VALIDATION ERROR (semantic closure failure):\n" + str(e), file=sys.stderr)
        return 2
    except Exception as e:
        print(f"EXPORTER ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        return 3

    serialized = json.dumps(bundle, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(serialized, encoding="utf-8")

    if args.print_digest:
        print(digest)
    if args.print_metrics:
        print(json.dumps(bundle["metrics"], sort_keys=True, indent=2))
    if not args.output and not args.print_digest and not args.print_metrics:
        sys.stdout.write(serialized)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
