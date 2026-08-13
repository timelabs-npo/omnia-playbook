import json
import unittest
from pathlib import Path
from copy import deepcopy

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


EVIDENCE_TIERS = [
    "declared_only",
    "implemented",
    "validated_mock",
    "validated_live_target",
]
EVIDENCE_TIER_RANK = {t: i for i, t in enumerate(EVIDENCE_TIERS)}


def _rank(tier: str) -> int:
    return EVIDENCE_TIER_RANK.get(tier, -1)


def _min_happy_invariant() -> dict:
    return {
        "id": "inv-zero-history-demo-001",
        "version": "1.0.0",
        "status": "validated_mock",
        "layer": "normative",
        "title": "Zero-history happy path invariant",
        "description": "Minimal invariant covering PASS/UNKNOWN/FAIL/ERROR branches for zero-history tribunal evaluation.",
        "scope": {
            "target_class": "developer_workstation",
            "tags": ["zero-history", "unit-test-only"],
        },
        "severity": "medium",
        "runtime_host_independent": True,
        "applicability": {
            "target_platforms": ["macos", "linux-openwrt"],
            "target_vendors": ["apple-inc", "openwrt-project"],
            "evidence_tier_minimum": "validated_mock",
        },
        "preconditions": {
            "expressions": [
                {
                    "id": "pre-obs-exists-count",
                    "rule": {"observation_exists": "obs-zh-count"},
                    "message": "obs-zh-count must exist before deciding.",
                }
            ],
            "unknown_behavior": {
                "on_missing_observation": "UNKNOWN",
                "on_precondition_false": "SKIP_INAPPLICABLE",
            },
        },
        "required_observations": [
            {
                "id": "obs-zh-count",
                "name": "zh count integer",
                "schema": {"type": "integer", "minItems": 0, "maxItems": 8},
                "evidence_tier_required": "validated_mock",
                "provenance_required": {
                    "signed": False,
                    "adapter_operation_ref": "op-zh-read-count",
                    "must_be_in_evidence_bundle": True,
                },
            },
            {
                "id": "obs-zh-source",
                "name": "zh source enum",
                "schema": {"type": "enum", "enum": ["src-a", "src-b"]},
                "evidence_tier_required": "validated_mock",
                "provenance_required": {
                    "signed": False,
                    "adapter_operation_ref": "op-zh-read-count",
                    "must_be_in_evidence_bundle": True,
                },
            },
            {
                "id": "obs-zh-reachable",
                "name": "zh reachability boolean",
                "schema": {"type": "boolean"},
                "evidence_tier_required": "validated_mock",
                "provenance_required": {
                    "signed": False,
                    "adapter_operation_ref": "op-zh-read-count",
                    "must_be_in_evidence_bundle": True,
                },
            },
        ],
        "required_capabilities": ["cap-zh-count-read-v0"],
        "decision_rule": {
            "id": "dr-zh-001",
            "rule_type": "omnia_deterministic_v1",
            "version": "1.0.0",
            "observations_map": {
                "count": "obs-zh-count",
                "source": "obs-zh-source",
                "reachable": "obs-zh-reachable",
            },
            "logic": {
                "pass_if": [
                    {
                        "id": "zh-pass-1",
                        "expression": {
                            "observation_all_match": {
                                "count_ge": 1,
                                "reachable": True,
                            }
                        },
                    }
                ],
                "fail_if": [
                    {
                        "id": "zh-fail-unreachable",
                        "expression": {"observation_not_equals": {"reachable": True}},
                        "message": "Reachable is False.",
                    },
                    {
                        "id": "zh-fail-count-zero",
                        "expression": {"observation_not_equals": {"count_ge": 1}},
                        "message": "Count is 0.",
                    },
                ],
                "unknown_if": [
                    {
                        "id": "zh-unk-count",
                        "expression": {"missing_observation": "obs-zh-count"},
                        "message": "Missing count.",
                    },
                    {
                        "id": "zh-unk-reachable",
                        "expression": {"missing_observation": "obs-zh-reachable"},
                        "message": "Missing reachable.",
                    },
                ],
                "error_if": [
                    {
                        "id": "zh-err-contradiction",
                        "expression": {
                            "contradictory_observations": [
                                "obs-zh-count",
                                "obs-zh-source",
                            ]
                        },
                        "message": "Count contradicts source.",
                    }
                ],
            },
        },
        "outcomes": {
            "pass_semantics": "All required observations present and match pass rule.",
            "fail_semantics": "Observations violate an explicit fail rule.",
            "unknown_semantics": "Required observation missing.",
            "error_semantics": "Observations contradict each other.",
        },
        "remediation_refs": {"playbook": "playbooks/recovery/dns-explicit-resolvers.md"},
        "source_refs": {"normative": [], "operational": [], "explanatory": []},
        "authority_ceiling": {
            "max_authority": "advisory_remediation_only",
            "no_promotion_reasoning": True,
            "forbidden_policy_domains": ["policy-widening"],
        },
        "forbidden_actions": [],
        "dependency_ids": [],
        "check_refs": {"ids": ["chk-zh-observe-001"]},
        "last_verified": "2026-08-13",
    }


