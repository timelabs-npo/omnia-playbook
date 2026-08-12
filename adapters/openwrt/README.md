# OpenWrt Adapter

Adapter manifest: [adapter.json](adapter.json)

Status: **VALIDATED** for the declared supported capability only. OpenWrt mappings outside the declared capability are explicitly **UNIMPLEMENTED**. Directory existence alone does **not** mark OpenWrt broadly supported.

Ontology (declared in manifest):
- ontology.type: device_operating_system
- ontology.platform_vendor: operating_system_vendor
- ontology.platform_name: OpenWrt
- ontology.vendor_name: OpenWrt Project

Validated capabilities (see manifest):
- `cap-openwrt-dns-resolver-inspect-v0`: read-only DNS resolver inspection via `/etc/resolv.conf` for Linux/OpenWrt targets in the DNS explicit resolver invariant.
