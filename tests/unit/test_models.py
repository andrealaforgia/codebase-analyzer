"""Unit tests for agent JSON output contract models.

Tests validate that each of the 6 agent Pydantic models:
- Accepts valid fixture data
- Is frozen (immutable)
- Validates required fields, types, and value ranges
- Produces clear errors identifying the failing field
"""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from src.report.models import (
    CodeSmellDetectorData,
    CognitiveLoadAnalyzerData,
    DDDArchitectData,
    LegacyCodeExpertData,
    RefactoringExpertData,
    TestDesignReviewerData,
)

FIXTURES_DIR = Path(__file__).parent.parent / "acceptance" / "codebase-analyzer" / "fixtures"


def _load_fixture(filename: str) -> dict:
    return json.loads((FIXTURES_DIR / filename).read_text())


# ---------------------------------------------------------------------------
# 1. CodeSmellDetectorData
# ---------------------------------------------------------------------------


class TestCodeSmellDetectorData:
    def test_valid_fixture_is_accepted(self):
        data = _load_fixture("code-smell-detector-data.json")
        model = CodeSmellDetectorData(**data)
        assert model.grade == "B"
        assert model.total_issues == 23

    def test_healthy_fixture_is_accepted(self):
        data = _load_fixture("healthy/code-smell-detector-data.json")
        model = CodeSmellDetectorData(**data)
        assert model.grade == "A"
        assert model.total_issues == 3

    def test_model_is_frozen(self):
        data = _load_fixture("code-smell-detector-data.json")
        model = CodeSmellDetectorData(**data)
        with pytest.raises(ValidationError):
            model.grade = "A"

    def test_grade_rejects_invalid_letter(self):
        data = _load_fixture("code-smell-detector-data.json")
        data["grade"] = "X"
        with pytest.raises(ValidationError, match="grade"):
            CodeSmellDetectorData(**data)

    def test_total_issues_rejects_negative(self):
        data = _load_fixture("code-smell-detector-data.json")
        data["total_issues"] = -1
        with pytest.raises(ValidationError, match="total_issues"):
            CodeSmellDetectorData(**data)

    def test_severity_distribution_requires_all_keys(self):
        data = _load_fixture("code-smell-detector-data.json")
        data["severity_distribution"] = {"high": 1, "medium": 2}
        with pytest.raises(ValidationError, match="low"):
            CodeSmellDetectorData(**data)

    def test_solid_compliance_requires_all_principles(self):
        data = _load_fixture("code-smell-detector-data.json")
        del data["solid_compliance"]["DIP"]
        with pytest.raises(ValidationError, match="DIP"):
            CodeSmellDetectorData(**data)

    def test_solid_compliance_rejects_out_of_range(self):
        data = _load_fixture("code-smell-detector-data.json")
        data["solid_compliance"]["SRP"] = -0.1
        with pytest.raises(ValidationError, match="SRP"):
            CodeSmellDetectorData(**data)

    def test_solid_compliance_rejects_above_max(self):
        data = _load_fixture("code-smell-detector-data.json")
        data["solid_compliance"]["OCP"] = 10.1
        with pytest.raises(ValidationError, match="OCP"):
            CodeSmellDetectorData(**data)

    def test_top_issue_requires_all_fields(self):
        data = _load_fixture("code-smell-detector-data.json")
        data["top_issues"] = [{"file": "a.py", "issue": "bad"}]
        with pytest.raises(ValidationError, match="severity"):
            CodeSmellDetectorData(**data)

    def test_missing_required_field_produces_clear_error(self):
        data = _load_fixture("code-smell-detector-data.json")
        del data["grade"]
        with pytest.raises(ValidationError, match="grade"):
            CodeSmellDetectorData(**data)


# ---------------------------------------------------------------------------
# 2. TestDesignReviewerData
# ---------------------------------------------------------------------------


