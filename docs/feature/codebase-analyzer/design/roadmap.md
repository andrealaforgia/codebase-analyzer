# Implementation Roadmap: Codebase Analyzer

## Rejected Simple Alternatives

### Alternative 1: Shell script orchestrator
- **What**: Bash script that runs `claude` commands sequentially and concatenates markdown outputs
- **Expected impact**: 30% of problem -- orchestration only, no visualization, no normalization
- **Why insufficient**: No score normalization, no interactive charts, no drill-down. Raw markdown concatenation does not produce a denial-proof report.

### Alternative 2: Manual agent runs + static HTML template
- **What**: Run agents manually, paste scores into a pre-built HTML template with hardcoded chart configs
- **Expected impact**: 60% of problem -- visual report exists but requires manual data entry
- **Why insufficient**: Manual data entry is error-prone and defeats the automation goal (US-01, US-02). No score derivation transparency. Does not scale across client engagements.

### Why automation is necessary
1. Simple alternatives fail because: manual synthesis is the core pain point (opportunity score 16.5) and error-prone score entry destroys the credibility this tool exists to build
2. Complexity justified by: automated pipeline from agent JSON to rendered HTML eliminates all manual steps and guarantees score consistency across report levels

---

## Roadmap

### Phase 01: Foundation -- Agent Contracts and Data Models

#### Step 01-01: Agent JSON output contracts and Pydantic models
- **Description**: Define Pydantic models for all 6 agent JSON schemas. These are the integration contracts that agents must conform to and the normalizer consumes.
- **Acceptance Criteria**:
  - Each of the 6 agents has a corresponding Pydantic model
  - Models validate required fields, types, and value ranges
  - Invalid JSON produces clear error identifying the agent and field
  - Models are frozen (immutable)
- **Architectural Constraints**:
  - Dataclasses/Pydantic only, no class hierarchies
  - Models live in a single `models.py` module
- **Story Trace**: US-02, US-05

#### Step 01-02: Report data structures and overall score model
- **Description**: Define the unified report data structure: metadata, normalized dimension scores, overall health score, rating, business risk assessments. This is the data shape the report generator receives.
- **Acceptance Criteria**:
  - Report data model includes metadata, dimension scores, overall score, risk assessments
  - Overall score computable from dimension scores via documented formula
  - Rating derivable from overall score via threshold lookup
  - Missing dimensions representable (optional fields)
- **Architectural Constraints**:
  - Frozen dataclass or Pydantic model
  - Formula constants (weights, thresholds) are named values, not magic numbers
- **Story Trace**: US-03, US-05

### Phase 02: Score Pipeline -- Normalization and Risk

#### Step 02-01: Score normalization functions
- **Description**: Pure functions that transform raw agent JSON (validated by models) into normalized 0-10 dimension scores using the documented formulas.
- **Acceptance Criteria**:
  - Each agent type has a normalization function
  - Output scores are in 0-10 range
  - Applying the formula to known input reproduces expected output
  - Functions return both the normalized score and the formula-with-values string (for derivation panels)
- **Architectural Constraints**:
  - Pure functions: raw data in, (score, formula_string) out
  - No file I/O or side effects
- **Story Trace**: US-05

#### Step 02-02: Overall health score and business risk derivation
- **Description**: Pure functions for weighted health score calculation (0-100) and business risk category assessment (Delivery Velocity, Incident, Onboarding).
- **Acceptance Criteria**:
  - Health score is weighted average of available dimensions, scaled to 0-100
  - Missing dimensions cause weight redistribution (not score penalty)
  - Each risk category produces a severity level (HIGH/MODERATE/LOW) and contributing dimension citations
  - All-healthy dimensions produce LOW across all risk categories
- **Architectural Constraints**:
  - Pure functions: dimension scores in, health score + risk assessments out
  - Risk model weights and thresholds are named constants
- **Story Trace**: US-03, US-04

### Phase 03: Report Generation -- Templates and Rendering

#### Step 03-01: HTML base template with inlined libraries and navigation
- **Description**: Jinja2 base template containing the HTML skeleton, inlined Chart.js/D3.js/Mermaid.js, sticky navigation bar, print CSS, and report data injection point.
- **Acceptance Criteria**:
  - Single HTML file renders in a modern browser with no external dependencies
  - Sticky navigation bar with section links is present
  - Print CSS hides interactive elements and produces clean output
  - Report data injectable as `const reportData = {...}` in script tag
- **Architectural Constraints**:
  - JS libraries stored as minified files in `src/assets/`, inlined via Jinja2 include
  - No CSS framework -- custom CSS only
- **Story Trace**: US-07

#### Step 03-02: Executive summary section with radar chart and gauges
- **Description**: Jinja2 template section rendering overall health gauge, 6-axis radar chart, dimension score bars, weakest dimension callout, and business risk summary.
- **Acceptance Criteria**:
  - Overall score displayed as gauge with rating label
  - Radar chart renders with correct axis labels and data points
  - Weakest dimension visually highlighted with risk annotation
  - Business risk categories displayed with severity badges
  - Executive summary scannable in under 2 minutes on standard display
