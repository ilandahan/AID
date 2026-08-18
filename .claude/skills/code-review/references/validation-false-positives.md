# Validation & Audit False Positives Guide

Patterns that cause false positives in automated validation systems, linters, and audit tools.

**Key Principle:** False positives erode user trust. Each false positive trains users to ignore warnings.

---

## Why This Matters for Code Review

When reviewing code that implements validation/audit systems, check for these anti-patterns:

| If You See | Check For |
|------------|-----------|
| Fuzzy/distance matching | Dictionary collision |
| Strict format validation | Valid format variations |
| Universal rules | Context-dependent applicability |
| Threshold-based checks | Real-world threshold values |
| Container/parent checks | Correct scope (content vs container) |
| Consistency checks | Intentional variance |

---

## False Positive Categories

### 1. Dictionary Collision (Fuzzy Matching)

**Symptom:** Levenshtein distance or fuzzy matching flags valid terms as typos.

**Example:**
```
"Outline" vs "Outlined" → distance = 1 → FALSE POSITIVE!
```

Both are valid terms in the dictionary, but fuzzy matching sees them as "close enough to be a typo."

**Fix Pattern:**
```typescript
// ❌ WRONG: Check distance first
for (const correct of dictionary) {
  const distance = levenshtein(value, correct);
  if (distance <= 2 && distance > 0) {
    flagAsTypo(value, correct);  // May flag valid terms!
  }
}

// ✅ CORRECT: Check exact match FIRST
const isExactMatch = dictionary.some(term =>
  term.toLowerCase() === value.toLowerCase()
);
if (isExactMatch) {
  return valid(); // Skip fuzzy matching for exact matches
}
// Then do fuzzy matching
```

**Review Question:** "Does this fuzzy matcher first check if the value is already a valid dictionary term?"

---

### 2. Format Variation Blindness

**Symptom:** Validator enforces ONE format when multiple are valid.

**Examples:**
| Domain | Valid Variations |
|--------|-----------------|
| Component names | "Button", "UI / Button", "buttons/primary" |
| State names | "Default", "Rest", "Normal" |
| Date formats | ISO 8601, Unix timestamp, human-readable |
| Version strings | "1.0.0", "v1.0.0", "1.0" |

**Fix Pattern:**
```typescript
// ❌ WRONG: Single format required
if (!name.includes('/')) {
  flagAsInvalid(name);
}

// ✅ CORRECT: Accept valid variations
const isMultiPart = name.includes('/');
const isSingleWord = !name.includes(' ') && name.length > 0;
const isKeyValue = name.includes('=');

if (isMultiPart || isSingleWord || isKeyValue) {
  return valid();
}
```

**Review Question:** "Are there other valid formats this validator doesn't recognize?"

---

### 3. Universal Rules on Context-Dependent Domains

**Symptom:** Applying rules meant for one context to all contexts.

**Example:**
```
Rule: "All components must have Focus state"
Applied to: Badge, Avatar, Divider (non-interactive!)
Result: FALSE POSITIVES
```

**Fix Pattern:**
```typescript
// ❌ WRONG: Universal rule
if (!hasFocusState(component)) {
  flagAsMissing('Focus state');
}

// ✅ CORRECT: Context-aware rule
const INTERACTIVE_PATTERNS = [/button/i, /input/i, /link/i, /tab/i];

function isInteractive(name: string): boolean {
  return INTERACTIVE_PATTERNS.some(p => p.test(name));
}

if (isInteractive(component.name) && !hasFocusState(component)) {
  flagAsMissing('Focus state');  // Only for interactive!
}
```

**Review Question:** "Does this rule apply universally, or only to a subset of inputs?"

---

### 4. Arbitrary Threshold Selection

**Symptom:** Threshold values chosen arbitrarily, not based on real-world data.

**Examples:**
| Domain | Arbitrary | Real-World |
|--------|-----------|------------|
| Border radii count | 2 max | 4 (0, 8, 16, 999) |
| Cyclomatic complexity | 10 | Depends on domain |
| Line length | 80 | 120 for modern screens |
| Function arguments | 3 | Context-dependent |

**Fix Pattern:**
```typescript
// ❌ WRONG: Arbitrary threshold
const MAX_RADII = 2;  // Why 2? No justification.

// ✅ CORRECT: Justified threshold with escape hatch
const MAX_RADII = 4;  // Based on real designs: 0 (sharp), small, medium, pill (999)
// Document the reasoning!
```

**Review Question:** "Is this threshold based on real-world data, or is it arbitrary?"

---

### 5. Container vs Content Confusion

**Symptom:** Measuring/validating the container instead of the content.

**Examples:**
| What's Measured | What Should Be Measured |
|-----------------|------------------------|
| COMPONENT_SET frame size | Individual variant size |
| Parent frame context | Component internal structure |
| Array length | Array content |
| File size | Content complexity |

