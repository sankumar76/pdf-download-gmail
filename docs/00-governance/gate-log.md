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

---

## G6 – Peer Review — STORY-01.01 (PGD-13) — 2026-10-30 — attempt 3 (C27 verification failed)

- **Decision:** CONDITIONAL GO, attempt 3. C27 is not closed. Under D-47 the PR returns as G6 attempt 3, loop 3 of 3. The story stays in Changes Requested and does not go to In QA. The label is what the checklist gives when no mandatory item fails; C28 is a **counted** loop and D-47's exemption does not apply to it (D-50)
- **Decided by:** master  ·  **Human override:** none
- **Attempt:** 3 (dev↔review loop 3 of 3, the last)
- **Artefacts evaluated:**
  - PR #22 `feat/PGD-13-redaction`, head `71b590e`, delta `146236f..71b590e`: exactly the four C27 files (master read `git diff --name-status`).
  - Reviews 5717359480 (quality, REQUEST CHANGES) and 5717150462 (standards, APPROVE WITH COMMENTS), with inline QUA-31, QUA-32, QUA-33, STD-40..43, read with `gh api`. Threads r4427511853 (QUA-27, Not fixed) and r4427512278 (QUA-28, Verified fixed). Consolidated comment 6531333500.
  - Performance review 5708338494 (attempt 1).
  - Check runs on `71b590e`: 10/10 success, run 41108747121, read by master. `mergeable_state` clean; `main` is `27876b6`.
  - Jira PGD-13 AC-1..8 and c.10222–10227.
  - `gmail_pdf/redaction.py`, `gmail_pdf/cli/main.py`, `tests/unit/test_redaction_hooks.py` and the `hook_failure` row, read at `71b590e`. Architecture line 172. Coding Standards lines 10, 12 and 70.
  - The reviewer's export of `redaction.py` is byte-identical to the worktree file (`cmp`).
  - Master's own probes, below.

| # | Check | Mandatory | Result | Evidence |
|---|-------|-----------|--------|----------|
| 1 | Three reports present | ✱ | ✅ | Quality and standards on `71b590e`; performance from attempt 1. Master timed the only hot path touched, see below |
| 2 | Zero open Blocker/Critical | ✱ | ✅ | None raised. QUA-31 is not Critical: every case AC-5 and AC-8 list passes, and production code registers no secret yet |
| 3 | Majors fixed or accepted | | ⚠️ | **QUA-31 Major, open, fix now (D-49).** QUA-27 Fixed for `Exception`, Not fixed against the C27 outcome |
| 4 | C27 verification | | ❌ | QUA-27 not verified fixed. F2 and F5 survive, so "each guard removed in turn and a named test failing" is not met. QUA-28 and STD-38 closed |
| 5 | ADR/architecture conformance (D-44) | | ✅ | Whitespace-stripped pattern identical to the SA ruling (both reviewers, by script). No new SA confirmation needed |
| 6 | Findings cite file:line | | ✅ | All inline comments are anchored |
| 7 | CI / G5 | | ✅ | CI 10/10 read by master; orchestrator rerun 621 passed, 99.70 %, ruff, mypy --strict, bandit clean |

**Master's probes** (real child interpreters at `71b590e`, `-I -B`, sentinels counted on stdout plus stderr, 3.12.10 / 3.14.7; sentinel `SENTINEL-CLIENT-SECRET-0001`). "Fix" is `except BaseException` at lines 398 and 423 patched in memory; the branch and the worktree were not changed. `git status` of the worktree was unchanged afterwards.

| # | Case | `71b590e` | Fix |
|---|---|---|---|
| P1 | Ordinary `RuntimeError` through the hook, real `interrupt_main()` after the fixed line | 1 / 2, "Original exception was:" | 0 / 0, exit 1, fixed line |
| P2 | Non-`Exception` raised inside the hook, through `cli.main.main` | 3 / 4, raw | 0 / 0, exit 1 |
| P3 | One real interrupt during `report_unexpected_failure`, through `main` | 0 / 0, `Run cancelled`, exit `0xC000013A` | same |
| P4 | Two real interrupts, through `main`, timing forced | 1 / 2, raw | 0 / 0 |
| P5 | Real interrupt inside `_unraisable_hook`, mid-run | run continues, 419 bytes of noise | run continues, 0 bytes |
| P6 | `SystemExit(7)` inside `sys.excepthook` | 0 sentinels, exit 7 | 0 sentinels, exit 1 |
| P7 | `SystemExit(7)` inside the worker hook | 0 sentinels, run continues | same |
| P8 | Real interrupt in the filter, line 181 kept as `Exception` | not run | run stops, `Run cancelled` |
| P8' | Same with line 181 also widened to `BaseException` | not run | **run continues: the Ctrl+C is lost** |
| P9 | Non-`Exception` through `logger.exception`, main thread | 3 / 4, raw | 0 / 0, exit 1 |
| P9b | Same in a worker thread | 1 / 1 | 0 / 0 |
| P10 | Real interrupt delivered at `_handle_uncaught` entry, before the `try` (forced with `sys.settrace`) | 1 / 2, raw | **1 / 2, raw: not closed** |
| P11 | `redact` fails, record with `args` and `stack_info`, raw second handler | 0 / 0; F2 2 / 4; F5 2 / 2 | not run |

Limits of this evidence: the fix was patched in memory, not implemented. P4 and P10 force the timing. No physical key press was used. The first P11 run died on my own hand-built record (rc 1, no `CONTINUED`) and was discarded and repeated. Some counts differ from the reviewer's X-cases by one; the probe bodies differ and the outcome is the same. pytest was not run on the fix by master; the reviewer's scratch copy gave 621 passed.

**Performance check:** `RedactingFilter.filter`, best of 7 runs of 20,000 records, two repeats on 3.12.10: 6.27 and 6.20 µs per record at `146236f`, 6.25 and 6.31 at `71b590e`. No change.

**Dispositions**
| Finding(s) | Severity | Disposition |
|---|---|---|
| QUA-31 `gmail_pdf/redaction.py:398, 423` | **Major** (confirmed, D-49) | **Fix now** (C28) |
| QUA-27 | Major | **Fixed for `Exception`, Not fixed against the C27 outcome.** Closes with QUA-31 against the outcome restated in D-49. The thread stays open |
| QUA-32 `redaction.py:183, 186` | Minor | **Fix now** (C28). Redaction path, and C27 asked for it |
| STD-41 `tests/unit/test_redaction_hooks.py:371, 411, 429, 446` | Minor | **Fix now** (C28). Same lines as the new breakers, and a deferral would cost more |
| QUA-33 `tests/unit/test_sentinel_matrix.py:263` | Info | **Fix now** (C28). Marker line. A row that can silently become a no-op is not left on a security story |
| STD-40 `redaction.py` 453, `test_redaction_hooks.py` 467 lines | Minor | **Inline justification now** (C28), as Coding Standards line 10 allows. Splitting is **not allowed in this loop**. The test-file split is deferred to STORY-01.04 (TD-B) |
| STD-42 `redaction.py:146` | Info | Move the constant in C28, one line |
| STD-43 `redaction.py:162, 172, 433` | Info | Absorbed by the QUA-31 docstrings |
| QUA-28, STD-38 | Minor | **Closed**, verified by the reviewers |
| STD-39, QUA-29, QUA-30 | Info | No action, as at attempt 2 |
| Residual: real interrupt at hook entry (P10), P4 class | Not a finding | **Accepted residual** until STORY-06.02 (D-49, TD-A). Reproducing it is not a finding |
| `main`'s `except Exception` block interrupted: exit `0xC000013A`, not 1 (P3) | Not a finding | Windows, AC-8 edge, no sentinel. Note on TD-A |

**Conditions / remediation**
| # | Owner agent | Artefact | Required change | Due gate |
|---|-------------|----------|-----------------|----------|
| C28 | developer (fix); orchestrator, reviewer-quality, reviewer-standards (verify); solution-architect (acknowledgement) | PR #22: `gmail_pdf/redaction.py`, `tests/unit/test_redaction_hooks.py`, `tests/unit/test_redaction_logging.py`, `tests/unit/test_sentinel_matrix.py` only; no new file; at most two commits, then head H is frozen | (1) **QUA-31:** `except BaseException` at lines 398 and 423 with the reason inline; nothing else widens; lines 163 and 181 stay `except Exception`. Docstrings at 159, 172, 433 and PR deviation 7 claim exactly the outcome restated in D-49, including the entry-window limit. (2) **Tests:** breakers raising `KeyboardInterrupt` and `SystemExit` over the three hooks, wrapped so a failure is a named `pytest.fail`; a test that a `KeyboardInterrupt` during formatting or `redact` still leaves `logger.*`. (3) **QUA-32:** one parametrised test, F2 and F5 must fail it. (4) **STD-41:** `trigger` alone in the shared lists, a mapping for the two stderr tests. (5) **QUA-33:** marker in the child, asserted; T1 must fail. (6) **STD-40:** one sentence of justification in each file. (7) **STD-42:** move the constant. **Verified by:** orchestrator: diff `71b590e..H` within the four files, local rerun, ruff, mypy --strict, bandit, CI 10/10 from check runs on H, merge state clean, tested `main` SHA compared (RISK-023). reviewer-quality, fresh export of H, one run: all probes X1..X17 and P4 on 3.12.10 and 3.14.7, 0 sentinels; Q1, Q2 (398, 423 back to `Exception`), Q3, Q4 (181, 163 widened), F2, F5, T1 each fail a named test; the full set G1..G8, F1..F6, M1..M9, N1..N8, D1 still fails; replies in the QUA-27, QUA-31, QUA-32 threads. reviewer-standards: diff `71b590e..H`; STD-40..43; each broad except carries a reason. solution-architect: one PR comment before G7 GO acknowledging STORY-06.02 as the closure of the residual; not part of the loop. reviewer-performance: not needed. **Clean:** the orchestrator moves PGD-13 to In QA, with no further master decision at G6. **Failure:** see D-50: Santhosh, before any developer run | Before G7 starts (master confirms C28 as G7 check 0); QA tests H only |
| C29 | reviewer-quality (TD-A), reviewer-standards (TD-B), scrum-master (link, plan row) | GitHub tech-debt issues; STORY-06.02 and STORY-01.04; `sprint-01-plan.md` follow-ups | **TD-A → STORY-06.02:** real interrupt at hook entry (P10, P4 class); SIGINT sets the flag so no `KeyboardInterrupt` reaches a hook; test both presses; note the P3 exit code. **TD-B → STORY-01.04:** split `tests/unit/test_redaction_hooks.py` under 400 lines before that story's G5. Both linked by the scrum-master | Sprint-02 G4 |

**Risks registered:** RISK-005 note added. No new risk.

**Rationale:**
- Both mandatory items are met, so the checklist gives CONDITIONAL GO, as D-47 said it would on this kind of evidence. Same evidence, same label, whatever the loop count.
- The likelihood is low and was weighed: a real leak needs a failure carrying a secret, plus a signal or a non-`Exception` inside a window of milliseconds. D-40, D-45 and D-46 do not turn on likelihood. QUA-27's triggers were contrived too, and it was Major. Rating this Minor would give a different answer for the same pattern, in the loop where it would be convenient.
- D-47 is met on two independent limbs: a new Major and a failed verification. A lower rating of QUA-31 would not have changed the result.
- The fix does not close everything. P10 shows that no `except` clause reaches an interrupt delivered before the `try` starts. Claiming otherwise would repeat the over-claim that C27 was meant to end, so the docstrings state the limit and D-49 accepts it.
- G6 is not in `HUMAN_APPROVAL_POINTS`. The human path opens only if C28 fails (D-50).

**Posted:** PR #22 comment 6531522614; Jira PGD-13 c.10228.

---

## G6 – Peer Review — STORY-01.01 (PGD-13) — 2026-10-30 — C28 rating only (D-50), not a new attempt

- **Decision:** no new G6 decision. Seven new findings rated: all Minor or Info. **C28 is closed on `a135b4c`.** Under the exit rule PGD-13 moves to In QA with no further G6 decision; master confirms C28 as G7 check 0, and QA tests `a135b4c` only
- **Decided by:** master  ·  **Human override:** none  ·  **Human approval required:** no
- **Attempt:** none. Loop 3 of 3 stays the last; no developer run
- **Artefacts evaluated:**
  - PR #22 head `a135b4c`; delta `71b590e..a135b4c` read by master: `redaction.py`, `test_redaction_hooks.py`, `test_sentinel_matrix.py`; commits `32304ab`, `a135b4c`.
  - Reviews 5718016476 (quality; correction 6532402803) and 5717840658 (standards) with inline QUA-34..37 and STD-44..46; consolidated verification 6532433039; SA acknowledgement 6531815106.
  - Check runs on `a135b4c`: 10/10 success, read by master. `mergeable_state` clean; `main` `27876b6`.
  - Issues #23, #27, #28, #29. Jira PGD-13 AC-1..8 and c.10230–10235. JQL: no issue labelled `aiid-STORY-06.02`, `aiid-STORY-01.04` or `aiid-STORY-07.01`.
  - Raw reviewer results read, not only the tables: `out.json` for `a135b4c`, 51 cases on 3.12.10 and on 3.14.7, all 18 listed probes present, every case loaded the export, non-zero rows P10, E1, E11 only. Mutant table: all 37 required mutants killed; the only survivors are Q5, Q6, Q7. Q7 log: 649 passed on its own copy.
  - `git show 27876b6:gmail_pdf/cli/main.py`: no `except Exception`, so line 84 is new in this PR.

**C28 exit rule on `a135b4c`**
| # | Item | Result | Evidence |
|---|------|--------|----------|
| 1 | Diff within the four files, no new file, at most two commits | ✅ | Three files, two commits, read by master |
| 2 | Local rerun, ruff, mypy --strict, bandit | ✅ | Orchestrator: 649 passed, 99.70 %; clean |
| 3 | CI 10/10 on H, merge state, tested `main` SHA | ✅ | Run 41116702718, read by master; clean; `27876b6` |
| 4 | X1..X17 and P4 on 3.12.10 and 3.14.7, 0 sentinels | ✅ | `out.json` read by master; P4 reproduced by master |
| 5 | Q1..Q4, F2, F5, T1 and the full set each fail a named test | ✅ | Mutant table read by master |
| 6 | STD-40..43; each broad except carries a reason | ✅ | Fixed. Line 167's reason is in the docstring directly above it (STD-44, Info; ruling below) |
| 7 | Replies in the QUA-27, QUA-31, QUA-32 threads | ✅ | Reviewer-quality, per Jira c.10234 |
| 8 | SA acknowledgement before G7 GO (not part of the loop) | ✅ | 6531815106, qualified; satisfied (D-52) |

**Master's probes** (in memory, worktree unchanged by `git status`; real child interpreters, `-I -B`; fake sentinel `SENTINEL-CLIENT-SECRET-0001`; 3.12.10 / 3.14.7):

| Case | Sentinels | Exit |
|---|---|---|
| P4 on `a135b4c` | 0 / 0 | `0xC000013A` |
| P4 with Q7 | 1 / 1 | `0xC000013A` |
| `_run` raises `SystemExit(<sentinel>)` through `main` | 1 / 1 | 1 |
| `_run` calls `sys.exit(f"error: {exc}")` | 1 / 1 | 1 |
| `_run` raises `SystemExit(0)` | 0 / 0, no output | 0 |

Unit runs in memory on 3.12.10: hooks and logging test files 165 passed with Q7; the reviewer's 8-case test passes on the head and fails 8 of 8 on Q7. Search for text-carrying exits: `gmail_pdf/`, every installed runtime package and the stdlib modules on the runtime path found none that the product reaches; `argparse` exits with an integer, and the other hits are dev tools or command-line entry scripts the product does not import (`click`, `piptools`, `diff_cover`, `idna`, `json.tool`). Limits: in-memory Q7 does not reach child-interpreter tests, so the 649 figure is the reviewer's; P4 forces timing and no physical key was pressed.

**Ratings and dispositions**
| Finding | Reviewer | Master | Disposition |
|---------|----------|--------|-------------|
| QUA-34 `redaction.py:399-400`, cancel branch guard untested; 2 of 24 cases cannot fail | Minor | **Minor** | TD-C (new), STORY-01.04, with #27. Before any change to `_handle_uncaught`, so before STORY-06.02 G5 at the latest |
| QUA-35 `redaction.py:186`, "`BaseException` passes" pinned for `KeyboardInterrupt` only | Info | **Info** | TD-C |
| QUA-36 `redaction.py:444-445`, "fixed line is still printed" holds for `Exception` only | Info | **Info** | TD-C, wording, next time the file is touched |
| QUA-37 `cli/main.py:84`, `SystemExit(text)` prints raw | Info | **Minor, re-rated up** | #23, STORY-07.01. Interim: reviewer-standards checks each G6 diff for text in `sys.exit` or `SystemExit` until #23 closes |
| STD-44 `redaction.py:167` | Info | **Info** | #28, STORY-01.04 |
| STD-45 `test_redaction_hooks.py:3-5` | Info | **Info** | #28; falls away with #27 |
| STD-46 `test_redaction_hooks.py:545` | Info | **Info** | #28, STORY-01.04 |
| E11, forced at hook exit with a tracer, 1 / 1 | Not raised | Not a finding | Same residual class as P10 (D-52); noted on #29 |
| Q5, Q6, Q7 survive | Not listed | **Not a listed check failing** | Rated through QUA-34 and QUA-35 |

**Conditions / remediation**
| # | Owner agent | Artefact | Required change | Due gate |
|---|-------------|----------|-----------------|----------|
| C28 | | | **Closed on `a135b4c`** | Master confirms at G7 check 0 |
| C29 (extended) | scrum-master; reviewer-quality; reviewer-standards | Jira; `sprint-01-plan.md`; GitHub | As recorded at attempt 3, plus: **scrum-master:** create STORY-06.02 in Jira under PGD-7 after the `aiid-STORY-06.02` search, with the SA's six items, the TD-A items and the sprint-01-plan row as ACs, and link #29. Add follow-up rows: STORY-01.04 for #27, #28 and TD-C; STORY-07.01 for QUA-37 on #23. STORY-01.04 and STORY-07.01 have no Jira issue yet, so links go on at creation. **reviewer-quality, before G7 GO:** open TD-C (QUA-34 with its 8-case test and the 2 cases that cannot fail, QUA-35, QUA-36); add QUA-37 to #23; add E11 to #29. | Sprint-02 G4; reviewer-quality items before G7 GO |

**Risks registered:** RISK-005 note changed (D-52). No new risk. Score stays 10 until PGD-13 passes G7.

