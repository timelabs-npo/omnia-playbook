#!/usr/bin/env python3
"""Compile a versioned Omnia source manifest into an OMNA ABI 1.0 bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from omnia_bus_codec import compile_bundle, decode_bundle


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--inspect-json", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    manifest = args.manifest if args.manifest.is_absolute() else root / args.manifest
    output = args.output if args.output.is_absolute() else root / args.output
    encoded = compile_bundle(root, manifest)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(encoded)
    if args.inspect_json:
        inspect_path = args.inspect_json if args.inspect_json.is_absolute() else root / args.inspect_json
        inspect_path.parent.mkdir(parents=True, exist_ok=True)
        inspect_path.write_text(json.dumps(decode_bundle(encoded), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{output}: {len(encoded)} bytes sha256={hashlib.sha256(encoded).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
