# User Stories: Codebase Analyzer

## Story Map

```
Workflow:  [Configure] --> [Execute] --> [Generate Report] --> [Review] --> [Present]
              |               |               |                  |             |
Row 1:     Launch with     Orchestrate     Executive          Score        Navigate
(MVP)      target dir      6 agents        summary +          derivation   sections
           + defaults       sequentially    radar chart        panels
              |               |               |                  |
Row 2:     Custom project  Parallel         Business risk      Per-agent    Print
           name, agent     execution +      summary            detail       mode
           selection        progress                            sections
              |               |               |
Row 3:     Config file     Agent failure    Heatmaps,
(Future)   for defaults    recovery +       treemaps,
           per client      partial results   trends
```

Row 1 = Walking skeleton (MVP). Row 2 = Full product. Row 3 = Future enhancements.

---

## US-01: Launch Codebase Analysis

### Problem

Andrea is a software consultant who evaluates client codebases. She currently runs 6 analysis agents one by one against each client's codebase, manually launching each from the command line. This is tedious and error-prone -- she sometimes forgets an agent or points one at the wrong directory. She needs a single entry point that validates the target codebase and launches all agents.

### Who

- Software consultant | Evaluating a client's codebase | Wants a single command to launch comprehensive analysis

### Solution

A CLI command that accepts a target directory, validates it contains source code, detects project metadata (file count, primary language), and confirms settings before launching analysis.

### Job Story Trace

- JS-01: Comprehensive Codebase Assessment (primary)
- JS-03: Repeatable Consulting Asset (secondary)

### Domain Examples

#### 1: Happy Path -- Andrea analyzes the Acme Corp Java platform

Andrea has cloned the Acme Corp repository to `/projects/acme-platform`. She runs `codebase-analyzer analyze /projects/acme-platform --project-name "Acme Corp Platform" --output ./reports/acme-2026-03.html`. The tool detects 847 Java/Python source files, displays the configuration, and prompts her to confirm. She confirms and analysis begins.

#### 2: Minimal Configuration -- Andrea uses defaults for a quick check

Andrea runs `codebase-analyzer analyze /projects/vertex-api`. The tool defaults the project name to "vertex-api", the output to `./vertex-api-report.html`, and selects all 6 agents. She confirms and analysis begins.

#### 3: Partial Analysis -- Andrea only needs two dimensions

Andrea wants a quick code quality check without the full suite. She runs `codebase-analyzer analyze /projects/acme-platform --agents smell,test`. Only Code Smell Detection and Test Design Review agents are queued. The report will contain 2 dimensions with a 2-axis radar chart.

#### 4: Wrong Directory -- Andrea points at a non-existent path

Andrea accidentally types `/projects/acme-platfrm` (typo). The tool reports the directory does not exist and suggests similar paths if possible.

#### 5: Empty Directory -- No source files found

Andrea points the tool at a documentation-only directory. The tool warns that no source files were detected and suggests checking the path.

### UAT Scenarios (BDD)

#### Scenario: Launch with target directory and custom options
```gherkin
Given Andrea has the Acme Corp codebase at "/projects/acme-platform"
When she runs "codebase-analyzer analyze /projects/acme-platform --project-name 'Acme Corp Platform' --output ./reports/acme-2026-03.html"
Then the tool displays:
  | field     | value                          |
  | Project   | Acme Corp Platform             |
  | Target    | /projects/acme-platform        |
  | Files     | 847 source files detected      |
  | Language  | Java (primary)                 |
  | Agents    | All 6 selected                 |
  | Output    | ./reports/acme-2026-03.html    |
And prompts "Confirm analysis? [Y/n]"
```

#### Scenario: Launch with minimal arguments using defaults
```gherkin
Given Andrea has a codebase at "/projects/vertex-api"
When she runs "codebase-analyzer analyze /projects/vertex-api"
Then the project name defaults to "vertex-api"
And the output defaults to "./vertex-api-report.html"
And all 6 agents are selected by default
And the confirmation prompt displays the detected settings
```

