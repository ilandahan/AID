# AID Sub-Agent Standard Structure

This document defines the standard file structure for all AID sub-agents.

## Location

All agents live in `agents/` — the official Claude Code location and the single
source of truth. Linked projects reach it through a symlink (macOS/Linux) or junction
(Windows), so editing here updates every linked project at once.

## Every Agent Is ONE File

| Path | Purpose | Required |
|------|---------|----------|
| `agents/{agent-name}.md` | **Definition and prompt** — YAML frontmatter that makes Claude Code register the agent, followed by the full prompt inlined in the body | YES |
| `agent-assets/{agent-name}/` | **Supporting assets** — calibration examples (`examples/good-*.md`, `examples/bad-*.md`) for maintainers | Optional |

`agents/` is **flat**: one self-contained `<agent-name>.md` per agent and nothing else.
Claude Code registers EVERY `.md` under `agents/` as an agent, recursively, so a subfolder
there (prompt fragments, examples, templates) would register as junk agents. Never add one.

Without the `.md` definition file Claude Code does **not** register the agent, and
`subagent_type="{agent-name}"` fails to resolve.

The prompt is inlined in the definition, not loaded from a separate file. A plugin agent
runs with the user's project as its working directory, so a relative path to an external
prompt file would resolve against their code, not the plugin:

```markdown
---
name: my-agent            # MUST match the filename exactly
description: What it does and when to use it. Drives automatic delegation.
tools: Read, Grep, Glob   # omit to inherit all tools
model: inherit            # inherit | opus | sonnet | haiku
---

One-line identity statement.

## Context
Original Request: {{ORIGINAL_REQUEST}}

## Your Task
...

## Response Format (JSON)
...
```

`testing/e2e/test_agents_and_hooks.py` enforces this: `agents/` must contain only `.md`
definitions (no folders, no nested `.md`), frontmatter `name` must equal the filename,
`description` must be substantive, and every repo path the definition references in
backticks must exist.

---

## Key Principle: Agents Have Prompts Only

**Agents contain:** The prompt sent TO the sub-agent, inlined in `agents/{agent-name}.md`.

**Skills contain:** Instructions for WHEN and HOW to spawn the agent.

```
┌─────────────────────────────────────────────────────────────┐
│  skills/{skill-name}/SKILL.md                               │
│  "When to spawn, how to extract variables, response handling"│
└───────────────────────────┬─────────────────────────────────┘
                            │ tells main agent to spawn
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  agents/{agent-name}.md                                     │
│  "Frontmatter + the prompt with {{variables}}"              │
└─────────────────────────────────────────────────────────────┘
```

---

## Standard Layout

```
agents/                       # FLAT - scanned by Claude Code
├── {agent-name}.md           # Frontmatter + inlined prompt (REQUIRED)
└── ...

agent-assets/                 # NOT scanned as agents
├── AGENT-STANDARD.md         # This document
└── {agent-name}/             # Optional, per agent
    └── examples/             # Calibration examples
        ├── good-*.md         # What correct output looks like
        └── bad-*.md          # Anti-patterns to avoid
```

**Note:** No SKILL.md next to agents. That belongs in `skills/`.

---

## File Purposes

### agents/{agent-name}.md (Required)

The frontmatter registers the agent; the body is the actual prompt sent to the sub-agent.
It contains `{{variables}}` that the spawning agent fills in.

**Frontmatter:**
- `name` - must equal the filename without `.md`
- `description` - what it does and when to use it (drives delegation)
- `tools` - the tool allowlist (omit to inherit all tools)
- `model` - `inherit`, `opus`, `sonnet` or `haiku`

**Body:**
- Sub-agent identity and role
- Context section with variable placeholders
- Task instructions
- Evaluation criteria, rules and scoring guides it needs (inlined, not linked)
- Expected response format (JSON schema, inlined)

### agent-assets/{agent-name}/examples/ (Optional)

