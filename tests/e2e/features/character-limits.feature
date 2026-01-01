@character-limits @validation @P0
Feature: Character Limit Enforcement
  As a CMS system
  I must enforce character limits by preventing further typing
  So that content fits within system constraints

  Background:
    Given I am logged in as an Editor

  # =============================================================================
  # CRITICAL: PRD states "user will not be able to continue typing"
  # All character limit tests are P0 priority
  # =============================================================================

  # =============================================================================
  # REFERENCE DATA CHARACTER LIMITS
  # =============================================================================

  @TC-CHR-001
  Scenario: Unit Name enforces 35 character maximum
    Given I am on the Unit management screen
    When I type exactly 35 characters in the Unit Name field
    Then the field should contain exactly 35 characters
    When I attempt to type the 36th character
    Then the input should be blocked
    And the character counter should show "35/35"

  @TC-CHR-002
  Scenario: Topic Name enforces 30 character maximum
    Given I am on the Topic management screen
    When I type exactly 30 characters in the Topic Name field
    Then the field should contain exactly 30 characters
    When I attempt to type the 31st character
    Then the input should be blocked

  @TC-CHR-005
  Scenario: CEFR Descriptor Short enforces 60 character maximum
    Given I am editing a Topic
    When I type exactly 60 characters in the CEFR Descriptor Short field
    Then the field should contain exactly 60 characters
    When I attempt to type the 61st character
    Then the input should be blocked

  # =============================================================================
  # INSTRUCTIONS FIELD - UNIVERSAL 80 CHARACTER LIMIT
  # =============================================================================

  @TC-CHR-006 @smoke
  Scenario Outline: Instructions field enforces 80 character limit for all activity types
    Given I have created a "<activity_type>" activity
    And I am on the question creation screen
    When I type exactly 80 characters in the Instructions field
    Then the Instructions field should contain exactly 80 characters
    When I attempt to type the 81st character
    Then the input should be blocked

    Examples:
      | activity_type         |
      | Grammar               |
      | Text-to-Text          |
      | Image-to-Text         |
      | Text-to-Image         |
      | Audio-to-Image        |
      | Memory Game           |
      | Natural Conversations |
      | Listening             |
      | Speaking              |
      | Reading               |
      | Vocabulary            |
      | Spelling              |
      | Open Writing          |

  # =============================================================================
  # QUESTION FIELD - VARYING LIMITS BY ACTIVITY TYPE
  # =============================================================================

  @TC-CHR-007
  Scenario Outline: Question field enforces 80 character limit for standard activity types
    Given I have created a "<activity_type>" activity
    And I am on the question creation screen
    When I type exactly 80 characters in the Question field
    Then the Question field should contain exactly 80 characters
    When I attempt to type the 81st character
    Then the input should be blocked

    Examples:
      | activity_type  |
      | Grammar        |
      | Text-to-Text   |
      | Image-to-Text  |
      | Text-to-Image  |
      | Memory Game    |
      | Reading        |
      | Vocabulary     |
      | Spelling       |

  @TC-CHR-008
  Scenario: Open Writing Question field enforces 98 character limit
    Given I have created an "Open Writing" activity
    And I am on the question creation screen
    When I type exactly 98 characters in the Question field
    Then the Question field should contain exactly 98 characters
    When I attempt to type the 99th character
    Then the input should be blocked

  @TC-CHR-009
  Scenario Outline: Question/Transcript field has no limit for audio-based activities
    Given I have created a "<activity_type>" activity
    And I am on the question creation screen
    When I type 500 characters in the Question/Transcript field
    Then all 500 characters should be accepted
    And there should be no character limit indicator

    Examples:
      | activity_type         |
      | Natural Conversations |
      | Audio-to-Image        |
      | Listening             |
      | Speaking              |

  # =============================================================================
  # ANSWER FIELD LIMITS
  # =============================================================================

  @TC-CHR-010
  Scenario Outline: Answer field enforces 38 character limit for most activity types
    Given I have created a "<activity_type>" activity
    And I am on the question creation screen
    When I type exactly 38 characters in the Correct Answer field
    Then the Correct Answer field should contain exactly 38 characters
    When I attempt to type the 39th character
    Then the input should be blocked

    Examples:
      | activity_type         |
      | Grammar               |
      | Text-to-Text          |
      | Image-to-Text         |
      | Natural Conversations |
      | Listening             |
      | Speaking              |
      | Reading               |
      | Vocabulary            |
      | Open Writing          |

  @TC-CHR-011
  Scenario: Spelling Answer field enforces 10 character limit
    Given I have created a "Spelling" activity
    And I am on the question creation screen
    When I type exactly 10 characters in the Word/Phrase field
    Then the Word/Phrase field should contain exactly 10 characters
    When I attempt to type the 11th character
    Then the input should be blocked
    And this is a UNIQUE limit compared to other activity types

  # =============================================================================
  # DISTRACTOR FIELD LIMITS
  # =============================================================================

  @TC-CHR-012
  Scenario Outline: Distractor fields enforce 38 character limit
    Given I have created a "<activity_type>" activity
    And I am on the question creation screen
    When I type exactly 38 characters in the "<distractor_field>" field
    Then the field should contain exactly 38 characters
    When I attempt to type the 39th character
    Then the input should be blocked

    Examples:
      | activity_type | distractor_field |
      | Grammar       | Distractor 1     |
      | Grammar       | Distractor 2     |
      | Grammar       | Distractor 3     |
      | Text-to-Text  | Distractor 1     |
      | Listening     | Distractor 1     |
      | Vocabulary    | Distractor 1     |

  # =============================================================================
  # BOUNDARY TESTS
  # =============================================================================

  @TC-CHR-020
  Scenario: Saving content at exact character limit
    Given I have created a "Grammar" activity
    And I am on the question creation screen
    When I enter exactly 80 characters in the Instructions field
    And I save the question
    Then the question should save successfully
    And all 80 characters should be preserved
    And there should be no truncation

  @TC-CHR-021
  Scenario: Typing final allowed character
    Given I have created a "Grammar" activity
    And I am on the question creation screen
    When I type 79 characters in the Instructions field
    Then I should be able to type one more character
    And the field should now contain 80 characters
    And further typing should be blocked

  @TC-CHR-022
  Scenario: Paste behavior when content exceeds limit
    Given I have created a "Grammar" activity
    And I am on the question creation screen
    And I have copied 100 characters to my clipboard
    When I paste into the Instructions field which has an 80 character limit
    Then only the first 80 characters should be pasted
    Or the paste should be blocked entirely with a warning
    And the field should never contain more than 80 characters

  @TC-CHR-023
  Scenario: Character counter displays correctly
    Given I have created a "Grammar" activity
    And I am on the question creation screen
    When the Instructions field is empty
    Then the character counter should show "0/80"
    When I type 40 characters
    Then the character counter should show "40/80"
    When I type 40 more characters
    Then the character counter should show "80/80"
    And the counter should indicate the limit is reached

  # =============================================================================
  # MULTI-BYTE CHARACTER HANDLING
  # =============================================================================

  @TC-CHR-030
  Scenario: Character limit counts characters not bytes for Unicode
    Given I have created a "Grammar" activity
    And I am on the question creation screen
    When I type "Héllo! ¿Cómo estás?" in the Instructions field
    Then the character count should be 19 not the byte count
    And I should be able to type 61 more characters to reach the 80 limit

  @TC-CHR-031
  Scenario: CJK characters count correctly
    Given I have created a "Grammar" activity
    And I am on the question creation screen
    When I type "你好世界" in the Instructions field
    Then the character count should be 4
    And I should be able to type 76 more characters

  @TC-CHR-032
  Scenario: Emoji characters count correctly
    Given I have created a "Grammar" activity
    And I am on the question creation screen
    When I type "Hello 👋 World 🌍" in the Instructions field
    Then the character count should reflect the actual character count
    And emoji should be counted as characters not bytes
