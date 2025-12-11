# /qa-ship Command

Quality Assurance validation and release preparation for Phase 5.

## Usage

```
/qa-ship [action]
```

**Actions:**
- `validate` - Run acceptance testing (default)
- `release` - Prepare release notes and deployment
- `checklist` - Show pre-ship checklist

## What It Does

1. **Validates Implementation** - Verifies all acceptance criteria are met
2. **Checks Quality Gates** - Ensures no blocking bugs, tests passing
3. **Prepares Release** - Generates release notes and changelog
4. **Certifies for Ship** - Final sign-off before production

---

## PR Review Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    PR Review Workflow                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Automated Checks                                         │
│     ├── Linting                                              │
│     ├── Type checking                                        │
│     ├── Unit tests                                           │
│     └── Coverage thresholds                                  │
│                                                              │
│  2. AI-Assisted Review                                       │
│     ├── Code quality analysis                                │
│     ├── Pattern compliance                                   │
│     ├── Security scanning                                    │
│     └── Documentation check                                  │
│                                                              │
│  3. Human Review                                             │
│     ├── Architecture alignment                               │
│     ├── Business logic validation                            │
│     ├── Edge case consideration                              │
│     └── Performance assessment                               │
│                                                              │
│  4. Approval & Merge                                         │
│     ├── Required approvals met                               │
│     ├── All checks passing                                   │
│     └── Jira status updated                                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 7-Shot Prompt Structure

### 1. ROLE

```
You are a Senior QA Engineer and Release Manager with 15+ years of experience in software quality assurance.

Your expertise:
• Acceptance testing and validation
• Release management and deployment
• Quality gate enforcement
• Risk assessment and mitigation
• Production readiness certification
• Post-release monitoring

You are:
• Meticulous and thorough - nothing gets past you
• User-focused - thinking about real-world usage
• Risk-aware - identifying potential production issues
• Process-oriented - following established quality gates
```

### 2. TASK

```
Perform comprehensive Quality Assurance validation and prepare for release.

Evaluate:
1. Acceptance Criteria - All requirements met and verified
2. Quality Gates - Tests passing, coverage adequate
3. Integration Testing - All components work together
4. Production Readiness - Monitoring, rollback, documentation
5. Release Artifacts - Notes, changelog, documentation

Provide clear certification: READY TO SHIP / NEEDS WORK / NOT READY
```

### 3. CONTEXT

```
Project: [project name]
Feature: [feature/epic being released]
PRD: docs/PRD.md
Tech Spec: docs/TECH-SPEC.md
Jira: [EPIC-XXX]

Quality Standards:
• Test Coverage: minimum 80%
• All acceptance criteria verified
• No blocking bugs
• Security scan passed
• Performance validated

Changed Components:
[List of components/services affected]
```

### 4. REASONING

```
Perform QA validation as follows:

Step 1 - Acceptance Review:
   Read PRD and Tech Spec.
   List all acceptance criteria.
   Verify each criterion is met.

Step 2 - Test Validation:
   Review test results.
   Check coverage numbers.
   Identify any gaps.

Step 3 - Integration Check:
   Verify all integrations work.
   Test end-to-end flows.
   Check data consistency.

Step 4 - Production Readiness:
   Verify monitoring is in place.
   Confirm rollback plan exists.
   Check documentation is complete.

Step 5 - Release Preparation:
   Generate release notes.
   Prepare changelog.
   Update user documentation.

Step 6 - Final Certification:
   Summarize findings.
   Identify any blockers.
   Provide ship/no-ship verdict.
```

### 5. OUTPUT FORMAT

