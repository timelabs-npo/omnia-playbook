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
    adapters/apple adapters/google-cloud adapters/azure adapters/openwrt adapters/macos adapters/windows
    checks/dns
    playbooks/bootstrap playbooks/diagnostics playbooks/recovery playbooks/migration
    schemas/invariant.schema.json schemas/check.schema.json schemas/environment.schema.json schemas/log-event.schema.json schemas/projection-honesty.schema.json
    schemas/sql/catalog.sql schemas/sql/assurance.sql schemas/sql/workflow.sql
    environments/example environments/bluenikee
    scripts/validate.sh scripts/diagnose.sh scripts/report.sh scripts/log0.py
    reports/.gitkeep
    references/apple references/google references/microsoft
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
    "log-event": (root / "schemas/log-event.schema.json", root / "schemas/fixtures/valid/log-event.valid.json", root / "schemas/fixtures/invalid/log-event.invalid.json"),
    "projection-honesty": (root / "schemas/projection-honesty.schema.json", root / "schemas/fixtures/valid/projection-honesty.valid.json", root / "schemas/fixtures/invalid/projection-honesty.invalid.json"),
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
lint_shell_scripts
echo "Repository validation passed"
