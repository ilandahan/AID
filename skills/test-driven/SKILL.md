---
name: test-driven
description: "Comprehensive TDD (Test-Driven Development) methodology for writing production-quality tests. Use this skill when writing tests before implementation, reviewing test quality, ensuring comprehensive coverage, avoiding test anti-patterns, or when asked about testing best practices. Covers minimal mocking strategies, realistic test data, strong assertions, and test independence."
---

# Test-Driven Development Skill

Write production-quality tests using strict TDD methodology with minimal mocking and real integration.

## TDD Workflow

### Step 1: Understand Requirements
- Read feature specifications thoroughly
- Identify all user scenarios (happy paths, edge cases, errors)
- Define expected inputs and outputs clearly

### Step 2: Design Test Cases BEFORE Coding
1. List all scenarios to be tested
2. Design realistic test data matching production patterns
3. Plan assertion strategy
4. Identify what should NOT be mocked

### Step 3: Write Tests FIRST
- Tests must fail initially (no implementation exists)
- Use clear, descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)

### Step 4: Implement to Pass
- Write minimal code to pass tests
- Keep implementation general (no test-specific logic)
- Avoid hardcoding values

### Step 5: Verify & Refactor
- All tests pass
- Run independent verification with different data
- Check for overfitting

## Minimal Mocking Strategy

**Target: <20% mocking in test suites**

### When NOT to Mock (Use Real)

| Component | Approach |
|-----------|----------|
| Database | Use test database with transaction rollback |
| Redis/Cache | Use test instance or embedded Redis |
| Internal functions | Refactor if needed, don't mock |
| File system | Use temp directories |
| HTTP requests | Use `responses`, `httpretty`, `vcrpy` |
| Time-based logic | Use `freezegun` or similar |

### When to Mock (Limited Cases)
- External paid APIs (Stripe, payment gateways)
- Services you don't control
- Non-deterministic external dependencies

## Realistic Test Data

**Test data must reflect production complexity:**

```python
# ✅ GOOD - Realistic, comprehensive test data
test_users = [
    {
        "name": "María García-López",
        "email": "maria.garcia@example.com",
        "bio": "Passionate about AI and machine learning. 🤖",
        "phone": "+1-555-123-4567"
    },
    {
        "name": "李明",
        "email": "li.ming+test@example.co.uk",
        "bio": "",  # Edge case: empty bio
        "phone": None  # Edge case: missing phone
    },
    {
        "name": "O'Brien-Smith III",
        "email": "test.user@subdomain.example.org",
        "bio": "A" * 500,  # Edge case: max length
        "phone": "555.123.4567 ext 123"
    }
]

# ❌ BAD - Simplified, unrealistic test data
test_user = {
    "name": "a",
    "email": "a@a.com",
    "bio": "test"
}
```

## Strong Assertions

```python
# ✅ GOOD - Specific, comprehensive assertions
def test_create_configuration():
    config = create_configuration(user_input)
    
    assert config['tenant_name'] == 'acme_corp'
    assert config['company_name'] == 'ACME Corporation'
    assert isinstance(config['metadata'], dict)
    assert 'shopify' in config['integrations']
    assert config['integrations']['shopify']['store_url'] == 'https://acme.myshopify.com'
    assert len(config['tools']) >= 2

# ❌ BAD - Weak assertions
def test_create_configuration():
    config = create_configuration(user_input)
    assert config is not None  # Useless
    assert len(config) > 0  # Too vague
```

## Comprehensive Coverage Checklist

- [ ] Happy path (normal, expected usage)
- [ ] Edge cases (boundary values, empty, null, max/min)
- [ ] Error conditions (invalid input, missing data)
- [ ] Exception handling (correct exception types)
- [ ] Async flows (concurrent operations, timeouts)
- [ ] Integration scenarios (multi-component)
- [ ] Regression tests (previously fixed bugs)

## Test Independence

```python
# ✅ GOOD - Independent tests with fixtures
@pytest.fixture
def test_config():
    """Fresh config for each test."""
    return create_config()

def test_create_config(test_config):
    assert test_config is not None

def test_update_config(test_config):
    """Doesn't depend on test_create_config."""
    test_config['name'] = "Updated"
    save_config(test_config)
    loaded = load_config(test_config['id'])
    assert loaded['name'] == "Updated"

# ❌ BAD - Shared state
class TestConfig:
    config = None  # Shared class variable - BAD!
    
    def test_01_create(self):
        self.config = create_config()
```

## Anti-Patterns to Avoid

