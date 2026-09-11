# Technical reset

12 September 2026 · Technical refinement only · Implementation remains locked

This package is the current reference for the desktop, connection and file requirements. All current macOS prototypes are discarded as the product baseline. Earlier reviews remain historical evidence; their directions to repair, preserve or extend a prototype are superseded. No new macOS/product implementation follows from this package until the technical contract converges and its implementation gate is accepted. LIT oracle work and engine qualification follow their separate prerequisite gates.

The immediate work is to define the actual connection chain, application control boundaries, failure behavior and admissible evidence. Network continuity is the current critical workstream, not the full beta release. The requested beta still includes iCloud Drive, Google Drive, OneDrive, S3/MinIO, Mac folders, Windows folders and NAS, with the accepted sync and archive behavior. Each requires its own acceptance evidence.

## Read in this order

1. [Technical contract](TECHNICAL_CONTRACT.md): useful outcomes, ownership, change behavior and implementation gates.
2. [LIT-001 admission gate](LIT_GATE.md): the recovered candidate, source-level incompatibilities and required verification sequence.
3. [Network contract](NETWORK_CONTRACT.md): deployment profiles, application scope, continuity and proof gates.
4. [Requirements register](REQUIREMENTS.md): accepted network, window, provider, sync, archive and maintenance requirements.
5. [Verification status](VERIFICATION_STATUS.json): proposed, blocked and unexecuted states.
6. [Source digests](SOURCE_DIGESTS.json): identities of reviewed source bytes, using relative paths and source aliases.

## Binding constraints

- Preserve ongoing application work during refinement. Planned policy changes must not close existing connections; external failures still require an explicit recovery contract.
- Keep SCION and GNS3 behavior distinct from any application adapter or controller. Configuration, effective policy and useful traffic require separate evidence.
- Make the main work window normally movable, resizable, minimizable and keyboard accessible. A tray popup is optional compact status; genuine System Settings integration is native configuration.
- Use plain English product labels. Timelabs belongs only in About or legal information, never product navigation.
- Treat NDI as a reference toolkit, not a beta runtime dependency.

## Evidence limits

The recovered LIT review candidate is **NOT_FROZEN**. No implementation has been admitted against it, no compliant publication receipt has been issued for this reset, and no accepted LIT chain is claimed. Source comparison is not runtime conformance. An ordinary file hash is not a LIT receipt, proof of truth, application success or a release certificate.

This public package contains technical requirements and sanitized review conclusions. It contains no private host setup, account credentials, raw runtime logs or executable product changes. Historical source documents and their hashes identify what was reviewed; they do not imply that the source itself is included here. Private evidence stays outside this repository.

Return to the [guides index](../../../../../../docs/README.md) or [AI helper guide](../../../../../../docs/ai-helper.md).
