# ADR-002: Score Normalization Strategy -- Unified 0-10 Scale

## Status
Accepted

## Context

Six agents produce scores in different formats:
- Code smell detector: letter grade A-F
- Test design reviewer: Farley Index 0-10
- Cognitive load analyzer: CLI Score 0-1000 (higher = worse)
- DDD architect: qualitative assessment (no numeric score)
- Legacy code expert: qualitative assessment (no numeric score)
- Refactoring expert: recommendation count with risk levels

The report needs a unified scale for the master radar chart, overall health score, and cross-dimension comparison. Every normalized score must be transparent and reproducible.

## Decision

Normalize all scores to a **0-10 scale** (higher = better) using per-dimension formulas. For agents without numeric output (DDD, legacy), require the agent itself to produce a 0-10 self-assessment score in its JSON output, guided by a scoring rubric embedded in the agent prompt.

### Formulas

| Agent | Formula |
|-------|---------|
| code-smell-detector | Lookup: `{A:10, B:8, C:6, D:4, F:2}` |
| test-design-reviewer | Direct passthrough (already 0-10) |
| cognitive-load-analyzer | `max(0, min(10, 10 - cli_score / 100))` |
| ddd-architect | Agent self-assessed 0-10 (rubric in prompt) |
| legacy-code-expert | Agent self-assessed 0-10 (rubric in prompt) |
| refactoring-expert | `max(0, 10 - weighted_count / threshold)` where weighted_count = `high*3 + medium*2 + low*1`, threshold = 10 |

## Alternatives Considered

### Alternative 1: Percentile-based normalization (0-100)
- **What**: All scores normalized to 0-100 using statistical percentile mapping
- **Expected impact**: Finer granularity, familiar percentage scale
- **Why rejected**: Requires a reference distribution (what is the 50th percentile for code smells?). With no benchmark dataset, percentiles would be arbitrary. 0-10 is sufficient for radar charts and risk thresholds. Simpler is better for transparency.

### Alternative 2: LLM-based normalization for all agents
- **What**: A normalization agent reads all markdown reports and assigns 0-10 scores
- **Expected impact**: Handles qualitative agents naturally
- **Why rejected**: Non-deterministic. Running the same analysis twice could produce different scores. Violates the reproducibility requirement (US-05). Andrea cannot defend a score that changes between runs.

### Alternative 3: Skip normalization -- show raw scores only
- **What**: Display each agent's native score format without normalization
- **Expected impact**: Maximum accuracy per dimension
- **Why rejected**: Cannot produce a unified radar chart or overall health score. Cannot compare dimensions. The executive summary requires cross-dimension comparison.

## Consequences

- **Positive**: Every score is reproducible from raw data + formula. Andrea can defend any number.
- **Positive**: Radar chart and overall score are mathematically derived, not LLM-guessed.
- **Negative**: DDD and legacy scores involve agent self-assessment (LLM judgment), which is less deterministic than formula-based normalization. Mitigated by embedding a detailed scoring rubric in the agent prompt.
- **Negative**: Grade-to-numeric mapping for smell detector is a design choice (why B=8, not B=7?). Must be documented in methodology section.
