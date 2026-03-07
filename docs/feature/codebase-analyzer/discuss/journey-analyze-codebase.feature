Feature: Analyze Client Codebase
  As a software consultant evaluating a client's codebase,
  Andrea needs to produce an undeniable, evidence-based quality report
  that client leadership cannot dismiss, driving them from denial to action.

  Background:
    Given Andrea has a local copy of the "Acme Corp Platform" codebase
    And the codebase contains 847 Java and Python source files
    And all 6 analysis agents are available and configured

  # ─── Step 1: Configure and Launch ──────────────────────────────

  Scenario: Launch analysis with minimal configuration
    When Andrea runs "codebase-analyzer analyze /projects/acme-platform"
    Then the tool detects 847 source files
    And identifies Java as the primary language
    And defaults the project name to "acme-platform"
    And defaults the output to "./acme-platform-report.html"
    And displays a confirmation prompt with all detected settings

  Scenario: Launch analysis with full configuration
    When Andrea runs the analyzer with these options:
      | option         | value                              |
      | target         | /projects/acme-platform            |
      | project-name   | Acme Corp Platform                 |
      | output         | ./reports/acme-corp-2026-03.html   |
      | agents         | all                                |
    Then the confirmation prompt shows "Acme Corp Platform" as project name
    And the output path shows "./reports/acme-corp-2026-03.html"

  Scenario: Launch analysis with selected agents only
    Given Andrea only needs code smell and test design analysis for a quick check
    When Andrea runs the analyzer with --agents "smell,test"
    Then only the Code Smell Detection and Test Design Review agents are queued
    And the report will contain 2 dimensions instead of 6
    And the radar chart will show 2 axes instead of 6

  Scenario: Target directory does not exist
    When Andrea runs "codebase-analyzer analyze /nonexistent/path"
    Then the tool displays "Error: Directory not found: /nonexistent/path"
    And suggests similar existing directories if possible
    And exits with a non-zero status code

  Scenario: Target directory contains no source files
    Given the directory "/projects/empty-dir" exists but contains only documentation
    When Andrea runs "codebase-analyzer analyze /projects/empty-dir"
    Then the tool warns "No source files detected in /projects/empty-dir"
    And suggests checking the path or specifying file extensions

  # ─── Step 2: Monitor Agent Execution ───────────────────────────

  Scenario: All agents complete successfully in sequence
    Given Andrea has confirmed the analysis of Acme Corp Platform
    When the orchestrator runs all 6 agents
    Then each agent displays a progress bar during execution
    And each agent displays its primary score upon completion:
      | agent                    | score display            |
      | Code Smell Detection     | Grade: B, 23 issues     |
      | Test Design Review       | Farley Index: 7.2/10    |
      | Cognitive Load Analysis  | CLI Score: 312/1000     |
      | DDD Architecture Review  | Compliance: 65%         |
      | Legacy Code Assessment   | Risk: Medium            |
      | Refactoring Analysis     | 14 recommendations      |
    And elapsed time and estimated remaining time are shown throughout

  Scenario: Agent fails with timeout
    Given analysis is running and 3 agents have completed successfully
    When the DDD Architecture agent exceeds the 10-minute timeout
    Then the tool displays "DDD Architecture Review: FAILED (timeout after 10m)"
    And prompts "Continue with remaining agents? [Y/n]"
    And if Andrea confirms, the remaining agents continue
    And the final report marks the DDD dimension as "Not Available"

  Scenario: Agent fails with unexpected error
    Given the Legacy Code agent encounters a parsing error
    When the error occurs during agent execution
    Then the tool displays the error type and a brief message
    And logs the full error details to a diagnostic file
    And prompts Andrea to continue or abort
    And provides a command to retry just the failed agent

  Scenario: Refactoring agent waits for code smell agent
    Given code smell detection is still running
    When the orchestrator reaches the refactoring analysis queue position
    Then the refactoring agent shows "queued (waiting for Code Smell Detection)"
    And begins automatically once code smell detection completes
    And independent agents continue running in parallel

  # ─── Step 3: Review Report and Validate Scores ─────────────────

  Scenario: CLI displays completion summary
    Given all agents have completed and the report has been generated
    When the report generation finishes
    Then the CLI displays the output file path
    And shows a quick summary: overall score, weakest dimension, strongest dimension
    And shows how many agents completed out of total
    And prompts to open the report in the default browser

  Scenario: Executive summary communicates health at a glance
    Given Andrea opens the generated HTML report for Acme Corp Platform
    When the executive summary section loads
    Then the overall health score of 58/100 is displayed prominently with rating "Needs Attention"
    And a 6-axis radar chart shows the quality shape with all dimensions
    And each dimension is listed with its normalized score and plain-language rating
    And the weakest dimension (Refactoring Debt: 3.0/10) is visually highlighted

  Scenario: Business risk summary uses executive language
    Given Andrea is viewing the executive summary
    When she scrolls to the Business Risk Summary section
    Then she sees risk categories framed as business impacts:
      | risk category            | level    | description contains              |
      | Delivery Velocity Risk   | HIGH     | estimated velocity impact         |
      | Incident Risk            | MODERATE | code smells and test coverage     |
      | Onboarding Risk          | MODERATE | estimated ramp-up time            |
    And each risk category links to the underlying dimension evidence

  Scenario: Score derivation is fully transparent and traceable
    Given Andrea sees the Refactoring Debt score of 3.0/10
    When she navigates to the score derivation detail
    Then she sees the raw agent data: 14 recommendations (2 high, 7 medium, 5 low risk)
    And the normalization formula with actual values substituted
    And a plain-language explanation: "The codebase has accumulated significantly more refactoring debt than a healthy project"
    And a link to view all 14 specific recommendations

  Scenario: Radar chart accurately represents all dimensions
    Given the report contains scores for all 6 dimensions
    When the 6-axis radar chart renders
    Then each axis is labeled with the dimension name and score
    And the chart shape visually highlights the weakest areas (indented)
    And hovering over a radar point shows the exact score and rating

  Scenario: Report with missing dimension handles gracefully
    Given the DDD Architecture agent failed during analysis
    When the report generates with 5 of 6 dimensions
    Then the radar chart shows 5 axes instead of 6
    And the DDD section displays "Not Available -- agent timed out during analysis"
    And the overall score is calculated from the 5 available dimensions
    And a note explains the adjusted calculation

  # ─── Step 4: Present to Client Leadership ──────────────────────

  Scenario: Progressive drill-down from summary to evidence
    Given Andrea is presenting the report to Acme Corp VP of Engineering
    When the VP questions the overall score of 58/100
    Then Andrea navigates from executive summary to Refactoring Debt dimension
    And from dimension overview to score derivation showing raw data and formula
    And from score derivation to specific file-level findings
    And each level provides increasingly concrete evidence

  Scenario: File-level evidence provides undeniable proof
    Given Andrea has drilled down to the Refactoring Debt detail section
    When she opens a specific high-priority recommendation
    Then she sees the affected file name and path
    And the specific metrics (line count, complexity, violation type)
    And a severity rating with explanation
    And a recommended action

  Scenario: Report navigation supports live presentation
    Given Andrea is screen-sharing the report during a client meeting
    When she needs to navigate between different sections
    Then a sticky navigation bar is always visible at the top
    And clicking a section tab scrolls smoothly to that section
    And the current section is visually highlighted in the navigation

  Scenario: Report works offline as standalone document
    Given the CTO of Acme Corp has downloaded the report HTML file
    When the CTO opens the file on a computer without internet access
    Then all charts and visualizations render correctly
    And all navigation and drill-down interactions work
    And no external resource failures degrade the experience

  Scenario: Print mode produces clean PDF-ready output
    Given Andrea wants to provide a printed executive summary handout
    When she activates print mode or prints the page
    Then interactive elements are replaced with static representations
    And the layout is optimized for A4/Letter paper
    And charts render as static images
    And the executive summary fits on 1-2 pages

  # ─── Cross-Journey Properties ──────────────────────────────────

  @property
  Scenario: Score consistency across report levels
    Given a dimension score is displayed at the executive summary level
    Then the same score appears in the dimension detail section
    And the score derivation section produces the same value from raw data
    And no rounding inconsistencies exist between display levels

  @property
  Scenario: Business risk ratings are derivable from dimension scores
    Given the dimension scores are known
    Then the business risk ratings can be independently calculated
    And no risk rating contradicts its underlying dimension scores
    And the risk model is documented in the report methodology section

  @property
  Scenario: Report generation is deterministic
    Given the same codebase is analyzed twice with the same agent versions
    Then both reports produce identical scores
    And identical business risk ratings
    And identical dimension rankings
