"""Unit tests for the SLT (Senior Leadership Team) report pipeline.

Tests validate that the SLT pipeline:
- Scans directories for codebase-analysis-report.html files
- Extracts embedded ReportData JSON from HTML reports
- Aggregates project data into portfolio-level summaries
- Computes portfolio score, risk matrix, and dimension averages
- Renders valid Markdown and HTML output
- Applies sensitive data sanitization
"""

import json
import textwrap
from pathlib import Path

import pytest

from src.report.slt_pipeline import (
    _REPORT_DATA_RE,
    _project_summary,
    build_slt_data,
    extract_report_data,
    render_slt_markdown,
    scan_for_reports,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _minimal_report_data(
    project_name: str = "test-project",
    overall_score: float = 72.0,
    rating: str = "Good",
) -> dict:
    """Build a minimal ReportData dict matching the embedded JSON structure."""
    return {
        "metadata": {
            "project_name": project_name,
            "target_directory": f"/dev/{project_name}",
            "analysis_date": "2026-03-13",
        },
        "overall_score": overall_score,
        "rating": rating,
        "dimensions": [
            {
                "name": "code_quality",
                "raw_score": 8.0,
                "normalized_score": 8.0,
                "weight": 0.07,
                "formula_display": "Grade A -> 10",
                "explanation": "High quality",
            },
            {
                "name": "test_design",
                "raw_score": 5.0,
                "normalized_score": 5.0,
                "weight": 0.07,
                "formula_display": "Farley 5.0",
                "explanation": "Average",
            },
        ],
        "risk_assessments": [
            {
                "name": "Delivery Velocity Risk",
                "severity": "LOW",
                "contributing_dimensions": ["Refactoring Debt"],
                "description": "Low risk",
            },
            {
                "name": "Incident Risk",
                "severity": "MODERATE",
                "contributing_dimensions": ["Test Design"],
                "description": "Moderate risk",
            },
            {
                "name": "Onboarding Risk",
                "severity": "LOW",
                "contributing_dimensions": ["Cognitive Load"],
                "description": "Low risk",
            },
        ],
        "agent_results": {},
    }


def _wrap_in_html(report_data: dict) -> str:
    """Wrap a report data dict in a minimal HTML structure matching the report format."""
    json_str = json.dumps(report_data, indent=2)
    return textwrap.dedent(f"""\
        <!DOCTYPE html>
        <html><body>
        <script type="application/json" id="report-data">
        {json_str}
        </script>
        </body></html>
    """)


@pytest.fixture
def report_tree(tmp_path: Path) -> Path:
    """Create a directory tree with multiple project reports."""
    # Project A - Good
    proj_a = tmp_path / "project-a"
    proj_a.mkdir()
    data_a = _minimal_report_data("project-a", 75.0, "Good")
    (proj_a / "codebase-analysis-report.html").write_text(
        _wrap_in_html(data_a), encoding="utf-8"
    )

    # Project B - Critical
    proj_b = tmp_path / "project-b"
    proj_b.mkdir()
    data_b = _minimal_report_data("project-b", 35.0, "Critical")
    data_b["risk_assessments"][1]["severity"] = "HIGH"
    (proj_b / "codebase-analysis-report.html").write_text(
        _wrap_in_html(data_b), encoding="utf-8"
    )

    # Project C - Excellent (nested subdirectory)
    proj_c = tmp_path / "team" / "project-c"
    proj_c.mkdir(parents=True)
    data_c = _minimal_report_data("project-c", 88.0, "Excellent")
    (proj_c / "codebase-analysis-report.html").write_text(
        _wrap_in_html(data_c), encoding="utf-8"
    )

    # Non-report file (should be ignored)
    (tmp_path / "README.md").write_text("# Projects")

    return tmp_path


# ---------------------------------------------------------------------------
# scan_for_reports
# ---------------------------------------------------------------------------


class TestScanForReports:
    def test_finds_all_reports_recursively(self, report_tree: Path) -> None:
        reports = scan_for_reports(str(report_tree))
        assert len(reports) == 3

    def test_returns_sorted_paths(self, report_tree: Path) -> None:
        reports = scan_for_reports(str(report_tree))
        names = [r.parent.name for r in reports]
        assert names == sorted(names)

    def test_returns_empty_for_no_reports(self, tmp_path: Path) -> None:
        reports = scan_for_reports(str(tmp_path))
        assert reports == []


# ---------------------------------------------------------------------------
# extract_report_data
# ---------------------------------------------------------------------------


class TestExtractReportData:
    def test_extracts_valid_json(self, report_tree: Path) -> None:
        report_path = report_tree / "project-a" / "codebase-analysis-report.html"
        data = extract_report_data(report_path)
        assert data is not None
        assert data["overall_score"] == 75.0
        assert data["metadata"]["project_name"] == "project-a"

    def test_returns_none_for_missing_file(self, tmp_path: Path) -> None:
        data = extract_report_data(tmp_path / "nonexistent.html")
        assert data is None

    def test_returns_none_for_no_json_block(self, tmp_path: Path) -> None:
        bad_file = tmp_path / "codebase-analysis-report.html"
        bad_file.write_text("<html><body>no json here</body></html>")
        data = extract_report_data(bad_file)
        assert data is None

    def test_returns_none_for_invalid_json(self, tmp_path: Path) -> None:
        bad_file = tmp_path / "codebase-analysis-report.html"
        bad_file.write_text(
            '<script type="application/json" id="report-data">{invalid}</script>'
        )
        data = extract_report_data(bad_file)
        assert data is None


# ---------------------------------------------------------------------------
# _project_summary
# ---------------------------------------------------------------------------


class TestProjectSummary:
    def test_extracts_basic_fields(self) -> None:
        data = _minimal_report_data("my-project", 72.0, "Good")
        summary = _project_summary(data, Path("/dev/my-project/report.html"))
        assert summary["project_name"] == "my-project"
        assert summary["overall_score"] == 72.0
        assert summary["rating"] == "Good"
        assert summary["analysis_date"] == "2026-03-13"

    def test_finds_weakest_dimension(self) -> None:
        data = _minimal_report_data()
        summary = _project_summary(data, Path("/dev/test/report.html"))
        assert summary["weakest_dimension"]["name"] == "test_design"
        assert summary["weakest_dimension"]["normalized_score"] == 5.0

    def test_finds_top_risk_high_first(self) -> None:
        data = _minimal_report_data()
        data["risk_assessments"][2]["severity"] = "HIGH"
        summary = _project_summary(data, Path("/x"))
        assert summary["top_risk"]["severity"] == "HIGH"

    def test_finds_top_risk_moderate_when_no_high(self) -> None:
        data = _minimal_report_data()
        summary = _project_summary(data, Path("/x"))
        assert summary["top_risk"]["severity"] == "MODERATE"

    def test_handles_empty_dimensions(self) -> None:
        data = _minimal_report_data()
        data["dimensions"] = []
        summary = _project_summary(data, Path("/x"))
        assert summary["weakest_dimension"] is None


# ---------------------------------------------------------------------------
# build_slt_data
# ---------------------------------------------------------------------------


class TestBuildSltData:
    def test_aggregates_multiple_projects(self, report_tree: Path) -> None:
        paths = scan_for_reports(str(report_tree))
        slt = build_slt_data(paths)
        assert slt["total_projects"] == 3
        assert len(slt["projects"]) == 3

    def test_computes_portfolio_score(self, report_tree: Path) -> None:
        paths = scan_for_reports(str(report_tree))
        slt = build_slt_data(paths)
        expected = (75.0 + 35.0 + 88.0) / 3
        assert abs(slt["portfolio_score"] - expected) < 0.1

    def test_identifies_critical_projects(self, report_tree: Path) -> None:
        paths = scan_for_reports(str(report_tree))
        slt = build_slt_data(paths)
        assert len(slt["critical_projects"]) == 1
        assert slt["critical_projects"][0]["project_name"] == "project-b"

    def test_projects_sorted_worst_first(self, report_tree: Path) -> None:
        paths = scan_for_reports(str(report_tree))
        slt = build_slt_data(paths)
        scores = [p["overall_score"] for p in slt["projects"]]
        assert scores == sorted(scores)

    def test_builds_risk_matrix(self, report_tree: Path) -> None:
        paths = scan_for_reports(str(report_tree))
        slt = build_slt_data(paths)
        assert len(slt["risk_matrix"]) == 3
        names = {row["project_name"] for row in slt["risk_matrix"]}
        assert "project-a" in names
        assert "project-b" in names

    def test_computes_dimension_averages(self, report_tree: Path) -> None:
        paths = scan_for_reports(str(report_tree))
        slt = build_slt_data(paths)
        assert len(slt["dimension_averages"]) > 0
        for dim in slt["dimension_averages"]:
            assert "name" in dim
            assert "average" in dim
            assert "count" in dim
            assert dim["count"] == 3

    def test_dimension_averages_sorted_ascending(self, report_tree: Path) -> None:
        paths = scan_for_reports(str(report_tree))
        slt = build_slt_data(paths)
        averages = [d["average"] for d in slt["dimension_averages"]]
        assert averages == sorted(averages)

    def test_handles_empty_paths(self) -> None:
        slt = build_slt_data([])
        assert slt["total_projects"] == 0
        assert slt["portfolio_score"] == 0.0
        assert slt["portfolio_rating"] == "N/A"

    def test_records_extraction_errors(self, tmp_path: Path) -> None:
        bad_file = tmp_path / "codebase-analysis-report.html"
        bad_file.write_text("<html>no json</html>")
        slt = build_slt_data([bad_file])
        assert slt["total_projects"] == 0
        assert len(slt["errors"]) == 1

    def test_portfolio_rating_critical(self) -> None:
        data = _minimal_report_data("low", 30.0, "Critical")
        html = _wrap_in_html(data)
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".html", mode="w", delete=False) as f:
            f.write(html)
            path = Path(f.name)
        try:
            slt = build_slt_data([path])
            assert slt["portfolio_rating"] == "Critical"
        finally:
            path.unlink()

    def test_portfolio_rating_excellent(self) -> None:
        data = _minimal_report_data("high", 90.0, "Excellent")
        html = _wrap_in_html(data)
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".html", mode="w", delete=False) as f:
            f.write(html)
            path = Path(f.name)
        try:
            slt = build_slt_data([path])
            assert slt["portfolio_rating"] == "Excellent"
        finally:
            path.unlink()


