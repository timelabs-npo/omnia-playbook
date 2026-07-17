# DNS Explicit Resolver Recovery (Documentation-Only)

This playbook is remediation guidance only and does **not** execute system changes.

1. Identify your target resolver set for the current environment.
2. Apply DNS resolver settings using approved platform administrative processes.
3. Re-run `make diagnose` to confirm explicit and observable resolver configuration.
4. Record result with `make report`.