class TestTestDesignReviewerData:
    def test_valid_fixture_is_accepted(self):
        data = _load_fixture("test-design-reviewer-data.json")
        model = TestDesignReviewerData(**data)
        assert model.farley_index == 7.2
        assert model.rating == "Good"

    def test_model_is_frozen(self):
        data = _load_fixture("test-design-reviewer-data.json")
        model = TestDesignReviewerData(**data)
        with pytest.raises(ValidationError):
            model.farley_index = 5.0

    def test_farley_index_rejects_below_zero(self):
        data = _load_fixture("test-design-reviewer-data.json")
        data["farley_index"] = -0.1
        with pytest.raises(ValidationError, match="farley_index"):
            TestDesignReviewerData(**data)

    def test_farley_index_rejects_above_ten(self):
        data = _load_fixture("test-design-reviewer-data.json")
        data["farley_index"] = 10.1
        with pytest.raises(ValidationError, match="farley_index"):
            TestDesignReviewerData(**data)

    def test_property_scores_must_have_all_fields(self):
        data = _load_fixture("test-design-reviewer-data.json")
        data["properties"]["Understandable"] = {"static": 7.5, "llm": 7.0}
        with pytest.raises(ValidationError, match="blended"):
            TestDesignReviewerData(**data)

    def test_tautology_counts_requires_all_keys(self):
        data = _load_fixture("test-design-reviewer-data.json")
        data["tautology_counts"] = {"mock_tautology": 3}
        with pytest.raises(ValidationError, match="mock_only"):
            TestDesignReviewerData(**data)

    def test_worst_offender_requires_issues_list(self):
        data = _load_fixture("test-design-reviewer-data.json")
        data["worst_offenders"] = [{"file": "test.py", "score": 4.0}]
        with pytest.raises(ValidationError, match="issues"):
            TestDesignReviewerData(**data)

    def test_missing_required_field_produces_clear_error(self):
        data = _load_fixture("test-design-reviewer-data.json")
        del data["farley_index"]
        with pytest.raises(ValidationError, match="farley_index"):
            TestDesignReviewerData(**data)


# ---------------------------------------------------------------------------
# 3. CognitiveLoadAnalyzerData
# ---------------------------------------------------------------------------


class TestCognitiveLoadAnalyzerData:
    def test_valid_fixture_is_accepted(self):
        data = _load_fixture("cognitive-load-analyzer-data.json")
        model = CognitiveLoadAnalyzerData(**data)
        assert model.cli_score == 312
        assert model.rating == "Moderate"

    def test_model_is_frozen(self):
        data = _load_fixture("cognitive-load-analyzer-data.json")
        model = CognitiveLoadAnalyzerData(**data)
        with pytest.raises(ValidationError):
            model.cli_score = 500

    def test_cli_score_rejects_below_zero(self):
        data = _load_fixture("cognitive-load-analyzer-data.json")
        data["cli_score"] = -1
        with pytest.raises(ValidationError, match="cli_score"):
            CognitiveLoadAnalyzerData(**data)

    def test_cli_score_rejects_above_thousand(self):
        data = _load_fixture("cognitive-load-analyzer-data.json")
        data["cli_score"] = 1001
        with pytest.raises(ValidationError, match="cli_score"):
            CognitiveLoadAnalyzerData(**data)

    def test_dimension_requires_all_fields(self):
        data = _load_fixture("cognitive-load-analyzer-data.json")
        data["dimensions"]["Structural Complexity"] = {"raw": "medium", "normalized": 5.5}
        with pytest.raises(ValidationError, match="weighted"):
            CognitiveLoadAnalyzerData(**data)

    def test_interaction_penalty_is_float(self):
        data = _load_fixture("cognitive-load-analyzer-data.json")
        model = CognitiveLoadAnalyzerData(**data)
        assert model.interaction_penalty == 0.15

    def test_worst_offender_requires_primary_dimension(self):
        data = _load_fixture("cognitive-load-analyzer-data.json")
        data["worst_offenders"] = [{"file": "a.py", "score": 50.0}]
        with pytest.raises(ValidationError, match="primary_dimension"):
            CognitiveLoadAnalyzerData(**data)

    def test_missing_required_field_produces_clear_error(self):
        data = _load_fixture("cognitive-load-analyzer-data.json")
        del data["cli_score"]
        with pytest.raises(ValidationError, match="cli_score"):
            CognitiveLoadAnalyzerData(**data)