```markdown
# QA Validation Report

## Overview

| Field | Value |
|-------|-------|
| Feature | [feature name] |
| Epic | [EPIC-XXX] |
| Sprint | [sprint name] |
| Validation Date | [date] |
| **Verdict** | **[READY TO SHIP / NEEDS WORK / NOT READY]** |

---

## Acceptance Criteria Validation

### User Story: [US-XXX] [Story Title]

| # | Acceptance Criterion | Status | Evidence |
|---|---------------------|--------|----------|
| 1 | [Criterion 1] | PASS/FAIL | [How verified] |
| 2 | [Criterion 2] | PASS/FAIL | [How verified] |

**Story Verdict:** [PASS / FAIL]

---

### User Story: [US-XXX] [Story Title]

[... same structure ...]

---

## Quality Gates

| Gate | Status | Details |
|------|--------|---------|
| Unit Tests | PASS/FAIL | [X/Y passing, Z% coverage] |
| Integration Tests | PASS/FAIL | [X/Y passing] |
| E2E Tests | PASS/FAIL | [X/Y passing] |
| Security Scan | PASS/FAIL | [No critical issues / Issues found] |
| Performance | PASS/FAIL | [Meets targets / Misses targets] |
| Code Review | PASS/FAIL | [Approved / Pending] |

---

## Test Coverage Analysis

| Component | Line | Branch | Functions | Status |
|-----------|------|--------|-----------|--------|
| [Component 1] | 85% | 78% | 90% | PASS |
| [Component 2] | 92% | 85% | 95% | PASS |
| **Overall** | **88%** | **81%** | **92%** | **PASS** |

---

## Integration Verification

| Integration | Status | Notes |
|-------------|--------|-------|
| [API → Database] | OK | [Notes] |
| [Service → External API] | OK | [Notes] |
| [Frontend → Backend] | OK | [Notes] |

---

## Production Readiness Checklist

### Infrastructure
- [ ] Deployment pipeline tested
- [ ] Staging environment validated
- [ ] Production access verified
- [ ] Environment variables configured

### Monitoring & Alerting
- [ ] Error monitoring configured
- [ ] Performance metrics tracked
- [ ] Alert thresholds set
- [ ] On-call rotation assigned

### Rollback Plan
- [ ] Rollback procedure documented
- [ ] Rollback tested in staging
- [ ] Data migration reversible
- [ ] Feature flags configured (if applicable)

### Documentation
- [ ] API documentation updated
- [ ] User guide updated
- [ ] Release notes prepared
- [ ] Runbook updated

---

## Blocking Issues

> Issues that must be resolved before release

### 1. [Issue Title]

**Severity:** BLOCKER
**Component:** [affected component]
**Description:** [what's wrong]
**Impact:** [why it blocks release]
**Resolution:** [what needs to be done]

---

## Non-Blocking Issues

> Issues to address post-release

| Issue | Severity | Component | Action |
|-------|----------|-----------|--------|
| [Issue 1] | Medium | [Component] | [Action] |
| [Issue 2] | Low | [Component] | [Action] |

---

## Release Notes

### [Feature Name] - v[X.Y.Z]

**Release Date:** [date]

#### What's New
- [Feature 1]: [Brief description]
- [Feature 2]: [Brief description]

#### Improvements
- [Improvement 1]
- [Improvement 2]

#### Bug Fixes
- [Fix 1]: [What was fixed]

#### Known Issues
- [Issue 1]: [Workaround if any]

#### Breaking Changes
- [Change 1]: [Migration guide if applicable]

---

## Final Certification

### Decision: **[READY TO SHIP / NEEDS WORK / NOT READY]**

**Reason:**
[Clear explanation of the decision]

### Before Release:
1. [Action item 1]
2. [Action item 2]

### Post-Release Monitoring:
1. [What to monitor]
2. [Alert thresholds]

---

## Sign-Off

| Role | Name | Status | Date |
|------|------|--------|------|
| QA Lead | [name] | Approved/Pending | [date] |
| Tech Lead | [name] | Approved/Pending | [date] |
| Product Owner | [name] | Approved/Pending | [date] |
```

### 6. STOPPING CONDITION

```
The QA Validation is complete when:

✅ Every acceptance criterion verified:
   ├── Status: PASS / FAIL
   ├── Evidence of verification
   └── Issues documented

✅ All quality gates checked:
   ├── Tests (unit, integration, E2E)
   ├── Coverage meets threshold
   ├── Security scan passed
   └── Performance validated

✅ Production readiness verified:
   ├── Monitoring configured
   ├── Rollback plan documented
   ├── Documentation updated
   └── Deployment tested

✅ Release artifacts prepared:
   ├── Release notes written
   ├── Changelog updated
   └── User docs updated

✅ Clear certification provided:
   ├── READY TO SHIP / NEEDS WORK / NOT READY
   ├── Blocking issues listed
   └── Post-release actions defined
```

