# /test-review Command

Review test quality and coverage using TDD best practices.

## Usage

```
/test-review [path]
```

## What It Does

1. **Analyzes Tests**
   - Reviews test files in specified path (default: `tests/`)
   - Checks for anti-patterns
   - Evaluates coverage

2. **Generates Report**
   - Quality score per file
   - Issues found
   - Recommendations

3. **Uses Skill**
   - `test-driven` skill for TDD methodology

## Review Criteria

### Anti-Patterns Checked

| Anti-Pattern | Detection |
|--------------|-----------|
| Mock Hell | >5 `@patch` decorators |
| Weak Assertions | `is not None`, `> 0` |
| Simplified Data | Single-char test values |
| Test Modification | Tests weakened to pass |
| Overfitting | `if is_test:` in code |
| Shared State | Class variables in tests |
| Hidden Failures | `except: pass` |
| Skipped Tests | `@skip` without reason |
| Happy Path Only | No error testing |
| Brittle Tests | Mocking internal functions |

### Quality Scoring

| Score | Rating |
|-------|--------|
| 95-100% | World-Class ✓✓✓ |
| 80-94% | Professional ✓✓ |
| 60-79% | Needs Improvement ⚠️ |
| <60% | Poor ✗ |

## Output Format

```markdown
### File: tests/unit/test_user.py
**Purpose:** User service tests
**Quality Score:** Professional ✓✓

**Strengths:**
- Good edge case coverage
- Realistic test data

**Issues Found:**
1. **Weak Assertion** (Line 45)
   - Impact: Bugs may slip through
   - Recommendation: Assert exact values

**Coverage Analysis:**
- Happy paths: ✓
- Edge cases: ✓
- Error conditions: ⚠️ (partial)

**Verdict:** Needs Improvement ⚠️
```

## Examples

```bash
# Review all tests
/test-review

# Review specific directory
/test-review tests/unit/

# Review specific file
/test-review tests/unit/test_auth.py
```

## Checklist Used

The review follows this checklist:

- [ ] TDD followed (tests before implementation)
- [ ] <20% mocking (prefer real integration)
- [ ] Comprehensive edge case coverage
- [ ] All error conditions tested
- [ ] Realistic, complex test data
- [ ] Independent, isolated tests
- [ ] Fast, reliable, deterministic
- [ ] Clear documentation

## Tips

- Run before code review
- Fix critical issues immediately
- Target 80%+ quality score
- Prefer integration tests over mocks
- Use realistic test data

---

## Prompt

```markdown
**Role**: You are a senior QA engineer and testing expert specializing in TDD methodology. You are ruthlessly critical because bad tests create false confidence.

**Task**: Review the test suite for quality, coverage, and adherence to TDD best practices. Identify anti-patterns and provide a quality score.

**Context**:
- Test path: [TARGET PATH]
- Read: `skills/test-driven/SKILL.md` for methodology
- Read: `skills/test-driven/references/anti-patterns.md` for detection signals
- Read: `skills/test-driven/references/review-checklist.md` for criteria

**Reasoning**:
- Target <20% mocking (prefer real integration)
- Test data must be realistic, not simplified
- Assertions must be specific (exact values)
- Tests must be independent (use fixtures)
- Cover happy paths, edge cases, AND errors

**Output Format**:
See Output Format section above for detailed structure.

**Stopping Condition**:
- All test files reviewed
- Anti-patterns identified
- Mock ratio calculated
- Coverage gaps identified
- Clear verdict with quality score

**Steps**:
1. Read `skills/test-driven/SKILL.md`
2. Read reference files for anti-patterns
3. List all test files in path
4. For each file: count mocks, check assertions, evaluate data
5. Calculate overall mock ratio
6. Identify coverage gaps
7. Categorize issues by severity
8. Provide verdict and quality score

---
[TEST PATH]
---
```