#### Scenario: Launch with selected agents only
```gherkin
Given Andrea wants a quick check of code smells and test design
When she runs "codebase-analyzer analyze /projects/acme-platform --agents smell,test"
Then only 2 agents are queued: Code Smell Detection and Test Design Review
And the confirmation prompt shows "Agents: 2 of 6 selected"
```

#### Scenario: Target directory does not exist
```gherkin
Given the directory "/projects/acme-platfrm" does not exist
When Andrea runs "codebase-analyzer analyze /projects/acme-platfrm"
Then the tool displays "Error: Directory not found"
And exits with a non-zero status code
```

#### Scenario: Target directory has no source files
```gherkin
Given "/projects/docs-only" exists but contains only markdown files
When Andrea runs "codebase-analyzer analyze /projects/docs-only"
Then the tool displays "Warning: No source files detected"
And does not proceed to analysis
```

### Acceptance Criteria

- [ ] CLI accepts a target directory as the first positional argument
- [ ] CLI auto-detects file count and primary language from target directory
- [ ] CLI displays all configuration settings and prompts for confirmation before proceeding
- [ ] Project name defaults to directory basename when --project-name is not provided
- [ ] Output path defaults to `./{project-name}-report.html` when --output is not provided
- [ ] Agent selection defaults to all 6 when --agents is not provided
- [ ] Non-existent target directory produces clear error and non-zero exit code
- [ ] Target directory with no source files produces a warning and does not proceed

### Technical Notes

- CLI framework choice deferred to DESIGN wave
- Auto-detection of primary language based on file extension frequency
- Source file detection should use configurable extension list (not hardcoded)
- Confirmation prompt should be skippable with --yes flag for CI/CD usage

### Dependencies

- None (first story in the chain)

### MoSCoW: Must Have

---

## US-02: Orchestrate Multi-Agent Analysis

### Problem

Andrea currently runs each of the 6 analysis agents manually, one at a time, waiting for each to finish before starting the next. For a medium-sized codebase, this takes 15-25 minutes of active babysitting. She wants to launch once and have all agents run automatically, with visibility into what is happening.

### Who

- Software consultant | Running multi-agent analysis | Wants automated orchestration with progress visibility

### Solution

An orchestrator that launches the 6 analysis agents, manages dependencies between them (refactoring agent depends on code smell agent), runs independent agents in parallel where possible, and displays real-time progress with per-agent status and scores.

### Job Story Trace

- JS-01: Comprehensive Codebase Assessment (primary)
- JS-03: Repeatable Consulting Asset (secondary)

### Domain Examples

#### 1: Happy Path -- All 6 agents complete successfully on Acme Corp

Andrea confirms the analysis. The orchestrator launches 5 independent agents in parallel. As each completes, its primary score is displayed (e.g., "Grade: B, 23 issues"). The refactoring agent starts automatically after code smell detection finishes. All 6 complete in 12 minutes. Report generation begins.

#### 2: Agent Failure -- DDD agent times out on Meridian Health codebase

Andrea is analyzing the Meridian Health platform (1,200 files). The DDD Architecture agent hangs and exceeds the 10-minute timeout. The tool displays the failure, prompts Andrea to continue or abort. She continues. The remaining agents complete normally. The final report marks DDD as "Not Available."

#### 3: Large Codebase -- Progress feedback matters on TechVentures monolith

Andrea is analyzing TechVentures' monolith (3,400 files). The cognitive load agent takes 8 minutes. During execution, she sees "Analyzing structural complexity..." then "Analyzing naming quality..." -- the sub-task labels let her know it has not stalled.

### UAT Scenarios (BDD)

#### Scenario: All agents complete successfully with progress display
```gherkin
Given Andrea has confirmed analysis of the Acme Corp Platform codebase
When the orchestrator runs all 6 agents
Then each agent displays a progress indicator during execution
And each completed agent shows its primary score
And elapsed time and estimated remaining time are visible throughout
And report generation starts automatically when all agents finish
```

#### Scenario: Single agent fails without killing the run
```gherkin
Given analysis is running on the Meridian Health codebase
And 3 agents have completed successfully
When the DDD Architecture agent exceeds the 10-minute timeout
Then the tool displays "DDD Architecture Review: FAILED (timeout)"
And prompts "Continue with remaining agents? [Y/n]"
And if Andrea confirms, the remaining agents continue to completion
And the final report marks DDD as "Not Available" with the failure reason
```

