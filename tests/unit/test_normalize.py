"""Unit tests for score normalization functions.

Tests validate that each normalization function:
- Transforms raw agent data into a DimensionScore with correct normalized_score
- Produces a formula_display string showing the calculation with actual values
- Produces an explanation string describing what the score means
- Clamps output to [0, 10] range
- Sets the correct dimension weight

Tests also validate the normalize_all orchestrator function.
"""

import json
from pathlib import Path

import pytest

from src.report.models import (
    CodeSmellDetectorData,
    CognitiveLoadAnalyzerData,
    DDDArchitectData,
    DimensionScore,
    LegacyCodeExpertData,
    RefactoringExpertData,
    TestDesignReviewerData,
)
from src.report.normalize import (
    normalize_code_quality,
    normalize_cognitive_load,
    normalize_ddd_compliance,
    normalize_legacy_safety,
    normalize_refactoring_debt,
    normalize_test_design,
    normalize_all,
)

FIXTURES_DIR = Path(__file__).parent.parent / "acceptance" / "codebase-analyzer" / "fixtures"


def _load_fixture(filename: str) -> dict:
    return json.loads((FIXTURES_DIR / filename).read_text())


# ---------------------------------------------------------------------------
# Helper: build minimal agent data models for targeted tests
# ---------------------------------------------------------------------------


def _make_code_smell(**overrides) -> CodeSmellDetectorData:
    defaults = {
        "grade": "B",
        "total_issues": 10,
        "severity_distribution": {"high": 1, "medium": 3, "low": 6},
        "category_distribution": {"Bloaters": 5, "Dispensables": 5},
        "solid_compliance": {"SRP": 7.0, "OCP": 7.0, "LSP": 7.0, "ISP": 7.0, "DIP": 7.0},
        "top_issues": [],
    }
    defaults.update(overrides)
    return CodeSmellDetectorData(**defaults)


def _make_cognitive_load(**overrides) -> CognitiveLoadAnalyzerData:
    defaults = {
        "cli_score": 312,
        "rating": "Moderate",
        "dimensions": {
            "Structural Complexity": {"raw": "medium", "normalized": 5.5, "weighted": 1.1},
        },
        "interaction_penalty": 0.15,
        "worst_offenders": [],
    }
    defaults.update(overrides)
    return CognitiveLoadAnalyzerData(**defaults)


def _make_refactoring(**overrides) -> RefactoringExpertData:
    defaults = {
        "total_recommendations": 14,
        "priority_matrix": [],
        "risk_distribution": {"low": 5, "medium": 7, "high": 2},
        "category_distribution": {"Architecture": 4},
        "implementation_sequence": [],
    }
    defaults.update(overrides)
    return RefactoringExpertData(**defaults)


# ---------------------------------------------------------------------------
# 1. normalize_code_quality: grade mapping
# ---------------------------------------------------------------------------


class TestNormalizeCodeQuality:
    """Grade mapping: A=10, B=8, C=6, D=4, F=2."""

    def test_grade_b_maps_to_eight(self):
        data = _make_code_smell(grade="B")
        result = normalize_code_quality(data)
        assert result.normalized_score == 8.0

    def test_grade_a_maps_to_ten(self):
        data = _make_code_smell(grade="A")
        result = normalize_code_quality(data)
        assert result.normalized_score == 10.0

    def test_grade_c_maps_to_six(self):
        data = _make_code_smell(grade="C")
        result = normalize_code_quality(data)
        assert result.normalized_score == 6.0

    def test_grade_d_maps_to_four(self):
        data = _make_code_smell(grade="D")
        result = normalize_code_quality(data)
        assert result.normalized_score == 4.0

    def test_grade_f_maps_to_two(self):
        data = _make_code_smell(grade="F")
        result = normalize_code_quality(data)
        assert result.normalized_score == 2.0

    def test_returns_dimension_score_with_correct_name(self):
        data = _make_code_smell(grade="B")
        result = normalize_code_quality(data)
        assert result.name == "code_quality"

    def test_returns_correct_weight(self):
        data = _make_code_smell(grade="B")
        result = normalize_code_quality(data)
        assert result.weight == 0.20

    def test_raw_score_is_grade_string(self):
        """Raw score stores the numeric mapping of the grade."""
        data = _make_code_smell(grade="B")
        result = normalize_code_quality(data)
        assert result.raw_score == 8.0

    def test_formula_display_shows_grade_mapping(self):
        data = _make_code_smell(grade="B")
        result = normalize_code_quality(data)
        assert "B" in result.formula_display
        assert "8.0" in result.formula_display

    def test_explanation_is_nonempty_string(self):
        data = _make_code_smell(grade="B")
        result = normalize_code_quality(data)
        assert isinstance(result.explanation, str)
        assert len(result.explanation) > 0

    def test_fixture_data_produces_expected_score(self):
        fixture = _load_fixture("code-smell-detector-data.json")
        data = CodeSmellDetectorData(**fixture)
        result = normalize_code_quality(data)
        assert result.normalized_score == 8.0


