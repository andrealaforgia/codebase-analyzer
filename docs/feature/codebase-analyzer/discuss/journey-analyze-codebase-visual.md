# Journey: Analyze Client Codebase -- Visual Map

## Overview

**Goal**: Run multi-agent analysis on a client codebase, produce a professional HTML report, and present findings to client leadership.

**Persona**: Andrea Laforgia, Senior Software Consultant

**Emotional Arc**: Confident Setup --> Trusting Execution --> Critical Review --> Empowered Delivery

---

## Journey Flow

```
[Trigger]              [Step 1]           [Step 2]            [Step 3]
Client engagement  --> Configure &    --> Monitor agent   --> Review report
requires assessment    launch analysis    execution            & validate scores

Feels: Purposeful      Feels: Efficient   Feels: Informed     Feels: Critical,
                                                               then Satisfied
Artifacts: codebase    Artifacts: CLI     Artifacts:          Artifacts:
directory path,        command, agent     progress output,    report.html
project name           selection          agent status

                       [Step 4]            [Step 5]
                   --> Prepare for     --> Present to
                       client meeting      client leadership

                       Feels: Confident    Feels: Authoritative,
                                           Empowered
                       Artifacts:          Artifacts:
                       report.html,        report.html (live),
                       talking points      client decisions
```

---

## Step 1: Configure and Launch Analysis

### Emotional State
- **Entry**: Purposeful, efficient -- "I know what I need to do, let me get this running"
- **Exit**: Relieved -- "It is working, I can focus on other things while it runs"

### CLI Interaction

```
$ codebase-analyzer analyze /path/to/client-project \
    --project-name "Acme Corp Platform" \
    --output ./reports/acme-corp-2026-03.html

  Codebase Analyzer v1.0
  ─────────────────────────────────────────────
  Project:    Acme Corp Platform
  Target:     /path/to/client-project
  Files:      847 source files detected
  Language:   Java (primary), Python (secondary)
  Agents:     All 6 selected
  Output:     ./reports/acme-corp-2026-03.html
  ─────────────────────────────────────────────

  Confirm analysis? [Y/n] y

  Starting analysis...
```

### Key Design Notes

- Minimal required arguments: target directory only (sensible defaults for everything else)
- Auto-detection of project metadata (file count, primary language) gives immediate confidence that the tool is pointed at the right place
- Confirmation prompt prevents wasted runs on wrong directory
- Project name defaults to directory name but is overridable for client-facing reports

### Error Path

```
$ codebase-analyzer analyze /wrong/path

  Error: Directory not found: /wrong/path

  Did you mean one of these?
    /path/to/client-project
    /path/to/other-project

  Usage: codebase-analyzer analyze <target-dir> [options]
```

---

## Step 2: Monitor Agent Execution

### Emotional State
- **Entry**: Trusting -- "The tool is handling it"
- **Mid**: Engaged -- "I can see what each agent is finding"
- **Exit**: Anticipatory -- "Almost done, I want to see the results"

### CLI Interaction -- Progress View

```
  Analyzing Acme Corp Platform...
  ─────────────────────────────────────────────

  [1/6] Code Smell Detection        ████████████████████ done  (2m 14s)
        Grade: B | 23 issues found

  [2/6] Test Design Review           ████████████████████ done  (1m 48s)
        Farley Index: 7.2/10

  [3/6] Cognitive Load Analysis      ████████████████████ done  (3m 02s)
        CLI Score: 312/1000

  [4/6] DDD Architecture Review      ██████████░░░░░░░░░░ 52%   (est. 2m left)
        Analyzing bounded contexts...

  [5/6] Legacy Code Assessment       ░░░░░░░░░░░░░░░░░░░░ queued
  [6/6] Refactoring Analysis         ░░░░░░░░░░░░░░░░░░░░ queued (after #1)

  ─────────────────────────────────────────────
  Elapsed: 7m 04s | Estimated remaining: 6m
```

### Key Design Notes

