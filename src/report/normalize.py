"""Score normalization functions for agent data.

Each function transforms raw agent data (validated Pydantic model) into a
normalized DimensionScore on the 0-10 scale using documented formulas.

All functions are pure: no side effects, no I/O. Formula string generation
is delegated to formulas.py.

Dimension weights (21 dimensions):
    code_quality     = 0.07    test_design         = 0.07
    cognitive_load   = 0.07    security            = 0.07
    ddd_compliance   = 0.05    legacy_safety       = 0.05
    error_handling   = 0.05    dependency_health   = 0.05
    refactoring_debt = 0.05    api_design          = 0.05
    concurrency      = 0.05    code_ownership      = 0.05
    documentation    = 0.04    dead_code           = 0.04
    devops_maturity  = 0.04    consistency         = 0.04
    compliance       = 0.04    data_layer          = 0.03
    observability    = 0.03    accessibility       = 0.03
    system_comprehensibility = 0.03
"""

from __future__ import annotations

import math
from collections.abc import Callable
from typing import Any

from src.report.formulas import (
    code_quality_explanation,
    code_quality_formula_display,
    cognitive_load_explanation,
    cognitive_load_formula_display,
    ddd_compliance_explanation,
    ddd_compliance_formula_display,
    generic_explanation,
    generic_formula_display,
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
    GenericAgentData,
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
        weight=0.07,
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
        weight=0.07,
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
        weight=0.07,
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
        weight=0.05,
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
        weight=0.05,
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
        weight=0.05,
        formula_display=refactoring_debt_formula_display(
            high, medium, low, weighted_count, normalized,
        ),
        explanation=refactoring_debt_explanation(normalized),
    )


# ---------------------------------------------------------------------------
# Generic normalizer for new agents (0-100 -> 0-10)
# ---------------------------------------------------------------------------


# Maps agent keys to (dimension_name, weight) for the 15 generic agents
_GENERIC_AGENT_CONFIG: dict[str, tuple[str, float]] = {
    "security_assessor": ("security", 0.07),
    "error_handling_reviewer": ("error_handling", 0.05),
    "api_design_reviewer": ("api_design", 0.05),
    "dependency_auditor": ("dependency_health", 0.05),
    "concurrency_analyzer": ("concurrency", 0.05),
    "documentation_reviewer": ("documentation", 0.04),
    "dead_code_detector": ("dead_code", 0.04),
    "devops_evaluator": ("devops_maturity", 0.04),
    "ownership_analyzer": ("code_ownership", 0.05),
    "consistency_checker": ("consistency", 0.04),
    "data_layer_reviewer": ("data_layer", 0.03),
    "observability_assessor": ("observability", 0.03),
    "system_auditor": ("compliance", 0.04),
    "accessibility_assessor": ("accessibility", 0.03),
    "system_explorer": ("system_comprehensibility", 0.03),
}


def _normalize_generic(agent_key: str, data: GenericAgentData) -> DimensionScore:
    """Normalize a generic agent score from 0-100 to 0-10."""
    dimension_name, weight = _GENERIC_AGENT_CONFIG[agent_key]
    normalized = _clamp(data.overall_score / 10.0)
    return DimensionScore(
        name=dimension_name,
        raw_score=data.overall_score,
        normalized_score=normalized,
        weight=weight,
        formula_display=generic_formula_display(dimension_name, data.overall_score, normalized),
        explanation=generic_explanation(dimension_name, normalized),
    )


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

# Maps agent keys to their normalizer functions and expected data types
_NORMALIZERS: dict[str, tuple[type, Callable[..., DimensionScore]]] = {
    "code_smell_detector": (CodeSmellDetectorData, normalize_code_quality),
    "test_design_reviewer": (TestDesignReviewerData, normalize_test_design),
    "cognitive_load_analyzer": (CognitiveLoadAnalyzerData, normalize_cognitive_load),
    "ddd_assessor": (DDDArchitectData, normalize_ddd_compliance),
    "legacy_code_analyzer": (LegacyCodeExpertData, normalize_legacy_safety),
    "refactoring_advisor": (RefactoringExpertData, normalize_refactoring_debt),
}


def normalize_all(results: dict[str, Any]) -> list[DimensionScore]:
    """Normalize all available agent results into DimensionScores.

    Takes a dict of agent_key -> validated Pydantic model and returns
    a list of DimensionScores for all recognized agents. Handles both
    the original 6 specific agents and the 12 new generic agents.
    Unknown agent keys are silently skipped.
    """
    scores: list[DimensionScore] = []

    # Original 6 agents with specific normalizers
    for agent_key, (expected_type, normalizer) in _NORMALIZERS.items():
        if agent_key in results and isinstance(results[agent_key], expected_type):
            scores.append(normalizer(results[agent_key]))

    # 12 new agents with generic normalization
    for agent_key in _GENERIC_AGENT_CONFIG:
        if agent_key in results and isinstance(results[agent_key], GenericAgentData):
            scores.append(_normalize_generic(agent_key, results[agent_key]))

    return scores


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _clamp(value: float, low: float = 0.0, high: float = 10.0) -> float:
    """Clamp a value to [low, high] range.

    Raises ValueError for non-finite values (NaN, Inf, -Inf).
    """
    if math.isnan(value) or math.isinf(value):
        raise ValueError(f"Cannot clamp non-finite value: {value}")
    return max(low, min(high, value))
