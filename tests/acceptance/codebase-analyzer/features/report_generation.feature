Feature: Report Generation
  As a software consultant delivering findings to client leadership,
  Andrea needs a self-contained HTML report with an executive summary,
  radar chart, dimension breakdowns, and business risk framing,
  so that the report communicates codebase health at a glance
  and supports progressive drill-down during presentations.

  Background:
    Given analysis results are available for the "Acme Corp Platform" project
    And all 6 agents completed successfully

  # --- Executive Summary ---

  @skip
  Scenario: Executive summary shows overall health score prominently
    Given the overall health score is 58 out of 100
    And the rating is "Needs Attention"
    When the report is generated
    Then the executive summary displays the score "58" prominently
    And the rating "Needs Attention" is displayed alongside the score

  @skip
  Scenario: Radar chart renders with all 6 dimensions
    Given all 6 dimension scores are available
    When the report is generated
    Then the radar chart has 6 labeled axes
    And each axis shows the corresponding dimension score
    And the chart shape reflects the relative strengths and weaknesses

  @skip
  Scenario: Weakest dimension is highlighted in executive summary
    Given Refactoring Debt is the lowest score at 3.0 out of 10
    When the report is generated
    Then Refactoring Debt is visually highlighted as the weakest dimension
    And a risk annotation explains the impact of the low score

  @skip
  Scenario: Dimension bars show all scores with plain-language ratings
    Given all 6 dimension scores are available
    When the report is generated
    Then each dimension shows its name, numeric score, and a plain-language rating
    And the dimensions are ordered by score for easy scanning

  # --- Business Risk Summary in Report ---

  @skip
  Scenario: Business risk summary appears in the report
    Given the risk model has been applied to the dimension scores
    When the report is generated
    Then the business risk summary section is present
    And it shows Delivery Velocity Risk, Incident Risk, and Onboarding Risk
    And each risk has a severity badge and descriptive text

  @skip
  Scenario: Risk categories in the report link to contributing evidence
    Given Delivery Velocity Risk is rated "HIGH"
    When the report is generated
    Then the Delivery Velocity Risk section references the contributing dimensions
    And links navigate to the relevant dimension detail sections

  # --- Per-Dimension Detail Sections ---

  @skip
  Scenario: Each dimension has a dedicated detail section
    Given all 6 agents completed successfully
    When the report is generated
    Then 6 dimension detail sections are present in the report
    And each section is accessible from the executive summary

  @skip
  Scenario: Code quality detail shows severity and category breakdowns
    Given the code smell agent found 23 issues across severity levels
    When the report is generated
    Then the Code Quality section shows the grade prominently
    And a severity distribution breakdown is displayed
    And a category distribution breakdown is displayed

  @skip
  Scenario: Test design detail shows property-level scores
    Given the test design agent produced 8 property scores
    When the report is generated
    Then the Test Design section shows the Farley Index prominently
    And individual property scores are displayed

  @skip
  Scenario: Each dimension section links to its score derivation
    Given a dimension detail section is in the report
    When the report is generated
    Then each dimension section includes a link to its score derivation panel

  # --- Partial Results ---

  @skip
  Scenario: Report generates successfully with only 5 dimensions
    Given the DDD agent failed and only 5 dimension scores are available
    When the report is generated
    Then the report is generated without errors
    And the radar chart shows 5 axes instead of 6
    And the DDD section shows "Not Available" with the failure reason
    And the overall score is calculated from 5 dimensions with adjusted weights

  @skip
  Scenario: Report generates with minimum 1 dimension
    Given only the Code Quality agent completed
    When the report is generated
    Then the report is generated without errors
    And the overall score is based on the single available dimension
    And 5 sections show "Not Available"

  # --- Report Self-Containment ---

  @skip
  Scenario: Report is a single self-contained HTML file
    Given the report has been generated
    When the output file is examined
    Then the file has an .html extension
    And all visualization libraries are embedded within the file
    And no external resource references exist in the HTML

  @skip
  Scenario: Report contains embedded data for offline access
    Given the report has been generated
    When the HTML is parsed
    Then report data is embedded as a data structure within the file
    And chart configurations are derived from the embedded data

  # --- Error Paths ---

  @skip
  Scenario: Report generation fails gracefully when no agent data exists
    Given no agent results are available
    When report generation is attempted
    Then a clear error indicates no analysis data was found
    And no partial or corrupt HTML file is produced

  @skip
  Scenario: Report handles malformed agent data gracefully
    Given one agent produced data with missing required fields
    When the report is generated
    Then the dimension with invalid data is marked as "Not Available"
    And the error reason identifies the malformed field
    And other dimensions render correctly

  @skip
  @property
  Scenario: Report generation is deterministic
    Given the same set of agent results
    When the report is generated twice
    Then both reports contain identical scores and risk ratings
