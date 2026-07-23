# Contributing

## Scope

Keep contributions vendor-neutral by default. Put vendor-specific implementation details under `adapters/` only.

## Required checks

Run before opening a pull request:

```bash
make validate
make test
```

Install the pinned development dependencies from `requirements-dev.txt` first. The validation baseline supports stock macOS Bash 3.2 and Python 3.11 or newer.

## Safety

- All executable checks must be read-only.
- Remediation must be documentation-driven in this bootstrap phase.
- Never commit secrets, credentials, account identifiers, or private topology details.
- Do not run `make diagnose` or `make report` as a routine contribution check. Those commands inspect live host DNS state, and the current prototype retains raw resolver output in local reports.
