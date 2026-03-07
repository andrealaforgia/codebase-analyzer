"""Step definitions for the walking skeleton scenarios.

These tests invoke the pipeline through its driving port (the pipeline
entry point function), using fixture JSON data in place of real agent output.

Walking skeletons validate the thinnest E2E slice: agent data -> normalization
-> risk assessment -> HTML report with observable user value.
"""

from pytest_bdd import scenarios, given, when, then, parsers

# Register all scenarios from the walking skeleton feature file.
scenarios("../features/walking_skeleton.feature")


# --- Given Steps ---


@given(
    'analysis results are available for the "Acme Corp Platform" project',
    target_fixture="project_name",
)
def analysis_results_available():
    """Project context for the analysis."""
    return "Acme Corp Platform"


@given("the analysis included all 6 quality dimensions")
def all_six_dimensions():
    """Confirms all agents produced results (fixture default)."""
    pass


@given(
    "the analysis produced these dimension scores:",
    target_fixture="dimension_scores",
)
def dimension_scores_from_table(datatable):
    """Parse dimension scores from the Gherkin data table."""
    scores = {}
    for row in datatable:
        scores[row["dimension"]] = float(row["score"])
    return scores


# --- When Steps ---


@when(
    parsers.parse('the report is generated for "{project_name}"'),
    target_fixture="generated_report",
)
def generate_report(project_name, dimension_scores, output_path):
    """Invoke the report pipeline through its driving port.

    This is the primary entry point -- the driving port for acceptance tests.
    It orchestrates: normalize -> risk -> assemble -> render -> write.

    TODO: Replace with actual pipeline invocation once implemented:
        from src.report.pipeline import generate_report
        result = generate_report(
            agent_data=dimension_scores,
            project_name=project_name,
            output_path=output_path,
        )
    """
    # Placeholder: will be replaced with real pipeline call.
    # For now, return a stub that the first scenario can fail against
    # for the right business reason (pipeline not implemented).
    raise NotImplementedError(
        "Pipeline driving port not yet implemented. "
        "This is the expected first failure in outside-in TDD."
    )


# --- Then Steps ---


@then("Andrea receives a self-contained HTML report")
def report_is_self_contained(generated_report, output_path):
    """Verify the report file exists and is valid HTML."""
    assert output_path.exists(), f"Report file not found at {output_path}"
    content = output_path.read_text()
    assert "<html" in content.lower(), "Output is not an HTML file"


@then(
    parsers.parse("the report shows an overall health score of {score:d} out of 100"),
)
def report_shows_overall_score(generated_report, output_path, score):
    """Verify the overall health score is present in the report."""
    content = output_path.read_text()
    assert str(score) in content, (
        f"Overall score {score} not found in report"
    )


@then(
    parsers.parse('the report displays the rating "{rating}"'),
)
def report_displays_rating(generated_report, output_path, rating):
    """Verify the rating label is present in the report."""
    content = output_path.read_text()
    assert rating in content, f"Rating '{rating}' not found in report"


@then("the report includes a radar chart with all 6 dimensions")
def report_has_radar_chart(generated_report, output_path):
    """Verify the radar chart configuration exists in the report."""
    content = output_path.read_text()
    # Radar chart implemented via Chart.js -- look for radar type config
    assert "radar" in content.lower(), "Radar chart not found in report"


@then("each dimension score is visible in the report")
def all_dimension_scores_visible(generated_report, output_path, dimension_scores):
    """Verify every dimension score appears in the report."""
    content = output_path.read_text()
    for dimension, score in dimension_scores.items():
        assert dimension in content, f"Dimension '{dimension}' not found in report"
