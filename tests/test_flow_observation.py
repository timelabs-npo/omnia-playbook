"""Independent semantic checks; deliberately no Blueshoes implementation imports."""
import hashlib
import json
import unittest
from datetime import datetime
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / 'schemas/fixtures/flow'
KINDS = dict(darwin='darwin_start_us', win32='win32_creation_100ns',
             linux='linux_start_ticks', openbsd='openbsd_start_us')


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key')
        result[key] = value
    return result


def load(path):
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique_keys)


def lf_bytes(path):
    return path.read_text(encoding='utf-8').replace('\r\n', '\n').encode()


class FlowContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # jsonschema silently skips date-time when its optional checker is absent.
        if 'date-time' not in FormatChecker().checkers:
            raise RuntimeError('Install rfc3339-validator==0.1.4; date-time checking is mandatory')
        cls.manifest = load(CORPUS / 'manifest.json')
        cls.schemas = {kind: load(ROOT / 'schemas' / name) for kind, name in
                       [('native', 'native-flow-sample.schema.json'),
                        ('observation', 'flow-observation.schema.json')]}
        registry = Registry().with_resources((s['$id'], Resource.from_contents(s))
                                             for s in cls.schemas.values())
        cls.validators = {k: Draft202012Validator(v, registry=registry,
                             format_checker=FormatChecker()) for k, v in cls.schemas.items()}

    def test_corpus_integrity_and_scope(self):
        self.assertEqual(45, len(self.manifest['cases']))
        self.assertEqual({'NOT_EXECUTED'}, set(self.manifest['native_gates'].values()))
        self.assertEqual(self.manifest['schema_sha256'], hashlib.sha256(
            lf_bytes(ROOT / 'schemas/flow-observation.schema.json')).hexdigest())
        for case in self.manifest['cases']:
            with self.subTest(case=case['id']):
                self.assertEqual(case['sha256'], hashlib.sha256(lf_bytes(CORPUS / case['path'])).hexdigest())

    def test_independent_schema_and_semantic_expectations(self):
        for case in self.manifest['cases']:
            with self.subTest(case=case['id']):
                try:
                    doc = load(CORPUS / case['path'])
                except ValueError:
                    self.assertFalse(case['accepted'])
                    continue
                errors = list(self.validators[case['kind']].iter_errors(doc))
                if case['schema_valid'] is not None:
                    self.assertEqual(case['schema_valid'], not errors)
                accepted = not errors
                if accepted:
                    records = doc['records'] if case['kind'] == 'native' else [doc]
                    if case['kind'] == 'native':
                        accepted = len({r['record_id'] for r in records}) == len(records)
                    for rec in records:
                        if any(v is not None and v > 2**64 - 1 for v in rec['counters'].values()):
                            accepted = False
                        proc = rec.get('process')
                        if proc and proc['kind'] != KINDS[doc['platform']]:
                            accepted = False
                self.assertEqual(case['accepted'], accepted)
                if not accepted or case['kind'] != 'native':
                    continue
                rec = doc['records'][0]
                expected = case['expected']
                proc = rec.get('process')
                bound = bool(proc and proc['pid'] and proc['birth_before']
                             and proc['birth_before'] == proc['birth_after'])
                if 'process_bound' in expected:
                    self.assertEqual(expected['process_bound'], bound)
                age = (datetime.fromisoformat(self.manifest['now']) - datetime.fromisoformat(doc['observed_at'])).total_seconds() * 1000
                freshness = doc['freshness']
                if freshness != 'stale':
                    if age < 0:
                        freshness = 'unknown'
                    elif age > self.manifest['max_age_ms']:
                        freshness = 'stale'
                if 'freshness' in expected:
                    self.assertEqual(expected['freshness'], freshness)
                for key in ('bytes_up', 'bytes_down'):
                    if key in expected:
                        self.assertEqual(expected[key], rec['counters'][key])
                if 'destination_address' in expected:
                    self.assertEqual(expected['destination_address'], rec['destination']['address'])
                if 'display_mode' in expected:
                    self.assertEqual(expected['display_mode'], rec['display_location']['mode'])

    def test_equivalent_platform_data_and_identity_separation(self):
        docs = [load(CORPUS / ('equivalent-' + p + '.json')) for p in KINDS]
        baseline = docs[0]['records'][0]
        for doc in docs[1:]:
            rec = doc['records'][0]
            for key in ('source', 'destination', 'protocol', 'counters', 'policy', 'route', 'display_location'):
                self.assertEqual(baseline[key], rec[key])
            self.assertEqual(baseline['process']['pid'], rec['process']['pid'])
            self.assertEqual(baseline['process']['birth_before'], rec['process']['birth_before'])
        original = load(CORPUS / 'equivalent-win32.json')
        reused = load(CORPUS / 'pid-reused-new-birth.json')
        self.assertEqual(original['records'][0]['process']['pid'], reused['records'][0]['process']['pid'])
        self.assertNotEqual(original['records'][0]['process']['birth_before'], reused['records'][0]['process']['birth_before'])
        self.assertNotEqual(original['snapshot_id'], load(CORPUS / 'tuple-reuse.json')['snapshot_id'])

    def test_nullable_counter_compatibility_direction(self):
        revised = self.schemas['observation']
        original = json.loads(json.dumps(revised))
        for key in ('bytes_up', 'bytes_down'):
            original['properties']['counters']['properties'][key]['type'] = 'integer'
        old = Draft202012Validator(original, format_checker=FormatChecker())
        self.assertTrue(old.is_valid(load(CORPUS / 'wire-valid.json')))
        self.assertFalse(old.is_valid(load(CORPUS / 'wire-null-counters.json')))
        self.assertTrue(self.validators['observation'].is_valid(load(CORPUS / 'wire-null-counters.json')))


if __name__ == '__main__':
    unittest.main()
