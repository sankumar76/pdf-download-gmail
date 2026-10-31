# Test Plan — Gmail PDF Attachment Downloader (R1 Core + CLI first, R2 GUI later)

| Field | Value |
|-------|-------|
| Owner | qa-engineer (co-owners for two items: solution-architect for the C12 benchmark case, product-owner for the open questions in section 17) |
| Version | 0.3 (0.1 closed master's condition C19 / tracked item T-03 from the G7 decision of PGD-12; 0.2 closed C35; 0.3 closes C41 (c) and C42; see Annex B) |
| Date | 2026-10-31 (first version 2026-10-30) |
| Based on | PRD v0.4 (commit 5dc3289, NFR-001..025, FR-001..066), architecture v0.2 (sections 4, 6.5, 7), test-strategy v0.2, ADR-001..007, UX spec v0.3, coding-standards section 6 and 10 as amended, definition-of-done, decisions D-21, D-22, D-30, D-31, D-32, D-36, D-37, D-43, and the PGD-12 test report ([PGD-12-test-report.md](PGD-12-test-report.md)); for 0.3 also PRD v0.5 (commit 52fecb7: FR-015 date bounds, PA-12) and decisions D-61, D-79, D-80, D-81, D-85 |
| Status | Draft for master's check as G7 check 0 of the next story (PGD-13, or whichever reaches G7 first) |

How to read this plan: sections 1 to 8 follow the template and say how QA works on every story. Sections 9 to 17 are the project-specific commitments (exit codes, the C12 benchmark case, the no-traceback check, G8 checks, residual risks, defect mapping, per-story focus, charters, open questions). It restates the test strategy only where QA adds a decision; the strategy remains the technical source (solution-architect).

---

## 1. Objectives & Scope

**Objective.** Give master and the delivery lead independent, evidence-based confidence at G7 (per story) and G8 (per release) that the tool does what the acceptance criteria say and nothing harmful that they do not: it finds exactly the PDFs in an inclusive date range, names them predictably, never overwrites, never leaks a credential, and only reads the mailbox (`gmail.readonly`).

**In scope**
| Area | Items | When |
|------|-------|------|
| R1 core + CLI (v0.9.0) | FR-001..006, 008..033, 036, 037, 039..046, 065, 066 (FR-017 conditional on the recall sweep); sponsor acceptance criteria AC-01..09 on the CLI; GOAL-01..07 and GOAL-10 on fixtures | Sprint 01 onward, per story at G7; R1 at G8 |
| Non-functional | NFR-001..004 (performance), 005 (audit), 006..010 (reliability, scale), 011..016 (security, privacy), 020 (platforms), 022 (quality gates), 023 (dependencies), 024 (formats) | Mapped in section 3 and annex A |
| Release gates | G7 per story, G8 release readiness with the sponsor (real mailbox, GOAL-09 and GOAL-11 trials) | Section 12 |
| R2 desktop GUI (v1.0.0) | FR-047..060, 062, 064; NFR-004, 017, 018, 021; GUI parity (GOAL-07), design system (GOAL-08), screenshot matrix | **Held by C11** (spike S-02 and ADR-001 Accepted). Strategy section 4 stands; this plan gets a GUI annex when the first GUI story is Ready |

**Out of scope**: NFR-025 (availability, no SLO); formal WCAG conformance (a Won't, NFR-017); NFR-019 screen reader (R3); live Gmail in any automated test (coding-standards section 10); load tests beyond the NFR-001..003, 009, 010 benchmarks; penetration testing of Google's services.

**Assumptions** (flagged, not facts): (A1) Windows 11 64-bit is the target and primary test OS (Q-02, D-33); macOS and Linux are best effort, core + CLI only (NFR-020). (A2) The performance targets are PM proposals under PA-01 until the sponsor confirms them at G8. (A3) Real Gmail boundary behaviour (AA-01), long paths on Windows (AA-06) and quota (AA-04) cannot be proved on a fake and are confirmed in W3 on the sponsor's machine. (A4) Q-04 (consent screen in Testing, 7-day refresh token) and Q-10 (retention) stay assumptions until the G8 re-check (D-34).

---

## 2. Test Approach

The levels, tools and locations are those of test-strategy section 2. QA's role at each level is stated below. Traceability uses the registered `req` marker, so the AC matrix at G7 is built from `pytest --collect-only` plus the test report.

| Level | Purpose | Owner | Tooling | Location (today) | Entry / exit criteria |
|-------|---------|-------|---------|------------------|-----------------------|
| Unit | Logic of `domain/*`, `app/*` with fakes, `redaction` | developer; QA reviews depth on security-relevant code | pytest, parametrised tables; no hypothesis | `tests/unit/` | Entry: story Ready. Exit: every AC has a marker-linked test; every branch of security-relevant modules (`redaction.py`, `infra/file_store.py`, `infra/manifest.py`, `domain/naming.py`, `domain/name_allocator.py`) is tested (strategy section 5) |
| Integration / contract | `infra/*` against real `tmp_path`; gateway and retry against `HttpMockSequence` (real request building, no network) | developer + QA | pytest, `googleapiclient.http.HttpMockSequence`, stub auth flow | `tests/integration/` (created by PGD-14 and PGD-15; does not exist yet) | Exit: only the three allowed Gmail methods appear in the recorder; exact `q` and `fields` parameters asserted |
| Acceptance | Each AC verified end to end by QA at G7 | qa-engineer | The developer's marker-linked tests run fresh, plus QA mutation and probe scripts; QA adds a test only where an AC has a gap (marker `req`, placed beside the level it belongs to, never in a separate `tests/acceptance/`) | `tests/unit`, `tests/integration`, `tests/e2e` | Exit: AC matrix, all Pass |
| E2E (CLI) | `python -m gmail_pdf`, the shim and `gmail-pdf` as child processes, fake mailbox via the env hook, socket guard active in the child | developer (per story), QA reviews and extends | pytest + `subprocess` helper `tests/support/subprocess_env.py` (`run_guarded`) | `tests/e2e/` today; architecture 10.1 names `tests/e2e/cli/` (move when the first multi-file CLI e2e story lands) | Exit: exit codes, stdout and stderr streams, files and folder diffs asserted |
| E2E (GUI) | Presenter and widget flows, offscreen | developer + QA | pytest-qt, `QT_QPA_PLATFORM=offscreen` | `tests/e2e/gui/` (R2) | Held by C11 |
| Non-functional | Performance benchmarks, security smoke, reliability fault injection, accessibility (R2) | qa-engineer with developer | `perf` marker suite, sentinel matrix, fault-injection loops, scripts | `tests/perf/` (STORY-02.08), `tests/unit/test_sentinel_matrix.py` (PGD-13) | Section 3 and annex A |
| Exploratory | Risk discovery by charter, time-boxed | qa-engineer | Charters in section 16 | Test report, "Exploratory" section | At least one session per story; charters rotate by risk |
| Static / supply chain | ruff (S rules), mypy strict, bandit, pip-audit, gitleaks, allow-list test | developer runs, CI enforces, QA re-checks at G7 and G8 | See the CI stages in section 4 | CI | Green on the final head |

**Coverage gates (D-30; supersede D-24).** At least 80 % of changed lines in `gmail_pdf/**` (`diff-cover coverage.xml --compare-branch=origin/main --fail-under=80`, on coverage combined from the Windows and Ubuntu legs) **and** at least 80 % of the whole package with branch coverage (`pytest -q --cov=gmail_pdf --cov-branch --cov-fail-under=80`; `fail_under = 80` also lives in `pyproject.toml`, so the CLAUDE.md command `pytest -q --cov=gmail_pdf` enforces it). GUI code is not exempt. There are no coverage pragmas (D-31). The gates are floors: QA still checks branch-level depth on the security-relevant modules named above.

**Gmail test doubles** (strategy section 3): `FakeGmail` (in memory; paging, shuffle, nested MIME, scripted faults, latency through an injectable sleeper, call recorder) for unit and e2e; `HttpMockSequence` scripts for gateway and retry; `FakeTokenProvider`, a stub installed-app flow, `FakeClock`, `FakeSleeper`. The fake is test code in `tests/fakes/`; its known fidelity gaps are tracked in #11, #12, #13 and DEF-001 (section 14).

---

## 3. Risk-Based Prioritisation

Impact and likelihood are 1 to 5 (5 is worst); risk is the product. Test depth sets how hard QA looks at G7. Risks reference the register where they exist.

| Area / feature | Impact | Likelihood | Risk | Test depth |
|----------------|:-----:|:----------:|:----:|-----------|
| Secret leak on any text surface: stdout, stderr, log, CSV, excepthook, thread hook, exception chains (RISK-005, FR-005, NFR-012) | 5 | 3 | 15 | Deep: sentinel matrix extended by every story that adds a surface; mutation (remove a redaction call, matrix must go red); over-redaction negatives; QA reads the diff for `print`, `logging` and `str(exc)` |
| Missed or wrongly included messages at range edges: zone, DST, epoch semantics (AA-01, FR-008, FR-012, BR-002) | 5 | 3 | 15 | Deep: literal expected epochs, inclusive and exclusive fakes, Kiritimati and Pago Pago, DST days, leap day; real-boundary check in W3 |
| Overwrite or loss of user files, partial files, path traversal (FR-023, FR-027, FR-028, coding-standards section 10) | 5 | 2 | 10 | Deep from EPIC-04 and EPIC-05: before/after folder hashes, malicious-name table, race at the final name |
| Performance gates failing late: NFR-001/002 and the recall sweep (CC-02, RISK-007, RISK-010) | 4 | 3 | 12 | Benchmark case BM-02 (section 10) before STORY-02.09 is Ready; STORY-02.08 harness |
| Interrupt, cancel and exit-code correctness: Ctrl+C on Windows, exit 1 sub-cases (D-21, FR-037, NFR-007) | 4 | 3 | 12 | Section 9 matrix; 100-iteration kill loop in EPIC-05/06 |
| Test infrastructure trust: socket guard, fake mailbox, env hook (NFR-014 evidence, every later story depends on it) | 4 | 2 | 8 | Done for PGD-12; re-probe on any change to `tests/support/` or `tests/fakes/` |
| Supply chain: dependency allow-list, hashes, advisories (NFR-023, ADR-002) | 4 | 2 | 8 | Allow-list mutation each time `pyproject.toml` changes; pip-audit at G8 (section 12) |
| Console encoding on Windows when output carries non-ASCII file names (section 13, R-05) | 3 | 3 | 9 | Charter EC-9; run with `PYTHONUTF8` unset |
| CI not required on `main` (#7, RISK-022) | 4 | 2 | 8 | Merge precondition check by QA at G7; admin action by the delivery lead |
| GUI items (R2: responsiveness, R-COUNT, design tokens, contrast) | 3 | 3 | 9 | Planned, not started (C11) |
| Documentation checks (README, `--help` content) | 2 | 2 | 4 | Light; EPIC-08 |

---

## 4. Environments & Test Data

| Environment | Purpose | Data | Notes |
|-------------|---------|------|-------|
| Developer machine | TDD and the fast suite `pytest -q -m "not perf"` | Synthetic only | Windows 11, Python 3.12 from a hash-pinned install (`pip install --require-hashes -r requirements-dev.txt`, `pip install --no-deps -e .`) |
| QA local | G7 verification on the PR head, mutation and probe scripts in a scratch copy of the repository (never in the working tree under test) | Synthetic only | Windows 11, Python 3.12 (3.10 only through the CI leg unless a full install is available); **no network calls** from probes: remote targets in guard probes use RFC 5737 addresses or example domains and are refused before sending |
| GitHub Actions | PR gates and nightly `perf` | Synthetic only; **no secrets configured** (only the automatic read-only `GITHUB_TOKEN` for gitleaks) | Stages and matrix below |
| Sponsor machine | W3 real-mailbox acceptance, GOAL-09 and GOAL-11 trials, NFR-001 real timing, AA-01, AA-04, AA-06 | Real mailbox, owner-run; agents and QA never see contents or credentials (SEC-08, NFR-015) | Scheduled with TR-006 |

**CI stages (test-strategy section 9, implemented in `.github/workflows/ci.yml`)**: `lint` (ruff check and format) · `types` (`mypy gmail_pdf --strict`) · `test` (Windows × 3.10, 3.11, 3.12; Ubuntu × 3.12; macOS × 3.12, core + CLI) · `coverage` (combine Windows and Ubuntu data, `coverage report --fail-under=80`, `diff-cover --fail-under=80`, `fetch-depth: 0`) · `security` (pip-audit on `requirements.txt`, bandit, allow-list test, gitleaks) · `package` (wheel, clean venv on Windows, `gmail-pdf --help`) · nightly `perf` on Windows. QA relies on the CI result for the legs it cannot run locally (3.10, 3.11, Ubuntu, macOS) and says so in each report.

**Test data.** Synthetic only (`example.com`, `example.org`); builders in `tests/fixtures/` (`MessageBuilder`); canonical sets: RD section 4.4 table, boundary messages, `America/New_York` DST days; large binaries and perf mailboxes are generated at run time, never committed. Fake credentials and tokens are generated in `tmp_path` with sentinel values (`SENTINEL-CLIENT-SECRET-…`, `SENTINEL-REFRESH-…`, `ya29.SENTINEL…`). **Reset/seed:** every test builds its own mailbox and temp folder; seeds are fixed (shuffle seed, jitter seed); no test depends on the machine's zone, clock or working directory. **Third-party stubs:** none call out; `HttpMockSequence` replaces HTTP, a stub flow replaces consent.

---

## 5. Entry & Exit Criteria

**Entry to QA (per story, G7)**: G6 passed (master GO, label `gate:g6-pass`); the PR head is green on all CI jobs; the Dev Record is in the PR; the orchestrator moved the story to In QA.

**Exit from QA (per story)**: every AC has a verdict with fresh evidence from QA's own run; no open Sev-1 or Sev-2; Sev-3 either fixed or accepted by master with a logged reason; regression green (full suite on the final head, repeated and per-file isolation); exploratory session recorded; the report `docs/07-qa/<KEY>-test-report.md` is committed to the story branch; Jira and PR comments posted. QA recommends ACCEPT or REJECT; master decides at G7; **qa-engineer then sets Done or Rejected** (CLAUDE.md section 4). QA never merges (`MERGE_POLICY = docs-auto, code-human`).

**Release (G8)**: section 12.

**Re-test rule.** A fix to a Sev-1 to Sev-3 defect is verified by QA by the original reproduction plus the developer's regression test; the defect is then Verified. A change that touches `tests/support/`, `tests/fakes/` or `bootstrap.py` triggers the guard and hook probes again (they are cheap).

---

## 6. Defect Management

| Severity | Meaning | Jira priority | Fix expectation |
|----------|---------|---------------|-----------------|
| Sev-1 Critical | Data loss or overwrite, secret exposure, write access to the mailbox, AC outcome not delivered, no workaround | Highest | Blocks G7 and any merge; fix and re-test before the next story starts |
| Sev-2 Major | An AC fails or a core flow is badly wrong with a workaround, an NFR gate fails | High | Blocks G7 (DoD: no open Sev-1 or Sev-2) |
| Sev-3 Moderate | Wrong behaviour in a secondary path, misleading message, test-quality hole that could hide a defect | Medium | Fix before G8; master may accept with a logged reason |
| Sev-4 Minor | Cosmetic, robustness of test-support code, documentation | Low | Backlog, scheduled with the next story that touches the area |

Type is always stated: Product, Test (test code or infrastructure), Environment, Requirement. **Lifecycle:** New → Open → Fixed → Verified → Closed, or Reopened. **Where the record lives** (CLAUDE.md section 7.1): a Jira Bug linked to the story (label `aiid-DEF-NNN`, priority from the table) mirrored as a GitHub issue (`bug`, `sev-N`, `ai-delivery`) and cross-linked; no `defects/DEF-*.md` files in this mode. IDs are `DEF-NNN`; DEF-001 and DEF-002 exist. Search before create. Flaky tests are Test defects (section 7).

---

## 7. Regression Strategy

| Item | Policy |
|------|--------|
| Composition | The whole `tests/` tree on every PR in CI (all legs). Nothing is excluded except the `perf` marker (nightly). Baseline at the end of PGD-12: 271 tests, 98.90 % coverage |
| Per story at G7 | QA runs the full suite on the final head locally (Windows, 3.12) **four times**, **each test file alone** (independence), plus ruff, mypy, bandit and diff-cover; reads the CI check runs for the final head and checks the 3.10, 3.11, Ubuntu and macOS legs |
| Release (G8) | Complete regression across all sprint stories on Windows 3.10, 3.11 and 3.12, the `perf` suite, the sentinel matrix across every surface, the fault-injection loops, a clean-venv wheel install, and the real-mailbox run (section 12) |
| Mutation spot checks | For every enforcement-style test (allow-list, import boundaries, redaction matrix, no-overwrite, read-only scope) QA breaks the rule in a scratch copy and confirms the shipped test goes red (done for AC-5 and AC-6 in PGD-12) |
| Flaky-test policy | A test that fails once and passes on rerun is a Test defect, Sev-3, reported with the failing output. It is never skipped, marked xfail, retried by the runner or deleted to get green; the developer fixes the cause in the same story or the next. Skips are allowed only for platform reasons with an explicit reason string (for example POSIX mode tests on Windows) and QA checks the matching leg actually ran them |
| Determinism | Fixed seeds, fake clock and sleeper, fixed zones; no real sleeping outside the `perf` suite |

---

## 8. Reporting & Metrics

Each story gets `docs/07-qa/<KEY>-test-report.md` from the template (AC → test IDs → technique → result → evidence; automated results; non-functional checks; exploratory notes; defects; residual risks) and a summary comment on the PR and on the Jira story. Each release gets `docs/07-qa/release-<version>-qa-summary.md`.

| Metric | Definition | Baseline (PGD-12) |
|--------|------------|-------------------|
| Pass rate | Passed ÷ total tests on the final head | 271 of 271 |
| AC coverage | ACs with at least one marker-linked, passing test ÷ all ACs of the story | 9 of 9 |
| Coverage | Changed code and whole package against the 80 % gates | 100 % and 98.90 % |
| Defects by severity and status | Open and closed per story and per release | Sev-4: 2 open |
| Defect removal efficiency | Defects found before QA (G5, G6) ÷ all defects found before release | G6 raised 2 Major findings and about 30 Minor items across 38 review threads; QA found 0 AC failures and 2 Sev-4; 0 escaped so far |
| Defect density | Open defects per story point | Tracked from sprint 02 |
| Flakiness | Tests that failed once and passed on rerun | 0 |

**Traceability convention (proposal, needs developer and solution-architect agreement; OQ-4).** Story ACs are numbered `AC-1..n` per story, and the sponsor's acceptance criteria are `AC-01..09`, so the marker `req("NFR-022", "AC-7")` is ambiguous across stories. From PGD-13 onward add the story key: `req("FR-005", "PGD-13:AC-1")`. QA can then build each matrix from `--collect-only` without guessing. Until agreed, QA maps by file and test name as in the PGD-12 report.

---

## 9. Exit-code mapping: QA confirmation (D-21 / PQ-02)

QA co-owns PQ-02 and confirms the closed set 0 to 3 of D-21 (architecture 6.5, FR-043) as **testable and adequate**, with the conditions below. This is the G3 follow-up asked for in the consistency report.

| Outcome | Exit | First line (stdout or stderr) | Source | Verified so far |
|---------|:----:|--------------------------------|--------|-----------------|
| Success, including 0 PDFs and a dry run, and `--help` | 0 | summary; `No PDFs found` for an empty range | FR-043, FR-016, FR-044 | `--help` exits 0 (PGD-12 AC-1) |
| Any attachment error (`COMPLETED_WITH_ERRORS`) | 1 | summary with error count | FR-036, FR-043 | EPIC-03/06 |
| Cancel (Ctrl+C, Cancel button) | 1 | `Run cancelled` (plus "saved files are kept…") | FR-037, D-37/AQ-04 | PGD-13 AC-8 (interim), STORY-06.02 |
| Unreadable or newer-schema manifest | 1 | `error: <file> cannot be read …`; log and header-only CSV written; manifest and `.bak` byte-identical | FR-032, D-36 | EPIC-05 |
| Unexpected internal failure, including persistent list failure after retries | 1 | `error: unexpected failure, see the run log[: <path>]` | D-21, architecture 6.5 | PGD-13 AC-5, PGD-17 AC-4 |
| Bad arguments or validation error | 2 | `error: --start: Enter the date as YYYY-MM-DD, for example 2026-01-31.` etc.; nothing created | FR-015, FR-045, D-21 | unknown flag exits 2 (PGD-12); PGD-16 |
| Credentials missing or not a Desktop client, consent failed, `RefreshError` | 3 | one-line `error:` with action hint; interim `error: Gmail sign-in is not available in this build yet.` | FR-003, FR-006, architecture 6.5 | PGD-15 AC-6 (interim), EPIC-01 |

**Conditions and checks QA will apply**
1. **One table-driven test** (developer, from PGD-15 where `ExitCode` and `RunResult` exist) maps every `RunResult` to its exit code; QA fails G7 of any story that adds a result or code outside the closed set. No code 4, 5 or 130.
2. **Exit 1 is shared by four outcomes**, so the first line must be distinct and asserted exactly in each case, and the log, CSV or summary `result` field must tell them apart. A test that only checks `returncode == 1` is not enough for these cases.
3. **Windows Ctrl+C trap.** An unhandled `KeyboardInterrupt` on Windows can end the process with status `0xC000013A` (3221225786) rather than 1. The PGD-13 AC-8 test must run the CLI in a child process, deliver `CTRL_BREAK_EVENT` or `CTRL_C_EVENT` to its own process group, and assert exit 1 and the single line `Run cancelled`. QA will check this on the final head and reports a Product defect if the code differs.
4. **No success look-alikes.** A run that did not complete (cancel, manifest, internal) must never exit 0, and `--help` or an empty range must never exit non-zero.
5. **Streams.** Results on stdout; progress, warnings and errors on stderr (UX section 12); both asserted separately.

Observed in PGD-12: `gmail-pdf --help`, `python -m gmail_pdf --help` and the shim exit 0; `--bogus` exits 2 with usage on stderr. Sponsor sign-off on the mapping stays on the G8 list (PRD section 14.3 item 11).

---

## 10. Benchmark case BM-02: recall-sweep cost against NFR-002 (C12 / CC-02)

Co-owned with the solution-architect; needed **before STORY-02.09 is Ready**. STORY-02.08 builds the harness. QA owns the case design and the verdict.

**Why.** ADR-007 sets the sweep cost gate from NFR-001 only (ratio `sweep_extra / baseline` up to 0.8). NFR-002 allows 480 s for a re-run or dry run of 1,000 messages at 300 ms per call. A dry run costs one `messages.get` per message (no attachment bytes, D-22) = 300 s, so the sweep may add at most (480 − 300) ÷ 0.3 = **600 calls per 1,000 baseline messages: ratio 0.6**. At 0.8 a dry run would take about 540 s and fail NFR-002 although the ADR gate says pass.

| Item | Specification |
|------|---------------|
| Mailbox | `FakeGmail` with 1,000 baseline messages (one PDF ≤ 1 MB each) plus `round(r × 1,000)` extra messages found only by the sweep (an unnamed `application/pdf` part), generated at run time |
| Latency | Fixed 300 ms per API call (NFR-001/002 mock). Two modes: (a) **virtual time**, `latency_s=0.3` with an accumulating fake sleeper, deterministic and fast, in the normal suite; (b) **real sleep**, marker `perf`, nightly on Windows |
| Ratios r | 0, 0.5, **0.6**, 0.8, 1.0 (the ADR's 0, 0.5, 1.0 plus the two decisive points) |
| Modes | Dry run on a fresh folder; re-run after a completed run (both are NFR-002); first real run (NFR-001: ≤ 900 s) |
| Measured | Call counts by method from the recorder (list pages, `messages.get`, `attachments.get`); modelled time `T(r) = 0.3 × calls`; tool overhead (NFR-003) and list-page cost recorded separately |
| Pass (dry run, re-run) | `T(r) + overhead ≤ 480 s` for the chosen r; for the first run `T(r) + overhead ≤ 900 s` |
| Expected | Call-count model: dry run at r = 0.6 gives about 1,600 gets (480 s before list pages and overhead), at r = 0.8 about 1,800 gets (540 s, **fail**). The case must show r = 0.8 failing NFR-002 and prove the gate used by the product is the stricter of NFR-001 and NFR-002 |
| Verdict | QA reports the maximum permitted r = `(480 − list cost − overhead − 300) ÷ 300`, not only the 0.6 ceiling |

**QA notes for the solution-architect.** (1) 0.6 is a **ceiling, not a margin**: it assumes zero list and tool overhead. NFR-003 allows 50 ms per message at p95, which alone is 50 s per 1,000 messages and would lower the permitted ratio to about 0.43 if the overhead were at its limit. The harness will measure the real overhead and state the margin. (2) Please confirm in the ADR-007 restatement what counts toward the ratio (extra `messages.get` calls only, or also extra list pages) and whether a dry run pays the sweep (ADR-007 says it does) (OQ-2). (3) The fake's call recorder and injectable sleeper already support mode (a); no new fake feature is needed. (4) Real timing on the sponsor's mailbox (S-01, W3) is informational and investigated if above twice the mock result (NFR-001). Fallbacks if the gate fails: sweep off by default, or promote FR-038 (up to four parallel workers).

---

## 11. No-traceback check for the fake-mailbox hook and the CLI (D-21 "no stack trace")

**Rule.** No CLI outcome, including every failure of the test-only hook, may print a stack trace, the fixture file path, a secret, or the text of a chained exception. User-facing error text comes only from `redaction.safe_message` and `domain/messages.py`. The redacted traceback may appear in the run log at DEBUG only. (Master's note at G7: the fixture path is not a secret; the rule is kept because D-21 forbids a trace on screen and the chain would otherwise carry whatever path or text the caller supplied.)

**Why it is needed now.** In PGD-12 the hook's messages never echo the mailbox path, but the exception chain (`raise … from exc`) still holds the original `FileNotFoundError` text with the path. Today the CLI does not call the hook; PGD-15 wires it, so the check starts there.

| ID | Case (child process, hook env vars, socket guard on) | Expected |
|----|---------------------------------------------------------|----------|
| NT-01 | `GMAIL_PDF_TEST_FAKE_MAILBOX` set, `GMAIL_PDF_TESTING` not `1` (hook refused), **valid arguments** (valid dates and a valid zone). PGD-15 AC-6 (ii) | Exit 1; the single fixed stderr line `error: GMAIL_PDF_TEST_FAKE_MAILBOX is a test-only setting and needs GMAIL_PDF_TESTING=1.`; stdout empty; no trace, no path; no fall-through to real mode (no sign-in, no network call). Not the unexpected-failure line. **Invalid input beats the refused hook (QUA-62):** with a malformed or out-of-bounds date, a reversed range or an unknown zone the same environment exits 2 with the validation sentence and never prints this line, because validation runs before `build_deps` (PGD-16 AC-6); a probe asserts both directions. A future `--end` puts the AC-3 warning line first (QUA-63, row NT-09) |
| NT-02 | `GMAIL_PDF_TESTING=1`, file missing; and the path is a directory; and the file is unreadable. PGD-15 AC-6 (iii) | Exit 1; the single fixed line `error: The fake mailbox file could not be read; check GMAIL_PDF_TEST_FAKE_MAILBOX.`; no path; no trace; no fall-through |
| NT-03 | Content that is not a valid mailbox. PGD-15 AC-6 (iii), master's R1 rows (G6 attempt 2): malformed JSON; wrong format version; message without `id`; invalid UTF-8; a UTF-8 BOM; `payload.parts` of `[5]`, `[null]` and `["x"]` with no root filename; `labelIds` of `5`, `null` and `[[]]`; `internalDate` of 5000 digits; `latency_s` of `"inf"` and `1e300` | Same fixed line as NT-02, exit 1, for every row. **Binding outcome (R1):** for any file content the command ends in success or in exit 1 with exactly this line; content never produces `error: unexpected failure, see the run log` |
| NT-04 | Deeply nested JSON (DEF-001 / GitHub #15). PGD-15 AC-6 (iii), master's R1 rows: the load-time depth cap passes and cap + 1 fails; `payload.parts` at depths 247, 1000 and 1400; a deep value in the resource at 500 and 2900; a deep value under an unread top-level key at 2900; a sweep of depth 1 to 3000 in steps of 25 in `parts` and in the resource | Each row is a success or the same fixed line as NT-02 (exit 1); zero unexpected-failure lines, zero raw `RecursionError`. Cap boundary: QA probes both sides of the cap that the developer's test pins |
| NT-05 | Built wheel without `tests/`, both variables set. PGD-15 AC-6 (iii) | Exit 1; the single fixed line `error: The fake mailbox is only available from a source checkout (tests/ not importable).`; no path; no trace; no fall-through |
| NT-06 | An exception carrying a sentinel raised inside the runner and inside a worker thread | `error: unexpected failure, see the run log`; exit 1; no sentinel (PGD-13 AC-5, AC-6) |
| NT-07 | `KeyboardInterrupt` | `Run cancelled`; exit 1; no trace (section 9 item 3) |
| NT-08 | Scripted persistent HTTP 503 on the list call | Not reported as empty; exit 1; one `error:` line (PGD-17 AC-4) |
| NT-09 | Real mode: neither `GMAIL_PDF_TEST_FAKE_MAILBOX` nor `GMAIL_PDF_TESTING` set, valid arguments. PGD-15 AC-6 (i) | Exit 3; the single fixed line `error: Gmail sign-in is not available in this build yet.`; stdout empty; no credential read, no network call. Exit 3 belongs to real mode only, so QA asserts that NT-01 to NT-05 never exit 3 and that this row never exits 1. Invalid input in real mode exits 2 with the validation sentence, never 3 (PGD-16 AC-2, AC-4, AC-6, AC-9). **Line count (QUA-63, product-owner c.10312, D-79):** "the single fixed line" is the line for an `--end` that is today or earlier. With `--end` after today the AC-3 line `warning: End date is in the future. Only mail received so far is included.` comes first on stderr and the fixed line second, because the warning is printed before `build_deps` (order: parse, validate, print warnings, `build_deps`, run). The same two-line shape holds for NT-01 to NT-05, whose fixed lines also come from `build_deps`. QA asserts the order and the exact two lines; the exit code does not change. Interim line (A-5, R-09): STORY-01.04 and STORY-01.06 remove or replace it, and this row then changes with them |

**Assertions on stdout and stderr together**: none of `Traceback (most recent call last)`, `File "`, the fixture path or its directory, any sentinel, or any `__cause__` or `__context__` text; error cases print at most the documented number of lines (a future `--end` adds the AC-3 warning line before the fixed line, QUA-63); developer-mode flags (`-X dev`, `PYTHONDEVMODE`, `PYTHONFAULTHANDLER`) are unset in the child. **Owner:** the developer writes NT-01 to NT-09 as parametrised e2e cases in the stories named (PGD-13, PGD-15, PGD-16 for the QUA-62 and QUA-63 order cases, PGD-17); QA reviews them at G7 and runs NT-01 to NT-05 as probes with a deliberately distinctive file name. NT-01 to NT-05 and NT-09 are the three outcomes of PGD-15 AC-6 as amended by the product-owner (Jira c.10250, decision D-61): (i) NT-09, (ii) NT-01, (iii) NT-02 to NT-05; each has its own fixed line, so a probe proves the reason and not only the exit code.

---

## 12. Release gate G8: QA checks

| Check | Method | When |
|-------|--------|------|
| Full regression and NFR smoke | Section 7 release row; summary in `docs/07-qa/release-<version>-qa-summary.md` with pass rates, open defects by severity and residual risks | G8 |
| **pip-audit re-run** | `pip-audit -r requirements.txt` on the release commit, with date and result recorded. **Also `pip-audit -r requirements-dev.txt` once #14 lands** (solution-architect note on C16; the CI `security` job covers the runtime file only). A finding with a fix: developer bumps the pin and regenerates hashes; a finding without a fix: a `tech-debt` issue and a master decision (ADR-002 rule 4) | G8 (and after any pin change) |
| Secrets and repository hygiene | gitleaks over the full history, `.gitignore` patterns (PGD-14), `git ls-files` against the ignored patterns, no `secrets/` contents anywhere | G8 |
| Static | ruff, mypy strict, bandit clean on the release commit | G8 |
| Install proof | Wheel built, installed into a clean Windows venv with `--require-hashes`, `gmail-pdf --help` | G8 |
| Real-mailbox acceptance run | Sponsor-run (TR-006): AC-01..09 on a real range, timing against NFR-001 (informational, investigate above 2 × the mock result), AA-01 boundary behaviour, AA-04 quota, AA-06 long paths, Q-04 and Q-10 re-check | W3, before G8 |
| GOAL-09 and GOAL-11 trials | Stopwatch trials against the 30 s-per-PDF baseline; measured, gate nothing (D-11, D-38) | G7/G8 |
| Open-risk register | Residual risks of section 13 re-read; RISK-022 (CI not required on `main`) state | G8 |
| R1 exit criteria | Every R1 story Done; AC-01..09 verified on the CLI; GOAL-01..07 and GOAL-10 metrics on fixtures; NFR-011..013 evidence (release plan, R1 exit criteria) | G8 |

---

## 13. Residual risks recorded by QA

| ID | Risk | Source | Mitigation / plan | Owner |
|----|------|--------|-------------------|-------|
| R-01 | **Dynamic imports are invisible to AC-6.** The import-boundary check is an AST walk, so `importlib.import_module("…")` or `__import__` can break layering unseen. Accepted by master as within the AC; the application uses dynamic import only in the gated test hook, by design | PGD-12 report, G7 | Reviewers flag any new dynamic import in `gmail_pdf/`; QA greps `import_module` and `__import__` in `gmail_pdf/` at each G7 | reviewer-quality, qa-engineer |
| R-02 | **The exception chain holds the fixture path.** Hook messages omit the path, but `raise … from exc` keeps the original text in `__cause__`. Not a secret (master), but the on-screen rule of D-21 applies | PGD-12 report | Section 11 check; `safe_message` must walk the chain (PGD-13 AC-4) | developer, qa-engineer |
| R-03 | **Branch protection is not configured** (#7, RISK-022). The CI checks are not required on `main`, so a red PR could be merged | Master G7 | Delivery lead enables required checks; QA states in each report whether all jobs are green on the exact head to be merged | Santhosh |
| R-04 | pip-audit evidence is CI-only per story; the advisory database moves | PGD-12 AC-4 | G8 re-run (section 12) | qa-engineer |
| R-05 | **CI sets `PYTHONUTF8=1`**, which masks legacy-codepage failures. A pipe on Windows defaults to cp1252, so printing a non-ASCII file name could raise `UnicodeEncodeError` (QA hit this in a probe script) | QA observation, 2026-10-29 | Charter EC-9 with `PYTHONUTF8` unset before any story that prints file names (dry run list, summary); ask for an explicit decision in the console module (OQ-5) | developer, qa-engineer |
| R-06 | Fake fidelity gaps could let a defect hide: page token not tied to the query (#11), static attachment ids (#12), no part headers (#13), raw exceptions on odd input (DEF-001), `sendmsg` on Unix (DEF-002); RISK-021 | G6 deferrals, PGD-12 | Fix windows in section 14; integration tests with `HttpMockSequence` cover what the fake cannot | developer |
| R-07 | Memory measurements cannot separate product growth from fixture growth while the fake keeps rendered messages (PERF-01, #9, #10) | G6 deferral | Lazy factory seam before STORY-02.08 reaches G5 | developer |
| R-08 | AA-01 (Gmail epoch semantics), AA-04 (quota), AA-06 (long paths) cannot be proved on a fake | PRD assumptions | Real-mailbox run in W3 (section 12) | Santhosh, qa-engineer |
| R-09 | Interim placeholders in PGD-15 (`Messages in range: N`, interim exit 3 sign-in line) must be removed by the stories that replace them | PGD-15 A-5 | QA checks the replacing stories carry and meet that AC (STORY-07.04, STORY-01.04/01.06) | qa-engineer |
| R-10 | **CLOSED 2026-10-31 (D-80).** `argparse` accepts unambiguous option prefixes by default (`--sta` for `--start`), which would bypass the unknown-flag rule of FR-045 | QA error guessing | Decided yes (OQ-3, D-80): `allow_abbrev=False` is in scope of PGD-16 and carried by AC-6, so `--sta`, `--en` and `--t` exit 2 and nothing runs. QA still runs the rows at the PGD-16 G7 (section 15) | Closed (was: developer, product-owner) |
| R-11 | Windows file-system behaviour (case, long paths, reserved names) cannot be exercised on POSIX legs, and POSIX mode tests skip on Windows | NFR-020 | QA checks the right legs ran the skipped tests; Windows evidence stays the primary source | qa-engineer |

---

## 14. Defect mapping and fix windows

| Defect | Severity | Jira | GitHub | Where it is routed (master, G7 of PGD-12) | QA verification |
|--------|----------|------|--------|---------------------------------------------|-----------------|
| DEF-001 Fake mailbox hook and `FakeGmail` let edge-case input escape as raw exceptions (`RecursionError`, `ValueError`, `KeyError`) | Sev-4 | [PGD-63](https://sankumar76.atlassian.net/browse/PGD-63) | [#15](https://github.com/sankumar76/pdf-download-gmail/issues/15) | **PGD-15, fix before its G5**; it sits in the same files as #11 (RISK-021) | Re-run the three reproductions and NT-04 at the G7 of PGD-15; confirm the developer's regression tests |
| DEF-002 Socket guard does not cover `sendmsg(address)` on Unix | Sev-4 | [PGD-64](https://sankumar76.atlassian.net/browse/PGD-64) | [#16](https://github.com/sankumar76/pdf-download-gmail/issues/16) | **Sprint-02 G4**, or the next story that touches `tests/support/`, whichever is earlier. `sendmsg` does not exist on Windows 11 | Code inspection plus the Ubuntu and macOS legs; guard probes re-run |
| DEF-007 A start date before 1970-01-02 (1970-01-01 in UTC or Asia/Kolkata, and any earlier date) ends in the unexpected-failure line (exit 1) instead of a rejection, also for a range that holds messages | Sev-3 (re-rated from Sev-4, D-67) | [PGD-69](https://sankumar76.atlassian.net/browse/PGD-69) | [#39](https://github.com/sankumar76/pdf-download-gmail/issues/39) | **PGD-16 AC-9, in PR #41 before its G5** (fallback PGD-17). Product-owner: reject, not clamp (PGD-69 c.10295, PGD-16 c.10296, D-80). Product-manager: fits FR-015, PRD v0.5 (D-81). STORY-01.04 is not Ready while it is open (hard stop, D-67); RISK-026 closes with it | At the PGD-16 G7 on `c8b76ae`: the product-owner's exit-2 results (section 15, DEF-007 row), the control rows that still exit 0, the floor and ceiling dates in every zone, and real mode (exit 2, never 3). After the merge, QA closes #39 and PGD-69 (D-85) |

Tracked G6 items that QA also watches: #7, #8, #9 and #10 (STORY-02.08), #11 (PGD-15), #12 (STORY-03.03), #13 (PGD-18), #14 (ADR-002 dev list).

---

## 15. Per-story acceptance focus, sprint 01 (PGD-13 to PGD-18)

For each story QA verifies every AC of the Jira story with fresh evidence, then applies the extra focus below.

| Story | Focus ACs and risk | Extra QA checks (techniques) |
|-------|--------------------|------------------------------|
| **PGD-13 STORY-01.01** One redaction path (5 pts) | AC-1..2 registry and patterns; AC-3 logging and third-party caps; AC-4 `safe_message`; AC-5 hooks; AC-6 sentinel matrix; AC-7 install order; AC-8 Ctrl+C. Risk 15 | Mutation: delete one redaction call or one hook install, the matrix must fail. Error guessing: secret split across a chained exception, in a URL query string, empty and 7-character values, repeated registration, an exception whose `__str__` raises, Unicode text, a secret in a worker thread. Over-redaction negatives (ordinary text unchanged). Call-order test for AC-7. Section 9 item 3 (Windows Ctrl+C status) and NT-06, NT-07. Static check that `redaction.py` imports only stdlib and `domain.messages`. Review the diff for any `print` or `str(exc)` outside the one path. Every branch of `redaction.py` tested even above the 80 % gate |
| **PGD-14 STORY-01.02** Secret files out of git, protected on disk (3 pts) | AC-1 patterns and `git check-ignore`; AC-2 POSIX modes; AC-3 failed write keeps old content; AC-4 token location warning (Windows); AC-5 tracked files and gitleaks. Risk 15 (RISK-005) | Equivalence classes for patterns (positive and near-miss names such as `credentials.json.txt`, nested folders, upper case); all pre-existing `.gitignore` lines kept; `git add -f` is not prevented, so the tracked-files test is the control. AC-2 skips on Windows, so QA confirms the Ubuntu and macOS legs executed it (not skipped). Injected `OSError` mid-write leaves no temp file. Drive-letter case, `..` escape and a symlinked home for AC-4. Confirm no test or code reads a real `secrets/` folder (SEC-08) |
| **PGD-15 STORY-02.02** Select messages for an inclusive range (8 pts) | AC-1..3 range maths; AC-4 query and request parameters; AC-5 and AC-6 CLI; AC-7 retry; AC-8 static discovery offline; AC-9 quota note; AC-10 default zone. Risk 15 | Boundary-value analysis with literal epochs in `Asia/Kolkata`, `Pacific/Kiritimati`, `Pacific/Pago_Pago`, `America/New_York` DST days, leap day, year edge, start equal to end; **both** epoch interpretations of the fake. Exact `q` string (no trailing space) and `fields`, `maxResults`, `userId`, `includeSpamTrash` on `HttpMockSequence`; recorder shows only allowed methods. Retry: all listed statuses, `Retry-After` in seconds and as an HTTP date, delay bounds, 6 attempts, cancel-aware wait. AC-8 under the guard with no network. Check AC-9 evidence quality. **Verify DEF-001 (#15) is fixed.** NT-01 to NT-04, NT-08. Interim `Messages in range: N` and exit-3 line tracked for removal (R-09). Probe `--sta` abbreviation (R-10) |
| **PGD-16 STORY-02.03** Reject bad input before contacting Google (5 pts) | AC-1 malformed dates; AC-2 reversed range; AC-3 future end warning; AC-4 time zone; AC-5 several errors; AC-6 no side effects and abbreviated flags; AC-7 shared message table and `ValidationResult.request`; AC-8 sentinel path; **AC-9 date bounds 1970-01-02 to 9999-12-30 (DEF-007)** | Equivalence partitioning and boundary table for dates (every form listed, plus `0000-00-00`, leap day on a non-leap year, very long input, option-like values such as `--start --end`, repeated flags, `--start=…` form); exact strings and order; exit 2 for all. Zone-dependent "today" with a fixed clock. Folder diff before and after, zero recorder calls, no credential read. **Real mode** (neither hook variable): every rejection exits 2, never 3, and `build_deps` is not reached (AC-2, AC-4, AC-6). **Order (QUA-62, QUA-63):** invalid input beats the refused hook (NT-01); a future `--end` with a failing build gives the AC-3 warning line, then the fixed build line (NT-09). **AC-4 rows for the O1 classes:** no `--tz` and `tzlocal` failing with each of `LookupError`, `ValueError`, `OSError`, `AttributeError` and `TypeError` (and a subclass of each, for example `ZoneInfoNotFoundError` and `FileNotFoundError`), on the hook and in real mode: exit 2, the AC-4 sentence after any date lines, `build_deps` not called; with `--tz` given, no system-zone lookup; also tzlocal's real Windows function over a faked registry whose value has the wrong type (`AttributeError`, `TypeError`). **Abbreviations (OQ-3, R-10 closed):** `--sta`, `--en` and `--t` exit 2 and nothing runs; the full names still work. **AC-9:** see the DEF-007 row below. Message wording only from `messages.py` (grep the `cli/` tree), no flag-name literal in `messages.py` (STD-55). Sentinel in `--start` appears nowhere |
| **DEF-007 = PGD-69 = #39**, fixed inside PGD-16 AC-9 (Sev-3) | Reject, not clamp (product-owner, D-80): `--start` and `--end` must each lie from 1970-01-02 to 9999-12-30 inclusive, as calendar dates, the same in every zone; otherwise exit 2, one fixed line `error: --start: Enter a date from 1970-01-02 to 9999-12-30.` (or `--end:`), no echo, no query built. Master keeps the rating at Sev-3; reopen it if real Gmail is ever shown to match less on a negative bound | Boundary-value analysis (1970-01-01, 1970-01-02, 9999-12-30, 9999-12-31) and a decision table over start in or out of bounds, end in or out, zone valid or not, hook or real mode. Fake mailbox with 4 messages in range, real child processes on `c8b76ae`; **the product-owner's exit-2 results:** (1) `1970-01-01..2026-12-31` in UTC, Asia/Kolkata and America/New_York, `1960-01-01..2026-12-31` UTC, `1900-01-01..2026-12-31` Asia/Kolkata and `0001-01-01..2026-12-31` UTC: exit 2, the single `--start:` line, no message count (America/New_York was exit 0 and now exits 2, because the rule is a calendar date; the other rows were exit 1 with the unexpected-failure line). (2) `1970-01-01..1970-01-01` and `1969-12-31..1969-12-31` UTC: exit 2, two lines, `--start:` then `--end:`. (3) `2026-01-01..9999-12-31` in any zone: exit 2, one `--end:` line; `9999-12-31..9999-12-31`: `--start:` then `--end:`. (4) `1960-01-01..1950-01-01` UTC: `--start:` then `--end:`, no reversed-range line (AC-5); `1970-01-01..2026-01-01` with `--tz Mars/Olympus`: `--start:` then `--tz:`. (5) Real mode, `1960-01-01..2026-12-31` UTC: exit 2, one `--start:` line (was exit 3), `build_deps` not called. **Controls that still exit 0:** `1970-01-02..1970-01-02` UTC (`Messages in range: 0`); `1970-01-02..2026-12-31` in UTC, Pacific/Kiritimati, Pacific/Apia and Etc/GMT-14, and `2000-01-01..2026-12-31` UTC (`Messages in range: 4`); `2026-01-01..9999-12-30` in UTC, Etc/GMT-14 and Etc/GMT+12 (AC-3 warning, normal result). **Sweep:** floor and ceiling dates in every name of `available_timezones()` build a `q` whose `after:` and `before:` are integers of 0 or more on the real gateway under `HttpMockSequence`; the unexpected-failure line never appears for a date reason. After the merge QA closes #39 and PGD-69 (D-85) |
| **PGD-17 STORY-02.06** End an empty range normally (2 pts) | AC-1 empty result; AC-2 all out of range; AC-3 clean output; AC-4 failure is not empty; AC-5 exit mapping | Decision table: {no match, match but out of range, list fails after 6 attempts, empty range plus future end date} × {stdout, stderr, exit, files}. Streams asserted separately. Section 9 items 1, 2 and 4. NT-08 |
| **PGD-18 STORY-03.01** Recognise a PDF part (3 pts, stretch) | AC-1..5 type and name matrix; AC-6 Drive link is not an attachment; AC-7 body never decoded; AC-8 whitespace and trailing dot | Full type-by-name decision table including `.PDF` with octet-stream, multiple dots, Unicode and RFC 2047/2231 names, `x.pdf.exe`, `pdf`, empty name; mutation: make the function read `body.data`, the sentinel test must fail (NFR-016). Every branch of the detector tested. Result feeds the manifest `detector_version` note |

---

## 16. Exploratory charters

Each session is time-boxed (60 to 90 minutes), recorded in the story's test report with mission, areas, findings and any defects. Charters rotate by risk; repeat a charter when its area changes.

| ID | Mission | Areas | When |
|----|---------|-------|------|
| EC-1 | Break the test-support seams every story relies on | Socket guard bypass routes, fake mailbox faults, paging, epoch modes, env hook values and malformed files (done for PGD-12) | Re-run when `tests/support/`, `tests/fakes/` or `bootstrap.py` change |
| EC-2 | Find a text surface that bypasses redaction | Every `print`, logger, exception message, thread, `atexit`, `repr` of objects holding credentials; odd exception types | PGD-13, then every story that adds output |
| EC-3 | Break date-range and time-zone logic | Half-hour and +14 h zones, DST transitions, leap day, system zone variants, patched `tzlocal` | PGD-15, PGD-16 |
| EC-4 | Abuse the command line | Abbreviated and repeated flags, Unicode and very long values, option-like values, empty strings, quoting on cmd and PowerShell | PGD-16, STORY-07.01 |
| EC-5 | Get a secret file into git or leave it readable | Name variants, nested folders, `git add -f`, CRLF in `.gitignore`, negation patterns, permission edge cases on POSIX | PGD-14 |
| EC-6 | Make an empty run look like a failure, or a failure look empty | Retry exhaustion, partial listing, cancel during listing, future end date | PGD-17 |
| EC-7 | Fool the PDF detector | Odd types and names, encoded names, disguised non-PDFs, Drive links | PGD-18, EPIC-03 |
| EC-8 | Break retry and backoff | Retry-After formats, 403 variants, timeouts, cancel during a wait | PGD-15 |
| EC-9 | Windows console and encoding | `PYTHONUTF8` unset, cp1252 pipes, redirected output, paths with spaces, non-ASCII names (R-05) | Before the first story that prints file names |
| EC-10 | Safe-write and interrupt behaviour | No overwrite, race at the final name, kill at injected points, read-only target (EPIC-04/05/06) | When those stories are Ready |
| EC-11 | Packaging and clean install | Wheel contents, clean venv, entry points, hook from a wheel | G8 and any change to `pyproject.toml` |

---

## 17. Open questions and items for other roles

| ID | Question or item | Owner | Needed by |
|----|------------------|-------|-----------|
| OQ-1 | **CLOSED 2026-10-31.** Decided by the product-owner in the PGD-15 AC-6 amendment (Jira c.10250, 2026-10-30), recorded as D-61: exit 1 with a dedicated fixed line, not the unexpected-failure line QA had proposed. Refused hook: `error: GMAIL_PDF_TEST_FAKE_MAILBOX is a test-only setting and needs GMAIL_PDF_TESTING=1.` Unreadable or malformed fake file: `error: The fake mailbox file could not be read; check GMAIL_PDF_TEST_FAKE_MAILBOX.` `tests/` not importable: `error: The fake mailbox is only available from a source checkout (tests/ not importable).` Real mode without a hook variable: exit 3, `error: Gmail sign-in is not available in this build yet.` Tests: NT-01 to NT-05 and NT-09 (section 11) | product-owner, developer | Closed (was: before PGD-15 G5) |
| OQ-2 | In the ADR-007 restatement (C12), what counts toward the sweep ratio, and does the 0.6 ceiling leave room for list and tool overhead? (section 10) | solution-architect | Before STORY-02.09 Ready |
| OQ-3 | **CLOSED 2026-10-31.** Decided yes by the product-owner (Jira PGD-16 c.10296, 2026-10-31), recorded as D-80 (3): `allow_abbrev=False`, in scope of PGD-16, carried by AC-6, closing R-10. Rows: `--sta 2026-01-01 --end 2026-01-31`, `--start 2026-01-01 --en 2026-01-31` and `--t UTC` exit 2 and nothing runs; the full names still work. The wording and redaction of argparse's own message stay with STORY-07.01 and #23 | product-owner | Closed (was: PGD-16) |
| OQ-4 | Agree the `req("…", "PGD-13:AC-1")` marker convention (section 8) | developer, solution-architect | PGD-13 G5 |
| OQ-5 | Console encoding policy for stdout and stderr on Windows pipes (R-05) | developer, solution-architect | Before the first story that prints file names |

Issues for other roles (not QA's to fix): enable required checks on `main` (#7, delivery lead); ADR-002 dev-list update and a `pip-audit -r requirements-dev.txt` result (#14, solution-architect); link #15 to PGD-15 and schedule #16 (C20, scrum-master).

---

## Annex A. NFR verification map

| NFR | How verified | Level and place | When |
|-----|--------------|-----------------|------|
| NFR-001 first-run throughput | Benchmark at 300 ms per call, sweep ratios (section 10) | `perf` suite, nightly | STORY-02.08, G8 |
| NFR-002 re-run and dry-run scan | BM-02 | `perf` + virtual-time case | Before STORY-02.09 Ready |
| NFR-003 tool overhead | Zero-latency, 1,000 messages, p95 per message | `perf` | STORY-02.08 |
| NFR-005 audit completeness | Reconciliation over at least 8 scripted runs | e2e | EPIC-07 |
| NFR-006 retry | `FakeClock` and `FakeSleeper` unit table, `HttpMockSequence` integration | unit, integration | PGD-15 |
| NFR-007 interrupt safety | 100-point kill loop | e2e | EPIC-05/06 |
| NFR-008 failure isolation | One fault each at message fetch, attachment fetch, decode, disk write | e2e | EPIC-03/06 |
| NFR-009, 010 memory and volume | `tracemalloc` and RSS, 500 vs 10,000 message fixtures, manifest scale | `perf` | STORY-02.08 |
| NFR-011 read-only | Scope list and recorder allow-list, AST test for write methods | unit, integration | EPIC-01, PGD-15 onward |
| NFR-012 secret hygiene | Sentinel matrix, secret scan | unit, CI | PGD-13 onward |
| NFR-013 secret files | Mode and pattern tests | integration | PGD-14 |
| NFR-014 no egress | Socket guard (unit), host recorder on `httplib2` (integration) | unit, integration | Done for the guard (PGD-12) |
| NFR-016 data minimisation | Body-text sentinel absent from log, CSV, manifest | unit | PGD-18, EPIC-07 |
| NFR-017..019, 021 accessibility and display (R2) | Keyboard and focus tests, contrast script, screenshot matrix, Narrator walkthrough | GUI | Held by C11 |
| NFR-020 platforms | CI matrix; Windows local at G7 | CI | Every PR |
| NFR-022 quality gates | Section 2 gates | CI | Every PR |
| NFR-023 dependencies | Allow-list test, pip-audit | unit, CI | Every PR with a dependency change; G8 |
| NFR-024 formats | Table-driven date and Unicode-name tests | unit | PGD-15, PGD-16, EPIC-04 |

## Annex B. Change log

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 0.1 | 2026-10-30 | qa-engineer | First version, closes C19 / T-03. Confirms D-21; adds BM-02 (C12), the no-traceback check, the G8 pip-audit plan, residual risks R-01 to R-11, the defect mapping for DEF-001 and DEF-002, per-story focus for PGD-13 to PGD-18, charters EC-1 to EC-11, open questions OQ-1 to OQ-5 |
| 0.2 | 2026-10-31 | qa-engineer | C35 (gate-log, G6 attempt 2 of PGD-15). Section 11: NT-01 now exit 1 with the fixed test-only-setting line; NT-02 to NT-05 state their fixed lines and exit 1; NT-03 and NT-04 gain master's R1 rows (shape rows and depth rows, binding outcome: success or the fixed line, never the unexpected-failure line); new NT-09 for the real-mode exit 3 line; NT-01 to NT-05 and NT-09 tied to PGD-15 AC-6 (c.10250, D-61). Section 17: OQ-1 closed. The rest of C32 stays due at the sprint-02 G4 |
| 0.3 | 2026-10-31 | qa-engineer | C41 (c) and C42 (gate-log, G6 attempt 2 of PGD-16). Header brought to this version (it still read 0.1 while this log held 0.2). Section 14: DEF-007 row. Section 15: PGD-16 row now 5 pts and AC-1..AC-9, with the AC-4 rows for the O1 classes (`LookupError`, `ValueError`, `OSError`, `AttributeError`, `TypeError`), the real-mode and order checks; new DEF-007 row with the product-owner's exit-2 results. Section 11: NT-01 says "valid arguments" and that invalid input beats the refused hook (QUA-62); NT-09 and the assertions follow the product-owner's QUA-63 answer (c.10312, D-79). Section 13: R-10 closed (D-80). Section 17: OQ-3 closed (D-80). The rest of C32 stays due at the sprint-02 G4 |
