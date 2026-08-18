# AID Sub-Agent Standard Structure

This document defines the standard file structure for all AID sub-agents.

## Location

All agents live in `.claude/agents/` — the official Claude Code location and the single
source of truth. Linked projects reach it through a symlink (macOS/Linux) or junction
(Windows), so editing here updates every linked project at once.

## Every Agent Needs TWO Things

| Path | Purpose | Required |
|------|---------|----------|
| `.claude/agents/{agent-name}.md` | **Definition** — YAML frontmatter that makes Claude Code register the agent | YES |
| `.claude/agents/{agent-name}/` | **Assets** — prompt, references, templates, examples | YES |

Without the `.md` definition file Claude Code does **not** register the agent, and
`subagent_type="{agent-name}"` fails to resolve. The folder alone is not enough.

The definition is a thin loader that points at `AGENT-PROMPT.md` instead of duplicating
it, so the prompt stays in exactly one place:

```markdown
---
name: my-agent            # MUST match the filename exactly
description: What it does and when to use it. Drives automatic delegation.
tools: Read, Grep, Glob   # omit to inherit all tools
model: inherit            # inherit | opus | sonnet | haiku
---

One-line identity statement.

Load before working:
1. `.claude/agents/my-agent/AGENT-PROMPT.md` — authoritative prompt
2. `.claude/agents/my-agent/templates/response.json` — exact response shape
```

`testing/e2e/test_agents_and_hooks.py` enforces this: every agent folder must have a
matching definition, frontmatter `name` must equal the filename, and every file the
definition references must exist.

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
│  .claude/agents/{agent-name}/AGENT-PROMPT.md                │
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
| **memory-analysis-agent** | Feedback analysis & skill improvement | AGENT-PROMPT.md |
| **code-review-agent** | Isolated code review (security, quality, docs, architecture) | AGENT-PROMPT.md |
| **test-review-agent** | Isolated test quality review (assertions, coverage, mocks, independence) | AGENT-PROMPT.md |
| **visual-qa-agent** | Visual/interaction review of a running app in a real browser | AGENT-PROMPT.md |

---

## Corresponding Skills

Each agent should have a skill that tells the main agent when/how to spawn it:

| Agent | Skill Location |
|-------|----------------|
| reflection-agent | `.claude/skills/reflection/SKILL.md` |
| qa-validator-agent | `.claude/hooks/validate-qa-gate.py` (QA gate Stop hook) |
| phase-review-agent | `.claude/skills/phase-enforcement/SKILL.md` |
| aid-test-agent | `.claude/commands/aid-test.md` |
| memory-analysis-agent | `.claude/skills/memory-system/SKILL.md` |
| code-review-agent | `.claude/skills/pipeline-orchestrator/SKILL.md` |
| test-review-agent | `.claude/skills/pipeline-orchestrator/SKILL.md` |

---

## Spawning Pattern

Sub-agents are spawned by NAME, which works because each has a registered definition
file (`.claude/agents/{agent-name}.md`):

```
Task(
  subagent_type: "reflection-agent",
  prompt: [the task, with {{variables}} replaced],
  description: "[Brief description]"
)
```

The definition loads `AGENT-PROMPT.md` itself, so the prompt does not have to be pasted
in. Use `subagent_type: "general-purpose"` only for an agent that has no definition
file — if you find yourself doing that for one of the agents listed above, its
definition is missing and Claude Code cannot see it.

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

1. Create folder: `.claude/agents/{agent-name}/`
2. Create `AGENT-PROMPT.md` with the full prompt template
3. Create `references/` with supporting documentation (if needed)
4. Create `templates/` with response JSON schemas
5. Create `examples/` with good/bad examples
6. **Create the definition `.claude/agents/{agent-name}.md`** (frontmatter `name` must
   equal the filename). Without it Claude Code will not register the agent.
7. Create the corresponding **skill** in `.claude/skills/` that tells the main agent when
   to spawn it
8. Add it to this document's agent list
9. Run `python -m pytest testing/e2e/test_agents_and_hooks.py` — it fails if the
   definition is missing, misnamed, or points at files that do not exist

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
