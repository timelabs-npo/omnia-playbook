# macOS Adapter

Adapter manifest: [adapter.json](adapter.json)

Status: **VALIDATED** for the declared supported capability only. OS-wide macOS adapter mappings outside the declared capability are explicitly **UNIMPLEMENTED**. Directory existence alone does **not** mark macOS broadly supported.

Ontology (declared in manifest):
- ontology.type: operating_system
- ontology.platform_vendor: operating_system_vendor
- ontology.platform_name: macOS
- ontology.vendor_name: Apple Inc.

Validated capabilities (see manifest):
- `cap-macos-dns-resolver-inspect-v0`: read-only DNS resolver inspection via `scutil --dns` for the DNS explicit resolver invariant.
