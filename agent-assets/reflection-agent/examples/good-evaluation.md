# Good Evaluation Example

Phase 4 code evaluation for "Create login API endpoint with JWT authentication"

## Key Characteristics

- **Accurate scores**: Security 6/10 for hardcoded SECRET_KEY (not inflated)
- **Specific locations**: "SECRET_KEY is hardcoded on line 15"
- **Actionable guidance**: "Move SECRET_KEY to environment variable using os.getenv()"
- **Balanced feedback**: do_not_change lists what's working well
- **Weighted score**: 8.1/10 (passes despite issues)

## Response Structure

```json
{
  "evaluation": {
    "why_alignment": {"score": 9, "note": "Directly addresses JWT login requirement"},
    "phase_compliance": {"score": 10, "note": "Appropriate Phase 4 code"},
    "correctness": {"score": 8, "note": "Functional but missing get_user_by_email impl"},
    "security": {"score": 6, "note": "SECRET_KEY hardcoded - security risk", "vulnerabilities": ["SECRET_KEY hardcoded on line 15", "No rate limiting"]},
    "completeness": {"score": 8, "note": "Core complete, tests missing"}
  },
  "overall": {"weighted_score": 8.1, "pass": true, "status": "PASSED"},
  "revision_guidance": {
    "required_changes": [],
    "suggested_improvements": ["Move SECRET_KEY to env var", "Add rate limiting"],
    "do_not_change": ["WHY documentation pattern", "bcrypt password verification", "Generic error messages"]
  }
}
```