#### Scenario: Dependent agent waits for prerequisite
```gherkin
Given the Code Smell Detection agent is still running
When the orchestrator reaches the Refactoring Analysis queue position
Then Refactoring Analysis shows "queued (waiting for Code Smell Detection)"
And it starts automatically once Code Smell Detection completes
And other independent agents continue running in parallel
```

#### Scenario: Progress shows sub-task activity for long-running agents
```gherkin
Given the Cognitive Load agent is analyzing TechVentures' 3,400-file monolith
When Andrea checks the terminal during execution
Then she sees the current sub-task (e.g., "Analyzing structural complexity...")
And the progress bar reflects estimated completion within the agent
And elapsed time for this agent is displayed
```

### Acceptance Criteria

- [ ] Orchestrator launches all selected agents after user confirmation
- [ ] Independent agents run in parallel; dependent agents wait for prerequisites
- [ ] Each agent displays a progress indicator during execution
- [ ] Each completed agent displays its primary metric/score
- [ ] Elapsed time and estimated remaining time are visible throughout
- [ ] A single agent failure prompts user to continue or abort
- [ ] Continuing after failure marks the dimension as "Not Available" in the report
- [ ] Report generation starts automatically when all agents finish (or user chooses to continue with partial results)

### Technical Notes

- Agent dependency graph: refactoring-expert depends on code-smell-detector; all others are independent
- Timeout should be configurable per agent (default: 10 minutes)
- Each agent must produce structured JSON output alongside its markdown report
- Agent invocation mechanism deferred to DESIGN wave (Task tool, subprocess, etc.)

### Dependencies

- US-01 (launch and configuration provides target_dir, agent_selection, project_name)

### MoSCoW: Must Have

---

## US-03: Generate Executive Summary with Overall Health Score

### Problem

Andrea currently reads through 6 separate markdown reports and mentally synthesizes an overall picture. Client leadership needs a 2-minute overview, not 6 reports. Andrea needs an executive summary that communicates codebase health at a glance with a single score, a visual quality shape (radar chart), and per-dimension ratings -- all in language that non-technical leaders can understand.

### Who

- Software consultant | Preparing findings for client executives | Wants a scannable summary that communicates health instantly

### Solution

An executive summary section in the HTML report featuring: an overall health score (0-100 with letter grade), a 6-axis radar chart showing the quality shape, per-dimension score bars with plain-language ratings, and identification of the weakest dimension.

### Job Story Trace

- JS-02: Executive Communication of Technical Risk (primary)
- JS-04: Overcoming Client Denial (secondary)

### Domain Examples

#### 1: Balanced Codebase -- Vertex API scores well across dimensions

Vertex API gets an overall score of 78/100 (Good). The radar chart shows a relatively even hexagon with all dimensions between 6.5 and 8.5. No single dimension dominates as a weakness. The summary highlights test design (8.2/10) as the strongest area.

#### 2: Lopsided Codebase -- Acme Corp has severe refactoring debt

Acme Corp Platform scores 58/100 (Needs Attention). The radar chart shows a pronounced dent in the refactoring axis (3.0/10) while other dimensions are moderate (5.5-7.2). The summary highlights refactoring debt as the critical weakness and the primary risk driver.

#### 3: Critical Codebase -- NovaPay legacy system is in poor shape

NovaPay's legacy payment processor scores 32/100 (Critical). The radar chart is small and collapsed inward across most axes. Legacy safety (2.1/10) and cognitive load (2.8/10) are critical. The summary uses "Critical" rating and emphasizes business risk urgently.

### UAT Scenarios (BDD)

#### Scenario: Overall health score accurately reflects dimension scores
```gherkin
Given the Acme Corp analysis produced these normalized dimension scores:
  | dimension        | score |
  | Code Quality     | 6.0   |
  | Test Design      | 7.2   |
  | Cognitive Load   | 6.9   |
  | DDD Compliance   | 6.5   |
  | Legacy Safety    | 5.5   |
  | Refactoring Debt | 3.0   |
When the overall health score is calculated
Then the score is 58/100 using the documented weighted formula
And the rating is "Needs Attention" based on documented thresholds
```

