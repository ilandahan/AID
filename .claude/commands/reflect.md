---
description: Show detailed quality check breakdown or re-evaluate last response
---

# /reflect - Quality Check Deep Dive

## Usage

```
/reflect              # Show detailed breakdown of last quality check
/reflect --history    # Show all quality checks from this session
/reflect --strict     # Re-evaluate last output with threshold 8 (instead of 7)
/reflect --explain <criterion>  # Explain why a criterion got its score
```

## What This Does

The Reflection system automatically runs on every significant output. This command lets you:

1. **See Details** - Understand exactly why each criterion got its score
2. **Re-evaluate** - Run the check again with stricter standards
3. **Learn** - Understand the evaluation criteria better

## When to Use

- When you want to understand why something scored lower
- When you need higher confidence in the output
- When you disagree with a score and want to discuss
- When learning what makes a good output in each phase

---

## Detailed Breakdown Format

When running `/reflect`, show:

```
╭─────────────────────────────────────────────────────────────────────────╮
│ 🔍 Quality Check - Detailed Breakdown                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ Phase: [Current Phase Name]                                             │
│ Output Type: [Code/PRD/Architecture/etc]                                │
│ Iterations: [N]                                                         │
│                                                                         │
│ ═══════════════════════════════════════════════════════════════════    │
│                                                                         │
│ 1. WHY Alignment                                          Score: X/10   │
│    ─────────────────────────────────────────────────────────────────    │
│    ✓ Does it answer the user's underlying need?           [Yes/No]     │
│    ✓ Connected to stated goal?                            [Yes/No]     │
│    ✓ Solving actual problem?                              [Yes/No]     │
│                                                                         │
│    Assessment: [Detailed explanation of score]                          │
│                                                                         │
│ 2. Phase Compliance                                       Score: X/10   │
│    ─────────────────────────────────────────────────────────────────    │
│    ✓ Appropriate for Phase [N]?                           [Yes/No]     │
│    ✓ Not jumping ahead?                                   [Yes/No]     │
│    ✓ Not going back?                                      [Yes/No]     │
│                                                                         │
│    Assessment: [Detailed explanation of score]                          │
│                                                                         │
│ 3. Correctness                                            Score: X/10   │
│    ─────────────────────────────────────────────────────────────────    │
│    ✓ [Phase-specific check 1]                             [Yes/No]     │
│    ✓ [Phase-specific check 2]                             [Yes/No]     │
│    ✓ [Phase-specific check 3]                             [Yes/No]     │
│                                                                         │
│    Assessment: [Detailed explanation of score]                          │
│                                                                         │
│ 4. Security                                               Score: X/10   │
│    ─────────────────────────────────────────────────────────────────    │
│    ✓ [Security check 1]                                   [Yes/No]     │
│    ✓ [Security check 2]                                   [Yes/No]     │
│                                                                         │
│    Assessment: [Detailed explanation of score]                          │
│                                                                         │
│ 5. Completeness                                           Score: X/10   │
│    ─────────────────────────────────────────────────────────────────    │
│    ✓ [Completeness check 1]                               [Yes/No]     │
│    ✓ [Completeness check 2]                               [Yes/No]     │
│                                                                         │
│    Assessment: [Detailed explanation of score]                          │
│                                                                         │
│ ═══════════════════════════════════════════════════════════════════    │
│                                                                         │
│ 📊 Overall Score: X.X/10 (weighted average)                            │
│                                                                         │
│ Weight Distribution:                                                    │
│   WHY Alignment (3) + Phase (2) + Correctness (3) +                    │
│   Security (2) + Completeness (2) = 12 total weight                    │
│                                                                         │
│ Calculation: (W1×3 + P×2 + C×3 + S×2 + Co×2) / 12 = X.X               │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│ 📝 Revision History (if any):                                          │
│                                                                         │
│ Iteration 1: Score 5.2 → Issues: Security (3/10), Completeness (4/10)  │
│   Fixed: Added input validation, included error handling                │
│                                                                         │
│ Iteration 2: Score 7.8 → PASSED                                        │
│                                                                         │
╰─────────────────────────────────────────────────────────────────────────╯
```

