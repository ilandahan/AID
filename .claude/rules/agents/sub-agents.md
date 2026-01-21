# Sub-Agent Rules

Sub-agents are isolated processes spawned via the Task tool. They receive NO conversation context and evaluate/perform tasks independently.

---

## Core Principle: Context Isolation

Sub-agents are powerful because they have **no bias from the main conversation**. They see only what you explicitly pass to them.

```
┌─────────────────────────────────────────────────────────────┐
│  MAIN AGENT                                                  │
│  • Full conversation history                                 │
│  • User interactions                                         │
│  • Reasoning and decisions                                   │
│  • Previous attempts                                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │  Task tool passes ONLY:
                      │  • Explicit prompt
                      │  • Specified variables
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  SUB-AGENT (Isolated)                                        │
│  • Only sees the prompt it receives                          │
│  • No conversation history                                   │
│  • No knowledge of main agent's reasoning                    │
│  • Evaluates/acts purely on provided input                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Available Sub-Agents

| Agent | Purpose | Location |
|-------|---------|----------|
| **reflection-agent** | Objective quality evaluation | `agents/reflection-agent/` |
| **qa-validator-agent** | Task completion validation | `agents/qa-validator-agent/` |
| **phase-review-agent** | Phase gate validation | `agents/phase-review-agent/` |
| **aid-test-agent** | AID methodology testing | `agents/aid-test-agent/` |

---

## Spawning Pattern

All sub-agents use the Task tool:

```
Task(
  subagent_type: "general-purpose",
  model: "opus",
  prompt: [Rendered prompt with variables],
  description: "[Brief description]"
)
```

---

## Agent File Structure

Each agent follows this structure:

```
{agent-name}/
├── SKILL.md           # When/how to spawn (for main agent)
├── AGENT-PROMPT.md    # The prompt template with {{variables}}
├── references/        # Supporting documentation
├── templates/         # Response format schemas
└── examples/          # Good/bad output examples
```

---

## Variable Replacement Rules

Before spawning, replace all `{{VARIABLE}}` placeholders in the prompt:

1. **Extract from conversation** - User requests, stated WHY, etc.
2. **Read from files** - State, context, source code
3. **Use exact text** - Never summarize or paraphrase

### Example

```markdown
# In AGENT-PROMPT.md
Original Request: {{ORIGINAL_REQUEST}}
Stated WHY: {{STATED_WHY}}
```

```markdown
# After replacement
Original Request: Add user authentication with email/password login
Stated WHY: Users need secure access without sharing credentials
```

---

## Response Handling

Sub-agents return JSON responses. Parse and act on them:

```json
{
  "verdict": "PASS|FAIL",
  "score": 7.5,
  "issues": [...],
  "guidance": {...}
}
```

| Response | Action |
|----------|--------|
| `verdict: PASS` | Proceed with output |
| `verdict: FAIL` | Apply guidance, retry (max 3) |
| Parse error | Fall back to inline evaluation |

---

## Golden Rules

1. **Never include conversation history** in agent prompts
2. **Extract verbatim text** - Don't summarize user requests
3. **Include source files** - Let agents verify claims
4. **Parse responses carefully** - Agents return JSON
5. **Respect agent verdicts** - They see things you might miss

---

## Anti-Patterns

```
❌ WRONG: Summarizing the user's request
   "User wants login functionality"

✅ RIGHT: Exact user message
   "Add user authentication with email/password login, password reset flow,
    and remember me checkbox. Use the existing users table."
```

```
❌ WRONG: Including reasoning
   "We chose bcrypt for password hashing because..."

✅ RIGHT: Just the output
   [code block with bcrypt usage - agent will verify it's there]
```

```
❌ WRONG: Mentioning iterations
   "This is attempt 2, previous attempt failed because..."

✅ RIGHT: Fresh evaluation each time
   [just the output, no history]
```

---

## When to Use Sub-Agents

| Use Sub-Agent | Don't Use Sub-Agent |
|---------------|---------------------|
| Quality evaluation | Simple file reads |
| Task validation | Status checks |
| Phase gate checks | Clarifying questions |
| Code review | Command help |
| Security review | Basic research |

---

## Related Documentation

- `agents/AGENT-STANDARD.md` - Full agent structure specification
- `rules/agents/reflection-agent.md` - Reflection agent specific rules
- `skills/reflection/SKILL.md` - How to invoke reflection agent
