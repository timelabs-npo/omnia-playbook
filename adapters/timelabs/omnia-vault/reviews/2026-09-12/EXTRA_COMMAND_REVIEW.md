# Commands behind the interface

This public guide records the reviewed command surface and the checks it needs. Detailed security findings remain in the private review and should use the repository's private reporting process. No command below was executed in this review.

## Removing a button is not enough

The reviewed product starts a local command server. Some functions absent from the Tauri command list remain reachable through that server. Both the Unix and Windows branches must be included in the implementation review. A local transport is not proof that every caller has the right to change a resource.

For every retained operation, require a supported purpose, validated fields, an identified caller, an explicit target, active-work checks, bounded input and time, and a truthful result. Disable unsupported operations through every entry point. A text classifier, a string response, or an absent request field must not grant permission to execute.

## Socket inventory

There were 13 handlers and 15 accepted names in the reviewed source. Aliases are shown together. These identifiers describe the product under review, not an executor supplied by omnia-playbook.

| Names | Required purpose or decision |
|---|---|
| `status`, `check_daemon_health` | Report exactly which server or dependency was checked |
| `get_metrics`, `get_system_metrics` | Return measured values, scope and collection time |
| `quick_clean` | Use the same eligibility and result checks as the UI |
| `flip_backbone` | Disable a text-only route claim; retain only if a real supported action exists |
| `get_llm_providers` | Keep configuration separate from verified availability |
| `query_llm` | Outside normal beta scope; require a defined external-data policy if retained |
| `prepare_and_reboot` | Disable unless there is a supported, explicitly authorized host workflow |
| `stop_ssh_tunnel` | Stop only the owned connection and report the outcome |
| `start_ssh_tunnel` | Validate target and settings; verify readiness and preserve process ownership |
| `get_tunnel_status` | Distinguish process, local port and remote service |
| `restart_tunnel` | Apply the same safeguards and result checks as the UI |
| `toggle_tunnel` | Require an explicit intended state; reject invalid input |
| `restart_ndi` | Disable unsupported stream behavior; saved settings are a different action |

## Optional AI and text review

If AI remains in a development-only workflow, state the provider and data sent, use protected credential references, keep secrets and private content out of process arguments and error reports, and enforce time and size limits. Missing keys, unsupported providers, bad responses and HTTP errors are failures or unavailable states, not simulated success. A response is not automatically correct or verified.

A keyword-based text review is only a classification. Permission belongs to the actual requested action and its policy. Removing the AI page must not leave an unintended external-request path enabled elsewhere.

Test malformed requests, slow clients, access failure, unsupported commands, duplicate changes, child-process failure and timeout with synthetic data. Report actual results. See [backend guide](BACKEND_REVIEW.md) and [acceptance cases](REVIEW_SCOPE.md).