#### Scenario: Radar chart visually communicates the quality shape
```gherkin
Given the Acme Corp dimension scores range from 3.0 to 7.2
When the 6-axis radar chart renders in the executive summary
Then the chart shows a hexagon with a visible dent at the Refactoring axis
And each axis is labeled with the dimension name
And hovering over a data point shows the exact score
```

#### Scenario: Weakest dimension is highlighted
```gherkin
Given the lowest dimension score is Refactoring Debt at 3.0/10
When the executive summary renders
Then Refactoring Debt is visually highlighted as the weakest dimension
And an annotation explains the risk: "14 high-priority refactoring items increase cost and risk of future changes"
```

#### Scenario: Executive summary fits on one screen
```gherkin
Given Andrea opens the report on a standard laptop display (1920x1080)
When the executive summary section loads
Then all key information is visible without scrolling:
  overall score, radar chart, dimension bars, and weakest dimension callout
```

#### Scenario: Report with partial results adjusts gracefully
```gherkin
Given the DDD agent failed and only 5 dimension scores are available
When the executive summary renders
Then the radar chart shows 5 axes instead of 6
And the overall score is calculated from 5 dimensions with adjusted weights
And a note explains: "DDD Compliance: Not Available (agent timeout)"
```

### Acceptance Criteria

- [ ] Overall health score is calculated as documented weighted average of normalized dimensions, scaled to 0-100
- [ ] Overall rating is assigned based on documented score thresholds
- [ ] 6-axis radar chart renders with correct dimension labels and scores
- [ ] Weakest dimension is highlighted with risk annotation
- [ ] Executive summary is scannable in under 2 minutes on a standard display
- [ ] Missing dimensions are handled gracefully with adjusted calculations and explanatory notes

### Technical Notes

- Score thresholds for ratings need to be defined and documented (e.g., 0-40 Critical, 41-60 Needs Attention, 61-80 Good, 81-100 Excellent)
- Weight distribution for overall score documented in research: Code Quality 0.20, Test Design 0.20, Cognitive Load 0.20, DDD 0.15, Legacy Safety 0.15, Refactoring 0.10
- Radar chart library choice deferred to DESIGN wave (Chart.js recommended in research)
- Responsive design needed for both presentation (large screen) and laptop viewing

### Dependencies

- US-02 (agent results must be available)
- Score normalization formulas must be defined (see US-05)

### MoSCoW: Must Have

---

## US-04: Translate Quality Metrics to Business Risk

### Problem

Andrea presents codebase findings to client leadership -- CTOs, VPs of Engineering, CEOs -- who do not think in terms of "Farley Index 7.2" or "cyclomatic complexity 28." They think in terms of business risk: will this codebase slow us down, cause outages, make hiring harder, or cost us money? Andrea needs the report to automatically translate technical dimensions into business risk categories.

### Who

- Software consultant | Presenting to non-technical client leadership | Wants technical metrics framed as business risks

### Solution

A Business Risk Summary section in the report that maps dimension scores to business risk categories (Delivery Velocity Risk, Incident Risk, Onboarding Risk) with severity levels and estimated impact descriptions.

### Job Story Trace

- JS-02: Executive Communication of Technical Risk (primary)
- JS-04: Overcoming Client Denial (primary)

### Domain Examples

#### 1: High Velocity Risk -- Acme Corp's refactoring debt slows development

Acme Corp's Refactoring Debt (3.0/10) and Cognitive Load (6.9/10, moderate) combine to produce a HIGH Delivery Velocity Risk. The report estimates "25-35% slower than healthy baseline" for feature development velocity.

#### 2: Incident Risk -- Meridian Health's legacy code is fragile

Meridian Health has Legacy Safety at 3.2/10 and Test Design at 4.5/10. The report flags HIGH Incident Risk: "Critical paths in payment processing have limited test coverage and high dependency density. Estimated: elevated production incident frequency."

#### 3: Low Risk Profile -- Vertex API is healthy

