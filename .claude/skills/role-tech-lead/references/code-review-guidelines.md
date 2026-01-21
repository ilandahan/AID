# Code Review Guidelines for Tech Leads

## Review Philosophy

### Goals of Code Review
1. **Catch bugs** - Find issues before production
2. **Share knowledge** - Spread understanding across team
3. **Maintain standards** - Enforce consistency
4. **Mentor** - Help developers grow

### Reviewer Mindset
- Assume good intent
- Be specific, not vague
- Explain WHY, not just WHAT
- Praise good work too
- Timely reviews (within 24h)

## What to Review

### Architecture & Design
- [ ] Follows established patterns
- [ ] Appropriate separation of concerns
- [ ] No circular dependencies
- [ ] Scalable design
- [ ] Doesn't over-engineer

### Code Quality
- [ ] Readable and self-documenting
- [ ] Meaningful names
- [ ] DRY (Don't Repeat Yourself)
- [ ] Single responsibility
- [ ] Appropriate abstraction level

### Security
- [ ] Input validation present
- [ ] Authorization checks correct
- [ ] No hardcoded secrets
- [ ] SQL injection prevented
- [ ] XSS prevented
- [ ] Sensitive data handled properly

### Testing
- [ ] Adequate test coverage
- [ ] Tests are meaningful (not just for coverage)
- [ ] Edge cases covered
- [ ] Tests are maintainable
- [ ] No flaky tests introduced

### Performance
- [ ] No obvious N+1 queries
- [ ] Appropriate indexing considered
- [ ] No unnecessary operations in loops
- [ ] Memory usage reasonable
- [ ] No blocking calls in async code

### Error Handling
- [ ] Errors handled appropriately
- [ ] Errors logged with context
- [ ] User-facing errors are friendly
- [ ] No swallowed exceptions

## Review Comment Examples

### Bad Comments

```
❌ "This is wrong"
❌ "Why did you do this?"
❌ "This is bad code"
❌ "Fix this"
```

### Good Comments

```
✅ "Consider using `map` here instead of `forEach` with push -
    it's more idiomatic and avoids mutation"

✅ "This could cause an N+1 query issue in production.
    Consider eager loading the associations:
    User.findAll({ include: [Profile] })"

✅ "Nice refactor! This is much cleaner than before."

✅ "Nit: Naming suggestion - `getUserById` might be clearer
    than `fetchUser` since we're querying by ID"
```

## Comment Prefixes

| Prefix | Meaning | Action Required |
|--------|---------|-----------------|
| **Blocker:** | Must fix before merge | Yes |
| **Suggestion:** | Recommended improvement | Optional |
| **Nit:** | Minor style/preference | Optional |
| **Question:** | Need clarification | Respond |
| **Praise:** | Good work | None |

## Review Workflow

### Before Requesting Review
Developer should:
- [ ] Self-review the diff
- [ ] Run all tests locally
- [ ] Check linting passes
- [ ] Write clear PR description
- [ ] Link related issues

### During Review
Reviewer should:
- [ ] Understand the context (read PR description, linked issues)
- [ ] Pull and run locally if needed
- [ ] Check tests exist and pass
- [ ] Leave constructive comments
- [ ] Approve, request changes, or comment

### After Review
Developer should:
- [ ] Respond to all comments
- [ ] Make requested changes
- [ ] Re-request review if needed

## Sensitive Topics

### When Developer Disagrees

```markdown
Reviewer: "Consider using X instead of Y"
Developer: "I chose Y because [reason]. Thoughts?"

Options:
1. Discuss and reach consensus
2. Get third opinion
3. Tech lead makes final call
4. Document as ADR if significant
```

### When to Escalate
- Significant architectural disagreement
- Security concerns
- Repeated pattern violations
- Blocked PRs affecting timeline

## PR Size Guidelines

| Size | Lines Changed | Review Time | Recommendation |
|------|---------------|-------------|----------------|
| XS | < 50 | < 15 min | Ideal |
| S | 50-200 | 15-30 min | Good |
| M | 200-500 | 30-60 min | Acceptable |
| L | 500-1000 | 1-2 hours | Split if possible |
| XL | > 1000 | > 2 hours | Must split |

## Checklist for Approval

Before approving, ensure:
- [ ] All blocker comments resolved
- [ ] Tests pass
- [ ] No security issues
- [ ] Follows team standards
- [ ] Documentation updated (if needed)
- [ ] Migration plan exists (if needed)

## Common Anti-Patterns to Flag

### Code Smells
- God classes/functions (too many responsibilities)
- Deep nesting (> 3 levels)
- Magic numbers/strings
- Dead code
- Copy-paste code

### Architecture Smells
- Bypassing layers
- Business logic in controllers
- Database access in views
- Hardcoded configuration
- Missing error handling

### Testing Smells
- Testing implementation, not behavior
- No assertions
- Hardcoded test data that can break
- Tests depending on other tests
- Mocking everything
