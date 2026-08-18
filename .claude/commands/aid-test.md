---
description: Run AID methodology test as isolated sub-agent with ultrathink quality verification
---

# /aid-test

Launch an isolated sub-agent to test AID methodology (Phases 0-3) with **ultrathink** quality verification at each step.

## Usage

```
/aid-test              # Full test (Phases 0-3) with ultrathink
/aid-test --phase 0    # Test only Phase 0
/aid-test --phase 3    # Test only Phase 3 (including sub-phases 3a, 3b, 3c)
/aid-test --quick      # 1 output per phase (still uses ultrathink)
/aid-test --verbose    # Show all reflection + thinking details
```

## What This Does

Launches a **sub-agent** that runs independently to:
1. Simulate realistic outputs for each phase
2. **Use ultrathink** on every simulated user message for deep quality verification
3. Run quality checks with reflection
4. Test deliberate failures (verify bad content is caught)
5. Validate phase gate transitions
6. **Test Phase 3 sub-phases** (consolidation, breakdown, JSON export)
7. Generate comprehensive test report with thinking analysis

## Ultrathink Integration

**CRITICAL**: Every simulated user message in the test MUST include `ultrathink` to trigger extended thinking for quality verification.

### Why Ultrathink?

| Without Ultrathink | With Ultrathink |
|-------------------|-----------------|
| Quick surface-level check | Deep reasoning about correctness |
| May miss edge cases | Catches subtle issues |
| Basic validation | Comprehensive quality analysis |
| Standard output | Verified, high-confidence output |

### Ultrathink Message Format

Each simulated user message follows this pattern:

```
[SIMULATED USER - STEP N]
ultrathink

{actual user request}

VERIFY:
- [ ] Output matches phase requirements
- [ ] WHY alignment maintained
- [ ] No phase gate violations
- [ ] Quality score >= 7
```

## Execution

When this command is invoked, use the Task tool to launch a sub-agent:

```
Task(
  subagent_type: "general-purpose",
  prompt: "You are the AID Test Agent with ULTRATHINK verification.

CRITICAL INSTRUCTION: For EVERY simulated user message, you MUST:
1. Include 'ultrathink' keyword to trigger extended thinking
2. Use deep reasoning to verify quality before producing output
3. Log thinking insights in the test report

Read and follow .claude/agents/aid-test-agent/AGENT-PROMPT.md exactly.

Run the complete test sequence for Phases 0-3.
For Phase 3, test all sub-phases (3a: Consolidation, 3b: Task Breakdown, 3c: JSON Export).

ULTRATHINK VERIFICATION CHECKLIST (apply to each step):
□ Is the output correct for this phase?
□ Does it follow WHY-driven principles?
□ Are there any edge cases missed?
□ Would this pass a thorough code review?
□ Is the quality score >= 7?

Generate all outputs to .aid/test-outputs/test-{timestamp}/.
Include thinking-log.md with ultrathink insights.
Return a summary when complete.",
  description: "AID methodology test with ultrathink"
)
```

## Isolation

The sub-agent:
- Does NOT modify project state (.aid/state.json)
- Does NOT create docs/ files
- Does NOT interact with external services (no Jira MCP)
- Only writes to .aid/test-outputs/
- Uses JSON export instead of Jira for Phase 3c

## Expected Output

Sub-agent returns summary:

```
AID Test Complete (with Ultrathink Verification)
=====================================
Test ID: 20260105-143022
Duration: 15 min
Thinking Mode: ULTRATHINK (extended reasoning)

Phase Results:
  Phase 0: 3/3 passed, gate OK
    └─ Ultrathink verified: 3/3 ✓
  Phase 1: 3/3 passed, gate OK
    └─ Ultrathink verified: 3/3 ✓
  Phase 2: 3/3 passed, gate OK
    └─ Ultrathink verified: 3/3 ✓
  Phase 3:
    3a (Consolidation): 5/5 passed
      └─ Ultrathink verified: 5/5 ✓
    3b (Breakdown): 4/4 passed
      └─ Ultrathink verified: 4/4 ✓
    3c (JSON Export): 5/5 passed
      └─ Ultrathink verified: 5/5 ✓
    Gate: OK

JSON Validation:
  Epics: 3
  Stories: 12
  Tasks: 28
  Dependencies valid: 28/28
  Information complete: 28/28

Ultrathink Quality Summary:
  Total steps verified: 23
  Deep reasoning applied: 23/23 ✓
  Edge cases caught: 4
  Quality improvements: 2

Reflection Validation: 7/7 violations detected

Overall: PASSED ✓

Reports:
  .aid/test-outputs/test-20260105-143022/report.md
  .aid/test-outputs/test-20260105-143022/thinking-log.md
```