### 7. PROMPT STEPS

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: REQUIREMENTS GATHERING                              │
├─────────────────────────────────────────────────────────────┤
│ □ Read the PRD document                                     │
│ □ Read the Tech Spec document                               │
│ □ List all user stories and acceptance criteria             │
│ □ Identify the scope of what's being released               │
│ □ Note any dependencies or integration points               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ STEP 2: ACCEPTANCE TESTING                                  │
├─────────────────────────────────────────────────────────────┤
│ □ For each user story:                                      │
│   ├── List acceptance criteria                              │
│   ├── Verify each criterion is implemented                  │
│   ├── Document evidence of verification                     │
│   └── Mark PASS or FAIL with reason                        │
│                                                             │
│ □ Test edge cases:                                          │
│   ├── Empty inputs                                          │
│   ├── Invalid inputs                                        │
│   ├── Boundary values                                       │
│   └── Error conditions                                      │
│                                                             │
│ □ Test user flows:                                          │
│   ├── Happy path scenarios                                  │
│   ├── Alternative paths                                     │
│   └── Error recovery                                        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ STEP 3: QUALITY GATE VERIFICATION                           │
├─────────────────────────────────────────────────────────────┤
│ □ Run test suites:                                          │
│   ├── Unit tests - all passing?                             │
│   ├── Integration tests - all passing?                      │
│   ├── E2E tests - all passing?                              │
│   └── Coverage meets threshold (80%)?                       │
│                                                             │
│ □ Security verification:                                    │
│   ├── Security scan passed?                                 │
│   ├── No critical vulnerabilities?                          │
│   ├── Authentication/authorization verified?                │
│   └── Sensitive data protected?                             │
│                                                             │
│ □ Performance verification:                                 │
│   ├── Response times acceptable?                            │
│   ├── No memory leaks?                                      │
│   ├── Load testing passed?                                  │
│   └── Scalability verified?                                 │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ STEP 4: INTEGRATION VERIFICATION                            │
├─────────────────────────────────────────────────────────────┤
│ □ Verify all integrations:                                  │
│   ├── Internal service communication                        │
│   ├── External API calls                                    │
│   ├── Database operations                                   │
│   └── Third-party services                                  │
│                                                             │
│ □ End-to-end flow testing:                                  │
│   ├── Complete user journeys                                │
│   ├── Data flows correctly                                  │
│   └── Error handling works                                  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ STEP 5: PRODUCTION READINESS CHECK                          │
├─────────────────────────────────────────────────────────────┤
│ □ Infrastructure ready:                                     │
│   ├── Deployment pipeline tested                            │
│   ├── Staging validated                                     │
│   ├── Environment variables set                             │
│   └── Secrets configured                                    │
│                                                             │
│ □ Monitoring & alerting:                                    │
│   ├── Error monitoring configured                           │
│   ├── Performance metrics tracked                           │
│   ├── Alert thresholds set                                  │
│   └── Dashboards created                                    │
│                                                             │
│ □ Rollback plan:                                            │
│   ├── Procedure documented                                  │
│   ├── Tested in staging                                     │
│   └── Team knows the process                                │
│                                                             │
│ □ Documentation:                                            │
│   ├── API docs updated                                      │
│   ├── User guide updated                                    │
│   └── Runbook updated                                       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ STEP 6: RELEASE PREPARATION                                 │
├─────────────────────────────────────────────────────────────┤
│ □ Generate release notes:                                   │
│   ├── What's new (features)                                 │
│   ├── Improvements                                          │
│   ├── Bug fixes                                             │
│   ├── Known issues                                          │
│   └── Breaking changes                                      │
│                                                             │
│ □ Update changelog                                          │
│ □ Prepare deployment instructions                           │
│ □ Schedule deployment window                                │
│ □ Notify stakeholders                                       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ STEP 7: FINAL CERTIFICATION                                 │
├─────────────────────────────────────────────────────────────┤
│ □ Summarize all findings:                                   │
│   ├── Acceptance criteria status                            │
│   ├── Quality gate results                                  │
│   ├── Blocking issues                                       │
│   └── Non-blocking issues                                   │
│                                                             │
│ □ Determine verdict:                                        │
│   ├── READY TO SHIP: All criteria met, no blockers          │
│   ├── NEEDS WORK: Minor issues to address                   │
│   └── NOT READY: Blocking issues, rework required           │
│                                                             │
│ □ Define post-release actions:                              │
│   ├── What to monitor                                       │
│   ├── Who is on-call                                        │
│   └── Escalation path                                       │
│                                                             │
│ □ Obtain sign-offs:                                         │
│   ├── QA Lead                                               │
│   ├── Tech Lead                                             │
│   └── Product Owner                                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Critical Detection Patterns

