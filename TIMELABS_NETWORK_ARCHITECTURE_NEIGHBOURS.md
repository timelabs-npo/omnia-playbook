# TIMELABS_NETWORK_ARCHITECTURE_NEIGHBOURS

## SYSTEM → PRIMITIVE → CAPABILITY decomposition snapshots

### SCION
- **Primitive:** ISD trust-root partitioning
  - **Capability:** isolate trust domains and reduce global PKI blast radius.
- **Primitive:** path-aware forwarding
  - **Capability:** explicit selectable/inspectable paths with multipath failover.
- **Primitive:** cryptographic control-plane artifacts
  - **Capability:** stronger route authenticity checks than baseline BGP.

### HIP / HIPv2
- **Primitive:** cryptographic host identity (HIT)
  - **Capability:** session continuity across locator changes.
- **Primitive:** identity-locator decoupling
  - **Capability:** mobility and multihoming without transport teardown.

### LISP / ILNP
- **Primitive:** ID/locator split with mapping system
  - **Capability:** scalable locator changes and overlay mobility.
- **Primitive:** mapping indirection
  - **Capability:** policy-mediated reachability and endpoint move support.

### NDN / CCNx
- **Primitive:** name-based routing
  - **Capability:** content retrieval without endpoint coupling.
- **Primitive:** in-network caching
  - **Capability:** resilience and latency improvements under disruption.

### libp2p / Kademlia
- **Primitive:** decentralized peer discovery and rendezvous
  - **Capability:** bootstrap and route around central DNS assumptions.
- **Primitive:** transport abstraction
  - **Capability:** QUIC/TCP/noise-based communication portability.

### Yggdrasil / cjdns
- **Primitive:** key-derived addressing
  - **Capability:** cryptographic identity tied to overlay address space.
- **Primitive:** encrypted mesh forwarding
  - **Capability:** censorship/interference-resistant peer paths.

### WireGuard / Tailscale / ZeroTier / Nebula
- **Primitive:** identity-bound encrypted overlay tunnels
  - **Capability:** secure cross-NAT connectivity.
- **Primitive:** control-plane policy + device identity
  - **Capability:** service identity, ACL enforcement, reachability orchestration.

### mDNS / DNS-SD / SVCB+HTTPS RRs
- **Primitive:** service-centric naming/discovery
  - **Capability:** endpoint indirection and local/global service bootstrap.

### ICE/STUN/TURN + QUIC migration + MPTCP + MP-QUIC
- **Primitive:** path probing + candidate pairing
  - **Capability:** NAT traversal and rendezvous.
- **Primitive:** connection identifier migration
  - **Capability:** mobility without application session reset.
- **Primitive:** multipath scheduling
  - **Capability:** load balancing and failover continuity.

### MASQUE / CONNECT-UDP / CONNECT-IP
- **Primitive:** HTTP/3 proxy tunnel substrate
  - **Capability:** deployable UDP/IP mediation through existing HTTPS infrastructure.

### OpenBSD manipulation alphabet mapping
- OBSERVE: `ifconfig`, `route -n show`, `pfctl -s info`, `sysctl`, BPF/pcap.
- CLASSIFY: PF tables/tags/labels/anchors.
- DECIDE: PF rule ordering + tables + route selection + `rtable`/`rdomain`.
- STEER: `route-to`, `reply-to`, policy routes, route sockets.
- TRANSFORM: `nat-to`, `rdr-to`, normalization.
- INTERCEPT: `divert-to`, `divert-reply`, relayd patterns.
- PROXY/TUNNEL: userspace proxies, `iked`/IPsec, WireGuard support, tun/tap.
- MUTATE: constrained by explicit operator gates and rollback procedures.
- SYNCHRONIZE: `pfsync` + `CARP` for HA state continuity.
- FAILOVER: `CARP` role transfer, alternate routes, bounded health checks.
- ROLLBACK: restore known-good PF/routing snapshots.
- VERIFY: post-change netcheck and deterministic receipt logging.

## Chinese networking ontology deltas (high impact)
1. **标识网络** usually separates naming, identity, and locator more explicitly than English networking docs.
2. **算力网络** introduces compute-routing as first-class path-selection dimension.
3. **意图驱动网络** treats policy compilation from intent as a lifecycle (intent → decomposition → orchestration → verification), not only static ACLs.
4. **确定性网络** emphasizes strict bounded guarantees for mission-critical flows, useful for Timelabs authority-ceiling reasoning.
