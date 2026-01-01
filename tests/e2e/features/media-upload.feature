@media @upload @P1
Feature: Media Upload
  As an Editor
  I want to upload images and audio files
  So that activities have the required media assets

  Background:
    Given I am logged in as an Editor

  # =============================================================================
  # IMAGE UPLOAD
  # =============================================================================

  @TC-MED-001
  Scenario: Upload valid image formats
    Given I am on a question screen that requires an image
    When I click "Upload Image"
    And I select a valid JPEG image
    Then the image should upload successfully
    And a thumbnail preview should be displayed

  @TC-MED-002
  Scenario: Upload image via drag and drop
    Given I am on a question screen that requires an image
    When I drag and drop a valid PNG image onto the upload area
    Then the image should upload successfully
    And a thumbnail preview should be displayed

  @TC-MED-003 @negative
  Scenario: Reject invalid image format
    Given I am on a question screen that requires an image
    When I attempt to upload a .txt file as an image
    Then the upload should be rejected
    And I should see an error message "Invalid file format"

  @TC-MED-004 @negative
  Scenario: Reject PDF as image
    Given I am on a question screen that requires an image
    When I attempt to upload a .pdf file as an image
    Then the upload should be rejected
    And I should see an error message indicating only image formats are accepted

  # =============================================================================
  # AUDIO UPLOAD
  # =============================================================================

  @TC-MED-005
  Scenario: Upload valid MP3 audio
    Given I have created a Natural Conversations activity
    And I am on the question creation screen
    When I click "Upload Audio"
    And I select a valid .mp3 file
    Then the audio should upload successfully
    And a playback control should be available

  @TC-MED-006 @negative
  Scenario: Reject invalid audio format
    Given I have created an Audio-to-Image activity
    And I am on the question creation screen
    When I attempt to upload a .wav file as audio
    Then the upload should be rejected if only MP3 is supported
    And I should see an error message about accepted formats

  @TC-MED-007
  Scenario: Audio playback after upload
    Given I have uploaded an audio file to a question
    When I click the playback control
    Then the audio should play
    And I should be able to pause/stop the playback

  # =============================================================================
  # IMAGE SOURCE ATTRIBUTION
  # =============================================================================

  @TC-MED-008
  Scenario: Enter image source after upload
    Given I am on a question screen that requires an image
    When I upload an image successfully
    Then a thumbnail preview should display
    And the Image Source field should become available
    When I enter text in the Image Source field
    Then the source should be associated with the uploaded image

  # =============================================================================
  # IMAGE REPLACEMENT
  # =============================================================================

  @TC-MED-009
  Scenario: Replace existing image
    Given I have a question with an uploaded image
    When I click to replace the image
    And I upload a new image
    Then the new image should replace the old one
    And the new thumbnail should be displayed
    And the Image Source field should be cleared or retained based on design

  # =============================================================================
  # ACTIVITY-SPECIFIC MEDIA REQUIREMENTS
  # =============================================================================

  @TC-MED-010
  Scenario: Memory Game requires 6 images
    Given I have created a Memory Game activity
    And I am on the matching game screen
    Then I should see 6 image upload areas
    When I upload images for all 6 pairs
    Then all 6 thumbnails should be displayed
    And I should be able to approve for translation

  @TC-MED-011
  Scenario: Text-to-Image requires images for answer options
    Given I have created a Text-to-Image activity
    And I am on the question creation screen
    Then I should see image upload areas for:
      | Field        |
      | Correct Answer |
      | Distractor 1   |
      | Distractor 2   |
      | Distractor 3   |
    And each image upload should have an associated Image Source field

  @TC-MED-012
  Scenario: Audio-to-Image requires both audio and images
    Given I have created an Audio-to-Image activity
    And I am on the question creation screen
    Then I should see an audio upload area for the question
    And I should see image upload areas for the answer options
    When I upload audio and all required images
    Then I should be able to save the question

  @TC-MED-013
  Scenario: Spelling requires both audio and image
    Given I have created a Spelling activity
    And I am on the question creation screen
    Then I should see an audio upload area
    And I should see an image upload area
    When I upload both audio and image
    Then I should be able to save the question

  @TC-MED-014 @negative
  Scenario: Cannot save Spelling question without audio
    Given I have created a Spelling activity
    And I am on the question creation screen
    When I fill in the Word/Phrase and other text fields
    And I upload an image
    But I do not upload audio
    And I click "Save and Continue"
    Then the save should be blocked
    And I should see an error indicating audio is required

  # =============================================================================
  # IMAGE SIZE VALIDATION (if system enforces)
  # =============================================================================

  @TC-MED-020
  Scenario Outline: Image dimensions per activity type
    Given I have created a "<activity_type>" activity
    And I am on the question creation screen
    When I upload an image
    Then the system should process it for mobile dimensions "<mobile_size>"
    And the system should process it for desktop dimensions "<desktop_size>"

    Examples:
      | activity_type          | mobile_size | desktop_size |
      | Reading                | 305x205     | 305x205      |
      | Image-to-Text          | 326x204     | 705x440      |
      | Text-to-Image          | 155x97      | 360x225      |
      | Audio-to-Image         | 155x97      | 360x225      |
      | Open Writing           | 366x218     | 560x363      |
      | Spelling               | 326x176     | 675x420      |
      | Memory Game            | 106x106     | 220x220      |

  # =============================================================================
  # FILE SIZE LIMITS (if applicable)
  # =============================================================================

  @TC-MED-021 @negative
  Scenario: Reject oversized image file
    Given I am on a question screen that requires an image
    When I attempt to upload an image larger than the allowed size limit
    Then the upload should be rejected
    And I should see an error message about file size

  @TC-MED-022 @negative
  Scenario: Reject oversized audio file
    Given I am on a question screen that requires audio
    When I attempt to upload an audio file larger than the allowed size limit
    Then the upload should be rejected
    And I should see an error message about file size
