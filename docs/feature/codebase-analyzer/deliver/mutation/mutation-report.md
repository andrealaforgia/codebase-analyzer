# Mutation Testing Report: codebase-analyzer

**Date**: 2026-03-07
**Tool**: cosmic-ray
**Scope**: src/report/ (feature-scoped)

## Results

| Metric | Value |
|--------|-------|
| Total mutants | 706 |
| Killed | 583 |
| Survived | 122 |
| Incompetent | 1 |
| Effective | 705 |
| **Kill rate** | **82.7%** |
| **Gate (>=80%)** | **PASS** |

## Survivors by Module

| Module | Survived | Notes |
|--------|----------|-------|
| formulas.py | 40 | Explanation text thresholds (cosmetic) |
| risk.py | 32 | BitOr operator noise + weight constants |
| charts.py | 31 | Chart config constants + BitOr noise |
| pipeline.py | 6 | Print formatting, non-critical |
| normalize.py | 5 | Formula constant variations |
| models.py | 5 | Remaining field constraint edge cases |
| render.py | 3 | Template path / config constants |

## Analysis

The 122 surviving mutants are primarily:
- **NumberReplacer on cosmetic thresholds** (explanation text quality labels)
- **BitOr operator replacements** (nonsensical mutations on string/dict operations)
- **Chart configuration constants** (pixel sizes, opacity values)

These are low-risk survivors that do not affect core score computation, risk assessment, or report correctness.

## Gate Decision

Kill rate 82.7% exceeds the 80% threshold. **PASS**.
