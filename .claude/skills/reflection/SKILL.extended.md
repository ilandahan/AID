# Reflection & Self-Critique Skill

## Overview

This skill implements **automatic transparent quality checks** on all significant outputs.
Every response goes through a self-critique loop before being presented to the user,
with results always visible to build trust and ensure quality.

---

## Core Principle

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Prompt    │ ───► │   Draft     │ ───► │  Reflect    │ ───► │   Output    │
└─────────────┘      └─────────────┘      └─────────────┘      └─────────────┘
                      (internal)          (score & improve)    (with QC box)
```

---

## When to Apply Quality Check

### Always Apply To:
- Code generation (any language)
- Architecture and design decisions
- PRD sections and requirements
- Technical specifications
- Test writing
- Implementation plans
- API designs
- Database schemas

### Skip For:
- Simple questions ("what's the current phase?")
- Status checks (`/aid-status`)
- File reading confirmations
- Clarifying questions back to user
- Command help requests
- Conversation/chat without deliverables

---

## Quality Check Display Format

### Standard Format (Always Show)

```
╭─────────────────────────────────────────────────────────────╮
│ 🔍 Quality Check                                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [ICON] WHY Alignment     X/10   [brief note]               │
│  [ICON] Phase Compliance  X/10   [brief note]               │
│  [ICON] Correctness       X/10   [brief note]               │
│  [ICON] Security          X/10   [brief note]               │
│  [ICON] Completeness      X/10   [brief note]               │
│                                                             │
│  ══════════════════════════════════════════════════════    │
│  📊 Overall: X.X/10                                         │
│  [STATUS LINE]                                              │
│                                                             │
│  [OPTIONAL: Improvements made / Recommendations]            │
│                                                             │
╰─────────────────────────────────────────────────────────────╯
```

### Score Icons

| Score Range | Icon | Meaning |
|-------------|------|---------|
| 8-10 | ✅ | Excellent - meets high standards |
| 6-7.9 | ⚠️ | Acceptable - minor concerns noted |
| 0-5.9 | ❌ | Needs revision - should not appear in final output |

### Status Lines

| Scenario | Status Line |
|----------|-------------|
| First attempt, score ≥ 7 | `✅ PASSED on first attempt` |
| Passed after N revisions | `🔄 PASSED after N revision(s)` |
| Borderline (7.0-7.5) | `⚠️ PASSED with notes` |
| Max revisions reached | `⚠️ PASSED (max revisions) - review recommended` |

---

## Criteria Definitions

### Universal Criteria (All Phases)

#### 1. WHY Alignment (Weight: 3)
Does the output serve the user's underlying need?
- Did I understand what they really want?
- Does this solve their actual problem?
- Is the response connected to their stated goal?

#### 2. Phase Compliance (Weight: 2)
Is this appropriate for the current development phase?
- Am I staying within phase boundaries?
- Not jumping ahead to implementation?
- Not going back to already-decided matters?

#### 3. Correctness (Weight: 3)
Is the content accurate and functional?
- For code: Does it work? Syntax errors?
- For specs: Are facts accurate?
- For plans: Is the logic sound?

#### 4. Security (Weight: 2)
Are there security concerns?
- No exposed secrets or credentials?
- No vulnerabilities (OWASP top 10)?
- Data handling is safe?

#### 5. Completeness (Weight: 2)
Does it cover everything requested?
- All requirements addressed?
- No missing critical pieces?
- Edge cases considered?

---

## Phase-Specific Criteria

Detailed criteria for each phase are in:
- `criteria/phase-0-discovery.yaml`
- `criteria/phase-1-prd.yaml`
- `criteria/phase-2-tech-spec.yaml`
- `criteria/phase-3-impl-plan.yaml`
- `criteria/phase-4-development.yaml`
- `criteria/phase-5-qa-ship.yaml`

---

## Reflection Process

### Step 1: Generate Draft (Internal)
Create the initial response without showing to user.

### Step 2: Apply Criteria
Load criteria for current phase and evaluate:

```yaml
evaluation:
  why_alignment:
    score: 8
    note: "Addresses the original need"
  phase_compliance:
    score: 10
    note: "Appropriate for Phase 4"
  correctness:
    score: 7
    note: "Code works, missing one edge case"
  security:
    score: 9
    note: "No security issues found"
  completeness:
    score: 8
    note: "Covers most requirements"
```

### Step 3: Calculate Overall Score
Weighted average based on criteria weights.

### Step 4: Decision

```
IF overall_score >= 7:
    → Show Quality Check box + response
ELSE IF iterations < 3:
    → Revise internally based on lowest scores
    → Go back to Step 2
