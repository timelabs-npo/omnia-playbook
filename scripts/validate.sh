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
    schemas/adapter.schema.json schemas/invariant.schema.json schemas/check.schema.json schemas/environment.schema.json
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

schema_map = {
    "invariant": root / "schemas/invariant.schema.json",
    "check": root / "schemas/check.schema.json",
    "environment": root / "schemas/environment.schema.json",
    "adapter": root / "schemas/adapter.schema.json",
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
adapter_schema = load_json(root / "schemas/adapter.schema.json")

environment_validator = Draft202012Validator(environment_schema)
invariant_validator = Draft202012Validator(invariant_schema)
check_validator = Draft202012Validator(check_schema)
adapter_validator = Draft202012Validator(adapter_schema)

environment_files = sorted((root / "environments").rglob("environment.json"))
invariant_files = sorted((root / "checks").rglob("invariant-*.yaml"))
check_files = sorted((root / "checks").rglob("chk-*.yaml"))
adapter_files = sorted((root / "adapters").rglob("adapter.json"))

if not environment_files:
    raise SystemExit("No environment files found")
if not invariant_files:
    raise SystemExit("No invariant files found")
if not check_files:
    raise SystemExit("No check files found")
if not adapter_files:
    raise SystemExit("No adapter manifest files found")

adapter_dirs = sorted({path.parent.name for path in adapter_files})
adapter_dirs_direct = sorted(p.name for p in (root / "adapters").iterdir() if p.is_dir())
for adapter_dir in adapter_dirs_direct:
    if adapter_dir not in adapter_dirs:
        raise SystemExit(f"Adapter directory missing manifest adapter.json: adapters/{adapter_dir}")

adapter_docs = {}
for path in adapter_files:
    doc = load_json(path)
    errors = sorted(adapter_validator.iter_errors(doc), key=lambda e: e.path)
    if errors:
        raise SystemExit(f"{path.relative_to(root)} failed adapter schema validation: {errors[0].message}")
    adapter_id = path.parent.name
    if doc["id"] in adapter_docs:
        raise SystemExit(f"Duplicate adapter manifest id: {doc['id']}")
    cap_ids = {cap["id"] for cap in doc["declared_capabilities"]}
    for validated_cap_id in doc.get("validated_capability_ids", []):
        if validated_cap_id not in cap_ids:
            raise SystemExit(f"{path.relative_to(root)} validated_capability_ids references undeclared capability: {validated_cap_id}")
        cap = next(cap for cap in doc["declared_capabilities"] if cap["id"] == validated_cap_id)
        if cap["support_tier"] != "supported" or cap["status"] != "VALIDATED":
            raise SystemExit(f"{path.relative_to(root)} capability {validated_cap_id} must be support_tier=supported and status=VALIDATED to be in validated_capability_ids")
        evidence_refs = cap["evidence"]["references"]
        if not evidence_refs:
            raise SystemExit(f"{path.relative_to(root)} capability {validated_cap_id} must have at least one evidence reference")
        for evidence_ref in evidence_refs:
            evidence_path = root / evidence_ref
            if not evidence_path.exists():
                raise SystemExit(f"{path.relative_to(root)} capability {validated_cap_id} references missing evidence: {evidence_ref}")
    if doc["support_tier"] == "supported":
        if doc["status"] != "VALIDATED":
            raise SystemExit(f"{path.relative_to(root)} support_tier=supported requires status=VALIDATED")
        if not doc.get("validated_capability_ids"):
            raise SystemExit(f"{path.relative_to(root)} support_tier=supported requires at least one validated_capability_ids entry")
    else:
        if doc.get("validated_capability_ids"):
            raise SystemExit(f"{path.relative_to(root)} support_tier={doc['support_tier']} must not declare validated_capability_ids")
    adapter_docs[doc["id"]] = (path, adapter_id, doc)

adapter_id_by_dir = {adapter_id: doc_id for (doc_id, (_, adapter_id, _)) in adapter_docs.items()}
for _doc_id, (_path, adapter_id, doc) in adapter_docs.items():
    manifest_dir = _path.parent.name
    expected_ids = [f"adapter-{manifest_dir}", f"adapter-{manifest_dir}-*"]
    matches_prefix = doc["id"].startswith(f"adapter-{manifest_dir}")
    if not matches_prefix:
        raise SystemExit(f"Ambiguous taxonomy: {_path.relative_to(root)} id='{doc['id']}' must match directory adapters/{manifest_dir} prefix 'adapter-{manifest_dir}'")
    status = doc["status"]
    if status == "VALIDATED" and doc["support_tier"] != "supported":
        raise SystemExit(f"Ambiguous taxonomy: {_path.relative_to(root)} status=VALIDATED implies support_tier=supported")
    if status == "UNIMPLEMENTED" and doc["support_tier"] == "supported":
        raise SystemExit(f"Ambiguous taxonomy: {_path.relative_to(root)} UNIMPLEMENTED cannot declare support_tier=supported")

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
        manifest_path = adapter_path / "adapter.json"
        if not manifest_path.exists():
            raise SystemExit(f"{path.relative_to(root)} adapter adapters/{adapter} missing required adapter.json manifest")
        manifest = load_json(manifest_path)
        if manifest["support_tier"] != "supported":
            raise SystemExit(f"{path.relative_to(root)} adapter adapters/{adapter} is not support_tier=supported per adapter.json; environments must not claim unsupported adapters")

print("Repository artifact validation passed")
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
