"""SLT (Senior Leadership Team) report generation pipeline.

Scans a directory tree for existing codebase-analysis-report.html files
produced by /alf-analyze, extracts embedded ReportData JSON from each,
aggregates scores across projects, and generates a portfolio-level
summary report in both Markdown and HTML formats.

Pipeline:
    scan_for_reports -> extract_report_data -> build_slt_data -> render -> write
"""

from __future__ import annotations

import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

from src.report.sanitize import sanitize_value

_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

# Pattern to extract the JSON blob from <script type="application/json" id="report-data">
_REPORT_DATA_RE = re.compile(
    r'<script\s+type="application/json"\s+id="report-data">\s*(.*?)\s*</script>',
    re.DOTALL,
)

# Default report filename produced by /alf-analyze
_REPORT_FILENAME = "codebase-analysis-report.html"


# ---------------------------------------------------------------------------
# Data structures (plain dicts -- no Pydantic needed for aggregation)
# ---------------------------------------------------------------------------


def _empty_project_summary() -> dict[str, Any]:
    return {
        "project_name": "",
        "target_directory": "",
        "analysis_date": "",
        "overall_score": 0.0,
        "rating": "N/A",
        "dimensions": [],
        "risk_assessments": [],
    }


# ---------------------------------------------------------------------------
# IO boundary: scan directory tree for reports
# ---------------------------------------------------------------------------


def scan_for_reports(root_dir: str) -> list[Path]:
    """Recursively find all codebase-analysis-report.html files under root_dir.

    Returns a sorted list of absolute paths to discovered report files.
    """
    root = Path(root_dir).resolve()
    reports = sorted(root.rglob(_REPORT_FILENAME))
    return reports


# ---------------------------------------------------------------------------
# IO boundary: extract ReportData JSON from an HTML report
# ---------------------------------------------------------------------------


def extract_report_data(report_path: Path) -> dict[str, Any] | None:
    """Read an HTML report file and extract the embedded ReportData JSON.

    Returns the parsed dict or None if extraction fails.
    """
    try:
        html_content = report_path.read_text(encoding="utf-8")
    except OSError:
        return None

    match = _REPORT_DATA_RE.search(html_content)
    if not match:
        return None

    try:
        raw = html.unescape(match.group(1))
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


# ---------------------------------------------------------------------------
# Pure functions: aggregate project data into SLT summary
# ---------------------------------------------------------------------------


def _project_summary(report_data: dict[str, Any], report_path: Path) -> dict[str, Any]:
    """Extract a project-level summary from a single report's data."""
    metadata = report_data.get("metadata", {})
    dimensions = report_data.get("dimensions", [])
    risks = report_data.get("risk_assessments", [])

    # Find weakest dimension
    weakest = None
    if dimensions:
        weakest = min(dimensions, key=lambda d: d.get("normalized_score", 10))

    # Find highest risk
    top_risk = None
    for risk in risks:
        if risk.get("severity") == "HIGH":
            top_risk = risk
            break
    if not top_risk and risks:
        for risk in risks:
            if risk.get("severity") == "MODERATE":
                top_risk = risk
                break
    if not top_risk and risks:
        top_risk = risks[0]

    return {
        "project_name": metadata.get("project_name", report_path.parent.name),
        "target_directory": metadata.get("target_directory", str(report_path.parent)),
        "analysis_date": metadata.get("analysis_date", "unknown"),
        "overall_score": report_data.get("overall_score", 0.0),
        "rating": report_data.get("rating", "N/A"),
        "dimensions": dimensions,
        "risk_assessments": risks,
        "weakest_dimension": weakest,
        "top_risk": top_risk,
        "report_path": str(report_path),
    }


