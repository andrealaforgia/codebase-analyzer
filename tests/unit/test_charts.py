"""Unit tests for chart configuration builder functions.

Tests verify that pure functions in charts.py produce valid Chart.js
configuration dictionaries from DimensionScore data.
"""

import pytest

from src.report.charts import (
    build_dimension_bars_config,
    build_gauge_config,
    build_radar_config,
    find_weakest_dimension,
)
from src.report.models import DimensionScore


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------


def _make_dimension(
    name: str = "code_quality",
    normalized_score: float = 7.5,
    weight: float = 0.20,
) -> DimensionScore:
    """Build a minimal valid DimensionScore for testing."""
    return DimensionScore(
        name=name,
        raw_score=normalized_score,
        normalized_score=normalized_score,
        weight=weight,
        formula_display=f"formula = {normalized_score}",
        explanation=f"{name} explanation",
    )


def _make_dimensions() -> list[DimensionScore]:
    """Build a representative set of dimension scores for testing."""
    return [
        _make_dimension("Code Quality", 7.5),
        _make_dimension("Test Design", 6.0),
        _make_dimension("Cognitive Load", 8.2),
        _make_dimension("DDD Compliance", 3.5, weight=0.15),
        _make_dimension("Legacy Safety", 5.0, weight=0.15),
        _make_dimension("Refactoring Debt", 4.0, weight=0.10),
    ]


# ---------------------------------------------------------------------------
# build_radar_config
# ---------------------------------------------------------------------------


class TestBuildRadarConfig:
    def test_returns_radar_chart_type(self):
        config = build_radar_config(_make_dimensions())
        assert config["type"] == "radar"

    def test_labels_match_dimension_names(self):
        dimensions = _make_dimensions()
        config = build_radar_config(dimensions)
        labels = config["data"]["labels"]
        expected_names = [d.name for d in dimensions]
        assert labels == expected_names

    def test_data_points_match_normalized_scores(self):
        dimensions = _make_dimensions()
        config = build_radar_config(dimensions)
        data_points = config["data"]["datasets"][0]["data"]
        expected_scores = [d.normalized_score for d in dimensions]
        assert data_points == expected_scores

    def test_scale_max_is_ten(self):
        config = build_radar_config(_make_dimensions())
        scale_max = config["options"]["scales"]["r"]["max"]
        assert scale_max == 10

    def test_scale_min_is_zero(self):
        config = build_radar_config(_make_dimensions())
        scale_min = config["options"]["scales"]["r"]["min"]
        assert scale_min == 0

    def test_has_semi_transparent_blue_fill(self):
        config = build_radar_config(_make_dimensions())
        dataset = config["data"]["datasets"][0]
        assert "rgba" in dataset["backgroundColor"]
        assert dataset["fill"] is True

    def test_empty_dimensions_returns_empty_labels_and_data(self):
        config = build_radar_config([])
        assert config["data"]["labels"] == []
        assert config["data"]["datasets"][0]["data"] == []


# ---------------------------------------------------------------------------
# build_gauge_config
# ---------------------------------------------------------------------------


class TestBuildGaugeConfig:
    def test_returns_doughnut_chart_type(self):
        config = build_gauge_config(75.0, "Good")
        assert config["type"] == "doughnut"

    def test_score_value_in_data(self):
        config = build_gauge_config(75.0, "Good")
        data_values = config["data"]["datasets"][0]["data"]
        assert data_values[0] == 75.0

    def test_remainder_fills_to_hundred(self):
        config = build_gauge_config(75.0, "Good")
        data_values = config["data"]["datasets"][0]["data"]
        assert data_values[0] + data_values[1] == 100.0

    def test_excellent_rating_uses_green(self):
        config = build_gauge_config(90.0, "Excellent")
        colors = config["data"]["datasets"][0]["backgroundColor"]
        assert "#28a745" in colors[0] or "green" in colors[0].lower()

    def test_good_rating_uses_blue(self):
        config = build_gauge_config(70.0, "Good")
        colors = config["data"]["datasets"][0]["backgroundColor"]
        assert "#007bff" in colors[0] or "blue" in colors[0].lower()

    def test_needs_attention_rating_uses_orange(self):
        config = build_gauge_config(50.0, "Needs Attention")
        colors = config["data"]["datasets"][0]["backgroundColor"]
        assert "#fd7e14" in colors[0] or "orange" in colors[0].lower()

    def test_critical_rating_uses_red(self):
        config = build_gauge_config(25.0, "Critical")
        colors = config["data"]["datasets"][0]["backgroundColor"]
        assert "#dc3545" in colors[0] or "red" in colors[0].lower()

    def test_half_rotation_for_gauge_appearance(self):
        config = build_gauge_config(75.0, "Good")
        assert config["options"]["rotation"] == -90
        assert config["options"]["circumference"] == 180