- Each agent shows its primary score immediately upon completion -- builds anticipation and trust
- Running agent shows what it is currently doing -- transparency reduces anxiety
- Queued agents are visible with dependency note (agent 6 waits for agent 1)
- Time estimates set expectations for long runs on large codebases

### Error Path -- Agent Failure

```
  [4/6] DDD Architecture Review      ████████████████░░░░ FAILED (timeout)
        Error: Agent timed out after 10 minutes

  ─────────────────────────────────────────────
  Continue with remaining agents? [Y/n] y

  Note: DDD dimension will show "Not Available" in the report.
        Re-run with: codebase-analyzer analyze --retry-agent ddd ...
```

- Agent failure does not kill the entire run
- User can choose to continue with partial results
- Report clearly marks missing dimensions
- Retry command provided for targeted re-run

---

## Step 3: Review Report and Validate Scores

### Emotional State
- **Entry**: Critical, scrutinizing -- "Are these scores defensible? Can I stand behind every number?"
- **Mid**: Analytical -- "Let me trace this score back to the raw findings"
- **Exit**: Satisfied or concerned -- either "This accurately reflects the codebase" or "This score seems off, I need to investigate"

### Report -- Executive Summary Section

```
+================================================================+
|                                                                  |
|    CODEBASE HEALTH REPORT                                       |
|    Acme Corp Platform                                           |
|    Assessment Date: 2026-03-07                                  |
|    847 files | 62,400 LOC | Java/Python                        |
|                                                                  |
+================================================================+

+-- Overall Health -------------------------------------------------+
|                                                                    |
|    Overall Score: 58/100 (NEEDS ATTENTION)                        |
|                                                                    |
|         Code Quality     [====------]  6.0/10  (Grade B)         |
|         Test Design      [=======---]  7.2/10  (Good)            |
|         Cognitive Load   [=======---]  6.9/10  (Moderate)        |
|         DDD Compliance   [======----]  6.5/10  (Moderate)        |
|         Legacy Safety    [=====-----]  5.5/10  (Elevated Risk)   |
|         Refactoring Debt [===-------]  3.0/10  (Significant)     |
|                                                                    |
|    [6-axis radar chart showing the "shape" of codebase health]   |
|                                                                    |
|    KEY RISK: Refactoring debt is the weakest dimension.          |
|    The codebase has accumulated 14 high-priority refactoring      |
|    items that increase the cost and risk of future changes.       |
|                                                                    |
+--------------------------------------------------------------------+

+-- Business Risk Summary ------------------------------------------+
|                                                                    |
|    DELIVERY VELOCITY RISK:        HIGH                            |
|    Refactoring debt + cognitive load slow feature development.    |
|    Estimated velocity impact: 25-35% slower than healthy baseline |
|                                                                    |
|    INCIDENT RISK:                 MODERATE                        |
|    Legacy code with limited test coverage in critical paths.      |
|    23 code smells include 1 high-severity coupling issue.         |
|                                                                    |
|    ONBOARDING RISK:               MODERATE                        |
|    Cognitive Load Index of 312 means new developers face          |
|    significant ramp-up time (est. 3-4 weeks vs 1-2 weeks norm).  |
|                                                                    |
|    KEY PERSON DEPENDENCY RISK:    NOT ASSESSED                    |
|    (Requires team structure data beyond code analysis)            |
|                                                                    |
+--------------------------------------------------------------------+
```

### Score Transparency -- Every Number is Traceable

```
+-- Score Derivation: Refactoring Debt 3.0/10 ----------------------+
|                                                                     |
|    Raw Data:                                                        |
|      14 refactoring recommendations from alf-refactoring-expert    |
|      2 high-risk | 7 medium-risk | 5 low-risk                     |
|                                                                     |
|    Normalization:                                                   |
|      Formula: max(0, 10 - (weighted_count / threshold))           |
|      Weighted count: (2 x 3) + (7 x 2) + (5 x 1) = 25           |
|      Threshold: 10 (expected max for healthy codebase)             |
|      Score: max(0, 10 - 25/10 * 2.8) = 3.0                       |
|                                                                     |
|    What this means:                                                 |
|      The codebase has accumulated significantly more refactoring   |
|      debt than a healthy project. High-risk items affect core      |
|      business logic and will compound if not addressed.            |
|                                                                     |
|    [Link: View all 14 recommendations in detail section]           |
|                                                                     |
+---------------------------------------------------------------------+
```

