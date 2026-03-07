"""Step definitions for report generation scenarios.

Tests invoke the report generator through its driving port -- the pipeline
entry point that accepts assembled report data and produces an HTML file.
Report content is verified by parsing the generated HTML.

TODO: Replace stubs with actual imports once implemented:
    from src.report.pipeline import generate_report
    from src.report.render import render_report
"""

from pytest_bdd import scenarios, given, when, then, parsers

scenarios("../features/report_generation.feature")


# --- Given Steps ---


@given(
    'analysis results are available for the "Acme Corp Platform" project',
    target_fixture="project_name",
)
def analysis_results_available():
    return "Acme Corp Platform"


@given("all 6 agents completed successfully")
def all_agents_completed():
    pass


@given(
    parsers.parse("the overall health score is {score:d} out of 100"),
    target_fixture="overall_score",
)
def given_overall_score(score):
    return score


@given(parsers.parse('the rating is "{rating}"'), target_fixture="overall_rating")
def given_overall_rating(rating):
    return rating


@given("all 6 dimension scores are available")
def all_six_scores_available():
    pass


@given(
    parsers.parse("Refactoring Debt is the lowest score at {score:g} out of 10"),
    target_fixture="weakest_dimension",
)
def weakest_dimension(score):
    return {"name": "Refactoring Debt", "score": score}


@given("the risk model has been applied to the dimension scores")
def risk_model_applied():
    pass


@given(parsers.parse('Delivery Velocity Risk is rated "{severity}"'))
def velocity_risk_rated(severity):
    pass


@given(
    parsers.parse("the code smell agent found {count:d} issues across severity levels"),
)
def code_smell_issues(count):
    pass


@given(parsers.parse("the test design agent produced {count:d} property scores"))
def test_design_properties(count):
    pass


@given("a dimension detail section is in the report")
def dimension_detail_exists():
    pass


@given(
    "the DDD agent failed and only 5 dimension scores are available",
    target_fixture="partial_results",
)
def ddd_failed_5_dimensions():
    return {"missing": ["DDD Compliance"], "available_count": 5}


@given(
    "only the Code Quality agent completed",
    target_fixture="partial_results",
)
def only_code_quality():
    return {"missing": [
        "Test Design", "Cognitive Load", "DDD Compliance",
        "Legacy Safety", "Refactoring Debt",
    ], "available_count": 1}


@given("the report has been generated", target_fixture="generated_report_path")
def report_already_generated(output_path):
    # Placeholder: in actual tests, will generate the report first.
    return output_path


@given("no agent results are available")
def no_agent_results():
    pass


@given("one agent produced data with missing required fields")
def one_agent_malformed():
    pass


@given("the same set of agent results")
def same_agent_results():
    pass


# --- When Steps ---


@when("the report is generated", target_fixture="report_generation_result")
def generate_report(project_name, all_agent_data, output_path):
    """Invoke report generation through the pipeline driving port.

    TODO: Replace with actual pipeline call:
        from src.report.pipeline import generate_report
        return generate_report(
            agent_data_dir=agent_data_dir,
            project_name=project_name,
            output_path=output_path,
        )
    """
    raise NotImplementedError("Report generation not yet implemented.")


@when("the output file is examined", target_fixture="report_file_analysis")
def examine_output_file(generated_report_path):
    raise NotImplementedError("Report file examination not yet implemented.")


@when("the HTML is parsed", target_fixture="parsed_html")
def parse_html(generated_report_path):
    raise NotImplementedError("HTML parsing not yet implemented.")


@when("report generation is attempted", target_fixture="report_error_result")
def attempt_report_generation():
    raise NotImplementedError("Error path report generation not yet implemented.")


@when(
    "the report is generated twice",
    target_fixture="dual_report_results",
)
def generate_report_twice():
    raise NotImplementedError("Dual report generation not yet implemented.")


# --- Then Steps ---


@then(parsers.parse('the executive summary displays the score "{score}" prominently'))
def summary_displays_score(report_generation_result, score):
    pass


@then(
    parsers.parse(
        'the rating "{rating}" is displayed alongside the score'
    ),
)
def rating_displayed(report_generation_result, rating):
    pass


@then(parsers.parse("the radar chart has {count:d} labeled axes"))
def radar_chart_axes(report_generation_result, count):
    pass


@then("each axis shows the corresponding dimension score")
def axes_show_scores(report_generation_result):
    pass