Calibration examples showing good and bad outputs, for maintainers tuning the prompt.

**Files:**
- `good-*.md` - Examples of correct, high-quality responses
- `bad-*.md` (or `failed-*.md`) - Anti-patterns and what to avoid

The agent does not load these at runtime. Anything the agent must see goes in its
definition body.

---

## Current Sub-Agents

| Agent | Purpose | Definition | Assets |
|-------|---------|------------|--------|
| **aid-test-agent** | Validates AID methodology | `agents/aid-test-agent.md` | `agent-assets/aid-test-agent/` |
| **reflection-agent** | Quality evaluation and session review | `agents/reflection-agent.md` | `agent-assets/reflection-agent/` |
| **qa-validator-agent** | Task completion validation | `agents/qa-validator-agent.md` | `agent-assets/qa-validator-agent/` |
| **phase-review-agent** | Phase gate validation (all six phase prompts inlined) | `agents/phase-review-agent.md` | `agent-assets/phase-review-agent/` |
| **memory-analysis-agent** | Feedback analysis & skill improvement | `agents/memory-analysis-agent.md` | `agent-assets/memory-analysis-agent/` |
| **code-review-agent** | Isolated code review (security, quality, docs, architecture) | `agents/code-review-agent.md` | `agent-assets/code-review-agent/` |
| **test-review-agent** | Isolated test quality review (assertions, coverage, mocks, independence) | `agents/test-review-agent.md` | `agent-assets/test-review-agent/` |
| **visual-qa-agent** | Visual/interaction review of a running app in a real browser | `agents/visual-qa-agent.md` | - |

---

## Corresponding Skills

Each agent should have a skill that tells the main agent when/how to spawn it:

| Agent | Skill Location |
|-------|----------------|
| reflection-agent | `skills/reflection/SKILL.md` |
| qa-validator-agent | `hooks/validate-qa-gate.py` (QA gate Stop hook) |
| phase-review-agent | `skills/phase-enforcement/SKILL.md` |
| aid-test-agent | `commands/aid-test.md` |
| memory-analysis-agent | `skills/memory-system/SKILL.md` |
| code-review-agent | `skills/pipeline-orchestrator/SKILL.md` |
| test-review-agent | `skills/pipeline-orchestrator/SKILL.md` |

---

## Spawning Pattern

Sub-agents are spawned by NAME, which works because each has a registered definition
file (`agents/{agent-name}.md`):

```
Task(
  subagent_type: "aid:reflection-agent",   (link-project route only: "reflection-agent")
  prompt: [the task inputs, with {{variables}} filled in],
  description: "[Brief description]"
)
```

The plugin is `aid`, so an agent is `aid:<agent-name>` (the plugin's agents); the bare
name is only for the link-project route, where this linked project's .claude/agents is
AID's linked folder. The definition brings its own prompt, `tools:` list and
model, so pass only the task inputs. Never run an AID agent's job as
the built-in `general-purpose` agent: that agent has every tool, whatever the AID agent's
`tools:` says. The autoresearch scorer is the exception to the fallback: it is spawned only
as `aid:reflection-agent`.

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

1. **Create the definition `agents/{agent-name}.md`** directly in `agents/` (no
   subfolder). Frontmatter: `name` (must equal the filename), `description`, `tools`,
   `model`. Without it Claude Code will not register the agent.
2. Write the full prompt in the body of that file: identity, `{{variables}}`, task,
   criteria, and the expected JSON response format. Inline anything the agent must read.
3. Optionally create `agent-assets/{agent-name}/examples/` with good/bad calibration
   examples
4. Create the corresponding **skill** in `skills/` that tells the main agent when
   to spawn it
5. Add it to this document's agent list
6. Run `python -m pytest testing/e2e/test_agents_and_hooks.py` — it fails if `agents/`
   is not flat, or the definition is misnamed or points at files that do not exist

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
- **Isolation enforced** - The agent file has no "instructions for main agent"
