# ADR-005: Development Paradigm -- Functional-First Python

## Status
Accepted

## Context

The codebase analyzer's Python components (normalizer, risk engine, report generator) need a clear design approach. The data flow is inherently a pipeline: raw agent JSON -> normalize -> derive risks -> assemble data -> render templates -> write HTML. The tool is maintained by one developer.

## Decision

**Functional-first** Python with:
- **Pure functions** for all computation (normalization, risk derivation, formula rendering, chart config building). No side effects in the pipeline core.
- **Frozen dataclasses and Pydantic models** for all data structures. Immutable data flowing through the pipeline.
- **Protocols** for type boundaries (port definitions). No ABC inheritance hierarchies.
- **Composition pipelines** -- functions composed via explicit chaining, not class method chains.
- **Effect boundaries** at the edges only: file I/O (reading JSON, writing HTML) is isolated at the pipeline entry and exit points.

## Alternatives Considered

### Alternative 1: OOP with ports-and-adapters (ABC-based)
- **What**: Abstract base classes for ports, concrete adapter classes, service classes for business logic
- **Expected impact**: Familiar pattern, IDE support for abstract method enforcement
- **Why rejected**: The data flow is a pipeline, not a network of collaborating objects. Classes would be thin wrappers around single functions. ABC hierarchies add ceremony without value when Protocol covers the type boundary need. One developer does not benefit from the guardrails that ABCs provide in team settings.

### Alternative 2: Mixed OOP/FP
- **What**: Classes for complex components (ReportGenerator), functions for simple transforms
- **Expected impact**: Pragmatic, use the right tool per component
- **Why rejected**: Inconsistency increases cognitive load. The pipeline is simple enough to be purely functional throughout. Mixing paradigms creates "which style is this module?" questions during maintenance.

## Consequences

- **Positive**: Pipeline reads top-to-bottom as a data transformation chain. Easy to reason about.
- **Positive**: Pure functions are trivially testable -- input data in, output data out, no setup/teardown.
- **Positive**: Immutable data structures prevent accidental mutation bugs in the normalization/rendering pipeline.
- **Positive**: Protocols provide structural typing without inheritance ceremony.
- **Negative**: Some Python developers find functional style less idiomatic. Mitigated by single-developer context.
- **Negative**: Protocols lack runtime enforcement (unlike ABC). Mitigated by Pydantic validation at boundaries.
