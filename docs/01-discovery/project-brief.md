# Project Brief — Gmail PDF Attachment Downloader

| Field | Value |
|-------|-------|
| Version | 0.3 (G3 condition C7 closed; delivery-lead answers of 2026-10-29 applied) |
| Author | business-analyst |
| Date | 2026-10-29 |
| Status | In Review (G3 C7 update) |
| Jira | [PGD-1](https://sankumar76.atlassian.net/browse/PGD-1) |
| Companion docs | [requirements-catalog.md](requirements-catalog.md), [stakeholder-map.md](stakeholder-map.md) |

## 1. Executive Summary
Santhosh (MD) needs every PDF attachment that arrived in one Gmail account during a chosen date range, saved locally with predictable, date-prefixed names, without opening emails one by one. Today this is manual. The product is a local **desktop application with a graphical UI plus a command-line interface (CLI)**, both on one shared core (decision D-01). It reads the mailbox with read-only permission, never overwrites a file, and a re-run of the same range saves nothing new. Security of the Gmail credentials is the dominant risk and is treated as a first-class business requirement. There is no database.

## 2. Problem Statement
- **Who is affected:** the mailbox owner and sole sponsor/user, Santhosh (see `stakeholder-map.md`).
- **Current situation (as-is):** PDFs are found and saved by hand: open each email, save each attachment, rename or organise it manually. *Source: requirements doc §1 purpose ("without manually opening emails" per `docs/project-state.md` Request). No further as-is detail was provided.*
- **Future situation (to-be):** the user picks a date range (and optionally a time zone and extra Gmail search text) in the GUI or CLI, previews with a dry run, runs the download, and gets files named `YYYYMMDD_<name>.pdf` plus a log and CSV report.
- **Pain / impact:** manual effort is about **30 seconds per PDF** (delivery lead estimate, PGD-1 comment 10108, Q-12 resolved; a stated estimate, not a measurement: ASSUMPTION-17). Volume and error data are still not provided. Risks of the manual approach implied by the requirements doc: missed attachments, inconsistent names, overwritten files.
- **Evidence:** `Gmail PDF Attachment Downloader — Requirements.md` (2026-10-28), `docs/project-state.md`, PGD-1 comment 10108 (30 s per PDF). No other evidence exists; none is invented here.

## 3. Business Objectives (SMART)
Targets below are derived from the acceptance criteria in requirements doc §6.2 unless marked PROPOSED. No fixed deadline exists (Q-01 resolved: as soon as possible, R1 core + CLI first), so "by when" is expressed as a delivery gate.

| ID | Objective | Metric | Baseline | Target | By when |
|----|-----------|--------|----------|--------|---------|
| GOAL-01 | Complete retrieval | Share of PDF attachments from emails received in the inclusive date range that are saved, measured on a mocked/fixture mailbox that covers nested MIME parts and the range boundaries | Manual, about 30 s per PDF (Q-12); completeness not measured | 100 % saved; 0 saved from outside the range (23:59:59 on end date included, 00:00:00 next day excluded) | G7 of the MVP story set |
| GOAL-02 | Predictable naming | Share of saved files whose name matches `YYYYMMDD_<sanitised name>.pdf`, and match of the requirements doc §4.4 example table | Manual, inconsistent | 100 % match; example table reproduced exactly | G7 |
| GOAL-03 | Safe re-runs | New files written when the same range is run a second time; share reported `SKIPPED_ALREADY_DOWNLOADED` | n/a | 0 new files; 100 % of previously saved attachments reported as skipped | G7 |
| GOAL-04 | No data loss, no path escape | Existing files overwritten; files written outside the output folder when attachment names are malicious (e.g. `../../x.pdf`) | n/a | 0 and 0 | G7 |
| GOAL-05 | Credential and mailbox safety | OAuth scopes requested; mailbox write operations; occurrences of token, refresh token or client secret in logs, console, GUI dialogs, error text or repository | n/a | Exactly 1 scope (`gmail.readonly`); 0 write calls; 0 occurrences (verified by automated log scan and secret scan) | G6 and G7 |
| GOAL-06 | Resilience and resumability | A stopped run (Ctrl+C or GUI Cancel) followed by a re-run of the same range: duplicates created and attachments lost; one failing message stopping the run | n/a | 0 duplicates, 0 lost; 0 runs aborted by a single message failure (exit code 1 with summary instead) | G7 |
| GOAL-07 | Unified GUI/CLI behaviour | Differences in file names, statuses and CSV content between GUI and CLI for the same inputs and mailbox fixture | n/a | 0 differences | G7 |
| GOAL-08 | Design-standard compliance (CLAUDE.md §9) | Hard-coded colours, font sizes or spacing values and non-standard buttons in GUI code and screens; windows below the defined minimum size that break layout | n/a | 0 hard-coded values; 1 reusable button component; 4 typography roles only; layout intact from the minimum window size to a large monitor and at OS display scaling above 100 % | G6 (review) and G7 |
| GOAL-09 | Ease of first use (**Should** success metric per PD-08; not a release gate; sponsor confirms at G8, PA-02) | Time for a user who has completed the one-time Google setup to run a dry run for a one-week range from the GUI | n/a | 5 minutes or less, no command typing | G7 (usability check) |
| GOAL-10 | Auditability (added per PRD GOAL-10, closes G1 condition C2) | For every run that passes input validation and is not a dry run (outcomes: success, some errors, cancelled, zero matches, authentication failure): (a) a run log and a CSV exist at the documented path; (b) CSV header equals the LOG-02 list exactly; (c) every PDF candidate examined has exactly one row with one valid LOG-03 status; (d) per-status row counts equal the summary counts | n/a | 100 % of runs; 0 discrepancies. After a hard kill, ≤ 1 attachment is missing from the CSV | G7 (reconciliation test over ≥ 6 scripted runs, CLI and GUI) |

| GOAL-11 (**PROPOSED**) | Time saved against the manual process | Hands-on time per PDF to find, save and name a PDF, excluding the one-time Google setup | About 30 s per PDF by hand (delivery lead estimate, Q-12, comment 10108; not measured, ASSUMPTION-17) | Elapsed run time within the PRD NFR-001 budget (15 min per 1,000 messages, about 0.9 s per message); the user's own hands-on time per PDF is 0 s once the range is entered | G7 (timed run on the fixture) and G8 (sponsor confirms on a real mailbox) |

GOAL-09 and GOAL-10 follow `docs/02-product/prd.md` v0.1 §3 (PD-08 and GOAL-10); the PRD wording is authoritative if the two differ. GOAL-11 is a BA proposal that applies the Q-12 baseline. product-manager owns the time-saved goal in PRD v0.4 (C8); if its ID or wording differs, the PRD wins and this row is renumbered at the next sync.

## 4. Stakeholders & Personas
Detail in [stakeholder-map.md](stakeholder-map.md).

| Stakeholder / Persona | Role | Primary need | Influence | Interest |
|-----------------------|------|--------------|-----------|----------|
| Santhosh / MD | Sponsor, delivery lead, end user, final approver | Complete, safe, repeatable downloads | High | High |
| P-01 GUI user (Santhosh) | Primary persona | Run downloads without commands | n/a | High |
| P-02 CLI user (Santhosh) | Secondary persona | Scriptable runs with exit codes | n/a | Medium |
| Google (Gmail API, OAuth policy) | External platform | Policy-compliant, quota-respecting client | High (feasibility) | Low |
| Senders of the emails | Passive data subjects | Their content is not exposed | Low | Low |
| AI delivery team | Builders and verifiers | Clear, testable requirements | Medium | High |

## 5. Scope
**In scope**
- Read-only access to one Gmail account (personal Gmail or Google Workspace) via OAuth 2.0 with `gmail.readonly` only.
- PDF attachments only, including PDFs nested in multipart or forwarded (`message/rfc822`) messages.
- Filtering by inclusive start and end date in a chosen IANA time zone; optional extra Gmail query; optional inclusion of Spam/Trash.
- Date-prefixed file names, sanitised names, deterministic numeric suffixes, no overwrites, manifest-based re-run safety and resume.
- Dry run, run log, CSV report, run summary, defined exit codes.
- **Desktop GUI and CLI on one shared core (D-01)**, with GUI design standards from CLAUDE.md §9.
- README with the one-time Google Cloud setup.

**Out of scope**
- Sending, deleting, labelling or modifying any email.
- PDFs hosted behind links (Google Drive links, download URLs in the body).
- Other file types (.docx, .xlsx, images).
- Multiple mailboxes per run; service account / domain-wide delegation and IMAP App Password access (listed in requirements doc §2.3 as alternatives, not the default).
- Any database.
- Doing the one-time Google Cloud Console setup (done by the user, requirements doc §2.1).

**Superseded:** requirements doc §1 "Out of scope: A graphical interface" is **superseded by D-01** (PGD-1 comment 10081). It is no longer out of scope.

**Future consideration** (not committed)
- Standalone installer/packaging (Q-03); sign-out/revoke action in the GUI (Q-13); multi-account use; scheduled unattended runs.

## 6. Key Requirements Summary
Full list with IDs, sources and priorities in `requirements-catalog.md`.
- BRQ-001..011 (retrieval, naming, no data loss, re-run safety, read-only, credential safety, auditability (maps to GOAL-02 and GOAL-10), resilience, GUI+CLI parity, design standards, ease of first use).
- Carried-over source requirements keep their original IDs: SEC-01..09, FR-01..18, NFR-01..05, LOG-01..05, plus parameters (CFG-), validations (VAL-), edge cases (EC-) and acceptance criteria (AC-01..09).
- New GUI requirements GUI-01..19 (sources: D-01, CLAUDE.md §9; GUI-19 is a BA proposal).
- Business rules BR-001..014; data requirements DR-001..008; transition requirements TR-001..006.

## 7. Constraints
| ID | Constraint | Source |
|----|-----------|--------|
| CONSTRAINT-01 | Request only the `gmail.readonly` scope | SEC-01, G0 decision |
| CONSTRAINT-02 | Python 3.10 or later (3.12 target) | Req doc §1, CLAUDE.md §1 |
| CONSTRAINT-03 | Google API client libraries only; any other third-party dependency needs written justification (a GUI framework needs a G3 ADR) | Req doc §1, RISK-001 |
| CONSTRAINT-04 | No database | CLAUDE.md §9, project-state |
| CONSTRAINT-05 | Desktop GUI and CLI on one shared core | D-01 |
| CONSTRAINT-06 | GUI follows CLAUDE.md §9 (four-role type scale, one spacing scale, one reusable button, one palette, resizable with minimum size, high-DPI) | CLAUDE.md §9 |
| CONSTRAINT-07 | Local tool; mailbox content is processed on the user's machine only | Req doc §1 ("local") |
| CONSTRAINT-08 | Attachments up to Gmail's 25 MB limit must work | NFR-05 |
| CONSTRAINT-09 | Delivery toolchain: pytest, ruff, mypy strict; package `gmail_pdf` | CLAUDE.md §1 |
| CONSTRAINT-10 | Developers and agents never open or print contents of `credentials.json` or `token.json` | SEC-08 |

## 8. Assumptions
Full list with owners in the catalogue; headline items:

| ID | Assumption | Impact if false | Validation owner |
|----|------------|-----------------|------------------|
| ASSUMPTION-01 | One user and one Gmail account per run | Multi-account scope would change auth and manifest design | Santhosh |
| ASSUMPTION-02 | Windows 11 is the target platform (**confirmed**, Q-02, comment 10108); macOS/Linux best-effort, not asked | Packaging, permissions (SEC-04) and GUI tests change | Santhosh (Q-02, resolved) |
| ASSUMPTION-04 | OAuth consent screen is in Testing status, so tokens expire after about 7 days unless the screen is published (RISK-003). Delivery lead is unsure (comment 10108); the assumption stands, re-check at G8 (D-28) | Re-consent frequency changes | Santhosh (Q-04) |
| ASSUMPTION-08 | The manifest is the only guarantee of re-run idempotency; if it is lost, a re-run behaves like a first run with `_1` suffixes. **Superseded by PD-02** (warn in MVP; recovery in R3) | Duplicates on re-run if the user expects otherwise | product-manager (Q-06, resolved) |
| ASSUMPTION-15 | The Gmail `filename:pdf` search is accepted as the candidate filter even though it may miss PDFs with no file name. **Superseded by ADR-007** (baseline search plus recall sweep, on by default; residual measured by S-01, issue #2) | GOAL-01 recall below 100 % on real mailboxes | solution-architect (Q-07, resolved) |
| ASSUMPTION-17 | The manual baseline of about 30 s per PDF is the delivery lead estimate and has not been timed | GOAL-11 time-saved claim changes | Santhosh (re-check at G8) |

## 9. Dependencies
| Dependency | Type | Owner | Status |
|------------|------|-------|--------|
| Gmail API and OAuth 2.0 service | 3rd party | Google | Available; quota/policy not verified |
| Google Cloud project, OAuth consent screen, Desktop client credentials (req doc §2.1) | 3rd party / user action | Santhosh | Not confirmed done |
| Google API client Python libraries | 3rd party | solution-architect (selection) | To be pinned at G3 |
| GUI framework | 3rd party | solution-architect (ADR) | Undecided (RISK-001) |
| Jira PGD and GitHub repo `sankumar76/PDF-Download-Gmail` | Internal | Santhosh | Operating |
| A test mailbox or a mocked Gmail API for verification | Data | qa-engineer / developer | To be planned at G3 |

## 10. Business Risks
Source of truth: `docs/00-governance/risk-register.md` (owned by master; IDs from PGD-1 comment 10082, RISK-007..009 registered at G1, re-assessment of RISK-002/004/006 dated 2026-10-29). Score = P x I (1-5 each). If this table and the register differ, the register wins.

| Risk | P | I | Score | Owner | Status | Mitigation |
|------|---|---|-------|-------|--------|------------|
| RISK-001 GUI added to a CLI-shaped spec: new dependency, more effort, conflict with the no-extra-dependencies rule | 3 | 3 | 9 | solution-architect (ADR), product-manager (scope) | Open | UI-framework ADR (G3); PRD separates core+CLI from GUI polish (G2); GUI is a thin layer |
| RISK-002 Jira key typo (`PDG` instead of `PGD`) in CLAUDE.md creates or searches issues in a non-existent project | 1 | 2 | 2 | Santhosh (T-01); orchestrator interim | Reduced (open until the CLAUDE.md change is committed) | T-01 done: CLAUDE.md §1/§1a now say `PGD` (was 3x2=6). Close when the change is committed |
| RISK-003 Testing-status consent screen expires tokens after about 7 days, so unattended runs fail with `invalid_grant` | 4 | 2 | 8 | business-analyst (G1), solution-architect (G3) | Open | SEC-07 re-consent path; README/GUI explain publishing to "In production"; Q-04 |
| RISK-004 Jira status categories misconfigured (T-02) | 1 | 2 | 2 | Santhosh (Jira admin) | Closed (verified 2026-10-29) | T-02 fixed; master verified the PGD status categories (was 3x2=6) |
| RISK-005 Token or client secret leaks via logs, GUI dialogs, crash traces or a committed `secrets/` folder | 2 | 5 | 10 | solution-architect (G3); reviewer-standards, qa-engineer | Open | SEC-01..09; single redacting error path for GUI and CLI (GUI-11); `.gitignore` (SEC-05); secret-scan and log-scan tests (GOAL-05) |
| RISK-006 Write-guard hook blocked the governance records | 1 | 3 | 3 | Santhosh (hook config) | Closed (verified 2026-10-29) | B-01 resolved (session runs as plain `claude`, comment 10084); master wrote the governance records (was 5x3=15) |
| RISK-007 Search-recall gap: `filename:pdf` may miss unnamed PDFs, so FR-10 never applies and recall falls below GOAL-01 (registered from former PROPOSED-RISK-A) | 3 | 4 | 12 | solution-architect (spike, G3); product-manager (accept residual, G2) | Open | Spike and ADR at G3 (Q-07, ASSUMPTION-15); state any accepted residual gap in README/GUI help |
| RISK-008 Manifest lost, corrupted or output folder changed, so a re-run creates `_1` duplicates and GOAL-03 fails in practice (registered from former PROPOSED-RISK-B) | 3 | 3 | 9 | product-manager (Q-06, G2); solution-architect (manifest integrity, G3) | Open | Decide behaviour at G2 (Q-06); atomic manifest write, backup, optional rebuild by SHA-256 at G3; warn when manifest missing in a non-empty folder |
| RISK-009 Downloaded PDFs (possibly financial) and logs (sender, subject) sit unencrypted on disk or get committed (registered from former PROPOSED-RISK-C) | 2 | 4 | 8 | Santhosh (Q-10); solution-architect (G3); reviewer-standards, qa-engineer | Open | SEC-05 `.gitignore` for output folder; decide default output location at G3; README guidance (TR-002); Q-10 |

## 11. Compliance & Regulatory Considerations
Assessment from BA knowledge; **no web research was performed in this run** and no URLs are cited. Santhosh should confirm.
- **Google API terms and OAuth policy:** `gmail.readonly` is a sensitive/restricted Gmail scope. For an unverified app used only by the owner as a Test user, Google shows an "unverified app" warning; the requirements doc §2.3 accepts this. Verification is not needed for personal use (to validate, Q-04).
- **Privacy (e.g. GDPR):** emails and attachments may contain personal data of third parties. Processing is local, by the mailbox owner, with no transmission to any party other than Google's API. ASSUMPTION-12: the app sends no telemetry or analytics. If the tool is ever used on behalf of an organisation, the organisation's data-protection obligations need review (Q-10).
- **Financial/health/payment regulation (SOX, PCI-DSS, HIPAA):** none identified for the tool itself. Downloaded PDFs may contain such data; protecting the output folder is the user's responsibility (DR-002).
- **Internal policy:** CLAUDE.md §6 rule 7 (no secrets or real personal data in code, tests, fixtures or documents) applies; tests use synthetic data only.

## 12. Open Questions
None is blocking, so no Jira question issues were created (playbook §4.2 applies to blocking questions only). Full table with affected requirements is in the catalogue. Status after G3 condition C7 (2026-10-29): resolved are Q-01, Q-02, Q-12 (delivery-lead answers, comment 10108), Q-03, Q-07, Q-08, Q-11 (architecture ADRs) and Q-05, Q-06, Q-09, Q-13 (PRD). **Open: Q-04 and Q-10, both needed by G8** (delivery lead unsure; working assumptions ASSUMPTION-04 and ASSUMPTION-11 stand).

| ID | Question | Owner | Needed by | Status |
|----|----------|-------|-----------|--------|
| Q-01 | Is there a target date or deadline for the MVP and for the GUI? | Santhosh | G2 | **Resolved** (comment 10108, 2026-10-29): as soon as possible, no fixed date; R1 (core + CLI) first. ASSUMPTION-14 confirmed |
| Q-02 | Which operating systems must be supported? | Santhosh | G2 | **Resolved** (comment 10108): Windows 11 is the target OS. PA-09 and ASSUMPTION-02 confirmed for Windows |
| Q-03 | How is the app delivered: run from source, pip install, or a standalone executable? | Santhosh, solution-architect | G3 | **Resolved by ADR-005** (pip-installable package with CLI and GUI entry points; frozen executable deferred; Santhosh confirms at G8) |
| Q-04 | Personal Gmail or Workspace? Consent screen Testing or In production? | Santhosh | **G8** (D-28; was G3) | Open. Delivery lead unsure (comment 10108); ASSUMPTION-04 stands (Testing, 7-day expiry); the design works in both states (RISK-003) |
| Q-05 | Must the GUI expose every CLI option, including `--skip-identical`, `--query`, `--include-spam-trash`? Which optional ones are in the MVP? | product-manager | G2 | **Resolved by PD-01** (GUI shows seven fields; paths and log level in Advanced, R3; no skip-identical or config file in MVP) |
| Q-06 | Re-run behaviour if the manifest is lost or a user deleted a saved file | product-manager, Santhosh | G2 | **Resolved by PD-02** (manifest authoritative; unreadable manifest stops the run; missing manifest warns; recovery in R3) |
| Q-07 | How to find PDFs with no file name given FR-02's `filename:pdf` filter? | solution-architect | G3 | **Resolved by ADR-007** (complementary sweep `has:attachment -filename:pdf`, on by default; residual recall measured by S-01, GitHub issue #2; PD-06) |
| Q-08 | Are a YAML parser (for `config.yaml`) and time-zone data for Windows acceptable justified dependencies? | solution-architect | G3 | **Resolved by ADR-002** (no YAML, CFG-11 is a Won't; `tzdata` and `tzlocal` accepted for time zones) |
| Q-09 | Tie-break order for messages with identical `internalDate` | product-manager | G2 | **Resolved by PD-03** (messageId ascending, shorter ID first, then lexicographic) |
| Q-10 | Retention, clean-up and privacy expectations for logs, CSV reports and downloads | Santhosh | **G8** | Open. Delivery lead unsure (comment 10108); ASSUMPTION-11 stands (user-managed retention, no telemetry; PA-08); re-check at G8 |
| Q-11 | Performance expectation (e.g. time for 10,000 matches) and how to read NFR-05 "stream to disk" given the API returns each attachment whole | solution-architect, Santhosh | G3 | **Resolved.** Performance part by PD-07 (targets NFR-001..004, pending sponsor confirmation PA-01); NFR-05 memory-reading part by ADR-006 and architecture §7 (bounded memory per message; ASSUMPTION-16 confirmed) |
| Q-12 | Current manual effort/volume, to set a measured baseline for the benefit | Santhosh | G2 (nice to have) | **Resolved** (comment 10108): about 30 s per PDF by hand. Used as the baseline in §2, GOAL-01 and GOAL-11. Volume is still unknown |
| Q-13 | Wanted in the GUI: sign-out/revoke action, keyboard-only operation and screen-reader support? | product-manager, ux-expert | G2 | **Resolved by PD-04** (sign-out Should R3; keyboard Must R2; screen reader Should R3; no formal WCAG) |

## 13. Glossary
| Term | Definition |
|------|------------|
| Gmail API | Google's programmatic interface to a Gmail mailbox |
| OAuth 2.0 | Authorisation standard: the user approves access in a browser; the app never sees the password |
| Scope | The permission requested; `gmail.readonly` allows reading only |
| Consent screen | Google's page where the user approves access; status Testing or In production |
| Token / refresh token | Credentials issued after consent; the refresh token renews access without the browser. Secret |
| `credentials.json` | Client ID/secret file downloaded from Google Cloud; secret |
| `token.json` | Saved token file; secret |
| `invalid_grant` | Google error returned when a refresh token is revoked or expired |
| Test user | Account allowed to use an app whose consent screen is in Testing |
| `internalDate` | Time Gmail received the message (milliseconds since epoch) |
| messageId / partId | Gmail's message identifier / the MIME part position inside a message; together the manifest key |
| attachmentId | Gmail identifier for an attachment payload; changes between requests, so not a key |
| MIME part | A section of an email (body, attachment, nested message) |
| `message/rfc822` | A forwarded email attached inside another email |
| IANA time zone | Named zone such as `Asia/Kolkata` |
| Inclusive range | Start date from 00:00:00 through end date 23:59:59, in the chosen time zone |
| Collision / duplicate (naming) | A target file name that already exists (case-insensitive) in the output folder or was assigned earlier in the run |
| Manifest | File `.manifest.json` in the output folder recording what was saved, keyed by messageId + partId |
| Dry run | A run that lists planned file names and writes no PDFs |
| Shared core | The one body of logic used by both GUI and CLI (D-01) |
| Design tokens | Named shared values for type, spacing and colour (CLAUDE.md §9.2) |
| High-DPI | Honouring OS display scaling so text and controls stay crisp |
| SHA-256 | Content fingerprint of a file, used to detect identical PDFs |
| Atomic rename | Writing to a temporary file and renaming it into place so no partial file appears |
| MoSCoW | Must / Should / Could / Won't priority scale |

## 14. Sources
- `Gmail PDF Attachment Downloader — Requirements.md` (repo root, 2026-10-28): SEC-01..09, FR-01..18, NFR-01..05, LOG-01..05, §6.2 acceptance criteria.
- `docs/project-state.md` (intake, D-01, D-02, B-01, T-01, T-02).
- `CLAUDE.md` §1, §1a, §6, §9.
- Jira PGD-1 comments 10080 to 10084 (G0 GO, RISK-001..006, run resumed).
- Jira PGD-1 comments 10106 (G3 record, C7) and 10108 (delivery-lead answers to Q-01, Q-02, Q-04, Q-10, Q-12); decision-log D-28; ADR-002, ADR-005, ADR-006, ADR-007.
- No interviews, web research or mailbox data were used.
