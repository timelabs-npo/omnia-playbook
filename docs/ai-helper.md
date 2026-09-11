# AI helper guide

Use this repository as a descriptive reference for understanding a system, reviewing a proposed change, and recording what was checked. It is not an automatic repair service or a new product runtime.

This guide generalizes a desktop and network review method. It does not contain private host observations, credentials, account identities, or a claim that a particular installation passed the checks.

## Read the current material in order

The [guides index](README.md) connects the current correction review and the continuity requirements. Start with the [correction task](../adapters/timelabs/omnia-vault/reviews/2026-09-12/CORRECTION_TASK.md), then its inventories and [coverage record](../adapters/timelabs/omnia-vault/reviews/2026-09-12/REVIEW_SCOPE.md). Use the [technical specification](requirements/continuity/technical-spec.md), [registry](requirements/continuity/registry.md), and [contracts](requirements/continuity/uml-contracts.md) to retain the wider accepted outcome.

The dated review is a source snapshot, not proof of implementation. Requirements are descriptive contracts, not an active engine. The correction task's smaller beta scope takes precedence over optional suggestions in its appendices; deferred implementation does not silently cancel a previously accepted requirement.

## Start with the request

Write a short scope record before proposing work:

| Field | What to record |
|---|---|
| User outcome | What the person wants to accomplish |
| Included work | The requested functions and surfaces |
| Existing work | What must keep working |
| Current evidence | What was reported, observed, or read in source |
| Authority | The target and operations already authorized |
| Completion | The result that would demonstrate the requested work is done |

Keep earlier accepted requirements when a later message adds a correction. Do not quietly reduce the provider list, change a two-way sync into one-way copying, replace an existing settings surface, or introduce a new network architecture to make a demonstration easier.

Documentation is not authority to execute. Apply the [local agent policy](../local-agent/ssh-policy.md) to any host access. Executable checks contributed here must remain read-only; remediation stays in documented procedures under the current [contribution rules](../CONTRIBUTING.md).

## Identify the implementation that actually runs

Check the entry point, build configuration, selected frontend, backend commands, installed component, and running version. A similar file or an older frontend does not prove that the current build uses it.

For a desktop product, distinguish a native settings pane, a menu bar item, and a separate application window. A window styled like system settings does not become an operating-system pane. Preserve a working native surface unless the user explicitly changes that requirement.

Put platform-specific implementation guidance under [adapters](../adapters/). Keep this guide independent of a particular framework or machine layout.

## Trace every visible function

Use a review table that connects the screen to the implementation:

| Current element | User purpose | Actual effect | Evidence | Decision | New label | Acceptance case |
|---|---|---|---|---|---|---|
| A control or reading | The decision or action it supports | Handler, source, target and result | Source revision, observation or test | Keep, Rename, Move, Remove, or Not ready | Clear English | A reproducible check |

Include navigation, menu items, buttons, fields, toggles, badges, tables, error text and empty states. Trace hidden command entry points too: removing a button does not disable a callable mutation.

Keep labels such as **System**, **Files**, **Network**, **Cleanup**, **Details**, **About**, **Review app files**, **Start connection**, and **Restart connection** only when they match the function. Keep recognizable provider names and necessary identifiers. Move implementation slogans and internal module names out of the normal product flow. Required license notices retain their proper names.

## Distinguish facts from claims

For each important claim, record:

- The source and revision or observation time.
- The host, resource, service, account or folder to which it applies, using public-safe aliases in shared material.
- What the evidence establishes.
- What it does not establish.
- The next check needed, if any.

Useful evidence categories are **Reported**, **Observed**, **Source reviewed**, **Tested**, and **Not checked**. A user-reported success remains a reported success until independently checked; do not silently discard it or promote it into a broader guarantee.

Examples of separate observations:

| Evidence | What still needs its own check |
|---|---|
| A process is running | Whether its service answers correctly |
| A local port accepts a connection | Whether the intended remote service is available |
| Routes are listed | Which route was selected and carried traffic |
| A request receives a response | The actual transport used and any fallback |
| A settings file was written | Whether the target applied those settings |
| A local write completed | Remote synchronization, archive durability and restore |
| A deletion was attempted | Which files were actually removed and which failed |

Do not convert an exception, a missing credential or a simulation into success. Do not show sample values as live readings. A valid empty result, an unavailable source, and a stale last result need different states.

The existing [check schema](../schemas/check.schema.json) describes executable check configuration. The fields in this guide are a documentation method; they are not a new implemented report schema or an automatic policy engine.

## Write a concrete correction task

Lead with the problem and the behavior that should replace it. Then provide:

1. Scope and preserved working behavior.
2. The current implementation and supporting evidence.
3. Decisions for every affected function.
4. Exact product labels and truthful state definitions.
5. Acceptance cases and expected observations.
6. Required return material: changed files, checks actually run, results and remaining limits.

Correct false success and misleading control scope before polishing the layout. Prefer a small correction to the existing system. Do not build a new subsystem solely to justify an unsupported card or label.

For useful controls, describe **Check → Working → Check result → Completed or Failed**. This is a behavior contract to implement and test, not a statement that this repository already supplies a command lifecycle. Overlapping changes to the same resource, late responses and timeouts need explicit handling.

## Keep file and provider scope explicit

A product that requests multiple storage providers needs a separate capability and acceptance record for each one. A common view does not make their semantics identical. Record the actual runtime, selected location, access grant, supported operations, limits, and last successful check.

Distinguish discovery, listing, reading available bytes, downloading missing content, writing, remote synchronization, conflict handling, archive creation and restore. A placeholder entry is not proof that file content is available. Two-way sync needs an explicit conflict rule. A successful archive receipt must not stand in for a tested restore or authorize source removal by itself.

Provider-specific authentication, permissions and API mappings belong in adapter documentation with primary sources and version constraints. A provider can remain in scope while honestly marked **Not set up** or **Not checked**. Do not invent connected accounts, synced jobs or backup coverage.

Reference toolkits can inform a registry, diagnostics or interaction design without becoming runtime dependencies. Identify that relationship explicitly. A research appendix is not authorization to install or integrate the referenced tools.

## Test and report at the right scope

Select checks for retained behavior: absent collector, stale data, empty inventory, denied access, failed command, timeout, duplicate action, wrong target, settings readback, changed files after preview, reconnection and restore where applicable. Use synthetic fixtures for destructive-action and failure tests.

Report **Passed**, **Failed**, **Blocked**, **Not run**, or **Not applicable** for each case, with the specific evidence and time. A successful build verifies a build. A screenshot verifies appearance. Neither is a substitute for the behavior check.

Before contributing, run the required repository checks and report their actual outcomes. The [README](../README.md) contains a known baseline validation failure; do not relabel a baseline failure as a successful run or silently fix unrelated scope. No cloud credentials should be needed for documentation validation.

## Share a safe knowledge layer

Publish generalized methods, synthetic fixtures, primary-source references, and sanitized summaries. Keep machine paths, host addresses, account identifiers, access tokens, private topology and raw logs out of this public repository, as required by [SECURITY.md](../SECURITY.md).

When a detailed review pack lives in a private workspace, use it as source material for a public-safe summary. Do not copy it wholesale or publish local file links. Public documentation can describe how to check a system while the actual observations stay in the appropriate private evidence store.
