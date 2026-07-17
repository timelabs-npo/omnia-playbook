# SSH Policy

## Authority

A local agent may use SSH only when a human operator explicitly authorizes the target and operation.

## Default mode

- Read-only inspection.
- No package installation.
- No configuration writes.
- No service restart or reboot.
- No credential, firewall, routing, DNS, DHCP, or wireless mutation.

## Required controls

- Verify the target host key out of band before trusting a changed fingerprint.
- Use a dedicated agent key rather than a personal key.
- Keep private keys outside the repository.
- Record commands, timestamps, target aliases, exit codes, and sanitized outputs.
- Require a separate approval for every mutating operation.

## Prohibited repository content

Never commit private keys, passwords, tokens, real public IP addresses, or unredacted private topology.
