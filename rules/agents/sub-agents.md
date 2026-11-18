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
| **reflection-agent** | Objective quality evaluation | `agents/reflection-agent.md` |
| **qa-validator-agent** | Task completion validation | `agents/qa-validator-agent.md` |
| **phase-review-agent** | Phase gate validation | `agents/phase-review-agent.md` |
| **aid-test-agent** | AID methodology testing | `agents/aid-test-agent.md` |

---

## Spawning Pattern

All sub-agents are spawned BY NAME with the Task tool. The plugin is `aid`, so
`agents/<agent-name>.md` is `aid:<agent-name>`; in a repo checkout without the plugin the
bare name works. The agent's prompt, `tools:` list and model come from its own agent file,
so the Task prompt passes only the inputs (its `{{VARIABLES}}`). Never run an AID agent's
job as `general-purpose`: that agent has every tool, whatever the AID agent's `tools:` says.

```
Task(
  subagent_type: "aid:<agent-name>",   (fallback: "<agent-name>")
  prompt: [the task inputs: the agent's {{VARIABLES}}, filled in],
  description: "[Brief description]"
)
```

---

## Agent File Structure

`agents/` is flat: one self-contained file per agent. Claude Code registers every `.md`
under `agents/` as an agent, so never add a subfolder there.

```
agents/{agent-name}.md          # Frontmatter (name, description, tools, model)
                                # + the full prompt with {{variables}}, inlined
agent-assets/{agent-name}/      # Optional: calibration examples (good/bad outputs)
skills/{skill-name}/SKILL.md    # When/how to spawn (for main agent)
```

See `agent-assets/AGENT-STANDARD.md` for the full standard.

---

## Variable Replacement Rules

Before spawning, replace all `{{VARIABLE}}` placeholders in the prompt:

1. **Extract from conversation** - User requests, stated WHY, etc.
2. **Read from files** - State, context, source code
3. **Use exact text** - Never summarize or paraphrase

### Example

```markdown
# In agents/<agent-name>.md
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

- `agent-assets/AGENT-STANDARD.md` - Full agent structure specification
- `rules/agents/reflection-agent.md` - Reflection agent specific rules
- `skills/reflection/SKILL.md` - How to invoke reflection agent
