# Sprint 01 Plan

| Field | Value |
|-------|-------|
| Dates | Proposed 2026-10-30 to 2026-11-12 (assumed 2-week timebox; no fixed date exists, D-33 "as soon as possible"). The start is the day the developer begins STORY-02.01 |
| Sprint goal | By the end of the sprint the project has a secure, CI-gated walking skeleton in which a Windows 11 command-line run against a fake Gmail mailbox selects exactly the messages inside an inclusive, time-zone-aware date range, rejects bad input before any call to Google, ends an empty range cleanly, and can never print a secret or commit a secret file |
| Capacity assumption | **30 story points (assumption, not measured).** There is no velocity (D-33; consistency report section 5). Basis: the work is split into 6 committed stories (29 points) of which two are 8-point enablers/first slices on a serial critical path, so the plan commits below a full-wave scope on purpose. The sprint-1 recommendation in the backlog (section 3) says the full W1 set is more than one sprint. After this sprint, replace the assumption with the measured velocity |
| Facilitator | scrum-master |
| Jira | Intake [PGD-1](https://sankumar76.atlassian.net/browse/PGD-1); stories PGD-12..PGD-18 (below); sub-tasks PGD-19..PGD-62 |
| Release / wave | R1 Core + CLI (v0.9.0), wave W1, first cut |
| Status model | Stories were created as Draft (Jira "To Do"). The product-owner validated the Definition of Ready on 2026-10-29 (READY on all seven, PGD-1 comments 10124-10131, 8d4d01e). The scrum-master then moved all seven to **Ready** (Jira "Ready for Dev", verified by JQL on 2026-10-29) |

## Estimation notes
- Jira story-points field is **not configured** (CLAUDE.md section 1a). Each estimate is in the story description (Estimate line) and mirrored by a `points-N` label. Fibonacci scale.
- **Enabler sizing (consistency report CC-01):**
  - STORY-02.01 (walking skeleton, CI, fake mailbox) = **8 points**: package/pins/entry points 2, CI workflow with matrix, coverage combine, security and package stages 3, FakeGmail and fixture builders 3. It is not part of the PRD's 19 points for EPIC-02.
  - STORY-02.08 (benchmark and memory harness) = **8 points**, **not in sprint 01** (it depends on STORY-02.04 paging and carries the corrected 0.6 sweep bound as an AC, CC-02). Planned for sprint 02. Latency-mock runner for NFR-001..003 at sweep ratios 0/0.5/1.0 (3), memory and growth profile for NFR-009/010 (3), result recording and S-01 write-up (2).
  - The two enablers together add 16 points to the R1 total (99 PRD points to about 115). Product-owner informed through this plan. EPIC-02 does still fit R1; it no longer fits one sprint, which is expected.
- Sprint 01 stories were sized by this agent; developer may challenge at refinement. Re-estimate rule: if STORY-02.01 or STORY-02.02 overruns, split along the seams named in their Risks sections and tell the product-owner.

## Committed Stories (in execution order)
| # | Story | Jira | Points | Depends on | Critical path | Tier | Status |
|---|-------|------|--------|-----------|---------------|------|--------|
| 1 | STORY-02.01 Enabler E-1: walking skeleton, CI and fake mailbox (EPIC-02) | [PGD-12](https://sankumar76.atlassian.net/browse/PGD-12) | 8 | none | Yes | Goal-critical | **Ready** (DoR: READY, no changes; 9 ACs) |
| 2 | STORY-01.01 One redaction path for every text surface (EPIC-01) | [PGD-13](https://sankumar76.atlassian.net/browse/PGD-13) | 5 | PGD-12 | Yes | Goal-critical | **Ready** (DoR: READY after PO amendments; now 8 ACs: AC-8 Ctrl+C, AC-7 import wording) |
| 3 | STORY-01.02 Keep secret files out of git and protected on disk (EPIC-01) | [PGD-14](https://sankumar76.atlassian.net/browse/PGD-14) | 3 | PGD-12 | No (parallel with 2) | Droppable | **Ready** (DoR: READY, no AC changes; 5 ACs) |
| 4 | STORY-02.02 Select the messages for an inclusive date range (EPIC-02) | [PGD-15](https://sankumar76.atlassian.net/browse/PGD-15) | 8 | PGD-12, PGD-13 | Yes | Goal-critical | **Ready** (DoR: READY after PO amendments; now 10 ACs: AC-10 default zone, AC-4 precision, `cli/console.py`) |
| 5 | STORY-02.03 Reject bad input before contacting Google (EPIC-02) | [PGD-16](https://sankumar76.atlassian.net/browse/PGD-16) | 3 | PGD-15, PGD-13 | Yes | Goal-critical | **Ready** (DoR: READY after PO amendments; AC-3 skip rule, AC-4 exact wording and unresolvable system zone) |
| 6 | STORY-02.06 End an empty range normally (EPIC-02) | [PGD-17](https://sankumar76.atlassian.net/browse/PGD-17) | 2 | PGD-15 | No (parallel with 5) | Droppable | **Ready** (DoR: READY, no AC changes; 5 ACs) |

**Total committed:** 29 points / capacity 30 points (assumed).
**Critical path:** STORY-02.01 (8) then STORY-01.01 (5) then STORY-02.02 (8) then STORY-02.03 (3) = 24 points, serial. STORY-01.02 and STORY-02.06 run beside the path. Redaction (01.01) precedes anything that logs or prints, so no later line can bypass it (RISK-005, release plan W1 note).
**Goal-critical set:** 02.01, 01.01, 02.02, 02.03 (24 points). If time runs short, 01.02 and 02.06 move to sprint 02; the goal wording above still holds except "ends an empty range cleanly" and "can never commit a secret file". Say so at the review.

## Stretch Stories
| Story | Jira | Points | Depends on | Start only if |
|-------|------|--------|-----------|---------------|
| STORY-03.01 Recognise a PDF part (EPIC-03) | [PGD-18](https://sankumar76.atlassian.net/browse/PGD-18) | 3 | PGD-15 (epic order; the fixture builders come from PGD-12) | STORY-02.02 has passed G5 and the developer has idle capacity. Pure logic, no CLI work. **Ready (stretch)**: DoR READY after PO amendment (now 8 ACs: AC-8 whitespace and trailing-dot rule) |

## Held or deferred (explicitly NOT in sprint 01)
| Item | Reason | Condition to release |
|------|--------|----------------------|
| **STORY-02.09 Find PDFs that Gmail's filename search misses (recall sweep)** | **HELD, CC-02 open** (ADR-007 gate 0.8 against the NFR-002 bound 0.6). Not created in Jira, not a Ready candidate | solution-architect restates the ADR-007 cost gate against NFR-002 (or the story carries the 0.6 bound as an AC), and STORY-02.08 numbers exist. Also depends on EPIC-03 extraction. Earliest sprint 03 |
| STORY-02.08 benchmark and memory harness | Sized (8) but depends on 02.04; belongs with the W1 exit check | Sprint 02 |
| EPIC-09 (PGD-10), EPIC-10 (PGD-11) stories and STORY-08.03 | **Held by C11** (S-02 spike and ADR-001 Accepted). No story created, none Ready, none in a sprint | solution-architect clears C11; applied again at every G4, no later than W4 |
| STORY-01.07 live sign-in, W3 items | Needs TR-006 (sponsor's credentials) | Santhosh |
| Remaining W1 stories: 02.04, 02.05, 02.07, 03.02-03.04, 04.01-04.05, 07.01 | Beyond a conservative first cut; written in sprint-02 refinement from the epic files | Sprint 02 planning. The W1 exit check (dry run prints the RD section 4.4 names exactly) is therefore a sprint 02 outcome, not sprint 01 |

## Requirement coverage of sprint 01
| Requirement | Story |
|-------------|-------|
| FR-004, NFR-013 | STORY-01.02 |
| FR-005, NFR-012, NFR-015 | STORY-01.01 |
| FR-008, FR-009, FR-012, NFR-006, NFR-024 | STORY-02.02 |
| FR-015 | STORY-02.03 |
| FR-016 | STORY-02.06 |
| FR-019 (stretch) | STORY-03.01 |
| NFR-020, NFR-022, NFR-023, NFR-014, G3 pip-audit follow-up | STORY-02.01 |
| Not yet started: FR-010, FR-011, FR-013, FR-014 (02.04, 02.05, 02.07), FR-045, FR-044 (07.01) | Sprint 02 |

## Assumption verification map (G3 follow-up)
| Item | Where verified | Note |
|------|----------------|------|
| `pip-audit` on the first pinned `requirements.txt` | STORY-02.01 AC-4 | Result recorded in the PR |
| AA-01 (Gmail epoch boundary semantics) | STORY-02.02 AC-2, AC-4 | +/-1 s widening plus local re-check, tested for both inclusive and exclusive fakes; the real behaviour is confirmed in W3 on the sponsor's mailbox (cannot be proved on a fake) |
| AA-03 (static discovery, no discovery fetch) | STORY-02.02 AC-8 | Under the socket guard |
| AA-04 (Gmail quota well above about 200 calls/min) | STORY-02.02 AC-9 | Documentation check recorded in the PR |
| AA-06 (`\\?\` long paths on Windows 11) | **Not in sprint 01.** STORY-04.05 (W1, sprint 02) | Needs `file_store`; flagged so it is not forgotten |
| AA-09 (`run_local_server` timeout parameter) | **Not in sprint 01.** STORY-01.04 (W2) | |

## Windows 11 notes (target OS, D-33)
CI runs `windows-latest` on Python 3.10, 3.11 and 3.12 plus Ubuntu and macOS legs (test-strategy section 9). Stories carry path-length, line-ending, `shell: bash` and mode-bit notes where relevant (STORY-02.01, 01.02). POSIX permission tests run on the Ubuntu and macOS legs only.

## Risks to the Sprint Goal
| Risk | Mitigation | Owner |
|------|------------|-------|
| STORY-02.01 is 8 points and every other story waits for it (RISK-010) | Start it first and alone; keep CI and fake-mailbox work in separate sub-tasks so the skeleton can merge as soon as T1-T4 and T8 are green; split at the review loop if needed | developer, scrum-master |
| STORY-02.02 is 8 points (range, query, gateway, retry, planner, CLI) | Seams are named (retry helper T3/T4 can move to its own story); the goal-critical set stays at 24 points | developer, scrum-master |
| First `pip-audit` finds a vulnerability without a fix | Raise a `tech-debt` issue; master decides (ADR-002 rule 4) | developer, master |
| Hash-pinned requirements differ per OS (platform-specific wheels) | Generate on Windows 11 and verify installs on Ubuntu and macOS legs; decision recorded in the PR | developer |
| AA-01 cannot be settled on a fake | Documented double-interpretation tests now; real check in W3 (needs TR-006) | qa-engineer, Santhosh |
| Interim CLI output (`Messages in range: N`, interim exit 3 message) is replaced later | Wording kept in `domain/messages.py`; product-owner accepts the interim wording at DoR (A-1) | product-owner |
| Solo developer agent capacity unknown (no velocity) | 30-point assumption is deliberately conservative; droppable tier defined above | scrum-master |
| RISK-005 credential leakage | 01.01 precedes every logging or printing story; sentinel matrix harness extended by each later story | developer, reviewer-standards |

## Product-owner decisions on the open items (DoR validation, 2026-10-29)
All six accepted; none remains open. A-3 is an Assumption owned by ux-expert (non-blocking).
| ID | Story | Decision |
|----|-------|----------|
| A-1 | STORY-01.01, 02.06 | **Accepted.** `error: unexpected failure, see the run log` is used in the interim build before a run log exists; the same wording is reused for a failed list call (02.06 AC-4). UX gives no path suffix, architecture 6.5 appends `: <path>`: alignment logged as CC-10 (ux-expert, solution-architect) |
| A-2 | STORY-02.03 | **Decided.** Several input errors are printed one per line, each error being one line (UX "one line each") |
| A-3 | STORY-02.03 | **Decided (Assumption).** `error: --tz: Unknown time zone. Use an IANA name such as Asia/Kolkata.` (no echo of input). ux-expert to add the line to UX section 12 (CC-11) |
| A-4 | STORY-01.02 | **Accepted.** `client_secret*.json` is ignored in `.gitignore` in addition to the architecture list |
| A-5 | STORY-02.02 | **Accepted with a removal rule.** The interim stdout line `Messages in range: N` and the interim real-mode `error: Gmail sign-in is not available in this build yet.` (exit 3) must be removed or replaced by STORY-07.04 and STORY-01.04/01.06; those stories carry an AC to that effect (see "Follow-ups for later stories") |
| A-6 | STORY-02.02 | **Accepted.** The retry helper (NFR-006) is built in STORY-02.02 as the consistency report allocates it; paging (`nextPageToken`) stays in STORY-02.04 |

Other PO findings (Minor, none blocking sprint 01): CC-10 unexpected-failure wording differs between UX and architecture (ux-expert, solution-architect); CC-11 add the A-3 line to UX section 12 (ux-expert); CC-12 token write helper location and the `redaction.py` to `domain.messages` import, now named in PGD-13 AC-7 (solution-architect, non-blocking); CC-13 sub-task summaries cite the amended ACs (scrum-master, done: PGD-32 and PGD-33 gain PGD-13 AC-8, PGD-41 gains PGD-15 AC-10, PGD-60 gains PGD-18 AC-8).

## Follow-ups for later stories (include when drafting them)
| Story | Add this to the story |
|-------|-----------------------|
| STORY-01.04 (sign-in, mock-tested), STORY-01.06 (missing or wrong credentials) | AC: the interim real-mode line `error: Gmail sign-in is not available in this build yet.` (STORY-02.02 AC-6) and its `messages.py` constant are removed and replaced by the real sign-in behaviour and exit 3 mapping; a test proves the string no longer exists (A-5) |
| STORY-07.04 (final summary) | AC: the interim stdout line `Messages in range: N` (STORY-02.02 AC-5) is replaced by the seven-field FR-042 summary; a test proves the interim line is gone (A-5). Also keep the "No PDFs found / 0 PDFs found." first lines for candidate-level emptiness (STORY-02.06 Dev Context note) |
| STORY-07.02 (run log), STORY-07.03 (CSV report) | Extend PGD-17 (STORY-02.06) AC-3: an empty range now creates the run log and a header-only CSV (it creates no file in sprint 01); add a zero-match case to the NFR-005 reconciliation test |
| STORY-06.02 (Ctrl+C) | Replace the interim `Run cancelled` behaviour of PGD-13 AC-8 with the safe stop and cancelled summary |
| STORY-03.02, 07.04 | "Messages found but 0 PDF candidates" must print the same empty-range wording (STORY-02.06) |
| STORY-04.05 (sprint 02) | Verify AA-06 (`\\?\` long paths on Windows 11) |
| STORY-02.08 (sprint 02, benchmark and memory harness) | **ACs from deferred PGD-12 review findings, to be closed before STORY-02.08 reaches G5; master checks them at that sprint's G4** (decision-log D-41, RISK-014). From GitHub [#9](https://github.com/sankumar76/pdf-download-gmail/issues/9) (PERF-01, PERF-05): (a) a lazy factory seam in `FakeGmail` (for example `message_factory=Callable[[int], FakeMessage]` with `count=N`, or attachments as `Callable[[], bytes]`) so fake-owned state is about the id list (~100 B per message); (b) `test_memory_bounds` measures product allocations only (`tracemalloc` filtered to `gmail_pdf/` frames, or the fixture built before the baseline); (c) the 25 MB attachment case runs through the real gateway over `HttpMockSequence`, because `FakeGmail.get_attachment` has no base64 transient and under-states the NFR-009 peak; (d) state whether the NFR-001 fixture shares one PDF `bytes` object or uses distinct ones. From [#10](https://github.com/sankumar76/pdf-download-gmail/issues/10) (PERF-02, PERF-03; PERF-06 conditional): (e) the `GMAIL_PDF_TEST_FAKE_MAILBOX` JSON can describe a generated mailbox (for example `{"generate": {"count": 10000, "seed": 7, "pdf_bytes": 1048576}}`) expanded lazily through the seam, no `indent=2` for large dumps; (f) `record_calls: bool = True` or a bounded `deque` for `calls`, and `_cursors[cursor]` freed when the last page is returned; (g) only if FR-038 is promoted: guard `_take_fault` and the recorder append with a `threading.Lock` |
| STORY-03.03 (get the bytes of a PDF) | **AC or sub-task from GitHub [#12](https://github.com/sankumar76/pdf-download-gmail/issues/12)** (QUA-05, AA-02, AR-05, RISK-016), closed before its G5: opt-in `FakeGmail(..., rotate_attachment_ids=True)` gives every attachment part a fresh id on each `get_message` (for example `f"{base}~{generation}"`) and `get_attachment` answers 404 for ids from older generations; a test proves the re-fetch finds the part again by `partId` (a retry of the old id must fail) |
| **STORY-02.04 (paging; no Jira key yet)** | **Pacer AC (G6 condition C33, 2026-10-31; decision-log D-59; GitHub [#35](https://github.com/sankumar76/pdf-download-gmail/issues/35), design on [#34](https://github.com/sankumar76/pdf-download-gmail/issues/34) SA ruling 6537220451). It must merge before STORY-01.04 wires the real gateway.** AC: a client-side pacer in `infra/`, called inside the gateway's per-attempt function so retries are charged; list 5, `get(full)` 60, `attachments.get` 20 units; each call waits until `next_allowed`, then sets `next_allowed = max(now, next_allowed) + units * 60 / rate`; rate is a constant of 5,400 units/min (90 % of the 6,000 cap, reviewed after STORY-01.07); no new flag (FR-045), no new dependency; waits go through `cancel.wait` so Cancel ends them (NFR-004); fake-clock tests for spacing per method, retries charged, and cancel during a wait. Also from #35: QUA-45 (add network-unreachable `OSError` and `http.client.HTTPException` to architecture 6.4, then one literal test per class; the SA ruling comes before the story is Ready, C37c) and PERF-15 (counters for calls, retries and backoff seconds, in place before STORY-01.07). **Gate for the plan: STORY-01.04 may not be Ready until STORY-02.04 exists in Jira with this pacer AC.** Create it after the `aiid-STORY-02.04` search, with a Blocks link to STORY-01.04 once that exists (C33, due by the sprint-02 G4) |
| STORY-01.04 (sign-in, mock-tested; no Jira key yet) | **GitHub [#36](https://github.com/sankumar76/pdf-download-gmail/issues/36) (C33).** (1) QUA-48: `GmailGateway.__init__` needs the `CancelToken` at construction but `_execute` creates it after `build_deps`; AC: a test proves the planner and the gateway hold the same token (the SA chooses `build_deps(cancel=...)` or a per-call token if the port shape changes, C37d, before this story is Ready). (2) PERF-16: import the gateway inside the real-mode branch of `build_deps`; a test proves `googleapiclient` is absent from `sys.modules` after `--help` and after a bad-input exit. Keep the SA's conditions from PR #33 comment 6537214922: `build_deps` stays free of credential reads, and the AC-6 no-fall-through test stays green. **Not Ready until STORY-02.04 exists with the pacer AC (#35).** This row is in addition to the A-5 row above |
| STORY-01.07 (live sign-in; no Jira key yet) | **GitHub [#34](https://github.com/sankumar76/pdf-download-gmail/issues/34) (C33).** AC: record `get(full)` latency, 403/429 counts, whether `Retry-After` appears, and the project's quota as shown in the Cloud console. Counts only, no mail content. This is the first real-service measurement; every quota figure so far is arithmetic (D-63). The pacer rate constant is reviewed here. Needs the PERF-15 counters from #35 and the answer to Q-14 (project history, November 2025 to April 2026; needed by the sprint-02 G4) |
| STORY-02.08 (benchmark and memory harness) | **Added by C33.** Report each benchmark with the pacer off and on (SA ruling on #34). Per C36, a pacer-on miss must not promote FR-038, and the delivery lead's decision on Q-15 (keep the mock targets and state the real-service figures beside them, or restate them) comes before this story is Ready. This row is in addition to the #9 and #10 ACs above |
| STORY-03.02 | **Added by C33.** One `messages.get(format=full)` per message, extending the existing planner loop. The only second fetch is the AA-02 stale-id case (SA ruling on #34). Keep the "Messages found but 0 PDF candidates" row above |
| STORY-06.01 (per-message failure isolation; no Jira key yet) | **GitHub [#37](https://github.com/sankumar76/pdf-download-gmail/issues/37) (C33; D-59 point 5).** ACs: a failed `get_message` becomes an `ERROR` row and the rest continues (FR-036, NFR-008), handled in the application-layer per-message loop (phase 2 in `app/planner.py`, phase 3 in the downloader), not in `infra/retry.py`, the gateway or the CLI; a failed phase 1 listing stays a run-level failure; the handler lets `RunCancelledError` through, so Cancel stays a stop; the SA states in architecture 6.4 and 6.5 how an exhausted call maps and whether a run of exhausted calls stops early (C37b). Also: STD-53 (the gateway validates what it returns, and a missing or non-numeric `internalDate` or a missing `id` raises a `GmailApiError`-family error with a fixed sentence and no payload text) and QUA-51 (same type for a 2xx body that is not a JSON object) |
| STORY-06.02 (Ctrl+C) | **Added by C33.** PERF-14 (Minor, GitHub [#29](https://github.com/sankumar76/pdf-download-gmail/issues/29)): `CancelToken.wait` must end promptly on Ctrl+C on Windows; the review measured `KeyboardInterrupt` 2.71 s after the signal on `wait(3.0)`. This is SA item 4 on #29. It adds to the row above and to the C29 items for this story (TD-A, the SA's six items); creating the story in Jira is C29 |
| STORY-07.01 (console module) | **Added by C33.** QUA-46 (Minor, GitHub [#32](https://github.com/sankumar76/pdf-download-gmail/issues/32) = DEF-006, Jira Bug [PGD-68](https://sankumar76.atlassian.net/browse/PGD-68)): a closed stdout or stderr pipe makes the process exit 120. AC: `--help` with stdout on a closed pipe exits 0, and an unexpected failure with stderr closed exits 1 (D-21; 120 is outside the set 0 to 3), by redirecting the closed stream to the null device and mapping the outcome to the D-21 code. Treat it together with OQ-5 and QUA-37 |

## Linked tech-debt for sprint 01 stories (G6 condition C17, 2026-10-29)
Deferred findings from the PGD-12 review (PR #6), linked in Jira as remote links with a comment on the story.
| Story | Jira | GitHub issue | Must be done |
|-------|------|--------------|--------------|
| STORY-02.02 | [PGD-15](https://sankumar76.atlassian.net/browse/PGD-15) | [#11](https://github.com/sankumar76/pdf-download-gmail/issues/11) QUA-03 | In the PGD-15 PR, before its G5: `FakeGmail` ties each page token to `(query, include_spam_trash)`, raises `FakeGmailHttpError(400, "invalidPageToken")` on a mismatch, with a test that sends a baseline token with the sweep query and expects 400. No AC of PGD-15 changes |
| STORY-03.01 (stretch) | [PGD-18](https://sankumar76.atlassian.net/browse/PGD-18) | [#13](https://github.com/sankumar76/pdf-download-gmail/issues/13) QUA-06 (RISK-021) | In the PGD-18 PR, before its G5: `MessageBuilder` emits default per-part headers (`Content-Type` with `name=`, `Content-Disposition` with `filename=`, `Content-Transfer-Encoding: base64`) and accepts `headers=` overrides, one test per default header. No AC of PGD-18 changes |
| STORY-02.02 | [PGD-15](https://sankumar76.atlassian.net/browse/PGD-15) | [#15](https://github.com/sankumar76/pdf-download-gmail/issues/15) = Jira Bug [PGD-63](https://sankumar76.atlassian.net/browse/PGD-63) DEF-001 (Sev-4, G7 finding on PGD-12; label `sprint-01`; "PGD-63 blocks PGD-15") | In the PGD-15 PR, before its G5, together with #11: (a) `bootstrap._load_fake_mailbox` also catches `RecursionError` and reports `AdapterUnavailableError`; (b) `_parse_token` and `_term` use `isascii()` plus `isdecimal()` so a superscript digit gives `FakeGmailHttpError(400, "invalidPageToken")` or `UnsupportedQueryError`; (c) `from_json_dict` validates `payload` and `internalDate` at load time; a regression test for each. No AC of PGD-15 changes |
| STORY-02.02 | [PGD-15](https://sankumar76.atlassian.net/browse/PGD-15) | [#31](https://github.com/sankumar76/pdf-download-gmail/issues/31) = Jira Bug [PGD-67](https://sankumar76.atlassian.net/browse/PGD-67) DEF-005 (Sev-3, G7 finding on PGD-13, build a135b4c; "PGD-67 blocks PGD-15"; condition C30, decision-log D-54) | In the PGD-15 PR, before its G5: pin the literals the PGD-13 ACs state, so tests no longer follow the production constants: one test with `assert redaction.MIN_SECRET_LENGTH == 8` and boundary strings of literal length 7 and 8 (AC-1), and one with `assert set(redaction.THIRD_PARTY_LOGGERS) == {"googleapiclient", "google_auth_oauthlib", "urllib3", "oauthlib"}` (AC-3). No AC of PGD-15 or PGD-13 changes. QA re-runs mutants M13, M20, M22 and M23 at PGD-15's G7 and each must fail (turn a test red). Fallback if PGD-15 cannot carry it: STORY-01.04's G5. "Fix before G8" stands (D-54) |
| (next story that touches `tests/support/`) | [PGD-64](https://sankumar76.atlassian.net/browse/PGD-64) (label `sprint-02`) | [#16](https://github.com/sankumar76/pdf-download-gmail/issues/16) DEF-002 (Sev-4, G7 finding on PGD-12) | Scheduled for sprint 02, to be fixed by the sprint-02 G4 at the latest. Fold into the next story that touches `tests/support/`; if none does by sprint-02 planning, the scrum-master creates a 1-point chore. Fix: guard `socket.socket.sendmsg(address)` via `_check_address` with a Unix-only test, or list it under "Not covered, by design" in the guard's docstring |
| (solution-architect) | n/a | [#14](https://github.com/sankumar76/pdf-download-gmail/issues/14) | ADR-002 tomli update; owner is the solution-architect, no story |

## Impediments
| ID | Description | Impact | Owner | Action | Target date | Status |
|----|-------------|--------|-------|--------|-------------|--------|
| IMP-01 | CC-02 open: ADR-007 cost gate 0.8 versus NFR-002 bound 0.6 | Blocks STORY-02.09 only (held); no sprint 01 effect | solution-architect | Restate the gate as the stricter of NFR-001 and NFR-002 (or exempt dry runs with a reason) | Before STORY-02.09 is Ready (W2) | Open |
| IMP-02 | C11: S-02 spike not run, ADR-001 Proposed | Blocks EPIC-09/10 and STORY-08.03 (held); no sprint 01 effect | solution-architect | Run S-02 (GitHub #3), accept ADR-001 | No later than W4 | Open |
| IMP-03 | TR-006 (sponsor `credentials.json`, 10+ named PDFs) | Blocks W3 only | Santhosh | Prepare Google Cloud setup and samples | Before W3 | Open |

---
# Sprint 01 Review & Retrospective  _(completed at sprint close)_
## Outcome
Planned vs completed, sprint goal met? (Y/N + why): _to be completed_
## Metrics
| Metric | Value |
|--------|-------|
| Velocity | |
| Avg cycle time per story | |
| Avg review loops per story | |
| Findings by severity (review) | |
| Defects found in QA (by severity) | |
| Escaped defects | |
## Demo Notes
_to be completed_
## Retrospective
| Went well | To improve | Action (owner, due) |
|-----------|-----------|---------------------|
| | | |

**Improvements to agents / templates / standards:** _to be completed_