# ---------------------------------------------------------------------------
# 4. DDDArchitectData
# ---------------------------------------------------------------------------


class TestDDDArchitectData:
    def test_valid_fixture_is_accepted(self):
        data = _load_fixture("ddd-architect-data.json")
        model = DDDArchitectData(**data)
        assert model.overall_score == 6.5
        assert model.bounded_context_count == 4

    def test_model_is_frozen(self):
        data = _load_fixture("ddd-architect-data.json")
        model = DDDArchitectData(**data)
        with pytest.raises(ValidationError):
            model.overall_score = 9.0

    def test_overall_score_rejects_below_zero(self):
        data = _load_fixture("ddd-architect-data.json")
        data["overall_score"] = -0.1
        with pytest.raises(ValidationError, match="overall_score"):
            DDDArchitectData(**data)

    def test_overall_score_rejects_above_ten(self):
        data = _load_fixture("ddd-architect-data.json")
        data["overall_score"] = 10.1
        with pytest.raises(ValidationError, match="overall_score"):
            DDDArchitectData(**data)

    def test_subdomain_distribution_requires_all_keys(self):
        data = _load_fixture("ddd-architect-data.json")
        data["subdomain_distribution"] = {"core": 2, "supporting": 1}
        with pytest.raises(ValidationError, match="generic"):
            DDDArchitectData(**data)

    def test_anti_pattern_requires_all_fields(self):
        data = _load_fixture("ddd-architect-data.json")
        data["anti_patterns"] = [{"name": "Bad Pattern"}]
        with pytest.raises(ValidationError, match="severity"):
            DDDArchitectData(**data)

    def test_pattern_maturity_requires_all_keys(self):
        data = _load_fixture("ddd-architect-data.json")
        del data["pattern_maturity"]["events"]
        with pytest.raises(ValidationError, match="events"):
            DDDArchitectData(**data)

    def test_pattern_maturity_rejects_out_of_range(self):
        data = _load_fixture("ddd-architect-data.json")
        data["pattern_maturity"]["strategic"] = -0.1
        with pytest.raises(ValidationError, match="strategic"):
            DDDArchitectData(**data)

    def test_context_map_mermaid_is_string(self):
        data = _load_fixture("ddd-architect-data.json")
        model = DDDArchitectData(**data)
        assert "graph LR" in model.context_map_mermaid

    def test_missing_required_field_produces_clear_error(self):
        data = _load_fixture("ddd-architect-data.json")
        del data["overall_score"]
        with pytest.raises(ValidationError, match="overall_score"):
            DDDArchitectData(**data)


# ---------------------------------------------------------------------------
# 5. LegacyCodeExpertData
# ---------------------------------------------------------------------------


