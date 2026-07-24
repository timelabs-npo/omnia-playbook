#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODE="${1:-}"
export ROOT_DIR

usage() {
  cat <<'EOF'
Usage: ./scripts/validate.sh [--links-only|--structure-only]

With no option, run the complete repository validation.
  --links-only      Check internal Markdown links only.
  --structure-only  Check the required current repository structure only.
EOF
}

case "${MODE}" in
  ""|--links-only|--structure-only)
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
    checks/dns checks/openbsd
    playbooks/bootstrap playbooks/diagnostics playbooks/recovery playbooks/migration playbooks/openbsd-sealed-brick
    schemas/invariant.schema.json schemas/check.schema.json schemas/environment.schema.json
    environments/example environments/bluenikee environments/openbsd-sealed-brick
    scripts/validate.sh scripts/diagnose.sh scripts/report.sh
    reports/.gitkeep reports/trae-openbsd-sealed-brick.md
    references/apple references/google references/microsoft references/openbsd
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

mapping = {
    "invariant": (root / "schemas/invariant.schema.json", root / "schemas/fixtures/valid/invariant.valid.json", root / "schemas/fixtures/invalid/invariant.invalid.json"),
    "check": (root / "schemas/check.schema.json", root / "schemas/fixtures/valid/check.valid.json", root / "schemas/fixtures/invalid/check.invalid.json"),
    "environment": (root / "schemas/environment.schema.json", root / "schemas/fixtures/valid/environment.valid.json", root / "schemas/fixtures/invalid/environment.invalid.json"),
}

for name, (schema_path, valid_path, invalid_path) in mapping.items():
    schema = json.loads(schema_path.read_text())
    validator = Draft202012Validator(schema)

    valid_doc = json.loads(valid_path.read_text())
    valid_errors = sorted(validator.iter_errors(valid_doc), key=lambda e: e.path)
    if valid_errors:
        raise SystemExit(f"{name} valid fixture failed schema validation: {valid_errors[0].message}")

    invalid_doc = json.loads(invalid_path.read_text())
    invalid_errors = sorted(validator.iter_errors(invalid_doc), key=lambda e: e.path)
    if not invalid_errors:
        raise SystemExit(f"{name} invalid fixture unexpectedly passed schema validation")

print("Schema/fixture validation passed")
PY
}

validate_repository_artifacts() {
  python3 - <<'PY'
import json
import os
import subprocess
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


environment_schema = load_json(root / "schemas/environment.schema.json")
invariant_schema = load_json(root / "schemas/invariant.schema.json")
check_schema = load_json(root / "schemas/check.schema.json")

environment_validator = Draft202012Validator(environment_schema)
invariant_validator = Draft202012Validator(invariant_schema)
check_validator = Draft202012Validator(check_schema)

environment_files = sorted((root / "environments").rglob("environment.json"))
invariant_files = sorted((root / "checks").rglob("invariant-*.yaml"))
check_files = sorted((root / "checks").rglob("chk-*.yaml"))

if not environment_files:
    raise SystemExit("No environment files found")
if not invariant_files:
    raise SystemExit("No invariant files found")
if not check_files:
    raise SystemExit("No check files found")

check_docs = {}
for path in check_files:
    doc = load_yaml(path)
    errors = sorted(check_validator.iter_errors(doc), key=lambda e: e.path)
    if errors:
        raise SystemExit(f"{path.relative_to(root)} failed schema validation: {errors[0].message}")
    if doc["id"] in check_docs:
        raise SystemExit(f"Duplicate check id: {doc['id']}")
    check_docs[doc["id"]] = (path, doc)
    remediation_path = root / doc["remediation_playbook"]
    if not remediation_path.exists():
        raise SystemExit(f"{path.relative_to(root)} references missing remediation playbook: {doc['remediation_playbook']}")

invariant_docs = {}
for path in invariant_files:
    doc = load_yaml(path)
    errors = sorted(invariant_validator.iter_errors(doc), key=lambda e: e.path)
    if errors:
        raise SystemExit(f"{path.relative_to(root)} failed schema validation: {errors[0].message}")
    if doc["id"] in invariant_docs:
        raise SystemExit(f"Duplicate invariant id: {doc['id']}")
    invariant_docs[doc["id"]] = (path, doc)
    remediation_path = root / doc["remediation"]["playbook"]
    if not remediation_path.exists():
        raise SystemExit(f"{path.relative_to(root)} references missing remediation playbook: {doc['remediation']['playbook']}")
    for source in doc["sources"]:
        source_path = root / source
        if not source_path.exists():
            raise SystemExit(f"{path.relative_to(root)} references missing source: {source}")
    for check_id in doc["check"]["ids"]:
        if check_id not in check_docs:
            raise SystemExit(f"{path.relative_to(root)} references missing check id: {check_id}")

for path, doc in check_docs.values():
    if doc["invariant"] not in invariant_docs:
        raise SystemExit(f"{path.relative_to(root)} references missing invariant id: {doc['invariant']}")

for path in environment_files:
    doc = load_json(path)
    errors = sorted(environment_validator.iter_errors(doc), key=lambda e: e.path)
    if errors:
        raise SystemExit(f"{path.relative_to(root)} failed schema validation: {errors[0].message}")
    for adapter in doc["adapters"]:
        adapter_path = root / "adapters" / adapter
        if not adapter_path.exists():
            raise SystemExit(f"{path.relative_to(root)} references missing adapter directory: adapters/{adapter}")

print("Repository artifact validation passed")
PY
}

lint_shell_scripts() {
  while IFS= read -r file; do
    shellcheck "$file"
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
check_internal_markdown_links
validate_yaml_syntax
validate_json_syntax
validate_schemas_and_fixtures
validate_repository_artifacts
lint_shell_scripts
echo "Repository validation passed"
