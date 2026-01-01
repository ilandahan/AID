# Common Issues and Fixes

Frequently encountered problems in Figma component reviews and how to resolve them.

---

## Implementation Issues

### 1. Layout Artifacts (`translate-x-[-50%]`)

**Symptom:**
```jsx
<div className="... translate-x-[-50%]">
```

**Cause:** 
Figma centering using absolute positioning instead of Auto Layout.

**Impact:** -5 points (Visual Consistency)

**Fix in Figma:**
1. Select the problematic frame
2. Remove absolute positioning
3. Apply Auto Layout to parent
4. Use `justify-content: center` instead

**Prevention:**
- Always use Auto Layout for centering
- Avoid manual X/Y position offsets
- Use constraints relative to parent, not canvas

---

### 2. Missing Focus State

**Symptom:**
No `:focus` or `:focus-visible` variant in component set.

**Impact:** -8 points (Accessibility States) - **CRITICAL**

**Why it matters:**
- Keyboard users cannot see where they are
- WCAG 2.4.7 failure
- Blocks export

**Fix in Figma:**
1. Duplicate Default state
2. Rename to `State=Focus`
3. Add visible focus indicator:
   - Blue outline (2px)
   - Offset from border (2px)
   - Or inner glow effect

**Correct styling:**
```css
/* In generated code, add: */
&:focus-visible {
  outline: 2px solid var(--color/azure/48);
  outline-offset: 2px;
  box-shadow: 0 0 0 4px rgba(12, 140, 233, 0.2);
}
```

---

### 3. Inconsistent Font-Weight

**Symptom:**
```jsx
// Variant A
font-weight: 600

// Variant B (same visual role)
font-weight: 500
```

**Impact:** -5 points (Visual Consistency)

**Cause:**
- Different font files applied
- Manual override in some variants
- Copy-paste from different source

**Fix in Figma:**
1. Create Text Style for button labels
2. Apply same style to all variants
3. Use font weight from style, not override

**Detection:**
Look for `font-[var(--font-weight/600,500)]` - the mismatch in default vs override indicates inconsistency.

---

### 4. Hardcoded Colors

**Symptom:**
```jsx
// Bad
background: #0c8ce9

// Good
background: var(--color/azure/48, #0c8ce9)
```

**Impact:** -10 points (Token System)

**Fix in Figma:**
1. Create Color Styles for all colors
2. Apply styles to all fills/strokes
3. Name semantically: `color/azure/48`

**Verification:**
Check generated code for `var(--color/...)` usage. All colors should use variables with fallbacks.

---

### 5. Missing Disabled State for Some Sizes

**Symptom:**
- Full + Disabled: ✅ exists
- Medium + Disabled: ✅ exists
- Compact + Disabled: ❌ missing

**Impact:** -6 points per missing variant (Accessibility States)

