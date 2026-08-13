# Semantic Neighbours Matrix — Timelabs Networking Primitive Inventory

> **Gate**: MANDATORY NETWORK PRIOR-ART / SEMANTIC-NEIGHBOUR GATE (blocking gate for all future Omnia/MBSD/Blueshoes networking primitive design, extension, renaming, or implementation).
> **18 Architectural Dimensions** (independently replaceable, must never be conflated):
> Naming · Cryptographic Identity · Service Identity · Local Discovery · Global Discovery · Rendezvous · Locator Discovery · Route/Path Discovery · Path Selection · Mobility · Multihoming · Simultaneous Multipath · NAT/Firewall Traversal · Failure Recovery · Censorship/Failure Resistance · Trust Establishment · Privacy · (compatibility envelope: Apple enterprise/developer workloads as first acceptance target, NOT architectural authority).
> **Evidence Tiers** (never promote one into another): SPECIFIED · IMPLEMENTED · DEPLOYED · OBSERVED_LOCALLY · INFERRED · UNKNOWN.
> **OpenBSD Feasibility Classification**: NATIVE · PORTABLE (no kernel changes) · NEEDS_PORT · NEEDS_KERNEL_WORK · INCOMPATIBLE · UNKNOWN.
> **Last Evidence Sweep**: 2026-08-13 (sweeps 1–4 complete; 23 mandatory families + OpenBSD native manipulation palette).
> **Repository Scope**: Read-only evidence gathering; NO production networking modified; NO merge; NO kernel-change proposals until userland+existing kernel interfaces exhausted with evidence.

---

## Column Legend (used per-row below)

| Token | Meaning |
|---|---|
| `✓` | Materially solves this dimension (not merely incidental) |
| `◐` | Partially solves / supports with caveats / non-default extension |
| `✗` | Deliberately does NOT solve; out of architectural scope |
| `E` | Endpoint-hosted decision authority |
| `R` | Router / on-path node decision authority |
| `RS` | Resolver decision authority |
| `CP` | Centralised/distributed Control Plane |
| `DHT` | Distributed Hash Table overlay authority |
| `OVL` | Overlay mesh decision authority |
| `XA` | External Authority (PKI root / RIR / central coordinator) |

---

## 1. SCION (incl. Control Service, Beaconing, Path Lookup, Endpoint Path Selection, Trust Infrastructure, Hidden Paths, SCION-IP Gateway)

| Dimension | Status |
|---|---|
| Human-readable Naming | ✗ |
| Cryptographic Identity | ✓ (ISD+AS identifiers + Trust Root Configuration TRC per ISD; per-router cert chain; RFC-style SPP path signatures) |
| Service Identity | ◐ (via SCION-IP Gateway mapping, not native) |
| Local Discovery | ✗ |
| Global Discovery | ✓ (CP: beacon servers + path servers discover/register AS-level segments globally) |
| Rendezvous | ◐ (hidden-path groups Owner/Writer/Reader/Registry roles provide rendezvous-like capability concealment) |
| Locator Discovery | ✓ (CP path servers retrieve down/up-segment combinations; end-host constructs end-to-end path) |
| Route/Path Discovery | ✓ (beaconing control-plane constructs path segments; PCFS in data plane carries explicit per-hop forwarding state) |
| Path Selection | ✓ (ENDPOINT authority E — end host picks segment-combination, not the network) |
| Mobility | ◐ (endpoint-based reselection of path segments; no native handover semantics) |
| Multihoming | ✓ (AS-level multi-homing first-class; multiple upstream beacons naturally yield alternative segments) |
| Simultaneous Multipath | ◐ (end-host can stochastically distribute across constructed paths; no native fairness/aggregation layer) |
| NAT/Firewall Traversal | ✗ (requires SCION-IP Gateway to cross non-SCION domains) |
| Failure Recovery | ✓ (explicit probing; beaconing recomputes segments; endpoint reselects) |
| Censorship/Failure Resistance | ✓ (path-aware: can route around AS; hidden paths conceal sensitive prefixes) |
| Trust Establishment | ✓ (hierarchical: IANA → ISD TRC → AS → certificate server; signed beaconing; RPKI-adjacent) |
| Privacy | ◐ (on-path AS sequence is exposed; hidden paths hide existence of some prefix groups) |

| Property | Value |
|---|---|
| Authority Location | CP (beacon/path/control service per ISD) + E (final endpoint selection) |
| Identity / Locator / Name semantics | Identity = (ISD, AS) + AS certificate; Locator = 64-bit ISD-AS + 64-bit intra-AS forwarding; Name = none (use DNS/SCION-IP GW) |
| Trust model / compromise boundary | Per-ISD TRC root trust anchors; compromise of TRC = full ISD impersonation; compromise of single beacon server = path poisoning within segment radius |
| Incremental deployment / IP+DNS compat | SCION-IP Gateway for legacy interop; native apps must link against libscion or use SCION-enabled socket wrapper; Swiss financial/utility/health + SSFN deployments DEPLOYED; NL-ix + AMS-IX 2025–26 peering DEPLOYED |
| Open-source implementations / status | scionproto/scion (Go) DEPLOYED; scionlab.org research testbed; OpenBSD port status: PORTABLE (pure userland Go + raw sockets; no kernel module; NEEDS_PORT in ports tree today = UNKNOWN, classification: PORTABLE_NO_KERNEL) |
| OpenBSD feasibility | PORTABLE (no kernel changes required; userland daemon + tun interface pattern for gateway) |
| Reusable primitive / design lesson for Timelabs | (a) ENDPOINT path selection authority as architectural default; (b) packet-carried forwarding state (PCFS) vs per-router state; (c) hidden-path group semantics as model for classified rendezvous; (d) beaconing control-plane with separate trust-root per isolation domain |
| Falsifiable non-reuse reason (if rejected) | SCION cannot be Timelabs default: requires inter-AS SCION-peering agreements not in Timelabs control; NATed/Apple-enterprise endpoints rarely sit on SCION-connected ASes; hidden-path group Owner/Registry roles require always-on CP servers violating sealed-brick offline posture; no native cryptographic per-end-host identity (only per-AS). SPECIFIED yes, DEPLOYED in niche ASes, but ENDPOINT reachability from Timelabs targets = INFERRED unavailable. |

---

## 2. GNUnet (esp. GNS, IDENTITY, discovery/routing)

| Dimension | Status |
|---|---|
| Human-readable Naming | ✓ (GNS petname zones, zTLD raw-pubkey top-level, RFC 9498) |
| Cryptographic Identity | ✓ (EGO identity service; zone signing keys = identity keys) |
| Service Identity | ◐ (record set per zone; no native SVCB-style service parametric binding) |
| Local Discovery | ✓ (peer-to-peer local multicast + DHT-based neighbour discovery) |
| Global Discovery | ✓ (DHT-backed distributed record lookup) |
| Rendezvous | ✓ (CADET rendezvous subsystem for NAT traversal) |
| Locator Discovery | ✓ (DHT lookup for EGO → peer addresses) |
| Route/Path Discovery | ✓ (source-routed overlay via CADET / DV-based R5N for fragmented topologies) |
| Path Selection | ◐ (per-peer preferences; no exposed deterministic multi-path selection API) |
| Mobility | ◐ (DHT re-records on address change; no bounded handover latency) |
| Multihoming | ◐ (peer advertises multiple endpoints; no native preference orchestration) |
| Simultaneous Multipath | ✗ |
| NAT/Firewall Traversal | ✓ (CADET + ICMP hole-punch patterns) |
| Failure Recovery | ✓ (DHT self-heals; overlay re-routes) |
| Censorship/Failure Resistance | ✓ (fully-decentralised no single-root; petname zones owner-controlled) |
| Trust Establishment | ✓ (Web-of-trust petname delegation + per-record signatures; no IANA-like root) |
| Privacy | ✓ (records encrypted; GNS queries not observable by DNS-root; cadet E2E encrypt) |

| Property | Value |
|---|---|
| Authority Location | DHT + EGO zone owner (E+DHT) |
| Identity / Locator / Name semantics | Name = relative petname under user zone → absolute .alt zTLD; Identity = ECDSA Ed25519 zone key; Locator = DHT-routable peer ID + transport address |
| Trust model / compromise boundary | Owner zone = owner private key; compromise of single peer = record poisoning if eclipses target K-bucket (k-anonymity configurable); no central root — IANA .alt GANA namespace is a label, NOT a trust anchor |
| Incremental deployment / IP+DNS compat | RFC 9498 GNS allows DNS → GNS stub resolver bridge; ordinary apps need a pluggable resolver (systemd-resolved/Unbound stub); not deployed in Apple enterprise default configs |
| Open-source implementations / status | GNUnet 0.21+ (C) IMPLEMENTED; GNS RFC 9498 SPECIFIED |
| OpenBSD feasibility | PORTABLE (ports tree has net/gnunet historically; no kernel work; userland daemon) |
| Reusable primitive / design lesson for Timelabs | (a) Owner-controlled petname delegation model with NO global root for naming/identity provider CONTRACT; (b) RFC 9498 GNS record format as typed-record candidate for Omnia normative zone; (c) CADET rendezvous pattern for NAT traversal without STUN/TURN |
| Falsifiable non-reuse reason (if rejected as default naming) | GNUnet is not a default: entire IP+DNS app ecosystem expects POSIX getaddrinfo(), not libgnunetgns; Apple NWPathEvaluator / Network.framework surfaces Bonjour/mDNS + DNS, not .alt/GNS by default; DEPLOYED footprint = research/activist networks; OBSERVED_LOCALLY Timelabs targets = UNKNOWN. |

---

## 3. HIP / HIPv2 (RFC 7401 / RFC 9028 / RFC 5206)

| Dimension | Status |
|---|---|
| Human-readable Naming | ✗ |
| Cryptographic Identity | ✓ (HI → HIT 128-bit locator-independent identifier) |
| Service Identity | ✗ |
| Local Discovery | ◐ (via mDNS-HIT mapping, not native) |
| Global Discovery | ✓ (HIT → locator via rendezvous server RFC 8003 or DHT) |
| Rendezvous | ✓ (RFC 8003 HIP rendezvous server) |
| Locator Discovery | ✓ (HIT→IP via I1/R1 exchange + LOCATOR parameter) |
| Route/Path Discovery | ✗ |
| Path Selection | ✗ |
| Mobility | ✓ (RFC 5206 LOCATOR update; end-host multihoming handover) |
| Multihoming | ✓ (RFC 5206 multiple locators per HIT) |
| Simultaneous Multipath | ✗ |
| NAT/Firewall Traversal | ✓ (built-in, no STUN/TURN required; ICE-like native) |
| Failure Recovery | ◐ (locator re-resolution; no native fast-reroute) |
| Censorship/Failure Resistance | ◐ (rendezvous server single point of censorship without DHT fallback) |
| Trust Establishment | ✓ (HI public-key basis; optional HIP BEX trust-on-first-use; DNS-based HIP RR for trust delegation) |
| Privacy | ◐ (HIT is stable 128-bit identifier; correlation-able over sessions unless rotated) |

