# Debugging Checklist

Quick reference for systematic debugging. Print this and keep it visible.

---

## Before ANY Fix

```
□ Did I read the COMPLETE error message?
□ Can I reproduce it consistently?
□ Did I check recent changes (git diff)?
□ Do I understand WHY it's happening?
```

**If any answer is NO → Stop. Investigate more.**

---

## The Four Phases

### Phase 1: Root Cause Investigation
```
□ Read error messages completely
□ Note line numbers, file paths, error codes
□ Reproduce consistently (exact steps)
□ Check git diff / recent commits
□ Add logging at component boundaries
□ Gather evidence BEFORE proposing fixes
```

### Phase 2: Pattern Analysis
```
□ Find similar WORKING code in codebase
□ Read reference implementation COMPLETELY
□ List ALL differences (nothing is too small)
□ Understand dependencies and assumptions
```

### Phase 3: Hypothesis & Testing
```
□ State hypothesis clearly: "X is broken because Y"
□ Make SMALLEST possible change
□ Test ONE variable at a time
□ If wrong → new hypothesis (don't pile fixes)
```

### Phase 4: Implementation
```
□ Write failing test FIRST
□ Implement SINGLE fix
□ Verify test passes
□ Check for regressions
□ Add defense-in-depth validation
```

---

## Red Flags - STOP Immediately

If you're thinking any of these, STOP and return to Phase 1:

- [ ] "Quick fix for now, investigate later"
- [ ] "Just try changing X and see"
- [ ] "Multiple changes, run tests"
- [ ] "I don't fully understand but might work"
- [ ] "Proposing solutions without tracing data"
- [ ] "One more fix attempt" (after 2+ failures)

---

## Fix Counter

Track your attempts. If ≥3 fixes failed, it's an architecture problem.

```
Fix #1: _______________________ Result: □ Pass □ Fail
Fix #2: _______________________ Result: □ Pass □ Fail
Fix #3: _______________________ Result: □ Pass □ Fail

→ If 3 failed: STOP. Question the architecture.
```

---

## Multi-Component Debugging Template

```
Layer 1: ____________
  Input:  _____________
  Output: _____________
  Status: □ OK □ FAIL

Layer 2: ____________
  Input:  _____________
  Output: _____________
  Status: □ OK □ FAIL

Layer 3: ____________
  Input:  _____________
  Output: _____________
  Status: □ OK □ FAIL

→ Bug is between Layer ___ and Layer ___
```

---

## Root Cause Tracing

```
Error appears at: _______________________
         ↑
Called by: _______________________
         ↑
Called by: _______________________
         ↑
Called by: _______________________
         ↑
SOURCE: _______________________

→ Fix at SOURCE, not at symptom location
```

---

## Defense-in-Depth Checklist

After fixing a bug, add validation at each layer:

```
□ Layer 1 (Entry): Reject invalid input at API boundary
□ Layer 2 (Logic): Validate for this specific operation
□ Layer 3 (Environment): Add guards for test/CI contexts
□ Layer 4 (Debug): Add logging for forensics
```

---

## Time Check

| Debugging Time | Action |
|----------------|--------|
| < 30 min | Normal - continue systematic approach |
| 30-60 min | Review: Am I following the process? |
| > 60 min | STOP. Rubber duck. Get fresh eyes. |
| > 2 hours | Likely architecture issue. Escalate. |

---

## Quick Commands

```bash
# Recent changes
git diff HEAD~5

# Find who changed file
git log --oneline -10 -- path/to/file

# Find when line was added
git blame path/to/file

# Find polluting test
./find-polluter.sh '.git' 'src/**/*.test.ts'

# Check file sizes
./check-file-size.sh src/ --ci
```

---

## Post-Fix Checklist

```
□ Test passes
□ No regressions
□ Defense-in-depth added
□ Root cause documented
□ Similar bugs prevented
```
