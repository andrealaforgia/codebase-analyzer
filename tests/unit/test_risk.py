"""Unit tests for business risk derivation from dimension scores.

Tests validate that risk assessment functions correctly:
- Compute weighted scores from contributing dimensions
- Apply severity thresholds (HIGH < 4.0, MODERATE < 6.0, LOW >= 6.0)
- Redistribute weights when dimensions are missing
- Return MODERATE with insufficient data note when no contributing dimensions
- Produce LOW across all categories when all dimensions are healthy
"""

import pytest

from src.report.models import DimensionScore
from src.report.risk import (
    assess_all_risks,
    assess_delivery_velocity_risk,
    assess_incident_risk,
    assess_onboarding_risk,
)


def _make_dimension(name: str, score: float) -> DimensionScore:
    """Create a DimensionScore with the given name and normalized score."""
    return DimensionScore(
        name=name,
        raw_score=score,
        normalized_score=score,
        weight=0.15,
        formula_display=f"{name} = {score}",
        explanation=f"{name} explanation",
    )


# ---------------------------------------------------------------------------
# Delivery Velocity Risk: refactoring_debt (0.5) + cognitive_load (0.3) + code_quality (0.2)
# ---------------------------------------------------------------------------


class TestAssessDeliveryVelocityRisk:
    def test_high_severity_when_weighted_score_below_four(self):
        dimensions = [
            _make_dimension("Refactoring Debt", 2.0),
            _make_dimension("Cognitive Load", 3.0),
            _make_dimension("Code Quality", 4.0),
        ]
        # weighted = 2.0*0.5 + 3.0*0.3 + 4.0*0.2 = 1.0 + 0.9 + 0.8 = 2.7
        result = assess_delivery_velocity_risk(dimensions)
        assert result.severity == "HIGH"
        assert result.name == "Delivery Velocity Risk"
        assert "Refactoring Debt" in result.contributing_dimensions
        assert "Cognitive Load" in result.contributing_dimensions
        assert "Code Quality" in result.contributing_dimensions

    def test_moderate_severity_when_weighted_score_between_four_and_six(self):
        dimensions = [
            _make_dimension("Refactoring Debt", 6.0),
            _make_dimension("Cognitive Load", 5.0),
            _make_dimension("Code Quality", 5.0),
        ]
        # weighted = 6.0*0.5 + 5.0*0.3 + 5.0*0.2 = 3.0 + 1.5 + 1.0 = 5.5
        result = assess_delivery_velocity_risk(dimensions)
        assert result.severity == "MODERATE"

    def test_low_severity_when_weighted_score_at_or_above_six(self):
        dimensions = [
            _make_dimension("Refactoring Debt", 8.0),
            _make_dimension("Cognitive Load", 7.0),
            _make_dimension("Code Quality", 7.0),
        ]
        # weighted = 8.0*0.5 + 7.0*0.3 + 7.0*0.2 = 4.0 + 2.1 + 1.4 = 7.5
        result = assess_delivery_velocity_risk(dimensions)
        assert result.severity == "LOW"

    def test_description_uses_business_language(self):
        dimensions = [
            _make_dimension("Refactoring Debt", 2.0),
            _make_dimension("Cognitive Load", 2.0),
            _make_dimension("Code Quality", 2.0),
        ]
        result = assess_delivery_velocity_risk(dimensions)
        assert len(result.description) > 0
        assert isinstance(result.description, str)


# ---------------------------------------------------------------------------
# Incident Risk: legacy_safety (0.4) + test_design (0.3) + code_quality (0.3)
# ---------------------------------------------------------------------------


class TestAssessIncidentRisk:
    def test_high_severity_when_weighted_score_below_four(self):
        dimensions = [
            _make_dimension("Legacy Safety", 2.0),
            _make_dimension("Test Design", 3.0),
            _make_dimension("Code Quality", 3.0),
        ]
        # weighted = 2.0*0.4 + 3.0*0.3 + 3.0*0.3 = 0.8 + 0.9 + 0.9 = 2.6
        result = assess_incident_risk(dimensions)
        assert result.severity == "HIGH"
        assert result.name == "Incident Risk"
        assert "Legacy Safety" in result.contributing_dimensions
        assert "Test Design" in result.contributing_dimensions
        assert "Code Quality" in result.contributing_dimensions

    def test_low_severity_when_weighted_score_at_or_above_six(self):
        dimensions = [
            _make_dimension("Legacy Safety", 8.0),
            _make_dimension("Test Design", 7.0),
            _make_dimension("Code Quality", 7.0),
        ]
        # weighted = 8.0*0.4 + 7.0*0.3 + 7.0*0.3 = 3.2 + 2.1 + 2.1 = 7.4
        result = assess_incident_risk(dimensions)
        assert result.severity == "LOW"


# ---------------------------------------------------------------------------
# Onboarding Risk: cognitive_load (0.5) + code_quality (0.3) + ddd_compliance (0.2)
# ---------------------------------------------------------------------------