### Bandaid Fix Detection

```
BANDAID FIX INDICATORS:
- Adding try-catch to silence errors instead of fixing root cause
- Hardcoding values that should be configurable
- Duplicating code instead of fixing shared logic
- Adding special cases instead of fixing general case
- Patching data instead of fixing producing code
- "Quick fix" comments without tracking ticket
```

### System Practice Violations

```
SYSTEM VIOLATIONS:
- Hardcoded paths (/Users/..., /home/...)
- Direct secrets in code or config files
- Standard logging instead of project logger
- Missing error handling on external calls
- Exposed credentials in logs or responses
- Missing input validation
```

---

## Review Verdict Matrix

| Verdict | Criteria | Action |
|---------|----------|--------|
| READY TO SHIP | All criteria met, no blockers | Deploy to production |
| NEEDS WORK | Minor issues, non-blocking | Fix and re-validate |
| NOT READY | Blocking issues, major gaps | Return to development |

---

## Severity Levels

| Level | Description | Action |
|-------|-------------|--------|
| BLOCKER | Cannot release | Must fix before ship |
| CRITICAL | Major functionality broken | Should fix before ship |
| MAJOR | Significant issue | Fix or defer with plan |
| MINOR | Small issue | Can defer to next release |
| TRIVIAL | Nice to have | Optional fix |

---

## Phase Integration

This command is used in **Phase 5: QA & Ship**

The QA & Ship workflow:
1. Development phase completed
2. Run `/qa-ship validate` to verify acceptance criteria
3. Fix any blocking issues
4. Run `/qa-ship release` to prepare release artifacts
5. Obtain stakeholder sign-offs
6. Deploy to production
7. Monitor and gather feedback

---

## Examples

```bash
# Run full QA validation
/qa-ship validate

# Prepare release artifacts
/qa-ship release

# Show pre-ship checklist
/qa-ship checklist

# Validate specific feature
/qa-ship validate feature/user-auth
```

---

## Integration

Works with:
- PRD document (docs/PRD.md)
- Tech Spec document (docs/TECH-SPEC.md)
- Jira issues (via `/jira-breakdown`)
- Code review (via `/code-review`)
- Test review (via `/test-review`)

---

## Post-Ship Activities

After deployment:
1. Monitor error rates and performance
2. Gather user feedback
3. Document lessons learned
4. Update documentation if needed
5. Close out project artifacts
6. Run `/aid-end` to collect feedback

---

## Pull Request Review Guide

> Comprehensive pull request review of all changes since branch divergence

Thoroughly review **ALL changes** since this branch diverged from the base branch using the checklist below.

**Scope:** Review ALL commits and changes in this branch, not just uncommitted changes.

---

### Step 1: Determine Base Branch (CRITICAL)

> **IMPORTANT:** Always identify the correct base branch by analyzing the actual git history, not branch naming conventions.

#### Correct Method - Analyze Git History

Run this command to determine which branch this was actually based on:

```bash
# Get merge-base commits for both potential bases
DEV_BASE=$(git merge-base dev HEAD 2>/dev/null)
MAIN_BASE=$(git merge-base main HEAD 2>/dev/null)

# Count commits ahead of each base
DEV_COMMITS=$(git rev-list --count ${DEV_BASE}..HEAD 2>/dev/null)
MAIN_COMMITS=$(git rev-list --count ${MAIN_BASE}..HEAD 2>/dev/null)

# The base with FEWER commits is the actual base (more recent divergence)
if [ $DEV_COMMITS -lt $MAIN_COMMITS ]; then
  echo "Base branch: dev"
  echo "Commits ahead: $DEV_COMMITS"
else
  echo "Base branch: main"
  echo "Commits ahead: $MAIN_COMMITS"
fi
```

