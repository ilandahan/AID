@status @workflow @P0
Feature: Content Status Workflow
  As a CMS system
  I must enforce proper status transitions
  So that content follows the correct approval workflow

  # =============================================================================
  # ACTIVITY STATUS FLOW:
  # Draft → In Translation → Ready → In Staging → In Production
  #                                       ↓
  #                              (Edit) → Draft (reset)
  # =============================================================================

  # =============================================================================
  # ACTIVITY STATUS TESTS
  # =============================================================================

  @TC-STS-001 @smoke
  Scenario: New activity starts with Draft status
    Given I am logged in as an Editor
    When I create a new Grammar activity with all required fields
    And I save the activity
    Then the activity status should be "Draft"

  @TC-STS-002 @smoke
  Scenario: Approve activity for translation after all questions saved
    Given I am logged in as an Editor
    And I have a Grammar activity in "Draft" status
    And the activity has 5 questions defined
    And all 5 questions have been saved
    When I click "Approve for Translation"
    Then a popup should appear with a green checkmark
    And the popup should show the Activity Title
    And the popup should display "Grammar activity type with 5 questions has been approved and is now available for translation"
    And the popup should have a "Create New Activity" button
    And the popup should have a "See All Activities" button
    And the activity status should change to "In Translation"

  @TC-STS-003 @negative
  Scenario: Cannot approve for translation with incomplete questions
    Given I am logged in as an Editor
    And I have a Grammar activity in "Draft" status
    And the activity has 5 questions defined
    But only 3 questions have been saved
    When I attempt to click "Approve for Translation"
    Then the button should be disabled or show an error
    And I should see a message "All questions must be saved before approving"
    And the activity status should remain "Draft"

  @TC-STS-004
  Scenario: Translator completes translation and marks Ready
    Given I am logged in as a Translator
    And there is an activity in "In Translation" status
    When I complete all required translations for the activity
    And I click "Approve for Staging"
    Then the activity status should change to "Ready"
    And the activity should be available for ordering in Topic Builder

  @TC-STS-005
  Scenario: Ready activity moves to In Staging when added to topic
    Given I am logged in as an Editor
    And there is an activity in "Ready" status
    When I open the Topic Builder
    And I add the Ready activity to a topic
    And I save the topic
    Then the activity status should change to "In Staging"
    And the activity should inherit the topic's staging status

  @TC-STS-006 @critical
  Scenario: Editing activity resets status to Draft
    Given I am logged in as an Editor
    And there is an activity in "Ready" status
    When I open the activity for editing
    And I change any field in a question
    And I save the changes
    Then the activity status should RESET to "Draft"
    And the activity must go through the approval flow again

  @TC-STS-007
  Scenario: Editing In Staging activity resets to Draft
    Given I am logged in as an Editor
    And there is an activity in "In Staging" status
    When I edit any question content
    And I save the changes
    Then the activity status should RESET to "Draft"
    And the activity should be removed from the topic order

  # =============================================================================
  # TOPIC STATUS FLOW:
  # To Do → In Progress → In Staging → In Production
  # =============================================================================

  @TC-STS-010
  Scenario: New topic with no activities has To Do status
    Given I am logged in as an Editor
    When I view a topic that has no activities ordered within it
    Then the topic status should be "To Do"

  @TC-STS-011
  Scenario: Topic changes to In Progress when activities added
    Given I am logged in as an Editor
    And there is a topic in "To Do" status
    When I open the Topic Builder for this topic
    And I add at least one activity
    And I click "Save and Set as In Progress"
    Then the topic status should change to "In Progress"

  @TC-STS-012
  Scenario: Topic changes to In Staging when all activities Ready
    Given I am logged in as an Editor
    And there is a topic in "In Progress" status
    And all activities within the topic are in "Ready" status
    When I open the Topic Builder
    And I verify all activities are Ready
    And I click "Save and Set as Ready for Production"
    Then the topic status should change to "In Staging" (Done)
    And all activities should inherit "In Staging" status

  @TC-STS-013
  Scenario: Topic completion shows confirmation popup
    Given I am logged in as an Editor
    And there is a topic with all activities ready
    When I click "Save and Set as Done"
    Then a popup should appear with the message "[Topic title] is done!"
    And the popup should display "By completing activities within this topic, students should be able to [CEFR Descriptor_short]"
    And the popup should have an "OK" button
    When I click "OK"
    Then I should be redirected to the Main Topics page

  # =============================================================================
  # STATUS TRANSITION VALIDATION
  # =============================================================================

  @TC-STS-020 @negative
  Scenario: Cannot skip Draft status
    Given there is a new activity
    Then the activity cannot be directly set to "In Translation" without first being "Draft"
    And the activity cannot be directly set to "Ready" without going through "In Translation"

  @TC-STS-021 @negative
  Scenario: Cannot approve incomplete Memory Game for translation
    Given I have a Memory Game activity in "Draft" status
    And only 4 of 6 pairs are complete
    When I attempt to approve for translation
    Then the approval should be blocked
    And I should see a message about requiring 6 pairs

  @TC-STS-022
  Scenario: Status history is maintained
    Given I am logged in as an Editor
    And I have an activity in "Draft" status
    When I move the activity through Draft → In Translation → Ready
    And then I edit the activity (resetting to Draft)
    Then the status history should show all transitions
    And the current status should be "Draft"

  # =============================================================================
  # BULK STATUS OPERATIONS
  # =============================================================================

  @TC-STS-030
  Scenario: Publishing topic moves all activities to Production
    Given I am logged in as an Admin
    And there is a topic in "In Staging" status
    And all activities in the topic are in "In Staging" status
    When I publish the topic to Production
    Then the topic status should change to "In Production"
    And all activities within the topic should change to "In Production"

  @TC-STS-031
  Scenario: Cannot publish topic with non-Ready activities
    Given I am logged in as an Admin
    And there is a topic with some activities still in "Draft" status
    When I attempt to publish the topic
    Then the publish should be blocked
    And I should see a list of activities that are not ready
