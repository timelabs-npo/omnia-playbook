# Documentation verification — 12 September 2026

Scope: descriptive AI helper, continuity requirements and public-safe review material. No executable checks or runtime behavior were changed. Baseline: `0e3fc9c3503865200ec8dd2eb843561d71018912` on `main`.

| Check | Actual result | Limit |
|---|---|---|
| `make validate` | Failed after internal Markdown links passed | The same five baseline paths are missing: `checks/routing`, `checks/connectivity`, `checks/certificates`, `checks/secrets`, `checks/system`. Later schema/lint stages did not run. |
| `make diagnose` | Exit 0; script reported `Status: pass` on Darwin and `Observed resolvers: n/a` | This does not verify the expected resolver, SCION, the helper, or any other platform. The resolver list is not established by this result. |
| `make report` | Exit 0; local Markdown and JSON report files created | Raw reports remain ignored local files and are not included in this public change. Report generation does not validate a network. |
| `./scripts/validate.sh --links-only` | Passed | Checks local Markdown targets; it does not validate every external URL or render diagrams. |
| `git diff --check` | Passed | Whitespace check only. |
| Public-content review | New text checked for machine paths, account/host identifiers, private address patterns, common credential patterns, English prose and balanced code fences | Pattern checks complement source review; they are not a general secret-detection guarantee. |
| Registry continuity | All 44 original registry IDs retained | IDs describe requirements, not installed or tested collectors. |

The seven review files describe a separate product source review. That review did not run its mutation controls or network gates. Acceptance cases are tasks to perform, not passing results. Detailed security findings and private host evidence remain outside this public copy.

Do not fill the missing check directories with empty placeholders or report full validation as passed. Repairing that baseline is separate work from this documentation update.
