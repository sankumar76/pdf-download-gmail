# Product Requirements Document — Gmail PDF Attachment Downloader

| Field | Value |
|-------|-------|
| Version | 0.5 |
| Owner | product-manager |
| Date | 2026-10-31 |
| Status | G2 CONDITIONAL GO closed (v0.2); v0.3 resolves UX issues (PD-11..16); v0.4 closes G3 condition C8 and records the delivery lead's answers and decisions (PD-17..20, PD-10 updated); v0.5 states the FR-015 date bounds (PGD-16 AC-9, PA-12) |
| Source brief | `docs/01-discovery/project-brief.md` v0.1 (+ `requirements-catalog.md` v0.1, `stakeholder-map.md` v0.1) |
| Jira | [PGD-1](https://sankumar76.atlassian.net/browse/PGD-1) |
| Companion | [release-plan.md](release-plan.md) |

**ID conventions.** FR-NNN / NFR-NNN are PRD IDs (new numbering). Source IDs (RD FR-01, SEC-01, LOG-01, GUI-01 …) are mapped in §15, so nothing is orphaned. PRD-only items use `PD-` (product decision), `PA-` (PM assumption), `PQ-` (PM open question) to avoid colliding with the BA's `ASSUMPTION-`/`Q-` series. "RD" = `Gmail PDF Attachment Downloader — Requirements.md`.

## 0. G1 conditions closure (C2–C4), G2 condition C6 and decisions at a glance

| Item | Where closed | Outcome |
|------|--------------|---------|
| C2 audit-trail metric | §3 GOAL-10, FR-039..043 and 046, NFR-005 | New measurable goal GOAL-10: 100 % of non-dry-run runs (success, partial, cancelled, zero-match, failed auth, unreadable manifest, internal failure) leave a log and a CSV that reconcile with the run summary (v0.4: PD-18) |
| C3 performance NFR | §5 NFR-001..004 (PD-07) | Numeric targets proposed (**PA-01, pending sponsor confirmation at G8**); not a Won't |
| C4 GOAL-09 | §3 (PD-08) | Adopted as a **Should** success metric (not a release gate); **PA-02 pending sponsor confirmation at G8**; no FR depends on GOAL-09 alone |
| Q-05 GUI exposure / MVP flags | PD-01 | Decided |
| Q-06 manifest lost | PD-02 | Decided |
| Q-09 tie-break | PD-03 | Decided (messageId ascending, accepted) |
| Q-13 sign-out, keyboard, screen reader | PD-04 | Decided |
| MVP split core+CLI vs GUI (RISK-001) | §6, PD-05 | MVP = R1 (Core + CLI) + R2 (Desktop GUI); R1 ships alone |
| G2 C6 coverage target vs standards | NFR-022, PD-10 | v0.2 aligned the PRD to 100 % / 85 %. **Superseded in v0.4** by the delivery lead's change to coding-standards §6 (PGD-1 c.10108): at least 80 % of changed code per PR and at least 80 % of the whole package. The DoD says the same |
| UX issues to PM (ux-spec §11) | PD-11..16, FR-033/037/043/045/058/060, NFR-021 | v0.3: manifest advice reworded (PD-11), minimum window 800 × 560 (PD-12), outcome semantics for cancel / unreadable history / internal failure (PD-13), UA-07..09 accepted (PD-14), shortcuts (PD-15), `--help` allowed (PD-16). No FR added or removed; counts unchanged |
| **G3 C8 (v0.4)** | §4 FR-032/039/040/043/044, §5 NFR-005/009/016/022, §12, §14 | PD-17 NFR-009 growth clause reworded (AR-03); PD-18 an unreadable manifest writes a run log and a header-only CSV, no PDF, manifest untouched (AQ-03); PD-19 AQ-04 (cancel exits 1), AA-07 (CSV UTF-8 with BOM), AA-08 (timestamps in the run's zone) and AA-11 (full `--query` only at DEBUG) confirmed; PD-20 / GOAL-11 time saved against the sponsor's 30 s per PDF manual baseline (Q-12); PQ-01..03, Q-03, Q-07, Q-08, Q-11 closed in §12 |
| Delivery-lead answers (PGD-1 c.10108) | §12, §14.3 | Q-01 no deadline (as soon as possible, R1 first); Q-02 Windows 11; Q-12 about 30 s per PDF; Q-04 and Q-10 stay assumptions until G8; NFR-022 now 80 % / 80 %; shadcn is ignored for this project, so AQ-02 is not carried into this PRD |

The full list of decisions awaiting sponsor confirmation is in §14.3.

## 1. Vision

For **Santhosh (MD), who must collect every PDF attachment received in his Gmail account during a chosen period**, the Gmail PDF Attachment Downloader is a **local desktop application (with a CLI on the same core)** that saves each PDF as `YYYYMMDD_<name>.pdf` into a folder, with read-only mailbox access, no overwritten files and a re-run that adds nothing new. Unlike opening emails one by one, it is complete, repeatable and auditable. Unlike a generic mail-export tool, it can only read (one OAuth scope, `gmail.readonly`), never lets a credential reach a log or a dialog, and treats the sponsor's naming and collision rules as a contract. It is local, has no database and sends nothing anywhere except to Google's API.

## 2. Target Users & Personas

| Persona | Description | Key jobs-to-be-done | Frequency of use |
|---------|-------------|---------------------|------------------|
| P-01 GUI user (today Santhosh) — primary | Mailbox owner, non-developer comfort level assumed | Pick a date range, preview names, run, watch progress, cancel safely, open the folder/log/CSV | Frequency not stated. **PA-03:** ad hoc, one run per period. Manual effort today is about 30 s per PDF (Q-12) |
| P-02 CLI user (today Santhosh) — secondary | Same person scripting or repeating runs | Run with flags, rely on exit codes 0/1/2/3, schedule or re-run | Frequency not stated (PA-03) |
| Approver | Santhosh as sponsor (G8 sign-off) | Confirm the PA- items in §14.3 | Once per release |

One user and one Gmail account per run (ASSUMPTION-01). Other stakeholders (Google, senders, delivery team) are in `stakeholder-map.md`.

## 3. Outcomes & Success Metrics

Goals GOAL-01..09 come from the brief and keep its targets. **GOAL-10 is added by this PRD** to close C2 (the brief maps BRQ-007 to GOAL-02, whose metric is naming only); the brief now mirrors it. **GOAL-11 (time saved) is added in v0.4** from the sponsor's answer to Q-12; the business-analyst should mirror it in the brief (see §16).

| Goal | Metric | Type | Baseline | Target | Measurement method |
|------|--------|------|----------|--------|--------------------|
| GOAL-01 Complete retrieval | Share of PDFs in the inclusive range saved; PDFs saved from outside the range | Lagging | Manual, unmeasured | 100 % saved; 0 outside (23:59:59 end date in, 00:00:00 next day out). **Real-mailbox acceptance (PA-04):** 0 misses among ≥ 10 sponsor-named known PDFs in a one-week range | Fixture mailbox with nested MIME and boundary cases (CLI and GUI); one sponsor acceptance run at G7 (needs TR-006) |
| GOAL-02 Predictable naming | Files matching `YYYYMMDD_<sanitised>.pdf`; RD §4.4 example table reproduced | Lagging | Manual, inconsistent | 100 % match; 6/6 example rows exact | Table-driven tests; CSV `saved_file` pattern check |
| GOAL-03 Safe re-runs | New files from a second run of the same range; share of earlier attachments reported `SKIPPED_ALREADY_DOWNLOADED` | Lagging | n/a | 0 new; 100 % skipped (manifest intact) | Two-run fixture test; AC-05 |
| GOAL-04 No loss, no path escape | Files overwritten; files written outside the output folder | Lagging | n/a | 0 and 0 | Collision/malicious-name tests (AC-06); file-system diff before/after |
| GOAL-05 Credential and mailbox safety | Scopes requested; write API calls; secret occurrences in log, CSV, console, GUI text, errors, repo | Lagging | n/a | 1; 0; 0 | Recording mock asserts scope list and allowed methods; sentinel-secret test matrix; repo secret scan per PR |
| GOAL-06 Resilience and resumability | After Ctrl+C, Cancel or a hard kill then a re-run: duplicates and lost attachments; runs aborted by one failing message | Lagging | n/a | 0, 0, 0 (exit code 1 with summary instead) | Fault-injection and interrupt tests (NFR-007) |
| GOAL-07 GUI/CLI parity | Differences in names, statuses, CSV content for identical inputs and fixture | Leading | n/a | 0 differences (timestamps excluded) | Same fixture through both front ends; diff the CSVs |
| GOAL-08 Design-standard compliance (CLAUDE.md §9) | Hard-coded colours/sizes/spacing; non-standard buttons; layouts broken between minimum size and large monitor, at 100/150/200 % scaling | Leading | n/a | 0; 1 button component; 4 type roles; 0 broken layouts | Code search at G6; screenshot matrix at G7; ux-expert checklist (FR-062) |
| GOAL-09 Ease of first use — **adopted, Should (PD-08)** | Median time from launching the GUI to dry-run results shown for a one-week range, after the one-time Google setup | Lagging | n/a | ≤ 5 min, no command typing | Stopwatch, 3 trials by the sponsor at G7 (needs TR-006). **PA-02: sponsor confirms at G8; if dropped, no FR is removed** |
| **GOAL-10 Auditability (new, C2)** | For every run that passes input validation and is not a dry run (outcomes: success, some errors, cancelled, zero matches, authentication failure, unreadable manifest, internal failure; PD-18): (a) a run log and a CSV exist at the documented path (the CSV holds only the header when the run stops before examining any candidate); (b) CSV header equals the LOG-02 list exactly; (c) every PDF candidate examined has exactly one row with one valid LOG-03 status; (d) per-status row counts equal the summary counts | Lagging | n/a | 100 % of runs; 0 discrepancies. After a hard kill, ≤ 1 attachment is missing from the CSV | Automated reconciliation test over ≥ 8 scripted runs (the seven outcomes above plus a hard-kill run), for CLI and GUI; sponsor spot check on one real run |
| **GOAL-11 Time saved (new, v0.4; PD-20)** | (a) Tool time per PDF saved, against the manual baseline of **30 s per PDF** (the sponsor's estimate, Q-12, not a timed study); (b) net time saved on a real range of at least 50 PDFs = PDFs saved × 30 s − (hands-on time + tool time) | Lagging | About 30 s per PDF by hand (for example 100 PDFs ≈ 50 min) | (a) ≤ 3 s per PDF (≤ 10 % of the baseline) on the NFR-001 benchmark, whose target of 15 min per 1,000 messages is ≈ 0.9 s; (b) ≥ 50 % of the manual time saved. **Should metric, not a release gate; PA-11** | (a) NFR-001 benchmark time divided by PDFs saved; (b) one stopwatch-timed sponsor run on the real mailbox at G7 (needs TR-006), hands-on time as in GOAL-09. If the sponsor's real baseline differs, the figures are recomputed; no FR changes |

Leading indicators tracked per story set: AC-01..09 verified for both CLI and GUI (18 checks, target 18/18 at G7); 0 open Blocker/Critical review findings at G6.

## 4. Functional Requirements

Priority = MoSCoW (one per FR). Rel = first release (R1 Core + CLI, R2 Desktop GUI, R3 hardening, BL backlog; see §6). Goals are brief goals GOAL-01..10. Effort (pts) is relative PM sizing for §8 only.

### 4.1 Access and authentication (EPIC-01)
| ID | Requirement (user point of view) | Priority | Rel | Source | Goal | Fit criterion |
|----|----------------------------------|----------|-----|--------|------|---------------|
| FR-001 | I sign in once through my browser with read-only Gmail access. Later runs need no browser. The app never sees my password. | Must | R1 | UR-004, SEC-01, SEC-02, BR-013, BRQ-005 | GOAL-05 | Requested scope list equals exactly `gmail.readonly`; consent uses the loopback flow (no pasted code); second run opens no browser (AC-01) |
| FR-002 | I can point the app at my credentials and token files by option or environment variable (`GMAIL_CREDENTIALS_PATH`, `GMAIL_TOKEN_PATH`); defaults apply otherwise. | Must | R1 | SEC-03, CFG-08, CFG-09 | GOAL-05 | Tests for option, env var and default precedence |
| FR-003 | If my saved sign-in has expired it renews silently; if it was revoked or is invalid, the app removes the stale token and takes me through sign-in again with a clear message. | Must | R1 | SEC-07, UR-010, RISK-003 | GOAL-05 | Simulated `invalid_grant`: token file removed, consent restarted, message names the reason; no secret shown |
| FR-004 | My secrets are protected on disk and kept out of git: `secrets/` 700 and `token.json` 600 on macOS/Linux, inside the user profile on Windows; `.gitignore` covers `secrets/`, credential and token JSON, `.env`, the output folder. | Must | R1 | SEC-04, SEC-05 | GOAL-05 | POSIX permission test; Windows path check; `.gitignore` pattern test; repo secret scan clean |
| FR-005 | No token, refresh token or client secret ever appears in logs, CSV, console, GUI dialogs, details panes, copied diagnostics or crash output. One redaction path serves CLI and GUI. | Must | R1 (GUI surfaces in R2) | SEC-06, GUI-11, AC-07, RISK-005 | GOAL-05 | Sentinel-secret matrix over every error path, CLI and GUI, finds 0 occurrences |
| FR-006 | If `credentials.json` is missing I see the Google setup steps (RD §2.1) and what to do next, not a stack trace. CLI exits with code 3; the GUI shows the same steps. | Must | R1 (GUI in R2) | VAL-03, GUI-10, UR-010, TR-001 | GOAL-05, GOAL-09 | Missing-file test: steps shown, exit 3, no trace |
| FR-007 | I can sign out: the app removes the local token and tells me how to revoke access in my Google Account. | Should | R3 | UR-013, TR-004 | GOAL-05 | Token file gone after action; next run asks for consent; steps text shown. Revocation endpoint call is **not** included (PD-04) |

### 4.2 Finding messages (EPIC-02)
| ID | Requirement | Priority | Rel | Source | Goal | Fit criterion |
|----|-------------|----------|-----|--------|------|---------------|
| FR-008 | I choose a start and end date and optionally a time zone (default: system zone, shown and editable). The range is inclusive: start 00:00:00 through end 23:59:59 in that zone; the next-day boundary is a calendar day, not +86,400 s. | Must | R1 | UR-001, BR-002, CFG-01, CFG-02, CFG-04, ASSUMPTION-10 | GOAL-01 | Boundary tests: 23:59:59 end date in, 00:00:00 next day out; DST-crossing range |
| FR-009 | The app selects candidate messages with a Gmail search for attachments in the range using epoch-second bounds (Gmail reads calendar dates as Pacific time). | Must | R1 | FR-02 (RD), BRQ-001 | GOAL-01 | Query-string unit test; fixture messages inside/outside range |
| FR-010 | I can add extra Gmail search text (for example `from:billing@vendor.com`) in the CLI (`--query`) and the GUI. | Should | R1 (GUI field in R2) | UR-008, CFG-05 | GOAL-01 | Query appended; test with sender filter |
| FR-011 | All result pages are read (500 per page) until none remain. | Must | R1 | FR-03 (RD), EC-07 | GOAL-01 | Mock with 3 pages yields all messages |
| FR-012 | A message whose received time falls outside the range is skipped even if the search returned it. | Must | R1 | FR-04 (RD), BR-014 | GOAL-01 | Out-of-range message skipped, none saved |
| FR-013 | I can include Spam and Trash (off by default) in the CLI (`--include-spam-trash`) and the GUI. | Should | R1 (GUI in R2) | UR-009, CFG-06, EC-05, BR-012 | GOAL-01 | Default excludes; option passes `includeSpamTrash` |
| FR-014 | Runs process messages in a fixed order, so file names are the same on every run: received time ascending, then messageId ascending (length first, then lexicographic), then MIME parts in document order (PD-03). | Must | R1 | FR-05 (RD), BR-004, Q-09 | GOAL-02, GOAL-03 | Two runs on one fixture, including two messages with equal received time, give identical names |
| FR-015 | Invalid input is rejected before any call to Google: start after end, a malformed date, or a date outside 1970-01-02 to 9999-12-30 gives a one-line error (CLI exit 2; GUI inline message in FR-048). The bounds are calendar dates, the same in every time zone, for start and end alike; a date outside them is rejected, never adjusted. FR-008's choice of dates is read with these bounds. An end date in the future gives a warning and the run continues. | Must | R1 (GUI in R2) | VAL-01, VAL-02, UR-010, DEF-007 (PGD-69) | GOAL-01, GOAL-07 | Tests for malformed, reversed, out-of-bounds and future-end ranges; 1970-01-02 and 9999-12-30 accepted and 1970-01-01 and 9999-12-31 rejected, in every time zone |
| FR-016 | A range with no matching PDFs ends normally, reports "0 PDFs found", exit 0. | Must | R1 | EC-06 | GOAL-01 | Empty fixture: exit 0, summary shows 0 |
| FR-017 | PDFs that carry no file name, or a name the Gmail index does not match, are still found and saved (as `YYYYMMDD_attachment.pdf` when unnamed). The method is a G3 decision (spike on Q-07). | Should | R1 (conditional on spike) | FR-10 (RD), BRQ-001, RISK-007 | GOAL-01 | Fixture with an unnamed PDF part in an in-range message is saved. If the spike shows the extra Gmail calls break NFR-001/002, the architect raises a scope-change proposal and the README states the residual gap (PD-06) |

### 4.3 Extracting PDFs (EPIC-03)
| ID | Requirement | Priority | Rel | Source | Goal | Fit criterion |
|----|-------------|----------|-----|--------|------|---------------|
| FR-018 | Every PDF in a message is found, including PDFs inside nested multipart parts and inside forwarded (`message/rfc822`) emails; a message with several PDFs saves all of them. | Must | R1 | FR-06 (RD), EC-01, BRQ-001 | GOAL-01 | Nested and multi-PDF fixtures: all PDFs present |
| FR-019 | A part counts as a PDF if its type is `application/pdf`, or its name ends in `.pdf` (any case) with type `application/octet-stream`. Links to Drive-hosted files are not attachments and are ignored. | Must | R1 | FR-07 (RD), BR-008, EC-04 | GOAL-01 | Type/name matrix test; Drive-link-only message yields no row |
| FR-020 | The app gets the bytes of a part whether Gmail provides it as a separate attachment or inline, decoding URL-safe base64. | Must | R1 | FR-08 (RD) | GOAL-01 | Both representations tested |
| FR-021 | A part whose bytes do not start with `%PDF-` is not saved and is reported `NOT_A_PDF`. Password-protected or corrupt PDFs that pass the header check are saved as-is. | Must | R1 | FR-09 (RD), EC-03, BR-008 | GOAL-01, GOAL-04 | Disguised file rejected; encrypted PDF saved unchanged |

### 4.4 Naming (EPIC-04)
| ID | Requirement | Priority | Rel | Source | Goal | Fit criterion |
|----|-------------|----------|-----|--------|------|---------------|
| FR-022 | Each file is named `YYYYMMDD_<original name>`, the date being the email's received date in the chosen time zone; the `Date` header is used only if the received date is missing. | Must | R1 | FR-11 (RD), BR-001, AC-03 | GOAL-02 | Example table rows 1..6 exact; near-midnight test in two zones |
| FR-023 | Names are sanitised before prefixing: folder parts removed; `<>:"/\|?*` and control characters become `_`; repeated spaces collapsed; leading/trailing dots and spaces trimmed; RFC 2047/2231 names decoded; Unicode letters kept; extension forced to lower-case `.pdf`. | Must | R1 | FR-12 (RD), SEC-09, BR-011 | GOAL-02, GOAL-04 | Table-driven tests incl. `../../Report:Q4.pdf` → `20260120_Report_Q4.pdf` |
| FR-024 | A full file name never exceeds 200 characters; only the stem is shortened, never the date prefix, suffix or extension. | Must | R1 | FR-13 (RD), BR-010 | GOAL-02 | 300-character name test |
| FR-025 | A PDF with no file name is named `attachment.pdf` before prefixing. | Must | R1 | FR-10 (RD), BR-009 | GOAL-02 | Example row `20260121_attachment.pdf` |
| FR-026 | When a name is already taken (on disk or earlier in the run, compared case-insensitively) the new file gets `_1`, then `_2`, … before `.pdf`; the first file keeps the plain name. | Must | R1 | FR-14, FR-15 (RD), BR-003, AC-04 | GOAL-02, GOAL-04 | Example rows 1..3; `Invoice.pdf` vs `invoice.PDF` |
| FR-027 | A file is only ever written inside the output folder. If the final path resolves elsewhere the file is not written and an `ERROR` row is reported. | Must | R1 | SEC-09, BR-011, AC-06 | GOAL-04 | `../../x.pdf` and absolute-path names land inside the folder or error; none outside |

### 4.5 Saving and re-run safety (EPIC-05)
| ID | Requirement | Priority | Rel | Source | Goal | Fit criterion |
|----|-------------|----------|-----|--------|------|---------------|
| FR-028 | No existing file is ever overwritten or deleted. Each file is written to a temporary file and moved into place only when complete. | Must | R1 | FR-16 (RD), BR-005, BRQ-003 | GOAL-04 | Interrupted write leaves no partial file under a final name; existing file byte-identical after run |
| FR-029 | The app keeps a manifest in the output folder, keyed by messageId + partId. A re-run skips what is in it and reports `SKIPPED_ALREADY_DOWNLOADED`. A file I deleted by hand but still listed in the manifest is **not** re-downloaded (PD-02); to get it again I use a new output folder (PD-11). | Must | R1 | FR-17 (RD), BR-006, AC-05, UR-012 | GOAL-03 | Second run: 0 new files, 100 % skipped; deleted-file case: still skipped, and the notice says why and names the new-folder route (PD-11) |
| FR-030 | If a run is stopped for any reason, running the same range again continues without duplicates and without losing attachments. | Must | R1 | UR-012, EC-07, BRQ-004 | GOAL-06 | Kill mid-run, re-run: 0 duplicates, 0 lost (NFR-007) |
| FR-031 | Different files with the same name are both kept. Byte-identical PDFs from different emails are both kept by default. | Must | R1 | FR-18 (RD), BR-007, EC-02 | GOAL-04 | Two identical PDFs in two emails produce two files |
| FR-032 | If the manifest cannot be read, the run stops before saving any PDF, names the file, and tells me how to restore it or move it aside. It is never silently replaced. The run still leaves its run log and a header-only CSV, so the audit trail covers this outcome too (PD-18). | Should | R1 | RISK-008, PD-02, PD-18 | GOAL-03, GOAL-10 | Corrupt-manifest fixture (non-dry run): no PDF written; manifest and its backup byte-identical before and after; message shown; exit 1; run log present and CSV holds exactly the header row. A dry run on the same fixture writes nothing at all, shows the same message and exits 1 |
| FR-033 | If there is no manifest but the output folder already holds date-prefixed PDFs, or the manifest lists files that are missing, the app warns before and in the run summary (CLI and GUI). When the manifest is missing, the warning states the consequence: PDFs already in the folder will be saved again with `_1`, `_2` endings, and nothing is overwritten (PD-11). | Should | R1 | RISK-008, PD-02, PD-11 | GOAL-03 | Warning present in both scenarios; counts shown; missing-manifest wording includes the duplicate-suffix consequence and the new-folder alternative |
| FR-034 | If the manifest is missing, the app recognises PDFs it already saved and does not save them again: it rebuilds the manifest from earlier run reports and content hashes, matching each existing file at most once, and reports them `SKIPPED_ALREADY_DOWNLOADED`. Missing files are fetched again. | Should | R3 | RISK-008, Q-06, PD-02 | GOAL-03 | Delete manifest after a run, re-run: 0 new files; two identical PDFs each matched to a different file; deleted file re-fetched |
| FR-035 | An optional "skip identical" setting skips a PDF whose SHA-256 is already saved and reports `SKIPPED_IDENTICAL`. Off by default. | Could | BL | FR-18 (RD optional), BR-007, LOG-03 | GOAL-03 | Option on skips the second identical file; off keeps both |

### 4.6 Resilience (EPIC-06)
| ID | Requirement | Priority | Rel | Source | Goal | Fit criterion |
|----|-------------|----------|-----|--------|------|---------------|
| FR-036 | One failing message or attachment does not stop the run. It is logged as `ERROR`, the rest continues, and the run ends with exit code 1 and a summary. | Must | R1 | NFR-02 (RD), BRQ-008 | GOAL-06 | Inject faults at fetch, decode, write: run completes, other files saved |
| FR-037 | I can stop a run safely (Ctrl+C in the CLI, Cancel in the GUI). The current file is finished or discarded, the manifest is saved, the log and CSV are closed, and the summary is shown. The summary says the run was cancelled, that saved files are kept, and that running the same range again continues where it stopped (PD-13). | Must | R1 (GUI in R2) | NFR-03 (RD), UR-006, GUI-07 | GOAL-06, GOAL-10 | Stop mid-run: no temp file remains, manifest valid, summary shown with "cancelled" wording; a script sees a non-zero exit (FR-043) |
| FR-038 | Message fetching may use up to 4 parallel workers. File-name assignment stays single-threaded, so names equal those of a sequential run. **Trigger:** promote to Must if NFR-001 or NFR-002 fail on the first benchmark. | Could | BL | NFR-04 (RD) | GOAL-02 | Parallel and sequential runs on one fixture give identical names |

### 4.7 Audit trail, dry run (EPIC-07)
| ID | Requirement | Priority | Rel | Source | Goal | Fit criterion |
|----|-------------|----------|-----|--------|------|---------------|
| FR-039 | Every non-dry run writes a run log `logs/run_<YYYYMMDD_HHMMSS>.log` under the output folder, recording the app version, parameters (no secrets; the full `--query` text only at `DEBUG`, otherwise only its length), start/end time and one line per decision. Times in the log, the CSV and the two file names use the run's chosen time zone (PD-19). | Must | R1 | LOG-01, BRQ-007 | GOAL-10 | File present after success, error, cancel, zero-match, failed-auth, unreadable-manifest and injected internal-failure runs; query text absent at `INFO`, present at `DEBUG` |
| FR-040 | Every non-dry run writes `logs/report_<YYYYMMDD_HHMMSS>.csv` with the columns `status, saved_file, original_name, email_date, from, subject, message_id, part_id, size_bytes, sha256`, one row per PDF candidate examined. A message that cannot be read gives one `ERROR` row. Rows are written as each attachment completes. A run that stops before examining any candidate (failed authentication, unreadable manifest) still writes the CSV with the header only. The file is UTF-8 with a byte-order mark so that Excel shows non-ASCII subjects correctly; the columns and their order are unchanged (PD-19). | Must | R1 | LOG-01, LOG-02, BRQ-007 | GOAL-10 | First three bytes are EF BB BF; the header after the mark equals the list; row-per-candidate and reconciliation tests (GOAL-10 c, d); header-only CSV in the failed-auth and unreadable-manifest fixtures |
| FR-041 | Each row carries one status: `SAVED`, `SAVED_RENAMED`, `SKIPPED_ALREADY_DOWNLOADED`, `SKIPPED_IDENTICAL`, `NOT_A_PDF`, `ERROR`. | Must | R1 | LOG-03 | GOAL-10 | Each status produced in tests; no other value appears |
| FR-042 | Each run ends with a summary: messages scanned, PDFs saved, renamed, skipped, errors, total size, elapsed time (console for CLI; summary view for GUI in FR-052). | Must | R1 (GUI in R2) | LOG-04, UR-007 | GOAL-10 | All seven fields present; counts reconcile with the CSV |
| FR-043 | The CLI exits 0 on success (including 0 PDFs found and a dry run), 1 if any attachment errored, 2 for bad arguments, 3 for missing credentials or failed authentication. Outcomes the RD does not name must never look like success to a script (PD-13): a run I cancelled, a run stopped because the manifest cannot be read (FR-032), and an unexpected internal failure each end with a non-zero code other than 2 or 3, and print a different first line (`Run cancelled` / `error: <file> cannot be read ...` / `error: unexpected failure, see the run log`) with no stack trace or secret (FR-005). Mapping decided (D-21, confirmed by PD-19): all three exit **1**, so the sponsor's four-code contract (0/1/2/3) stays closed; the first line and the run result tell them apart; any new code needs a scope-change proposal. | Must | R1 | LOG-05, UR-011 | GOAL-10, GOAL-07 | One test per code; one test each for cancel, unreadable manifest and injected internal failure: exit code non-zero and not 2/3, distinguishing first line present, no stack trace |
| FR-044 | Dry run lists the file names a real run would assign and writes **nothing** into the output folder: no PDFs, no manifest, no logs, and the folder is not created (PD-05). Results are shown on screen. | Must | R1 (GUI list in FR-049) | CFG-07, AC-09, UR-003 | GOAL-02, GOAL-09 | Output folder tree identical before and after; planned names equal real-run names for the same mailbox state, except that a dry run fetches no attachment bytes (D-22): it cannot report `NOT_A_PDF` and labels its names "planned, not verified" |

### 4.8 Command line (EPIC-07)
| ID | Requirement | Priority | Rel | Source | Goal | Fit criterion |
|----|-------------|----------|-----|--------|------|---------------|
| FR-045 | The CLI accepts the RD §3 flags with their defaults (`--start`, `--end`, `--out` default `./downloads` created if missing, `--tz`, `--query`, `--include-spam-trash`, `--dry-run`, `--credentials`, `--token`, `--log-level`) and nothing else in MVP, except the standard `--help` / `-h`, which prints the flag table and exits 0 without contacting Google or reading credentials (PD-16). | Must | R1 | UR-001, UR-002, CFG-01..09, RD §3 | GOAL-07 | Flag table test; unknown flag → exit 2; `--help` prints every flag with its default, exit 0, no network call |
| FR-046 | I can set the log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`; default `INFO`). | Should | R1 | CFG-10 | GOAL-10 | Level changes log verbosity; secrets never appear at `DEBUG` (FR-005) |

### 4.9 Desktop GUI workflow (EPIC-09)
The GUI is a thin layer over the shared core (D-01). Framework choice is a G3 ADR (RISK-001).

| ID | Requirement | Priority | Rel | Source | Goal | Fit criterion |
|----|-------------|----------|-----|--------|------|---------------|
| FR-047 | One desktop window lets me do the whole job without typing commands: set start, end, time zone, output folder (with a browse button), optional query and Spam/Trash choice; sign in; run a dry run; run; cancel; review results (PD-01). | Must | R2 | GUI-01, GUI-03, BRQ-009, UR-001..004 | GOAL-07, GOAL-09 | Walkthrough from launch to saved files with no terminal |
| FR-048 | The GUI checks my inputs with the same rules and messages as FR-015 and shows errors next to the field before the run starts. | Must | R2 | GUI-04 | GOAL-07 | Start after end blocks Run with an inline message |
| FR-049 | A dry run shows the planned file names in a list. | Must | R2 | GUI-05, UR-003 | GOAL-07, GOAL-02 | Output folder unchanged; list equals CLI dry run |
| FR-050 | While a run is in progress I see live counts: messages scanned, saved, renamed, skipped, errors. | Must | R2 | GUI-06, UR-005 | GOAL-07 | Counts change during a slow-mock run |
| FR-051 | A Cancel control is available during a run and behaves as FR-037. | Must | R2 | GUI-07, UR-006 | GOAL-06, GOAL-07 | Cancel mid-run leaves no temp file, valid manifest |
| FR-052 | When a run ends I see the FR-042 summary and can open the output folder, the run log and the CSV from the window. | Must | R2 | GUI-08, UR-007 | GOAL-10, GOAL-07 | Each link opens the right location |
| FR-053 | The window stays responsive during a run (resize, move, Cancel). | Must | R2 | GUI-09 | GOAL-07 | NFR-004 |
| FR-064 | GUI and CLI give identical results for identical inputs and mailbox state: names, statuses, manifest, log and CSV content (timestamps excluded). | Must | R2 | GUI-02, BRQ-009 | GOAL-07 | Same fixture through both; CSVs equal |
| FR-061 | An "Advanced" area in the GUI sets credentials path, token path and log level. Until then these are set by CLI options or environment variables (PD-01). | Should | R3 | GUI-03, CFG-08..10 | GOAL-07 | Each advanced field changes the same behaviour as its CLI option |

### 4.10 GUI design system and adaptability (EPIC-10) — CLAUDE.md §9
| ID | Requirement | Priority | Rel | Source | Goal | Fit criterion |
|----|-------------|----------|-----|--------|------|---------------|
| FR-054 | Text uses exactly four roles — main headings, subheadings, body text, small labels — each with one size and weight, defined once as shared tokens. | Must | R2 | GUI-12, §9.2 | GOAL-08 | Code search: no other text sizes or weights |
| FR-055 | All padding, margins and gaps come from one spacing scale defined once. | Must | R2 | GUI-13, §9.2 | GOAL-08 | No literal spacing values outside the token file |
| FR-056 | All buttons are one shared reusable component; primary, secondary and destructive exist only as variants of it. | Must | R2 | GUI-14, §9.2 | GOAL-08 | One button implementation; no per-screen button styling |
| FR-057 | All colours come from one palette defined as tokens; no hard-coded colours. | Must | R2 | GUI-15, §9.2 | GOAL-08 | No literal colour values outside the token file |
| FR-058 | Windows are resizable with a minimum size of **800 × 560 logical px** (PD-12) and lay out cleanly from small laptop screens to large monitors. Where the available work area is smaller than the minimum, the window is clamped to the work area and content scrolls rather than being clipped. | Must | R2 | GUI-16, §9.3 | GOAL-08 | Screenshot review at 800 × 560, at 1920 × 1080 with 200 % scaling (work area ≈ 960 × 520 logical px: window clamped, nothing clipped) and at 3840 × 2160 |
| FR-059 | Text and controls stay crisp and correctly sized at OS display scaling of 100 %, 150 % and 200 %. | Must | R2 | GUI-17, §9.3 | GOAL-08 | Screenshots at three scalings on Windows |
| FR-060 | I can operate every control with the keyboard alone, in a logical tab order, and always see which control has focus (PD-04). Keyboard shortcuts: **Enter** (focus in a field) starts a Dry run and **Ctrl+Enter** starts a Run; both are listed on screen, neither is the only way to start anything, and a Run never starts from a bare Enter (PD-15). | Must | R2 | GUI-19, Q-13, UA-10 | GOAL-08, GOAL-09 | NFR-017; Enter in a field starts a dry run (nothing written), Ctrl+Enter starts a run, bare Enter on a focused button activates that button only |
| FR-062 | A ux-expert checklist confirms that every screen looks designed by the same hand (modern, professional per §9.1) and uses FR-054..057 consistently. | Must | R2 | GUI-18, §9.1 | GOAL-08 | Signed checklist at G6/G7; no further polish work is required beyond it |
| FR-063 | A screen reader can read and operate the main flow (names and roles exposed for every control). | Should | R3 | Q-13, PD-04 | GOAL-08 | NFR-019 |

### 4.11 Documentation (EPIC-08)
| ID | Requirement | Priority | Rel | Source | Goal | Fit criterion |
|----|-------------|----------|-----|--------|------|---------------|
| FR-065 | A README lets me complete the one-time Google setup (RD §2.1), run the GUI and the CLI, and understand all flags, exit codes and the output layout. | Must | R1 (GUI parts R2) | TR-001, TR-002, BRQ-011 | GOAL-09, GOAL-07 | A reader unfamiliar with the project follows it to a successful dry run (also the GOAL-09 trial) |
| FR-066 | The README explains 7-day token expiry in Testing status and publishing to "In production", how to revoke access, the residual search-recall gap if accepted (PD-06), the manifest rules (PD-02) including how to re-fetch a deleted file (new output folder; why deleting the manifest is not advised, PD-11), and that downloads and logs hold third-party data and are the user's to protect and delete. | Should | R1 | TR-003, TR-004, RISK-003, RISK-007, RISK-009, Q-10 | GOAL-05 | Sections present; reviewed by reviewer-standards |

Priority totals: **66 FRs = 53 Must, 11 Should, 2 Could** (each FR has exactly one priority).

## 5. Non-Functional Requirements (quantified)

Numbers marked **PA-01** are PM proposals pending sponsor confirmation at G8; the solution-architect may challenge them at G3 with spike data (change via scope-change proposal). The source gave no performance target (Q-11); per D-03 this PRD proposes one rather than recording a Won't.

| ID | Category | Requirement | Target / threshold | Measurement method |
|----|----------|-------------|--------------------|--------------------|
| NFR-001 | Performance (PA-01) | First-run throughput | 1,000 matched messages (one PDF ≤ 1 MB each) complete in ≤ 15 min wall-clock with the mock API at a fixed 300 ms per call (ideal ≈ 10 min) | Benchmark test on the reference machine; one timed sponsor run on the real mailbox is recorded (informational; investigate if > 2 × the mock result) |
| NFR-002 | Performance (PA-01) | Re-run and dry-run scan time (no attachment bytes fetched for already-saved items) | 1,000 messages in ≤ 8 min under the same mock | Benchmark test |
| NFR-003 | Performance (PA-01) | Tool overhead excluding network waits | ≤ 50 ms per message at p95 | Zero-latency mock, 1,000 messages, timing in the benchmark |
| NFR-004 | Performance / UI (PA-01) | GUI responsiveness | Window visible ≤ 3 s after launch (p95 of 10 launches); event-loop stall ≤ 200 ms during a run; Cancel takes effect ≤ 5 s (mock latency ≤ 500 ms) | Instrumented GUI test; stopwatch on 10 launches |
| NFR-005 | Observability | Audit completeness (GOAL-10) | 100 % of eligible runs (the seven outcomes in GOAL-10) produce log + CSV that reconcile; ≤ 1 CSV row lost after a hard kill | Reconciliation test over ≥ 8 scripted runs, CLI and GUI |
| NFR-006 | Reliability | Retry on HTTP 429 and 5xx: exponential backoff with jitter, start 1 s, cap 64 s, 6 attempts, honour `Retry-After` | Attempts ≤ 6; delays within bounds; success after the Nth retry | Mock returns 429 then 200; attempts and delays asserted. Real-run: 429 responses ≤ 2 % of calls (PA-01) |
| NFR-007 | Reliability | Interrupt safety (FR-030, FR-037) | 100 stop/kill points over a fixture: 0 partial files under final names; manifest parses 100/100 after a graceful stop; after a hard kill ≤ 1 leftover temp file, ignored on the next run; re-run gives 0 duplicates and 0 lost | Fault-injection loop of 100 iterations |
| NFR-008 | Reliability | Failure isolation (FR-036) | With ≥ 1 injected fault each at message fetch, attachment fetch, decode and disk write: 100 % of other attachments saved, exit code 1 | Fault-injection test |
| NFR-009 | Scalability (PA-01; PD-17) | Memory | Peak memory ≤ 300 MB while saving a 25 MB attachment (core + CLI). Retained memory grows by ≤ 2 KB per candidate message and per manifest entry between a 500-message and a 10,000-message fixture (≈ 19 MB over 9,500 messages), and no attachment bytes are kept after a message is finished | Memory profile in the test run (`tracemalloc` plus process-memory sampling); growth = (peak at 10,000 − peak at 500) ÷ 9,500 messages; the W1 benchmark confirms the 2 KB figure (RISK-014) |
| NFR-010 | Scalability (PA-01) | Volume | 10,000 matched messages per range complete or resume with 0 duplicates; manifest holds ≥ 50,000 entries; manifest update ≤ 50 ms at p95 with 10,000 entries; single attachment up to 25 MB works | Large-fixture run; microbenchmark |
| NFR-011 | Security | Least privilege | Exactly 1 OAuth scope; 0 mailbox write calls (allowed API methods: message list, message get, attachment get) | Recording mock asserts scope list and every call |
| NFR-012 | Security | Secret hygiene (FR-005) | 0 occurrences of sentinel token/refresh token/client secret in log, CSV, console, GUI text, exception text across all error paths; 0 findings in repo secret scan on every PR | Sentinel test matrix; secret-scanning tool in review |
| NFR-013 | Security | Secret files (FR-004) | POSIX 700 / 600 verified; Windows secrets path under user profile; `.gitignore` covers 100 % of listed patterns | Permission and pattern tests |
| NFR-014 | Security / Privacy | No egress except Google | 0 outbound connections to hosts other than Google API/OAuth endpoints; 0 telemetry (ASSUMPTION-12). Consistent with Google's API user-data rules as understood by the PM (no web research done; sponsor to confirm, Q-04) | Test with network allow-list; dependency review |
| NFR-015 | Security (process) | Developers and agents never read `credentials.json`/`token.json` (SEC-08) | 0 secret contents in repo, tests, Jira, PRs | Review check at G6; secret scan |
| NFR-016 | Privacy | Data minimisation and retention (PA-08) | Logs and CSV hold only LOG-02 fields plus run parameters; the full `--query` text appears only in a `DEBUG` log (it may contain e-mail addresses, PD-19); 0 occurrences of message body text; no automatic deletion — retention is user-managed | Sentinel body-text test; README check |
| NFR-017 | Accessibility | Keyboard operation and focus (FR-060) | 100 % of controls reachable and operable by keyboard; visible focus indicator on 100 %. WCAG 2.2 AA principles 2.1.1, 2.4.7 used as the reference; formal WCAG conformance is a Won't for a desktop app | Manual walkthrough plus framework test where possible |
| NFR-018 | Accessibility | Contrast (FR-057) | Text/background token pairs ≥ 4.5:1; focus indicator and component borders ≥ 3:1 | Script computing ratios from the palette tokens |
| NFR-019 | Accessibility (Should, R3) | Screen reader (FR-063) | 100 % of interactive controls expose an accessible name and role; main flow completes with Windows Narrator | Narrator walkthrough |
| NFR-020 | Compatibility | Platforms and Python | Windows 11 64-bit is primary: full test suite and GUI acceptance. macOS and Linux (current release at G7) best effort: core + CLI tests pass, GUI smoke only. Python 3.10, 3.11 and 3.12 tests all pass | CI matrix; manual GUI run on Windows 11 |
| NFR-021 | Compatibility / UI | Display | 0 clipped or overlapping controls from the 800 × 560 minimum window size to 3840 × 2160 at 100/150/200 % scaling, including 1920 × 1080 at 200 % (work area ≈ 960 × 520 logical px, FR-058) | Screenshot matrix reviewed by ux-expert and qa-engineer |
| NFR-022 | Maintainability | Quality gates, every PR | `pytest` 100 % pass; **line coverage of changed code ≥ 80 %** and **line coverage of the whole `gmail_pdf` package ≥ 80 %** (`coding-standards.md` §6 as amended by the delivery lead, PGD-1 c.10108; the DoD says the same); `ruff` 0 violations; `mypy --strict` 0 errors. Supersedes the v0.2 values 100 % / 85 % (PD-10) | `pytest -q --cov=gmail_pdf` with `--cov-fail-under=80` for the whole package; changed-code coverage by a diff-coverage report against `main` with a threshold of 80 (tooling and treatment of untestable GUI glue: test strategy, solution-architect); `ruff` and `mypy` commands from CLAUDE.md §1 |
| NFR-023 | Maintainability | Dependencies | 0 runtime third-party dependencies beyond the three Google libraries without an accepted ADR (GUI framework and any time-zone data package need one) | Dependency list vs ADR index at G3 and G6 |
| NFR-024 | Localisation | Language and formats | UI text English only; dates `YYYY-MM-DD` input, `YYYYMMDD` in names; 100 % of Unicode letters in test names preserved | Table-driven tests |
| NFR-025 | Availability | Not applicable: local tool; availability depends on Gmail and the user's machine. No SLO (Won't) | — | — |

## 6. Scope

### 6.1 Release structure (PD-05)
MVP = **R1 + R2**. R1 (Core + CLI) is independently shippable and delivers the primary outcome (GOAL-01..07, GOAL-10); R2 adds the desktop GUI (GOAL-08, GOAL-09 and GUI parity). GUI work that is not needed to be usable and compliant with §9.2–9.3 (Advanced area, screen reader) is **not** in the MVP, which keeps RISK-001's trigger ("GUI polish in Must") from firing.

| Release | Must | Should | Could | Won't (this release) |
|---------|------|--------|-------|----------------------|
| **R1 Core + CLI** (v0.9, MVP part 1) | FR-001..006, 008, 009, 011, 012, 014..016, 018..031, 036, 037, 039..045, 065 (37) | FR-010, 013, 017, 032, 033, 046, 066 (7) | — | GUI (R2), FR-007, 034, 035, 038 |
| **R2 Desktop GUI** (v1.0, MVP complete) | FR-047..060, 062, 064 (16) | GUI fields for FR-010 and 013 | — | FR-061, 063 (R3) |
| **R3 Hardening** (v1.1) | — | FR-007, 034, 061, 063 | — | See below |
| **Backlog** (unscheduled) | — | — | FR-035, 038 | — |

### 6.2 Won't have (this release) — and what happens if we don't build it
| Item | Decision | If we don't build it |
|------|----------|----------------------|
| `config.yaml` / `.env` settings file (CFG-11) | Won't (BA proposed Should). Flags and the two environment variables cover the need; a YAML parser is a new dependency (Q-08) | CLI users type flags. No requirement or goal depends on it |
| `--skip-identical` (FR-035) | Could, backlog | Identical PDFs from different emails are both kept, which is the safe default (BR-007) |
| Parallel fetching (FR-038) | Could, with a promotion trigger (NFR-001/002 fail) | Sequential runs may be slower; no correctness loss |
| Standalone installer / packaging (Q-03) | Won't | The sponsor runs from source or `pip install`; revisit after G3 |
| Scheduled / unattended runs, multi-account, service accounts, IMAP | Won't (brief §5 out of scope) | Not needed by the sponsor; RISK-003 makes unattended runs fragile anyway |
| Download of Drive-hosted or linked PDFs; non-PDF types; any mailbox write | Won't (RD §1) | Out of the problem statement |
| Revocation call to Google's endpoint | Won't (FR-007 removes the local token and shows revoke steps) | Sponsor revokes in Google Account; keeps network surface to the minimum |
| Formal WCAG 2.2 AA conformance for the desktop app | Won't; principles in NFR-017..019 | No external accessibility audit obligation known |
| Dark theme (UA-09, UQ-09); sort or filter in the dry-run table (UA-08); remembering the last-used folder and Spam/Trash choice (UQ-05) | Won't in R1/R2 (PD-14) | One light palette; the table is already in the fixed FR-014 order and the CSV can be sorted elsewhere; defaults apply on each launch |
| Availability SLO, telemetry, automatic retention clean-up | Won't | Local tool; user-managed (PA-08) |

### 6.3 Justification of Musts (challenge: "what happens if we don't build it?")
| Epic | Why Must | If missing |
|------|----------|------------|
| EPIC-01 Access (FR-001..006) | Read-only sign-in is the safety premise (GOAL-05); redaction and secret handling answer the highest-impact risk (RISK-005) | Tool cannot run safely, or a credential leaks |
| EPIC-02 Search (FR-008, 009, 011, 012, 014..016) | Defines "every PDF in the range" and fixed order | Wrong or incomplete set; names change between runs |
| EPIC-03 Extract (FR-018..021) | Forwarded and nested PDFs are in the sponsor's acceptance bar | Missed PDFs (GOAL-01 fails) |
| EPIC-04 Naming (FR-022..027) | AC-03/04/06; sponsor's contract | Unusable names, overwrites, path escape |
| EPIC-05 Saving (FR-028..031) | AC-05 and "never overwrite" | Data loss or duplicates on every re-run |
| EPIC-06 Resilience (FR-036, 037) | Large mailboxes and stop/resume (EC-07) | One bad email kills a 10,000-message run |
| EPIC-07 Audit/CLI (FR-039..046) | GOAL-10, scripting, dry run (AC-09) | No proof of what happened; no safe preview |
| EPIC-08 README (FR-065) | The Google setup is a manual prerequisite (TR-001) | Sponsor cannot reach first run |
| EPIC-09/10 GUI (FR-047..060, 062, 064) | D-01 and CLAUDE.md §9 make the GUI part of the product | Product form rejected by sponsor |

## 7. Epics (outline — detailed by product-owner)

Size: S ≤ 8 pts, M 9–15, L 16–20, XL > 20 (relative PM points, MVP scope only; post-MVP points in brackets).

| Epic | Goal / user value | FRs | Release | Size (pts) | Dependencies |
|------|-------------------|-----|---------|-----------|--------------|
| EPIC-01 Secure read-only Gmail access | Sign in once, read-only, secrets never leak | FR-001..006; FR-007 (R3) | R1 (GUI surfaces R2) | L (17) [+2] | TR-006 for live consent; FR-005 before any logging |
| EPIC-02 Find messages in a date range | Exactly the right messages, in a fixed order | FR-008..017 | R1 | L (19) | G3 spike Q-07 for FR-017 |
| EPIC-03 Extract PDF attachments | Every PDF, including nested and forwarded | FR-018..021 | R1 | M (12) | EPIC-02 |
| EPIC-04 Predictable file naming | `YYYYMMDD_` names, safe and collision-free | FR-022..027 | R1 | M (12) | EPIC-03 |
| EPIC-05 Safe saving and re-run safety | Never overwrite; re-runs add nothing | FR-028..033; FR-034 (R3); FR-035 (BL) | R1 | M (14) [+5 +2] | EPIC-04 |
| EPIC-06 Resilient, cancellable runs | One failure or a stop never harms the run | FR-036, 037; FR-038 (BL) | R1 (GUI Cancel R2) | S (5) [+5] | EPIC-05 |
| EPIC-07 Audit trail, dry run and CLI | Prove what happened; preview safely; scriptable | FR-039..046 | R1 | L (16) | EPIC-04, FR-005 |
| EPIC-08 Onboarding documentation | Reach a first successful run unaided | FR-065, 066 | R1 (GUI parts R2) | S (4) | EPIC-01, EPIC-07 |
| EPIC-09 Desktop GUI workflow | Do the whole job in one window | FR-047..053, 064 | R2 | XL (25) | R1 core callable with progress and cancel; G3 UI-framework ADR; ux-expert spec |
| EPIC-10 GUI design system and adaptability | One consistent, resizable, high-DPI, keyboard-operable look | FR-054..060, 062; FR-061, 063 (R3) | R2 | L (17) [+5] | G3 ADR; tokens first (FR-054..057) |

MVP total 141 pts (R1 = 99, R2 = 42).

## 8. Prioritisation Rationale

**Method.** RICE is not informative here: one user, so Reach is constant. Value-versus-effort is used instead. Score = (Value + Risk reduction) × 10 ÷ pts, each rated 1–5 by the PM. The score orders work *within* what dependencies allow; dependency order wins (see release plan waves).

| Epic | Value | Risk reduction (risk) | Pts | Score |
|------|-------|-----------------------|-----|-------|
| EPIC-06 Resilience | 4 | 3 (GOAL-06) | 5 | 14.0 |
| EPIC-08 README | 3 | 2 (RISK-003) | 4 | 12.5 |
| EPIC-05 Saving | 5 | 4 (RISK-008) | 14 | 6.4 |
| EPIC-01 Access | 5 | 5 (RISK-005) | 17 | 5.9 |
| EPIC-03 Extract | 5 | 2 | 12 | 5.8 |
| EPIC-04 Naming | 5 | 2 | 12 | 5.8 |
| EPIC-07 Audit/CLI | 4 | 3 (C2) | 16 | 4.4 |
| EPIC-02 Search | 5 | 3 (RISK-007) | 19 | 4.2 |
| EPIC-10 GUI design | 3 | 3 (RISK-001) | 17 | 3.5 |
| EPIC-09 GUI workflow | 4 | 3 (RISK-001) | 25 | 2.8 |

Reading: the two GUI epics score lowest per point, which supports shipping Core + CLI first (R1) and keeping the GUI thin (RISK-001). They stay Must for the product because D-01 and §9 are the sponsor's decisions.

**Must share of MVP effort: 131 of 141 pts (93 %), against the ≈ 60 % guideline. This is a deliberate, recorded deviation (PD-09).** The sponsor's own specification is a safety and correctness contract: all 37 RD IDs and the nine acceptance criteria are mandatory, and D-01 adds a GUI. Only 10 pts (7 %) are genuinely discretionary. Descoping Musts would break the acceptance criteria, so delivery confidence is protected differently: (1) R1 ships alone and delivers the primary outcome; (2) work is sequenced in waves with the riskiest, dependency-free logic first and live Google access last; (3) items that were Should or Must in the catalogue but are not needed for usability moved out of the MVP (FR-034, 061, 063, CFG-11); (4) the scrum-master plans sprints below measured velocity; (5) FR-038 is a pre-agreed fallback if performance is short. Raised to master as RISK-010.

## 9. Assumptions, Constraints, Dependencies

**Carried constraints:** CONSTRAINT-01..10 (brief §7): `gmail.readonly` only; Python 3.10+ (3.12 target); Google libraries only unless an ADR justifies another; no database; GUI + CLI on one core; CLAUDE.md §9; local processing; 25 MB attachments; pytest/ruff/mypy-strict, package `gmail_pdf`; secrets never read by developers.

**Carried assumptions:** ASSUMPTION-01..16 (catalogue). Updated by this PRD: ASSUMPTION-05 (MoSCoW) confirmed with the deltas in §15.2; ASSUMPTION-06 refined by PD-01; ASSUMPTION-07 confirmed by PD-03; ASSUMPTION-08/09 replaced by PD-02; ASSUMPTION-10 kept (FR-008).

**New PM assumptions** (need sponsor confirmation unless noted; see §14.3):
| ID | Assumption |
|----|------------|
| PA-01 | Numeric targets in NFR-001..004, 006 (real-run part), 009, 010 are PM proposals; no baseline exists. (NFR-022 is no longer one: the delivery lead set it, v0.4) |
| PA-02 | GOAL-09 (≤ 5 min to dry run) is a worthwhile Should metric |
| PA-03 | Use is ad hoc (one run per period), not high frequency (the sponsor answered Q-12 with the effort per PDF, not the frequency) |
| PA-04 | A sponsor acceptance run on the real mailbox (≥ 10 known PDFs, one-week range) is acceptable as GOAL-01 evidence |
| PA-05 | CLI-first order (R1 before R2) is acceptable even though the GUI user is the primary persona |
| PA-06 | Dry run writes nothing into the output folder, including no log or CSV |
| PA-07 | Sign-out only removes the local token and shows revoke steps |
| PA-08 | Retention of downloads, logs and CSVs is user-managed; no auto-delete; no telemetry (Q-10) |
| PA-09 | **Confirmed by the sponsor (PGD-1 c.10108):** Windows 11 is the target platform (Q-02) and there is no fixed deadline, as soon as possible, R1 first (Q-01). No longer awaiting G8 |
| PA-10 | The `filename:pdf` recall gap (RISK-007) is accepted conditionally (PD-06) |
| PA-11 | The 30 s per PDF manual baseline (Q-12) is the sponsor's estimate, not a measurement; the GOAL-11 targets (≤ 3 s per PDF, ≥ 50 % net saving) are PM proposals (PD-20) |
| PA-12 | No mailbox holds mail with a received time before 1970-01-02 or after 9999-12-30, so the FR-015 date bounds exclude no real mail. Gmail began in 2004 (delivery lead's note); imported mail can carry older dates, but none before 1970 is expected. Sponsor confirmation at G8 (owner: Santhosh); if mail older than 1970 turns up, the floor returns to the delivery lead as a scope question |

**Dependencies:**
| Dependency | Needed by | Owner |
|------------|-----------|-------|
| Sponsor completes Google Cloud setup and places `credentials.json` (TR-006) | Live consent, real-mailbox acceptance (R1 wave 3, G7) | Santhosh |
| G3 ADRs: GUI framework (ADR-001, Proposed until spike S-02; no EPIC-09/10 story is Ready before then, C11); recall sweep (ADR-007, residual measured by spike S-01); dependencies (ADR-002); delivery form (ADR-005); memory reading (ADR-006) | ADR-002, 005, 006, 007 are accepted; ADR-001 is needed before R2 | solution-architect |
| ux-expert spec incl. §9 tokens and GUI-10 setup flow | R2 | ux-expert |
| R1 core callable by the GUI with progress events and cancellation | R2 | solution-architect, developer |
| Mock Gmail API / fixtures with synthetic data only (CLAUDE.md §6.7) | All stories | developer, qa-engineer |
| Jira PGD, GitHub repo | Process | Santhosh |

## 10. Risks

IDs RISK-001..009 are in `docs/00-governance/risk-register.md`. New ones are **proposed** for master to register.

| Risk | P | I | Mitigation | Owner |
|------|---|---|------------|-------|
| RISK-001 GUI added to a CLI spec | 3 | 3 | MVP split R1/R2 (§6); polish out of Must; thin GUI; ADR | PM, SA |
| RISK-003 Testing-status tokens expire in ~7 days | 4 | 2 | FR-003, FR-066 | SA, developer |
| RISK-005 Credential leakage | 2 | 5 | FR-005, NFR-012, secret scan | SA, reviewers |
| RISK-007 Search-recall gap | 3 | 4 | FR-017 (Should, spike), PD-06 conditional acceptance, README note, sponsor spot check (PA-04) | SA, PM |
| RISK-008 Manifest loss causes duplicates | 3 | 3 | FR-032, 033 in R1, FR-034 in R3 (PD-02) | PM, SA |
| RISK-009 Unprotected downloads/logs | 2 | 4 | SEC-05, FR-066, NFR-016, G3 default-folder decision | Santhosh, SA |
| **RISK-010 (proposed)** Must is 93 % of MVP effort, so any slip hits acceptance criteria | 3 | 3 | R1 ships alone; waves; sprint plans below velocity; FR-038 fallback (§8) | PM, scrum-master |
| **RISK-011 (proposed)** Performance targets are unvalidated assumptions (PA-01) | 3 | 2 | Benchmark in wave 1; architect challenges at G3; sponsor confirms at G8 | PM, SA |
| **RISK-012 (proposed)** Chosen GUI framework cannot meet §9 (token control, high-DPI, keyboard focus) | 2 | 3 | ADR must show a spike against FR-054..060 before acceptance | SA |

## 11. Traceability Matrix

Goal → BRQ/UR → FR → Epic. Every FR appears in at least one row; every goal has at least one FR (GOAL-11 through the retrieval path listed).

| Goal | BRQ / UR | FR | Epic |
|------|----------|----|------|
| GOAL-01 Complete retrieval | BRQ-001; UR-001, 008, 009 | FR-008..013, 015..021 | EPIC-02, 03 |
| GOAL-02 Predictable naming | BRQ-002; UR-003 | FR-014, 022..026, 038, 044, 049 | EPIC-02, 04, 06, 07, 09 |
| GOAL-03 Safe re-runs | BRQ-004; UR-012 | FR-014, 029, 032..035 | EPIC-02, 05 |
| GOAL-04 No loss, no path escape | BRQ-003 | FR-021, 023, 026, 027, 028, 031 | EPIC-03, 04, 05 |
| GOAL-05 Credential and mailbox safety | BRQ-005, 006; UR-004, 010, 013 | FR-001..007, 066 | EPIC-01, 08 |
| GOAL-06 Resilience and resumability | BRQ-004, 008; UR-006, 012 | FR-030, 036, 037, 051 | EPIC-05, 06, 09 |
| GOAL-07 GUI/CLI parity | BRQ-009; UR-005, 011 | FR-015, 043, 045, 047..053, 061, 064, 065 | EPIC-07, 08, 09 |
| GOAL-08 Design standards | BRQ-010 | FR-054..060, 062, 063 | EPIC-10 |
| GOAL-09 Ease of first use (Should) | BRQ-011; UR-003 | FR-006, 044, 047, 060, 065 (all also trace to another goal) | EPIC-01, 07, 08, 09, 10 |
| GOAL-10 Auditability (new) | BRQ-007; UR-007, 011 | FR-032, 037, 039..043, 046, 052 | EPIC-05, 06, 07, 09 |
| GOAL-11 Time saved (new, v0.4, Should) | Q-12 baseline; BRQ-001; UR-003 | FR-009, 011, 018, 022, 028, 044, 047 and NFR-001..003 (all also trace to another goal; no FR depends on GOAL-11 alone) | EPIC-02, 03, 04, 05, 07, 09 |

FR-by-FR owner epic: FR-001..007 EPIC-01; FR-008..017 EPIC-02; FR-018..021 EPIC-03; FR-022..027 EPIC-04; FR-028..035 EPIC-05; FR-036..038 EPIC-06; FR-039..046 EPIC-07; FR-047..053, 061, 064 EPIC-09; FR-054..060, 062, 063 EPIC-10; FR-065, 066 EPIC-08.

## 12. Open Questions

Owners and needed-by dates; none blocks G2 or G3. Carried BA questions keep their IDs; PM-raised ones use `PQ-`.

| ID | Question | Owner | Needed by | Working assumption |
|----|----------|-------|-----------|--------------------|
| Q-01 | Deadline for MVP/GUI | Santhosh | **Answered (PGD-1 c.10108):** as soon as possible, no fixed date; R1 first | The release plan keeps sequence, not dates |
| Q-02 | Operating systems | Santhosh | **Answered:** Windows 11 | NFR-020; PA-09 confirmed |
| Q-03 | Delivery form (source, pip, executable) | SA | **Resolved by ADR-005:** pip-installable package with entry points | — |
| Q-04 | Personal or Workspace; consent screen status; verification | Santhosh | **G8** (D-28); the sponsor is not sure (c.10108) | Testing status, 7-day token expiry (ASSUMPTION-04); re-check at G8 |
| Q-07 | Finding unnamed PDFs | SA | **Resolved by ADR-007:** recall sweep on by default; residual measured by spike S-01 (GitHub #2) | FR-017, PD-06 |
| Q-08 | YAML and time-zone dependencies | SA | **Resolved by ADR-002:** no YAML; `tzdata` and `tzlocal` | CFG-11 stays a Won't |
| Q-10 | Retention, clean-up, privacy | Santhosh | **G8**; the sponsor is not sure (c.10108) | PA-08 |
| Q-11 (memory part) | Reading of NFR-05 | SA | **Resolved by ADR-006 and architecture §7:** ASSUMPTION-16 confirmed (one message and one attachment at a time); wording in NFR-009 (PD-17) | — |
| Q-12 | Manual effort baseline | Santhosh | **Answered:** about 30 s per PDF | GOAL-11, PA-11 |
| PQ-01 | Does a dry run download attachment bytes? | SA, PM | **Closed (D-22, ADR-006):** no; names are labelled "planned, not verified" and `NOT_A_PDF` cannot appear in a dry run | FR-044 |
| PQ-02 | Numeric exit code for an unreadable manifest, a cancelled run and an unexpected internal failure | SA, qa-engineer | **Closed (D-21, PD-19):** all exit 1; the code set stays 0–3 | FR-043 |
| PQ-03 | Default folders when the GUI is launched by double-click | SA | **Closed (D-23):** GUI secrets in the local app-data folder, output in the Downloads folder; the CLI keeps the RD defaults | FR-002, 004 |
| PQ-04 | Remember the last-used output folder and Spam/Trash choice between launches (UQ-05)? Needs a preferences file | PM, SA | R2 planning | No (PD-14): defaults on each launch |

Resolved by this PRD: Q-05 (PD-01), Q-06 (PD-02), Q-09 (PD-03), Q-13 (PD-04), performance part of Q-11 (PD-07). Closed in v0.4 from the architecture and the sponsor's answers: Q-01, Q-02, Q-03, Q-07, Q-08, Q-11 (remainder), Q-12, PQ-01, PQ-02, PQ-03. Still open: Q-04 and Q-10 (G8, working assumptions) and PQ-04 (R2 planning). AQ-02 (shadcn) was withdrawn by the delivery lead and is not carried.

## 13. Change Log
| Version | Date | Change | Reason | Decision ref |
|---------|------|--------|--------|--------------|
| 0.1 | 2026-10-29 | Initial PRD for G2; GOAL-10 added; PD-01..09 recorded | G1 conditions C2–C4; open questions Q-05, 06, 09, 13 | G1 CONDITIONAL GO, D-01, D-03 |
| 0.2 | 2026-10-29 | (a) NFR-022 now requires 100 % changed-code coverage per PR (coding-standards §6), keeps ≥ 85 % as a whole-package floor, names the measurement method; PD-10 and PA-01 wording updated. (b) "FR-039..044" corrected to "FR-039..043, 046" for C2 / GOAL-10 (§0, §14.2) and to "FR-039..043" for BRQ-007 (§15.1), because FR-044 (dry run) is outside GOAL-10; EPIC-07 range in §6 aligned to FR-039..046. No change to scope, priorities or FR text | G2 condition C6 | G2 CONDITIONAL GO (gate-log, PGD-1 c.10095) |
| 0.3 | 2026-10-29 | Resolves ux-expert issues (ux-spec §11). (a) PD-11: PD-02(d) and FR-029/033 reworded; the README and in-app advice for re-fetching a deleted file is "use a new output folder", not "delete the manifest"; FR-034 stays Should/R3. (b) PD-12: FR-058 minimum window 800 × 560 logical px, clamped where the work area is smaller; NFR-021 extended to 1920 × 1080 at 200 %. (c) PD-13: FR-043 and FR-037 state user-facing outcomes for cancel, unreadable manifest, internal failure (numeric mapping left to the solution-architect). (d) PD-14: UA-07..09 accepted (decimal MB, no table sort/filter, light theme only) and listed as Won't; PQ-04 added (UQ-05). (e) PD-15: FR-060 shortcuts Enter = Dry run, Ctrl+Enter = Run. (f) PD-16: FR-045 allows `--help` / `-h`. §14.3 item 5 amended, item 11 added; PQ-02/03 narrowed. No FR added, removed or re-prioritised (66 FRs = 53 Must, 11 Should, 2 Could); effort and epic sizes unchanged. These are clarifications of v0.2 FR text, raised for master to log, not new scope | ux-spec §11 "Issues for other roles" (product-manager 1–3); PGD-1 c.10100 | Proposed D-14..D-19 (master to number) |
| 0.4 | 2026-10-29 | Closes G3 condition C8 and applies the delivery lead's decisions. (a) PD-17: NFR-009 growth clause becomes ≤ 2 KB per candidate message and per manifest entry (AR-03). (b) PD-18: FR-032 and its acceptance test now say no PDF is written and the manifest is untouched, but a run log and a header-only CSV are written; GOAL-10's outcome list adds unreadable manifest and internal failure; NFR-005 and the reconciliation test grow to ≥ 8 runs; FR-039/040 aligned. (c) PD-19: AQ-04 (cancel exits 1, D-21; FR-043 text), AA-07 (CSV UTF-8 with BOM; FR-040), AA-08 (run's time zone; FR-039), AA-11 (full query at DEBUG only; FR-039, NFR-016) confirmed. (d) NFR-022 and PD-10: coverage ≥ 80 % of changed code per PR and ≥ 80 % of the whole package, superseding 100 % / 85 % (D-24, D-25). (e) PD-20 and GOAL-11: time saved against the sponsor's 30 s per PDF baseline (Q-12); PA-11 added. (f) §12: Q-01, 02, 03, 07, 08, 11, 12 and PQ-01..03 closed; Q-04 and Q-10 stay assumptions to G8 (D-28); PA-09 confirmed; §14.3 updated (answered items removed; Q-04, D-21 mapping and PD-18/19 added). (g) AQ-02 (shadcn) is not added to §14.3, because the delivery lead has decided shadcn is ignored for this project. No FR added, removed or re-prioritised (66 FRs = 53 Must, 11 Should, 2 Could); effort and epic sizes unchanged. The FR-032 and FR-043 changes clarify existing behaviour and are raised for master to log | G3 condition C8; PGD-1 c.10106, c.10108, c.10109 | Proposed D-29..D-32 for PD-17..20 (master to number); PD-10 supersedes D-24 |
| 0.5 | 2026-10-31 | Clarification of FR-015, raised for master to log; PA-12 added. FR-015 now states that a date outside 1970-01-02 to 9999-12-30 is rejected (CLI exit 2, same sentence for `--start` and `--end`, never clamped), and its fit criterion adds the bound cases. FR-008 text is unchanged and reads as "dates that pass FR-015". FR-048 carries the rule to the GUI without edit ("same rules and messages as FR-015"). No FR added, removed or re-prioritised (66 FRs = 53 Must, 11 Should, 2 Could); effort and epic sizes unchanged. **Why it is not a scope change:** FR-015 already covers invalid input; the bounds add no capability and remove none a user can use (PA-12); the requirements document leaves open which dates are valid and rejects only "malformed" ones, so the bounds fill a gap in it. Without them a date at or before 1970-01-01, or 9999-12-31, ends in the unexpected-failure line or a negative `after:` bound (DEF-007, Sev-3, RISK-026). **One behaviour changes:** `--start 1970-01-01` in America/New_York ended in exit 0 and now ends in exit 2; the old result depended on the zone, and 1970-01-02 gives the same range for a real mailbox. A user who wants everything types 1970-01-02 | DEF-007 (PGD-69); GitHub #39; PGD-16 AC-9 (product-owner, PGD-16 c.10296) | D-67, D-70 (delivery lead left the reject-or-clamp choice to the product-owner); master to number this ruling |

## 14. Product Decisions and Sponsor Confirmation

### 14.1 Decisions (made by the PM; proposed for master to log in `decision-log.md`)

| ID | Decision | Alternatives considered | Rationale | Effect |
|----|----------|-------------------------|-----------|--------|
| PD-01 (Q-05) | **GUI exposure and MVP flags.** R2 GUI exposes start, end, time zone, output folder, dry run, Spam/Trash, extra query. Credentials path, token path and log level move to an Advanced area in R3 (until then: CLI options, environment variables, defaults). `--skip-identical` and a config file are not in the MVP in either front end. Every GUI option has an identical CLI equivalent; the reverse need not hold in the MVP. | Expose every flag in the GUI (BA's GUI-03); expose none beyond dates | A single user has no need for path pickers on day one; fewer controls means a smaller §9 surface; parity (FR-064) is about results, not about every option | FR-047, 061; GUI-03 priority lowered for paths |
| PD-02 (Q-06) | **Manifest rules.** (a) Manifest present = authoritative; a deleted file is not re-downloaded (it is flagged by FR-033). (b) Unreadable manifest = stop, never overwrite (FR-032). (c) Missing manifest in a non-empty folder = warn and continue as a first run in the MVP (FR-033); from R3, recognise already-saved PDFs from earlier CSV reports and content hashes, each file matched at most once (FR-034). (d) A new output folder is a new library. ~~Deleting the manifest is the documented way to re-fetch a deleted file.~~ **Amended by PD-11 (v0.3):** to re-fetch a deleted file, use a new output folder; deleting the manifest is not advised. | Dedup by `attachmentId` (rejected: unstable per RD FR-17); write provenance into the PDF or file name (rejected: alters content or breaks AC naming); platform-specific file streams (rejected: not portable); hash-only matching (rejected as sole method: ambiguous for identical PDFs, so claim-once with CSV evidence) | Safe by default (no data loss), cheap in the MVP, reduces RISK-008 further in R3. Replaces ASSUMPTION-08/09 | FR-029, 032..034 |
| PD-03 (Q-09) | **Tie-break accepted.** Order = received time ascending, then messageId ascending (shorter ID first, then lexicographic), then MIME parts in document order. | Gmail list order (newest first, unstable); thread order | Independent of API paging, identical on every run | FR-014 |
| PD-04 (Q-13) | **Sign-out, keyboard, screen reader.** Sign-out = remove local token + show Google revoke steps (Should, R3). Keyboard-only operation and visible focus = Must in R2. Screen-reader support = Should, R3. Formal WCAG conformance = Won't. | Full accessibility in MVP; none | Keyboard is cheap with a native framework and basic to "professional" (§9.1); screen-reader testing is costly and no need is known | FR-007, 060, 063; NFR-017..019 |
| PD-05 | **MVP shape and dry-run behaviour.** MVP = R1 (Core + CLI) + R2 (Desktop GUI); R1 ships alone. Dry run writes nothing into the output folder (resolves RD "writes nothing" versus AC-09 "writes no PDFs"). | GUI and CLI together in one release; dry run writing log/CSV | Satisfies RISK-001; keeps AC-09 and GUI-05 ("folder unchanged") literally true | §6, FR-044 |
| PD-06 (RISK-007) | **Conditional acceptance of the recall gap.** Baseline search is the RD's (FR-009). FR-017 (Should) closes the gap if the G3 spike shows cost within NFR-001/002. If not, the gap is accepted, documented in the README and shown by the "messages scanned" figure. | Require broad search now (Must) | Sponsor's RD chose the filter knowingly; cost unknown until the spike | FR-017, 066 |
| PD-07 (C3, D-03) | **Performance targets.** Numeric targets proposed in NFR-001..004; FR-038 pre-agreed fallback. Not recorded as a Won't. | Won't | A target keeps the spike honest; sponsor can relax it | NFR-001..004 |
| PD-08 (C4) | **GOAL-09 adopted as a Should metric**, measured at G7, not a release gate. | Drop; Could | The sponsor's wish for a user-friendly tool (§9.1) is best expressed by a measurable time-to-first-result; no FR depends on GOAL-09 alone | §3 |
| PD-09 | **Must share exception.** Must is 93 % of MVP effort; accepted with mitigations (§8). | Descope acceptance criteria | See §8 | RISK-010 |
| PD-10 (C6; updated v0.4) | **Coverage rule.** Per-PR gate = line coverage of changed code ≥ 80 %, and of the whole `gmail_pdf` package ≥ 80 % (`coding-standards.md` §6, amended by the delivery lead in commits e71302b, 834f7d2 and 481a46f; PGD-1 c.10108). This **supersedes** the v0.2 rule (100 % changed code, 85 % package floor) and D-24; D-25 (pragma exceptions) is no longer needed. The DoD's 80 % / 80 % line is the same rule. | Keep 100 % / 85 % (rejected: the owner of the standard changed it); 90 % (the old DoD figure, no longer in force) | The delivery lead owns the standard and the PRD follows it; one pair of numbers across PRD, standards and DoD removes the C6 ambiguity for good | NFR-022 |
| PD-11 (ux-spec §11 PM issue 2; amends PD-02(d); RISK-008) | **Re-fetching a deleted file: reword the advice, do not promote FR-034.** README, in-app notices (MW-2) and FR-033's missing-manifest warning say: to get a deleted file again, choose a **new output folder** (the old folder is left untouched; PD-02(d) "a new folder is a new library"). Deleting `.manifest.json` is **not** advised: in the MVP it makes every PDF already in the folder download again with `_1`, `_2` endings (nothing is overwritten) until FR-034 (R3). A narrower date range is useful only together with a new folder (it limits what the new folder receives); on its own it does not help, because the manifest still lists the deleted file. FR-034 stays Should / R3. **Promotion trigger:** the sponsor says at G8 that re-fetching deleted files or manifest loss is a regular need, or a manifest-loss incident occurs in use; then FR-034 moves to R2 (+5 pts, MVP 146, Must share unchanged because FR-034 is a Should). | (1) Promote FR-034 to R2: removes the duplicate-suffix trap but adds 5 pts of hash/CSV matching to an MVP that is already 93 % Must (PD-09, RISK-010) for a rare, ad hoc event (PA-03); and FR-034 is a recovery for *accidental* manifest loss, not a good way to re-fetch one file. (2) Keep the old wording (rejected: it tells users to do the one thing that creates duplicates). (3) Add a "re-fetch this file" command (rejected: new scope, new FR, not requested) | Costs nothing in effort; removes the only place where the documented advice itself caused the RISK-008 failure; the new-folder route is already in PD-02(d), is safe under FR-028 and needs no new code. Trade-off: the file lands in a different folder, which is acceptable for a rare action | FR-029, 033, 066; PD-02(d); README; MW-1/MW-2 text |
| PD-12 (PQ-03; UA-01) | **Minimum window size 800 × 560 logical px** (not 800 × 600). Rationale: at 1920 × 1080 with 200 % scaling the desktop is 960 × 540 logical px, so 600 px of height can never fit and the minimum would break NFR-021 on a common laptop. The window is clamped to the available work area where that is smaller than the minimum, and content scrolls instead of clipping. **Note for master/SA/UX:** 560 is still above the 540 px desktop, and the work area after the taskbar is ≈ 520, so at 1080p/200 % the clamp rule (not the number) is what protects users; UA-01 should confirm the framework can clamp or scroll below its own minimum. | 800 × 600 (rejected: does not fit); 800 × 540 (not chosen: UX layout is designed for 560 with column scrolling below 640 px) | Matches the UX layout; makes the requirement testable on the hardest realistic display | FR-058, NFR-021 |
| PD-13 (UA-04; PQ-02 product part) | **What cancel, unreadable manifest and internal failure mean to the user.** (a) *Cancelled*: not an error and not a success. Saved files, manifest, log and CSV are intact; the summary says "Run cancelled", that the range was not completed and that running it again continues (FR-037). A script must see non-zero, because an incomplete range must not look like success. (b) *Unreadable manifest*: the run stops before writing anything; the message names the file and gives restore or move-aside steps (FR-032); non-zero. (c) *Internal failure*: a one-line redacted message pointing to the run log, no stack trace, no secret (FR-005); non-zero. In all three the first line differs from "Run complete" and from the exit-2/3 messages, and the GUI shows the same wording. The **numeric mapping is the solution-architect's**; PM position is exit 1 for all three, keeping the sponsor's 0–3 contract (RD LOG-05). **Closed in v0.4:** D-21 fixes exit 1 for all three and PD-19 confirms it. Adding a code is a scope-change proposal. | Exit 0 for cancel (rejected: hides an incomplete range from scripts); new codes 4/5/130 (not now: changes the sponsor's contract for no stated need) | Matches UX assumption UA-04 and PQ-02; gives the architect a testable requirement without fixing the numbers | FR-032, 036, 037, 043 |
| PD-14 (UA-07, 08, 09, UQ-09, UQ-05) | **Display and scope choices accepted.** (a) Sizes shown as decimal MB (1 MB = 1,000,000 bytes); the CSV `size_bytes` is exact, so nothing is lost if Explorer shows a slightly different figure. (b) No sort or filter in the dry-run table in R2 (rows follow the fixed FR-014 order; users can sort the CSV elsewhere). (c) One light theme in R2; no dark theme (halves the NFR-018/021 test matrix; nothing in the brief or §9 asks for it). (d) Last-used folder and Spam/Trash choice are not remembered (PQ-04). All four are Won't for R1/R2 (§6.2). | Binary MB (matches Explorer, but "MB" ambiguity either way); sorting and dark theme in R2 | Low value for one ad hoc user; protects the Must-heavy MVP (RISK-010) | NFR-018, 021, 024; ux-spec |
| PD-15 (UA-10) | **Keyboard shortcuts.** Enter in a field = Dry run (writes nothing); Ctrl+Enter = Run. Run needs a deliberate chord so a stray Enter cannot start writing files. Shortcuts are shown on screen and are never the only route (FR-060, PD-04). | Enter = Run (rejected: the writing action should not be the accidental one); no shortcuts | Safe default matches the "preview first" journey and GOAL-09 | FR-060 |
| PD-16 (UQ-10) | **`--help` is allowed** although FR-045 says "nothing else": the standard `--help` / `-h` prints the flag table and defaults and exits 0, with no network call and no credential access. No other extra flag (for example `--version`) is added. | Forbid (rejected: an unusable CLI with no discoverable flags; the spirit of FR-045 is "no extra functionality") | Costs nothing; supports P-02 and FR-065 | FR-045 |
| PD-17 (C8(i); AR-03; RISK-014) | **NFR-009 growth clause reworded.** "Growth ≤ 10 % between 500 and 10,000 messages" becomes "retained memory grows by ≤ 2 KB per candidate message and per manifest entry, and no attachment bytes are kept across messages". The ≤ 300 MB peak for a 25 MB attachment is unchanged. FR-014 forces the tool to hold and sort every candidate before naming, so memory must grow with the number of messages; a percentage of a small baseline cannot be met, a per-item figure can, and it still catches a leak. The W1 benchmark confirms the figure; if it measures higher, the architect raises a scope-change proposal. | Keep ≤ 10 % and state why (rejected: the architect shows it is unattainable by design, so it would fail falsely); drop the growth clause (rejected: unbounded growth at 10,000 messages would go unnoticed) | A testable number that follows from the requirement instead of fighting it; reduces RISK-014 | NFR-009, §5 |
| PD-18 (C8(ii); AQ-03; GOAL-10) | **Unreadable manifest: what "nothing is written" means.** The run saves no PDF and leaves the manifest and its backup untouched, but it does write its run log and a header-only CSV. Those two files are the record of why nothing happened; GOAL-10's reconciliation holds with 0 rows and 0 counts. GOAL-10's outcome list now names this case and the internal failure. A **dry run** on an unreadable manifest writes nothing (PD-05) and only shows the message. FR-032's acceptance test is changed to match. | FR-032 read literally, no file at all (rejected: the user would have only a console message and GOAL-10 would have a hole); exclude this outcome from GOAL-10 (rejected: it is exactly the case where an audit record matters) | Master recommended this reading (gate record G3, C8); it is the architect's design (architecture §6.5); costs nothing | FR-032, 039, 040; §3 GOAL-10; NFR-005 |
| PD-19 (C8(iii); AQ-04, AA-07, AA-08, AA-11) | **Four architecture assumptions confirmed.** (a) AQ-04: a cancelled run exits 1 (D-21; PD-13). (b) AA-07: the CSV is UTF-8 with a byte-order mark; columns and order stay as LOG-02, so a script must read it as `utf-8-sig`. (c) AA-08: the timestamps in the run log, the CSV and the two file names use the run's chosen time zone (default: system zone). (d) AA-11: the full `--query` text is logged only at `DEBUG`; at `INFO` the log records its length, because it may contain e-mail addresses. | (b) plain UTF-8 (rejected: Excel garbles non-ASCII subjects and names, and the sponsor opens the CSV in Excel); (c) UTC (rejected: file names would not match the dates in the PDF names); (d) always log the query (rejected: personal data in a file the user may share) | Each is the more useful default for one user on Windows and Excel; none changes a requirement ID or the sponsor's column contract | FR-039, 040, 043; NFR-016 |
| PD-20 (Q-12; GOAL-11) | **Time-saved goal.** Q-12 is answered: about 30 s per PDF by hand. GOAL-11 measures the saving as (a) tool time per PDF ≤ 3 s, that is ≤ 10 % of the baseline (the NFR-001 target is ≈ 0.9 s), and (b) a net saving of ≥ 50 % on a real range of at least 50 PDFs once the user's own hands-on time is counted. It is a Should metric like GOAL-09, not a release gate; no FR depends on it alone and none is added. | Must release gate (rejected: the baseline is an estimate); a single "≥ 90 % saved" target (rejected: hands-on time, up to the 5 min of GOAL-09, makes it unreachable for small ranges); no goal (rejected: it is the business case for the tool) | Gives the sponsor a number he can check against his own estimate; reuses NFR-001 and GOAL-09 evidence | §3 GOAL-11; PA-11 |

Also proposed for master: **GOAL-10 (Auditability)** as a PRD-level goal closing C2, and MoSCoW deltas against the catalogue (§15.2). Suggested decision-log IDs are left to master.

### 14.2 G1 condition status
C2 closed (GOAL-10, FR-039..043 and 046, NFR-005; FR-044 dry run is not a GOAL-10 requirement). C3 closed (NFR-001..004 as PA-01 proposals). C4 closed (PD-08, Should, confirmation at G8). C1 belongs to the business-analyst. **G3 C8 closed in v0.4** (PD-17..19; §12).

### 14.3 Decisions needing sponsor confirmation (at G8, the only human approval point)
Work proceeds on the labelled assumption; if the sponsor changes one, it follows the scope-change route (appended to §13, summarised to master).

1. **PA-01** Performance and capacity numbers (NFR-001..004, 009, 010), including 15 min per 1,000 messages and the per-item memory growth of PD-17. (Coverage, NFR-022, is no longer here: the delivery lead set 80 % / 80 %.)
2. **PA-02 / PD-08** GOAL-09 kept as a Should metric (≤ 5 min to a GUI dry run); **PA-11 / PD-20** GOAL-11 time saved against the 30 s per PDF baseline (≤ 3 s per PDF, ≥ 50 % net saving).
3. **PA-05 / PD-05** Core + CLI released first (R1, v0.9), GUI second (R2, v1.0).
4. **PD-01** GUI MVP shows seven fields; Advanced area (paths, log level) in R3; no skip-identical and no config file.
5. **PD-02 / PD-11 / PA-07** Manifest rules, including "deleted file not re-downloaded", re-fetching a deleted file by using a new output folder (deleting the manifest is not advised), recovery in R3; sign-out removes the local token only.
6. **PA-06** Dry run writes nothing in the output folder (no log or CSV).
7. **PD-04** Keyboard operation is Must; screen reader Should in R3; no formal WCAG conformance.
8. **PD-06 / PA-04** Conditional acceptance of the recall gap; acceptance by a sponsor-supplied real-mailbox sample.
9. **PA-08 / Q-10** Retention is user-managed; no telemetry (the sponsor was not sure, so this is re-checked at G8). PA-09 is no longer listed: Windows 11 and "no deadline" were confirmed (Q-01, Q-02).
10. **PD-09** Must is 93 % of MVP effort (informational).
11. **PD-13** A cancelled run, an unreadable manifest and an unexpected failure all end with a non-zero CLI exit code (PM position: 1), so scripts never mistake an incomplete range for success. This reads the RD's exit-code list (0/1/2/3) for cases it does not name. **Mapping decided (D-21, PD-19): all three exit 1; the code set stays closed at 0–3.**
12. **Q-04** Consent-screen status (Testing or In production; personal Gmail or Workspace): the sponsor is not sure, so ASSUMPTION-04 (Testing, 7-day token expiry) stays and is re-checked at G8 (D-28).
13. **PD-18 / PD-19** An unreadable manifest still writes a run log and a header-only CSV; the CSV is UTF-8 with a byte-order mark (for Excel); timestamps use the run's time zone; the full search text is logged only at `DEBUG`.

## 15. Source-ID Mapping (no orphans)

### 15.1 Catalogue → PRD
| Source IDs | PRD |
|------------|-----|
| BRQ-001 | FR-008..013, 015..021 |
| BRQ-002 / 003 / 004 | FR-022..026 / 023, 027, 028, 031 / 029, 030, 037 |
| BRQ-005 / 006 | FR-001, NFR-011 / FR-002..006, NFR-012..016 |
| BRQ-007 | FR-039..043, GOAL-10 |
| BRQ-008 / 009 / 010 / 011 | FR-036, 037 / FR-045, 047, 064 / FR-054..060, 062 / FR-006, 047, 065 |
| UR-001..013 | UR-001 FR-008, 045, 047 · UR-002 FR-045, 047 · UR-003 FR-044, 049 · UR-004 FR-001 · UR-005 FR-050 · UR-006 FR-037, 051 · UR-007 FR-042, 052 · UR-008 FR-010 · UR-009 FR-013 · UR-010 FR-003, 006, 015 · UR-011 FR-043 · UR-012 FR-030 · UR-013 FR-007 |
| SEC-01..09 | FR-001 (01, 02) · FR-002 (03) · FR-004 (04, 05) · FR-005 (06) · FR-003 (07) · NFR-015 (08) · FR-023, 027 (09) |
| FR-01..18 (RD) | 01 FR-008 · 02 FR-009, 010 · 03 FR-011 · 04 FR-012 · 05 FR-014 · 06 FR-018 · 07 FR-019 · 08 FR-020 · 09 FR-021 · 10 FR-025 · 11 FR-022 · 12 FR-023 · 13 FR-024 · 14, 15 FR-026 · 16 FR-028 · 17 FR-029 · 18 FR-031, 035 |
| NFR-01..05 (RD) | NFR-006 · FR-036, NFR-008 · FR-037, NFR-007 · FR-038 · NFR-009 |
| LOG-01..05 | FR-039, 040 · FR-040 · FR-041 · FR-042 · FR-043 |
| CFG-01..11 | CFG-01, 02, 04 FR-008, 045 · CFG-03 FR-045 · CFG-05 FR-010 · CFG-06 FR-013 · CFG-07 FR-044 · CFG-08, 09 FR-002 · CFG-10 FR-046 · CFG-11 Won't (§6.2) |
| VAL-01..03 | FR-015 · FR-015 · FR-006 |
| EC-01..07 | FR-018 · FR-031 · FR-021 · FR-019 · FR-013 · FR-016 · FR-011, 030, NFR-010 |
| AC-01..09 | FR-001 · FR-008, 012 · FR-022 · FR-026 · FR-029 · FR-027 · FR-005, NFR-012 · NFR-022 · FR-044 (each holds for CLI and GUI, FR-064) |
| GUI-01..19 | 01 FR-047 · 02 FR-064 · 03 FR-047, 061 · 04 FR-048 · 05 FR-049 · 06 FR-050 · 07 FR-051 · 08 FR-052 · 09 FR-053 · 10 FR-006 · 11 FR-005 · 12 FR-054 · 13 FR-055 · 14 FR-056 · 15 FR-057 · 16 FR-058 · 17 FR-059 · 18 FR-062 · 19 FR-060 |
| BR-001..014 | 001 FR-022 · 002 FR-008 · 003 FR-026 · 004 FR-014 · 005 FR-028 · 006 FR-029 · 007 FR-031, 035 · 008 FR-019, 021 · 009 FR-025 · 010 FR-024 · 011 FR-023, 027 · 012 FR-013 · 013 FR-001 · 014 FR-012 |
| DR-001..008 | NFR-016, FR-029, 039, 040; DR-003/004 NFR-012, 013 |
| TR-001..006 | FR-065 (001, 002) · FR-066 (003, 004) · TR-005 and TR-006 are user actions (dependencies, §9) |

### 15.2 MoSCoW deltas against the catalogue (ASSUMPTION-05 confirmed with these changes)
| Item | Catalogue | PRD | Reason |
|------|-----------|-----|--------|
| CFG-11 settings file | Should | Won't | Extra dependency, no goal (§6.2) |
| GUI-03 paths and log level in GUI | Must | Should (R3) | PD-01 |
| GUI-19 keyboard operation | Should | Must | PD-04 |
| UR-013 sign-out | Could | Should (R3) | PD-04 |
| GUI-18 consistency | Must | Must, as a checklist (FR-062) | Subjective part bounded; avoids "GUI polish in Must" |
| FR-17 manifest loss handling | (open) | Must for authoritative manifest; Should for FR-032..034 | PD-02 |
| Unnamed PDF discovery | (open) | Should (FR-017) | PD-06 |
| FR-18 optional skip, NFR-04 workers | Could | Could (BL) | Unchanged |

## 16. Issues for Other Roles
- **business-analyst:** mirror GOAL-10 in the brief and map BRQ-007 to GOAL-02 and GOAL-10; update catalogue Q-05, Q-06, Q-09, Q-13 and Q-11 (performance part now PD-07) as resolved; keep brief §10 aligned with RISK-007..009 (C1, your lane). **(v0.4)** Add GOAL-11 (time saved, 30 s per PDF baseline, Q-12) to the brief's goals; record the Q-01, Q-02 and Q-12 answers (PGD-1 c.10108); the brief's NFR-09 memory wording follows PRD NFR-009 (PD-17).
- **master:** (v0.4) log PD-17..20 (suggested D-29..D-32); note that PD-10 is updated to 80 % / 80 % (D-24 and D-25 are superseded); add GOAL-11 to the goal list; RISK-014 can close when the W1 benchmark confirms the 2 KB figure. Earlier: log PD-01..09 and GOAL-10 as decisions; register RISK-010..012; record that RISK-001's trigger was avoided by the R1/R2 split. **v0.3:** log PD-11..16 (suggested D-14..D-19). RISK-008: score stays 3 x 3 (likelihood is unchanged: manifest loss still creates duplicates until FR-034); add that the documented advice no longer causes the failure (PD-11) and that FR-033's warning now states the consequence; add the FR-034 promotion trigger from PD-11. Add PD-13 as sponsor-confirmation item 11.
- **solution-architect:** (v0.4) architecture §7 NFR-009 row and AR-03 take the PD-17 wording (the W1 benchmark confirms 2 KB); §6.5 already matches PD-18; test-strategy gates follow NFR-022 (80 % / 80 %). (v0.3) UA-04 numeric exit-code mapping within PD-13 (non-zero, not 2/3, distinct first line); UA-01 confirm the clamp-and-scroll rule of FR-058 (1080p at 200 % has a ≈ 520 px work area, below the 560 minimum); `--help` per PD-16; PQ-01..03; spike on Q-07 against NFR-001/002; ADR for the GUI framework must show it can meet FR-054..060 (RISK-012); decide manifest integrity (atomic write, last-good backup) and how FR-034 matches files; core API needs progress events and cancellation for R2.
- **ux-expert:** (v0.3) FR-058 is 800 × 560; update MW-2 and MW-1 wording and the README pointer to the PD-11 advice (new output folder, not manifest deletion); FR-033 missing-manifest text states the `_1` consequence; add the screenshot at 1920 × 1080 / 200 %; FR-058 minimum size; GUI-10 setup flow (FR-006); ux checklist for FR-062; tab order (FR-060); show manifest-warning states (FR-033).
- **qa-engineer:** AC-01..09 for both front ends; GOAL-10 reconciliation test over ≥ 8 runs including the unreadable-manifest and internal-failure outcomes (header-only CSV); BOM check on the CSV (PD-19); real-mailbox acceptance depends on TR-006.
- **product-owner:** create EPIC-01..10 from §7; story-slice by vertical increments; carry FR fit criteria into ACs.
