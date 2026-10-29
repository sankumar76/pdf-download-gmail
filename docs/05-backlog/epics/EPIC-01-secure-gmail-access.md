# EPIC-01: Secure read-only Gmail access

| Field | Value |
|-------|-------|
| Owner | product-owner |
| Jira | [PGD-2](https://sankumar76.atlassian.net/browse/PGD-2) (relates to Intake [PGD-1](https://sankumar76.atlassian.net/browse/PGD-1)) |
| Release | R1 Core + CLI (v0.9.0); the GUI surfaces of FR-005 and FR-006 belong to R2 (EPIC-09) |
| Wave | W1 (FR-005, FR-004), W2 (FR-001..003, FR-006), W3 (live consent) |
| Priority | Backlog rank 2 of 10 (FR-005 is the first functional story of sprint 1) |
| PRD size | L (17 pts, PRD §7) |
| Status | Ready for story slicing (scrum-master) |

## Goal & User Value
I sign in once through my browser with read-only Gmail access. Later runs need no browser. The app never sees my password, and no token, refresh token or client secret ever reaches a log, CSV, console line, dialog or crash output. This is the safety premise of the product (GOAL-05) and answers the highest-impact risk (RISK-005).

## Requirements Covered
- Functional: FR-001, FR-002, FR-003, FR-004, FR-005, FR-006. (FR-007 sign-out is R3 and out of scope.)
- Non-functional: NFR-011 (one scope, 0 write calls), NFR-012 (secret hygiene), NFR-013 (secret files), NFR-014 (no egress except Google), NFR-015 (agents never read secrets), NFR-020 (Windows paths).
- Business rules / source IDs: BR-013; SEC-01..07; VAL-03; AC-01, AC-07; TR-001, TR-006 (sponsor action, dependency).

## Scope
**In:**
- The one redaction path (`gmail_pdf.redaction`) installed before any logging exists (FR-005, ADR-003).
- Scope constant `gmail.readonly` and the read-only gateway allow-list asserted by a recording mock (NFR-011).
- Loopback consent; silent refresh; `invalid_grant` recovery with a clear message (FR-001, FR-003).
- Credentials and token paths by option, `GMAIL_CREDENTIALS_PATH` / `GMAIL_TOKEN_PATH` and defaults (FR-002; CLI defaults per D-23).
- Secret-file protection and `.gitignore` coverage (FR-004).
- Missing or wrong-type `credentials.json`: the setup steps, exit 3, no stack trace; the local client-file check (FR-006, ADR-003 §4, UA-12).
- Live consent against the sponsor's real mailbox (W3, needs TR-006).

**Out:** sign-out (FR-007, R3); at-rest token encryption (TD-01, GitHub #5); GUI sign-in and setup screens (EPIC-09: SCR-03, DLG-01, DLG-02, DLG-07).

## UX & Architecture References
- Screens / journeys: UJ-01, UJ-05 (CLI wording in UX §12); SCR-03, DLG-01, DLG-02, DLG-07 are R2 surfaces ([ux-spec](../../03-ux/ux-spec.md) §9 rows 001-006).
- Components: `infra.auth`, `infra.paths`, `redaction`, `domain.messages` ([architecture](../../04-architecture/architecture.md) §4.1, §8.1-8.4, §12).
- ADRs: [ADR-003](../../04-architecture/adr/ADR-003-token-storage-and-secrets.md) (token storage, defaults, redaction), [ADR-002](../../04-architecture/adr/ADR-002-dependency-policy.md).
- PRD: [§4.1](../../02-product/prd.md); release plan W1-W3.

## Stories (ordered)
Candidates only. The scrum-master creates the stories (IDs below are reserved by this order). Wave is shown in the intent.

| # | Story ID | Title | Intent (one line) | Splitting pattern | Depends on | Status |
|---|----------|-------|-------------------|-------------------|------------|--------|
| 1 | STORY-01.01 | One redaction path for every text surface | [W1] A planted sentinel secret never appears in CLI output, log or error text; the hook is installed before logging (FR-005, NFR-012, NFR-015) | Business-rule variation (surface by surface; GUI surface later in EPIC-09) | Enabler STORY-02.01 | Candidate |
| 2 | STORY-01.02 | Keep secret files out of git and protected on disk | [W1] `.gitignore` patterns, POSIX 700/600, Windows profile path (FR-004, NFR-013) | Business-rule variation (platform) | STORY-02.01 | Candidate |
| 3 | STORY-01.03 | Choose credential and token locations | [W2] Option > env var > default precedence (FR-002) | Business-rule variation (precedence levels) | STORY-01.02 | Candidate |
| 4 | STORY-01.04 | Sign in once, read-only (mock-tested) | [W2] Scope list equals `gmail.readonly`; second run opens no browser; only the 3 allowed API methods are called (FR-001, NFR-011, AC-01) | Workflow step (first consent, then reuse) | STORY-01.01, 01.03 | Candidate |
| 5 | STORY-01.05 | Recover from an expired or revoked sign-in | [W2] Silent refresh; `invalid_grant` removes the token and restarts consent with a named reason (FR-003) | Happy / unhappy path | STORY-01.04 | Candidate |
| 6 | STORY-01.06 | Guide the user when credentials are missing or wrong | [W2] Setup steps, wrong-client-file message, exit 3, no trace (FR-006 CLI; ADR-003 §4) | Happy / unhappy path | STORY-01.03; exit-code story STORY-07.05 for the final exit mapping | Candidate |
| 7 | STORY-01.07 | Live sign-in on the sponsor's mailbox | [W3] Real consent with the sponsor's `credentials.json`; verifies Q-04 behaviour and records any `invalid_grant` (GOAL-05, RISK-003) | Workflow step (mock to live) | STORY-01.04..06; TR-006 from Santhosh | Candidate |

## Epic Acceptance Criteria
- [ ] The scope list requested equals exactly `gmail.readonly`; consent uses the loopback flow; the second run opens no browser (AC-01).
- [ ] The recording mock proves 0 mailbox write calls; only list, get and attachment-get are used (NFR-011).
- [ ] A simulated `invalid_grant` removes the stale token, restarts consent and names the reason; no secret is shown.
- [ ] The sentinel-secret matrix over every error path finds 0 occurrences in log, CSV, console and exception text (NFR-012; the GUI surfaces are verified in EPIC-09).
- [ ] A missing or wrong-type `credentials.json` shows the setup steps, exits 3 and prints no stack trace.
- [ ] Option, env var and default precedence is tested; the `.gitignore` pattern test, POSIX permission test and Windows path check pass; the repo secret scan is clean.
- [ ] A real consent on the sponsor's mailbox succeeds (W3) with no secret in any artefact.

## Dependencies & Risks
- Depends on: STORY-02.01 (package skeleton, CI, fake mailbox) so redaction and tests have a home; TR-006 (sponsor's Google Cloud setup and `credentials.json`) for story 7 only.
- FR-005 must land before any logging or CSV story (EPIC-07) so no log line can bypass it.
- Risks: RISK-005 credential leakage (mitigated by 01.01 first), RISK-003 token expiry in Testing status, RISK-009 unprotected downloads. Assumption: Q-04 stays ASSUMPTION-04 until G8 (D-34).
- Developers and agents never read real `credentials.json` or `token.json` (SEC-08, NFR-015); tests use generated fake files in `tmp_path`.
