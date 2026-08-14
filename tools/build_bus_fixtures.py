#!/usr/bin/env python3
"""Rebuild committed positive/negative ABI fixtures and their hash manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from omnia_bus_codec import encode_bundle, load_bundle, mutate_for_negative_fixture


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "bus/fixtures/dns-macos.bundle.json"
OUT = ROOT / "artifacts/omnia-bus-v1"


def main() -> int:
    bundle = load_bundle(ROOT, SOURCE)
    outputs = {"omnia-dns-macos.omnb": encode_bundle(bundle)}
    for case in ("contradictory", "provenance-missing", "boundary", "unsupported-version", "malformed"):
        outputs[f"{case}.omnb"] = mutate_for_negative_fixture(bundle, case)
    OUT.mkdir(parents=True, exist_ok=True)
    for name, data in outputs.items():
        (OUT / name).write_bytes(data)
    entries = [
        {"path": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
        for name, data in sorted(outputs.items())
    ]
    manifest = {
        "schema": "omnia.rheknel.fixture-manifest/v1",
        "abi": "1.0",
        "source_manifest": str(SOURCE.relative_to(ROOT)),
        "source_baseline": "timelabs-npo/omnia-playbook@c9220eee388bba1b4d256d0a6ebd241cf5060102",
        "entries": entries,
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    sums = "".join(f"{entry['sha256']}  {entry['path']}\n" for entry in entries)
    (OUT / "SHA256SUMS").write_text(sums, encoding="ascii")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
