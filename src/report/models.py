"""Pydantic models for agent JSON output contracts.

Each of the 6 analysis agents produces a JSON report conforming to one of these
frozen models.  Validation enforces required fields, types, and value ranges so
that invalid agent output is rejected with clear error messages identifying the
offending field.
"""

from __future__ import annotations

from typing import Literal

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
