"""Content-validation tests for JSON data output sections in agent markdown definitions.

Each of the 6 analysis agents must include a JSON Data Output section in its
markdown definition file instructing it to write a structured JSON data file
alongside the existing markdown report.  These tests verify that:

- Each agent .md file contains the JSON output section
- The correct output filename is specified
- All required schema fields are referenced
- DDD and legacy agents include overall_score instructions
- Existing behavior preservation is documented
"""

from pathlib import Path

import pytest

AGENTS_DIR = Path(__file__).parent.parent.parent.parent / "claude-code-agents"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_agent_content(relative_path: str) -> str:
    """Load an agent markdown file, asserting it exists."""
    path = AGENTS_DIR / relative_path
    assert path.exists(), f"Agent definition file not found at {path}"
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def code_smell_detector_content() -> str:
    return _load_agent_content("alf-code-smell-detector/alf-code-smell-detector.md")


@pytest.fixture
def test_design_reviewer_content() -> str:
    return _load_agent_content("alf-test-design-reviewer/alf-test-design-reviewer.md")


@pytest.fixture
def cognitive_load_analyzer_content() -> str:
    return _load_agent_content("alf-cognitive-load-analyzer/alf-cognitive-load-analyzer.md")


@pytest.fixture
def ddd_architect_content() -> str:
    return _load_agent_content("alf-ddd-assessor/alf-ddd-assessor.md")


@pytest.fixture
def legacy_code_expert_content() -> str:
    return _load_agent_content("alf-legacy-code-analyzer/alf-legacy-code-analyzer.md")


@pytest.fixture
def refactoring_expert_content() -> str:
    return _load_agent_content("alf-refactoring-advisor/alf-refactoring-advisor.md")


# ---------------------------------------------------------------------------
# 1. Code Smell Detector
# ---------------------------------------------------------------------------


class TestCodeSmellDetectorJsonOutput:
    """Verify code-smell-detector.md contains JSON data output instructions."""

    def test_has_json_output_section(self, code_smell_detector_content: str):
        assert "json data output" in code_smell_detector_content.lower(), (
            "code-smell-detector.md must contain a JSON Data Output section"
        )

    def test_specifies_correct_output_filename(self, code_smell_detector_content: str):
        assert "code-smell-detector-data.json" in code_smell_detector_content, (
            "Must specify output filename code-smell-detector-data.json"
        )

    def test_includes_grade_field(self, code_smell_detector_content: str):
        assert '"grade"' in code_smell_detector_content, (
            "Must reference the 'grade' field in the JSON schema"
        )

    def test_includes_total_issues_field(self, code_smell_detector_content: str):
        assert '"total_issues"' in code_smell_detector_content, (
            "Must reference the 'total_issues' field in the JSON schema"
        )

    def test_includes_severity_distribution_field(self, code_smell_detector_content: str):
        assert '"severity_distribution"' in code_smell_detector_content, (
            "Must reference the 'severity_distribution' field in the JSON schema"
        )

    def test_includes_category_distribution_field(self, code_smell_detector_content: str):
        assert '"category_distribution"' in code_smell_detector_content, (
            "Must reference the 'category_distribution' field in the JSON schema"
        )

    def test_includes_solid_compliance_field(self, code_smell_detector_content: str):
        assert '"solid_compliance"' in code_smell_detector_content, (
            "Must reference the 'solid_compliance' field in the JSON schema"
        )

    def test_includes_top_issues_field(self, code_smell_detector_content: str):
        assert '"top_issues"' in code_smell_detector_content, (
            "Must reference the 'top_issues' field in the JSON schema"
        )

    def test_preserves_existing_behavior(self, code_smell_detector_content: str):
        content_lower = code_smell_detector_content.lower()
        assert "existing" in content_lower and ("unchanged" in content_lower or "preserve" in content_lower), (
            "Must document that existing markdown output behavior is preserved"
        )


# ---------------------------------------------------------------------------
# 2. Test Design Reviewer
# ---------------------------------------------------------------------------


class TestTestDesignReviewerJsonOutput:
    """Verify test-design-reviewer.md contains JSON data output instructions."""

    def test_has_json_output_section(self, test_design_reviewer_content: str):
        assert "json data output" in test_design_reviewer_content.lower(), (
            "test-design-reviewer.md must contain a JSON Data Output section"
        )

    def test_specifies_correct_output_filename(self, test_design_reviewer_content: str):
        assert "test-design-reviewer-data.json" in test_design_reviewer_content, (
            "Must specify output filename test-design-reviewer-data.json"
        )

    def test_includes_farley_index_field(self, test_design_reviewer_content: str):
        assert '"farley_index"' in test_design_reviewer_content, (
            "Must reference the 'farley_index' field in the JSON schema"
        )

    def test_includes_rating_field(self, test_design_reviewer_content: str):
        assert '"rating"' in test_design_reviewer_content, (
            "Must reference the 'rating' field in the JSON schema"
        )

    def test_includes_properties_field(self, test_design_reviewer_content: str):
        assert '"properties"' in test_design_reviewer_content, (
            "Must reference the 'properties' field in the JSON schema"
        )

    def test_includes_tautology_counts_field(self, test_design_reviewer_content: str):
        assert '"tautology_counts"' in test_design_reviewer_content, (
            "Must reference the 'tautology_counts' field in the JSON schema"
        )

    def test_includes_worst_offenders_field(self, test_design_reviewer_content: str):
        assert '"worst_offenders"' in test_design_reviewer_content, (
            "Must reference the 'worst_offenders' field in the JSON schema"
        )

    def test_preserves_existing_behavior(self, test_design_reviewer_content: str):
        content_lower = test_design_reviewer_content.lower()
        assert "existing" in content_lower and ("unchanged" in content_lower or "preserve" in content_lower), (
            "Must document that existing report behavior is preserved"
        )


