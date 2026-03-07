# JTBD Analysis: Codebase Analyzer

## Context

Andrea is a software consultant who evaluates client codebases for quality, risk, and improvement opportunities. The analysis results are presented to client leadership (non-technical executives) who make budget, staffing, and strategic decisions based on the findings.

---

## Job Statements

### Primary Job

**Help me produce undeniable, evidence-based assessments of codebase quality that client leadership cannot dismiss or minimize.**

### Supporting Jobs

1. Help me automate the tedious process of running and synthesizing multiple analysis agents.
2. Help me translate technical quality metrics into business risk language that executives understand.
3. Help me deliver a professional, reusable analysis asset I can deploy across many client engagements.

---

## Job Stories

### JS-01: Comprehensive Codebase Assessment

**When** I have been hired by a client to evaluate their codebase and need to present findings to their leadership,
**I want to** run a comprehensive, multi-dimensional analysis and produce a visual report that makes quality issues undeniable,
**so I can** deliver findings that leadership cannot minimize or deny, driving them to act on technical debt and risk.

#### Functional Job
Orchestrate 6 specialized analysis agents against a client codebase, normalize their diverse outputs into a unified scoring model, and generate a professional visual report.

#### Emotional Job
Feel confident and authoritative when presenting findings. Feel that the evidence is so clear and well-presented that it speaks for itself -- no amount of client pushback can undermine the data.

#### Social Job
Be perceived by client leadership as a credible, thorough, data-driven consultant whose assessments carry weight. Build a reputation for producing reports that are impossible to ignore.

---

### JS-02: Executive Communication of Technical Risk

**When** I am walking client leadership through codebase findings and they are not deeply technical,
**I want to** present technical quality issues as business risks with clear visual indicators,
**so I can** bridge the gap between engineering metrics and executive decision-making without losing credibility with either audience.

#### Functional Job
Translate code smells, cognitive load scores, test quality indices, DDD compliance, legacy risk, and refactoring debt into business-relevant risk categories (velocity impact, incident likelihood, onboarding cost, bus factor).

#### Emotional Job
Feel equipped rather than anxious when a CTO pushes back with "our code is fine." The report should be the shield -- the data is incontrovertible.

#### Social Job
Be seen as someone who speaks both engineering and business fluently. Client leadership trusts the analysis because it connects to outcomes they care about (cost, time-to-market, risk of outages).

---

### JS-03: Repeatable Consulting Asset

**When** I have multiple client engagements requiring codebase evaluation,
**I want to** run the analysis tool against any codebase and get a consistent, professional report without manual synthesis,
**so I can** scale my consulting practice without the tedium of manually running agents and assembling findings.

#### Functional Job
Point the tool at a codebase directory, select which agents to run, and receive a polished HTML report ready for client presentation -- with no manual report assembly.

#### Emotional Job
Feel efficient and professional. The tedium of manual synthesis was draining -- automation should free mental energy for interpretation and recommendations.

#### Social Job
Clients see a branded, professional report -- not a cobbled-together collection of markdown files. The polish signals competence and investment in quality.

---

### JS-04: Overcoming Client Denial

**When** I present findings and the client leadership minimizes problems or denies issues exist,
**I want to** point to specific, visualized evidence with severity ratings and business impact annotations,
**so I can** make the findings undeniable and shift the conversation from "is there a problem?" to "what do we do about it?"

#### Functional Job
Provide drill-down capability from summary scores to specific file-level findings with severity, evidence, and recommended actions. Each claim in the report must be traceable to concrete data.

#### Emotional Job
Feel empowered in difficult conversations. When a VP says "our engineering team says the code is fine," the report should make avoidance untenable.

#### Social Job
Be perceived as fair but thorough -- not alarmist. The report presents evidence, not opinions. Leadership respects the methodology because it is systematic and reproducible.

---

## Four Forces Analysis

### Force 1: Push of Current Situation (Strong)

- Running 6 agents manually one by one is tedious and time-consuming
- Manually synthesizing markdown reports from diverse agents into coherent findings is error-prone
- Clients have historically minimized or denied problems when presented with raw agent output
- Current process does not scale -- each new client engagement requires the same manual work
- Raw technical output does not resonate with executive audiences

### Force 2: Pull of New Solution (Strong)

- Single command produces a comprehensive, visual, professional report
- Visualizations make quality issues immediately apparent -- "the radar chart has a dent"
- Business risk framing connects to decisions executives actually make
- Reusable across many clients without re-doing manual work
- Dual-layer report (executive summary + technical deep-dive) serves both audiences in one artifact

### Force 3: Anxiety of New Solution (Moderate)

- **Primary anxiety**: Scores and visualizations might be ambiguous or misleading
- Normalized scores might not accurately represent the severity of issues
- A misleading visualization could undermine credibility if the client's technical team challenges it
- Over-simplification of complex quality dimensions might lose nuance
- If the tool produces a "green" report for a codebase with real problems, trust is destroyed

### Force 4: Habit of Present (Low)

- The manual process, while tedious, gives full control over interpretation
- Andrea understands the raw agent outputs and can manually calibrate emphasis
- Existing workflow is proven -- it works, just slowly
- No relearning cost with the manual approach

### Force Balance Assessment

| Force | Strength | Signal |
|-------|----------|--------|
| Push | Strong | "Very tedious," manual synthesis, client denial pattern |
| Pull | Strong | Professional reports, undeniable evidence, scale across clients |
| Anxiety | Moderate | Misleading scores/visualizations could destroy credibility |
| Habit | Low | Manual process works but does not scale |

**Switch likelihood**: High. Push + Pull strongly exceed Anxiety + Habit.