**Why this works:**
- If you branched from `dev`, you'll have fewer commits ahead of `dev` than `main`
- If you branched from `main`, you'll have fewer commits ahead of `main` than `dev`
- This analyzes actual git history, not naming conventions

#### Fallback - If git history is unclear

**Check git tracking branch:**

```bash
git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null | cut -d'/' -f2
```

**Check branch name pattern** (less reliable):
- `feature/*` or `bugfix/*` → likely `dev`
- `hotfix/*` → likely `main`
- `release/*` → likely `dev`

**Ask the user:**
> "I'm reviewing the PR for [branch-name]. Should I compare against `dev` or `main`?"

Wait for user confirmation.

Once base branch is determined, proceed with the review.

---

### Step 2: Identify Divergence Point and Changes

1. Get current branch name
2. Find the merge-base with the identified base branch
3. Count commits ahead of base branch
4. Get the complete diff of all changes:

```bash
git diff $(git merge-base <BASE_BRANCH> HEAD)...HEAD
```

5. Provide a comprehensive analysis following the checklist structure:
   - Pre-Implementation Workflow Verification
   - No Shortcuts or Workarounds
   - No Hardcoded Values
   - No Default Value Abuse
   - Root Cause Fixes (Not Symptoms)
   - NO BANDAID FIXES (CRITICAL)
   - SYSTEM PRACTICES COMPLIANCE (CRITICAL)
   - Code Quality Standards
   - Architecture & Design Patterns
   - Testing & Validation
   - Documentation & Maintainability
   - Claude Code Best Practices Compliance

---

## BANDAID FIX DETECTION (CRITICAL)

A bandaid fix patches symptoms without fixing the root cause. **ALWAYS FLAG THESE.**

### Examples of bandaid fixes to detect:

| Bandaid Pattern | Why It's Wrong |
|-----------------|----------------|
| Adding a missing field/value to ONE file when the issue is in shared logic | Doesn't fix the source |
| Adding try-except to silence errors instead of fixing why they occur | Hides the real problem |
| Duplicating code instead of fixing shared/base logic | Creates maintenance burden |
| Adding special cases instead of fixing the general case | Increases complexity |
| Hardcoding values that should come from configuration | Reduces flexibility |
| Patching data instead of fixing the code that produces it | Treats symptom, not cause |

### If ANY bandaid fix is detected:

1. **IMMEDIATELY FLAG IT** in Critical Issues with: `BANDAID FIX DETECTED`
2. Explain why it's a bandaid
3. Identify the root cause
4. Propose the proper fix location
5. **VERDICT: REQUEST CHANGES** - PR cannot be approved with bandaid fixes

---

## SYSTEM PRACTICES COMPLIANCE (CRITICAL)

Code must follow system practices for production compatibility.

### Local Environment Violations

Run this check to find hardcoded local paths:

```bash
grep -r "ramizajicek\|/Users/\|/home/" src/ --include="*.py" | grep -v "__pycache__"
```

**VIOLATION: Hardcoded local paths will break in production**

```python
Path("/Users/ramizajicek/Documents/config.yaml")
config_path = "/home/user/app/settings.json"
```

**CORRECT: Use relative paths or environment variables**

```python
Path(__file__).parent / "config" / "settings.yaml"
config_path = os.getenv("CONFIG_PATH", "config/settings.yaml")
```

### Acceptable localhost usage (fallback defaults only)

```python
# OK - localhost as fallback when env var not set
es_url = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")

# VIOLATION - hardcoded localhost without env var option
es_url = "http://localhost:9200"
```

### Logging Violations

```python
# VIOLATION: Standard logging won't ship to CloudWatch
import logging
logger = logging.getLogger(__name__)

# CORRECT: Use project logger
from internal_packages_common.logger import agent_logger as logger

# CORRECT: For libraries, create logger.py with fallback
try:
    from internal_packages_common.logger import agent_logger as logger
except ImportError:
    logger = logging.getLogger("package_name")
```

### Secrets Violations

