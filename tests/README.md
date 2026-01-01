# Language Learning CMS - Test Suite

## Overview

This directory contains the complete test suite for the Language Learning CMS, derived from the PRD requirements.

## Directory Structure

```
tests/
├── README.md                    # This file
├── testrail-import.csv          # TestRail-compatible CSV for import
└── e2e/
    └── features/
        ├── activity-creation.feature    # Activity creation tests (all 14 types)
        ├── character-limits.feature     # Character limit enforcement tests
        ├── status-workflow.feature      # Status transition tests
        ├── topic-builder.feature        # Topic Builder functionality
        ├── translation-flow.feature     # Translation workflow tests
        └── media-upload.feature         # Media upload validation
```

## Test Case Summary

| Category | Feature File | Test Count | P0 | P1 | P2 |
|----------|--------------|------------|----|----|-----|
| Activity Creation | `activity-creation.feature` | 20 | 8 | 10 | 2 |
| Character Limits | `character-limits.feature` | 22 | 18 | 4 | 0 |
| Status Workflow | `status-workflow.feature` | 13 | 6 | 5 | 2 |
| Topic Builder | `topic-builder.feature` | 13 | 0 | 9 | 4 |
| Translation Flow | `translation-flow.feature` | 14 | 1 | 11 | 2 |
| Media Upload | `media-upload.feature` | 22 | 2 | 16 | 4 |
| **TOTAL** | | **104** | **35** | **55** | **14** |

## Test ID Convention

```
TC-[CATEGORY]-[NUMBER]

Categories:
- ACT: Activity Creation
- CHR: Character Limits
- STS: Status Workflow
- TPB: Topic Builder
- TRN: Translation
- MED: Media Upload
- CAS: Cascading Dropdowns
- NEG: Negative/Edge Cases
```

## Priority Definitions

| Priority | Description | Execution Frequency |
|----------|-------------|---------------------|
| **P0 (Critical)** | Blocks release, core functionality | Every build |
| **P1 (High)** | Important features, regression risk | Daily |
| **P2 (Medium)** | Secondary features | Weekly |
| **P3 (Low)** | Nice-to-have, edge cases | Pre-release |

## Regression Suites

### Smoke Suite (Run on Every Build)
Tagged with `@smoke` - approximately 10 tests covering critical paths.

```bash
# Run smoke tests
npx cucumber-js --tags "@smoke"
```

### P0 Suite (Critical)
Tagged with `@P0` - approximately 35 tests.

```bash
# Run P0 tests
npx cucumber-js --tags "@P0"
```

### Full Regression
All tests - approximately 104 tests.

```bash
# Run all tests
npx cucumber-js
```

## Activity Type Test Coverage

| Activity Type | TC ID Range | Unique Tests |
|---------------|-------------|--------------|
| Grammar | TC-ACT-010 | Grammar rules screen |
| Memory Game | TC-ACT-011, 012 | 6 pairs requirement |
| Natural Conversations | TC-ACT-013 | Dual instructions |
| Reading | TC-ACT-014, 015 | Rich text, highlighted words |
| Spelling | TC-ACT-016 | 10 char answer limit |
| Open Writing | TC-ACT-017 | 98 char question limit |
| Text-to-Image | TC-ACT-018 | Image answers |
| Audio-to-Image | TC-ACT-019 | Audio + image required |
| Text-to-Text | TC-ACT-003 | Standard 30 char title |
| Image-to-Text | TC-ACT-004 | Standard flow |
| Speaking | TC-ACT-004 | 60 char title |
| Vocabulary | TC-ACT-004 | 60 char title |
| Listening | TC-ACT-004 | 60 char title |

## Character Limit Matrix

| Field | Limit | Activity Types | TC ID |
|-------|-------|----------------|-------|
| Unit Name | 35 | All | TC-CHR-001 |
| Topic Name | 30 | All | TC-CHR-002 |
| Activity Title | 30 | Most | TC-ACT-003 |
| Activity Title | 60 | Text-to-Image, Speaking, Spelling, Vocabulary, Listening | TC-ACT-004 |
| CEFR Descriptor Short | 60 | All | TC-CHR-005 |
| Instructions | 80 | All | TC-CHR-006 |
| Question | 80 | Most | TC-CHR-007 |
| Question | 98 | Open Writing | TC-CHR-008 |
| Question | Unlimited | Natural Conversations, Audio-to-Image, Listen, Speak | TC-CHR-009 |
| Answer | 38 | Most | TC-CHR-010 |
| Answer | 10 | Spelling | TC-CHR-011 |
| Distractor | 38 | All with distractors | TC-CHR-012 |

## TestRail Import

To import tests into TestRail:

1. Open TestRail
2. Go to Test Cases → Import
3. Select CSV format
4. Upload `testrail-import.csv`
5. Map columns as follows:
   - ID → Case ID
   - Title → Title
   - Section → Section
   - Priority → Priority
   - Type → Type
   - Preconditions → Preconditions
   - Steps → Steps
   - Expected Result → Expected

## Running with Cucumber.js

### Setup

```bash
npm install @cucumber/cucumber --save-dev
```

### Configuration (`cucumber.js`)

```javascript
module.exports = {
  default: {
    paths: ['tests/e2e/features/**/*.feature'],
    require: ['tests/e2e/steps/**/*.js'],
    format: ['progress', 'html:reports/cucumber-report.html'],
    parallel: 2
  }
};
```

### Running Tests

```bash
# All tests
npx cucumber-js

# Specific feature
npx cucumber-js tests/e2e/features/activity-creation.feature

# By tag
npx cucumber-js --tags "@P0"
npx cucumber-js --tags "@character-limit"
npx cucumber-js --tags "@smoke"

# Exclude tags
npx cucumber-js --tags "not @P3"
```

## Test Data Requirements

### Reference Data
- 6 Levels (Pre-A through C1)
- Multiple Units per Level
- Multiple Topics per Unit
- 6 Lesson Types
- 14 Activity Types

### Test User Accounts
| Email | Role | Purpose |
|-------|------|---------|
| test_editor@example.com | Editor | Activity creation |
| test_translator@example.com | Translator | Translation flow |
| test_admin@example.com | Admin | Full access |

### Test Media Assets
| File | Type | Purpose |
|------|------|---------|
| test-image-valid.jpg | Image | Valid upload |
| test-image-large.jpg | Image | Size limit test |
| test-audio-valid.mp3 | Audio | Valid upload |
| test-audio-invalid.wav | Audio | Format rejection |

### Character Limit Test Strings
```javascript
const testStrings = {
  chars_10: "0123456789",
  chars_30: "012345678901234567890123456789",
  chars_35: "01234567890123456789012345678901234",
  chars_38: "01234567890123456789012345678901234567",
  chars_60: "012345678901234567890123456789012345678901234567890123456789",
  chars_80: "01234567890123456789012345678901234567890123456789012345678901234567890123456789",
  chars_98: "01234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567",
  chars_100: "0123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789"
};
```

## Related Documents

- Technical Specification: `docs/tech-spec/language-learning-cms-spec.md`
- Database Schema: `docs/tech-spec/database-schema.sql`
- Full Test Suite: `docs/tech-spec/test-suite-language-learning-cms.md`

## Maintenance

- Update test cases when PRD changes
- Add regression tests for bug fixes
- Review P0 coverage quarterly
- Archive deprecated tests
