# Quality Check Rules

Every significant output MUST go through quality evaluation via the **reflection-agent** (isolated sub-agent).

> ⚠️ **IMPORTANT**: Quality checks use an isolated sub-agent to avoid confirmation bias. See `rules/agents/reflection-agent.md` for isolation rules.

---

## Why Agent-Based (Not Inline)

| Inline Self-Reflection | Agent-Based Reflection |
|------------------------|------------------------|
| Same context as work | Isolated context |
| Knows reasoning → agrees | No reasoning → objective |
| Scores trend to 10/10 | Scores based on merit |
| Can't verify claims | Reads source files |

**Rule**: Always spawn reflection-agent. Never evaluate your own work inline.

---

## When to Apply Quality Check

| Apply (Spawn Agent) | Skip |
|---------------------|------|
| Code generation | Simple questions |
| Architecture decisions | Status checks |
| PRD/requirements | File reading |
| Technical specs | Clarifying questions |
| Test writing | Command help |

---

## Process

1. **Generate draft** (internal)
2. **Extract isolation context** (see below)
3. **Spawn reflection-agent** with isolated inputs
4. **Parse response** - if pass=false, apply guidance
5. **Revise and re-spawn** (max 3 times)
6. **Display Quality Check box** with agent's scores

---

## Isolation Context (CRITICAL)

Pass to agent:
- `{{ORIGINAL_REQUEST}}` - User's exact request (**VERBATIM**)
- `{{STATED_WHY}}` - The established WHY (**EXACT TEXT**)
- `{{OUTPUT_TO_EVALUATE}}` - Your draft
- `{{FILES_TO_VERIFY}}` - Content of referenced files
- `{{PHASE_CRITERIA}}` - From criteria YAML

**DO NOT pass**: Conversation history, reasoning, previous attempts, summaries.

---

## Quality Check Display Format

After receiving agent response, display:

```
╭─────────────────────────────────────────────────────────────╮
│ 🔍 Quality Check                                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [icon] WHY Alignment     X/10   [agent's note]             │
│  [icon] Phase Compliance  X/10   [agent's note]             │
│  [icon] Correctness       X/10   [agent's note]             │
│  [icon] Security          X/10   [agent's note]             │
│  [icon] Completeness      X/10   [agent's note]             │
│                                                             │
│  ══════════════════════════════════════════════════════     │
│  📊 Overall: X.X/10                                         │
│  STATUS: PASSED | PASSED after N revision(s) | WARNING      │
│                                                             │
│  [If revised: 📝 Improvements made: ...]                    │
│                                                             │
╰─────────────────────────────────────────────────────────────╯
```

---

## Score Icons

| Score | Icon | Action |
|-------|------|--------|
| 8-10 | ✅ | Excellent - show output |
| 6-7.9 | ⚠️ | Acceptable - show with notes |
| 0-5.9 | ❌ | Revise based on agent guidance (up to 3 times) |

---

## Scoring Criteria (Weights)

| Criterion | Weight | Focus |
|-----------|--------|-------|
| WHY Alignment | 3 | Does output serve the stated WHY? |
| Phase Compliance | 2 | Appropriate for current phase? |
| Correctness | 3 | Accurate? Verified in source files? |
| Security | 2 | No vulnerabilities or exposed secrets? |
| Completeness | 2 | All parts of original request addressed? |

**Total Weight: 12**
**Pass Threshold: 7.0/10**

---

## Revision Rules

1. **Max 3 agent evaluations** before showing output
2. **Apply revision_guidance** from agent response
3. **Track improvements** - Show what changed: `"Security 5→8/10 Fixed: Added validation"`
4. **Escalate if stuck** - If can't reach 7.0 after 3 tries, show with warning
5. **Never hide low scores** - Transparency builds trust

---

## Auto-Fail Conditions

Agent will automatically score < 6 for:
- Phase violations (doing Phase 4 work in Phase 2)
- Security vulnerabilities (injection, XSS, exposed secrets)
- Output doesn't address original request
- Output contradicts stated WHY

---

## Quality Commands

| Command | Purpose |
|---------|---------|
| `/reflect` | Show detailed breakdown of last quality check |
| `/reflect --session` | Run session review (project load perspective) |
| `/reflect --history` | Show all quality checks from session |
| `/reflect --strict` | Re-evaluate with threshold 8.0 |

---

## Related Rules

- `rules/agents/reflection-agent.md` - Full isolation rules
- `rules/general/why-first.md` - WHY extraction rules
- `rules/general/phase-gates.md` - Phase compliance rules
