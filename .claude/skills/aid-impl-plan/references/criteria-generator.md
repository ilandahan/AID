# Criteria Generator

## Purpose

This document provides the prompt template and process for auto-generating
QA acceptance criteria from the consolidated spec during Phase 3c.

---

## When to Use

Phase 3c: Success Criteria Generation
- After: 3b Task Breakdown (tasks defined)
- Before: 3d Jira Population

---

## Generation Process

### Step 1: Gather Input Context

For each task, collect:

```yaml
task_input:
  task_id: "{from breakdown}"
  task_name: "{from breakdown}"

  # From Epic (business context - sanitized)
  epic:
    goal: "{Epic business goal}"

  # From Story (product context - sanitized)
  story:
    user_value: "{Story user value}"
    acceptance_criteria:
      - "{Story AC 1}"
      - "{Story AC 2}"

  # From Task (scope only - NOT implementation details)
  task:
    scope_includes: "{what this task covers}"
    scope_excludes: "{what this task does NOT cover}"
    related_tasks: "{other tasks that handle deferred items}"
```

### Step 2: Apply Generation Prompt

```markdown
# Criteria Generation Prompt

You are generating QA acceptance criteria for task: {task_id}

## Context (Read-Only)

### Business Goal (from Epic)
{epic.goal}

### User Value (from Story)
{story.user_value}

### Story Acceptance Criteria
{story.acceptance_criteria}

### Task Scope
- Includes: {task.scope_includes}
- Excludes: {task.scope_excludes}
- Related: {task.related_tasks}

---

## Generate Criteria

### MUST Achieve (3-5 items)
Extract from Story acceptance criteria:
- Which criteria apply specifically to THIS task?
- What user-facing behavior must this task enable?
- What is the minimum viable outcome?

Rules:
- Be specific and testable
- No implementation details (no "use X library")
- Focus on WHAT, not HOW
- Each criterion should be independently verifiable

### MUST NOT (2-4 items)
Derive negative criteria:
- What should this code NEVER do?
- What security violations must be prevented?
- What performance anti-patterns to avoid?
- What data should never be exposed?

Rules:
- Focus on constraints, not implementation
- Think about edge cases and failure modes
- Consider security, privacy, and performance

### NOT INCLUDED (2-4 items)
Define scope boundaries:
- What features are explicitly OUT of scope?
- What related functionality belongs to other tasks?
- What is deferred to future work?

Rules:
- Reference specific task IDs for deferred work
- Be explicit to prevent scope creep
- Clear boundaries help QA know what NOT to check

### Best Practices (2-3 items)
Apply project standards:
- What test coverage is expected?
- What code quality standards apply?
- What accessibility requirements exist?

Rules:
- Reference project coding standards
- Keep to measurable/verifiable items
- Don't include implementation guidance

---

## Output Format

Generate a `.aid/qa/{task_id}.yaml` file with this structure:

```yaml
schema_version: "1.0"
task_id: "{task_id}"
task_name: "{task_name}"
generated_at: "{ISO timestamp}"
generated_from: "consolidated-spec.md"

business_context:
  epic_goal: "{sanitized - no tech details}"
  user_value: "{sanitized - no tech details}"
  acceptance_criteria:
    - "{from story}"

criteria:
  must_achieve:
    - "{criterion 1}"
    - "{criterion 2}"

  must_not:
    - "{anti-pattern 1}"
    - "{anti-pattern 2}"

  not_included:
    - "{out of scope 1} (see {TASK_ID})"
    - "{out of scope 2}"

  best_practices:
    - "{standard 1}"
    - "{standard 2}"

files_to_review: []
review_history: []
```

---

## CRITICAL: Sanitization Rules

Before including ANY text in the criteria file:

### Remove Technical Terms
- ❌ "Use Zod for validation" → ✅ "Input is validated"
- ❌ "Call the /api/users endpoint" → ✅ "User data is retrieved"
- ❌ "Store in PostgreSQL" → ✅ "Data is persisted"

### Remove Implementation Details
- ❌ "Debounce by 300ms" → ✅ "Input doesn't trigger excessive processing"
- ❌ "Use React Hook Form" → ✅ "Form handles user input"
- ❌ "Return HTTP 422" → ✅ "Validation errors are communicated"

### Keep User-Facing Language
- ✅ "Error message displays below the field"
- ✅ "User can correct their input"
- ✅ "Form cannot be submitted until valid"
```

---

## Step 3: Validation Check

Before saving, verify criteria passes iron rules:

```yaml
validation_checklist:
  - [ ] No technical terms (API, schema, component, database)
  - [ ] No library names (Zod, React, PostgreSQL)
  - [ ] No implementation guidance (use X, implement Y)
  - [ ] No business justification (because users want)
  - [ ] All criteria are testable
  - [ ] All criteria are specific (not vague)
  - [ ] Scope boundaries reference other tasks by ID
```

---

## Step 4: Batch Review Checkpoint

After generating ALL criteria files:

```
Generated criteria for {N} tasks:

Sample (first 3):
─────────────────────────────────────
Task: AUTH-123 - Email Validation
  ✅ must_achieve: 4 criteria
  ❌ must_not: 3 criteria
  🚫 not_included: 2 boundaries
  ⭐ best_practices: 2 standards

Task: AUTH-124 - Password Validation
  ✅ must_achieve: 5 criteria
  ❌ must_not: 4 criteria
  🚫 not_included: 1 boundary
  ⭐ best_practices: 2 standards

Task: AUTH-125 - Form Submission
  ✅ must_achieve: 3 criteria
  ❌ must_not: 2 criteria
  🚫 not_included: 3 boundaries
  ⭐ best_practices: 3 standards
─────────────────────────────────────

Review all criteria before proceeding?
[View All] [Approve] [Edit]
```

---

## Common Patterns

### For Form/Input Tasks

```yaml
must_achieve:
  - "Input is validated before submission"
  - "Error feedback displays near the invalid field"
  - "Error clears when user corrects input"
  - "Form cannot be submitted while invalid"

must_not:
  - "Must NOT submit invalid data"
  - "Must NOT expose sensitive data in logs"
  - "Must NOT trigger validation excessively"

best_practices:
  - "Unit tests cover valid and invalid scenarios"
  - "Error messages are accessible (screen reader compatible)"
```

### For API/Data Tasks

```yaml
must_achieve:
  - "Data is retrieved successfully"
  - "Appropriate feedback for empty/missing data"
  - "Loading state is indicated"
  - "Errors are handled gracefully"

must_not:
  - "Must NOT expose internal error details to users"
  - "Must NOT cache sensitive data inappropriately"
  - "Must NOT make redundant requests"

best_practices:
  - "Loading and error states are tested"
  - "Empty state is handled"
```

### For Display/UI Tasks

```yaml
must_achieve:
  - "Content displays correctly"
  - "Layout adapts to different screen sizes"
  - "Interactive elements are accessible"
  - "State changes are reflected visually"

must_not:
  - "Must NOT break layout on edge cases"
  - "Must NOT hide important information"
  - "Must NOT create accessibility barriers"

best_practices:
  - "Visual regression tests exist"
  - "Responsive breakpoints are tested"
```

---

## Output Location

All generated criteria files go to:

```
.aid/qa/
├── {TASK-ID-1}.yaml
├── {TASK-ID-2}.yaml
├── {TASK-ID-3}.yaml
└── ...
```

These files are:
- NOT synced to Jira (intentional isolation)
- Read by QA sub-agent during Phase 4
- Updated with review history after each QA cycle
