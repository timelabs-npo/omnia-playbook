# omnia-playbook ↔ Blueshoes flow evolution link

This semantic/red-team branch is paired with:

- repository: `timelabs-npo/Blueshoes`
- branch: `evolution/clashmac-flow-observation-v1`
- Blueshoes base head: `00a59701b97e49e49b7b83c5df974533cdeae255`
- ClashMac behavioral reference: `666OS/ClashMac@6bd4eee77ac3face93d6ba38fdc505e15a4e376e`

The shared target is a clean-room, cross-platform observation contract. `FlowObservationV1` is observation-only and cannot authorize mutation.

Blueshoes may consume validated observations into its Flow Graph / Flow Surgery model. Any later mutation proposal still requires typed capability semantics, host policy, native adapter execution, and a durable receipt.

## Read-only implementation evidence

The first slice is implemented in the standalone Blueshoes `runtime/flow-observation`
crate at tested implementation `32307237d4c5c305b6cbb2509503a8cea9d5758e`.
It pins this repository's data/schema corpus at
`30002c67533258691203391b4f0c30a3125d8e23`, with no validator/oracle code import.
See [corpus evidence](FLOW_OBSERVATION_EVIDENCE.md) for 49 independent cases,
cross-platform/native gate distinctions and the explicit nullable-counter revision.
The first Flow Graph is observation_only and introduces no mutation capability.
