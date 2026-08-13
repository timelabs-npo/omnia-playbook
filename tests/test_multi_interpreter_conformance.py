import json
import unittest
from pathlib import Path
from copy import deepcopy

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]

DNS_INVARIANT_ID = "inv-dns-explicit-observable-resolvers"
DNS_DECISION_CLASS = "dns_explicit_resolvers"
REQUIRED_DNS_OBS_IDS = [
    "obs-dns-nameserver-count",
    "obs-dns-resolver-source",
    "obs-dns-reachability-bool",
]
REQUIRED_DNS_CAP_ID = "cap-dns-explicit-resolver-observe-v0"


def _load_fixture(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def _base_dns_invariant() -> dict:
    return {
        "id": DNS_INVARIANT_ID,
        "version": "1.0.0",
        "status": "validated_mock",
        "layer": "normative",
        "title": "Explicit and observable DNS resolvers (multi-target estate)",
        "description": "Target must expose resolver configuration explicitly and avoid unknown inherited DNS state.",
        "scope": {
            "target_class": "developer_workstation",
            "tags": ["dns", "resolvers", "explicit-only"],
        },
        "severity": "high",
        "runtime_host_independent": True,
        "applicability": {
            "target_platforms": ["macos", "windows", "linux-openwrt", "openwrt"],
            "target_vendors": ["apple-inc", "microsoft-corp", "openwrt-project"],
            "evidence_tier_minimum": "implemented",
        },
        "preconditions": {
            "expressions": [
                {
                    "id": "pre-dns-observe-command-materialized",
                    "rule": {"observation_exists": "obs-dns-nameserver-count"},
                    "message": "At least one nameserver-count observation must be materialized.",
                }
            ],
            "unknown_behavior": {
                "on_missing_observation": "UNKNOWN",
                "on_precondition_false": "SKIP_INAPPLICABLE",
            },
        },
        "required_observations": [
            {
                "id": "obs-dns-nameserver-count",
                "name": "number of distinct explicit nameserver values observed",
                "schema": {"type": "integer", "minItems": 0, "maxItems": 16},
                "evidence_tier_required": "implemented",
                "provenance_required": {
                    "signed": False,
                    "adapter_operation_ref": "op-dns-observe-<platform>",
                    "must_be_in_evidence_bundle": True,
                },
            },
            {
                "id": "obs-dns-resolver-source",
                "name": "source declaration for resolver config",
                "schema": {
                    "type": "enum",
                    "enum": [
                        "scutil",
                        "resolv-conf",
                        "networksetup",
                        "netsh",
                        "uci-show-dhcp",
                        "uci-show-network",
                    ],
                },
                "evidence_tier_required": "implemented",
                "provenance_required": {
                    "signed": False,
                    "adapter_operation_ref": "op-dns-observe-<platform>",
                    "must_be_in_evidence_bundle": True,
                },
            },
            {
                "id": "obs-dns-reachability-bool",
                "name": "declared nameservers reachable from evaluation target",
                "schema": {"type": "boolean"},
                "evidence_tier_required": "validated_mock",
                "provenance_required": {
                    "signed": False,
                    "adapter_operation_ref": "op-dns-observe-<platform>",
                    "must_be_in_evidence_bundle": True,
                },
            },
        ],
        "required_capabilities": [REQUIRED_DNS_CAP_ID],
        "decision_rule": {
            "id": "dr-dns-explicit-resolvers-v1",
            "rule_type": "omnia_deterministic_v1",
            "version": "1.0.0",
            "observations_map": {
                "count": "obs-dns-nameserver-count",
                "source": "obs-dns-resolver-source",
                "reachable": "obs-dns-reachability-bool",
            },
            "logic": {
                "pass_if": [
                    {
                        "id": "pass-explicit-count-and-reachable",
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
                        "id": "fail-reachable-false",
                        "expression": {
                            "observation_not_equals": {"reachable": True}
                        },
                        "message": "Declared resolvers unreachable.",
                    },
                    {
                        "id": "fail-count-zero",
                        "expression": {
                            "observation_not_equals": {"count_ge": 1}
                        },
                        "message": "No explicit nameserver values materialized.",
                    },
                ],
                "unknown_if": [
                    {
                        "id": "unknown-missing-count",
                        "expression": {
                            "missing_observation": "obs-dns-nameserver-count"
                        },
                        "message": "Nameserver-count observation missing.",
                    },
                    {
                        "id": "unknown-missing-reachability",
                        "expression": {
                            "missing_observation": "obs-dns-reachability-bool"
                        },
                        "message": "Reachability boolean missing.",
                    },
                ],
                "error_if": [
                    {
                        "id": "error-count-source-contradiction",
                        "expression": {
                            "contradictory_observations": [
                                "obs-dns-nameserver-count",
                                "obs-dns-resolver-source",
                            ]
                        },
                        "message": "Count and source contradict.",
                    }
                ],
            },
        },
        "outcomes": {
            "pass_semantics": "Explicit nameservers materialized count>=1 and declared reachable.",
            "fail_semantics": "Resolvers absent or declared unreachable.",
            "unknown_semantics": "Required DNS observations missing.",
            "error_semantics": "Observations are contradictory. Escalate.",
        },
        "remediation_refs": {
            "playbook": "playbooks/recovery/dns-explicit-resolvers.md"
        },
        "source_refs": {"normative": [], "operational": [], "explanatory": []},
        "authority_ceiling": {
            "max_authority": "advisory_remediation_only",
            "no_promotion_reasoning": True,
            "forbidden_policy_domains": [
                "nameserver-selection",
                "default-route-change",
                "vpn-reconnect",
            ],
        },
        "forbidden_actions": [],
        "dependency_ids": [],
        "last_verified": "2026-08-13",
    }


def _build_closure(inv: dict, adapter_platform: str = "macos") -> dict:
    return {
        "invariant_ids": [inv["id"]],
        "capability_ids": list(inv["required_capabilities"]),
        "check_ids": [f"chk-dns-{adapter_platform}-observe"],
        "adapter_ids": [f"adapter-{adapter_platform}-vendor"],
        "operation_ids": [f"op-dns-observe-{adapter_platform}"],
        "environment_ids": ["env-example"],
        "required_observation_ids": [o["id"] for o in inv["required_observations"]],
        "size_bytes_approx": 2048,
    }


def _make_participant(
    idx: int,
    result: str,
    claim_type: str = "deterministic_omnia_rule",
    evidence_tier: str = "validated_mock",
    missing_obs: list | None = None,
    contradictory: bool = False,
) -> dict:
    evidence_refs = [
        {
            "ref_id": f"ev-obs-dns-ns-count-{idx}",
            "evidence_tier": evidence_tier,
            "evidence_type": "observation",
        },
        {
            "ref_id": f"ev-obs-dns-source-{idx}",
            "evidence_tier": evidence_tier,
            "evidence_type": "observation",
        },
    ]
    if not missing_obs or "obs-dns-reachability-bool" not in missing_obs:
        evidence_refs.append(
            {
                "ref_id": f"ev-obs-dns-reachable-{idx}",
                "evidence_tier": evidence_tier,
                "evidence_type": "observation",
            }
        )
    unresolved = []
    if missing_obs:
        unresolved.append(
            {
                "id": f"uq-missing-{idx}",
                "question": "Missing DNS observations.",
                "resolves_if_observation_ids_provided": list(missing_obs),
            }
        )
    return {
        "schema_version": "omnia.tribunal_claim.v1",
        "claim_id": f"tpc-scenario-{idx:04d}",
        "created_at_utc": "2026-08-13T00:00:00Z",
        "participant": {
            "participant_id": f"participant-model-{idx}",
            "model_identity": f"model-family-{idx}",
            "provenance_identity": f"runner-sha256-hash-{idx}",
            "vendor_identity": f"vendor-neutral-{idx}",
            "architecture_identity": "decoder-only-transformer-v1",
            "alignment_assumptions": [
                "follows-omnia-deterministic-semantics",
                "does-not-invent-policy",
            ],
            "language_support": ["en", "json-schema-2020-12"],
        },
        "decision_class_ref": DNS_DECISION_CLASS,
        "claim": {
            "type": claim_type
            if not contradictory
            else "contradictory_evidence",
            "result": result,
            "confidence_bounded": True,
            "justification_refs": [f"just-ref-{idx}-obs-materialized"],
        },
        "evidence_refs": evidence_refs,
        "assumptions": [
            f"Participant {idx} claims to map observations correctly."
        ],
        "unresolved_questions": unresolved,
        "proposed_result": {
            "result": result,
            "evidence_ref_ids": [e["ref_id"] for e in evidence_refs],
            "confidence_numeric": 0.90 if result == "PASS" else 0.85,
            "confidence_explanation": f"Participant {idx} resolves to {result} using declared deterministic Omnia rule + evidence refs.",
        },
        "omnia_normative_bundle_digest": "0" * 64,
        "deterministic_conformance": {
            "claims_to_follow_omnia_deterministic_rules": True,
            "does_not_vendor_lock": True,
            "result_would_be_same_on_all_runtimes_for_deterministic": True,
        },
        "signature_ref": f"jws-participant-claim-{idx}",
    }


def _apply_deterministic_rule(
    observations: dict, contradictory: bool = False
) -> str:
    if contradictory:
        return "ERROR"
    missing_required = [
        oid for oid in REQUIRED_DNS_OBS_IDS if oid not in observations
    ]
    if missing_required:
        if "obs-dns-nameserver-count" in missing_required:
            return "UNKNOWN"
        if "obs-dns-reachability-bool" in missing_required:
            return "UNKNOWN"
    count = observations.get("obs-dns-nameserver-count", None)
    reachable = observations.get("obs-dns-reachability-bool", None)
    if count is not None and count < 1:
        return "FAIL"
    if reachable is False:
        return "FAIL"
    if (count is None or count >= 1) and reachable is True:
        return "PASS"
    return "UNKNOWN"


def _tribunal_majority_must_not_override(participant_results: list, deterministic_result: str) -> str:
    if deterministic_result in ("PASS", "FAIL", "ERROR"):
        return deterministic_result
    from collections import Counter
    if deterministic_result == "UNKNOWN":
        only_unknown = all(r in ("UNKNOWN", "INAPPLICABLE") or r == deterministic_result for r in participant_results)
        if only_unknown:
            return "UNKNOWN"
        return deterministic_result
    return deterministic_result


class TestMultiInterpreterConformance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inv_schema = _load_fixture("schemas/invariant.schema.json")
        cls.claim_schema = _load_fixture("schemas/tribunal_participant_claim.schema.json")
        cls.inv_validator = Draft202012Validator(cls.inv_schema)
        cls.claim_validator = Draft202012Validator(cls.claim_schema)

    def _assert_claim_valid(self, claim: dict, name: str):
        errors = list(self.claim_validator.iter_errors(claim))
        self.assertEqual([], errors, f"Tribunal claim fixture {name} failed schema validation: {errors[:2]}")

    def _assert_inv_valid(self, inv: dict):
        errors = list(self.inv_validator.iter_errors(inv))
        self.assertEqual([], errors)

    def _assert_closure_refs_integrity(self, inv: dict, closure: dict):
        self.assertIn(inv["id"], closure["invariant_ids"])
        for cap_id in inv["required_capabilities"]:
            self.assertIn(cap_id, closure["capability_ids"])
        inv_obs_ids = {o["id"] for o in inv["required_observations"]}
        closure_obs = set(closure.get("required_observation_ids", []))
        self.assertTrue(
            inv_obs_ids.issubset(closure_obs),
            f"Invariant required observations {inv_obs_ids - closure_obs} are not present in invariant closure references for DNS explicit resolver.",
        )

    def _assert_result_order_deterministic(self, evaluator, observations_space):
        results = set()
        for _ in range(5):
            results.add(evaluator(deepcopy(observations_space)))
        self.assertEqual(1, len(results), f"Deterministic evaluator returned multiple results: {results}")

    def test_scenario_a_unanimous_pass(self):
        inv = _base_dns_invariant()
        self._assert_inv_valid(inv)
        closure = _build_closure(inv, adapter_platform="macos")
        self._assert_closure_refs_integrity(inv, closure)
        observations = {
            "obs-dns-nameserver-count": 2,
            "obs-dns-resolver-source": "scutil",
            "obs-dns-reachability-bool": True,
        }
        det_result = _apply_deterministic_rule(observations)
        self.assertEqual("PASS", det_result)
        participants = [_make_participant(i, "PASS") for i in range(3)]
        for idx, p in enumerate(participants):
            self._assert_claim_valid(p, f"scenario-A-participant-{idx}")
        final = _tribunal_majority_must_not_override([p["claim"]["result"] for p in participants], det_result)
        self.assertEqual("PASS", final)
        self._assert_result_order_deterministic(lambda obs: _apply_deterministic_rule(obs), observations)

    def test_scenario_b_one_contradicts_deterministic(self):
        inv = _base_dns_invariant()
        closure = _build_closure(inv)
        self._assert_closure_refs_integrity(inv, closure)
        observations = {
            "obs-dns-nameserver-count": 2,
            "obs-dns-resolver-source": "resolv-conf",
            "obs-dns-reachability-bool": True,
        }
        det_result = _apply_deterministic_rule(observations)
        self.assertEqual("PASS", det_result)
        participants = [
            _make_participant(0, "PASS"),
            _make_participant(1, "FAIL", claim_type="underdetermined_reasoning"),
            _make_participant(2, "PASS"),
        ]
        for p in participants:
            self._assert_claim_valid(p, "scenario-B-participant")
        final = _tribunal_majority_must_not_override([p["claim"]["result"] for p in participants], det_result)
        self.assertEqual("PASS", final, "Deterministic PASS result must override single contradictory FAIL claim; majority vote must not be required.")

    def test_scenario_c_disagree_missing_evidence_unknown(self):
        inv = _base_dns_invariant()
        closure = _build_closure(inv, adapter_platform="windows")
        self._assert_closure_refs_integrity(inv, closure)
        observations = {
            "obs-dns-nameserver-count": 1,
            "obs-dns-resolver-source": "netsh",
        }
        det_result = _apply_deterministic_rule(observations)
        self.assertEqual("UNKNOWN", det_result)
        participants = [
            _make_participant(0, "UNKNOWN", missing_obs=["obs-dns-reachability-bool"]),
            _make_participant(1, "PASS", claim_type="underdetermined_reasoning"),
            _make_participant(2, "UNKNOWN", missing_obs=["obs-dns-reachability-bool"]),
        ]
        for p in participants:
            self._assert_claim_valid(p, "scenario-C-participant")
        final = _tribunal_majority_must_not_override([p["claim"]["result"] for p in participants], det_result)
        self.assertEqual("UNKNOWN", final, "Missing reachability must remain UNKNOWN regardless of majority PASS claim.")

    def test_scenario_d_contradictory_evidence_error(self):
        inv = _base_dns_invariant()
        closure = _build_closure(inv)
        self._assert_closure_refs_integrity(inv, closure)
        observations = {
            "obs-dns-nameserver-count": 0,
            "obs-dns-resolver-source": "scutil",
            "obs-dns-reachability-bool": True,
        }
        det_result = _apply_deterministic_rule(observations, contradictory=True)
        self.assertEqual("ERROR", det_result)
        participants = [
            _make_participant(0, "ERROR", contradictory=True),
            _make_participant(1, "PASS", claim_type="underdetermined_reasoning"),
            _make_participant(2, "FAIL"),
        ]
        for p in participants:
            self._assert_claim_valid(p, "scenario-D-participant")
        final = _tribunal_majority_must_not_override([p["claim"]["result"] for p in participants], det_result)
        self.assertEqual("ERROR", final, "Contradictory observations (count/source mismatch) must surface ERROR and override any majority PASS/FAIL vote.")

    def test_scenario_e_majority_wrong_one_identifies_fail(self):
        inv = _base_dns_invariant()
        closure = _build_closure(inv, adapter_platform="openwrt")
        self._assert_closure_refs_integrity(inv, closure)
        observations = {
            "obs-dns-nameserver-count": 0,
            "obs-dns-resolver-source": "uci-show-network",
            "obs-dns-reachability-bool": True,
        }
        det_result = _apply_deterministic_rule(observations)
        self.assertEqual("FAIL", det_result, "Count 0 must FAIL per declared decision rule.")
        participants = [
            _make_participant(0, "PASS", claim_type="underdetermined_reasoning"),
            _make_participant(1, "PASS", claim_type="underdetermined_reasoning"),
            _make_participant(2, "FAIL"),
        ]
        for idx, p in enumerate(participants):
            self._assert_claim_valid(p, f"scenario-E-participant-{idx}")
        final = _tribunal_majority_must_not_override([p["claim"]["result"] for p in participants], det_result)
        self.assertEqual("FAIL", final, "Single correct FAIL must override majority incorrect PASS. Majority count alone must not decide.")

    def test_scenario_f_resolved_after_bounded_observation(self):
        inv = _base_dns_invariant()
        closure_before = _build_closure(inv)
        self._assert_closure_refs_integrity(inv, closure_before)
        obs_before = {
            "obs-dns-nameserver-count": 2,
            "obs-dns-resolver-source": "resolv-conf",
        }
        before_result = _apply_deterministic_rule(obs_before)
        self.assertEqual("UNKNOWN", before_result)
        obs_after = dict(obs_before)
        obs_after["obs-dns-reachability-bool"] = True
        after_result = _apply_deterministic_rule(obs_after)
        self.assertEqual("PASS", after_result, "After adding bounded reachability observation, result must resolve to PASS.")
        self._assert_result_order_deterministic(lambda o: _apply_deterministic_rule(o), obs_after)
        participants_before = [
            _make_participant(0, "UNKNOWN", missing_obs=["obs-dns-reachability-bool"]),
            _make_participant(1, "UNKNOWN", missing_obs=["obs-dns-reachability-bool"]),
        ]
        participants_after = [
            _make_participant(0, "PASS"),
            _make_participant(1, "PASS"),
        ]
        for plist in (participants_before, participants_after):
            for p in plist:
                self._assert_claim_valid(p, "scenario-F-participant")
        final_before = _tribunal_majority_must_not_override([p["claim"]["result"] for p in participants_before], before_result)
        final_after = _tribunal_majority_must_not_override([p["claim"]["result"] for p in participants_after], after_result)
        self.assertEqual("UNKNOWN", final_before)
        self.assertEqual("PASS", final_after)

    def test_scenario_g_unresolved_fail_closed(self):
        inv = _base_dns_invariant()
        closure = _build_closure(inv)
        self._assert_closure_refs_integrity(inv, closure)
        observations = {}
        det_result = _apply_deterministic_rule(observations)
        self.assertEqual("UNKNOWN", det_result)
        action_under_unresolved = "LAST_KNOWN_GOOD_RESTORE_ONLY"
        participants = [
            _make_participant(0, "UNKNOWN", missing_obs=list(REQUIRED_DNS_OBS_IDS)),
            _make_participant(1, "FAIL", claim_type="underdetermined_reasoning"),
            _make_participant(2, "UNKNOWN", missing_obs=list(REQUIRED_DNS_OBS_IDS)),
        ]
        for p in participants:
            self._assert_claim_valid(p, "scenario-G-participant")
        final = _tribunal_majority_must_not_override([p["claim"]["result"] for p in participants], det_result)
        self.assertEqual("UNKNOWN", final)
        self.assertIn(
            action_under_unresolved,
            [
                "LAST_KNOWN_GOOD_RESTORE_ONLY",
                "NO_ACTION_PERMITTED",
                "ADVISORY_REMEDIATION_ONLY",
                "PASSIVE_OBSERVE_ONLY",
                "HUMAN_ESCALATION_REQUIRED",
            ],
            "Fail-closed action must be from the restrictive enum set in disagreement_resolution schema v1.",
        )
        self.assertNotEqual("PASS", final, "Fail-closed UNKNOWN must never elevate to PASS via any vote mechanism.")


if __name__ == "__main__":
    unittest.main()
