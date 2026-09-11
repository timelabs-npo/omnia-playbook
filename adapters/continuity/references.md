# Reference notes for continuity tooling

These references explain useful capabilities and their limits. They are not evidence that a tool is installed, integrated, or working in a deployment. Tool and vendor names identify sources, not product labels. NDI remains a reference for observability and control; this document does not propose an NDI implementation.

Research reviewed: 12 September 2026. Check the installed version, operating system, edition, and license before relying on a capability.

## NDI: what can be observed and controlled

NDI separates source discovery, receiver behavior, media measurement, and configuration. This is a useful model for presenting precise evidence instead of a single global “online” indicator.

| Reference | What it exposes or controls | Relevant limit |
| --- | --- | --- |
| [Discovery](https://docs.ndi.video/all/using-ndi/ndi-tools/ndi-tools-for-windows/discovery) | Registered sources and receivers, host grouping, addresses, and source selection. Receiver control depends on advertising and control being enabled. | Registration does not prove media delivery. A discovery server is not a media relay. |
| [Studio Monitor](https://docs.ndi.video/all/using-ndi/ndi-tools/ndi-tools-for-windows/studio-monitor) and [Video Monitor](https://docs.ndi.video/all/using-ndi/ndi-tools/ndi-tools-for-mac/video-monitor) | Preview an actual stream; expose supported viewing, recording, and device controls. | Windows and macOS tools have different capabilities. A preview verifies that receiver and stream, not the entire network. |
| [Access Manager](https://docs.ndi.video/all/using-ndi/ndi-tools/ndi-tools-for-windows/access-manager) | Discovery, groups, and network configuration for NDI applications. | Saved configuration and applied runtime state are separate facts. A configuration interface is not evidence of successful delivery. |
| [Analysis](https://docs.ndi.video/all/using-ndi/utilities/analysis) | A diagnostic receiver reporting formats, frame arrival timing and sizes, with console and CSV output. | It adds receiver traffic and does not render the stream. Arrival variation is not end-to-end display latency. |
| [Router](https://docs.ndi.video/all/using-ndi/ndi-tools/ndi-tools-for-windows/router) | Selects sources for virtual outputs and saves routing presets. | It is an NDI source-selection tool, not a general IP router. Media need not pass through the Router application. |
| [Bridge](https://docs.ndi.video/all/using-ndi/ndi-tools/ndi-tools-for-windows/bridge) | Shares NDI sources between networks using host/join operation and configuration. | The desktop tool and the separately documented Bridge Service are distinct surfaces. |
| [Bridge Service API](https://docs.ndi.video/all/developing-with-ndi/utilities/bridge-service/api), [WebSockets](https://docs.ndi.video/all/developing-with-ndi/utilities/bridge-service/websockets), and [webhooks](https://docs.ndi.video/all/developing-with-ndi/utilities/bridge-service/webhooks) | Configuration, service state, start/stop and connection tests; event and log delivery. | Service availability is separate from a particular media session. Do not assume the service is available on every operating system. |
| [Platform tool comparison](https://docs.ndi.video/all/using-ndi/ndi-tools/ndi-tools-for-mac-vs-windows) | Test Patterns supplies a controlled source; capture tools publish desktop content; virtual camera tools consume streams. | Source, transport, and consumer are different roles. Windows/macOS tool availability and feature parity must be checked. |

The [receiver SDK](https://docs.ndi.video/all/developing-with-ndi/sdk/ndi-recv) exposes connection counts, frame queues, and received/dropped frame counters. A dropped frame counter can indicate that the application is not consuming frames quickly enough; it is not an IP packet-loss measurement. Queue lengths count frames, not milliseconds. An allocated receiver object alone does not establish a working connection.

The [discovery, monitoring, and control APIs](https://docs.ndi.video/all/developing-with-ndi/sdk/ndi-recv-discovery-monitor-and-control) distinguish advertising, listening, and permission to control. Some event monitoring and command capabilities require the Advanced SDK. Availability must be checked before a UI promises control. NDI measurements do not establish SCION path health, GNS3 readiness, or general operating-system health.

## Mole: useful maintenance patterns

The reviewed [Mole CLI source](https://github.com/tw93/Mole/blob/2ab192fb59674d12f95b95d46a13b956c50e8b1a/README.md) provides JSON interfaces for status, analysis, and history, plus a persistent status watch mode. Its [watch implementation](https://github.com/tw93/Mole/blob/2ab192fb59674d12f95b95d46a13b956c50e8b1a/cmd/status/watch.go) is a useful reference for retaining a collector instead of starting a fresh process for every UI refresh. These links pin the reviewed source; they do not claim to represent the latest release.

Mole's [network summary](https://github.com/tw93/Mole/blob/2ab192fb59674d12f95b95d46a13b956c50e8b1a/cmd/status/metrics_network.go) filters interfaces and limits the displayed set. It cannot serve as a complete tunnel or interface inventory. Consumers should define units, observation time, collection errors, and stale values explicitly; an absent measurement must not become a healthy zero.

The [maintenance safety review](https://github.com/tw93/Mole/blob/2ab192fb59674d12f95b95d46a13b956c50e8b1a/SECURITY_AUDIT.md) offers useful patterns: identify protected paths, check active owners, and skip uncertain or busy targets. These patterns do not authorize unrestricted cleanup. An autonomous action still needs a bounded target, active-transfer guards, a result check, and a recorded outcome. The CLI and [native application](https://mole.fit/) are separate artifacts; do not infer a supported automation API from a graphical control.

## Provider differences that affect synchronization

Requested provider coverage is a requirements scope, not a claim of complete connector support. Each connector needs a tested capability profile.

| Provider or source | Contract to preserve |
| --- | --- |
| iCloud Drive | [CloudKit](https://developer.apple.com/icloud/cloudkit/) provides application containers; it is not a generic interface to every file in a user's iCloud Drive. A locally visible item may require [Download Now or Keep Downloaded](https://support.apple.com/en-gb/guide/mac-help/mchl1a02d711/26/mac/26). Distinguish file discovery, readable local bytes, and confirmed remote persistence. |
| Google Drive | Use stable file identity and [change records](https://developers.google.com/workspace/drive/api/reference/rest/v3/changes). A removal can mean lost access, not deletion. [Binary download and native-document export](https://developers.google.com/workspace/drive/api/guides/manage-downloads) are different operations; an exported representation is not a guaranteed lossless native-document round trip. |
| OneDrive | Preserve drive/item identity and [delta cursors](https://learn.microsoft.com/en-us/graph/api/driveitem-delta?view=graph-rest-1.0). Delta results describe state changes, not a complete event history. [Upload sessions](https://learn.microsoft.com/en-us/graph/api/driveitem-createuploadsession?view=graph-rest-1.0) have expiration, resume state, conflict behavior, and conditional requests that must be handled explicitly. |
| Amazon S3 | Bucket keys are object names, not filesystem identities. Use the applicable [conditional writes](https://docs.aws.amazon.com/AmazonS3/latest/userguide/conditional-writes.html), checksums, and reconciliation. [Multipart ETags are not whole-object MD5 hashes](https://docs.aws.amazon.com/AmazonS3/latest/userguide/checking-object-integrity-upload.html). [Versioning](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html) and retention are separate policies. |
| MinIO / AIStor | Treat [S3 compatibility](https://docs.min.io/aistor/developers/s3-api-compatibility/) as a documented capability set. Record the actual server release and edition; test needed operations rather than assuming every AWS behavior or current AIStor feature exists in another deployment. |
| Local macOS and Windows folders | Use explicit roots and OS permissions. Test case sensitivity, Unicode names, links, locking, rename behavior, and metadata preservation. A Windows folder accessed through WSL is a separate access path with its own behavior to verify. |
| NAS | [SMB access](https://support.apple.com/guide/mac-help/connect-to-a-windows-computer-from-a-mac-mchlp1660/mac) provides a mounted share, not a universal NAS API. Verify server identity, reconnect behavior, permissions, supported metadata, and interrupted writes for each supported access method. |

All connectors must distinguish listing failure, lost permission, missing content, and a confirmed deletion. Pagination and cursors need durable checkpoints. A resumed upload must still refer to the intended source version. Provider identifiers and ETags are not interchangeable with content-integrity checks.

## Synchronization, archive, and source boundaries

The selected synchronization policy is bidirectional synchronization of configured folders, preserving both versions on conflict. Each mapping needs stable endpoints, an explicit delete policy, durable pending work, and evidence that a completed write contains the expected content. Hydrating a placeholder, evicting a recoverable local cache, and deleting authoritative data are separate actions.

Archive coverage is all user files, subject to configurable exclusions and actual access permissions. Coverage must report unreadable, unavailable, or excluded items; a file name alone does not prove its contents were archived. Synchronization is not a substitute for independently recoverable history.

[Git stash](https://git-scm.com/docs/git-stash) distinguishes tracked changes from optional untracked and ignored content. An archive collector must preserve existing source state; it must not create, pop, drop, or reset a stash merely to collect it. Arbitrary files are not automatically Git stashes.

Git is neither encryption nor unlimited storage. [Git LFS](https://git-lfs.com/) separates repository pointers from payload storage, which still has capacity, availability, and cost limits. An encrypted archive needs protected payloads and sensitive manifests, recoverable keys, version identity, retention, quota handling, and restore verification. The [restic threat model](https://restic.readthedocs.io/en/stable/100_references.html#threat-model) is a useful reference for authenticated encrypted backup and its limits; it is not a mandated replacement backend. Use the existing configured backend and key scheme as the starting point, with private configuration kept outside public documentation and repositories.

Provider API traffic does not automatically traverse SCION because SCION is present. Stock [SCION IP Gateway](https://docs.scion.org/en/latest/sig.html) documents a specific IP connectivity mechanism. Route selection and successful end-to-end transfer need separate evidence. UI availability, discovery, an accepted command, and a verified data result should remain distinct observations.
