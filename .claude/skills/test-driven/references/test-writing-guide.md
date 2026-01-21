# Test Review Checklist

Comprehensive checklist for reviewing test quality and testing practices.

## 0. Test-Driven Development Verification

- [ ] Verify tests were written BEFORE implementation (check git history if possible)
- [ ] Confirm tests initially failed before implementation was added
- [ ] Check that tests define clear input/output expectations, not implementation details
- [ ] Ensure tests weren't modified to pass after implementation (anti-pattern)
- [ ] Validate that test cases are independent and don't rely on implementation internals

## 1. No Test Shortcuts or Cheating

- [ ] Identify tests that were weakened to make them pass
- [ ] Look for overly permissive assertions (e.g., `assert result is not None`)
- [ ] Check for tests that skip critical validation steps or edge cases
- [ ] Find disabled/skipped tests without proper justification
- [ ] Verify no tests were removed because they were "too hard to fix"
- [ ] Check for tests that only test happy paths
- [ ] Look for tests with try-except blocks that hide actual failures

## 2. Minimal Mocking - Prefer Real Integration

**Target: <20% mocking in test suites**

- [ ] Identify excessive use of mocks where real implementations could be used
- [ ] Check if mocks are testing implementation details rather than behavior
- [ ] Verify mocks accurately represent real behavior
- [ ] Ensure mocked external services have corresponding integration tests
- [ ] Look for "mock hell" - tests with 10+ mocked dependencies
- [ ] Check for mocks of internal functions (suggests tight coupling)
- [ ] Prefer test databases/Redis over mocking data layer
- [ ] Prefer HTTP mocking libraries over function mocks for API calls
- [ ] Verify mock return values match actual API responses

## 3. Test Coverage - Breadth and Depth

- [ ] Verify all critical user flows have end-to-end tests
- [ ] Check that edge cases are tested, not just happy paths
- [ ] Ensure error conditions and exceptions are tested
- [ ] Validate boundary conditions are tested (empty, null, max/min)
- [ ] Check for missing tests on recently added features
- [ ] Verify regression tests exist for previously fixed bugs
- [ ] Ensure async code paths are tested
- [ ] Check that all public APIs have corresponding tests
- [ ] Validate configuration variations are tested

## 4. Test Data Quality - Real World Scenarios

- [ ] Check that test data is realistic, not artificially simplified
- [ ] Verify test inputs match actual production data patterns
- [ ] Ensure test data includes edge cases (special characters, unicode, long strings)
- [ ] Check that test datasets are comprehensive (multiple scenarios)
- [ ] Validate that test data doesn't have magic values that only work for tests
- [ ] Ensure ground truth data is comprehensive and validated
- [ ] Check that test scenarios cover multi-step workflows
- [ ] Verify test data includes negative cases (invalid inputs)

## 5. Test Independence and Isolation

- [ ] Verify tests can run in any order
- [ ] Check that tests clean up after themselves
- [ ] Ensure tests don't rely on external services without proper setup/teardown
- [ ] Validate that parallel test execution works correctly
- [ ] Check for shared state between tests (global variables, class attributes)
- [ ] Verify each test has proper fixtures/setup
- [ ] Ensure tests use isolated databases/Redis instances

## 6. Integration vs Unit Testing Balance

- [ ] Verify sufficient integration tests exist (not just unit tests)
- [ ] Check that critical workflows have end-to-end tests
- [ ] Ensure unit tests don't mock so much they become meaningless
- [ ] Validate integration tests cover multi-component interactions
- [ ] Check that external API integrations have real integration tests
- [ ] Verify database interactions are tested with real database
- [ ] Ensure Redis/cache interactions are tested with real Redis
- [ ] Check that LLM integrations have both unit and integration tests

## 7. No Overfitting to Tests

- [ ] Verify implementation doesn't contain test-specific logic
- [ ] Check that code doesn't have special cases just to make tests pass
- [ ] Ensure implementation is general, not tailored to specific test inputs
- [ ] Validate that code would work with different inputs
- [ ] Look for hardcoded values in implementation matching test expectations
- [ ] Check for conditional logic that only exists for tests
- [ ] Verify independent verification was performed

