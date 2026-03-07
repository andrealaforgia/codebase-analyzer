"""Content-validation tests for the orchestrator agent markdown definition.

These tests verify that codebase-analyzer.md exists and contains all required
sections for the orchestrator to function correctly:
- Target directory parameter acceptance
- All 6 subagent references
- Parallel execution instructions for independent agents
- Sequential dependency (refactoring waits for code-smell-detector)
- Python pipeline invocation
- Failure handling instructions
- Results directory and JSON output file references
"""

from pathlib import Path

import pytest

AGENT_DEFINITION_PATH = Path(__file__).parent.parent.parent / "codebase-analyzer.md"


@pytest.fixture
def agent_content() -> str:
    """Load the orchestrator agent markdown file content."""
    assert AGENT_DEFINITION_PATH.exists(), (
        f"Agent definition file not found at {AGENT_DEFINITION_PATH}"
    )
    return AGENT_DEFINITION_PATH.read_text(encoding="utf-8")


class TestOrchestratorAgentDefinitionExists:
    def test_agent_markdown_file_exists(self):
        assert AGENT_DEFINITION_PATH.exists(), (
            "codebase-analyzer.md must exist at project root"
        )

    def test_agent_file_is_not_empty(self, agent_content: str):
        assert len(agent_content.strip()) > 0, (
            "codebase-analyzer.md must not be empty"
        )


class TestTargetDirectoryParameter:
    def test_accepts_target_directory_parameter(self, agent_content: str):
        assert "target" in agent_content.lower() and "directory" in agent_content.lower(), (
            "Agent must document accepting a target directory parameter"
        )

    def test_validates_target_directory(self, agent_content: str):
        assert "valid" in agent_content.lower() and "directory" in agent_content.lower(), (
            "Agent must validate the target directory exists"
        )


class TestOptionalConfiguration:
    def test_accepts_project_name_config(self, agent_content: str):
        assert "project_name" in agent_content or "project name" in agent_content.lower(), (
            "Agent must accept optional project name configuration"
        )

    def test_accepts_output_path_config(self, agent_content: str):
        assert "output_path" in agent_content or "output path" in agent_content.lower(), (
            "Agent must accept optional output path configuration"
        )


class TestSubagentReferences:
    """Verify all 6 subagent types are referenced in the agent definition."""

    EXPECTED_AGENT_TYPES = [
        "alf-code-smell-detector",
        "test-design-reviewer",
        "cognitive-load-analyzer",
        "alf-ddd-architect",
        "alf-legacy-code-expert",
        "alf-refactoring-expert",
    ]

    @pytest.mark.parametrize("agent_type", EXPECTED_AGENT_TYPES)
    def test_subagent_type_is_referenced(self, agent_content: str, agent_type: str):
        assert agent_type in agent_content, (
            f"Agent definition must reference subagent type '{agent_type}'"
        )

    EXPECTED_AGENT_PATHS = [
        "code-smell-detector/code-smell-detector.md",
        "test-design-reviewer/test-design-reviewer.md",
        "cognitive-load-analyzer/cognitive-load-analyzer.md",
        "domain-driven-design/ddd-architect-agent.md",
        "legacy-code-expert/legacy-code-expert.md",
        "refactoring-expert/refactoring-expert.md",
    ]

    @pytest.mark.parametrize("agent_path", EXPECTED_AGENT_PATHS)
    def test_subagent_definition_path_is_referenced(self, agent_content: str, agent_path: str):
        assert agent_path in agent_content, (
            f"Agent definition must reference subagent path '{agent_path}'"
        )

    EXPECTED_JSON_FILES = [
        "code-smell-detector-data.json",
        "test-design-reviewer-data.json",
        "cognitive-load-analyzer-data.json",
        "ddd-architect-data.json",
        "legacy-code-expert-data.json",
        "refactoring-expert-data.json",
    ]

    @pytest.mark.parametrize("json_file", EXPECTED_JSON_FILES)
    def test_json_output_file_is_referenced(self, agent_content: str, json_file: str):
        assert json_file in agent_content, (
            f"Agent definition must reference expected JSON output '{json_file}'"
        )


class TestParallelExecution:
    def test_parallel_execution_is_documented(self, agent_content: str):
        assert "parallel" in agent_content.lower(), (
            "Agent must document parallel execution of independent agents"
        )

    def test_five_agents_run_in_parallel(self, agent_content: str):
        content_lower = agent_content.lower()
        assert ("5" in agent_content or "five" in content_lower) and "parallel" in content_lower, (
            "Agent must specify that 5 agents run in parallel"
        )


class TestSequentialDependency:
    def test_refactoring_waits_for_code_smell_detector(self, agent_content: str):
        content_lower = agent_content.lower()
        has_dependency = (
            ("refactoring" in content_lower and "smell" in content_lower)
            or ("refactoring" in content_lower and "wait" in content_lower)
            or ("sequential" in content_lower and "refactoring" in content_lower)
        )
        assert has_dependency, (
            "Agent must document that refactoring agent waits for code-smell-detector"
        )

    def test_refactoring_receives_smell_report(self, agent_content: str):
        content_lower = agent_content.lower()
        assert "refactoring" in content_lower and "smell" in content_lower, (
            "Agent must explain refactoring agent receives code smell report as input"
        )


class TestFailureHandling:
    def test_failure_handling_is_documented(self, agent_content: str):
        content_lower = agent_content.lower()
        has_failure_docs = "fail" in content_lower or "error" in content_lower
        assert has_failure_docs, (
            "Agent must document failure handling behavior"
        )

    def test_remaining_agents_continue_on_failure(self, agent_content: str):
        content_lower = agent_content.lower()
        has_continue_docs = "continue" in content_lower or "remaining" in content_lower
        assert has_continue_docs, (
            "Agent must document that remaining agents continue when one fails"
        )


class TestPythonPipelineInvocation:
    def test_pipeline_invocation_is_documented(self, agent_content: str):
        assert "generate_report" in agent_content, (
            "Agent must reference the generate_report Python function"
        )

    def test_pipeline_uses_uv_run(self, agent_content: str):
        assert "uv run" in agent_content, (
            "Agent must invoke the Python pipeline via 'uv run'"
        )

    def test_pipeline_references_correct_module(self, agent_content: str):
        assert "src.report.pipeline" in agent_content, (
            "Agent must reference the src.report.pipeline module"
        )

    def test_pipeline_invoked_after_all_agents(self, agent_content: str):
        content_lower = agent_content.lower()
        has_ordering = (
            ("after" in content_lower and "agent" in content_lower)
            or ("complete" in content_lower and "pipeline" in content_lower)
        )
        assert has_ordering, (
            "Agent must specify that the pipeline runs after all agents complete"
        )
