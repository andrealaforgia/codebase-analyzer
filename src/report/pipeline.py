"""Report generation pipeline -- composition root.

Chains all pure functions into a single pipeline:
    load_agent_results -> build_report_data -> render_report -> write_report

The pipeline separates pure computation from IO effects:
- load_agent_results: IO boundary (reads JSON files from disk)
- build_report_data: pure function (assembles ReportData from validated models)
- generate_report: IO boundary (orchestrates the full pipeline, writes output)

All domain logic (normalization, risk assessment, rendering) is delegated to
the pure functions in normalize.py, risk.py, render.py, and charts.py.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from src.report.models import (
    CodeSmellDetectorData,
    CognitiveLoadAnalyzerData,
    DDDArchitectData,
    DimensionScore,
    GenericAgentData,
    LegacyCodeExpertData,
    ProjectMetadata,
    RefactoringExpertData,
    ReportData,
    TestDesignReviewerData,
    compute_overall_score,
    derive_rating,
)
from src.report.normalize import normalize_all
from src.report.render import render_report, write_report
from src.report.risk import assess_all_risks
from src.report.sanitize import sanitize_agent_results


# ---------------------------------------------------------------------------
# Agent file mapping: agent_key -> expected JSON filename
# ---------------------------------------------------------------------------

AGENT_FILE_MAP: dict[str, str] = {
    # Original 6 agents
    "code_smell_detector": "code-smell-detector-data.json",
    "test_design_reviewer": "test-design-reviewer-data.json",
    "cognitive_load_analyzer": "cognitive-load-analyzer-data.json",
    "ddd_assessor": "ddd-architect-data.json",
    "legacy_code_analyzer": "legacy-code-expert-data.json",
    "refactoring_advisor": "refactoring-expert-data.json",
    # 15 generic agents
    "security_assessor": "security-assessor-data.json",
    "error_handling_reviewer": "error-handling-reviewer-data.json",
    "api_design_reviewer": "api-design-reviewer-data.json",
    "dependency_auditor": "dependency-auditor-data.json",
    "concurrency_analyzer": "concurrency-analyzer-data.json",
    "documentation_reviewer": "documentation-reviewer-data.json",
    "dead_code_detector": "dead-code-detector-data.json",
    "devops_evaluator": "devops-evaluator-data.json",
    "ownership_analyzer": "ownership-analyzer-data.json",
    "consistency_checker": "consistency-checker-data.json",
    "data_layer_reviewer": "data-layer-reviewer-data.json",
    "observability_assessor": "observability-assessor-data.json",
    # 3 additional agents
    "system_auditor": "system-auditor-data.json",
    "accessibility_assessor": "accessibility-assessor-data.json",
    "system_explorer": "system-explorer-data.json",
}

# ---------------------------------------------------------------------------
# Agent model mapping: agent_key -> Pydantic model class
# ---------------------------------------------------------------------------

AGENT_MODEL_MAP: dict[str, type] = {
    # Original 6 agents (specific models)
    "code_smell_detector": CodeSmellDetectorData,
    "test_design_reviewer": TestDesignReviewerData,
    "cognitive_load_analyzer": CognitiveLoadAnalyzerData,
    "ddd_assessor": DDDArchitectData,
    "legacy_code_analyzer": LegacyCodeExpertData,
    "refactoring_advisor": RefactoringExpertData,
    # 15 generic agents
    "security_assessor": GenericAgentData,
    "error_handling_reviewer": GenericAgentData,
    "api_design_reviewer": GenericAgentData,
    "dependency_auditor": GenericAgentData,
    "concurrency_analyzer": GenericAgentData,
    "documentation_reviewer": GenericAgentData,
    "dead_code_detector": GenericAgentData,
    "devops_evaluator": GenericAgentData,
    "ownership_analyzer": GenericAgentData,
    "consistency_checker": GenericAgentData,
    "data_layer_reviewer": GenericAgentData,
    "observability_assessor": GenericAgentData,
    # 3 additional agents (generic model)
    "system_auditor": GenericAgentData,
    "accessibility_assessor": GenericAgentData,
    "system_explorer": GenericAgentData,
}

# ---------------------------------------------------------------------------
# Dimension name mapping: snake_case (from normalize) -> display name (for risk)
# ---------------------------------------------------------------------------

_DIMENSION_DISPLAY_NAMES: dict[str, str] = {
    # Original 6
    "code_quality": "Code Quality",
    "test_design": "Test Design",
    "cognitive_load": "Cognitive Load",
    "ddd_compliance": "DDD Compliance",
    "legacy_safety": "Legacy Safety",
    "refactoring_debt": "Refactoring Debt",
    # 15 generic dimensions
    "security": "Security Posture",
    "error_handling": "Error Handling",
    "api_design": "API Design",
    "dependency_health": "Dependency Health",
    "concurrency": "Concurrency Safety",
    "documentation": "Documentation",
    "dead_code": "Dead Code",
    "devops_maturity": "DevOps Maturity",
    "code_ownership": "Code Ownership",
    "consistency": "Consistency",
    "data_layer": "Data Layer",
    "observability": "Observability",
    # 3 additional dimensions
    "compliance": "Compliance",
    "accessibility": "Accessibility",
    "system_comprehensibility": "System Comprehensibility",
}


# ---------------------------------------------------------------------------
# IO boundary: load agent results from directory
# ---------------------------------------------------------------------------


def load_agent_results(results_dir: str) -> tuple[dict[str, Any], list[str]]:
    """Scan a directory for known agent JSON files, validate each with Pydantic.

    Returns a tuple of:
    - dict mapping agent_key to validated Pydantic model instances
    - list of error/missing messages (empty if all agents loaded successfully)

    Never raises -- all errors are captured as messages in the second element.
    """
    results: dict[str, Any] = {}
    messages: list[str] = []
    directory = Path(results_dir)

    for agent_key, filename in AGENT_FILE_MAP.items():
        filepath = directory / filename
        if not filepath.exists():
            messages.append(
                f"{agent_key}: file not found ({filename})"
            )
            continue

        try:
            raw_text = filepath.read_text(encoding="utf-8")
            raw_data = json.loads(raw_text)
        except (json.JSONDecodeError, OSError) as error:
            messages.append(
                f"{agent_key}: failed to read {filename} -- {error}"
            )
            continue

        model_class = AGENT_MODEL_MAP[agent_key]
        try:
            validated_model = model_class.model_validate(raw_data)
            results[agent_key] = validated_model
        except ValidationError as error:
            messages.append(
                f"{agent_key}: validation failed -- {error}"
            )

    return results, messages


# ---------------------------------------------------------------------------
# Pure function: translate dimension names for risk module compatibility
# ---------------------------------------------------------------------------


def _translate_dimension_names(
    dimensions: list[DimensionScore],
) -> list[DimensionScore]:
    """Translate snake_case dimension names to display names.

    The normalize module produces names like 'code_quality', but the risk
    module expects display names like 'Code Quality'. This function bridges
    that gap by creating new DimensionScore instances with display names.
    """
    translated: list[DimensionScore] = []
    for dimension in dimensions:
        display_name = _DIMENSION_DISPLAY_NAMES.get(dimension.name, dimension.name)
        translated.append(
            DimensionScore(
                name=display_name,
                raw_score=dimension.raw_score,
                normalized_score=dimension.normalized_score,
                weight=dimension.weight,
                formula_display=dimension.formula_display,
                explanation=dimension.explanation,
            )
        )
    return translated


# ---------------------------------------------------------------------------
# Pure function: assemble ReportData from validated agent results
# ---------------------------------------------------------------------------


def _serialize_agent_results(results: dict[str, Any]) -> dict[str, Any]:
    """Convert validated Pydantic models to plain dicts for ReportData storage."""
    return {
        agent_key: model.model_dump() if hasattr(model, "model_dump") else model
        for agent_key, model in results.items()
    }


def build_report_data(
    results: dict[str, Any],
    project_name: str,
    target_dir: str,
) -> ReportData:
    """Assemble a complete ReportData from validated agent results.

    Pure function: takes validated agent results dict and produces a fully
    populated ReportData ready for rendering. Calls normalization, risk
    assessment, and score computation functions.
    """
    dimensions = normalize_all(results)
    display_dimensions = _translate_dimension_names(dimensions)
    overall_score = compute_overall_score(display_dimensions)
    rating = derive_rating(overall_score)
    risk_assessments = assess_all_risks(display_dimensions)
    metadata = ProjectMetadata(
        project_name=project_name,
        target_directory=target_dir,
        analysis_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    )
    agent_results_serialized = _serialize_agent_results(results)
    agent_results_sanitized = sanitize_agent_results(agent_results_serialized)

    # Use snake_case dimensions for ReportData (template expects snake_case keys)
    # Display names are only needed for risk assessment (already computed above)
    return ReportData(
        metadata=metadata,
        dimensions=dimensions,
        overall_score=overall_score,
        rating=rating,
        risk_assessments=risk_assessments,
        agent_results=agent_results_sanitized,
    )


# ---------------------------------------------------------------------------
# IO boundary: top-level pipeline orchestrator
# ---------------------------------------------------------------------------


def _print_report_summary(
    output_path: str,
    report_data: ReportData,
    results: dict[str, Any],
    messages: list[str],
) -> None:
    """Print a human-readable summary of the generated report to stdout."""
    available_agents = sorted(results.keys())
    missing_agents = sorted(
        key for key in AGENT_FILE_MAP if key not in results
    )

    print(f"Report generated: {output_path}")
    print(f"  Overall score: {report_data.overall_score:.1f}/100 ({report_data.rating})")
    print(f"  Available agents ({len(available_agents)}): {', '.join(available_agents)}")
    if missing_agents:
        print(f"  Missing agents ({len(missing_agents)}): {', '.join(missing_agents)}")
    if messages:
        for message in messages:
            print(f"  Note: {message}")


def generate_report(
    results_dir: str,
    output_path: str,
    project_name: str = "Codebase Analysis",
) -> int:
    """Generate an HTML report from agent JSON files in a directory.

    Top-level orchestrator that chains all pipeline steps:
    1. Load and validate agent JSON files
    2. Build report data (normalization, risk assessment, scoring)
    3. Render HTML from report data
    4. Write HTML to output file

    Returns 0 on success, 1 on fatal error (no agent results at all).
    Partial results (some agents missing) produce a valid report with
    available data and return 0.
    """
    results, messages = load_agent_results(results_dir)

    if not results:
        print(f"Fatal: no agent results found in {results_dir}")
        for message in messages:
            print(f"  - {message}")
        return 1

    report_data = build_report_data(results, project_name, results_dir)
    html = render_report(report_data)
    write_report(html, output_path)
    _print_report_summary(output_path, report_data, results, messages)

    return 0
