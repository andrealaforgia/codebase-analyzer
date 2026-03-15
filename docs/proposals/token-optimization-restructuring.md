# Token Optimization Proposal: Codebase Analyzer Agent Restructuring

> **Status: IMPLEMENTED** (2026-03-15)
> All phases (A through D) implemented in a single pass.
> - Orchestrator updated: `alf-codebase-analyzer.md`
> - 6 new consolidated agents created in `~/.claude/agents/`
> - Refactoring advisor updated with ownership analysis + Haiku model
> - All 21 JSON output filenames preserved -- zero pipeline changes needed
> - API design reviewer added to observability-compliance group (was missing from original proposal)

## Executive Summary

The current architecture launches 21 independent Claude Code agents against a target codebase. Each agent independently discovers the project structure, tech stack, and reads source files -- producing massive file-read overlap. Conservative estimates put redundant token consumption at 60-70% of the total run cost.

This proposal restructures the system from 21 independent agents into a **3-phase architecture** that reduces agent count from 21 to 8, eliminates redundant exploration, and leverages model tiering. Estimated token savings: **55-70%** of the current run cost.

---

## 1. Analysis: Where Tokens Go Today

### 1.1 Token Consumption Breakdown (per agent)

Each of the 21 agents performs roughly these steps:

| Step | Est. Tokens (input) | Redundancy |
|------|---------------------|------------|
| Agent prompt loading | 2K-8K | None (unique per agent) |
| Project structure discovery (glob, ls) | 3K-8K | **21x redundant** |
| Tech stack detection (read manifests) | 2K-5K | **21x redundant** |
| Source file reading | 10K-50K | **~3-8x redundant** |
| Analysis reasoning | 5K-15K | None (unique per agent) |
| JSON output generation | 1K-3K | None (unique per agent) |
| **Total per agent** | **23K-89K** | |

With 21 agents, total input tokens: **~480K-1.9M per run**.

### 1.2 Overlap Map

I categorized every agent by what files they need to read:

| File Category | Agents That Read It | Overlap Factor |
|---------------|-------------------|----------------|
| Project root structure | All 21 | 21x |
| package.json / pyproject.toml / pom.xml | 18 of 21 | 18x |
| README, docs/ | 5 (docs, system-explorer, consistency, onboarding, devops) | 5x |
| CI/CD config files | 3 (devops, security, consistency) | 3x |
| Dockerfiles, infra config | 3 (devops, security, observability) | 3x |
| Source files (business logic) | 15+ agents | 5-8x per file |
| Test files | 4 (test-design, code-smell, cognitive-load, dead-code) | 4x |
| Git history | 2 (ownership, system-explorer) | 2x |
| Config/env files | 4 (security, observability, consistency, devops) | 4x |
| Import/dependency graph | 6 (dead-code, dependency, concurrency, legacy, DDD, cognitive) | 6x |

**Key insight**: The project structure + tech stack detection step (5K-13K tokens) is repeated 21 times for zero additional value. That alone wastes ~100K-260K input tokens per run.

### 1.3 Agent Analysis: Exploration Depth vs. Analytical Depth

| Category | Agents | Exploration Required | Analytical Complexity |
|----------|--------|---------------------|----------------------|
| Heavy explorers + deep analysis | code-smell, test-design, cognitive-load, DDD, legacy | Very high -- read many files deeply | High -- custom models, complex scoring |
| Heavy explorers + moderate analysis | security, concurrency, error-handling | High -- scan many files for patterns | Medium -- pattern matching + severity |
| Moderate explorers + light analysis | dead-code, consistency, documentation, observability | Medium -- scan structure + samples | Low-medium -- mostly counting/checking |
| Config readers only | dependency-auditor, devops-evaluator | Low -- read a few config files | Low -- parse manifests, check CI configs |
| Git readers only | ownership-analyzer | Low -- git log commands only | Medium -- statistical analysis |
| Derivative (depends on other agent) | refactoring-advisor | None extra -- reads code-smell output | Medium -- recommendation synthesis |
| Config + light source reading | api-design, data-layer, accessibility | Low-medium | Low-medium |
| Full exploration (already exists) | system-explorer | Very high | High (already does full walkthrough) |

---

## 2. Proposed Architecture: 3-Phase Execution