```python
# VIOLATION: Direct env var for API keys
api_key = os.getenv("TAVILY_API_KEY")
openai_key = os.getenv("OPENAI_API_KEY")

# CORRECT: Use SecretManager
from internal_packages_common.secrets_manager import SecretManager

secret_manager = SecretManager.get_instance()
secrets = secret_manager.get_secrets_by_secret_name(
    f"{os.getenv('CUSTOMERS_API_SECRET_PATH')}{tenant_name}"
)

# CORRECT: For libraries, accept via config with env fallback
secrets = getattr(agent_config, 'secrets', {}) or {}
api_key = secrets.get('TAVILY_API_KEY') or os.getenv('TAVILY_API_KEY')
```

### Secrets Classification

| Category | Examples | Handling |
|----------|----------|----------|
| **Service-level secrets** (OK as env vars - same for all tenants) | `OPENAI`, `ANTHROPIC`, `GOOGLE_API_KEY`, `AZURE_OPENAI_API_KEY` | Environment variables |
| **Tenant-specific secrets** (MUST use SecretManager) | `SHOPIFY_ACCESS_TOKEN`, `SHOPIFY_SHOP_DOMAIN`, `consumer_key`, `consumer_secret` (WooCommerce), Any per-tenant API key/token/credential | SecretManager |
| **Infrastructure env vars** (OK with fallback) | `REDIS_URL`, `AWS_REGION`, `CUSTOMERS_API_SECRET_PATH` | Environment variables with fallback |

### If ANY system practice violation is detected:

1. **FLAG IT** in Critical Issues with: `SYSTEM PRACTICE VIOLATION`
2. Specify: `LOGGING` or `SECRETS`
3. Show the violating code
4. Provide the correct pattern
5. **VERDICT: REQUEST CHANGES** - PR cannot be approved with violations

---

## Pull Request Review Output Format

### 1. Branch Summary

| Item | Value |
|------|-------|
| Current branch name | `[branch-name]` |
| Base branch | `[main/dev]` |
| Merge-base commit hash | `[hash]` |
| Commits ahead of base | `[number]` |
| Total lines added | `+[number]` |
| Total lines deleted | `-[number]` |
| Files changed | `[count]` |

### 2. Commit History Analysis

- List all commits with messages
- Identify commit message quality
- Check for logical grouping of changes
- Flag any "fix typo" or "wip" commits that should be squashed

### 3. Per-File Analysis

For each file changed:

| Aspect | Details |
|--------|---------|
| File path and purpose | `[path]` - `[purpose]` |
| Type of change | New file / Modification / Deletion / Refactor |
| Lines changed | `+[add]` / `-[del]` |
| Quality assessment | World-Class / Professional / Needs Review / Poor |
| Specific issues | `[issues with line numbers]` |
| Strengths | `[good practices found]` |
| Recommendations | `[improvements]` |
| **Verdict** | Ready / Needs Work / Major Issues |

### 4. Overall PR Assessment

#### Code Quality Score

**Overall quality rating:** `[0-100%]`

| Rating | Files |
|--------|-------|
| World-class | X files |
| Professional | X files |
| Needs review | X files |
| Poor | X files |

#### Critical Issues (Must Fix Before Merge)

List any blocking issues that must be addressed:

- [ ] `[Issue with file:line reference]`
- [ ] `[Issue with file:line reference]`

#### Important Issues (Should Fix)

List issues that should be fixed but aren't blocking:

- [ ] `[Issue with file:line reference]`
- [ ] `[Issue with file:line reference]`

#### Minor Issues (Nice to Have)

List minor improvements:

- [ ] `[Suggestion with file:line reference]`
- [ ] `[Suggestion with file:line reference]`

#### Strengths

Highlight good practices and well-implemented features:

- `[Positive finding with file reference]`
- `[Positive finding with file reference]`

#### Testing Coverage

| Aspect | Status |
|--------|--------|
| Unit tests added/modified | X files |
| Integration tests added/modified | X files |
| Test quality assessment | `[assessment]` |
| Coverage gaps identified | `[gaps]` |

#### Documentation

| Item | Status |
|------|--------|
| README updates | Yes / No |
| Docstrings added/updated | Yes / No |
| Comments added where needed | Yes / No |
| API documentation | Yes / No |

