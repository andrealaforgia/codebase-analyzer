"""Report rendering module.

Pure function render_report transforms ReportData into a complete HTML string.
Effect function write_report persists HTML to disk at the boundary.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

from src.report.charts import (
    build_dimension_bars_config,
    build_gauge_config,
    build_radar_config,
    find_weakest_dimension,
)
from src.report.models import DimensionScore, ReportData

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


def _serialize_chart_config(config: dict[str, Any]) -> str:
    """Serialize a chart config dict to a JSON string for template embedding."""
    return json.dumps(config, default=str)


def _build_dimensions_by_name(
    dimensions: list[DimensionScore],
) -> dict[str, DimensionScore]:
    """Index dimension scores by name for O(1) lookup in templates."""
    return {dimension.name: dimension for dimension in dimensions}


def render_report(report_data: ReportData) -> str:
    """Render a complete HTML report from ReportData.

    Builds chart configurations from dimension scores, serializes report_data
    to JSON for injection into the template, and returns the complete HTML
    string including the executive summary with gauge, radar, and bar charts.
    """
    environment = _create_jinja_environment()
    template = environment.get_template("base.html")
    report_data_json = _serialize_report_data(report_data)

    radar_config = build_radar_config(report_data.dimensions)
    gauge_config = build_gauge_config(report_data.overall_score, report_data.rating)
    bars_config = build_dimension_bars_config(report_data.dimensions)
    weakest = find_weakest_dimension(report_data.dimensions)

    dimensions_by_name = _build_dimensions_by_name(report_data.dimensions)

    return template.render(
        metadata=report_data.metadata,
        report_data=report_data,
        report_data_json=report_data_json,
        radar_config=radar_config,
        gauge_config=gauge_config,
        bars_config=bars_config,
        weakest=weakest,
        dimensions_by_name=dimensions_by_name,
        radar_config_json=_serialize_chart_config(radar_config),
        gauge_config_json=_serialize_chart_config(gauge_config),
        bars_config_json=_serialize_chart_config(bars_config),
    )


def write_report(html: str, output_path: str) -> None:
    """Write the rendered HTML string to a file.

    Creates parent directories if they do not exist.
    This is the effect boundary -- the only function that performs IO.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
