@smoke @critical
Feature: AID System Health Check
  """
  WHY: Verify the AID methodology system is properly configured
  and all core infrastructure is operational before development begins.
  IMPACT: If health check fails, Phase 4 development cannot proceed safely.
  """

  Scenario: AID state file exists and is valid
    """
    WHY: Without valid state, phase enforcement cannot work.
    """
    Given the AID system is initialized
    Then the file ".aid/state.json" should exist
    And the file should contain valid JSON
    And the JSON should have a "current_phase" field

  Scenario: AID context file exists and is valid
    """
    WHY: Without context tracking, session continuity is broken.
    """
    Given the AID system is initialized
    Then the file ".aid/context.json" should exist
    And the file should contain valid JSON
    And the JSON should have a "current_task" field

  Scenario: Pipeline config is valid
    """
    WHY: Invalid pipeline config will cause the automated
    development loop to fail at Phase 4.
    """
    Given the AID system is initialized
    Then the file ".aid/pipeline/config.json" should exist
    And the file should contain valid JSON
    And the JSON should have a "max_iterations" field
    And the JSON should have a "test_commands" field
    And the JSON should have a "thresholds" field