### Phase 0: Pre-Scan (New -- Orchestrator-executed)

The orchestrator itself (not a subagent) runs a deterministic pre-scan of the target codebase using Bash commands. This produces a **Codebase Context File** that all subsequent agents receive as input, eliminating redundant exploration.

**What the pre-scan collects** (all via Bash, no LLM reasoning needed):

```
1. File tree (find . -type f | head -500)
2. File extensions distribution (find . -type f | sed 's/.*\.//' | sort | uniq -c | sort -rn)
3. LOC by language (wc -l on source files, grouped by extension)
4. Package manifests content (cat package.json, pyproject.toml, etc.)
5. Lock file presence (ls *.lock, uv.lock, etc.)
6. CI/CD config listing (ls .github/workflows/, .gitlab-ci.yml, etc.)
7. Dockerfile presence and content
8. README first 100 lines
9. Directory structure (tree -L 3 -d)
10. Test directory structure and test framework detection
11. Git summary (git log --oneline -20, git shortlog -sn)
12. Top 20 largest source files by line count
13. Entry point detection (main.py, index.js, etc.)
14. Import graph summary (grep -r "^import\|^from.*import" --include="*.py" | head -200)
```

**Output**: `{results_dir}/codebase-context.json` (~5K-15K tokens)

**Token cost**: ~2K tokens for Bash commands. **Saves ~200K tokens** (vs. 21 agents each doing this independently).

### Phase 1: Deep Analysis Agents (4 agents, Sonnet/Opus, parallel)

These agents perform analysis that requires deep source code reading and complex reasoning. They receive the Codebase Context File as input, skipping all discovery steps.

| # | Agent | Current Agents Merged | Model | Rationale |
|---|-------|-----------------------|-------|-----------|
| 1 | **alf-code-quality-analyst** | code-smell-detector + cognitive-load-analyzer + consistency-checker | Sonnet | All three need to read the same source files deeply. Code smells, cognitive load, and consistency are aspects of the same "code quality" assessment. Produces 3 separate JSON files (preserving the report structure). |
| 2 | **alf-test-design-reviewer** | test-design-reviewer (unchanged) | Sonnet | Unique methodology (Farley Index, property-based scoring). Specific Pydantic model. Cannot merge without losing analytical depth. |
| 3 | **alf-architecture-analyst** | DDD-assessor + legacy-code-analyzer + system-explorer | Sonnet | All three analyze the same architectural concerns: module boundaries, coupling, dependency structure, comprehensibility. Produces 3 separate JSON files. |
| 4 | **alf-security-reliability-analyst** | security-assessor + error-handling-reviewer + concurrency-analyzer | Sonnet | All three scan source files for pattern-based vulnerabilities and defects. Security, error handling, and concurrency are complementary reliability concerns. Produces 3 separate JSON files. |

**Why these groupings work**:
- Each consolidated agent reads source files once and applies multiple analytical lenses
- Agents in the same group need the same files (high overlap)
- Agents in different groups need different files (low overlap)

### Phase 2: Lightweight Analysis Agents (3 agents, Haiku, parallel)

These agents don't need deep source code reading. They primarily analyze metadata, configuration files, and project structure -- data that's already in the Codebase Context File or available via a few targeted reads.

| # | Agent | Current Agents Merged | Model | Rationale |
|---|-------|-----------------------|-------|-----------|
| 5 | **alf-dependency-ops-auditor** | dependency-auditor + devops-evaluator | Haiku | Both primarily read config/manifest files. Dependency analysis and CI/CD evaluation share package manifest reading. |
| 6 | **alf-documentation-assessor** | documentation-reviewer + dead-code-detector | Haiku | Both analyze file-level metadata: does it exist, is it referenced, is it stale. Overlap in orphan file detection and doc-to-code gap analysis. |
| 7 | **alf-observability-compliance-assessor** | observability-assessor + system-auditor + accessibility-assessor + data-layer-reviewer | Haiku | All four are lightweight pattern scanners with generic output models. Each checks a specific concern against known patterns (logging patterns, compliance patterns, WCAG patterns, SQL patterns). |

### Phase 3: Derivative Agent (1 agent, Haiku, sequential)

