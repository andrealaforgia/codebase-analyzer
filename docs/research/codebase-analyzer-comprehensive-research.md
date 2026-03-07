# Codebase Analyzer: Comprehensive Research Document

## 1. Executive Summary

This research explores how to build a **visual codebase analysis tool** that orchestrates multiple specialized AI agents to assess a codebase across different quality dimensions, then generates a rich HTML report with interactive charts, heatmaps, treemaps, radar diagrams, and other visualizations.

The tool integrates six existing agents:
1. **alf-code-smell-detector** -- Code quality grade (A-F) with categorized smell detection
2. **alf-refactoring-expert** -- Refactoring priority matrix with impact/complexity scoring
3. **alf-ddd-architect** -- Domain-Driven Design compliance assessment
4. **alf-legacy-code-expert** -- Legacy code risk and testability analysis
5. **test-design-reviewer** -- Farley Index (0-10) for test design quality
6. **cognitive-load-analyzer** -- Cognitive Load Index (0-1000) across 8 dimensions

**Key finding**: The optimal approach is a Python-based CLI orchestrator that runs each agent as a subagent (via Claude Code's Task/Agent tool), collects their structured JSON/markdown outputs, and renders a self-contained HTML report using Jinja2 templates with embedded Chart.js/D3.js visualizations.

---

## 2. Agent Output Analysis

### 2.1 alf-code-smell-detector

**Output files**: `code-smell-detector-summary.md`, `code-smell-detector-report.md`

**Key metrics extractable**:
- Code Quality Grade: A-F (maps to 5-0 numeric scale)
- Issue counts by severity: High, Medium, Low
- Issue distribution by category: Bloaters, Change Preventers, Couplers, Dispensables, OO Abusers
- SOLID violation counts (SRP, OCP, LSP, ISP, DIP)
- Project size (file count)

**Visualization potential**:
- Pie chart: Issue distribution by severity
- Bar chart: Issues per category
- Radar chart: SOLID compliance (5 axes)
- Grade badge/gauge

### 2.2 alf-refactoring-expert

**Output files**: `code-refactoring-summary.md`, `code-refactoring-report.md`

**Key metrics extractable**:
- Priority matrix: Impact vs Complexity per refactoring
- Risk levels: Low/Medium/High per recommendation
- Refactoring category distribution (Composing Methods, Moving Features, etc.)
- Implementation sequence (ordered recommendations)

**Visualization potential**:
- Scatter plot: Impact vs Complexity quadrant
- Stacked bar: Refactoring risk distribution
- Timeline/Gantt: Implementation sequence
- Heatmap: Risk by category

### 2.3 alf-ddd-architect

**Output files**: Architectural analysis report (markdown)

**Key metrics extractable**:
- Bounded context count and relationships
- Subdomain classification (Core/Supporting/Generic)
- Anti-pattern counts (Anemic Domain Model, Big Ball of Mud, etc.)
- Tactical pattern usage (Entities, Value Objects, Aggregates, Domain Events)
- Ubiquitous Language coverage

**Visualization potential**:
- Context map diagram (Mermaid)
- Pie chart: Subdomain distribution
- Bar chart: Anti-pattern frequency
- Radar chart: DDD pattern maturity (Strategic, Tactical, Language, Boundaries, Events)

### 2.4 alf-legacy-code-expert

**Output files**: Legacy code analysis report (markdown)

**Key metrics extractable**:
- Dependency count and types
- Seam availability (Object, Link, Preprocessing)
- Testability score (derived from dependency density)
- Change risk per module
- Test point availability

**Visualization potential**:
- Dependency graph (force-directed or hierarchical)
- Risk heatmap by module
- Bar chart: Dependencies by breaking technique needed
- Gauge: Overall testability score

### 2.5 test-design-reviewer

**Output files**: Structured report with Farley Index

**Key metrics extractable** (highly structured):
- Farley Index: 0-10 (weighted composite)
- 8 property scores (Static, LLM, Blended): Understandable, Maintainable, Repeatable, Atomic, Necessary, Granular, Fast, First
- Signal counts per type with severity
- Tautology Theatre counts (Mock Tautologies, Mock-Only, Trivial, Framework)
- Top 5 worst offenders with scores

**Visualization potential**:
- Radar/spider chart: 8 properties
- Gauge: Farley Index
- Stacked bar: Static vs LLM scoring per property
- Heatmap: Signal severity by property
- Table: Worst offenders with drill-down

### 2.6 cognitive-load-analyzer

**Output files**: Structured report with CLI score

**Key metrics extractable** (highly structured):
- CLI Score: 0-1000
- 8 dimension scores (Raw, Normalized, Weighted): Structural Complexity, Nesting Depth, Volume/Size, Naming Quality, Coupling, Cohesion, Duplication, Navigability
- Interaction penalty
- Top 5 worst offenders
- Tool/fallback mode per dimension

**Visualization potential**:
- Radar/spider chart: 8 dimensions
- Gauge: CLI Score with color zones
- Bar chart: Weighted contribution per dimension
- Treemap/heatmap: Worst offending files/functions

---

## 3. Visualization Strategy

### 3.1 Chart Types by Purpose

| Visualization | Purpose | Library | Use Case |
|---|---|---|---|
| **Radar/Spider Chart** | Multi-dimensional comparison | Chart.js | Overall quality radar (6 agents), Farley properties, CLI dimensions |
| **Gauge/Donut** | Single composite score | Chart.js (doughnut) | Farley Index, CLI Score, Code Quality Grade |
| **Pie Chart** | Distribution breakdown | Chart.js | Issue severity, subdomain types, smell categories |
| **Bar Chart (horizontal)** | Ranked comparisons | Chart.js | Top offenders, dimension scores, category counts |
| **Stacked Bar** | Composition over categories | Chart.js | Risk distribution, static vs LLM scoring |
| **Heatmap** | Intensity across 2 dimensions | D3.js or Chart.js (matrix) | File complexity heatmap, risk by module/dimension |
| **Treemap** | Hierarchical size/color encoding | D3.js | File size + complexity, package structure |
| **Scatter Plot** | Two-variable correlation | Chart.js | Impact vs Complexity (refactoring quadrant) |
| **Mermaid Diagram** | Architecture/relationships | Mermaid.js | Bounded context map, dependency graph |
| **Progress Bars** | Percentage completion | CSS | SOLID compliance per principle |

### 3.2 Recommended Library Stack

**Primary: Chart.js v4** ([d3js.org](https://d3js.org/), [chart.js docs](https://www.chartjs.org/))
- Pros: CDN-loadable (~200KB), simple API, responsive, rich chart types including radar/doughnut/bar/scatter
- Cons: No native treemap or heatmap (needs plugins)
- Use for: 80% of visualizations (radar, pie, bar, gauge, scatter)

**Secondary: D3.js v7** ([d3js.org](https://d3js.org/))
- Pros: Ultimate flexibility, heatmaps, treemaps, force-directed graphs
- Cons: Larger (~250KB), more complex API
- Use for: Treemaps, heatmaps, dependency graphs

**Diagrams: Mermaid.js** ([mermaid.ai](https://mermaid.ai/open-source/syntax/radar.html))
- Pros: Declarative syntax, CDN-loadable, supports many diagram types
- Use for: Bounded context maps, dependency flow diagrams

**Alternative considered but not recommended:**
- **Plotly.js**: Self-contained offline HTML export possible, but ~3MB per file is too heavy ([plotly docs](https://plotly.com/python/interactive-html-export/))
- **Chartkick.py**: Convenient but limited chart types ([chartkick.com](https://chartkick.com/python))

### 3.3 The Composite "Health Dashboard" Concept

Inspired by [CodeCharta](https://codecharta.com/), [SonarQube](https://docs.sonarsource.com/sonarqube-server/10.8/user-guide/code-metrics/metrics-definition), and [Code Climate](https://codeclimate.com/quality), the report should present a **unified health score** alongside per-dimension breakdowns:

```
Overall Codebase Health: 72/100 (Good)

+-------------------+------------------+------------------+
| Code Smells: B    | Test Design: 7.2 | Cognitive Load:  |
| (23 issues)       | (Farley Index)   | 312/1000         |
+-------------------+------------------+------------------+
| DDD Compliance:   | Refactoring:     | Legacy Risk:     |
| 65% (Moderate)    | 14 recommended   | Medium           |
+-------------------+------------------+------------------+
```

---

## 4. Architecture Design

### 4.1 High-Level Architecture

```
+------------------+     +-------------------+     +------------------+
|                  |     |                   |     |                  |
|  CLI Entrypoint  +---->+  Agent Orchestrator+---->+  Report Generator|
|  (Python/Shell)  |     |  (runs 6 agents)  |     |  (Jinja2 + JS)   |
|                  |     |                   |     |                  |
+------------------+     +--------+----------+     +--------+---------+
                                  |                         |
                         +--------v----------+     +--------v---------+
                         |                   |     |                  |
                         | Agent Results     |     | HTML Report      |
                         | (JSON/Markdown)   |     | (self-contained) |
                         |                   |     |                  |
                         +-------------------+     +------------------+
```

### 4.2 Component Breakdown

#### Component 1: CLI Entrypoint
- **Language**: Python 3.11+ or Shell script
- **Responsibility**: Accept target directory, configuration options, output path
- **Interface**: `codebase-analyzer analyze <target-dir> [--output report.html] [--agents all|smell,test,cognitive]`

#### Component 2: Agent Orchestrator
- **Responsibility**: Launch each agent as a Claude Code subagent, collect results
- **Key design decision**: Agents run **sequentially** (some depend on prior results, e.g., refactoring-expert needs code-smell-detector output) or **in parallel** where independent
- **Parallelization opportunities**:
  - Parallel group 1: `code-smell-detector`, `test-design-reviewer`, `cognitive-load-analyzer`, `ddd-architect`, `legacy-code-expert`
  - Sequential: `refactoring-expert` (depends on `code-smell-detector`)
- **Output**: Structured intermediate format (JSON preferred for programmatic consumption)

#### Component 3: Result Normalizer
- **Responsibility**: Parse diverse agent outputs (markdown reports) into a unified JSON schema
- **Challenge**: Most agents output markdown, not structured data
- **Solution options**:
  1. **Post-process markdown** with regex/LLM parsing (fragile)
  2. **Modify agents** to also output a JSON summary alongside markdown (preferred)
  3. **Use a normalization agent** that reads markdown and extracts structured data

#### Component 4: Report Generator
- **Technology**: Python + Jinja2 templates
- **Approach**: Render a single HTML file with:
  - CSS inlined or loaded via CDN (Bootstrap/Tailwind for layout)
  - Chart.js + D3.js loaded via CDN
  - All data embedded as JavaScript `const` in `<script>` tags
  - Mermaid.js for architecture diagrams
- **Layout**: Tabbed or scrollable dashboard with sections per agent

### 4.3 Unified Data Schema

```json
{
  "metadata": {
    "project_name": "my-project",
    "target_directory": "/path/to/project",
    "analysis_date": "2026-03-07T12:00:00Z",
    "total_files": 150,
    "total_loc": 25000,
    "primary_language": "Python"
  },
  "overall_health": {
    "score": 72,
    "rating": "Good",
    "grade": "B"
  },
  "dimensions": {
    "code_smells": {
      "grade": "B",
      "numeric_score": 4,
      "total_issues": 23,
      "severity_distribution": { "high": 1, "medium": 8, "low": 14 },
      "category_distribution": {
        "Bloaters": 5, "Couplers": 3, "Dispensables": 8, "Change Preventers": 2, "OO Abusers": 5
      },
      "solid_compliance": {
        "SRP": 0.7, "OCP": 0.8, "LSP": 0.9, "ISP": 0.6, "DIP": 0.75
      },
      "top_issues": [...]
    },
    "refactoring": {
      "total_recommendations": 14,
      "priority_matrix": [...],
      "risk_distribution": { "low": 5, "medium": 7, "high": 2 },
      "implementation_sequence": [...]
    },
    "ddd_compliance": {
      "overall_score": 0.65,
      "bounded_contexts": 4,
      "subdomain_distribution": { "core": 1, "supporting": 2, "generic": 1 },
      "anti_patterns_found": [...],
      "pattern_maturity": {
        "strategic_design": 0.6, "tactical_design": 0.7, "ubiquitous_language": 0.5, "boundaries": 0.7, "events": 0.4
      }
    },
    "legacy_risk": {
      "overall_risk": "Medium",
      "risk_score": 0.45,
      "dependency_count": 32,
      "testability_score": 0.6,
      "seam_availability": { "object": 12, "link": 3, "preprocessing": 0 },
      "modules_at_risk": [...]
    },
    "test_design": {
      "farley_index": 7.2,
      "rating": "Good",
      "properties": {
        "Understandable": { "static": 8.0, "llm": 7.5, "blended": 7.8 },
        "Maintainable": { "static": 7.0, "llm": 6.5, "blended": 6.8 },
        "Repeatable": { "static": 9.0, "llm": 8.5, "blended": 8.8 },
        "Atomic": { "static": 7.5, "llm": 7.0, "blended": 7.3 },
        "Necessary": { "static": 6.0, "llm": 6.5, "blended": 6.2 },
        "Granular": { "static": 7.0, "llm": 7.5, "blended": 7.2 },
        "Fast": { "static": 8.5, "llm": 8.0, "blended": 8.3 },
        "First": { "static": 5.0, "llm": 6.0, "blended": 5.4 }
      },
      "tautology_count": 3,
      "worst_offenders": [...]
    },
    "cognitive_load": {
      "cli_score": 312,
      "rating": "Moderate",
      "dimensions": {
        "D1_structural_complexity": { "raw": "avg_cc=5.2", "normalized": 0.35, "weighted": 52.5 },
        "D2_nesting_depth": { "raw": "P90=4", "normalized": 0.30, "weighted": 37.5 },
        "D3_volume_size": { "raw": "avg=120LOC", "normalized": 0.25, "weighted": 31.3 },
        "D4_naming_quality": { "raw": "score=0.72", "normalized": 0.28, "weighted": 35.0 },
        "D5_coupling": { "raw": "avg_imports=6", "normalized": 0.40, "weighted": 50.0 },
        "D6_cohesion": { "raw": "LCOM=0.35", "normalized": 0.35, "weighted": 43.8 },
        "D7_duplication": { "raw": "3.2%", "normalized": 0.15, "weighted": 15.0 },
        "D8_navigability": { "raw": "avg_depth=3", "normalized": 0.25, "weighted": 31.3 }
      },
      "interaction_penalty": 15.6,
      "worst_offenders": [...]
    }
  }
}
```

---

## 5. Report Layout Design

### 5.1 Page Structure

```
+========================================+
|  CODEBASE HEALTH REPORT               |
|  Project: my-project | Date: 2026-03-07|
+========================================+

+-- Section 1: Executive Dashboard ------+
|                                        |
|  [Overall Health Gauge: 72/100]        |
|                                        |
|  +--------+ +--------+ +--------+     |
|  |Smells:B| |Test:7.2| |CLI:312 |     |
|  +--------+ +--------+ +--------+     |
|  +--------+ +--------+ +--------+     |
|  |DDD: 65%| |Refactor | |Legacy  |     |
|  |        | |14 items | |Medium  |     |
|  +--------+ +--------+ +--------+     |
|                                        |
|  [6-Axis Radar: All Dimensions]        |
+----------------------------------------+

+-- Section 2: Code Smells Analysis -----+
|  [Grade Badge: B]                      |
|  [Pie: Severity Distribution]          |
|  [Bar: Issues by Category]             |
|  [Radar: SOLID Compliance]             |
|  [Table: Top Issues]                   |
+----------------------------------------+

+-- Section 3: Test Design Quality ------+
|  [Gauge: Farley Index 7.2/10]          |
|  [Radar: 8 Properties Spider Chart]    |
|  [Stacked Bar: Static vs LLM Scores]  |
|  [Table: Worst Offenders]              |
|  [Tautology Theatre Summary]           |
+----------------------------------------+

+-- Section 4: Cognitive Load -----------+
|  [Gauge: CLI 312/1000]                 |
|  [Radar: 8 Dimensions]                 |
|  [Bar: Weighted Contributions]         |
|  [Heatmap: File Complexity Grid]       |
|  [Table: Top 5 Worst Offenders]        |
+----------------------------------------+

+-- Section 5: DDD Compliance -----------+
|  [Mermaid: Bounded Context Map]        |
|  [Pie: Subdomain Distribution]         |
|  [Radar: DDD Pattern Maturity]         |
|  [Bar: Anti-Patterns Found]            |
+----------------------------------------+

+-- Section 6: Legacy Risk ---------------+
|  [Gauge: Testability Score]            |
|  [Heatmap: Module Risk Map]            |
|  [Bar: Dependencies by Type]           |
|  [Table: Modules at Risk]              |
+----------------------------------------+

+-- Section 7: Refactoring Roadmap ------+
|  [Scatter: Impact vs Complexity]       |
|  [Stacked Bar: Risk Distribution]      |
|  [Ordered List: Implementation Plan]   |
+----------------------------------------+

+-- Section 8: Appendix ------------------+
|  [Full findings from each agent]       |
|  [Methodology notes]                   |
+----------------------------------------+
```

### 5.2 The Master Radar Chart

The centerpiece visualization is a **6-axis radar chart** showing normalized scores (0-10) for each dimension:

| Axis | Source | Normalization |
|---|---|---|
| Code Quality | alf-code-smell-detector | Grade A=10, B=8, C=6, D=4, F=2 |
| Test Design | test-design-reviewer | Farley Index (already 0-10) |
| Cognitive Load | cognitive-load-analyzer | Inverted: `10 - (CLI_score / 100)`, capped at 0-10 |
| DDD Compliance | alf-ddd-architect | Overall score * 10 |
| Legacy Safety | alf-legacy-code-expert | Inverted risk: `10 * (1 - risk_score)` |
| Refactoring Debt | alf-refactoring-expert | `10 - (recommendation_count / max_expected * 10)` |

This gives a single "shape" that visually communicates codebase health at a glance.

---

## 6. Technical Implementation Approaches

### 6.1 Approach A: Claude Code Agent (Recommended for MVP)

Build the orchestrator **as a Claude Code agent itself** that:
1. Launches each analysis agent via the `Agent` tool (Task-based subagents)
2. Collects results
3. Uses a Python script to parse results and generate HTML

**Pros**: Leverages existing agent infrastructure, no external dependencies
**Cons**: Requires Claude Code to be running, not a standalone CLI

### 6.2 Approach B: Python CLI with Subprocess

Build a Python CLI that:
1. Invokes `claude` CLI commands to run each agent
2. Parses output files
3. Generates HTML report via Jinja2

```python
# Pseudo-code
import subprocess
import json
from jinja2 import Template

# Run agents
subprocess.run(["claude", "-a", "alf-code-smell-detector", ...])
subprocess.run(["claude", "-a", "test-design-reviewer", ...])
# ... etc

# Parse results
results = parse_agent_outputs("./reports/")

# Generate HTML
template = Template(open("report_template.html").read())
html = template.render(data=results)
open("report.html", "w").write(html)
```

**Pros**: Standalone, scriptable, CI/CD-friendly
**Cons**: Requires `claude` CLI installed, agent invocation API may vary

### 6.3 Approach C: Hybrid Claude Agent + Python Generator

The agent orchestrates analysis and produces a JSON data file, then a Python script takes that JSON and renders the HTML report. This separates concerns cleanly.

**Recommended**: Approach C for production quality.

### 6.4 HTML Report Generation (Jinja2 + Chart.js)

The Jinja2 template approach ([GeeksforGeeks guide](https://www.geeksforgeeks.org/data-visualization/how-to-use-jinja-for-data-visualization/), [Jinchart](https://github.com/Winnetou/jinchart)):

```html
<!DOCTYPE html>
<html>
<head>
  <title>Codebase Health Report - {{ metadata.project_name }}</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5/dist/css/bootstrap.min.css" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
  <script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
</head>
<body>
  <script>
    // Embed all data as JS const from Jinja2
    const reportData = {{ data | tojson }};
  </script>

  <!-- Dashboard sections reference reportData to render charts -->
  <canvas id="masterRadar"></canvas>
  <script>
    new Chart(document.getElementById('masterRadar'), {
      type: 'radar',
      data: {
        labels: ['Code Quality', 'Test Design', 'Cognitive Load', 'DDD', 'Legacy Safety', 'Refactoring'],
        datasets: [{
          data: [
            reportData.dimensions.code_smells.numeric_score * 2,
            reportData.dimensions.test_design.farley_index,
            10 - (reportData.dimensions.cognitive_load.cli_score / 100),
            reportData.dimensions.ddd_compliance.overall_score * 10,
            10 * (1 - reportData.dimensions.legacy_risk.risk_score),
            Math.max(0, 10 - reportData.dimensions.refactoring.total_recommendations / 2)
          ],
          // ... styling
        }]
      },
      options: { scales: { r: { min: 0, max: 10 } } }
    });
  </script>
</body>
</html>
```

---

## 7. Existing Tools and Inspiration

### 7.1 CodeCharta (MaibornWolff)
- Open-source, 3D city metaphor for code visualization
- Two-part: Shell (CCSH) for metric collection, Web Studio for visualization
- Imports from SonarQube, Tokei, CodeMaat, SourceMonitor, CSV
- **Lesson**: Separation of collection and visualization is key
- Source: [codecharta.com](https://codecharta.com/), [GitHub](https://github.com/MaibornWolff/codecharta)

### 7.2 SonarQube
- Industry standard for code quality
- Dimensions: Reliability, Security, Maintainability, Complexity, Duplication, Coverage
- Dashboard with metric cards, issue lists, trend charts
- **Lesson**: Multi-dimensional quality rating with letter grades (A-E) per dimension
- Source: [SonarQube Docs](https://docs.sonarsource.com/sonarqube-server/10.8/user-guide/code-metrics/metrics-definition)

### 7.3 NDepend / JArchitect / CppDepend
- Treemap visualization of code metrics
- Rectangle size = LOC, color = complexity severity
- **Lesson**: Treemaps are excellent for "where are the hotspots?" questions
- Source: [NDepend Treemap](https://www.ndepend.com/docs/treemap-visualization-of-code-metrics)

### 7.4 Code Climate (now Qlty)
- Automated code review with maintainability score
- Technical debt ratio = remediation time / implementation time
- **Lesson**: Single composite score with drill-down capability
- Source: [codeclimate.com](https://codeclimate.com/quality)

### 7.5 Allure Report
- Rich HTML test reports with charts and timelines
- Pie charts, bar graphs, trend analysis, categories
- **Lesson**: Self-contained HTML reports with CDN-loaded JS are effective and shareable
- Source: [allurereport.org](https://allurereport.org/)

---

## 8. Key Design Decisions

### 8.1 Structured Output from Agents

**Decision**: Modify each agent to output a JSON summary alongside their markdown report.

**Rationale**: Parsing markdown with regex is fragile. A structured JSON output ensures reliable data extraction for visualization. The markdown report remains the human-readable artifact.

**Implementation**: Add a JSON output section to each agent's workflow:
```markdown
<!-- JSON_DATA_START -->
```json
{ "grade": "B", "total_issues": 23, ... }
```
<!-- JSON_DATA_END -->
```

Alternatively, agents write a separate `{agent-name}-data.json` file.

### 8.2 Normalized Scoring (0-10 Scale)

**Decision**: Normalize all agent scores to a 0-10 scale for the master radar chart.

| Agent | Raw Score | Normalization Formula |
|---|---|---|
| code-smell-detector | Grade A-F | A=10, B=8, C=6, D=4, F=2 |
| test-design-reviewer | Farley 0-10 | Direct (already 0-10) |
| cognitive-load-analyzer | CLI 0-1000 | `10 - (score/100)`, clamped to [0,10] |
| ddd-architect | Qualitative | LLM-assessed 0-10 or derived from anti-pattern count |
| legacy-code-expert | Qualitative | LLM-assessed 0-10 or derived from risk factors |
| refactoring-expert | Count-based | `max(0, 10 - count/threshold)` |

### 8.3 Single-File HTML Report

**Decision**: Generate a single, self-contained HTML file (CDN-loaded JS).

**Rationale**:
- Easy to share (email, Slack, Git)
- No server needed
- CDN libraries (~500KB total) load fast
- For offline use, libraries can be inlined (adds ~3MB)

### 8.4 Overall Health Score Calculation

**Decision**: Weighted average of normalized dimension scores.

```
health_score = (
    code_quality * 0.20 +
    test_design * 0.20 +
    cognitive_load * 0.20 +
    ddd_compliance * 0.15 +
    legacy_safety * 0.15 +
    refactoring_debt * 0.10
) * 10  // Scale to 0-100
```

Weights reflect that code quality, test quality, and cognitive load are the most universally applicable dimensions.

---

## 9. Implementation Roadmap

### Phase 1: Foundation (MVP)
1. Create a Claude Code orchestrator agent (`codebase-analyzer-agent`)
2. Run 3 agents that produce structured output: `test-design-reviewer`, `cognitive-load-analyzer`, `alf-code-smell-detector`
3. Build minimal Jinja2 HTML template with:
   - 3 gauge charts (one per agent score)
   - 1 radar chart (3 axes)
   - Data tables for top issues
4. Generate single HTML file

### Phase 2: Full Agent Integration
5. Integrate remaining agents: `alf-ddd-architect`, `alf-legacy-code-expert`, `alf-refactoring-expert`
6. Add JSON output capability to all agents (or build parser/normalizer)
7. Expand radar to 6 axes
8. Add per-dimension detail sections

### Phase 3: Rich Visualizations
9. Add D3.js treemap for file-level complexity heatmap
10. Add Mermaid bounded context diagrams
11. Add scatter plots for refactoring priority quadrant
12. Add heatmaps for cross-dimensional analysis
13. Add file-level drill-down

### Phase 4: Polish and Distribution
14. CLI wrapper for easy invocation
15. Configuration file for customizing weights/thresholds
16. Dark mode / print-friendly mode
17. Historical comparison (diff two reports)
18. CI/CD integration (exit code based on health threshold)

---

## 10. Risk Assessment

| Risk | Impact | Mitigation |
|---|---|---|
| Agent output format is unstable/inconsistent | High | Define JSON contract, add validation |
| Agent execution time is long (minutes per agent) | Medium | Parallelize independent agents, add progress indicators |
| CDN unavailability for offline use | Low | Option to inline JS libraries |
| Markdown parsing is fragile | High | Prefer JSON output from agents |
| Score normalization is subjective | Medium | Document methodology, allow weight customization |
| DDD/Legacy agents lack numeric scores | Medium | Use LLM to extract/assign scores, or add scoring to agents |

---

## 11. Sources

### Code Quality Tools and Metrics
- [SonarQube Metric Definitions](https://docs.sonarsource.com/sonarqube-server/10.8/user-guide/code-metrics/metrics-definition)
- [12 Code Quality Metrics Every Dev Team Should Track](https://www.augmentcode.com/guides/12-code-quality-metrics-every-dev-team-should-track)
- [Code Climate Quality](https://codeclimate.com/quality)
- [10 Best Code Analysis Tools 2026](https://www.qodo.ai/blog/code-analysis-tools/)

### Visualization Libraries
- [D3.js](https://d3js.org/) - Data-Driven Documents
- [D3 Graph Gallery](https://d3-graph-gallery.com/) - Heatmaps, histograms, pie charts
- [Chart.js](https://www.chartjs.org/) - Simple yet flexible JS charting
- [Mermaid Radar Diagram](https://mermaid.ai/open-source/syntax/radar.html)
- [JSCharting Heatmap](https://jscharting.com/examples/chart-types/heatmap/)

### Codebase Visualization Tools
- [CodeCharta](https://codecharta.com/) - 3D code maps
- [CodeCharta GitHub](https://github.com/MaibornWolff/codecharta)
- [NDepend Treemap Visualization](https://www.ndepend.com/docs/treemap-visualization-of-code-metrics)
- [Allure Report](https://allurereport.org/) - Interactive test reports

### Report Generation
- [Jinja2 for Data Visualization](https://www.geeksforgeeks.org/data-visualization/how-to-use-jinja-for-data-visualization/)
- [Jinchart - Jinja2 Chart.js Filters](https://github.com/Winnetou/jinchart)
- [Plotly Interactive HTML Export](https://plotly.com/python/interactive-html-export/)
- [Chartkick.py](https://chartkick.com/python)
- [Generate HTML Reports with Python, Pandas, and Plotly](https://moderndata.plotly.com/generate-html-reports-with-python-pandas-and-plotly/)

### Radar Charts
- [Radar Chart Wikipedia](https://en.wikipedia.org/wiki/Radar_chart)
- [Radar Chart Explained - Highcharts](https://www.highcharts.com/blog/tutorials/radar-chart-explained-when-they-work-when-they-fail-and-how-to-use-them-right/)

### Treemaps for Code
- [Softvis Collection - Metrics Treemaps](http://www.softviscollection.org/vis/metrics-treemap/)
- [Treemaps as Tool to Visualize Software Projects](https://rizwaniqbal.com/posts/treemap/)
