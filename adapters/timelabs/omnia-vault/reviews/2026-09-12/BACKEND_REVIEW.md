# Backend review: public correction guide

This is a public-safe summary of the 12 September 2026 source review. Detailed security findings and machine-specific evidence remain in the private review pack. This file defines work and checks; it does not claim that the product has been fixed or tested.

## Main corrections

| Area | Required correction | Completion evidence |
|---|---|---|
| Network observations | Replace fixed services, paths, lab devices, traffic and timing with actual collectors or Unavailable | Disconnected collectors cannot leave sample data looking live |
| Connection controls | Name the affected proxy, local tunnel, remote service or test machine separately | Requested change, applied settings and checked service result are distinct |
| Action results | Check exit status, deadlines and readback | Failed and partial actions never become success text |
| NDI | Keep as reference; a settings-file write is not a stream restart | No broadcasting claim without a real sender and check |
| Cleanup | One eligibility rule for preview and deletion; check active ownership and outcomes | Empty preview is zero; active files survive; failed removals are not counted |
| Measurements | Retain timed counter samples; state units, drive/interface scope and age | Missing data is unavailable; host totals are not labelled SCION traffic |
| Background work | Bound child processes, prevent overlapping changes and define ownership | Slow tasks do not freeze UI; exit and window-close behavior are explicit |
| Platform support | Use actual platform capabilities and identify remote targets | A Mac build does not establish Windows behavior |
| Optional AI | Remove from normal beta scope; separately review any retained command | No simulated success or unapproved external data transfer |

## Registered app commands covered

These 16 command names existed in the reviewed product registration. They are source identifiers, not commands added to this playbook. Several share implementation with the local socket; review both interfaces.

| Command | Product purpose or decision |
|---|---|
| `get_system_metrics` | Keep measured local system data with clear definitions |
| `run_quick_clean` | Restrict to reviewed, eligible app resources and accurate results |
| `get_tunnel_status` | Separate local process, local port and remote service checks |
| `toggle_tunnel` | Keep only for the named, owned connection |
| `restart_tunnel` | Keep with active-work checks and verified result |
| `get_valves` | Replace the ambiguous state with actual component observations |
| `set_valve` | Rename user-facing actions by their real effect; do not infer route use |
| `get_scion_daemons` | Supply actual service data, not a sample list |
| `get_scion_routing_paths` | Supply actual paths; distinguish available, selected and used |
| `get_gns3_nodes` | Query the selected real project and compatible server API |
| `get_ndi_config` | Not an active stream check; remove the cloned runtime page |
| `restart_ndi` | Disable unsupported runtime claim; do not equate saved settings with broadcast |
| `query_llm` | Outside normal beta scope; review before any optional enablement |
| `get_llm_providers` | A listed provider or present key does not prove connection |
| `lit_publish_text` | Local publication only until the archive contract is met |
| `evaluate_proposal` | A text classification must not grant execution authority |

## Conditions before using local publication as an archive

The requested archive is broader than a local byte store. Its acceptance must cover:

1. Stable full identities and an explicit owner.
2. A stable operation ID for retries; reject reuse for different content.
3. The revision the caller actually edited, with conflict preservation.
4. A defined full-snapshot or item-revision model and correct reads of unchanged items.
5. Verification of the manifest, item size, and content, with storage errors distinct from missing data.
6. Persistent storage, documented durability and recovery after interruption.
7. Encryption before remote upload, protected key references and a tested restore path.
8. Clear separation of local write, remote write, verified archive and successful restore.

These are conditions for the archive feature. They do not require rebuilding the archive during an interface correction. Do not delete a source because a local receipt exists. Do not publish live credentials or private payloads to demonstrate these checks.

See [extra command review](EXTRA_COMMAND_REVIEW.md), [acceptance cases](REVIEW_SCOPE.md), and the [continuity requirements](../../../../../docs/requirements/continuity/technical-spec.md).
