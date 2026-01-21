# AID Sub-Agent Standard Structure

This document defines the standard file structure for all AID sub-agents.

## Folder Locations

| Location | Purpose |
|----------|---------|
| `agents/` (root) | **Source** - Edit agents here |
| `.claude/agents/` | **Copy** - Official Claude Code location (auto-copied by link-project scripts) |

**Note:** Always edit in `agents/` (source). Running `link-project.sh` or `link-project.bat` will copy agents to `.claude/agents/` in target projects.

---

## Key Principle: Agents Have Prompts Only

**Agents contain:** The prompt templates and supporting materials sent TO the sub-agent.

**Skills contain:** Instructions for WHEN and HOW to spawn the agent.

```
┌─────────────────────────────────────────────────────────────┐
│  .claude/skills/{skill-name}/SKILL.md                       │
│  "When to spawn, how to extract variables, response handling"│
└───────────────────────────┬─────────────────────────────────┘
                            │ tells main agent to spawn
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  agents/{agent-name}/AGENT-PROMPT.md                        │
│  "The actual prompt with {{variables}} sent to sub-agent"   │
└─────────────────────────────────────────────────────────────┘
```

---

## Standard Agent Structure

```
{agent-name}/
├── AGENT-PROMPT.md       # Primary prompt template (REQUIRED)
├── references/           # Supporting documentation
│   └── *.md, *.yaml      # Rules, scenarios, context for prompt
├── templates/            # Response format schemas
│   └── *.json            # Expected JSON response structures
└── examples/             # Calibration examples
    ├── good-*.md         # What correct output looks like
    └── bad-*.md          # Anti-patterns to avoid
```

**Note:** No SKILL.md in agent folders. That belongs in `.claude/skills/`.

---

## File Purposes

### AGENT-PROMPT.md (Required)

The actual prompt sent to the sub-agent. Contains `{{variables}}` that get replaced.

**Contents:**
- Sub-agent identity and role
- Context section with variable placeholders
- Task instructions
- Evaluation criteria (if applicable)
- Expected response format (JSON schema)

**Example:**
```markdown
# Quality Evaluator

You are an independent evaluator...

## Context
Original Request: {{ORIGINAL_REQUEST}}
Stated WHY: {{STATED_WHY}}

## Your Task
Evaluate the following output...

## Response Format (JSON)
```json
{"score": 0, "pass": false, ...}
```
```

### references/ (Optional)

Supporting documentation that provides context for the prompt.

**Examples:**
- `isolation-rules.md` - Rules for context isolation
- `scoring-guide.md` - How to score outputs
- `phase-criteria.yaml` - Phase-specific rules

### templates/ (Recommended)

JSON schemas showing expected response format.

**Examples:**
- `evaluation-response.json` - Schema for evaluation results
- `review-report.json` - Schema for review output

### examples/ (Recommended)

Calibration examples showing good and bad outputs.

**Files:**
- `good-*.md` - Examples of correct, high-quality responses
- `bad-*.md` - Anti-patterns and what to avoid

---

## Current Sub-Agents

| Agent | Purpose | Prompt Files |
|-------|---------|--------------|
| **aid-test-agent** | Validates AID methodology | AGENT-PROMPT.md |
| **reflection-agent** | Quality evaluation | AGENT-PROMPT.md, SESSION-REVIEW-PROMPT.md |
| **qa-validator-agent** | Task completion validation | AGENT-PROMPT.md |
| **phase-review-agent** | Phase gate validation | AGENT-PROMPT.md, phase-prompts/*.md |

---

## Corresponding Skills

Each agent should have a skill that tells the main agent when/how to spawn it:

| Agent | Skill Location |
|-------|----------------|
| reflection-agent | `.claude/skills/reflection/SKILL.md` |
| qa-validator-agent | `.claude/skills/qa-validator/SKILL.md` (or hooks) |
| phase-review-agent | `.claude/skills/phase-enforcement/SKILL.md` |
| aid-test-agent | `.claude/commands/aid-test.md` |

---

## Spawning Pattern

All sub-agents are spawned using the Task tool:

```
Task(
  subagent_type: "general-purpose",
  model: "opus",
  prompt: [AGENT-PROMPT.md with {{variables}} replaced],
  description: "[Brief description]"
)
```

**CRITICAL:** Sub-agents receive NO conversation context. They evaluate inputs in complete isolation.

---

## Variable Replacement

Before spawning, the main agent must replace all `{{VARIABLE}}` placeholders:

1. **Extract from conversation** - User requests, stated WHY
2. **Read from files** - State JSON, source code, criteria YAML
3. **Pass verbatim** - Don't summarize or paraphrase

**Example transformation:**
```
Before: "Original Request: {{ORIGINAL_REQUEST}}"
After:  "Original Request: Add user authentication with email/password"
```

---

## Adding a New Sub-Agent

1. Create folder: `agents/{agent-name}/`
2. Create `AGENT-PROMPT.md` with full prompt template
3. Create `references/` with supporting documentation (if needed)
4. Create `templates/` with response JSON schemas
5. Create `examples/` with good/bad examples
6. Create corresponding **skill** in `.claude/skills/` that tells main agent when to spawn
7. Add to this document's agent list
8. Run link-project script to copy to `.claude/agents/`

---

## Why This Structure?

### Separation of Concerns

| Component | Responsibility |
|-----------|----------------|
| **Skill** | WHEN to spawn, HOW to extract variables, WHAT to do with response |
| **Agent** | The PROMPT itself - what the sub-agent sees and does |

### Benefits

- **No duplication** - Each piece of info lives in one place
- **Clear ownership** - Skills own "when", agents own "what"
- **Easier maintenance** - Update prompt without touching spawn logic
- **Isolation enforced** - Agent folder has no "instructions for main agent"