Vertex API scores above 7 on all dimensions. Business risk section shows all categories as LOW with note: "This codebase has healthy technical foundations. Continued investment in test design and documentation will maintain this position."

### UAT Scenarios (BDD)

#### Scenario: Business risk section present in executive summary
```gherkin
Given the Acme Corp report has been generated with all 6 dimension scores
When Andrea opens the executive summary
Then a Business Risk Summary section appears after the dimension overview
And it contains at least 3 risk categories: Delivery Velocity, Incident, and Onboarding
And each category has a severity level (HIGH/MODERATE/LOW) and description
```

#### Scenario: Delivery velocity risk derived from refactoring and cognitive load
```gherkin
Given Acme Corp has Refactoring Debt at 3.0/10 and Cognitive Load at 6.9/10
When the business risk model evaluates Delivery Velocity Risk
Then the risk is rated HIGH
And the description mentions estimated velocity impact
And the description links to the contributing dimensions
```

#### Scenario: Risk categories link to underlying evidence
```gherkin
Given the Incident Risk is rated MODERATE for Acme Corp
When Andrea clicks on the Incident Risk category
Then she is navigated to the relevant dimension detail sections
And the connection between dimension scores and risk rating is explained
```

#### Scenario: All dimensions healthy produces low risk profile
```gherkin
Given Vertex API has all dimension scores above 7.0/10
When the business risk model evaluates all risk categories
Then all risk categories are rated LOW
And the summary notes that the codebase has healthy technical foundations
```

### Acceptance Criteria

- [ ] Business risk summary appears in executive summary section
- [ ] At least 3 risk categories are assessed: Delivery Velocity, Incident, Onboarding
- [ ] Each risk category shows a severity level (HIGH/MODERATE/LOW) and descriptive text
- [ ] Risk ratings are derived from specific dimension scores using a documented model
- [ ] Each risk category links to the contributing dimension evidence
- [ ] A healthy codebase (all dimensions above threshold) produces LOW risk across categories

### Technical Notes

- Risk model (which dimensions contribute to which risk category, thresholds) must be documented in the report's methodology section
- Risk descriptions should use business language, not technical jargon
- The risk model is an approximation -- the report should note it is based on code analysis and does not account for team structure, processes, or non-code factors
- Some risks (e.g., Key Person Dependency) cannot be assessed from code alone -- mark as "Not Assessed (requires team data)"

### Dependencies

- US-03 (dimension scores must be calculated and displayed)
- US-05 (normalization formulas must be defined)

### MoSCoW: Must Have

---

## US-05: Score Transparency and Derivation

### Problem

Andrea's primary anxiety is that scores might be ambiguous or misleading. If a client's CTO challenges a score, Andrea must be able to explain exactly how it was calculated -- from raw agent data through normalization formula to final number. Without full transparency, one successfully challenged number destroys trust in the entire report.

### Who

- Software consultant | Defending scores during client pushback | Needs every number to be fully traceable from summary to raw data

### Solution

Score derivation panels for each dimension that show: the raw agent output data, the normalization formula with actual values substituted, and a plain-language explanation of what the score means. The drill-down creates a "denial-proof" evidence chain from summary to specific findings.

### Job Story Trace

- JS-04: Overcoming Client Denial (primary)
- JS-02: Executive Communication of Technical Risk (secondary)

### Domain Examples

#### 1: Refactoring Debt Derivation -- Acme Corp 3.0/10

Andrea clicks into the Refactoring Debt score. She sees: raw data (14 recommendations: 2 high-risk, 7 medium-risk, 5 low-risk), the normalization formula (`max(0, 10 - weighted_count / threshold * factor)` with values substituted: `max(0, 10 - 25/10 * 2.8) = 3.0`), and explanation: "Significantly more refactoring debt than a healthy project. High-risk items affect core business logic."

#### 2: Farley Index Derivation -- Vertex API 8.4/10

Andrea opens the Test Design score. She sees: the 8 property scores (Understandable: 8.5, Maintainable: 8.0, Repeatable: 9.2, etc.), the composite formula weights, the resulting Farley Index of 8.4, and explanation: "Strong test design with excellent repeatability. Maintainability is the area with most room for improvement."

