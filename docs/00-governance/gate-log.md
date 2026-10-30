# Gate Log

> Append-only record of every quality-gate decision. Written by `master`.
> Format: one entry per decision, newest at the bottom, using `docs/templates/gate-record.md`.

---

## G0 – Intake — 2026-10-29

> Back-filled on 2026-10-29 from Jira [PGD-1 comment 10081](https://sankumar76.atlassian.net/browse/PGD-1?focusedCommentId=10081).
> The original decision could not be written here because of blocker B-01 (write guard), which is now resolved.
> The substance of the decision is unchanged.

- **Decision:** GO
- **Decided by:** master  ·  **Human override:** none
- **Attempt:** 1
- **Artefacts evaluated:** `docs/project-state.md` (Request section, 2026-10-29); `Gmail PDF Attachment Downloader — Requirements.md` (repo root, on `main` at commit 1021f34); `CLAUDE.md` §1, §1a, §9; Jira PGD-1 description

| # | Check | Mandatory | Result | Evidence |
|---|-------|-----------|--------|----------|
| 1 | Problem statement | ✱ | ✅ | `docs/project-state.md` Request L21; PGD-1 description; req doc §1 |
| 2 | Sponsor / decision-maker named | ✱ | ✅ | Santhosh / MD, in project-state L22 and CLAUDE.md §1 |
| 3 | Desired outcome | | ✅ | project-state L23; req doc §6.2 (9 acceptance criteria that can be checked) |
| 4 | Known constraints | | ✅ | project-state L24; req doc §1 tech stack, §2.2 SEC-01..09; CLAUDE.md §9 |
| 5 | Inputs listed | | ✅ | project-state L25; req doc tracked on `main` (commit 1021f34) |
| 6 | Input conflicts resolved (supporting) | | ✅ | Req doc §1 puts the GUI out of scope, but CLAUDE.md §9 requires one: resolved by **D-01**. Key PDG vs PGD: resolved by **D-02** |

**Conditions / remediation**
| # | Owner agent | Artefact | Required change | Due gate |
|---|-------------|----------|-----------------|----------|
| — | — | — | None. The follow-ups below are not conditions. | — |

Follow-ups (not conditions):
- Santhosh: append the D-01/D-02 notes to CLAUDE.md (T-01). *Status 2026-10-29: done. The key correction is in CLAUDE.md §1/§1a as an uncommitted working-copy change.*
- business-analyst: catalogue the SEC/FR/NFR/LOG IDs, add GUI requirements sourced to D-01, and mark req doc §1 "GUI out of scope" as superseded (G1).
- solution-architect: write a UI-framework ADR that justifies the extra dependency (G3).

**Risks registered:** RISK-001, RISK-002, RISK-003, RISK-004, RISK-005, RISK-006 (PGD-1 comment 10082)
**Rationale:** Both mandatory G0 items have evidence: the problem statement and a named sponsor. All supporting items are present. The two conflicts between inputs, GUI scope and the Jira key, were settled by delivery-lead decisions D-01 and D-02 before discovery. G0 is not in `HUMAN_APPROVAL_POINTS`, so no human approval is needed.

---

## G1 – Discovery — 2026-10-29

- **Decision:** CONDITIONAL GO
- **Decided by:** master  ·  **Human override:** none
- **Attempt:** 1
- **Artefacts evaluated:** `docs/01-discovery/project-brief.md` v0.1, `requirements-catalog.md` v0.1 and `stakeholder-map.md` v0.1 (all at commit ef16e90 on `docs/PGD-1-inception`, no later changes); source `Gmail PDF Attachment Downloader — Requirements.md` (RD); Jira PGD-1 comment 10086 (business-analyst hand-off) and 10087 (brief); `docs/00-governance/*`

| # | Check | Mandatory | Result | Evidence |
|---|-------|-----------|--------|----------|
| 1 | Goals are SMART | ✱ | ✅ | Brief §3 L25-35: GOAL-01..09 each have a metric, baseline, numeric target and a "by when". "By when" is a delivery gate, not a date, because there is no deadline (Q-01, ASSUMPTION-14). GOAL-09 is labelled PROPOSED (see C4) |
| 2 | In / out of scope stated | ✱ | ✅ | Brief §5 L49-70: in scope, out of scope, future consideration. RD §1 "GUI out of scope" is marked superseded by D-01 (L67; catalogue L19) |
| 3 | Stakeholders & personas identified | ✱ | ✅ | `stakeholder-map.md` L6-15 (7 stakeholders, influence/interest, success measure), grid L17-21, RACI L23-36; personas P-01/P-02 (brief §4, catalogue L39) |
| 4 | Requirements catalogue has IDs and sources | ✱ | ✅ | Every row in the catalogue has an ID and a Source column. Master checked by grep: the RD has 37 unique SEC/FR/NFR/LOG IDs and the catalogue has the same 37. Sampled wording of SEC-04, FR-02, FR-13, NFR-01, NFR-05 and LOG-05 matches RD L46, L91, L108, L133, L137 and L145 |
| 5 | Business rules captured | | ✅ | Catalogue L173-189: BR-001..014, each with type, source and exceptions |
| 6 | Open questions have owners | | ✅ | Catalogue L254-268: Q-01..Q-13, each with owner, needed-by and a linked assumption. None blocks G2, so there are rightly no Jira question issues (playbook §4.2) |
| 7 | Assumptions labelled | | ✅ | Catalogue L232-249: ASSUMPTION-01..16, each with impact-if-false and owner; brief §8 |
| 8 | Consistency with governance records (supporting) | | ⚠️ | Brief §10 L115-127 still shows the pre-reassessment scores: RISK-002 P=3, RISK-004 P=3, RISK-006 P=5 ("master to re-assess"). The register now has RISK-002 at 2 (reduced) and RISK-004/006 closed, and proposed risks A/B/C are now RISK-007/008/009 → C1 |
| 9 | Forward readiness for G2 (supporting) | | ⚠️ | (a) G2 requires quantified NFRs, but the RD has no performance target and Q-11 is due only at G3 (catalogue L93, L266) → C3. (b) BRQ-007 (audit trail, LOG-01..05) maps to GOAL-02, whose metric is file naming only, so no goal measures the audit trail (catalogue L32) → C2 |
| 10 | Requirement quality (supporting) | | ✅ | Vague terms were rewritten or flagged (catalogue L278: GUI-18 has a verifiable proxy; the NFR-05 reading is labelled ASSUMPTION-16). Unsourced items are labelled as BA proposals (GUI-19, UR-013, GOAL-09, all MoSCoW per ASSUMPTION-05) |

**Conditions / remediation**
| # | Owner agent | Artefact | Required change | Due gate |
|---|-------------|----------|-----------------|----------|
| C1 | business-analyst | `docs/01-discovery/project-brief.md` §10 | Align the risk table with `risk-register.md`: RISK-002 = 2 (reduced, open until the CLAUDE.md change is committed), RISK-004 closed, RISK-006 closed, and replace PROPOSED-RISK-A/B/C with RISK-007/008/009 and their scores | G2 |
| C2 | product-manager | `docs/02-product/prd.md` (success metrics) | Give BRQ-007 / LOG-01..05 a measurable success metric (e.g. 100 % of runs, including cancelled and failed runs, produce a log and a CSV, with one row per candidate attachment and a valid LOG-03 status), or trace LOG-01..05 to a goal whose metric covers them | G2 |
| C3 | product-manager (Santhosh consulted) | `docs/02-product/prd.md` (NFRs) | Answer the performance part of Q-11 at G2, not G3 (D-03). State a quantified performance NFR (e.g. elapsed time per 1,000 matched messages under the Gmail quota) or record "no performance target" as an explicit Won't with sponsor agreement. Keep NFR-01..05 numeric | G2 |
| C4 | product-manager (Santhosh consulted) | `docs/02-product/prd.md` (success metrics) | Confirm GOAL-09 (dry run in 5 minutes or less from the GUI) with the sponsor and keep it as a success metric, or drop it or mark it Could. It cannot stay PROPOSED in the PRD | G2 |

Follow-ups (not conditions):
- product-manager: decide Q-05, Q-06, Q-09, Q-13 and confirm MoSCoW (ASSUMPTION-05). Q-06 also mitigates RISK-008.
- solution-architect: run a spike on Q-07 (RISK-007); decide Q-08 and Q-11 (memory reading); write the UI-framework ADR (RISK-001).
- Santhosh: answer Q-01, Q-02, Q-04, Q-10 (Q-10 also mitigates RISK-009) before G2 is decided where possible; commit the CLAUDE.md working-copy change (closes RISK-002).

**Risks registered:** RISK-007 (search-recall gap), RISK-008 (manifest loss → duplicates), RISK-009 (downloaded PDFs and logs unprotected on disk). Re-checked: RISK-002 stays reduced and open (CLAUDE.md is still modified and uncommitted at G1); RISK-001, 003 and 005 are unchanged.
**Rationale:** All four mandatory G1 items have file and line evidence. Grep confirmed that all 37 source IDs are catalogued with their original IDs and sources, and sampled wording is faithful to the RD. The conditions are supporting gaps: the brief's risk table is stale, and two things would make the G2 mandatory checks fail if left alone (no quantified performance NFR, no metric for the audit trail). Each condition has an owner and is due at G2. G1 is not in `HUMAN_APPROVAL_POINTS`, so no human approval is needed.


---

## G2 – Product Definition — 2026-10-29

- **Decision:** CONDITIONAL GO
- **Decided by:** master  ·  **Human override:** none
- **Attempt:** 1
- **Artefacts evaluated:** `docs/02-product/prd.md` v0.1 and `release-plan.md` v0.1 (commit 28589b4 on `docs/PGD-1-inception`, draft PR #1); `docs/01-discovery/project-brief.md` and `requirements-catalog.md` **as committed at 3c3366f**. The business-analyst's uncommitted working-copy edits to `docs/01-discovery/*` were not evaluated. Also: `docs/00-governance/*`, `docs/standards/coding-standards.md`, `definition-of-done.md`, RD (`Gmail PDF Attachment Downloader — Requirements.md`), Jira PGD-1 comments 10090–10093 (briefs, BA C1 hand-off 10091, PM hand-off 10092)

| # | Check | Mandatory | Result | Evidence |
|---|-------|-----------|--------|----------|
| 1 | Every FR traces to a brief goal | ✱ | ✅ | PRD §4: Goal column filled for 66/66 FRs (master scripted check; FR-001..066 all present, no gaps or duplicates). The §11 matrix covers all 66 FRs (master checked the union). GOAL-01..09 keep the brief §3 targets. FR-039..042 and FR-046 trace only to GOAL-10, which the PRD defines as G1 C2 allowed. They also trace through BRQ-007 to brief GOAL-02 (catalogue BRQ-007 row). The brief does not mirror GOAL-10 yet → C5 |
| 2 | NFRs quantified | ✱ | ✅ | PRD §5 NFR-001..025: 24 have numeric targets, and NFR-025 (availability) is an explicit Won't. The performance targets NFR-001..004 are numeric, which satisfies D-03 (e.g. NFR-001: 1,000 messages ≤ 15 min at 300 ms per call). They are labelled PA-01 and await sponsor confirmation (RISK-011, RISK-013) |
| 3 | MVP scope explicit with MoSCoW | ✱ | ✅ | PRD §6.1: MVP = R1 + R2. Master recount: 53 Must (R1 37 + R2 16), 11 Should, 2 Could = 66. §6.2 lists the Won'ts with the consequence of each. §15.2 lists the MoSCoW changes from the catalogue |
| 4 | Success metrics defined | ✱ | ✅ | PRD §3: GOAL-01..10 each have a metric, type, baseline, target and measurement method. Leading indicators are at L61 |
| 5 | Epics outlined | | ✅ | PRD §7: EPIC-01..10 with FRs, release, size and dependencies. Every FR has an owning epic (L354). Points add up to R1 99 + R2 42 = 141 |
| 6 | Release plan present | | ✅ | `release-plan.md` §1–§7: R1/R2/R3/backlog, waves W1–W6 with exit checks, entry and exit criteria, critical path |
| 7 | No contradiction with the brief | | ⚠️ | No conflict of substance. The PRD refines the brief: GOAL-07 excludes timestamps, GOAL-01 adds the PA-04 real-mailbox check, and PD-05 resolves RD "writes nothing" vs AC-09. Gaps: (a) GOAL-10 is not in brief §3 yet; (b) brief §12 has Q-01, Q-02 and Q-10 needed by G2 (owner Santhosh), but PRD §12 moves them to G8 under the labelled assumptions PA-08 and PA-09. The brief's needed-by dates are stale → C5 |
| 8 | G1 C1 closed (brief §10 = register) | | ✅ | Brief §10 at 3c3366f against `risk-register.md`: all nine rows match on P, I, score and status. RISK-002 = 1×2 reduced and open; RISK-004 and 006 closed; RISK-007/008/009 = 12/9/8 with the register owners. PGD-1 c.10091 |
| 9 | G1 C2 closed (audit-trail metric) | | ✅ | PRD §3 GOAL-10 (L59): four checkable sub-metrics, 100 % of runs, 0 discrepancies, hard-kill tolerance ≤ 1. NFR-005; FR-039..043 and FR-046 |
| 10 | G1 C3 closed (performance NFR) | | ✅ | NFR-001..004 are numeric (PD-07), not a Won't. The sponsor was not consulted at G2, and confirmation is deferred to G8 (PRD §14.3 item 1). That is allowed because the condition required either numbers or a Won't agreed with the sponsor. The residual exposure is RISK-011 |
| 11 | G1 C4 closed (GOAL-09) | | ✅ | GOAL-09 is adopted as a Should metric (PD-08) and is no longer PROPOSED. Master verified that every FR tracing to GOAL-09 (FR-006, 044, 047, 060, 065) also traces to another goal |
| 12 | Consistency with standards | | ⚠️ | NFR-022 sets line coverage of `gmail_pdf` at ≥ 85 %. `coding-standards.md` §6 L46 sets 100 % on changed code, and `definition-of-done.md` L9 sets ≥ 90 % on changed code. The PRD does not say which rule governs at G5/G6 → C6 |
| 13 | Scope reductions against the source are logged | | ✅ | RD L65 makes `config.yaml`/`.env` optional. The PRD sets CFG-11 to Won't (§6.2, PD-01, §14.3 item 4), and the GUI-03 paths move to R3. Logged as D-04 and D-13. Every RD ID maps in §15.1 |
| 14 | MoSCoW balance | | ⚠️ | Must is 93 % of MVP effort (PRD §8 L289). The PM recorded this as deviation PD-09 with five mitigations. Accepted as RISK-010 (not a blocker: the Musts are the sponsor's own acceptance contract) |

**Conditions / remediation**
| # | Owner agent | Artefact | Required change | Due gate |
|---|-------------|----------|-----------------|----------|
| C5 | business-analyst | `docs/01-discovery/project-brief.md` §3 and §12; `requirements-catalog.md` | (a) Add GOAL-10 Auditability with the PRD §3 metric and map BRQ-007 to GOAL-02 and GOAL-10. (b) Mark Q-05, Q-06, Q-09, Q-13 and the performance part of Q-11 resolved, citing PD-01..04 and PD-07. (c) Move Q-01, Q-02 and Q-10 to needed-by G8, linked to PA-09 and PA-08 (or have Santhosh answer them). Then commit. This work was already in progress at decision time (PGD-1 c.10093) | G3 |
| C6 | product-manager (with solution-architect test strategy) | `docs/02-product/prd.md` NFR-022 | Make NFR-022 consistent with `coding-standards.md` §6 and the DoD. Either state that ≥ 85 % is a whole-package floor and that per-PR changed-code coverage follows the coding standards, or propose a standards change through master. Editorial fix at the same time: §0 and §15.1 say "FR-039..044" for C2 and BRQ-007, but FR-044 (dry run) is outside GOAL-10. Correct this to FR-039..043, 046 or state the reason | G3 |

Follow-ups (not conditions):
- orchestrator: post the PRD §14.3 sponsor-confirmation list on PGD-1 now as a **non-blocking FYI** @-mentioning Santhosh. The point is to catch objections before the build, not only at G8 (mitigates RISK-011 and RISK-013). This does not add a human approval point.
- solution-architect (G3): PQ-01..03; Q-07 spike against NFR-001/002 (RISK-007); UI-framework ADR with a spike against FR-054..060 (RISK-012); manifest integrity (RISK-008); core API with progress events and cancellation.
- Santhosh: commit the CLAUDE.md working-copy change. It is still modified at G2, so RISK-002 stays open.

**Risks registered:** RISK-010 (Must-heavy MVP), RISK-011 (performance targets not validated), RISK-012 (GUI framework vs §9), RISK-013 (sponsor confirms ten product decisions only at G8). Re-assessed: RISK-001 (trigger avoided by the R1/R2 split), RISK-007 (residual conditionally accepted, PD-06), RISK-008 (behaviour decided, PD-02). Scores unchanged. RISK-002 stays open.
**Rationale:** All four mandatory G2 items have line-level evidence. Master counted the FRs and checked the goal traceability for all 66. All G1 conditions C1–C4 are closed. The two conditions are consistency gaps outside the PRD's mandatory content: the brief does not yet mirror GOAL-10, and the coverage NFR is ambiguous against the standards. Neither puts users, data or correctness at risk before G3, so each has an owner and is due at G3. G2 is not in `HUMAN_APPROVAL_POINTS`, so no human approval is needed.

---

## G3 – Solution Design — 2026-10-29

- **Decision:** CONDITIONAL GO
- **Decided by:** master  ·  **Human override:** none
- **Attempt:** 1
- **Artefacts evaluated:** `docs/04-architecture/architecture.md` v0.1, `adr/ADR-001..007`, `test-strategy.md` v0.1 (commit 75b7e47); `docs/03-ux/ux-spec.md` v0.2, `wireframes/main-window.md`, `wireframes/dialogs.md` (commit d200c27); `docs/02-product/prd.md` v0.3 (f1ba385; v0.2 = 27428e0); `docs/01-discovery/project-brief.md` and `requirements-catalog.md` v0.2 (5ac4b4a); `docs/standards/coding-standards.md`, `definition-of-done.md`; `docs/00-governance/*`; Jira PGD-1 comments 10095–10105; GitHub issues #2–#5 (draft PR #1, branch `docs/PGD-1-inception`)

| # | Check | Mandatory | Result | Evidence |
|---|-------|-----------|--------|----------|
| 1 | Architecture addresses every FR and NFR (coverage table) | ✱ | ✅ | architecture §12 (FR map) and §7 (NFR tactics). Master checked by script: FR-001..066 all covered (ranges expanded, 0 missing, 0 extra); NFR-001..025 have one row each (NFR-025 is a Won't). PRD v0.3 recount: 66 FRs, 25 NFRs. Each NFR row names a tactic, components and a verification method |
| 2 | ADRs for significant decisions, alternatives considered | ✱ | ✅ | ADR-001..007 each weigh 3 or more options with pros and cons (GUI framework, dependencies and time zones, token storage and redaction, manifest and safe writes, packaging, execution model and dry run, search recall). ADR-001 is **Proposed** until spike S-02 (issue #3); R1 does not depend on it → C11 |
| 3 | Security & data-protection approach defined | ✱ | ✅ | architecture §2 trust boundaries TB-1..6; §8.1–8.8 (scope constant, read-only gateway allow-list, one redaction path, STRIDE per boundary, input validation incl. path traversal, CSV/log/rich-text injection, MIME limits, supply chain); §5.3 classification and retention; ADR-003; test-strategy §6 sentinel matrix. At-rest encryption is explicitly not provided (TD-01, issue #5) |
| 4 | UX spec covers every user-facing FR with all states | ✱ | ✅ | ux-spec §9 maps all 66 FRs to a screen, a state or "no UI". §6.0 has the run state machine and a 14-state interaction matrix. SCR-01..06 each list Default, Loading, Empty, Partial, Error, Success, Disabled and Permission-denied states. DLG-01..08 are in `wireframes/dialogs.md`; CLI interaction is §12 |
| 5 | Accessibility target stated | ✱ | ✅ | ux-spec §8: WCAG 2.2 AA as reference (formal conformance a Won't, D-07); keyboard Must (§8.1); focus (§8.2); contrast ≥ 4.5:1 / 3:1 with computed values (§7.3); screen reader Should, R3 (§8.5); NFR-017..019 |
| 6 | Technical risks logged | | ✅ | architecture §14 AR-01..06, TD-01..02; GitHub #2 (S-01), #3 (S-02), #4 (AR-04), #5 (TD-01); registered here as RISK-014..019 |
| 7 | Test strategy present | | ✅ | `test-strategy.md` §1–§11: pyramid, Gmail doubles, GUI approach, coverage gates, security, performance, reliability and audit, CI pipeline |
| 8 | UX ↔ architecture conflicts resolved | | ⚠️ | architecture §17.1 resolves UA-01..06, UQ-02/06/10/12, PD-12 and PD-15. Still open: (a) UX-I-01..06 are unacknowledged (QSS cannot express the 120 ms motion token or line heights; scrim; env-var help line; tabular figures), and ux-spec §7.2/§8.3 still specify 120 ms transitions. (b) Count refresh is "≤ 4 per second" in ux-spec L168/L270 but "≤ 10 Hz" in architecture §4.3 and the §7 NFR-004 row. (c) UJ-01/UA-05 says a wrong client file is caught only when Google rejects it; ADR-003 §4 now catches it locally. (d) The architecture header and §17 cite ux-spec v0.1 (7159423), but v0.2 (d200c27) is the reviewed version. → C9, C10 |
| 9 | CLAUDE.md §9 supported (supporting) | | ⚠️ | Design: ADR-001 token contract (`theme/tokens.py` as single source, generated QSS, `AppButton` only, Qt 6 high-DPI, clamp-and-scroll for PD-12); guard tests in test-strategy §4 items 4–6; ux-spec §7 (four type roles, one spacing scale, one palette, one button). Proof outstanding: S-02 (focus-ring offset, per-monitor re-layout and live announcements are unverified) → C11 (RISK-012) |
| 10 | G2 C5 closed (discovery aligned) | | ⚠️ | 5ac4b4a: (a) ✅ GOAL-10 is in brief §3 L36, and BRQ-007 maps to GOAL-02 and GOAL-10 (catalogue L32). (b) ✅ Q-05/06/09/13 and the Q-11 performance part are resolved in brief §12 and the catalogue. (c) **Not done:** Needed-by is still G2 for Q-01/02/10. Brief L144/145/153 only add "(PRD: G8)"; catalogue L256/257/265 are unchanged and have no PA link → carried into C7 |
| 11 | G2 C6 closed (NFR-022, FR range) | | ✅ | PRD v0.2 (27428e0): NFR-022 L210 requires 100 % changed-code coverage per PR (coding-standards §6 governs; the DoD's 90 % is implied) and keeps 85 % only as a whole-package floor (PD-10). §0 L19 and §14.2 L414 say FR-039..043 and 046; §15.1 L439 maps BRQ-007 to FR-039..043 |
| 12 | Consistency with standards | | ✅ | The two conflicts the SA raised were ruled in this gate: pragma exceptions vs §6 (D-25), and §10 `os.replace` vs "never overwrite" (D-26). Coverage gates in test-strategy §5 match NFR-022/PD-10 (D-24). The coding-standards §7 web budgets are ruled not applicable (D-26) |
| 13 | Architecture ↔ PRD consistency | | ⚠️ | (a) AR-03: architecture §7 L455 judges NFR-009's "growth ≤ 10 %" unattainable with the FR-014 sort; the PRD is unchanged. (b) AQ-03: FR-032's acceptance test says "no files written" (PRD L119), but architecture §6.5 L371 writes a run log and a header-only CSV; GOAL-10's outcome list (PRD L61) does not name the unreadable-manifest case. (c) AQ-04 and AA-07/08/11 are unconfirmed. (d) PQ-01..03 are still open in PRD §12 although ADR-006, §6.5 and §8.2 answer them. → C8 |
| 14 | Open questions past their needed-by gate | | ⚠️ | Q-04 (Santhosh, needed by G3; brief L147, catalogue L259, PRD L368) is unanswered. It does not block G3: the architecture works for both consent-screen states (§8.1, FR-003, RISK-003). Rescheduled to G8 by D-28 → C7, C8 |
| 15 | Artefacts committed and traceable | | ✅ | Architecture, ADRs and test strategy are committed in 75b7e47 and UX v0.2 in d200c27. The SA and UX hand-offs (PGD-1 c.10103/10104) say "uncommitted", but the files were committed afterwards. Sampled traces, no broken link: GOAL-04 → FR-028 → arch §6.3, ADR-004 → test-strategy §6 "No overwrite" and §8 NFR-007 loop; GOAL-10 → FR-040 → `infra.audit` (§4.1) → test-strategy §8 reconciliation; FR-060 → ux-spec §8.1 → ADR-001 checklist 5/6a → test-strategy §4 item 2 |

**Conditions / remediation**
| # | Owner agent | Artefact | Required change | Due gate |
|---|-------------|----------|-----------------|----------|
| C7 | business-analyst | `docs/01-discovery/project-brief.md` §12; `requirements-catalog.md` Q and DR tables | (i) Finish G2 C5(c): set Needed-by of Q-01, Q-02 and Q-10 to **G8** in both files, linked to ASSUMPTION-14 (Q-01), PA-09 (Q-02) and PA-08 (Q-10). (ii) Set Q-04 Needed-by to **G8** per D-28 (working assumption ASSUMPTION-04, RISK-003). (iii) Mark these resolved and cite the source: Q-03 (ADR-005), Q-07 (ADR-007; residual measured by S-01, issue #2), Q-08 (ADR-002: no YAML; `tzdata` + `tzlocal`), Q-11 remainder (ADR-006, architecture §7: ASSUMPTION-16 confirmed). (iv) DR-005: change the classification from Internal to **Confidential** and add From, Subject, `internal_date_ms` and per-message records to its content (architecture §5.3). Commit | G4 |
| C8 | product-manager | `docs/02-product/prd.md` v0.4 | (i) Decide AR-03: reword NFR-009's growth clause or keep it and state why. The SA proposes "≤ 2 KB per candidate message and per manifest entry between the 500- and 10,000-message fixtures; no attachment bytes retained across messages". The W1 benchmark confirms the number (RISK-014; extends PA-01). (ii) Decide AQ-03 and make FR-032's acceptance test and GOAL-10's outcome list agree with the decision. Master recommends the SA reading: a run log and a header-only CSV are written, no PDF is written and the manifest is untouched, so GOAL-10 holds for this outcome. (iii) Confirm or reject AQ-04 (cancel exits 1, as in D-21), AA-07 (CSV in UTF-8 with BOM), AA-08 (log and CSV timestamps in the run's zone) and AA-11 (full `--query` text only at DEBUG). (iv) In §12, mark PQ-01 (D-22), PQ-02 (D-21), PQ-03 (D-23), Q-03, Q-07, Q-08 and the Q-11 remainder resolved; move Q-04 to needed-by G8 (D-28). Add D-21's numeric mapping to §14.3 item 11, and add AQ-02 (D-20) to §14.3 | G4 |
| C9 | ux-expert | `docs/03-ux/ux-spec.md` v0.3 | Accept or counter-propose UX-I-01..06 and update the spec: §7.2/§8.3 `motion.fast` = 0 in R2 (token kept); §7.1 line heights become guidance checked on screenshots; scrim fallback (UX-I-03); env-var sharing line in DLG-07 (UX-I-04); tabular-figure fallback (UX-I-06). Agree one count-refresh rule with the architecture, for example "the view refreshes ≤ 4 times a second from the ≤ 10 Hz event stream". Update the UJ-01 recovery and UA-05 to the local wrong-client-file check (ADR-003 §4, same message text) | G4 |
| C10 | solution-architect | `docs/04-architecture/architecture.md` v0.2; `test-strategy.md` v0.2 | (i) The header, Inputs and §17 title cite ux-spec **v0.2** (d200c27) and record the C9 outcome; §7 and §12 cite PRD v0.3. (ii) Align with D-25 and D-26: remove pragma exception (c) from test-strategy §5. The §10.2 write-path rule must say that streamed user-visible files (run log, CSV) are opened with exclusive create (`"x"` mode) and never replaced, that PDFs use `move_no_clobber`, and that `os.replace` is used only for the manifest snapshot and the token. (iii) Close the AQ-01 and AQ-05 rows and link AQ-03/04 to C8 | G4 |
| C11 | solution-architect (developer runs the spike) | ADR-001; GitHub #3; sprint plans | Run S-02 and record the report in ADR-001. ADR-001 then becomes **Accepted**, or is re-opened with the fallback. **No EPIC-09 or EPIC-10 (R2 GUI) story may be marked Ready (DoR) until ADR-001 is Accepted.** scrum-master and product-owner apply this rule at every G4 | G4 of the first sprint that contains an EPIC-09/10 story (no later than wave W4) |

Follow-ups (not conditions):
- orchestrator: post a second **non-blocking FYI** to Santhosh on PGD-1 now. Cover AQ-02 (shadcn/ui is adopted as a design language in a Qt desktop UI, not as React components, although his global instructions name shadcn), Q-04 (consent-screen status) and the CLI exit-code mapping in D-21. This catches objections before R2 is built (RISK-019, RISK-013).
- Delivery lead (Santhosh): (a) Commit the CLAUDE.md working-copy change; RISK-002 stays open until then. (b) FYI from the SA: the CLAUDE.md §1 build command installs runtime pins only, but developers and CI also need `pip install -r requirements-dev.txt`. Appending a note is optional and append-only (CLAUDE.md §8). It is not a condition because the README and CI workflow carry the command anyway. (c) Apply the D-25/D-26 wording to `docs/standards/coding-standards.md` §6, §7 and §10, which is outside master's write area. Until then, the decision-log entries govern reviews.
- developer (W1 stories): running `pip-audit` on the first pinned `requirements.txt` is an acceptance criterion, because no CVE scan was possible at G3. Verify AA-01, AA-03, AA-04, AA-06 and AA-09 in the stories that touch them.
- qa-engineer: as co-owner of PQ-02, confirm the D-21 exit-code mapping in the test plan.

**Risks registered:** RISK-014 (AR-03, NFR-009 growth clause), RISK-015 (AR-04, FAT fallback race), RISK-016 (AR-05, stale attachmentId), RISK-017 (AR-06, Windows long paths), RISK-018 (TD-01, plaintext token), RISK-019 (AQ-02, sponsor rejects the design-language reading of shadcn). TD-02 is not a risk; it is the accepted side effect of the CSV-injection control (D-27). Re-assessed: RISK-001 P 3→2 (ADR-001 adds one UI dependency; trigger not fired); RISK-007 P 3→2 (recall sweep on by default, ADR-007; residual measured by S-01); RISK-008 P 3→2 (ADR-004 journal and `.bak` plus PD-11 remove the crash and advice causes; user deletion or a folder change remains); RISK-012 unchanged at 6, now controlled by C11; RISK-005, 009, 011 and 013 unchanged; RISK-002 stays open.
**Rationale:** All five mandatory G3 items have file-level evidence. Master checked FR and NFR coverage by script (66/66 and 25/25); seven ADRs weigh alternatives; the security design covers every trust boundary; the UX spec maps all 66 FRs with full state sets; and an accessibility target is stated. The open items are consistency gaps between artefacts (UX-I-01..06, AQ-03, AR-03, stale needed-by dates) and the unproven GUI spike. None of them puts users, data or correctness at risk before stories are written, so each has an owner and a due gate, and C11 keeps every R2 GUI story out of a sprint until ADR-001 is proven. G3 is not in `HUMAN_APPROVAL_POINTS`, so no human approval is needed.

---

## G4 – Backlog Ready — Sprint 01 — 2026-10-29

- **Decision:** CONDITIONAL GO
- **Decided by:** master  ·  **Human override:** none
- **Attempt:** 1
- **Artefacts evaluated:** `docs/05-backlog/epics/EPIC-01..10` and `backlog.md` (fb39980); `consistency-report.md` incl. "Sprint-01 DoR validation" (fb39980 + 8d4d01e); `sprint-01-plan.md` (d1f1358, 385ecb3); Jira Epics PGD-2..11, Stories PGD-12..18 (status "Ready for Dev", labels `sprint-01`, `points-N`), Sub-tasks PGD-19..62 (44, counted by JQL), Blocks links; PGD-12, PGD-13 and PGD-15 read in full (description, ACs, parent, sub-tasks, links); PGD-1 hand-offs c.10117 (SA), 10119/10131 (PO), 10121/10122/10133 (SM), brief c.10134. G3 condition evidence: `project-brief.md` v0.3 and `requirements-catalog.md` (5dc3289, 6ea45af); `prd.md` v0.4 and `release-plan.md` v0.2 (5dc3289); `ux-spec.md` v0.3 (4f1536f); `architecture.md` v0.2, `test-strategy.md` v0.2, ADR-001 and ADR-004 (4892c8c); `docs/standards/definition-of-ready.md`; decision-log D-29..D-34. Branch `docs/PGD-1-inception` at 385ecb3 (draft PR #1)

| # | Check | Mandatory | Result | Evidence |
|---|-------|-----------|--------|----------|
| 1 | PO consistency report shows no Critical issues | ✱ | ✅ | consistency-report §1 L13 and L173: 0 Critical, 2 Major, 11 Minor. CC-01 (Major) is resolved by the PO: the enablers STORY-02.01/02.08 are hosted in EPIC-02 and sized in sprint-01-plan L15–18. CC-02 (Major) is open but holds only STORY-02.09, which is not in sprint 01 (plan L43) → C12 |
| 2 | Every sprint-1 story meets the DoR 100 % | ✱ | ✅ | PO verdicts READY ×7 (consistency-report L141–151; Jira comments 10124–10130). Master read PGD-12, PGD-13 and PGD-15 in full against `definition-of-ready.md`: story form with persona; FR/NFR trace and parent epic; Must priority; BR-IDs where they apply (PGD-15 BR-002/014; PGD-13 states that none applies and cites SEC-06); 9, 8 and 10 ACs with IDs in Given/When/Then, with negative, boundary and NFR paths (e.g. PGD-13 AC-3 "0 occurrences", PGD-15 AC-3 DST, AC-7 retry); Dev Context names architecture sections, ADRs and exact files; dependencies are Blocks links to in-sprint stories; open items A-1..A-6 are decided (plan L86–95); UX = CLI, ux-spec §12 (no GUI states apply); estimates and 10/7/9 sub-tasks. Remaining four stories: PO checklist verdicts accepted, and the sub-task count of 44 was confirmed by JQL |
| 3 | Stories trace to FRs and epics | ✱ | ✅ | Jira `parent`: PGD-12/15 → PGD-3 (EPIC-02), PGD-13 → PGD-2 (EPIC-01). Sprint coverage table (plan L49–59): FR-004/005/008/009/012/015/016/019 and NFR-006/012/013/014/015/020/022/023/024. Enabler PGD-12 carries no FR by design and traces to NFRs, which the DoR allows ("FR/NFR ID"). Trace sample, no broken link: GOAL-05 → FR-005 (PRD L79) → EPIC-01 STORY-01.01 (epic file L44) → PGD-13 AC-1..8 → `tests/unit/test_redaction.py`, `test_sentinel_matrix.py`; GOAL-01 → FR-012 (PRD L90) → EPIC-02 STORY-02.02 (L45) → PGD-15 AC-2 → `tests/unit/test_planner.py` |
| 4 | Dependencies sequenced | | ✅ | Blocks links read in Jira: PGD-12 → 13, 14, 15; PGD-13 → 15, 16; PGD-15 → 16, 17, 18. The critical path 02.01 → 01.01 → 02.02 → 02.03 (24 points) is in plan L32. Redaction comes before any printing or logging story (RISK-005). CC-06 sequencing is applied in the backlog order |
| 5 | Sprint goal stated | | ✅ | sprint-01-plan L6, with a goal-critical set and a droppable tier (L33) |
| 6 | Capacity plausible | | ✅ | 29 points committed against an assumed 30 (L7, L31). No velocity exists (D-33), so the plan commits a conservative first cut below the full W1 set (backlog L54), names split seams for both 8-point stories, and puts the stretch story PGD-18 behind G5 of 02.02. Accepted as an explicit assumption; it is replaced by measured velocity after the sprint (RISK-010) |
| 7 | G3 C7 closed (business-analyst) | | ✅ | (i) Q-01/Q-02 are now **answered** (D-33; brief L147–148, catalogue L257–258), which supersedes the needed-by move; Q-10 → **G8** (brief L156, catalogue L266). (ii) Q-04 → **G8 (D-28)** (brief L150, catalogue L260). (iii) Q-03 (ADR-005), Q-07 (ADR-007, S-01 #2), Q-08 (ADR-002) and the Q-11 remainder (ADR-006, arch §7) are resolved with the source cited (brief L149/153/154/157; catalogue L259/263/264/267). (iv) DR-005 is **Confidential** with From, Subject, `internal_date_ms` and per-message records (catalogue L200). Also: GOAL-11 is mirrored (brief L38, 6ea45af) and ASSUMPTION-17 is added. **Closed** |
| 8 | G3 C8 closed (product-manager) | | ✅ | PRD v0.4: (i) PD-17 rewords NFR-009 to ≤ 2 KB per candidate message and per manifest entry (L200, L416). (ii) PD-18: FR-032 acceptance test (L122) and the GOAL-10 outcome list (L63) agree: run log and header-only CSV, no PDF, manifest untouched; this is master's recommended reading. (iii) PD-19 confirms AQ-04, AA-07, AA-08 and AA-11 (L418). (iv) §12 marks PQ-01/02/03, Q-03/07/08 and the Q-11 remainder resolved (L372–381); Q-04 → G8 (L373); the D-21 mapping is in §14.3 item 11 (L439). AQ-02 is withdrawn under D-29, so it is correctly **not** added to §14.3 (L384). NFR-022 is 80 %/80 % per D-30 (L213). Release plan v0.2 is aligned (5dc3289). **Closed** |
| 9 | G3 C9 closed (ux-expert) | | ✅ | ux-spec v0.3 §0.1 (L26–39): UX-I-01..06 all accepted; `motion.fast` = 0 in R2 (L32, L397); line height is guidance checked on G7 screenshots (L33, L315); scrim fallback (L34, L299, L340); the env-var sharing line in DLG-07 (L35); tabular-figure fallback (L37). One count-refresh rule **R-COUNT** (worker ≤ 10 Hz, redraw ≤ 4 times a second; L39, L288). UJ-01/UA-05 use the local wrong-client-file check (L64, L484). **Closed**. Residual Minor CC-07 (spec not re-checked against PRD v0.4 PD-18 wording) → C13 |
| 10 | G3 C10 closed (solution-architect) | | ✅ | (i) The architecture header and Inputs cite ux-spec v0.3 and PRD v0.4, naming v0.2/v0.3 as the versions reviewed at G3 (arch L8–9); §7 (L427), §12 (L619) and §17 (L756, L791) cite current versions; R-COUNT is adopted in §4.3 L183, L407 and the NFR-004 row L432. (ii) Measured against the **current** rulings, which supersede the D-25/D-26 wording in C10: test-strategy §5 has the 80 %/80 % gates (L56–58, D-30) and **no pragma exception** (L63, D-31). The write-path rule in arch §10.2 L588–591 and §5.2 L260–261 says the run log and CSV are opened with exclusive create `"x"` and never replaced, PDFs use `move_no_clobber` and never `os.replace`, and `os.replace` is used only for the manifest snapshot and the token (D-32). The ADR-004 standards note (L55) is aligned. (iii) AQ-01 and AQ-05 are Closed; AQ-03/04 are closed by C8 (arch L718–722). NFR-009 row is aligned to PD-17 (L437, L457). **Closed** |
| 11 | G3 C11 respected (R2 GUI gate) | | ✅ | No EPIC-09/10 story exists in Jira (JQL: stories are PGD-12..18 only). EPIC-09/10 files carry the gate banner (EPIC-09 L3, L13, L41). ADR-001 is still **Proposed** (ADR-001 L5). PGD-12 AC-5 explicitly keeps PySide6 out of the allow-list. C11 stays **open by design** and is carried forward |
| 12 | Open Major findings with owners | | ⚠️ | CC-02: the ADR-007 sweep cost gate (ratio 0.8) does not protect NFR-002 (dry run ≤ 480 s → ratio ≤ 0.6). Owners are the SA (restate the gate) and qa-engineer (benchmark case). Tracked as IMP-01 (plan L112). No sprint-01 effect → C12 |
| 13 | Cross-artefact drift (Minor) | | ⚠️ | Open Minor items: CC-03, 04, 05 (PM), CC-07, 11 (UX), CC-10 (UX + SA), CC-12 (SA). Master found more stale text: the PGD-12/13/15 descriptions say "Status: Draft" (PGD-12 also says "Awaiting product-owner DoR validation") while Jira shows Ready for Dev; `backlog.md` L10 says "Stories: None created yet"; the PRD v0.4 header still cites "Source brief v0.1"; and ux-spec v0.3 Inputs cite PRD v0.3 (part of CC-07). The Jira status field is authoritative, so none of this misleads a developer in sprint 01 → C13, C14 |
| 14 | Integration evidence (Jira/GitHub) | | ✅ | Every hand-off and brief is on PGD-1 (c.10117–10134). Labels `ai-delivery`, `aiid-*` and `agent-*` are on every epic and story. The story-points field is not configured, so `points-N` labels are used; the sprint field cannot be set by tool, so a `sprint-01` label is used (playbook §4.4). Accepted under D-39. Stories live in Jira only (CLAUDE.md §7.1), so no story markdown is expected |

**G3 condition status:** C7 ✅ closed · C8 ✅ closed · C9 ✅ closed · C10 ✅ closed · C11 ⏳ open by design (carried forward).

**Conditions / remediation**
| # | Owner agent | Artefact | Required change | Due gate |
|---|-------------|----------|-----------------|----------|
| C11 (carried) | solution-architect (developer runs the spike) | ADR-001; GitHub #3; sprint plans | Unchanged from G3: run S-02, record it in ADR-001 and make it **Accepted** (or re-open it with the fallback). No EPIC-09/EPIC-10 story or STORY-08.03 may be marked Ready until then; product-owner and scrum-master apply this at every G4 | G4 of the first sprint that contains an EPIC-09/10 story (no later than wave W4) |
| C12 | solution-architect (with qa-engineer) | `docs/04-architecture/adr/ADR-007-*.md`; test-plan benchmark case | CC-02: restate the ADR-007 recall-sweep cost gate as the stricter of the NFR-001 and NFR-002 bounds (ratio ≤ 0.6 at the PRD figures), or state why dry runs are exempt and get the PM to agree the NFR-002 reading. qa-engineer adds the 0.6 benchmark case. STORY-02.08/02.09 carry the corrected bound as an AC until the ADR changes | G4 of the sprint that first contains STORY-02.09 (before it is Ready; planned W2/sprint 03) |
| C13 | product-manager (CC-03, 04, 05; PRD header "Source brief v0.3"); ux-expert (CC-07, CC-11; CC-10 jointly); solution-architect (CC-10 jointly, CC-12) | `prd.md`, `release-plan.md`; `ux-spec.md` §0/§6.B/§12; `architecture.md` §4.1, §6.5 | Close the Minor consistency items in the report: remove stale spike wording (CC-03); fix FR-061's owner epic (CC-04); itemise the R2 surfaces of R1 FRs and the README GUI part in PRD §7 (CC-05); re-check the UX spec against PRD v0.4 PD-18/19 (CC-07); add the A-3 unknown-zone line (CC-11); agree one unexpected-failure first line (CC-10); confirm the token-write location and the `redaction.py` → `domain.messages` import (CC-12) | G4 of sprint 02 (CC-07 in any case before an R2 DLG-03/SCR-06 story is Ready) |
| C14 | scrum-master (story descriptions), product-owner (`backlog.md`) | Jira PGD-12..18 descriptions; `docs/05-backlog/backlog.md` | Remove or refresh the stale "Status: Draft" / "Awaiting product-owner DoR validation" lines in the story descriptions (Jira status is the record), and update `backlog.md` L10 to list the sprint-01 stories. In future, keep status out of description text | G4 of sprint 02 |

Follow-ups (not conditions):
- orchestrator: G4 is CONDITIONAL GO. Under `MERGE_POLICY = docs-auto` and playbook §5.1, mark draft PR #1 ready and squash-merge it if checks pass and it touches only `docs/` (the untracked `.claude/agent-memory/` is not part of the PR unless you commit it deliberately). Story branches are created from `main` **after** this merge. Then brief the developer for PGD-12 first.
- scrum-master: when drafting STORY-01.04/01.06, 07.02/07.03, 07.04, 06.02 and 04.05, include the follow-up ACs in sprint-01-plan L99–107 (A-5 interim-string removal, zero-match log and header-only CSV, AA-06). Master checks them at the sprint-02 G4 (RISK-020).
- qa-engineer: confirm the D-21 exit-code mapping in the test plan (G3 follow-up, still open; the test plan does not exist yet).
- orchestrator: optional non-blocking FYI to Santhosh: the two enablers add about 16 points to R1 (99 → about 115, CC-01). This is effort, not scope; no FR changes (RISK-010).

**Risks registered:** RISK-020 (interim CLI strings from A-5 ship in v0.9.0 if the removal ACs are not drafted). Re-assessed: RISK-010 (enablers add about 16 R1 points; sprint 01 commits 29 of an assumed 30; score unchanged), RISK-014 (PD-17 rewords NFR-009, so P drops from 4 to 2; open until the W1 benchmark measures the 2 KB figure), RISK-007 (CC-02/C12 noted).
**Rationale:** All three mandatory G4 items have Jira- and file-level evidence. The consistency report has 0 Critical issues. All seven sprint-01 stories are READY under the DoR, and master's full read of three of them found every DoR item met. Every story has a parent epic and an FR/NFR trace, with sampled goal → FR → story → AC → test chains intact. G3 conditions C7–C10 are closed, measured against the current standards rulings (D-30..D-32), which superseded the D-25/D-26 wording in C10. The ⚠️ items are an open Major (CC-02) that touches only a held story outside sprint 01, Minor documentation drift and C11, which is open by design. None of them puts users, data or correctness at risk in sprint 01, so each carries an owner and a due gate. G4 is not in `HUMAN_APPROVAL_POINTS`, so no human approval is needed.

---

## G6 – Peer Review — STORY-02.01 (PGD-12) — 2026-10-29

- **Decision:** CONDITIONAL GO (story goes to **Changes Requested** for the fix-now list; it does not enter QA until C15 is closed)
- **Decided by:** master  ·  **Human override:** none
- **Attempt:** 1 (dev↔review loop 1 of 3)
- **Artefacts evaluated:** PR #6 `feat/PGD-12-walking-skeleton`, head `99979e7`, base `main` `50d2385` (34 new files, 9 commits). Reviews: standards [5706665315](https://github.com/sankumar76/pdf-download-gmail/pull/6#pullrequestreview-5706665315), quality [5706676804](https://github.com/sankumar76/pdf-download-gmail/pull/6#pullrequestreview-5706676804), performance [5706701035](https://github.com/sankumar76/pdf-download-gmail/pull/6#pullrequestreview-5706701035); 34 inline review threads (all read; all unresolved, none outdated); consolidated comment [6511894214](https://github.com/sankumar76/pdf-download-gmail/pull/6#issuecomment-6511894214). Check runs for `99979e7`: 10/10 success (run 40978322562). Jira PGD-12 (description, AC-1..9, 10 sub-tasks Done, status In Review), comments 10140–10144. `tests/unit/test_import_boundaries.py` read in full and QUA-01 reproduced by master. `gmail_pdf/**/__init__.py` (no imports). `pyproject.toml:35`; ADR-002 L30; EPIC-02 L51, EPIC-03 L41–44; reviewer severity scale (`.claude/agents/review/reviewer-quality.md` L63–66); `definition-of-done.md` §Peer Review

| # | Check | Mandatory | Result | Evidence |
|---|-------|-----------|--------|----------|
| 1 | Three reports present (standards, quality, performance) | ✱ | ✅ | Three submitted PR reviews on `99979e7` (event COMMENT under `single-token`, verdict in body): standards APPROVE WITH COMMENTS, quality REQUEST CHANGES, performance APPROVE WITH COMMENTS. Hand-offs PGD-12 c.10141–10143. Labels per playbook §5.3 |
| 2 | Zero open Blocker/Critical findings | ✱ | ✅ | 0 Blocker and 0 Critical in all three reviews. **QUA-01 severity ruled Major, not Critical** (D-40): the rubric's Critical is "AC not met". AC-6's rules are enforced for every absolute import in every module and for relative imports in every non-`__init__` module; the negative tests fail as required; and the delivered package gives the correct result, because no `gmail_pdf/**/__init__.py` contains any import (master checked). The defect is a gap in future enforcement for one import form, which is Major ("should fix before merge"). Not deferrable: see #3 |
| 3 | Major findings fixed or explicitly accepted with a logged reason | | ⚠️ | **QUA-01** (`tests/unit/test_import_boundaries.py:87-102`): reproduced by master: `check_tree({"gmail_pdf.app": "from ..infra import gmail_gateway"})` → `[]` (false negative); `check_tree({"gmail_pdf.domain": "from . import errors"})` → 2 violations (false positive); `violations_in(..., is_package=True)` is correct. **Not accepted** → fix in this PR (C15). **PERF-01** (`tests/fakes/fake_gmail.py:72-77`): **accepted as deferred** (D-41) → [#9](https://github.com/sankumar76/pdf-download-gmail/issues/9), target STORY-02.08 before its G5 |
| 4 | Findings cite file:line | | ✅ | All 34 inline threads anchor to path + line; the consolidated table cites file:line for every Major and Minor; QUA-12 is PR-level by nature |
| 5 | Every AC has implementation evidence (quality AC table) | | ✅ | Quality review AC table: AC-1..5, 7, 8, 9 Met; AC-6 met with defect (QUA-01). Sub-tasks PGD-19..28 Done. **AC-3 / QUA-12 ruled met** (D-43): the AC's outcome is that every listed stage executes on a PR with no secrets and the run is green; the first run on the PR was red only on the three Windows test legs from a test-helper path lookup, fixed in `99979e7`, and the run on the reviewed head is green on all 10 jobs with every stage present. QA re-verifies AC-3 on the final head because C15 changes `ci.yml` |
| 6 | Dependency control (NFR-023, Coding Standards §5) | | ⚠️ | STD-08: `tomli; python_version < '3.11'` (`pyproject.toml:35`) is not on the ADR-002 dev list (ADR-002 L30) and has no architect approval on record. Low risk (dev-only, MIT, pip-audit clean, disclosed). Ruling D-42: approval now (C16), ADR-002 amendment as follow-up [#14](https://github.com/sankumar76/pdf-download-gmail/issues/14) |
| 7 | Security hygiene | | ✅ | No secrets (standards review: `example.com` / RFC 5737 fixtures; only the automatic `GITHUB_TOKEN`; SHA-pinned actions; `permissions: contents: read`); `security` job green (pip-audit, bandit, gitleaks, allow-list test). Fake-mailbox hook gated by two env vars (AC-9). QUA-09 overclaim on DNS egress → fix now (C15) so the NFR-014 evidence is not overstated |
| 8 | G5 evidence consistent | | ✅ | 131 passed, 98.80 % (gate 80 %, D-30), ruff and `mypy --strict` clean; reproduced by reviewer-quality on Windows 11 / 3.12.10 and by the orchestrator (c.10140); CI 10/10 green |

**Dispositions (every Major and Minor finding)**

| Finding(s) | Severity | Disposition | Where |
|---|---|---|---|
| QUA-01 | Major | **Fix in this PR** (carry `is_package` through `package_sources`/`check_tree`; add the false-negative and false-positive tests) | C15 |
| PERF-01 (+ PERF-05 Info) | Major | **Defer**, accepted (D-41) | [#9](https://github.com/sankumar76/pdf-download-gmail/issues/9) → STORY-02.08 |
| STD-10 = QUA-08; STD-09 | Minor | **Fix in this PR** (production code in `gmail_pdf/bootstrap.py`: narrow the `ModuleNotFoundError` catch; translate `OSError`/`ValueError` to `AdapterUnavailableError` without echoing the path) | C15 |
| STD-15 = PERF-04; QUA-10 | Minor | **Fix in this PR** (`timeout-minutes` on every job; `cancel-in-progress` only for `pull_request`) — protects the `main` baseline before the first code merge | C15 |
| QUA-02, QUA-04 | Minor | **Fix in this PR** (validate `times`/`skip`; reject `OR`/`AND`/braces/parentheses/quotes as the docstring promises) | C15 |
| QUA-07, STD-05 | Minor | **Fix in this PR** (same test: per-mode exact assertion on the unwidened query, parametrised, no branching) | C15 |
| QUA-09 | Minor | **Fix in this PR**: preferred, guard `getaddrinfo`/`gethostbyname`/`sendto` with the loopback check and install the guard in `pytest_configure`; acceptable, narrow the docstring to what is enforced and open a `follow-up` issue for the rest | C15 |
| STD-01, STD-02, STD-04 | Minor | **Fix in this PR** (move the JSON persistence block to `tests/fakes/fake_gmail_json.py`; split `test_fake_gmail.py` by capability; one behaviour per test / parametrise with ids). Rationale: Coding Standards §1/§6 are written rules, the files will grow with #9–#13, and the split is mechanical now | C15 |
| STD-03, STD-06, STD-07 | Minor | **Fix in this PR** (named defaults; typed helper instead of `type: ignore`; delete dead `noqa: ANN401`, justify the remaining ignores) | C15 |
| STD-11 | Minor | **Fix in this PR** (move the subprocess tests to `tests/e2e/`; Architecture §10.1 is the layout every later story copies) | C15 |
| STD-08 | Minor | **Split**: architect approval now; ADR-002 amendment deferred (D-42) | C16; [#14](https://github.com/sankumar76/pdf-download-gmail/issues/14) |
| QUA-03 | Minor | **Defer** | [#11](https://github.com/sankumar76/pdf-download-gmail/issues/11) → STORY-02.02 (PGD-15), before its G5 |
| QUA-05 | Minor | **Defer** | [#12](https://github.com/sankumar76/pdf-download-gmail/issues/12) → STORY-03.03 (EPIC-03, AA-02/AR-05), before its G5 |
| QUA-06 | Minor | **Defer** | [#13](https://github.com/sankumar76/pdf-download-gmail/issues/13) → STORY-03.01 (PGD-18), before its G5 |
| PERF-02, PERF-03 (+ PERF-06 Info) | Minor | **Defer** | [#10](https://github.com/sankumar76/pdf-download-gmail/issues/10) → STORY-02.08 |
| Info: STD-12, 13, 14, 16, 17; QUA-11, QUA-12; PERF-05, PERF-06 | Info | No action required. STD-12/13 optional in this PR; STD-14 when `ExitCode` lands; STD-16 developer may open a `follow-up`; QUA-11 tracked in #8; QUA-12 ruled (D-43); PERF-05/06 folded into #9/#10 | — |

**Conditions / remediation**
| # | Owner agent | Artefact | Required change | Due gate |
|---|-------------|----------|-----------------|----------|
| C15 | developer (fix); reviewer-quality and reviewer-standards (delta re-review); reviewer-performance only for PERF-04 if it wishes | PR #6 (`tests/unit/test_import_boundaries.py`, `gmail_pdf/bootstrap.py`, `tests/unit/test_bootstrap.py`, `.github/workflows/ci.yml`, `tests/fakes/fake_gmail.py`, new `tests/fakes/fake_gmail_json.py`, `tests/unit/test_fake_gmail*.py`, `tests/support/socket_guard.py`, `tests/conftest.py`, `tests/e2e/`) | Fix QUA-01 (Major) and Minor STD-01..07, STD-09, STD-10/QUA-08, STD-11, STD-15/PERF-04, QUA-02, QUA-04, QUA-07, QUA-09, QUA-10 as in the dispositions table. Reply "Fixed" in each thread. G5 loop green on the new head (pytest, coverage ≥ 80/80, ruff, `mypy --strict`, CI 10/10). Reviewers re-review the new diff only and reply in the original threads. The orchestrator moves PGD-12 to In QA when every C15 thread is marked Fixed and the delta re-reviews raise no new Blocker/Critical/Major; any new Blocker/Critical/Major returns to master as G6 attempt 2 | Before G7 starts (master confirms closure as the first G7 check) |
| C16 | solution-architect | PR #6 comment; ADR-002 (follow-up #14) | STD-08: post approval or rejection of `tomli` (Python < 3.11, dev-only) on PR #6; if rejected, the developer removes it under C15. Amend the ADR-002 dev list via #14 | Approval: before G7 GO of PGD-12. ADR amendment: sprint-02 G4 |
| C17 | scrum-master (product-owner validates) | Jira PGD-15, PGD-18; future STORY-02.08 and STORY-03.03 | Link #11 in PGD-15 and #13 in PGD-18 (sub-task or Dev Context line; no AC change needed, test infrastructure). When drafting STORY-02.08 add #9/#10 as ACs; when drafting STORY-03.03 add #12. Each must close before the target story's G5 | PGD-15/PGD-18 links: before either story goes In Progress. Drafted stories: the G4 of the sprint that contains them |

Follow-ups (not conditions):
- qa-engineer (G7): verify AC-3 and AC-6 on the **final** head, because C15 changes `ci.yml` and the boundary test; include the QUA-01 false-negative case as AC-6 evidence.
- orchestrator: transition PGD-12 to **Changes Requested** (CLAUDE.md §4); brief the developer with the C15 list. `MERGE_POLICY = docs-auto, code-human`: PR #6 waits for the delivery lead after G7.
- Standards recommendation (D-40): reviewer severity scale to state that an AC whose outcome is delivered but whose enforcing check has a gap is Major; Critical is reserved for an AC outcome not delivered. Proposed to the delivery lead; standards are his to change.

**Risks registered:** RISK-021 (deferred fake-fidelity gaps QUA-03/05/06 let product code pass against an over-permissive fake). Re-assessed: RISK-014 (PERF-01 adds a measurement-validity cause to the NFR-009 benchmark; mitigated by #9 in STORY-02.08; score unchanged at 4); RISK-016 (QUA-05: the AA-02 fallback is untestable until #12 closes; score unchanged).
**Rationale:** Both mandatory G6 items have PR-level evidence: three reports exist and none has an open Blocker or Critical finding. QUA-01 stays Major because AC-6's outcome is delivered for the current package (master reproduced the defect and confirmed no `__init__` module imports anything), but the AC says the test *enforces* the layering, so the gap is not accepted and must be fixed before QA. PERF-01 is accepted as deferred with a logged reason, because PGD-12 measures no NFR and its only consumer is STORY-02.08. The cheap Minor items in production code, CI and test conventions are fixed now, and the fake-fidelity items move to the first story that depends on each. G6 is not in `HUMAN_APPROVAL_POINTS`, so no human approval is needed.

---

## G6 – Peer Review — STORY-02.01 (PGD-12) — 2026-10-29 — attempt 2

- **Decision:** CONDITIONAL GO. One docstring-level fix (C18) is needed before QA starts. No further G6 attempt is needed unless the C18 delta goes beyond the scope stated below
- **Decided by:** master  ·  **Human override:** none
- **Attempt:** 2 (fix loop 1 of 3 completed; C18 is a single-file follow-up within loop 2)
- **Artefacts evaluated:** PR #6, head `5f67b59` (16 commits, 42 files, base `50d2385`); fix commits 3b12e14, 1f21246, d729d6c, a42ea30, 1fd8de8, e4bce0c, 5f67b59. Standards re-review [5707087304](https://github.com/sankumar76/pdf-download-gmail/pull/6#pullrequestreview-5707087304) (APPROVE); quality re-review [5707092105](https://github.com/sankumar76/pdf-download-gmail/pull/6#pullrequestreview-5707092105) (APPROVE WITH COMMENTS); performance review 5706701035 (unchanged, APPROVE WITH COMMENTS; its items deferred to #9/#10); the thread replies and the new inline comments QUA-13, QUA-14, STD-18 and STD-19 (read with `gh api`). Check runs for `5f67b59`: 10/10 success (run 40985658014). PR body Dev Record with findings table. SA ruling, PR comment [6512025330](https://github.com/sankumar76/pdf-download-gmail/pull/6#issuecomment-6512025330). Jira PGD-12 c.10147, 10150–10158. Remote links on PGD-15 (id 10000 → #11) and PGD-18 (id 10001 → #13), read with `listJiraIssueRemoteIssueLinks`. `docs/05-backlog/sprint-01-plan.md` working-tree diff (+10 lines with the #9/#10/#12 ACs; **uncommitted**). Local checkout at `5f67b59`: master re-ran the QUA-01 probe and read the `tests/support/socket_guard.py` docstring

| # | Check | Mandatory | Result | Evidence |
|---|-------|-----------|--------|----------|
| 1 | Three reports present | ✱ | ✅ | Attempt-1 reports plus the delta re-reviews from standards and quality on `5f67b59`. Performance had no fix-now item of its own; PERF-04 = STD-15 was verified by standards. Labels: `review:standards-approved`, `review:quality-approved`, `review:performance-approved` |
| 2 | Zero open Blocker/Critical findings | ✱ | ✅ | Re-reviews: standards 0/0/0/0 + 2 Info; quality 0/0/0 + 1 Minor + 1 Info. No Blocker or Critical has ever been open on this PR |
| 3 | Major findings fixed or accepted | | ✅ | **QUA-01 fixed** (3b12e14). Master re-ran the probe on the `5f67b59` checkout: `check_tree` now takes `(source, is_package)`; `{"gmail_pdf.app": ("from ..infra import gmail_gateway", True)}` gives 2 violations (was `[]`); `{"gmail_pdf.domain": ("from . import errors", True)}` gives `[]` (was 2 false positives); the real package gives `[]`. Two regression tests were added. reviewer-quality also verified it. **PERF-01** remains accepted as deferred (D-41, #9) |
| 4 | C15 closed (fix-now list) | | ✅ | All 17 IDs (19 with aliases) have a "Fixed in <sha>" reply. The reviewers verified each one: standards marked STD-01..07, 09, 10, 11 and 15 Fixed; quality marked QUA-01, 02, 04, 07, 08, 09 and 10 Verified fixed. Size: no file in `gmail_pdf/` or `tests/` is over 400 lines (`fake_gmail.py` 387). G5 re-check: 265 passed, 98.90 %, diff-cover 100 % (81/81), ruff and `mypy --strict` clean, CI 10/10. **Closed** |
| 5 | C16 closed (STD-08 `tomli`) | | ✅ | The solution-architect **APPROVED** it (PR comment 6512025330; Jira c.10151), with reasons and rejected alternatives. Standards marks STD-08 "Rebuttal accepted". The ADR-002 amendment remains in #14 (sprint-02 G4). **Closed** |
| 6 | C17 closed (deferred items linked) | | ✅ | PGD-15 has a remote link to #11 and PGD-18 a remote link to #13, both "must be addressed before G5". The #9/#10 ACs (a)–(g) for STORY-02.08 and the #12 AC for STORY-03.03 are in the `sprint-01-plan.md` follow-ups, but that file is **uncommitted** (held for the sprint-close status PR, c.10150). Closed for G6. The orchestrator must commit the plan before the sprint-02 G4, where master checks it (RISK-020/021 pattern) |
| 7 | New findings on the delta | | ⚠️ | **QUA-13 (Minor)**, `tests/support/socket_guard.py:4-10`. Master read the docstring at `5f67b59`: it still says "so no DNS query leaves the machine", but `gethostbyname_ex`, `gethostbyaddr` and `getnameinfo` are neither guarded nor on the "Not covered, by design" list. This is the same over-claim of NFR-014 evidence that attempt 1 ruled fix-now (QUA-09: "acceptable: narrow the docstring"), so for consistency it is **fix now** → C18. QUA-14, STD-18 and STD-19 are Info → see the dispositions table |
| 8 | ACs and security | | ✅ | Quality: all 9 ACs met, and AC-6's defect is fixed. The security job is green; no secrets; no new dependency in the delta (standards: no `open`/`os.replace`/`unlink` added in `gmail_pdf/`; no pragma) |

**Dispositions (new findings on the delta)**

| Finding | Severity | Disposition |
|---|---|---|
| QUA-13 `tests/support/socket_guard.py:4-10` | Minor | **Fix before G7 (C18).** Minimum: add `gethostbyname_ex`, `gethostbyaddr` and `getnameinfo` to the "Not covered, by design" paragraph, or reword the "no DNS query leaves the machine" claim to name only the guarded entry points. Alternatively, guard all three with `_check_host` (for `getnameinfo`, check `sockaddr[0]`) and add a `pytest.raises(NetworkAccessError)` test for each. No tech-debt issue |
| QUA-14 `gmail_pdf/bootstrap.py:55-60` | Info | No action required: it affects only hand-written test fixture files, and the hook is gated by two env vars. Optional in the C18 commit: validate `isinstance(resource.get("id"), str)` in `tests/fakes/fake_gmail_json.py::from_json_dict` and raise `ValueError` (with a test), so the existing translation covers it |
| STD-18 `tests/support/socket_guard.py:63` | Info | No action required. Optional in the C18 commit, because it is in the same file: one `_refuse(host)` helper, keeping the `None`/empty-host difference explicit |
| STD-19 `tests/unit/test_fake_gmail_canonical.py:84, 97` | Info | No action required. The conditional on `bounds` is a small oracle, and the single-assertion structure asked for by STD-05 is met |

**Conditions / remediation**
| # | Owner agent | Artefact | Required change | Due gate |
|---|-------------|----------|-----------------|----------|
| C18 | developer (fix); reviewer-quality (replies Fixed/Not fixed in the QUA-13 thread); reviewer-standards only if STD-18 is included | PR #6: `tests/support/socket_guard.py` (plus `tests/unit/test_socket_guard.py` if guarding; plus `tests/fakes/fake_gmail_json.py` and its test if the optional QUA-14 change is taken) | Fix QUA-13 as in the dispositions table. CI 10/10 on the new head. **Scope rule:** the delta may touch only the files named here. If it touches `gmail_pdf/`, `.github/` or any other file, or the reviewer raises any new Blocker/Critical/Major, it returns to master as G6 attempt 3. Within scope, the orchestrator moves PGD-12 to In QA once the reviewer marks QUA-13 Fixed and CI is green | Before G7 starts. Master confirms C15 and C18 as the first G7 check |

Carried, not conditions: qa-engineer re-verifies **AC-3** (`ci.yml` changed in 5f67b59: timeouts and concurrency) and **AC-6** (boundary test changed in 3b12e14) on the final head, as directed at attempt 1. The orchestrator commits `docs/05-backlog/sprint-01-plan.md` (C17 evidence) with the governance files.

**Condition status:** C15 ✅ closed · C16 ✅ closed · C17 ✅ closed (plan file still to be committed) · C18 ⏳ open (new).
**Risks registered:** none new. RISK-014, RISK-016 and RISK-021 are unchanged; their mitigations (#9–#13) are now linked to target stories.
**Rationale:** Both mandatory items are met, the one Major (QUA-01) is fixed and independently re-verified by master, and C15–C17 are closed with PR, CI and Jira evidence. The only open item is that the NFR-014 egress-guard docstring still claims more than the code enforces. Attempt 1 ruled this exact over-claim fix-now (QUA-09), so the same evidence gives the same decision. It is a one-paragraph change with no runtime effect, so it is a scoped pre-G7 condition, not another full review loop. G6 is not in `HUMAN_APPROVAL_POINTS`; under `MERGE_POLICY = docs-auto, code-human`, the delivery lead merges PR #6 after G7.

---

## G7 – QA Acceptance — STORY-02.01 (PGD-12) — 2026-10-29

- **Decision:** GO (ACCEPT). The story may move to Done. **Merging PR #6 needs the delivery lead** (`MERGE_POLICY = docs-auto, code-human`)
- **Decided by:** master  ·  **Human override:** none
- **Attempt:** 1
- **Artefacts evaluated:**
  - `docs/07-qa/PGD-12-test-report.md` (commit 88bf54d, read in full); code under test `f85d267`.
  - C18 diff `5f67b59..f85d267`: 4 files, all under `tests/`. These are `socket_guard.py`, `test_socket_guard.py`, `fake_gmail_json.py` and `test_fake_gmail_canonical.py`, which now holds the JSON tests after the STD-02 split.
  - reviewer-quality "Verified fixed" replies r4419691700 (QUA-13) and r4419691990 (QUA-14).
  - `gh api commits/f85d267/check-runs`: 10/10 success (run 40987328532).
  - PR #6 comment 6513098595 (QA), Jira PGD-12 c.10166, Jira Bugs PGD-63 and PGD-64 (Low priority, `sev-4`, To Do), and GitHub #15 and #16 (`bug`, `sev-4`, `ai-delivery`).
  - `socket_guard.py` docstring at HEAD.

| # | Check | Mandatory | Result | Evidence |
|---|-------|-----------|--------|----------|
| 0 | G6 conditions C15–C18 closed | | ✅ | C15, C16 and C17 closed at G6 attempt 2. **C18 closed:** the delta stayed in scope (tests only; `gmail_pdf/` and `.github/` untouched). The docstring now lists all five resolver entry points as guarded, and `gethostbyname_ex`, `gethostbyaddr` and `getnameinfo` are wrapped and tested. reviewer-quality verified the fix with a stubbed-resolver probe (r4419691700), and the optional QUA-14 change was also verified (r4419691990). No new findings. CI 10/10 on `f85d267` |
| 1 | Every AC has a verification result with evidence | ✱ | ✅ | Test report matrix L22–30: all 9 ACs pass, each with test IDs, technique and fresh evidence. **AC-3:** 10/10 on `f85d267`, with each stage checked against the AC text (D-43). **AC-6:** the QUA-01 `__init__` cases were re-checked, and a mutation of the real tree turns the shipped test red. **AC-5:** mutation with `requests` and `PySide6-Essentials` turns the shipped tests red. **AC-4:** CI `security` evidence only, because the advisory service needs the network; the requirements are unchanged since `6bb1da8`, and a re-run is due at G8. **AC-8:** 24 refusal probes plus a loopback positive control |
| 2 | No open Sev-1/Sev-2 defects | ✱ | ✅ | Report L82: Sev-1 0, Sev-2 0, Sev-3 0, Sev-4 2. JQL `project = PGD AND issuetype = Bug` returns only PGD-63 and PGD-64, both priority Low with label `sev-4` |
| 3 | Regression suite result recorded and green | ✱ | ✅ | 271/271 on Python 3.12.10 (four runs, per-file isolation, no flakiness); `--cov-fail-under=80` met at 98.90 %; diff-cover 100 %; ruff, `mypy --strict` and bandit clean (L37–47). The local 3.10 run (270/271) missed only the console-script test in an offline scratch venv without the editable install. That is the test's own "run `pip install -e .`" message, and CI `test (win-310)` is green on `f85d267`. Accepted as an environment artefact |
| 4 | Exploratory testing notes present | | ✅ | Report L64–73: charter, 90-minute time box, areas covered, observations, 2 defects |
| 5 | Accessibility checks for UI stories | | n/a | No UI in this story (L62). CLAUDE.md §9 is not applicable until R2 |
| 6 | Security and scope | | ✅ | NFR-014 egress: all probes refused before sending (L56). NFR-015/012: no credentials in the diff; only `example.com`/`example.org`; gitleaks green. Error leakage: hook messages never echo the path (L58). Protected files untouched (L61) |

**Defect dispositions**
| Defect | Severity | Disposition |
|---|---|---|
| DEF-001 · [PGD-63](https://sankumar76.atlassian.net/browse/PGD-63) · [#15](https://github.com/sankumar76/pdf-download-gmail/issues/15): the hook and FakeGmail let crafted input escape as raw `RecursionError`, `ValueError` or `KeyError` | Sev-4 (test support) | **Keep open; do not fix in PR #6.** It fails no AC, affects only hand-written fixture files behind two env vars, and belongs with the fake-fidelity bundle (RISK-021). **Target:** PGD-15 (STORY-02.02), which already carries #11 in the same files, before its G5. scrum-master adds a remote link like C17 |
| DEF-002 · [PGD-64](https://sankumar76.atlassian.net/browse/PGD-64) · [#16](https://github.com/sankumar76/pdf-download-gmail/issues/16): `socket.sendmsg(address)` is not guarded on Unix | Sev-4 (test support) | **Keep open; do not fix in PR #6.** `sendmsg` does not exist on Windows 11, the target OS (D-33). It is reachable only on the Ubuntu and macOS CI legs, and only through a deliberate call. **Target:** the next story that changes `tests/support/`, and no later than the sprint-02 G4, where master checks it. Until then the docstring's "every entry point" claim is one call too wide on POSIX. This is the third over-claim on this module (QUA-09, QUA-13, DEF-002), so the fix should also add `sendmsg` to the guard, or name it under "Not covered" |

**Residual items**
| Item | Disposition |
|---|---|
| `docs/07-qa/test-plan.md` does not exist (it carries the PQ-02/D-21 exit-code confirmation and the C12/CC-02 benchmark case) | **C19** (project level, not on PGD-12). Tracked item T-03 |
| CI checks are not required on `main` (branch protection, #7) | **RISK-022** registered. Delivery-lead action; recommended before or with the PR #6 merge |
| AC-6 cannot see dynamic imports (`importlib.import_module`, `__import__`) | **Accepted** as within AC-6, which specifies an AST walk. The application uses dynamic import only in the gated test hook, by design. Reviewers flag any new dynamic import in `gmail_pdf/`. No issue |
| The hook's exception chain (`from exc`) still holds the mailbox path | No action for PGD-12. The path is a test fixture path, not a secret. The CLI's "no stack trace" rule (D-21) must hold when the hook is wired into CLI runs. qa-engineer adds this check to the test plan (C19) |
| AC-4 was not re-run from the package index | Re-run `pip-audit -r requirements.txt` at G8 (master's G8 checklist). Add `-r requirements-dev.txt` when #14 lands |
| PR head is now `88bf54d` (docs-only, the test report); its CI run 40989128456 was still in progress when this decision was taken | **Merge precondition:** before the delivery lead merges, all 10 CI jobs on the PR head must be green. The orchestrator confirms this in the approval request |

**Conditions / remediation**
| # | Owner agent | Artefact | Required change | Due gate |
|---|-------------|----------|-----------------|----------|
| C19 | qa-engineer (with solution-architect for the C12 case) | `docs/07-qa/test-plan.md` | Write the project test plan from `docs/templates/test-plan.md`. It must contain the D-21 exit-code mapping confirmation (PQ-02; observed now: `--help` exits 0, an unknown argument exits 2), the ratio 0.6 benchmark case for CC-02/C12, a "no traceback, no fixture path on screen" check for the hook in CLI runs, and the G8 `pip-audit` re-run | The next story's G7 (PGD-13 or whichever reaches G7 first). Master checks it as G7 check 0 |
| C20 | scrum-master | Jira PGD-15 (remote link to #15); sprint-02 plan | Link DEF-001 (#15, PGD-63) to PGD-15 "before G5". Schedule DEF-002 (#16, PGD-64) into the next story that changes `tests/support/`, or into sprint 02 | PGD-15 link: before PGD-15 goes In Progress. DEF-002: sprint-02 G4 |

Follow-ups (not conditions):
- qa-engineer: after this decision, move PGD-12 to Done (CLAUDE.md §4).
- orchestrator: post the merge request to Santhosh (playbook §3.4) with the precondition above, and remove `gate:g6-changes` if it is still present. Commit the uncommitted governance files and `docs/05-backlog/sprint-01-plan.md` (C17 evidence). Optionally, before merging, ask Santhosh to configure branch protection (#7).

**Risks registered:** RISK-022 (CI checks not required on `main`). RISK-005 re-assessed: the egress guard and the gitleaks/bandit/pip-audit stages are now evidenced (G6/G7 PGD-12), but redaction (STORY-01.01) is not yet built, so the score is unchanged. RISK-021 now also tracks DEF-001 and DEF-002.
**Rationale:** All three mandatory G7 items have file-, CI- and Jira-level evidence. Every AC was verified on the final code with fresh runs, and the two gate-style ACs (5 and 6) were mutation-tested. There is no Sev-1, Sev-2 or Sev-3 defect, and the full regression is green locally and on all ten CI jobs. The two Sev-4 defects sit in test-support code, fail no AC and are scheduled with owners. The missing project test plan is a QA-process gap, not a defect in this story, so it is a condition on the next G7 (C19) and does not block PGD-12. G7 is not in `HUMAN_APPROVAL_POINTS`, but the code merge is human under `MERGE_POLICY`.

---

## G6 – Peer Review — STORY-01.02 (PGD-14) — 2026-10-30

- **Decision:** CONDITIONAL GO. The story goes to **Changes Requested** for the fix-now list (C21). It does not enter QA until C21 is closed, and G7 GO also needs C22
- **Decided by:** master  ·  **Human override:** none
- **Attempt:** 1 (dev↔review loop 1 of 3)
- **Artefacts evaluated:**
  - PR #17 `feat/PGD-14-secret-files`, head `93ecd5e`, base `1ce8473` (9 files, 2 commits).
  - Reviews: standards 5708044489 (APPROVE WITH COMMENTS), quality 5708066212 (APPROVE WITH COMMENTS), performance 5708057780 (APPROVE). All three bodies and all 15 inline comments were read with `gh api`.
  - Consolidated comment 6514981472.
  - Check runs for `93ecd5e`: 10/10 success (run 41001643114).
  - Jira PGD-14 (AC-1..5, Dev Context) and hand-offs c.10182–10184.
  - ADR-003 decision 1 and architecture §4.1, §6.8, §8.2 and §10.2, as cited by the reviewers. Decision-log D-23, D-32, D-40 and D-42.

| # | Check | Mandatory | Result | Evidence |
|---|-------|-----------|--------|----------|
| 1 | Three reports present | ✱ | ✅ | Three PR reviews on `93ecd5e` (COMMENT event under `single-token`, verdict in body); labels `review:*-approved` |
| 2 | Zero open Blocker/Critical findings | ✱ | ✅ | All three reviews: 0 Blocker, 0 Critical. QUA-15 was re-rated Major (#3), not Critical: AC-4's listed cases (inside, outside, `..`, case) all pass, and no code path can feed a user-supplied path into the function until STORY-01.03 |
| 3 | Major findings fixed or accepted | | ⚠️ | **QUA-15 is re-rated from Minor to Major (D-45).** AC-4 says `token_location_warning` "never blocks or raises" (D-23), and the reviewer's probe shows `ValueError` on a path containing NUL (`paths.py:136-142`). Under D-40, an AC whose outcome is delivered but whose explicit guarantee has a hole is Major, and it is not deferrable → fix now (C21) |
| 4 | Findings cite file:line | | ✅ | All 15 inline comments are anchored to a file and line; the consolidated table cites file:line |
| 5 | AC evidence (quality AC table) | | ✅ | AC-1..5 Met. Notes: AC-1 and AC-5 have the isolation gap QUA-16; AC-4 has QUA-15. AC-2 POSIX modes run on the Ubuntu and macOS CI legs and are spy-tested on Windows |
| 6 | Architecture / ADR conformance | | ⚠️ | STD-21 = QUA-20: the code uses `O_EXCL` on the temp file, but the **Accepted** ADR-003 decision 1 and architecture §8.2 say `O_TRUNC`. Both reviewers endorse `O_EXCL` as stricter. STD-20: the token writer is in `infra/paths.py` (the story's Dev Context) while architecture §4.1/§10.2 name `infra/auth.py`. Ruling D-44: the SA acknowledges on the PR before G7 GO (C22); the documents follow in #20 |
| 7 | Security hygiene | | ✅ | Placeholder fixtures only; the error message is a constant and `from None` keeps the content out of the encode error; `os.replace` only for the app-owned token (D-32); temp file `0o600` + `O_EXCL` + fsync; `security` job green. STD-22(c) (a token `*.tmp` left by a hard kill outside `secrets/`) is a secret-in-git vector → fix now |

**Dispositions (every Minor and Major finding)**

| Finding(s) | Severity | Disposition |
|---|---|---|
| QUA-15 `gmail_pdf/infra/paths.py:136-142` | **Major** (re-rated) | **Fix in this PR.** Fail safe: an unclassifiable path (`ValueError`, e.g. NUL) returns `Warning(TOKEN_OUTSIDE_PROFILE)` and never raises; add the NUL test |
| QUA-16 `tests/e2e/test_gitignore_matching.py:58-70` | Minor | **Fix in this PR.** Isolate git from user config (`XDG_CONFIG_HOME`/`HOME` to an empty temp dir, or `-c core.excludesFile=<empty>`); AC-5 checks repository rules only (`--exclude-per-directory=.gitignore`, not `--exclude-standard`). Add the negative test the reviewer describes. This is the AC-1/AC-5 evidence and the docstring over-claims, so it is fixed now for consistency with QUA-09/QUA-13 |
| STD-22 `.gitignore:21-25` | Minor | **Fix in this PR.** Append `.venv/`, `venv/`, `dist/`, `build/` and `*.tmp` (or the narrower `.*.tmp`), and extend `REQUIRED_ARTEFACT_PATTERNS`/`IGNORED_PATHS` with the temp-file samples. A left-over token temp file is a secret-in-git vector (AC-1 intent, Coding Standards §9/§10) |
| STD-23 `tests/integration/test_private_files.py:216, 86-91` | Minor | **Fix in this PR.** One behaviour per test (Coding Standards §6), for consistency with the PGD-12 STD-04 ruling |
| STD-20 `gmail_pdf/infra/paths.py:67` | Minor | **Split.** Now: add the docstring restriction "app-owned state only (token, manifest snapshot); never for a user-visible file (coding-standards §10, D-32)". SA acknowledgement before G7 GO (C22). Document reconciliation deferred → [#20](https://github.com/sankumar76/pdf-download-gmail/issues/20) |
| STD-21 = QUA-20 `gmail_pdf/infra/paths.py:118-125` | Minor / Info | **No code change.** SA acknowledgement before G7 GO (C22). ADR-003, §8.2 and §7 amendment → [#20](https://github.com/sankumar76/pdf-download-gmail/issues/20) |
| QUA-17 = STD-25 `gmail_pdf/domain/events.py:19-20` | Minor / Info | **Split.** Now: one docstring line, "import as `events.Warning`; never import the name directly". Rename or lint enforcement is the SA's call (§6.8) → [#21](https://github.com/sankumar76/pdf-download-gmail/issues/21), before STORY-01.03 is Ready |
| QUA-18 (Info) | Info | → [#21](https://github.com/sankumar76/pdf-download-gmail/issues/21) (stable string values, same change) |
| PERF-07 (Info) | Info | → [#20](https://github.com/sankumar76/pdf-download-gmail/issues/20) item 3: STORY-01.04 AC "write the token only on change", with a test of at most one write per run |
| QUA-19 (Info) | Info | Optional in this PR (same file as STD-22): `.coverage` + `.coverage.*` instead of `.coverage*` |
| STD-24, STD-26, PERF-08 (Info) | Info | No action required |

**Conditions / remediation**
| # | Owner agent | Artefact | Required change | Due gate |
|---|-------------|----------|-----------------|----------|
| C21 | developer (fix); reviewer-quality and reviewer-standards (delta re-review) | PR #17: `gmail_pdf/infra/paths.py`, `gmail_pdf/domain/events.py` (docstring only), `.gitignore`, `tests/integration/test_private_files.py`, `tests/unit/test_gitignore_patterns.py`, `tests/e2e/test_gitignore_matching.py` and the `paths` unit tests | Fix QUA-15 (Major), QUA-16, STD-22, STD-23, plus the docstring parts of STD-20 and QUA-17, as in the table. Reply "Fixed" in each thread; CI 10/10 on the new head. Reviewers re-review the new diff only. The orchestrator moves PGD-14 to In QA when every C21 thread is verified Fixed and no new Blocker/Critical/Major is raised; otherwise it returns as G6 attempt 2 | Before G7 starts (master confirms as G7 check 0) |
| C22 | solution-architect | PR #17 comment | Acknowledge STD-21 (accept or reject `O_EXCL` vs ADR-003 `O_TRUNC`) and STD-20 (confirm `infra/paths.py::write_private_text` as the token writer for now, or name where it moves). If rejected, the developer changes the code under C21. Document amendments follow in #20 | Before G7 GO of PGD-14 |
| C23 | scrum-master | STORY-01.04 and STORY-01.03 when drafted; sprint-02 plan | Add the PERF-07 AC (#20 item 3) to STORY-01.04; link #21 to STORY-01.03 (before Ready) | Sprint-02 G4 |

**Carried project-level conditions:** C19 (test plan) is evidenced by commit 62976ec on `docs/PGD-1-status-sprint-01`; master checks it at the next G7. C20 (#15 → PGD-15; #16 by sprint-02 G4) stays open.
**Risks registered:** none new. RISK-005 is unchanged: the evidence improved (gitignore and file modes), but redaction (STORY-01.01) is not yet built. RISK-009 (unprotected downloads) is partly mitigated by `downloads/` in `.gitignore`.
**Rationale:** Both mandatory items are met: three reports and no Blocker or Critical. QUA-15 is re-rated Major under the D-40 rule, because the code contradicts AC-4's explicit "never raises" guarantee, so it must be fixed before QA, as QUA-01 was. The other fixes are cheap. Two of them stop docstrings and test claims overstating the evidence (the recurring pattern on this project), and one closes a secret-in-git vector. The two architecture deviations are endorsed as stricter or harmless, but they contradict an Accepted ADR and the architecture text. Under D-44 the architect signs them off before G7 GO, consistent with D-42, and the documents follow in #20. G6 is not in `HUMAN_APPROVAL_POINTS`.

### G6 exit check — STORY-01.02 (PGD-14) — 2026-10-30 — head `39e1f18`

- **Ruling:** C21 and C22 are **closed**. A new condition, **C24** (QUA-21), must be fixed before In QA. The scope is fixed: the C24 delta may touch only `tests/e2e/test_gitignore_matching.py`. If the delta stays in scope, no G6 attempt 2 is needed.
- **Evidence:**
  - **Standards re-review: APPROVE.** STD-20, 22, 23 and 25 verified. STD-21 rebuttal accepted. New Info findings STD-27 and STD-28 (Jira c.10191).
  - **Quality re-review 5708212916: APPROVE WITH COMMENTS.** QUA-15 (Major) verified by probe. QUA-16, QUA-17 and QUA-19 verified. New Minor QUA-21 (Jira c.10192).
  - **CI and local run.** `gh api commits/39e1f18/check-runs` shows 10/10 success (run 41004166732). The orchestrator's local run: 387 passed, 99.42 %.
  - **C22 closed.** The SA's comment [6515049452](https://github.com/sankumar76/pdf-download-gmail/pull/17#issuecomment-6515049452) acknowledges both points:
    - STD-21: the `O_EXCL` + random name + `fsync` + `os.replace` sequence is now the required pattern for the token.
    - STD-20: `paths.py` owns the private-file mechanics, and `auth.py` writes the token only through `paths.write_private_text`.
    - It also sets a new `os.replace` allow-list: `paths.write_private_text`, `manifest.py`, and the `file_store` FAT fallback.
    - The document changes go into #20.
- **QUA-21 (Minor), `tests/e2e/test_gitignore_matching.py:69-78` → fix now (C24).**
  - The defect: `isolated_env` passes inherited `GIT_INDEX_FILE`, `GIT_DIR` and similar variables to git. If the suite runs inside a git hook, the AC-5 test's `git add -f token.json` stages `token.json` into the outer repo's real index. The reviewer reproduced this with temp repos.
  - Why fix now: that is the exact threat this story exists to prevent (a secret reaching a commit). It is also the same evidence class as QUA-16 and STD-22, which were ruled fix-now at attempt 1, and the fix is small and confined to one file.
  - The fix: drop the repository-location variables (`GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE`, `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES`, `GIT_COMMON_DIR`, `GIT_NAMESPACE`, `GIT_CEILING_DIRECTORIES`, `GIT_CONFIG_PARAMETERS`, `GIT_CONFIG_COUNT`) and add the reviewer's regression test: with an inherited `GIT_INDEX_FILE`, the outer index stays unchanged.
- **Info findings:**
  - **STD-27** (`tests/unit/test_token_location_warning.py:122-130`, branching in a test): no action now. It is outside the C24 file scope. Whoever next edits that file splits the `ValueError` case into its own parametrized test.
  - **STD-28** (`test_private_files.py` is 389 lines): no action now. The next addition to that file moves the AC-3 failure tests to `test_private_file_failures.py`.
  - No issues created for either.
- **C23 extended (scrum-master):** the STORY-01.04 Dev Context must also carry the SA rule from c.6515049452. `auth.py` writes the token only through `paths.write_private_text`. Any new caller outside `auth.py` needs SA acknowledgement under D-44.

| # | Owner agent | Artefact | Required change | Due gate |
|---|-------------|----------|-----------------|----------|
| C24 | developer (fix); reviewer-quality (verifies in the QUA-21 thread) | PR #17: `tests/e2e/test_gitignore_matching.py` only | Strip the inherited git repository-location variables in `isolated_env`. Add the inherited-`GIT_INDEX_FILE` regression test. CI 10/10 on the new head. If any other file changes, or a new Blocker, Critical or Major is raised, the PR returns as G6 attempt 2. Within scope, the orchestrator moves PGD-14 to In QA once reviewer-quality replies Fixed | Before G7 starts (master confirms C21 and C24 as G7 check 0) |

---

## G6 – Peer Review — STORY-01.01 (PGD-13) — 2026-10-30

- **Decision:** NO-GO. The story goes to Changes Requested, and G6 attempt 2 is required
- **Decided by:** master  ·  **Human override:** none
- **Attempt:** 1 (dev↔review loop 1 of 3)
- **Artefacts evaluated:**
  - PR #22 `feat/PGD-13-redaction`, head `6c5edb4`, base `1ce8473` (13 files; supersedes the closed #18 with an identical tree).
  - Reviews 5708306706 (standards, APPROVE WITH COMMENTS), 5708364198 (quality, REQUEST CHANGES) and 5708338494 (performance, APPROVE).
  - All 18 inline comments and consolidated comment 6515621219, read with `gh api`.
  - SA ruling 6515541757.
  - Check runs on `6c5edb4`: 10/10 (run 41005624066).
  - Jira PGD-13 AC-1..8 and c.10199–10202.
  - `tests/unit/test_sentinel_matrix.py` at `6c5edb4`; master read the harness fixture.
  - The decision was posted on PGD-13 (c.10203) and PR #22 (comment 6515649347) while the checkout was on another story's branch. This record was appended afterwards on `docs/PGD-1-status-sprint-01`.

| # | Check | Mandatory | Result | Evidence |
|---|-------|-----------|--------|----------|
| 1 | Three reports present | ✱ | ✅ | Three PR reviews on `6c5edb4` |
| 2 | Zero open Blocker/Critical | ✱ | ❌ | **QUA-22 Critical** (`test_sentinel_matrix.py:86-105`; vacuity guard at 195-201). The fixture patches `sys.stdout`/`sys.stderr` at setup, but pytest capture restores its own streams for the call phase, so the matrix never observes stdout or stderr. Mutant M4 (`safe_message` → raw `str(exc)`) passes 21/21. AC-6 names four surfaces and two are unobserved, so under D-40 the AC outcome is not delivered → Critical |
| 3 | Majors fixed or accepted | | ❌ | **QUA-23 Major** (`redaction.py:355-374`): `sys.unraisablehook` and `warnings.warn` print a registered sentinel to stderr (RISK-005, impact 5). Not accepted |
| 4 | Findings cite file:line | | ✅ | All inline comments are anchored |
| 5 | ADR/architecture conformance (D-44) | | ⚠️ | STD-33: the SA acknowledged the `(?<!\w)code` guard on condition of explicit `code_verifier`, `auth_code` and `device_code` keys plus test rows (6515541757) |
| 6 | Other ACs / CI | | ✅ | AC-1..5, 7 and 8 met (quality AC table); CI 10/10; no new dependency; layering proven (AC-7) |

**Dispositions**
| Finding(s) | Severity | Disposition |
|---|---|---|
| QUA-22 | Critical | Fix now: capture the streams in the call phase; make the vacuity guard per surface; M4 must fail with capture on |
| QUA-23 | Major | Fix now: a redacting `sys.unraisablehook` plus `logging.captureWarnings(True)`; add `unraisable-exception` and `library-warning` rows; narrow the over-claiming docstrings |
| STD-33 | Minor + SA condition | Fix now: the SA's pattern and test rows (D-44) |
| STD-29, STD-31, STD-32 | Minor | Fix now |
| STD-30 | Minor | Split: docstring fixed now; argparse redaction deferred → [#23](https://github.com/sankumar76/pdf-download-gmail/issues/23) (STORY-07.01) |
| QUA-24 (+ PERF-10 Info) | Minor | Defer → [#24](https://github.com/sankumar76/pdf-download-gmail/issues/24) (STORY-01.04; the SA signs off the patterns) |
| STD-37 | Info | Fix the docstring's first line now (over-claim); no action on the `__all__` part |
| `test_stack_info_is_redacted` (standards cross-reference) | — | Mutation-check now; fix if vacuous |
| STD-34, 35, 36, QUA-25, QUA-26, PERF-09 | Info | No action. QUA-26 is recommended together with the QUA-23 fix |

**Conditions / remediation**
| # | Owner agent | Artefact | Required change | Due gate |
|---|-------------|----------|-----------------|----------|
| R1 | developer | PR #22 (`gmail_pdf/redaction.py`, `gmail_pdf/cli/main.py`, tests under `tests/unit/`, `tests/support/sentinels.py`) | Fix QUA-22, QUA-23, STD-33 (SA pattern), STD-29, STD-31, STD-32, the STD-30/STD-37 docstrings, and the stack-info test check | G6 attempt 2 |
| R2 | reviewer-quality, reviewer-standards | PR #22 | Re-review the delta. Quality re-runs the mutation set: M4 and the two new paths must fail when unprotected | G6 attempt 2 |
| R3 | solution-architect | PR #22 reply on 6515541757 | Confirm that the implemented key/value pattern matches the ruling | G6 attempt 2 |
| — | scrum-master | STORY-07.01 and STORY-01.04 when drafted | Carry #23 and #24 as ACs | Sprint-02 G4 |

**Risks registered:** none new. RISK-005 stays at 10 🟡 until PGD-13 passes G7.
**Rationale:** The G6 pass criterion fails. QUA-22 leaves AC-6's stdout and stderr surfaces unverified, and those surfaces are the core NFR-012 evidence for the story that carries the project's safety premise (GOAL-05, RISK-005). QUA-23 is a real leak path. Both fixes are small. Because a Critical was open, closure needs a G6 attempt 2 by master, not the scoped exit used for Minor leftovers. The deferrals go to the stories that first produce the affected strings (#23, #24). G6 is not in `HUMAN_APPROVAL_POINTS`.

---

## G7 – QA Acceptance — STORY-01.02 (PGD-14) — 2026-10-30

- **Decision:** GO (ACCEPT). The story may move to Done. **Merging PR #17 needs the delivery lead** (`MERGE_POLICY = docs-auto, code-human`). **Merge precondition:** all 10 CI jobs green on the PR head `1ef31e8` (a docs-only commit with the test report). Its run was still in progress when this decision was taken
- **Decided by:** master  ·  **Human override:** none
- **Attempt:** 1
- **Artefacts evaluated:**
  - `docs/07-qa/PGD-14-test-report.md` at `1ef31e8`, read in full. The code under test is `6bd795b`.
  - C24 diff `39e1f18..6bd795b`: only `tests/e2e/test_gitignore_matching.py`.
  - `6bd795b..1ef31e8`: only the report.
  - QUA-21 thread: developer reply plus reviewer-quality "Verified fixed".
  - Check runs on `6bd795b`: 10/10 (run 41005608058).
  - Jira bugs PGD-65 and PGD-66, GitHub #25 and #26.
  - QA PR comment 6515703358 and Jira c.10207.
  - C19 artefact: `docs/07-qa/test-plan.md` at 62976ec (333 lines).

| # | Check | Mandatory | Result | Evidence |
|---|-------|-----------|--------|----------|
| 0 | Conditions closed (C21, C22, C24; C19 due at this G7) | | ✅ | **C21** closed at the G6 exit (39e1f18). **C22** closed (SA comment 6515049452). **C24** closed: the delta stayed in its one-file scope, reviewer-quality verified it by probe (outer index byte-identical; `GIT_DIR` case clean), and CI is 10/10 on `6bd795b`. **C19** closed: `test-plan.md` exists and contains the D-21/PQ-02 exit-code confirmation, the C12/CC-02 ratio-0.6 benchmark case (§ "Ratios r"), the no-traceback check for the hook and CLI (§11) and the G8 pip-audit re-run |
| 1 | Every AC has a verification result with evidence | ✱ | ✅ | Report matrix: AC-1..5 pass with fresh evidence. AC-1: mutation (removing any of 13 patterns fails the tests) plus probes in four temp repos (LF/CRLF, case rules). AC-2: POSIX modes verified **on Linux as non-root** in a `python:3.12-slim` container under umask 022, 077, 000 and 002; macOS is CI-only (green). AC-3: fault injection plus a kill between write and replace. AC-4: more than 30 path shapes on Windows and Linux, including NUL, and it never raises. AC-5: a force-added secret is reported, and gitleaks is green in CI |
| 2 | No open Sev-1/Sev-2 defects | ✱ | ✅ | Sev-1/2/3: 0. New Sev-4: DEF-003 (PGD-65, #25) and DEF-004 (PGD-66, #26) |
| 3 | Regression suite recorded and green | ✱ | ✅ | Windows 3.12: 398 passed, 11 skipped (the POSIX-only tests, each with a stated reason), repeatable and per-file isolated. Linux subset: 88 passed, 3 Windows-only skips. Coverage 99.42 %, diff-cover 100 %. ruff, mypy and bandit clean. CI 10/10 on `6bd795b` |
| 4 | Exploratory notes present | | ✅ | 90-minute charter (EC-5, EC-1); 8 observations; 2 defects |
| 5 | Accessibility (UI stories) | | n/a | No UI |
| 6 | G6 re-checks | | ✅ | QUA-15 (Major, D-45), QUA-16 and QUA-21 re-verified fixed by QA on both operating systems |

**Defect and observation dispositions**
| Item | Disposition |
|---|---|
| DEF-003 · [PGD-65](https://sankumar76.atlassian.net/browse/PGD-65) · [#25](https://github.com/sankumar76/pdf-download-gmail/issues/25) (Sev-4 product): a NUL or nameless path raises a raw `ValueError` where the docstring promises `PrivateFileError`; no content leaks | Keep open. **Target:** the next story that edits `infra/paths.py`, which is STORY-01.03 (defaults and precedence), before its G5. STORY-01.03 is also where user-supplied paths first reach these helpers, so the contract must hold there |
| DEF-004 · [PGD-66](https://sankumar76.atlassian.net/browse/PGD-66) · [#26](https://github.com/sankumar76/pdf-download-gmail/issues/26) (Sev-4 test): the `.gitignore` tests miss over-broad patterns and an appended `!secrets/` | Keep open. **Target:** the next story that edits `.gitignore` or its tests, and no later than the sprint-02 G4, where the scrum-master schedules it |
| Obs. 1: backup and case variants (`token.json.bak`, `*.pem`, `Token.json` on case-sensitive file systems) are not ignored | Not a defect: SEC-05 and AC-1 name exactly the delivered patterns, and gitleaks is the second control. **C26:** the solution-architect proposes, and the product-manager accepts or declines, an extension of the pattern list (backup suffixes, `*.pem`, case variants) by the sprint-02 G4. If accepted, it becomes an AC of the next `.gitignore` story together with DEF-004 |
| Obs. 2 and 4: a stale `.token.json.<hex>.tmp` survives a kill and is never swept; concurrent writers on Windows can fail | Constraints for STORY-01.04, added to [#20](https://github.com/sankumar76/pdf-download-gmail/issues/20): sweep stale `.token.json.*.tmp` when writing, and keep a single writer thread for the token. Both fail safe today (`0600`, ignored by git, content valid) |
| Obs. 3: advisory false positives (`\\?\`, UNC admin share, relative home, literal `~`) | No action for PGD-14 (fail safe). STORY-01.03 must `expanduser` user-supplied paths (carried with DEF-003) |
| Obs. 5–8: symlink tightening, no parent `fsync` (SA: optional), noisy `_discard` log, unstripped minor git variables | No action |

**Conditions / remediation**
| # | Owner agent | Artefact | Required change | Due gate |
|---|-------------|----------|-----------------|----------|
| C25 | scrum-master | Jira (STORY-01.03 when drafted; sprint-02 plan) | Link DEF-003 (#25) to STORY-01.03 with "before G5" and add an `expanduser` AC (Obs. 3). Schedule DEF-004 (#26) | Sprint-02 G4 |
| C26 | solution-architect (proposal), product-manager (decision) | `docs/04-architecture/` §10.1 `.gitignore` list; decision-log entry via master | Decide whether to extend the secret patterns with backup suffixes, `*.pem` and case variants (Obs. 1). Scope goes through the PM (CLAUDE.md §6.6) | Sprint-02 G4 |

Follow-ups (not conditions):
- qa-engineer: move PGD-14 to Done.
- orchestrator: request the human merge with the precondition above.
- master: comment on #20 adding Obs. 2 and 4.

**Risks registered:** none new. RISK-005 is partly evidenced: secret files are kept out of git and protected on disk (PGD-14). The score stays at 10 🟡 until redaction (PGD-13) passes G7. RISK-009 is partly mitigated by `downloads/` in `.gitignore`.
**Rationale:**
- All three mandatory G7 items have file-, CI- and Jira-level evidence.
- Every AC was verified on the code under test, including a non-root Linux run for the POSIX modes that Windows cannot exercise.
- The G6 Major (QUA-15) and the two isolation fixes were re-verified independently.
- The two Sev-4 defects fail no AC. Each is routed to the story that next touches its code.
- The project test plan (C19) now exists with every element required at the PGD-12 G7.
- G7 is not in `HUMAN_APPROVAL_POINTS`, but the code merge is human under `MERGE_POLICY`.

**Post-decision note (2026-10-30, G6 PGD-13 attempt 2):** the merge precondition above is met. Master read the check runs: 10/10 success on `1ef31e8`, and 10/10 on the merge commit `27876b6`. Santhosh merged PR #17 at 2026-10-30T09:06:37Z and approved it explicitly on PGD-1 c.10212 (request c.10210). No numbered condition closes with this: C25 and C26 stay open, due at the sprint-02 G4.

---

## G6 – Peer Review — STORY-01.01 (PGD-13) — 2026-10-30

- **Decision:** CONDITIONAL GO. Fix-now items (C27) must land and be verified before G7 starts. The story stays in Changes Requested until then
- **Decided by:** master  ·  **Human override:** none
- **Attempt:** 2 (dev↔review loop 2 of 3)
- **Artefacts evaluated:**
  - PR #22 `feat/PGD-13-redaction`, head `146236f`, base `1ce8473`, 14 files; delta `6c5edb4..146236f`.
  - Reviews 5716488827 (standards, APPROVE WITH COMMENTS), 5716664769 (quality, APPROVE WITH COMMENTS) and 5708338494 (performance, APPROVE, attempt 1; not repeated under the exit rule).
  - Inline findings QUA-27..30, STD-38, STD-39, read with `gh api`. Consolidated comment 6530170538.
  - SA ruling 6515541757 and confirmation 6529841053.
  - Check runs on `146236f`: 10/10 (run 41102046435). `mergeable_state` clean; `main` is `27876b6`; PR #22 and `main` changed no common file since `1ce8473` (master compared both file lists).
  - Jira PGD-13 AC-1..8 and c.10214–10218.
  - `gmail_pdf/redaction.py`, `gmail_pdf/cli/main.py` and `tests/unit/test_sentinel_matrix.py` read at `146236f`.
  - Master's own probes, below.

| # | Check | Mandatory | Result | Evidence |
|---|-------|-----------|--------|----------|
| 1 | Three reports present | ✱ | ✅ | Two re-reviews on `146236f`; performance from attempt 1, per the exit rule |
| 2 | Zero open Blocker/Critical | ✱ | ✅ | QUA-22 closed. Master read `Harness.run` (redirect in the test body) and the per-surface guard. Master's run: matrix 29 passed. M4 injected in memory, normal pytest capture: `chained-exception-message-stdout` and `-stderr` fail, 2 failed, 27 passed |
| 3 | Majors fixed or accepted | | ⚠️ | QUA-23 closed: 0 sentinels for `__del__` and `warnings.warn` on 3.12.10 and 3.14.7. **QUA-27 re-rated Major (D-46): open, fix now under C27** |
| 4 | Findings cite file:line | | ✅ | All new inline comments are anchored |
| 5 | ADR/architecture conformance (D-44) | | ✅ | SA 6529841053 confirms the pattern. Master compared the compiled source with the ruling: identical with whitespace removed. `status_code` and `zipcode` stay readable; `code_verifier`, `auth_code` and the `code=` value are redacted |
| 6 | Exit rule of attempt 1, other ACs, CI | | ✅ | R1, R2 and R3 done. 9 of 9 original and 8 of 8 new-protection mutants killed on the reviewer's own export. AC-6 now met. CI 10/10. Orchestrator rerun 569 passed, 99.68 %, ruff and mypy --strict clean |

**Master's QUA-27 probes** (real child interpreters at `146236f`, stderr counted, sentinel `SENTINEL-CLIENT-SECRET-0001`; 3.12.10 / 3.14.7). The fix column is the reviewer's helper at all three format sites plus a guard in `_handle_uncaught`, patched in memory; the branch was not changed.

| Case | Trigger | Head | With fix |
|---|---|---|---|
| 1a | `__del__`, exception with a raising `__cause__` property | 1 / 1 | 0 / 0 |
| 1b | Uncaught exception of that type, sentinel in its message | 2 / 2, "Original exception was:" | 0 / 0 |
| 1c | Same in a worker thread | 0 / 0 | 0 / 0 |
| 2a | Ordinary `RuntimeError`, `traceback.format_exception` fails (simulated `MemoryError`) | 1 / 1, raw original | 0 / 0 |
| 2b | Ordinary `RuntimeError`, `redact` fails (simulated) | 1 / 1, raw original. The helper alone still gives 1 / 1 | 0 / 0, nothing printed |
| 2c | Ordinary `RuntimeError` raised from `SyntaxError("x", ("f", 1, 1, 5))`: stdlib types, no simulation | 1 / 0 | 0 / 0 |
| 3a | `logger.exception` on a filtered handler, raising `__cause__` | 3 / 3, caller aborted | 0 / 0, caller continues |
| 3b | `main` with a failure of that type in `_run` | 3 / 3 | 0 / 0 |
| Shutdown | Object alive at exit whose `__del__` raises, installers called directly | 0 sentinels; about 630 bytes on both versions | 0 bytes |

Limits of this evidence: the fix was patched in memory, not implemented. The first 3a run used an unfiltered handler and was discarded and repeated. The reviewer saw the shutdown noise through `cli.main.main` on 3.14.7 only; master saw it on both versions with the installers called directly.

**Dispositions**
| Finding(s) | Severity | Disposition |
|---|---|---|
| QUA-27 `gmail_pdf/redaction.py:368`, extended to `:339` and `:161` | **Major** (re-rated, D-46) | **Fix in this PR** (C27) |
| QUA-28 `tests/unit/test_redaction_logging.py:256` | Minor | **Fix in this PR** (C27). About four lines. It restores handler-level proof for the stack text the AC-3 row of the PR claims; attempt 1 item 9 kept the test honest at filter level only. Over-claiming evidence is fixed now on this project |
| STD-38 `gmail_pdf/redaction.py:118` | Minor | **Fix in this PR** (C27). Coding Standards §10 sets 100; the line is 115. A commit is needed anyway, a tech-debt issue would cost more than the wrap, and the D-44 test rows guard it |
| QUA-29 `tests/unit/test_sentinel_matrix.py:126-127` | Info | No action. N1 and N2 fail the matrix today, and C27 verification proves the child wiring again through the `hook-failure` row. Optional in the C27 commit |
| QUA-30 `gmail_pdf/redaction.py:184-186` | Info | No action. Safe today. Issue #19 tracks later handlers; STORY-07.02 passes its run-log handler to `install_logging_redaction` |
| STD-39 `tests/unit/test_redaction_logging.py:198` | Info | No action: accepted idiom |
| SA note: a handler added without `install_logging_redaction` prints a registered secret in warning text | Not a finding | Already on #19 and #20. Not a defect while no real handler exists |
| STD-34, 35, 36, QUA-25, PERF-09 | Info | No action, as at attempt 1 |

No Major or Minor finding is deferred, so no new tech-debt issue is needed. #23 and #24 stand.

**Conditions / remediation**
| # | Owner agent | Artefact | Required change | Due gate |
|---|-------------|----------|-----------------|----------|
| C27 | developer (fix); reviewer-quality and reviewer-standards (verify); orchestrator (G5 rerun, CI) | PR #22: `gmail_pdf/redaction.py`, `tests/unit/test_redaction_hooks.py`, `tests/unit/test_redaction_logging.py`, `tests/unit/test_sentinel_matrix.py` only | (1) **QUA-27:** no exception escapes `sys.excepthook`, `threading.excepthook`, `sys.unraisablehook` or `RedactingFilter.filter`, whatever fails inside. Reviewer's helper at all three format sites plus a guard that also covers `_write_stderr`; the outcome is binding, placement is the developer's choice. If `redact` itself fails, keeping the fixed line is better if it stays small. Docstrings claim only what holds. (2) **Tests:** unit tests with `traceback.format_exception` and `redact` failing, for each entry point; a `hook-failure` path in `ERROR_PATHS` in a child interpreter with a real uncaught exit (the child return-code assertion may take an expected value). (3) **QUA-28:** the reviewer's logger-level stack test. (4) **STD-38:** wrap line 118; source identical to the SA ruling with whitespace removed. **Verified by:** orchestrator, local rerun and CI 10/10 from check runs on the new head; reviewer-quality, own export, the probes above on 3.12.10 and 3.14.7, each guard removed in turn and a named test failing, including `hook-failure` on stderr, N8 failing the new stack test, "Verified fixed" in the QUA-27 and QUA-28 threads; reviewer-standards, STD-38 and the new diff. No new SA confirmation if the whitespace-stripped source is unchanged; otherwise D-44 applies again. The orchestrator then moves PGD-13 to In QA. If another file changes, a new Blocker, Critical or Major is raised, or verification fails, the PR returns as G6 attempt 3, loop 3 of 3 (D-47) | Before G7 starts (master confirms C27 as G7 check 0); QA tests the new head only |

**Risks registered:** RISK-023 (stale green run, not-strict protection). RISK-022 closed (D-48). RISK-005 stays at 10 🟡 until PGD-13 passes G7.
**Rationale:**
- Both mandatory items are met: three reports and no open Blocker or Critical. QUA-22 and QUA-23 are confirmed closed by master's own runs, and every attempt-1 exit requirement is evidenced.
- QUA-27 is the same evidence pattern as QUA-15 (D-45): a delivered AC with a hole in its explicit guarantee, so it is Major and fixed before merge. The reviewer's Minor rating rested on a contrived trigger and on line 339 being "pre-existing", but that line is new in this PR and a failed `sys.excepthook` prints the original exception raw.
- It is not Critical, so this is not a NO-GO: every case AC-5 lists passes, no real dependency is known to trigger it, production code registers no secret yet, and its trigger is far narrower than QUA-23's, which was itself Major.
- RISK-005 has impact 5 and the fix is small. Leaving it would ship the redaction story knowing that one failure in a hook undoes it.
- G6 is not in `HUMAN_APPROVAL_POINTS`.
