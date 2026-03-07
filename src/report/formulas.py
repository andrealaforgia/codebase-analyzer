"""Formula display string generators for score normalization.

Each function produces a human-readable string showing the normalization
formula with actual values substituted -- used in the score derivation panel.

All functions are pure: no side effects, no I/O.
"""

from __future__ import annotations


def code_quality_formula_display(grade: str, score: float) -> str:
    """Show grade-to-score mapping with the actual grade highlighted."""
    return (
        f"Grade {grade} -> {score:.1f} "
        f"(mapping: A=10, B=8, C=6, D=4, F=2)"
    )


def code_quality_explanation(grade: str) -> str:
    """Plain-language explanation of code quality grade."""
    explanations = {
        "A": "Excellent code quality with minimal smells. The codebase follows clean code principles well.",
        "B": "Good code quality with some minor smells. Most code follows clean code principles.",
        "C": "Moderate code quality. Several code smells indicate areas needing attention.",
        "D": "Poor code quality with significant smells. The codebase needs substantial cleanup.",
        "F": "Critical code quality issues. Pervasive code smells impede maintainability.",
    }
    return explanations.get(grade, f"Code quality grade: {grade}")


def test_design_formula_display(farley_index: float) -> str:
    """Show Farley Index direct passthrough."""
    return f"Farley Index = {farley_index} (direct passthrough, scale 0-10)"


def test_design_explanation(farley_index: float) -> str:
    """Plain-language explanation of test design quality."""
    if farley_index >= 8.0:
        quality = "excellent"
    elif farley_index >= 6.0:
        quality = "good"
    elif farley_index >= 4.0:
        quality = "moderate"
    else:
        quality = "poor"
    return (
        f"Test design quality is {quality} (Farley Index {farley_index}/10). "
        f"Measures how well tests are understandable, maintainable, and isolated."
    )


def cognitive_load_formula_display(cli_score: int, normalized: float) -> str:
    """Show cognitive load inversion formula with values."""
    return (
        f"10 - ({cli_score} / 100) = {normalized:.2f} "
        f"-> clamped to [0, 10] = {normalized:.2f}"
    )


def cognitive_load_explanation(cli_score: int, normalized: float) -> str:
    """Plain-language explanation of cognitive load score."""
    if normalized >= 8.0:
        level = "low"
    elif normalized >= 5.0:
        level = "moderate"
    else:
        level = "high"
    return (
        f"Cognitive load is {level} (CLI score {cli_score}/1000). "
        f"Lower cognitive load means the code is easier to understand and modify."
    )


def ddd_compliance_formula_display(overall_score: float) -> str:
    """Show DDD score direct passthrough."""
    return f"DDD overall score = {overall_score} (agent self-assessed, scale 0-10)"


def ddd_compliance_explanation(overall_score: float) -> str:
    """Plain-language explanation of DDD compliance."""
    if overall_score >= 8.0:
        quality = "strong"
    elif overall_score >= 5.0:
        quality = "moderate"
    else:
        quality = "weak"
    return (
        f"Domain-driven design compliance is {quality} (score {overall_score}/10). "
        f"Measures bounded context clarity, ubiquitous language usage, and pattern maturity."
    )


def legacy_safety_formula_display(overall_score: float) -> str:
    """Show legacy safety score direct passthrough."""
    return f"Legacy safety score = {overall_score} (agent self-assessed, scale 0-10)"


def legacy_safety_explanation(overall_score: float) -> str:
    """Plain-language explanation of legacy safety."""
    if overall_score >= 7.0:
        quality = "safe"
    elif overall_score >= 4.0:
        quality = "moderate risk"
    else:
        quality = "high risk"
    return (
        f"Legacy code safety is {quality} (score {overall_score}/10). "
        f"Measures testability, seam availability, and dependency risk."
    )


def refactoring_debt_formula_display(
    high: int, medium: int, low: int, weighted_count: int, score: float,
) -> str:
    """Show refactoring debt weighted calculation."""
    return (
        f"10 - ({high}x3 + {medium}x2 + {low}x1) / 5 "
        f"= 10 - {weighted_count}/5 "
        f"= 10 - {weighted_count / 5:.1f} "
        f"= {score:.1f}"
    )


def refactoring_debt_explanation(score: float) -> str:
    """Plain-language explanation of refactoring debt."""
    if score >= 8.0:
        level = "low"
    elif score >= 5.0:
        level = "moderate"
    else:
        level = "high"
    return (
        f"Refactoring debt is {level} (score {score:.1f}/10). "
        f"Based on weighted count of high, medium, and low risk recommendations."
    )
