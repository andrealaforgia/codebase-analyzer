Feature: Business Risk Assessment
  As a software consultant presenting to non-technical client leadership,
  Andrea needs technical quality dimensions translated into business risk categories
  with severity levels and impact descriptions,
  so that executives understand findings in terms of delivery speed, outage risk,
  and team onboarding cost.

  Background:
    Given the dimension scores have been normalized for a codebase analysis

  # --- Happy Path: Risk Derivation from Dimension Scores ---

  @skip
  Scenario: High delivery velocity risk when refactoring debt is severe
    Given these dimension scores:
      | dimension        | score |
      | Refactoring Debt | 3.0   |
      | Cognitive Load   | 6.9   |
      | Code Quality     | 6.0   |
    When the Delivery Velocity Risk is assessed
    Then the risk severity is "HIGH"
    And the contributing dimensions include Refactoring Debt and Cognitive Load
    And the description mentions estimated velocity impact

  @skip
  Scenario: Moderate incident risk when test design and legacy safety are mediocre
    Given these dimension scores:
      | dimension     | score |
      | Legacy Safety | 5.5   |
      | Test Design   | 7.2   |
      | Code Quality  | 6.0   |
    When the Incident Risk is assessed
    Then the risk severity is "MODERATE"
    And the contributing dimensions include Legacy Safety

  @skip
  Scenario: Moderate onboarding risk when cognitive load is above average
    Given these dimension scores:
      | dimension      | score |
      | Cognitive Load | 6.9   |
      | Code Quality   | 6.0   |
      | DDD Compliance | 6.5   |
    When the Onboarding Risk is assessed
    Then the risk severity is "MODERATE"
    And the contributing dimensions include Cognitive Load and Code Quality

  @skip
  Scenario: All risk categories assessed together for complete picture
    Given these dimension scores:
      | dimension        | score |
      | Code Quality     | 6.0   |
      | Test Design      | 7.2   |
      | Cognitive Load   | 6.9   |
      | DDD Compliance   | 6.5   |
      | Legacy Safety    | 5.5   |
      | Refactoring Debt | 3.0   |
    When all business risk categories are assessed
    Then the report includes at least 3 risk categories
    And each category has a severity level and description
    And each category cites contributing dimensions

  # --- Healthy Codebase ---

  @skip
  Scenario: Healthy codebase produces low risk across all categories
    Given these dimension scores:
      | dimension        | score |
      | Code Quality     | 8.5   |
      | Test Design      | 8.2   |
      | Cognitive Load   | 8.0   |
      | DDD Compliance   | 7.5   |
      | Legacy Safety    | 7.8   |
      | Refactoring Debt | 8.0   |
    When all business risk categories are assessed
    Then all risk categories are rated "LOW"
    And the summary notes healthy technical foundations

  # --- Critical Codebase ---

  @skip
  Scenario: Critical codebase produces high risk across multiple categories
    Given these dimension scores:
      | dimension        | score |
      | Code Quality     | 3.0   |
      | Test Design      | 2.5   |
      | Cognitive Load   | 2.2   |
      | DDD Compliance   | 3.5   |
      | Legacy Safety    | 2.1   |
      | Refactoring Debt | 1.5   |
    When all business risk categories are assessed
    Then Delivery Velocity Risk is "HIGH"
    And Incident Risk is "HIGH"
    And Onboarding Risk is "HIGH"

  # --- Error and Edge Cases ---

  @skip
  Scenario: Risk assessment handles missing dimensions gracefully
    Given the DDD agent failed and only 5 dimension scores are available
    When all business risk categories are assessed
    Then risk categories that depend on DDD use only the available dimensions
    And the assessment notes which dimensions were unavailable

  @skip
  Scenario: Risk assessment with only 2 dimensions still produces useful results
    Given only Code Quality and Test Design scores are available
    When all business risk categories are assessed
    Then categories with sufficient data produce a severity rating
    And categories with insufficient data note limited confidence

  @skip
  @property
  Scenario: Risk ratings are always consistent with dimension scores
    Given any valid combination of dimension scores
    When business risk categories are assessed
    Then no risk category contradicts its underlying dimension scores
    And higher dimension scores never produce higher risk severity

  @skip
  @property
  Scenario: Risk assessment is deterministic
    Given the same dimension scores
    When the risk model is applied twice
    Then both assessments produce identical results
