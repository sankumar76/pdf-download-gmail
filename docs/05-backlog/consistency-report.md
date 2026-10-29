# Cross-Artefact Consistency Report (G4 Backlog Ready)

| Field | Value |
|-------|-------|
| Owner | product-owner |
| Date | 2026-10-29 |
| Jira | [PGD-1](https://sankumar76.atlassian.net/browse/PGD-1); epics PGD-2..PGD-11 |
| Artefacts checked | [prd.md](../02-product/prd.md) v0.4 and [release-plan.md](../02-product/release-plan.md) v0.2 (5dc3289); [project-brief.md](../01-discovery/project-brief.md) and [requirements-catalog.md](../01-discovery/requirements-catalog.md) v0.3 (5dc3289, 6ea45af); [ux-spec.md](../03-ux/ux-spec.md) v0.3 (4f1536f); [architecture.md](../04-architecture/architecture.md) v0.2, [test-strategy.md](../04-architecture/test-strategy.md) v0.2, ADR-001..007 (4892c8c); standards; [gate-log.md](../00-governance/gate-log.md) G3, [decision-log.md](../00-governance/decision-log.md) D-14..D-34; epics EPIC-01..10 in `docs/05-backlog/epics/` |
| Method | FR and NFR ID sets were extracted from the PRD tables and compared with the UX spec §9, architecture §12 and §7, and the epic FR ranges by a script (run 2026-10-29). Everything else was read and compared by hand; line-level evidence is cited per row |

## 1. Result

**Critical: 0 · Major: 2 · Minor: 7.** No issue blocks G4. Both Major issues have a product-owner resolution already applied in the backlog and an owner for the residual action (section 4). Nothing here changes PRD scope, architecture or UX; every fix for those artefacts is routed to its owner.

| Check | Result |
|-------|--------|
| 1. Every Must FR covered by an epic | PASS: 53 of 53 Must FRs are in an epic; 0 uncovered |
| 2. Every user-facing FR has a UX screen or "no UI" mapping | PASS: ux-spec §9 maps FR-001..066, 0 missing, 0 extra; see CC-07, CC-08 for wording follow-ups |
| 3. Every FR and NFR in the architecture coverage matrix | PASS: FR 66 of 66 (§12), NFR 25 of 25 (§7), 0 missing, 0 extra |
| 4. Terminology consistent | PASS with notes (section 3); 0 conflicts, 1 intended difference |
| 5. UX and architecture agree | PASS: architecture §17.4 lists every item Aligned; R-COUNT is one rule in both; 1 numeric gap between ADR-007 and NFR-002 (CC-02) is PRD to architecture, not UX |
| 6. Sequencing: enablers before dependents | PASS after PO ordering; 1 missing enabler owner (CC-01) and 3 hidden dependencies (CC-06) resolved in the backlog order |
| 7. NFRs allocated to stories or enablers | PASS: all 25 NFRs have an owning epic or enabler (section 6); NFR-019 is R3 and NFR-025 is a Won't |

## 2. Detailed checks

### 2.1 FR coverage by epic (check 1)
Release plan R1 lists FR-001..006, 008..033, 036, 037, 039..046, 065, 066 (44 FRs: 37 Must, 7 Should) and R2 lists FR-047..060, 062, 064 (16 Must). The epic assignment below reproduces those sets exactly. Points are the PRD §7 figures and add up to R1 = 99, R2 = 42, MVP = 141.

| Epic | FRs in epic | Must / Should / Could | Out of epic scope (reason) | Release | Pts |
|------|-------------|------------------------|----------------------------|---------|-----|
| EPIC-01 | 001..006 (+007) | 6 / 1 / 0 | FR-007 (R3) | R1 | 17 |
| EPIC-02 | 008..017 | 7 / 3 / 0 | none | R1 | 19 |
| EPIC-03 | 018..021 | 4 / 0 / 0 | none | R1 | 12 |
| EPIC-04 | 022..027 | 6 / 0 / 0 | none | R1 | 12 |
| EPIC-05 | 028..035 | 4 / 3 / 1 | FR-034 (R3), FR-035 (backlog) | R1 | 14 |
| EPIC-06 | 036..038 | 2 / 0 / 1 | FR-038 (backlog) | R1 | 5 |
| EPIC-07 | 039..046 | 7 / 1 / 0 | none | R1 | 16 |
| EPIC-08 | 065, 066 | 1 / 1 / 0 | GUI parts of FR-065 (R2) | R1 | 4 |
| EPIC-09 | 047..053, 064 (+061) | 8 / 1 / 0 | FR-061 (R3) | R2 | 25 |
| EPIC-10 | 054..060, 062 (+063) | 8 / 1 / 0 | FR-063 (R3) | R2 | 17 |

Total: 66 FRs = 53 Must, 11 Should, 2 Could; every FR appears in exactly one epic (FR-061 placement: see CC-04).

### 2.2 UX coverage (check 2)
ux-spec §9 lists all 66 FRs; those with no direct screen are named "No UI" or "no UI of their own" (FR-009, 011, 012, 014, 018..021, 028, 031, 034, 035, 038), so none is orphaned. Every R2 user-facing FR (047..060, 062, 064) has SCR/DLG or §7/§8 references with the full state set (gate-log G3 check 4). The R1 CLI behaviour is specified in ux-spec §12.

### 2.3 Architecture coverage (check 3)
architecture §12 maps FR-001..066 to components and §7 has one row per NFR-001..025 with tactic, component and verification (script: 0 missing, 0 extra). The architecture header and §17 cite PRD v0.4 and ux-spec v0.3 (C10 closed).

### 2.4 Status of G3 conditions (spot check, master confirms at G4)
| Condition | Evidence found | PO view |
|-----------|----------------|---------|
| C7 (business-analyst) | Catalogue v0.3 header: Q-01, 02, 03, 07, 08, 11, 12 resolved; Q-04 and Q-10 needed by G8; DR-005 Confidential; brief carries GOAL-11 | Closed |
| C8 (product-manager) | PRD v0.4: PD-17 (NFR-009), PD-18 (FR-032 and GOAL-10), PD-19 (AQ-04, AA-07, AA-08, AA-11), PQ-01..03 closed in §12 | Closed |
| C9 (ux-expert) | ux-spec v0.3: UX-I-01..06 accepted, R-COUNT, local client-file check | Closed; CC-07 is a Minor follow-up |
| C10 (solution-architect) | architecture v0.2 and test-strategy v0.2 cite ux v0.3 and PRD v0.4; write-path rule §10.2; no pragma exception | Closed |
| C11 (solution-architect) | ADR-001 Proposed; S-02 open (GitHub #3) | Open by design: EPIC-09 and EPIC-10 carry the gate in their files and Jira epics |

## 3. Terminology (check 4)

| Term | Where used | Finding |
|------|-----------|---------|
| manifest (`.manifest.json`) vs "download history" | PRD, architecture, ADRs, code use *manifest*; ux-spec uses *download history* in user-facing text | Intended and stated in ux-spec "Conventions" (first use in a dialog names both). Stories must use *manifest* in code and developer-facing ACs and the UX wording in user-visible text; the shared text table `domain/messages.py` is the single source. No conflict |
| run, dry run, output folder, time zone, run log, CSV report | PRD, UX, architecture | Consistent |
| statuses `SAVED`, `SAVED_RENAMED`, `SKIPPED_ALREADY_DOWNLOADED`, `SKIPPED_IDENTICAL`, `NOT_A_PDF`, `ERROR` | PRD FR-041, architecture `Status`, UX | Consistent. Dry-run display labels `would-save`, `would-save-renamed`, `already-downloaded` are separate (CC-08) |
| ID spaces | RD uses FR-01..18, NFR-01..05, AC-01..09, LOG-01..05; PRD uses FR-001..066, NFR-001..025 | PRD §15 maps them. Stories reference PRD IDs only. "AC-01..09" in the RD are the sponsor's acceptance tests; story acceptance criteria are `AC-1..` inside a story (DoR), so story ACs must cite the sponsor test as "RD AC-05" to avoid confusion |
| Entry points | ADR-005 `gmail-pdf`, `gmail-pdf-gui`, `python -m gmail_pdf`, RD shim `gmail_pdf_downloader.py` | Consistent with PRD FR-045 and test-strategy §9 |

## 4. Issues

Severity: **Critical** blocks G4; **Major** needs an owner action before the affected story is Ready or before the affected wave exits; **Minor** is wording or tidy-up.

| ID | Severity | Issue | Evidence | Owner | Status / resolution |
|----|----------|-------|----------|-------|---------------------|
| CC-01 | Major | **No epic owns the engineering foundation.** The test strategy says the CI workflow and the fake mailbox are created "in the first W1 story" (test-strategy §9, §11), the architecture needs the package skeleton, `pyproject.toml`, pins and `pip-audit` (gate-log G3 follow-up), and NFR-020/022/023 are cross-cutting. None of this is an FR, so no PRD epic carries it, and the PRD point sizes (EPIC-02 = 19) do not list it. Without an owner, W1 has no first story and sprint 1 has no capacity line for it | PRD §7 epic table; test-strategy §9, §11; architecture §10.1, §11; gate-log G3 follow-ups | product-owner (resolved), scrum-master (size), product-manager (informed) | **Resolved in backlog by PO decision:** two explicit enabler stories are hosted in EPIC-02, STORY-02.01 (walking skeleton, CI, fake mailbox) and STORY-02.08 (benchmark and memory harness), each with a justification, first in the order. No new epic and no scope change. Open action: scrum-master sizes them; if EPIC-02 no longer fits sprint 1, tell the product-owner. RISK-010 watch applies |
| CC-02 | Major | **The recall-sweep cost gate does not protect NFR-002.** ADR-007 sets the gate from NFR-001 only (`sweep_extra / baseline` up to 0.8). A dry run costs one `messages.get` per message (baseline 1,000 x 0.3 s = 300 s), and NFR-002 allows 480 s, so the sweep may add at most (480 - 300) / 0.3 = 600 calls per 1,000 baseline messages, a ratio of 0.6. At 0.8 a dry run would take about 540 s and fail NFR-002 even though the gate says "pass". ADR-007 also says dry runs pay the sweep cost | PRD NFR-002; architecture §7 NFR-002 row (dry run about 5 min); ADR-007 "Cost gate" and "Consequences" | solution-architect (restate the gate as the stricter of NFR-001 and NFR-002, or state why dry runs are exempt); qa-engineer (benchmark case) | Open, not Critical: S-01 measures the ratio in W1 (synthetic) and W3 (real) and the fallback (sweep off, or FR-038) exists. STORY-02.08 and STORY-02.09 carry the corrected bound as an acceptance criterion until the ADR is updated. Needed by: before STORY-02.09 is Ready (W2) |
| CC-03 | Minor | **Stale spike references in the release plan.** W2 notes "FR-017 enters here if the Q-07 spike (G3) shows it fits"; R1 entry criteria say "Q-07 spike scheduled"; W4 notes "the framework spike against FR-054..060 happens at G3". Q-07 was resolved by ADR-007 (sweep on by default, S-01 measured in W1 and W3) and the GUI spike S-02 has not run (C11). The PRD FR-017 text also says the method "is a G3 decision (spike on Q-07)" | release-plan §2 W2 row, §2 entry criteria, §3 W4 row, §5 first row; PRD FR-017 | product-manager | Open. Not blocking: PRD §9 and the epic files carry the binding C11 rule and the S-01 gate |
| CC-04 | Minor | **FR-061 (Advanced area, R3) has two owner epics.** PRD §7 lists it under EPIC-10 (and EPIC-10 "[+5]" matches it), but PRD §4.9 heading, the §11 "FR-by-FR owner epic" line and the architecture put it with the GUI workflow. R3, no sprint effect | PRD §4.9, §7, §11 | product-manager | Open. PO placed FR-061 in EPIC-09 (two of three statements, and its parent is the settings form); PM to confirm or move |
| CC-05 | Minor | **R2 surfaces of R1 FRs and the README GUI part are not itemised in PRD §7.** The release plan W5 includes the GUI surfaces of FR-005, 006, 015, 037 and 042 and R2 includes the GUI fields for FR-010 and FR-013, and FR-065 has "GUI parts R2", but PRD §7 lists EPIC-09 as FR-047..053, 064 and EPIC-08 as FR-065, 066 without them, so their effort may be outside the 25-point EPIC-09 and 4-point EPIC-08 sizes | PRD §4.1 Rel column, §7; release-plan §1, §3 W5 | product-manager | Open. PO included them in EPIC-09 scope and added the held STORY-08.03 (README GUI section, held by C11). Size growth is watched under RISK-001 |
| CC-06 | Minor | **Hidden sequencing dependencies not stated in PRD §7.** (a) FR-032's test needs the run log and header-only CSV (FR-039, 040, EPIC-07) but EPIC-05 is listed before EPIC-07; (b) FR-037's summary needs FR-042 and the exit code needs FR-043; (c) the dry-run `already-downloaded` label (FR-044, W1) and the check "planned names equal real-run names" need the manifest (FR-029) and the save path (FR-028), which are W2 | architecture §7 NFR-005 row (log and CSV open before the manifest is loaded); PRD FR-032, FR-037, FR-044 | scrum-master (apply), product-owner (order) | Resolved in the backlog order: W2 order is 07.02, 07.03, 07.04, 05.01..05.03, 06.01, 05.04, 05.05, 06.02, 07.05, 07.06. The W1 dry-run story covers the manifest-absent case; the parity check closes in W2. Each dependency is written into the candidate stories' "Depends on" |
| CC-07 | Minor | **UX spec not re-checked against PRD v0.4.** ux-spec cites PRD v0.3 (header, Inputs). PRD v0.4 changed FR-032/039/040/043/044 (PD-18, PD-19). The "download history unreadable" text says "Nothing was downloaded and the file was not changed" which stays true, but the spec does not say that a run log and a header-only CSV now exist for that outcome and for failed sign-in, or whether DLG-03 and the CLI line should point to the run log. The CSV BOM (PD-19) has no UX impact | ux-spec header, §6.B text table line "Download history unreadable", §12 line for history unreadable; PRD PD-18 | ux-expert | Open, Minor. Needed by: before the R2 stories for DLG-03 and SCR-06 are Ready. R1 CLI wording is unaffected |
| CC-08 | Minor | **Dry-run display labels are not in the PRD.** UX §12 and architecture §6.8 use `would-save`, `would-save-renamed`, `already-downloaded` in the dry-run list; the PRD defines only the six CSV statuses and says "no other value appears" (FR-041, CSV rows). A dry run writes no CSV, so there is no contradiction, but acceptance criteria need explicit wording | ux-spec §12 (dry-run example); architecture `PlannedName`; ADR-006; PRD FR-041, FR-044 | product-manager (optional clarification in FR-044) | Resolved for stories: ACs state that the labels are display-only and are not LOG-03 statuses. PM may add one sentence to FR-044 |
| CC-09 | Minor | **Wave placements adjusted from the release plan (no scope change).** (a) FR-010 and FR-013 are scheduled in W1, because the FR-045 flag table must be complete in the first CLI. (b) The CLI half of FR-006 (missing file, wrong client file, exit 3) and the local client-file check need no live access, so they move from W3 to W2, next to FR-001..003; only live consent stays in W3. (c) FR-004 `.gitignore` and the secret scan move to W1 so that no fixture or credential file can ever be committed. (d) EPIC-04's write-time containment check rides with EPIC-05 in W2 | release-plan §2 wave table; PRD FR-045; architecture §4.1 | product-owner (decision); product-manager (informed) | Recorded as PO ordering decisions (D-PO-1..4 in backlog.md). W1 and W2 exit checks are unchanged |

### Other observations (no action)
- `AUTOMATION_LEVEL=full`: sprint-1 start needs no human approval; the first human approval point remains G8.
- TR-006 (sponsor's `credentials.json` and ≥ 10 named PDFs, PA-04) is a W3 external dependency. It is not an issue today but the schedule for W3 cannot start without it; the backlog lists it as a dependency.
- Q-04 and Q-10 remain assumptions to G8 (D-34); no story depends on their answers.

## 5. Issues for other roles
| To | Item |
|----|------|
| solution-architect | CC-02 (restate the sweep cost gate against NFR-002; update ADR-007). C11 stays open until S-02 passes and ADR-001 is Accepted |
| product-manager | CC-03 (stale spike wording), CC-04 (FR-061 owner epic), CC-05 (R2 surfaces and README GUI part in the epic lists and sizes), CC-08 (optional dry-run label sentence), CC-01 (PRD points exclude the enablers; informed) |
| ux-expert | CC-07 (re-check against PRD v0.4; run log and header-only CSV after an unreadable history or failed sign-in) |
| scrum-master | CC-01 (size 02.01 and 02.08), CC-06 (apply the W2 order and dependencies), capacity: no velocity exists (D-33), plan sprint 1 below the full W1 set |
| qa-engineer | CC-02 benchmark case at sweep ratio 0.6; confirm D-21 exit-code mapping in the test plan (G3 follow-up) |

## 6. NFR allocation (check 7)

"AC in every story" means the criterion is stated in each story that touches the behaviour; the owning story carries the measurement.

| NFR | Owner (epic / story) | Cross-cutting handling |
|-----|----------------------|------------------------|
| 001, 002, 003 | EPIC-02 / STORY-02.08 (benchmark harness) | Real timing recorded in W3 (EPIC-01 STORY-01.07); the sweep bound in CC-02 |
| 004 | EPIC-09 / STORY-09.04 (GUI), EPIC-10 (launch), EPIC-06 / STORY-06.02 (CLI Cancel 5 s) | R2 held by C11 |
| 005 | EPIC-07 / STORY-07.06 | Log and CSV opened before auth and manifest load |
| 006 | EPIC-02 / STORY-02.02 (retry helper with the gateway) | AC in every story that calls Google |
| 007 | EPIC-05 / STORY-05.03, EPIC-06 / STORY-06.02 | 100-iteration fault-injection loop |
| 008 | EPIC-06 / STORY-06.01 | Fault points also in 03.03 (decode) and 05.01 (write) |
| 009, 010 | EPIC-02 / STORY-02.08 | Manifest bound in 05.02; large attachment in 03.03 |
| 011 | EPIC-01 / STORY-01.04 | Recording mock reused by every Google-touching test |
| 012 | EPIC-01 / STORY-01.01 | Sentinel check is an AC in every story that adds a text surface; gitleaks in 02.01 |
| 013 | EPIC-01 / STORY-01.02 | |
| 014 | EPIC-01 / STORY-01.04 (network allow-list test) | Dependency review in 02.01 |
| 015 | EPIC-01 / STORY-01.01 and enabler 02.01 | Review check at G6; fixtures are generated fakes |
| 016 | EPIC-07 / STORY-07.02, 07.03 | Body-text sentinel in 03.02 |
| 017, 018 | EPIC-10 / STORY-10.04, 10.01 | R2 held by C11 |
| 019 | none (R3, Should) | Not scheduled; FR-063 |
| 020 | Enabler STORY-02.01 (CI matrix) | AA-06 long paths in 04.05; GUI acceptance in EPIC-10 |
| 021 | EPIC-10 / STORY-10.02, 10.03, 10.05 | R2 held by C11 |
| 022 | Enabler STORY-02.01 (gates) | Definition of Done on every story |
| 023 | Enabler STORY-02.01 (allow-list check) | AC in any story that adds a dependency |
| 024 | EPIC-02 / STORY-02.03, EPIC-04 / STORY-04.02 | |
| 025 | n/a (Won't) | |

---

# Sprint-01 DoR validation (G4)

| Field | Value |
|-------|-------|
| Date | 2026-10-29 |
| Validated by | product-owner |
| Inputs | [sprint-01-plan.md](sprint-01-plan.md) (d1f1358) including open items A-1..A-6; [definition-of-ready.md](../standards/definition-of-ready.md); stories PGD-12..PGD-18 and sub-tasks PGD-19..PGD-62 read in Jira; UX section 12, architecture 4.1, 6.2-6.5, 8.4, ADR-002, ADR-003, test-strategy section 2 |
| Where the verdicts live | One comment per story on Jira (PGD-12..PGD-18) with the DoR checklist; the PO Validation section was appended to the description of every story whose ACs I changed (PGD-13, 15, 16, 18). Descriptions of PGD-12, 14, 17 are unchanged |

## Verdicts

| Jira | Story | Points | Verdict | Gaps found and fixed |
|------|-------|--------|---------|----------------------|
| PGD-12 | STORY-02.01 enabler | 8 | READY | none; enabler form accepted |
| PGD-13 | STORY-01.01 redaction | 5 | READY after PO amendments | AC-5 printed the unexpected-failure line for Ctrl+C (fixed: new AC-8 `Run cancelled`, exit 1); AC-7 said `redaction.py` imports only stdlib but `safe_message` takes its sentences from `domain.messages` (fixed: AC-7 names that module; Assumption A-2) |
| PGD-14 | STORY-01.02 secret files | 3 | READY | none in the ACs; test guidance and one architecture note added |
| PGD-15 | STORY-02.02 date range | 8 | READY after PO amendments | FR-008 default system zone had no AC (added AC-10); NFR-024 trace claimed but not tested here (clarified); AC-4 trailing-space precision; `cli/console.py` added to the file list |
| PGD-16 | STORY-02.03 input validation | 3 | READY after PO amendments | Unknown-zone wording (A-3) and multi-error rule (A-2) decided; AC-3 skip rule; AC-4 exact text and the unresolvable-system-zone case |
| PGD-17 | STORY-02.06 empty range | 2 | READY | none; A-1 decided |
| PGD-18 | STORY-03.01 PDF part (stretch) | 3 | READY (stretch) | FR-019 silent on `"a.pdf "` and `"a.pdf."` (added AC-8) |

All seven stories pass every DoR item: story form with trace and value; 3-10 ACs with IDs in Given/When/Then (counts 9, 8, 5, 10, 8, 5, 8); negative and NFR paths; Dev Context with architecture sections, ADRs and file lists; dependencies known and inside the sprint (blocked-by links PGD-12 to 13, 14, 15; PGD-13 to 15 and 16; PGD-15 to 16, 17, 18 verified in Jira); UX references (CLI, UX section 12; no GUI states apply); estimate and sub-tasks. No story depends on an EPIC-09/10 item, so C11 is not touched. Sprint arithmetic: committed 29 points against the assumed 30; the goal-critical set is 24 points (the sprint plan is unchanged by this validation).

## Decisions on the open items (A-1..A-6)

| ID | Decision | Basis |
|----|----------|-------|
| A-1 | **Accepted.** `error: unexpected failure, see the run log` is used before a run log exists (PGD-13, PGD-17). Interim build only; R1 has the log. Reused for a failed list call (PGD-17 AC-4); no new wording is invented | UX section 12 first-line table; D-21; the text is safe (no secret, no trace) |
| A-2 | **Accepted.** Several input errors print one per line, each error one line; order start, end, range, tz | UX "one line each"; FR-015 |
| A-3 | **Decided as an Assumption.** `error: --tz: Unknown time zone. Use an IANA name such as Asia/Kolkata.` Logged for ux-expert to add to UX section 12 | No UX text existed; follows the `--start:` pattern; no correctness or security effect |
| A-4 | **Accepted.** `client_secret*.json` added to `.gitignore` | Google's download name; more protection, no cost |
| A-5 | **Accepted with a condition.** The interim `Messages in range: N` line and interim exit-3 message are placeholders; STORY-07.04 and STORY-01.04/01.06 must carry an AC that removes or replaces them, so an interim string cannot ship in v0.9.0 | Avoids a stale placeholder in release |
| A-6 | **Accepted.** Retry helper built in STORY-02.02; paging stays in STORY-02.04 | NFR allocation, section 6 of this report |

## Issues for other roles (new, none blocking)

| ID | Severity | To | Item |
|----|----------|----|------|
| CC-10 | Minor | ux-expert, solution-architect | The unexpected-failure first line differs: UX section 12 `error: unexpected failure, see the run log`; architecture 6.5 `error: unexpected failure, see the run log: <path>`. Stories use the UX string until a log path exists. Agree one wording |
| CC-11 | Minor | ux-expert | Add the unknown-time-zone line (A-3) to UX section 12 "Errors" |
| CC-12 | Minor | solution-architect | (a) `write_private_text` (the token write, `os.replace`) sits in `infra/paths.py` (PGD-14) while architecture 4.1 places token writing in `infra/auth.py`; confirm the location and the section 10.2 `os.replace` allow-list. (b) `redaction.py` imports the dependency-free `domain.messages` for `safe_message`'s fixed sentences (PGD-13 AC-7); confirm this fits the layering rules in 4.1 |
| CC-13 | Minor | scrum-master | (a) Sub-task summaries should cite the new AC ids: PGD-32 and PGD-33 add AC-8; PGD-41 adds AC-10; PGD-60 adds AC-8 of PGD-18. (b) When STORY-01.04/01.06 and 07.04 are drafted, add the A-5 removal AC. (c) When STORY-07.02/07.03 are drafted, extend PGD-17 AC-3 for the zero-match log and header-only CSV (GOAL-10) |

CC-10..CC-13 take the issue count in this report to 0 Critical, 2 Major, 11 Minor (CC-01..CC-13; CC-09 is informational).