**Rationale:**
- Each finding was rated on its own evidence, and a rating of Major was tested for each. QUA-34 and QUA-37 were the two where it was arguable; both are argued in D-51, so the delivery lead can overrule them. Both are named in the code-merge request.
- QUA-37 went up, not down, and that does not stop the story. The reviewer's three stated reasons do not carry the rating; the rating rests on AC-5's reach and on no input, timing or exception object on this head reaching the print.
- Master's fix table said "over the three hooks", not "each branch of a hook". That is the second time master's recipe was narrower than its purpose (C27 was the first); the developer delivered what was asked.

**Posted:** PR #22 comment 6532598449; Jira PGD-13 c.10236; #28 comment 6532599519; risk note PGD-1 c.10237.

---

## G7 – QA Acceptance — STORY-01.01 (PGD-13) — 2026-10-30

- **Decision:** GO (ACCEPT). The story may move to Done. **Merging PR #22 needs the delivery lead** (`MERGE_POLICY = docs-auto, code-human`); no merge in this run. The merge precondition and the items to name are below
- **Decided by:** master  ·  **Human override:** none  ·  **Human approval required:** no for G7; the code merge is Santhosh's
- **Attempt:** 1
- **Artefacts evaluated:**
  - `docs/07-qa/PGD-13-test-report.md` at `a84d558`, read in full. The code under test is `a135b4c`.
  - QA summary PR #22 comment 6535886785; Jira PGD-13 c.10242, AC-1..8; PGD-67, PGD-68; #29, #30, #31, #32; `QUA-37` comment on #23.
  - `docs/07-qa/test-plan.md` sections 2, 5, 6, 7, 9, 11, 13, 15; definition-of-done; PRD FR-005, FR-043; architecture lines 172, 296; `sprint-01-plan.md`; PGD-15.
  - Source read on a fresh export: `gmail_pdf/cli/main.py`, `gmail_pdf/redaction.py`, `tests/e2e/test_redaction_subprocess.py`, `tests/unit/test_sentinel_matrix.py`.
  - Check runs: `a135b4c` 10/10 (41116702718); **`a84d558` 10/10 (41146185678), read by master before and after posting the decision, completed, `pull_request` event**. `mergeStateStatus` CLEAN; `main` `27876b6`.

| # | Check | Mandatory | Result | Evidence |
|---|-------|-----------|--------|----------|
| 0 | C28 closed as ruled | | ✅ | `git diff a135b4c a84d558 -- gmail_pdf tests` empty, one commit since (the report). Reviewer-quality items in place: TD-C #30, QUA-37 on #23, E11 on #29. SA acknowledgement 6531815106 (D-52) |
| 1 | Every AC has a verification result with evidence | ✱ | ✅ | QA matrix: AC-1..8 Pass. Master re-ran AC-1, AC-3, AC-5 and AC-8 (below). AC-8 stands with the recorded limit (D-53) |
| 2 | No open Sev-1/Sev-2 defects | ✱ | ✅ | Open: DEF-005 Sev-3, DEF-006 Sev-4. Test plan section 6 says what QA quotes: "test-quality hole that could hide a defect"; "Fix before G8; master may accept with a logged reason" |
| 3 | Regression suite recorded and green | ✱ | ✅ | Master: `a135b4c` 649 passed, 99.70 %, `redaction.py` and `cli/main.py` 100 %; merge ref `ef75d59` 775 passed, 12 skipped. CI 10/10 on the PR head |
| 4 | Exploratory notes present | | ✅ | Charters EC-2 and EC-9, mutation pass of 26 |
| 5 | Accessibility (UI stories) | | n/a | No UI |
| 6 | Sev-3 fixed or accepted (test plan section 5) | | ✅ | DEF-005 accepted for this story's exit (D-54) |
| 7 | Traceability sample | | ✅ | GOAL-05 → FR-005 (PRD line 79) → PGD-13 AC-5 → `tests/e2e/test_redaction_subprocess.py` (`req("AC-5")`). Reverse: `test_sentinel_matrix.py` 33 passed → AC-6 → FR-005 → GOAL-05 |

**Master's probes** (fresh export of `a135b4c`; real child interpreters; hidden console of its own; genuine console `CTRL_C_EVENT`; `SetConsoleCtrlHandler(None, False)` in the child because the harness inherits "ignore Ctrl+C"; fake sentinels; CPython 3.12.10; every child reported the export's `redaction.py`). Scripts in the session scratchpad, folder `g7`. Results were the same through `python -m gmail_pdf`, the root shim and `gmail-pdf.exe`:

| Case | Status | stdout | stderr | Sentinels | Traceback |
|---|---|---|---|---|---|
| `RuntimeError` with a chained sentinel; `KeyError` with a token | 1 | empty | `error: unexpected failure, see the run log` | 0 | no |
| One Ctrl+C during the run | 1 | empty | `Run cancelled` | 0 | no |
| Ctrl+C while `main` reports a failure | `0xC000013A` | empty | the failure line, then `Run cancelled` | 0 | no |
| Second Ctrl+C while `Run cancelled` is reported, no failure (new; timing forced) | `0xC000013A` | empty | `Run cancelled` twice | 0 | no |
| Worker-thread failure | 0 | empty | the failure line | 0 | no |

Literal probes: AC-1 7 characters ignored, 8 redacted. AC-3 five loggers by five levels, 0 sentinels, 17 lines; the four named loggers read WARNING; `httplib2.debuglevel` 0. AC-5 traceback through a logger handler with no filter: contains a traceback, 0 sentinels, 1 `[REDACTED]`; stderr one line. Mutants reproduced on their own exports: M20 649 passed, M23 649 passed, M22 639 passed, M13 609 passed and 10 skipped. With M22 and M13 the handler filter still gives 0 sentinels. Limits: 3.12.10 only; timing in the two limit rows is forced by a wrapper; no physical key was pressed.

**Regression detail.** Merge ref: `ef75d59` (parents `27876b6`, `a84d558`) is the current ref; QA's `d44b60e` was built from `a135b4c`; the two differ by the report only. `-rs` on an export: 1 skip "not a git work tree", 11 POSIX-mode skips. CI on the PR head: Windows 776 passed, 11 skipped; Ubuntu and macOS 784 passed, 3 skipped; 787 in all, so the POSIX rows ran on the legs meant to run them.

**Report corrections** (the report stays as committed: a docs commit restarts CI on the head):
- Skips: the text says 10 POSIX-mode tests; it is 11. The PR comment is right.
- QA did not read the POSIX legs, which test plan section 7 asks for. Master did.
- DEF-006 is pre-existing for stderr as well as stdout.
- NT-06 "Pass" holds for the runner path only; the plan's row says exit 1 and the worker gives 0.
- R-12 target: not EPIC-02/06 (ruling 6).
- Test plan section 9 item 3 asks that the AC-8 test deliver a real event and that a differing status be a Product defect. The shipped test raises `KeyboardInterrupt`; QA's probe delivered the event; the limit stays on #29, not a defect (attempt 3, D-53).

**Rulings and dispositions**
| # | Item | Ruling |
|---|---|---|
| 1 | C28 | Confirmed closed on `a135b4c` |
| 2 | AC-8 | **Stands, with the recorded limit** (D-53) |
| 3 | Regression | Confirmed: 649; 775 + 12 (11 POSIX, 1 export artefact) |
| 4 | DEF-005 · PGD-67 · #31 | **Sev-3 confirmed. Accepted for PGD-13's exit; not required before merge. Target PGD-15, before its G5** (D-54). AC-1 and AC-3 are verified on this head |
| 5 | DEF-006 · PGD-68 · #32 | **Sev-4 stands; not a regression of this story. Target STORY-07.01** (D-55) |
| 6 | R-12 | **Registered as RISK-024, score 4. AC goes to the first story that starts a thread** (D-56) |
| 7 | RISK-005 | **Stays 2 × 5 = 10.** Re-assess at the G7 of STORY-01.04 |
| - | `register_secret` padded values | Not a defect (AC-1 says exact occurrence). STORY-01.04 strips or rejects them (C31) |
| - | `py.warnings` muted until a handler exists | STORY-07.02 decides where they go (C31) |
| - | Pattern gaps (escaped JSON, quoted value with a space) | Same class as #24; named in the merge request |
| - | OQ-5 console encoding | Stays open, with QA's evidence, before the first story that prints file names |

