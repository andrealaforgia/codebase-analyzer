# ADR-004: Report Format -- Self-Contained HTML with Inlined Libraries

## Status
Accepted

## Context

The report is a consulting deliverable shared with client leadership and technical leads. It must work in multiple contexts: live screen-share during meetings, standalone exploration by clients after meetings, printed handouts, and environments with restricted or no internet access (client VPNs, air-gapped networks).

## Decision

Generate a **single self-contained HTML file** with all JavaScript libraries (Chart.js, D3.js, Mermaid.js), CSS, and report data inlined. No external resource dependencies at view time. Target file size ~3MB.

Libraries are stored as minified source files in `src/assets/` and inlined into the HTML during report generation via Jinja2 template inclusion.

## Alternatives Considered

### Alternative 1: CDN-loaded libraries with offline fallback
- **What**: Default to CDN loading (~500KB HTML) with `--offline` flag to inline
- **Expected impact**: Smaller default file size, faster first load on fast connections
- **Why rejected**: A consulting report must never fail during a client presentation. CDN unavailability at a client site (firewalls, VPN restrictions, conference WiFi) would produce a broken report at the worst possible moment. The downside of a failed presentation outweighs the benefit of a smaller file.

### Alternative 2: Multi-file report with directory structure
- **What**: Generate `report/index.html` + `report/assets/` directory with separate JS/CSS files
- **Expected impact**: Better caching, easier debugging of individual files
- **Why rejected**: Sharing a directory is harder than sharing a single file. Email attachments, Slack, Git -- all easier with one file. Clients lose assets when copying just the HTML file.

### Alternative 3: PDF report (static)
- **What**: Generate a PDF with static charts rendered server-side
- **Expected impact**: Universally viewable, no browser dependency
- **Why rejected**: No interactivity. The denial-proof drill-down pattern requires clickable navigation from summary to evidence. PDF cannot provide 4-level progressive disclosure. Print CSS mode addresses the PDF use case for handouts.

## Consequences

- **Positive**: Works everywhere -- any browser, any OS, offline, behind firewalls
- **Positive**: Single file is trivially shareable (email, Slack, Git)
- **Positive**: No deployment infrastructure needed
- **Negative**: ~3MB file size (acceptable for a consulting report; comparable to a few high-res images)
- **Negative**: Library updates require updating the inlined source files in the repo