**Fix Pattern:**
```typescript
// ❌ WRONG: Measure container
const width = componentSet.width;  // Container is huge!

// ✅ CORRECT: Measure content
let targetNode = componentSet;
if (componentSet.type === 'COMPONENT_SET') {
  const firstVariant = componentSet.children.find(c => c.type === 'COMPONENT');
  if (firstVariant) {
    targetNode = firstVariant;  // Measure actual variant
  }
}
const width = targetNode.width;
```

**Review Question:** "Is this checking the right level of the hierarchy?"

---

### 6. Intentional Variance Flagged as Inconsistency

**Symptom:** Flagging intentional differences as errors.

**Examples:**
| "Inconsistency" | Why It's Intentional |
|-----------------|---------------------|
| Different layer counts | `hasIcon=true` adds icon layer |
| Different heights | `size=small` vs `size=large` |
| Different colors | `variant=primary` vs `variant=secondary` |
| Different states | `disabled=true` greys out content |

**Fix Pattern:**
```typescript
// ❌ WRONG: Flag as error
if (!allVariantsHaveSameLayerCount(component)) {
  flagAsError('Inconsistent structure');
}

// ✅ CORRECT: Info only, not error
return {
  passed: true,  // Always pass
  message: allSame
    ? 'Consistent structure'
    : 'Layer counts vary (may be intentional for variants like hasIcon)',
  severity: 'info'  // NOT 'error' or 'warning'
};
```

**Review Question:** "Could this 'inconsistency' be intentional due to variants/modes?"

---

### 7. External Context Pollution

**Symptom:** Checking external/parent context instead of internal structure.

**Example:**
```
Check: "Is component wrapped in unnecessary frame?"
Problem: Checks the USER'S CANVAS, not the component!
```

**Fix Pattern:**
```typescript
// ❌ WRONG: Check parent (external context)
if (node.parent.type === 'FRAME' && node.parent.children.length === 1) {
  flagAs('Unnecessary wrapper');  // This is the user's layout!
}

// ✅ CORRECT: Check internal structure only
if ('children' in node) {
  for (const child of node.children) {
    if (isUnnecessaryWrapper(child)) {
      flagAs('Unnecessary internal wrapper');
    }
  }
}
```

**Review Question:** "Is this check looking at internal structure or external context?"

---

## Severity Calibration

Not every issue should block the user:

| Severity | When to Use | Blocks Export? |
|----------|------------|----------------|
| `error` | Functional issues, accessibility violations | Yes |
| `warning` | Best practices, optimization opportunities | No |
| `info` | Suggestions, educational notes | No |

**Rule of Thumb:** If you're unsure, use `info`. Users can upgrade severity in settings.

---

## Code Review Checklist for Validators

When reviewing code that validates/audits other code:

```markdown
### Fuzzy Matching
- [ ] Does fuzzy matcher check for exact dictionary match first?
- [ ] Is edit distance threshold appropriate for word length?

### Format Validation
- [ ] Does validator accept all valid format variations?
- [ ] Is strict format enforcement intentional and documented?

### Context Awareness
- [ ] Does rule apply universally or only to specific contexts?
- [ ] Is there detection logic for context type?

### Thresholds
- [ ] Are threshold values based on real-world data?
- [ ] Is the reasoning documented?

### Scope
- [ ] Is the correct level of hierarchy being checked?
- [ ] Is internal structure checked (not external context)?

### Intentional Variance
- [ ] Could flagged "inconsistencies" be intentional?
- [ ] Is severity appropriate (info vs error)?
```

---

## References

### Figma Plugin Example

The Figma component auditor ([ComponentAuditor.ts](../../../integrations/figma-plugin/ComponentAuditor.ts)) demonstrates these patterns:

| Issue # | Pattern | Fix |
|---------|---------|-----|
| 1 | Dictionary collision | Line 379-386: Check exact match first |
| 2 | Format variation | Line 281-292: Accept single-word names |
| 3 | Variant format | Line 269-275: Recognize Property=Value |
| 4-6 | Context-dependent | Line 40-61: isInteractiveComponent() |
| 7 | Container confusion | Line 862-870: Measure variant, not set |
| 8 | Arbitrary threshold | Line 666-668: Increase to 4 |
| 9 | Intentional variance | Line 587-596: Info, not error |
| 10 | External context | Line 523-570: Check internal only |

### General References

| Resource | Topic |
|----------|-------|
| [./common-issues.md](../figma-design-review/references/common-issues.md) | Design review false positives |
| ESLint rule configuration | Severity calibration patterns |
| Static analysis best practices | Threshold selection methodology |

---

## Key Takeaways

1. **Exact match before fuzzy match** - Always check if value is already valid
2. **Accept variations** - Multiple valid formats exist in most domains
3. **Context matters** - Not all rules apply universally
4. **Justify thresholds** - Base on data, not intuition
5. **Measure the right thing** - Content, not container
6. **Intentional != Inconsistent** - Variants are meant to differ
7. **Stay in scope** - Check internal structure, not external context
8. **Calibrate severity** - Not everything is an error