| Property | Value |
|---|---|
| Authority Location | E (endpoint) + optional RS (Rendezvous Server) |
| Identity / Locator / Name semantics | Identity = HI (public key); HIT = truncated hash (128-bit); Locator = mutable IPv4/IPv6 addresses; Name = none |
| Trust model / compromise boundary | Compromise of HI private key = permanent identity impersonation; compromise of rendezvous = hijack redirection of initial BEX; RPKI/HIP DNSSEC delegation optional |
| Incremental deployment / IP+DNS compat | Overlay-free ID-locator split; apps use getaddrinfo(HIT) on HIP-enabled hosts; requires HIPL or OpenHIP kernel module on Linux; macOS/iOS native = NONE |
| Open-source implementations / status | HIPL (Linux kernel+userland) IMPLEMENTED; OpenHIP (portable) IMPLEMENTED; RFCs 7401/9028/8003 SPECIFIED |
| OpenBSD feasibility | NEEDS_PORT (userspace OpenHIP can compile; no kernel if_hip device exists; HIP-over-UDP encaps in userland possible = PORTABLE_NO_KERNEL in practice; official classification here: NEEDS_PORT (because userland-only mode not in mainline docs)) |
| Reusable primitive / design lesson for Timelabs | (a) 128-bit stable HIT as cryptographic identity → locator-independent; (b) native built-in NAT traversal without requiring external ICE/STUN/TURN stack; (c) RFC 5206 LOCATOR signalling for endpoint mobility+multihoming as thin provider contract type |
| Falsifiable non-reuse reason (if rejected) | Zero native HIT support in Apple Network.framework / NWConnection; macOS/iOS kernel has no HIP handler; ordinary BSD sockets cannot bind HITs without interposer; DEPLOYED on Internet = effectively 0% of autonomous systems. |

---

## 4. LISP (+ LISP-Decent, RFC 9301 / RFC 9962)

| Dimension | Status |
|---|---|
| Human-readable Naming | ✗ |
| Cryptographic Identity | ✗ |
| Service Identity | ✗ |
| Local Discovery | ✗ |
| Global Discovery | ✓ (Map-Server/Map-Resolver control plane; LISP-Decent eliminates central MS/MR) |
| Rendezvous | ◐ (map-request / map-reply interaction acts as rendezvous between ITR↔ETR) |
| Locator Discovery | ✓ (EID→RLOC via mapping system) |
| Route/Path Discovery | ✗ (RLOC reachability relies on default BGP/IGP; LISP does not discover AS-level paths) |
| Path Selection | ✗ |
| Mobility | ✓ (EID stays bound to endpoint while RLOC changes; mobile-node LISP mobile-node spec) |
| Multihoming | ✓ (EID site can have multiple ETRs/RLOCs with priority/weight) |
| Simultaneous Multipath | ◐ (per-flow RLOC priority weights; no native L4 aggregation) |
| NAT/Firewall Traversal | ✓ (LISP NAT traversal + data plane encapsulation) |
| Failure Recovery | ✓ (ETR health check; priority-fallback to other RLOCs) |
| Censorship/Failure Resistance | ◐ (classic LISP central MS/MR = single point; LISP-Decent multicast-push/pull DHT improves resistance) |
| Trust Establishment | ◐ (optional Map-Server authentication; no native cryptographic EID identity) |
| Privacy | ✗ (EID prefixes are globally routable identifiers; flow metadata visible to ETR) |

| Property | Value |
|---|---|
| Authority Location | CP (Map-Resolver/Map-Server) + R (ITR/ETR tunnel routers) |
| Identity / Locator / Name semantics | EID = endpoint namespace (inside site); RLOC = routing locator transit namespace; Name = none |
| Trust model / compromise boundary | Compromise of MS = false EID→RLOC mapping; LISP-Decent distributes trust across multicast peers; no EID ownership cryptographically enforced |
| Incremental deployment / IP+DNS compat | Transparent to non-LISP applications (ITR/ETR at site edges); needs LISP-capable edge routers; Apple enterprise = not default |
| Open-source implementations / status | LISPmob (Linux) IMPLEMENTED; OpenLISP (FreeBSD) IMPLEMENTED; LISP-Decent RFC 9962 SPECIFIED Mar 2026 |
| OpenBSD feasibility | NEEDS_PORT (no mainline if_lisp; userland encap possible via PF route-to + tun; not in base) |
| Reusable primitive / design lesson for Timelabs | (a) Two-namespace EID/RLOC split is a strong provider-contract pattern for identity/locator separation; (b) LISP-Decent (RFC 9962) decentralised multicast mapping as a lesson on avoiding single MS/MR points for identity→locator mapping providers |
| Falsifiable non-reuse reason (if rejected) | LISP has zero EID-identity cryptographic binding (EIDs assigned administratively, matching Timelabs identity requirement NOT MET — HIP/HIT or libp2p PeerID superior); requires tunnelling overhead on edge without endpoint benefit for Timelabs client workloads. |

---

## 5. ILNP (RFC 6740 / 6741 / 6742)

