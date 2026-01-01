@activity @creation @P0
Feature: Activity Creation
  As an Editor
  I want to create learning activities
  So that students can practice language skills

  Background:
    Given I am logged in as an Editor
    And I am on the Activities page

  # =============================================================================
  # COMMON ACTIVITY CREATION TESTS
  # =============================================================================

  @TC-ACT-001 @smoke
  Scenario: Create Activity with all required fields
    When I click "Create Activity"
    And I select CEFR Level "Level 2 Beginner"
    Then the Unit dropdown should populate with Level 2 units
    When I select Unit "Unit 3 Travel and Transportation"
    Then the Topic dropdown should populate with Unit 3 topics
    When I select Topic "Getting There"
    And I hover over the Topic information icon
    Then I should see the CEFR Descriptor tooltip
    When I select Activity Type "Grammar"
    And I select Lesson Type "Grammar"
    And I enter Title "Present Tense Practice"
    And I enter Number of Questions "5"
    Then Time per Question should default to "30" seconds
    When I click "Create"
    Then the Activity should be created with status "Draft"
    And I should be redirected to the question creation screen

  @TC-ACT-002 @negative
  Scenario: Cannot create activity without required Title field
    When I click "Create Activity"
    And I select CEFR Level "Level 2 Beginner"
    And I select Unit "Unit 3 Travel and Transportation"
    And I select Topic "Getting There"
    And I select Activity Type "Grammar"
    And I select Lesson Type "Grammar"
    And I leave the Title field empty
    And I enter Number of Questions "5"
    And I click "Create"
    Then the form should not submit
    And I should see a validation error on the Title field
    And I should remain on the creation form

  @TC-ACT-003 @character-limit
  Scenario: Activity title enforces 30 character maximum
    When I click "Create Activity"
    And I select Activity Type "Grammar"
    And I type "123456789012345678901234567890" in the Title field
    Then the Title field should contain exactly 30 characters
    When I attempt to type an additional character
    Then the input should be blocked
    And the character counter should show "30/30"

  @TC-ACT-004 @character-limit
  Scenario Outline: Activity types with 60 character title limit
    When I click "Create Activity"
    And I select Activity Type "<activity_type>"
    And I type a 60 character string in the Title field
    Then the Title field should contain exactly 60 characters
    When I attempt to type the 61st character
    Then the input should be blocked

    Examples:
      | activity_type    |
      | Text-to-Image    |
      | Speaking         |
      | Spelling         |
      | Vocabulary       |
      | Listening        |

  # =============================================================================
  # GRAMMAR ACTIVITY SPECIFIC TESTS
  # =============================================================================

  @TC-ACT-010 @grammar
  Scenario: Grammar Activity - Complete grammar rules screen
    Given I have created a Grammar activity
    And I am on the Grammar Rules screen
    When I enter Short Grammar Rule "Use 'have' with I/you/we/they"
    And I enter Long Grammar Rule "The verb 'have' is used with plural subjects and first/second person singular"
    And I enter Example Sentence 1 "I have a car."
    And I enter Example Sentence 2 "They have two children."
    And I click "Next"
    Then I should proceed to the Questions screen
    And the grammar rules should be saved to the activity

  # =============================================================================
  # MEMORY GAME SPECIFIC TESTS
  # =============================================================================

  @TC-ACT-011 @memory-game @P0
  Scenario: Memory Game requires exactly 6 pairs
    Given I have created a Memory Game activity
    And I am on the matching game screen
    When I fill in Word/Phrase for only 5 pairs
    And I upload images for 5 pairs
    And I enter Image Source for 5 pairs
    And I attempt to click "Approve for Translation"
    Then the button should be disabled or show an error
    And I should see a message indicating 6 pairs are required

  @TC-ACT-012 @memory-game
  Scenario: Memory Game can be saved with words only
    Given I have created a Memory Game activity
    And I am on the matching game screen
    When I fill in Word/Phrase for all 6 pairs
    But I do not upload any images
    And I click "Save and Continue"
    Then the activity should save successfully
    And I should be able to return later to add images
    And the activity status should remain "Draft"

  # =============================================================================
  # NATURAL CONVERSATIONS SPECIFIC TESTS
  # =============================================================================

  @TC-ACT-013 @natural-conversations
  Scenario: Natural Conversations has dual instruction fields
    Given I have created a Natural Conversations activity
    And I am on the question creation screen
    Then I should see an "Instructions for Listen" field
    And I should see an "Instructions for Speak" field
    And each instruction field should have its own "Display in Native Language" toggle
    When I enter both instruction sets
    And I save the question
    Then both instruction sets should be saved
    And each should have independent native language settings

  # =============================================================================
  # READING ACTIVITY SPECIFIC TESTS
  # =============================================================================

  @TC-ACT-014 @reading
  Scenario: Reading Activity supports rich text formatting
    Given I have created a Reading activity
    And I am on the Text Creation screen
    When I enter a Reading Title
    And I type text in the Text field
    And I select a word and click the Bold button
    And I select another word and click the Italic button
    And I select another word and click the Underline button
    And I click "Next"
    Then the formatting should be applied visually
    And the preview should show the formatted text
    And the formatting should be preserved when saved

  @TC-ACT-015 @reading
  Scenario: Reading Activity highlighted words feature
    Given I have created a Reading activity
    And I am on the Text Creation screen
    When I enter Reading Text with vocabulary words
    And I click "Add Highlighted Word"
    And I enter word "transportation"
    And I select Part of Speech "noun"
    And I add 2 more highlighted words with their parts of speech
    And I click "Next"
    Then the highlighted words should appear in the list
    And each should display the word and part of speech
    And the words should appear bold in the text preview
    And the words should be marked for translation

  # =============================================================================
  # SPELLING ACTIVITY SPECIFIC TESTS
  # =============================================================================

  @TC-ACT-016 @spelling @character-limit @P0
  Scenario: Spelling Activity has 10 character answer limit
    Given I have created a Spelling activity
    And I am on the question creation screen
    When I type "automobile" in the Word/Phrase field
    Then the field should contain exactly 10 characters
    When I attempt to type the 11th character
    Then the input should be blocked
    And this limit should be different from other activity types

  # =============================================================================
  # OPEN WRITING SPECIFIC TESTS
  # =============================================================================

  @TC-ACT-017 @open-writing @character-limit @P0
  Scenario: Open Writing has 98 character question limit
    Given I have created an Open Writing activity
    And I am on the question creation screen
    When I type exactly 98 characters in the Question field
    Then the field should contain exactly 98 characters
    When I attempt to type the 99th character
    Then the input should be blocked

  # =============================================================================
  # TEXT-TO-IMAGE SPECIFIC TESTS
  # =============================================================================

  @TC-ACT-018 @text-to-image
  Scenario: Text-to-Image requires images for answer options
    Given I have created a Text-to-Image activity
    And I am on the question creation screen
    When I enter Instructions
    And I enter Question text
    And I upload an image for Correct Answer
    And I enter the Correct Answer Image Source
    And I upload an image for Distractor 1
    And I enter the Distractor 1 Image Source
    And I leave Distractor 2 and 3 empty
    And I click "Save and Continue"
    Then the question should save successfully
    And the minimum requirement of Correct Answer + 1 Distractor with images should be met

  # =============================================================================
  # AUDIO-TO-IMAGE SPECIFIC TESTS
  # =============================================================================

  @TC-ACT-019 @audio-to-image @P0
  Scenario: Audio-to-Image requires audio upload
    Given I have created an Audio-to-Image activity
    And I am on the question creation screen
    When I enter Instructions
    And I enter Audio Transcript
    But I do not upload an audio file
    And I upload answer images
    And I click "Save and Continue"
    Then the save should be blocked
    And I should see an error message "Audio file required"
    And the Audio upload field should be highlighted

  # =============================================================================
  # POINTS CALCULATION TESTS
  # =============================================================================

  @TC-ACT-020
  Scenario Outline: Points per question auto-calculates correctly
    When I click "Create Activity"
    And I select Activity Type "<activity_type>"
    And I enter Number of Questions "<num_questions>"
    Then the Points per Question field should show "<expected_points>"

    Examples:
      | activity_type | num_questions | expected_points |
      | Text-to-Image | 4             | 25              |
      | Speaking      | 5             | 20              |
      | Spelling      | 10            | 10              |
      | Vocabulary    | 3             | 33              |
      | Listening     | 2             | 50              |
