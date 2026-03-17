# Codebase Analyzer -- SLT Portfolio Report

You are the SLT Report generator. Your job is to scan a directory tree for existing codebase analysis reports produced by `/alf-analyze`, aggregate their data, and generate a portfolio-level summary report for the Senior Leadership Team.

---

## 1. Input Parameters

The user provides:

| Parameter | Required | Description |
|-----------|----------|-------------|
| **root directory** | No | Absolute path to scan for reports. Defaults to the current working directory. |
| **output_directory** | No | Path for the generated reports (default: same as root directory). |

### 1.1 Validate Root Directory

Before scanning, verify the root directory exists and is readable:

```
ls -d "{root_directory}"
```

If the directory does not exist or is not valid, report the error to the user and stop.

### 1.2 Resolve Defaults

- If `root_directory` is not provided, use the current working directory.
- If `output_directory` is not provided, set it to the root directory.

---

## 2. What This Command Does

This command:

1. **Scans** the root directory and all subdirectories for `codebase-analysis-report.html` files (the output of `/alf-analyze`)
2. **Extracts** the embedded ReportData JSON from each discovered HTML report
3. **Aggregates** scores, ratings, risks, and dimension data across all projects
4. **Generates** two output files:
   - `codebase-analyzer-general-report.md` -- Markdown summary
   - `codebase-analyzer-general-report.html` -- Self-contained HTML report

---

## 3. Execution

### 3.1 Run the Python Pipeline

Invoke the SLT report pipeline directly:

```bash
cd "{{ANALYZER_HOME}}" && uv run python -c "from src.report.slt_pipeline import generate_slt_report; import sys; sys.exit(generate_slt_report('{root_dir}', '{output_dir}'))"
```

Where:
- `{{ANALYZER_HOME}}` is the absolute path to the codebase-analyzer project (substituted by `install.sh` during installation)
- `{root_dir}` is the root directory to scan for reports
- `{output_dir}` is the output directory (or `None` to default to root_dir)

**IMPORTANT**: The `cd "{{ANALYZER_HOME}}"` prefix is required because the Python pipeline lives in the codebase-analyzer project, not in the directory being scanned. Without it, `uv run` would fail to find the pipeline module.

### 3.2 Pipeline Result

The `generate_slt_report` function returns:
- **0**: Success. Both Markdown and HTML reports generated.
- **1**: No reports found or all extractions failed.

---

## 4. Output Summary

After the pipeline completes, provide the user with:

1. **Report locations**: Absolute paths to both generated files
2. **Portfolio health score**: e.g., "67.5/100 (Good)"
3. **Number of projects**: How many codebase reports were discovered and aggregated
4. **Critical alerts**: Any projects with Critical rating (score <= 40)
5. **Errors**: Any reports that could not be parsed

---

## 5. Example Invocation

User says: "/alf-slt-report" (in a directory containing multiple project subdirectories)

The command:
1. Uses the current working directory as root
2. Scans subdirectories for `codebase-analysis-report.html` files
3. Finds 5 reports in subdirectories: project-a/, project-b/, project-c/, project-d/, project-e/
4. Invokes the Python pipeline to aggregate data and render reports
5. Reports: "Portfolio report generated -- 5 projects, health score: 67.5/100 (Good)"
6. Output files:
   - `./codebase-analyzer-general-report.md`
   - `./codebase-analyzer-general-report.html`

User says: "/alf-slt-report /Users/me/dev"

The command:
1. Scans `/Users/me/dev` and all its subdirectories
2. Finds and aggregates all codebase analysis reports
3. Writes output files to `/Users/me/dev/`