# ---------------------------------------------------------------------------
# build_dimension_bars_config
# ---------------------------------------------------------------------------


class TestBuildDimensionBarsConfig:
    def test_returns_bar_chart_type(self):
        config = build_dimension_bars_config(_make_dimensions())
        assert config["type"] == "bar"

    def test_horizontal_orientation(self):
        config = build_dimension_bars_config(_make_dimensions())
        assert config["options"]["indexAxis"] == "y"

    def test_labels_sorted_by_score_ascending(self):
        dimensions = _make_dimensions()
        config = build_dimension_bars_config(dimensions)
        labels = config["data"]["labels"]
        # Weakest first: DDD (3.5), Refactoring (4.0), Legacy (5.0),
        # Test Design (6.0), Code Quality (7.5), Cognitive Load (8.2)
        assert labels[0] == "DDD Compliance"
        assert labels[-1] == "Cognitive Load"

    def test_data_sorted_ascending(self):
        config = build_dimension_bars_config(_make_dimensions())
        data = config["data"]["datasets"][0]["data"]
        assert data == sorted(data)

    def test_red_color_for_score_below_four(self):
        config = build_dimension_bars_config(_make_dimensions())
        colors = config["data"]["datasets"][0]["backgroundColor"]
        # First bar is DDD Compliance at 3.5 -- should be red
        assert "#dc3545" in colors[0] or "red" in colors[0].lower()

    def test_orange_color_for_score_between_four_and_six(self):
        config = build_dimension_bars_config(_make_dimensions())
        colors = config["data"]["datasets"][0]["backgroundColor"]
        # Refactoring Debt at 4.0 and Legacy Safety at 5.0 should be orange
        assert "#fd7e14" in colors[1] or "orange" in colors[1].lower()

    def test_green_color_for_score_six_or_above(self):
        config = build_dimension_bars_config(_make_dimensions())
        colors = config["data"]["datasets"][0]["backgroundColor"]
        # Cognitive Load at 8.2 is last -- should be green
        assert "#28a745" in colors[-1] or "green" in colors[-1].lower()

    def test_empty_dimensions_returns_empty_data(self):
        config = build_dimension_bars_config([])
        assert config["data"]["labels"] == []
        assert config["data"]["datasets"][0]["data"] == []


# ---------------------------------------------------------------------------
# find_weakest_dimension
# ---------------------------------------------------------------------------


class TestFindWeakestDimension:
    def test_returns_dimension_with_lowest_score(self):
        dimensions = _make_dimensions()
        weakest = find_weakest_dimension(dimensions)
        assert weakest is not None
        assert weakest.name == "DDD Compliance"
        assert weakest.normalized_score == 3.5

    def test_returns_none_for_empty_list(self):
        result = find_weakest_dimension([])
        assert result is None

    def test_single_dimension_returns_that_dimension(self):
        dimension = _make_dimension("Only One", 5.0)
        result = find_weakest_dimension([dimension])
        assert result is not None
        assert result.name == "Only One"

    def test_tie_returns_first_occurrence(self):
        dimensions = [
            _make_dimension("First", 3.0),
            _make_dimension("Second", 3.0),
        ]
        result = find_weakest_dimension(dimensions)
        assert result is not None
        assert result.name == "First"