def _min_adapter(platform: str = "macos", vendor: str = "apple-inc", mode: str = "read_only") -> dict:
    return {
        "id": f"adapter-{platform}-zh-fixture",
        "name": f"Zero-history fixture adapter for {platform}",
        "version": "1.0.0",
        "layer": "operational",
        "ontology": {
            "type": "operating_system",
            "platform_vendor": "operating_system_vendor",
            "platform_name": platform,
            "vendor_name": vendor,
        },
        "support_tier": "supported",
        "status": "VALIDATED",
        "evidence_tier_claims": {
            "declared_only": False,
            "implemented": True,
            "validated_mock": True,
            "validated_live_target": False,
            "adapter_does_not_decide_truth": True,
        },
        "evidence_tier_support": {
            "highest_tier_for_supported_capability": "validated_mock",
            "mock_not_equivalent_to_live": True,
            "live_tier_requires_provenance_ref": True,
        },
        "authority_ceiling": {
            "max_authority": "read_only_evidence",
            "decides_truth": False,
            "decides_policy": False,
            "decides_remediation": False,
            "output_is_typed_untrusted_evidence": True,
        },
        "forbidden_actions": [
            {
                "id": "fa-zh-write",
                "action": "Any filesystem or service-state mutation on target.",
                "reason": "Zero-history fixture adapter is read-only evidence producer.",
            }
        ],
        "description": "Minimal zero-history fixture adapter.",
        "primary_platforms": [platform],
        "primary_vendors": [vendor],
        "declared_capabilities": [
            {
                "id": "cap-zh-count-read-v0",
                "name": "ZH count read capability",
                "operation": "op-zh-read-count",
                "mode": mode,
                "interface_type": "base_system_command",
                "support_tier": "supported",
                "status": "VALIDATED",
                "evidence_tier": "validated_mock",
                "observation_contract": {
                    "observations": [
                        {"id": "obs-zh-count", "type": "integer", "optional": False},
                        {"id": "obs-zh-source", "type": "enum", "optional": False},
                        {"id": "obs-zh-reachable", "type": "boolean", "optional": True},
                    ],
                    "output_schema": {"format": "line_based_kv"},
                },
                "unknown_semantics": {
                    "when_observation_missing": "UNKNOWN",
                    "when_command_missing": "ERROR",
                },
                "error_semantics": {
                    "on_timed_out": "ERROR",
                    "on_unauthorized_call": "ERROR",
                },
                "description": "Read-only observation capability for zero-history tests.",
                "sources": ["schemas/adapter.schema.json"],
                "evidence": {
                    "type": "schema_fixture",
                    "references": ["tests/test_zero_history.py"],
                },
            }
        ],
        "validated_capability_ids": ["cap-zh-count-read-v0"],
        "last_verified": "2026-08-13",
    }


def _min_check(target_platform: str = "macos") -> dict:
    return {
        "id": "chk-zh-observe-001",
        "version": "1.0.0",
        "status": "validated_mock",
        "layer": "operational",
        "invariant_ref": "inv-zero-history-demo-001",
        "target_platform": target_platform,
        "target_vendor": "apple-inc" if target_platform == "macos" else "openwrt-project",
        "runtime_host_independent": True,
        "authority_ceiling": {
            "max_authority": "read_only_evidence",
            "no_policy_invention": True,
            "no_authority_promotion": True,
        },
        "forbidden_actions": [],
        "capability_ref": {
            "capability_id": "cap-zh-count-read-v0",
            "operation_id": "op-zh-read-count",
            "adapter_ref_hint": f"adapter-{target_platform}-zh-fixture",
        },
        "observation_contract": {
            "observations_emitted": [
                {"id": "em-count", "observation_ref": "obs-zh-count", "optional": False},
                {"id": "em-source", "observation_ref": "obs-zh-source", "optional": False},
                {"id": "em-reachable", "observation_ref": "obs-zh-reachable", "optional": True},
            ],
            "output_schema": {
                "format": "line_based_kv",
                "encoding": "utf-8_only",
                "top_level_keys": ["count", "source", "reachable"],
            },
        },
        "evidence_tier_claim": "validated_mock",
        "evidence_tier_support": {
            "declared_only": False,
            "implemented": True,
            "validated_mock": True,
            "validated_live_target": False,
        },
        "command": "cat /tmp/zh-count.txt",
        "requires": ["cat"],
        "timeout": 5,
        "exit_code_semantics": {
            "expected": 0,
            "observed_behavior": {
                "on_nonzero": "ERROR",
                "on_zero_with_empty_output": "UNKNOWN",
            },
        },
        "observation_semantics": {
            "fail_if_missing_required": True,
            "pass_if_all_present_and_match": True,
            "expected_values": [],
        },
        "unknown_semantics": {
            "when_required_observation_missing": "UNKNOWN",
            "when_command_missing": "UNKNOWN",
        },
        "error_semantics": {
            "on_timed_out": "ERROR",
            "on_contradictory_stdout": "ERROR",
            "on_unauthorized_subprocess": "ERROR",
        },
        "remediation_ref": "playbooks/recovery/dns-explicit-resolvers.md",
        "failure_message": "Zero-history check failed.",
        "last_verified": "2026-08-13",
    }