| Pattern | Detection Signal | Action |
|---------|-----------------|--------|
| Mock Hell | >5 `@patch` decorators | Use real integration |
| Weak Assertion | `is not None`, `> 0` | Assert exact values |
| Simplified Data | Single-char values | Use production-like data |
| Test Modification | Tests weakened to pass | Fix implementation |
| Overfitting | `if is_test:` in code | Remove test-specific code |
| Shared State | Class variables | Use fixtures |
| Hidden Failures | `except: pass` | Let tests fail |
| Happy Path Only | No `pytest.raises` | Add error tests |

---

## Prompt: Test Review

```markdown
**Role**: You are a senior QA engineer and testing expert specializing in TDD methodology, test architecture, and quality assurance. You are ruthlessly critical of test quality because bad tests create false confidence.

**Task**: Review the provided test suite for quality, coverage, and adherence to TDD best practices. Identify anti-patterns, weak assertions, and gaps in coverage.

**Context**:
- Test files to review: [FILES]
- Testing framework: pytest / jest / vitest
- Target: <20% mocking, real integration preferred
- Standards: See references/anti-patterns.md and references/review-checklist.md

**Reasoning**:
- Tests written BEFORE implementation (check git history if possible)
- Tests should NOT be modified to pass—fix implementation instead
- Prefer real integration over mocks (database, Redis, HTTP)
- Test data must be realistic, not simplified
- Assertions must be specific and meaningful
- Tests must be independent (no shared state)
- Coverage must include happy paths, edge cases, AND error conditions

**Output Format**:
```
# Test Review Summary

## Overall Quality Score: XX%

### Statistics
- Total test files: X
- Mock ratio: X% (target: <20%)
- Coverage: Happy paths ✓/✗ | Edge cases ✓/✗ | Errors ✓/✗

### Critical Issues 🔴 (Must Fix)
1. **[Anti-Pattern Type]** - `file:line`
   - Problem: [description]
   - Impact: [why this matters]
   - Fix: [specific recommendation]

### Major Issues 🟠 (Should Fix)
[same format]

### Minor Issues 🟡 (Consider)
[same format]

### Strengths
- [What's done well]

## Verdict
[WORLD-CLASS ✓✓✓ | PROFESSIONAL ✓✓ | NEEDS IMPROVEMENT ⚠️ | POOR ✗]
```

**Stopping Condition**:
- All test files reviewed
- Anti-patterns identified and documented
- Mock ratio calculated
- Coverage gaps identified
- Clear verdict with actionable improvements
- No ambiguous findings

**Steps**:
1. Read references/anti-patterns.md for detection signals
2. Read references/review-checklist.md for evaluation criteria
3. List all test files to review
4. For each file:
   a. Count mock usage (target <20%)
   b. Check assertion strength (specific values vs. `is not None`)
   c. Evaluate test data realism
   d. Check for shared state / test dependencies
   e. Verify coverage (happy + edge + error)
   f. Look for try-except hiding failures
5. Calculate overall mock ratio
6. Identify coverage gaps
7. Document all issues with file:line references
8. Categorize by severity
9. Provide verdict and prioritized action items

---
[TEST FILES TO REVIEW HERE]
---
```

## Prompt: Write Tests (TDD)

```markdown
**Role**: You are a senior test engineer practicing strict TDD. You write tests BEFORE implementation, use minimal mocking, and create realistic test data.

**Task**: Write comprehensive tests for the specified feature BEFORE any implementation exists. Tests must fail initially.

**Context**:
- Feature to test: [FEATURE DESCRIPTION]
- Testing framework: pytest / jest / vitest
- Integration: Use real database/Redis where possible
- Mock only: External paid APIs, services you don't control

**Reasoning**:
- Tests define the contract—write them first
- Use realistic test data matching production patterns
- Cover happy paths, edge cases, AND error conditions
- Assertions must be specific (exact values, not just truthy)
- Each test must be independent (use fixtures)
- Prefer real integration over mocks

**Output Format**:
1. Test file with complete test cases
2. Fixtures for setup/teardown
3. Realistic test data
4. Comments explaining each test's purpose

**Stopping Condition**:
- All scenarios covered (happy, edge, error)
- Tests run and FAIL (no implementation yet)
- Zero mock abuse (<20% mocking)
- All assertions are specific
- Tests are independent

**Steps**:
1. Analyze feature requirements
2. List all scenarios: happy paths, edge cases, errors
3. Design realistic test data
4. Write test fixtures for setup/teardown
5. Write tests in order: happy path → edge cases → errors
6. Use strong, specific assertions
7. Verify tests can run (and fail)
8. Document test purpose in docstrings

---
[FEATURE DESCRIPTION HERE]
---
```

## References

- `references/anti-patterns.md` - Detailed anti-pattern examples
- `references/test-writing-guide.md` - Comprehensive test writing guide
- `references/review-checklist.md` - Test review checklist
