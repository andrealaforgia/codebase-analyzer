Feature: Agent Data Validation
  As a software consultant who relies on accurate data from analysis agents,
  Andrea needs agent outputs to be validated against their defined contracts
  before scores are calculated,
  so that malformed data never produces misleading scores in the report.

  # --- Happy Path: Valid Agent Data ---

  @skip
  Scenario: Valid code smell agent data passes validation
    Given the code smell agent produced well-formed output
    And the output contains a grade, issue counts, severity distribution, and SOLID compliance
    When the output is validated
    Then validation succeeds
    And the data is ready for normalization

  @skip
  Scenario: Valid test design agent data passes validation
    Given the test design agent produced well-formed output
    And the output contains a Farley Index, 8 property scores, and tautology counts
    When the output is validated
    Then validation succeeds

  @skip
  Scenario: Valid cognitive load agent data passes validation
    Given the cognitive load agent produced well-formed output
    And the output contains a CLI score, 8 dimension scores, and interaction penalty
    When the output is validated
    Then validation succeeds

  @skip
  Scenario: Valid refactoring agent data passes validation
    Given the refactoring agent produced well-formed output
    And the output contains a recommendation count, priority matrix, and risk distribution
    When the output is validated
    Then validation succeeds

  # --- Error Paths: Invalid Agent Data ---

  @skip
  Scenario: Missing required field is caught with clear error
    Given the code smell agent output is missing the "grade" field
    When the output is validated
    Then validation fails
    And the error message identifies the agent as "code-smell-detector"
    And the error message identifies the missing field as "grade"

  @skip
  Scenario: Invalid grade value is caught
    Given the code smell agent reported a grade of "E"
    When the output is validated
    Then validation fails
    And the error explains that grade must be one of A, B, C, D, or F

  @skip
  Scenario: Negative severity count is caught
    Given the code smell agent reported -3 high-severity issues
    When the output is validated
    Then validation fails
    And the error identifies the invalid value in severity distribution

  @skip
  Scenario: CLI score outside valid range is caught
    Given the cognitive load agent reported a CLI score of 1500
    When the output is validated
    Then validation fails
    And the error explains that CLI score must be between 0 and 1000

  @skip
  Scenario: Farley Index outside valid range is caught
    Given the test design agent reported a Farley Index of 12.5
    When the output is validated
    Then validation fails
    And the error explains that Farley Index must be between 0 and 10

  @skip
  Scenario: Completely empty agent output is caught
    Given an agent produced an empty file
    When the output is validated
    Then validation fails
    And the error explains that the output contains no data

  @skip
  Scenario: Non-JSON agent output is caught
    Given an agent produced output that is not valid data format
    When the output is validated
    Then validation fails
    And the error explains that the output could not be parsed

  @skip
  @property
  Scenario: Valid data always passes validation
    Given any agent output that conforms to the documented contract
    When the output is validated
    Then validation always succeeds

  @skip
  @property
  Scenario: Validation errors always identify the agent and field
    Given any agent output that violates the documented contract
    When the output is validated
    Then the error always names the agent
    And the error always identifies the problematic field or constraint
