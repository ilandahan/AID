# /jira-breakdown Command

Generate Jira project structure from technical specification.

## Usage

```
/jira-breakdown [feature-name]
```

## What It Does

1. **Reads Tech Spec**
   - Parses `docs/tech-specs/TECH-SPEC-<feature-name>.md`
   - Extracts components and tasks

2. **Generates Hierarchy**
   - Epic (feature level)
   - Stories (user-facing functionality)
   - Tasks (technical work)
   - Subtasks (atomic work units)

3. **Creates in Jira** (if MCP connected)
   - Uses Atlassian MCP server
   - Creates issues with estimates

## Hierarchy Structure

```
Epic: User Authentication System
├── Story: User Registration
│   ├── Task: Create registration API endpoint
│   │   ├── Subtask: Define TypeScript interfaces
│   │   ├── Subtask: Implement validation
│   │   ├── Subtask: Write unit tests
│   │   └── Subtask: Write integration tests
│   ├── Task: Create registration form component
│   │   ├── Subtask: Create FormField atoms
│   │   ├── Subtask: Create RegistrationForm organism
│   │   └── Subtask: Write component tests
│   └── Task: Email verification flow
│       ├── Subtask: Create email service
│       ├── Subtask: Create verification endpoint
│       └── Subtask: Write tests
├── Story: User Login
│   └── ...
└── Story: Password Reset
    └── ...
```

## Output Format

```markdown
# Jira Breakdown: User Authentication

## Epic
**Title:** User Authentication System
**Description:** Complete authentication flow including registration, login, and password reset
**Estimate:** 3 sprints

---

## Story 1: User Registration
**Points:** 8
**Acceptance Criteria:**
- User can register with email/password
- Email validation required
- Password strength enforcement

### Task 1.1: Registration API
**Estimate:** 1d
- [ ] Define interfaces (2h)
- [ ] Implement endpoint (4h)
- [ ] Write tests (2h)

### Task 1.2: Registration Form
**Estimate:** 1d
- [ ] Create atoms (2h)
- [ ] Build form organism (4h)
- [ ] Component tests (2h)

---

## Story 2: User Login
**Points:** 5
...
```

## Examples

```bash
# Generate from existing tech spec
/jira-breakdown user-authentication

# Interactive mode
/jira-breakdown
```

## Estimation Guidelines

| Item Type | Time Unit |
|-----------|-----------|
| Epic | Sprints |
| Story | Story Points |
| Task | Days |
| Subtask | Hours |

### Story Points Reference
| Points | Complexity |
|--------|------------|
| 1 | Trivial change |
| 2 | Simple task |
| 3 | Small feature |
| 5 | Medium feature |
| 8 | Large feature |
| 13 | Epic-level work |

## Jira MCP Integration

If Atlassian MCP is configured in `.mcp.json`:

```json
{
  "mcpServers": {
    "atlassian": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-atlassian"],
      "env": {
        "ATLASSIAN_SITE_URL": "${ATLASSIAN_SITE_URL}",
        "ATLASSIAN_USER_EMAIL": "${ATLASSIAN_USER_EMAIL}",
        "ATLASSIAN_API_TOKEN": "${ATLASSIAN_API_TOKEN}"
      }
    }
  }
}
```

The command will:
1. Create Epic in Jira
2. Create Stories linked to Epic
3. Create Tasks linked to Stories
4. Set estimates and assignees

## After Breakdown

1. Review estimates with team
2. Prioritize stories
3. Assign to sprint
4. Start Phase 5: Development
   ```
   /phase 5
   ```

## Tips

- Break tasks into 2-4 hour subtasks
- Include testing in every task
- Consider dependencies
- Add buffer for unknowns
- Review with team before committing
