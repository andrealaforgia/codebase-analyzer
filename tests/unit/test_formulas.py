"""Unit tests for formula explanation functions -- boundary threshold tests.

Tests verify that explanation functions select the correct branch AT the exact
threshold value (e.g., exactly 8.0) and just below it (e.g., 7.99), killing
mutants that change `>=` to `>`.
"""

import pytest

from src.report import formulas


# ---------------------------------------------------------------------------
# code_quality_explanation: grade-based (discrete), no numeric thresholds
# ---------------------------------------------------------------------------


class TestCodeQualityExplanation:
    """code_quality_explanation uses a dict lookup on grade letter."""

    @pytest.mark.parametrize(
        "grade, expected_fragment",
        [
            ("A", "Excellent"),
            ("B", "Good"),
            ("C", "Moderate"),
            ("D", "Poor"),
            ("F", "Critical"),
        ],
    )
    def test_each_grade_produces_distinct_explanation(self, grade, expected_fragment):
        result = formulas.code_quality_explanation(grade)
        assert expected_fragment in result

    def test_unknown_grade_returns_fallback(self):
        result = formulas.code_quality_explanation("Z")
        assert "Z" in result


# ---------------------------------------------------------------------------
# test_design_explanation: thresholds at 8.0, 6.0, 4.0
# ---------------------------------------------------------------------------


class TestTestDesignExplanation:
    """test_design_explanation thresholds: >=8.0 excellent, >=6.0 good, >=4.0 moderate, else poor."""

    def test_at_8_0_is_excellent(self):
        result = formulas.test_design_explanation(8.0)
        assert "excellent" in result

    def test_just_below_8_0_is_good(self):
        result = formulas.test_design_explanation(7.99)
        assert "good" in result

    def test_at_6_0_is_good(self):
        result = formulas.test_design_explanation(6.0)
        assert "good" in result

    def test_just_below_6_0_is_moderate(self):
        result = formulas.test_design_explanation(5.99)
        assert "moderate" in result

    def test_at_4_0_is_moderate(self):
        result = formulas.test_design_explanation(4.0)
        assert "moderate" in result

    def test_just_below_4_0_is_poor(self):
        result = formulas.test_design_explanation(3.99)
        assert "poor" in result

    def test_at_10_is_excellent(self):
        result = formulas.test_design_explanation(10.0)
        assert "excellent" in result

    def test_at_0_is_poor(self):
        result = formulas.test_design_explanation(0.0)
        assert "poor" in result


# ---------------------------------------------------------------------------
# cognitive_load_explanation: thresholds at 8.0, 5.0
# ---------------------------------------------------------------------------


class TestCognitiveLoadExplanation:
    """cognitive_load_explanation thresholds: >=8.0 low, >=5.0 moderate, else high."""

    def test_at_8_0_is_low(self):
        result = formulas.cognitive_load_explanation(200, 8.0)
        assert "low" in result

    def test_just_below_8_0_is_moderate(self):
        result = formulas.cognitive_load_explanation(201, 7.99)
        assert "moderate" in result

    def test_at_5_0_is_moderate(self):
        result = formulas.cognitive_load_explanation(500, 5.0)
        assert "moderate" in result

    def test_just_below_5_0_is_high(self):
        result = formulas.cognitive_load_explanation(501, 4.99)
        assert "high" in result

    def test_at_10_is_low(self):
        result = formulas.cognitive_load_explanation(0, 10.0)
        assert "low" in result

    def test_at_0_is_high(self):
        result = formulas.cognitive_load_explanation(1000, 0.0)
        assert "high" in result


# ---------------------------------------------------------------------------
# ddd_compliance_explanation: thresholds at 8.0, 5.0
# ---------------------------------------------------------------------------


class TestDddComplianceExplanation:
    """ddd_compliance_explanation thresholds: >=8.0 strong, >=5.0 moderate, else weak."""

    def test_at_8_0_is_strong(self):
        result = formulas.ddd_compliance_explanation(8.0)
        assert "strong" in result

    def test_just_below_8_0_is_moderate(self):
        result = formulas.ddd_compliance_explanation(7.99)
        assert "moderate" in result

    def test_at_5_0_is_moderate(self):
        result = formulas.ddd_compliance_explanation(5.0)
        assert "moderate" in result

    def test_just_below_5_0_is_weak(self):
        result = formulas.ddd_compliance_explanation(4.99)
        assert "weak" in result

    def test_at_10_is_strong(self):
        result = formulas.ddd_compliance_explanation(10.0)
        assert "strong" in result

    def test_at_0_is_weak(self):
        result = formulas.ddd_compliance_explanation(0.0)
        assert "weak" in result


# ---------------------------------------------------------------------------
# legacy_safety_explanation: thresholds at 7.0, 4.0
# ---------------------------------------------------------------------------


class TestLegacySafetyExplanation:
    """legacy_safety_explanation thresholds: >=7.0 safe, >=4.0 moderate risk, else high risk."""

    def test_at_7_0_is_safe(self):
        result = formulas.legacy_safety_explanation(7.0)
        assert "safe" in result

    def test_just_below_7_0_is_moderate_risk(self):
        result = formulas.legacy_safety_explanation(6.99)
        assert "moderate risk" in result

    def test_at_4_0_is_moderate_risk(self):
        result = formulas.legacy_safety_explanation(4.0)
        assert "moderate risk" in result

    def test_just_below_4_0_is_high_risk(self):
        result = formulas.legacy_safety_explanation(3.99)
        assert "high risk" in result

    def test_at_10_is_safe(self):
        result = formulas.legacy_safety_explanation(10.0)
        assert "safe" in result

    def test_at_0_is_high_risk(self):
        result = formulas.legacy_safety_explanation(0.0)
        assert "high risk" in result


# ---------------------------------------------------------------------------
# refactoring_debt_explanation: thresholds at 8.0, 5.0
# ---------------------------------------------------------------------------


class TestRefactoringDebtExplanation:
    """refactoring_debt_explanation thresholds: >=8.0 low, >=5.0 moderate, else high."""

    def test_at_8_0_is_low(self):
        result = formulas.refactoring_debt_explanation(8.0)
        assert "low" in result

    def test_just_below_8_0_is_moderate(self):
        result = formulas.refactoring_debt_explanation(7.99)
        assert "moderate" in result

    def test_at_5_0_is_moderate(self):
        result = formulas.refactoring_debt_explanation(5.0)
        assert "moderate" in result

    def test_just_below_5_0_is_high(self):
        result = formulas.refactoring_debt_explanation(4.99)
        assert "high" in result

    def test_at_10_is_low(self):
        result = formulas.refactoring_debt_explanation(10.0)
        assert "low" in result

    def test_at_0_is_high(self):
        result = formulas.refactoring_debt_explanation(0.0)
        assert "high" in result
