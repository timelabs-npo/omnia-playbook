# Omnia Playbook

Omnia Playbook is a reference for checking a system, explaining what was observed, and preparing a clear correction task. It connects requirements, platform behavior, read-only checks, evidence and documented procedures. It does not provide an automatic repair or sync service.

## Start here

- [Guide index](docs/README.md) — choose the right layer for a request.
- [AI helper guide](docs/ai-helper.md) — keep scope, evidence, authority and completion clear.
- [Desktop correction review](adapters/timelabs/omnia-vault/reviews/2026-09-12/CORRECTION_TASK.md) — a public-safe example with a full function inventory and acceptance cases.
- [System care and file requirements](docs/requirements/continuity/technical-spec.md) — the requested behavior, [44-entry registry](docs/requirements/continuity/registry.md) and [UML contracts](docs/requirements/continuity/uml-contracts.md).
- [Contribution rules](CONTRIBUTING.md) — where material belongs and which checks to run.

The review and requirements are descriptive. They are not proof that the app was corrected, that a network was tested, or that all listed providers are connected. Detailed private evidence belongs outside this public repository.

## What works here today

The executable scope is a read-only DNS diagnostic and report scripts. The repository also has invariant/check/environment schemas, fixtures, foundation documents, and platform adapter scaffolds. Several directories describe intended work rather than implemented checks.

The new AI helper and continuity documents add a knowledge layer. They add no background agent, privileged executor, network rule, provider connection, or cleanup action.

## How to use the layers

| Location | Purpose |
|---|---|
| [docs/](docs/) | Explain the review method, requirements and evidence limits |
| [foundation/](foundation/) | Define what should remain true and why |
| [adapters/](adapters/) | Explain platform and vendor-specific behavior; several entries are placeholders |
| [checks/](checks/) | Observe without changing configuration; DNS is the current implemented slice |
| [playbooks/](playbooks/) | Describe procedures; a procedure is not evidence that it ran |
| [references/](references/) | Keep sources near the claims they support |
| [reports/](reports/) | Hold generated observations with their time and limits |

```text
requirement → platform mapping → read-only check → observation
                                                    ↓
                                                  report
                                                    ↓
                                              proposed action
                                                    ↓
                                      separately authorized execution
```

A process running, a port answering, a route being listed, and a successful application request are different observations. A local write, a remote backup and a restored file also need separate evidence. Keep those distinctions in both reports and product status.

## Run and read the checks

Run these as separate steps from the repository root:

```bash
make validate
make diagnose
make report
```

Inspect each result. The [Makefile](Makefile) and [scripts](scripts/) define their actual behavior. Full validation uses Bash, Ruby, Python with `jsonschema`, `jq` and `shellcheck`. Diagnosis also needs the host's resolver inspection tool. Report generation writes local files and may include private network data; review locally before sharing.

The [DNS invariant](foundation/dns.md) asks which resolver a machine is configured to use. The [diagnostic](scripts/diagnose.sh) has inspection paths for macOS, Linux/OpenWrt and Windows. It does not by itself prove that a resolver is trusted or explain every connection failure.

### Known baseline limits

The earlier verification on 6 September 2026 used main baseline [`0b2edc1085`](https://github.com/timelabs-npo/omnia-playbook/commit/0b2edc1085482c576afa694d7310d34ac6cd87f0):

| Command | Observed result and limit |
|---|---|
| `make validate` | Failed because `checks/routing`, `checks/connectivity`, `checks/certificates`, `checks/secrets` and `checks/system` were absent. Later validation stages did not run. |
| `make diagnose` | Exited 0 on one macOS host, with `Observed resolvers: n/a`. This did not confirm the expected resolver or other platforms. |
| `make report` | Not executed in that pass. |

See [this documentation update's verification](docs/verification-2026-09-12.md) for fresh results. Keep an existing failure visible; do not turn it into a pass by adding empty placeholder checks.

## Contribute a useful change

Define the requirement, map the platform, add a read-only check and synthetic fixtures where needed, describe the procedure, and report the actual validation results. Keep vendor-specific implementation details in adapters. Never commit credentials, account identifiers, private topology or raw private logs. Follow [SECURITY.md](SECURITY.md) for private reporting.

Start with [CONTRIBUTING.md](CONTRIBUTING.md), the [AI helper guide](docs/ai-helper.md), and the [DNS diagnostic playbook](playbooks/diagnostics/dns.md).

## Related projects

These are separate components and research directions, not one verified integrated runtime.

| Project | Role |
|---|---|
| [Rhea](https://github.com/timelabs-npo/rhea-project) | Proposals and coordination |
| [Rheknel](https://github.com/timelabs-npo/rheknel) | Research into checks before admitting an action |
| [Omnia Vault](https://github.com/timelabs-npo/omnia-vault) | Identity, history and state preservation research |
| [Blueshoes](https://github.com/timelabs-npo/Blueshoes) | Network observation and traffic control research |
| [MBSD](https://github.com/timelabs-npo/mbsd) | Operating-system boundaries |

[BSD 3-Clause License](LICENSE). Maintained by Timelabs Non-Profit Corp.
