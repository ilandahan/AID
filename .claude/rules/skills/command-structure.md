---
paths:
  - ".claude/commands/**/*"
---

# Command Structure Rules

Rules for creating and modifying slash commands.

---

## Command File Location

All commands go in `.claude/commands/`:

```
.claude/commands/
├── aid-init.md           # Phase initialization
├── aid-start.md          # Start work session
├── discovery.md          # Phase 0 entry point
├── phase.md              # Check current phase
├── gate-check.md         # Verify phase gate
└── ...
```

---

## Command File Format

```markdown
# Command Name

Brief description of what this command does.

## Usage

```
/command-name [options]
```

## When to Use

- Scenario 1
- Scenario 2

## Process

1. Step 1
2. Step 2
3. Step 3

## Output

[Expected output or behavior]

## Related Commands

- /related-command-1
- /related-command-2
```

---

## Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| AID lifecycle | `aid-{action}` | `/aid-init`, `/aid-start`, `/aid-end` |
| Phase management | `phase-{action}` | `/phase`, `/phase-advance`, `/phase-approve` |
| Feature commands | `{feature}` | `/discovery`, `/code-review`, `/test-review` |
| Context | `context-{action}` | `/context`, `/context-update` |

---

## Command Categories

### Lifecycle Commands
- `/aid-init` - Initialize project
- `/aid-start` - Start session (select role + phase)
- `/aid-end` - End session with feedback
- `/aid-status` - Show current state

### Phase Commands
- `/phase` - Show current phase
- `/gate-check` - Check gate requirements
- `/phase-approve` - Human approval
- `/phase-advance` - Move to next phase

### Development Commands
- `/discovery` - Start Phase 0
- `/code-review` - Review code
- `/write-tests` - TDD test writing
- `/test-review` - Review test quality

### Quality Commands
- `/reflect` - Show quality check details
- `/context` - Show work context

---

## Command-Skill Integration

Commands can invoke skills:

```markdown
# /code-review

[Command documentation]

## Skills Loaded

This command loads:
- `skills/code-review/SKILL.md`
- `skills/test-driven/SKILL.md` (if reviewing tests)
```

---

## Command Output Standards

Commands should provide clear output:

```markdown
## Output Format

### Success
```
✅ [Action completed]

[Summary of what was done]

Next steps:
- Step 1
- Step 2
```

### Error
```
❌ [Action failed]

Reason: [Why it failed]

To fix:
- Fix step 1
- Fix step 2
```
```

---

## State Management

Commands that modify state must:

1. **Read current state** from `.aid/state.json` or `.aid/context.json`
2. **Validate** the operation is allowed
3. **Update state** atomically
4. **Confirm** the change to user

---

## Command Checklist

- [ ] File in `.claude/commands/`
- [ ] Name follows conventions
- [ ] Clear usage instructions
- [ ] When to use documented
- [ ] Step-by-step process
- [ ] Expected output shown
- [ ] Related commands listed
- [ ] Skills loaded documented (if applicable)
- [ ] State changes documented (if applicable)