---

## --strict Mode

When user runs `/reflect --strict`:

1. Re-evaluate the last output with threshold 8 instead of 7
2. Show what would need to change to meet the higher bar
3. Offer to revise if user wants

```
╭─────────────────────────────────────────────────────────────────────────╮
│ 🔍 Strict Mode Evaluation (threshold: 8)                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ Current Score: 7.4/10                                                   │
│ Strict Threshold: 8.0/10                                                │
│ Status: ❌ Would NOT pass strict mode                                   │
│                                                                         │
│ To reach 8.0, improve:                                                  │
│   • Correctness: 7→8 (add edge case for empty input)                   │
│   • Completeness: 7→8 (add error message documentation)                │
│                                                                         │
│ Would you like me to revise to meet strict standards? (y/n)            │
│                                                                         │
╰─────────────────────────────────────────────────────────────────────────╯
```

---

## --history Mode

Show all quality checks from the session:

```
╭─────────────────────────────────────────────────────────────────────────╮
│ 🔍 Quality Check History                                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ #  Time     Type              Score    Status                          │
│ ─────────────────────────────────────────────────────────────────────  │
│ 1  10:23   Code Generation    8.8/10   ✅ First attempt                │
│ 2  10:35   Architecture       7.2/10   🔄 After 1 revision             │
│ 3  10:48   Code Generation    9.1/10   ✅ First attempt                │
│ 4  11:02   PRD Section        7.5/10   ⚠️ Borderline                   │
│ 5  11:15   Code Generation    8.4/10   🔄 After 2 revisions            │
│                                                                         │
│ ═══════════════════════════════════════════════════════════════════    │
│                                                                         │
│ Session Statistics:                                                     │
│   Average Score: 8.2/10                                                │
│   First Attempt Pass Rate: 60% (3/5)                                   │
│   Average Revisions: 0.6                                               │
│                                                                         │
│ Common Improvement Areas:                                               │
│   • Security (improved 2 times)                                        │
│   • Completeness (improved 2 times)                                    │
│                                                                         │
╰─────────────────────────────────────────────────────────────────────────╯
```

---

## --explain Mode

Deep dive into a specific criterion:

```
/reflect --explain security
```

Output:

```
╭─────────────────────────────────────────────────────────────────────────╮
│ 🔍 Criterion Explanation: Security                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ Current Phase: 4 (Development)                                          │
│ Last Score: 8/10                                                        │
│                                                                         │
│ What This Criterion Measures:                                           │
│ ─────────────────────────────────────────────────────────────────────  │
│ Security evaluates whether the code follows security best practices    │
│ and doesn't introduce vulnerabilities.                                  │
│                                                                         │
│ Checks Applied:                                                         │
│ ─────────────────────────────────────────────────────────────────────  │
│ ✅ No hardcoded secrets or credentials                                  │
│ ✅ Input validation present                                             │
│ ✅ No SQL injection vulnerabilities                                     │
│ ⚠️  XSS prevention could be stronger                                    │
│ ✅ Authentication properly implemented                                  │
│                                                                         │
│ Why You Got 8/10:                                                       │
│ ─────────────────────────────────────────────────────────────────────  │
│ The code is secure overall. Deducted 2 points because:                 │
│ 1. User-generated content rendered without explicit escaping (-1)      │
│ 2. No Content-Security-Policy header mentioned (-1)                    │
│                                                                         │
│ To Get 10/10:                                                          │
│ ─────────────────────────────────────────────────────────────────────  │
│ • Add explicit HTML escaping for user content                          │
│ • Include CSP header recommendation                                     │
│                                                                         │
╰─────────────────────────────────────────────────────────────────────────╯
```

---

## Integration Notes

This command works with the automatic reflection system. Every significant output already goes through reflection - this command just makes the details visible.

The criteria are loaded from:
`.claude/skills/reflection/criteria/phase-{N}-{name}.yaml`