### Key Design Notes

- Executive summary fits on one screen -- 2-minute scan for leadership
- Business risk framing uses language executives understand (velocity, incidents, onboarding, key person)
- Every score has a drill-down showing raw data, formula, and plain-language explanation
- "What this means" section translates numbers into consequences
- Score derivation is fully transparent so Andrea can defend any number

---

## Step 4: Prepare for Client Meeting

### Emotional State
- **Entry**: Confident -- "The report is solid, the data is clear"
- **Exit**: Ready -- "I know the story I want to tell with this data"

### Interaction

This step is human-driven -- Andrea reviews the report, identifies the 3-4 most important points for the meeting, and prepares her narrative. The tool supports this by providing:

- A printable executive summary (the report has a print-friendly CSS mode)
- Section anchors for quick navigation during screen-share
- Collapsible detail sections so she can progressively disclose complexity

### Key Design Notes

- Report must work as a standalone document (client explores after meeting)
- Report must work as a presentation aid (Andrea navigates during screen-share)
- Navigation must be fast -- clicking between sections, not scrolling through pages
- Print mode strips interactive elements for PDF/printout

---

## Step 5: Present to Client Leadership

### Emotional State
- **Entry**: Authoritative -- "I have the evidence to back every claim"
- **Peak tension**: Client pushback -- "Our engineers say the code is fine"
- **Resolution**: Empowered -- "Let me show you the specific findings"
- **Exit**: Satisfied -- "They cannot deny the data, the conversation has shifted to action"

### Interaction

Andrea screen-shares the report. She starts with the executive summary (overall score, radar chart, business risk summary). When leadership pushes back:

1. She clicks into the specific dimension being challenged
2. Shows the score derivation (raw data, formula, explanation)
3. Drills into specific file-level findings with evidence
4. The visual evidence (heatmaps, treemaps, charts) makes the issue tangible

### The "Denial-Proof" Design Pattern

```
Level 1: Executive Summary
  "Your codebase scores 58/100 -- Needs Attention"
  --> Client response: "That seems subjective"

Level 2: Dimension Breakdown
  "Refactoring debt scores 3/10 with 14 high-priority items"
  --> Client response: "14 items doesn't sound like a lot"

Level 3: Score Derivation
  "Here's exactly how 3/10 was calculated from the raw data"
  --> Client response: "But are these items really problems?"

Level 4: Specific Evidence
  "Here is the OrderProcessor class at 450 lines with
   cyclomatic complexity of 28 and 6 SOLID violations.
   This single file is responsible for 40% of your
   production incidents in the last quarter."
  --> Client: "...what do we do about it?"
```

Each drill-down level makes denial harder. By Level 4, the conversation has shifted from "is there a problem?" to "what do we do about it?" -- which is the goal.

---

## Emotional Arc Summary

```
Step 1           Step 2           Step 3           Step 4           Step 5
Configure        Monitor          Review           Prepare          Present

Purposeful  -->  Trusting    -->  Critical    -->  Confident   -->  Authoritative
Efficient        Anticipatory     Analytical       Ready            Empowered
                                  Satisfied

[=========================================================================]
Low anxiety                                                   Peak tension
High control     Medium control   High control     High control  (client pushback)
                                                                then Resolution
```

The emotional arc follows the **Confidence Building** pattern:
- Confidence builds progressively through Steps 1-4
- Step 5 has the peak tension point (client denial/pushback)
- The resolution is empowerment through undeniable evidence
- The tool's job is to ensure Andrea never feels exposed or unsupported during Step 5
