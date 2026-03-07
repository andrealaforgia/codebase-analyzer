# Definition of Ready Validation

## US-01: Launch Codebase Analysis

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear, domain language | PASS | "Andrea runs 6 analysis agents one by one, manually launching each. Tedious and error-prone." Uses consulting domain language. |
| User/persona with specific characteristics | PASS | Andrea Laforgia, software consultant, evaluating client codebases, presenting to non-technical leadership. |
| 3+ domain examples with real data | PASS | 5 examples: Acme Corp (847 files, Java), Vertex API (defaults), partial agents (smell,test), wrong path, empty directory. |
| UAT scenarios in Given/When/Then (3-7) | PASS | 5 scenarios covering happy path, defaults, agent selection, invalid path, no source files. |
| AC derived from UAT | PASS | 8 acceptance criteria, each traceable to one or more UAT scenarios. |
| Right-sized (1-3 days, 3-7 scenarios) | PASS | Estimated 2-3 days, 5 scenarios. Single demonstrable feature: launch and confirm. |
| Technical notes identify constraints | PASS | CLI framework deferred, auto-detection by extension, configurable extension list, --yes flag for CI. |
| Dependencies resolved or tracked | PASS | No dependencies (first story). |

**DoR Status**: PASSED

---

## US-02: Orchestrate Multi-Agent Analysis

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear, domain language | PASS | "Runs each agent manually, one at a time, 15-25 minutes of active babysitting." Clear pain in domain language. |
| User/persona with specific characteristics | PASS | Andrea, software consultant, running multi-agent analysis on client codebases. |
| 3+ domain examples with real data | PASS | 3 examples: Acme Corp (all 6 succeed, 12 min), Meridian Health (DDD timeout, 1200 files), TechVentures (long-running, 3400 files). |
| UAT scenarios in Given/When/Then (3-7) | PASS | 4 scenarios: all succeed, single failure, dependency waiting, progress visibility. |
| AC derived from UAT | PASS | 8 acceptance criteria traceable to scenarios. |
| Right-sized (1-3 days, 3-7 scenarios) | PASS | Estimated 2-3 days, 4 scenarios. Demonstrable: agents run with progress. |
| Technical notes identify constraints | PASS | Dependency graph documented, timeout configurable, JSON output requirement, invocation mechanism deferred. |
| Dependencies resolved or tracked | PASS | Depends on US-01 (tracked). |

**DoR Status**: PASSED

---

## US-03: Executive Summary with Overall Health Score

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear, domain language | PASS | "Mentally synthesizes 6 reports. Leadership needs a 2-minute overview." Clear domain pain. |
| User/persona with specific characteristics | PASS | Andrea presenting to client executives (non-technical leadership). Dual audience documented. |
| 3+ domain examples with real data | PASS | 3 examples: Vertex API (78/100, balanced), Acme Corp (58/100, lopsided), NovaPay (32/100, critical). Real scores and dimension breakdowns. |
| UAT scenarios in Given/When/Then (3-7) | PASS | 5 scenarios: score calculation, radar chart, weakest dimension, screen fit, partial results. |
| AC derived from UAT | PASS | 6 acceptance criteria traceable to scenarios. |
| Right-sized (1-3 days, 3-7 scenarios) | PASS | Estimated 2-3 days, 5 scenarios. Demonstrable: executive summary page. |
| Technical notes identify constraints | PASS | Score thresholds, weight distribution, chart library deferred, responsive design needed. |
| Dependencies resolved or tracked | PASS | US-02 (tracked), normalization formulas (tracked via US-05). |

**DoR Status**: PASSED

---

## US-04: Translate Quality Metrics to Business Risk

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear, domain language | PASS | "CTOs and VPs do not think in Farley Index or cyclomatic complexity. They think in business risk." Clear communication gap described. |
| User/persona with specific characteristics | PASS | Andrea presenting to client leadership (CTOs, VPs, CEOs). Non-technical audience explicitly identified. |
| 3+ domain examples with real data | PASS | 3 examples: Acme Corp (HIGH velocity risk from refactoring debt), Meridian Health (HIGH incident risk from legacy+test), Vertex API (all LOW risk). |
| UAT scenarios in Given/When/Then (3-7) | PASS | 4 scenarios: risk section present, velocity risk derived, risk links to evidence, healthy codebase = low risk. |
| AC derived from UAT | PASS | 6 acceptance criteria traceable to scenarios. |
| Right-sized (1-3 days, 3-7 scenarios) | PASS | Estimated 1-2 days, 4 scenarios. Demonstrable: risk summary section. |
| Technical notes identify constraints | PASS | Risk model documentation requirement, business language constraint, limitation acknowledgment (code-only analysis), non-assessable risks noted. |
| Dependencies resolved or tracked | PASS | US-03 and US-05 (both tracked). |

**DoR Status**: PASSED

---

## US-05: Score Transparency and Derivation

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear, domain language | PASS | "If a CTO challenges a score, Andrea must explain exactly how it was calculated. One successfully challenged number destroys trust in the entire report." Critical anxiety documented. |
| User/persona with specific characteristics | PASS | Andrea defending scores during client pushback. Adversarial context (client denial) explicitly noted. |
| 3+ domain examples with real data | PASS | 3 examples: Refactoring Debt derivation (Acme Corp, formula with values), Farley Index derivation (Vertex API, 8 properties), Cognitive Load derivation (NovaPay, inversion formula). |
| UAT scenarios in Given/When/Then (3-7) | PASS | 5 scenarios: raw data shown, formula with values, plain-language explanation, drill-down to files, formula reproducibility. |
| AC derived from UAT | PASS | 6 acceptance criteria traceable to scenarios. |
| Right-sized (1-3 days, 3-7 scenarios) | PASS | Estimated 2-3 days, 5 scenarios. Demonstrable: derivation panels for each dimension. |
| Technical notes identify constraints | PASS | Starting formulas in research, formula display requirement, embedded data, rounding strategy. |
| Dependencies resolved or tracked | PASS | US-02 and US-03 (both tracked). |

**DoR Status**: PASSED

---

## Summary

| Story | DoR Status | Items Passed | Items Failed |
|-------|-----------|-------------|-------------|
| US-01: Launch Codebase Analysis | PASSED | 8/8 | 0 |
| US-02: Orchestrate Multi-Agent Analysis | PASSED | 8/8 | 0 |
| US-03: Executive Summary with Health Score | PASSED | 8/8 | 0 |
| US-04: Business Risk Translation | PASSED | 8/8 | 0 |
| US-05: Score Transparency and Derivation | PASSED | 8/8 | 0 |

All 5 Must Have stories pass the Definition of Ready. They are eligible for handoff to the DESIGN wave.

US-06 (Per-Dimension Detail Sections) and US-07 (Report Navigation and Presentation) are classified as Should Have. They also pass DoR but are documented for second-priority implementation.
