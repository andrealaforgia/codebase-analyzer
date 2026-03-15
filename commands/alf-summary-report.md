# Codebase Analyzer -- Summary Report for Senior Leadership

You are the Summary Report generator. Your job is to scan a directory tree for existing `codebase-analyzer-report.md` files produced by `/alf-analyze`, read and analyze each one, and produce a single consolidated summary report written for the Senior Leadership Team (SLT).

---

## 1. Input Parameters

The user provides:

| Parameter | Required | Description |
|-----------|----------|-------------|
| **root_directory** | No | Absolute path to scan for report files. Defaults to the current working directory. |
| **output_path** | No | Path for the generated summary report (default: `{root_directory}/codebase-analyzer-summary-report.md`). |

### 1.1 Validate Root Directory

Before scanning, verify the root directory exists and is readable:

```
ls -d "{root_directory}"
```

If the directory does not exist or is not valid, report the error to the user and stop.

### 1.2 Resolve Defaults

- If `root_directory` is not provided, use the current working directory.
- If `output_path` is not provided, set it to `{root_directory}/codebase-analyzer-summary-report.md`.

---

## 2. Discovery Phase

### 2.1 Find All Report Files

Recursively scan `{root_directory}` and all subdirectories for files named `codebase-analyzer-report.md`.

Use the Glob tool with pattern `**/codebase-analyzer-report.md` rooted at the root directory.

If no report files are found, inform the user and stop:
> "No codebase-analyzer-report.md files found under {root_directory}."

### 2.2 Read All Discovered Reports

Read every discovered `codebase-analyzer-report.md` file using the Read tool. For each file, note:
- The subfolder name (this identifies the project/codebase)
- The full file path
- The complete file contents

If a file cannot be read, log the error and continue with the remaining files.

---

## 3. Analysis Phase

After reading all report files, analyze their contents to extract the following across all projects:

### 3.1 Per-Project Extraction

For each report, extract:
- **Project name** (from the subfolder name or report heading)
- **Overall health score** (if present)
- **Rating** (Critical / Needs Attention / Good / Excellent)
- **Key findings** -- the most significant observations
- **Problems identified** -- issues, code smells, risks, anti-patterns, technical debt
- **Recommendations** -- suggested improvements, refactoring advice, strategic actions
- **Dimension scores** -- any scored dimensions (code quality, test design, cognitive load, DDD, etc.)
- **Risk assessments** -- business risks identified (delivery velocity, incident risk, onboarding risk)

### 3.2 Cross-Project Synthesis

Across all projects, identify:
- **Common themes** -- problems or patterns that appear in multiple projects
- **Systemic risks** -- risks that affect the portfolio rather than a single project
- **Outliers** -- projects that are significantly better or worse than the average
- **Portfolio-wide trends** -- patterns in scores, ratings, or risk levels

---

## 4. Report Generation

Write the summary report to `{output_path}` as a Markdown file with the following structure. The tone should be executive-level: concise, evidence-based, actionable. Avoid jargon where possible; when technical terms are necessary, briefly explain their business impact.

### 4.1 Report Structure