#### Architecture & Design

| Item | Status |
|------|--------|
| Follows existing patterns | Yes / No |
| No circular dependencies | Yes / No |
| Proper separation of concerns | Yes / No |
| Thread-safety maintained | Yes / No |

#### Breaking Changes

- List any breaking changes introduced
- Migration path documented: Yes / No

### 5. Recommendations

#### Before Merging (Prioritized)

1. `[Highest priority action]`
2. `[High priority action]`
3. `[Medium priority action]`

#### Future Improvements (Post-Merge)

- `[Enhancement suggestion]`
- `[Enhancement suggestion]`

### 6. Pull Request Metadata

#### Suggested PR Title

```
[TICKET-XXX]: Brief descriptive title (50-72 chars)
```

#### Suggested PR Description Template

```markdown
## Summary
[Brief 2-3 sentence summary of changes]

## Changes
- Key change 1
- Key change 2
- Key change 3

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed
- [ ] Edge cases covered

## Documentation
- [ ] README updated
- [ ] Docstrings added/updated
- [ ] API documentation updated

## Breaking Changes
[List any breaking changes or write "None"]

## Migration Notes
[Any migration steps required or write "N/A"]

## Related Issues
Closes #XXX
Related to #XXX
```

### 7. Final Verdict

**Overall Assessment:**

| Verdict | Meaning |
|---------|---------|
| APPROVE | High quality, no issues |
| APPROVE WITH MINOR CHANGES | Minor issues, can merge after fixes |
| REQUEST CHANGES | Major issues must be fixed before merge |
| REJECT | Requires substantial rework |

**Merge Recommendation:**

| Status | Description |
|--------|-------------|
| READY TO MERGE | High quality, no blocking issues |
| NEEDS MINOR FIXES | Address minor issues, then merge |
| NEEDS SIGNIFICANT WORK | Major issues must be fixed before merge |
| NOT READY | Requires substantial rework |

**Confidence Level:** `[High / Medium / Low]`

**Reviewer Notes:**
> `[Any additional context, concerns, or suggestions]`

---

## Review Process Checklist

Be extremely thorough and critical - this is the final checkpoint before merging to the base branch:

- [ ] **Review ALL commits** - Check commit history and messages
- [ ] **Review ALL file changes** - Even configuration and test files
- [ ] **Check for regression risks** - Could this break existing functionality?
- [ ] **Validate test coverage** - Are new features properly tested?
- [ ] **Verify documentation** - Is everything documented?
- [ ] **Check for security issues** - Input validation, injection risks, etc.
- [ ] **Assess performance impact** - Any performance regressions?
- [ ] **Review error handling** - Proper exception handling throughout?
- [ ] **Check backwards compatibility** - Any breaking changes?
- [ ] **Validate architectural alignment** - Follows project patterns?

---

## Key Reminders

> **Remember:**
> - This is a pull request review, not just a commit review
> - Consider the cumulative impact of ALL changes in the branch
> - Think about maintenance burden for future developers
> - Better to request changes now than deal with production issues later
> - Provide constructive feedback with specific line references
> - Highlight both issues AND strengths

**Production confidence is the goal** - only approve if you're confident this code can run in production.

---

## Development Artifacts Review

Perform a comprehensive review of all files added or changed in the current branch compared to the main branch. Identify potential development artifacts that may no longer be needed in the repository.

### Scope of Review

Analyze all changed files in this branch and categorize them as:

| Category | Description |
|----------|-------------|
| **Production Code** | Core functionality, necessary for the application |
| **Tests** | Essential test files for CI/CD and validation |
| **Documentation** | Important docs (README, API docs, architecture) |
| **Development Artifacts** | Files created during development that may not be needed |

### Categories of Potential Artifacts to Identify

#### 1. Temporary Test/Debug Files

- Ad-hoc test scripts (`test_*.py` files not in test suite)
- Debug scripts or diagnostic tools created for troubleshooting
- Standalone verification scripts used during development
- Mock data files created for manual testing
- Test output files (`*.log`, `*.txt`, `*.json` in non-standard locations)

#### 2. Draft/Working Documentation