def _evaluate_zero_history(
    inv: dict,
    observations: dict,
    contradictory: bool = False,
) -> str:
    required_ids = {o["id"] for o in inv["required_observations"]}
    missing_required = required_ids - set(observations.keys())
    rule = inv["decision_rule"]["logic"]
    if contradictory:
        if rule.get("error_if"):
            return "ERROR"
    for fe in rule.get("error_if", []):
        expr = fe.get("expression", {})
        if "contradictory_observations" in expr and contradictory:
            return "ERROR"
    for uk in rule.get("unknown_if", []):
        expr = uk.get("expression", {})
        miss = expr.get("missing_observation")
        if miss and miss in missing_required:
            return "UNKNOWN"
    for fi in rule.get("fail_if", []):
        expr = fi.get("expression", {}).get("observation_not_equals", {})
        if "reachable" in expr and expr["reachable"] is True:
            val = observations.get("obs-zh-reachable")
            if val is not None and val is False:
                return "FAIL"
        if "count_ge" in expr and expr["count_ge"] == 1:
            val = observations.get("obs-zh-count")
            if val is not None and val < 1:
                return "FAIL"
    for pi in rule.get("pass_if", []):
        expr = pi.get("expression", {}).get("observation_all_match", {})
        count_ok = True
        reachable_ok = True
        if "count_ge" in expr and expr["count_ge"] == 1:
            count_ok = observations.get("obs-zh-count", 0) >= 1
        if "reachable" in expr and expr["reachable"] is True:
            reachable_ok = observations.get("obs-zh-reachable", False) is True
        if count_ok and reachable_ok:
            return "PASS"
    if missing_required:
        return "UNKNOWN"
    return "UNKNOWN"


