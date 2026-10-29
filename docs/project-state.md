# Project State Ledger

> Single source of truth for where the project stands. Maintained by `orchestrator`
> (progress) and `master` (gate decisions). Every agent reads this first.

## Summary

| Field              | Value                    |
|--------------------|--------------------------|
| Project            | PDF-Download-gmail — Gmail PDF Attachment Downloader |
| Jira Intake issue  | [PGD-1](https://sankumar76.atlassian.net/browse/PGD-1) (project key **PGD**) |
| Current phase      | G0 Intake                |
| Last gate passed   | G1 Discovery (CONDITIONAL GO, 2026-10-29) |
| Next gate          | G2 Product Definition    |
| Current sprint     | —                        |
| Overall health     | 🟢 Green                 |
| Last updated       | 2026-10-29 by orchestrator |

## Request (G0 Intake)

- **Problem statement:** Santhosh needs to bulk-download every PDF attachment from one Gmail account for a given date range, without manually opening emails, with predictable date-prefixed names, no overwrites, and safe read-only access.
- **Sponsor:** Santhosh / MD (delivery lead and final approver).
- **Desired outcome:** All PDFs received in an inclusive date range (in the chosen time zone) are saved as `YYYYMMDD_<name>.pdf` with deterministic `_1`, `_2` … suffixes. Re-runs save 0 duplicates. No credential ever leaks. See the acceptance criteria in requirements doc §6.2.
- **Known constraints:** Python 3.10+ (3.12 target); Google API client libraries only (no other third-party dependencies unless justified); `gmail.readonly` scope only; no database; desktop GUI that meets the CLAUDE.md §9 design standards.
- **Inputs provided:** `Gmail PDF Attachment Downloader — Requirements.md` (repo root, Oct 28, 2026), with IDs SEC-01..09, FR-01..18, NFR-01..05 and LOG-01..05; CLAUDE.md §9.
- **Intake decisions (delivery lead, 2026-10-29):**
  - **D-01** The product is a desktop **GUI app plus CLI** on one shared core. CLAUDE.md §9 supersedes "A graphical interface" being out of scope in the requirements doc.
  - **D-02** The Jira project key is **PGD**; CLAUDE.md §1a says `PDG`, which is a typo. The correction still needs to be appended to CLAUDE.md, because the orchestrator's write guard blocks that file.

## Phase Progress

| Gate | Status       | Date | Decision ref |
|------|--------------|------|--------------|
| G0 Intake               | ✅ GO | 2026-10-29 | [PGD-1 comment 10081](https://sankumar76.atlassian.net/browse/PGD-1?focusedCommentId=10081) (decision, D-01, D-02); [comment 10082](https://sankumar76.atlassian.net/browse/PGD-1?focusedCommentId=10082) (RISK-001..006). Repo record: `docs/00-governance/gate-log.md` (G0, 2026-10-29), `decision-log.md` (D-01, D-02), `risk-register.md` (RISK-001..006) |
| G1 Discovery            | ✅ CONDITIONAL GO | 2026-10-29 | `docs/00-governance/gate-log.md` (G1, attempt 1); conditions C1 (business-analyst: brief §10 risk table), C2–C4 (product-manager: audit-trail metric, quantified performance NFR per D-03, confirm GOAL-09), all due G2; risks RISK-007..009; decision D-03; [PGD-1 comment 10088](https://sankumar76.atlassian.net/browse/PGD-1?focusedCommentId=10088) (decision), [10089](https://sankumar76.atlassian.net/browse/PGD-1?focusedCommentId=10089) (risks) |
| G2 Product Definition   | ⏳ Pending | | |
| G3 Solution Design      | ⏳ Pending | | |
| G4 Backlog Ready        | ⏳ Pending | | |
| G8 Release Readiness    | ⏳ Pending | | |

## Story Board (current sprint)

| Story ID | Title | Status | Owner agent | G5 | G6 | G7 | Notes |
|----------|-------|--------|-------------|----|----|----|-------|

## Open Questions

| ID | Question | Raised by | Owner | Needed by | Status |
|----|----------|-----------|-------|-----------|--------|

## Blockers

| ID | Description | Since | Owner | Action |
|----|-------------|-------|-------|--------|
| B-01 | master cannot write `docs/00-governance/**`. The orchestrator's PreToolUse write guard (`restrict-writes.sh docs/project-state.md docs/06-reviews/`) also applies to the master subagent and blocks gate-log.md, decision-log.md and risk-register.md. G0 is recorded in Jira PGD-1 (comments 10081, 10082) only. Blocks the repo audit trail for G1–G8 (RISK-006). | 2026-10-29 | Santhosh (hook config; settings are append-only) | ✅ Resolved 2026-10-29: session relaunched as plain `claude`; master back-filled docs/00-governance/ (RISK-006 closed) |

## Tracked Items

| ID | Item | Owner | Status |
|----|------|-------|--------|
| T-01 | Append the Jira key correction (PDG → PGD) and the product-form decision to CLAUDE.md. CLAUDE.md is append-only, and the orchestrator is write-guarded from it. | Santhosh (human) | ✅ Done (key fixed in CLAUDE.md §1/§1a; working-copy change, commit pending by Santhosh) |
| T-02 | Jira workflow status categories look wrong: "Blocked" is in the *done* category and "Done" is in the *in-progress* category. JQL and reports that use `statusCategory` will mislead. | Santhosh (Jira admin) | ✅ Done (verified by master via Jira statuses; RISK-004 closed) |

## Activity Log (newest first)

| Date | Agent | Action | Artefacts |
|------|-------|--------|-----------|
| 2026-10-29 | master | G1 Discovery: **CONDITIONAL GO** (attempt 1). All mandatory checks passed (37/37 source IDs catalogued). Conditions C1–C4 due at G2. Registered RISK-007..009; logged D-03 (Q-11 performance part moves to G2) | docs/00-governance/gate-log.md, risk-register.md, decision-log.md; PGD-1 |
| 2026-10-29 | master | G0 back-fill: gate-log, decision-log (D-01, D-02) and risk-register (RISK-001..006; RISK-004/006 closed, RISK-002 reduced) written | docs/00-governance/*; PGD-1 comment 10085 |
| 2026-10-29 | orchestrator | Run resumed as plain `claude` (B-01 resolved). Branch docs/PGD-1-inception created. Briefs for master (back-fill) and business-analyst (G1) posted | PGD-1 comment 10084 |
| 2026-10-29 | orchestrator | Run paused after G0. Root cause of B-01: the session was launched with `--agent orchestrator`, so the orchestrator's frontmatter write guard applies to every subagent too; combined with each subagent's own guard, the only writable path is project-state.md. Every specialist is blocked. Pause reason posted on PGD-1 | PGD-1 |
| 2026-10-29 | master | G0 Intake: **GO** (attempt 1). Logged D-01, D-02 and RISK-001..006 on PGD-1. Governance files blocked by the write guard (B-01) | PGD-1 comments 10081, 10082; docs/project-state.md |
| 2026-10-29 | orchestrator | Preflight passed (GitHub OK; Jira OK on PGD). Created Intake issue PGD-1 and recorded intake decisions D-01 and D-02 | PGD-1, docs/project-state.md |
