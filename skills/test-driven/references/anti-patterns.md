# Testing Anti-Patterns Reference

Detailed examples of what to avoid in test writing.

---

## 1. Writing Implementation Before Tests

### ❌ WRONG ORDER

```python
# 1. Write implementation first
def process_data(data): ...

# 2. Then write tests
def test_process_data(): ...
```

### ✅ CORRECT ORDER (TDD)

```python
# 1. Write test first
def test_process_data_returns_cleaned_dict():
    result = process_data({"name": " John ", "age": "30"})
    assert result == {"name": "John", "age": 30}

# 2. Watch it fail (no implementation exists)

# 3. Then implement
def process_data(data):
    return {
        "name": data["name"].strip(),
        "age": int(data["age"])
    }
```

---

## 2. Modifying Tests to Make Them Pass

### ❌ BAD - Weakening test to pass

```python
# Original test (failing)
def test_validate_email():
    assert validate_email("test@example.com") == True
    assert validate_email("invalid") == False  # This fails

# Wrong fix: Weaken the test
def test_validate_email():
    result = validate_email("test@example.com")
    assert result is not None  # Weakened assertion!
    # Removed failing assertion entirely
```

### ✅ GOOD - Fix the implementation

```python
def validate_email(email: str) -> bool:
    # Proper email validation
    return "@" in email and "." in email.split("@")[1]
```

---

## 3. Excessive Mocking (Mock Hell)

### ❌ BAD - Mock hell

```python
@patch('module.redis_client')
@patch('module.database')
@patch('module.cache')
@patch('module.external_api')
@patch('module.logger')
@patch('module.config')
@patch('module.session')
def test_create_user(mock_session, mock_config, mock_logger,
                     mock_api, mock_cache, mock_db, mock_redis):
    # 50 lines of mock setup...
    # Test is now meaningless
```

### ✅ GOOD - Real integration

```python
def test_create_user(test_db, test_redis):
    """Use real database and Redis."""
    user_data = {"name": "John Doe", "email": "john@example.com"}
    user = create_user(user_data, db=test_db, redis=test_redis)
    
    # Real integration - actually tests the full flow
    assert user.id is not None
    assert test_db.query(User).filter_by(email="john@example.com").count() == 1
    assert test_redis.exists(f"user:{user.id}") == 1
```

---

## 4. Weak Assertions

### ❌ BAD - Useless assertions

```python
def test_create_config():
    config = create_configuration()
    assert config  # Only checks truthy
    assert config is not None  # Trivial
    assert len(config) > 0  # Too vague
```

### ✅ GOOD - Strong, specific assertions

```python
def test_create_config():
    config = create_configuration()
    assert config['tenant_name'] == 'acme_corp'  # Exact value
    assert config['type'] == 'sales'
    assert 'shopify' in config['integrations']
    assert config['integrations']['shopify']['api_key'] is not None
    assert len(config['tools']) >= 3  # Specific requirement
```

---

## 5. Simplified Test Data

### ❌ BAD - Unrealistic test data

```python
test_user = {
    "name": "a",
    "email": "a@a.com",
    "description": "test"
}
```

### ✅ GOOD - Realistic test data

```python
test_users = [
    {
        "name": "María García-López",
        "email": "maria.garcia+test@example.com",
        "description": "Senior software engineer passionate about AI. 🚀 "
                      "Currently building conversational AI systems.",
        "phone": "+34-123-456-789",
        "preferences": {"language": "es", "timezone": "Europe/Madrid"}
    },
    {
        "name": "O'Brien-Smith III",
        "email": "test.user@subdomain.example.org",
        "description": "",  # Edge case: empty
        "phone": None,  # Edge case: missing
        "preferences": {}
    }
]
```

---

## 6. Test-Specific Logic in Implementation

### ❌ BAD - Overfitted implementation

```python
def process_input(text: str, is_test: bool = False) -> dict:
    if is_test:
        # Special handling for tests
        return {"result": "test_value"}
    # Real logic
    return extract_data(text)
```

### ✅ GOOD - General implementation

```python
def process_input(text: str) -> dict:
    # Works the same way for tests and production
    return extract_data(text)
```

---

## 7. Hardcoded Test Values in Implementation

### ❌ BAD - Overfitted to pass tests

```python
def process_user_input(text: str) -> dict:
    """Overfitted to pass tests."""
    # Hardcoded for test case
    if text == "create sales agent":
        return {"type": "sales", "action": "create"}
    
    # Won't work for any other input
    return {"type": "unknown", "action": "none"}
```

### ✅ GOOD - General implementation

```python
def process_user_input(text: str) -> dict:
    """General NLP-based intent detection."""
    llm_response = llm.classify_intent(text)
    action = extract_action(text)
    agent_type = extract_agent_type(text)
    
    return {
        "type": agent_type,
        "action": action,
        "confidence": llm_response.confidence
    }
```

---