| # | Agent | Current Agents Merged | Model | Rationale |
|---|-------|-----------------------|-------|-----------|
| 8 | **alf-refactoring-advisor** | refactoring-advisor + ownership-analyzer | Haiku | Refactoring advisor already depends on code-smell-detector output. Adding ownership analysis (git-based, no source reading) lets it correlate refactoring recommendations with ownership hotspots. Produces 2 separate JSON files. |

### Execution Flow

```
Phase 0: Pre-Scan (orchestrator, ~5 seconds)
    |
    v
[codebase-context.json written]
    |
    +---> Phase 1 (parallel, 4 Sonnet agents)
    |     [code-quality] [test-design] [architecture] [security-reliability]
    |
    +---> Phase 2 (parallel, 3 Haiku agents)
    |     [dependency-ops] [documentation] [observability-compliance]
    |
    v
Phase 1 + Phase 2 complete
    |
    v
Phase 3: [refactoring-advisor] (sequential, reads Phase 1 output)
    |
    v
Python pipeline (unchanged)
```

**Phase 1 and Phase 2 run in parallel** -- there's no dependency between them.

---

## 3. Token Savings Estimate

### Current Architecture (21 agents, all Sonnet)

| Component | Tokens per Run |
|-----------|---------------|
| Discovery/exploration (21 agents x ~10K each) | ~210K |
| Source file reading (21 agents, ~3-8x overlap) | ~400K-800K |
| Agent prompts (21 x ~4K avg) | ~84K |
| Reasoning + output (21 x ~10K avg) | ~210K |
| **Total estimate** | **~900K-1.3M** |

### Proposed Architecture (8 agents, mixed models)

| Component | Tokens per Run |
|-----------|---------------|
| Pre-scan (Bash, no LLM) | ~2K |
| Context file reading (8 agents x ~10K) | ~80K |
| Source file reading (4 Sonnet agents, no overlap within groups) | ~80K-150K |
| Config/metadata reading (3 Haiku agents) | ~20K-40K |
| Agent prompts (8 x ~6K avg, longer due to multi-concern) | ~48K |
| Reasoning + output (4 Sonnet x ~20K + 4 Haiku x ~8K) | ~112K |
| **Total estimate** | **~342K-432K** |

### Savings Summary

| Metric | Current | Proposed | Savings |
|--------|---------|----------|---------|
| Total agents | 21 | 8 | 62% fewer |
| Exploration tokens | ~210K | ~2K + ~80K = ~82K | **~60% saved** |
| File reading tokens | ~400-800K | ~100-190K | **~65-75% saved** |
| Sonnet tokens | ~900K-1.3M | ~260-310K | **~70-75% saved** |
| Haiku tokens (new) | 0 | ~80-120K | New cost, but ~5-10x cheaper per token |
| **Net token cost reduction** | | | **~55-70%** |

The Haiku token costs are approximately 10x cheaper than Sonnet, so the effective cost reduction is even higher than the raw token reduction suggests.

---

## 4. Detailed Agent Designs

### 4.1 Codebase Context File Schema

Written by the orchestrator's pre-scan (Phase 0). All Phase 1-3 agents receive this.

```json
{
  "project": {
    "name": "my-project",
    "root": "/absolute/path",
    "primary_language": "python",
    "languages": {"python": 15000, "javascript": 2000},
    "total_files": 47,
    "total_loc": 17000
  },
  "structure": {
    "tree": "... (tree -L 3 -d output)",
    "entry_points": ["src/main.py", "src/cli.py"],
    "test_dirs": ["tests/"],
    "test_framework": "pytest"
  },
  "dependencies": {
    "manifest_files": ["pyproject.toml"],
    "manifest_contents": {"pyproject.toml": "... (full content)"},
    "lock_file": "uv.lock",
    "lock_file_present": true
  },
  "devops": {
    "ci_configs": [".github/workflows/ci.yml"],
    "ci_config_contents": {".github/workflows/ci.yml": "..."},
    "dockerfiles": ["Dockerfile"],
    "dockerfile_contents": {"Dockerfile": "..."}
  },
  "git": {
    "recent_commits": "... (git log --oneline -20)",
    "contributors": "... (git shortlog -sn)",
    "branch": "main"
  },
  "files": {
    "largest_source_files": [
      {"path": "src/report/render.py", "lines": 280},
      {"path": "src/report/normalize.py", "lines": 270}
    ],
    "import_graph_sample": "... (first 200 import lines)"
  },
  "readme_excerpt": "... (first 100 lines of README)"
}
```