#### 3: Cognitive Load Derivation -- NovaPay 782/1000 (inverted: 2.2/10)

Andrea opens the Cognitive Load score. She sees: the 8 dimension raw scores, the weighted contribution of each, the CLI Score of 782/1000, the inversion formula (`10 - (782/100) = 2.2`), clamped to the 0-10 range, and explanation: "Extremely high cognitive load. New developers will face severe ramp-up challenges. Structural complexity and coupling are the primary contributors."

### UAT Scenarios (BDD)

#### Scenario: Score derivation shows raw data from agent
```gherkin
Given the Acme Corp report shows Refactoring Debt at 3.0/10
When Andrea opens the score derivation panel for Refactoring Debt
Then she sees the raw agent data: 14 recommendations with risk distribution
And the data matches the actual output from the refactoring agent
```

#### Scenario: Normalization formula is displayed with actual values
```gherkin
Given Andrea is viewing the Refactoring Debt score derivation
When she examines the normalization section
Then the formula is displayed symbolically (e.g., "max(0, 10 - weighted_count / threshold * factor)")
And actual values are substituted (e.g., "max(0, 10 - 25/10 * 2.8) = 3.0")
And the result matches the displayed dimension score
```

#### Scenario: Plain-language explanation accompanies every score
```gherkin
Given Andrea is viewing any dimension's score derivation
When the derivation panel renders
Then a "What this means" section explains the score in non-technical language
And the explanation describes the business consequence of the score level
```

#### Scenario: Drill-down from score to specific file-level findings
```gherkin
Given Andrea is viewing the Refactoring Debt score derivation
When she clicks "View all 14 recommendations"
Then she sees each recommendation with affected file, severity, and description
And each recommendation includes the specific code metrics that triggered it
```

#### Scenario: Applying displayed formula to displayed data reproduces score
```gherkin
Given Andrea reads the raw data and formula from a score derivation panel
When she manually applies the formula to the raw data
Then the result matches the displayed score exactly (no rounding discrepancies)
```

### Acceptance Criteria

- [ ] Every dimension has a score derivation panel accessible from the executive summary
- [ ] Score derivation shows the raw data from the agent output
- [ ] Normalization formula is displayed both symbolically and with actual values substituted
- [ ] A plain-language "What this means" explanation accompanies every score
- [ ] Drill-down to specific file-level findings is available from derivation panels
- [ ] Applying the displayed formula to the displayed raw data reproduces the displayed score

### Technical Notes

- Normalization formulas documented in research (section 8.2) serve as starting point; finalize during DESIGN
- Formula display must use actual values, not just symbolic -- clients should see the arithmetic
- Score derivation data must be embedded in the HTML report, not fetched from external sources
- Rounding strategy must be consistent: round at display time only, not intermediate steps

### Dependencies

- US-02 (agent results with raw data)
- US-03 (dimension scores to drill into)

### MoSCoW: Must Have

---

## US-06: Per-Dimension Detail Sections

### Problem

Client technical leads (CTOs, senior engineers) need to explore specific findings within each quality dimension. The executive summary tells them "Refactoring Debt is 3.0/10" but they need to see which specific files and what specific issues. Each of the 6 analysis dimensions has unique metrics and needs appropriate visualizations to communicate effectively.

### Who

- Software consultant and client technical leads | Exploring specific findings | Want per-dimension detail with appropriate visualizations

### Solution

A dedicated section for each of the 6 analysis dimensions with dimension-specific charts, tables of specific findings, severity indicators, and links to score derivation. Each section uses the visualization type best suited to that dimension's data.

### Job Story Trace

- JS-04: Overcoming Client Denial (primary)
- JS-01: Comprehensive Codebase Assessment (secondary)

### Domain Examples

#### 1: Code Smells Section -- Acme Corp

Shows: Grade badge (B), pie chart of issue severity distribution (1 high, 8 medium, 14 low), bar chart of issues by category (Bloaters: 5, Dispensables: 8, etc.), SOLID compliance radar (5 axes), and a sortable table of the top issues with file name, issue type, and severity.

