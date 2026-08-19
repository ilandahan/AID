# Example: Passing AID Test

## Result

```json
{
  "test_id": "20260113-143052",
  "duration_minutes": 12,
  "files_generated": 24,
  "phases": {
    "phase_0": {"good": 3, "failed": 1, "gate": "OK"},
    "phase_1": {"good": 3, "failed": 2, "gate": "OK"},
    "phase_2": {"good": 3, "failed": 2, "gate": "OK"},
    "phase_3a": {"good": 2, "failed": 1, "gate": "OK"},
    "phase_3b": {"good": 3, "failed": 1, "gate": "OK"},
    "phase_3c": {"good": 2, "failed": 1, "gate": "OK"}
  },
  "violations_detected": "8/8",
  "overall": "PASSED"
}
```

## Success Indicators

| Indicator | Expected | Why Important |
|-----------|----------|---------------|
| files_generated | 24 | All phases tested |
| violations_detected | 8/8 | Quality checks catch issues |
| All gates OK | Yes | Flow enforcement works |
| Good outputs >= 7 | Yes | Methodology produces quality |
| Bad outputs < 7 | Yes | Guardrails work |