### 4.2 Consolidated Agent: alf-code-quality-analyst

**Merges**: code-smell-detector + cognitive-load-analyzer + consistency-checker

**Why these three**: All need to read source files line-by-line. Code smell detection examines function/class structure. Cognitive load measures nesting, naming, coupling -- the same structural analysis. Consistency checking requires scanning all files for convention patterns. By reading each file once and applying three analytical lenses, we eliminate ~2x redundant file reads.

**Output**: Three separate JSON files (preserving pipeline compatibility):
- `code-smell-detector-data.json` (CodeSmellDetectorData model)
- `cognitive-load-analyzer-data.json` (CognitiveLoadAnalyzerData model)
- `consistency-checker-data.json` (GenericAgentData model)

**Key concern -- analytical depth**: The current code-smell-detector is 754 lines with extremely detailed SOLID/GRASP frameworks. The cognitive-load-analyzer has a sophisticated 8-dimension model with sigmoid normalization. The combined agent would need to maintain both analytical frameworks.

**Mitigation**: Extract domain knowledge into Skills:
- Skill: `code-smell-rubric` (~300 lines) -- smell catalog, SOLID detection patterns
- Skill: `cli-dimensions-and-formulas` (already exists) -- cognitive load sigmoid parameters
- Skill: `consistency-patterns` (~100 lines) -- convention detection heuristics

The combined agent definition stays under 400 lines. Skills are loaded on demand.

### 4.3 Consolidated Agent: alf-architecture-analyst

**Merges**: DDD-assessor + legacy-code-analyzer + system-explorer

**Why these three**: All analyze the same macro-level concerns: module boundaries, dependency structure, coupling between components, and architectural clarity. DDD looks at bounded contexts; legacy-code looks at dependency graphs and testability seams; system-explorer maps architecture for comprehensibility. They read the same set of files: entry points, module boundaries, import graphs, and documentation.

**Output**: Three JSON files:
- `ddd-architect-data.json` (DDDArchitectData model)
- `legacy-code-expert-data.json` (LegacyCodeExpertData model)
- `system-explorer-data.json` (GenericAgentData model)

### 4.4 Consolidated Agent: alf-security-reliability-analyst

**Merges**: security-assessor + error-handling-reviewer + concurrency-analyzer

**Why these three**: All perform pattern-based scanning of source files for defect patterns. Security scans for injection, secrets, and OWASP patterns. Error handling scans for catch blocks, missing error paths, and resilience patterns. Concurrency scans for race conditions, missing locks, and async issues. All three look at the same code paths (request handlers, service boundaries, database calls) and classify findings by severity.

**Output**: Three JSON files:
- `security-assessor-data.json` (GenericAgentData model)
- `error-handling-reviewer-data.json` (GenericAgentData model)
- `concurrency-analyzer-data.json` (GenericAgentData model)

### 4.5 Haiku Agents

The three Haiku agents handle analyses that primarily read metadata and configuration rather than deep source code:

**alf-dependency-ops-auditor**: Reads package manifests, lock files, CI configs, Dockerfiles. All of this data is already in the Codebase Context File. The agent applies checklists and heuristics -- well within Haiku's capability.

**alf-documentation-assessor**: Scans for documentation files, counts docstrings, checks for orphaned files. Mostly counting and presence-checking, not deep reasoning.

**alf-observability-compliance-assessor**: Pattern scans for logging, tracing, metrics instrumentation, WCAG patterns, SQL patterns, audit patterns. Each is a grep-like pattern match with severity classification.

---

## 5. Pipeline Changes Required

### 5.1 Orchestrator Changes

The orchestrator needs three modifications:

1. **Add Phase 0 pre-scan**: Execute Bash commands to produce `codebase-context.json`
2. **Change agent invocations**: 8 agents instead of 21. Each receives the context file path.
3. **Adjust agent prompt template**: Include `Read codebase-context.json FIRST before any exploration`

### 5.2 Python Pipeline Changes