- Multiple versions of the same documentation
- Working notes or development journals
- Code review notes or TODO lists saved as files
- Planning documents that are now implemented
- Redundant README files in subdirectories

#### 3. Example/Sample Files

- Example configurations used for reference during development
- Sample data files used for manual testing
- Template files that were copied and modified (originals no longer needed)
- Proof-of-concept implementations superseded by production code

#### 4. Duplicate or Old Versions

- Files with suffixes like `_old`, `_backup`, `_v2`, `_copy`
- Multiple implementations of the same functionality
- Deprecated handlers/agents replaced by newer versions
- Old configuration files replaced by new formats

#### 5. Build/Generated Artifacts

- Compiled files (`*.pyc`, `__pycache__`)
- Generated reports not tracked in git
- Temporary build outputs
- Cache files

#### 6. Environment-Specific Files

- Local configuration files (should be in `.gitignore`)
- Developer-specific settings
- IDE configuration files
- Local database files or credentials

#### 7. Commented-Out Code Files

- Entire files that are commented out
- Disabled modules or features no longer used

### Artifacts Review Process

**Get branch comparison:**

```bash
git diff main...HEAD --name-status
```

**For each file, determine:**

| Question | Evaluation |
|----------|------------|
| **Purpose** | What was this file created for? |
| **Current status** | Is it actively used? Referenced by other code? |
| **Production necessity** | Is it needed for the application to run? |
| **Test necessity** | Is it part of the test suite or CI/CD? |
| **Documentation value** | Does it provide important information? |

**Categorize files:**

| Symbol | Category | Meaning |
|--------|----------|---------|
| Keep (Essential) | Production code, active tests, important docs |
| Review (Uncertain) | May be needed, requires user confirmation |
| Consider Removing | Likely development artifact |

### Artifacts Report Output Format

#### Summary Statistics

```
Total files added/modified in branch: [X]
Files recommended for keeping:        [X]
Files suggested for removal:          [X]
Files requiring user decision:        [X]
```

#### Detailed Analysis by Category

For each file suggested for removal, provide:

| Field | Description |
|-------|-------------|
| File path | Full path to the file |
| File size and type | Size in KB/MB and file extension |
| Reason for suggestion | Which category above |
| Risk assessment | Safe to remove / Verify first / Keep for now |
| Dependencies | If any other files reference it |
| Recommendation | Specific action to take |

#### Example Format

```
SUGGESTED FOR REMOVAL
Category: Temporary Test Files

file: melingo_agent/tests/debug_validation.py (1.2 KB)
   Reason: Standalone debug script, not part of pytest suite
   Risk: Safe to remove
   Dependencies: None found
   Recommendation: This appears to be a one-off debugging script.
                   Can be safely removed if no longer needed.

file: test_output.log (45 KB)
   Reason: Test output file
   Risk: Safe to remove
   Dependencies: None
   Recommendation: Log files should not be committed. Add to .gitignore.
```

### Important Artifacts Review Guidelines

| Guideline | Description |
|-----------|-------------|
| **Be conservative** | When in doubt, categorize as "Review" not "Remove" |
| **Check dependencies** | Search for imports/references before suggesting removal |
| **Consider context** | Some "temporary" files may be examples for documentation |
| **Flag, don't delete** | Only suggest removals, never automatically delete |
| **Provide reasoning** | Explain WHY each file might not be needed |
| **Group by risk** | Separate "safe to remove" from "verify first" |

### Files to NEVER Suggest Removing

> **Protected Files:**
> - Core application code (agents, handlers, utilities)
> - Active test files in the test suite
> - Main documentation (README.md, API docs, architecture docs)
> - Configuration files referenced in code
> - Production templates and validation rules
> - Requirements files (`pyproject.toml`, `requirements.txt`)

### Artifacts Review Final Output

End the artifacts review with:

| Section | Content |
|---------|---------|
| **Safe to remove** | List of files that can be deleted with high confidence |
| **Verify before removing** | Files that might be artifacts but need user confirmation |
| **Keep** | Files that should remain |
| **Suggested .gitignore additions** | Patterns for files that shouldn't be tracked |

> **Always ask the user which files they'd like to remove before taking any action.**