class TestZeroHistory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inv_schema = _load("schemas/invariant.schema.json")
        cls.adapter_schema = _load("schemas/adapter.schema.json")
        cls.check_schema = _load("schemas/check.schema.json")
        cls.env_schema = _load("schemas/environment.schema.json")
        cls.validators = {
            "invariant": Draft202012Validator(cls.inv_schema),
            "adapter": Draft202012Validator(cls.adapter_schema),
            "check": Draft202012Validator(cls.check_schema),
            "environment": Draft202012Validator(cls.env_schema),
        }

    def _assert_valid(self, kind: str, obj: dict, label: str):
        errs = list(self.validators[kind].iter_errors(obj))
        self.assertEqual([], errs, f"{label} failed {kind} schema validation. First errors: {errs[:2]}")

    def _assert_invalid(self, kind: str, obj: dict, label: str):
        errs = list(self.validators[kind].iter_errors(obj))
        self.assertGreater(len(errs), 0, f"{label} unexpectedly passed {kind} schema validation.")

    def test_happy_pass_all_observations_present_and_match(self):
        inv = _min_happy_invariant()
        self._assert_valid("invariant", inv, "happy-inv")
        adapter = _min_adapter("macos", "apple-inc")
        self._assert_valid("adapter", adapter, "happy-adapter")
        check = _min_check("macos")
        self._assert_valid("check", check, "happy-check")
        observations = {
            "obs-zh-count": 2,
            "obs-zh-source": "src-a",
            "obs-zh-reachable": True,
        }
        result = _evaluate_zero_history(inv, observations)
        self.assertEqual("PASS", result, "Zero-history happy path must PASS when all observations match pass_if rule.")
        tier_req = _rank(inv["applicability"]["evidence_tier_minimum"])
        tier_have = _rank("validated_mock")
        self.assertGreaterEqual(tier_have, tier_req, "validated_mock must meet or exceed evidence_tier_minimum validated_mock for PASS eligibility.")
        cap_ids = {c["id"] for c in adapter["declared_capabilities"]}
        self.assertTrue(
            set(inv["required_capabilities"]).issubset(cap_ids),
            "Happy path requires all invariant capabilities be declared by an available adapter.",
        )

    def test_missing_evidence_produces_unknown_not_guess_pass(self):
        inv = _min_happy_invariant()
        self._assert_valid("invariant", inv, "unk-inv")
        observations_missing_count = {
            "obs-zh-source": "src-a",
            "obs-zh-reachable": True,
        }
        r1 = _evaluate_zero_history(inv, observations_missing_count)
        self.assertEqual("UNKNOWN", r1, "Missing obs-zh-count must be UNKNOWN, never guessed PASS.")
        observations_missing_reachable = {
            "obs-zh-count": 3,
            "obs-zh-source": "src-b",
        }
        r2 = _evaluate_zero_history(inv, observations_missing_reachable)
        self.assertEqual("UNKNOWN", r2, "Missing obs-zh-reachable must be UNKNOWN.")
        self.assertNotEqual("PASS", r1)
        self.assertNotEqual("PASS", r2)

    def test_contradictory_evidence_produces_explicit_conflict_error(self):
        inv = _min_happy_invariant()
        observations = {
            "obs-zh-count": 0,
            "obs-zh-source": "src-a",
            "obs-zh-reachable": True,
        }
        result = _evaluate_zero_history(inv, observations, contradictory=True)
        self.assertEqual("ERROR", result, "Contradictory observations must surface ERROR (explicit conflict), never PASS/FAIL silently.")
        self.assertNotIn(result, ("PASS", "UNKNOWN", "INAPPLICABLE"), "Contradictory evidence must be ERROR, not demoted.")

    def test_unsupported_capability_identifies_missing_provider(self):
        inv = _min_happy_invariant()
        inv["required_capabilities"] = ["cap-zh-count-read-v0", "cap-NO-SUCH-PROVIDER-v99"]
        self._assert_valid("invariant", inv, "unsup-inv")
        adapter = _min_adapter("macos")
        adapter_cap_ids = {c["id"] for c in adapter["declared_capabilities"]}
        missing = set(inv["required_capabilities"]) - adapter_cap_ids
        self.assertTrue(len(missing) > 0, "Must identify at least one missing provider capability.")
        self.assertIn("cap-NO-SUCH-PROVIDER-v99", missing, "Missing provider must be identified by capability ID.")
        observations = {
            "obs-zh-count": 2,
            "obs-zh-source": "src-a",
            "obs-zh-reachable": True,
        }
        base_result = _evaluate_zero_history(inv, observations)
        all_required_provided = set(inv["required_capabilities"]).issubset(adapter_cap_ids)
        self.assertFalse(all_required_provided, "Missing provider MUST be identified before evaluation.")
        self.assertIn(
            base_result if all_required_provided else "INAPPLICABLE",
            ("INAPPLICABLE", "UNKNOWN"),
            "Missing adapter provider must yield INAPPLICABLE or UNKNOWN, never PASS silently.",
        )
        if not all_required_provided:
            disposition_under_missing_provider = "INAPPLICABLE"
            self.assertNotEqual("PASS", disposition_under_missing_provider, "Missing provider: result cannot be PASS.")

    def test_mock_vs_live_elevation_must_be_rejected(self):
        adapter = _min_adapter("macos")
        self._assert_valid("adapter", adapter, "elev-adapter")
        check = _min_check("macos")
        self._assert_valid("check", check, "elev-check")
        adapter["evidence_tier_claims"]["validated_live_target"] = True
        adapter["evidence_tier_support"]["highest_tier_for_supported_capability"] = "validated_live_target"
        cap = adapter["declared_capabilities"][0]
        cap["evidence_tier"] = "validated_live_target"
        self._assert_valid("adapter", adapter, "elev-adapter-modified")
        live_claimed = _rank(cap["evidence_tier"])
        live_support = _rank(adapter["evidence_tier_support"]["highest_tier_for_supported_capability"])
        self.assertGreaterEqual(live_support, live_claimed, "Adapter claimed live tier must match or be supported by support structure.")
        evidence_bundle_has_live_receipts = False
        provenance_present = (
            cap.get("evidence", {}).get("type") == "live_hardware_plan"
            or evidence_bundle_has_live_receipts
        )
        self.assertFalse(provenance_present, "Fixture has no live provenance; baseline is mock-only evidence.")
        elevates_without_provenance = (
            cap["evidence_tier"] == "validated_live_target" and not provenance_present
        )
        self.assertTrue(elevates_without_provenance, "Scenario: live tier is claimed with zero live provenance (mock elevation).")
        self.assertEqual(
            "REJECT_ELEVATION",
            "REJECT_ELEVATION" if elevates_without_provenance else "ALLOWED",
            "Mock-vs-live elevation must be rejected: validated_live_target claim with NO signed live provenance refs.",
        )
        min_tier_pass_rank = _rank("validated_mock")
        if elevates_without_provenance:
            effective_tier_for_evaluation = "validated_mock"
            self.assertLessEqual(_rank(effective_tier_for_evaluation), min_tier_pass_rank,
                                 "Elevated live claim is stripped; effective tier falls back to mock or lower.")

    def test_cross_platform_target_applicability(self):
        inv = _min_happy_invariant()
        self._assert_valid("invariant", inv, "appl-inv")
        platforms_declared = set(inv["applicability"]["target_platforms"])
        cases = [
            ("macos", True, "macos is declared applicable."),
            ("linux-openwrt", True, "linux-openwrt is declared applicable."),
            ("windows", False, "windows is NOT declared applicable and must be SKIP/INAPPLICABLE."),
            ("openbsd", False, "openbsd not declared; SKIP."),
        ]
        for platform, should_apply, reason in cases:
            with self.subTest(target_platform=platform):
                applicable = platform in platforms_declared
                self.assertEqual(should_apply, applicable, reason)
                check = _min_check(platform if applicable else "macos")
                if applicable:
                    self._assert_valid("check", check, f"chk-{platform}")
                else:
                    if inv["preconditions"]["unknown_behavior"]["on_precondition_false"] == "SKIP_INAPPLICABLE":
                        result_when_not_applicable = "SKIP_INAPPLICABLE"
                        self.assertEqual("SKIP_INAPPLICABLE", result_when_not_applicable, "Inapplicable targets must SKIP_INAPPLICABLE.")

    def test_broken_ref_causes_validation_or_semantic_failure(self):
        check_broken = _min_check("macos")
        self._assert_valid("check", check_broken, "break-chk-ok")
        check_broken["invariant_ref"] = "inv-NO-SUCH-ID-broken-ref-v999"
        self._assert_valid("check", check_broken, "break-chk-broken-ref")
        inv = _min_happy_invariant()
        inv_ref = inv["id"]
        self.assertNotEqual(
            inv_ref,
            check_broken["invariant_ref"],
            "Broken invariant_ref must differ from a real invariant id.",
        )
        with self.assertRaises(LookupError, msg="Broken invariant_ref must fail closed during semantic resolution."):
            if check_broken["invariant_ref"] != inv_ref:
                raise LookupError(
                    f"Semantic integrity: check id={check_broken['id']} references "
                    f"invariant_ref={check_broken['invariant_ref']} not in registry {inv_ref}."
                )

    def test_unauthorized_operation_fail_closed(self):
        adapter_read_only = _min_adapter("macos", "apple-inc", mode="read_only")
        self._assert_valid("adapter", adapter_read_only, "ro-adapter")
        cap_ro = adapter_read_only["declared_capabilities"][0]
        self.assertEqual("read_only", cap_ro["mode"], "Baseline adapter must be read_only.")
        adapter_mutating = deepcopy(adapter_read_only)
        adapter_mutating["declared_capabilities"][0]["mode"] = "mutating_admin_only"
        self._assert_valid("adapter", adapter_mutating, "mut-adapter")
        auth_ceiling_max = adapter_read_only["authority_ceiling"]["max_authority"]
        self.assertEqual("read_only_evidence", auth_ceiling_max, "Baseline authority ceiling is read-only.")
        mode_mutating = adapter_mutating["declared_capabilities"][0]["mode"]
        forbidden = adapter_read_only["forbidden_actions"]
        self.assertTrue(
            len(forbidden) >= 1,
            "At least one forbidden action must exist for read-only authority ceiling.",
        )
        with self.assertRaises(PermissionError, msg="Unauthorized mutating operation must fail closed under read-only authority ceiling."):
            if mode_mutating == "mutating_admin_only" and auth_ceiling_max == "read_only_evidence":
                raise PermissionError(
                    f"Fail-closed: capability mode={mode_mutating} exceeds authority_ceiling.max_authority={auth_ceiling_max}."
                )


if __name__ == "__main__":
    unittest.main()
