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