def build_slt_data(
    report_paths: list[Path],
) -> dict[str, Any]:
    """Build the complete SLT report data from discovered report files.

    Extracts data from each report, computes portfolio-level aggregations,
    and returns a dict ready for rendering.

    Pure function after IO extraction.
    """
    projects: list[dict[str, Any]] = []
    errors: list[str] = []

    for path in report_paths:
        data = extract_report_data(path)
        if data is None:
            errors.append(f"Failed to extract data from {path}")
            continue
        # Sanitize extracted data to prevent sensitive info leaking
        data = sanitize_value(data)
        projects.append(_project_summary(data, path))

    if not projects:
        return {
            "projects": [],
            "errors": errors,
            "portfolio_score": 0.0,
            "portfolio_rating": "N/A",
            "total_projects": 0,
            "report_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "risk_matrix": [],
            "dimension_averages": [],
            "critical_projects": [],
        }

    # Portfolio-level score
    scores = [p["overall_score"] for p in projects]
    portfolio_score = sum(scores) / len(scores)

    if portfolio_score <= 40.0:
        portfolio_rating = "Critical"
    elif portfolio_score <= 60.0:
        portfolio_rating = "Needs Attention"
    elif portfolio_score <= 80.0:
        portfolio_rating = "Good"
    else:
        portfolio_rating = "Excellent"

    # Risk matrix: project x risk category
    risk_categories = ["Delivery Velocity Risk", "Incident Risk", "Onboarding Risk"]
    risk_matrix = []
    for project in projects:
        row = {"project_name": project["project_name"], "risks": {}}
        for risk in project["risk_assessments"]:
            row["risks"][risk["name"]] = risk["severity"]
        risk_matrix.append(row)

    # Dimension averages across projects
    dimension_scores: dict[str, list[float]] = {}
    for project in projects:
        for dim in project["dimensions"]:
            name = dim.get("name", "")
            score = dim.get("normalized_score", 0.0)
            dimension_scores.setdefault(name, []).append(score)

    dimension_averages = sorted(
        [
            {"name": name, "average": sum(vals) / len(vals), "count": len(vals)}
            for name, vals in dimension_scores.items()
        ],
        key=lambda d: d["average"],
    )

    # Critical projects (score <= 40)
    critical_projects = [p for p in projects if p["overall_score"] <= 40.0]

    # Sort projects by score ascending (worst first)
    projects_sorted = sorted(projects, key=lambda p: p["overall_score"])

    return {
        "projects": projects_sorted,
        "errors": errors,
        "portfolio_score": portfolio_score,
        "portfolio_rating": portfolio_rating,
        "total_projects": len(projects),
        "report_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "risk_categories": risk_categories,
        "risk_matrix": risk_matrix,
        "dimension_averages": dimension_averages,
        "critical_projects": critical_projects,
    }


# ---------------------------------------------------------------------------
# Rendering: Markdown
# ---------------------------------------------------------------------------