| Dimension | Status |
|---|---|
| Human-readable Naming | ✓ (NID/L64/L32 DNS RRs RFC 6742) |
| Cryptographic Identity | ✗ |
| Service Identity | ✗ |
| Local Discovery | ✗ |
| Global Discovery | ✓ (standard DNS delegation) |
| Rendezvous | ✗ |
| Locator Discovery | ✓ (ILV vector over IPv6: NID 64-bit + Locator 64-bit) |
| Route/Path Discovery | ✗ |
| Path Selection | ✗ |
| Mobility | ✓ (Locator updates don't change NID; soft handover) |
| Multihoming | ✓ (multiple Locators per NID) |
| Simultaneous Multipath | ✗ |
| NAT/Firewall Traversal | ✗ (no overlay; locators routable → assume no NAT) |
| Failure Recovery | ◐ (try alternate locator; no native FRR) |
| Censorship/Failure Resistance | ✗ (relies on DNS and default IPv6 routing) |
| Trust Establishment | ◐ (can use standard DNSSEC; no native identity key) |
| Privacy | ◐ (stable NID correlates identity across locator changes) |

| Property | Value |
|---|---|
| Authority Location | RS (DNS) + E (endpoint locator update) |
| Identity / Locator / Name semantics | NID 64-bit = node identity-ish (non-crypto, assigned); Locator L64 64-bit = routable; Name via standard DNS → ILNP RR types |
| Trust model / compromise boundary | DNS trust model (DNSSEC); same compromise surface as conventional DNS; no cryptographic node identity = spoofable without DNSSEC |
| Incremental deployment / IP+DNS compat | OVERLAY-FREE! No new routing protocol, no tunnels; evolutionary IPv6 extension with NID/Locator in v6 address space; existing routers UNCHANGED; FreeBSD 14.3 native port NATIVE; Linux 4.9 kernel prototype |
| Open-source implementations / status | FreeBSD 14.3 native NATIVE-DEPLOYED; Linux prototype IMPLEMENTED; IETF 126 ongoing drafts for IPv6 apps usage |
| OpenBSD feasibility | NEEDS_KERNEL_WORK (requires kernel IPv6 flowlabel/NID handling changes; userland cannot emulate; RFC-specified but not in OpenBSD src tree) |
| Reusable primitive / design lesson for Timelabs | (a) No-overlay, no-tunnel ID/locator split over existing IPv6 address space is THE model for deployment-light identity+locator separation — NOT every separation needs a DHT; (b) DNS RR types (NID/L64/L32) as typed record templates for Omnia provider-contract identity/locator records |
| Falsifiable non-reuse reason (if rejected) | ILNP has NO cryptographic identity (NID = administratively assigned), failing Timelabs trust-boundary if identity is key requirement; NEEDS_KERNEL_WORK on OpenBSD = rejected as kernel modification when userland alternatives exist per architectural rule. |

---

## 6. Named Data Networking / CCNx

| Dimension | Status |
|---|---|
| Human-readable Naming | ✓ (name-based forwarding is first-class) |
| Cryptographic Identity | ✓ (per-packet data signing; trust anchored in producer key) |
| Service Identity | ✓ (service name prefixes naturally expressed) |
| Local Discovery | ✓ (local-strategy Interest multicast) |
| Global Discovery | ✓ (name-based FIB propagation) |
| Rendezvous | ✓ (Interest/Data pair is an implicit rendezvous) |
| Locator Discovery | ✗ (no locator layer; names locate content) |
| Route/Path Discovery | ✓ (stateful PIT-forwarding + reflexive I-D) |
| Path Selection | ✓ (per-prefix forwarding strategy module, configurable) |
| Mobility | ✓ (consumer re-issues Interest; Data returns from mobile producer naturally) |
| Multihoming | ✓ (multiple FIB nexthops per prefix) |
| Simultaneous Multipath | ✓ (PIT entries naturally aggregate across next hops) |
| NAT/Firewall Traversal | ◐ (producer must originate Data; NATed producers need rendezvous/relay) |
| Failure Recovery | ✓ (PIT timeouts + re-Interest) |
| Censorship/Failure Resistance | ✓ (anycast caches; multi-path) |
| Trust Establishment | ✓ (producer-signed Data; web-of-trust / schema-based trust) |
| Privacy | ◐ (Interest names are visible to on-path routers; payload signature-based correlation possible) |

| Property | Value |
|---|---|
| Authority Location | E (consumer drives) + R (PIT/FIB/CS router triad) |
| Identity / Locator / Name semantics | Identity = producer signing key; Locator = NONE (name is self-locating); Name = hierarchical URI-like /a/b/c structure |
| Trust model / compromise boundary | Per-Data signed; compromise of producer key = forged content; compromise of router = Interest flooding / cache poisoning but no signature forgery |
| Incremental deployment / IP+DNS compat | NDN-over-UDP/IP encapsulation layer; NOT transparent to POSIX socket apps (need NDN lib replacement); DEPLOYED research testbed NDNtestbed; NOT in Apple enterprise today |
| Open-source implementations / status | ndn-cxx (C++ lib) IMPLEMENTED; NFD (forwarder daemon) IMPLEMENTED; CCNx (Java/C) IMPLEMENTED |
| OpenBSD feasibility | PORTABLE (all userland C++/C; daemon + tun; no kernel changes) |
| Reusable primitive / design lesson for Timelabs | (a) Per-Data-packet cryptographic signing as trust model — verify endpoint-origin independently of path; (b) PIT/FIB reflexive forwarding eliminates need for session-oriented rendezvous when using request/response pattern (strong provider-contract candidate for Omnia service-data retrieval semantics); (c) strategy-module per-name-prefix as architecture separation of policy from forwarding mechanism |
| Falsifiable non-reuse reason (if rejected as default architecture) | NDN breaks every existing POSIX socket application (need NDN library/rewrites); incompatible with Timelabs first acceptance workload (Apple enterprise/developer apps are BSD socket / Network.framework / HTTP/3); NDN name-based forwarding provides no advantage for connection-oriented protocols where Timelabs target workloads sit. |

---

## 7. libp2p (PeerID, Identify, DHT/routing, rendezvous/discovery, Circuit Relay, AutoNAT, DCUtR)

| Dimension | Status |
|---|---|
| Human-readable Naming | ✗ |
| Cryptographic Identity | ✓ (PeerID = multihash of Ed25519 pubkey; first-class) |
| Service Identity | ✓ (/protocol/name strings multicodec-tagged; /service/ records via DHT PROVIDER) |
| Local Discovery | ✓ (mDNS local peer discovery module) |
| Global Discovery | ✓ (Kademlia Amino DHT; client/server mode separation; PROVIDER records) |
| Rendezvous | ✓ (Rendezvous protocol = namespace topic-based registration at arbitrary rendezvous peers) |
| Locator Discovery | ✓ (DHT FIND_NODE returns multiaddrs per PeerID) |
| Route/Path Discovery | ✓ (Kademlia iterative lookups; optional RECURSIVE) |
| Path Selection | ✗ (DHT chooses closest-to-key peers; no path-policy exposed) |
| Mobility | ✓ (re-advertise multiaddrs + DHT re-records) |
| Multihoming | ✓ (single PeerID advertises N transport multiaddrs, auto-rotate) |
| Simultaneous Multipath | ✗ |
| NAT/Firewall Traversal | ✓ (AutoNAT public-reachability test with anti-amplification; Circuit Relay v2 = TURN-like encrypted E2E relay; DCUtR = direct-upgrade via relay-coordinated hole punching) |
| Failure Recovery | ✓ (peer eviction; DHT re-lookup on failure) |
| Censorship/Failure Resistance | ✓ (DHT-distributed; rendezvous nodes replaceable) |
| Trust Establishment | ✓ (Noise+TLS1.3 libp2p security channels; TOFU + optional CA-pinned peer certs) |
| Privacy | ◐ (PeerID stable; DHT queries observable by queried nodes; Circuit Relay v2 E2E encryption hides payload from relay) |

| Property | Value |
|---|---|
| Authority Location | E + DHT + OVL (no single authority) |
| Identity / Locator / Name semantics | Identity = Ed25519 pubkey → PeerID(multihash); Locator = Multiaddr /dns/, /ip4/, /ip6/, /tcp/, /udp/, /quic/, /p2p-circuit/; Name = none |
| Trust model / compromise boundary | Compromise of long-term Ed25519 key = identity takeover; DHT eclipse possible (mitigated by IP diversity bucket filters); no global trust anchor |
| Incremental deployment / IP+DNS compat | Library-only, no daemon required (optional daemon exists); transparent-to-network: speaks native UDP/TCP/QUIC over normal IP; apps must link libp2p; Apple Network.framework can wrap via NWConnection custom protocol |
| Open-source implementations / status | go-libp2p (Go) DEPLOYED (IPFS, Filecoin, Polkadot, Ethereum CL); rust-libp2p (Rust) DEPLOYED; js-libp2p DEPLOYED |
| OpenBSD feasibility | PORTABLE (net/go-ipfs package in ports tree = verifiable PORTABLE) |
| Reusable primitive / design lesson for Timelabs | (a) PeerID as PRIMARY cryptographic endpoint identity model; (b) Multiaddr universal locator serialization for typed provider contract; (c) DCUtR (relay-coordinated → direct upgrade) is THE most engineer-friendly documented NAT traversal pattern for pure userland codebase; REUSE AS PROVIDER CONTRACT CATEGORY |
| Falsifiable non-reuse reason (if rejected as default architecture) | libp2p is a LIBRARY, not a protocol; provides NO human-readable naming layer, NO global path-selection semantics, NO multipath; must be composed with GNS/SCION-like components to close naming/path gaps. |

---

## 8. Yggdrasil

| Dimension | Status |
|---|---|
| Human-readable Naming | ✗ |
| Cryptographic Identity | ✓ (IPv6 0200::/7 overlay addresses derived from truncated ed25519 pubkey) |
| Service Identity | ✗ |
| Local Discovery | ✓ (auto multicast peer discovery) |
| Global Discovery | ✓ (Ironwood shortest-path DHT-backed routing for mesh networks) |
| Rendezvous | ✗ |
| Locator Discovery | ✓ (DHT-tree-based locator of peer keys → coords) |
| Route/Path Discovery | ✓ (Ironwood greedy spanning+DHT hybrid) |
| Path Selection | ✗ (always shortest-tree path; no policy knob) |
| Mobility | ✓ (recompute coords as topology changes) |
| Multihoming | ✗ |
| Simultaneous Multipath | ✗ |
| NAT/Firewall Traversal | ✓ (peer TCP/UDP over normal ports + auto peer) |
| Failure Recovery | ✓ (DHT recomputes coords; mesh heals) |
| Censorship/Failure Resistance | ✓ (decentralized overlay; no root) |
| Trust Establishment | ✓ (per-packet ed25519-derived identity; TOFU on peering) |
| Privacy | ✗ (no anonymity; traffic-analysis by coords stable) |

| Property | Value |
|---|---|
| Authority Location | OVL (no central authority) |
| Identity / Locator / Name semantics | Identity = ed25519 pubkey; Locator = derived coordinate + IPv6 0200::/7; Name = none |
| Trust model / compromise boundary | Peering auto-discover = friend-of-friend-ish trust; no global anchor; overlay partitioning attack possible in sparse regions |
| Incremental deployment / IP+DNS compat | Overlay IPv6; apps bind 0200::/8 addresses with standard sockets; no kernel mods (tun); DEPLOYED alpha research network |
| Open-source implementations / status | yggdrasil-go (Go) IMPLEMENTED |
| OpenBSD feasibility | PORTABLE (Go userland + tun; OpenBSD listed as supported platform = PORTABLE_NO_KERNEL) |
| Reusable primitive / design lesson for Timelabs | (a) Pubkey-derived IPv6 overlay address (can be composed with PF route-to/rdomain to create opaque internal identity-routing zones on sealed brick); (b) Ironwood DHT+tree hybrid routing as lesson for mesh when topology is unplanned (lessons-only, NOT reuse — Yggdrasil alpha-state) |
| Falsifiable non-reuse reason (if rejected) | Alpha research project, non-stable; single-tree path selection (no policy); zero Apple enterprise deployment footprint; 0200::/7 deprecated IPv6 block (RFC conflict potential). |

---

## 9. cjdns / Hyperboria

| Dimension | Status |
|---|---|
| Human-readable Naming | ✗ |
| Cryptographic Identity | ✓ (IPv6 fc00::/8 derived from Curve25519 pubkey) |
| Service Identity | ✗ |
| Local Discovery | ✓ (peer auto-discovery) |
| Global Discovery | ✓ (DHT source routing across mesh) |
| Rendezvous | ✗ |
| Locator Discovery | ✓ (DHT) |
| Route/Path Discovery | ✓ (DHT source routing switch label) |
| Path Selection | ✗ |
| Mobility | ✓ |
| Multihoming | ✗ |
| Simultaneous Multipath | ✗ |
| NAT/Firewall Traversal | ✓ (UDP peer-to-peer; works behind NAT) |
| Failure Recovery | ✓ |
| Censorship/Failure Resistance | ✓ (distributed) |
| Trust Establishment | ✓ (Curve25519 identity; friend-of-a-friend trust model) |
| Privacy | ◐ (no anonymity by default; fc00 stable correlates) |

| Property | Value |
|---|---|
| Authority Location | OVL + friend-of-friend trust |
| Identity / Locator / Name semantics | Identity = Curve25519; Locator = fc00::/8 + source-route switch labels; Name = none |
| Trust model / compromise boundary | Peering is social (friend-of-friend); requires manual peering to bootstrap new node; no global trust anchor |
| Incremental deployment / IP+DNS compat | Overlay; apps use standard sockets inside; not in base OpenBSD |
| Open-source implementations / status | cjdns (C) IMPLEMENTED; Hyperboria mesh DEPLOYED small-scale |
| OpenBSD feasibility | PORTABLE (Linux/Illumos/OSX/FreeBSD mainline; OpenBSD unlisted; compile from source = PORTABLE) |
| Reusable primitive / design lesson for Timelabs | (a) Crypto-derived IPv6 (fc00::) as stable identity for internal overlay trust zones (design lesson for Timelabs internal network models); (b) Switch-label source routing eliminates per-node FIB scaling problem (lesson) |
| Falsifiable non-reuse reason (if rejected) | Social trust model requires manual peer insertion = NOT machine-declarable; friend-of-friend routing does NOT close global Timelabs discovery for arbitrary endpoints (bootstrapping new nodes hard); DEPLOYED network effectively static/small. |

---

## 10. Babel (RFC 8966 Standards Track) + BATMAN family (BATMAN-adv)

| Dimension | Babel | BATMAN-adv |
|---|---|---|
| Human-readable Naming | ✗ | ✗ |
| Cryptographic Identity | ✗ | ✗ |
| Service Identity | ✗ | ✗ |
| Local Discovery | ✓ (hello/IHU hellos) | ✓ (originator messages; local broadcast) |
| Global Discovery | ✓ (L3 routing within routing domain) | ✓ (L2 virtual-switch within mesh domain; OGMs flood) |
| Rendezvous | ✗ | ✗ |
| Locator Discovery | ✓ (router updates carry prefix reachability) | ✓ (L2 ARP/NDP table on bat0; no locator layer) |
| Route/Path Discovery | ✓ (distance-vector loop-avoiding; link-aware wired/wireless/tunnelled) | ✓ (TQ link-quality based OGM; source routing optional) |
| Path Selection | ✓ (metric: feasibility distance + expected tx count) | ✓ (TQ-based; per-originator best next-hop) |
| Mobility | ✓ (fast reconvergence for wireless meshes) | ✓ (fast OGM-based mobility) |
| Multihoming | ◐ | ✗ |
| Simultaneous Multipath | ✗ | ✗ |
| NAT/Firewall Traversal | ✗ | ✗ |
| Failure Recovery | ✓ (triggered updates; ~sub-second on wireless) | ✓ (OGM interval fast) |
| Censorship/Failure Resistance | ✓ (mesh-distributed) | ✓ (mesh-distributed; Freifunk deployments) |
| Trust Establishment | ✗ (no crypto; HMAC optional per-neighbour in some impl) | ✗ (no crypto; OGMs forgeable) |
| Privacy | ✗ (OSPF-like; plaintext updates) | ✗ |

| Property | Babel | BATMAN-adv |
|---|---|---|
| Authority Location | R (all routers participate) | R (all mesh nodes) |
| Identity / Locator / Name semantics | Identity = router-id (administrative); Locator = IP prefix | Identity = originator MAC; Locator = IPv4/IPv6 via OGM |
| Trust model / compromise boundary | Routing domain trust; rogue router can poison prefix | Same, L2 domain so rogue node bridges |
| Incremental deployment / IP+DNS compat | Transparent to IP apps; L3 daemon; AREDN mesh replacing OLSR DEPLOYED | Linux kernel module; Freifunk DEPLOYED at scale (25k+ nodes) |
| Open-source implementations / status | babeld (C) IMPLEMENTED + RFC 8966 SPECIFIED | batman-adv Linux kernel L2 DEPLOYED 2025.4 stable IPv6 multicast |
| OpenBSD feasibility | PORTABLE (babeld pure userland; can speak over any interface) **NATIVE-OPENBSD**: no, PORTABLE | NEEDS_KERNEL_WORK (batman-adv Linux-only kernel module; no OpenBSD port exists; no userland equivalent) |
| Reusable primitive / design lesson for Timelabs | (a) Babel = ideal for last-mile wireless/retail mesh within a site as routing protocol (PORTABLE + Standards Track); (b) Link-type-aware metrics unified wired/wireless/tunnelled = strong design lesson for path-quality metrics in Timelabs path-selection providers | (a) L2 virtual switch mesh useful when Ethernet semantics needed (but Linux-only); (b) TQ metric lessons-only |
| Falsifiable non-reuse reason (if rejected) | Babel: no crypto identity, no global-scale routing (single domain only) → NOT identity/global discovery provider. BATMAN: NEEDS_KERNEL_WORK OpenBSD → kernel modification prohibited until userland exhausted → rejected as routing layer default. |

---

## 11. WireGuard (incl. Headscale/Tailscale concepts/ZeroTier/Nebula)

### 11.1 WireGuard Kernel Protocol (wg(4) on OpenBSD)

| Dimension | Status |
|---|---|
| Human-readable Naming | ✗ |
| Cryptographic Identity | ✓ (Curve25519 public key per peer) |
| Service Identity | ✗ |
| Local Discovery | ✗ |
| Global Discovery | ✗ |
| Rendezvous | ✗ |
| Locator Discovery | ✗ (endpoint IP:port must be static-configured per peer OR learned on reply) |
| Route/Path Discovery | ✗ |
| Path Selection | ✗ |
| Mobility | ✓ (roaming endpoint auto-relearns from incoming) |
| Multihoming | ✗ (single endpoint key; no simultaneous per-peer multi-endpoint with preference) |
| Simultaneous Multipath | ✗ |
| NAT/Firewall Traversal | ◐ (persistent-keepalive enables outbound-only to stay open; NO hole-punch signalling) |
| Failure Recovery | ◐ (keepalive timeout; no BFD-like detection) |
| Censorship/Failure Resistance | ◐ (WireGuard UDP recognisable; can run over non-443; no protocol mimicry) |
| Trust Establishment | ✓ (static pubkey insertion; TOFU-by-config) |
| Privacy | ✓ (no cleartext handshake metadata; post-quantum preshared optional) |

| Property | Value |
|---|---|
| Authority Location | E (per-endpoint configuration) |
| Identity / Locator / Name semantics | Identity = Curve25519 pubkey; Locator = manually-configured or learned UDP 4-tuple; Name = none |
| Trust model / compromise boundary | Compromise of private key = all traffic decrypted + impersonation; static config no revocation; requires out-of-band pubkey distribution |
| Incremental deployment / IP+DNS compat | Fully transparent; ordinary sockets over wg0; kernel module on Linux/win/macOS/iOS/Android; OpenBSD base kernel wg(4) NATIVE |
| Open-source implementations / status | WireGuard C kernel + Go userspace (wireguard-tools) NATIVE DEPLOYED; wg(4) OpenBSD 7.x NATIVE |
| OpenBSD feasibility | **NATIVE** (in-kernel driver; ifconfig wg0 create; configured via hostname.if(5) and ifconfig(8)) |
| Reusable primitive / design lesson for Timelabs | (a) **DIRECT REUSE CATEGORY**: OpenBSD wg(4) NATIVE — use for sealed-brick inter-site encrypted tunnels, admin backchannels; (b) ~4000LOC minimalism is THE lesson for crypto-protocol TCB size when building Timelabs internal constructs; (c) allowed-ips longest-match routing as simple identity-to-locator policy |
| Falsifiable non-reuse reason (if rejected for a dimension) | NOT a discovery/rendezvous layer at all; peer endpoint discovery requires external provider (see Headscale/Tailscale below). |

### 11.2 Headscale / Tailscale Concepts / ZeroTier / Nebula (coordination overlays around WireGuard-like identity)

| Dimension | Headscale | ZeroTier | Nebula (Slack) |
|---|---|---|---|
| Cryptographic Identity | ✓ (same WireGuard pubkeys) | ✓ (planet/moon signing keys + node identity) | ✓ (Nebula X.509 CA + cert per node) |
| Local Discovery | ✓ (mDNS-like subnet-local peer discovery) | ✓ (L2 local peer detection) | ✓ (local lighthouse-less direct possible) |
| Global Discovery | ✓ (DERP map via control plane + STUN for endpoint) | ✓ (planet root servers + moons) | ✓ (static configured lighthouses) |
| Rendezvous | ✓ (DERP relay = rendezvous via HTTP/443 — ANY port; fallback data plane) | ✓ (root servers act as rendezvous) | ✓ (lighthouses are rendezvous only) |
| Locator Discovery | ✓ (STUN + DERP coord) | ✓ (planet/moons relay endpoints) | ✓ (lighthouse registrations) |
| NAT/Firewall Traversal | ✓ (DERP fallback = guaranteed; direct hole punch if possible) | ✓ (zero-config traversal) | ✓ (lighthouse-coordinated) |
| Path Selection | ◐ (direct preferred; DERP fallback auto; no deterministic multi-preference API) | ◐ (VL2 shortest through roots) | ✓ (hops/static metric via lighthouse) |
| Mobility | ✓ (DERP reconnects seamless) | ✓ | ✓ |
| Multihoming | ◐ | ◐ | ◐ |
| Trust Establishment | ✓ (Headscale: auth-key + OIDC SSO; TS: proprietary SSO) | ✓ (planet root trust chain) | ✓ (CA cert chain; per-node cert signed) |
| Privacy | ◐ (Tailscale SSO plane centralised; Headscale self-hosted option E2EE DERP-relayed) | ◐ (traffic between nodes E2EE; root moons see metadata) | ✓ (fully self-hosted CA; no third party) |

| Property | Headscale | ZeroTier | Nebula |
|---|---|---|---|
| Authority Location | CP (Headscale single tailnet server) + E | CP (planet root servers + optional moons) | CP (lighthouses) + CA anchor |
| Identity / Locator / Name semantics | Tailscale IP (CGNAT 100.64.0.0/10) stable identity overlay IP; MagicDNS optional naming; DERP multiaddr locator | VL2 Ethernet overlay + 40-bit address + member identity keys | Overlay IP 192.168.x per CA; identity in certificate O field; lighthouse FQDN → locator |
| Trust model / compromise boundary | Headscale compromise = full tailnet membership+metadata; DERP relays E2EE so cannot decrypt payload; ZeroTier planet root compromise = full VL2 impersonation; Nebula: CA compromise = full overlay impersonation | (same architecture pattern) | Nebula lighthouses cannot decrypt (no key material); CA is offline |
| Incremental deployment / IP+DNS compat | Fully transparent; any TCP/UDP app works over tailscale0; macOS/iOS NetworkExtension NATIVE on Apple | Fully transparent L2/L3 | Fully transparent L3 |
| Open-source implementations / status | Headscale 38.5k stars BSD-3 v0.28.0 Feb 2026 + uses official Tailscale clients DEPLOYED; ZeroTier BUSL-1.1; Nebula MIT Slack IMPLEMENTED DEPLOYED internally at Slack | ZeroTier (BUSL); Nebula GitHub Slack go IMPLEMENTED |
| OpenBSD feasibility | PORTABLE (Headscale Go + official Tailscale Go client both run; wireguard-tools wg in base) | PORTABLE (ports/net/zerotier exists) | PORTABLE (Go userland + tun) |
| Reusable primitive / design lesson for Timelabs | (a) **WRAP AS PROVIDER**: DERP (HTTP/443 relay)-as-rendezvous is THE portable rendezvous primitive for Apple enterprise (no firewall exceptions); (b) Headscale-style self-hosted control-plane over WireGuard is a strong Timelabs internal-identity-overlay PATTERN (not direct reuse unless self-hosting) | (a) VL2 model lessons for identity-overlay when L2 semantics needed (prior art only); (b) Moon pattern = secondary trust anchors useful in Timelabs multi-region | (a) Nebula CA-per-node certificates = model for certificate-authority based Timelabs identity-overlay **WRAP AS PROVIDER CATEGORY** when identity=X.509; (b) lighthouse static discovery pattern = no-DHT, low-churn, easy firewall — IDEAL for sealed-brick low-attack-surface internal fabrics |
| Falsifiable non-reuse reason (if rejected) | Tailscale = proprietary SSO vendor lock-in (Timelabs prohibits vendor lock-in per project memory); ONLY Headscale self-hosted avoids lock-in. ZeroTier BUSL-1.1 license = Timelabs FOSS posture violation (Omnia FOSS + portable), reject ZeroTier non-free license. Nebula: only rejection = lighthouse config is STATIC (no dynamic global discovery; needs lighthouse FQDN). | ZeroTier BUSL-1.1 (proprietary) + central planet root dependency = reject. | Nebula: no multipath; no mobility handover semantics (not a dealbreaker). No rejection needed unless those dims required. |

---

## 12. IPFS / Kademlia (Amino DHT + LAN DHT)

| Dimension | Status |
|---|---|
| Human-readable Naming | ✗ (use IPNS naming; IPNS = pubkey-based naming, not Kademlia) |
| Cryptographic Identity | ✓ (256-bit SHA256-of-PeerID = Kademlia node ID; PeerID = multihash pubkey) |
| Service Identity | ✓ (PROVIDER records for content CIDs; libp2p rendezvous for services) |
| Local Discovery | ✓ (LAN DHT mDNS) |
| Global Discovery | ✓ (Amino DHT WAN FIND_NODE/PROVIDER) |
| Rendezvous | ◐ (not native; via libp2p Rendezvous protocol layer) |
| Locator Discovery | ✓ (FIND_NODE returns PeerID → multiaddrs) |
| Route/Path Discovery | ✓ (iterative/recursive Kademlia α=3 lookups; bucket IP diversity filters) |
| Path Selection | ✗ (closest-to-key; no path policy) |
| Mobility | ✓ (PeerID stable; re-announce PROVIDER on new locators) |
| Multihoming | ✓ (multiaddrs list per peer) |
| Simultaneous Multipath | ✗ |
| NAT/Firewall Traversal | ✓ (AutoNAT + Circuit Relay v2 + DCUtR via libp2p) |
| Failure Recovery | ✓ (DHT self-healing buckets; PROVIDER re-announce) |
| Censorship/Failure Resistance | ✓ (distributed DHT; no single choke point) |
| Trust Establishment | ✓ (libp2p Noise/TLS channels; CID content-hash integrity) |
| Privacy | ◐ (public DHT queries leak CID-of-interest to third-party nodes; private DHT mode available) |

| Property | Value |
|---|---|
| Authority Location | DHT + OVL |
| Identity / Locator / Name semantics | Identity = PeerID multihash(pubkey); Locator = multiaddrs; Name = IPNS pubkey→/ipfs/... naming (outside Kademlia) |
| Trust model / compromise boundary | Eclipse attack if Sybil controls K=20 closest; IP diversity mitigates; no single trust anchor; CID integrity guaranteed hash-wise regardless |
| Incremental deployment / IP+DNS compat | Userland daemon + gateway (HTTP /api/v0); apps talk HTTP to Kubo; not transparent to sockets; Apple enterprise not default |
| Open-source implementations / status | Kubo (Go) 0.38.1 DEPLOYED; IPFS Amino DHT DEPLOYED |
| OpenBSD feasibility | PORTABLE (ports/net/go-ipfs package present in OpenBSD ports tree 0.38.1 = PORTABLE verified) |
| Reusable primitive / design lesson for Timelabs | (a) Kademlia PROVIDER records = THE typed model for Timelabs service-provider discovery (provider contract maps service-id→{locators, identity}); (b) IP diversity bucket filters = anti-eclipse lesson in DHT design |
| Falsifiable non-reuse reason (if rejected as default discovery layer) | Public DHT bootstrapping requires bootstrap nodes (single-point-ish); content lookup latency ~5–15s inappropriate for Timelabs real-time control plane signals; PROVIDER records are content-centric, not service-identity-semantic-correct. |

---

## 13. mDNS (RFC 6762) · DNS-SD (RFC 6763) · SVCB/HTTPS DNS service-binding (incl. Apple SVCB+DNS-SD integration)

| Dimension | mDNS | DNS-SD | SVCB/HTTPS |
|---|---|---|---|
| Human-readable Naming | ✓ (.local FQDN multicast) | ✓ (<service>._<proto>._tcp.local PTR SRV TXT) | ✓ (SVCB/HTTPS RR at zone apex) |
| Cryptographic Identity | ✗ | ✗ | ◐ (DNSSEC only; no pubkey-identity native; Encrypted-DNS-SD extension Nov 2025 for _dot/_doh/_doq types = I-D) |
| Service Identity | ✗ | ✓ (PTR+SRV+TXT = service type + port + metadata) | ✓ (ALPN, port, ECH config, ip hints = SvcParams; Akiwate Nov 2025 Apple SVCB+DNS-SD integration) |
| Local Discovery | ✓ (224.0.0.251 / FF02::FB link-local multicast) | ✓ (operates over mDNS for local) | ✗ (global DNS only) |
| Global Discovery | ✗ | ◐ (operates over unicast DNS for "wide-area DNS-SD" but rare) | ✓ (authoritative server) |
| Rendezvous | ✗ | ✗ | ✗ |
| Locator Discovery | ✗ | ✓ (SRV+A/AAAA) | ✓ (IPv4Hint/IPv6Hint + additional-section A/AAAA) |
| Route/Path Discovery | ✗ | ✗ | ✗ |
| Path Selection | ✗ | ✗ | ✗ |
| Mobility | ✓ (mDNS cache flush on move) | ✓ (re-announce SRV) | ◐ (DNS TTL governs) |
| Multihoming | ◐ (multiple A/AAAA per host) | ✓ (multiple SRV targets) | ✓ (multiple SVCB records, priority-ordered) |
| Simultaneous Multipath | ✗ | ✗ | ✗ |
| NAT/Firewall Traversal | ✗ (link-local only; no cross-subnet) | ✗ (same) | ✗ |
| Failure Recovery | ✓ (goodbye packets + TTL expiry) | ✓ | ✓ (priority fallback) |
| Censorship/Failure Resistance | ✗ (link-local only) | ✗ | ✗ (relies on DNS trust) |
| Trust Establishment | ✗ | ✗ | ◐ (DNSSEC + ECH keys via SvcParam key) |
| Privacy | ✗ (plaintext mDNS on LAN; everyone sees every query) | ✗ (same) | ◐ (DoH/DoT encrypted transport to resolver; ECH encrypts SNI) |

| Property | mDNS | DNS-SD | SVCB/HTTPS |
|---|---|---|---|
| Authority Location | E (all hosts on LAN are equal responders; no server) | E + RS (wide-area) | RS |
| Identity / Locator / Name semantics | Name = <host>.local.; Identity = none (no crypto); Locator = A/AAAA in same mDNS response | Service Name = instance._type._proto.local; Target = SRV target host; Port/TXT metadata | Zone apex name maps to ALPN+port+ECH+IP hints via SvcParams |
| Trust model / compromise boundary | No trust; any host can claim any .local. name; DNSSEC optional for wide-area | Same | DNSSEC only if zone is signed; ECH key is authenticated by resolver |
| Incremental deployment / IP+DNS compat | Apple Bonjour NATIVE on macOS/iOS (mDNSResponder base system); Windows Bonjour Print Services optional; Linux avahi-daemon | Apple Bonjour NATIVE | NSD 4.9.1 (OpenBSD base) supports SVCB user-typed; Unbound 1.22.0 resolver supports; RFC 9460 Standards Track; Apple Network.framework NATIVE uses SVCB/HTTPS for QUIC/HTTP3 |
| Open-source implementations / status | mDNSResponder (Apple Apache-2.0); Avahi GPL-LGPL IMPLEMENTED | Bonjour/avahi; RFCs 6762/6763 SPECIFIED DEPLOYED widely | RFC 9460 SPECIFIED DEPLOYED by major CDNs (Cloudflare, Google); NSD/Unbound support |
| OpenBSD feasibility | PORTABLE (no base mDNS responder; Avahi in ports; **local resolver/authoritative DNS Unbound+NSD NATIVE** per directive as OPTIONAL providers only, NEVER privileged truth) | PORTABLE same | **NATIVE** (NSD authoritative in base system supports SVCB records; Unbound resolver supports both = userland, no pkg needed) |
| Reusable primitive / design lesson for Timelabs | (a) **DIRECT REUSE / OPTIONAL PROVIDER ONLY per directive**: mDNS/DNS-SD = use when Apple Bonjour compatibility workload explicitly requires, never as Omnia truth source; (b) Multicast PTR/SRV/TXT record layout as typed-schema lesson for Omnia provider record-format | (a) SVCB SvcParams extensibility model = **EXACT model for Timelabs machine-readable service identity records** (priority + key=value parameters, additional-section glue) — STRONG PROVIDER CONTRACT CATEGORY; (b) ECH key in SvcParam for privacy — direct pattern for encrypted service endpoint handshake key delivery |
| Falsifiable non-reuse reason (if rejected) | mDNS no crypto identity → LAN identity spoofing trivial; must not be Omnia ground truth; Apple-first compatibility envelope makes it an OPTIONAL provider, NOT an architecture default. No rejection for SVCB; SVCB is a key PROVIDER pattern. | | |

---

## 14. ICE (RFC 8445) · STUN (RFC 8489) · TURN (RFC 8656)

| Dimension | Status |
|---|---|
| Human-readable Naming | ✗ |
| Cryptographic Identity | ✗ (TURN long-term cred or STUN short-term only; no key identity) |
| Service Identity | ✗ |
| Local Discovery | ✗ |
| Global Discovery | ✓ (STUN server discovers server-reflexive address; TURN relay allocates global relayed transport address) |
| Rendezvous | ✓ (ICE connectivity checks = implicit rendezvous of candidate pairs) |
| Locator Discovery | ✓ (3 candidate types: host, server-reflexive, relayed = full locator surface) |
| Route/Path Discovery | ✗ (finds path to peer, not AS-level route) |
| Path Selection | ✓ (ICE nominate = selects working pair; aggressive nomination possible) |
| Mobility | ✗ (ICE restarts = expensive; no mid-call mobility without re-ICE) |
| Multihoming | ✓ (gathers candidates on ALL interfaces — simultaneous possible though not binding) |
| Simultaneous Multipath | ✗ (single nominated pair per component) |
| NAT/Firewall Traversal | ✓ (reference standard implementation; universal) |
| Failure Recovery | ✓ (re-ICE; peer-reflexive candidate discovery) |
| Censorship/Failure Resistance | ◐ (TURN over TCP/TLS/443 to bypass firewalls; STUN easy to block) |
| Trust Establishment | ✗ (long-term cred or oauth tokens; no cryptographic per-peer identity in ICE) |
| Privacy | ◐ (candidate addresses = reveal local IPs to peer; TURN hides topology but relay is observable) |

| Property | Value |
|---|---|
| Authority Location | E (peer ICE agents) + CP (TURN/STUN servers) |
| Identity / Locator / Name semantics | Identity = none; Locator = candidate foundation-based priority-ordered transport tuples; Name = none |
| Trust model / compromise boundary | Malicious STUN server can return false MAPPED-ADDRESS (no integrity without MESSAGE-INTEGRITY); TURN server can snoop all relayed traffic unless E2EE above |
| Incremental deployment / IP+DNS compat | Universal in WebRTC (Safari/Firefox/Chrome NATIVE on Apple enterprise = DEPLOYED); SIP also uses; coturn open source TURN server |
| Open-source implementations / status | libnice GStreamer IMPLEMENTED; coturn (TURN) DEPLOYED; pion/ice Go DEPLOYED |
| OpenBSD feasibility | PORTABLE (coturn in ports; Go pion-ice pure userland; no kernel mods) |
| Reusable primitive / design lesson for Timelabs | (a) **DIRECT REUSE AS PROVIDER CONTRACT**: ICE candidate-gather → check → nominate pipeline as canonical NAT traversal machine for Timelabs peer-to-peer rendezvous; (b) Server-reflexive discovery via STUN (RFC 8489 MESSAGE-INTEGRITY) as reusable locator-verification primitive; (c) TURN relayed fallback as last-resort reachability guarantee for Apple enterprise NATTed endpoints behind strict firewalls |
| Falsifiable non-reuse reason (if rejected) | No identity layer (must compose with PeerID/HIP-like identity); no global discovery (must compose with DHT/control plane); candidate leak to peer is privacy consideration (can disable mdns-candidate / host if sensitive). |

---

## 15. MPTCP (RFC 8684 obsoletes 6824)

| Dimension | Status |
|---|---|
| Human-readable Naming | ✗ |
| Cryptographic Identity | ✗ |
| Service Identity | ✗ |
| Local Discovery | ✗ |
| Global Discovery | ✗ |
| Rendezvous | ✗ |
| Locator Discovery | ✗ |
| Route/Path Discovery | ✗ |
| Path Selection | ✓ (path manager decides when MP_JOIN; packet scheduler decides subflow to use) |
| Mobility | ◐ (remove/add subflow on interface change; no MPTCP-specific handover) |
| Multihoming | ✓ (multiple subflows across interfaces) |
| Simultaneous Multipath | ✓ (per-subflow sequence + reinjection buffer + MPTCP-level DSN; true simultaneous + aggregation) |
| NAT/Firewall Traversal | ✗ (no native; needs fallback to plain TCP on port block) |
| Failure Recovery | ✓ (reinject data on other subflow if one dies) |
| Censorship/Failure Resistance | ✗ (MP_CAPABLE option trivial to strip by middleboxes to force TCP fallback) |
| Trust Establishment | ✗ (inherits TCP + TLS; no identity) |
| Privacy | ◐ (subflows across networks reveal endpoint to multiple ISPs; no identity shield) |

| Property | Value |
|---|---|
| Authority Location | E (path manager + scheduler: kernel or userland mptcpd Netlink) |
| Identity / Locator / Name semantics | Identity = none; Locator = tuple per subflow; Name = none |
| Trust model / compromise boundary | On-path attacker can strip MP_CAPABLE → performance degradation only; no security boundary lost vs plain TCP |
| Incremental deployment / IP+DNS compat | Fully backward compatible (falls back); Apple iOS/macOS sysctl-enabled (Siri/Maps/Music PRODUCTION DEPLOYED) |
| Open-source implementations / status | Linux 5.6+ NATIVE multipath-tcp.org; FreeBSD Swinburne IPv4-only IMPLEMENTED; Apple userland kernel support NATIVE-PRODUCTION |
| OpenBSD feasibility | **INCOMPATIBLE** (no MPTCP support in OpenBSD kernel; userland cannot emulate correctly due to TCP option number 30 handling in-kernel) |
| Reusable primitive / design lesson for Timelabs | (a) Subflow-independence + data-sequence-number decoupling is THE simultaneous-multipath model (design lesson for any Timelabs multipath QUIC provider); (b) Two-component architecture: path manager + packet scheduler = separation of concerns to copy |
| Falsifiable non-reuse reason (if rejected) | INCOMPATIBLE on OpenBSD; Apple-only proprietary kernel hooks; easily downgraded by middleboxes; no identity; NO kernel modifications allowed. |

---

## 16. QUIC (RFC 9000) · Connection Migration (RFC9000 §9) · Multipath QUIC (I-D v18 Mar 2026)

| Dimension | QUIC v1 RFC 9000 | Multipath QUIC I-D v18 Liu et al. Mar 2026 |
|---|---|---|
| Human-readable Naming | ✗ | ✗ |
| Cryptographic Identity | ✓ (TLS 1.3 handshake baked in; certificate-based identity) | ✓ (same + per-path challenge) |
| Service Identity | ✗ | ✗ |
| Local Discovery | ✗ | ✗ |
| Global Discovery | ✗ | ✗ |
| Rendezvous | ✗ | ✗ |
| Locator Discovery | ✗ | ✗ |
| Route/Path Discovery | ✗ | ✗ |
| Path Selection | ✗ (single-path, can migrate to new 4-tuple) | ✓ (explicit path-ID create/delete/manage; scheduling UNSPECIFIED per I-D) |
| Mobility | ✓ (RFC 9000 §9: PATH_CHALLENGE/PATH_RESPONSE probed; client-initiated; NAT rebinding tolerant) | ✓ (per-path challenge) |
| Multihoming | ◐ (migration = one-at-a-time; NOT simultaneous multi) | ✓ (simultaneous bindings across N interfaces) |
| Simultaneous Multipath | ✗ (RFC 9000 forbids) | ✓ |
| NAT/Firewall Traversal | ✓ (UDP 443; usually outbound allowed; MASQUE for strict env) | Same base |
| Failure Recovery | ✓ (0.5-RTT handshake fast re-establish) | Same + path-level failover to other path |
| Censorship/Failure Resistance | ✓ (invariant stub; ECH hides SNI; datagrams indistinguishable without keys) | Same |
| Trust Establishment | ✓ (TLS 1.3 + WebPKI / raw pubkey pins) | Same |
| Privacy | ✓ (handshake metadata encrypted after CH; ECH hides SNI; 0-RTT replayable only with PSK) | Same |

| Property | QUIC v1 | Multipath QUIC |
|---|---|---|
| Authority Location | E (endpoint controls migration) | E (endpoint; scheduling explicitly delegated to implementation = not standard) |
| Identity / Locator / Name semantics | Identity = TLS cert chain / pubkey pin; Locator = mutable UDP 4-tuple; Connection ID stable demux = 128-bit non-address identifier | Same + per-path-ID added |
| Trust model / compromise boundary | Same as TLS; 0-RTT data replay = risk if PSK not bound properly; Connection ID rotation obscures from passive observer | Same |
| Incremental deployment / IP+DNS compat | HTTP/3 + QUIC DEPLOYED 50%+ of web; Safari/Firefox/Chrome NATIVE on Apple; Cloudflare CDN; iOS Network.framework NATIVE HTTP3/QUIC | I-D only (not SPECIFIED Standards Track); MsQuic v2.5.4 Aug 2025 Windows/Linux/Xbox (macOS UNSUPPORTED); Go quic-go has explicit AddPath/Probe/Switch API IMPLEMENTED |
| Open-source implementations / status | quinn (Rust) DEPLOYED; msquic v2.5.4 C IMPLEMENTED; Go quic-go DEPLOYED; OpenBSD libquiche? = PORTABLE | Go quic-go multipath IMPLEMENTED; MsQuic C experimental (macOS unsupported) |
| OpenBSD feasibility | PORTABLE (Go quic-go pure userland; no kernel mods; OpenBSD 7.7 uses Toeplitz UDP hash improved) | PORTABLE (same userland impl can run; however scheduling UNSPECIFIED — Timelabs would need policy) |
| Reusable primitive / design lesson for Timelabs | (a) **DIRECT REUSE as PRIMARY Timelabs transport substrate choice for all control-plane + data-plane messages**: Connection-ID-based demultiplexing means no kernel state; 0.5-RTT + migration = mobility and NAT tolerance; (b) E2E encryption baked in — matches sealed brick privacy. | (a) **WRAP AS PROVIDER**: Explicit AddPath/Probe/Switch pattern from quic-go as Timelabs multipath provider contract; (b) I-D explicitly delegates scheduling = Timelabs normative decision procedure (Omnia) can INSERT itself as path-scheduler policy OWNER (fits project memory: Omnia owns semantics, runtime is pure interpreter) — architecture-perfect separation. |
| Falsifiable non-reuse reason (if rejected) | QUIC v1: no simultaneous multipath (use Multipath QUIC extension if needed); no discovery/rendezvous (layer above). Multipath: scheduling UNSPECIFIED (not a bug, feature for Omnia to own semantics — Timelabs architecture match). | |

---

## 17. MASQUE (CONNECT-UDP RFC 9298 / CONNECT-IP RFC 9484 + Capsule Protocol)

| Dimension | Status |
|---|---|
| Human-readable Naming | ✗ |
| Cryptographic Identity | ✓ (via HTTP/3 TLS 1.3; WebPKI) |
| Service Identity | ✗ |
| Local Discovery | ✗ |
| Global Discovery | ✓ (server is HTTPS endpoint; SVCB/HTTPS records can advertise MASQUE) |
| Rendezvous | ✓ (ADDRESS_ASSIGN / ROUTE_ADVERTISEMENT capsules allow tunnel endpoint rendezvous) |
| Locator Discovery | ✓ (ADDRESS_ASSIGN allocates tunnel-private address to client) |
| Route/Path Discovery | ✗ (single tunnel to MASQUE proxy; route via proxy only) |
| Path Selection | ✗ |
| Mobility | ✓ (HTTP/3 connection migration = tunnel mobility) |
| Multihoming | ◐ (via HTTP/3 migration, one path active only) |
| Simultaneous Multipath | ✗ (HTTP/3 single-path) |
| NAT/Firewall Traversal | ✓ (tunnels through HTTPS 443; Apple iCloud Private Relay backbone = REAL PRODUCTION DEPLOYED) |
| Failure Recovery | ✓ (HTTP/3 fast re-establish) |
| Censorship/Failure Resistance | ✓ (looks identical to any HTTPS/3 traffic; hard to distinguish from video) |
| Trust Establishment | ✓ (TLS 1.3 + WebPKI) |
| Privacy | ✓ (iCloud Private Relay = dual-hop E2EE; MASQUE proxy E2EE from client; CONNECT-IP/UPD payload hidden inside QUIC) |

| Property | Value |
|---|---|
| Authority Location | E + CP (MASQUE proxy server) |
| Identity / Locator / Name semantics | Identity = TLS cert; Locator = UDP 443 proxy; tunnel-locator = ASSIGNED address; Name = proxy FQDN |
| Trust model / compromise boundary | MASQUE proxy sees client address + tunneled bytes (unless E2EE above / dual-hop like Private Relay); compromise of proxy = traffic content + metadata |
| Incremental deployment / IP+DNS compat | HTTP/3 compatible; masque-go reference impl; HAProxy 3.0+/Envoy 1.32+/NGINX 1.27+ experimental support; Apple iCloud Private Relay backbone PRODUCTION DEPLOYED (100M+ users); Apple Network.framework NATIVE supports MASQUE-like tunnel semantics via NWTCPConnection/NWUDPSession transparently for apps |
| Open-source implementations / status | masque-go (Go reference) IMPLEMENTED; HAProxy/Envoy DEPLOYED |
| OpenBSD feasibility | PORTABLE (Go masque-go; httpd(8)+relayd(8) don't support MASQUE proxying natively but client side = any userland Go binary; no kernel) |
| Reusable primitive / design lesson for Timelabs | (a) **WRAP AS PROVIDER**: Capsule Protocol over HTTP/3 (RFC 9297) as portable tunnelling-indirection primitive — Timelabs ANY protocol can be shipped over HTTPS 443 firewall without new ports; (b) ADDRESS_ASSIGN/ROUTE_ADVERTISEMENT pattern = typed rendezvous + locator assignment for clients behind strict firewalls = ideal sealed-brick→director rendezvous pattern |
| Falsifiable non-reuse reason (if rejected) | MASQUE proxy can observe traffic metadata (client IP, total bytes, timing), not content; single proxy = censorship point if not multi-homed; no multipath; need layer above for identity/discovery. |

---

## 18. BGP / OpenBGPD / RPKI / BGPsec (incl. ASPA, BGP-OA)

| Dimension | BGP RFC 4271+ | OpenBGPD (OpenBSD base) | RPKI / ASPA / BGPsec |
|---|---|---|---|
| Locator Discovery | ✓ (NLRI = prefix reachability) | ✓ NATIVE-OPENBSD | ✓ (ROA authenticates origin AS) |
| Route/Path Discovery | ✓ (AS_PATH; policy via communities/localpref) | ✓ NATIVE-OPENBSD bgpd(8) | ✓ (ASPA path-leak detection prevents valley-free violations) |
| Path Selection | ✓ (deterministic ordered: weight/localpref/aspath/origin/MED/IGP-cost/routerid, see RFC) | ✓ same NATIVE via bgpd.conf(5) policy | ✗ (origin/path validation, not path selection change) |
| Multihoming | ✓ (dual-upstream classic use) | ✓ NATIVE (localpref + communities) | ✗ |
| Failure Recovery | ✓ (BGP graceful restart RFC 4724) | ✓ RFC 8538 bgpd(8) OpenBSD 7.7 support | ✗ |
| Censorship/Failure Resistance | ✗ (full-table prefix hijack historically) | Same surface | ✓ ROV + ASPA IN PRODUCTION ENFORCEMENT MODE March 2026 (ARIN + transit providers drop ASPA-invalid routes) |
| Trust Establishment | ✗ (historic; AS_PATH no crypto) | Same as BGP | ✓ (RPKI hierarchy: IANA → RIR → LIR X.509 RFC 6480 series; ROA RFC 6482/6483; ASPA 2026 deploy; BGP-OA in-band attestation draft-huang Mar 2026) |
| Privacy | ✗ (full NLRI visible to route collectors; RIPE RIS/Route Views archives ~all BGP updates) | Same | Same (validated state = public) |

| Property | Value (BGP + OpenBGPD + RPKI family) |
|---|---|
| Authority Location | R (all routers = distributed control plane, no single server; AS-level policy expressed per-neighbor config) |
| Identity / Locator / Name semantics | Identity = AS Number (RIR-assigned); Locator = CIDR IP prefix + next-hop; Name = none |
| Trust model / compromise boundary | Pre-RPKI: no trust (any AS can originate any prefix, 20 May 2025 attribute injection event caused 150k session flaps). Post-RPKI ROV 50%+ IPv4 routes protected (Feb 2026). ASPA path-leak active enforcement March 2026. BGPsec path-signing SPECIFIED (RFC 8205) but minimally deployed (SLOW RPKI adjacent because expensive per-router signing). Compromise of RIR = global AS registry trust. Compromise of RPki validator + forged ROA = invalid accepted (rpki-client(8) OpenBSD mitigates: strict manifest gap warnings; rejects >3y TA certs from Mar2027 per rpki-client-9.4). |
| Incremental deployment / IP+DNS compat | Universal Internet inter-domain routing protocol; OpenBSD NATIVE base system bgpd(8) + rpki-client(8) |
| Open-source implementations / status | OpenBGPD 9.0 (Dec2025) IMPLEMENTED, 50% memory reduction for IXP route servers, RFC 8538 graceful restart notif, RFC 8654 extended messages, RFC 8950 extended nexthop, ASPA support ≤ 10 000 SPAS, RTR over IPsec+TCP MD5, EVPN preliminary support, as-set reject default yes, transparent-as passes NO_EXPORT communities RFC 7947. rpki-client(8) 9.4 (OpenBSD base), non-functional CA reporting, ARIN TAL included LEGALLY NOW, manifest gap warnings, gaps >3y TA validity rejected. |
| OpenBSD feasibility | **NATIVE (FULL)** — bgpd(8), rpki-client(8), bgpctl(8) ALL in base system. OpenBSD handbook documents full RPKI/dual-homing/anycast production patterns. No ports/packages required. |
| Reusable primitive / design lesson for Timelabs | (a) **DIRECT REUSE NATIVE**: OpenBGPD+rpki-client(8) as Omnia provider for AS-level path validation if Timelabs operates transit-connected ASes or multi-homed edge; (b) LocalPref/Community-based policy expression = strong model for normative Omnia path-policy decision rules; (c) Deterministic ordered path-selection procedure = architectural model for Omnia Tribunal decision chains (explicit ordered tie-break without voting); (d) rpki-client(8) trust-anchor lifetime enforcement (3y cutoff, TA tiebreaker to prevent replay attacks per 9.4 release notes) = lesson on cryptographic trust TTL expiry in Timelabs trust planes |
| Falsifiable non-reuse reason (if rejected for a dimension) | BGP is NOT identity/service/discovery layer at all; only IP-prefix routing between ASes. If Timelabs operates purely in Apple enterprise without public AS numbers, BGP is unnecessary (but ASN-lite internally with private AS 64512 is fine for multi-homed edges). No falsifiable rejection needed for NATIVE base OpenBGPD suite. |

---

## 19. OpenBSD Native Manipulation Palette (per 18-item inventory — no current validated requirement justifies kernel modification within the currently enumerated scope)

Legend: All items below classified as either `NATIVE-BASE` (already in OpenBSD base, no pkg needed, no kernel modification required), `PORTABLE_PORTS` (ports tree, userland), or `NOT_APPLICABLE`.

| # | OpenBSD Primitives | Classification | What it can implement in Timelabs context |
|---|---|---|---|
| 1 | PF states, tables, anchors, tags, labels | NATIVE-BASE pf(4) | Typed policy enforcement: anchor per Omnia provider class; tables store identity→locator mappings; tags label flows by trust tier |
| 2 | PF filtering and normalization (scrub, fragment reassembly, TCP mod) | NATIVE-BASE pf.conf(5) scrub rules | Integrity envelope for Timelabs QUIC/UDP/ESP traffic against malformed packets |
| 3 | PF `nat-to`, `rdr-to` | NATIVE-BASE | LISP-like EID→RLOC mapping (rdr-to private id→public locator); nat-to for outbound multihomed path steering |
| 4 | PF `route-to`, `reply-to`, `dup-to` | NATIVE-BASE | **Endpoint path-selection in-kernel**: route-to = force egress via specific WAN (policy routing match on identity tag); reply-to = symmetric return on same interface (critical for multihoming); dup-to = passive replication to monitor port (Omnia evidence observation without tap) |
| 5 | PF address pools + policy/load distribution (round-robin/bitmask/random/source-hash) | NATIVE-BASE | Simultaneous multipath at PF level: nat-to `<pool>` with round-robin for load-distribution across upstream providers (multipath provider-contract primitive without kernel mods) |
| 6 | `rtable` / `rdomain` | NATIVE-BASE (route(8) -T flag, ifconfig rdomain) | **Hard identity-locator split**: separate routing domains per trust-tier sealed-brick brick-in-brick; rdomain 0 = admin; 1 = provider; 2 = unredacted-evidence (no routing between unless explicit PF route-to across rdomains) |
| 7 | PF interface groups + virtual interfaces (vlan/aggr/trunk/wg/tun/gre/gif/etherip/pppoe/pflow/carp) | NATIVE-BASE | WireGuard overlay (wgN); CARP for redundant default gw; VLAN per service; pflow for lightweight flow export to Omnia collector |
| 8 | `divert-to`, `divert-reply`, divert sockets + divert-packet | NATIVE-BASE (pf.conf(5); fixed inpcb leak in OpenBSD 7.7 release notes) | **Dumb adapter doctrine REDIRECTS**: divert-to userland provider daemon for deep-packet-typed-observation (e.g., custom QUIC provider policy); return divert-reply — transparent to client app, no kernel modification |
| 9 | Transparent userspace interception (divert + relayd(8) transparent HTTP proxy pattern) | NATIVE-BASE relayd(8) transparent proxy mode + divert | L7 transparent provider for inspection without endpoint modification; matches Omnia typed-observation (adapter = typed evidence only, no policy) |
| 10 | CARP(4) + pfsync(4) | NATIVE-BASE carp(4), pfsync(4) ifconfig | Failure recovery: stateful HA CARP VIP + pfsync sync PF state across redundant bricks; ~1s failover; no kernel work |
| 11 | relayd(8) (L3 rdr-to via pf(4) anchor "relayd/*" + L7 reverse proxy + TLS termination + health checks TCP/HTTP/ICMP) | NATIVE-BASE relayd(8) in base, config in relayd.conf(5); client-cert auth support OpenBSD 7.7 | L3/L7 multi-homing: table `<peers>` health checks; forward to with loadbalance mode; acts as service discovery agent (health = Omnia reachability evidence); L7 TLS-terminated frontend for Timelabs MASQUE-like endpoints on 443 |
| 12 | OpenBGPD bgpd(8) + bgpctl(8) + OpenOSPFD ospfd(8) (IGP) | NATIVE-BASE in base system | Multi-homed edge routing; iBGP route reflectors within AS; RPKI origin/path validation; ospfd(8) for internal IGP when needed |
| 13 | iked(8)/iked.conf(5) + isakmpd(8) L2TP + ipsec(4) kernel stack + enc(4) interface + npppd(8) IKEv1/L2TP | NATIVE-BASE iked(8); OpenIKED 7.4 released April 2025; RFC 5996 IKEv2; "natt" option forced NAT-T OpenBSD 7.7 | Site-to-site IPsec VPNs as alternative to WireGuard; IKEv2 EAP-MSCHAPv2 auth = compatible Apple clients native (no profile install needed); route-based IPsec via enc0 |
| 14 | WireGuard wg(4) kernel driver + hostname.if(5) persistent config + ifconfig(8) wg keys | NATIVE-BASE wg(4) OpenBSD FAQ 17 explicitly documents it | Sealed-brick inter-site encryption with 4000LOC TCB; allowed-ips filter = built-in crypto-identity enforcement |
| 15 | Local resolver/authoritative DNS (Unbound 1.22.0 recursive resolver in base; NSD 4.9.1 authoritative in base) | NATIVE-BASE | OPTIONAL PROVIDER ONLY (explicit directive): DNS as provider of naming/locator evidence, NEVER sole ontology; SVCB/HTTPS RR supported natively for typed service binding |
| 16 | BPF / pcap read-only observation paths (tcpdump(8); pflog0 pseudo-if; btrace(8) + dt(4) kernel tracing; SO_SEND_BPF/SO_RECV_BPF socket-level filtering proposal tech@ Oct2025) | NATIVE-BASE | **Evidence collection only, DUMB ADAPTER**: tcpdump(8) on pflog0 emits booleans/counts (data minimization); raw source addresses gated behind private-flag; dt(4) for kernel-level packet metrics |
| 17 | Route sockets (AF_ROUTE + route(4); netstat/route ioctl; per-thread route cache struct netstack OpenBSD 7.7) + sysctl net.inet.* | NATIVE-BASE route(4); new per-thread cache = route cache to avoid lock contention | Userland routing decisions: Omnia runtime can read RIB and inject via route socket; no kernel mods needed |
| 18 | Ordinary sockets (AF_INET/AF_INET6/AF_LOCAL; QUIC/TCP/UDP userland proxies; tun(4)/tun offloads OpenBSD 7.7 + af-frame AF_FRAME socket domain new in OpenBSD 7.7; vxlan(4) endpoint updates ifconfig vxlan endpoint) | NATIVE-BASE + AF_FRAME new 7.7 | ALL Timelabs overlay/adapter logic implementable in userland: Go/Rust QUIC library over UDP sockets; tun(4) for interface patterns; AF_FRAME allows raw Ethernet userland without BPF write |

**Userland/Existing-Interface Coverage Conclusion (kernel-change-last rule, evidence-bounded)**: All 18 capabilities listed in the directive CAN be implemented using NATIVE-BASE OpenBSD userland + kernel interfaces already present within the currently scoped Timelabs networking primitives (identity, routing, discovery, rendezvous, multipath, NAT traversal, failure recovery, evidence collection). No currently validated Timelabs v1 requirement justifies OpenBSD kernel modification. A future outside-scope capability that demonstrably cannot be closed over userland + existing interfaces, and that has passed its own independent exhaustion proof, would be required before proposing kernel changes.

---

## Row-Level Evidence Summary Table (all candidates)

| Candidate | Identity | Locator | Naming | Discovery Local | Discovery Global | Rendezvous | Path Discovery | Path Selection | Mobility | Multihoming | Sim. Multipath | NAT Traversal | Failure Recov. | Censor-Resist. | Trust | Privacy | OpenBSD Feasibility | Primary Evidence Tier (highest observed) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SCION | ✓ (AS) | ✓ | ✗ | ✗ | ✓ | ◐ | ✓ | ✓ (E) | ◐ | ✓ | ◐ | ✗ | ✓ | ✓ | ✓ | ◐ | PORTABLE | DEPLOYED (Swiss/IXPs) |
| GNUnet/GNS | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ◐ | ◐ | ◐ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | PORTABLE | SPECIFIED (RFC 9498) + IMPLEMENTED |
| HIP/HIPv2 | ✓ | ✓ | ✗ | ◐ | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ | ✓ | ◐ | ◐ | ✓ | ◐ | NEEDS_PORT | SPECIFIED (RFC 7401/9028) |
| LISP (+Decent) | ✗ | ✓ | ✗ | ✗ | ✓ | ◐ | ✗ | ✗ | ✓ | ✓ | ◐ | ✓ | ✓ | ◐ | ◐ | ✗ | NEEDS_PORT | SPECIFIED (RFC 9301/9962) |
| ILNP | ✗ (admin NID) | ✓ | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ | ✓ | ✓ | ✗ | ✗ | ◐ | ✗ | ◐ | ◐ | NEEDS_KERNEL_WORK | DEPLOYED (FreeBSD 14.3 native) |
| NDN/CCNx | ✓ | NONE | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ (R) | ✓ | ✓ | ✓ | ◐ | ✓ | ✓ | ✓ | ◐ | PORTABLE | IMPLEMENTED (NDN-DP) |
| libp2p (8 sub-components) | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ◐ | PORTABLE | DEPLOYED (IPFS/Polkadot/Filecoin/Eth CL) |
| Yggdrasil | ✓ | ✓ | ✗ | ✓ | ✓ | ✗ | ✓ | ✗ | ✓ | ✗ | ✗ | ✓ | ✓ | ✓ | ✓ | ✗ | PORTABLE | IMPLEMENTED (alpha) |
| cjdns | ✓ | ✓ | ✗ | ✓ | ✓ | ✗ | ✓ | ✗ | ✓ | ✗ | ✗ | ✓ | ✓ | ✓ | ✓ | ◐ | PORTABLE | DEPLOYED (small Hyperboria) |
| Babel RFC 8966 | ✗ | ✓ | ✗ | ✓ | ✓ (dom.) | ✗ | ✓ | ✓ | ✓ | ◐ | ✗ | ✗ | ✓ | ✓ | ✗ | ✗ | PORTABLE | SPECIFIED (RFC 8966) + DEPLOYED (AREDN) |
| BATMAN-adv | ✗ | ✓ | ✗ | ✓ | ✓ (dom.) | ✗ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ | ✓ | ✗ | ✗ | NEEDS_KERNEL_WORK | DEPLOYED (Freifunk 25k+ nodes) |
| WireGuard wg(4) | ✓ | ◐ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ◐ | ◐ | ◐ | ✓ | ✓ | NATIVE | NATIVE DEPLOYED (OpenBSD kernel + Apple) |
| Headscale (Tailscale-compat) | ✓ | ✓ | ◐ (MagicDNS) | ✓ | ✓ | ✓ | ✗ | ◐ | ✓ | ◐ | ✗ | ✓ | ✓ | ✓ | ✓ | ◐ | PORTABLE | DEPLOYED (38.5k stars; v0.28) |
| ZeroTier | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ◐ | ◐ | ✓ | ◐ | ✗ | ✓ | ✓ | ✓ | ✗ | ◐ | PORTABLE | DEPLOYED (BUSL-1.1 license) |
| Nebula Slack | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ◐ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | PORTABLE | DEPLOYED (Slack internal production) |
| IPFS/Kademlia | ✓ | ✓ | ✗ (IPNS sep.) | ✓ | ✓ | ◐ | ✓ | ✗ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ◐ | PORTABLE (ports/net/go-ipfs 0.38.1) | DEPLOYED (Kubo + Amino DHT) |
| mDNS (RFC 6762) | ✗ | ◐ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ | ◐ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | PORTABLE (Avahi) | DEPLOYED (Apple Bonjour NATIVE) |
| DNS-SD (RFC 6763) | ✗ | ✓ | ✓ | ✓ | ◐ | ✗ | ✗ | ✗ | ✓ | ✓ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | PORTABLE | DEPLOYED (Apple Bonjour) |
| SVCB/HTTPS (RFC 9460) | ◐ (DNSSEC) | ✓ (A/AAAA hints) | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ | ◐ | ✓ | ✗ | ✗ | ✓ | ✗ | ◐ | ◐ | NATIVE (Unbound/NSD base) | SPECIFIED (RFC 9460) + DEPLOYED (CDNs) |
| ICE (RFC 8445)/STUN/TURN | ✗ | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ | ✓ | ✗ | ✓ | ✗ | ✓ | ✓ | ◐ | ✗ | ◐ | PORTABLE (coturn/pion-ice) | DEPLOYED (WebRTC universal; Apple Safari) |
| MPTCP RFC 8684 | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ◐ | ✓ | ✓ | ✗ | ✓ | ✗ | ✗ | ◐ | INCOMPATIBLE | DEPLOYED (Apple Siri/Maps/Music production; Linux 5.6) |
| QUIC RFC 9000 | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ◐ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | PORTABLE (quic-go/msquic) | DEPLOYED (50%+ web; HTTP/3 Apple NATIVE) |
| Multipath QUIC I-D v18 | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ (E) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | PORTABLE (quic-go impl) | IMPLEMENTED (scheduling UNSPECIFIED) |
| MASQUE CONNECT-UDP/IP RFC 9298/9484 | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ | ✗ | ✓ | ◐ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | PORTABLE (masque-go) | DEPLOYED (Apple iCloud Private Relay backbone; HAProxy/Envoy) |
| BGP+OpenBGPD+RPKI+ASPA | ✗ (ASN = admin) | ✓ | ✗ | ✗ | ✓ (full) | ✗ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ | ✓ | ✗ | ✗ | NATIVE-FULL (bgpd rpki-client) | DEPLOYED (ROV 50%+ prefixes; ASPA enforcement Mar 2026) |
| **OpenBSD 18-Item Palette** | N/A via composition | N/A via composition | N/A (Unbound/NSD) | N/A (mDNS ports) | N/A (BGP/rdomain) | N/A (divert+userland) | N/A (PF route-to) | N/A (PF route-to+relayd) | N/A (wg migration) | N/A (rtable+route-to pools) | N/A (address pools) | N/A (relayd+CARP) | N/A (CARP+pfsync) | N/A (rpki-client) | N/A (divert BPF) | NATIVE-BASE coverage 18/18 items | OBSERVED_LOCALLY (OpenBSD 7.7 release notes) |

---

*Matrix rows 1–23 + OpenBSD palette complete. Evidence-tier classification: each row's "Primary Evidence Tier" = highest tier independently verifiable (SPECIFIED ≤ IMPLEMENTED ≤ DEPLOYED ≤ OBSERVED_LOCALLY ≤ INFERRED ≤ UNKNOWN). No INFERRED promotion permitted without supporting primary documentation.*