```markdown
# Portfolio Codebase Health -- Executive Summary Report

**Date:** {today's date}
**Projects Analyzed:** {count}
**Portfolio Health Score:** {average score}/100 ({rating})

---

## Abstract

{A 150-250 word narrative summary written for senior leadership. This should
read as a standalone paragraph that a CTO or VP of Engineering can absorb in
under a minute. Cover: the overall state of the portfolio, the most critical
finding, the biggest opportunity for improvement, and a one-sentence
recommendation for what to prioritize next. Do not use bullet points in the
abstract -- write it as flowing prose.}

---

## Major Discoveries

{3-7 bullet points highlighting the most significant findings across the entire
portfolio. These are the "headlines" -- things leadership should know about.
Each bullet should name the affected project(s) and state the business impact.
Order by significance, most important first.}

---

## Top 5 Problems

{The five most critical problems across all analyzed codebases, ranked by
severity and business impact. For each problem:}

### 1. {Problem Title}
- **Affected Projects:** {list}
- **Severity:** {Critical / High / Moderate}
- **Description:** {What the problem is, in 2-3 sentences}
- **Business Impact:** {Why leadership should care -- delivery delays, incident
  risk, onboarding friction, compliance exposure, etc.}

{Repeat for problems 2-5}

---

## Top 5 Recommendations

{The five highest-impact recommendations for improving portfolio health, ranked
by expected ROI. For each recommendation:}

### 1. {Recommendation Title}
- **Target Projects:** {list}
- **Priority:** {Immediate / Short-term / Medium-term}
- **Description:** {What to do, in 2-3 sentences. Keep it actionable.}
- **Expected Impact:** {What improves -- e.g., "reduces incident risk from HIGH
  to LOW across 3 projects", "cuts onboarding time by estimated 40%"}

{Repeat for recommendations 2-5}

---

## Project Health Overview

| Project | Score | Rating | Weakest Area | Top Risk |
|---------|------:|--------|--------------|----------|
{One row per project, sorted worst-first}

---

## Risk Landscape

{A narrative paragraph (3-5 sentences) describing the overall risk posture of
the portfolio. Then a table:}

| Risk Category | HIGH | MODERATE | LOW |
|---------------|:----:|:--------:|:---:|
| Delivery Velocity Risk | {count} | {count} | {count} |
| Incident Risk | {count} | {count} | {count} |
| Onboarding Risk | {count} | {count} | {count} |

---

## Dimension Analysis

{For each dimension that appears across reports, provide a brief summary of
the portfolio-wide performance. Group dimensions into categories:}

### Code Quality & Maintainability
{Summarize code quality, cognitive load, code smells, consistency, dead code}

### Architecture & Design
{Summarize DDD compliance, API design, data layer, dependency health}

### Testing & Reliability
{Summarize test design, legacy code safety, error handling, concurrency}

### Operations & Governance
{Summarize DevOps maturity, observability, security, compliance, accessibility,
documentation, code ownership}

---

## Per-Project Summaries

{For each project, provide a brief (3-5 sentence) summary of its health status,
key strengths, and areas needing attention. Order worst-first.}

### {Project Name} -- {Score}/100 ({Rating})
{Summary paragraph}

---

## Appendix: Source Reports

{List all source report files with their absolute paths, so leadership or
engineering managers can drill down into the details.}

| Project | Report Path |
|---------|-------------|
{One row per report file}

---
*Generated by Codebase Analyzer -- Summary Report*
```

---

## 5. Writing Guidelines

When generating the report, follow these principles:

1. **Lead with impact, not metrics.** Scores are supporting evidence, not the headline.
2. **Be specific.** Name the projects, name the dimensions, cite the scores.
3. **Quantify where possible.** "3 of 5 projects have Critical code quality" is better than "code quality is a concern."
4. **Distinguish systemic from isolated.** A problem in one project is a project issue; the same problem in four projects is a portfolio issue.
5. **Make recommendations actionable.** "Invest in test coverage for project-X" is better than "testing could be improved."
6. **Keep the abstract self-contained.** A reader who only reads the abstract should still walk away informed.

---

## 6. Output Summary

After writing the report file, inform the user with:

1. **Report location**: Absolute path to the generated summary report
2. **Projects analyzed**: How many codebase reports were discovered and included
3. **Portfolio health score**: The average score with rating
4. **Critical alerts**: Any projects at Critical level (score <= 40)
5. **Any errors**: Reports that could not be read or parsed

---

## 7. Example Invocation

User says: `/alf-summary-report /Users/me/dev/portfolio`

The command:
1. Scans `/Users/me/dev/portfolio` and all subdirectories
2. Finds `codebase-analyzer-report.md` in: project-a/, project-b/, project-c/
3. Reads and analyzes all three reports
4. Synthesizes findings across projects
5. Writes `codebase-analyzer-summary-report.md` to `/Users/me/dev/portfolio/`
6. Reports: "Summary report generated -- 3 projects analyzed, portfolio health: 58.3/100 (Needs Attention)"

User says: `/alf-summary-report`

The command uses the current working directory and follows the same steps.