## 8. Test Assertions - Strong and Specific

- [ ] Check that assertions are specific and meaningful
- [ ] Verify assertions test the actual requirement
- [ ] Ensure multiple related assertions are used
- [ ] Check that error messages in assertions are descriptive
- [ ] Validate that assertions test exact values where possible
- [ ] Ensure assertions check all fields in complex objects
- [ ] Verify assertions validate both positive and negative conditions

## 9. Error Handling and Edge Cases

- [ ] Verify tests cover error conditions, not just success paths
- [ ] Check that exception handling is tested
- [ ] Ensure timeout scenarios are tested for async operations
- [ ] Validate retry logic is tested
- [ ] Check that validation errors are tested
- [ ] Ensure malformed input handling is tested
- [ ] Verify rate limiting and throttling are tested where applicable
- [ ] Check that concurrent access scenarios are tested

## 10. Test Maintainability and Readability

- [ ] Verify test names clearly describe what is being tested
- [ ] Check that tests follow AAA pattern (Arrange, Act, Assert)
- [ ] Ensure test code is well-organized with clear setup/teardown
- [ ] Validate that test helpers/fixtures are reusable
- [ ] Check for duplicate test code that should be extracted
- [ ] Verify test data is clearly defined
- [ ] Ensure test files are organized logically

## 11. Performance and Reliability

- [ ] Check that tests complete in reasonable time
- [ ] Verify tests don't have arbitrary sleep() calls
- [ ] Ensure tests are deterministic (no flaky tests)
- [ ] Check that slow tests are marked appropriately
- [ ] Validate that resource-intensive tests use appropriate fixtures
- [ ] Verify tests don't leak resources
- [ ] Check that tests have appropriate timeouts

## 12. Simulation and Ground Truth Testing

- [ ] Verify simulation tests have comprehensive ground truth data
- [ ] Check that ground truth data is validated and realistic
- [ ] Ensure simulation scenarios cover diverse use cases
- [ ] Validate that simulation tests include multi-turn conversations
- [ ] Check that ground truth includes expected intermediate states
- [ ] Verify simulation tests catch regressions
- [ ] Ensure LLM-based simulation tests have deterministic validation

## 13. Test Documentation and Reporting

- [ ] Verify test docstrings explain what is being tested
- [ ] Check that complex test setup is documented
- [ ] Ensure test reports include meaningful output
- [ ] Validate that failed tests provide actionable debugging info
- [ ] Check that test coverage reports are generated
- [ ] Verify test results are tracked over time

---

## Critical Anti-Patterns to Flag ðŸš«

### Must Fix Immediately

| Anti-Pattern | Description | Impact |
|--------------|-------------|--------|
| Mock Abuse | >50% of test file is mock setup | Tests meaningless |
| Test Modification | Tests changed to pass instead of fixing code | False confidence |
| Assertion Weakness | Only testing `not None` or basic types | Bugs slip through |
| No Integration Tests | Only unit tests with heavy mocking | Real issues missed |
| Overfitting | Implementation has test-specific logic | Won't work in production |
| Simplified Test Data | Test data doesn't reflect real-world | False confidence |
| Skipped Tests | Tests disabled without tracking | Coverage gaps |
| No Edge Cases | Only happy path testing | Bugs in edge cases |

### Warning Anti-Patterns âš ï¸

| Anti-Pattern | Description | Impact |
|--------------|-------------|--------|
| Excessive Mocking | Mocking internal functions | Suggests coupling |
| Brittle Tests | Tests break with minor refactoring | Maintenance burden |
| Slow Tests | Tests take >10s without justification | Dev friction |
| Duplicate Tests | Multiple tests testing same thing | Maintenance burden |
| Poor Test Names | Names like `test_1`, `test_function` | Hard to understand |
| No Error Testing | Only testing success scenarios | Error handling untested |
| Hardcoded Values | Magic numbers/strings in tests | Hard to understand |
| Shared State | Tests depend on execution order | Flaky tests |

---

## Test Quality Scoring Rubric