**Conditions / remediation**
| # | Owner agent | Artefact | Required change | Due gate |
|---|-------------|----------|-----------------|----------|
| C30 | scrum-master | Jira PGD-15, PGD-67; `sprint-01-plan.md` linked tech-debt table | PGD-67 blocks PGD-15; remote link to #31; row "in the PGD-15 PR, before its G5; no AC of PGD-15 changes". qa-engineer re-runs M13, M20, M22 and M23 at PGD-15's G7: each must fail | Before PGD-15 starts |
| C31 | scrum-master | `sprint-01-plan.md` follow-up table | Rows: STORY-07.01 DEF-006 AC (#32; closed stream gives the D-21 code with no extra text, in a child process); STORY-06.02 second-press row with P3 (#29); STORY-01.04 strip or reject padded secrets; STORY-07.02 `py.warnings` destination; RISK-024's AC on the FR-038 story if promoted, otherwise the EPIC-09 `gui.worker` story | Sprint-02 G4 |
| C32 | qa-engineer | `docs/07-qa/test-plan.md` | Split NT-06 into runner (exit 1) and worker (fixed line; exit per RISK-024). Point section 9 item 3 at STORY-06.02 and record the #29 limit. Add R-12 with RISK-024, and DEF-003..006 to section 14. Reset OQ-4: its needed-by, PGD-13 G5, passed unanswered and the story uses `req("AC-5")` | Sprint-02 G4 |

**Merge precondition (orchestrator; re-read at the moment of the request):**
1. PR head still `a84d558`, and `git diff a135b4c <head> -- gmail_pdf tests` empty.
2. 10/10 `success` from check runs on that exact head.
3. RISK-023: the `main` that run tested equals current `main`. If not, update the branch and re-read CI. That merge is not a D-50 commit as long as the code diff holds only what `main` brought; if `main` changed `gmail_pdf/` or `tests/`, return to master first. The status branch is not merged to `main` before PR #22.
4. No `REQUEST_CHANGES` review outstanding.

**Items to name in the merge request:** QUA-34 (#30); QUA-37 (#23, T-05); DEF-005 (#31; accepted, target PGD-15, not pinned at merge); DEF-006 (#32); the accepted residual and the `0xC000013A` limit (#29; D-52, D-53; R1 G8 rule); #23 argparse echo; #24 pattern gaps with QA's two new forms; RISK-024; RISK-005 stays 10; STORY-01.04, 06.02 and 07.01 have no Jira issue yet although they carry most of this. The merge unblocks PGD-15..18.

Follow-ups (not conditions): qa-engineer sets Done. orchestrator sets the label and requests the human merge.

**Risks registered:** RISK-024 (new, score 4). RISK-005 re-assessed, unchanged at 10.

**Rationale:**
- All three mandatory items have evidence that master reproduced in part from a fresh export, and QA's figures that master re-ran held.
- GO, not CONDITIONAL GO: no mandatory or checklist item is short. C30..C32 are project-level follow-ups, as C19, C20, C25 and C26 were at earlier G7 GOs.
- The hard questions were AC-8 and DEF-005, and neither is waved through by likelihood. AC-8 turns on what the criterion covers and on the attempt 3 ruling. DEF-005 turns on the difference between evidence about this head and protection for later heads.
- The double press is new evidence that QA's "needs a failure" understates the limit. It stays in class: a second event during the report of the first, and it needed forced timing. It is named to Santhosh rather than left in a table.

**Posted:** PR #22 comment 6536097991; Jira PGD-13 c.10244; #29 comment 6536098631; #31 comment 6536098986; #32 comment 6536099416; risks PGD-1 c.10245.

---

## G6 – Peer Review — STORY-02.02 (PGD-15) — 2026-10-31

- **Decision:** NO-GO. The story goes to Changes Requested, and G6 attempt 2 is required
- **Decided by:** master  ·  **Human override:** none  ·  **Human approval required:** no
- **Attempt:** 1 (dev↔review loop 1 of 3)
- **Artefacts evaluated:**
  - PR #33 `feat/PGD-15-date-range-selection`, head `c847e1a`, base `main` `2743016` (41 files, 8 commits). PR description and Dev Record read in full.
  - Reviews 5720567531 (quality, REQUEST CHANGES; correction 6537777230), 5720364445 (standards, REQUEST CHANGES), 5720404048 (performance, APPROVE WITH COMMENTS). All 29 inline comments read with `gh api`. Consolidated comment 6537798473.
  - SA ruling PR #33 6537214922 and #34 6537220451.
  - Check runs on `c847e1a`: 10/10 `success` (run 41154541843), read by master. `mergeable_state` clean. `main` is still `2743016` (read from the API).
  - Jira PGD-15 AC-1..10 with AC-6 as amended (c.10250), c.10261–10267. PGD-16. JQL: no issue labelled `aiid-STORY-02.04`, `01.04`, `01.07`, `06.01`, `06.02`, `07.01`, `02.08` or `03.02`.
  - Code read at `c847e1a`: `cli/main.py`, `cli/console.py`, `cli/args.py`, `bootstrap.py`, `app/planner.py`, `app/runner.py`, `infra/retry.py`, `infra/gmail_gateway.py`, `domain/errors.py`, `domain/events.py`, `tests/fakes/fake_gmail.py`, `tests/fakes/fake_gmail_json.py`, `tests/unit/test_exit_statements.py`, `tests/e2e/test_select_range.py`.
  - Reviewer evidence: `qual/mut1.jsonl` recounted, 151 mutants, 13 survivors, the same 13 named in the review.
  - Architecture 6.3..6.5, lines 381 and 587; PRD FR-036, FR-038, NFR-001, NFR-002, NFR-006; EPIC-01, EPIC-02, EPIC-06 story lists; test plan NT-01..06, OQ-1; `sprint-01-plan.md` follow-up tables.

| # | Check | Mandatory | Result | Evidence |
|---|-------|-----------|--------|----------|
| 1 | Three reports present | ✱ | ✅ | Three PR reviews, all on `c847e1a` |
| 2 | Zero open Blocker/Critical | ✱ | ❌ | **QUA-39 Critical confirmed** (D-57): AC-6 (iii) names "deeply nested JSON", and a parseable deep file prints the unexpected-failure line |
| 3 | Majors fixed or accepted | | ✅ | STD-48 re-rated Minor (D-58). PERF-11 and PERF-12 stay Major, accepted deferred with conditions (D-59), #35, #37 |
| 4 | Findings cite file:line | | ✅ | All inline comments anchored |
| 5 | Architecture acknowledgement (D-44) | | ⚠️ | Eight acknowledged (D-60). A ninth is owed before G7 GO: fixed build-failure lines bypass `safe_message` (architecture lines 381, 587), which reviewer-standards raised and the SA ruling does not address |
| 6 | Other ACs, CI | | ✅ | Quality AC table: AC-1..5 and 7..10 pass. Orchestrator: 1077 passed, 12 skipped, 99.88 %; ruff, mypy --strict, bandit clean. CI 10/10 |
| 7 | T-05 interim control | | ✅ | Reviewer-standards pass. Master's grep over `gmail_pdf/` and the root shim: the only raises are `raise SystemExit(main())` at `__main__.py:6` and the shim, plus the argparse catch in `cli/main.py:134` |
| 8 | Issues tied to this story | | ⚠️ | #11 and #31 done (four DEF-005 mutants fail 17, 5, 3, 3). **QUA-39 is DEF-001's residual, so #15 stays open** until it is fixed; QA confirms at G7 |
| 9 | Traceability sample | | ✅ | GOAL-01 → FR-012 → PGD-15 AC-2 → `tests/unit/test_planner.py` (`req("AC-2")`). Reverse: `test_select_range.py` `req("AC-6")` → AC-6 → FR-008, FR-012, D-21 |

**Master's probes** (`c847e1a` export and worktree unchanged; real child interpreters, Python 3.12.10 from the PGD-15 venv; `gmail_pdf.__file__` inside the export; scripts in the session scratchpad, folder `g6m`):

| Case | Result |
|---|---|
| `payload.parts` depth 2..244, name at the root | exit 0, `Messages in range: 1` |
| `payload.parts` depth 247, 300, 500, 1000, 1400, 1490 | exit 1, **unexpected-failure line** |
| `payload.parts` depth 1600, 5000, 100000; `"[" * 200000` | exit 1, fixed line |
| Deep list in `resource.x`, depth up to 494 | exit 0 |
| Deep list in `resource.x`, depth 496, 1000, 2900 | exit 1, **unexpected-failure line** |
| Deep list under an unread top-level key, depth 1000, 2900 | exit 0, count 0 |
| `parts` `[5]`, `[null]`, `["x"]` with no root filename; `labelIds` `5`, `null`, `[[]]`; `internalDate` 5000 digits | exit 1, **unexpected-failure line** |
| `latency_s` `"inf"`, `1e300` (**not in the review**) | exit 1, **unexpected-failure line** |
| `page_size` 0 or negative, bad `epoch_bounds`, duplicate ids, bad base64, bad seed | exit 1, fixed line |
| All rows above | one stderr line, no `Traceback`, the content sentinel on no surface |
| `deepcopy` at load only, patched on an export | The deep rows give the fixed line at the sampled depths; an unread deep key stays exit 0. Largest `parts` depth that copies: 248 on 3.12.10 and 3.14.7 |
| Depth cap 200 by an iterative walk, plus shape, date and latency checks, patched on an export | Every row gives success or the fixed line; 199 levels under a top-level key pass, 200 fail. 241 tests of the e2e, fake, bootstrap and planner files pass |
| Real mode, `--tz Mars/Olympus`; reversed range; bad date | 3; 3; 2 (QUA-47 confirmed) |
| `--help` with stdout on a closed pipe | 120 (QUA-46 confirmed) |
| `DateRange` literals for QUA-43 | Havana S=1772946000, Cairo S=1776981600, Pago_Pago S=1767265200, Apia S==E |
| `users().messages()` rebuilt or reused | 1.07 ms or 0.03 ms per request build, best of 5 runs of 500 (PERF-13 confirmed in direction) |
| Raise inside or outside the `except` | `from None` keeps the original on `__context__`; outside the clause it is `None` (STD-51) |
| `CancelToken.wait(3.0)` with `signal.raise_signal` from a helper thread | `KeyboardInterrupt` 2.71 s after the signal (PERF-14 confirmed, one run; no key pressed) |
| The nine STD-48 sample sources | None flagged. `raise SystemExit(x)` and `sys.exit(CONST)` are flagged, so the docstring's "known int constant" branch does not exist |

Limits: 3.12.10 only for the CLI rows; CI covers 3.10 and 3.11 for the suite, not these rows. No real Gmail call was made. The candidate fixes were patched on exports and are not an implementation. First-run figures for quota are the SA's arithmetic; master checked the sums, including 15.0, 16.1, 10.0 and 11.1. One SA sentence is conditional: "at least 20 min" if `get(full)` takes 600 ms or more needs `attachments.get` at 600 ms too; with 300 ms it is 15 min (for the #34 docs). The first posted text said the `deepcopy` limit moves with Python version; measurement did not show that, and PR comment 6537957962 corrects it.

**Rulings** are in D-57..D-63. In short:
- **QUA-39** stays Critical, and the finding is wider than reviewed (`latency_s`).
- **STD-48** is Minor. T-05 stays a review step; the test is a guard.
- **PERF-11:** pacing is a mitigation of throttling, not of the time floor, so the reviewer's condition is not satisfied by the SA's ruling, but its deadline has not passed. No escalation today; armed through C33 and C36.
- **PERF-12:** uncaught is correct in this story. Isolation belongs in the application-layer per-message loop.

**Dispositions**
| Finding(s) | Reviewer | Master | Disposition |
|---|---|---|---|
| QUA-39 | Critical | **Critical** | Fix now, R1 |
| STD-48 | Major | **Minor**, re-rated down | Fix now (docstring over-claim; a commit lands anyway) |
| PERF-11 | Major, conditional | **Major** | Accepted deferred; no code change; #35; closes on Q-15 |
| PERF-12 | Major, conditional | **Major** | Accepted deferred; #35 (pacer), #37 (isolation) |
| QUA-40, 41, 42, 43, 44 | Minor | Minor | Fix now: seven real test gaps, each a few lines |
| QUA-47 | Minor | Minor | Docstrings now; behaviour to PGD-16 (C34) |
| QUA-49 | Minor | Minor | Fix now: test-strategy 6 lists 403 and 500; RISK-005 surface |
| STD-49, 50, 51, 52, 56 | Minor | Minor | Fix now. STD-51 takes the code option, so "dropped" is true. STD-56 by inline justification (463 and 404 lines; the review's 464 and 405 are one high) |
| PERF-13 | Minor | Minor | Fix now: one line in a file already being changed |
| QUA-45 | Minor | Minor | Deferred, #35: the code follows architecture 6.4, so the SA rules first |
| QUA-46 | Minor | Minor | Deferred, #32, STORY-07.01: DEF-006's class (D-55) |
| QUA-48 | Minor | Minor | Deferred, #36, STORY-01.04: its first consumer (D-41 rule) |
| STD-53, QUA-51 | Minor, Info | Same | Deferred, #37, STORY-06.01: the type is shaped by its consumer |
| STD-54 | Minor | Minor | Deferred, #21, before STORY-01.03: needs the first producer |
| STD-55 | Minor | Minor | Deferred to PGD-16, which rewrites those sentences (C34) |
| STD-57 | Minor | Minor | No action: the squash-merge removes it; no history rewrite |
| PERF-14 | Minor | Minor | Deferred, #29, STORY-06.02 as an AC |
| PERF-15, PERF-16 | Info | Info | #35 before STORY-01.07; #36 |
| STD-58 | Info | Info | #23, STORY-07.01 |
| QUA-50, STD-59 | Info | Info | No action |

**Remediation (fix list, all developer, attempt 2)**
| # | Item | Sev | ACs | Files | Required outcome |
|---|---|---|---|---|---|
| R1 | QUA-39 | Critical | AC-6 (iii) | `tests/fakes/fake_gmail_json.py`, `tests/e2e/test_select_range.py`, `tests/unit/test_fake_gmail_canonical.py` | **Binding:** for any file content, the AC-6 command ends in success or in exit 1 with exactly `FAKE_MAILBOX_UNREADABLE_LINE`; content never produces the unexpected-failure line. Covers any `Exception` caused by content at load, in `list_message_ids` with the baseline query, and in `get_message` for each id. Not claimed: `MemoryError` on a huge file; reads added by later stories, which keep this rule. **Method:** validate at load, with an explicit iterative depth cap over the whole document. `bootstrap.py` does not change. **E2e rows:** the cap passes, cap + 1 fails; `parts` 247, 1000, 1400; resource 500, 2900; unread top-level key 2900; `parts` `[5]`, `[null]`, `["x"]` with no root filename; `labelIds` `5`, `null`, `[[]]`; `internalDate` 5000 digits; `latency_s` `"inf"`, `1e300` |
| R2 | STD-48 | Minor | T-05 | `tests/unit/test_exit_statements.py` | Flags `import sys as s`, `from sys import exit [as x]`, builtin `exit`/`quit`, a name bound to `sys.exit` or `SystemExit`, a `SystemExit` subclass; one negative case each. Docstring says what is accepted and what is not covered (`getattr`, `parser.error`/`parser.exit`, third-party code, a local `main`) |
| R3 | QUA-40 | Minor | AC-7 | `tests/unit/test_retry.py` | 408, 409; 400 and 404 with a rate-limit reason |
| R4 | QUA-41 | Minor | AC-5, FR-043 | `tests/unit/test_cli_select_range.py` | Cancelled summary through `main` gives `(1, "Run cancelled\n", "")` |
| R5 | QUA-42 | Minor | AC-7, AC-8 | `tests/integration/test_gateway_httpmock.py` | `cache_discovery=False` asserted; a 503 on `get_message` logs `Retrying get_message:` |
| R6 | QUA-43 | Minor | AC-3 | `tests/unit/test_daterange.py` | Literal rows: Havana, Cairo, Pago_Pago, Apia, values above |
| R7 | QUA-44 | Minor | AC-10, FR-008 | same | Exact sentence asserted |
| R8 | QUA-47 | Minor | AC-6 text | `gmail_pdf/cli/main.py`, docstrings only | Lines 23 and 163 state the real-mode exits |
| R9 | QUA-49 | Minor | AC-7, FR-005 | `tests/unit/test_sentinel_matrix.py`, gateway docstring | Rows for 403, 500, non-JSON 403; docstring names the library's 403 log line |
| R10 | STD-49 | Minor | none | `gmail_pdf/infra/gmail_gateway.py` | One named alias carrying the justification |
| R11 | STD-50 | Minor | AC-7 | `gmail_pdf/infra/retry.py` | `call_with_retry` at most 40 lines, behaviour unchanged |
| R12 | STD-51 | Minor | AC-7, FR-005 | gateway, `gmail_pdf/domain/errors.py` (docstring only), `tests/integration/test_gateway_httpmock.py` | Domain error raised outside the `except`; test asserts `__context__ is None` |
| R13 | STD-52 | Minor | none | `gmail_pdf/app/planner.py`, `gmail_pdf/app/runner.py`, docstrings only | Complete `Raises:` |
| R14 | STD-56 | Minor | none | `tests/unit/test_sentinel_matrix.py`, `tests/fakes/fake_gmail.py`, comment only | One-line justification |
| R15 | PERF-13 | Minor | AC-4 unchanged | gateway | `messages()` built once in `__init__` |
| R16 | PR text | | | PR #33 description | Correct decision 4, item 10 ("enforces") and "correctness is unaffected" |

**Exit rule, G6 attempt 2, loop 2 of 3 (D-62):**
1. **Orchestrator, new head H:** project commands; CI 10/10 from check runs; tested `main` SHA (RISK-023); diff only in the files above. A file outside the list: stop and ask before pushing.
2. **reviewer-quality, own export of H, delta only:** every R1 row; a sweep of depth 1..3000 in steps of 25 in `parts` and in the resource, each a success or the fixed line, 0 unexpected-failure lines; each new check removed in turn fails a named test; `d-fold-1`, `r-add-408`, `r-reason-any-status`, `g-cache-discovery`, `g-method-name-in-log`, `m-return-0`, `tz-system-empty` now fail; restoring `from None` fails; retry mutants re-run after R11; replies in the threads.
3. **reviewer-standards, delta only:** STD-48 forms each flagged; STD-49..52, 56; R15 read; T-05 on H.
4. **reviewer-performance:** no re-review, unless the gateway or retry diff goes beyond R9..R12 and R15.
5. **solution-architect:** does not review the fix. Owes one PR reply before G7 GO (C37).
6. **Master decides attempt 2** on that evidence. All pass and no new Major or higher: GO, PGD-15 moves to In QA; QA tests H only and re-runs M13, M20, M22, M23 (C30).
7. **New Minor or Info in the delta:** rating only, a tech-debt issue, no commit. A reviewer's added mutant is a finding, not a listed check (D-51). Items ruled here are not reopened. A delta finding is measured against `main` (D-46).
8. **A miss on a Minor item alone:** fixed in the same file under D-47, no new attempt.
9. **A miss on R1, an unapproved file, or a new Major or higher:** attempt 3, loop 3 of 3, the last; after that, Santhosh, under the orchestrator's limit. A CI rerun after an infrastructure failure is not a failure.

**Conditions**
| # | Owner agent | Artefact | Required change | Due gate |
|---|-------------|----------|-----------------|----------|
| C33 | scrum-master, product-owner | `sprint-01-plan.md` follow-up table; Jira | Rows: STORY-02.04 pacer AC, "must merge before STORY-01.04" (#35); STORY-01.04 (#36); STORY-01.07: `get(full)` latency, 403/429 counts, `Retry-After` seen or not, project quota, counts only (#34, Q-14); STORY-02.08: pacer off and on; STORY-03.02: one `get(full)` per message; STORY-06.01 (#37); STORY-06.02 PERF-14 (#29); STORY-07.01 QUA-46 (#32). Then create STORY-02.04 in Jira after the `aiid-` search, with a Blocks link to STORY-01.04 when that exists. **STORY-01.04 may not be Ready until STORY-02.04 exists with the pacer AC** | Rows before PGD-15 G7 GO; Jira by the sprint-02 G4, with C29 |
| C34 | product-owner, scrum-master | Jira PGD-16 | Real-mode rows: neither hook variable set, `--tz Mars/Olympus` and a reversed range each exit 2, not 3, with no credential read; validation runs before `build_deps`. Remove the interim sentences so one table remains (FR-064). STD-55 | Before PGD-16 starts |
| C35 | qa-engineer | `docs/07-qa/test-plan.md` | NT-01 becomes exit 1 with the fixed line; close OQ-1; tie NT-01..05 to PGD-15 AC-6; add the R1 rows to NT-03 and NT-04. The rest of C32 stays due at the sprint-02 G4 | Before the PGD-15 G7 report |
| C36 | product-manager, solution-architect | PRD NFR-001/002, FR-038; ADR-007 | Q-15 proposal. FR-038 trigger reworded so a pacer-on miss does not promote it. ADR-007 gate restated in units against both NFRs, closing CC-02 and IMP-01 (C12 extended). The delivery lead decides before STORY-02.08 is Ready | Sprint-02 G4 |
| C37 | solution-architect | PR #33; architecture; #34 | (a) One reply acknowledging or refusing the ninth deviation. (b) The #34 doc updates, plus 6.4 and 6.5 on an exhausted call. (c) QUA-45 ruling. (d) QUA-48 port shape | (a) before G7 GO; (b) sprint-02 G4; (c) before STORY-02.04 is Ready; (d) before STORY-01.04 is Ready |

**Risks registered:** RISK-025 (new, score 9). RISK-011 raised from 6 to 8. RISK-007, RISK-010 and RISK-021 noted. RISK-005 unchanged at 10.

**Rationale:**
- The label comes from the checklist: a Critical is open, so NO-GO. Master tried to break that reading. The brief's facts are real: test-only hook, exit 1, one line, no leak. They limit the reach, but they do not make a listed case pass, and a rating on this project has turned on the AC's words since D-40. QUA-27 leaked a sentinel and stayed Major because no listed case failed; QUA-22 was a test harness and went Critical because a listed surface was missed. Reading QUA-39 the other way would invert both.
- The cost is one loop, and it is not the reason. With 15 fix items and production edits, a master decision on the next head would be needed anyway.
- STD-48 went down and PERF-11 did not go up, for the same reason: the rule asks what the words say, not how the finding feels.
- The reviewer's QUA-39 recipe missed `latency_s` and an unread deep key, so the outcome is written first and the rows second, as the PGD-13 lessons require.

**Posted:** PR #33 comment 6537950749, correction 6537957962; Jira PGD-15 c.10268; risks PGD-1 c.10269; new issues #35, #36, #37; comments on #21 (6537937814), #23 (6537938120), #29 (6537937382), #32 (6537936974).

---

## G6 – Peer Review — STORY-02.02 (PGD-15) — 2026-10-31 — attempt 2

- **Decision:** GO, under the exit rule D-62. PGD-15 moves to In QA (orchestrator). Loop 3 of 3 is unused
- **Decided by:** master  ·  **Human override:** none  ·  **Human approval required:** no; the code merge stays human
- **Attempt:** 2 (dev↔review loop 2 of 3)
- **Artefacts evaluated:**
  - PR #33 head `7883f9c`, base `main` `2743016`. PR description read in full, including the fix-loop section. Delta `c847e1a..7883f9c`: 16 files.
  - Reviews 5721304055 (quality; correction 6539176633) and 5721115331 (standards), bodies and all 9 inline comments read with `gh api`. Consolidated evidence 6539192141. Review 5720404048 (performance, `c847e1a`) stands.
  - SA ruling 6538205936 and note #34 6538206581. Architecture lines 381, 485, 488, 587 read.
  - Check runs on `7883f9c`: 10/10 `success`, read by master. `mergeable_state` clean. `main` still `2743016`.
  - Commit `b20be4e` (C33 rows). Jira PGD-15, PGD-16, PGD-18. Issues #15, #35, #37.
  - Code read at `7883f9c`: `tests/fakes/fake_gmail_json.py`, `tests/fakes/fake_gmail.py`, `gmail_pdf/app/planner.py`, `gmail_pdf/infra/gmail_gateway.py`, `tests/unit/test_exit_statements.py`, `tests/e2e/test_select_range.py` lines 225-345; `cli/main.py` and `infra/retry.py` diffs.

| # | Check | Mandatory | Result | Evidence |
|---|-------|-----------|--------|----------|
| 1 | Reports present | ✱ | ✅ | Quality and standards on `7883f9c`. Performance stands under exit rule item 4: master read the retry diff (extraction of `_back_off`, no change of behaviour) and the gateway at H; both stay within R9..R12 and R15 |
| 2 | Zero open Blocker/Critical | ✱ | ✅ | **QUA-39 closed** (D-64); master's probe below |
| 3 | Majors fixed or accepted | | ✅ | No new Major. PERF-11, PERF-12 stay accepted deferred (D-59) |
| 4 | Findings cite file:line | | ✅ | All anchored |
| 5 | R1..R16 | | ✅ | Table below |
| 6 | Unapproved file | | ✅ | 16 files, all listed. `cli/main.py` has two docstring hunks; `bootstrap.py` and `domain/messages.py` have no diff |
| 7 | Architecture acknowledgement (D-44) | | ✅ | Ninth acknowledged; **C37(a) closed** (D-66) |
| 8 | CI, base | | ✅ | 10/10 on `7883f9c`; orchestrator rerun 1164 passed, 12 skipped, 99.88 %, ruff, mypy --strict, bandit clean |
| 9 | T-05 interim control | | ✅ | Reviewer-standards PASS. Master's grep over `gmail_pdf/` and the root shim: only `raise SystemExit(main())`, plus prose and the catch |
| 10 | Issues tied to this story | | ⚠️ | #11, #31 done. QUA-39, DEF-001's residual, is fixed; **#15 stays open until QA confirms at G7** |
| 11 | Traceability sample | | ✅ | AC-6 (iii) → `test_content_that_parses_but_cannot_be_read_still_ends_in_the_fixed_line` (`req("AC-6", "QUA-39")`). Reverse: that test → AC-6 → FR-008, D-21 |

**R1..R16**
| Item | Result | Evidence |
|---|---|---|
| R1 QUA-39 | ✅ | All rows; outcome confirmed by master (below) |
| R2 STD-48 | ✅ | Every listed form flagged, one negative each; listed "not covered" items stated. STD-63 is not a miss (D-65) |
| R3 QUA-40 | ✅ | Master read `test_retry.py:98-108`: 408, 409, 400 and 404 with rate-limit reasons |
| R4 QUA-41 | ✅ | `m-return-0` killed |
| R5 QUA-42 | ✅ | `g-cache-discovery` and `g-method-name-in-log` killed, both directions |
| R6, R7 QUA-43, 44 | ✅ | Four literal rows matched by hand and by a separate oracle (reviewer); `tz-system-empty` killed |
| R8 QUA-47 | ✅ | Docstrings match behaviour (reviewer, real children). Master read the hunks |
| R9 QUA-49 | ✅ | Master read `test_sentinel_matrix.py:394-405`: 403 JSON, 403 non-JSON, 500; gateway docstring names the library's log line |
| R10 STD-49 | ✅ | `GoogleObject: TypeAlias = Any` with its reason |
| R11 STD-50 | ✅ | 36 lines; 40,000 scripted calls identical to `c847e1a` |
| R12 STD-51 | ✅ | Raised outside the handler; `__context__ is None` asserted; `from None` removal killed |
| R13 STD-52 | ✅ | `Raises:` complete; code unchanged |
| R14 STD-56 | ✅ | Both justifications present |
| R15 PERF-13 | ✅ | `messages()` built once at gateway line 105. Leftover line 104 is STD-61, not a miss |
| R16 PR text | ✅ | **Read by master; not in the consolidated table.** Item 4 now states the exit 3 cases; item 10 says "tripwire, not the control"; AA-04 says correctness is not established |

**Master's probes** (`git archive` of `7883f9c` in the scratchpad, folder `g6m2`; Python 3.12.10; `gmail_pdf.__file__` confirmed inside the export; AC-6 command):

| Case | Result |
|---|---|
| 52 real children: every R1 row, QUA-53 and its mirror, deepest legal reads, encodings, roots, settings, unterminated `[` and `{"a":` at 300,000 | 15 success, 37 fixed line, **0 unexpected, 0 other** |
| Deepest legal, listed and read | `parts` chain beside the PDF part 96 exit 0, 97 fixed line; read resource value 196 exit 0, 197 fixed line |
| 51 JSON paths x 65 hostile values, plus deletions, plus 6,000 documents of 2 to 4 random edits, through real `main()`, sleep stubbed | 9,365 runs: 2,492 success, 6,873 fixed line, **0 unexpected, 0 other** |
| **Control:** same 9,365 documents on the `c847e1a` export | 3,835 success, 5,015 fixed line, **515 unexpected**. The harness detects the failure |
| `q-tree-stop-at-leaf` patched, `parts: [{"parts": [5]}, {}]` | Head: fixed line. Mutant: **unexpected-failure line** (QUA-53 reproduced) |
| Digit cap 19 with a 20-digit date; latency cap 3599 with 3600 | Both give the fixed line: tighter, inside the outcome (QUA-54) |
| `non_integer_exits` on a tuple, walrus, `for` target, default argument, dict value | All `[]`, not flagged; plain assignment flagged (STD-63 confirmed and wider) |
| `_BUILD_FAILURES` and `_report_build_failure`, AST at H against `c847e1a` | Identical. The four constants are plain literals with no `{`, `}` or `%` |
| `git grep _service 7883f9c` | Line 104 alone sets it; nothing reads it (STD-61) |

Limits: 3.12.10 only for these rows. The in-process sweep shares the test process, and its first run was invalid: my sleep stub missed, because `sleep` is a default bound at definition, so a legal latency slept; the results above are from the corrected run. "Any file content" cannot be proved by tests. **No CI row reads a document near the cap through `get_message`:** the deepest read row is `parts-20`, the `parts-*` refusal rows stop at load (QUA-55), and the top-level 199 row is never read. So on 3.10 and 3.11 the read at the cap rests on arithmetic: pure-Python `deepcopy` at about 2 frames per level against a limit of 1000, with the reviewer's 410 measured on 3.12. #38 adds the row. No real Gmail call.

**Ratings** (D-65; rating only under D-62)
| Finding | Reviewer | Master | Disposition |
|---|---|---|---|
| QUA-52 = STD-61 `gmail_gateway.py:104` | Minor | **Minor**, counted once | #35, STORY-02.04; fallback STORY-03.03 |
| STD-60 `test_select_range.py:244, 245, 249, 286` | Minor | **Minor** | #38, PGD-16 |
| QUA-53 `test_fake_gmail_canonical.py:288` | Minor | **Minor** | #38, PGD-16, first in that issue |
| QUA-54 `test_fake_gmail_canonical.py:303` | Minor | **Info, re-rated down** | #38, PGD-16 |
| QUA-55 `test_select_range.py:292` | Info | **Info** | #38, PGD-16, with master's added row |
| QUA-56 `retry.py:117` | Info | **Info** | #35, STORY-02.04 |
| STD-62 `planner.py:39`, `runner.py:36`, `cli/main.py:25` | Info | **Info** | #38, PGD-16 |
| STD-63 `test_exit_statements.py:13` | Info | **Info**, not a miss on R2 | #38, PGD-16 |

All opened by master. No commit in PR #33 (D-65).

**Conditions on G7 PGD-15**
| # | Owner | Required |
|---|---|---|
| 1 | qa-engineer | Test `7883f9c` only. A code change after H: stop and return to master. The report commit is the one exception |
| 2 | qa-engineer | C35 first: check 0 |
| 3 | qa-engineer | M13, M20, M22, M23 each fail (C30). Reviewer's figures: 17, 5, 3, 3 |
| 4 | qa-engineer | Confirm #15 / DEF-001 against its three items and the QUA-39 forms, then state whether PGD-63 and #15 can close |
| 5 | master | Read the report against the test plan row by row, not only the AC matrix |
| 6 | qa-engineer | Not defects: #38, the #35 additions, the arithmetic limit above, a legal `latency_s` of 3600 sleeping |
| 7 | orchestrator | Before the merge request: CI 10/10 on the PR head, tested `main` SHA (RISK-023), and name PERF-11, PERF-12, #35 and #38 |

**Conditions**
| # | Owner agent | Artefact | Required change | Due gate |
|---|-------------|----------|-----------------|----------|
| C33 | | | **Rows part closed:** all eight are in `b20be4e`, and STORY-01.04's says "Not Ready until STORY-02.04 exists with the pacer AC". The Jira part stays due at the sprint-02 G4 | Sprint-02 G4 |
| C37(a) | | | **Closed** (D-66). C37(b), (c), (d) stay open | As recorded |
| C38 | scrum-master | `sprint-01-plan.md`; Jira PGD-16 | (a) Row and remote link: #38 → PGD-16, in the PR before G5, no AC change. (b) STORY-02.04 row gains STD-61 and QUA-56 (#35). (c) STORY-01.04 and STORY-01.06 rows carry SA condition 2: the four fixed lines are no precedent, `GmailApiError`, `RetryExhaustedError` and real sign-in failures stay on `safe_message`, and an exit code chosen by type takes its text from `safe_message` | (a) before PGD-16 starts, with C34; (b), (c) sprint-02 G4 |

**Risks registered:** no new risk. RISK-021 note added. RISK-005, RISK-011, RISK-025 unchanged.

**Rationale:**
- The label comes from the exit rule and the checklist: every listed item passed and nothing rates Major or higher. Master tried to break it on its own terms: a different mutator, a cross product rather than a fuzz, and a control that proves the harness can see the failure.
- The check most likely to change the result was whether STD-63 is a miss on R2, because that would have needed a commit. It is not, and the reasons are in D-65. A wish for a clean docstring is not a reason to read it as a miss, and a wish to avoid a commit is not the reason it is not one.
- The attempt 2 evidence table had no row for R16. Master read it. A fix item with no named verifier is a gap in the exit rule, and the next rule should name one.

**Posted:** PR #33 comment 6539633088; Jira PGD-15 c.10279; new issue #38; #35 comment 6539632665.

---

## G7 – QA Acceptance — STORY-02.02 (PGD-15) — 2026-10-31

- **Decision:** GO (ACCEPT). The story may move to Done after C41. **Merging PR #33 needs the delivery lead** (`MERGE_POLICY = docs-auto, code-human`); no merge in this run. The merge precondition and the items to name are below
- **Decided by:** master  ·  **Human override:** none  ·  **Human approval required:** no for G7; the code merge is Santhosh's
- **Attempt:** 1
- **Artefacts evaluated:**
  - `docs/07-qa/PGD-15-test-report.md` at `e98bc92`, read in full. The code under test is `7883f9c`.
  - QA summary PR #33 comment 6540103534; Jira PGD-15 c.10282, c.10283, AC-1..10 and Dev Context; PGD-69 and #39; PGD-16 and PGD-17 ACs; PGD-63, PGD-64, PGD-67; #11, #15, #31.
  - `docs/07-qa/test-plan.md` at `7945587`, all sections, against the report row by row; PRD FR-008, FR-012, FR-015; G6 conditions and D-54, D-61, D-62, D-64, D-65, D-66.
  - Source read at `7883f9c`: `gmail_pdf/domain/daterange.py`, `domain/query.py`, `app/planner.py`, `app/runner.py`, `cli/args.py`, `cli/main.py`, `infra/tz.py`, `bootstrap.py`, `tests/support/mailboxes.py`, the query terms of `tests/fakes/fake_gmail.py`.
  - Check runs on `e98bc92`: 10/10 `success`, run 41176853832, `pull_request`, attempt 1, read by master, per-leg totals from the job logs. `mergeable_state` clean. `main` `2743016`, merge ref `2e8ad40` (parents `2743016`, `e98bc92`). 30 reviews, all `COMMENTED`.
  - `git reflog`: the main checkout sat on the branch at `7883f9c` from 01:42 to 02:31, which agrees with the report's Environment row.

| # | Check | Mandatory | Result | Evidence |
|---|-------|-----------|--------|----------|
| 0 | C35 closed | | ✅ | Plan at `7945587`: NT-01 exit 1, NT-02..05 fixed lines, R1 rows in NT-03 and NT-04, NT-09, tie to AC-6, OQ-1 closed, Annex B 0.2 |
| 1 | Every AC has a verification result with evidence | ✱ | ✅ | QA matrix AC-1..10 Pass. Master reproduced AC-5, AC-6, the AC-1 literals (`calendar.timegm`), M13..M23 |
| 2 | No open Sev-1/Sev-2 defects | ✱ | ✅ | Open: DEF-007 only, re-rated Sev-3 (D-67) |
| 3 | Regression recorded and green | ✱ | ✅ | QA 1164 passed, 12 skipped, four runs and per file; 99.88 %; merge ref as a work tree the same. CI 10/10 on the PR head. Master's control without the long-path file: 1117 passed, 12 skipped |
| 4 | Exploratory notes present | | ✅ | EC-1, EC-3, EC-8, EC-9 |
| 5 | Accessibility (UI stories) | | n/a | No UI |
| 6 | Sev-3 fixed or accepted (test plan section 5) | | ✅ | DEF-007 accepted for this story's exit, with a target (D-67) |
| 7 | Traceability sample | | ✅ | GOAL-01 → FR-008 (PRD line 86) → AC-2 → `tests/unit/test_planner.py` (`req("AC-2")`). Reverse: that test → AC-2 → FR-012, FR-008 → GOAL-01 |
| 8 | G6 conditions 1-7 | | ✅ | 1 QA tested `7883f9c` only (`git diff 7883f9c e98bc92 -- gmail_pdf tests` empty, orchestrator). 2 C35 first. 3 mutants. 4 #15 confirmed. 5 below. 6 no such item logged as a defect. 7 below |
| 9 | Report read against the plan, row by row | | ⚠️ | Four rows short, closed by master's runs; corrections below |

**Master's probes** (fresh `git archive` of `7883f9c` in the scratchpad, folder `g7m`; Windows, CPython 3.12.10; real child interpreters; socket guard on; `gmail_pdf.__file__` inside the export for `-m` and the shim; scripts `p_child.py`, `p_gw.py`, `p_mut.py`):

| Row | Result |
|---|---|
| AC-5: `-m`, shim, exe, `PYTHONUTF8` set and unset | 6 of 6: exit 0, `Messages in range: 2\n`, stderr empty, working directory empty |
| AC-6 (i), (ii) x4 values, (iii) x9 (bad JSON, wrong version, no id, bad UTF-8, BOM, 100,000 levels, missing, directory, no-share lock), three entry points | 42 of 42: exact exit, exact single line, stdout empty, no path, trace or sentinel, nothing created |
| NT-04 sweep, depth 1..3000 step 25, `parts` and resource value | 240 runs: parts 4 success (1..76), 116 fixed line (from 101); resource 8 success (1..176), 112 fixed line (from 201). **0 unexpected, 0 other** |
| NT-05 on a built wheel (`python -m build --wheel --no-isolation`) | `gmail_pdf-0.9.0.dev0-py3-none-any.whl`, 29 entries, no `tests`. `-m` and exe: exit 1, the source-checkout line, nothing created; `find_spec("tests")` None |
| M13, M22, M20, M23, one edit per fresh copy | 17, 5, 3, 3 failed, by the same tests QA names. Without the long-path file: 1117 tests |
| A1, a dependency added to `pyproject.toml` | 2 failed in `test_dependency_allowlist.py` |
| X1, `sys.exit("text")` added to `cli/console.py` | 1 failed, `test_no_exit_in_the_package_carries_a_non_integer` |
| CI legs on `e98bc92` | Windows 3.10, 3.11, 3.12: 1164 passed, 12 skipped. Ubuntu, macOS: 1173 passed, 3 skipped. The 3 are the three `WINDOWS_ONLY` tests of `test_token_location_warning.py`, so the 12 Windows skips ran on the POSIX legs |
| DEF-007 rows | Table in ruling 4 |
| Real gateway, 1960..2026 UTC, on `HttpMockSequence` | `q` sent as `has:attachment filename:pdf after:-315619201 before:1798761601` |
| Real gateway behind `main`, six 503 with `Retry-After: 0` | Five `Retrying list_message_ids: attempt N of 6 after 0.0 s` lines, then `error: unexpected failure, see the run log`, exit 1 |
| `available_timezones()` | `Asia/Kolkata ` , `Asia\Kolkata`, `asia/kolkata`, `utc` not members; `Asia/Kolkata`, `UTC`, `EST`, `GMT`, `Factory` members |

Limits: 3.12.10 only. The exe rows in the export may load the venv's editable install: the `PYTHONVERBOSE` row did not settle it, and it is the same commit, clean, so the result stands. The 47 tests of `test_gitignore_matching.py` were left out of master's runs because of the scratch path length; QA and CI ran them. No real Gmail call. My first mutant run was invalid: two regexes were written for a multi-line tuple, M13 cut code out of the file and M22 did not apply. Those copies are left in `g7m/mx` and `g7m/mz`; the results above are from `g7m/my`.

**Report corrections** (the report stays as committed: a docs commit restarts CI on the head):
- DEF-007: Sev-4, "no practical loss" and "the selection stays exact" do not stand (ruling 4). The defect's title also misses that the end date does not matter.
- NT-04: QA ran the named depths but not the plan's sweep of 1 to 3000 in steps of 25. Master ran it. "Pass" holds with that run.
- NT-05: the plan says a built wheel; QA used a source-only copy and said so under Residual Risks, while the row reads Pass. Master built one. "Pass" holds with that run.
- Plan sections 3 and 7: `pyproject.toml` changed, so the allow-list mutant was due; QA ran the test without the mutant. `test_exit_statements.py` is a new enforcement-style test and was not in QA's list. Master ran both.
- Plan section 7: QA read the POSIX legs' status, not their tests. Same miss as PGD-13. Master read them.
- Plan section 14 says DEF-002 goes to "the next story that touches `tests/support/`, whichever is earlier". PGD-13 and PGD-15 both touched that folder, neither touched `socket_guard.py`. The intent is the guard; PGD-64 stays on sprint 02 (C20).
- `e297c7c` is the merge ref QA tested; GitHub rebuilt it as `2e8ad40` after the report commit. The two differ by the report only.

**Rulings and dispositions**
| # | Item | Ruling |
|---|---|---|
| 1 | C35 | **Closed.** The header "Version 0.1", the date and the Status line are stale; the content is 0.2. Goes to C32, no commit needed now |
| 2 | G7 | **GO.** Every mandatory item passes |
| 3 | DEF-005 · PGD-67 · #31; DEF-001 · PGD-63 · #15; #11 | **Fixed and verified on this head. They close with the merge, not before** (D-68). The PR has no closing keywords, so nothing closes itself |
| 4 | DEF-007 · PGD-69 · #39 | **Sev-3, type Product and Requirement. Accepted for this exit. Fix in PGD-16 with a new AC** (D-67, C39). Rows below |
| 5a | Retry lines on stderr | Confirmed. **No defect on this head.** Unreachable, AC-7 met, NT-08's "one `error:` line" holds literally. **#40, C40** (D-68) |
| 5b | First-page-only count | **No defect.** The Dev Context sets a single page. It undercounts with exit 0 by design until STORY-02.04. Named at merge; QA adds a row past 500 (C32) |
| 5c | `--tz` forms | **No defect here, no new AC.** PGD-16 AC-4 already says valid names come from `available_timezones()`, and T3 says so too. Rows only (C39 d) |
| 5d | `GMAIL_PDF_TEST_FAKE_MAILBOX=""` | **No action.** An empty value names no file; `test_empty_hook_variable_is_treated_as_unset` has pinned it since PGD-12 |
| 6 | Risks | RISK-026 new, score 4. RISK-021 noted. RISK-005, 011, 020, 023, 025 unchanged. **C38 stays open:** (a) before PGD-16 starts, (b), (c) by the sprint-02 G4; `sprint-01-plan.md` has no #38 row yet |
| - | `--sta` abbreviation (R-10, OQ-3) | Not a PGD-15 defect. OQ-3's needed-by is PGD-16 and it has no answer yet, so C39 (b) carries it before the date passes |
| - | OQ-5 console encoding | Stays open, no new evidence of harm |

**DEF-007 rows** (fake mailbox with 4 messages in range; real children, `-m`):
| Range, zone | Result |
|---|---|
| `1970-01-02..1970-01-02` UTC | exit 0, `Messages in range: 0` |
| `1970-01-02..2026-12-31` UTC, Kiritimati, Apia; `2000-01-01..2026-12-31` UTC | exit 0, `Messages in range: 4` |
| `1970-01-01..2026-12-31` New_York | exit 0, `Messages in range: 4` |
| `1970-01-01..1970-01-01` UTC; `1969-12-31..1969-12-31` UTC | exit 1, unexpected-failure line |
| `1970-01-01..2026-12-31` UTC, Kolkata; `1960-01-01..2026-12-31` UTC; `1900-01-01..2026-12-31` Kolkata; `0001-01-01..2026-12-31` UTC | **exit 1, unexpected-failure line, with 4 messages in the range** |
| Real mode, `1960-01-01..2026-12-31` UTC | exit 3, the sign-in line |

**Conditions / remediation**
| # | Owner agent | Artefact | Required change | Due gate |
|---|-------------|----------|-----------------|----------|
| C32 (extended) | qa-engineer | `docs/07-qa/test-plan.md` | Added to C32: header version, date and Status line; section 14 DEF-002 wording names the guard file; a STORY-02.04 row with a count past 500 (QA's 1,203 mailbox); section 7 restated in the report template as a row each: POSIX legs read, allow-list mutant when `pyproject.toml` changes, every new enforcement test mutated, NT sweeps and wheel as written | Sprint-02 G4 |
| C39 | product-owner, scrum-master | Jira PGD-16, PGD-69; `sprint-01-plan.md` | (a) New AC on PGD-16 (8 to 9, within the limit; scrum-master confirms the estimate). **Binding outcome:** for every date pair that passes the format and order checks, in every zone, the command ends in a normal result or in exit 2 with one fixed sentence, never in the unexpected-failure line for a date reason; and no `q` sent through the gateway carries a negative bound. Covers `--start`, `--end`, `--tz` on the hook and the `q` at the gateway. Rows: the table above plus a real-mode row; `9999-12-31` stays exit 2. The PO chooses reject or clamp, and notes how PGD-15 AC-4's "any range" reads after it. (b) OQ-3 answered on PGD-16. (c) PGD-69 linked to PGD-16; row in the plan: "fixed in the PGD-16 PR before G5"; fallback PGD-17; **STORY-01.04 is not Ready while PGD-69 is open**. (d) No AC change: `Asia/Kolkata `, `Asia\Kolkata`, `asia/kolkata`, `utc` as rows under PGD-16 AC-4, exit 2, with `UTC` as the positive row | Before PGD-16 starts, with C34 and C38 (a) |
| C40 | product-owner, scrum-master | Jira PGD-17 AC-4; `sprint-01-plan.md` | Per #40: PO states on AC-4 whether retry notices may appear on stderr before the run log exists. Row on STORY-07.02: the handler carries these records, tested through the real gateway. Settled before STORY-01.04 is Ready | Before PGD-17 starts; row by the sprint-02 G4 |
| C41 | qa-engineer | Jira PGD-69, PGD-63, PGD-67; #39, #15, #11, #31; test plan | (a) PGD-69 and #39: Sev-3, priority Medium, label `sev-3` for `sev-4`, title without "in a zone east of UTC", wide-range rows added. (b) Verified comments on PGD-63, PGD-67, #15, #11, #31: Jira has no Verified status and PGD-63 carries no QA note. (c) DEF-007 row in plan sections 14 and 15 before the PGD-16 G7. Then set PGD-15 Done | (a), (b) before the merge request; (c) before the PGD-16 G7 |

**Closure after the merge.** On the orchestrator's relay of the merge SHA: qa-engineer closes #15 and #31 and moves PGD-63 and PGD-67 to Done, as the defect owner (test plan section 6). The orchestrator closes #11, a tech-debt issue with no Jira record (playbook 5.5). Master transitions nothing.

**Merge precondition (orchestrator; re-read at the moment of the request):**
1. PR head still `e98bc92`, and `git diff 7883f9c <head> -- gmail_pdf tests` empty.
2. 10/10 `success` from check runs on that exact head. Read now: run 41176853832.
3. RISK-023: the `main` that run tested equals current `main`, now both `2743016`. If not, update the branch and re-read CI. That merge is not a commit for D-62 as long as the code diff holds only what `main` brought; if `main` changed `gmail_pdf/` or `tests/`, return to master. The status branch is not merged to `main` before PR #33.
4. No `REQUEST_CHANGES` review outstanding. Now 30 reviews, all `COMMENTED`.
5. C41 (a), (b) done, and QA has set PGD-15 Done.

**Items to name in the merge request:** PERF-11, PERF-12 (accepted deferred, armed; D-59); #35; #38; **DEF-007 Sev-3 accepted (#39, D-67) with RISK-026**; #40 retry lines; the first-page-only interim count, which undercounts past one page until STORY-02.04; the 3.10 and 3.11 depth arithmetic limit (D-64); #15, #11 and #31 closing with the merge, and who closes them; Q-14 and Q-15 still his. The merge unblocks PGD-16..18, with C34, C38 (a) and C39 before PGD-16 starts and C40 before PGD-17 starts. RISK-005 stays 10, RISK-011 8, RISK-025 9.

Follow-ups (not conditions): orchestrator sets the label and requests the human merge.

**Risks registered:** RISK-026 (new, score 4). RISK-021 note added. RISK-005, RISK-011, RISK-020, RISK-023 and RISK-025 unchanged.

**Rationale:**
- All three mandatory items have evidence, and master reproduced the ones that carry the most risk. GO, not CONDITIONAL GO: C39..C41 are project-level follow-ups, as C30..C32 were at the PGD-13 G7, and C41 is bookkeeping, not a gap in the evidence about this head.
- The hard question was DEF-007, and the rating did not need likelihood in either direction. QA's reasons fell on testing them: the range does not have to sit at the epoch, and the local re-check works in one direction only. It stops at Sev-3 on what was observed: no AC fails, the failure is loud, and a later start works. The unknown is real Gmail's reading of a negative bound, and the fix removes the unknown rather than measuring it.
- The row reading paid for itself again: four rows short of the plan, all of which held when run. A "Pass" row whose evidence differs from the row's words needs a correction, even when the result stands.

**Posted:** PR #33 comment 6540247264; Jira PGD-15 c.10284; #39 comment 6540239278; new issue #40; risks PGD-1 c.10285.

---

## G6 – Peer Review — STORY-02.03 (PGD-16) — 2026-10-31

- **Decision:** NO-GO. Attempt 2 follows on a new head under the exit rule below (D-78)
- **Decided by:** master  ·  **Human override:** none  ·  **Human approval required:** no; both Critical ratings are named to the delivery lead, who may overrule them
- **Attempt:** 1, loop 1 of 3. Head `93fb918`, base `main` `9a1ffe5`
- **Artefacts evaluated:**
  - Consolidated findings PR #41 comment 6541390048; reviews 5722058811 (quality), 5721961706 (standards), 5722048956 (performance), bodies and all inline comments read with `gh api`; SA ruling 6541109827; G5 comment 6541000495. 3 reviews, all `COMMENTED`.
  - Jira PGD-16 description, AC-1..9 as amended, comments c.10296, c.10298, c.10299, c.10300, c.10302..10307; issue links (PGD-69 blocks PGD-16); remote link #38 read with `listJiraIssueRemoteIssueLinks`.
  - Source at `93fb918`: `infra/tz.py`, `cli/main.py`, `cli/args.py`, `bootstrap.py`, `domain/validation.py`, `domain/daterange.py`, `domain/errors.py`; `tests/unit/test_cli_select_range.py`, `tests/unit/test_daterange.py` in part; base `tests/unit/test_daterange.py` row `test_the_last_representable_day_is_rejected_not_crashed`; tzlocal 5.4.5 `win32.py`, `unix.py`, `utils.py`.
  - PRD v0.5 at `52fecb7`; `sprint-01-plan.md`; architecture line 187; Coding Standards lines 10 and 70; reviewer severity scales; #34's last comment; `test-plan.md` OQ-3, R-10, NT-01, NT-09.
  - Check runs on `93fb918`: 10/10 `success`, read by master. `main` `9a1ffe5` current; `mergeable_state` clean.

| # | Check | Mandatory | Result | Evidence |
|---|-------|-----------|--------|----------|
| 0 | Prerequisites C34, C38 (a), C39 (a..d) | | ✅ | PGD-16 description; remote link #38; PGD-69 blocks PGD-16; plan rows for #38 and #39 |
| 1 | Three reports present | ✱ | ✅ | Reviews above; quality and standards REQUEST CHANGES, performance APPROVE WITH COMMENTS |
| 2 | Zero open Blocker/Critical | ✱ | ❌ | QUA-57 Critical (D-75); STD-64 = QUA-58 re-rated Critical (D-76) |
| 3 | Majors fixed or accepted | | ✅ | None left after re-rating |
| 4 | Findings cite file:line | | ✅ | All inline but PERF-20, which has no code location |
| 5 | Architecture acknowledgement (D-44) | | ⚠️ | Six acknowledged, one rejected, R1..R5 required (D-77); not on the branch |
| 6 | Other ACs, CI | | ✅ | Quality AC table: AC-1, 2, 3, 5, 6, 7, 8, 9 met; AC-4 partly. Orchestrator: 1423 passed, 12 skipped, 99.89 %; ruff, mypy --strict (25 files), bandit clean. CI 10/10, run 41183160333 |
| 7 | T-05 interim control | | ✅ | Reviewer-standards pass; no text-carrying exit (orchestrator) |
| 8 | Issues tied to this story | | ✅ | #38: all six rows read done; closes with the merge. DEF-007 rows hold; QA verifies PGD-69 at G7. DEF-005 mutants 17, 5, 3, 3 |
| 9 | Traceability sample | | ✅ | GOAL-01 → FR-015 (PRD line 93) → PGD-16 AC-9 → `tests/e2e/test_invalid_input.py`. Reverse: `req("AC-4")` on `test_an_unusable_system_zone_without_tz_gets_the_zone_sentence` → AC-4 → FR-015, VAL-02 |

**Binding outcomes**
- **O1, QUA-57:** with no `--tz`, any exception of class `LookupError`, `ValueError`, `OSError`, `AttributeError` or `TypeError`, subclasses included, from `tzlocal.get_localzone_name()` means the system zone is unresolved. `system_zone_name()` returns `None` and the command exits 2 with the exact AC-4 sentence, after any date lines in AC-5 order, in both modes, before `build_deps`, with 0 Google calls and nothing created. A given `--tz` never looks the zone up. Not claimed: any other class (none found reading tzlocal 5.4.5), which stays on the last line of defence; `MemoryError`; `KeyboardInterrupt`; a wrong but valid system zone.
- **O2, STD-64:** nothing under `gmail_pdf/cli/` imports `gmail_pdf.infra`, the same for `gui`; both names come through `bootstrap`; the boundary test enforces it; no behaviour changes.

**Master's probes** (fresh `git archive` of `93fb918` in the scratchpad, folder `g6m16`; Windows, CPython 3.12.10, tzlocal 5.4.5; real children; `gmail_pdf.__file__` asserted inside each export; scripts `reg_child.py`, `reg_run.py`, `rows.py`, `fx_build.py`):

| Registry, no `--tz`, real mode | `93fb918` | SA's tuple | O1 tuple |
|---|---|---|---|
| Good value | exit 3, sign-in line | same | same |
| No `TimeZoneKeyName` | **exit 1, unexpected-failure line** | exit 2 | exit 2 |
| Same, `--start x` | **exit 1, date line lost** | exit 2, two lines | exit 2, two lines |
| Unknown name; `FileNotFoundError`; `PermissionError`; DST-off row | exit 2 | exit 2 | exit 2 |
| `REG_DWORD`, `REG_BINARY`, none | **exit 1** | **exit 1** | exit 2 |
| `REG_DWORD`, `--start x` | **exit 1** | **exit 1** | exit 2, two lines |
| No key, `--tz UTC` | exit 3, no lookup | same | same |

All rows: one stderr line unless stated, working directory empty.

| Sample row on `93fb918` | Result |
|---|---|
| `1970-01-01..2026-12-31` New_York; `1960-01-01..2026-12-31` UTC, hook and real | exit 2, one `--start:` line |
| `1970-01-02..2026-12-31` New_York, Etc/GMT-14; `2026-01-01..9999-12-30` Etc/GMT+12 | exit 0, count 4, future-end warning |
| `2026-01-01..9999-12-31` UTC | exit 2, one `--end:` line |
| Real mode: reversed; `Mars/Olympus`; `--sta` | exit 2 each; working directory empty |
| Refused hook: bad date; valid input | exit 2, date line; exit 1, refused line |
| `DateRange.from_days(date.max, date.max, UTC)` | `OverflowError` (QUA-59) |
| `DateRange.from_days(1970-01-01, ...)` UTC | `ValueError`, "starts before the epoch" at S = 0 (STD-69) |
| `git grep after:-` equivalent over `gmail_pdf`, `tests` | One test comment only |

| Mutant on a scratch copy with the O1 tuple, class rows for `OSError`, `LookupError`, `ValueError`, `AttributeError`, `TypeError`, and one row each for F7 and F8 | Fails |
|---|---|
| T2 drop `OSError` | `lookup-fails`, `os-error` |
| T3 drop `ValueError` | `value-error` |
| T4a drop `LookupError`; T4b `LookupError` to `KeyError` | `lookup-error` |
| T5 drop `AttributeError`; T6 drop `TypeError` | `attribute-error`; `type-error` |
| C3 UTC clock in `main` | Kiritimati row |
| C4 `SystemClock` one day ahead | bracket row |
| V5 refusal before validation | refused-hook row |

Limits: 3.12.10 only. The registry is faked; no real machine was damaged. The `ZoneInfoNotFoundError` row and the `--start x` CLI row were not in the mutant copy. Reading, not a run: the SA's single `lookup-error` row cannot kill T3. No real Gmail call. The AC-9 sweep is the reviewer's, 2,990 children; master ran samples only.

**Ratings and dispositions** (D-75, D-76, D-79)
| Finding | Reviewer | Master | Disposition |
|---|---|---|---|
| QUA-57 `infra/tz.py:21` | Critical | **Critical, wider** | F1 |
| STD-64 = QUA-58 `cli/main.py:52` | Major | **Critical** | F2 |
| STD-67 = QUA-60 `domain/errors.py:43` | Minor | Minor | F3 (R3) |
| STD-65 = QUA-64 `validation.py:3` | Minor, Info | Minor | F5 (R5) |
| STD-68 = QUA-65 `runner.py:34` | Minor, Info | Minor; `None` branch to #43 | F5 (R5) |
| QUA-59 `daterange.py:54` | Minor | Minor; no guard | F6 |
| QUA-61 `test_daterange.py:283` | Minor | Minor | F7 |
| QUA-62 `cli/main.py:144` | Info | **Minor, re-rated up** | F8 |
| STD-66 `validation.py:5`, `messages.py:47`, `main.py` | Minor | Minor | F9 |
| STD-69 `daterange.py:52` | Minor | Minor | F10 |
| STD-70 five test files | Minor | Minor | F11 now; split to #42 |
| STD-71 `test_cli_select_range.py:199` | Minor | Minor | F12 |
| STD-72, STD-73, PERF-17 | Minor | Minor | #42, PGD-17 |
| QUA-66 | Info | Info | F13 |
| STD-74 | Info | Info | #42 |
| STD-75, PERF-19 | Info | Info | #43 |
| QUA-63 | Info | Info | No code; C43 |
| PERF-20 | Info | Info | C44 |
| STD-76, PERF-18 | Info | Info | No action |

**Survivors (item 6).** T3, T4, C3, C4 and V5 are all real and all must fail on H. T4 is restated as T4a and T4b, because the tuple changes; T2, T5 and T6 join them. N1, N2, R3 and I4 are equivalent, and the developer's "one survivor" is corrected in the PR text (F14).

**Fix list.** All owned by developer, one commit series, then H is frozen.
| # | Item | Files | Severity | Verified by |
|---|---|---|---|---|
| F1 | QUA-57, R1 widened: `except (LookupError, ValueError, OSError, AttributeError, TypeError):` with the reason inline; unused import dropped. Rows in both zone tests for `LookupError`, `ZoneInfoNotFoundError`, `ValueError`, `OSError`, `AttributeError`, `TypeError`. CLI row: `--start x` with `LookupError` gives the date line, then the zone line | `gmail_pdf/infra/tz.py`; `tests/unit/test_cli_select_range.py`; `tests/unit/test_daterange.py` | Critical | quality |
| F2 | STD-64 = QUA-58, R2, with synthetic `cli` and `gui` rows | `gmail_pdf/bootstrap.py`; `gmail_pdf/cli/main.py`; `tests/unit/test_import_boundaries.py` | Critical | standards |
| F3 | STD-67 = QUA-60, R3; name dropped from the set at `test_validation.py:486`, test renamed | `gmail_pdf/domain/errors.py`; `tests/unit/test_validation.py` | Minor | standards |
| F4 | R4, `test_only_validation_builds_a_run_request` | `tests/unit/test_validation.py` | SA condition | quality |
| F5 | STD-65 = QUA-64, STD-68 = QUA-65, R5 | `gmail_pdf/domain/models.py`; `gmail_pdf/app/runner.py`; `gmail_pdf/domain/validation.py` | Minor | standards |
| F6 | QUA-59: `OverflowError` in the `from_days` `Raises`; row restored as `pytest.raises(OverflowError)`; "It trusts its input" reworded | `gmail_pdf/domain/daterange.py`; `tests/unit/test_daterange.py` | Minor | quality |
| F7 | QUA-61: bracket before and after; row `--tz Pacific/Kiritimati --end 2026-02-16`, no warning | `tests/unit/test_daterange.py`; `tests/unit/test_cli_select_range.py` | Minor | quality |
| F8 | QUA-62: `hook_env(path, testing=None)` with a bad date gives exit 2 | `tests/e2e/test_invalid_input.py` | Minor | quality |
| F9 | STD-66 | `gmail_pdf/domain/validation.py`; `gmail_pdf/domain/messages.py`; `gmail_pdf/cli/main.py` | Minor | standards |
| F10 | STD-69: named constant, not a copy of `EARLIEST_DATE`; message "at or before the epoch" | `gmail_pdf/domain/daterange.py` | Minor | standards |
| F11 | STD-70 first part: one justification line per file, naming #42 where it applies | `tests/unit/test_cli_select_range.py`, `tests/unit/test_validation.py`, `tests/e2e/test_invalid_input.py`, `tests/integration/test_gateway_httpmock.py`, `tests/unit/test_fake_gmail_canonical.py` | Minor | standards |
| F12 | STD-71 | `tests/unit/test_cli_select_range.py` | Minor | standards |
| F13 | QUA-66 | `tests/unit/test_daterange.py` | Info | standards |
| F14 | PR text: "none weakened"; survivors; deviation 3; follow-up (a); the `cli` import | PR #41 body | none | master |

**Exit rule, attempt 2, loop 2 of 3 (D-78).** Scope: the files above and no others, no new file. Master decides on head H.
| Verifier | Must show on H |
|---|---|
| orchestrator | Diff `93fb918..H` in scope; local rerun, ruff, format, mypy --strict, bandit; CI 10/10 from check runs on H; `main` compared (RISK-023); no manifest changed |
| reviewer-quality | Delta plus a fresh export: every O1 registry row in real children; T2, T3, T4a, T4b, T5, T6, C3, C4, V5 each fail a named test; F1, F4, F6, F7, F8 |
| reviewer-standards | Delta: F2, F3, F5, F9..F13; T-05 on the delta |
| solution-architect | One PR comment on H: R1 as widened accepted, and the ruling carries, because the delta is wider than its carry test. Not a review, not a loop |
| reviewer-performance | Not needed, unless the delta changes `validate`'s logic or adds child processes beyond F8's row |
| master | F14; decides attempt 2 |

- All listed items verified, no new Major or higher: **GO, no further fix.**
- New Minor or Info in the delta: rating and a tech-debt issue, no commit. A reviewer's added mutant is a finding, not a listed check. Items ruled here are not reopened. A delta finding is measured against `main`.
- A miss on a Minor item alone (F3..F13): fixed in the same file under D-47, no new attempt.
- A miss on F1 or F2, an unapproved file, or a new Major or higher: attempt 3, loop 3 of 3, the last. A failure there goes to Santhosh.

**Conditions / remediation**
| # | Owner agent | Artefact | Required change | Due gate |
|---|-------------|----------|-----------------|----------|
| C42 | qa-engineer | `docs/07-qa/test-plan.md` | OQ-3 and R-10 closed (D-80). NT-01 says "valid arguments" and states that invalid input beats the refused hook (QUA-62). NT-09 and section 11 follow the PO's answer on QUA-63. AC-4 rows for the O1 classes | Before the PGD-16 G7 report |
| C43 | product-owner | Jira PGD-16 | Estimate phrase and Tasks line (c.10299). AC-7 notes `ValidationResult.request`. Dev Context drops "in `runner.run`", per the SA. File list gains `console.py`, `fake_time.py`, `test_gateway_httpmock.py`, `bootstrap.py`, `errors.py`, `models.py`, `test_import_boundaries.py`. Trace line cites FR-015 v0.5. States whether the future-end warning stays before `build_deps` (QUA-63); master recommends it stays | Before G7 PGD-16 |
| C44 | product-manager; ux-expert | PRD section 14.3; ux-spec section 12 | PM: add PA-12 to section 14.3, which G8 reads; say whether PERF-20 needs a number. ux-expert: add the A-3 and A-4 lines | PM: with C36, at the latest the sprint-02 G4. ux-expert: sprint-02 G4 |
| C45 | scrum-master | `sprint-01-plan.md`; Jira PGD-17 | Rows: #42 → PGD-17, before its G5, no AC change, estimate confirmed; #43 → the FR-048 story in the follow-ups table, naming the SA condition | #42 row before PGD-17 starts, with C40; #43 row by the sprint-02 G4 |

Earlier conditions: C34, C38 (a), C39 (a), (b), (c), (d) closed. C41 (c) stays due before the PGD-16 G7. At G7 PGD-16: QA tests H only, PGD-69 and #39 verified, #38 named as closing with the merge.

**Logged today:** D-80 (PO), D-81 (PM), D-82 (scrum-master, go-ahead, T-10).

**Risks registered:** no new risk. RISK-026 stays 4: AC-9 holds on the head, unmerged; it closes when PGD-69 closes. RISK-010 and RISK-021 notes added. RISK-005, 011, 020, 023, 025 unchanged.

**Rationale:**
- QUA-57 is the D-57 case: the AC names the Given and the Given fails. Everything offered against Critical is likelihood or size. The check worth running was the fix, not the finding: the SA's tuple clears the reviewer's row and leaves three of the same family on the failure line, so the outcome was written first and the recipe widened to meet it.
- STD-64 was the harder call. The stated reason for Major was size, and the scale's words have no behaviour clause, so master followed the words and stated the cost of doing so. It changes no fix and no loop here. Both Criticals are named to the delivery lead.
- The story is close: AC-9, the hard point, held. The exit rule keeps a verified fix from spending a further loop.

**Posted:** PR #41 comment 6541541697; Jira PGD-16 c.10309; risks PGD-1 c.10310; new issues #42, #43.

---

## G6 – Peer Review — STORY-02.03 (PGD-16), attempt 2 — 2026-10-31

- **Decision:** GO, under exit rule D-78, no further fix (D-83)
- **Decided by:** master  ·  **Human override:** none  ·  **Human approval required:** no; D-75 and D-76 stay named to the delivery lead, who may overrule them
- **Attempt:** 2, loop 2 of 3. Head `c8b76ae`, base `main` `9a1ffe5`; the head is frozen for G7
- **Artefacts evaluated:**
  - Reviews 5722358281 (quality) and 5722291466 (standards) on `c8b76ae`, bodies read with `gh api`; 43 reviews on the PR, all `COMMENTED`. Review 5722048956 (performance, attempt 1) carries. SA confirmation PR #41 comment 6542039822, read in full.
  - PR #41 body at `c8b76ae`, Fix loop table and Corrections 1..6. Jira PGD-16 description, PO amendment 2, c.10312, c.10313, c.10315..10318. PGD-69 and #39, #38, read directly.
  - Source at `c8b76ae`: `infra/tz.py`, `bootstrap.py`, `cli/main.py` in part, `tests/unit/test_import_boundaries.py`, the package delta and the `tests/e2e/test_invalid_input.py` delta; `docs/07-qa/test-plan.md` read for OQ-3, R-10, NT-01, NT-09, DEF-007.
  - Check runs on `c8b76ae`: 10/10 `success`, read by master, run 41190187409. `main` `9a1ffe5` read from GitHub; `mergeable_state` clean.

| # | Check | Mandatory | Result | Evidence |
|---|-------|-----------|--------|----------|
| 1 | Three reports present | ✱ | ✅ | Quality and standards APPROVE on `c8b76ae`; performance carries, D-78's rule not met (row 6) |
| 2 | Zero open Blocker/Critical | ✱ | ✅ | QUA-57, STD-64 = QUA-58 fixed and verified. 0 new findings from both reviews |
| 3 | Majors fixed or accepted | | ✅ | None |
| 4 | F1, O1 | | ✅ | Quality 72 of 72 registry rows, 42 of 42 subclass rows; master's table below |
| 5 | F2, O2 | | ✅ | Standards by reading; the stated gap is filled by master's run (D-84), table below |
| 6 | Performance trigger | | ✅ | Quality: `validate` AST equal; 218 to 219 children, F8's row only. Master read the e2e delta: one new test, one child |
| 7 | Nine mutants, F4, F6, F7, F8 | | ✅ | Quality: each fails a named test on the whole suite, V5 control survives with the row deselected. Master reran T5, T6 |
| 8 | F3, F5, F9..F13, T-05 | | ✅ | Standards. Master read the package delta and raises nothing |
| 9 | SA one comment | | ✅ | c.6542039822: ruling carries, R1 as widened accepted, D-44 condition met |
| 10 | Orchestrator items | | ✅ | c.10314: 16 files, all on the list, no manifest. Rerun 1447 passed, 12 skipped, 99.89 %; ruff, mypy --strict, bandit clean. Quality's 13th skip is the export ("not a git work tree") |
| 11 | F14, PR text | | ✅ | Read below (D-85) |
| 12 | #38 rows on this head | | ✅ | QUA-53 `test_fake_gmail_canonical.py:294`; QUA-54 `:340`; QUA-55 `test_select_range.py:326`; no `type: ignore` in that file; STD-62 no `STD-53` or "decision 4"; STD-63 `test_exit_statements.py:23` |
| 13 | Findings cite file:line | | ✅ | No new finding; replies are in the original threads |

**Master's probes** (fresh `git archive` of `c8b76ae` in the scratchpad, folder `g6m16b`; Windows, CPython 3.12.10, tzlocal 5.4.5; scripts `reg_child.py`, `reg_run.py`, `f2_mut.py`, `rows.py`). Nothing was deleted; the folders remain.

| O1, real child, real mode and hook | Lookups | Builds | Result |
|---|---|---|---|
| `no-key`, `no-values`, `unknown-name`, `open-fails`, `denied`, `dword`, `binary`, `none`, `dst-off-fraction`, valid dates | 1 | 0 | exit 2, AC-4 sentence only |
| `no-key`, `dword`, `binary`, `none`, `--start x` | 1 | 0 | exit 2, date line, then zone line |
| `no-key`, `open-fails`, `dword`, `--tz UTC` | 0 | 1 | exit 3 real, exit 0 hook |
| Control `good` | 1 | 1 | exit 3 real, exit 0 hook |

34 children, 17 rows each mode; `gmail_pdf.__file__` asserted inside the export; working directory empty.

| F2 mutant, one fresh copy each, `test_import_boundaries.py` | Result |
|---|---|
| M0 control, a comment | 38 passed |
| A0 attempt 1 import restored | `test_the_real_package_obeys_the_layering_rules` fails |
| A1 `from ..infra import tz` in `cli/main.py` | same test fails |
| A2 `import gmail_pdf.infra.tz` in `cli/console.py` | same test fails |
| A3 `from gmail_pdf import infra` in `cli/args.py` | same test fails |
| A4 function-local import in `cli/main.py` | same test fails |
| A5 new `gmail_pdf/gui/app.py` importing `infra.tz` | same test fails |
| R1 whole rule removed | 5 synthetic rows fail |
| R2 `gui` half removed | 2 rows fail |
| R3 `cli` half removed | 3 rows fail |
| T5 drop `AttributeError`; T6 drop `TypeError` (zone test files) | 2 rows each, named |

Also: `cli/main.py` AST equal between `93fb918` and `c8b76ae` apart from imports and docstrings, so O2's "no behaviour changes" holds for that file. AC-9 sample rows from attempt 1 rerun, results as recorded on `93fb918`, plus `from_days(1970-01-01, UTC)` gives "at or before the epoch".

Limits: 3.12.10 only. The registry is faked. Master's mutants ran on test subsets; the whole-suite mutant runs are quality's, the whole-suite pass is the orchestrator's and quality's. An AST walk does not see `importlib`; `gmail_pdf/cli/` has no such call. `gmail_pdf/gui/` does not exist yet, so A5 added it. No real Gmail call.

**Rulings** (D-83, D-84, D-85). Attempt 1 ratings are not reopened. No new finding, no new tech-debt issue, #42 and #43 unchanged.

**Conditions / remediation**
| # | Owner agent | Artefact | Required change | Due gate |
|---|-------------|----------|-----------------|----------|
| C41 (a), remainder | qa-engineer | Jira PGD-69 | Summary still reads "or in a zone east of UTC"; the condition required it gone, and c.10288 reported (a) done. #39's title is right | Before the PGD-16 G7 report |
| C41 (c) | qa-engineer | `docs/07-qa/test-plan.md` | Unchanged: the plan has no DEF-007 row yet | Before the PGD-16 G7 |
| C42 | qa-engineer | `docs/07-qa/test-plan.md` | Unchanged: OQ-3 and R-10 still open in the plan. QUA-63 now has the PO's answer (c.10312). O1 rows use the five classes | Before the PGD-16 G7 report |
| C43, remainder | product-owner | Jira PGD-16 | Listed items read done (c.10312). The SA's three lines join it (c.10315). Not a blocker: no AC changes | Before G7 PGD-16; open at the decision it is ⚠️, not ❌ |

**G7 PGD-16:** QA tests `c8b76ae` only, and `git diff c8b76ae <head> -- gmail_pdf tests` stays empty to the merge. DEF-005 M13, M22, M20, M23 fail at 17, 5, 3, 3; another figure is reported, not explained away. Report read against the plan by row. QA posts Verified on PGD-69 and #39 (Jira has no Verified status) and sets PGD-16 Done on G7 GO.

**After the merge** (order per D-85; the PGD-15 closure is the precedent): qa-engineer closes #39 and PGD-69; orchestrator closes #38; master closes RISK-026 once PGD-69 closes; STORY-01.04's hard stop lifts then. **Name in the merge request:** #38, #39, PGD-69 and their closers; the New_York change (D-81); the two-line output of QUA-63; the faked-registry limit; #42, #43.

**Risks registered:** no new risk. RISK-021 and RISK-026 notes added, scores unchanged. RISK-005, 010, 011, 020, 023, 025 unchanged.

**Rationale:** D-78's list is met and the one stated gap was closed by a run, not waived. A named verifier's check that could not be run is either run by someone else or stays open, and here it ran. The reviewers found nothing new, and master's own rows found nothing either. The story ends G6 within the loops allowed, with AC-9 still holding.

**Posted:** PR #41 comment 6542299100 (edited once after posting, to drop an `@` mention that was not a GitHub login; the content is unchanged); Jira PGD-16 c.10320.

---

## G7 – QA Acceptance — STORY-02.03 (PGD-16) — 2026-10-31

- **Decision:** GO (ACCEPT) (D-86). qa-engineer sets PGD-16 Done now. **Merging PR #41 needs the delivery lead** (`MERGE_POLICY = docs-auto, code-human`); no merge in this run. The merge precondition and the items to name are below
- **Decided by:** master  ·  **Human override:** none  ·  **Human approval required:** no for G7; the code merge is Santhosh's
- **Attempt:** 1
- **Artefacts evaluated:**
  - `docs/07-qa/PGD-16-test-report.md` at `c66257d`, read in full. The code under test is `c8b76ae`.
  - QA summary PR #41 comment 6542876885; Jira PGD-16 description and c.10319..10324; PGD-69 and c.10322; #39 comment 6542873957; PGD-72; PGD-17; #38, #42.
  - `docs/07-qa/test-plan.md` v0.3 at `4211f2f`, all sections, against the report row by row; PRD FR-015, FR-043, FR-045; catalogue CFG-01, CFG-02; G6 decision 6542299100; D-51, D-65, D-75..85.
  - Source read at `c8b76ae`: `cli/main.py`, `cli/args.py`, `infra/tz.py`, `domain/query.py`, the `runner.py` and `console.py` delta, `tests/e2e/test_invalid_input.py` lines 128..150, `redaction.py` constants.
  - Check runs on `c66257d`: 10/10 `success`, run 41197671982, `pull_request`, attempt 1, every job's `head_sha` `c66257d`, read by master; per-leg totals from the job logs. `mergeable_state` clean. `main` `9a1ffe5`. Merge ref now `b740312`. 43 reviews, all `COMMENTED`. PR #41 is the only open PR.
  - `git reflog`: the main checkout sat on the branch at `c8b76ae` from 06:42:56 to 07:38:04, which agrees with the report's Environment row. `c66257d` adds the report only; `git diff c8b76ae c66257d` shows that one file.

| # | Check | Mandatory | Result | Evidence |
|---|-------|-----------|--------|----------|
| 0 | C41 (a) remainder, C41 (c), C42 | | ✅ | PGD-69 summary read on Jira, no "east of UTC". Plan v0.3: sections 14, 15 DEF-007 and O1 rows; NT-01, NT-09; R-10, OQ-3 closed; Annex B 0.3. Closed; C41 is closed whole |
| 1 | Every AC has a verification result with evidence | ✱ | ✅ | QA matrix AC-1..9 Pass. Master reran AC-4, AC-6, AC-9 in real children (table below) |
| 2 | No open Sev-1/Sev-2 defects | ✱ | ✅ | QA raised none. DEF-007 Verified on `c8b76ae`, closes with the merge |
| 3 | Regression recorded and green | ✱ | ✅ | QA 1447 passed, 12 skipped, four runs and per file; 99.89 %; diff-cover 100 %. Merge ref as a work tree 1447/12. CI on the PR head 10/10; legs below |
| 4 | Exploratory notes present | | ✅ | EC-3, EC-4, EC-9; fuzz of 200,000 triples |
| 5 | Accessibility (UI stories) | | n/a | No UI |
| 6 | Sev-3 fixed or accepted | | ✅ | DEF-007 fixed by AC-9 |
| 7 | Traceability sample | | ✅ | GOAL-07 → FR-015 (PRD line 93) → PGD-16 AC-9 → `tests/e2e/test_invalid_input.py:342` `req("AC-9", "DEF-007")`. Reverse: that test → AC-9 → FR-015 → GOAL-01, GOAL-07 |
| 8 | G6 conditions (D-85) | | ✅ | QA tested `c8b76ae` only; DEF-005 17, 5, 3, 3; PGD-69 and #39 Verified; `git diff c8b76ae c66257d -- gmail_pdf tests` empty |
| 9 | Report read against the plan, row by row | | ⚠️ | Four rows short, closed by master's runs; corrections below |
| 10 | C43 remainder | | ⚠️ | SA's three lines read done (c.10319, PO amendment 3). PGD-72's summary still says "and runner" (ruling 5) |

**Master's probes** (fresh `git archive` of `c8b76ae` in the scratchpad, folder `g7m16`; Windows, CPython 3.12.10; real child interpreters; guard on; `gmail_pdf.__file__` asserted inside the export; expected values written from the story text; scripts `p_g7.py`, `c_audit.py`, `p_gw16.py`, `p_mut.py`, `p_def005.py`). Nothing was deleted; the folders remain.

| Row | Result |
|---|---|
| AC-4 `--tz`: `Mars/Olympus`, `IST`, empty, trailing space, `Asia\Kolkata`, `utc`, `asia/kolkata`; `UTC`, `Asia/Kolkata`; `-m`, shim, exe; hook and real | 54 of 54: exit 2 with the exact line, stdout empty, nothing created; accepted names exit 0 hook, 3 real |
| AC-4, no `--tz`, `tzlocal` patched to raise: `LookupError`, `KeyError`, `IndexError`, `ZoneInfoNotFoundError`, `ValueError`, `UnicodeDecodeError`, `OSError`, `FileNotFoundError`, `PermissionError`, `AttributeError` and a subclass, `TypeError` and a subclass; both modes; valid dates and `--start x` | 52 of 52: exit 2, date line first where one applies, 1 lookup, 0 `build_deps`, 0 `runner.run` |
| AC-4, system zone returns empty, `No/Such`, `IST`; both modes | 6 of 6 |
| AC-4, `--tz UTC` with the lookup failing | 4 of 4: 0 lookups |
| AC-6, audit hook in the child: bad start, bad end, lone start, lone end, reversed, below the floor, above the ceiling, bad zone, future end with a bad zone, sentinel start; both modes | 20 of 20: exact lines, 0 builds, 0 runs, 0 socket, write or temp events, no file opened outside the interpreter and the package, working directory empty. Lone-date rows have no `--tz`, so the registry is read: 14 `winreg` events and no other |
| AC-6, `--sta`, `--en`, `--t`; both modes | 6 of 6: exit 2, usage then `unrecognized arguments`, 0 builds |
| AC-6 contrast and order | Valid hook: mailbox opened, 1 build, 1 run. Valid real: 1 build, exit 3. Refused hook with a bad date: exit 2, the date line. Empty `USERPROFILE`, `APPDATA`, `LOCALAPPDATA`: nothing created |
| AC-9 decision table: starts `0001-01-01`, `1960-01-01`, `1969-12-31`, `1970-01-01`, `1970-01-02`, `2000-01-01`, `2026-03-01`, `9999-12-30`, `9999-12-31`; ends `1950-01-01`, `1970-01-01`, `1970-01-02`, `2026-04-30`, `2026-12-31`, `9999-12-30`, `9999-12-31`; 7 zones and `Mars/Olympus`; both modes | 1008 of 1008, stdout, stderr and exit equal to an oracle from AC-3, AC-5 and AC-9; 0 unexpected-failure lines |
| AC-9 floor and ceiling, all 598 zones, real children on the hook | 1196 of 1196 |
| `q` through `runner.run` and the real gateway on `HttpMockSequence`, 598 zones × floor, ceiling, floor..ceiling | 1794 of 1794 equal to `after:{S-1} before:{E+1}` computed from wall midnight and `utcoffset`, not from `daterange.py`; smallest `after:` 35999 |
| DEF-005 M13, M22, M20, M23, one fresh copy each, module printed inside it, whole suite minus `test_gitignore_matching.py` | **17, 5, 3, 3**, the tests QA names. Control C0: 1400 passed, 12 skipped |
| Plan section 7: E1 constant back, E2 flag literal in `messages.py`, E3 sentence in `cli/main.py`, E4 `messages` imported in `args.py`, E5 flag renamed, E6 second `RunRequest(`, E7 sentence in `infra/tz.py` | Each fails one named test in `test_validation.py`. Control E0: 172 passed |
| E8, neither date goes to validation when `--tz` is given | Fails only `test_with_neither_date_the_usage_text_and_exit_zero_stay[only-tz]` |
| NT-05 on a built wheel (`python -m build --wheel --no-isolation`) | `gmail_pdf-0.9.0.dev0-py3-none-any.whl`, 30 entries, no `tests`; `find_spec("tests")` None; `-m` exit 1 with the source-checkout line; invalid input exit 2; nothing created |
| NT-04 sweep, depth 1..3000 step 25, `parts` and resource value | 240 runs: parts 4 success (1..76), 116 fixed line (from 101); resource 8 success (1..176), 112 fixed line (from 201). 0 unexpected, 0 other. Same edges as `7883f9c` |
| Neither date: `--tz Mars/Olympus` both modes, `--tz UTC`, no arguments, `--help --tz Mars/Olympus` | Usage on stdout, exit 0, stderr empty, 0 lookups, 0 builds, 0 runs, nothing created |
| No arguments with `tzlocal` failing (`LookupError`, `TypeError`) | Usage, exit 0, 0 lookups |
| CI legs on `c66257d`, job logs read | Windows 3.10, 3.11, 3.12: 1447 passed, 12 skipped. Ubuntu, macOS: 1456 passed, 3 skipped. `test_token_location_warning.py` has three `WINDOWS_ONLY` marks (lines 144, 151, 158), so the 12 Windows skips ran on the POSIX legs, by arithmetic and the markers |

Limits: Windows, 3.12.10 only. Master's AC-4 class rows patch `tzlocal`, as the AC says; the faked-registry rows are QA's 48 and master's 34 at G6, on this head, no real registry. The exe rows put the export first on `PYTHONPATH` but may load the venv's editable install, which is the same commit, clean. `test_gitignore_matching.py` (47 tests) is out of master's runs for the scratch path length; QA and CI ran it. cp1252 rows are QA's. The wheel ran through `-m` only; the CI `package` job installs one. My first AC-6 run gave four BAD rows: the expected list was mine and allowed no registry read on rows with no `--tz`. Rerun with that stated, and each row shows only `winreg` events. My first probe also lacked `sys.exit(rc)` in the wrapper. No real Gmail call.

**Report corrections** (the report stays as committed: a docs commit restarts CI on the head):
- **NT-05:** the plan says a built wheel; QA used a `gmail_pdf`-only `git archive`, the row reads Pass, and Known Limits says a wheel was not checked. Same short row as PGD-15. Master built one. "Pass" holds with that run.
- **NT-04:** 26 rows, not the plan's sweep of 1 to 3000 in steps of 25. Same short row as PGD-15. Master ran it. "Pass" holds with that run.
- **Plan section 7:** QA's 17 mutants hit the rules. AC-7's new enforcement tests were not mutated by QA, and the row credits other roles' runs. Master ran E1..E7; G6 covered the boundary rule and F4. "Pass" holds with those runs.
- **Plan section 15, O1:** the row reads each class and a subclass. QA's 12 rows have no `ValueError` and no subclass of `ValueError`, `AttributeError` or `TypeError`; the in-repo rows and quality's cover classes. Master's 52 rows cover them. "Pass" holds.
- **AC-6:** "0 files opened" stands. A rejected input with no `--tz` does read the registry; AC-6 does not forbid that, it holds no credential, and it is deviation 7.
- **c.10323** says Done "after a GO and the merge"; the report's Sign-off says Done on GO. D-85 governs: Done now.
- `408b7bd` is the merge ref QA tested; GitHub rebuilt it as `b740312` after the report commit. The two differ by the report only.

**Rulings and dispositions**
| # | Item | Ruling |
|---|---|---|
| 1 | C41 (a) remainder, C41 (c), C42 | **Closed.** C41 closes whole. The plan's Status line stays stale, under C32 extended |
| 2 | G7 | **GO** (D-86). Every mandatory item passes |
| 3 | `--tz Mars/Olympus` with neither date | **AC-4 is delivered. No defect. Info, type Requirement** (D-87). PO rules what follows; C46, row on STORY-07.01 |
| 4 | QA's `gh api --allow-escape-sequences` | **No record beyond the report and this line.** A CLI safeguard on terminal output, not a permission denial: nothing in the settings names it, the call was a read of our own CI logs, and the output went to a scratchpad file and was stripped before reading. `gh run view <run> --log --job <id>` printed the same logs to a file for master with no flag, so the next run uses that |
| 5 | PO's remaining lines | SA's three: read done on PGD-16, closed. **PGD-72's summary should read "in cli.main":** a Done sub-task, no AC, D-85 said "may". C43 remainder, product-owner, due with C40. Not a merge condition |
| 6 | Closure | **Confirmed, D-85 stands.** PGD-16 is set Done now; the open "PGD-69 blocks PGD-16" link does not hold it. After the merge SHA is relayed: qa-engineer closes #39 and PGD-69; orchestrator closes #38; master closes RISK-026; STORY-01.04's hard stop lifts then |
| 7 | PGD-17 | **It cannot proceed without PGD-16 merged, so under the delivery lead's instruction it does not start** (D-88) |
| 8 | Risks | No new risk. RISK-026 stays 4 until PGD-69 closes. RISK-020 note added, score 4 |
| - | Long-path failure in the merge export | Environment, as at PGD-15: deterministic on path length, passes under 260, CI passes. Not a flaky test under plan section 7 |

**Conditions / remediation**
| # | Owner agent | Artefact | Required change | Due gate |
|---|-------------|----------|-----------------|----------|
| C43, remainder | product-owner | Jira PGD-72 | Summary reads "in cli.main", not "in cli.main and runner". The SA's three lines are closed | With C40, before PGD-17 starts |
| C45, extended | scrum-master | Jira PGD-17 | Added: a "PGD-16 blocks PGD-17" link, and the Dependencies line names PGD-16 for the AC-3 warning, the five shared files and #42 (D-88) | With the #42 row, before PGD-17 starts |
| C46 | product-owner, scrum-master | `sprint-01-plan.md` follow-ups; STORY-07.01 when drafted | PO states what ends the neither-date path: whether it stays exit 0 given CFG-01, CFG-02 and FR-043, and what a given but invalid value (`--tz Mars/Olympus`) does on it. Master recommends that every given value is checked. Scrum-master adds it to the STORY-07.01 row. A change to FR-043 or FR-045 goes through the product-manager (rule 6). The `only-tz` test row changes with the ruling | Sprint-02 G4, and before STORY-07.01 is Ready |

Earlier conditions: C41 closed. C42 closed. C43 remainder and C45 restated above. C11–C14, C20, C23, C25, C26, C29, C31, C32 (extended), C33 (Jira part), C36, C37 (b, c, d), C38 (b, c), C40, C44 stay open, due as recorded.

**Closure after the merge.** On the orchestrator's relay of the merge SHA: qa-engineer closes #39 and PGD-69 and comments on PGD-16; the orchestrator closes #38; master closes RISK-026 and records it; STORY-01.04's hard stop (D-67) lifts then. Master transitions nothing.

**Merge precondition (orchestrator; re-read at the moment of the request):**
1. PR head still `c66257d`, and `git diff c8b76ae <head> -- gmail_pdf tests` empty.
2. 10/10 `success` from check runs on that exact head. Read now: run 41197671982.
3. RISK-023: the `main` that run tested equals current `main`, now both `9a1ffe5`. If not, update the branch and re-read CI. That merge is not a commit for D-62 as long as the code diff holds only what `main` brought; if `main` changed `gmail_pdf/` or `tests/`, return to master. The status branch is not merged to `main` before PR #41.
4. No `REQUEST_CHANGES` review outstanding. Now 43 reviews, all `COMMENTED`. `mergeable_state` clean.
5. qa-engineer has set PGD-16 Done; PR labelled `gate:g7-pass`.

**Items to name in the merge request:** #38, #39 and PGD-69 close with the merge, and who closes them; RISK-026 and STORY-01.04's hard stop follow; the New_York change: `1970-01-01..` in America/New_York was exit 0 and is now exit 2 (D-81); QUA-63's two-line output: a future `--end` with a failing build prints the warning, then the fixed line (D-79); the faked-registry limit: AC-4's system-zone rows ran over a faked `winreg`, never a real registry, and a class outside the five is exit 1 by O1; #42 and #43; D-75 and D-76's scale wording, still his; **new:** a bad `--tz` with neither date prints usage and exits 0 until STORY-07.01 (D-87, C46); **new:** PGD-17 waits for this merge (D-88). RISK-005 stays 10, RISK-011 8, RISK-025 9. PA-12 goes to him at G8 (C44).

Follow-ups (not conditions): qa-engineer sets Done. Orchestrator sets the label and requests the human merge.

**Risks registered:** no new risk. RISK-020 and RISK-026 notes added, scores unchanged. RISK-005, 010, 011, 021, 023, 024, 025 unchanged.

**Rationale:**
- All three mandatory items have evidence, and master reproduced the three the brief named. GO, not CONDITIONAL GO: both ⚠️ rows are non-mandatory, the report rows held when run, and C43, C45, C46 are follow-ups, as C39..C41 were at the PGD-15 G7.
- The hard question was a command AC-4 appears to name and the code does not reject. It turned on testing the reading, not on likelihood: read over AC-1, AC-4's own second limb would turn bare `gmail-pdf` on a broken zone into exit 2, and nobody asked for that. It is not closed as nothing, because a script does get exit 0 with nothing done, against CFG-01 and FR-043. That is the interim AC-1 dated, so it needs a carrier, not a defect.
- PGD-17 is a question of fact, and the fact is on `main`: the warning its Testing Notes need is not there.

**Posted:** PR #41 comment 6543091879; Jira PGD-16 c.10325 (edited once, to link the comment; the content is unchanged).

---

## G6 – Peer Review — STORY-02.06 (PGD-17) — 2026-10-31

- **Decision:** CONDITIONAL GO (D-90). C47 is a scoped pre-G7 condition under D-47, with the exit rule below (D-92). Orchestrator: PGD-17 to Changes Requested, label `gate:g6-changes`, until C47 is verified; then In QA and `gate:g6-pass`, with no further G6 decision
- **Decided by:** master  ·  **Human override:** none  ·  **Human approval required:** no
- **Attempt:** 1, loop 1 of 3. Head `8a000e4`, base `main` `19f1157`
- **Artefacts evaluated:**
  - Consolidated findings PR #44 comment 6545244329; reviews 5723479229 (quality), 5723063837 (standards), 5723123007 (performance), bodies and all 14 inline comments read with `gh api`; SA ruling 6544413346; G5 comment 6544277371. 3 reviews, all `COMMENTED`.
  - Jira PGD-17 description, AC-1..5 as amended, c.10331, c.10332, c.10334..10341, issue links, remote links 10010, 10011; PGD-16 AC-6; PGD-72; #38, #40, #42.
  - Source at `8a000e4`: the whole `gmail_pdf/` diff, `tests/unit/test_cli_list_failure.py`, `tests/unit/test_cli_invalid_input.py` lines 150..216, `tests/support/gateway_rig.py`, `tests/conftest.py` restore. PR body at the same head.
  - `sprint-01-plan.md` at `cf6716c`, `test-plan.md` v0.3 (sections 11, 15), `git log --merges`, repository merge settings, PGD-1 c.10292, c.10293, c.10327..10333.
  - Check runs on `8a000e4`: 10/10 `success`, run 41207307634, read by master. `main` `19f1157`, `feat/PGD-17-empty-range` `8a000e4`, read with `git ls-remote`. `mergeable_state` clean. PR #44 labels unchanged by master.

| # | Check | Mandatory | Result | Evidence |
|---|-------|-----------|--------|----------|
| 0 | Prerequisites C40, C43 remainder, C45 extended | | ✅ | PGD-17 AC-4 and Dev Context; PGD-72 summary; link 10028; remote links; plan rows 117, 135, 136. Closed (D-96) |
| 1 | Three reports present | ✱ | ✅ | Reviews above: quality and standards APPROVE WITH COMMENTS, performance APPROVE |
| 2 | Zero open Blocker/Critical | ✱ | ✅ | None raised. QUA-67, QUA-68 tested for more than Minor: they stay Minor (D-91) |
| 3 | Majors fixed or accepted | | ✅ | None raised, none re-rated |
| 4 | Findings cite file:line | | ✅ | All inline but STD-85, a commit message, which has no code location |
| 5 | Architecture acknowledgement (D-44) | | ⚠️ | All five acknowledged, conditional on R1, which is not on the branch; fix-now (D-90, D-95) |
| 6 | ACs, CI | | ✅ | Quality AC table: AC-1..5 met, AC-4 with a test gap. Orchestrator: 1538 passed, 12 skipped, 99.89 %; ruff, mypy --strict (25 files), bandit clean. CI 10/10 |
| 7 | T-05 interim control | | ✅ | Reviewer-standards pass; master's grep over the added lines: no hit |
| 8 | Issues tied to this story | | ⚠️ | #42: four rows read done, PERF-17 reads done only on the C47 head (D-94). #40: stderr rule delivered, stays open for STORY-07.02 |
| 9 | Traceability sample | | ✅ | GOAL-01 → FR-016 (PRD line 94) → PGD-17 AC-1 → `tests/e2e/test_empty_range.py` line 60 `req("AC-1", "AC-2")`, module `req("FR-016", "EC-06")`. Reverse: `test_cli_list_failure.py` `req("FR-016", "EC-06", "AC-4")` → AC-4 → FR-016 → GOAL-01 |

**Master's probes** (fresh `git archive` of `8a000e4` in the scratchpad, folder `g6m17`, one fresh copy per row; Windows, CPython 3.12.10; `gmail_pdf.__file__` asserted inside each copy; whole suite minus perf; scripts `fixapply.py`, `drive.py`, `child.py`). Nothing was deleted; the folders remain. "With the fixes" means R1 as the SA wrote it, QUA-67's snippet with annotations added, and QUA-68's three lines.

| Row | Head as reviewed | With the fixes |
|---|---|---|
| Control | 1537 passed, 13 skipped | 1541 passed, 13 skipped, 99.89 % |
| F7 `runner.run` catches `GmailApiError` and returns an empty `COMPLETED` | **Survives** | Fails `list-404`, `list-403` |
| F9 the same catch in `cli._execute` | **Survives** | Fails `list-404`, `list-403` |
| F11 the planner skips a message whose `get_message` fails | **Survives** | Fails `get-message-503` |
| Z1 a file created for the rejected zone `IST` | **Survives** | Fails `[test-hook-IST]`, `[real-mode-IST]` |
| Z2 a file created for any rejected zone | Fails 9, all child rows | Fails 23 |
| L1 the library's `NullHandler` removed in `conftest` | **Survives** | Fails R1, `list-403` |
| L2 `main`'s call removed | Not rerun here; the PR, quality and the SA report it failing | Fails 6: three leg (b), R1, `get-message-503`, handler-once |

| AC-4 and empty rows, real child, no pytest, 0 root handlers, real `main` and `GmailGateway` over `HttpMockSequence` | Result |
|---|---|
| 503 x 6; 429 x 6; 403 `rateLimitExceeded` x 6; 403 `insufficientPermissions`; 404; 400 | exit 1, stdout empty, stderr exactly the one line, nothing created |
| Empty answer; two 503s then an empty answer | exit 0, `No PDFs found`, `0 PDFs found.`, stderr empty, nothing created |
| Harness control: 503 x 6 on a copy with `main`'s call removed | The five `Retrying` lines, then the error line, exit 1. The harness sees the failure |
| QUA-71, `test_cli_list_failure.py` alone: handler added late, with the restore / without it; call removed, with the restore / without it | 3 failed / 0 failed; 4 failed / 4 failed. The restore matters for a late handler, not for a removed call, as QUA-71 says |

Also: with the fixes the two files stand alone (24 and 75 passed), ruff and format clean, 292 and 340 lines, coverage 99.89 % unchanged. A work tree adds the one test an export skips, so H should show **1542 passed, 12 skipped**.

Limits: Windows, 3.12.10 only. The fixes ran on copies, not on the branch. No real Gmail, no real credentials. Scripted transport. Master's runs add nothing for 3.10, 3.11, Ubuntu or macOS; CI does.

**Ratings and dispositions** (D-91, D-93, D-94)
| Finding | Reviewer | Master | Disposition |
|---|---|---|---|
| QUA-67 `test_cli_list_failure.py:200` | Minor | Minor | F2 |
| QUA-68 `test_cli_invalid_input.py:213-216` | Minor | Minor | F3 |
| QUA-69 | Info | Info | #36, STORY-01.04 |
| QUA-70 | Info | Info | Closed by F2's `get-message-503` row |
| QUA-71 | Info | Info | F4, PR text |
| QUA-72 | Info | Info | No action |
| STD-77 | Minor | Minor | No code; #36, SA's move trigger |
| STD-78, STD-79, STD-80, STD-81 | Minor | Minor | #45 |
| STD-82, STD-83 | Info | Info | #45 |
| STD-84 | Info | Info | No action |
| STD-85 | Info | Info | No rewrite; PR body stands; one line in the merge request |

**Fix list.** All owned by developer, one commit series, then H is frozen.
| # | Item | Files | Severity | Verified by |
|---|---|---|---|---|
| F1 | SA's R1: `test_leg_b_a_rate_limit_403_on_every_attempt_leaves_only_the_error_line`, name and body as in the ruling, its own test | `tests/unit/test_cli_list_failure.py` | SA condition (D-44) | quality |
| F2 | QUA-67, QUA-70: `test_every_failed_read_is_a_failed_run`, parametrized, rows `list-404`, `list-403`, `get-message-503`, asserting the outcome and the request count; annotated, `ok` and `Response` imported | `tests/unit/test_cli_list_failure.py` | Minor | quality |
| F3 | QUA-68: `test_a_zone_outside_the_iana_set_is_rejected_as_written_in_both_modes` runs in an empty working directory and asserts nothing was created, in both modes, in the form of its neighbour at line 161 | `tests/unit/test_cli_invalid_input.py` | Minor | quality |
| F4 | QUA-71: reword deviation 2 ("without it, a handler left by an earlier test hides a `main` that adds it too late"). "Every removed child has an in-process row" gains that the zone rows gained the created-files check at F3. Evidence and Follow-ups (`#45`) brought to H. Does not move the head | PR #44 body | none | master |

**Exit rule, C47 (D-92).** Scope: the two test files above and no others, no new file, nothing under `gmail_pdf/`, no manifest. Master makes no further G6 decision if it passes.
| Verifier | Must show on H |
|---|---|
| orchestrator | Diff `8a000e4..H` is those two files; `gmail_pdf/` diff empty; local rerun **1542 passed, 12 skipped**, ruff, format, mypy --strict, bandit; CI 10/10 from check runs on H; `main` compared (RISK-023) |
| reviewer-quality | Delta plus a fresh export: F1's text equals the ruling; L1 and L2 fail it; F7 and F9 fail `list-404` and `list-403`; F11 fails `get-message-503`; Z1 fails 2 rows of F3 |
| reviewer-standards | Delta: no suppression marker, the two files under 400 lines, T-05 on the delta |
| solution-architect | One PR comment on H: R1 landed as ruled and the ruling carries, because the delta is wider than its carry test. Not a review, not a loop |
| reviewer-performance | Not needed: no package change and no child process in the delta |
| master | F4; confirms C47 as G7 check 0 |

- All listed items verified, no new Major or higher: **C47 closes, no further G6 decision.** PGD-17 goes to In QA. The attempt stays 1 and no loop is spent.
- New Minor or Info in the delta: master rates it, a tech-debt issue follows, no commit. Rating is not a new attempt. A reviewer's added mutant is a finding, not a listed check. A delta finding is measured against `main`. Items ruled here are not reopened.
- A miss on F1, F2 or F3 alone: one correction in the same file under D-47, no new attempt.
- A second miss, a file outside the scope, any change under `gmail_pdf/`, or a new Major or higher: G6 attempt 2, loop 2 of 3, decided by master.
- A CI rerun of the same head after an infrastructure failure is not a failure (D-50).

**Conditions / remediation**
| # | Owner agent | Artefact | Required change | Due gate |
|---|-------------|----------|-----------------|----------|
| C47 | developer | The two test files; PR #44 body | F1..F4, exit rule above | Before G7 PGD-17 starts |
| C48 | scrum-master | `sprint-01-plan.md`; #45 | (a) STORY-07.02 row (line 115): the `NullHandler` stays and the "replaced" wording goes. The run-log handler goes on a parent of the retry logger, root recommended, never on the retry logger, no `propagate = False`. Tests through the real gateway: a normal run has five records in the file and one stderr line; a dry run has the same stderr and writes nothing. The comment at `cli/main.py:61` and AC-4's "until the run log exists" are updated then. The question below goes on the row. (b) STORY-01.04 row (line 116): extend the handler to `google_auth_httplib2` and `google.oauth2.credentials`; move it to `bootstrap`; test stderr with real `Credentials` over a scripted transport; `paths._discard` becomes a designed `warning:` line; revisit `test_a_warning_from_another_gmail_pdf_logger_still_reaches_stderr` (QUA-69). (c) A row on STORY-01.04/01.06 for the first story that adds a third `RunResult`: `print_summary`'s `else` and `exit_code` become explicit. (d) Name a story that exists in Jira for #45 | (a), (b), (c) before the PGD-17 merge request; ⚠️ at G7, not a blocker. (d) sprint-02 G4 |
| C49 | qa-engineer | `docs/07-qa/test-plan.md` | Section 11 NT-08 follows AC-4: stderr exactly the one line after any `warning:`, no retry notice, and it runs in-process, not as a child, because the hook cannot carry a fault (c.10331; #40 item 3). Section 15 PGD-17 row: 5 points, AC-4's rule and the two legs | Before the PGD-17 G7 report |

Question for ux-expert and product-owner, before STORY-07.02 is Ready: a failed dry run says "see the run log" and no log exists (SA; D-95). Not master's to decide.

Earlier conditions: C40, C43 (remainder), C45 (extended) closed (D-96). C11–C14, C20, C23, C25, C26, C29, C31, C32 (extended), C33 (Jira part), C36, C37 (b, c, d), C38 (b, c), C44, C46 stay open, due as recorded.

**G7 PGD-17:** C47 is check 0. C49 first. QA tests H only, and `git diff H <head> -- gmail_pdf tests` stays empty to the merge. Leg (b) fails with the `main.py` change removed (Testing Notes). DEF-005 M13, M22, M20, M23 fail at 17, 5, 3, 3. Report read against the plan by row; NT-04 and NT-05 come in short until C32.

**After the merge:** the orchestrator closes #42 (D-94, T-14). #40 stays open for STORY-07.02. **Name in the merge request:** #42's closer; #40 open; the PGD-18 question (D-97); STD-85's line (D-93); D-75, D-76 and the scale wording, still his; the failed-dry-run wording question.

**Logged today:** D-96 (C40, A-1, C43, C45, 5 points, 34 against 30, T-13 reused). **Rulings beyond the gate:** PGD-18 (D-97), c.10292 (D-98).

**Risks registered:** no new risk. RISK-010 and RISK-005 notes added, scores unchanged. RISK-011, 020, 021, 023, 024, 025 unchanged.

**Rationale:**
- Every mandatory item passes, so the label comes from the checklist: CONDITIONAL GO, not NO-GO, and not GO, because the SA's acknowledgement carries a condition that is not on the branch.
- The two ratings were the real question, and both stay Minor by the words of D-40, D-51 and D-65 (1). They are still fixed now, under D-79, because each pins an AC and sits in a file R1 or #42 already opens. "Rating" and "fix now" are separate questions.
- The delta is two test files by design, so C47 can end the gate with no further decision.

**Posted:** PR #44 comment 6545642477; Jira PGD-17 c.10342 (edited once, to link the comment; the content is unchanged); PGD-1 c.10343 (risks, PGD-18, c.10292). Issue #45; notes on #36 (6545544168), #40 (6545544701), #42 (6545545232).

---

## G7 – QA Acceptance — STORY-02.06 (PGD-17) — 2026-10-31

- **Decision:** GO (ACCEPT) (D-99). DEF-008 is Sev-3 and accepted for this exit (D-101). No merge in this run: `MERGE_POLICY` code-human
- **Decided by:** master  ·  **Human override:** none  ·  **Human approval required:** no for this gate; the merge is human
- **Attempt:** 1. Code head `48fea17`, PR head `aee5f56`, base `main` `19f1157`
- **Artefacts evaluated:**
  - `docs/07-qa/PGD-17-test-report.md` at `aee5f56`, read in full against `docs/07-qa/test-plan.md` v0.4 at `2dde0ef`, sections 2 to 16 and Annex A, by row.
  - QA summary PR #44 c.6546818154; PGD-17 c.10348..10353; PGD-82; #46; #42; #45.
  - G6 decision c.6545642477; quality review 5723760900 (body and the QUA-73 inline); standards review 5723696124; SA comment 6545847040; PR #44 body read against F4.
  - Source at `48fea17`: `app/planner.py`, `app/runner.py`, `cli/console.py`, `cli/main.py`, `domain/models.py`, `domain/validation.py`, `infra/gmail_gateway.py`, `tests/fakes/fake_gmail.py`, `fake_gmail_json.py`, `tests/support/`.
  - `sprint-01-plan.md` at `2dde0ef`, rows 113..116; PRD FR-011, FR-016, FR-043, NFR-014; EPIC-02 story list; D-49, D-51, D-55, D-57, D-65, D-67, D-68, D-85, D-87, D-88, D-89..D-98.
  - Check runs on `aee5f56`: 10/10 `SUCCESS`, run 41225166460, read by master after the one job still running had finished. `refs/pull/44/merge` `b09a1ed`, parents `19f1157` and `aee5f56`, tree equal to `aee5f56` (QA's `30e679a` is stale because GitHub rebuilt the ref, the same tree apart from the report). `mergeStateStatus` CLEAN; every review `COMMENTED`, no `REQUEST_CHANGES`. `git diff 48fea17 aee5f56 -- gmail_pdf tests` empty; one commit, the report only. PR labels and Jira status not changed by master.

| # | Check | Mandatory | Result | Evidence |
|---|-------|-----------|--------|----------|
| 0 | C47, F4 | | ✅ | Orchestrator, quality, standards and SA rows read. F4 read in the body: deviation 2 reworded, "every removed child" sentence states the F3 row, Evidence and Follow-ups at H. C47 closed (D-99) |
| 0 | C49 | | ✅ | Plan v0.4 at `f048000`: NT-08 two legs and the pitfall, PGD-17 row at 5 points. Closed. Its version cell still reads 0.3: C32 extended already covers it |
| 0 | QUA-73 | | ✅ | Info, row on #45 (D-100) |
| 1 | Every AC has a result with evidence | ✱ | ✅ | Report AC matrix; master's runs below |
| 2 | No open Sev-1 or Sev-2 | ✱ | ✅ | DEF-008 tested and stays Sev-3 (D-101). No other defect |
| 3 | Regression recorded and green | ✱ | ✅ | QA 1542 passed, 12 skipped x4, reversed, each of 43 files alone; CI 10/10 on `48fea17` (41217084383) and `aee5f56` (41225166460), POSIX legs 1551 and 3 read by QA. Master's fresh export, control row: 1495 passed, 12 skipped without `test_gitignore_matching.py` (47 tests, scratch path limit) |
| 4 | DEF-005 mutants (C30) | | ✅ | M13 17, M22 5, M20 3, M23 3 on master's fresh copies |
| 5 | Exploratory notes | | ✅ | EC-1, EC-6, EC-9 recorded; EC-6 found DEF-008 |
| 6 | Accessibility | | ✅ | n/a: no UI in this story |
| 7 | Report against the plan, by row | | ⚠️ | Four rows short (below), all closed by master's runs; NT-06's worker row is the known limit, C32 and RISK-024 |
| 8 | C48 (a, b, c) | | ✅ | Rows 115, 116 and the third `RunResult` row read against the condition text at `2dde0ef`. Closed. (d) stays due at the sprint-02 G4 |
| 9 | Traceability sample | | ✅ | GOAL-01 → FR-016 (PRD line 94) → PGD-17 AC-5 → `test_runner_empty.py::test_completed_with_no_messages_maps_to_exit_code_zero`, in QA's 14 of 14 and master's run. Reverse: `test_every_failed_read_is_a_failed_run` `req("FR-016", "EC-06", "AC-4")` → AC-4 → FR-016 → GOAL-01 |

**Master's probes** (fresh `git archive` of `48fea17` and `19f1157` in the scratchpad, folder `g7m17`, scripts `lib.py`, `c_gw.py`, `p_ac.py`, `p_nt.py`, `p_reg.py`; Windows, CPython 3.12.10; module path asserted in each export). The environment is built in Python. Before any child starts, a proof in the same environment, making no socket call, stops the driver unless `sitecustomize`, `socket_guard` and `guarded_connect` come from that export; each gateway child repeats the check first and exits 97 if it fails. Nothing was deleted.

| Row | Result |
|---|---|
| AC-1, AC-2, AC-3, controls: `-m` and shim x `PYTHONUTF8` set and unset; empty mailbox in Kolkata, UTC, Kiritimati; all-outside mailbox in Kolkata; future end; non-empty; real mode; exe | **29 of 29.** My first run read 12 BAD: the rows were mine. The "outside" mailbox is outside in Kolkata only, and inside a range to 2099, so `Messages in range: 1` was right. Expectations corrected, not the rule |
| AC-1 domain, AC-5 | `RunResult.COMPLETED`, `()`, exit 0, `is_empty` true; cancelled exit 1, not empty |
| `main` contrast | `Messages in range: 0` for the same empty file |
| AC-4: real `entry()`, real streams, real `GmailGateway` over `HttpMockSequence`, no pytest, 0 root handlers. 503, 429, 500, `rateLimitExceeded`, `userRateLimitExceeded` x6; 404, 403 denied, 401, 400; `get_message` 503 x6, 404; past and future end; two encodings | **44 of 44:** exit 1, empty stdout, exactly the one line after any warning, the right request count, nothing created, `NullHandler` on the retry logger |
| Controls: empty; two 503s then empty | The two lines, exit 0, empty stderr |
| `main`'s call removed | The five `Retrying` lines, then the error line |
| #42 removed values as real children | 34 of 34 |

**The report read against the plan.** Short rows, each run by master:
| Plan row | Short by | Master |
|---|---|---|
| NT-03 | QA's 14 shapes lack `parts` of `[5]`, `[null]`, `["x"]` and `labelIds` of `5`, `null`, `[[]]`, all named in the row | 12 of 12, two entry points: exit 1, the fixed line |
| NT-02 | Unreadable file not run on Windows (stated) | A locked file, `PermissionError` shown first: 2 of 2 |
| NT-04 | Cap, named depths and sweep not run (stated) | 248 children: 13 success, 235 fixed line, 0 unexpected-failure lines. 196 levels under a resource key pass, 197 give the line. Parts 247, 1000, 1400, resource 500, 2900, unread key 2900: the fixed line |
| NT-05 | A `git archive` copy, not a built wheel (stated) | Wheel built, 30 files, none under `tests`, `find_spec('tests')` None: exit 1, exactly the line; invalid input exits 2 |

NT-04 and NT-05 are the rows expected short until C32. NT-03's gap is the same class, so it joins C51. The report's other rows hold on reading. Its "header 0.4" is loose: the row reads "0.3 (... 0.4 closes C49 ...)".

**Rating and rulings** (D-100..D-104)
| Item | QA or reviewer | Master | Disposition |
|---|---|---|---|
| QUA-73 | Info | Info | Row on #45, no commit |
| DEF-008 | Sev-3 | Sev-3, wider than filed, accepted, armed | STORY-02.04, C50, C33 addition, RISK-027 |
| QA's socket lapse | Disclosed | No defect, no risk, no Bug | Plan section 4 sentence, C51 |
| #42 evidence | Pass | Holds on H | Closes with the merge (T-14) |

**DEF-008 rows** (`c_gw.py` and the hook; head / `main` `19f1157`):
| Form | Head | `main` |
|---|---|---|
| Page 1 `{"nextPageToken": "T2"}`, page 2 a message | `No PDFs found`, `0 PDFs found.`, exit 0, 1 request | `Messages in range: 0`, exit 0, 1 request |
| Page 1 `{"messages": [], "nextPageToken": "T2"}` | Same | Same |
| Page 1 token only, page 2 six 503s | Same; the failure is never seen | Same |
| Page 1 only an out-of-range id, with a token; page 2 a message | Same, 2 requests | `Messages in range: 0` |
| Page 1 an in-range id, with a token; page 2 a message | `Messages in range: 1`, the accepted under-count (D-68) | Same |
| **Hook,** `page_size` 1, one message past the range, one in range | `No PDFs found`, exit 0, `-m` and shim | `Messages in range: 0` |
| **Hook,** `page_size` 1, one past the range, three in range | Same | Same |
| Hook, same files, `page_size` 500 | `Messages in range: 1` | Same |
| `FakeGmail` walked, 0 to 8 messages, page sizes 1 to 10 | 147 pages, 0 empty pages with a token | n/a |

Limits: Windows, 3.12.10; scripted transport; no real Gmail, no real credentials. 3.10, 3.11, Ubuntu and macOS are CI's. The exe row ran the editable install, at the same `48fea17`.

**Conditions / remediation**
| # | Owner agent | Artefact | Required change | Due gate |
|---|-------------|----------|-----------------|----------|
| C50 | scrum-master | `sprint-01-plan.md` | (a) STORY-02.04 row: the DEF-008 AC and rows of D-102. (b) STORY-01.04 row: Ready needs STORY-02.04 in Jira with both ACs; it does not start while PGD-82 is open. (c) A tech-debt table row for PGD-82 and #46: closer qa-engineer after STORY-02.04 merges. (d) STORY-07.02 row: "Closes #40 at its G6" becomes "with the merge" (D-85, D-94) | Before the PGD-17 merge request; ⚠️ at G7, not a blocker |
| C51 | qa-engineer | PGD-82, #46; `test-plan.md` | PGD-82 and #46 take the wider reach of D-101, and "linked AC" reads FR-011, none failed. Plan v0.5: the five C47 rows; DEF-008 in section 14; the section 4 sentence (D-103); R-06 notes that `FakeGmail` cannot give an empty page with a token; NT-03 rows run as written | Sprint-02 G4, with C32 |
| C33 (added) | scrum-master | Jira STORY-02.04 | Created with the DEF-008 AC as well as the pacer AC, PGD-82 linked to it | Sprint-02 G4, as C33 |

Earlier conditions: C47, C48 (a, b, c), C49 closed. C11–C14, C20, C23, C25, C26, C29, C31, C32 (extended), C33 (Jira part, added to above), C36, C37 (b, c, d), C38 (b, c), C44, C46, C48 (d) stay open, due as recorded.

**Merge precondition.** Read by the orchestrator at the moment of the request, each from the live source:
1. The PR head is `aee5f56`, or any later head with `git diff 48fea17 <head> -- gmail_pdf tests` empty.
2. All 10 check runs `success` on that head (`aee5f56`: run 41225166460).
3. The `main` SHA that run tested equals current `main`, `19f1157` when read here (RISK-023). If `main` moved, update the branch so CI runs on a fresh merge ref.
4. No `REQUEST_CHANGES` review; `mergeStateStatus` CLEAN.
5. PGD-17 Done, set by qa-engineer on this GO, read back; label `gate:g7-pass`.
6. C50 (a..d) committed on the status branch and read back. The status branch is not merged before PR #44.

**Name in the merge request, each by itself:**
- **DEF-008, Sev-3, accepted, wider than filed (D-101).** In plain words: until paging lands, the tool reads the first result page only, and can say "No PDFs found" when later pages hold mail. No real run reaches it, because real mode still stops at sign-in. Fix in STORY-02.04; STORY-01.04 does not start while PGD-82 is open (D-102); RISK-027.
- **The first-page-only under-count stays** until STORY-02.04 (D-68).
- **#42** closes with this merge, by the orchestrator (T-14). **#40** stays open for STORY-07.02.
- **The removed child cases (#42):** the suite no longer runs those 28 cases as real children, what that loses is in D-104; his call only if he disagrees with #42's trade.
- **Merge method, his choice.** All five merges so far were merge commits, while CLAUDE.md section 1 says squash. **STD-85:** commit `ab78828`'s message says "41 + 25"; the real split is 23 + 43. If squashed, the message must not carry that figure; if merged, the PR body is the record (D-93).
- **PGD-18 needs a ruling from the product-owner and him (D-97):** (A) keep it as stretch, starting after this merge, sprint closes at 37 if it lands; (B) move it to sprint 02, sprint closes at 34. Master recommends (A). Until answered it does not start. The answer must say who gave it.
- **PGD-1 c.10292:** who posted it stays unanswered (D-98).
- **D-75, D-76 and the severity scale wording stay open to him.** They are not accepted.
- **Failed dry run:** "see the run log" with no log exists: ux-expert and product-owner, before STORY-07.02 is Ready (D-95).
- **For information:** one QA scratch probe ran without the socket guard and made three outbound attempts, carrying no credential or data (D-103).

**After the merge:** the orchestrator closes #42 (T-14). PGD-82 and #46 stay open. RISK-027 stays open.

**Risks registered:** RISK-027 new, score 4, closes with PGD-82. RISK-010 note, score unchanged. RISK-005, 011, 020, 021, 023, 024, 025 unchanged.

**Rationale:**
- All three mandatory items have evidence, and master reproduced AC-1 and AC-4 in real children. GO, not CONDITIONAL GO: the one ⚠️ row is non-mandatory and held when run, and C50 and C51 are follow-ups, as C39..C41 were at the PGD-15 G7.
- The hard question was DEF-008's rating. It stays Sev-3 by reach alone, and the record says so plainly: two of D-67's reasons against Sev-2 do not carry over, so the rating is armed against the one change that would make it false.
- The brief's premise, "only once the real gateway is wired", was true of the form filed and not of the class. Changing the input found that, as it did at D-67.

**Posted:** PR #44 comment 6546989378; Jira PGD-17 c.10354 (edited once, to link the comment; the content is unchanged); PGD-82 c.10355; PGD-1 c.10356 (risks). Notes on #46 (6546999023), #45 (6546999670), #42 (6547000047).
