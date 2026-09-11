# Continuity: system care and file management

Status: descriptive requirements, 12 September 2026. These are accepted product directions and required checks, not a claim that omnia-playbook runs a sync, archive, maintenance, or routing service. Product-specific review material belongs under adapters; this document defines behavior.

## Outcome

Help a person keep working while their selected files move between locations, with clear handling of outages, conflicts, storage limits and recovery. The interface should answer: Is work continuing? Where are my files going? What needs my attention?

The first deployment has a Mac as the main workspace and a Windows/WSL helper. Preserve the real System Settings pane and use the menu bar for common status. A separate window is useful only when detailed work needs more room. Do not copy the operating system's account sidebar into an app and call it System Settings.

## Required scope

- Locations: iCloud Drive, Google Drive, OneDrive, S3/MinIO, local Mac/Windows folders, and NAS. Each adapter must state its actual capabilities; being listed is not being connected.
- Selected folder pairs use two-way sync and keep conflicting versions. Never silently replace this with one-way overwrite.
- The private archive covers all user files with editable exclusions, including Git stashes and untracked work. Apply access grants explicitly and show anything that could not be read.
- Reuse the existing storage/key arrangement as the default once its non-secret settings are identified. Do not invent a new arrangement or copy credentials into Git.
- Automatic care applies to approved known resources and owned services. Respect active writes, queued transfers, archive work and recovery records.
- NDI is a reference for discovery, clear controls and focused checks. Its media tools are not required runtime dependencies. Other reference tools do not become product feature names.

## Model

| Record | Minimum meaning |
|---|---|
| Location | Stable ID, provider/type, host, account reference, selected root, granted access, supported operations and last successful check |
| Folder pair | Source and destination IDs/roots, two-way direction, filters, conflict and deletion rules, bandwidth/storage limits, enabled/paused state, settings revision |
| File version | Stable item identity, location/path, provider revision, available content, observed size/time and verified content identity where supported |
| Transfer | Stable operation ID, expected source/destination versions, progress, retry state, final result and verification |
| Conflict | Shared base plus both versions, reason, preserved copies and an explicit resolution |
| Archive snapshot | Selected scope, exclusions, manifest, encrypted objects, remote completion, verification and retention |
| Observation | Target, source, value or error, units, collection time and freshness limit |
| Action result | Request ID, intended effect, checked scope, actual outcome, errors, result check and any recovery action |

These records are requirements. They do not replace the repository's existing schemas or imply that new schemas have been implemented. See the [registry](registry.md) and [UML contracts](uml-contracts.md).

## Sync and conflict rules

Discover changes using each provider's supported change mechanism, with a saved checkpoint and a way to reconcile after gaps. An incomplete scan, lost permission or unavailable provider must never be treated as deletion of all unseen files.

Compare with a known shared version. Preserve both sides when both changed. Use stable operations so retries do not create duplicate writes or lose history. State how renames, case differences, links, metadata, large files and open files are handled by each adapter.

A listed remote item is not proof that its bytes are available locally. Keep placeholder, downloading, local dirty, remote verified and offline states distinct. Avoid two independent engines competing to write the same folder. Put provider-specific API and permission details in adapter documentation.

Deletion is a separate rule, with recoverable history where supported. A proposed default is to keep deletion propagation off until configured. Do not remove conflict or archive history automatically without an explicit retention rule.

## Archive and recovery rules

Separate sync from backup. Sync can spread an unwanted change; an archive needs versions and a tested restore path. Use an expandable private store, not a promise of infinite capacity. Ordinary Git alone is not proof of encryption, storage scale or archive durability.

Encrypt private content and sensitive manifests before remote upload according to the selected key scheme. Store key references, not real keys, in shared configuration. Exclude the archive's own output to prevent recursion. Credential material must not enter a general-purpose content archive by accident; define any dedicated secret backup separately through the chosen key scheme.

Only record protected status after the required remote write and verification. A local write, a published receipt and a restored file are separate milestones. Test missing objects, changed manifests, interrupted upload, retry, locked keys and recovery on a clean installation with synthetic data. Do not discard a source because a local receipt exists.

## Care and limits

Before cleanup, show the same eligible set the action will use. Check scope again at execution. Skip active/unknown files, pending sync work and recovery data. Count confirmed removals and failures, not attempted deletions. Show storage usage and available capacity with a named location and sample time.

Limit concurrent scans/transfers, CPU and disk work, network use, cache size and retries. On quota or access failure, pause new work safely and explain the next step. Show storage and transfer cost where the provider can supply it, with freshness and assumptions; do not present an unverified estimate as a bill.

No single health percentage should hide a failed critical transfer. A quiet system may still be unavailable. Report useful causes and next actions rather than a large permanent log stream.

## Interface contract

Use **Status**, **Files**, **Network**, **Cleanup**, **Details**, and **About**. Use **Checking**, **Not set up**, **Unavailable**, **Paused**, **Working**, **Completed**, and **Failed** only when they describe the actual state. Keep necessary provider/protocol names and identifiers in context. Do not label sample data live or rename an internal module into an unsupported product feature.

For every retained action: check target and active work, show pending state, run with a deadline, read back the result, and report the outcome. The same definition applies to the native pane, menu, app and any callable backend interface. Closing a window and quitting the owner of background work need distinct behavior.

## Acceptance

Verify provider capabilities one by one. Cover simultaneous edits, offline work, checkpoint loss, expired access, quota limits, interrupted transfers, duplicate requests, missing content, crash recovery and restore. A disconnected source must not produce mass deletions. A conflict must preserve both versions. A failed command must not produce success.

The current implementation can retain this full scope while marking an adapter **Not set up**. Release only the functions whose behavior is implemented and checked; do not pretend the entire requested product is complete because one network test passed.

See the [AI helper guide](../../ai-helper.md) for evidence and task structure, and the [adapter references](../../../adapters/continuity/references.md) for provider and tool distinctions.
