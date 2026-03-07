"""Unit tests for agent JSON output contract models and report data structures.

Tests validate that each of the 6 agent Pydantic models:
- Accepts valid fixture data
- Is frozen (immutable)
- Validates required fields, types, and value ranges
- Produces clear errors identifying the failing field

Tests also validate report-level models (ProjectMetadata, DimensionScore,
RiskCategory, ReportData) and pure functions (compute_overall_score,
derive_rating).
"""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from src.report.models import (
    CodeSmellDetectorData,
    CodeSmellTopIssue,
    CognitiveDimension,
    CognitiveLoadAnalyzerData,
    CognitiveWorstOffender,
    DDDAntiPattern,
    DDDArchitectData,
    DimensionScore,
    ImplementationSequenceItem,
    LegacyCodeExpertData,
    ModuleAtRisk,
    PatternMaturity,
    PriorityMatrixItem,
    ProjectMetadata,
    PropertyScores,
    RefactoringExpertData,
    ReportData,
    RiskCategory,
    RiskDistribution,
    SeamAvailability,
    SeverityDistribution,
    SolidCompliance,
    SubdomainDistribution,
    TautologyCounts,
    TestDesignReviewerData,
    TestDesignWorstOffender,
    compute_overall_score,
    derive_rating,
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


# ---------------------------------------------------------------------------
# 7. ProjectMetadata
# ---------------------------------------------------------------------------


class TestProjectMetadata:
    def test_valid_metadata_is_accepted(self):
        model = ProjectMetadata(
            project_name="my-project",
            target_directory="/tmp/my-project",
            analysis_date="2026-03-07",
        )
        assert model.project_name == "my-project"
        assert model.target_directory == "/tmp/my-project"
        assert model.analysis_date == "2026-03-07"

    def test_optional_fields_default_to_none(self):
        model = ProjectMetadata(
            project_name="p",
            target_directory="/tmp",
            analysis_date="2026-01-01",
        )
        assert model.total_files is None
        assert model.total_loc is None
        assert model.primary_language is None

    def test_optional_fields_accept_values(self):
        model = ProjectMetadata(
            project_name="p",
            target_directory="/tmp",
            analysis_date="2026-01-01",
            total_files=42,
            total_loc=10000,
            primary_language="Python",
        )
        assert model.total_files == 42
        assert model.total_loc == 10000
        assert model.primary_language == "Python"

    def test_model_is_frozen(self):
        model = ProjectMetadata(
            project_name="p",
            target_directory="/tmp",
            analysis_date="2026-01-01",
        )
        with pytest.raises(ValidationError):
            model.project_name = "other"

    def test_missing_required_field_produces_clear_error(self):
        with pytest.raises(ValidationError, match="project_name"):
            ProjectMetadata(
                target_directory="/tmp",
                analysis_date="2026-01-01",
            )


# ---------------------------------------------------------------------------
# 8. DimensionScore
# ---------------------------------------------------------------------------


class TestDimensionScore:
    def test_valid_dimension_score_is_accepted(self):
        model = DimensionScore(
            name="code_quality",
            raw_score=7.5,
            normalized_score=7.5,
            weight=0.20,
            formula_display="(SRP*0.2 + OCP*0.2 + ...) = 7.5",
            explanation="Code quality is good overall.",
        )
        assert model.name == "code_quality"
        assert model.normalized_score == 7.5
        assert model.weight == 0.20

    def test_model_is_frozen(self):
        model = DimensionScore(
            name="test_design",
            raw_score=6.0,
            normalized_score=6.0,
            weight=0.20,
            formula_display="farley_index = 6.0",
            explanation="Test design is decent.",
        )
        with pytest.raises(ValidationError):
            model.name = "other"

    def test_normalized_score_rejects_below_zero(self):
        with pytest.raises(ValidationError, match="normalized_score"):
            DimensionScore(
                name="x",
                raw_score=0.0,
                normalized_score=-0.1,
                weight=0.20,
                formula_display="f",
                explanation="e",
            )

    def test_normalized_score_rejects_above_ten(self):
        with pytest.raises(ValidationError, match="normalized_score"):
            DimensionScore(
                name="x",
                raw_score=0.0,
                normalized_score=10.1,
                weight=0.20,
                formula_display="f",
                explanation="e",
            )

    def test_weight_rejects_below_zero(self):
        with pytest.raises(ValidationError, match="weight"):
            DimensionScore(
                name="x",
                raw_score=0.0,
                normalized_score=5.0,
                weight=-0.01,
                formula_display="f",
                explanation="e",
            )

    def test_weight_rejects_above_one(self):
        with pytest.raises(ValidationError, match="weight"):
            DimensionScore(
                name="x",
                raw_score=0.0,
                normalized_score=5.0,
                weight=1.01,
                formula_display="f",
                explanation="e",
            )

    def test_missing_required_field_produces_clear_error(self):
        with pytest.raises(ValidationError, match="name"):
            DimensionScore(
                raw_score=5.0,
                normalized_score=5.0,
                weight=0.20,
                formula_display="f",
                explanation="e",
            )


# ---------------------------------------------------------------------------
# 9. RiskCategory
# ---------------------------------------------------------------------------


class TestRiskCategory:
    def test_valid_risk_category_is_accepted(self):
        model = RiskCategory(
            name="Delivery Velocity Risk",
            severity="HIGH",
            contributing_dimensions=["code_quality", "refactoring_debt"],
            description="High code smell count slows delivery.",
        )
        assert model.name == "Delivery Velocity Risk"
        assert model.severity == "HIGH"
        assert len(model.contributing_dimensions) == 2

    def test_model_is_frozen(self):
        model = RiskCategory(
            name="Risk",
            severity="LOW",
            contributing_dimensions=[],
            description="d",
        )
        with pytest.raises(ValidationError):
            model.severity = "HIGH"

    def test_severity_rejects_invalid_value(self):
        with pytest.raises(ValidationError, match="severity"):
            RiskCategory(
                name="Risk",
                severity="EXTREME",
                contributing_dimensions=[],
                description="d",
            )

    def test_severity_accepts_all_valid_values(self):
        for severity in ("HIGH", "MODERATE", "LOW"):
            model = RiskCategory(
                name="Risk",
                severity=severity,
                contributing_dimensions=[],
                description="d",
            )
            assert model.severity == severity

    def test_missing_required_field_produces_clear_error(self):
        with pytest.raises(ValidationError, match="name"):
            RiskCategory(
                severity="LOW",
                contributing_dimensions=[],
                description="d",
            )


# ---------------------------------------------------------------------------
# 10. ReportData
# ---------------------------------------------------------------------------


def _make_metadata(**overrides) -> dict:
    defaults = {
        "project_name": "test-project",
        "target_directory": "/tmp/test",
        "analysis_date": "2026-03-07",
    }
    defaults.update(overrides)
    return defaults


def _make_dimension(name: str, normalized_score: float, weight: float) -> dict:
    return {
        "name": name,
        "raw_score": normalized_score,
        "normalized_score": normalized_score,
        "weight": weight,
        "formula_display": f"{name} = {normalized_score}",
        "explanation": f"{name} explanation",
    }


class TestReportData:
    def test_valid_report_data_is_accepted(self):
        model = ReportData(
            metadata=_make_metadata(),
            dimensions=[
                _make_dimension("code_quality", 7.0, 0.20),
                _make_dimension("test_design", 8.0, 0.20),
            ],
            overall_score=75.0,
            rating="Good",
            risk_assessments=[],
            agent_results={},
        )
        assert model.overall_score == 75.0
        assert model.rating == "Good"
        assert len(model.dimensions) == 2

    def test_model_is_frozen(self):
        model = ReportData(
            metadata=_make_metadata(),
            dimensions=[],
            overall_score=50.0,
            rating="Needs Attention",
            risk_assessments=[],
            agent_results={},
        )
        with pytest.raises(ValidationError):
            model.overall_score = 99.0

    def test_rating_rejects_invalid_value(self):
        with pytest.raises(ValidationError, match="rating"):
            ReportData(
                metadata=_make_metadata(),
                dimensions=[],
                overall_score=50.0,
                rating="Terrible",
                risk_assessments=[],
                agent_results={},
            )

    def test_rating_accepts_all_valid_values(self):
        for rating in ("Critical", "Needs Attention", "Good", "Excellent"):
            model = ReportData(
                metadata=_make_metadata(),
                dimensions=[],
                overall_score=50.0,
                rating=rating,
                risk_assessments=[],
                agent_results={},
            )
            assert model.rating == rating

    def test_overall_score_rejects_below_zero(self):
        with pytest.raises(ValidationError, match="overall_score"):
            ReportData(
                metadata=_make_metadata(),
                dimensions=[],
                overall_score=-0.1,
                rating="Critical",
                risk_assessments=[],
                agent_results={},
            )

    def test_overall_score_rejects_above_hundred(self):
        with pytest.raises(ValidationError, match="overall_score"):
            ReportData(
                metadata=_make_metadata(),
                dimensions=[],
                overall_score=100.1,
                rating="Excellent",
                risk_assessments=[],
                agent_results={},
            )

    def test_dimensions_accepts_empty_list(self):
        model = ReportData(
            metadata=_make_metadata(),
            dimensions=[],
            overall_score=0.0,
            rating="Critical",
            risk_assessments=[],
            agent_results={},
        )
        assert model.dimensions == []

    def test_dimensions_accepts_up_to_six_items(self):
        dims = [_make_dimension(f"dim_{i}", 5.0, 0.15) for i in range(6)]
        model = ReportData(
            metadata=_make_metadata(),
            dimensions=dims,
            overall_score=50.0,
            rating="Needs Attention",
            risk_assessments=[],
            agent_results={},
        )
        assert len(model.dimensions) == 6

    def test_agent_results_accepts_arbitrary_dict(self):
        model = ReportData(
            metadata=_make_metadata(),
            dimensions=[],
            overall_score=50.0,
            rating="Needs Attention",
            risk_assessments=[],
            agent_results={"code_smell_detector": {"grade": "A", "total_issues": 0}},
        )
        assert model.agent_results["code_smell_detector"]["grade"] == "A"

    def test_missing_required_field_produces_clear_error(self):
        with pytest.raises(ValidationError, match="metadata"):
            ReportData(
                dimensions=[],
                overall_score=50.0,
                rating="Good",
                risk_assessments=[],
                agent_results={},
            )


# ---------------------------------------------------------------------------
# 11. compute_overall_score (pure function)
# ---------------------------------------------------------------------------


class TestComputeOverallScore:
    def test_all_six_dimensions_weighted_average(self):
        """health = (cq*0.20 + td*0.20 + cl*0.20 + ddd*0.15 + ls*0.15 + rd*0.10) * 10"""
        dimensions = [
            DimensionScore(name="code_quality", raw_score=8.0, normalized_score=8.0, weight=0.20, formula_display="f", explanation="e"),
            DimensionScore(name="test_design", raw_score=7.0, normalized_score=7.0, weight=0.20, formula_display="f", explanation="e"),
            DimensionScore(name="cognitive_load", raw_score=6.0, normalized_score=6.0, weight=0.20, formula_display="f", explanation="e"),
            DimensionScore(name="ddd_compliance", raw_score=5.0, normalized_score=5.0, weight=0.15, formula_display="f", explanation="e"),
            DimensionScore(name="legacy_safety", raw_score=4.0, normalized_score=4.0, weight=0.15, formula_display="f", explanation="e"),
            DimensionScore(name="refactoring_debt", raw_score=3.0, normalized_score=3.0, weight=0.10, formula_display="f", explanation="e"),
        ]
        # (8*0.20 + 7*0.20 + 6*0.20 + 5*0.15 + 4*0.15 + 3*0.10) * 10
        # = (1.6 + 1.4 + 1.2 + 0.75 + 0.6 + 0.3) * 10
        # = 5.85 * 10 = 58.5
        result = compute_overall_score(dimensions)
        assert result == pytest.approx(58.5)

    def test_all_perfect_scores_yield_hundred(self):
        dimensions = [
            DimensionScore(name="code_quality", raw_score=10.0, normalized_score=10.0, weight=0.20, formula_display="f", explanation="e"),
            DimensionScore(name="test_design", raw_score=10.0, normalized_score=10.0, weight=0.20, formula_display="f", explanation="e"),
            DimensionScore(name="cognitive_load", raw_score=10.0, normalized_score=10.0, weight=0.20, formula_display="f", explanation="e"),
            DimensionScore(name="ddd_compliance", raw_score=10.0, normalized_score=10.0, weight=0.15, formula_display="f", explanation="e"),
            DimensionScore(name="legacy_safety", raw_score=10.0, normalized_score=10.0, weight=0.15, formula_display="f", explanation="e"),
            DimensionScore(name="refactoring_debt", raw_score=10.0, normalized_score=10.0, weight=0.10, formula_display="f", explanation="e"),
        ]
        result = compute_overall_score(dimensions)
        assert result == pytest.approx(100.0)

    def test_all_zero_scores_yield_zero(self):
        dimensions = [
            DimensionScore(name="code_quality", raw_score=0.0, normalized_score=0.0, weight=0.20, formula_display="f", explanation="e"),
            DimensionScore(name="test_design", raw_score=0.0, normalized_score=0.0, weight=0.20, formula_display="f", explanation="e"),
            DimensionScore(name="cognitive_load", raw_score=0.0, normalized_score=0.0, weight=0.20, formula_display="f", explanation="e"),
            DimensionScore(name="ddd_compliance", raw_score=0.0, normalized_score=0.0, weight=0.15, formula_display="f", explanation="e"),
            DimensionScore(name="legacy_safety", raw_score=0.0, normalized_score=0.0, weight=0.15, formula_display="f", explanation="e"),
            DimensionScore(name="refactoring_debt", raw_score=0.0, normalized_score=0.0, weight=0.10, formula_display="f", explanation="e"),
        ]
        result = compute_overall_score(dimensions)
        assert result == pytest.approx(0.0)

    def test_missing_dimensions_redistribute_weights(self):
        """When dimensions are missing, redistribute weights proportionally."""
        # Only code_quality (0.20) and test_design (0.20) present.
        # Total original weight = 0.40, so each gets scaled:
        #   code_quality: 0.20/0.40 = 0.50, test_design: 0.20/0.40 = 0.50
        # health = (8*0.50 + 6*0.50) * 10 = 7.0 * 10 = 70.0
        dimensions = [
            DimensionScore(name="code_quality", raw_score=8.0, normalized_score=8.0, weight=0.20, formula_display="f", explanation="e"),
            DimensionScore(name="test_design", raw_score=6.0, normalized_score=6.0, weight=0.20, formula_display="f", explanation="e"),
        ]
        result = compute_overall_score(dimensions)
        assert result == pytest.approx(70.0)

    def test_single_dimension_scales_to_full_weight(self):
        """A single dimension gets weight 1.0 after redistribution."""
        dimensions = [
            DimensionScore(name="code_quality", raw_score=7.0, normalized_score=7.0, weight=0.20, formula_display="f", explanation="e"),
        ]
        result = compute_overall_score(dimensions)
        assert result == pytest.approx(70.0)

    def test_empty_dimensions_yield_zero(self):
        result = compute_overall_score([])
        assert result == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# 12. derive_rating (pure function)
# ---------------------------------------------------------------------------


class TestDeriveRating:
    def test_critical_at_zero(self):
        assert derive_rating(0.0) == "Critical"

    def test_critical_at_boundary(self):
        assert derive_rating(40.0) == "Critical"

    def test_needs_attention_just_above_forty(self):
        assert derive_rating(40.1) == "Needs Attention"

    def test_needs_attention_at_sixty(self):
        assert derive_rating(60.0) == "Needs Attention"

    def test_good_just_above_sixty(self):
        assert derive_rating(60.1) == "Good"

    def test_good_at_eighty(self):
        assert derive_rating(80.0) == "Good"

    def test_excellent_just_above_eighty(self):
        assert derive_rating(80.1) == "Excellent"

    def test_excellent_at_hundred(self):
        assert derive_rating(100.0) == "Excellent"


# ---------------------------------------------------------------------------
# 13. Sub-model immutability (frozen=True on every nested model)
# ---------------------------------------------------------------------------


class TestSubModelImmutability:
    """Verify that all sub-models are frozen (mutation raises ValidationError)."""

    def test_severity_distribution_is_frozen(self):
        model = SeverityDistribution(high=1, medium=2, low=3)
        with pytest.raises(ValidationError):
            model.high = 99

    def test_risk_distribution_is_frozen(self):
        model = RiskDistribution(low=1, medium=2, high=3)
        with pytest.raises(ValidationError):
            model.low = 99

    def test_code_smell_top_issue_is_frozen(self):
        model = CodeSmellTopIssue(file="a.py", issue="bad", severity="high", category="Bloaters")
        with pytest.raises(ValidationError):
            model.file = "other.py"

    def test_solid_compliance_is_frozen(self):
        model = SolidCompliance(SRP=7.0, OCP=7.0, LSP=7.0, ISP=7.0, DIP=7.0)
        with pytest.raises(ValidationError):
            model.SRP = 1.0

    def test_property_scores_is_frozen(self):
        model = PropertyScores(static=7.0, llm=7.0, blended=7.0)
        with pytest.raises(ValidationError):
            model.static = 1.0

    def test_tautology_counts_is_frozen(self):
        model = TautologyCounts(mock_tautology=0, mock_only=0, trivial=0, framework=0)
        with pytest.raises(ValidationError):
            model.mock_tautology = 99

    def test_test_design_worst_offender_is_frozen(self):
        model = TestDesignWorstOffender(file="test.py", score=4.0, issues=["bad"])
        with pytest.raises(ValidationError):
            model.file = "other.py"

    def test_cognitive_dimension_is_frozen(self):
        model = CognitiveDimension(raw="medium", normalized=5.5, weighted=1.1)
        with pytest.raises(ValidationError):
            model.raw = "high"

    def test_cognitive_worst_offender_is_frozen(self):
        model = CognitiveWorstOffender(file="a.py", score=50.0, primary_dimension="Structural")
        with pytest.raises(ValidationError):
            model.file = "other.py"

    def test_subdomain_distribution_is_frozen(self):
        model = SubdomainDistribution(core=2, supporting=1, generic=1)
        with pytest.raises(ValidationError):
            model.core = 99

    def test_ddd_anti_pattern_is_frozen(self):
        model = DDDAntiPattern(name="Bad", severity="High", location="module.py")
        with pytest.raises(ValidationError):
            model.name = "Other"

    def test_pattern_maturity_is_frozen(self):
        model = PatternMaturity(strategic=6.0, tactical=7.0, language=6.5, boundaries=5.5, events=7.5)
        with pytest.raises(ValidationError):
            model.strategic = 1.0

    def test_seam_availability_is_frozen(self):
        model = SeamAvailability(object=12, link=5, preprocessing=3)
        with pytest.raises(ValidationError):
            model.object = 99

    def test_module_at_risk_is_frozen(self):
        model = ModuleAtRisk(file="a.py", risk="High", dependencies=5, seams=2)
        with pytest.raises(ValidationError):
            model.file = "other.py"

    def test_priority_matrix_item_is_frozen(self):
        model = PriorityMatrixItem(item="Do X", impact="High", complexity="Low", risk="Medium")
        with pytest.raises(ValidationError):
            model.item = "Do Y"

    def test_implementation_sequence_item_is_frozen(self):
        model = ImplementationSequenceItem(order=1, item="Do X", rationale="Because")
        with pytest.raises(ValidationError):
            model.order = 2


# ---------------------------------------------------------------------------
# 14. Boundary value tests for field constraints (ge/le boundaries)
# ---------------------------------------------------------------------------


class TestSeverityDistributionBoundaries:
    """SeverityDistribution: high(ge=0), medium(ge=0), low(ge=0)."""

    @pytest.mark.parametrize("field", ["high", "medium", "low"])
    def test_zero_is_accepted(self, field):
        kwargs = {"high": 1, "medium": 1, "low": 1}
        kwargs[field] = 0
        model = SeverityDistribution(**kwargs)
        assert getattr(model, field) == 0

    @pytest.mark.parametrize("field", ["high", "medium", "low"])
    def test_negative_one_is_rejected(self, field):
        kwargs = {"high": 1, "medium": 1, "low": 1}
        kwargs[field] = -1
        with pytest.raises(ValidationError, match=field):
            SeverityDistribution(**kwargs)


class TestRiskDistributionBoundaries:
    """RiskDistribution: low(ge=0), medium(ge=0), high(ge=0)."""

    @pytest.mark.parametrize("field", ["low", "medium", "high"])
    def test_zero_is_accepted(self, field):
        kwargs = {"low": 1, "medium": 1, "high": 1}
        kwargs[field] = 0
        model = RiskDistribution(**kwargs)
        assert getattr(model, field) == 0

    @pytest.mark.parametrize("field", ["low", "medium", "high"])
    def test_negative_one_is_rejected(self, field):
        kwargs = {"low": 1, "medium": 1, "high": 1}
        kwargs[field] = -1
        with pytest.raises(ValidationError, match=field):
            RiskDistribution(**kwargs)


class TestSolidComplianceBoundaries:
    """SolidCompliance: SRP/OCP/LSP/ISP/DIP each ge=0, le=10."""

    @pytest.mark.parametrize("field", ["SRP", "OCP", "LSP", "ISP", "DIP"])
    def test_zero_is_accepted(self, field):
        kwargs = {"SRP": 5.0, "OCP": 5.0, "LSP": 5.0, "ISP": 5.0, "DIP": 5.0}
        kwargs[field] = 0.0
        model = SolidCompliance(**kwargs)
        assert getattr(model, field) == 0.0

    @pytest.mark.parametrize("field", ["SRP", "OCP", "LSP", "ISP", "DIP"])
    def test_ten_is_accepted(self, field):
        kwargs = {"SRP": 5.0, "OCP": 5.0, "LSP": 5.0, "ISP": 5.0, "DIP": 5.0}
        kwargs[field] = 10.0
        model = SolidCompliance(**kwargs)
        assert getattr(model, field) == 10.0

    @pytest.mark.parametrize("field", ["SRP", "OCP", "LSP", "ISP", "DIP"])
    def test_negative_is_rejected(self, field):
        kwargs = {"SRP": 5.0, "OCP": 5.0, "LSP": 5.0, "ISP": 5.0, "DIP": 5.0}
        kwargs[field] = -0.1
        with pytest.raises(ValidationError, match=field):
            SolidCompliance(**kwargs)

    @pytest.mark.parametrize("field", ["SRP", "OCP", "LSP", "ISP", "DIP"])
    def test_above_ten_is_rejected(self, field):
        kwargs = {"SRP": 5.0, "OCP": 5.0, "LSP": 5.0, "ISP": 5.0, "DIP": 5.0}
        kwargs[field] = 10.1
        with pytest.raises(ValidationError, match=field):
            SolidCompliance(**kwargs)


class TestCodeSmellDetectorDataBoundaries:
    """CodeSmellDetectorData: total_issues(ge=0)."""

    def test_total_issues_zero_is_accepted(self):
        data = _load_fixture("code-smell-detector-data.json")
        data["total_issues"] = 0
        model = CodeSmellDetectorData(**data)
        assert model.total_issues == 0


class TestTestDesignReviewerDataBoundaries:
    """TestDesignReviewerData: farley_index(ge=0, le=10)."""

    def test_farley_index_zero_is_accepted(self):
        data = _load_fixture("test-design-reviewer-data.json")
        data["farley_index"] = 0.0
        model = TestDesignReviewerData(**data)
        assert model.farley_index == 0.0

    def test_farley_index_ten_is_accepted(self):
        data = _load_fixture("test-design-reviewer-data.json")
        data["farley_index"] = 10.0
        model = TestDesignReviewerData(**data)
        assert model.farley_index == 10.0


class TestTautologyCountsBoundaries:
    """TautologyCounts: mock_tautology/mock_only/trivial/framework each ge=0."""

    @pytest.mark.parametrize("field", ["mock_tautology", "mock_only", "trivial", "framework"])
    def test_zero_is_accepted(self, field):
        kwargs = {"mock_tautology": 1, "mock_only": 1, "trivial": 1, "framework": 1}
        kwargs[field] = 0
        model = TautologyCounts(**kwargs)
        assert getattr(model, field) == 0

    @pytest.mark.parametrize("field", ["mock_tautology", "mock_only", "trivial", "framework"])
    def test_negative_one_is_rejected(self, field):
        kwargs = {"mock_tautology": 1, "mock_only": 1, "trivial": 1, "framework": 1}
        kwargs[field] = -1
        with pytest.raises(ValidationError, match=field):
            TautologyCounts(**kwargs)


class TestCognitiveLoadAnalyzerDataBoundaries:
    """CognitiveLoadAnalyzerData: cli_score(ge=0, le=1000)."""

    def test_cli_score_zero_is_accepted(self):
        data = _load_fixture("cognitive-load-analyzer-data.json")
        data["cli_score"] = 0
        model = CognitiveLoadAnalyzerData(**data)
        assert model.cli_score == 0

    def test_cli_score_thousand_is_accepted(self):
        data = _load_fixture("cognitive-load-analyzer-data.json")
        data["cli_score"] = 1000
        model = CognitiveLoadAnalyzerData(**data)
        assert model.cli_score == 1000


class TestDDDArchitectDataBoundaries:
    """DDDArchitectData: overall_score(ge=0,le=10), bounded_context_count(ge=0)."""

    def test_overall_score_zero_is_accepted(self):
        data = _load_fixture("ddd-architect-data.json")
        data["overall_score"] = 0.0
        model = DDDArchitectData(**data)
        assert model.overall_score == 0.0

    def test_overall_score_ten_is_accepted(self):
        data = _load_fixture("ddd-architect-data.json")
        data["overall_score"] = 10.0
        model = DDDArchitectData(**data)
        assert model.overall_score == 10.0

    def test_bounded_context_count_zero_is_accepted(self):
        data = _load_fixture("ddd-architect-data.json")
        data["bounded_context_count"] = 0
        model = DDDArchitectData(**data)
        assert model.bounded_context_count == 0

    def test_bounded_context_count_negative_is_rejected(self):
        data = _load_fixture("ddd-architect-data.json")
        data["bounded_context_count"] = -1
        with pytest.raises(ValidationError, match="bounded_context_count"):
            DDDArchitectData(**data)


class TestSubdomainDistributionBoundaries:
    """SubdomainDistribution: core/supporting/generic each ge=0."""

    @pytest.mark.parametrize("field", ["core", "supporting", "generic"])
    def test_zero_is_accepted(self, field):
        kwargs = {"core": 1, "supporting": 1, "generic": 1}
        kwargs[field] = 0
        model = SubdomainDistribution(**kwargs)
        assert getattr(model, field) == 0

    @pytest.mark.parametrize("field", ["core", "supporting", "generic"])
    def test_negative_one_is_rejected(self, field):
        kwargs = {"core": 1, "supporting": 1, "generic": 1}
        kwargs[field] = -1
        with pytest.raises(ValidationError, match=field):
            SubdomainDistribution(**kwargs)


class TestPatternMaturityBoundaries:
    """PatternMaturity: strategic/tactical/language/boundaries/events each ge=0, le=10."""

    @pytest.mark.parametrize("field", ["strategic", "tactical", "language", "boundaries", "events"])
    def test_zero_is_accepted(self, field):
        kwargs = {"strategic": 5.0, "tactical": 5.0, "language": 5.0, "boundaries": 5.0, "events": 5.0}
        kwargs[field] = 0.0
        model = PatternMaturity(**kwargs)
        assert getattr(model, field) == 0.0

    @pytest.mark.parametrize("field", ["strategic", "tactical", "language", "boundaries", "events"])
    def test_ten_is_accepted(self, field):
        kwargs = {"strategic": 5.0, "tactical": 5.0, "language": 5.0, "boundaries": 5.0, "events": 5.0}
        kwargs[field] = 10.0
        model = PatternMaturity(**kwargs)
        assert getattr(model, field) == 10.0

    @pytest.mark.parametrize("field", ["strategic", "tactical", "language", "boundaries", "events"])
    def test_negative_is_rejected(self, field):
        kwargs = {"strategic": 5.0, "tactical": 5.0, "language": 5.0, "boundaries": 5.0, "events": 5.0}
        kwargs[field] = -0.1
        with pytest.raises(ValidationError, match=field):
            PatternMaturity(**kwargs)

    @pytest.mark.parametrize("field", ["strategic", "tactical", "language", "boundaries", "events"])
    def test_above_ten_is_rejected(self, field):
        kwargs = {"strategic": 5.0, "tactical": 5.0, "language": 5.0, "boundaries": 5.0, "events": 5.0}
        kwargs[field] = 10.1
        with pytest.raises(ValidationError, match=field):
            PatternMaturity(**kwargs)


class TestLegacyCodeExpertDataBoundaries:
    """LegacyCodeExpertData: overall_score(ge=0,le=10), dependency_count(ge=0), testability_score(ge=0,le=1)."""

    def test_overall_score_zero_is_accepted(self):
        data = _load_fixture("legacy-code-expert-data.json")
        data["overall_score"] = 0.0
        model = LegacyCodeExpertData(**data)
        assert model.overall_score == 0.0

    def test_overall_score_ten_is_accepted(self):
        data = _load_fixture("legacy-code-expert-data.json")
        data["overall_score"] = 10.0
        model = LegacyCodeExpertData(**data)
        assert model.overall_score == 10.0

    def test_dependency_count_zero_is_accepted(self):
        data = _load_fixture("legacy-code-expert-data.json")
        data["dependency_count"] = 0
        model = LegacyCodeExpertData(**data)
        assert model.dependency_count == 0

    def test_dependency_count_negative_is_rejected(self):
        data = _load_fixture("legacy-code-expert-data.json")
        data["dependency_count"] = -1
        with pytest.raises(ValidationError, match="dependency_count"):
            LegacyCodeExpertData(**data)

    def test_testability_score_zero_is_accepted(self):
        data = _load_fixture("legacy-code-expert-data.json")
        data["testability_score"] = 0.0
        model = LegacyCodeExpertData(**data)
        assert model.testability_score == 0.0

    def test_testability_score_one_is_accepted(self):
        data = _load_fixture("legacy-code-expert-data.json")
        data["testability_score"] = 1.0
        model = LegacyCodeExpertData(**data)
        assert model.testability_score == 1.0


class TestSeamAvailabilityBoundaries:
    """SeamAvailability: object/link/preprocessing each ge=0."""

    @pytest.mark.parametrize("field", ["object", "link", "preprocessing"])
    def test_zero_is_accepted(self, field):
        kwargs = {"object": 1, "link": 1, "preprocessing": 1}
        kwargs[field] = 0
        model = SeamAvailability(**kwargs)
        assert getattr(model, field) == 0

    @pytest.mark.parametrize("field", ["object", "link", "preprocessing"])
    def test_negative_one_is_rejected(self, field):
        kwargs = {"object": 1, "link": 1, "preprocessing": 1}
        kwargs[field] = -1
        with pytest.raises(ValidationError, match=field):
            SeamAvailability(**kwargs)


class TestModuleAtRiskBoundaries:
    """ModuleAtRisk: dependencies(ge=0), seams(ge=0)."""

    @pytest.mark.parametrize("field", ["dependencies", "seams"])
    def test_zero_is_accepted(self, field):
        kwargs = {"file": "a.py", "risk": "High", "dependencies": 5, "seams": 2}
        kwargs[field] = 0
        model = ModuleAtRisk(**kwargs)
        assert getattr(model, field) == 0

    @pytest.mark.parametrize("field", ["dependencies", "seams"])
    def test_negative_one_is_rejected(self, field):
        kwargs = {"file": "a.py", "risk": "High", "dependencies": 5, "seams": 2}
        kwargs[field] = -1
        with pytest.raises(ValidationError, match=field):
            ModuleAtRisk(**kwargs)


class TestRefactoringExpertDataBoundaries:
    """RefactoringExpertData: total_recommendations(ge=0)."""

    def test_total_recommendations_zero_is_accepted(self):
        data = _load_fixture("refactoring-expert-data.json")
        data["total_recommendations"] = 0
        model = RefactoringExpertData(**data)
        assert model.total_recommendations == 0


class TestImplementationSequenceItemBoundaries:
    """ImplementationSequenceItem: order(ge=1)."""

    def test_order_one_is_accepted(self):
        model = ImplementationSequenceItem(order=1, item="Do X", rationale="Because")
        assert model.order == 1

    def test_order_zero_is_rejected(self):
        with pytest.raises(ValidationError, match="order"):
            ImplementationSequenceItem(order=0, item="Do X", rationale="Because")


class TestDimensionScoreBoundaries:
    """DimensionScore: normalized_score(ge=0,le=10), weight(ge=0,le=1)."""

    def test_normalized_score_zero_is_accepted(self):
        model = DimensionScore(
            name="x", raw_score=0.0, normalized_score=0.0, weight=0.2,
            formula_display="f", explanation="e",
        )
        assert model.normalized_score == 0.0

    def test_normalized_score_ten_is_accepted(self):
        model = DimensionScore(
            name="x", raw_score=10.0, normalized_score=10.0, weight=0.2,
            formula_display="f", explanation="e",
        )
        assert model.normalized_score == 10.0

    def test_weight_zero_is_accepted(self):
        model = DimensionScore(
            name="x", raw_score=5.0, normalized_score=5.0, weight=0.0,
            formula_display="f", explanation="e",
        )
        assert model.weight == 0.0

    def test_weight_one_is_accepted(self):
        model = DimensionScore(
            name="x", raw_score=5.0, normalized_score=5.0, weight=1.0,
            formula_display="f", explanation="e",
        )
        assert model.weight == 1.0


class TestReportDataBoundaries:
    """ReportData: overall_score(ge=0, le=100)."""

    def test_overall_score_zero_is_accepted(self):
        model = ReportData(
            metadata=_make_metadata(), dimensions=[], overall_score=0.0,
            rating="Critical", risk_assessments=[], agent_results={},
        )
        assert model.overall_score == 0.0

    def test_overall_score_hundred_is_accepted(self):
        model = ReportData(
            metadata=_make_metadata(), dimensions=[], overall_score=100.0,
            rating="Excellent", risk_assessments=[], agent_results={},
        )
        assert model.overall_score == 100.0