**Fix in Figma:**
1. Identify missing combinations
2. Duplicate nearest variant
3. Apply disabled styling:
   - Grey background (#6C757D)
   - Reduced opacity text
   - Remove shadow
4. Name correctly: `Size=Compact, State=Disabled, Style=Primary`

---

### 6. Code Duplication

**Symptom:**
```jsx
if (size === "Full" && state === "Default") {
  return (
    <div className="px-8 py-4 rounded-md bg-blue-500">
      <span className="text-white font-semibold">{label}</span>
    </div>
  );
}
if (size === "Full" && state === "Hover") {
  return (
    <div className="px-8 py-4 rounded-md bg-blue-600">
      <span className="text-white font-semibold">{label}</span>
    </div>
  );
}
// 16 more variants with same structure...
```

**Impact:** -5 points (Code Quality)

**Root Cause:**
Figma MCP generates separate branches for each variant. This is expected but can be optimized post-export.

**Post-Export Fix:**
```jsx
const sizeClasses = {
  Full: "px-8 py-4",
  Medium: "px-6 py-3",
  Compact: "px-4 py-2",
};

const stateClasses = {
  Default: "bg-blue-500",
  Hover: "bg-blue-600 shadow-lg",
  Disabled: "bg-gray-400 cursor-not-allowed",
};

return (
  <div className={`rounded-md ${sizeClasses[size]} ${stateClasses[state]}`}>
    <span className="text-white font-semibold">{label}</span>
  </div>
);
```

---

## Metadata Issues

### 7. Missing or Vague Description

**Symptom:**
```yaml
# Bad
description: "A button"

# Good
description: "Primary CTA button for lead capture on homepage hero section. Triggers contact form modal and sends inquiry to sales team. Used as the main conversion element above the fold."
```

**Impact:** -20 points (Description)

**Fix Template:**
```
[What it is]. [What it does]. [Where/when to use it].
```

**Examples by Component Type:**

**Button:**
```
Primary action button for form submissions. Triggers main conversion events and provides visual feedback on interaction. Use for single primary actions per viewport.
```

**Input:**
```
Text input field with validation support. Handles user text entry with real-time validation feedback. Use in forms requiring text data entry.
```

**Card:**
```
Product display card for e-commerce listings. Shows product image, title, price, and quick-add action. Use in product grids and carousels.
```

---

### 8. Insufficient Tags

**Symptom:**
```yaml
# Bad
tags: button

# Good  
tags: button, cta, lead, homepage, hero, conversion, primary, action, form-trigger
```

**Impact:** -7 points (Searchability)

**Tag Categories to Cover:**
1. **Type:** button, input, card, modal
2. **Purpose:** cta, navigation, display, form
3. **Location:** hero, sidebar, footer, modal
4. **Action:** submit, cancel, navigate, toggle
5. **Style:** primary, secondary, tertiary
6. **State:** interactive, static, loading

---

### 9. Missing Dev Metadata

**Symptom:**
```yaml
# Missing these fields:
testId: ???
ariaLabel: ???
analytics: ???
```

**Impact:** -5 points each (Dev Metadata)

**Fix - Standard Patterns:**

**testId:**
```yaml
# Pattern: {type}-{purpose}-{action}
testId: btn-lead-send
testId: input-email-validation
testId: card-product-quick-add
```

**ariaLabel:**
```yaml
# Pattern: {action} {context}
ariaLabel: Send message to start a conversation
ariaLabel: Enter your email address
ariaLabel: Add product to cart
```

**analytics:**
```yaml
# Pattern: {noun}_{verb} or {feature}_{action}
analytics: lead_button_click
analytics: product_card_view
analytics: form_submit_success
```

---

### 10. Missing Do's and Don'ts

**Symptom:**
No usage guidelines for component.

**Impact:** -14 points (Usage Guidelines)

**Fix - Template by Component Type:**

**Buttons:**
```yaml
dos:
  - Use Primary for single main action per viewport
  - Use Secondary alongside Primary for alternative actions
  - Keep label text short (2-3 words max)
  - Use Full size on mobile breakpoints

donts:
  - Don't use multiple Primary buttons in same section
  - Don't use Compact for important actions
  - Don't change button colors outside design system
  - Don't use disabled state without explaining why
```

**Inputs:**
```yaml
dos:
  - Always include label (don't rely on placeholder)
  - Show validation state immediately after blur
  - Provide helper text for complex requirements
  - Use appropriate input type (email, tel, etc.)

donts:
  - Don't use placeholder as label replacement
  - Don't show error before user interaction
  - Don't disable autocomplete without reason
  - Don't make required fields unclear
```

**Cards:**
```yaml
dos:
  - Maintain consistent aspect ratio in grids
  - Use lazy loading for images
  - Provide meaningful alt text
  - Keep content hierarchy clear

donts:
  - Don't overflow text without truncation
  - Don't use cards for single items
  - Don't mix card sizes in same row
  - Don't hide critical info on hover
```

---

## Quick Fix Priority Matrix

| Issue | Severity | Points Lost | Fix Time | Priority |
|-------|----------|-------------|----------|----------|
| Missing Focus state | Critical | -8 | 5 min | 🔴 1 |
| Missing Disabled state | Critical | -6 | 5 min | 🔴 2 |
| Missing description | High | -20 | 2 min | 🟠 3 |
| Layout artifacts | Medium | -5 | 10 min | 🟡 4 |
| Hardcoded colors | Medium | -10 | 15 min | 🟡 5 |
| Missing tags | Medium | -7 | 2 min | 🟡 6 |
| Missing testId | Low | -5 | 1 min | 🟢 7 |
| Code duplication | Low | -5 | Post-export | 🟢 8 |

---

## ⚠️ Audit False Positives (Avoid These)

When implementing automated audits, these patterns look like issues but are **actually valid**. Flagging them frustrates users and reduces trust in the audit system.

### False Positive Categories

#### 1. Dictionary Collision in Typo Detection

**Problem:** Fuzzy matching (Levenshtein distance) flags "Outline" as a typo for "Outlined" (distance = 1).

**Both are valid terms!** The dictionary contains both, so the checker flags valid terms.

**Fix Pattern:**
```typescript
// WRONG: Check distance first
if (distance <= 2) {
  flagAsTypo(value, closestMatch);
}

// CORRECT: Check exact match FIRST, then distance
const isExactMatch = dictionary.some(term =>
  term.toLowerCase() === value.toLowerCase()
);
if (isExactMatch) {
  continue; // Valid term, skip typo check
}
if (distance <= 2) {
  flagAsTypo(value, closestMatch);
}
```

**Reference:** [ComponentAuditor.ts:379-386](../../../integrations/figma-plugin/ComponentAuditor.ts#L379-L386)

---

#### 2. Single-Word Component Names

**Problem:** Audit requires "Category / Type" format, but rejects "Button", "Icon", "Card".

**Single-word names are valid!** Many atomic components have simple names.

**Fix Pattern:**
```typescript
// WRONG: Require multi-part names
if (!name.includes('/')) {
  flagAsInvalid(name);
}

// CORRECT: Allow single-word, suggest organization
const parts = name.split('/');
if (parts.length === 1 && parts[0].length > 0) {
  // Valid single-word name
  return { passed: true, suggestion: 'Consider Category / Type for organization' };
}
```

**Reference:** [ComponentAuditor.ts:281-292](../../../integrations/figma-plugin/ComponentAuditor.ts#L281-L292)

---

#### 3. Variant Name Format

**Problem:** "Size=Full, State=Hover" flagged as not following "Category / Type" format.

**Variant names use `Property=Value` format!** This is Figma's standard variant naming.

**Fix Pattern:**
```typescript
// CORRECT: Check for variant format first
if (name.includes('=')) {
  return { passed: true, message: 'Variant uses Property=Value format (correct)' };
}
// Then check component naming rules
```

**Reference:** [ComponentAuditor.ts:269-275](../../../integrations/figma-plugin/ComponentAuditor.ts#L269-L275)

---

#### 4. Focus State on Non-Interactive Components

**Problem:** Audit requires Focus state for ALL component sets, even Badge, Avatar, Divider.

**Non-interactive components don't need Focus!** Only interactive elements need keyboard navigation.

**Interactive Component Detection:**
```typescript
const INTERACTIVE_PATTERNS = [
  /button/i, /btn/i,
  /input/i, /field/i, /text-?area/i,
  /select/i, /dropdown/i, /picker/i,
  /checkbox/i, /radio/i, /toggle/i, /switch/i,
  /tab/i, /menu/i, /nav/i,
  /link/i, /anchor/i,
  /slider/i, /range/i,
  /modal/i, /dialog/i, /drawer/i,
];

function isInteractiveComponent(name: string): boolean {
  return INTERACTIVE_PATTERNS.some(pattern => pattern.test(name));
}

// Use in checks:
if (!isInteractiveComponent(componentSet.name)) {
  return { passed: true, message: 'Non-interactive - Focus not required' };
}
```

**Reference:** [ComponentAuditor.ts:40-61](../../../integrations/figma-plugin/ComponentAuditor.ts#L40-L61)

---

#### 5. Default State Naming Variations

**Problem:** Audit only accepts "Default", but designers use "Rest" or "Normal".

**All three are valid base states!**

**Fix Pattern:**
```typescript
// WRONG: Only check for "Default"
const hasDefault = variants.some(n => n.includes('default'));

// CORRECT: Accept all valid base state names
const hasDefault = variants.some(n =>
  n.includes('default') || n.includes('rest') || n.includes('normal')
);
```

**Reference:** [ComponentAuditor.ts:844-847](../../../integrations/figma-plugin/ComponentAuditor.ts#L844-L847)

---

#### 6. Hover State on Non-Interactive Components

**Problem:** Audit requires Hover for all component sets.

**Non-interactive components don't need Hover!**

**Fix Pattern:**
```typescript
const isInteractive = isInteractiveComponent(componentSet.name);

const missingStates = [];
if (!hasDefault) missingStates.push('Default/Rest/Normal');
if (!hasHover && isInteractive) missingStates.push('Hover'); // Only if interactive!
```

**Reference:** [ComponentAuditor.ts:850-855](../../../integrations/figma-plugin/ComponentAuditor.ts#L850-L855)

---

#### 7. Touch Target Measuring Container

**Problem:** COMPONENT_SET container is measured (often very large), not individual variants.

**Measure the variant, not the container!**

**Fix Pattern:**
```typescript
let targetNode = node;

// For COMPONENT_SET, measure first variant
if (node.type === 'COMPONENT_SET' && node.children.length > 0) {
  const firstVariant = node.children.find(c => c.type === 'COMPONENT');
  if (firstVariant) {
    targetNode = firstVariant;
  }
}

const width = targetNode.width;
const height = targetNode.height;
```

**Reference:** [ComponentAuditor.ts:862-870](../../../integrations/figma-plugin/ComponentAuditor.ts#L862-L870)

---

#### 8. Border Radius Threshold Too Strict

**Problem:** Only allowing 2 different radii. Many valid components use 3-4 (0, 8, 16, 999).

**Increase threshold to 4!**

| Radii Count | Status |
|-------------|--------|
| 1-2 | ✅ Pass |
| 3-4 | ✅ Pass (threshold = 4) |
| 5+ | ⚠️ Info (suggest standardizing) |

**Reference:** [ComponentAuditor.ts:666-668](../../../integrations/figma-plugin/ComponentAuditor.ts#L666-L668)

---

#### 9. Different Layer Counts as Error

**Problem:** Variants with different layer counts flagged as structural inconsistency.

**This is often intentional!** (e.g., `hasIcon=true` adds an icon layer)

**Fix Pattern:**
```typescript
return {
  passed: true, // Always pass - informational only
  message: allSame
    ? 'All variants have consistent structure'
    : 'Variants have different layer counts (may be intentional for hasIcon variants)',
  severity: allSame ? undefined : 'info' // Info, not warning/error
};
```

**Reference:** [ComponentAuditor.ts:587-596](../../../integrations/figma-plugin/ComponentAuditor.ts#L587-L596)

---

#### 10. Parent Context Checking

**Problem:** Checking if the selected component is wrapped in a frame (parent context).

**This checks the user's canvas, not the component!**

**Fix:** Only check internal structure (children), not parent context.

**Reference:** [ComponentAuditor.ts:523-570](../../../integrations/figma-plugin/ComponentAuditor.ts#L523-L570)

---

### False Positive Prevention Checklist

When implementing new audit checks, verify:

| Check | Question |
|-------|----------|
| ✅ Dictionary collision | If fuzzy matching, does value already exist in dictionary? |
| ✅ Valid variations | Are there multiple valid formats for this pattern? |
| ✅ Component type | Does this rule apply to ALL components or just interactive ones? |
| ✅ Container vs content | Am I measuring the right node (content, not container)? |
| ✅ Threshold tuning | Is the threshold based on real-world usage or arbitrary? |
| ✅ Intentional variance | Could the "inconsistency" be intentional (variants)? |
| ✅ Context scope | Am I checking internal structure or external context? |
| ✅ Severity calibration | Should this fail the audit or just inform? |

---

## Automated Detection Patterns

Use these regex patterns to detect issues in generated code:

```javascript
const issuePatterns = {
  // Layout artifacts
  translateArtifact: /translate-[xy]-\[-?\d+%?\]/,
  
  // Hardcoded colors
  hardcodedHex: /(?<!var\([^)]*)(#[0-9a-fA-F]{3,8})(?!\s*\))/,
  
  // Inconsistent font-weight
  fontWeightMismatch: /font-\[var\(--font-weight\/(\d+),(\d+)\)\]/,
  
  // Missing focus (check variant list)
  missingFocus: /State=Focus/,
  
  // Code duplication (count similar return statements)
  returnCount: /return\s*\(/g,
};

function detectIssues(code) {
  const issues = [];
  
  if (issuePatterns.translateArtifact.test(code)) {
    issues.push({ type: 'artifact', severity: 'medium' });
  }
  
  const hexMatches = code.match(issuePatterns.hardcodedHex);
  if (hexMatches && hexMatches.length > 0) {
    issues.push({ type: 'hardcoded-color', count: hexMatches.length });
  }
  
  const returnStatements = code.match(issuePatterns.returnCount);
  if (returnStatements && returnStatements.length > 10) {
    issues.push({ type: 'duplication', severity: 'low' });
  }
  
  return issues;
}
```