# ---------------------------------------------------------------------------
# 2. normalize_test_design: direct passthrough
# ---------------------------------------------------------------------------


class TestNormalizeTestDesign:
    """Farley Index direct passthrough (already 0-10 scale)."""

    def test_farley_index_passed_through_directly(self):
        data = TestDesignReviewerData(
            farley_index=7.2,
            rating="Good",
            properties={"Understandable": {"static": 7.0, "llm": 7.0, "blended": 7.0}},
            tautology_counts={"mock_tautology": 0, "mock_only": 0, "trivial": 0, "framework": 0},
            worst_offenders=[],
        )
        result = normalize_test_design(data)
        assert result.normalized_score == 7.2

    def test_returns_correct_name_and_weight(self):
        data = TestDesignReviewerData(
            farley_index=5.0,
            rating="Moderate",
            properties={"Understandable": {"static": 5.0, "llm": 5.0, "blended": 5.0}},
            tautology_counts={"mock_tautology": 0, "mock_only": 0, "trivial": 0, "framework": 0},
            worst_offenders=[],
        )
        result = normalize_test_design(data)
        assert result.name == "test_design"
        assert result.weight == 0.20

    def test_formula_display_shows_farley_index(self):
        data = TestDesignReviewerData(
            farley_index=7.2,
            rating="Good",
            properties={"Understandable": {"static": 7.0, "llm": 7.0, "blended": 7.0}},
            tautology_counts={"mock_tautology": 0, "mock_only": 0, "trivial": 0, "framework": 0},
            worst_offenders=[],
        )
        result = normalize_test_design(data)
        assert "7.2" in result.formula_display
        assert "Farley Index" in result.formula_display

    def test_fixture_data_produces_expected_score(self):
        fixture = _load_fixture("test-design-reviewer-data.json")
        data = TestDesignReviewerData(**fixture)
        result = normalize_test_design(data)
        assert result.normalized_score == 7.2


# ---------------------------------------------------------------------------
# 3. normalize_cognitive_load: 10 - cli_score/100, clamped [0, 10]
# ---------------------------------------------------------------------------


class TestNormalizeCognitiveLoad:
    """Formula: max(0, min(10, 10 - cli_score/100))."""

    def test_cli_score_312_produces_6_88(self):
        data = _make_cognitive_load(cli_score=312)
        result = normalize_cognitive_load(data)
        assert result.normalized_score == pytest.approx(6.88)

    def test_cli_score_0_produces_10(self):
        data = _make_cognitive_load(cli_score=0)
        result = normalize_cognitive_load(data)
        assert result.normalized_score == pytest.approx(10.0)

    def test_cli_score_1000_produces_0(self):
        data = _make_cognitive_load(cli_score=1000)
        result = normalize_cognitive_load(data)
        assert result.normalized_score == pytest.approx(0.0)

    def test_cli_score_500_produces_5(self):
        data = _make_cognitive_load(cli_score=500)
        result = normalize_cognitive_load(data)
        assert result.normalized_score == pytest.approx(5.0)

    def test_returns_correct_name_and_weight(self):
        data = _make_cognitive_load(cli_score=312)
        result = normalize_cognitive_load(data)
        assert result.name == "cognitive_load"
        assert result.weight == 0.20

    def test_formula_display_shows_calculation(self):
        data = _make_cognitive_load(cli_score=312)
        result = normalize_cognitive_load(data)
        assert "312" in result.formula_display
        assert "6.88" in result.formula_display

    def test_fixture_data_produces_expected_score(self):
        fixture = _load_fixture("cognitive-load-analyzer-data.json")
        data = CognitiveLoadAnalyzerData(**fixture)
        result = normalize_cognitive_load(data)
        assert result.normalized_score == pytest.approx(6.88)


