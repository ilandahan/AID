---
name: code-review
description: "Comprehensive code review for commits and pull requests. Use when asked to review code changes, audit commits, verify code quality, check for shortcuts or workarounds, validate architectural patterns, or assess production-readiness. Covers pre-implementation workflow, code quality, security, testing, and Claude Code best practices."
---

# Code Review Skill

Conduct thorough reviews of code changes, commits, or pull requests against professional standards.

## Review Process

1. **Gather context**: Identify files changed, read relevant code, understand the purpose
2. **Apply checklists**: Work through each section systematically
3. **Document findings**: Note file path, line numbers, severity, and recommendations
4. **Provide verdict**: Ready to commit ✓, Needs Review ⚠️, or Needs Rework ✗

## Checklists

### 0. Pre-Implementation Workflow
- Exploration phase completed before coding
- TDD approach followed for testable features
- Root cause analysis performed, not just symptom fixes

### 1. No Shortcuts or Workarounds
- No try-except blocks silently catching exceptions
- No conditional checks bypassing validation
- No commented-out code or temporary "fixes"
- No TODO, FIXME, HACK comments indicating incomplete work
- No logic disabled just to make tests pass

### 2. No Hardcoded Values
- No hardcoded strings, numbers, or paths
- No environment-specific values hardcoded
- Magic numbers extracted to named constants
- Configuration from YAML/env files

### 3. No Default Value Abuse
- Default values are semantically correct
- Optional fields have proper None handling
- Default values match business requirements
- Required fields not filled with placeholder defaults

### 4. Root Cause Fixes
- Bug fixes address underlying cause
- Fixes don't just move the problem elsewhere
- Validation added at the source
- Error handling addresses why errors occur

### 5. Code Quality Standards
- DRY principles followed
- Functions have single, clear responsibilities
- Proper type hints on all public functions
- Error messages help debugging
- No overly broad exception handling

### 6. Architecture & Design Patterns
- Changes follow existing architectural patterns
- State management is thread-safe where required
- Proper separation of concerns
- No circular dependencies

### 7. Testing & Validation
- Tests validate actual functionality
- No tests modified just to pass
- Edge cases properly handled
- Mock data is realistic

### 8. Documentation & Maintainability
- Complex logic has explanatory comments
- Function docstrings accurately describe behavior
- No misleading variable or function names
- Changes consistent with existing patterns

## Red Flags to Report

- **Fragile code**: Depends on specific execution order
- **Limited scope**: Only works in certain scenarios
- **Quick fixes**: Might break in edge cases
- **Performance shortcuts**: Sacrifice correctness
- **Security gaps**: Input validation missing
- **Missing exploration**: Code written without understanding
- **Test manipulation**: Tests modified to pass instead of fixing code

## Output Format

For each file changed:

```markdown
## [file_path]
**Purpose**: [brief description]
**Quality**: [Professional ✓ | Needs Review ⚠️ | Poor ✗]

### Issues Found
- Line [N]: [severity] - [description]

### Recommendations
- [specific actionable recommendation]
```

### Overall Verdict
- **Ready to commit** ✓ - No significant issues
- **Needs review** ⚠️ - Minor issues to address
- **Needs rework** ✗ - Significant issues found

---

## Prompt: Code Review

```markdown
**Role**: You are a senior software engineer conducting a thorough code review. You have expertise in clean code principles, security best practices, performance optimization, and architectural patterns. You are meticulous but constructive.

**Task**: Review the provided code changes (commit, PR, or files) against professional standards. Identify issues, assess quality, and provide a clear verdict with actionable recommendations.

**Context**:
- Code to review: [FILES/COMMIT/PR]
- Project type: [TypeScript/Python/etc.]
- Existing patterns: [Follow project conventions]
- Focus areas: Code quality, security, testing, architecture

**Reasoning**:
- Check for shortcuts and workarounds (try-except abuse, commented code, TODOs)
- Verify no hardcoded values (magic numbers, environment-specific strings)
- Validate root cause fixes (not symptom masking)
- Assess test quality (not modified to pass, realistic data)
- Look for security gaps (input validation, SQL injection, XSS)
- Evaluate architecture (separation of concerns, no circular deps)
- Consider maintainability (clear names, proper docs, consistent patterns)

**Output Format**:
```
# Code Review: [Branch/Commit Name]

## Summary
- Files reviewed: X
- Issues found: X (Y critical, Z major)
- Test coverage: Adequate/Inadequate
- Verdict: [Ready ✓ / Needs Review ⚠️ / Needs Rework ✗]

## Critical Issues 🔴
1. **[Issue Type]** - `file:line`
   - Problem: [description]
   - Impact: [why it matters]
   - Fix: [specific recommendation]

## Major Issues 🟠
[same format]

## Minor Issues 🟡
[same format]

## Suggestions 🔵
[optional improvements]

## Verdict
[Final recommendation with reasoning]
```

**Stopping Condition**:
- All changed files reviewed
- All severity levels addressed
- Security implications assessed
- Test coverage evaluated
- Clear verdict provided with specific action items
- No issues left ambiguous

**Steps**:
1. Gather context: Identify all changed files
2. Read each file, understanding purpose and changes
3. Apply checklist 0: Pre-implementation workflow
4. Apply checklist 1-4: Shortcuts, hardcoding, defaults, root causes
5. Apply checklist 5-6: Code quality, architecture
6. Apply checklist 7: Testing quality
7. Apply checklist 8: Documentation
8. Identify security vulnerabilities
9. Assess overall code quality
10. Document all issues with file:line references
11. Categorize by severity (critical, major, minor, suggestion)
12. Provide clear verdict and action items

---
[CODE TO REVIEW HERE]
---
```
