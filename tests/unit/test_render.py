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


# ---------------------------------------------------------------------------
# Helpers for dimension detail tests
# ---------------------------------------------------------------------------

ALL_DIMENSION_NAMES = [
    "code_quality",
    "test_design",
    "cognitive_load",
    "ddd",
    "legacy",
    "refactoring",
]

DIMENSION_SECTION_IDS = {
    "code_quality": "code-quality",
    "test_design": "test-design",
    "cognitive_load": "cognitive-load",
    "ddd": "ddd",
    "legacy": "legacy",
    "refactoring": "refactoring",
}


def _make_all_dimensions() -> list[DimensionScore]:
    """Build all six dimension scores for a complete report."""
    return [
        DimensionScore(
            name="code_quality",
            raw_score=7.5,
            normalized_score=7.5,
            weight=0.20,
            formula_display="(SRP*0.2 + OCP*0.2 + LSP*0.2 + ISP*0.2 + DIP*0.2) = 7.5",
            explanation="Code quality is good overall.",
        ),
        DimensionScore(
            name="test_design",
            raw_score=6.8,
            normalized_score=6.8,
            weight=0.20,
            formula_display="farley_index = 6.8",
            explanation="Test design is satisfactory.",
        ),
        DimensionScore(
            name="cognitive_load",
            raw_score=450.0,
            normalized_score=5.5,
            weight=0.20,
            formula_display="10 - (cli_score / 100) = 10 - (450 / 100) = 5.5",
            explanation="Moderate cognitive load detected.",
        ),
        DimensionScore(
            name="ddd",
            raw_score=6.0,
            normalized_score=6.0,
            weight=0.15,
            formula_display="overall_score = 6.0",
            explanation="DDD compliance is acceptable.",
        ),
        DimensionScore(
            name="legacy",
            raw_score=7.2,
            normalized_score=7.2,
            weight=0.15,
            formula_display="overall_score = 7.2",
            explanation="Legacy risk is manageable.",
        ),
        DimensionScore(
            name="refactoring",
            raw_score=3.5,
            normalized_score=3.5,
            weight=0.10,
            formula_display="10 - (total_recommendations / 10) = 3.5",
            explanation="Significant refactoring debt.",
        ),
    ]


def _make_report_with_all_dimensions(**overrides) -> ReportData:
    """Build a ReportData with all six dimensions present."""
    defaults = dict(
        metadata=ProjectMetadata(
            project_name="full-project",
            target_directory="/tmp/full",
            analysis_date="2026-03-07",
            total_files=100,
            total_loc=10000,
            primary_language="Python",
        ),
        dimensions=_make_all_dimensions(),
        overall_score=62.0,
        rating="Good",
        risk_assessments=[],
        agent_results={},
    )
    defaults.update(overrides)
    return ReportData(**defaults)


# ---------------------------------------------------------------------------
# render_report: dimension detail sections
# ---------------------------------------------------------------------------


class TestRenderReportDimensionDetails:
    """Each available dimension has a detail section with score derivation."""

    @pytest.mark.parametrize(
        "dimension_name",
        ALL_DIMENSION_NAMES,
    )
    def test_dimension_section_has_anchor_id(self, dimension_name):
        report_data = _make_report_with_all_dimensions()
        html = render_report(report_data)
        section_id = DIMENSION_SECTION_IDS[dimension_name]
        assert f'id="{section_id}"' in html

    def test_score_derivation_contains_formula_display(self):
        report_data = _make_report_with_all_dimensions()
        html = render_report(report_data)
        # Each dimension's formula_display text should appear in the output
        for dimension in report_data.dimensions:
            assert dimension.formula_display in html, (
                f"formula_display for {dimension.name} not found in HTML"
            )

    def test_score_derivation_contains_raw_score(self):
        report_data = _make_report_with_all_dimensions()
        html = render_report(report_data)
        # Raw score for cognitive_load (450.0) should appear
        assert "450.0" in html

    def test_score_derivation_contains_normalized_score(self):
        report_data = _make_report_with_all_dimensions()
        html = render_report(report_data)
        # The normalized score of 5.5 for cognitive_load should appear
        assert "5.5" in html

    def test_score_derivation_contains_explanation(self):
        report_data = _make_report_with_all_dimensions()
        html = render_report(report_data)
        for dimension in report_data.dimensions:
            assert dimension.explanation in html, (
                f"explanation for {dimension.name} not found in HTML"
            )

    def test_score_derivation_heading_present(self):
        report_data = _make_report_with_all_dimensions()
        html = render_report(report_data)
        assert "Score Derivation" in html


# ---------------------------------------------------------------------------
# render_report: bidirectional navigation
# ---------------------------------------------------------------------------


class TestRenderReportBidirectionalNavigation:
    """Dimension sections link back to executive summary."""

    def test_back_to_summary_links_exist(self):
        report_data = _make_report_with_all_dimensions()
        html = render_report(report_data)
        # Each dimension section should have a link back to the executive summary
        assert html.count('href="#executive-summary"') >= len(
            report_data.dimensions
        ), (
            "Expected at least one 'Back to Summary' link per available dimension"
        )

    def test_back_to_summary_link_text(self):
        report_data = _make_report_with_all_dimensions()
        html = render_report(report_data)
        assert "Back to Summary" in html


# ---------------------------------------------------------------------------
# render_report: missing dimensions show "Not Available"
# ---------------------------------------------------------------------------


class TestRenderReportMissingDimensions:
    """Dimensions not present in the data show 'Not Available'."""

    def test_missing_dimension_shows_not_available(self):
        # Only provide code_quality -- the other 5 are missing
        report_data = _make_report_data(
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
        )
        html = render_report(report_data)
        assert "Not Available" in html

    def test_available_dimension_does_not_show_not_available_in_its_section(self):
        # code_quality is present, so its section should NOT say "Not Available"
        report_data = _make_report_with_all_dimensions()
        html = render_report(report_data)
        # Find the code-quality section specifically
        code_quality_start = html.index('id="code-quality"')
        code_quality_section = html[
            code_quality_start : code_quality_start + 2000
        ]
        assert "Not Available" not in code_quality_section


# ---------------------------------------------------------------------------
# render_report: methodology appendix
# ---------------------------------------------------------------------------


class TestRenderReportMethodologyAppendix:
    """The methodology section shows scoring methodology details."""

    def test_methodology_section_exists(self):
        html = render_report(_make_report_with_all_dimensions())
        assert 'id="methodology"' in html

    def test_methodology_contains_weight_table(self):
        html = render_report(_make_report_with_all_dimensions())
        # Weight percentages should be in the methodology section
        assert "20%" in html
        assert "15%" in html
        assert "10%" in html

    def test_methodology_contains_rating_thresholds(self):
        html = render_report(_make_report_with_all_dimensions())
        # Rating threshold ranges should appear
        assert "0-40" in html or "0 - 40" in html
        assert "Critical" in html
        assert "Excellent" in html

    def test_methodology_contains_dimension_names(self):
        html = render_report(_make_report_with_all_dimensions())
        # The methodology should reference dimension names
        assert "Code Quality" in html
        assert "Test Design" in html
        assert "Cognitive Load" in html

    def test_methodology_contains_ai_note(self):
        html = render_report(_make_report_with_all_dimensions())
        assert "AI analysis" in html.lower() or "ai analysis" in html.lower()
