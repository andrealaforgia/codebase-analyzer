# ADR-006: Visualization Stack -- Chart.js + D3.js + Mermaid.js

## Status
Accepted

## Context

The report requires interactive visualizations: radar charts (master 6-axis, per-dimension), gauge/doughnut charts (overall score, per-agent scores), bar charts (issue distribution, dimension contributions), scatter plots (impact vs complexity), heatmaps (file complexity), treemaps (codebase structure), and architecture diagrams (bounded context maps). All must render in a self-contained HTML file.

## Decision

Three-library stack:
- **Chart.js v4** (MIT, ~200KB minified): Primary library for 80% of charts -- radar, doughnut, bar, scatter. Simple declarative API, responsive, tooltips built-in.
- **D3.js v7** (ISC, ~250KB minified): Secondary library for heatmaps and treemaps. Full control over SVG rendering for complex visualizations.
- **Mermaid.js v10** (MIT, ~1.5MB minified): Diagram rendering for bounded context maps from DDD agent output.

Total inlined size: ~2MB for JS libraries.

## Alternatives Considered

### Alternative 1: Plotly.js only
- **What**: Single library for all chart types including radar, heatmap, treemap
- **Expected impact**: One API to learn, built-in interactivity
- **Why rejected**: ~3MB for Plotly alone. Combined with report data, total file size exceeds 5MB. Plotly's API is heavier than needed for the chart types used. Research confirmed this concern.

### Alternative 2: Chart.js only (no D3.js)
- **What**: Use Chart.js plugins (chartjs-chart-matrix, chartjs-chart-treemap) for heatmaps and treemaps
- **Expected impact**: Single charting API, simpler stack
- **Why rejected**: Chart.js plugins for matrix/treemap are less mature and less flexible than D3.js for these specific chart types. The heatmap and treemap visualizations are important for the "denial-proof" pattern (file-level evidence) and need full control over rendering.

### Alternative 3: Highcharts
- **What**: Commercial charting library with comprehensive chart type support
- **Expected impact**: Professional charts, excellent documentation
- **Why rejected**: Proprietary license (requires commercial license for commercial use). OSS-first principle. Chart.js + D3.js cover all requirements with MIT/ISC licenses.

## Consequences

- **Positive**: MIT/ISC licensed -- no commercial license concerns for consulting use
- **Positive**: Chart.js handles the common cases simply; D3.js handles the complex cases with full control
- **Positive**: Mermaid.js renders DDD context maps from the agent's native output format
- **Negative**: Two charting libraries means two APIs. Mitigated by clear separation: Chart.js for standard charts, D3.js only for heatmaps/treemaps.
- **Negative**: ~2MB of inlined JS. Acceptable for a consulting report viewed locally.