## 8. Tests with Shared State

### ❌ BAD - Shared state and dependencies

```python
class TestConfigManagement:
    config = None  # Shared class variable - BAD!
    
    def test_01_create(self):
        """Tests numbered to enforce order - BAD!"""
        self.config = create_config()
        assert self.config is not None
    
    def test_02_update(self):
        """Depends on test_01_create running first - BAD!"""
        self.config['name'] = "Updated"
        save_config(self.config)
        assert True
```

### ✅ GOOD - Independent tests with fixtures

```python
@pytest.fixture
def test_config():
    """Provide fresh config for each test."""
    return create_config()

def test_create_config(test_config):
    """Independent test."""
    assert test_config is not None
    assert 'name' in test_config

def test_update_config(test_config):
    """Also independent."""
    test_config['name'] = "Updated"
    save_config(test_config)
    loaded = load_config(test_config['id'])
    assert loaded['name'] == "Updated"
```

---

## 9. Hiding Failures with Try-Except

### ❌ BAD - Hiding failures

```python
def test_api_call():
    try:
        result = make_api_call()
        assert result is not None
    except Exception:
        pass  # Silently passes on failure!
```

### ✅ GOOD - Let failures fail

```python
def test_api_call_success():
    result = make_api_call()
    assert result['status'] == 'success'
    assert 'data' in result

def test_api_call_handles_timeout():
    with pytest.raises(TimeoutError) as exc:
        make_api_call(timeout=0.001)
    assert "timed out" in str(exc.value)
```

---

## 10. Skipped Tests Without Justification

### ❌ BAD - Skipped without reason

```python
@pytest.mark.skip
def test_complex_scenario():
    # Who knows why this is skipped?
    pass
```

### ✅ GOOD - Skipped with justification

```python
@pytest.mark.skip(reason="Requires external API - see JIRA-1234")
def test_external_api_integration():
    pass

@pytest.mark.skipif(
    not os.getenv("REDIS_URL"),
    reason="Redis not configured in CI environment"
)
def test_redis_cache():
    pass
```

---

## 11. Only Testing Happy Paths

### ❌ BAD - Only happy path

```python
def test_create_user():
    user = create_user({"name": "John", "email": "john@example.com"})
    assert user.id is not None
    # No error case testing!
```

### ✅ GOOD - Comprehensive coverage

```python
class TestCreateUser:
    def test_create_user_success(self):
        """Happy path."""
        user = create_user({"name": "John", "email": "john@example.com"})
        assert user.id is not None
        assert user.name == "John"
    
    def test_create_user_missing_email(self):
        """Error: missing required field."""
        with pytest.raises(ValidationError) as exc:
            create_user({"name": "John"})
        assert "email" in str(exc.value).lower()
    
    def test_create_user_invalid_email(self):
        """Error: invalid email format."""
        with pytest.raises(ValidationError) as exc:
            create_user({"name": "John", "email": "not-an-email"})
        assert "valid email" in str(exc.value).lower()
    
    def test_create_user_unicode_name(self):
        """Edge case: unicode characters."""
        user = create_user({"name": "李明", "email": "li@example.com"})
        assert user.name == "李明"
```

---

## 12. Brittle Tests (Implementation-Dependent)

### ❌ BAD - Tests implementation details

```python
def test_user_creation():
    with patch('module._internal_helper') as mock_helper:
        with patch('module._validate_internal') as mock_validate:
            mock_helper.return_value = "internal_value"
            mock_validate.return_value = True
            
            result = create_user(...)
            
            # Testing internal implementation details
            mock_helper.assert_called_once_with("specific_arg")
            mock_validate.assert_called_with(internal_format=True)
```

### ✅ GOOD - Tests behavior/outcomes

```python
def test_user_creation(test_db):
    # Test the actual outcome, not how it got there
    user = create_user({"name": "John", "email": "john@example.com"})
    
    # Verify actual results
    assert user.id is not None
    assert user.name == "John"
    assert user.email == "john@example.com"
    
    # Verify side effects that matter
    saved_user = test_db.query(User).filter_by(email="john@example.com").first()
    assert saved_user is not None
```

---

## Quick Reference: Anti-Pattern Detection

| Pattern | Detection Signal | Action |
|---------|-----------------|--------|
| Mock Hell | >5 `@patch` decorators | Use real integration |
| Weak Assertion | `is not None`, `> 0` | Assert exact values |
| Simplified Data | Single-char values | Use production-like data |
| Test Modification | Git history shows test weakening | Fix implementation |
| Overfitting | `if is_test:` in implementation | Remove test-specific code |
| Shared State | Class variables in test class | Use fixtures |
| Hidden Failures | `except: pass` in tests | Let tests fail |
| Skipped Tests | `@skip` without reason | Add justification or fix |
| Happy Path Only | No `pytest.raises` | Add error tests |
| Brittle Tests | Mocking internal functions | Test behavior |