class TestLegacyCodeExpertData:
    def test_valid_fixture_is_accepted(self):
        data = _load_fixture("legacy-code-expert-data.json")
        model = LegacyCodeExpertData(**data)
        assert model.overall_score == 5.5
        assert model.risk_level == "Medium"

    def test_model_is_frozen(self):
        data = _load_fixture("legacy-code-expert-data.json")
        model = LegacyCodeExpertData(**data)
        with pytest.raises(ValidationError):
            model.risk_level = "Low"

    def test_overall_score_rejects_below_zero(self):
        data = _load_fixture("legacy-code-expert-data.json")
        data["overall_score"] = -0.1
        with pytest.raises(ValidationError, match="overall_score"):
            LegacyCodeExpertData(**data)

    def test_overall_score_rejects_above_ten(self):
        data = _load_fixture("legacy-code-expert-data.json")
        data["overall_score"] = 10.1
        with pytest.raises(ValidationError, match="overall_score"):
            LegacyCodeExpertData(**data)

    def test_risk_level_rejects_invalid_value(self):
        data = _load_fixture("legacy-code-expert-data.json")
        data["risk_level"] = "Extreme"
        with pytest.raises(ValidationError, match="risk_level"):
            LegacyCodeExpertData(**data)

    def test_testability_score_rejects_below_zero(self):
        data = _load_fixture("legacy-code-expert-data.json")
        data["testability_score"] = -0.01
        with pytest.raises(ValidationError, match="testability_score"):
            LegacyCodeExpertData(**data)

    def test_testability_score_rejects_above_one(self):
        data = _load_fixture("legacy-code-expert-data.json")
        data["testability_score"] = 1.01
        with pytest.raises(ValidationError, match="testability_score"):
            LegacyCodeExpertData(**data)

    def test_seam_availability_requires_all_keys(self):
        data = _load_fixture("legacy-code-expert-data.json")
        data["seam_availability"] = {"object": 12, "link": 5}
        with pytest.raises(ValidationError, match="preprocessing"):
            LegacyCodeExpertData(**data)

    def test_module_at_risk_requires_all_fields(self):
        data = _load_fixture("legacy-code-expert-data.json")
        data["modules_at_risk"] = [{"file": "a.py", "risk": "High"}]
        with pytest.raises(ValidationError, match="dependencies"):
            LegacyCodeExpertData(**data)

    def test_missing_required_field_produces_clear_error(self):
        data = _load_fixture("legacy-code-expert-data.json")
        del data["risk_level"]
        with pytest.raises(ValidationError, match="risk_level"):
            LegacyCodeExpertData(**data)


# ---------------------------------------------------------------------------
# 6. RefactoringExpertData
# ---------------------------------------------------------------------------


class TestRefactoringExpertData:
    def test_valid_fixture_is_accepted(self):
        data = _load_fixture("refactoring-expert-data.json")
        model = RefactoringExpertData(**data)
        assert model.total_recommendations == 14

    def test_model_is_frozen(self):
        data = _load_fixture("refactoring-expert-data.json")
        model = RefactoringExpertData(**data)
        with pytest.raises(ValidationError):
            model.total_recommendations = 0

    def test_total_recommendations_rejects_negative(self):
        data = _load_fixture("refactoring-expert-data.json")
        data["total_recommendations"] = -1
        with pytest.raises(ValidationError, match="total_recommendations"):
            RefactoringExpertData(**data)

    def test_priority_matrix_item_requires_all_fields(self):
        data = _load_fixture("refactoring-expert-data.json")
        data["priority_matrix"] = [{"item": "Do something"}]
        with pytest.raises(ValidationError, match="impact"):
            RefactoringExpertData(**data)

    def test_risk_distribution_requires_all_keys(self):
        data = _load_fixture("refactoring-expert-data.json")
        data["risk_distribution"] = {"low": 5, "medium": 7}
        with pytest.raises(ValidationError, match="high"):
            RefactoringExpertData(**data)

    def test_implementation_sequence_item_requires_all_fields(self):
        data = _load_fixture("refactoring-expert-data.json")
        data["implementation_sequence"] = [{"order": 1}]
        with pytest.raises(ValidationError, match="item"):
            RefactoringExpertData(**data)

    def test_implementation_sequence_order_must_be_positive(self):
        data = _load_fixture("refactoring-expert-data.json")
        data["implementation_sequence"] = [
            {"order": 0, "item": "Do X", "rationale": "Because"}
        ]
        with pytest.raises(ValidationError, match="order"):
            RefactoringExpertData(**data)

    def test_missing_required_field_produces_clear_error(self):
        data = _load_fixture("refactoring-expert-data.json")
        del data["total_recommendations"]
        with pytest.raises(ValidationError, match="total_recommendations"):
            RefactoringExpertData(**data)
