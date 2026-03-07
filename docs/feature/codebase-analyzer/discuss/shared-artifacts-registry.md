# Shared Artifacts Registry: Codebase Analyzer

## Purpose

This registry tracks every data value that appears in multiple places across the codebase analyzer journey. Each artifact has a single source of truth and documented consumers. Inconsistency in any artifact is a defect.

---

## Artifact Registry

### project_name

| Property | Value |
|---|---|
| Source of truth | CLI `--project-name` argument, or directory basename if not provided |
| Owner | CLI entrypoint |
| Integration risk | HIGH -- appears in client-facing report header |
| Consumers | CLI launch confirmation, Report HTML `<title>` tag, Report header section, Progress display during execution |
| Validation | Assert project_name in CLI output matches report header matches HTML title |

### target_dir

| Property | Value |
|---|---|
| Source of truth | CLI positional argument (first arg) |
| Owner | CLI entrypoint |
| Integration risk | HIGH -- wrong directory means wrong codebase analyzed |
| Consumers | CLI launch confirmation, Agent invocation (each agent receives this path), Report metadata section |
| Validation | Assert directory exists and contains source files before agent launch |

### output_path

| Property | Value |
|---|---|
| Source of truth | CLI `--output` argument, or default `"./{project_name}-report.html"` |
| Owner | CLI entrypoint |
| Integration risk | MEDIUM -- file must be writable and path must match what user expects |
| Consumers | CLI launch confirmation, CLI completion message ("Report saved to: ..."), File system write target |
| Validation | Assert CLI completion message path matches actual file location |

### file_count

| Property | Value |
|---|---|
| Source of truth | Filesystem scan of target_dir (source files only) |
| Owner | CLI entrypoint (pre-analysis scan) |
| Integration risk | LOW -- informational, not used in scoring |
| Consumers | CLI launch confirmation, Report metadata section |
| Validation | Count shown at launch matches count in report metadata |

### primary_language

| Property | Value |
|---|---|
| Source of truth | File extension analysis of target_dir |
| Owner | CLI entrypoint (pre-analysis scan) |
| Integration risk | LOW -- informational, not used in scoring |
| Consumers | CLI launch confirmation, Report metadata section |
| Validation | Language shown at launch matches language in report metadata |

### agent_results (per agent)

| Property | Value |
|---|---|
| Source of truth | Each agent's structured JSON output file |
| Owner | Orchestrator (collects from each agent) |
| Integration risk | HIGH -- raw data feeds all downstream scoring and visualization |
| Consumers | Progress display (preview scores), Result normalizer, Report generator (all chart data), Score derivation panels |
| Validation | Raw data in score derivation panel matches actual agent JSON output. Normalized scores derive correctly from raw data using documented formula. |

### dimension_scores (normalized, per dimension)

| Property | Value |
|---|---|
| Source of truth | Result normalizer (applies documented formula to agent_results) |
| Owner | Result normalizer component |
| Integration risk | HIGH -- these are the numbers Andrea must defend to clients |
| Consumers | CLI completion summary, Executive summary dimension bars, Master radar chart, Per-dimension detail sections, Overall score calculation, Business risk calculation |
| Validation | Score in executive summary matches score in dimension detail matches score on radar chart. Score derivation panel reproduces the same value from raw data + formula. |

### overall_score

| Property | Value |
|---|---|
| Source of truth | Weighted average formula applied to dimension_scores |
| Owner | Result normalizer component |
| Integration risk | HIGH -- the single number clients see first |
| Consumers | CLI completion summary, Report executive summary header, Overall health gauge visualization |
| Validation | overall_score = weighted_sum(dimension_scores) * 10. Verify formula documented in report methodology section produces same result. |

### overall_rating

| Property | Value |
|---|---|
| Source of truth | Rating derived from overall_score thresholds |
| Owner | Result normalizer component |
| Integration risk | HIGH -- plain-language label that frames first impression |
| Consumers | CLI completion summary, Report executive summary header |
| Validation | Rating matches documented threshold table (e.g., 0-40 = Critical, 41-60 = Needs Attention, 61-80 = Good, 81-100 = Excellent) |

### business_risk_assessments

| Property | Value |
|---|---|
| Source of truth | Risk model applied to dimension_scores |
| Owner | Report generator (risk derivation logic) |
| Integration risk | HIGH -- business-facing language clients act on |
| Consumers | Executive summary business risk section, Per-risk detail panels |
| Validation | Each risk level is derivable from its contributing dimension scores using documented risk model. No risk rating contradicts its underlying dimensions. |

### normalization_formulas (per dimension)

| Property | Value |
|---|---|
| Source of truth | Documented formula per dimension in report methodology section |
| Owner | Result normalizer component (code) + Report template (display) |
| Integration risk | HIGH -- if code and displayed formula diverge, trust is destroyed |
| Consumers | Score derivation panels in report, Report methodology/appendix section |
| Validation | Formula shown in score derivation panel is identical to formula in code. Applying displayed formula to displayed raw data produces displayed score. |

---

## Integration Checkpoints

### Checkpoint 1: Launch Confirmation Accuracy

**When**: After CLI displays project metadata, before user confirms

**Validates**:
- project_name matches --project-name argument or directory basename
- target_dir exists and contains source files
- file_count matches actual filesystem scan
- primary_language matches extension analysis
- output_path is writable

**Failure mode**: User launches analysis on wrong directory, wastes 10+ minutes

### Checkpoint 2: Agent Result Integrity

**When**: After each agent completes, before results are consumed

**Validates**:
- Agent produced valid structured JSON output
- Required fields are present in agent output
- Score values are within expected ranges

**Failure mode**: Malformed agent output causes incorrect normalization or report rendering errors

### Checkpoint 3: Score Consistency Across Report

**When**: After report generation, before report is opened

**Validates**:
- CLI summary scores match report scores
- Executive summary scores match dimension detail scores
- Radar chart data points match displayed score values
- Score derivation panels reproduce scores from raw data + formula

**Failure mode**: Inconsistent scores between report sections destroy credibility during client presentation

### Checkpoint 4: Business Risk Derivability

**When**: After report generation

**Validates**:
- Each business risk level is consistent with contributing dimension scores
- Risk model is documented and the documented model produces the displayed ratings
- No risk is rated LOW when contributing dimensions are scored below 5/10

**Failure mode**: Client technical team independently examines scores and finds risk rating is not supported by underlying data
