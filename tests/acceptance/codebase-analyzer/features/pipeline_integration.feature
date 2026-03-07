Feature: Analysis Pipeline Integration
  As a software consultant who needs a reliable end-to-end flow,
  Andrea needs the pipeline to read agent data files, validate them,
  normalize scores, derive risks, and produce a complete HTML report
  in a single invocation,
  so that the entire flow from agent output to presentation-ready report
  is automated and trustworthy.

  # --- Happy Path: Full Pipeline ---

  @skip
  Scenario: Full pipeline produces a report from 6 agent data files
    Given agent data files exist for all 6 agents in the output directory
    And all agent data files contain valid data
    When the report pipeline is invoked for project "Acme Corp Platform"
    Then a valid HTML report file is written to the output path
    And the report contains an executive summary with overall score
    And the report contains 6 dimension detail sections
    And the report contains a business risk summary

  @skip
  Scenario: Pipeline reports which agents were processed
    Given agent data files exist for all 6 agents
    When the report pipeline is invoked
    Then the pipeline reports 6 agents processed successfully
    And 0 agents failed or missing

  # --- Partial Results ---

  @skip
  Scenario: Pipeline handles missing agent files gracefully
    Given agent data files exist for only 4 of 6 agents
    And the DDD and legacy agent files are missing
    When the report pipeline is invoked
    Then a report is generated with 4 dimension scores
    And DDD Compliance and Legacy Safety are marked as "Not Available"
    And the overall score uses adjusted weights for the 4 available dimensions
    And the pipeline reports 4 agents processed and 2 missing

  @skip
  Scenario: Pipeline handles one valid and five invalid agent files
    Given one agent data file is valid and five are malformed
    When the report pipeline is invoked
    Then a report is generated with 1 dimension score
    And 5 dimensions are marked as "Not Available"
    And the report includes explanations for each failure

  # --- Error Paths ---

  @skip
  Scenario: Pipeline fails when no agent files exist at all
    Given the output directory contains no agent data files
    When the report pipeline is invoked
    Then the pipeline exits with a non-zero status
    And a clear error explains that no agent data was found
    And no output file is produced

  @skip
  Scenario: Pipeline fails when output path is not writable
    Given all 6 agent data files are valid
    And the output path points to a read-only location
    When the report pipeline is invoked
    Then the pipeline exits with a non-zero status
    And a clear error explains the output path is not writable

  @skip
  Scenario: Pipeline handles mixed valid and invalid agent data
    Given the code smell agent produced valid data
    And the test design agent produced malformed data
    And the remaining 4 agents produced valid data
    When the report pipeline is invoked
    Then 5 dimensions are calculated successfully
    And Test Design is marked as "Not Available" due to invalid data
    And the report is otherwise complete

  # --- Pipeline Composition ---

  @skip
  Scenario: Pipeline processes agents in correct order
    Given all 6 agent data files are valid
    When the report pipeline is invoked
    Then validation runs before normalization
    And normalization runs before risk assessment
    And risk assessment runs before report rendering

  @skip
  Scenario: Pipeline preserves raw data for derivation panels
    Given all 6 agent data files are valid
    When the report pipeline is invoked
    Then the generated report contains the raw agent data for each dimension
    And the derivation panels can reconstruct scores from the embedded raw data

  @skip
  @property
  Scenario: Pipeline output is deterministic for identical inputs
    Given the same set of agent data files
    When the pipeline is invoked twice
    Then both invocations produce reports with identical scores
    And identical risk assessments
    And identical dimension rankings