### World-Class Testing (95-100%) âœ“âœ“âœ“

- âœ… TDD followed, tests written before implementation
- âœ… <20% mocking, prefer real integration
- âœ… Comprehensive edge case coverage
- âœ… All error conditions tested
- âœ… Realistic, complex test data
- âœ… Full integration test suite
- âœ… Independent, isolated tests
- âœ… Fast, reliable, deterministic
- âœ… Clear documentation and reporting

### Professional Testing (80-94%) âœ“âœ“

- âœ… Most critical paths tested
- âœ… Some mocking, but with integration tests
- âœ… Good edge case coverage
- âœ… Most error conditions tested
- âœ… Realistic test data
- âœ… Mix of unit and integration tests
- âœ… Mostly independent tests
- âœ… Acceptable performance

### Needs Improvement (60-79%) âš ï¸

- âš ï¸ Basic test coverage
- âš ï¸ Heavy mocking without integration tests
- âš ï¸ Limited edge case coverage
- âš ï¸ Some error conditions tested
- âš ï¸ Simplified test data
- âš ï¸ Mostly unit tests
- âš ï¸ Some test interdependencies
- âš ï¸ Some flaky tests

### Poor Testing (<60%) âœ—

- âŒ Minimal test coverage
- âŒ Mock-heavy, no integration
- âŒ No edge case testing
- âŒ No error testing
- âŒ Artificial test data
- âŒ Only mocked unit tests
- âŒ Test interdependencies
- âŒ Unreliable, slow tests

---

## Output Format for Test Reviews

### Per-File Review

```markdown
### File: path/to/test_file.py
**Purpose:** [Brief description]
**Quality Score:** [World-Class âœ“âœ“âœ“ / Professional âœ“âœ“ / Needs Improvement âš ï¸ / Poor âœ—]

**Strengths:**
- [List specific good practices found]

**Issues Found:**
1. **[Issue Type]** (Line X): [Specific issue]
   - **Impact:** [Why this matters]
   - **Recommendation:** [How to fix]

**Coverage Analysis:**
- Happy paths: âœ“/âœ—
- Edge cases: âœ“/âœ—
- Error conditions: âœ“/âœ—
- Integration scenarios: âœ“/âœ—

**Mocking Analysis:**
- Mock ratio: X% (target: <20%)
- Mocked components: [List]
- Integration test coverage: âœ“/âœ—

**Verdict:** [Ready âœ“ / Needs Improvement âš ï¸ / Major Rework Required âœ—]
```

### Summary Report

```markdown
# Test Review Summary

## Overall Test Quality Score: XX%

### Statistics:
- Total test files: X
- World-class tests: X
- Professional tests: X
- Needs improvement: X
- Poor tests: X

### Critical Issues (Must Fix):
1. [Issue with file reference]
2. [Issue with file reference]

### Recommendations (Should Improve):
1. [Recommendation with file reference]
2. [Recommendation with file reference]

### Test Coverage Gaps:
- [Feature/module with insufficient tests]

### Mock Analysis:
- Overall mock ratio: XX%
- Files with excessive mocking: [List]
- Missing integration tests: [List]

### Next Steps:
1. [Prioritized action item]
2. [Prioritized action item]

## Verdict:
[WORLD-CLASS âœ“âœ“âœ“ / PROFESSIONAL âœ“âœ“ / NEEDS IMPROVEMENT âš ï¸ / REQUIRES MAJOR WORK âœ—]
```

---

## Review Principles

1. **Be ruthlessly critical** - World-class testing requires high standards
2. **Prefer real over mocked** - Integration tests catch real issues
3. **Check for test cheating** - Tests modified to pass are worse than no tests
4. **Validate test data quality** - Unrealistic data creates false confidence
5. **Verify TDD approach** - Tests should drive implementation, not follow it
6. **Look for overfitting** - Implementation shouldn't know about tests
7. **Demand comprehensive coverage** - Edge cases and errors are critical
8. **Ensure independence** - Tests should run in any order, any time
9. **Better no test than bad test** - Bad tests create false security

**The goal is production confidence, not just passing CI/CD.**