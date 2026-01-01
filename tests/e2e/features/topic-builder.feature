@topic-builder @P1
Feature: Topic Builder
  As an Editor
  I want to organize activities into topics
  So that students have a structured learning path

  Background:
    Given I am logged in as an Editor

  # =============================================================================
  # TOPIC SELECTION
  # =============================================================================

  @TC-TPB-001
  Scenario: Access Topic Builder and select topic
    When I click "Topic Builder" from the main menu
    Then I should see the Choose Topic screen
    When I select Level "Level 2 Beginner" from the dropdown
    Then the Unit dropdown should populate with Level 2 units
    When I select Unit "Unit 3 Travel and Transportation"
    Then the Topic dropdown should populate with Unit 3 topics
    When I select Topic "Getting There"
    And I click "Next"
    Then I should see the Topic Builder screen
    And the Activities picker should be displayed

  # =============================================================================
  # ACTIVITY MANAGEMENT
  # =============================================================================

  @TC-TPB-002
  Scenario: Filter activities by Lesson Type
    Given I am on the Topic Builder screen
    And there are activities of various lesson types available
    When I select Lesson Type filter "Grammar"
    Then only Grammar lesson type activities should be shown
    When I select Lesson Type filter "All"
    Then all available activities should be shown

  @TC-TPB-003
  Scenario: Add activity to topic
    Given I am on the Topic Builder screen
    And the Activities picker shows available activities in the left column
    When I click on an activity in the left column
    Then the activity should appear in the Selected Activities column on the right
    And the activity tile should display the activity name and lesson type

  @TC-TPB-004
  Scenario: Reorder activities using drag and drop
    Given I am on the Topic Builder screen
    And I have added 3 activities to the topic in order A, B, C
    When I drag activity C to position 1
    And I release the activity
    Then the order should update to C, A, B
    And I should see visual feedback during the drag operation

  @TC-TPB-005
  Scenario: Remove activity from topic
    Given I am on the Topic Builder screen
    And I have added 3 activities to the Selected Activities column
    When I click the remove/X button on one activity
    Then that activity should be removed from the Selected column
    And the activity should return to the available activities pool
    And the remaining activities should maintain their order

  @TC-TPB-006
  Scenario: Save topic and continue later
    Given I am on the Topic Builder screen
    And I have added some activities to the topic
    When I click "Save and Set as In Progress"
    Then the topic status should change to "In Progress"
    And I should be redirected to the Main Topics page
    When I return to the same topic later
    Then the previously added activities should still be present
    And I should be able to continue editing

  # =============================================================================
  # MAIN TOPICS PAGE
  # =============================================================================

  @TC-TPB-007
  Scenario: Filter and sort topics on Main Topics page
    Given I am on the Main Topics page
    When I filter by Level "Level 2 Beginner"
    Then only Level 2 topics should be displayed
    When I filter by Unit "Unit 3"
    Then only Unit 3 topics should be displayed
    When I filter by Status "In Progress"
    Then only In Progress topics should be displayed
    When I sort by "Topic Title"
    Then topics should be sorted alphabetically by title
    When I sort by "No. of Activities"
    Then topics should be sorted by activity count

  @TC-TPB-008
  Scenario: View topic activities from Main Topics page
    Given I am on the Main Topics page
    When I click on a topic
    Then I should see the Topic Activities page
    And I should see columns for:
      | Column          |
      | Activity Title  |
      | Creator         |
      | Activity Type   |
      | No. of Questions|
      | Lesson Type     |

  @TC-TPB-009
  Scenario: Edit topic from Topic Activities page
    Given I am viewing a topic's activities
    When I click "Edit"
    Then I should be brought to the Topic Builder page
    And I should be able to add, remove, or reorder activities

  # =============================================================================
  # TOPIC COMPLETION
  # =============================================================================

  @TC-TPB-010
  Scenario: Complete topic with all activities ready
    Given I am on the Topic Builder screen
    And all activities in the topic are in "Ready" status
    When I click "Save and Set as Done"
    Then the topic status should change to "Done"
    And a popup should appear with:
      | Element                                                    |
      | "[Topic title] is done!"                                   |
      | "By completing activities within this topic, students should be able to [CEFR Descriptor_short]" |
      | "OK" button                                                |
    When I click "OK"
    Then I should be redirected to the Main Topics page

  @TC-TPB-011 @negative
  Scenario: Cannot complete topic with non-Ready activities
    Given I am on the Topic Builder screen
    And some activities in the topic are still in "Draft" status
    When I attempt to click "Save and Set as Done"
    Then the button should be disabled or show an error
    And I should see a message indicating which activities are not ready

  # =============================================================================
  # ACTIVITY DISPLAY IN TOPIC
  # =============================================================================

  @TC-TPB-012
  Scenario: Activity tiles show relevant information
    Given I am on the Topic Builder screen
    When I add activities to the Selected Activities column
    Then each activity tile should display:
      | Information     |
      | Activity Name   |
      | Lesson Type     |
    And the tiles should be clearly distinguishable

  @TC-TPB-013
  Scenario: Empty topic shows appropriate message
    Given I am on the Topic Builder screen
    And no activities have been added to the topic
    Then the Selected Activities column should show an empty state message
    And I should be prompted to add activities from the left column
