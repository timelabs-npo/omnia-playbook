# Contributing

## Scope

Keep contributions vendor-neutral by default. Put vendor-specific implementation details under `adapters/` only.

## Required checks

Run before opening a pull request:

```bash
make validate
make diagnose
```

## Safety

- All executable checks must be read-only.
- Remediation must be documentation-driven in this bootstrap phase.
- Never commit secrets, credentials, account identifiers, or private topology details.
