# Stakeholder Map — Gmail PDF Attachment Downloader

> Owner: business-analyst · Version 0.2 (Q-01, Q-02, Q-12 answered; Q-04 and Q-10 to G8) · 2026-10-29 · Gate G1/G3
> Sources: `docs/project-state.md`, CLAUDE.md §1/§2, Jira PGD-1. No interviews were held; interests below are inferred from the documents and labelled as such. No personal data beyond the sponsor's name and role.

## Stakeholders
| Stakeholder | Type | Goals / interests | Pains / concerns | Influence | Interest | Success measure |
|-------------|------|-------------------|------------------|-----------|----------|-----------------|
| Santhosh / MD | Sponsor, delivery lead, end user, final approver (G8), Jira and GitHub admin, performs Google Cloud setup | Complete, correctly named PDFs; safe read-only access; repeatable runs; professional GUI | Credential leakage; overwritten or missing files; token expiry every 7 days (RISK-003) | High | High | AC-01..09 verified at G7; GOAL-01..09 met |
| P-01 GUI user (persona, today Santhosh) | Primary user | Run a download with no commands; see progress; cancel safely | Frozen window, unclear errors | n/a | High | GOAL-09, GOAL-07 |
| P-02 CLI user (persona, today Santhosh) | Secondary user | Scriptable runs with stable flags and exit codes | Behaviour differing from the GUI | n/a | Medium | LOG-05 honoured; GOAL-07 |
| Google (Gmail API, OAuth consent and app policy) | External platform | Policy-compliant clients; quota respected | Not a participant; its rules shape feasibility (scope policy, token expiry, quotas, 25 MB limit) | High on feasibility | Low | No policy violation; no 429 storms (NFR-01) |
| Senders and third parties named in emails | Passive data subjects | Their content stays private | Content copied to disk and logs (sender, subject) | Low | Low | No transmission beyond Google API (ASSUMPTION-12); Q-10 |
| AI delivery team (`product-manager`, `ux-expert`, `solution-architect`, `product-owner`, `scrum-master`, `developer`, 3 reviewers, `qa-engineer`) | Builders and verifiers | Clear, testable, traceable requirements | Ambiguity, silent scope change | Medium | High | Zero open Blocker/Critical at G6; all ACs verified at G7 |
| `master`, `orchestrator` | Governance and flow | Audit trail, gate decisions | Write-guard blocking governance records (B-01, reported resolved) | Medium | High | Gate log mirrored in repo |

## Influence / interest grid
| | High interest | Low interest |
|---|---|---|
| **High influence** | Santhosh (manage closely) | Google (monitor policy and limits) |
| **Low influence** | AI delivery team, P-01, P-02 (keep informed) | Third-party senders (respect, no active engagement) |

## RACI for key decisions
R = Responsible, A = Accountable, C = Consulted, I = Informed. `PM` product-manager, `SA` solution-architect, `UX` ux-expert, `Dev` developer, `QA` qa-engineer, `Master` master.

| Decision | Santhosh | PM | SA | UX | Dev | QA | Master |
|----------|----------|----|----|----|-----|----|--------|
| Scope and MoSCoW (incl. D-01 split of core/CLI vs GUI) | A | R | C | C | I | I | I |
| Resolve open questions Q-01..Q-13 | A | R (Q-05, 06, 09, 13) | R (Q-03, 07, 08, 11) | C | I | I | I |
| UI framework and dependency justification (ADR, G3) | A | C | R | C | C | I | C |
| Design tokens and GUI standards compliance (§9) | A | C | C | R | R | C | I |
| Publish OAuth consent screen to In production | A/R | I | C | I | I | I | I |
| Security controls SEC-01..09 verified | A | I | R | I | R | R | C |
| Gate decisions G1..G7 | I | C | C | C | C | C | A/R |
| Release readiness G8 sign-off | A/R | C | C | C | C | C | R |
| Override of any gate decision | A/R | I | I | I | I | I | R (logs it) |

## Engagement notes
- Santhosh answered Q-01 (as soon as possible), Q-02 (Windows 11) and Q-12 (about 30 s per PDF) on 2026-10-29 (PGD-1 comment 10108). Q-04 and Q-10: unsure; assumptions stand; re-check at G8 (D-28).
- Google's rules are monitored through the README and ADRs (no direct engagement).
