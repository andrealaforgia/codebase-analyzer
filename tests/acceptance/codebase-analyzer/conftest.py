"""Acceptance test configuration for codebase-analyzer.

Provides shared fixtures for all acceptance test features:
- Agent data loading from fixture files
- Pipeline invocation through driving ports
- Report parsing and assertion helpers

Integration approach: real internal services, mocked external agents.
Agents are expensive Claude Code subagents -- we use fixture JSON files
that represent realistic agent outputs instead.
"""

import json
from pathlib import Path

import pytest


# --- Fixture Paths ---

FIXTURES_DIR = Path(__file__).parent / "fixtures"
FEATURES_DIR = Path(__file__).parent / "features"


@pytest.fixture
def fixtures_dir() -> Path:
    """Path to the fixture data directory."""
    return FIXTURES_DIR


@pytest.fixture
def healthy_fixtures_dir() -> Path:
    """Path to the healthy codebase fixture data directory."""
    return FIXTURES_DIR / "healthy"


# --- Agent Data Loading ---

@pytest.fixture
def load_agent_data():
    """Factory fixture: load a specific agent's fixture data as a dict.

    Usage:
        data = load_agent_data("code-smell-detector")
    """
    def _load(agent_name: str, fixture_set: str = "default") -> dict:
        if fixture_set == "default":
            path = FIXTURES_DIR / f"{agent_name}-data.json"
        else:
            path = FIXTURES_DIR / fixture_set / f"{agent_name}-data.json"

        with open(path) as f:
            return json.load(f)

    return _load


@pytest.fixture
def all_agent_data(load_agent_data) -> dict[str, dict]:
    """Load all 6 agent fixture data files into a dict keyed by agent name."""
    agents = [
        "code-smell-detector",
        "test-design-reviewer",
        "cognitive-load-analyzer",
        "ddd-architect",
        "legacy-code-expert",
        "refactoring-expert",
    ]
    return {name: load_agent_data(name) for name in agents}


@pytest.fixture
def acme_corp_dimension_scores() -> dict[str, float]:
    """The Acme Corp Platform dimension scores used across walking skeletons.

    These are the canonical test values. Changing them requires updating
    all scenarios that reference Acme Corp scores.
    """
    return {
        "Code Quality": 6.0,
        "Test Design": 7.2,
        "Cognitive Load": 6.9,
        "DDD Compliance": 6.5,
        "Legacy Safety": 5.5,
        "Refactoring Debt": 3.0,
    }


@pytest.fixture
def healthy_dimension_scores() -> dict[str, float]:
    """Dimension scores for a healthy codebase (all above 7.0)."""
    return {
        "Code Quality": 8.5,
        "Test Design": 8.2,
        "Cognitive Load": 8.0,
        "DDD Compliance": 7.5,
        "Legacy Safety": 7.8,
        "Refactoring Debt": 8.0,
    }


# --- Temporary Output Directory ---

@pytest.fixture
def output_dir(tmp_path) -> Path:
    """Temporary directory for report output files."""
    return tmp_path


@pytest.fixture
def output_path(output_dir) -> Path:
    """Default output path for a generated report."""
    return output_dir / "acme-corp-platform-report.html"


# --- Agent Data Directory Setup ---

@pytest.fixture
def agent_data_dir(tmp_path, all_agent_data) -> Path:
    """Temporary directory populated with all 6 agent data files.

    Simulates the output directory after orchestrator has run all agents.
    """
    data_dir = tmp_path / "agent-output"
    data_dir.mkdir()
    for agent_name, data in all_agent_data.items():
        filepath = data_dir / f"{agent_name}-data.json"
        filepath.write_text(json.dumps(data, indent=2))
    return data_dir


@pytest.fixture
def partial_agent_data_dir(tmp_path, load_agent_data) -> Path:
    """Temporary directory with only 4 of 6 agent data files.

    Missing: ddd-architect, legacy-code-expert.
    """
    data_dir = tmp_path / "agent-output-partial"
    data_dir.mkdir()
    available_agents = [
        "code-smell-detector",
        "test-design-reviewer",
        "cognitive-load-analyzer",
        "refactoring-expert",
    ]
    for agent_name in available_agents:
        data = load_agent_data(agent_name)
        filepath = data_dir / f"{agent_name}-data.json"
        filepath.write_text(json.dumps(data, indent=2))
    return data_dir


@pytest.fixture
def empty_agent_data_dir(tmp_path) -> Path:
    """Temporary directory with no agent data files."""
    data_dir = tmp_path / "agent-output-empty"
    data_dir.mkdir()
    return data_dir