class TestAssessOnboardingRisk:
    def test_high_severity_when_weighted_score_below_four(self):
        dimensions = [
            _make_dimension("Cognitive Load", 2.0),
            _make_dimension("Code Quality", 3.0),
            _make_dimension("DDD Compliance", 3.0),
        ]
        # weighted = 2.0*0.5 + 3.0*0.3 + 3.0*0.2 = 1.0 + 0.9 + 0.6 = 2.5
        result = assess_onboarding_risk(dimensions)
        assert result.severity == "HIGH"
        assert result.name == "Onboarding Risk"
        assert "Cognitive Load" in result.contributing_dimensions
        assert "Code Quality" in result.contributing_dimensions
        assert "DDD Compliance" in result.contributing_dimensions

    def test_low_severity_when_weighted_score_at_or_above_six(self):
        dimensions = [
            _make_dimension("Cognitive Load", 8.0),
            _make_dimension("Code Quality", 7.0),
            _make_dimension("DDD Compliance", 7.0),
        ]
        # weighted = 8.0*0.5 + 7.0*0.3 + 7.0*0.2 = 4.0 + 2.1 + 1.4 = 7.5
        result = assess_onboarding_risk(dimensions)
        assert result.severity == "LOW"


# ---------------------------------------------------------------------------
# assess_all_risks: integration of all 3 risk categories
# ---------------------------------------------------------------------------


class TestAssessAllRisks:
    def test_all_healthy_dimensions_produce_low_across_all_categories(self):
        dimensions = [
            _make_dimension("Code Quality", 8.0),
            _make_dimension("Test Design", 8.0),
            _make_dimension("Cognitive Load", 8.0),
            _make_dimension("DDD Compliance", 8.0),
            _make_dimension("Legacy Safety", 8.0),
            _make_dimension("Refactoring Debt", 8.0),
        ]
        results = assess_all_risks(dimensions)
        assert len(results) == 3
        for risk in results:
            assert risk.severity == "LOW", f"{risk.name} should be LOW but was {risk.severity}"

    def test_returns_all_three_risk_categories(self):
        dimensions = [
            _make_dimension("Code Quality", 5.0),
            _make_dimension("Test Design", 5.0),
            _make_dimension("Cognitive Load", 5.0),
            _make_dimension("DDD Compliance", 5.0),
            _make_dimension("Legacy Safety", 5.0),
            _make_dimension("Refactoring Debt", 5.0),
        ]
        results = assess_all_risks(dimensions)
        names = {risk.name for risk in results}
        assert names == {"Delivery Velocity Risk", "Incident Risk", "Onboarding Risk"}

    def test_missing_dimension_redistributes_weights(self):
        # Only Refactoring Debt present for delivery velocity.
        # Weight redistribution: 0.5 / 0.5 = 1.0 for Refactoring Debt alone
        # weighted = 7.0 * 1.0 = 7.0 -> LOW
        dimensions = [
            _make_dimension("Refactoring Debt", 7.0),
        ]
        results = assess_all_risks(dimensions)
        delivery_risk = next(r for r in results if r.name == "Delivery Velocity Risk")
        assert delivery_risk.severity == "LOW"
        assert "Refactoring Debt" in delivery_risk.contributing_dimensions

    def test_no_contributing_dimensions_returns_moderate_with_note(self):
        # Empty list: no contributing dimensions for any category
        results = assess_all_risks([])
        assert len(results) == 3
        for risk in results:
            assert risk.severity == "MODERATE"
            assert "insufficient" in risk.description.lower()

    def test_partial_dimensions_for_mixed_severities(self):
        # Legacy Safety very low -> incident risk HIGH
        # Cognitive Load and Refactoring Debt high -> delivery velocity LOW
        dimensions = [
            _make_dimension("Refactoring Debt", 8.0),
            _make_dimension("Cognitive Load", 8.0),
            _make_dimension("Code Quality", 8.0),
            _make_dimension("Legacy Safety", 1.0),
            _make_dimension("Test Design", 1.0),
        ]
        results = assess_all_risks(dimensions)
        delivery_risk = next(r for r in results if r.name == "Delivery Velocity Risk")
        incident_risk = next(r for r in results if r.name == "Incident Risk")
        assert delivery_risk.severity == "LOW"
        assert incident_risk.severity == "HIGH"

    def test_threshold_boundary_at_exactly_four(self):
        # Weighted score exactly 4.0 should be MODERATE (not HIGH)
        # For delivery velocity: rd(0.5) + cl(0.3) + cq(0.2)
        # Need weighted = 4.0 exactly
        # 4.0*0.5 + 4.0*0.3 + 4.0*0.2 = 2.0 + 1.2 + 0.8 = 4.0
        dimensions = [
            _make_dimension("Refactoring Debt", 4.0),
            _make_dimension("Cognitive Load", 4.0),
            _make_dimension("Code Quality", 4.0),
        ]
        result = assess_delivery_velocity_risk(dimensions)
        assert result.severity == "MODERATE"

    def test_threshold_boundary_at_exactly_six(self):
        # Weighted score exactly 6.0 should be LOW (not MODERATE)
        # 6.0*0.5 + 6.0*0.3 + 6.0*0.2 = 3.0 + 1.8 + 1.2 = 6.0
        dimensions = [
            _make_dimension("Refactoring Debt", 6.0),
            _make_dimension("Cognitive Load", 6.0),
            _make_dimension("Code Quality", 6.0),
        ]
        result = assess_delivery_velocity_risk(dimensions)
        assert result.severity == "LOW"
