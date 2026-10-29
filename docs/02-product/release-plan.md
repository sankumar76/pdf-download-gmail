# Release Plan — Gmail PDF Attachment Downloader

| Field | Value |
|-------|-------|
| Version | 0.1 |
| Owner | product-manager |
| Date | 2026-10-29 |
| Status | In Review (G2) |
| Source | [prd.md](prd.md) v0.1 (§4 FRs, §6 scope, §7 epics, §14 decisions) |
| Jira | [PGD-1](https://sankumar76.atlassian.net/browse/PGD-1) |

No deadline or team velocity exists (Q-01, ASSUMPTION-14). This plan therefore orders work by **sequence and gates, not dates**. Points are the relative PM sizes in the PRD; the scrum-master calibrates sprints after the first one and plans below measured velocity (PRD §8).

## 1. Releases at a glance

| Release | Name | Version | Scope | Pts | Delivers | Ships alone? |
|---------|------|---------|-------|-----|----------|--------------|
| **R1** | Core + CLI (MVP part 1) | v0.9.0 | EPIC-01..08 (FR-001..006, 008..033, 036, 037, 039..046, 065, 066; FR-017 conditional) | 99 | Primary outcome: GOAL-01..07 and GOAL-10 through the CLI | **Yes** |
| **R2** | Desktop GUI (MVP part 2) | v1.0.0 | EPIC-09, EPIC-10 (FR-047..060, 062, 064; GUI fields for FR-010, 013; GUI surfaces of FR-005, 006, 015, 037, 042) | 42 | GOAL-08, GOAL-09, GUI parity; product form required by D-01 and CLAUDE.md §9 | No (needs R1 core) |
| **R3** | Hardening | v1.1.0 | FR-007 sign-out, FR-034 manifest recovery, FR-061 Advanced area, FR-063 screen reader | 12 | RISK-008 closed further; accessibility and settings reach | Yes |
| **Backlog** | Unscheduled | — | FR-035 skip-identical, FR-038 parallel fetch (promotion trigger below), items in PRD §6.2 | 7 | — | — |

**MVP = R1 + R2 = 141 pts.** R1 and R2 are separate releases so that the GUI risk (RISK-001) cannot delay the primary outcome. If the sponsor wants a single drop, R1 is simply tagged internally and R2 follows; scope is unchanged.

## 2. R1 — Core + CLI (v0.9.0)

**Objective.** Santhosh can run `--start/--end` against his real mailbox, preview with `--dry-run`, download, re-run safely, and audit the result.

**Epics and order (waves).** Waves are dependency order for the product-owner and scrum-master; sprint boundaries are theirs to set. Live Google access comes last because it needs the sponsor's setup (TR-006) and everything else can be proved on a mocked Gmail API with synthetic data.

| Wave | Epics / FRs | Outcome (exit check) | Notes |
|------|-------------|----------------------|-------|
| **W1 Dry-run skeleton on a mocked mailbox** | EPIC-02 (FR-008, 009, 011, 012, 014, 015, 016), EPIC-03 (FR-018..021), EPIC-04 (FR-022..027), FR-044, FR-045, **FR-005 redaction path** | A dry run on a fixture mailbox prints the RD §4.4 example names exactly; boundary, nested-MIME and malicious-name tests pass; benchmark harness exists (NFR-001..003) | **First-sprint candidate.** Redaction first so no later log line can bypass it. Delivers GOAL-02 and most of GOAL-01 without credentials |
| **W2 Safe save, audit, resilience** | EPIC-05 (FR-028..033), EPIC-06 (FR-036, 037), EPIC-07 (FR-039..043, 046), EPIC-01 mock-tested parts (FR-001..004) | Two-run test saves 0 new files; fault-injection and interrupt tests green (NFR-007, 008); GOAL-10 reconciliation test green; scope list asserted | FR-017 enters here if the Q-07 spike (G3) shows it fits NFR-001/002 |
| **W3 Live access and onboarding** | EPIC-01 live consent (needs TR-006), EPIC-08 (FR-065, 066), FR-006 | Real-mailbox acceptance: dry run then run on a one-week range, ≥ 10 sponsor-named PDFs found (PA-04); README followed unaided | Needs `credentials.json` from Santhosh. Records the real timing for NFR-001 |

**R1 entry criteria:** G3 passed (architecture, ADRs for dependencies, Q-07 spike scheduled), G4 passed (epics and first stories Ready).
**R1 exit criteria:** every R1 story Done (G5–G7); AC-01..09 verified on the CLI; GOAL-01..07 and GOAL-10 metrics met on fixtures (PRD §3); real-mailbox acceptance run done; NFR-011..013 evidence attached; release notes `release-notes-v0.9.0.md` written by the PM; G8 for the release with sponsor sign-off.

## 3. R2 — Desktop GUI (v1.0.0, MVP complete)

**Objective.** The same job through one window, compliant with CLAUDE.md §9, with no command typing.

| Wave | Epics / FRs | Outcome (exit check) | Notes |
|------|-------------|----------------------|-------|
| **W4 Shell and tokens** | EPIC-10 tokens first: FR-054..057, FR-056 button component; FR-058, 059 | One window with the four type roles, spacing scale, palette, one button; resize and 150 %/200 % scaling checked | Tokens before screens, so no screen can hard-code values (GOAL-08). The framework spike against FR-054..060 happens at G3 (RISK-012) |
| **W5 Workflow** | EPIC-09: FR-047..053, FR-064; GUI surfaces of FR-005, 006, 015, 037, 042 | Launch to saved files without a terminal; Cancel; progress; summary and open links; CSV from GUI equals CLI CSV | Needs the R1 core to expose progress events and cancellation |
| **W6 Quality bar** | FR-060 keyboard, FR-062 ux checklist, NFR-004, 017, 018, 021 | Screenshot matrix, Tab-order walkthrough, contrast script, GOAL-09 stopwatch trial with the sponsor | GOAL-09 needs TR-006 |

**R2 entry criteria:** R1 released; UI-framework ADR accepted; ux-spec passed G3.
**R2 exit criteria:** FR-047..060, 062, 064 Done; GOAL-07 diff test green (0 differences); GOAL-08 checks pass (0 hard-coded values, 1 button component, 4 roles); AC-01..09 verified on the GUI; release notes `release-notes-v1.0.0.md`; G8 with sponsor sign-off (the sponsor also confirms the PRD §14.3 items here).

## 4. R3 — Hardening (v1.1.0) and backlog

| Item | FR | Trigger / condition |
|------|----|---------------------|
| Sign-out | FR-007 | Planned after MVP |
| Manifest recovery from CSV reports and hashes | FR-034 | Planned; **pull forward into R1 if** a manifest loss or an unexpected `_1` file is seen in QA or by the sponsor (RISK-008 trigger) |
| Advanced settings area | FR-061 | Planned after MVP |
| Screen-reader support | FR-063 | Planned; pull forward if the sponsor or another user needs it |
| Skip-identical | FR-035 | Backlog; only on sponsor request |
| Parallel fetching (≤ 4 workers) | FR-038 | **Promote to Must in R1** if the W1 benchmark or the real timing misses NFR-001 or NFR-002 |
| Settings file, installer, scheduling, multi-account | PRD §6.2 | Won't until the sponsor asks |

## 5. Dependencies and critical path

| Dependency | Blocks | Owner | Needed by |
|------------|--------|-------|-----------|
| G3 ADRs (GUI framework, time-zone/YAML dependencies, Q-03 delivery form) and Q-07 spike | W1 (dependencies), FR-017, W4 | solution-architect | G3 |
| Synthetic fixture mailbox and mock Gmail API | All waves | developer, qa-engineer | W1 |
| Sponsor's Google Cloud setup and `credentials.json` (TR-006) | W3 live consent, real-mailbox acceptance, GOAL-09 trial | Santhosh | Start of W3 |
| Sponsor-named sample of ≥ 10 known PDFs (PA-04) | W3 acceptance | Santhosh | W3 |
| R1 core callable with progress and cancel | W5 | solution-architect | G3 |
| ux-spec with §9 tokens and setup flow | W4, W5 | ux-expert | G3 |

Critical path: G3 ADRs → W1 → W2 → W3 (needs sponsor setup) → R1 release → W4 → W5 → W6 → R2 release.

## 6. Release risks (see PRD §10)

| Risk | Release | Watch |
|------|---------|-------|
| RISK-010 Must is 93 % of MVP effort | R1, R2 | Velocity from the first sprint; any slip is raised as a scope-change proposal, never absorbed silently |
| RISK-011 Unvalidated performance targets | R1 | W1 benchmark; FR-038 trigger |
| RISK-007 Search recall | R1 | Q-07 spike; W3 sponsor sample |
| RISK-008 Manifest loss | R1, R3 | FR-032/033 in R1; FR-034 pull-forward trigger |
| RISK-003 Token expiry in Testing status | R1 | `invalid_grant` during W3; README (FR-066) |
| RISK-001 / RISK-012 GUI scope and framework fit | R2 | ADR spike result; EPIC-09 estimates growth sprint over sprint |

## 7. Release governance
- Story gates G5–G7 apply per story; G8 per release, decided by master with sponsor sign-off (`HUMAN_APPROVAL_POINTS = G8`).
- Release notes for each release are written by the PM from `docs/templates/release-notes.md` once the QA summary is available.
- Scope changes after G2 go through a PM proposal appended to the PRD change log and summarised for master (decision log). Nothing in this plan is edited silently once G2 passes.
