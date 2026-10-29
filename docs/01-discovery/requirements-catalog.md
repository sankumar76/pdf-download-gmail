# Requirements Catalogue — Gmail PDF Attachment Downloader

> Owner: business-analyst · Version 0.1 (Draft) · 2026-10-29 · Gate G1 · Jira [PGD-1](https://sankumar76.atlassian.net/browse/PGD-1)
> Priority uses MoSCoW. **The source document has no priorities; every priority below is a BA proposal (ASSUMPTION-05) for product-manager to confirm at G2.**
> Original source IDs (SEC, FR, NFR, LOG) are kept unchanged for traceability. IDs without an original (CFG, VAL, EC, AC) are numbered by the BA in source order. product-manager may renumber in the PRD but must keep a mapping.

## How to read this catalogue
| Prefix | Meaning | Origin |
|--------|---------|--------|
| BRQ | Business requirement | BA, derived from source |
| UR | User requirement | BA, derived from source and D-01 |
| SEC / FR / NFR / LOG | Source requirements, original IDs | Req doc §2.2, §4, §5.1, §5.2 |
| CFG / VAL / EC / AC | Parameters, validations, edge cases, acceptance criteria | Req doc §3, §3, §5.3, §6.2 |
| GUI | Desktop GUI requirements | D-01, CLAUDE.md §9 |
| BR / DR / TR | Business rules, data, transition | BA |

Source abbreviations: **RD** = `Gmail PDF Attachment Downloader — Requirements.md`; **D-01** = PGD-1 comment 10081; **§9** = CLAUDE.md §9.

**Superseded source text:** RD §1 "Out of scope: A graphical interface" and the title wording "command-line Python tool" are **superseded by D-01**. The CLI remains, with RD §3 flags and LOG-05 exit codes, and a desktop GUI is added on the same core.

---

## Business Requirements (BRQ)
| ID | Requirement | Rationale | Source | Priority | Goal |
|----|-------------|-----------|--------|----------|------|
| BRQ-001 | The organisation can obtain every PDF attachment received in one Gmail account within an inclusive date range, without manually opening emails | Core problem; removes manual effort and missed files | RD §1 | Must | GOAL-01 |
| BRQ-002 | Every saved file has a predictable name that starts with the email's received date and is unique within the output folder | Findability, sortability, no clashes | RD §1, FR-11..15 | Must | GOAL-02 |
| BRQ-003 | No existing local file is ever overwritten or lost, and files cannot be written outside the chosen output folder | Protect user data and system integrity | RD §1, FR-16, SEC-09 | Must | GOAL-04 |
| BRQ-004 | Running the same range again adds no duplicate files; a stopped run can be resumed | Safe, repeatable operation on large mailboxes | FR-17, §5.3, AC-05 | Must | GOAL-03, GOAL-06 |
| BRQ-005 | The tool can only read the mailbox; it cannot send, delete, label or modify any email | Minimise damage from misuse or compromise | RD §1, SEC-01 | Must | GOAL-05 |
| BRQ-006 | Mailbox passwords and OAuth secrets are never stored by the tool beyond the token file, and never appear in logs, output, dialogs or the repository | Account compromise is the highest-impact risk (RISK-005) | RD §2, SEC-03..08 | Must | GOAL-05 |
| BRQ-007 | Each run leaves an audit trail (log file, CSV report, console/GUI summary) showing what was saved, renamed, skipped or failed | Accountability and troubleshooting | LOG-01..04 | Must | GOAL-02 |
| BRQ-008 | A failure on one message or attachment does not prevent the rest of the run from completing | Reliability on large mailboxes | NFR-02, §5.3 | Must | GOAL-06 |
| BRQ-009 | The same operations are available through a desktop GUI and a CLI, and both produce identical results | Decision D-01 | D-01 | Must | GOAL-07 |
| BRQ-010 | The GUI looks professional and consistent, adapts to window size and display scaling, and follows the shared design standards | Sponsor standard | §9 | Must | GOAL-08 |
| BRQ-011 | A first-time user can reach a successful dry run from the GUI quickly, after the one-time Google setup | Usability (PROPOSED metric) | D-01, BA proposal | Should | GOAL-09 |

## Stakeholder / User Requirements (UR)
Personas: **P-01** GUI user, **P-02** CLI user (both currently Santhosh; ASSUMPTION-01).

| ID | As a… | I need to… | So that… | Source | Priority | Acceptance hint |
|----|-------|------------|----------|--------|----------|-----------------|
| UR-001 | P-01/P-02 | Choose a start date, end date and optionally a time zone | The range matches my local calendar days | RD §3, FR-01 | Must | Boundary tests: 23:59:59 on end date included, 00:00:00 next day excluded |
| UR-002 | P-01/P-02 | Choose or confirm the output folder (default `./downloads`, created if missing) | I know where files land | RD §3 | Must | Folder created when absent |
| UR-003 | P-01/P-02 | Preview what would be saved (dry run) | I can check names before anything is written | RD §3, AC-09 | Must | Planned names listed; zero PDFs written |
| UR-004 | P-01/P-02 | Sign in to Google once in my browser and not be asked again on later runs | Access is convenient and I never hand over my password | RD §2, AC-01 | Must | First run opens consent for read-only; second run needs no browser |
| UR-005 | P-01 | See progress while a run is in progress | I know it is working on large mailboxes | GUI-06 | Must | Counts update during the run |
| UR-006 | P-01/P-02 | Stop a run safely at any time | I do not corrupt files or lose my place | NFR-03 | Must | Temp file finished or discarded; manifest saved; summary shown |
| UR-007 | P-01/P-02 | See a summary and open the log and CSV report | I can verify and audit the run | LOG-01..04 | Must | Summary fields per LOG-04; report path reachable from GUI |
| UR-008 | P-01/P-02 | Narrow the search with extra Gmail query text, e.g. `from:billing@vendor.com` | I get only the relevant sender or subject | RD §3 `--query` | Should | Query appended to the search |
| UR-009 | P-01/P-02 | Choose to include Spam and Trash | I can capture attachments that landed there | RD §3, EC-05 | Should | Off by default; flag passed to API |
| UR-010 | P-01/P-02 | Get a clear, actionable message when credentials are missing, the token is revoked, or an argument is wrong | I can fix the problem without reading code | VAL-01, VAL-03, SEC-07 | Must | Message names the next step; no secret shown |
| UR-011 | P-02 | Use exit codes 0/1/2/3 and flags in scripts | I can automate runs | LOG-05, RD §3 | Must | Exit codes per LOG-05 |
| UR-012 | P-01/P-02 | Resume a stopped run without duplicates | Large runs can be split over time | FR-17, EC-07 | Must | Second run skips previously saved attachments |
| UR-013 | P-01 | Revoke access / sign out from the app | I can remove access without hand-deleting files | RD §2.1 revoke note; BA proposal | Could | Pending Q-13 |

## Source Requirements — Security (SEC)
| ID | Requirement (clarified, same intent) | Rationale | Source | Priority | Acceptance hint |
|----|--------------------------------------|-----------|--------|----------|-----------------|
| SEC-01 | Request only the scope `https://www.googleapis.com/auth/gmail.readonly`; never `gmail.modify`, `mail.google.com` or any send scope | Least privilege | RD §2.2 | Must | Automated test asserts the requested scope list equals exactly one value |
| SEC-02 | Perform consent with a loopback-redirect local-server flow on an automatically chosen free port; the deprecated copy-paste (out-of-band) flow must not be used. RD names `InstalledAppFlow.run_local_server(port=0)` (CONSTRAINT: `google-auth-oauthlib`) | Supported, safer flow | RD §2.2 | Must | Consent opens in the browser; no code to paste |
| SEC-03 | Read credentials and token file locations from options or the environment variables `GMAIL_CREDENTIALS_PATH` and `GMAIL_TOKEN_PATH`; default `./secrets/` | Keep secrets outside code | RD §2.2, CFG-08, CFG-09 | Must | Override tests for flag, env var and default |
| SEC-04 | On macOS/Linux create `secrets/` with permission 700 and write `token.json` with 600; on Windows keep the secrets folder inside the user profile | Restrict local access | RD §2.2 | Must | Permission test on POSIX; path check on Windows |
| SEC-05 | `.gitignore` excludes `secrets/`, credential `*.json`, `token.json`, `.env` and the download folder | Prevent committing secrets and personal data | RD §2.2 | Must | Pattern check; secret scan clean |
| SEC-06 | Never print, log or include in error text, GUI dialogs or crash output the access token, refresh token or client secret | Credential leakage (RISK-005) | RD §2.2 | Must | Log/console/GUI scan test with sentinel secrets finds none |
| SEC-07 | If the token is expired, refresh it; if refresh fails (revoked or `invalid_grant`), delete the stale token and restart consent with a clear message | Recovery without manual file edits (RISK-003) | RD §2.2 | Must | Simulated `invalid_grant` leads to token removal and re-consent |
| SEC-08 | During development, no one and no agent opens or prints the contents of `credentials.json` or `token.json`; only paths are referenced | Process control | RD §2.2 | Must (process) | Review check; fixtures contain no real secrets |
| SEC-09 | Sanitise every attachment name before writing so the file lands only inside the output folder | Path traversal | RD §2.2, FR-12 | Must | `../../x.pdf` is written inside the output folder (AC-06) |

## Source Requirements — Functional (FR)
| ID | Requirement (clarified, same intent) | Rationale | Source | Priority | Acceptance hint |
|----|--------------------------------------|-----------|--------|----------|-----------------|
| FR-01 | Convert the start date at 00:00:00 and the day after the end date at 00:00:00, in the chosen time zone, to Unix epoch seconds | Exact inclusive range (BR-002) | RD §4.1 | Must | DST-crossing range test |
| FR-02 | List messages with the Gmail search `has:attachment filename:pdf after:<start_epoch> before:<end_plus_1_epoch>` plus optional extra query text; epoch seconds are used because Gmail reads calendar dates as Pacific time | Correct range regardless of zone | RD §4.1 | Must | Query string unit test. See Q-07 recall gap |
| FR-03 | Read all result pages (page size 500) until no next-page token remains | Complete results | RD §4.1 | Must | Mock with 3 pages |
| FR-04 | After fetching each message, re-check its `internalDate` against the range and skip any outside it | Guard against search-index edge cases | RD §4.1, BR-014 | Must | Out-of-range message skipped |
| FR-05 | Process messages oldest first by `internalDate`, then attachments in MIME part order, so suffix numbering is identical on every run | Determinism | RD §4.1, BR-004 | Must | Two runs on same fixture give same names |
| FR-06 | Fetch each message in full and walk the MIME tree recursively, including nested multipart parts and attached `message/rfc822` messages | Forwarded emails | RD §4.2 | Must | Nested fixture yields all PDFs |
| FR-07 | Treat a part as a PDF if its MIME type is `application/pdf`, or its name ends in `.pdf` (case-insensitive) with MIME type `application/octet-stream` | Real-world mislabelled PDFs | RD §4.2, BR-008 | Must | Matrix test |
| FR-08 | If the part has an attachment id, download it through the attachments call; if it has inline body data, use that; decode URL-safe base64 | Both Gmail representations | RD §4.2 | Must | Both paths tested |
| FR-09 | Verify decoded bytes start with `%PDF-`; otherwise skip the part and report `NOT_A_PDF` | Reject disguised files | RD §4.2 | Must | Non-PDF rejected |
| FR-10 | A PDF with no file name is named `attachment.pdf` | Defined default | RD §4.2, BR-009 | Must | Example row 21 Jan |
| FR-11 | Name each file `YYYYMMDD_<original name>` where the date is the email's `internalDate` in the chosen time zone; fall back to the `Date` header only if `internalDate` is missing | Predictable names (BR-001) | RD §4.3 | Must | Example table |
| FR-12 | Sanitise the original name before prefixing: strip folder paths; replace `<>:"/\|?*` and control characters with `_`; collapse repeated spaces; trim leading/trailing dots and spaces; decode RFC 2047/2231 encoded names; keep Unicode letters; force extension to lower-case `.pdf` | Safe, readable names | RD §4.3, BR-011 | Must | Table-driven tests |
| FR-13 | Keep the full name within 200 characters by shortening only the stem, never the date prefix, suffix or extension | File-system limits | RD §4.3, BR-010 | Must | 300-character name test |
| FR-14 | A name is a duplicate if it already exists in the output folder or was assigned earlier in the same run; compare case-insensitively | Windows/macOS case-insensitivity | RD §4.4, BR-003 | Must | `Invoice.pdf` vs `invoice.PDF` |
| FR-15 | On a duplicate insert `_1` before `.pdf`, then `_2`, `_3`, … until free; the first file keeps the plain name | Deterministic suffixes | RD §4.4, BR-003 | Must | Example table rows 1 to 3 |
| FR-16 | Never overwrite: write to a temporary file in the output folder, then rename it into place atomically | No partial or overwritten files | RD §4.4, BR-005 | Must | Interrupted write leaves no partial target |
| FR-17 | Keep a manifest (`.manifest.json` in the output folder) keyed by Gmail messageId + MIME partId; on re-run skip anything already in it. attachmentId is not used because it changes | Idempotent re-runs | RD §4.4, BR-006 | Must | Second run: 0 new files, all `SKIPPED_ALREADY_DOWNLOADED` |
| FR-18 | Different files with the same name are both kept. Byte-identical PDFs from different emails are both kept by default; an optional "skip identical" option skips a file whose SHA-256 is already in the manifest | Never lose data by default | RD §4.4, BR-007 | Must (default behaviour); Could (optional skip) | Default keeps both; option skips second. See Q-05 |

## Source Requirements — Reliability (NFR)
No performance target (throughput, elapsed time) exists in the source (Q-11).

| ID | Requirement (clarified, same intent) | Rationale | Source | Priority | Acceptance hint |
|----|--------------------------------------|-----------|--------|----------|-----------------|
| NFR-01 | Retry HTTP 429 and 5xx with exponential backoff and jitter: start 1 s, maximum 64 s, 6 attempts; honour `Retry-After` when present | Quota and transient errors | RD §5.1 | Must | Mock 429 then success; attempt count and delays asserted |
| NFR-02 | One failed message or attachment must not stop the run; log it and continue | BRQ-008 | RD §5.1 | Must | Injected failure; run completes, exit code 1 |
| NFR-03 | Ctrl+C (CLI) and Cancel (GUI) stop cleanly: finish or discard the current temporary file, save the manifest, print the summary | No corruption; resumable | RD §5.1, GUI-07 | Must | No temp files remain; manifest valid |
| NFR-04 | Batch requests or a pool of at most 4 workers may be used for message fetching only if needed for speed; file-name assignment stays single-threaded so suffixes are deterministic | Determinism over speed | RD §5.1 | Could | Name-assignment order test |
| NFR-05 | Memory use stays bounded: process one message at a time; attachments up to Gmail's 25 MB limit must work. RD wording "stream each PDF to disk" is interpreted as bounded memory per message (ASSUMPTION-16, Q-11) | Large attachments | RD §5.1 | Must | 25 MB fixture; peak memory does not grow with the number of messages |

## Source Requirements — Logging and Output (LOG)
| ID | Requirement (clarified, same intent) | Rationale | Source | Priority | Acceptance hint |
|----|--------------------------------------|-----------|--------|----------|-----------------|
| LOG-01 | Write `downloads/logs/run_<YYYYMMDD_HHMMSS>.log` and `downloads/logs/report_<YYYYMMDD_HHMMSS>.csv` per run (under the output folder) | Audit trail | RD §5.2 | Must | Both files exist after a run |
| LOG-02 | CSV columns, in order: `status`, `saved_file`, `original_name`, `email_date`, `from`, `subject`, `message_id`, `part_id`, `size_bytes`, `sha256` | Complete report | RD §5.2 | Must | Header test |
| LOG-03 | Status values: `SAVED`, `SAVED_RENAMED` (suffix added), `SKIPPED_ALREADY_DOWNLOADED`, `SKIPPED_IDENTICAL`, `NOT_A_PDF`, `ERROR` | Consistent reporting | RD §5.2 | Must | Each status produced in tests |
| LOG-04 | End each run with a summary: messages scanned, PDFs saved, renamed, skipped, errors, total size, elapsed time (console for CLI, summary view for GUI) | At-a-glance result | RD §5.2, GUI-08 | Must | All seven fields present |
| LOG-05 | Exit code 0 on success, 1 if any attachment errored, 2 for bad arguments, 3 for missing credentials or failed authentication | Scriptability | RD §5.2 | Must | One test per code |

## Parameters (CFG), Validations (VAL), Edge Cases (EC), Acceptance Criteria (AC)
| ID | Statement | Source | Priority |
|----|-----------|--------|----------|
| CFG-01 | Start date, required, `YYYY-MM-DD`, inclusive from 00:00:00 (CLI `--start`) | RD §3 | Must |
| CFG-02 | End date, required, `YYYY-MM-DD`, inclusive to 23:59:59 (`--end`) | RD §3 | Must |
| CFG-03 | Output folder, default `./downloads`, created if missing (`--out`) | RD §3 | Must |
| CFG-04 | Time zone, IANA name, default system local zone, used for the range and the file-name date (`--tz`) | RD §3, ASSUMPTION-10 | Must |
| CFG-05 | Extra Gmail query appended to the search (`--query`), default empty | RD §3 | Should |
| CFG-06 | Include Spam/Trash (`--include-spam-trash`), default off | RD §3 | Should |
| CFG-07 | Dry run (`--dry-run`), default off: lists what would be saved, writes nothing | RD §3 | Must |
| CFG-08 | Credentials path (`--credentials` / `GMAIL_CREDENTIALS_PATH`), default `./secrets/credentials.json` | RD §3, SEC-03 | Must |
| CFG-09 | Token path (`--token` / `GMAIL_TOKEN_PATH`), default `./secrets/token.json` | RD §3, SEC-03 | Must |
| CFG-10 | Log level (`--log-level`) `DEBUG`/`INFO`/`WARNING`/`ERROR`, default `INFO` | RD §3 | Should |
| CFG-11 | Command-line flags override values from an optional `config.yaml` or `.env` (YAML dependency: Q-08) | RD §3 | Should |
| VAL-01 | Reject the run if start is after end or either date is malformed: one-line error, exit code 2 | RD §3 | Must |
| VAL-02 | Warn but continue if the end date is in the future | RD §3 | Must |
| VAL-03 | If `credentials.json` is missing, show the setup steps of RD §2.1 and exit with code 3 (GUI shows the same steps, GUI-10) | RD §3 | Must |
| EC-01 | A message with several PDFs: all are saved | RD §5.3 | Must |
| EC-02 | The same PDF in several messages of one thread: each message's copy is saved (subject to optional skip-identical) | RD §5.3 | Must |
| EC-03 | Password-protected or corrupt PDFs are saved as-is; only the `%PDF-` header is checked | RD §5.3 | Must |
| EC-04 | Google Drive attachments (links, not real attachments) are not downloaded | RD §5.3 | Must |
| EC-05 | Spam and Trash are excluded unless the include option is set | RD §5.3 | Must |
| EC-06 | A range with no matches ends with exit 0 and "0 PDFs found" | RD §5.3 | Must |
| EC-07 | Very large mailboxes (10,000+ matches): pagination and the manifest allow a stopped run to resume | RD §5.3 | Must |
| AC-01 | First run opens the browser consent for read-only Gmail access only; later runs need no browser | RD §6.2 | Must |
| AC-02 | Only PDFs from emails received inside the inclusive range (chosen time zone) are saved | RD §6.2 | Must |
| AC-03 | Every file name starts with the email date as `YYYYMMDD_` | RD §6.2 | Must |
| AC-04 | Collisions produce `_1`, `_2`, … in sequence, matching the RD §4.4 example table; nothing is overwritten | RD §6.2 | Must |
| AC-05 | Re-running the same range saves 0 new files and reports them `SKIPPED_ALREADY_DOWNLOADED` | RD §6.2 | Must |
| AC-06 | Malicious names such as `../../x.pdf` are written inside the output folder only | RD §6.2 | Must |
| AC-07 | No token, secret or credential appears in logs, console output or the repository | RD §6.2 | Must |
| AC-08 | Unit tests cover naming, sanitising, suffix sequencing, date-range boundaries (23:59 on the end date included, 00:00 next day excluded), nested MIME parts and non-PDF rejection; all pass under pytest | RD §6.2 | Must |
| AC-09 | Dry run lists planned file names and writes no PDFs | RD §6.2 | Must |

Extension for D-01 (BA addition): every AC above must hold for **both** the GUI and the CLI (BRQ-009).

## GUI Requirements (GUI)
Source for GUI-01..18: D-01 and CLAUDE.md §9 as noted. Framework choice is a G3 decision (RISK-001); nothing below prescribes one.

| ID | Requirement | Rationale | Source | Priority | Acceptance hint |
|----|-------------|-----------|--------|----------|-----------------|
| GUI-01 | The product provides a desktop application with a graphical window from which a user can complete the whole workflow: set parameters, authenticate, preview, run, cancel and review results. It is neither a website nor CLI-only | Product form | D-01, §9 | Must | End-to-end walkthrough with no command typing |
| GUI-02 | GUI and CLI use one shared core; for identical inputs and mailbox state they produce identical file names, statuses, manifest, log and CSV content. (CONSTRAINT) | One behaviour, one set of tests | D-01 | Must | Same fixture run through both gives byte-identical CSV (excluding timestamps) |
| GUI-03 | The GUI lets the user set every user-facing parameter in CFG-01..07 and CFG-10; credential and token paths are available in an advanced area. Optional behaviours in MVP: see Q-05 (ASSUMPTION-06) | Parity with CLI | D-01, RD §3 | Must | Each parameter reachable in GUI |
| GUI-04 | The GUI validates inputs with the same rules and messages as VAL-01 and VAL-02 and shows errors next to the field before starting a run | Early, clear feedback | D-01, VAL-01..02 | Must | Start date after end date blocks Run with inline message |
| GUI-05 | The GUI offers a dry run that shows the planned file names in a list and writes no PDFs | AC-09 | D-01, AC-09 | Must | Output folder unchanged after dry run |
| GUI-06 | During a run the GUI shows progress: messages scanned, PDFs saved, renamed, skipped, errors | UR-005 | D-01, LOG-04 | Must | Counts change while running |
| GUI-07 | The GUI provides a Cancel control with the semantics of NFR-03 | NFR-03 | D-01 | Must | Cancel mid-run leaves no temp file and a valid manifest |
| GUI-08 | On completion the GUI shows the LOG-04 summary and lets the user open the output folder, the run log and the CSV report | UR-007 | D-01, LOG-04 | Must | Links open the right locations |
| GUI-09 | Window controls remain responsive to user input while a run is in progress | A frozen window looks like a crash | D-01 | Must | Cancel and window resize work mid-run |
| GUI-10 | The GUI starts the browser consent flow (SEC-02) and, if credentials are missing, shows the RD §2.1 setup steps instead of a stack trace | VAL-03, UR-004 | D-01, VAL-03 | Must | Missing file shows steps; no exit without a message |
| GUI-11 | Every message shown by the GUI (errors, dialogs, details panes, copied diagnostics) passes through the same redaction as CLI output and never contains tokens or the client secret | SEC-06, RISK-005 | D-01, SEC-06 | Must | Sentinel-secret test on GUI error paths |
| GUI-12 | Typography uses exactly four roles — main headings, subheadings, body text, small labels — each with one defined size and weight, defined once as shared tokens | Consistency | §9.2 | Must | Review finds no other text sizes/weights |
| GUI-13 | All padding, margins and gaps come from one shared spacing scale defined once | Consistency | §9.2 | Must | No ad-hoc spacing values in screen code |
| GUI-14 | All buttons use one standard style implemented as one shared reusable component; variants (primary, secondary, destructive) exist only through that component | Consistency, reuse | §9.2 | Must | One button implementation; no per-screen styling |
| GUI-15 | All colours come from one palette defined as shared tokens; no hard-coded colours anywhere | Consistency | §9.2 | Must | Search finds no literal colour values outside the token definition |
| GUI-16 | Windows are resizable with a defined minimum size; layouts reflow cleanly from small laptop screens to large monitors | Adaptability | §9.3 | Must | Check at minimum size and at a large resolution |
| GUI-17 | The app honours operating-system display scaling (high-DPI) so text and controls stay crisp and correctly sized | Adaptability | §9.3 | Must | Check at 100 %, 150 % and 200 % scaling (Windows) |
| GUI-18 | The GUI has a modern, professional appearance in which every screen looks designed by the same hand. "Modern, professional" is subjective; it is verified through GUI-12..17 plus a ux-expert review checklist | Quality bar | §9.1 | Must | UX review sign-off against checklist |
| GUI-19 | The GUI is operable by keyboard alone with a visible focus indicator (PROPOSED, not sourced; confirm via Q-13) | Basic accessibility | BA proposal | Should | Tab order covers all controls |

## Business Rules (BR)
| ID | Rule | Type | Source | Exceptions |
|----|------|------|--------|------------|
| BR-001 | File name = `YYYYMMDD_` + sanitised original name, where `YYYYMMDD` is the date of the email's `internalDate` in the chosen time zone (system local zone by default). If `internalDate` is missing, use the `Date` header | Calculation | FR-11 | None |
| BR-002 | The date range is inclusive at both ends in the chosen time zone: from the start date at 00:00:00 up to and including the end date 23:59:59; equivalent to start 00:00 (included) to end-date-plus-one-calendar-day 00:00 (excluded). The next-day boundary is computed as a calendar day, not as +86,400 seconds, so daylight-saving changes are handled | Validation / calculation | FR-01, AC-02, AC-08 | None |
| BR-003 | A target name collides if it already exists in the output folder or was assigned earlier in the run (case-insensitive, whole name including the date prefix). The first holder keeps the plain name; later ones get `_1`, `_2`, … before `.pdf`, using the first free number | Policy | FR-14, FR-15 | None |
| BR-004 | Processing order is oldest `internalDate` first, then MIME part order. Equal `internalDate` ties are broken by messageId ascending (ASSUMPTION-07, Q-09). Name assignment is single-threaded | Policy | FR-05, NFR-04 | Tie-break pending Q-09 |
| BR-005 | An existing file is never overwritten or deleted by the tool; writes go to a temporary file renamed atomically | Policy | FR-16 | None |
| BR-006 | An attachment whose messageId + partId is already in the manifest is skipped and reported `SKIPPED_ALREADY_DOWNLOADED`; the manifest belongs to its output folder (ASSUMPTION-08, ASSUMPTION-09) | Policy | FR-17, AC-05 | Manifest lost or file deleted: see Q-06 |
| BR-007 | Files with the same name but different content are all kept. Byte-identical PDFs from different emails are all kept unless the optional skip-identical rule is on, in which case a PDF whose SHA-256 is already in the manifest is skipped as `SKIPPED_IDENTICAL` | Policy | FR-18, EC-02 | Optional rule is Could |
| BR-008 | A part is a PDF candidate if MIME type is `application/pdf`, or MIME type is `application/octet-stream` and the name ends in `.pdf` (case-insensitive). A candidate is saved only if its decoded bytes start with `%PDF-`; otherwise `NOT_A_PDF` | Validation | FR-07, FR-09 | Password-protected or corrupt PDFs are saved (EC-03) |
| BR-009 | A PDF without a file name is named `attachment.pdf` before prefixing | Policy | FR-10 | None |
| BR-010 | Maximum full file-name length is 200 characters; only the stem is shortened | Validation | FR-13 | None |
| BR-011 | Sanitisation (FR-12) is applied before prefixing; the resulting path must resolve inside the output folder or the file is not written and an `ERROR` is reported | Validation | FR-12, SEC-09 | None |
| BR-012 | Spam and Trash messages are excluded unless the user opts in | Policy | EC-05 | None |
| BR-013 | The application requests the single scope `gmail.readonly` and performs no mailbox write operations | Authorisation | SEC-01 | None |
| BR-014 | A message whose `internalDate` is outside the range is skipped even if the search returned it | Validation | FR-04 | None |

## Data Requirements (DR)
No database (CONSTRAINT-04); all data is local files. Retention is not stated in the source: ASSUMPTION-11 applies (user-managed, no automatic deletion).

| ID | Entity / data | Key attributes | Owner | Sensitivity | Retention | Source of truth |
|----|---------------|----------------|-------|-------------|-----------|-----------------|
| DR-001 | Email message metadata (read transiently) | messageId, `internalDate`, from, subject, parts | Mailbox owner | Confidential | Not stored except as fields in DR-006/DR-007 | Gmail |
| DR-002 | Saved PDF files | Final name, bytes, SHA-256, size | Mailbox owner | Confidential (may be Restricted if financial/personal) | User-managed | Output folder |
| DR-003 | OAuth client credentials (`credentials.json`) | Client ID, client secret | Mailbox owner | Restricted | Until the Google client is deleted | Google Cloud Console |
| DR-004 | OAuth token (`token.json`) | Access/refresh token, expiry | Mailbox owner | Restricted | Deleted on revoke or `invalid_grant` (SEC-07) | Google (issued), local file (copy) |
| DR-005 | Manifest (`.manifest.json`) | messageId + partId key, saved file name, SHA-256, status, timestamp | Mailbox owner | Internal | Lifetime of the output folder; per output folder | Output folder |
| DR-006 | Run log | Timestamped events, level, no secrets | Mailbox owner | Confidential (may include sender/subject) | User-managed | `logs/` under output folder |
| DR-007 | CSV report | Columns per LOG-02 | Mailbox owner | Confidential (sender, subject) | User-managed | `logs/` under output folder |
| DR-008 | Run configuration (flags, optional `config.yaml`/`.env`, GUI settings) | Parameters CFG-01..11, file paths | Mailbox owner | Internal; must hold no secret values, only paths | User-managed | Local file / GUI session |

## Transition Requirements (TR)
Greenfield: no data migration and no parallel run (Santhosh is the only user).

| ID | Requirement | Owner | Priority |
|----|-------------|-------|----------|
| TR-001 | README documents the one-time Google Cloud setup of RD §2.1 (project, Gmail API, consent screen with `gmail.readonly` only, Desktop OAuth client, placing `credentials.json` in `secrets/`) and the same steps are reachable from the GUI (GUI-10) | developer (README), ux-expert (GUI flow) | Must |
| TR-002 | README documents usage for GUI and CLI, including all flags, exit codes and the output layout | developer | Must |
| TR-003 | README explains the 7-day token expiry in Testing status and how to publish the consent screen to In production (RISK-003) | developer | Should |
| TR-004 | README documents revoking access (Google Account → Security → Third-party apps, then delete `token.json`) | developer | Should |
| TR-005 | Before the first real run the user performs a dry run on a one-week range (RD §6) | Santhosh | Should |
| TR-006 | Santhosh completes the Google Cloud setup (TR-001) before QA acceptance testing against a real mailbox; until then verification uses mocks only | Santhosh | Must |

## Constraints
| ID | Constraint | Source |
|----|------------|--------|
| CONSTRAINT-01 | Only `gmail.readonly` | SEC-01 |
| CONSTRAINT-02 | Python 3.10+ (3.12 target) | RD §1, CLAUDE.md §1 |
| CONSTRAINT-03 | Google API client libraries only; others need justification (GUI framework via G3 ADR) | RD §1, RISK-001 |
| CONSTRAINT-04 | No database | CLAUDE.md §9 |
| CONSTRAINT-05 | Desktop GUI + CLI on one shared core | D-01 |
| CONSTRAINT-06 | CLAUDE.md §9 design standards | CLAUDE.md §9 |
| CONSTRAINT-07 | Local processing only | RD §1 |
| CONSTRAINT-08 | 25 MB attachment limit must work | NFR-05 |
| CONSTRAINT-09 | pytest, ruff, mypy strict; package `gmail_pdf` | CLAUDE.md §1 |
| CONSTRAINT-10 | Secret files never read or printed during development | SEC-08 |

## Assumptions
| ID | Assumption | Impact if false | Owner |
|----|------------|-----------------|-------|
| ASSUMPTION-01 | One user and one Gmail account per run | Multi-account redesign | Santhosh |
| ASSUMPTION-02 | Windows 11 primary platform; macOS/Linux best-effort | Packaging, SEC-04, GUI testing scope | Santhosh (Q-02) |
| ASSUMPTION-03 | Python is installed on the user's machine; installer/packaging is not part of the MVP | Packaging effort added | Santhosh (Q-03) |
| ASSUMPTION-04 | Consent screen is in Testing status; tokens expire after about 7 days (RISK-003) | Different re-consent cadence | Santhosh (Q-04) |
| ASSUMPTION-05 | MoSCoW priorities here are BA proposals | PRD scope shifts | product-manager (G2) |
| ASSUMPTION-06 | GUI exposes the same parameters as the CLI, with credential and token paths under "advanced"; optional behaviours follow Q-05 | GUI-03 scope changes | product-manager (Q-05) |
| ASSUMPTION-07 | Equal-`internalDate` messages are ordered by messageId ascending | Suffix numbering differs | product-manager (Q-09) |
| ASSUMPTION-08 | Idempotency relies on the manifest; per output folder; a lost manifest means a re-run behaves like a first run (`_1` suffixes) | Duplicate files on re-run | product-manager (Q-06) |
| ASSUMPTION-09 | The manifest is authoritative: an attachment in the manifest is skipped even if the user deleted the saved file | User cannot re-fetch deleted files without clearing the manifest | product-manager (Q-06) |
| ASSUMPTION-10 | GUI default time zone is the system local zone, shown and editable | Wrong date prefix near midnight | ux-expert / product-manager |
| ASSUMPTION-11 | Retention of downloads, logs and reports is user-managed; no automatic deletion | Add retention features | Santhosh (Q-10) |
| ASSUMPTION-12 | The app sends no telemetry and contacts only Google's APIs | Privacy review needed | solution-architect |
| ASSUMPTION-13 | Internet access to Google APIs is available; no proxy support is needed | Proxy feature | Santhosh |
| ASSUMPTION-14 | No deadline or budget has been set | Planning constraints change | Santhosh (Q-01) |
| ASSUMPTION-15 | The `filename:pdf` search is accepted as the candidate filter, even though it may miss PDFs without a file name | GOAL-01 recall below 100 % | solution-architect (Q-07) |
| ASSUMPTION-16 | NFR-05 means bounded memory per message, not byte-by-byte streaming | Different memory design | solution-architect (Q-11) |

## Open Questions
None blocks G2 entry, so no Jira question issues were created. Each has a working assumption.

| ID | Question | Affects | Owner | Needed by | Status |
|----|----------|---------|-------|-----------|--------|
| Q-01 | Target date or deadline for MVP and GUI? | Planning, GOAL "by when" | Santhosh | G2 | Open (ASSUMPTION-14) |
| Q-02 | Which operating systems must be supported? | SEC-04, GUI-17, QA scope | Santhosh | G2 | Open (ASSUMPTION-02) |
| Q-03 | Delivery form: run from source, pip install, or standalone executable? | TR-001..002, architecture | Santhosh, solution-architect | G3 | Open (ASSUMPTION-03) |
| Q-04 | Personal Gmail or Workspace? Consent screen Testing or In production? Is verification needed? | SEC-07, RISK-003, TR-003 | Santhosh | G3 | Open (ASSUMPTION-04) |
| Q-05 | Must the GUI expose every CLI option; which optional ones (`--skip-identical`, `--query`, `--include-spam-trash`) are in the MVP? | GUI-03, FR-18, CFG-05..06 | product-manager | G2 | Open (ASSUMPTION-06) |
| Q-06 | Expected re-run behaviour when the manifest is lost or a saved file was deleted? | FR-17, BR-006, AC-05 | product-manager, Santhosh | G2 | Open (ASSUMPTION-08, 09) |
| Q-07 | How should PDFs with no file name be found, given the `filename:pdf` search filter? | FR-02, FR-10, GOAL-01 | solution-architect | G3 | Open (ASSUMPTION-15) |
| Q-08 | Are a YAML parser (`config.yaml`) and Windows time-zone data acceptable justified dependencies? | CFG-11, CFG-04, CONSTRAINT-03 | solution-architect | G3 | Open |
| Q-09 | Tie-break order when messages share the same `internalDate`? | FR-05, BR-004 | product-manager | G2 | Open (ASSUMPTION-07) |
| Q-10 | Retention, clean-up and privacy expectations for downloads, logs and CSV reports (they hold sender and subject)? | DR-002..008, compliance | Santhosh | G2 | Open (ASSUMPTION-11) |
| Q-11 | Performance expectation (e.g. run time for 10,000 matches) and acceptance of the NFR-05 reading? | NFR-04, NFR-05 | solution-architect, Santhosh | G3 | Open (ASSUMPTION-16) |
| Q-12 | Current manual effort and volume, to give a measured baseline? | Brief §2, GOAL baselines | Santhosh | G2 (nice to have) | Open |
| Q-13 | Wanted in the GUI: sign-out/revoke action, keyboard-only use, screen-reader support? | UR-013, GUI-19 | product-manager, ux-expert | G2 | Open |

## Issues for other roles
- **product-manager:** confirm MoSCoW; decide Q-05, Q-06, Q-09; reflect that D-01 splits the MVP into core+CLI and GUI (RISK-001); renumber with mapping if desired.
- **solution-architect:** RD §6.1 deliverable tree (`gmail_pdf_downloader.py`, module names) is a solution outline predating D-01, not a business requirement; treat as guidance. Decide Q-07, Q-08, Q-11; dependency justification for the GUI framework and any YAML/time-zone packages.
- **master:** done at G1 (register updated 2026-10-29): former PROPOSED-RISK-A/B/C are RISK-007/008/009; RISK-002 reduced (score 2, open); RISK-004 and RISK-006 closed.
- **ux-expert:** GUI-10 setup flow, GUI-18 review checklist, ASSUMPTION-10.
- **qa-engineer:** every AC-01..09 must be verified for both GUI and CLI.

## Quality check (BA self-check)
- Rewritten vague terms: "modern, professional" (GUI-18) given a verifiable proxy; "stream to disk" (NFR-05) flagged; "only if needed for speed" (NFR-04) kept as Could with no target (Q-11); "as appropriate" and "etc." not used.
- Source coverage: SEC-01..09, FR-01..18, NFR-01..05, LOG-01..05 all present (9 + 18 + 5 + 5 = 37 IDs). RD §3 table, validations, §5.3 edge cases and §6.2 criteria are catalogued as CFG/VAL/EC/AC.
