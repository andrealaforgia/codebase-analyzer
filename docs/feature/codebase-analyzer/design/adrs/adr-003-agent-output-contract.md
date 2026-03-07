# ADR-003: Agent Output Contract -- Structured JSON Files

## Status
Accepted

## Context

Analysis agents currently output markdown reports. The report generator needs structured, machine-parseable data to produce charts, calculate scores, and render derivation panels. The data extraction approach must be reliable across diverse agent outputs and resistant to format drift.

## Decision

**Modify each agent** to write a structured JSON file (`{agent-name}-data.json`) alongside its existing markdown report. Each agent's JSON schema is defined as an explicit contract. Agent modifications are made at the source in `/Users/andrealaforgia/dev/claude-code-agents/`.

JSON files are validated against Pydantic models before consumption by the normalizer. Schema violations produce clear error messages identifying the agent and missing/malformed field.

## Alternatives Considered

### Alternative 1: Parse markdown reports with regex/heuristics
- **What**: Extract structured data from existing markdown reports using pattern matching
- **Expected impact**: No agent modifications needed
- **Why rejected**: Fragile. Agents evolve their markdown format independently. A heading change or table restructure silently breaks extraction. Debugging invisible parsing failures during a client engagement is unacceptable.

### Alternative 2: Normalization agent (LLM reads markdown, extracts data)
- **What**: A 7th agent reads all markdown reports and produces unified JSON
- **Expected impact**: Handles arbitrary format changes
- **Why rejected**: Non-deterministic extraction. Same markdown could yield different JSON on different runs. Adds latency (another LLM invocation). Violates reproducibility requirement.

### Alternative 3: Embedded JSON in markdown (delimited blocks)
- **What**: Agents embed JSON within `<!-- JSON_DATA_START -->` markers in their markdown
- **Expected impact**: Single file output per agent, easy to extract
- **Why rejected**: Mixes concerns. Markdown becomes a transport format. Agents may inadvertently break delimiters. Separate files are cleaner and independently validatable.

## Consequences

- **Positive**: Reliable, deterministic data extraction. Schema-validated before use.
- **Positive**: Agents continue producing their existing markdown reports unchanged.
- **Positive**: Contract schemas serve as documentation and integration tests.
- **Negative**: Requires modifying 6 agent definition files. This is work outside the codebase-analyzer repo.
- **Negative**: Agent and contract schema must stay in sync. Mitigated by Pydantic validation catching drift immediately.
