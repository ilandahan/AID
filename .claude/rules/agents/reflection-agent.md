# Reflection Agent Rules

The reflection agent provides **isolated, objective quality evaluation**. These rules ensure proper context isolation.

---

## Core Principle: Isolation

The reflection agent MUST evaluate outputs **without access to conversation context**. This prevents confirmation bias where the evaluator agrees with reasoning it participated in.

---

## When to Spawn

| Spawn Reflection Agent | Skip |
|------------------------|------|
| Code generation (>10 lines) | Simple questions |
| Architecture decisions | Status checks |
| PRD/requirements | File reading |
| Technical specifications | Clarifying questions |
| Test writing | Command help |
| Implementation plans | |

---

## Context Isolation Rules

### MUST Pass to Agent

| Variable | Requirement |
|----------|-------------|
| `{{ORIGINAL_REQUEST}}` | User's exact request - **VERBATIM, not summarized** |
| `{{STATED_WHY}}` | The established WHY - **EXACT TEXT** |
| `{{OUTPUT_TO_EVALUATE}}` | The draft output |
| `{{FILES_TO_VERIFY}}` | Content of ALL referenced files |
| `{{PHASE_CRITERIA}}` | From `criteria/phase-{N}.yaml` |

### MUST NOT Pass to Agent

| Forbidden | Why |
|-----------|-----|
| Conversation history | Causes bias |
| Reasoning/justifications | Causes agreement |
| Previous attempts | Causes leniency |
| "Helpful context" | Causes bias |
| Summaries of request | Loses detail, adds spin |

---

## Extraction Rules

### Original Request
```
WRONG: "User wanted a login form"
RIGHT: "Add user authentication with email/password login, password reset,
       and remember me functionality. Use existing user table."
```
Copy the EXACT user message. Every word matters.

### Stated WHY
```
WRONG: "For security"
RIGHT: "Users need secure access to personal data without sharing
       credentials across devices. Reduces support tickets for
       password resets by 40%."
```
Copy the EXACT WHY from the WHY analysis phase.

### Files to Verify
Include content of ALL files the output:
- Claims to modify
- References or imports
- Depends on

Do NOT cherry-pick. Let the agent determine relevance.

---

## Two Modes

### Mode 1: Evaluation (On Output)
- **Trigger**: After generating significant output
- **Prompt**: `agents/reflection-agent/AGENT-PROMPT.md`
- **Purpose**: Objective quality assessment

### Mode 2: Session Review (On Project Load)
- **Trigger**: Project load, `/good-morning`, `/reflect --session`
- **Prompt**: `agents/reflection-agent/SESSION-REVIEW-PROMPT.md`
- **Purpose**: Fresh perspective on progress and direction

---

## Spawn Command

```
Task(
  subagent_type: "general-purpose",
  model: "opus",
  prompt: [Rendered AGENT-PROMPT.md with variables],
  description: "Objective quality evaluation"
)
```

---

## Response Handling

| Agent Returns | Action |
|---------------|--------|
| `pass: true` (score >= 7.0) | Display Quality Check box, show output |
| `pass: false` (score < 7.0) | Apply revision_guidance, re-spawn (max 3) |
| `score < 5.0` or violation | Escalate to user, do not proceed |

---

## Anti-Patterns (NEVER DO)

```
❌ "We decided to use bcrypt because..."
   (Includes reasoning - context leak)

❌ "Based on our earlier discussion..."
   (References history - defeats isolation)

❌ "This is attempt 2, the first had..."
   (Reveals iterations - causes leniency)

❌ "The user clarified they wanted..."
   (Additional context not in original - bias)
```

---

## Quality Check Display

After agent response, display:

```
╭─────────────────────────────────────────────────────────────╮
│ 🔍 Quality Check                                            │
├─────────────────────────────────────────────────────────────┤
│  [icon] WHY Alignment     X/10   [agent note]               │
│  [icon] Phase Compliance  X/10   [agent note]               │
│  [icon] Correctness       X/10   [agent note]               │
│  [icon] Security          X/10   [agent note]               │
│  [icon] Completeness      X/10   [agent note]               │
│  ══════════════════════════════════════════════════════     │
│  📊 Overall: X.X/10                                         │
│  STATUS: [PASSED | NEEDS_REVISION | CRITICAL_ISSUES]        │
╰─────────────────────────────────────────────────────────────╯
```
