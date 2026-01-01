@translation @P1
Feature: Translation Workflow
  As a Translator
  I want to translate activity content
  So that learners can use the content in their native language

  # =============================================================================
  # TRANSLATOR INTERFACE
  # =============================================================================

  @TC-TRN-001
  Scenario: View pending translations
    Given I am logged in as a Translator
    When I access the Translator interface
    And I set Status filter to "Waiting for Translation"
    Then I should see a table with the following columns:
      | Column         |
      | Activity Name  |
      | Activity Type  |
      | Level          |
      | Unit           |
      | Topic          |
      | Lesson         |
    And only activities with "Waiting for Translation" status should be shown

  @TC-TRN-002
  Scenario: Filter translations by Activity Type
    Given I am logged in as a Translator
    And I am on the Translator interface
    When I select Activity Type filter "Grammar"
    Then only Grammar activities should be displayed
    When I select Activity Type filter "All Activity Types"
    Then all activity types should be displayed

  @TC-TRN-003
  Scenario: Select target language for translation
    Given I am logged in as a Translator
    And I am on the Translator interface
    When I click on an activity
    Then the Translation view should open
    When I select target language "Spanish"
    Then the language should be clearly displayed
    And translation fields should appear for Spanish

  # =============================================================================
  # TRANSLATION BY ACTIVITY TYPE
  # =============================================================================

  @TC-TRN-004
  Scenario: Translate Grammar activity fields
    Given I am logged in as a Translator
    And I am translating a Grammar activity
    Then I should see translation fields for:
      | Field           |
      | Instructions    |
      | Grammar Tip     |
    When I translate the "Instructions" field
    And I translate the "Grammar Tip" field
    And I save the translations
    Then both translations should be saved
    And progress should be indicated

  @TC-TRN-005
  Scenario Outline: Translate activity with Instructions only
    Given I am logged in as a Translator
    And I am translating a "<activity_type>" activity
    Then I should see translation fields for "Instructions" only
    When I translate the Instructions field
    And I save the translation
    Then the translation should be saved

    Examples:
      | activity_type         |
      | Memory Game           |
      | Text-to-Text          |
      | Image-to-Text         |
      | Text-to-Image         |
      | Audio-to-Image        |
      | Speaking              |

  @TC-TRN-006
  Scenario: Translate Natural Conversations dual instructions
    Given I am logged in as a Translator
    And I am translating a Natural Conversations activity
    Then I should see translation fields for:
      | Field                    |
      | Instructions for Listen  |
      | Instructions for Speak   |
    When I translate both instruction fields
    And I save the translations
    Then both translations should be saved separately

  @TC-TRN-007
  Scenario: Translate Reading activity with highlighted words
    Given I am logged in as a Translator
    And I am translating a Reading activity
    Then I should see translation fields for:
      | Field             |
      | Instructions      |
      | Highlighted Words |
    When I translate the Instructions
    And I translate each highlighted word
    And I save the translations
    Then all translations should be saved

  @TC-TRN-008
  Scenario Outline: Translate activity with answers and distractors
    Given I am logged in as a Translator
    And I am translating a "<activity_type>" activity
    Then I should see translation fields for:
      | Field          |
      | Instructions   |
      | Correct Answer |
      | Distractors    |
    When I translate all fields
    And I save the translations
    Then all translations should be saved

    Examples:
      | activity_type |
      | Spelling      |
      | Vocabulary    |
      | Listening     |

  @TC-TRN-009
  Scenario: Translate Open Writing activity
    Given I am logged in as a Translator
    And I am translating an Open Writing activity
    Then I should see translation fields for:
      | Field        |
      | Instructions |
      | Question     |
    When I translate both fields
    And I save the translations
    Then both translations should be saved

  # =============================================================================
  # TRANSLATION COMPLETION
  # =============================================================================

  @TC-TRN-010 @P0
  Scenario: Complete translation and change status
    Given I am logged in as a Translator
    And I have completed all required translations for an activity
    When I mark the activity as "Ready to Use"
    Then the activity status should change from "Waiting for Translation" to "Ready to Use"
    And the activity should be available for ordering in Topic Builder

  @TC-TRN-011
  Scenario: Partial translation saved as in progress
    Given I am logged in as a Translator
    And I am translating an activity with multiple fields
    When I translate only some of the fields
    And I save and exit
    Then my partial translations should be saved
    And I should be able to return and complete them later
    And the activity status should remain "Waiting for Translation"

  @TC-TRN-012
  Scenario: Translation progress indicator
    Given I am logged in as a Translator
    And I am translating an activity with 5 translatable fields
    When I have translated 3 of 5 fields
    Then the progress indicator should show "3/5 complete" or "60%"
    When I complete all 5 fields
    Then the progress should show "5/5 complete" or "100%"

  # =============================================================================
  # MULTI-LANGUAGE SUPPORT
  # =============================================================================

  @TC-TRN-013
  Scenario: Switch between target languages
    Given I am logged in as a Translator
    And I am translating an activity
    And I have selected Spanish as the target language
    When I switch to French as the target language
    Then the French translation fields should appear
    And any existing French translations should be loaded
    And the Spanish translations should be preserved

  @TC-TRN-014
  Scenario: Same activity translated to multiple languages
    Given I am logged in as a Translator
    And I have an activity with Spanish translations complete
    When I select French as the target language
    Then I should be able to add French translations
    And the Spanish translations should remain unchanged
    And both language translations should be accessible
