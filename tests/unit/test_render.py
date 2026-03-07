"""Unit tests for the report rendering module.

Tests verify that render_report produces valid HTML with the required
structure (navigation, print CSS, data injection, library placeholders)
and that write_report persists HTML to disk.
"""

import json

import pytest

from src.report.models import (
    DimensionScore,
    ProjectMetadata,
    ReportData,
)
from src.report.render import render_report, write_report


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------


def _make_report_data(**overrides) -> ReportData:
    """Build a minimal valid ReportData for testing."""
    defaults = dict(
        metadata=ProjectMetadata(
            project_name="test-project",
            target_directory="/tmp/test",
            analysis_date="2026-03-07",
            total_files=42,
            total_loc=5000,
            primary_language="Python",
        ),
        dimensions=[
            DimensionScore(
                name="code_quality",
                raw_score=7.5,
                normalized_score=7.5,
                weight=0.20,
                formula_display="(SRP*0.2 + ...) = 7.5",
                explanation="Code quality is good.",
            ),
        ],
        overall_score=75.0,
        rating="Good",
        risk_assessments=[],
        agent_results={},
    )
    defaults.update(overrides)
    return ReportData(**defaults)


# ---------------------------------------------------------------------------
# render_report: HTML structure
# ---------------------------------------------------------------------------


class TestRenderReportProducesValidHtml:
    def test_output_contains_html5_doctype(self):
        html = render_report(_make_report_data())
        assert "<!DOCTYPE html>" in html

    def test_output_contains_meta_charset(self):
        html = render_report(_make_report_data())
        assert 'charset="UTF-8"' in html or "charset=UTF-8" in html

    def test_output_contains_meta_viewport(self):
        html = render_report(_make_report_data())
        assert "viewport" in html

    def test_output_contains_title_with_project_name(self):
        report_data = _make_report_data()
        html = render_report(report_data)
        assert "test-project" in html
        assert "<title>" in html


# ---------------------------------------------------------------------------
# render_report: navigation
# ---------------------------------------------------------------------------


EXPECTED_NAV_SECTIONS = [
    "Executive Summary",
    "Code Quality",
    "Test Design",
    "Cognitive Load",
    "DDD",
    "Legacy",
    "Refactoring",
    "Methodology",
]


class TestRenderReportContainsNavigation:
    def test_nav_element_is_present(self):
        html = render_report(_make_report_data())
        assert "<nav" in html

    @pytest.mark.parametrize("section_name", EXPECTED_NAV_SECTIONS)
    def test_nav_contains_section_link(self, section_name):
        html = render_report(_make_report_data())
        assert section_name in html


# ---------------------------------------------------------------------------
# render_report: report data injection
# ---------------------------------------------------------------------------


class TestRenderReportInjectsData:
    def test_report_data_script_tag_present(self):
        html = render_report(_make_report_data())
        assert "const reportData =" in html

    def test_injected_data_contains_project_name(self):
        html = render_report(_make_report_data())
        assert "test-project" in html

    def test_injected_data_contains_overall_score(self):
        report_data = _make_report_data(overall_score=85.0, rating="Excellent")
        html = render_report(report_data)
        assert "85.0" in html

    def test_injected_data_is_valid_json(self):
        html = render_report(_make_report_data())
        # Extract JSON between "const reportData = " and ";"
        marker_start = "const reportData = "
        start_idx = html.index(marker_start) + len(marker_start)
        end_idx = html.index(";", start_idx)
        json_str = html[start_idx:end_idx]
        data = json.loads(json_str)
        assert data["metadata"]["project_name"] == "test-project"


# ---------------------------------------------------------------------------
# render_report: print CSS
# ---------------------------------------------------------------------------


class TestRenderReportContainsPrintCss:
    def test_print_media_query_present(self):
        html = render_report(_make_report_data())
        assert "@media print" in html

    def test_print_css_hides_nav(self):
        html = render_report(_make_report_data())
        # The print CSS should hide the nav element
        assert "@media print" in html
        # Verify nav is targeted for hiding in print
        print_section_start = html.index("@media print")
        print_section = html[print_section_start:print_section_start + 500]
        assert "nav" in print_section


# ---------------------------------------------------------------------------
# render_report: library placeholders
# ---------------------------------------------------------------------------


class TestRenderReportContainsLibraryPlaceholders:
    def test_chart_js_placeholder_present(self):
        html = render_report(_make_report_data())
        assert "<!-- CHART_JS_PLACEHOLDER -->" in html

    def test_d3_js_placeholder_present(self):
        html = render_report(_make_report_data())
        assert "<!-- D3_JS_PLACEHOLDER -->" in html

    def test_mermaid_js_placeholder_present(self):
        html = render_report(_make_report_data())
        assert "<!-- MERMAID_JS_PLACEHOLDER -->" in html


# ---------------------------------------------------------------------------
# write_report: file persistence (integration-ish)
# ---------------------------------------------------------------------------


class TestWriteReport:
    def test_writes_html_to_file(self, tmp_path):
        output_file = tmp_path / "report.html"
        html_content = "<html><body>test</body></html>"
        write_report(html_content, str(output_file))
        assert output_file.exists()
        assert output_file.read_text() == html_content

    def test_creates_parent_directories_if_needed(self, tmp_path):
        output_file = tmp_path / "nested" / "dir" / "report.html"
        html_content = "<html><body>nested</body></html>"
        write_report(html_content, str(output_file))
        assert output_file.exists()
        assert output_file.read_text() == html_content
