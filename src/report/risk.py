"""Business risk derivation from dimension scores.

Pure functions that assess business risk categories from analysis dimension
scores.  Each risk category combines a subset of dimensions with specific
weights to produce a severity level (HIGH / MODERATE / LOW) and a
business-language description of the impact.

No I/O.  All functions are pure: list[DimensionScore] -> RiskCategory.
"""

from __future__ import annotations

from src.report.models import DimensionScore, RiskCategory


# ---------------------------------------------------------------------------
# Dimension weight configurations per risk category
# ---------------------------------------------------------------------------

_DELIVERY_VELOCITY_WEIGHTS: dict[str, float] = {
    "Refactoring Debt": 0.5,
    "Cognitive Load": 0.3,
    "Code Quality": 0.2,
}

_INCIDENT_WEIGHTS: dict[str, float] = {
    "Legacy Safety": 0.4,
    "Test Design": 0.3,
    "Code Quality": 0.3,
}

_ONBOARDING_WEIGHTS: dict[str, float] = {
    "Cognitive Load": 0.5,
    "Code Quality": 0.3,
    "DDD Compliance": 0.2,
}

# ---------------------------------------------------------------------------
# Severity thresholds
# ---------------------------------------------------------------------------

_HIGH_THRESHOLD = 4.0
_MODERATE_THRESHOLD = 6.0


# ---------------------------------------------------------------------------
# Internal helpers (pure)
# ---------------------------------------------------------------------------


def _find_dimension_by_name(
    name: str, dimensions: list[DimensionScore]
) -> DimensionScore | None:
    """Find a dimension by its name, or None if not present."""
    for dimension in dimensions:
        if dimension.name == name:
            return dimension
    return None


def _compute_weighted_score(
    dimensions: list[DimensionScore],
    weight_config: dict[str, float],
) -> tuple[float | None, list[str]]:
    """Compute the weighted score from available dimensions.

    Returns (weighted_score, contributing_dimension_names).
    If no contributing dimensions are found, returns (None, []).
    Weights are redistributed proportionally among available dimensions.
    """
    available_weights: dict[str, float] = {}
    available_scores: dict[str, float] = {}

    for dimension_name, weight in weight_config.items():
        dimension = _find_dimension_by_name(dimension_name, dimensions)
        if dimension is not None:
            available_weights[dimension_name] = weight
            available_scores[dimension_name] = dimension.normalized_score

    if not available_weights:
        return None, []

    total_weight = sum(available_weights.values())
    weighted_score = sum(
        available_scores[name] * (weight / total_weight)
        for name, weight in available_weights.items()
    )

    contributing_names = list(available_weights.keys())
    return weighted_score, contributing_names


def _classify_severity(weighted_score: float) -> str:
    """Classify a weighted score into a severity level."""
    if weighted_score < _HIGH_THRESHOLD:
        return "HIGH"
    if weighted_score < _MODERATE_THRESHOLD:
        return "MODERATE"
    return "LOW"


def _severity_descriptions() -> dict[str, dict[str, str]]:
    """Business-language descriptions keyed by (risk_category, severity)."""
    return {
        "Delivery Velocity Risk": {
            "HIGH": (
                "Significant technical debt and cognitive complexity are severely "
                "impeding delivery velocity. Teams spend more time navigating "
                "existing code than delivering new features."
            ),
            "MODERATE": (
                "Technical debt and code complexity are beginning to slow delivery. "
                "Proactive refactoring is recommended to prevent further velocity loss."
            ),
            "LOW": (
                "Codebase health supports sustainable delivery velocity. "
                "Technical debt is manageable and cognitive load is within acceptable bounds."
            ),
        },
        "Incident Risk": {
            "HIGH": (
                "Weak safety nets and poor test design create high exposure to "
                "production incidents. Changes carry significant regression risk."
            ),
            "MODERATE": (
                "Test coverage and legacy safety provide partial protection, but gaps "
                "remain. Some changes may introduce regressions undetected."
            ),
            "LOW": (
                "Strong test design and legacy safety measures provide robust protection "
                "against production incidents. Changes can be made with confidence."
            ),
        },
        "Onboarding Risk": {
            "HIGH": (
                "High cognitive load and unclear domain boundaries make onboarding "
                "new team members slow and error-prone. Expect extended ramp-up periods."
            ),
            "MODERATE": (
                "Moderate cognitive complexity and partial domain clarity may slow "
                "onboarding. New team members will need guided orientation."
            ),
            "LOW": (
                "Clear code structure and well-defined domain boundaries support "
                "efficient onboarding. New team members can become productive quickly."
            ),
        },
    }


def _assess_risk(
    risk_name: str,
    weight_config: dict[str, float],
    dimensions: list[DimensionScore],
) -> RiskCategory:
    """Assess a single risk category from dimension scores."""
    weighted_score, contributing_names = _compute_weighted_score(
        dimensions, weight_config
    )

    if weighted_score is None:
        return RiskCategory(
            name=risk_name,
            severity="MODERATE",
            contributing_dimensions=[],
            description=(
                f"Insufficient data to fully assess {risk_name.lower()}. "
                f"None of the contributing dimensions "
                f"({', '.join(weight_config.keys())}) were available."
            ),
        )

    severity = _classify_severity(weighted_score)
    descriptions = _severity_descriptions()
    description = descriptions[risk_name][severity]

    return RiskCategory(
        name=risk_name,
        severity=severity,
        contributing_dimensions=contributing_names,
        description=description,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def assess_delivery_velocity_risk(
    dimensions: list[DimensionScore],
) -> RiskCategory:
    """Assess delivery velocity risk from dimension scores.

    Contributing dimensions: Refactoring Debt (0.5), Cognitive Load (0.3),
    Code Quality (0.2).  Missing dimensions have their weights redistributed
    proportionally among available ones.
    """
    return _assess_risk("Delivery Velocity Risk", _DELIVERY_VELOCITY_WEIGHTS, dimensions)


def assess_incident_risk(
    dimensions: list[DimensionScore],
) -> RiskCategory:
    """Assess incident risk from dimension scores.

    Contributing dimensions: Legacy Safety (0.4), Test Design (0.3),
    Code Quality (0.3).  Missing dimensions have their weights redistributed
    proportionally among available ones.
    """
    return _assess_risk("Incident Risk", _INCIDENT_WEIGHTS, dimensions)


def assess_onboarding_risk(
    dimensions: list[DimensionScore],
) -> RiskCategory:
    """Assess onboarding risk from dimension scores.

    Contributing dimensions: Cognitive Load (0.5), Code Quality (0.3),
    DDD Compliance (0.2).  Missing dimensions have their weights redistributed
    proportionally among available ones.
    """
    return _assess_risk("Onboarding Risk", _ONBOARDING_WEIGHTS, dimensions)


def assess_all_risks(
    dimensions: list[DimensionScore],
) -> list[RiskCategory]:
    """Assess all three business risk categories from dimension scores.

    Returns a list of three RiskCategory values: Delivery Velocity Risk,
    Incident Risk, and Onboarding Risk.  If no contributing dimensions are
    available for a category, it returns MODERATE severity with a note about
    insufficient data.
    """
    return [
        assess_delivery_velocity_risk(dimensions),
        assess_incident_risk(dimensions),
        assess_onboarding_risk(dimensions),
    ]
