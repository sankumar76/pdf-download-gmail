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