ELSE:
    → Show Quality Check with warning
    → Show response with recommendation to review
```

### Step 5: Display
Always show the Quality Check box before the response.

---

## Revision Behavior

When revising, focus on:
1. Criteria with score < 7 (priority)
2. Specific issues identified
3. Do NOT over-engineer or add unrequested features

### Showing Improvements
When a score improved due to revision, display as:

```
│  ⚠️  Security         5→8/10 Fixed: Added input validation   │
```

And add improvements section:

```
│  📝 Improvements made:                                      │
│     • Added input sanitization for email field              │
│     • Added null check before processing                    │
```

---

## Examples

### Example 1: Clean Pass

```
╭─────────────────────────────────────────────────────────────╮
│ 🔍 Quality Check                                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ✅ WHY Alignment     9/10   Addresses the original need    │
│  ✅ Phase Compliance  10/10  Appropriate for Phase 4        │
│  ✅ Correctness       8/10   Code is valid and working      │
│  ✅ Security          8/10   No security issues found       │
│  ✅ Completeness      9/10   Covers all requirements        │
│                                                             │
│  ══════════════════════════════════════════════════════    │
│  📊 Overall: 8.8/10                                         │
│  ✅ PASSED on first attempt                                 │
│                                                             │
╰─────────────────────────────────────────────────────────────╯
```

### Example 2: Pass After Revision

```
╭─────────────────────────────────────────────────────────────╮
│ 🔍 Quality Check                                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ✅ WHY Alignment     9/10   Addresses the original need    │
│  ✅ Phase Compliance  10/10  Appropriate for Phase 4        │
│  ✅ Correctness       8/10   Code is valid                  │
│  ⚠️  Security         5→8/10 Fixed: Added input validation  │
│  ✅ Completeness      9/10   Covers all requirements        │
│                                                             │
│  ══════════════════════════════════════════════════════    │
│  📊 Overall: 8.6/10                                         │
│  🔄 PASSED after 1 revision                                 │
│                                                             │
│  📝 Improvements made:                                      │
│     • Added input sanitization for user input               │
│     • Added parameterized query to prevent SQL injection    │
│                                                             │
╰─────────────────────────────────────────────────────────────╯
```

### Example 3: Borderline Pass with Notes

```
╭─────────────────────────────────────────────────────────────╮
│ 🔍 Quality Check                                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ✅ WHY Alignment     8/10   Addresses the original need    │
│  ✅ Phase Compliance  10/10  Appropriate for Phase 2        │
│  ⚠️  Correctness      7/10   May be missing edge cases      │
│  ✅ Security          8/10   No security issues found       │
│  ⚠️  Completeness     7/10   Partial coverage               │
│                                                             │
│  ══════════════════════════════════════════════════════    │
│  📊 Overall: 7.4/10                                         │
│  ⚠️ PASSED with notes                                       │
│                                                             │
│  💡 Recommendation:                                         │
│     Consider reviewing edge cases for error handling.       │
│     The current design covers main flows but may need       │
│     additional error scenarios defined.                     │
│                                                             │
╰─────────────────────────────────────────────────────────────╯
```

---

## User Commands

| Command | Description |
|---------|-------------|
| `/reflect` | Show detailed breakdown of last quality check |
| `/reflect --history` | Show all quality checks from current session |
| `/reflect --strict` | Re-evaluate last output with threshold 8 instead of 7 |
| `/reflect --explain [criterion]` | Explain why a specific criterion got its score |

---

## Integration with AID Phases

The reflection system automatically loads phase-appropriate criteria:

| Phase | Focus Areas |
|-------|-------------|
| 0 Discovery | Research quality, bias avoidance, scope appropriateness |
| 1 PRD | User story quality, acceptance criteria clarity, WHY traceability |
| 2 Tech Spec | Architecture soundness, trade-off documentation, integration |
| 3 Impl Plan | Task breakdown quality, dependency mapping, estimation |
| 4 Development | Code quality, security, test coverage, documentation |
| 5 QA & Ship | Test coverage, acceptance criteria met, deployment readiness |

---

## Configuration

Settings in `.aid/config.yaml`:

```yaml
reflection:
  enabled: true
  threshold: 7
  max_iterations: 3
  show_quality_check: always  # always | on_revision | on_warning
  language: english           # english only
```

---

## Why This Matters

1. **Trust Building** - Users see their output went through QA
2. **Consistency** - Same quality bar applied to every deliverable
3. **Learning** - Users learn what criteria matter over time
4. **Discussion Basis** - If user disagrees with score, there's a starting point
5. **Documentation** - Quality trends visible over time
