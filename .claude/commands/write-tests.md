# /write-tests Command

Write tests using Test-Driven Development (TDD) methodology.

## Usage

```
/write-tests <feature-or-function>
```

## What It Does

1. **Analyzes Requirements**
   - Identifies test scenarios
   - Plans edge cases and errors
   - Designs realistic test data

2. **Writes Tests FIRST**
   - Before any implementation
   - Strong, specific assertions
   - Comprehensive coverage

3. **Guides Implementation**
   - Tests define expected behavior
   - Red → Green → Refactor cycle

4. **Uses Skill**
   - `test-driven` skill for methodology

## Examples

```bash
# Write tests for a function
/write-tests validate-email

# Write tests for a feature
/write-tests user-registration

# Write tests for an API endpoint
/write-tests POST /api/orders

# Write integration tests
/write-tests checkout-flow --integration
```

## TDD Workflow

```
1. Write test → 2. Run (FAIL) → 3. Implement → 4. Run (PASS) → 5. Refactor
       ↑                                                              │
       └──────────────────────────────────────────────────────────────┘
```

## Critical Rules

```
✅ DO:
- Write tests BEFORE implementation
- Use realistic test data
- Test happy paths AND edge cases
- Test error conditions
- Use strong assertions
- Keep tests independent

❌ DON'T:
- Mock more than 20% of dependencies
- Use weak assertions (is not None)
- Skip edge cases
- Use simplified test data
- Create test-specific implementation logic
```

## Test Categories

| Category | Purpose | Speed |
|----------|---------|-------|
| Unit | Single function isolation | Fast (<100ms) |
| Integration | Component interactions | Moderate (100ms-2s) |
| E2E | Full user workflows | Slow (2-30s) |

## Realistic Test Data

```python
# ❌ BAD - Simplified
test_user = {"name": "a", "email": "a@a.com"}

# ✅ GOOD - Realistic
test_users = [
    {
        "name": "María García-López",
        "email": "maria.garcia+test@example.com",
        "bio": "Senior engineer 🚀"
    },
    {
        "name": "李明",
        "email": "test@subdomain.example.org",
        "bio": ""  # Edge case: empty
    }
]
```

## Strong Assertions

```python
# ❌ BAD - Weak
assert result is not None
assert len(items) > 0

# ✅ GOOD - Strong
assert result['status'] == 'success'
assert result['user']['email'] == 'test@example.com'
assert len(items) == 3
assert items[0]['name'] == 'Expected Name'
```

## Coverage Checklist

- [ ] Happy path (normal usage)
- [ ] Edge cases (empty, null, max, min)
- [ ] Error conditions (invalid input)
- [ ] Exception handling
- [ ] Boundary values
- [ ] Async flows (if applicable)
- [ ] Integration scenarios

## Output Format

```python
import pytest
from myapp.auth import validate_email, ValidationError

class TestValidateEmail:
    """Email validation with comprehensive coverage."""
    
    # Happy paths
    def test_valid_email_standard(self):
        """Standard email format accepted."""
        assert validate_email("user@example.com") == True
    
    def test_valid_email_with_plus(self):
        """Email with plus addressing accepted."""
        assert validate_email("user+tag@example.com") == True
    
    # Edge cases
    def test_invalid_email_no_at(self):
        """Email without @ rejected."""
        with pytest.raises(ValidationError) as exc:
            validate_email("userexample.com")
        assert "invalid format" in str(exc.value).lower()
    
    def test_invalid_email_empty(self):
        """Empty string rejected."""
        with pytest.raises(ValidationError) as exc:
            validate_email("")
        assert "required" in str(exc.value).lower()
    
    # Unicode edge case
    def test_valid_email_unicode_domain(self):
        """International domain accepted."""
        assert validate_email("user@例え.jp") == True
```

## Minimal Mocking Strategy

```python
# ❌ BAD - Mock hell
@patch('module.db')
@patch('module.redis')
@patch('module.api')
@patch('module.logger')
def test_create_user(mock_logger, mock_api, mock_redis, mock_db):
    # 50 lines of mock setup...
    pass

# ✅ GOOD - Real integration
def test_create_user(test_db, test_redis):
    """Use real database and Redis."""
    user = create_user({"name": "John", "email": "john@example.com"})
    
    assert user.id is not None
    assert test_db.query(User).filter_by(email="john@example.com").count() == 1
```

## Tips

- Tests are requirements documentation
- If hard to test, design might be wrong
- Realistic data catches real bugs
- Strong assertions prevent false confidence
- Independent tests run anywhere, any order

---

## Prompt

```markdown
**Role**: You are a senior QA engineer specializing in Test-Driven Development. You write tests BEFORE implementation and never compromise on test quality.

**Task**: Write comprehensive tests for [FEATURE_OR_FUNCTION] following TDD methodology.

**Context**:
- Feature: [FEATURE_OR_FUNCTION]
- Framework: pytest (Python) / Jest (TypeScript)
- Read: `skills/test-driven/SKILL.md`
- Read: `skills/test-driven/references/anti-patterns.md`

**Reasoning**:
- Tests FIRST, implementation second
- Realistic test data (not simplified)
- Strong assertions (exact values, not just truthy)
- Comprehensive coverage (happy, edge, error)
- Minimal mocking (<20%)
- Independent, isolated tests

**Output Format**:
1. Test scenarios list
2. Test data design
3. Complete test file
4. Fixture definitions
5. Implementation guidance

**Stopping Condition**:
- All scenarios covered (happy, edge, error)
- Realistic test data used
- Strong assertions throughout
- Tests are independent
- Mock ratio <20%
- Tests would FAIL without implementation

**Steps**:
1. Analyze feature requirements
2. List all test scenarios
3. Design realistic test data
4. Write happy path tests
5. Write edge case tests
6. Write error condition tests
7. Create fixtures for isolation
8. Verify tests are independent
9. Document expected implementation behavior
10. Deliver complete test file

---
Feature: [FEATURE_OR_FUNCTION]
Requirements: [REQUIREMENTS]
---
```