@then("the chart shape reflects the relative strengths and weaknesses")
def chart_shape_reflects_scores(report_generation_result):
    pass


@then("Refactoring Debt is visually highlighted as the weakest dimension")
def weakest_highlighted(report_generation_result):
    pass


@then("a risk annotation explains the impact of the low score")
def risk_annotation_present(report_generation_result):
    pass


@then(
    "each dimension shows its name, numeric score, and a plain-language rating"
)
def dimension_bars_complete(report_generation_result):
    pass


@then("the dimensions are ordered by score for easy scanning")
def dimensions_ordered(report_generation_result):
    pass


@then("the business risk summary section is present")
def risk_summary_present(report_generation_result):
    pass


@then(
    "it shows Delivery Velocity Risk, Incident Risk, and Onboarding Risk"
)
def three_risk_categories(report_generation_result):
    pass


@then("each risk has a severity badge and descriptive text")
def risk_severity_badges(report_generation_result):
    pass


@then("the Delivery Velocity Risk section references the contributing dimensions")
def velocity_references_dimensions(report_generation_result):
    pass


@then("links navigate to the relevant dimension detail sections")
def links_navigate_to_details(report_generation_result):
    pass


@then(
    parsers.parse("{count:d} dimension detail sections are present in the report"),
)
def dimension_sections_count(report_generation_result, count):
    pass


@then("each section is accessible from the executive summary")
def sections_accessible_from_summary(report_generation_result):
    pass


@then("the Code Quality section shows the grade prominently")
def grade_prominent(report_generation_result):
    pass


@then("a severity distribution breakdown is displayed")
def severity_breakdown(report_generation_result):
    pass


@then("a category distribution breakdown is displayed")
def category_breakdown(report_generation_result):
    pass


@then("the Test Design section shows the Farley Index prominently")
def farley_index_prominent(report_generation_result):
    pass


@then("individual property scores are displayed")
def property_scores_displayed(report_generation_result):
    pass


@then("each dimension section includes a link to its score derivation panel")
def sections_link_to_derivation(report_generation_result):
    pass


@then("the report is generated without errors")
def report_generated_without_errors(report_generation_result):
    pass


@then(parsers.parse("the radar chart shows {count:d} axes instead of 6"))
def radar_chart_fewer_axes(report_generation_result, count):
    pass


@then(
    parsers.parse(
        'the DDD section shows "Not Available" with the failure reason'
    ),
)
def ddd_not_available(report_generation_result):
    pass


@then(
    "the overall score is calculated from 5 dimensions with adjusted weights"
)
def adjusted_weights_5(report_generation_result):
    pass


@then("the overall score is based on the single available dimension")
def single_dimension_score(report_generation_result):
    pass


@then(parsers.parse('{count:d} sections show "Not Available"'))
def sections_not_available(report_generation_result, count):
    pass


@then("the file has an .html extension")
def html_extension(report_file_analysis):
    pass


@then("all visualization libraries are embedded within the file")
def libraries_embedded(report_file_analysis):
    pass


@then("no external resource references exist in the HTML")
def no_external_references(report_file_analysis):
    pass


@then(
    "report data is embedded as a data structure within the file"
)
def data_embedded(parsed_html):
    pass


@then("chart configurations are derived from the embedded data")
def charts_from_embedded_data(parsed_html):
    pass


@then("a clear error indicates no analysis data was found")
def error_no_data(report_error_result):
    pass


@then("no partial or corrupt HTML file is produced")
def no_partial_file(report_error_result, output_path):
    assert not output_path.exists()


@then(
    parsers.parse(
        'the dimension with invalid data is marked as "Not Available"'
    ),
)
def invalid_dimension_not_available(report_generation_result):
    pass


@then("the error reason identifies the malformed field")
def error_identifies_field(report_generation_result):
    pass


@then("other dimensions render correctly")
def other_dimensions_render(report_generation_result):
    pass


@then("both reports contain identical scores and risk ratings")
def reports_identical(dual_report_results):
    pass


@then("the report contains an executive summary with overall score")
def has_executive_summary(report_generation_result):
    pass


@then(parsers.parse("the report contains {count:d} dimension detail sections"))
def has_dimension_sections(report_generation_result, count):
    pass


@then("the report contains a business risk summary")
def has_risk_summary(report_generation_result):
    pass
