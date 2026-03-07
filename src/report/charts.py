"""Pure functions that build Chart.js configuration dictionaries.

Each function takes domain data (DimensionScore, score, rating) and returns
a plain dict suitable for JSON serialization and injection into Chart.js
in the report template.  No side effects, no IO imports.
"""

from __future__ import annotations

from src.report.models import DimensionScore


# ---------------------------------------------------------------------------
# Color constants
# ---------------------------------------------------------------------------

_GREEN = "#28a745"
_BLUE = "#007bff"
_ORANGE = "#fd7e14"
_RED = "#dc3545"
_GRAY = "#e0e0e0"

_RATING_COLORS: dict[str, str] = {
    "Excellent": _GREEN,
    "Good": _BLUE,
    "Needs Attention": _ORANGE,
    "Critical": _RED,
}

_RADAR_FILL_COLOR = "rgba(0, 123, 255, 0.25)"
_RADAR_BORDER_COLOR = "rgba(0, 123, 255, 1)"


# ---------------------------------------------------------------------------
# Bar color assignment
# ---------------------------------------------------------------------------


def _bar_color_for_score(score: float) -> str:
    """Assign a color based on dimension score thresholds.

    Red for scores below 4, orange for 4 to below 6, green for 6 and above.
    """
    if score < 4:
        return _RED
    if score < 6:
        return _ORANGE
    return _GREEN


# ---------------------------------------------------------------------------
# Chart builders
# ---------------------------------------------------------------------------


def build_radar_config(dimensions: list[DimensionScore]) -> dict:
    """Build a Chart.js radar chart config from dimension scores.

    Labels come from dimension names, data from normalized_score values.
    Scale runs 0-10 with semi-transparent blue fill.
    """
    labels = [dimension.name for dimension in dimensions]
    data_points = [dimension.normalized_score for dimension in dimensions]

    return {
        "type": "radar",
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "label": "Dimension Scores",
                    "data": data_points,
                    "backgroundColor": _RADAR_FILL_COLOR,
                    "borderColor": _RADAR_BORDER_COLOR,
                    "borderWidth": 2,
                    "fill": True,
                },
            ],
        },
        "options": {
            "scales": {
                "r": {
                    "min": 0,
                    "max": 10,
                    "ticks": {"stepSize": 2},
                },
            },
            "plugins": {
                "legend": {"display": False},
            },
        },
    }


def build_gauge_config(score: float, rating: str) -> dict:
    """Build a Chart.js doughnut chart config that looks like a gauge.

    The filled arc represents the score (0-100), the remainder is gray.
    Color varies by rating: Excellent=green, Good=blue,
    Needs Attention=orange, Critical=red.
    Half-rotation (180 degrees) creates the gauge appearance.
    """
    fill_color = _RATING_COLORS.get(rating, _GRAY)
    remainder = 100.0 - score

    return {
        "type": "doughnut",
        "data": {
            "datasets": [
                {
                    "data": [score, remainder],
                    "backgroundColor": [fill_color, _GRAY],
                    "borderWidth": 0,
                },
            ],
        },
        "options": {
            "rotation": -90,
            "circumference": 180,
            "cutout": "70%",
            "plugins": {
                "legend": {"display": False},
                "tooltip": {"enabled": False},
            },
        },
    }


def build_dimension_bars_config(dimensions: list[DimensionScore]) -> dict:
    """Build a Chart.js horizontal bar chart config for dimension scores.

    Dimensions are sorted by score ascending (weakest first).
    Bar color: red for <4, orange for <6, green for >=6.
    """
    sorted_dimensions = sorted(dimensions, key=lambda d: d.normalized_score)
    labels = [dimension.name for dimension in sorted_dimensions]
    data_points = [dimension.normalized_score for dimension in sorted_dimensions]
    colors = [_bar_color_for_score(score) for score in data_points]

    return {
        "type": "bar",
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "label": "Score",
                    "data": data_points,
                    "backgroundColor": colors,
                    "borderWidth": 0,
                },
            ],
        },
        "options": {
            "indexAxis": "y",
            "scales": {
                "x": {
                    "min": 0,
                    "max": 10,
                },
            },
            "plugins": {
                "legend": {"display": False},
            },
        },
    }


def find_weakest_dimension(
    dimensions: list[DimensionScore],
) -> DimensionScore | None:
    """Return the dimension with the lowest normalized_score, or None if empty."""
    if not dimensions:
        return None
    return min(dimensions, key=lambda d: d.normalized_score)
