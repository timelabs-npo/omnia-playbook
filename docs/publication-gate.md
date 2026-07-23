# Publication gate

This gate applies before sending an Omnia repository, report, demo, or hosted
link to an external reviewer, regulator, public authority, or council.

## Mandatory technical gate

- [ ] The exact commit, tag, and artifact digests are recorded.
- [ ] CI and local validation pass on that exact commit.
- [ ] The shared artifact contains no raw host output, credentials, account
      identifiers, personal data, private topology, internal chat archives, or
      deleted Git history.
- [ ] Every public claim has a scope, evidence source, and freshness date.
- [ ] Experimental, implemented, tested, and released capabilities are
      distinguished.
- [ ] `PASS`, `FAIL`, `UNKNOWN`, and `ERROR` remain distinct.
- [ ] No digest, model agreement, or Tribunal result is described as proof of
      truth or legal compliance.
- [ ] The recipient can identify the Owner authority and the no-mutation
      default.
- [ ] Any automated action is bound to a signed policy, typed operation,
      explicit target, risk ceiling, receipt, retry budget, and emergency-stop
      behavior; otherwise the implementation remains read-only.
- [ ] Dependencies, licenses, and supplied artifacts have been inventoried.
- [ ] Security reporting has a verified private route.

## Mandatory organizational gate

- [ ] The legal entity name, jurisdiction, registration status, contact
      address, and authority to make organizational claims have been confirmed
      by the Owner and qualified counsel.
- [ ] License statements agree across the organization profile, repository,
      package metadata, source headers, and distributed artifacts.
- [ ] Privacy, retention, incident-notification, payment, donation, and
      charitable-use claims match actual operations and signed policies.
- [ ] Public links, hosted services, betas, and release references have been
      tested from a clean unauthenticated session.

## Decision

If any mandatory item is unresolved, the publication decision is **HOLD**.
`UNKNOWN` is not converted to `PASS`.
