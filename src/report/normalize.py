"""Score normalization functions for agent data.

Each function transforms raw agent data (validated Pydantic model) into a
normalized DimensionScore on the 0-10 scale using documented formulas.

All functions are pure: no side effects, no I/O. Formula string generation
is delegated to formulas.py.

Dimension weights (from architecture):
    code_quality     = 0.20
    test_design      = 0.20
    cognitive_load   = 0.20
    ddd_compliance   = 0.15
    legacy_safety    = 0.15
    refactoring_debt = 0.10
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from src.report.formulas import (
    code_quality_explanation,
    code_quality_formula_display,
    cognitive_load_explanation,
    cognitive_load_formula_display,
    ddd_compliance_explanation,
    ddd_compliance_formula_display,
    legacy_safety_explanation,
    legacy_safety_formula_display,
    refactoring_debt_explanation,
    refactoring_debt_formula_display,
    test_design_explanation,
    test_design_formula_display,
)
from src.report.models import (
    CodeSmellDetectorData,
    CognitiveLoadAnalyzerData,
    DDDArchitectData,
    DimensionScore,
    LegacyCodeExpertData,
    RefactoringExpertData,
    TestDesignReviewerData,
)

# ---------------------------------------------------------------------------
# Grade-to-score mapping for code smell grades
# ---------------------------------------------------------------------------

_GRADE_SCORES: dict[str, float] = {
    "A": 10.0,
    "B": 8.0,
    "C": 6.0,
    "D": 4.0,
    "F": 2.0,
}


# ---------------------------------------------------------------------------
# Individual normalization functions
# ---------------------------------------------------------------------------


def normalize_code_quality(data: CodeSmellDetectorData) -> DimensionScore:
    """Normalize code smell grade to 0-10 score.

    Formula: grade mapping {A:10, B:8, C:6, D:4, F:2}.
    """
    score = _GRADE_SCORES[data.grade]
    return DimensionScore(
        name="code_quality",
        raw_score=score,
        normalized_score=score,
        weight=0.20,
        formula_display=code_quality_formula_display(data.grade, score),
        explanation=code_quality_explanation(data.grade),
    )


def normalize_test_design(data: TestDesignReviewerData) -> DimensionScore:
    """Normalize test design Farley Index to 0-10 score.

    Formula: direct passthrough of farley_index (already 0-10 scale).
    """
    score = data.farley_index
    return DimensionScore(
        name="test_design",
        raw_score=score,
        normalized_score=score,
        weight=0.20,
        formula_display=test_design_formula_display(score),
        explanation=test_design_explanation(score),
    )


def normalize_cognitive_load(data: CognitiveLoadAnalyzerData) -> DimensionScore:
    """Normalize cognitive load CLI score to 0-10 score.

    Formula: max(0, min(10, 10 - cli_score / 100)).
    Higher CLI score = more cognitive load = lower normalized score.
    """
    raw_score = float(data.cli_score)
    normalized = _clamp(10.0 - raw_score / 100.0)
    return DimensionScore(
        name="cognitive_load",
        raw_score=raw_score,
        normalized_score=normalized,
        weight=0.20,
        formula_display=cognitive_load_formula_display(data.cli_score, normalized),
        explanation=cognitive_load_explanation(data.cli_score, normalized),
    )


def normalize_ddd_compliance(data: DDDArchitectData) -> DimensionScore:
    """Normalize DDD compliance to 0-10 score.

    Formula: direct passthrough of overall_score (agent self-assessed).
    """
    score = data.overall_score
    return DimensionScore(
        name="ddd_compliance",
        raw_score=score,
        normalized_score=score,
        weight=0.15,
        formula_display=ddd_compliance_formula_display(score),
        explanation=ddd_compliance_explanation(score),
    )


def normalize_legacy_safety(data: LegacyCodeExpertData) -> DimensionScore:
    """Normalize legacy code safety to 0-10 score.

    Formula: direct passthrough of overall_score (agent self-assessed).
    """
    score = data.overall_score
    return DimensionScore(
        name="legacy_safety",
        raw_score=score,
        normalized_score=score,
        weight=0.15,
        formula_display=legacy_safety_formula_display(score),
        explanation=legacy_safety_explanation(score),
    )


def normalize_refactoring_debt(data: RefactoringExpertData) -> DimensionScore:
    """Normalize refactoring debt to 0-10 score.

    Formula: max(0, 10 - weighted_count / 5)
    where weighted_count = high*3 + medium*2 + low*1 from risk_distribution.
    Clamped to [0, 10].
    """
    high = data.risk_distribution.high
    medium = data.risk_distribution.medium
    low = data.risk_distribution.low
    weighted_count = high * 3 + medium * 2 + low * 1
    normalized = _clamp(10.0 - weighted_count / 5.0)
    return DimensionScore(
        name="refactoring_debt",
        raw_score=float(weighted_count),
        normalized_score=normalized,
        weight=0.10,
        formula_display=refactoring_debt_formula_display(
            high, medium, low, weighted_count, normalized,
        ),
        explanation=refactoring_debt_explanation(normalized),
    )


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

# Maps agent keys to their normalizer functions and expected data types
_NORMALIZERS: dict[str, tuple[type, Callable[..., DimensionScore]]] = {
    "code_smell_detector": (CodeSmellDetectorData, normalize_code_quality),
    "test_design_reviewer": (TestDesignReviewerData, normalize_test_design),
    "cognitive_load_analyzer": (CognitiveLoadAnalyzerData, normalize_cognitive_load),
    "ddd_architect": (DDDArchitectData, normalize_ddd_compliance),
    "legacy_code_expert": (LegacyCodeExpertData, normalize_legacy_safety),
    "refactoring_expert": (RefactoringExpertData, normalize_refactoring_debt),
}


def normalize_all(results: dict[str, Any]) -> list[DimensionScore]:
    """Normalize all available agent results into DimensionScores.

    Takes a dict of agent_key -> validated Pydantic model and returns
    a list of DimensionScores for all recognized agents. Unknown agent
    keys are silently skipped.
    """
    scores: list[DimensionScore] = []
    for agent_key, (expected_type, normalizer) in _NORMALIZERS.items():
        if agent_key in results and isinstance(results[agent_key], expected_type):
            scores.append(normalizer(results[agent_key]))
    return scores


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _clamp(value: float, low: float = 0.0, high: float = 10.0) -> float:
    """Clamp a value to [low, high] range."""
    return max(low, min(high, value))
