# State and data contracts

Model draft, 12 September 2026. These diagrams describe requested responsibilities and data. They do not define a new SCION topology or establish that the backend exists. The menu bar app (`MenuBarExtra`) and native settings pane (`NSPreferencePane`) are the integration surfaces described by the product review; their presence does not establish these synchronization capabilities. Services in the diagrams are logical responsibilities, not a requirement to create separate processes.

See the [technical specification](technical-spec.md) for scope and the [monitor and action registry](registry.md) for requirement IDs. All identifiers below are generic contract fields. Public examples must not contain real host, account, credential, key, or private resource values.

## Mapping and archive model

```mermaid
classDiagram
    class Endpoint {
        endpointID
        providerType
        accountReference
        capabilities
        observationFreshness
    }
    class Mapping {
        mappingID
        policyRevision
        direction = bidirectional
        conflictPolicy = preserveBoth
        exclusions
        pause()
        resume()
    }
    class TransferOperation {
        operationID
        sourceVersion
        expectedDestinationVersion
        checkpoint
        verificationResult
        reconcile()
    }
    class ArchivePolicy {
        scope = userFiles
        exclusions
        retention
        quota
    }
    class ArchiveSnapshot {
        snapshotID
        encryptedManifest
        objectReferences
        commitEvidence
        restoreVerification
    }
    class ExistingProfile {
        storageProfileReference
        credentialReference
        keyProviderReference
        recoveryPolicyReference
    }
    Mapping "0..*" --> "2" Endpoint : source and destination
    Mapping "1" --> "0..*" TransferOperation : owns
    ArchivePolicy "1" --> "0..*" ArchiveSnapshot : retains
    ArchivePolicy --> ExistingProfile : default
    TransferOperation --> ExistingProfile : resolves credentials
    ArchiveSnapshot --> TransferOperation : upload and verify
```

The two endpoints in a mapping are two roles. They must not resolve to the same underlying resource scope. Archive scope is broader than the selected synchronization roots. `ExistingProfile` holds references, not secret values. These fields and relationships are requirements to validate against the actual provider adapters.

## Operation states

```mermaid
stateDiagram-v2
    [*] --> Planned
    Planned --> Queued: preview and policy validated
    Queued --> Transferring: dependencies available
    Transferring --> Verifying: destination reports completion
    Verifying --> Committed: version and integrity verified
    Transferring --> Reconciling: connection lost or result uncertain
    Reconciling --> Queued: resume or retry is safe
    Reconciling --> Verifying: prior write found
    Reconciling --> Conflict: versions diverged
    Verifying --> Conflict: destination changed
    Queued --> Paused: quota or user policy
    Transferring --> Paused: safe pause checkpoint
    Paused --> Reconciling: resume
    Conflict --> Planned: resolution preserves both versions
    Verifying --> Failed: integrity failure
    Committed --> [*]
```

`Committed` records a completed operation. A later change can make the mapping diverge again without changing that historical result. A separate health state reports unavailable or stale observations; it must not rewrite operation history. An `ArchiveSnapshot` becomes committed only after all required objects and its manifest have been confirmed.

## Shared state across the two interfaces

```mermaid
sequenceDiagram
    actor User
    participant Pane as Native settings pane
    participant Menu as Menu bar app
    participant Control as Existing coordinator and typed contract
    participant Executor as Mapping executor
    participant Provider as Destination adapter
    User->>Pane: Enable mapping after preview
    Pane->>Control: mapping ID + policy revision + request ID
    Control->>Executor: persist accepted operation
    Executor-->>Control: operation ID / queued
    Control-->>Pane: accepted, pending
    Control-->>Menu: same operation / queued
    Executor->>Provider: version-aware write
    alt Destination unchanged
        Provider-->>Executor: result + version evidence
        Executor->>Executor: verify and persist commit
        Executor-->>Control: committed evidence
    else Changed or uncertain
        Provider-->>Executor: conflict / timeout
        Executor->>Executor: reconcile or preserve both
        Executor-->>Control: unresolved with reason
    end
    Control-->>Pane: shared observed state
    Control-->>Menu: shared observed state
```

An interface may close after an operation is accepted. Execution and the durable queue remain the executor's responsibility. A command is not successfully completed merely because a button changed state. Both interfaces must report the same operation and observed result.