# ---------------------------------------------------------------------------
# 4. normalize_ddd_compliance: direct passthrough
# ---------------------------------------------------------------------------


class TestNormalizeDddCompliance:
    """DDD overall score direct passthrough (agent self-assessed, 0-10)."""

    def test_overall_score_passed_through_directly(self):
        data = DDDArchitectData(
            overall_score=6.5,
            bounded_context_count=4,
            subdomain_distribution={"core": 2, "supporting": 1, "generic": 1},
            anti_patterns=[],
            pattern_maturity={"strategic": 6.0, "tactical": 7.0, "language": 6.5, "boundaries": 5.5, "events": 7.5},
            context_map_mermaid="graph LR",
        )
        result = normalize_ddd_compliance(data)
        assert result.normalized_score == 6.5

    def test_returns_correct_name_and_weight(self):
        data = DDDArchitectData(
            overall_score=6.5,
            bounded_context_count=4,
            subdomain_distribution={"core": 2, "supporting": 1, "generic": 1},
            anti_patterns=[],
            pattern_maturity={"strategic": 6.0, "tactical": 7.0, "language": 6.5, "boundaries": 5.5, "events": 7.5},
            context_map_mermaid="graph LR",
        )
        result = normalize_ddd_compliance(data)
        assert result.name == "ddd_compliance"
        assert result.weight == 0.15

    def test_formula_display_shows_score(self):
        data = DDDArchitectData(
            overall_score=6.5,
            bounded_context_count=4,
            subdomain_distribution={"core": 2, "supporting": 1, "generic": 1},
            anti_patterns=[],
            pattern_maturity={"strategic": 6.0, "tactical": 7.0, "language": 6.5, "boundaries": 5.5, "events": 7.5},
            context_map_mermaid="graph LR",
        )
        result = normalize_ddd_compliance(data)
        assert "6.5" in result.formula_display

    def test_fixture_data_produces_expected_score(self):
        fixture = _load_fixture("ddd-architect-data.json")
        data = DDDArchitectData(**fixture)
        result = normalize_ddd_compliance(data)
        assert result.normalized_score == 6.5


# ---------------------------------------------------------------------------
# 5. normalize_legacy_safety: direct passthrough
# ---------------------------------------------------------------------------


class TestNormalizeLegacySafety:
    """Legacy overall score direct passthrough (agent self-assessed, 0-10)."""

    def test_overall_score_passed_through_directly(self):
        data = LegacyCodeExpertData(
            overall_score=5.5,
            risk_level="Medium",
            dependency_count=47,
            testability_score=0.62,
            seam_availability={"object": 12, "link": 5, "preprocessing": 3},
            modules_at_risk=[],
        )
        result = normalize_legacy_safety(data)
        assert result.normalized_score == 5.5

    def test_returns_correct_name_and_weight(self):
        data = LegacyCodeExpertData(
            overall_score=5.5,
            risk_level="Medium",
            dependency_count=47,
            testability_score=0.62,
            seam_availability={"object": 12, "link": 5, "preprocessing": 3},
            modules_at_risk=[],
        )
        result = normalize_legacy_safety(data)
        assert result.name == "legacy_safety"
        assert result.weight == 0.15

    def test_formula_display_shows_score(self):
        data = LegacyCodeExpertData(
            overall_score=5.5,
            risk_level="Medium",
            dependency_count=47,
            testability_score=0.62,
            seam_availability={"object": 12, "link": 5, "preprocessing": 3},
            modules_at_risk=[],
        )
        result = normalize_legacy_safety(data)
        assert "5.5" in result.formula_display

    def test_fixture_data_produces_expected_score(self):
        fixture = _load_fixture("legacy-code-expert-data.json")
        data = LegacyCodeExpertData(**fixture)
        result = normalize_legacy_safety(data)
        assert result.normalized_score == 5.5


