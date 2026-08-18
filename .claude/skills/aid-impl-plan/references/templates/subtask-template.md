# Sub-task Template: QA Gate

## Purpose

This template defines the structure for QA Gate sub-tasks attached to each Task.
Sub-tasks contain ONLY acceptance criteria - no technical or business context.

---

## Template

```markdown
# QA Gate: {TASK_ID}

## Task Reference
- **Task:** {TASK_ID} - {Task Name}
- **Story:** {STORY_ID} - {Story Name}
- **Criteria File:** `.aid/qa/{TASK_ID}.yaml`

---

## Success Criteria

### MUST Achieve
- [ ] {Criterion 1 - specific, testable, no implementation details}
- [ ] {Criterion 2 - measurable outcome}
- [ ] {Criterion 3 - verifiable behavior}

### MUST NOT
- [ ] {Anti-pattern 1 - what the code should NOT do}
- [ ] {Anti-pattern 2 - security/performance constraint}

### NOT INCLUDED (Scope Boundary)
- {Feature explicitly out of scope} → {Reference to other task if deferred}
- {Behavior not expected in this task}

### Best Practices
- [ ] {Quality standard 1 - e.g., "Unit tests exist"}
- [ ] {Quality standard 2 - e.g., "No console.log statements"}

---

## QA Process

1. Criteria file: `.aid/qa/{TASK_ID}.yaml`
2. Review triggered automatically on task completion
3. QA sub-agent validates against criteria above
4. Must pass ALL criteria before proceeding

## Status
- [ ] Pending QA review
- [ ] Passed
- [ ] Failed (see `.aid/qa/{TASK_ID}-review-N.json`)
```

---

## Example: Filled Template

```markdown
# QA Gate: AUTH-123

## Task Reference
- **Task:** AUTH-123 - Implement email validation on login form
- **Story:** AUTH-100 - Clear Validation Feedback
- **Criteria File:** `.aid/qa/AUTH-123.yaml`

---

## Success Criteria

### MUST Achieve
- [ ] Email format is validated before form can be submitted
- [ ] Error message displays directly below the invalid input field
- [ ] Error message clears automatically when user corrects the input
- [ ] Form submission is blocked when email validation fails

### MUST NOT
- [ ] Must NOT allow form submission with invalid email format
- [ ] Must NOT log email values to console or any log files
- [ ] Must NOT make API calls before client-side validation passes
- [ ] Must NOT expose validation logic details in error messages

### NOT INCLUDED (Scope Boundary)
- Password validation → AUTH-124
- "Remember me" checkbox functionality → Out of MVP scope
- SSO/OAuth integration → Future sprint

### Best Practices
- [ ] Unit tests exist for valid and invalid email scenarios
- [ ] Error messages are externalized (i18n-ready)
- [ ] Accessible error announcements for screen readers

---

## QA Process

1. Criteria file: `.aid/qa/AUTH-123.yaml`
2. Review triggered automatically on task completion
3. QA sub-agent validates against criteria above
4. Must pass ALL criteria before proceeding

## Status
- [x] Pending QA review
- [ ] Passed
- [ ] Failed (see `.aid/qa/AUTH-123-review-N.json`)
```

---

## Iron Rules for Sub-tasks

### ALLOWED Content
- Success criteria (WHAT to verify)
- Negative criteria (WHAT must not happen)
- Scope boundaries (WHAT is not included)
- Best practices (quality standards)

### FORBIDDEN Content (Never include)
- Technical implementation details ("Use Zod", "Debounce 300ms")
- Architecture reasoning ("Because the API...")
- Business justification ("Users want...")
- Code patterns or examples
- File paths or component names

### Validation Check
Before creating a sub-task, verify:
- [ ] No technical terms (API, schema, component, etc.)
- [ ] No implementation guidance (how to build)
- [ ] No business context (why users need it)
- [ ] All criteria are testable without knowing HOW code was written

---

## Naming Convention

```
QA Gate: {TASK_ID}
```

Examples:
- `QA Gate: AUTH-123`
- `QA Gate: E1-T05`
- `QA Gate: PROJ-456`

---

## Linking in Jira

When creating in Jira:
1. Create as Sub-task type
2. Link to parent Task
3. Set minimal description: "See criteria file: `.aid/qa/{TASK_ID}.yaml`"
4. Full criteria lives in `.aid/qa/` directory (not in Jira)

This prevents context leakage - QA agent reads `.aid/qa/` file, not Jira description.
