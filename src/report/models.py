"""Pydantic models for agent JSON output contracts and unified report data.

Each of the 21 analysis agents produces a JSON report conforming to one of
these frozen models.  Validation enforces required fields, types, and value
ranges so that invalid agent output is rejected with clear error messages
identifying the offending field.

The original 6 agents have specific models.  The 15 additional agents share a
common GenericAgentData model (overall_score 0-100, risk_distribution,
recommendations).

Report-level models (ProjectMetadata, DimensionScore, RiskCategory, ReportData)
define the unified data shape the report generator receives.  Pure functions
compute_overall_score and derive_rating transform dimension scores into a
health score and human-readable rating.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Shared sub-models
# ---------------------------------------------------------------------------


class SeverityDistribution(BaseModel):
    """Counts of issues by severity level."""

    model_config = ConfigDict(frozen=True)

    high: int = Field(ge=0)
    medium: int = Field(ge=0)
    low: int = Field(ge=0)


class RiskDistribution(BaseModel):
    """Counts of items by risk level."""

    model_config = ConfigDict(frozen=True)

    low: int = Field(ge=0)
    medium: int = Field(ge=0)
    high: int = Field(ge=0)


# ---------------------------------------------------------------------------
# 1. CodeSmellDetectorData
# ---------------------------------------------------------------------------


class CodeSmellTopIssue(BaseModel):
    model_config = ConfigDict(frozen=True)

    file: str
    issue: str
    severity: str
    category: str


class SolidCompliance(BaseModel):
    """SOLID principle compliance scores (0-10 scale)."""

    model_config = ConfigDict(frozen=True)

    SRP: float = Field(ge=0, le=10)
    OCP: float = Field(ge=0, le=10)
    LSP: float = Field(ge=0, le=10)
    ISP: float = Field(ge=0, le=10)
    DIP: float = Field(ge=0, le=10)


class CodeSmellDetectorData(BaseModel):
    """Contract for the Code Smell Detector agent output."""

    model_config = ConfigDict(frozen=True)

    grade: Literal["A", "B", "C", "D", "F"]
    total_issues: int = Field(ge=0)
    severity_distribution: SeverityDistribution
    category_distribution: dict[str, int]
    solid_compliance: SolidCompliance
    top_issues: list[CodeSmellTopIssue]


# ---------------------------------------------------------------------------
# 2. TestDesignReviewerData
# ---------------------------------------------------------------------------


class PropertyScores(BaseModel):
    """Static, LLM, and blended scores for a test design property."""

    model_config = ConfigDict(frozen=True)

    static: float
    llm: float
    blended: float


class TautologyCounts(BaseModel):
    """Counts of tautological test patterns detected."""

    model_config = ConfigDict(frozen=True)

    mock_tautology: int = Field(ge=0)
    mock_only: int = Field(ge=0)
    trivial: int = Field(ge=0)
    framework: int = Field(ge=0)


class TestDesignWorstOffender(BaseModel):
    model_config = ConfigDict(frozen=True)

    file: str
    score: float
    issues: list[str]


class TestDesignReviewerData(BaseModel):
    """Contract for the Test Design Reviewer agent output."""

    model_config = ConfigDict(frozen=True)

    farley_index: float = Field(ge=0, le=10)
    rating: str
    properties: dict[str, PropertyScores]
    tautology_counts: TautologyCounts
    worst_offenders: list[TestDesignWorstOffender]


# ---------------------------------------------------------------------------
# 3. CognitiveLoadAnalyzerData
# ---------------------------------------------------------------------------


class CognitiveDimension(BaseModel):
    """A single cognitive load dimension measurement."""

    model_config = ConfigDict(frozen=True)

    raw: str
    normalized: float
    weighted: float


class CognitiveWorstOffender(BaseModel):
    model_config = ConfigDict(frozen=True)

    file: str
    score: float
    primary_dimension: str


class CognitiveLoadAnalyzerData(BaseModel):
    """Contract for the Cognitive Load Analyzer agent output."""

    model_config = ConfigDict(frozen=True)

    cli_score: int = Field(ge=0, le=1000)
    rating: str
    dimensions: dict[str, CognitiveDimension]
    interaction_penalty: float
    worst_offenders: list[CognitiveWorstOffender]


# ---------------------------------------------------------------------------
# 4. DDDArchitectData
# ---------------------------------------------------------------------------


class SubdomainDistribution(BaseModel):
    """Counts of bounded contexts per subdomain type."""

    model_config = ConfigDict(frozen=True)

    core: int = Field(ge=0)
    supporting: int = Field(ge=0)
    generic: int = Field(ge=0)


class DDDAntiPattern(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    severity: str
    location: str


class PatternMaturity(BaseModel):
    """DDD pattern maturity scores (0-10 scale)."""

    model_config = ConfigDict(frozen=True)

    strategic: float = Field(ge=0, le=10)
    tactical: float = Field(ge=0, le=10)
    language: float = Field(ge=0, le=10)
    boundaries: float = Field(ge=0, le=10)
    events: float = Field(ge=0, le=10)


class DDDArchitectData(BaseModel):
    """Contract for the DDD Architect agent output."""

    model_config = ConfigDict(frozen=True)

    overall_score: float = Field(ge=0, le=10)
    bounded_context_count: int = Field(ge=0)
    subdomain_distribution: SubdomainDistribution
    anti_patterns: list[DDDAntiPattern]
    pattern_maturity: PatternMaturity
    context_map_mermaid: str


# ---------------------------------------------------------------------------
# 5. LegacyCodeExpertData
# ---------------------------------------------------------------------------


class SeamAvailability(BaseModel):
    """Counts of available seam types for legacy code modification."""

    model_config = ConfigDict(frozen=True)

    object: int = Field(ge=0)
    link: int = Field(ge=0)
    preprocessing: int = Field(ge=0)


class ModuleAtRisk(BaseModel):
    model_config = ConfigDict(frozen=True)

    file: str
    risk: str
    dependencies: int = Field(ge=0)
    seams: int = Field(ge=0)


class LegacyCodeExpertData(BaseModel):
    """Contract for the Legacy Code Expert agent output."""

    model_config = ConfigDict(frozen=True)

    overall_score: float = Field(ge=0, le=10)
    risk_level: Literal["Low", "Medium", "High", "Critical"]
    dependency_count: int = Field(ge=0)
    testability_score: float = Field(ge=0, le=1)
    seam_availability: SeamAvailability
    modules_at_risk: list[ModuleAtRisk]


# ---------------------------------------------------------------------------
# 6. RefactoringExpertData
# ---------------------------------------------------------------------------


class PriorityMatrixItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    item: str
    impact: str
    complexity: str
    risk: str


class ImplementationSequenceItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    order: int = Field(ge=1)
    item: str
    rationale: str


class RefactoringExpertData(BaseModel):
    """Contract for the Refactoring Expert agent output."""

    model_config = ConfigDict(frozen=True)

    total_recommendations: int = Field(ge=0)
    priority_matrix: list[PriorityMatrixItem]
    risk_distribution: RiskDistribution
    category_distribution: dict[str, int]
    implementation_sequence: list[ImplementationSequenceItem]


# ---------------------------------------------------------------------------
# 7-18. GenericAgentData (shared by 12 new agents)
# ---------------------------------------------------------------------------


class GenericRiskDistribution(BaseModel):
    """Counts of issues by severity for the new agent types."""

    model_config = ConfigDict(frozen=True)

    critical: int = Field(ge=0, default=0)
    high: int = Field(ge=0, default=0)
    medium: int = Field(ge=0, default=0)
    low: int = Field(ge=0, default=0)


class GenericRecommendation(BaseModel):
    model_config = ConfigDict(frozen=True)

    priority: int = Field(ge=1)
    title: str
    description: str
    effort: str = "medium"


class GenericAgentData(BaseModel):
    """Common contract for the 15 generic analysis agents.

    All generic agents report an overall_score (0-100), a risk_distribution
    with critical/high/medium/low counts, and a list of recommendations.
    Additional agent-specific fields are captured by the extra='allow' config
    and stored in agent_results for the HTML drill-down.
    """

    model_config = ConfigDict(frozen=True, extra="allow")

    overall_score: float = Field(ge=0, le=100)
    summary: str = ""
    risk_distribution: GenericRiskDistribution = GenericRiskDistribution()
    recommendations: list[GenericRecommendation] = []


# ---------------------------------------------------------------------------
# Report-level models
# ---------------------------------------------------------------------------


class ProjectMetadata(BaseModel):
    """Metadata about the analyzed project."""

    model_config = ConfigDict(frozen=True)

    project_name: str
    target_directory: str
    analysis_date: str
    total_files: int | None = None
    total_loc: int | None = None
    primary_language: str | None = None


class DimensionScore(BaseModel):
    """A single analysis dimension's score, normalized to the 0-10 scale.

    Each dimension carries its own weight for the overall health formula.
    formula_display shows the formula with substituted values.
    explanation provides a plain-language description of what the score means.
    """

    model_config = ConfigDict(frozen=True)

    name: str
    raw_score: float
    normalized_score: float = Field(ge=0, le=10)
    weight: float = Field(ge=0, le=1)
    formula_display: str
    explanation: str


class RiskCategory(BaseModel):
    """A business risk assessment derived from dimension scores."""

    model_config = ConfigDict(frozen=True)

    name: str
    severity: Literal["HIGH", "MODERATE", "LOW"]
    contributing_dimensions: list[str]
    description: str


class ReportData(BaseModel):
    """Unified report data structure passed to the report generator.

    Contains metadata, 0-21 dimension scores (some may be missing),
    an overall health score (0-100), a human-readable rating, business risk
    assessments, and raw agent results for detailed drill-down.
    """

    model_config = ConfigDict(frozen=True)

    metadata: ProjectMetadata
    dimensions: list[DimensionScore]
    overall_score: float = Field(ge=0, le=100)
    rating: Literal["Critical", "Needs Attention", "Good", "Excellent"]
    risk_assessments: list[RiskCategory]
    agent_results: dict[str, Any]


# ---------------------------------------------------------------------------
# Pure functions: overall score and rating derivation
# ---------------------------------------------------------------------------


def compute_overall_score(dimensions: list[DimensionScore]) -> float:
    """Compute weighted-average health score scaled to 0-100.

    Formula (all 6 dimensions present):
        health = (code_quality * 0.20 + test_design * 0.20 +
                  cognitive_load * 0.20 + ddd_compliance * 0.15 +
                  legacy_safety * 0.15 + refactoring_debt * 0.10) * 10

    When dimensions are missing, their weights are redistributed
    proportionally among the available dimensions so the score remains
    on the 0-100 scale.
    """
    if not dimensions:
        return 0.0

    total_weight = sum(dimension.weight for dimension in dimensions)
    if total_weight == 0.0:
        return 0.0

    weighted_sum = sum(
        dimension.normalized_score * (dimension.weight / total_weight)
        for dimension in dimensions
    )
    return weighted_sum * 10.0


def derive_rating(overall_score: float) -> str:
    """Derive a human-readable rating from the overall health score.

    Thresholds:
        0-40   -> Critical
        41-60  -> Needs Attention
        61-80  -> Good
        81-100 -> Excellent
    """
    if overall_score <= 40.0:
        return "Critical"
    if overall_score <= 60.0:
        return "Needs Attention"
    if overall_score <= 80.0:
        return "Good"
    return "Excellent"