# ---------------------------------------------------------------------------
# 3. Cognitive Load Analyzer
# ---------------------------------------------------------------------------


class TestCognitiveLoadAnalyzerJsonOutput:
    """Verify cognitive-load-analyzer.md contains JSON data output instructions."""

    def test_has_json_output_section(self, cognitive_load_analyzer_content: str):
        assert "json data output" in cognitive_load_analyzer_content.lower(), (
            "cognitive-load-analyzer.md must contain a JSON Data Output section"
        )

    def test_specifies_correct_output_filename(self, cognitive_load_analyzer_content: str):
        assert "cognitive-load-analyzer-data.json" in cognitive_load_analyzer_content, (
            "Must specify output filename cognitive-load-analyzer-data.json"
        )

    def test_includes_cli_score_field(self, cognitive_load_analyzer_content: str):
        assert '"cli_score"' in cognitive_load_analyzer_content, (
            "Must reference the 'cli_score' field in the JSON schema"
        )

    def test_includes_rating_field(self, cognitive_load_analyzer_content: str):
        assert '"rating"' in cognitive_load_analyzer_content, (
            "Must reference the 'rating' field in the JSON schema"
        )

    def test_includes_dimensions_field(self, cognitive_load_analyzer_content: str):
        assert '"dimensions"' in cognitive_load_analyzer_content, (
            "Must reference the 'dimensions' field in the JSON schema"
        )

    def test_includes_interaction_penalty_field(self, cognitive_load_analyzer_content: str):
        assert '"interaction_penalty"' in cognitive_load_analyzer_content, (
            "Must reference the 'interaction_penalty' field in the JSON schema"
        )

    def test_includes_worst_offenders_field(self, cognitive_load_analyzer_content: str):
        assert '"worst_offenders"' in cognitive_load_analyzer_content, (
            "Must reference the 'worst_offenders' field in the JSON schema"
        )

    def test_preserves_existing_behavior(self, cognitive_load_analyzer_content: str):
        content_lower = cognitive_load_analyzer_content.lower()
        assert "existing" in content_lower and ("unchanged" in content_lower or "preserve" in content_lower), (
            "Must document that existing report behavior is preserved"
        )


# ---------------------------------------------------------------------------
# 4. DDD Architect
# ---------------------------------------------------------------------------


class TestDDDArchitectJsonOutput:
    """Verify ddd-architect-agent.md contains JSON data output instructions."""

    def test_has_json_output_section(self, ddd_architect_content: str):
        assert "json data output" in ddd_architect_content.lower(), (
            "ddd-architect-agent.md must contain a JSON Data Output section"
        )

    def test_specifies_correct_output_filename(self, ddd_architect_content: str):
        assert "ddd-architect-data.json" in ddd_architect_content, (
            "Must specify output filename ddd-architect-data.json"
        )

    def test_includes_overall_score_field(self, ddd_architect_content: str):
        assert '"overall_score"' in ddd_architect_content, (
            "Must reference the 'overall_score' field in the JSON schema"
        )

    def test_includes_bounded_context_count_field(self, ddd_architect_content: str):
        assert '"bounded_context_count"' in ddd_architect_content, (
            "Must reference the 'bounded_context_count' field in the JSON schema"
        )

    def test_includes_subdomain_distribution_field(self, ddd_architect_content: str):
        assert '"subdomain_distribution"' in ddd_architect_content, (
            "Must reference the 'subdomain_distribution' field in the JSON schema"
        )

    def test_includes_anti_patterns_field(self, ddd_architect_content: str):
        assert '"anti_patterns"' in ddd_architect_content, (
            "Must reference the 'anti_patterns' field in the JSON schema"
        )

    def test_includes_pattern_maturity_field(self, ddd_architect_content: str):
        assert '"pattern_maturity"' in ddd_architect_content, (
            "Must reference the 'pattern_maturity' field in the JSON schema"
        )

    def test_includes_context_map_mermaid_field(self, ddd_architect_content: str):
        assert '"context_map_mermaid"' in ddd_architect_content, (
            "Must reference the 'context_map_mermaid' field in the JSON schema"
        )

    def test_includes_overall_score_rubric_justification(self, ddd_architect_content: str):
        content_lower = ddd_architect_content.lower()
        assert "overall_score" in content_lower and "rubric" in content_lower, (
            "DDD agent must include overall_score with rubric justification instructions"
        )

    def test_preserves_existing_behavior(self, ddd_architect_content: str):
        content_lower = ddd_architect_content.lower()
        assert "existing" in content_lower and ("unchanged" in content_lower or "preserve" in content_lower), (
            "Must document that existing report behavior is preserved"
        )


