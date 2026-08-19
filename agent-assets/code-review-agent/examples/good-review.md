# Good Code Review Example

This shows a correct, well-calibrated code review response.

## What Makes This Good

1. **Specific file:line references** — every issue points to exact location
2. **Concrete fixes** — not "make it better" but exactly what to change
3. **Correct severity assignment** — SQL injection is CRITICAL, not MAJOR
4. **Strengths acknowledged** — builds trust and calibrates feedback
5. **Ordered action_required** — CRITICALs first

## Example Response

```json
{
  "review_id": "cr-2024-01-15T10:30:00Z",
  "timestamp": "2024-01-15T10:30:00Z",
  "verdict": "FAIL",
  "categories": {
    "security": {
      "status": "FAIL",
      "issues": [
        {
          "severity": "CRITICAL",
          "file": "src/api/users.ts",
          "line": 45,
          "pattern": "SQL Injection",
          "description": "User ID from request params is interpolated directly into SQL query string: `SELECT * FROM users WHERE id = ${req.params.id}`",
          "fix": "Use parameterized query: `db.execute('SELECT * FROM users WHERE id = ?', [req.params.id])`"
        },
        {
          "severity": "MAJOR",
          "file": "src/api/auth.ts",
          "line": 23,
          "pattern": "Weak token generation",
          "description": "Session token generated with Math.random() which is cryptographically weak and predictable",
          "fix": "Use crypto.randomUUID() or crypto.randomBytes(32).toString('hex')"
        }
      ]
    },
    "code_quality": {
      "status": "PASS",
      "issues": [
        {
          "severity": "MINOR",
          "file": "src/services/UserService.ts",
          "line": 89,
          "pattern": "Magic number",
          "description": "Number 30 used without explanation in timeout calculation",
          "fix": "Extract to named constant: `const SESSION_TIMEOUT_MINUTES = 30`"
        }
      ]
    },
    "documentation": {
      "status": "PASS",
      "issues": [
        {
          "severity": "MINOR",
          "file": "src/api/users.ts",
          "line": 1,
          "pattern": "Missing file header",
          "description": "File lacks @file, @description, @related tags",
          "fix": "Add: /** @file users.ts @description User CRUD API endpoints @related ./UserService.ts */"
        }
      ]
    },
    "architecture": {
      "status": "PASS",
      "issues": []
    }
  },
  "summary": {
    "total_issues": 4,
    "critical": 1,
    "major": 1,
    "minor": 2
  },
  "strengths": [
    "Clean separation between route handlers and business logic in UserService",
    "Proper use of TypeScript interfaces for request/response types",
    "Consistent error handling pattern with custom AppError class"
  ],
  "action_required": [
    "1. [CRITICAL] Fix SQL injection in src/api/users.ts:45 — use parameterized query",
    "2. [MAJOR] Replace Math.random() token generation in src/api/auth.ts:23 — use crypto.randomUUID()"
  ],
  "handoff": {
    "next_action": "fix_and_retry",
    "message": "Fix the 2 security issues (1 CRITICAL, 1 MAJOR) and resubmit for review. Code quality and architecture are solid."
  }
}
```
