Feature: Score Transparency and Derivation
  As a software consultant defending scores during client pushback,
  Andrea needs every number to be fully traceable from executive summary
  through normalization formula to raw agent data,
  so that one challenged number cannot destroy trust in the entire report.

  # --- Score Derivation Panels ---

  @skip
  Scenario: Refactoring debt derivation shows raw data and formula
    Given the refactoring agent produced 14 recommendations
    And the risk distribution is 2 high-risk, 7 medium-risk, and 5 low-risk
    And the normalized score is 3.0 out of 10
    When the score derivation for Refactoring Debt is generated
    Then the derivation shows the raw recommendation count and risk breakdown
    And the formula is displayed with symbolic notation
    And the formula is displayed with actual values substituted
    And the formula result matches the displayed score of 3.0

  @skip
  Scenario: Test design derivation shows property-level breakdown
    Given the test design agent produced a Farley Index of 7.2
    And the 8 property scores are available
    When the score derivation for Test Design is generated
    Then the derivation shows each of the 8 property scores
    And the composite formula weights are shown
    And the resulting Farley Index matches 7.2

  @skip
  Scenario: Cognitive load derivation shows inversion from CLI score
    Given the cognitive load agent produced a CLI score of 312
    And the 8 dimension raw scores are available
    When the score derivation for Cognitive Load is generated
    Then the derivation shows the CLI score of 312 out of 1000
    And the inversion formula is displayed with values
    And the resulting quality score matches 6.9 out of 10

  @skip
  Scenario: Code quality derivation shows grade-to-score mapping
    Given the code smell agent produced a grade of "B"
    And the severity distribution is 1 high, 8 medium, and 14 low issues
    When the score derivation for Code Quality is generated
    Then the derivation shows the grade "B"
    And the grade-to-score mapping table is displayed
    And the resulting score matches 8.0 out of 10

  # --- Plain Language Explanations ---

  @skip
  Scenario: Each derivation includes a plain-language explanation
    Given any dimension has a normalized score
    When the score derivation is generated
    Then a "What this means" section explains the score in non-technical language
    And the explanation describes the business consequence of the score level

  @skip
  Scenario: Low score explanation emphasizes urgency
    Given the Refactoring Debt score is 3.0 out of 10
    When the explanation is generated
    Then the explanation indicates significant debt above healthy levels
    And the language conveys urgency without using technical jargon

  @skip
  Scenario: High score explanation confirms health
    Given the Test Design score is 8.2 out of 10
    When the explanation is generated
    Then the explanation confirms strong test design practices
    And identifies the area with most room for improvement

  # --- Formula Reproducibility ---

  @skip
  Scenario: Manually applying displayed formula reproduces displayed score
    Given the Refactoring Debt derivation shows raw data and formula
    When the formula is applied to the raw data values shown in the derivation
    Then the result is exactly 3.0 with no rounding discrepancy

  @skip
  Scenario: Overall score derivation shows weighted formula
    Given the 6 dimension scores and their weights are displayed
    When the overall score formula is applied
    Then the result matches the displayed overall score of 58 out of 100

  # --- Error and Edge Cases ---

  @skip
  Scenario: Derivation for missing dimension shows explanation
    Given the DDD agent failed during analysis
    When the DDD Compliance derivation section is generated
    Then it shows "Not Available" with the failure reason
    And no formula or misleading placeholder score is shown

  @skip
  Scenario: Derivation handles edge case scores correctly
    Given a dimension score is exactly 0.0
    When the score derivation is generated
    Then the formula is displayed with values producing 0.0
    And the explanation describes the most severe interpretation

  @skip
  Scenario: Derivation handles perfect scores correctly
    Given a dimension score is exactly 10.0
    When the score derivation is generated
    Then the formula is displayed with values producing 10.0
    And the explanation describes the best possible interpretation

  @skip
  @property
  Scenario: Score consistency across all report display levels
    Given a dimension score is displayed at the executive summary level
    Then the same score appears in the dimension detail section
    And the score derivation section produces the same value from raw data
    And no rounding inconsistencies exist between display levels
