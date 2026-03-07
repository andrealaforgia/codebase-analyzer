"""Integration tests for the report generation pipeline.

Tests validate the composition pipeline that chains all pure functions:
- load_agent_results reads and validates agent JSON files
- build_report_data assembles ReportData from validated agent results
- generate_report orchestrates the full pipeline from directory to HTML file

Testing strategy:
- load_agent_results: example-based (IO boundary, uses real fixture files)
- build_report_data: example-based (pure function, verifies composition)
- generate_report: example-based (end-to-end integration)
"""

import json
from pathlib import Path

import pytest

from src.report.models import ReportData
from src.report.pipeline import (
    AGENT_FILE_MAP,
    build_report_data,
    generate_report,
    load_agent_results,
)


FIXTURES_DIR = Path(__file__).resolve().parent.parent / "acceptance" / "codebase-analyzer" / "fixtures"


# ---------------------------------------------------------------------------
# load_agent_results
# ---------------------------------------------------------------------------


class TestLoadAgentResults:
    """Tests for reading and validating agent JSON files from a directory."""

    def test_loads_all_six_agents_from_fixtures_directory(self):
        results, messages = load_agent_results(str(FIXTURES_DIR))
        assert len(results) == 6
        assert len(messages) == 0

    def test_returns_empty_dict_and_messages_for_empty_directory(self, tmp_path):
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        results, messages = load_agent_results(str(empty_dir))
        assert results == {}
        assert len(messages) == 6  # one message per missing agent

    def test_returns_partial_results_when_some_files_missing(self, tmp_path):
        partial_dir = tmp_path / "partial"
        partial_dir.mkdir()
        # Copy only code-smell-detector and test-design-reviewer
        for filename in ["code-smell-detector-data.json", "test-design-reviewer-data.json"]:
            source = FIXTURES_DIR / filename
            dest = partial_dir / filename
            dest.write_text(source.read_text())
        results, messages = load_agent_results(str(partial_dir))
        assert len(results) == 2
        assert "code_smell_detector" in results
        assert "test_design_reviewer" in results
        assert len(messages) == 4  # four missing agents

    def test_captures_validation_error_for_malformed_json(self, tmp_path):
        malformed_dir = tmp_path / "malformed"
        malformed_dir.mkdir()
        # Write a file with invalid data (missing required fields)
        bad_file = malformed_dir / "code-smell-detector-data.json"
        bad_file.write_text(json.dumps({"grade": "X", "total_issues": -1}))
        results, messages = load_agent_results(str(malformed_dir))
        assert "code_smell_detector" not in results
        assert any("code_smell_detector" in msg for msg in messages)

    def test_captures_invalid_json_syntax_without_raising(self, tmp_path):
        bad_dir = tmp_path / "bad-json"
        bad_dir.mkdir()
        bad_file = bad_dir / "code-smell-detector-data.json"
        bad_file.write_text("{not valid json")
        results, messages = load_agent_results(str(bad_dir))
        assert "code_smell_detector" not in results
        assert any("code_smell_detector" in msg for msg in messages)

    def test_result_values_are_validated_pydantic_models(self):
        results, _ = load_agent_results(str(FIXTURES_DIR))
        from src.report.models import CodeSmellDetectorData
        assert isinstance(results["code_smell_detector"], CodeSmellDetectorData)

    def test_all_agent_keys_present_in_file_map(self):
        expected_keys = {
            "code_smell_detector",
            "test_design_reviewer",
            "cognitive_load_analyzer",
            "ddd_architect",
            "legacy_code_expert",
            "refactoring_expert",
        }
        assert set(AGENT_FILE_MAP.keys()) == expected_keys


# ---------------------------------------------------------------------------
# build_report_data
# ---------------------------------------------------------------------------


