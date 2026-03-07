Feature: Score Normalization
  As a software consultant who must defend every number in the report,
  Andrea needs each agent's raw output to be normalized to a consistent 0-10 scale
  using documented, reproducible formulas,
  so that dimension scores are comparable and defensible.

  # --- Happy Path: Each Agent Type Normalizes Correctly ---

  @skip
  Scenario: Code quality grade is normalized to 0-10 scale
    Given the code smell agent reported a grade of "B"
    When the score is normalized
    Then the Code Quality dimension score is 8.0 out of 10

  @skip
  Scenario: Test design Farley Index passes through directly
    Given the test design agent reported a Farley Index of 7.2
    When the score is normalized
    Then the Test Design dimension score is 7.2 out of 10

  @skip
  Scenario: Cognitive load CLI score is inverted to quality scale
    Given the cognitive load agent reported a CLI score of 312 out of 1000
    When the score is normalized
    Then the Cognitive Load dimension score is 6.9 out of 10

  @skip
  Scenario: DDD compliance score passes through from agent assessment
    Given the DDD agent reported an overall score of 6.5
    When the score is normalized
    Then the DDD Compliance dimension score is 6.5 out of 10

  @skip
  Scenario: Legacy safety score passes through from agent assessment
    Given the legacy code agent reported an overall score of 5.5
    When the score is normalized
    Then the Legacy Safety dimension score is 5.5 out of 10

  @skip
  Scenario: Refactoring debt is derived from weighted recommendation count
    Given the refactoring agent reported 14 recommendations
    And the weighted recommendation count is 25
    When the score is normalized
    Then the Refactoring Debt dimension score is within tolerance of the formula result

  # --- Overall Health Score Calculation ---

  @skip
  Scenario: Overall health score is a weighted average of all dimensions
    Given these normalized dimension scores:
      | dimension        | score | weight |
      | Code Quality     | 6.0   | 0.20   |
      | Test Design      | 7.2   | 0.20   |
      | Cognitive Load   | 6.9   | 0.20   |
      | DDD Compliance   | 6.5   | 0.15   |
      | Legacy Safety    | 5.5   | 0.15   |
      | Refactoring Debt | 3.0   | 0.10   |
    When the overall health score is calculated
    Then the overall score is 58 out of 100
    And the rating is "Needs Attention"

  @skip
  Scenario Outline: Overall rating follows documented thresholds
    Given the overall health score is <score>
    When the rating is determined
    Then the rating is "<rating>"

    Examples: Rating thresholds
      | score | rating          |
      | 32    | Critical        |
      | 40    | Critical        |
      | 41    | Needs Attention |
      | 58    | Needs Attention |
      | 60    | Needs Attention |
      | 61    | Good            |
      | 78    | Good            |
      | 80    | Good            |
      | 81    | Excellent       |
      | 95    | Excellent       |

  # --- Grade Mapping Completeness ---

  @skip
  Scenario Outline: All code quality grades map to valid scores
    Given the code smell agent reported a grade of "<grade>"
    When the score is normalized
    Then the Code Quality dimension score is <score> out of 10

    Examples: Grade to score mapping
      | grade | score |
      | A     | 10.0  |
      | B     | 8.0   |
      | C     | 6.0   |
      | D     | 4.0   |
      | F     | 2.0   |

  # --- Error Paths ---

  @skip
  Scenario: Cognitive load score at maximum produces minimum quality score
    Given the cognitive load agent reported a CLI score of 1000 out of 1000
    When the score is normalized
    Then the Cognitive Load dimension score is 0.0 out of 10

  @skip
  Scenario: Cognitive load score at minimum produces maximum quality score
    Given the cognitive load agent reported a CLI score of 0 out of 1000
    When the score is normalized
    Then the Cognitive Load dimension score is 10.0 out of 10

  @skip
  Scenario: Missing agent data does not prevent normalization of other agents
    Given the DDD agent produced no results
    And the remaining 5 agents produced valid results
    When the scores are normalized
    Then 5 dimension scores are available
    And DDD Compliance is marked as not available

  @skip
  Scenario: Invalid agent data is rejected with clear explanation
    Given the code smell agent produced malformed output
    When the output is validated
    Then a clear error identifies the agent and the invalid field

  @skip
  @property
  Scenario: Normalized scores are always within 0 to 10 range
    Given any valid agent output
    When the score is normalized
    Then the dimension score is between 0.0 and 10.0 inclusive

  @skip
  @property
  Scenario: Overall health score is always within 0 to 100 range
    Given any valid combination of dimension scores
    When the overall health score is calculated
    Then the score is between 0 and 100 inclusive

  @skip
  @property
  Scenario: Formula applied to raw data always reproduces the displayed score
    Given any agent's raw output and the documented normalization formula
    When the formula is applied to the raw data
    Then the result matches the normalized score exactly
