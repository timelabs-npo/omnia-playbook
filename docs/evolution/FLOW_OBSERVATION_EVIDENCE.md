# Independent Flow Observation corpus evidence

Tested corpus head: `30002c67533258691203391b4f0c30a3125d8e23`.
Paired tested Blueshoes implementation: `32307237d4c5c305b6cbb2509503a8cea9d5758e`.
Final documentation heads and CI states are kept in
[Blueshoes PR 9](https://github.com/timelabs-npo/Blueshoes/pull/9) and
[omnia-playbook PR 10](https://github.com/timelabs-npo/omnia-playbook/pull/10).

`python -m unittest discover -s tests -p 'test_*.py' -v`: PASS, 7 test methods,
including 49 independent data cases. Python 3.14.6, jsonschema 4.26.0 and
rfc3339-validator 0.1.4 were used locally. The date-time checker is mandatory;
tests fail closed when the optional checker is missing. The independent
[semantic-fixture CI](https://github.com/timelabs-npo/omnia-playbook/actions/runs/34000521436)
also passed. This repository imports no Blueshoes producer or graph implementation.

Corpus scope: equivalent Darwin/Windows/Linux/OpenBSD DTOs; PID reuse and rebinding;
missing identity; zero/unknown counters; stale/unknown/future time; masked display
separation; inert action-looking text; rejected raw-action fields; listener unknown
peers; IPv6 scopes; duplicate IDs/keys; exact u64 birth boundaries; integer-token
profile differences; NetBSD wire compatibility and nullable-counter compatibility.

Independent reviews found and corrected a rounded birth maximum and a numeric
lexeme profile mismatch before the final pin. The corpus includes the controls
that reproduce those defects. Blueshoes also corrected an ignored inert duplicate-key
fixture and verifies every pinned file is actually tracked in Git.

Wire schema SHA-256 (LF bytes):
`857de52ca0b7bb6ba6edbabccf753cbca59b5b1e884b819a2d57bbc4a7e81c2c`.
Original integer-only schema Git blob: `35d7b12f2cb2f14b9fc2e672504bb19f5f7df552`.
The revised schema accepts old valid V1 documents; old validators reject new null
byte counters. Rust's bounded integer-token profile is distinct from JSON Schema's
mathematical integer semantics. See [contract](FLOW_OBSERVATION_CONTRACT.md).

Portable fixture PASS never upgrades a native platform gate. This corpus's native
gates remain NOT_EXECUTED for all four platforms. The paired Blueshoes implementation
has separate Windows TCP IPv4/IPv6 native/schema receipts: 19 Rust tests, 5 boundary
tests and actual native graph projection. Darwin/Linux/OpenBSD collectors remain
stubs. Windows UDP, counters/rates, policy/route, initiation direction and atomic
socket identity/continuity remain NOT_EXECUTED. Endpoints use local/remote orientation;
graph edges express association with unknown traffic direction.

Full repository validation is still FAIL: required paths `checks/routing`,
`checks/connectivity`, `checks/certificates`, `checks/secrets`, `checks/system` are
missing, as at the starting head. Internal markdown links pass. Local read-only
`scripts/diagnose.sh` passes on Windows. The host lacks make, so its underlying
Python/Bash targets were executed directly. These baseline gaps are not represented
as a Flow Observation gate PASS.

No mutation capability, network changes, helper execution, main merge or audit/Kudu
branch edit was introduced. ClashMac is only the closed-source behavioral reference
`666OS/ClashMac@6bd4eee77ac3face93d6ba38fdc505e15a4e376e`; no source/assets/binaries imported.