# ---------------------------------------------------------------------------
# 6. normalize_refactoring_debt: weighted risk count formula
# ---------------------------------------------------------------------------


class TestNormalizeRefactoringDebt:
    """Formula: max(0, 10 - weighted_count / 5)
    where weighted_count = high*3 + medium*2 + low*1.
    """

    def test_fixture_risk_distribution_produces_5_0(self):
        """risk_distribution: {low: 5, medium: 7, high: 2}
        weighted = 2*3 + 7*2 + 5*1 = 6 + 14 + 5 = 25
        score = max(0, 10 - 25/5) = max(0, 5.0) = 5.0
        """
        data = _make_refactoring(
            risk_distribution={"low": 5, "medium": 7, "high": 2},
        )
        result = normalize_refactoring_debt(data)
        assert result.normalized_score == pytest.approx(5.0)

    def test_all_zeros_produces_ten(self):
        """No recommendations at all -> weighted = 0 -> score = 10."""
        data = _make_refactoring(
            risk_distribution={"low": 0, "medium": 0, "high": 0},
        )
        result = normalize_refactoring_debt(data)
        assert result.normalized_score == pytest.approx(10.0)

    def test_heavy_debt_clamps_to_zero(self):
        """weighted = 20*3 = 60 -> 10 - 60/5 = 10 - 12 = -2 -> clamped to 0."""
        data = _make_refactoring(
            risk_distribution={"low": 0, "medium": 0, "high": 20},
        )
        result = normalize_refactoring_debt(data)
        assert result.normalized_score == pytest.approx(0.0)

    def test_moderate_debt(self):
        """weighted = 1*3 + 2*2 + 3*1 = 3 + 4 + 3 = 10
        score = max(0, 10 - 10/5) = max(0, 8.0) = 8.0
        """
        data = _make_refactoring(
            risk_distribution={"low": 3, "medium": 2, "high": 1},
        )
        result = normalize_refactoring_debt(data)
        assert result.normalized_score == pytest.approx(8.0)

    def test_returns_correct_name_and_weight(self):
        data = _make_refactoring()
        result = normalize_refactoring_debt(data)
        assert result.name == "refactoring_debt"
        assert result.weight == 0.10

    def test_formula_display_shows_weighted_calculation(self):
        data = _make_refactoring(
            risk_distribution={"low": 5, "medium": 7, "high": 2},
        )
        result = normalize_refactoring_debt(data)
        assert "5.0" in result.formula_display

    def test_fixture_data_produces_expected_score(self):
        fixture = _load_fixture("refactoring-expert-data.json")
        data = RefactoringExpertData(**fixture)
        result = normalize_refactoring_debt(data)
        assert result.normalized_score == pytest.approx(5.0)


# ---------------------------------------------------------------------------
# 7. normalize_all: orchestrator
# ---------------------------------------------------------------------------


