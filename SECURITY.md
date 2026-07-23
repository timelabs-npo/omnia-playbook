# Security Policy

## Reporting a vulnerability

Do not disclose vulnerability details in a public issue.

Use GitHub's private vulnerability reporting for this repository when the
private advisory form is available. If it is unavailable, withhold technical
details until the organization publishes and verifies an alternative private
reporting channel. The project does not currently promise a response time or
bug bounty.

## Secure contribution rules

- Do not commit secrets, API keys, account identifiers, or private IP topology.
- Keep all checks read-only.
- Do not require cloud credentials for validation or CI.
- Treat diagnostic output as potentially sensitive before persistence.
- Do not describe model agreement, hashes, or digest chains as proof of truth.
- No mutating operation may depend on an unsigned, unbound approval artifact.