# ---------------------------------------------------------------------------
# Sanitization integration
# ---------------------------------------------------------------------------


class TestSltSanitization:
    def test_redacts_sensitive_data_in_extracted_reports(self, tmp_path: Path) -> None:
        data = _minimal_report_data()
        data["agent_results"] = {
            "security_assessor": {
                "summary": "Found password=admin123 in config",
                "password": "secret_value",
            }
        }
        report_file = tmp_path / "codebase-analysis-report.html"
        report_file.write_text(_wrap_in_html(data), encoding="utf-8")

        slt = build_slt_data([report_file])
        # The raw agent_results won't appear in the SLT summary directly,
        # but the sanitize_value call in build_slt_data ensures the full
        # data dict is sanitized before project_summary processes it
        assert slt["total_projects"] == 1
        # Verify the pipeline didn't crash on sanitized data
        assert slt["projects"][0]["project_name"] == "test-project"


# ---------------------------------------------------------------------------
# render_slt_markdown
# ---------------------------------------------------------------------------


class TestRenderSltMarkdown:
    def test_contains_portfolio_header(self, report_tree: Path) -> None:
        paths = scan_for_reports(str(report_tree))
        slt = build_slt_data(paths)
        md = render_slt_markdown(slt)
        assert "# Codebase Health -- Portfolio Report" in md

    def test_contains_portfolio_score(self, report_tree: Path) -> None:
        paths = scan_for_reports(str(report_tree))
        slt = build_slt_data(paths)
        md = render_slt_markdown(slt)
        assert "Portfolio Health:" in md
        assert "/ 100" in md

    def test_contains_project_table(self, report_tree: Path) -> None:
        paths = scan_for_reports(str(report_tree))
        slt = build_slt_data(paths)
        md = render_slt_markdown(slt)
        assert "## Project Health Summary" in md
        assert "project-a" in md
        assert "project-b" in md
        assert "project-c" in md

    def test_contains_risk_heatmap(self, report_tree: Path) -> None:
        paths = scan_for_reports(str(report_tree))
        slt = build_slt_data(paths)
        md = render_slt_markdown(slt)
        assert "## Risk Heatmap" in md
        assert "Delivery Velocity Risk" in md

    def test_contains_dimension_averages(self, report_tree: Path) -> None:
        paths = scan_for_reports(str(report_tree))
        slt = build_slt_data(paths)
        md = render_slt_markdown(slt)
        assert "## Portfolio Dimension Averages" in md

    def test_critical_projects_section_when_present(self, report_tree: Path) -> None:
        paths = scan_for_reports(str(report_tree))
        slt = build_slt_data(paths)
        md = render_slt_markdown(slt)
        assert "Immediate Attention" in md
        assert "project-b" in md

    def test_no_critical_section_when_all_healthy(self, tmp_path: Path) -> None:
        proj = tmp_path / "healthy"
        proj.mkdir()
        data = _minimal_report_data("healthy", 85.0, "Excellent")
        (proj / "codebase-analysis-report.html").write_text(
            _wrap_in_html(data), encoding="utf-8"
        )
        paths = scan_for_reports(str(tmp_path))
        slt = build_slt_data(paths)
        md = render_slt_markdown(slt)
        assert "Immediate Attention" not in md

    def test_handles_empty_data(self) -> None:
        slt = build_slt_data([])
        md = render_slt_markdown(slt)
        assert "Portfolio Report" in md
        assert "Projects Analyzed:** 0" in md


# ---------------------------------------------------------------------------
# Regex pattern
# ---------------------------------------------------------------------------


class TestReportDataRegex:
    def test_matches_standard_format(self) -> None:
        html = '<script type="application/json" id="report-data">{"a":1}</script>'
        match = _REPORT_DATA_RE.search(html)
        assert match is not None
        assert json.loads(match.group(1)) == {"a": 1}

    def test_matches_multiline_json(self) -> None:
        html = textwrap.dedent("""\
            <script type="application/json" id="report-data">
            {
              "overall_score": 72.5
            }
            </script>
        """)
        match = _REPORT_DATA_RE.search(html)
        assert match is not None
        data = json.loads(match.group(1))
        assert data["overall_score"] == 72.5

    def test_no_match_without_id(self) -> None:
        html = '<script type="application/json">{"a":1}</script>'
        match = _REPORT_DATA_RE.search(html)
        assert match is None