#### 2: Test Design Section -- Meridian Health

Shows: Farley Index gauge (4.5/10), 8-property spider chart, stacked bar comparing static vs LLM scoring per property, Tautology Theatre count (7 mock tautologies), and table of top 5 worst-offending test files.

#### 3: Cognitive Load Section -- TechVentures

Shows: CLI Score gauge (645/1000), 8-dimension radar chart, bar chart of weighted contributions per dimension, and table of top 5 worst-offending files with their dimension breakdowns.

### UAT Scenarios (BDD)

#### Scenario: Code Smells section shows severity and category breakdowns
```gherkin
Given the Acme Corp report includes Code Smell Detection results
When Andrea navigates to the Code Smells detail section
Then she sees the code quality grade displayed prominently
And a severity distribution visualization (1 high, 8 medium, 14 low)
And an issues-by-category breakdown
And a SOLID compliance visualization across 5 principles
And a table of top issues sorted by severity
```

#### Scenario: Test Design section shows property-level detail
```gherkin
Given the report includes Test Design Review results
When Andrea navigates to the Test Design detail section
Then she sees the Farley Index gauge
And an 8-property spider chart
And Tautology Theatre summary counts
And a table of worst-offending test files
```

#### Scenario: Each dimension section links back to executive summary
```gherkin
Given Andrea is viewing the Cognitive Load detail section
When she wants to return to the overall picture
Then a navigation element links back to the executive summary
And the executive summary's Cognitive Load entry links to this detail section
```

#### Scenario: Dimension section for failed agent shows explanation
```gherkin
Given the DDD Architecture agent failed during analysis
When Andrea navigates to the DDD Compliance section
Then she sees "Not Available" with the failure reason (e.g., "Agent timed out")
And a suggestion to re-run with "--retry-agent ddd"
And no placeholder or misleading visualizations are shown
```

### Acceptance Criteria

- [ ] Each of the 6 dimensions has a dedicated detail section in the report
- [ ] Each section includes dimension-appropriate visualizations (charts, gauges, tables)
- [ ] Each section includes a sortable/browsable table of specific findings
- [ ] Navigation between executive summary and dimension sections is bidirectional
- [ ] Failed agent dimensions show clear "Not Available" with explanation
- [ ] Each section links to its score derivation panel (US-05)

### Technical Notes

- Visualization types per dimension documented in research (section 2.1-2.6)
- Some visualizations require specific chart libraries (heatmaps need D3.js)
- Consider implementing dimension sections incrementally -- start with the 3 most structured agents (test-design-reviewer, cognitive-load-analyzer, code-smell-detector) that already have numeric outputs
- Agent-specific JSON schema contracts needed for reliable rendering

### Dependencies

- US-02 (agent results)
- US-03 (executive summary for navigation context)
- US-05 (score derivation panels)

### MoSCoW: Should Have

---

## US-07: Report Navigation and Presentation Support

### Problem

Andrea uses the report in two modes: as a presentation aid during client meetings (screen-sharing, navigating between sections) and as a standalone document clients explore after the meeting. The report must support both modes with fast navigation, progressive disclosure, and print capability.

### Who

- Software consultant | Presenting findings live and handing off for self-exploration | Wants a report that works as both presentation aid and standalone document

### Solution

Sticky navigation bar for section jumping, collapsible detail sections for progressive disclosure, smooth scroll transitions, and a print-friendly CSS mode that produces clean static output for PDF handouts.

### Job Story Trace

- JS-02: Executive Communication of Technical Risk
- JS-04: Overcoming Client Denial

### Domain Examples

#### 1: Live Presentation -- Andrea navigates quickly during pushback

During the Acme Corp meeting, the VP challenges the Refactoring score. Andrea clicks "Refactoring" in the navigation bar, then expands the score derivation, then opens a specific finding -- all in under 5 seconds. The navigation is fast enough that the meeting flow is not disrupted.

#### 2: Standalone Exploration -- CTO explores after the meeting

The Acme Corp CTO opens the report on their laptop. They browse at their own pace, expanding sections they find interesting, collapsing others. The report is self-contained -- no dependencies on external servers or Andrea's system.