## Test Artifacts

All outputs saved to:
```
.aid/test-outputs/test-{timestamp}/
  session.json          # Test metadata
  thinking-log.md       # NEW: Ultrathink insights for each step
  phase-0/
    research-summary.md
    stakeholder-analysis.md
    competitive-analysis.md
  phase-1/
    user-stories.md
    requirements.md
    scope.md
  phase-2/
    architecture-overview.md
    data-model.md
    api-design.md
  phase-3/
    consolidated-spec.md         # From 3a
    contradiction-log.md         # From 3a
    task-breakdown.md            # From 3b
    task-breakdown.json          # From 3c (CRITICAL)
    sprint-plan.yaml             # From 3b
    risks.md                     # From 3b
    validation-report.md         # JSON validation summary
  report.md             # Full test report
```

## What's Validated

| Area | Checks | Ultrathink Adds |
|------|--------|-----------------|
| Reflection | Catches phase violations, missing WHY, security gaps | Deep reasoning verification |
| Scoring | Good content >= 7, bad content < 7 | Edge case analysis |
| Gates | Required files exist, proper transitions | Transition logic verification |
| Phases | No jumping ahead, appropriate content | Content quality deep-dive |
| Phase 3a | Contradictions detected, resolution hierarchy | Resolution reasoning |
| Phase 3b | Task structure, estimates < 4 hrs, dependencies | Dependency logic check |
| Phase 3c | JSON valid, all tasks complete, dependencies linked | Schema completeness |

## Ultrathink Verification Steps

### For Each Phase Step:

```
┌──────────────────────────────────────────────────────────────┐
│  STEP: [Phase N - Step Name]                                 │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  1. TRIGGER: "ultrathink" keyword in message                 │
│                                                              │
│  2. EXTENDED THINKING:                                       │
│     • Analyze requirements deeply                            │
│     • Consider edge cases                                    │
│     • Verify WHY alignment                                   │
│     • Check for potential issues                             │
│                                                              │
│  3. GENERATE OUTPUT with confidence                          │
│                                                              │
│  4. VERIFY OUTPUT:                                           │
│     □ Matches phase requirements?                            │
│     □ WHY clearly stated?                                    │
│     □ No security issues?                                    │
│     □ Quality >= 7?                                          │
│                                                              │
│  5. LOG THINKING to thinking-log.md                          │
│                                                              │
╰──────────────────────────────────────────────────────────────╯
```

## Thinking Log Format

The `thinking-log.md` file captures ultrathink insights:

```markdown
# Ultrathink Verification Log

## Test ID: {timestamp}

---

### Step 1: Phase 0 - Research Summary

**Trigger:** ultrathink

**Extended Thinking:**
- Analyzed market research requirements
- Considered: competitor analysis depth, stakeholder needs
- Edge case: What if no direct competitors exist?
- WHY alignment: Research supports informed decision-making

**Verification:**
- [x] Output matches phase requirements
- [x] WHY alignment maintained
- [x] No phase gate violations
- [x] Quality score: 8/10

**Insights:**
- Added competitor alternative analysis section
- Improved stakeholder priority ranking

---

### Step 2: Phase 1 - User Stories
...
```

## Phase 3 Specific Tests (with Ultrathink)

### Phase 3a: Consolidation
- `ultrathink` Entry message displayed
- `ultrathink` PRD read section by section - verify completeness
- `ultrathink` Tech Spec read section by section - verify alignment
- `ultrathink` Research read (if exists) - verify relevance
- `ultrathink` Contradictions detected - verify resolution logic
- `ultrathink` Resolution hierarchy followed - verify reasoning
- `ultrathink` User approval simulated - verify approval criteria

### Phase 3b: Task Breakdown
- `ultrathink` Epics → Stories → Tasks hierarchy - verify structure
- `ultrathink` Each task requirements - verify completeness
- `ultrathink` Estimates < 4 hours - verify reasonableness
- `ultrathink` Dependencies mapped - verify no circular deps
- `ultrathink` Critical path identified - verify logic
- `ultrathink` Sprint assignments - verify capacity

### Phase 3c: JSON Export
- `ultrathink` Valid JSON structure - verify schema
- `ultrathink` All tasks have business_context - verify PRD tracing
- `ultrathink` All tasks have technical_notes - verify Tech Spec tracing
- `ultrathink` All tasks have spec_section_refs - verify references
- `ultrathink` All dependency IDs valid - verify no orphans
- `ultrathink` Complete information - verify developer can work standalone
