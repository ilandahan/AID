# Example: Failing AID Test

## Result

```json
{
  "test_id": "20260113-091522",
  "files_generated": 15,
  "phases": {
    "phase_0": {"good": 3, "failed": 0, "gate": "OK"},
    "phase_1": {"good": 2, "failed": 1, "gate": "FAIL"},
    "phase_2": {"gate": "SKIPPED"},
    "phase_3a": {"gate": "SKIPPED"}
  },
  "violations_detected": "2/8",
  "overall": "FAILED",
  "errors": [
    "Phase 1 gate failed: missing requirements.md",
    "Only 2 of 8 violations detected"
  ]
}
```

## Common Failures

1. **Incomplete Files**: Agent wrote "For brevity..." instead of content
2. **Violations Not Detected**: Score >= 7 when it should fail
3. **Gate Not Enforced**: Missing files didn't block transition

## Debugging

1. Check thinking-log.md for skipped phases
2. Check file counts (expected: 24)
3. Check violation scores (bad outputs should be < 7)
4. Check gate status

Re-run with `/aid-test --verbose` after fixes.
