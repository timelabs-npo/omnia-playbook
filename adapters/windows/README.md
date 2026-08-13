# Windows Adapter

Adapter manifest: [adapter.json](adapter.json)

Status: **VALIDATED** for the declared supported capability only. Windows adapter mappings outside the declared capability are explicitly **UNIMPLEMENTED**. Directory existence alone does **not** mark Windows broadly supported.

Ontology (declared in manifest):
- ontology.type: operating_system
- ontology.platform_vendor: operating_system_vendor
- ontology.platform_name: Windows
- ontology.vendor_name: Microsoft Corporation

Validated capabilities (see manifest):
- `cap-windows-dns-resolver-inspect-v0`: read-only DNS resolver inspection via PowerShell Get-DnsClientServerAddress for the DNS explicit resolver invariant.
