# TIMELABS_WORLD_MODEL_NEIGHBOURS

## HME / WorldEngine semantic-neighbour map

| Timelabs primitive | Close neighbours | Mechanism equivalence |
|---|---|---|
| CausalFrame (source + validity + freshness) | digital twin telemetry envelopes, robotics observation messages, event-sourcing envelopes | typed observation boundary with provenance and quality metadata |
| FeatureFrame | control-theory state estimation, simulation feature extraction | normalized bounded features feeding transition logic |
| StateMembrane | hysteresis state machines, supervisory control modes | dwell/hysteresis boundary preventing unstable transitions |
| WaveCell/WaveField | procedural animation kernels, oscillator banks, signal-driven control | deterministic modulation from state/features to actuation channels |
| BodyChannel graph | ECS component mapping, rig parameter buses | sparse linear binding from abstract state to embodiment channels |
| PoseFrame | deterministic simulation frame contracts | serializable authoritative output for rendering/actuation |
| EvidenceChain | transparency/event logs + reproducible simulations | replay-verifiable run history with hash integrity |

## Cross-discipline neighbours
- **ECS/game simulation kernels:** deterministic fixed-tick update loops.
- **Digital twins:** shadow/replay workflows before real mutation.
- **Robotics world representations:** map/pose/state confidence decomposition.
- **State-machine formalisms:** explicit transitions with guards/dwell.
- **Agent-based modeling + ALife:** emergent behavior under constrained rules.
- **Differentiable world models:** useful comparator, but often weaker on hard determinism contracts.

## Chinese world/embodiment ontology deltas
- **世界模型** in Chinese literature is frequently fused with **具身智能** closed-loop behavior, broader than latent predictive model framing.
- **虚实融合 / 数字孪生** framing emphasizes continuous bridge between simulation and operational system, supporting Timelabs replay-before-mutate motif.
- **多智能体 + 群体智能** vocabulary often distinguishes coordination strategy layers that Timelabs currently compresses under general “agent” language.
