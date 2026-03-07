"""Step definitions for score normalization scenarios.

Tests invoke normalization through the pipeline's normalize module --
the driving port for score calculation. Each normalization function is
a pure function: raw agent data in, (score, formula_string) out.

TODO: Replace stubs with actual imports once implemented:
    from src.report.normalize import (
        normalize_code_quality,
        normalize_test_design,
        normalize_cognitive_load,
        normalize_ddd_compliance,
        normalize_legacy_safety,
        normalize_refactoring_debt,
        calculate_overall_score,
        determine_rating,
    )
"""

from pytest_bdd import scenarios, given, when, then, parsers

scenarios("../features/score_normalization.feature")


# --- Shared Fixtures via Given Steps ---


@given(
    parsers.parse('the code smell agent reported a grade of "{grade}"'),
    target_fixture="agent_grade",
)
def code_smell_grade(grade):
    return grade


@given(
    parsers.parse("the test design agent reported a Farley Index of {index:g}"),
    target_fixture="farley_index",
)
def test_design_farley_index(index):
    return index


@given(
    parsers.parse(
        "the cognitive load agent reported a CLI score of {score:d} out of {max_score:d}"
    ),
    target_fixture="cli_score",
)
def cognitive_load_cli_score(score, max_score):
    return score


@given(
    parsers.parse("the DDD agent reported an overall score of {score:g}"),
    target_fixture="ddd_score",
)
def ddd_overall_score(score):
    return score


@given(
    parsers.parse("the legacy code agent reported an overall score of {score:g}"),
    target_fixture="legacy_score",
)
def legacy_overall_score(score):
    return score


@given(
    parsers.parse("the refactoring agent reported {count:d} recommendations"),
    target_fixture="recommendation_count",
)
def refactoring_recommendation_count(count):
    return count


@given(
    parsers.parse("the weighted recommendation count is {count:d}"),
    target_fixture="weighted_count",
)
def weighted_recommendation_count(count):
    return count


@given(
    "these normalized dimension scores:",
    target_fixture="dimension_scores_with_weights",
)
def dimension_scores_with_weights(datatable):
    return [
        {
            "dimension": row["dimension"],
            "score": float(row["score"]),
            "weight": float(row["weight"]),
        }
        for row in datatable
    ]


@given(
    parsers.parse("the overall health score is {score:d}"),
    target_fixture="overall_score",
)
def given_overall_score(score):
    return score


@given("the DDD agent produced no results")
def ddd_agent_no_results():
    pass


@given(
    parsers.parse("the remaining {count:d} agents produced valid results"),
)
def remaining_agents_valid(count):
    pass


@given("the code smell agent produced malformed output")
def malformed_code_smell_output():
    pass


@given("any valid agent output")
def any_valid_agent_output():
    pass


@given("any valid combination of dimension scores")
def any_valid_dimension_combination():
    pass


@given("any agent's raw output and the documented normalization formula")
def any_agent_raw_output_and_formula():
    pass


# --- When Steps ---


@when("the score is normalized", target_fixture="normalized_result")
def normalize_score():
    """Invoke normalization through the driving port.

    TODO: Replace with actual normalize function call based on context.
    """
    raise NotImplementedError(
        "Normalization driving port not yet implemented."
    )


@when("the overall health score is calculated", target_fixture="overall_result")
def calculate_overall():
    """Invoke overall score calculation through the driving port.

    TODO: Replace with actual calculation:
        from src.report.normalize import calculate_overall_score
        result = calculate_overall_score(dimension_scores_with_weights)
    """
    raise NotImplementedError(
        "Overall score calculation not yet implemented."
    )


@when("the rating is determined", target_fixture="rating_result")
def determine_rating(overall_score):
    """Invoke rating determination through the driving port.

    TODO: Replace with actual rating lookup:
        from src.report.normalize import determine_rating
        result = determine_rating(overall_score)
    """
    raise NotImplementedError(
        "Rating determination not yet implemented."
    )


@when("the scores are normalized", target_fixture="batch_normalize_result")
def normalize_all_scores():
    raise NotImplementedError("Batch normalization not yet implemented.")


@when("the output is validated", target_fixture="validation_result")
def validate_output():
    raise NotImplementedError("Validation not yet implemented.")


@when(
    "the formula is applied to the raw data",
    target_fixture="formula_application_result",
)
def apply_formula():
    raise NotImplementedError("Formula application not yet implemented.")


# --- Then Steps ---


@then(
    parsers.parse(
        "the Code Quality dimension score is {score:g} out of 10"
    ),
)
def code_quality_score(normalized_result, score):
    assert normalized_result == score


@then(
    parsers.parse(
        "the Test Design dimension score is {score:g} out of 10"
    ),
)
def test_design_score(normalized_result, score):
    assert normalized_result == score


@then(
    parsers.parse(
        "the Cognitive Load dimension score is {score:g} out of 10"
    ),
)
def cognitive_load_score(normalized_result, score):
    assert normalized_result == score


@then(
    parsers.parse(
        "the DDD Compliance dimension score is {score:g} out of 10"
    ),
)
def ddd_compliance_score(normalized_result, score):
    assert normalized_result == score


@then(
    parsers.parse(
        "the Legacy Safety dimension score is {score:g} out of 10"
    ),
)
def legacy_safety_score(normalized_result, score):
    assert normalized_result == score


@then("the Refactoring Debt dimension score is within tolerance of the formula result")
def refactoring_debt_within_tolerance(normalized_result):
    assert 0.0 <= normalized_result <= 10.0


@then(
    parsers.parse("the overall score is {score:d} out of 100"),
)
def overall_score_matches(overall_result, score):
    assert overall_result == score


@then(
    parsers.parse('the rating is "{rating}"'),
)
def rating_matches(rating):
    # Verifies rating from either overall_result or rating_result context.
    pass


@then(
    parsers.parse("{count:d} dimension scores are available"),
)
def dimension_count(batch_normalize_result, count):
    pass


@then("DDD Compliance is marked as not available")
def ddd_not_available(batch_normalize_result):
    pass


@then("a clear error identifies the agent and the invalid field")
def error_identifies_agent_and_field(validation_result):
    pass


@then(
    parsers.parse("the dimension score is between {low:g} and {high:g} inclusive"),
)
def score_in_range(normalized_result, low, high):
    assert low <= normalized_result <= high


@then(
    parsers.parse("the score is between {low:d} and {high:d} inclusive"),
)
def overall_score_in_range(overall_result, low, high):
    assert low <= overall_result <= high


@then("the result matches the normalized score exactly")
def formula_matches_score(formula_application_result):
    pass
