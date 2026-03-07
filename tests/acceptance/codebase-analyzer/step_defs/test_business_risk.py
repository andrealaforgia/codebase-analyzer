"""Step definitions for business risk assessment scenarios.

Tests invoke the risk engine through its driving port -- a pure function
that accepts normalized dimension scores and returns risk assessments.

TODO: Replace stubs with actual imports once implemented:
    from src.report.risk import (
        assess_delivery_velocity_risk,
        assess_incident_risk,
        assess_onboarding_risk,
        assess_all_risks,
    )
"""

from pytest_bdd import scenarios, given, when, then, parsers

scenarios("../features/business_risk.feature")


# --- Given Steps ---


@given("the dimension scores have been normalized for a codebase analysis")
def dimension_scores_normalized():
    """Background step: confirms we are working with normalized scores."""
    pass


@given("these dimension scores:", target_fixture="risk_dimension_scores")
def dimension_scores_for_risk(datatable):
    return {row["dimension"]: float(row["score"]) for row in datatable}


@given("the DDD agent failed and only 5 dimension scores are available")
def ddd_agent_failed(acme_corp_dimension_scores):
    scores = dict(acme_corp_dimension_scores)
    del scores["DDD Compliance"]
    return scores


@given(
    "only Code Quality and Test Design scores are available",
    target_fixture="risk_dimension_scores",
)
def only_two_dimensions():
    return {"Code Quality": 6.0, "Test Design": 7.2}


@given("the same dimension scores", target_fixture="risk_dimension_scores")
def same_dimension_scores(acme_corp_dimension_scores):
    return acme_corp_dimension_scores


@given("any valid combination of dimension scores")
def any_valid_scores():
    pass


# --- When Steps ---


@when(
    "the Delivery Velocity Risk is assessed",
    target_fixture="velocity_risk",
)
def assess_velocity_risk(risk_dimension_scores):
    """Invoke risk engine driving port for Delivery Velocity Risk.

    TODO: Replace with actual risk engine call:
        from src.report.risk import assess_delivery_velocity_risk
        return assess_delivery_velocity_risk(risk_dimension_scores)
    """
    raise NotImplementedError("Risk engine not yet implemented.")


@when("the Incident Risk is assessed", target_fixture="incident_risk")
def assess_incident_risk(risk_dimension_scores):
    raise NotImplementedError("Risk engine not yet implemented.")


@when("the Onboarding Risk is assessed", target_fixture="onboarding_risk")
def assess_onboarding_risk(risk_dimension_scores):
    raise NotImplementedError("Risk engine not yet implemented.")


@when(
    "all business risk categories are assessed",
    target_fixture="all_risks",
)
def assess_all_risks(risk_dimension_scores):
    """Invoke risk engine driving port for all risk categories.

    TODO: Replace with actual risk engine call:
        from src.report.risk import assess_all_risks
        return assess_all_risks(risk_dimension_scores)
    """
    raise NotImplementedError("Risk engine not yet implemented.")


@when("the risk model is applied twice", target_fixture="dual_risk_results")
def apply_risk_model_twice(risk_dimension_scores):
    raise NotImplementedError("Risk engine not yet implemented.")


@when("business risk categories are assessed", target_fixture="all_risks")
def assess_risks_property(risk_dimension_scores):
    raise NotImplementedError("Risk engine not yet implemented.")


# --- Then Steps ---


@then(parsers.parse('the risk severity is "{severity}"'))
def risk_severity_matches(severity):
    pass


@then(
    parsers.parse("the contributing dimensions include {dimensions}"),
)
def contributing_dimensions(dimensions):
    pass


@then("the description mentions estimated velocity impact")
def description_mentions_velocity_impact():
    pass


@then("the report includes at least 3 risk categories")
def at_least_three_categories(all_risks):
    assert len(all_risks) >= 3


@then("each category has a severity level and description")
def each_category_has_severity_and_description(all_risks):
    for risk in all_risks.values():
        assert "severity" in risk
        assert "description" in risk


@then("each category cites contributing dimensions")
def each_category_cites_dimensions(all_risks):
    for risk in all_risks.values():
        assert "contributing_dimensions" in risk


@then('all risk categories are rated "LOW"')
def all_risks_low(all_risks):
    for category, risk in all_risks.items():
        assert risk["severity"] == "LOW", (
            f"{category} is {risk['severity']}, expected LOW"
        )


@then("the summary notes healthy technical foundations")
def summary_notes_healthy(all_risks):
    pass


@then(parsers.parse('Delivery Velocity Risk is "{severity}"'))
def velocity_risk_severity(all_risks, severity):
    assert all_risks["Delivery Velocity"]["severity"] == severity


@then(parsers.parse('Incident Risk is "{severity}"'))
def incident_risk_severity(all_risks, severity):
    assert all_risks["Incident"]["severity"] == severity


@then(parsers.parse('Onboarding Risk is "{severity}"'))
def onboarding_risk_severity(all_risks, severity):
    assert all_risks["Onboarding"]["severity"] == severity


@then("risk categories that depend on DDD use only the available dimensions")
def ddd_excluded_from_risk(all_risks):
    pass


@then("the assessment notes which dimensions were unavailable")
def notes_unavailable_dimensions(all_risks):
    pass


@then("categories with sufficient data produce a severity rating")
def sufficient_data_categories(all_risks):
    pass


@then("categories with insufficient data note limited confidence")
def insufficient_data_noted(all_risks):
    pass


@then("no risk category contradicts its underlying dimension scores")
def no_contradictions(all_risks):
    pass


@then("higher dimension scores never produce higher risk severity")
def monotonic_risk(all_risks):
    pass


@then("both assessments produce identical results")
def deterministic_results(dual_risk_results):
    assert dual_risk_results[0] == dual_risk_results[1]
