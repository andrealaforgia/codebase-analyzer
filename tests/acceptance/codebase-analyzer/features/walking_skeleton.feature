@walking_skeleton
Feature: Codebase Analysis End-to-End
  As a software consultant evaluating a client's codebase,
  Andrea needs to produce an evidence-based quality report from agent results,
  so that client leadership receives an undeniable assessment of codebase health.

  These walking skeletons validate the thinnest vertical slices that deliver
  observable user value from agent data through to a complete HTML report.

  Background:
    Given analysis results are available for the "Acme Corp Platform" project
    And the analysis included all 6 quality dimensions

  @first
  Scenario: Andrea produces a health report from analysis results
    Given the analysis produced these dimension scores:
      | dimension        | score |
      | Code Quality     | 6.0   |
      | Test Design      | 7.2   |
      | Cognitive Load   | 6.9   |
      | DDD Compliance   | 6.5   |
      | Legacy Safety    | 5.5   |
      | Refactoring Debt | 3.0   |
    When the report is generated for "Acme Corp Platform"
    Then Andrea receives a self-contained HTML report
    And the report shows an overall health score of 58 out of 100
    And the report displays the rating "Needs Attention"
    And the report includes a radar chart with all 6 dimensions
    And each dimension score is visible in the report

  @skip
  Scenario: Andrea traces a score from summary through derivation to raw evidence
    Given the Refactoring Debt dimension scored 3.0 out of 10
    And the raw data shows 14 recommendations with 2 high-risk, 7 medium-risk, and 5 low-risk items
    When Andrea opens the score derivation for Refactoring Debt
    Then the derivation shows the raw recommendation counts
    And the normalization formula is displayed with actual values substituted
    And the calculated result matches the displayed score of 3.0
    And a plain-language explanation describes the business impact

  @skip
  Scenario: Andrea reviews business risk framing for client presentation
    Given the dimension scores have been normalized
    And the risk model has been applied
    When Andrea views the business risk summary
    Then Delivery Velocity Risk is assessed based on refactoring debt and cognitive load
    And Incident Risk is assessed based on legacy safety and test design
    And Onboarding Risk is assessed based on cognitive load and code quality
    And each risk category shows a severity level and contributing dimensions
