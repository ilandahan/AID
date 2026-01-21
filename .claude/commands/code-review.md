# /code-review Command

Comprehensive code review for commits and pull requests.

## Usage

```
/code-review [path|commit|pr]
```

## What It Does

1. **Analyzes Code**
   - Reviews changed files
   - Checks patterns and practices
   - Validates architecture

2. **Generates Report**
   - Issues by severity
   - Recommendations
   - Approval status

3. **Uses Skill**
   - `code-review` skill for best practices

## Review Categories

### 1. Code Quality
- Clean code principles
- DRY (Don't Repeat Yourself)
- Single responsibility
- Naming conventions
- Code complexity

### 2. Architecture
- Component structure (Atomic Design)
- Separation of concerns
- Dependency management
- Design patterns

### 3. TypeScript
- Type safety
- Interface definitions
- No `any` types
- Proper generics

### 4. Security
- Input validation
- SQL injection prevention
- XSS prevention
- Authentication/Authorization

### 5. Performance
- Unnecessary re-renders
- Memory leaks
- Database queries (N+1)
- Bundle size

### 6. Testing
- Test coverage
- Test quality
- Edge cases

## Severity Levels

| Level | Action Required |
|-------|-----------------|
| 🔴 Critical | Must fix before merge |
| 🟠 Major | Should fix before merge |
| 🟡 Minor | Consider fixing |
| 🔵 Info | Suggestion for improvement |

## Output Format

```markdown
# Code Review: feature/user-auth

## Summary
- Files reviewed: 12
- Issues found: 5
- Approval: ⚠️ Changes Requested

## Critical Issues 🔴
1. **SQL Injection Risk** - `src/api/users.ts:45`
   - Raw query with user input
   - Fix: Use parameterized queries

## Major Issues 🟠
1. **Missing Error Handling** - `src/hooks/useAuth.ts:23`
   - API call without try/catch
   - Fix: Add error boundary

## Minor Issues 🟡
1. **Magic Number** - `src/utils/validation.ts:12`
   - `if (password.length < 8)`
   - Fix: Extract to constant

## Suggestions 🔵
1. Consider extracting `formatDate` to utils

## Verdict
⚠️ **Changes Requested** - Fix critical and major issues
```

## Examples

```bash
# Review current changes
/code-review

# Review specific file
/code-review src/components/Button.tsx

# Review specific commit
/code-review abc123

# Review directory
/code-review src/api/
```

## Checklist Used

### Pre-Implementation
- [ ] Requirements understood
- [ ] Technical approach validated
- [ ] Tests written first (TDD)

### Code Quality
- [ ] Clean, readable code
- [ ] No code duplication
- [ ] Proper error handling
- [ ] Meaningful names

### Architecture
- [ ] Follows Atomic Design
- [ ] Proper component hierarchy
- [ ] No circular dependencies

### TypeScript
- [ ] Full type coverage
- [ ] No `any` types
- [ ] Interfaces documented

### Security
- [ ] Input validated
- [ ] No hardcoded secrets
- [ ] Proper authentication

### Testing
- [ ] Tests pass
- [ ] Coverage adequate
- [ ] Edge cases covered

## Integration

Works with:
- Git commits
- Pull requests (via GitHub MCP)
- Local file changes

## Tips

- Run before creating PR
- Fix all critical issues
- Address major issues
- Document exceptions
- Request re-review after fixes

---

## Prompt

```markdown
**Role**: You are a senior software engineer conducting a thorough code review with expertise in clean code, security, performance, and architectural patterns.

**Task**: Review the provided code changes against professional standards and provide a verdict with actionable recommendations.

**Context**:
- Code: [TARGET - file, commit, or PR]
- Focus: Code quality, security, testing, architecture
- Read: `skills/code-review/SKILL.md` for full checklist

**Reasoning**:
- Check for shortcuts (try-except abuse, TODOs, commented code)
- Verify no hardcoded values
- Validate root cause fixes
- Assess test quality
- Look for security gaps
- Evaluate architecture

**Output Format**:
See Output Format section above for detailed structure.

**Stopping Condition**:
- All changed files reviewed
- All severity levels addressed
- Clear verdict with action items

**Steps**:
1. Read `skills/code-review/SKILL.md`
2. Gather context on changed files
3. Apply checklists systematically
4. Document issues with file:line
5. Categorize by severity
6. Provide verdict

---
[CODE TO REVIEW]
---
```