# ---------------------------------------------------------------------------
# 5. Legacy Code Expert
# ---------------------------------------------------------------------------


class TestLegacyCodeExpertJsonOutput:
    """Verify legacy-code-expert.md contains JSON data output instructions."""

    def test_has_json_output_section(self, legacy_code_expert_content: str):
        assert "json data output" in legacy_code_expert_content.lower(), (
            "legacy-code-expert.md must contain a JSON Data Output section"
        )

    def test_specifies_correct_output_filename(self, legacy_code_expert_content: str):
        assert "legacy-code-expert-data.json" in legacy_code_expert_content, (
            "Must specify output filename legacy-code-expert-data.json"
        )

    def test_includes_overall_score_field(self, legacy_code_expert_content: str):
        assert '"overall_score"' in legacy_code_expert_content, (
            "Must reference the 'overall_score' field in the JSON schema"
        )

    def test_includes_risk_level_field(self, legacy_code_expert_content: str):
        assert '"risk_level"' in legacy_code_expert_content, (
            "Must reference the 'risk_level' field in the JSON schema"
        )

    def test_includes_dependency_count_field(self, legacy_code_expert_content: str):
        assert '"dependency_count"' in legacy_code_expert_content, (
            "Must reference the 'dependency_count' field in the JSON schema"
        )

    def test_includes_testability_score_field(self, legacy_code_expert_content: str):
        assert '"testability_score"' in legacy_code_expert_content, (
            "Must reference the 'testability_score' field in the JSON schema"
        )

    def test_includes_seam_availability_field(self, legacy_code_expert_content: str):
        assert '"seam_availability"' in legacy_code_expert_content, (
            "Must reference the 'seam_availability' field in the JSON schema"
        )

    def test_includes_modules_at_risk_field(self, legacy_code_expert_content: str):
        assert '"modules_at_risk"' in legacy_code_expert_content, (
            "Must reference the 'modules_at_risk' field in the JSON schema"
        )

    def test_includes_overall_score_rubric_justification(self, legacy_code_expert_content: str):
        content_lower = legacy_code_expert_content.lower()
        assert "overall_score" in content_lower and "rubric" in content_lower, (
            "Legacy agent must include overall_score with rubric justification instructions"
        )

    def test_preserves_existing_behavior(self, legacy_code_expert_content: str):
        content_lower = legacy_code_expert_content.lower()
        assert "existing" in content_lower and ("unchanged" in content_lower or "preserve" in content_lower), (
            "Must document that existing report behavior is preserved"
        )


# ---------------------------------------------------------------------------
# 6. Refactoring Expert
# ---------------------------------------------------------------------------


class TestRefactoringExpertJsonOutput:
    """Verify refactoring-expert.md contains JSON data output instructions."""

    def test_has_json_output_section(self, refactoring_expert_content: str):
        assert "json data output" in refactoring_expert_content.lower(), (
            "refactoring-expert.md must contain a JSON Data Output section"
        )

    def test_specifies_correct_output_filename(self, refactoring_expert_content: str):
        assert "refactoring-expert-data.json" in refactoring_expert_content, (
            "Must specify output filename refactoring-expert-data.json"
        )

    def test_includes_total_recommendations_field(self, refactoring_expert_content: str):
        assert '"total_recommendations"' in refactoring_expert_content, (
            "Must reference the 'total_recommendations' field in the JSON schema"
        )

    def test_includes_priority_matrix_field(self, refactoring_expert_content: str):
        assert '"priority_matrix"' in refactoring_expert_content, (
            "Must reference the 'priority_matrix' field in the JSON schema"
        )

    def test_includes_risk_distribution_field(self, refactoring_expert_content: str):
        assert '"risk_distribution"' in refactoring_expert_content, (
            "Must reference the 'risk_distribution' field in the JSON schema"
        )

    def test_includes_category_distribution_field(self, refactoring_expert_content: str):
        assert '"category_distribution"' in refactoring_expert_content, (
            "Must reference the 'category_distribution' field in the JSON schema"
        )

    def test_includes_implementation_sequence_field(self, refactoring_expert_content: str):
        assert '"implementation_sequence"' in refactoring_expert_content, (
            "Must reference the 'implementation_sequence' field in the JSON schema"
        )

    def test_preserves_existing_behavior(self, refactoring_expert_content: str):
        content_lower = refactoring_expert_content.lower()
        assert "existing" in content_lower and ("unchanged" in content_lower or "preserve" in content_lower), (
            "Must document that existing report behavior is preserved"
        )