**Minimal changes required.** The pipeline reads JSON files by filename from the results directory. As long as the consolidated agents write the same JSON filenames with the same schemas, the pipeline needs zero changes.

The key contract is preserved:
- Same 21 JSON filenames
- Same Pydantic model validation
- Same normalization formulas
- Same report rendering

### 5.3 Agent Definitions

Create 5 new consolidated agent definitions (the others remain unchanged or are slightly modified):
1. `alf-code-quality-analyst.md` (new, replaces 3)
2. `alf-architecture-analyst.md` (new, replaces 3)
3. `alf-security-reliability-analyst.md` (new, replaces 3)
4. `alf-dependency-ops-auditor.md` (new, replaces 2)
5. `alf-documentation-assessor.md` (new, replaces 2)
6. `alf-observability-compliance-assessor.md` (new, replaces 4)
7. `alf-test-design-reviewer.md` (minor update -- add context file reading)
8. `alf-refactoring-advisor.md` (update -- add ownership analysis)

---

## 6. Risks and Mitigations

### Risk 1: Loss of Analytical Depth in Consolidated Agents

**Concern**: A single agent juggling three analytical frameworks may produce shallower analysis than three dedicated specialists.

**Severity**: Medium-High for Tier 1 agents, Low for Tier 3-4 agents.

**Mitigation**:
- Extract domain knowledge to Skills (loaded on demand, not competing for context)
- Structure the consolidated agent as sequential phases: "First analyze for code smells, then for cognitive load, then for consistency" -- not "analyze everything at once"
- Each analytical framework produces its own JSON file, so quality is independently verifiable
- Run a comparison test: same codebase, 21-agent results vs 8-agent results, compare JSON outputs

### Risk 2: Consolidated Agents Hit maxTurns Limits

**Concern**: An agent doing the work of 3 may run out of turns before completing all analyses.

**Severity**: Medium.

**Mitigation**:
- Set `maxTurns: 50` for Phase 1 consolidated agents (vs. 30 for individual agents)
- The pre-scan context file saves ~5-8 turns of exploration per agent
- Monitor actual turn usage during testing and adjust

### Risk 3: Haiku Quality for Lightweight Agents

**Concern**: Haiku may produce lower-quality analysis for the generic agents.

**Severity**: Low. The generic agents produce `overall_score: 0-100` plus findings -- a simpler output contract that Haiku handles well.

**Mitigation**:
- Test Haiku agents independently against known codebases
- If quality is insufficient for a specific analysis, promote that agent to Sonnet
- The 15 generic agents all use the same simple output model -- Haiku is well-suited for structured output tasks

### Risk 4: Pre-scan Context File Staleness

**Concern**: The context file is a snapshot. If the codebase changes during analysis, agents may have stale context.

**Severity**: Very Low. Analysis runs take 5-15 minutes. Codebases don't change during a run.

### Risk 5: Consolidated Agent Prompt Complexity

**Concern**: A 400-line consolidated agent prompt may confuse the model.

**Severity**: Medium.

**Mitigation**:
- Keep agent definitions under 400 lines (my standard methodology)
- Domain knowledge goes into Skills (~200-300 lines each), loaded on demand
- The agent definition specifies the workflow sequence; Skills provide the rubrics
- Test with representative codebases to verify output quality

### Risk 6: Report Dimension Count Reduction

**Concern**: If we consolidate to fewer agents, do we lose report dimensions?

**Severity**: None -- this is a non-risk. **All 21 report dimensions are preserved.** Each consolidated agent writes multiple JSON files, one per dimension. The Python pipeline, normalization formulas, report templates, and 21-axis radar chart remain unchanged.

---

## 7. Migration Path

### Phase A: Pre-scan Implementation (1 day)

1. Add pre-scan Bash commands to the orchestrator
2. Define and write `codebase-context.json`
3. Test: verify context file captures all required metadata
4. **No other changes**: all 21 existing agents continue running, but each gets the context file as additional input
5. **Immediate savings**: Each agent can skip its discovery phase if it detects the context file. Estimated ~20% token reduction with zero risk.

### Phase B: Haiku Tier (2 days)