**Key blocker**: Anxiety about misleading representations. The tool must never produce a score that a knowledgeable technical person could credibly challenge as inaccurate.

**Key enabler**: The tedium of manual synthesis combined with the pattern of client denial. The tool solves both simultaneously.

**Design implication**: Every score must be transparent in its derivation. The report must show how each normalized score was calculated from raw data, so Andrea can defend any number. "Where does this 6.8 come from?" must always have a clear, traceable answer.

---

## 8-Step Universal Job Map

### 1. Define -- Determine goals, plan approach

Andrea receives a client engagement. She needs to determine: Which codebase? Which agents are relevant? What is the client most concerned about?

**Outcome**: "Minimize the time to determine which analysis dimensions are relevant for this client."

### 2. Locate -- Gather necessary inputs

Andrea needs access to the client's codebase (git clone or local copy). She needs the agents installed and configured. She needs to understand the codebase's primary language and framework.

**Outcome**: "Minimize the likelihood of running analysis on an incomplete or incorrect codebase snapshot."

### 3. Prepare -- Set up environment

Andrea navigates to the codebase directory. She configures any tool options (which agents, output path, project name for the report header).

**Outcome**: "Minimize the time to configure and launch the analysis."

### 4. Confirm -- Verify readiness

Before running (potentially long) analysis, Andrea confirms: correct directory, correct agents selected, output path writable.

**Outcome**: "Minimize the likelihood of wasting a long analysis run on misconfigured inputs."

### 5. Execute -- Perform the core task

The tool orchestrates 6 agents, collects results, normalizes scores, generates the HTML report. This takes minutes to tens of minutes depending on codebase size.

**Outcome**: "Minimize the time to complete the full multi-agent analysis."

### 6. Monitor -- Check progress

During execution, Andrea needs to know: Which agent is running? Is it progressing or stuck? How long until completion?

**Outcome**: "Minimize the likelihood of an undetected agent failure wasting the entire analysis run."

### 7. Modify -- Handle exceptions

An agent fails or produces unexpected output. Andrea needs to understand what went wrong and either re-run that agent or proceed with partial results.

**Outcome**: "Minimize the time to recover from a single agent failure without losing other agents' results."

### 8. Conclude -- Finalize and assess

The report is generated. Andrea opens it, reviews the executive summary, checks that scores make sense, verifies the visualizations communicate clearly. She may annotate or customize before presenting to the client.

**Outcome**: "Minimize the likelihood of presenting a report with misleading or indefensible scores."

---

## Opportunity Scoring

Scoring based on Andrea's described pain points and priorities. Importance/satisfaction estimated from interview responses (single-stakeholder, team-estimate confidence level).

| # | Outcome Statement | Imp. | Sat. | Score | Priority |
|---|---|---|---|---|---|
| 1 | Minimize the likelihood of presenting misleading or ambiguous quality scores | 95% | 20% | 17.0 | Extremely Underserved |
| 2 | Minimize the time to synthesize multiple agent outputs into a unified report | 90% | 15% | 16.5 | Extremely Underserved |
| 3 | Minimize the likelihood that client leadership can dismiss or minimize findings | 90% | 25% | 15.5 | Extremely Underserved |
| 4 | Minimize the time to translate technical metrics into business risk language | 85% | 20% | 14.5 | Underserved |
| 5 | Minimize the time to configure and launch analysis on a new client codebase | 80% | 30% | 12.0 | Appropriately Served |
| 6 | Minimize the likelihood of an undetected agent failure wasting the run | 75% | 25% | 12.5 | Underserved |
| 7 | Minimize the time to recover from a single agent failure | 70% | 30% | 11.0 | Appropriately Served |
| 8 | Minimize the time to determine which agents are relevant per client | 60% | 40% | 8.0 | Overserved |

### Top Opportunities (Score >= 12)

1. **Score clarity and defensibility** (17.0) -- Every score must be transparent, traceable, unambiguous
2. **Automated multi-agent synthesis** (16.5) -- Eliminate manual report assembly entirely
3. **Undeniable evidence presentation** (15.5) -- Visualizations that make denial impossible
4. **Business risk translation** (14.5) -- Bridge from technical metrics to executive decisions
5. **Agent failure resilience** (12.5) -- Graceful handling of partial results
6. **Quick launch on new codebase** (12.0) -- Minimal configuration for repeat use

### Data Quality Notes

- Source: single-stakeholder interview (Andrea)
- Sample size: 1 (primary user and buyer)
- Confidence: Medium (single stakeholder but deeply understood use case)
- Recommendation: treat scores as relative rankings, not absolutes

---

## Persona

### Andrea Laforgia -- Senior Software Consultant

**Role**: Independent/consulting software engineer who evaluates client codebases

**Context**: Hired by companies to assess codebase health. Delivers findings to client leadership (CTO, VP Engineering, CEO). Has deep technical expertise but must communicate to non-technical audiences.

**Key characteristics**:
- Technically expert -- understands all 6 analysis dimensions deeply
- Communication-oriented -- needs to translate technical findings to business impact
- Credibility-dependent -- reputation built on thorough, defensible assessments
- Efficiency-driven -- manual synthesis across clients is unsustainable
- Client-facing -- report is the primary deliverable, not just a tool for personal use

**Frustrations**:
- Manual agent orchestration is tedious and repetitive
- Raw markdown output does not convince executives
- Clients minimize or deny problems when evidence is not overwhelming
- Cannot scale consulting practice with manual process

**Goals**:
- Produce reports that make quality issues undeniable
- Present technical debt as business risk
- Scale across multiple client engagements
- Maintain credibility with both technical and executive audiences
