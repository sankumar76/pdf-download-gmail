# EPIC-02: Find messages in a date range

| Field | Value |
|-------|-------|
| Owner | product-owner |
| Jira | [PGD-3](https://sankumar76.atlassian.net/browse/PGD-3) (relates to Intake [PGD-1](https://sankumar76.atlassian.net/browse/PGD-1)) |
| Release | R1 Core + CLI (v0.9.0); GUI fields for FR-010 and FR-013 are in EPIC-09 |
| Wave | W1 (FR-008, 009, 010, 011, 012, 013, 014, 015, 016 and both enablers), W2 (FR-017) |
| Priority | Backlog rank 1 of 10 (hosts the sprint-1 foundation enablers) |
| PRD size | L (19 pts, PRD §7; the enablers below are not itemised in that figure, see consistency report CC-01) |
| Status | Ready for story slicing (scrum-master) |

## Goal & User Value
Exactly the right messages are selected for the chosen period, in a fixed order, so that file names are the same on every run (GOAL-01 complete retrieval, GOAL-02 predictable naming, GOAL-03 safe re-runs).

## Requirements Covered
- Functional: FR-008, FR-009, FR-010, FR-011, FR-012, FR-013, FR-014, FR-015, FR-016, FR-017 (Should, conditional on the S-01 gate).
- Non-functional: NFR-001, NFR-002, NFR-003 (performance, measured by the benchmark harness here), NFR-006 (retry and backoff in the gateway), NFR-009, NFR-010 (memory and volume harness), NFR-024 (date formats).
- Cross-cutting enablers hosted here (no FR): NFR-020 (CI matrix), NFR-022 (quality gates), NFR-023 (dependency allow-list), `pip-audit` on the first pinned requirements (gate-log G3 follow-up).
- Business rules / source IDs: BR-002, BR-004, BR-012, BR-014; UR-001, UR-008, UR-009; CFG-01, 02, 04..06; VAL-01, 02; EC-05..07; AC-02.

## Scope
**In:**
- Inclusive range in a chosen time zone (calendar-day boundary, DST); epoch-second search with the +/-1 s widening and a local re-check (FR-008, 009, 012; AA-01).
- Extra Gmail search text and the Spam/Trash option in the CLI (FR-010, FR-013). They are scheduled in W1 because the FR-045 flag table must be complete.
- All result pages, 500 per page (FR-011); fixed order: received time, then messageId (length, then lexicographic), then part order (FR-014).
- Input validation before any Google call, exit 2, and the future-end warning (FR-015); an empty range ends normally with exit 0 (FR-016).
- Recall sweep for unnamed PDFs, default on, ADR-007 (FR-017).
- Enablers (explicit, justified): E-1 walking skeleton, CI pipeline and fake mailbox with fixture builders; E-2 benchmark and memory harness (NFR-001..003, 009, 010).

**Out:** parallel fetching (FR-038, backlog; promoted if the first benchmark fails NFR-001/002); GUI fields (EPIC-09); the paging and retry code is exercised here but the live Google run is EPIC-01 story 7.

## UX & Architecture References
- Screens / journeys: SCR-01 (R2 fields); CLI messages in UX §12; UJ-02, UJ-03, UJ-05, UJ-07 ([ux-spec](../../03-ux/ux-spec.md) §9 rows 008-017).
- Components: `domain.daterange`, `domain.query`, `domain.validation`, `app.planner`, `infra.gmail_gateway`, `infra.retry`, `infra.tz` ([architecture](../../04-architecture/architecture.md) §4.1, §6.2-6.4, §7, §12); source tree §10.1; CI [test-strategy](../../04-architecture/test-strategy.md) §9.
- ADRs: [ADR-002](../../04-architecture/adr/ADR-002-dependency-policy.md) (tzdata, tzlocal, no YAML), [ADR-007](../../04-architecture/adr/ADR-007-candidate-search-recall.md) (sweep, S-01 gate, GitHub #2), [ADR-006](../../04-architecture/adr/ADR-006-core-execution-model.md).
- PRD: [§4.2](../../02-product/prd.md); release plan W1.

## Stories (ordered)
Candidates only; the scrum-master creates the stories.

| # | Story ID | Title | Intent (one line) | Splitting pattern | Depends on | Status |
|---|----------|-------|-------------------|-------------------|------------|--------|
| 1 | STORY-02.01 | Enabler E-1: walking skeleton, CI and fake mailbox | [W1] Package layout, `pyproject.toml`, ruff/mypy/pytest-cov gates, GitHub Actions per test-strategy §9, `FakeGmail` and fixture builders, dependency pins with `pip-audit`. Justification: no other story can be tested or merged without it (NFR-020, 022, 023); it carries no FR of its own | Explicit enabler (exception to vertical slicing) | none | Candidate |
| 2 | STORY-02.02 | Select the messages for an inclusive date range | [W1] `--start/--end/--tz` on the fake mailbox gives exactly the in-range messages, 23:59:59 in and next-day 00:00:00 out, DST-safe (FR-008, 009, 012) | Workflow step (first slice through all layers) | 02.01 | Candidate |
| 3 | STORY-02.03 | Reject bad input before contacting Google | [W1] Reversed or malformed dates give a one-line error and exit 2; a future end date warns and continues (FR-015) | Happy / unhappy path | 02.02 | Candidate |
| 4 | STORY-02.04 | Read every result page | [W1] A 3-page mock returns all messages (FR-011, EC-07) | Data variation (volume) | 02.02 | Candidate |
| 5 | STORY-02.05 | Process messages in a fixed order | [W1] Two runs, including two messages with equal received time, give identical order (FR-014, PD-03) | Business-rule variation | 02.02 | Candidate |
| 6 | STORY-02.06 | End an empty range normally | [W1] "0 PDFs found", exit 0 (FR-016) | Happy / empty path | 02.02 | Candidate |
| 7 | STORY-02.07 | Add search text and include Spam/Trash | [W1] `--query` and `--include-spam-trash` change the query as specified; default excludes Spam/Trash (FR-010, 013) | Business-rule variation (options) | 02.02 | Candidate |
| 8 | STORY-02.08 | Enabler E-2: benchmark and memory harness | [W1] Latency-mock benchmark for NFR-001..003 at sweep ratios 0/0.5/1.0 and the memory/growth profile for NFR-009/010; first S-01 numbers. Justification: the W1 exit check and RISK-011/014 need measured data before the sweep and FR-038 decisions | Explicit enabler | 02.01, 02.04 | Candidate |
| 9 | STORY-02.09 | Find PDFs that Gmail's filename search misses | [W2] Recall sweep `has:attachment -filename:pdf`, union de-duplicated, unnamed PDF saved as `attachment.pdf` (FR-017, ADR-007). Gate: switch off or promote FR-038 if `sweep_extra / baseline` exceeds the gate (see consistency report CC-02 for the NFR-002 bound) | Happy / unhappy path (gate) | 02.08, EPIC-03 | Candidate |

## Epic Acceptance Criteria
- [ ] Boundary tests pass: 23:59:59 on the end date is in range, 00:00:00 the next day is out, including a DST-crossing range (AC-02).
- [ ] The query-string unit test shows epoch-second bounds; a fixture mailbox with in-range and out-of-range messages yields only in-range ones.
- [ ] A 3-page mock returns all messages; a message outside the range that the search returned is skipped.
- [ ] Two runs on one fixture, including two messages with equal received time, give identical order and names.
- [ ] Reversed, malformed and future-end ranges behave per FR-015 (exit 2 before any Google call; warning for future end).
- [ ] An empty range exits 0 and reports "0 PDFs found".
- [ ] The benchmark harness runs NFR-001..003, 009 and 010 on the mock and records the results; the sweep (FR-017) is accepted or switched off against the S-01 gate.
- [ ] CI runs lint, types, tests (Windows 3.10-3.12), coverage and security stages (test-strategy §9); `pip-audit` has run on the pinned requirements.

## Dependencies & Risks
- Depends on: nothing upstream for 02.01. FR-017 needs EPIC-03 (extraction) and the W1 benchmark.
- Risks: RISK-007 search recall (S-01, GitHub #2), RISK-011 unvalidated performance targets (02.08), RISK-014 NFR-009 growth figure (02.08), RISK-010 Must share. Capacity: the two enablers are real work not itemised in the PRD's 19 pts; the scrum-master sizes them and tells the product-owner if EPIC-02 no longer fits sprint 1 (CC-01).
