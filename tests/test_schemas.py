import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]


class TestSchemaFixtures(unittest.TestCase):
    def _load(self, relative: str):
        return json.loads((ROOT / relative).read_text(encoding="utf-8"))

    def _assert_valid(self, schema_file: str, fixture_file: str):
        schema = self._load(schema_file)
        fixture = self._load(fixture_file)
        errors = list(Draft202012Validator(schema).iter_errors(fixture))
        self.assertEqual([], errors)

    def _assert_invalid(self, schema_file: str, fixture_file: str):
        schema = self._load(schema_file)
        fixture = self._load(fixture_file)
        errors = list(Draft202012Validator(schema).iter_errors(fixture))
        self.assertGreater(len(errors), 0)

    def test_invariant_fixtures(self):
        self._assert_valid("schemas/invariant.schema.json", "schemas/fixtures/valid/invariant.valid.json")
        self._assert_invalid("schemas/invariant.schema.json", "schemas/fixtures/invalid/invariant.invalid.json")

    def test_check_fixtures(self):
        self._assert_valid("schemas/check.schema.json", "schemas/fixtures/valid/check.valid.json")
        self._assert_invalid("schemas/check.schema.json", "schemas/fixtures/invalid/check.invalid.json")

    def test_environment_fixtures(self):
        self._assert_valid("schemas/environment.schema.json", "schemas/fixtures/valid/environment.valid.json")
        self._assert_invalid("schemas/environment.schema.json", "schemas/fixtures/invalid/environment.invalid.json")


if __name__ == "__main__":
    unittest.main()