class TestBuildReportData:
    """Tests for the pure function that assembles ReportData from agent results."""

    def test_produces_valid_report_data_with_all_agents(self):
        results, _ = load_agent_results(str(FIXTURES_DIR))
        report_data = build_report_data(results, "Test Project", "/tmp/target")
        assert isinstance(report_data, ReportData)
        assert report_data.metadata.project_name == "Test Project"
        assert report_data.metadata.target_directory == "/tmp/target"

    def test_produces_six_dimension_scores_with_all_agents(self):
        results, _ = load_agent_results(str(FIXTURES_DIR))
        report_data = build_report_data(results, "Test Project", "/tmp/target")
        assert len(report_data.dimensions) == 6

    def test_overall_score_is_between_zero_and_hundred(self):
        results, _ = load_agent_results(str(FIXTURES_DIR))
        report_data = build_report_data(results, "Test Project", "/tmp/target")
        assert 0.0 <= report_data.overall_score <= 100.0

    def test_rating_is_valid_category(self):
        results, _ = load_agent_results(str(FIXTURES_DIR))
        report_data = build_report_data(results, "Test Project", "/tmp/target")
        assert report_data.rating in ("Critical", "Needs Attention", "Good", "Excellent")

    def test_produces_three_risk_assessments(self):
        results, _ = load_agent_results(str(FIXTURES_DIR))
        report_data = build_report_data(results, "Test Project", "/tmp/target")
        assert len(report_data.risk_assessments) == 3
        risk_names = {r.name for r in report_data.risk_assessments}
        assert risk_names == {
            "Delivery Velocity Risk",
            "Incident Risk",
            "Onboarding Risk",
        }

    def test_handles_partial_results_without_error(self):
        results, _ = load_agent_results(str(FIXTURES_DIR))
        # Remove some agents
        partial = {"code_smell_detector": results["code_smell_detector"]}
        report_data = build_report_data(partial, "Partial Project", "/tmp")
        assert isinstance(report_data, ReportData)
        assert len(report_data.dimensions) == 1

    def test_handles_empty_results(self):
        report_data = build_report_data({}, "Empty Project", "/tmp")
        assert isinstance(report_data, ReportData)
        assert len(report_data.dimensions) == 0
        assert report_data.overall_score == 0.0

    def test_agent_results_preserved_in_report_data(self):
        results, _ = load_agent_results(str(FIXTURES_DIR))
        report_data = build_report_data(results, "Test Project", "/tmp/target")
        assert "code_smell_detector" in report_data.agent_results
        assert len(report_data.agent_results) == 6


# ---------------------------------------------------------------------------
# generate_report (end-to-end integration)
# ---------------------------------------------------------------------------


class TestGenerateReport:
    """End-to-end tests for the full pipeline: directory -> HTML file."""

    def test_produces_html_file_from_fixtures_directory(self, tmp_path):
        output_path = str(tmp_path / "report.html")
        exit_code = generate_report(str(FIXTURES_DIR), output_path)
        assert exit_code == 0
        assert Path(output_path).exists()
        content = Path(output_path).read_text()
        assert len(content) > 0
        assert "<html" in content.lower()

    def test_returns_nonzero_when_no_agent_files_exist(self, tmp_path):
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        output_path = str(tmp_path / "report.html")
        exit_code = generate_report(str(empty_dir), output_path)
        assert exit_code == 1
        assert not Path(output_path).exists()

    def test_returns_zero_with_partial_results(self, tmp_path):
        partial_dir = tmp_path / "partial"
        partial_dir.mkdir()
        # Copy only two agent files
        for filename in ["code-smell-detector-data.json", "test-design-reviewer-data.json"]:
            source = FIXTURES_DIR / filename
            dest = partial_dir / filename
            dest.write_text(source.read_text())
        output_path = str(tmp_path / "report.html")
        exit_code = generate_report(str(partial_dir), output_path)
        assert exit_code == 0
        assert Path(output_path).exists()

    def test_default_project_name_is_codebase_analysis(self, tmp_path):
        output_path = str(tmp_path / "report.html")
        exit_code = generate_report(str(FIXTURES_DIR), output_path)
        assert exit_code == 0
        content = Path(output_path).read_text()
        assert "Codebase Analysis" in content

    def test_custom_project_name_appears_in_report(self, tmp_path):
        output_path = str(tmp_path / "report.html")
        exit_code = generate_report(
            str(FIXTURES_DIR), output_path, project_name="My Custom Project"
        )
        assert exit_code == 0
        content = Path(output_path).read_text()
        assert "My Custom Project" in content

    def test_creates_parent_directories_if_needed(self, tmp_path):
        output_path = str(tmp_path / "deep" / "nested" / "report.html")
        exit_code = generate_report(str(FIXTURES_DIR), output_path)
        assert exit_code == 0
        assert Path(output_path).exists()


# ---------------------------------------------------------------------------
# Risk assessments in rendered HTML (D2)
# ---------------------------------------------------------------------------


class TestRiskAssessmentsInRenderedHtml:
    """Verify that risk assessments appear in the final rendered HTML output."""

    def test_risk_section_headings_appear_in_rendered_html(self, tmp_path):
        output_path = str(tmp_path / "report.html")
        exit_code = generate_report(str(FIXTURES_DIR), output_path)
        assert exit_code == 0
        content = Path(output_path).read_text()
        assert "Delivery Velocity Risk" in content
        assert "Incident Risk" in content
        assert "Onboarding Risk" in content

    def test_severity_badges_appear_in_rendered_html(self, tmp_path):
        output_path = str(tmp_path / "report.html")
        exit_code = generate_report(str(FIXTURES_DIR), output_path)
        assert exit_code == 0
        content = Path(output_path).read_text()
        # At least one of HIGH, MODERATE, LOW severity badges should be present
        severity_badges_found = [
            badge for badge in ("HIGH", "MODERATE", "LOW")
            if badge in content
        ]
        assert len(severity_badges_found) >= 1, (
            "Expected at least one severity badge (HIGH, MODERATE, LOW) in rendered HTML"
        )
