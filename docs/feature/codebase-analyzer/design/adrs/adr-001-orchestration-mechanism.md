# ADR-001: Orchestration Mechanism -- Claude Code Agent with Subagents

## Status
Accepted

## Context

The codebase analyzer must orchestrate 6 specialized analysis agents against a target codebase. The orchestrator needs to:
- Launch agents with target directory context
- Manage a dependency graph (refactoring depends on smell detection)
- Handle agent failures gracefully
- Collect structured results for report generation

Three approaches were evaluated based on the user's environment (Claude Code available, macOS, single developer).

## Decision

Use a **Claude Code Agent** as the orchestrator, launching subagents via the Agent/Task tool. The orchestrator is defined as a `.md` agent file. Report generation is delegated to Python scripts invoked via the Bash tool.

## Alternatives Considered

### Alternative 1: Standalone Python CLI with subprocess
- **What**: Python CLI (`click`/`typer`) that invokes `claude` CLI commands via subprocess
- **Expected impact**: Full automation, scriptable, CI/CD-friendly
- **Why rejected**: User explicitly requested Claude Code agent invocation. Subprocess approach adds shell escaping complexity, process management overhead, and requires the `claude` CLI binary to be separately available. The Agent tool provides native subagent management.

### Alternative 2: Hybrid -- Claude Code agent for orchestration, separate Python CLI for report
- **What**: Agent orchestrates analysis, writes JSON, then user separately runs `python generate_report.py`
- **Expected impact**: Clean separation but two-step workflow
- **Why rejected**: Violates the single-invocation requirement (US-01). User wants one interaction to produce the report. The orchestrator agent can invoke Python via Bash tool in a single flow.

## Consequences

- **Positive**: Native Claude Code integration; Agent tool handles subagent lifecycle; single invocation from Andrea's perspective; agents can communicate context naturally
- **Positive**: Report generation via Bash/Python gives deterministic computation (no LLM arithmetic for scores)
- **Negative**: Tool is not standalone -- requires Claude Code to be running
- **Negative**: Not directly CI/CD-scriptable (would need wrapper)
- **Negative**: Agent tool parallelization depends on Claude Code's concurrent subagent support