class TestNormalizeAll:
    """normalize_all dispatches to correct normalizer per agent key."""

    def test_all_six_agents_produce_six_dimension_scores(self):
        results = {
            "code_smell_detector": CodeSmellDetectorData(**_load_fixture("code-smell-detector-data.json")),
            "test_design_reviewer": TestDesignReviewerData(**_load_fixture("test-design-reviewer-data.json")),
            "cognitive_load_analyzer": CognitiveLoadAnalyzerData(**_load_fixture("cognitive-load-analyzer-data.json")),
            "ddd_architect": DDDArchitectData(**_load_fixture("ddd-architect-data.json")),
            "legacy_code_expert": LegacyCodeExpertData(**_load_fixture("legacy-code-expert-data.json")),
            "refactoring_expert": RefactoringExpertData(**_load_fixture("refactoring-expert-data.json")),
        }
        scores = normalize_all(results)
        assert len(scores) == 6
        assert all(isinstance(score, DimensionScore) for score in scores)

    def test_partial_agents_produce_partial_scores(self):
        results = {
            "code_smell_detector": CodeSmellDetectorData(**_load_fixture("code-smell-detector-data.json")),
            "test_design_reviewer": TestDesignReviewerData(**_load_fixture("test-design-reviewer-data.json")),
        }
        scores = normalize_all(results)
        assert len(scores) == 2

    def test_empty_dict_produces_empty_list(self):
        scores = normalize_all({})
        assert scores == []

    def test_unknown_agent_keys_are_skipped(self):
        results = {
            "code_smell_detector": CodeSmellDetectorData(**_load_fixture("code-smell-detector-data.json")),
            "unknown_agent": {"some": "data"},
        }
        scores = normalize_all(results)
        assert len(scores) == 1

    def test_dimension_names_are_correct(self):
        results = {
            "code_smell_detector": CodeSmellDetectorData(**_load_fixture("code-smell-detector-data.json")),
            "test_design_reviewer": TestDesignReviewerData(**_load_fixture("test-design-reviewer-data.json")),
            "cognitive_load_analyzer": CognitiveLoadAnalyzerData(**_load_fixture("cognitive-load-analyzer-data.json")),
            "ddd_architect": DDDArchitectData(**_load_fixture("ddd-architect-data.json")),
            "legacy_code_expert": LegacyCodeExpertData(**_load_fixture("legacy-code-expert-data.json")),
            "refactoring_expert": RefactoringExpertData(**_load_fixture("refactoring-expert-data.json")),
        }
        scores = normalize_all(results)
        names = {score.name for score in scores}
        assert names == {
            "code_quality",
            "test_design",
            "cognitive_load",
            "ddd_compliance",
            "legacy_safety",
            "refactoring_debt",
        }

    def test_all_scores_within_zero_to_ten(self):
        results = {
            "code_smell_detector": CodeSmellDetectorData(**_load_fixture("code-smell-detector-data.json")),
            "test_design_reviewer": TestDesignReviewerData(**_load_fixture("test-design-reviewer-data.json")),
            "cognitive_load_analyzer": CognitiveLoadAnalyzerData(**_load_fixture("cognitive-load-analyzer-data.json")),
            "ddd_architect": DDDArchitectData(**_load_fixture("ddd-architect-data.json")),
            "legacy_code_expert": LegacyCodeExpertData(**_load_fixture("legacy-code-expert-data.json")),
            "refactoring_expert": RefactoringExpertData(**_load_fixture("refactoring-expert-data.json")),
        }
        scores = normalize_all(results)
        for score in scores:
            assert 0.0 <= score.normalized_score <= 10.0, (
                f"{score.name} score {score.normalized_score} out of [0, 10]"
            )

    def test_weights_sum_to_one(self):
        results = {
            "code_smell_detector": CodeSmellDetectorData(**_load_fixture("code-smell-detector-data.json")),
            "test_design_reviewer": TestDesignReviewerData(**_load_fixture("test-design-reviewer-data.json")),
            "cognitive_load_analyzer": CognitiveLoadAnalyzerData(**_load_fixture("cognitive-load-analyzer-data.json")),
            "ddd_architect": DDDArchitectData(**_load_fixture("ddd-architect-data.json")),
            "legacy_code_expert": LegacyCodeExpertData(**_load_fixture("legacy-code-expert-data.json")),
            "refactoring_expert": RefactoringExpertData(**_load_fixture("refactoring-expert-data.json")),
        }
        scores = normalize_all(results)
        total_weight = sum(score.weight for score in scores)
        assert total_weight == pytest.approx(1.0)