#### 3: PDF Handout -- Andrea prints the executive summary

Andrea prepares for the Meridian Health meeting by printing the executive summary. The print mode produces 2 clean pages with the overall score, radar chart, dimension bars, and business risk summary -- no interactive clutter.

### UAT Scenarios (BDD)

#### Scenario: Sticky navigation enables fast section jumping
```gherkin
Given Andrea is viewing the Code Smells detail section
When she clicks "Executive Summary" in the sticky navigation bar
Then the page scrolls smoothly to the executive summary
And the navigation bar remains visible at the top
And "Executive Summary" is highlighted as the active section
```

#### Scenario: Sections expand and collapse for progressive disclosure
```gherkin
Given Andrea is in the executive summary
And the dimension detail sections are collapsed by default
When she clicks on "Code Quality: B (6.0/10)"
Then the Code Smells detail section expands to show full visualizations
And other sections remain collapsed
```

#### Scenario: Report functions offline without external dependencies
```gherkin
Given the CTO has downloaded the report HTML file
And their computer has no internet access
When they open the report in a browser
Then all visualizations render correctly
And all navigation and interactions work
And no console errors appear related to missing external resources
```

#### Scenario: Print mode produces clean PDF-ready output
```gherkin
Given Andrea activates print mode (browser print or dedicated button)
When the print layout renders
Then interactive elements are replaced with static representations
And the executive summary fits on 2 pages maximum
And charts appear as readable static images
And navigation elements are hidden
```

### Acceptance Criteria

- [ ] Sticky navigation bar is always visible with section links
- [ ] Clicking a section link scrolls smoothly to that section
- [ ] Active section is highlighted in navigation
- [ ] Detail sections are collapsible for progressive disclosure
- [ ] Report is fully functional offline (all resources embedded or CDN-loaded with fallback)
- [ ] Print mode produces clean, static output suitable for PDF

### Technical Notes

- Offline capability: either inline all JS/CSS libraries or load from CDN with graceful degradation
- Research recommends CDN loading (~500KB) with inline option for offline use (~3MB)
- Print CSS should use @media print rules
- Smooth scroll behavior via CSS `scroll-behavior: smooth` or JS
- Consider: should sections default to expanded or collapsed? Collapsed supports presentation mode; expanded supports self-exploration. May need a toggle.

### Dependencies

- US-03 (executive summary must exist)
- US-06 (dimension sections must exist to navigate to)

### MoSCoW: Should Have

---

## Story Summary

| ID | Title | MoSCoW | Effort Est. | Scenarios | Dependencies |
|---|---|---|---|---|---|
| US-01 | Launch Codebase Analysis | Must | 2-3 days | 5 | None |
| US-02 | Orchestrate Multi-Agent Analysis | Must | 2-3 days | 4 | US-01 |
| US-03 | Executive Summary with Health Score | Must | 2-3 days | 5 | US-02 |
| US-04 | Business Risk Translation | Must | 1-2 days | 4 | US-03, US-05 |
| US-05 | Score Transparency and Derivation | Must | 2-3 days | 5 | US-02, US-03 |
| US-06 | Per-Dimension Detail Sections | Should | 2-3 days | 4 | US-02, US-03, US-05 |
| US-07 | Report Navigation and Presentation | Should | 1-2 days | 4 | US-03, US-06 |

### Walking Skeleton (MVP)

The minimum end-to-end slice that delivers value:

**US-01 + US-02 + US-03 + US-05** = Andrea can launch analysis, agents run, and she gets a report with an executive summary, radar chart, dimension scores, and transparent score derivation.

**US-04** adds business risk framing essential for client presentations.

**US-06 + US-07** add depth and polish needed for the full consulting deliverable.

### Dependency Graph

```
US-01 (Launch)
  |
  v
US-02 (Orchestrate)
  |
  +-------+-------+
  v       v       v
US-03   US-05   US-06
(Summary) (Derivation) (Details)
  |       |       |
  +---+---+       |
      v           |
    US-04         |
    (Risk)        |
      |           |
      +-----+-----+
            v
          US-07
          (Navigation)
```