def render_slt_markdown(slt_data: dict[str, Any]) -> str:
    """Render the SLT summary as Markdown."""
    lines: list[str] = []
    lines.append("# Codebase Health -- Portfolio Report")
    lines.append("")
    lines.append(f"**Date:** {slt_data['report_date']}")
    lines.append(f"**Projects Analyzed:** {slt_data['total_projects']}")
    lines.append(
        f"**Portfolio Health:** {slt_data['portfolio_score']:.1f} / 100"
        f" ({slt_data['portfolio_rating']})"
    )
    lines.append("")

    # Critical alert
    if slt_data["critical_projects"]:
        lines.append("## Projects Requiring Immediate Attention")
        lines.append("")
        for p in slt_data["critical_projects"]:
            lines.append(
                f"- **{p['project_name']}** -- {p['overall_score']:.1f}/100 (Critical)"
            )
        lines.append("")

    # Project summary table
    lines.append("## Project Health Summary")
    lines.append("")
    lines.append(
        "| Project | Score | Rating | Weakest Dimension | Top Risk |"
    )
    lines.append(
        "|---------|------:|--------|-------------------|----------|"
    )
    for p in slt_data["projects"]:
        weakest_name = "N/A"
        if p.get("weakest_dimension"):
            weakest_name = (
                p["weakest_dimension"].get("name", "").replace("_", " ").title()
            )
            weakest_score = p["weakest_dimension"].get("normalized_score", 0)
            weakest_name = f"{weakest_name} ({weakest_score:.1f})"

        top_risk_name = "N/A"
        if p.get("top_risk"):
            top_risk_name = (
                f"{p['top_risk'].get('name', 'N/A')}"
                f" ({p['top_risk'].get('severity', 'N/A')})"
            )

        lines.append(
            f"| {p['project_name']} | {p['overall_score']:.1f} | {p['rating']}"
            f" | {weakest_name} | {top_risk_name} |"
        )
    lines.append("")

    # Risk heatmap
    if slt_data["risk_matrix"]:
        lines.append("## Risk Heatmap")
        lines.append("")
        risk_cats = slt_data.get("risk_categories", [])
        header = "| Project | " + " | ".join(risk_cats) + " |"
        separator = "|---------|" + "|".join(["-------"] * len(risk_cats)) + "|"
        lines.append(header)
        lines.append(separator)
        for row in slt_data["risk_matrix"]:
            cells = [
                row["risks"].get(cat, "N/A") for cat in risk_cats
            ]
            lines.append(f"| {row['project_name']} | " + " | ".join(cells) + " |")
        lines.append("")

    # Dimension averages
    if slt_data["dimension_averages"]:
        lines.append("## Portfolio Dimension Averages")
        lines.append("")
        lines.append("| Dimension | Average Score | Projects |")
        lines.append("|-----------|-------------:|:--------:|")
        for dim in slt_data["dimension_averages"]:
            name = dim["name"].replace("_", " ").title()
            lines.append(
                f"| {name} | {dim['average']:.1f} / 10 | {dim['count']} |"
            )
        lines.append("")

    lines.append("---")
    lines.append("*Generated by Codebase Analyzer -- SLT Report*")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Rendering: HTML
# ---------------------------------------------------------------------------


def render_slt_html(slt_data: dict[str, Any]) -> str:
    """Render the SLT summary as a self-contained HTML report."""
    environment = Environment(
        loader=FileSystemLoader(str(_TEMPLATES_DIR)),
        autoescape=True,
    )
    template = environment.get_template("slt_report.html")
    return template.render(**slt_data)


# ---------------------------------------------------------------------------
# IO boundary: top-level pipeline orchestrator
# ---------------------------------------------------------------------------


def generate_slt_report(
    root_dir: str,
    output_dir: str | None = None,
) -> int:
    """Generate SLT portfolio reports from all /alf-analyze reports under root_dir.

    Scans for codebase-analysis-report.html files, aggregates their data,
    and writes both Markdown and HTML reports.

    Returns 0 on success, 1 if no reports found.
    """
    report_paths = scan_for_reports(root_dir)

    if not report_paths:
        print(f"No codebase analysis reports found under {root_dir}")
        return 1

    print(f"Found {len(report_paths)} report(s):")
    for path in report_paths:
        print(f"  - {path}")

    slt_data = build_slt_data(report_paths)

    if not slt_data["projects"]:
        print("Failed to extract data from any reports")
        for error in slt_data["errors"]:
            print(f"  - {error}")
        return 1

    out = Path(output_dir) if output_dir else Path(root_dir).resolve()
    md_path = out / "codebase-analyzer-general-report.md"
    html_path = out / "codebase-analyzer-general-report.html"

    md_content = render_slt_markdown(slt_data)
    md_path.write_text(md_content, encoding="utf-8")
    print(f"Markdown report: {md_path}")

    html_content = render_slt_html(slt_data)
    html_path.write_text(html_content, encoding="utf-8")
    print(f"HTML report:     {html_path}")

    print(
        f"\nPortfolio Health: {slt_data['portfolio_score']:.1f}/100"
        f" ({slt_data['portfolio_rating']})"
    )
    print(f"Projects analyzed: {slt_data['total_projects']}")
    if slt_data["critical_projects"]:
        print(
            f"CRITICAL projects: {len(slt_data['critical_projects'])}"
        )
    if slt_data["errors"]:
        for error in slt_data["errors"]:
            print(f"  Warning: {error}")

    return 0
