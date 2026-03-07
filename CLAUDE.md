# Codebase Analyzer -- Project Instructions

## Project Overview

Claude Code orchestrator agent that launches 6 analysis subagents against a target codebase, normalizes scores, and generates a self-contained HTML report with interactive visualizations.

## Development Paradigm

**Functional-first Python** (ADR-005):
- Pure functions for all computation -- no side effects in the pipeline core
- Frozen dataclasses and Pydantic models for all data structures -- immutable data throughout
- Protocols for type boundaries -- no ABC inheritance hierarchies
- Composition pipelines -- explicit function chaining, not method chains
- Effect boundaries at edges only -- file I/O isolated at pipeline entry/exit

## Architecture

See `docs/feature/codebase-analyzer/design/architecture.md` for full architecture document.
See `docs/feature/codebase-analyzer/design/adrs/` for architectural decision records.
See `docs/feature/codebase-analyzer/design/roadmap.md` for implementation roadmap.

## Key Conventions

- Python 3.11+
- Package management: uv
- Data validation: Pydantic v2
- Templating: Jinja2
- No CSS frameworks in the report -- custom CSS only
- All report JS libraries (Chart.js, D3.js, Mermaid.js) are inlined -- no CDN dependencies

## Testing

- Unit tests for pure functions (normalize, risk, formulas, charts)
- Integration tests for the pipeline (JSON files -> HTML output)
- Pydantic models validate agent JSON contracts at boundary

## Project Structure

```
codebase-analyzer.md    # Orchestrator agent definition
src/report/             # Python pipeline modules
src/templates/          # Jinja2 HTML templates
src/assets/             # Minified JS libraries for inlining
tests/                  # Unit and integration tests
docs/                   # Architecture, ADRs, feature docs
```
