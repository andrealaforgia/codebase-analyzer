"""Report rendering module.

Pure function render_report transforms ReportData into a complete HTML string.
Effect function write_report persists HTML to disk at the boundary.
"""

from __future__ import annotations

import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from src.report.models import ReportData

_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


def _create_jinja_environment() -> Environment:
    """Create a Jinja2 environment pointing to the templates directory."""
    return Environment(
        loader=FileSystemLoader(str(_TEMPLATES_DIR)),
        autoescape=False,
    )


def _serialize_report_data(report_data: ReportData) -> str:
    """Serialize ReportData to a JSON string suitable for embedding in HTML."""
    return json.dumps(report_data.model_dump(), default=str, indent=2)


def render_report(report_data: ReportData) -> str:
    """Render a complete HTML report from ReportData.

    Sets up the Jinja2 environment, serializes report_data to JSON for
    injection into the template, and returns the complete HTML string.
    """
    environment = _create_jinja_environment()
    template = environment.get_template("base.html")
    report_data_json = _serialize_report_data(report_data)
    return template.render(
        metadata=report_data.metadata,
        report_data=report_data,
        report_data_json=report_data_json,
    )


def write_report(html: str, output_path: str) -> None:
    """Write the rendered HTML string to a file.

    Creates parent directories if they do not exist.
    This is the effect boundary -- the only function that performs IO.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
