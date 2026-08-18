---
paths:
  - "docs/prd/**/*.md"
  - "features/**/*.feature"
  - "**/*.steps.ts"
---

# Cucumber BDD Enforcement Rules

Rules for enforcing Gherkin-first acceptance criteria in AID methodology.

---

## IRON RULE: Gherkin for Acceptance Criteria

**All acceptance criteria in PRD documents MUST be written in Gherkin format.**

This is non-negotiable. Gherkin format ensures acceptance criteria are:
- **Executable** - Can be run as tests
- **Unambiguous** - Given/When/Then structure
- **Traceable** - Linked to PRD requirements
- **Living documentation** - Always up-to-date

### Valid Format

```gherkin
Feature: User Authentication
  Scenario: Successful login
    Given I am on the login page
    When I enter valid credentials
    Then I should see the dashboard
```

### Invalid Formats (Will be rejected)

```markdown
# Checklist format - REJECTED
- [ ] User can log in
- [ ] User sees dashboard after login

# Prose format - REJECTED
When the user enters valid credentials, they should be logged in
and redirected to the dashboard.

# Vague format - REJECTED
Login should work properly.
```

### Violation Response

When PRD acceptance criteria are not in Gherkin format:

```
GHERKIN ENFORCEMENT VIOLATION

Acceptance criteria must be in Gherkin format (Given/When/Then).

Found: [checklist/prose/vague format]
Required: Gherkin feature file format

Please convert to:

  Feature: [Story Title]
    Scenario: [Scenario Name]
      Given [precondition]
      When [action]
      Then [expected outcome]

See `cucumber-bdd` skill for syntax reference.
```

---

## Phase Gate Requirements

### Phase 1 (PRD) Gate - Feature Files

Before advancing from PRD to Tech Spec:

**Requirements:**
- [ ] Every user story has a `.feature` file
- [ ] Feature files are in `features/` directory
- [ ] Each feature has at least 2 scenarios (happy path + error)
- [ ] All scenarios have appropriate @tags
- [ ] Research backing noted in comments

**Verification:**
```bash
# Check feature files exist
ls features/**/*.feature

# Validate Gherkin syntax
npm run cucumber:dry
```

**Violation Response:**
```
PHASE 1 GATE: Cucumber Requirements Not Met

Missing: [list of missing items]

Cannot advance to Phase 2 until:
1. All user stories have .feature files
2. npm run cucumber:dry passes
```

---

### Phase 4 (Development) Gate - Step Definitions

Before advancing from Development to QA:

**Requirements:**
- [ ] Step definitions exist for ALL steps
- [ ] All scenarios pass locally
- [ ] No pending step definitions
- [ ] No @wip tags remaining (unless documented)

**Verification:**
```bash
# Check for undefined steps
npm run cucumber:dry

# Run all tests
npm run cucumber

# Should see: "X scenarios (X passed)"
```

**Violation Response:**
```
PHASE 4 GATE: Step Definitions Incomplete

Undefined steps: [count]
Failing scenarios: [count]

Cannot advance to Phase 5 until:
1. All steps have definitions
2. All scenarios pass
```

---

### Phase 5 (QA & Ship) Gate - Release Certification

Before releasing:

**Requirements:**
- [ ] `npm run cucumber` exits with code 0
- [ ] `npm run test:critical` passes
- [ ] No undefined or pending steps
- [ ] HTML report generated and reviewed
- [ ] No @wip or @skip tags in release

**Verification:**
```bash
# Final verification
npm run cucumber && npm run test:critical && npm run test:bdd

# Check for forbidden tags
grep -r "@wip\|@skip" features/ && echo "BLOCKED: Remove @wip/@skip tags"
```

**Violation Response:**
```
PHASE 5 GATE: Release Not Certified

Failing scenarios: [count]
@critical failures: [count]
Forbidden tags found: [@wip, @skip]

Cannot release until all Cucumber gates pass.
```

---

## Tag Standards

### Required Tags

Every scenario MUST have at least one of these tags:

| Tag | Usage | CI Behavior |
|-----|-------|-------------|
| `@critical` | Must pass for release | Blocks deployment if fails |
| `@smoke` | Quick sanity checks | Runs on every PR |
| `@regression` | Full test coverage | Runs nightly |

### Optional Tags

| Tag | Usage | CI Behavior |
|-----|-------|-------------|
| `@wip` | Work in progress | Excluded from CI |
| `@skip` | Temporarily disabled | Excluded (must document reason) |
| `@manual` | Cannot be automated | Excluded |
| `@security` | Security-related | Runs on security review |
| `@performance` | Performance-related | Runs on performance review |
| `@flaky` | Known flaky tests | Retried automatically |
| `@slow` | Takes >30 seconds | May be excluded from fast feedback |

### Feature Tags

Use feature-specific tags for filtering:
- `@auth`, `@checkout`, `@search`, `@admin`, etc.

---

## Tag Violations

### Missing Required Tag

```
TAG VIOLATION: Scenario has no required tag

Scenario: [name]
Location: [file:line]

Every scenario must have @critical, @smoke, or @regression.
Add appropriate tag based on:
- @critical: Required for release
- @smoke: Quick validation
- @regression: Full coverage
```

### Forbidden Tag in Release

```
TAG VIOLATION: Forbidden tag in release

Found: @wip at features/auth/login.feature:25
Found: @skip at features/checkout/cart.feature:42

Remove @wip and @skip tags, or exclude these scenarios
from the release scope.
```

---

## Enforcement Commands

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `npm run cucumber:dry` | Validate Gherkin syntax | Phase 1 gate, before commit |
| `npm run cucumber` | Execute all scenarios | Phase 4 gate, before PR |
| `npm run test:critical` | Run @critical only | Phase 5 gate, before release |
| `npm run test:smoke` | Run @smoke only | Quick validation |
| `npm run test:bdd` | Full run + HTML report | Release certification |

---

## Integration with Phase Enforcement

This rule integrates with `.claude/rules/general/phase-gates.md`:

```
Phase 0 ──► Phase 1 ──► Phase 2 ──► Phase 3 ──► Phase 4 ──► Phase 5
Discovery     PRD      Tech Spec   Impl Plan     Dev       QA & Ship
            [.feature]            [plan steps] [step defs] [all pass]
```

| Phase | Cucumber Artifact | Validation |
|-------|-------------------|------------|
| 1 PRD | `.feature` files | `cucumber:dry` passes |
| 3 Impl Plan | Step definition plan | Tasks include step implementation |
| 4 Development | Step definitions | `cucumber` passes |
| 5 QA & Ship | All scenarios pass | `test:critical` + `test:bdd` |

---

## Related Documentation

- `skills/cucumber-bdd/SKILL.md` - Cucumber skill reference
- `skills/aid-prd/SKILL.md` - PRD with Gherkin requirements
- `skills/test-driven/SKILL.md` - TDD with Cucumber integration
- `skills/aid-qa-ship/SKILL.md` - QA verification with Cucumber
