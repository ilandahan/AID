# Bad Code Review Example — Anti-Patterns to Avoid

This shows what a BAD review looks like. Do NOT produce output like this.

## Anti-Pattern 1: Vague Issues Without File References

```json
{
  "categories": {
    "security": {
      "status": "FAIL",
      "issues": [
        {
          "severity": "MAJOR",
          "file": "",
          "line": 0,
          "pattern": "Security concern",
          "description": "There might be some security issues",
          "fix": "Review security"
        }
      ]
    }
  }
}
```

**Why this is wrong:**
- No file path or line number
- Vague description ("might be some")
- Non-actionable fix ("review security")
- Wrong severity (if it's a real security issue, it should be CRITICAL)

## Anti-Pattern 2: Everything is PASS (Rubber Stamp)

```json
{
  "verdict": "PASS",
  "categories": {
    "security": { "status": "PASS", "issues": [] },
    "code_quality": { "status": "PASS", "issues": [] },
    "documentation": { "status": "PASS", "issues": [] },
    "architecture": { "status": "PASS", "issues": [] }
  },
  "strengths": ["Code looks good"],
  "action_required": []
}
```

**Why this is wrong:**
- No specific observations — reviewer clearly didn't read the code
- Generic strength ("code looks good" says nothing)
- Real reviews almost always find at least MINOR issues
- If code truly has no issues, strengths should be specific

## Anti-Pattern 3: Including Conversation Context

```json
{
  "categories": {
    "architecture": {
      "issues": [
        {
          "description": "Based on our earlier discussion about using Redux, this implementation..."
        }
      ]
    }
  }
}
```

**Why this is wrong:**
- References "our earlier discussion" — agent has NO conversation context
- Agent must evaluate only what was provided in the variables
- This indicates context leakage (the agent was given forbidden information)

## Anti-Pattern 4: Wrong Severity Calibration

```json
{
  "categories": {
    "security": {
      "issues": [
        {
          "severity": "MINOR",
          "pattern": "SQL Injection",
          "description": "User input in SQL query"
        }
      ]
    }
  }
}
```

**Why this is wrong:**
- SQL Injection is ALWAYS CRITICAL, never MINOR
- This miscalibration could allow a security vulnerability to ship
- Any injection vulnerability is auto-CRITICAL per review rules

## Anti-Pattern 5: Empty Strengths

```json
{
  "strengths": [],
  "action_required": [
    "1. Everything needs to be rewritten"
  ]
}
```

**Why this is wrong:**
- No strengths at all — even bad code usually has some positive aspects
- Destructive feedback without constructive balance
- "Rewrite everything" is not actionable
