# Reflection Skill

Automatic quality check on all significant outputs. Always show results to user.

## When to Apply

Apply: Code, architecture, PRD, specs, tests, plans, APIs, schemas
Skip: Simple questions, status checks, file reading, clarifying questions, help

## Process

1. Generate draft internally
2. Score against 5 criteria (see below)
3. If overall < 7: revise (max 3 times)
4. Show Quality Check box + response

## Quality Check Format

```
Quality Check
─────────────────────────────────────────
WHY Alignment     X/10  [note]
Phase Compliance  X/10  [note]
Correctness       X/10  [note]
Security          X/10  [note]
Completeness      X/10  [note]
─────────────────────────────────────────
Overall: X.X/10
Status: PASSED | PASSED after N revision(s) | PASSED with notes
[If revised: Improvements made: ...]
```

## Criteria

1. WHY Alignment (weight 3): Does output serve user's actual need?
2. Phase Compliance (weight 2): Appropriate for current phase?
3. Correctness (weight 3): Accurate, functional, no errors?
4. Security (weight 2): No vulnerabilities or exposed secrets?
5. Completeness (weight 2): All requirements addressed?

Total weight: 12. Overall = weighted sum / 12.

## Score Thresholds

- 8-10: Excellent, show output
- 6-7.9: Acceptable, show with notes
- 0-5.9: Revise internally

## Revision Display

When score improved: `Security 5->8/10 Fixed: Added input validation`

Add section: `Improvements made: [list of fixes]`

## Status Lines

- Score >= 7 first try: PASSED on first attempt
- Score >= 7 after revision: PASSED after N revision(s)
- Score 7.0-7.5: PASSED with notes
- Max revisions reached: PASSED (max revisions) - review recommended

## Phase-Specific Criteria

Load from: criteria/phase-{N}-{name}.yaml

Phase focus areas:
- 0 Discovery: Research quality, bias avoidance, scope
- 1 PRD: User stories, acceptance criteria, WHY traceability
- 2 Tech Spec: Architecture soundness, trade-offs, integration
- 3 Impl Plan: Task breakdown, dependencies, estimation
- 4 Development: Code quality, security, tests, docs
- 5 QA Ship: Test coverage, acceptance criteria, deployment readiness

## Commands

- /reflect: Detailed breakdown of last check
- /reflect --history: All checks from session
- /reflect --strict: Re-evaluate with threshold 8
- /reflect --explain [criterion]: Deep dive into score