1. Create `alf-dependency-ops-auditor.md` (merge dependency-auditor + devops-evaluator)
2. Create `alf-documentation-assessor.md` (merge documentation-reviewer + dead-code-detector)
3. Create `alf-observability-compliance-assessor.md` (merge observability + system-auditor + accessibility + data-layer)
4. Update orchestrator to use 3 Haiku agents instead of 9 individual agents
5. **Validation**: Compare output JSON from new agents vs. old agents on 3 test codebases
6. **Savings**: ~30% of total tokens (these 9 agents become 3 Haiku agents)

### Phase C: Sonnet Consolidation (3 days)

1. Create `alf-code-quality-analyst.md` with Skills extraction
2. Create `alf-architecture-analyst.md` with Skills extraction
3. Create `alf-security-reliability-analyst.md` with Skills extraction
4. Update `alf-refactoring-advisor.md` to include ownership analysis
5. Update orchestrator to use 4 Sonnet agents instead of 12
6. **Validation**: Compare output quality, turn counts, and token usage
7. **Savings**: Additional ~25-40% of remaining tokens

### Phase D: Cleanup (1 day)

1. Remove deprecated individual agent definitions
2. Update orchestrator to final 3-phase execution flow
3. Update documentation
4. Run full end-to-end test

**Total migration: ~7 working days**, with savings accruing incrementally at each phase.

---

## 8. Alternative Strategies Evaluated

### 8.1 Skills Instead of Agents (Evaluated, Partially Adopted)

**Idea**: Convert lightweight analyses to Skills that run within the orchestrator.

**Verdict**: Partially adopted. The domain knowledge (rubrics, checklists, patterns) is extracted into Skills. But the analysis execution itself stays in subagents because:
- The orchestrator context would grow enormously if it executed 21 analyses itself
- Subagents provide natural isolation (one failure doesn't kill the run)
- Parallel execution requires separate agents

### 8.2 Tiered Execution / Conditional Agents (Evaluated, Deferred)

**Idea**: Run core agents first, then conditionally spawn more based on findings.

**Verdict**: Deferred to a future optimization. The added complexity (orchestrator must interpret intermediate results) outweighs the savings when combined with the pre-scan + consolidation approach. If the 8-agent architecture still consumes too many tokens, tiered execution is the next lever.

### 8.3 Single Mega-Agent (Evaluated, Rejected)

**Idea**: One agent does all 21 analyses.

**Verdict**: Rejected. A single agent analyzing 21 dimensions would:
- Exhaust its context window on large codebases
- Produce shallow analysis across all dimensions
- Lose the parallelism benefit
- Have no failure isolation

### 8.4 Pure Skill-based Analysis in Orchestrator (Evaluated, Rejected)

**Idea**: Orchestrator reads all files itself, then applies 21 Skill rubrics sequentially.

**Verdict**: Rejected. The orchestrator would need to hold the entire codebase in context, which is impractical for codebases over ~5K LOC. Subagents allow each analysis to manage its own context window.

---

## 9. Decision Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Pre-scan approach | Orchestrator-executed Bash | Zero LLM cost, deterministic, fast |
| Agent count | 21 -> 8 | Eliminates 60% of redundant exploration |
| Model tiering | 4 Sonnet + 4 Haiku | Haiku for checklist/config analysis, Sonnet for deep code reasoning |
| Report dimensions | Preserved (all 21) | Zero pipeline changes required |
| Output contract | Unchanged (same JSON files) | Zero Python code changes |
| Migration | 4 phases, incremental | Each phase delivers measurable savings independently |
| Domain knowledge | Extracted to Skills | Keeps agent definitions under 400 lines |

---

## 10. Success Metrics

After full migration:

| Metric | Current (estimated) | Target | Measurement |
|--------|-------------------|--------|-------------|
| Total agents spawned | 21 | 8 | Count in orchestrator log |
| Total input tokens per run | ~900K-1.3M | ~340K-430K | Claude API token counter |
| Sonnet input tokens | ~900K-1.3M | ~260K-310K | Filter by model |
| Report dimensions | 21 | 21 | Count in generated HTML |
| Report quality | Baseline | Equivalent or better | Manual comparison on 3 codebases |
| Wall-clock time | ~15-25 min | ~8-15 min | Fewer agents = less API latency |
| Analytical depth (per dimension) | Baseline | Equivalent | JSON output comparison |