- **Architectural Constraints**:
  - Chart configs generated by Python chart builder functions, not hardcoded in template
  - Radar adapts to fewer axes when dimensions are missing
- **Story Trace**: US-03, US-04

#### Step 03-03: Score derivation panels and dimension detail sections
- **Description**: Reusable Jinja2 template for per-dimension detail: score derivation (raw data, formula with values, explanation), dimension-specific charts, and findings tables. Render once per available dimension.
- **Acceptance Criteria**:
  - Each dimension has a detail section accessible from executive summary
  - Score derivation shows raw data, formula with substituted values, and plain-language explanation
  - Applying displayed formula to displayed data reproduces displayed score
  - Failed dimensions show "Not Available" with reason
  - Navigation between executive summary and dimension sections is bidirectional
- **Architectural Constraints**:
  - Template is parameterized -- same template renders all 6 dimensions with different chart configs
  - Derivation formula strings generated by Python, not computed in JavaScript
- **Story Trace**: US-05, US-06

### Phase 04: Pipeline Assembly and Orchestrator Agent

#### Step 04-01: Python pipeline entry point
- **Description**: Single Python function that reads agent JSON files from a directory, runs normalization, derives risks, assembles report data, renders templates, and writes the HTML file.
- **Acceptance Criteria**:
  - Given a directory of valid agent JSON files, produces a valid HTML report
  - Handles partial results (missing agent files) without error
  - Reports which agents were available and which were missing
  - Exit code 0 on success, non-zero on fatal error (e.g., no agents at all)
- **Architectural Constraints**:
  - Composition pipeline: read -> validate -> normalize -> risk -> assemble -> render -> write
  - File I/O at boundaries only (read JSON at start, write HTML at end)
- **Story Trace**: US-01, US-02

#### Step 04-02: Orchestrator agent definition
- **Description**: Claude Code agent markdown file that validates target directory, launches 6 subagents (5 parallel + 1 sequential), handles failures, then invokes the Python pipeline to generate the report.
- **Acceptance Criteria**:
  - Agent accepts target directory and optional configuration (project name, output path, agent selection)
  - Independent agents launch without waiting for each other
  - Refactoring agent waits for code smell detector to complete
  - Agent failure is caught and reported; remaining agents continue
  - Python pipeline invoked after all agents complete (or fail)
  - Completion summary shows overall score, weakest/strongest dimensions
- **Architectural Constraints**:
  - Agent file only -- no Python code in the orchestrator
  - All computation delegated to Python pipeline via Bash tool
- **Story Trace**: US-01, US-02

### Phase 05: Agent Modifications (External Dependency)

#### Step 05-01: Add JSON output to all 6 analysis agents
- **Description**: Modify each agent's `.md` definition at `~/.claude/agents/` to write a `{agent-name}-data.json` file conforming to the defined contract schemas. Existing markdown output unchanged.
- **Acceptance Criteria**:
  - Each agent writes a valid JSON file alongside its markdown report
  - JSON conforms to the Pydantic model for that agent
  - DDD and legacy agents include a self-assessed 0-10 overall score with rubric justification
  - Existing agent behavior and markdown output is unchanged
- **Architectural Constraints**:
  - Modifications are additive -- do not change existing agent behavior
  - JSON schema matches the contracts defined in Phase 01
- **Story Trace**: US-02

---

## Roadmap Summary

| Phase | Steps | Story Coverage | Est. Production Files |
|-------|-------|---------------|----------------------|
| 01 Foundation | 2 | US-02, US-03, US-05 | 1 (models.py) |
| 02 Score Pipeline | 2 | US-03, US-04, US-05 | 3 (normalize.py, risk.py, formulas.py) |
| 03 Report Generation | 3 | US-03, US-04, US-05, US-06, US-07 | 8 (render.py, charts.py, pipeline.py + 5 templates) |
| 04 Pipeline + Orchestrator | 2 | US-01, US-02 | 2 (pipeline.py update, codebase-analyzer.md) |
| 05 Agent Modifications | 1 | US-02 | 6 (agent .md files, external repo) |

**Totals**: 10 steps, ~17 production files (excl. external agent mods)
**Step ratio**: 10 / 17 = 0.59 (well within 2.5 threshold)

## Dependency Graph

```
Phase 01 (Models)
    |
    v
Phase 02 (Normalize + Risk)
    |
    v
Phase 03 (Templates + Rendering)
    |
    v
Phase 04 (Pipeline + Agent)
    |
Phase 05 (Agent Mods) -- can start after Phase 01 contracts defined
```

Phase 05 can proceed in parallel with Phases 02-04 once the JSON contracts from Phase 01 are defined.
