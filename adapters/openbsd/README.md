# OpenBSD Adapter

OpenBSD is the substrate. The real interface is the base system itself: `pf`, `pfctl`, `ifconfig`, `route`, `rcctl`, `sysctl`, and the canonical files they manage.

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

The v0 boundary does not mutate `pf`, does not write configuration, does not widen policy, does not restart services, and does not grant shell-mediated authority to advisory workers.

See the architecture and rollback procedure in [playbooks/openbsd-sealed-brick/README.md](../../playbooks/openbsd-sealed-brick/README.md).
