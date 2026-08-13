# OpenBSD Adapter

Adapter manifest: [adapter.json](adapter.json)

OpenBSD is the substrate. The real interface is the base system itself: `pf`, `pfctl`, `ifconfig`, `route`, `rcctl`, `sysctl`, and the canonical files they manage.

Ontology (declared in manifest):
- ontology.type: operating_system
- ontology.platform_vendor: operating_system_vendor
- ontology.platform_name: OpenBSD
- ontology.vendor_name: OpenBSD Project

Support tier: `supported` for the declared validated capability(s). Directory existence alone does **not** grant support status; see manifest.

## Base interfaces

- packet filter policy: `/etc/pf.conf`, `pf`, `pfctl`
- interface state: `/etc/hostname.if`, `ifconfig`
- default route: `/etc/mygate`, `route`
- service enablement: `/etc/rc.conf.local`, `rcctl`
- kernel networking state: `sysctl`
- resolver state: `/etc/resolv.conf`

## Read-only v0 collection boundary

The v0 collection boundary is intentionally small and bounded. It is limited to allowlisted, read-only observations:

- `uname -srm`
- `ifconfig -A`
- `route -n show`
- `pfctl -s info`
- `pfctl -sr`
- `pfctl -sn`
- `rcctl ls on`
- `sysctl net.inet.ip.forwarding`
- `cat /etc/resolv.conf`

Public collection must emit minimized posture booleans and counts only. It must not emit IPs, MACs, interface names, route bodies, rule bodies, resolver addresses, search domains, or hostnames.

Raw native state is reserved for the explicit `--inspect-private` operator path, which must begin with:

- `LOCAL SENSITIVE OUTPUT`
- `DO NOT UPLOAD OR APPEND TO LOG.0`

The v0 boundary does not mutate `pf`, does not write configuration, does not widen policy, does not restart services, and does not grant shell-mediated authority to advisory workers.

See the architecture and rollback procedure in [playbooks/openbsd-sealed-brick/README.md](../../playbooks/openbsd-sealed-brick/README.md).
