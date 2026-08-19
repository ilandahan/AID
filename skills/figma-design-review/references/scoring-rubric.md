# Scoring Rubric Reference

Detailed criteria for evaluating Figma components.

---

## Dimension 1: Style Guide Implementation (70%)

### 1.1 Variant Structure (25 points)

#### Complete Variant Matrix (10 points)

| Score | Criteria |
|-------|----------|
| 10 | All logical combinations exist (Size × State × Style) |
| 7-9 | Missing 1-2 non-critical variants |
| 4-6 | Missing important variants (e.g., Disabled) |
| 1-3 | Significant gaps in variant coverage |
| 0 | No variant structure |

**Example - Full Coverage:**
```
Size: Full, Medium, Compact
State: Default, Hover, Focus, Disabled
Style: Primary, Secondary
= 3 × 4 × 2 = 24 variants
```

**Common Issues:**
- Missing Disabled state for some sizes
- Missing Focus state entirely
- Incomplete Size options

---

#### Consistent Naming Convention (5 points)

| Score | Criteria |
|-------|----------|
| 5 | Perfect: `Size=Full, State=Hover, Style=Primary` |
| 3-4 | Minor inconsistencies |
| 1-2 | Mixed conventions |
| 0 | No convention / chaotic |

**Correct Format:**
```
Property=Value, Property=Value
- PascalCase for properties
- PascalCase for values
- Comma + space separator
```

**Anti-patterns:**
```
❌ size=full (lowercase)
❌ Size-Full (hyphen)
❌ Full Size (space, reversed)
❌ SizeFull (no separator)
```

---

#### TypeScript Interface (5 points)

| Score | Criteria |
|-------|----------|
| 5 | Complete interface with types, defaults, and optional markers |
| 3-4 | Interface present but incomplete |
| 1-2 | Partial typing |
| 0 | No TypeScript |

**Ideal Interface:**
```typescript
type ButtonProps = {
  label?: string;                              // Optional with implicit default
  size?: "Compact" | "Full" | "Medium";        // Union type
  state?: "Hover" | "Default" | "Disabled";    // All states
  style?: "Primary" | "Secondary";             // All styles
  onClick?: () => void;                        // Event handler
};
```

---

### 1.2 Token System (25 points)

#### CSS Variables for Colors (10 points)

| Score | Criteria |
|-------|----------|
| 10 | All colors use `var(--color/...)` with fallbacks |
| 7-9 | Most colors tokenized, 1-2 hardcoded |
| 4-6 | Mixed approach |
| 1-3 | Mostly hardcoded |
| 0 | No tokens |

**Correct:**
```css
background: var(--color/azure/48, #0c8ce9);
color: var(--color/white/solid, white);
```

**Incorrect:**
```css
background: #0c8ce9;
color: white;
```

---

#### Semantic Token Naming (5 points)

| Score | Criteria |
|-------|----------|
| 5 | Meaningful names: `--color/azure/48`, `--color/primary` |
| 3-4 | Mostly semantic |
| 1-2 | Generic names: `--color-1`, `--blue` |
| 0 | No semantic meaning |

**Good Naming:**
```
--color/azure/48        (color family + lightness)
--color/primary         (semantic role)
--spacing/md            (size scale)
--font-family/heading   (usage context)
```

**Bad Naming:**
```
--var1
--blue-color
--padding-value
```

---

### 1.3 Visual Consistency (20 points)

#### Font-Weight Consistency (5 points)

| Score | Criteria |
|-------|----------|
| 5 | Same weight across all variants (e.g., all 600) |
| 3-4 | Intentional variation (bold for emphasis) |
| 1-2 | Unintentional inconsistency |
| 0 | Random variations |

**Issue Example:**
```jsx
// Variant A
font-weight: 600

// Variant B (same visual intent)
font-weight: 500  // ❌ Inconsistent
```

---

#### No Layout Artifacts (5 points)

| Score | Criteria |
|-------|----------|
| 5 | Clean positioning, no unexpected transforms |
| 3-4 | Minor artifacts that don't affect layout |
| 1-2 | Noticeable artifacts |
| 0 | Severe layout issues |

**Common Artifacts:**
```css
/* These shouldn't appear in production: */
translate-x-[-50%]    /* Figma centering artifact */
position: absolute    /* Without clear purpose */
left: 50%            /* Manual centering hack */
```

---

### 1.4 Accessibility States (20 points)

#### Focus State (8 points)

| Score | Criteria |
|-------|----------|
| 8 | Visible focus ring, proper outline, keyboard navigable |
| 5-7 | Focus exists but not prominent |
| 2-4 | Focus barely visible |
| 0 | No focus state |

**Good Focus State:**
```css
&:focus-visible {
  outline: 2px solid var(--color/azure/48);
  outline-offset: 2px;
}
```

---

#### Disabled State (6 points)

| Score | Criteria |
|-------|----------|
| 6 | All sizes have disabled, proper visual treatment |
| 4-5 | Most sizes have disabled |
| 2-3 | Only some sizes |
| 0 | No disabled state |

**Disabled Requirements:**
- Reduced opacity or greyed colors
- `cursor: not-allowed`
- `pointer-events: none` or click handler disabled
- `aria-disabled="true"`

---

### 1.5 Code Quality (10 points)

#### No Code Duplication (5 points)

| Score | Criteria |
|-------|----------|
| 5 | DRY code, shared utilities |
| 3-4 | Minor duplication |
| 1-2 | Significant repeated code |
| 0 | Copy-paste everywhere |

**Before (Bad):**
```jsx
if (size === "Full" && state === "Default") {
  return <div className="px-8 py-4 rounded-md">...</div>;
}
if (size === "Full" && state === "Hover") {
  return <div className="px-8 py-4 rounded-md">...</div>;  // Duplicated!
}
```

**After (Good):**
```jsx
const baseClasses = "px-8 py-4 rounded-md";
const stateClasses = {
  Default: "bg-blue-500",
  Hover: "bg-blue-600 shadow-lg",
};
return <div className={`${baseClasses} ${stateClasses[state]}`}>...</div>;
```

---

## Dimension 2: LLM Metadata Accessibility (30%)

### 2.1 Component Description (20 points)

| Score | Criteria |
|-------|----------|
| 18-20 | Purpose + use case + context (2-3 sentences) |
| 14-17 | Purpose + use case |
| 10-13 | Basic purpose only |
| 5-9 | Vague description |
| 0-4 | No description |

**Excellent Description:**
```
Primary CTA button for lead capture on homepage hero section.
Triggers contact form modal and sends inquiry to sales team.
Used as the main conversion element above the fold.
```

**Poor Description:**
```
A button.
```

---

### 2.2 Searchability - Tags (15 points)

| Score | Criteria |
|-------|----------|
| 13-15 | 6+ relevant tags covering type, purpose, location |
| 10-12 | 4-5 good tags |
| 6-9 | 2-3 basic tags |
| 1-5 | 1 tag or irrelevant tags |
| 0 | No tags |

**Comprehensive Tags:**
```
tags: button, cta, lead, homepage, hero, conversion, primary, action, form-trigger
```

**Insufficient Tags:**
```
tags: button
```

---

### 2.3 Development Metadata (25 points)

| Field | Points | Purpose |
|-------|--------|---------|
| `testId` | 5 | Automated testing selectors |
| `ariaLabel` | 5 | Screen reader accessibility |
| `analytics` | 5 | Event tracking |
| `category` | 5 | Component classification |
| `level` | 5 | Atomic design hierarchy |

**Complete Metadata:**
```yaml
testId: btn-lead-send
ariaLabel: Send message to start a conversation
analytics: lead_button_click
category: button
level: atom
priority: critical
```

---

### 2.4 Usage Guidelines (20 points)

#### Do's and Don'ts (14 points)

| Score | Criteria |
|-------|----------|
| 12-14 | 3+ do's and 3+ don'ts, specific and actionable |
| 8-11 | 2 each, somewhat helpful |
| 4-7 | 1 each or vague |
| 0-3 | Missing or unhelpful |

**Good Guidelines:**
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
```

---

### 2.5 Technical Specifications (20 points)

| Component | Points | Example |
|-----------|--------|---------|
| Tokens documented | 8 | colors, spacing, typography values |
| Specs documented | 6 | minWidth: 120px, minHeight: 52px |
| A11y requirements | 6 | contrast: 4.5:1, touchTarget: 44px |

**Complete Specs:**
```yaml
tokens:
  colors: Azure Radiance (#0C8CE9), Denim (#0A6FBA)
  spacing: padding-x: 32px, padding-y: 16px
  radius: 6px
  typography: Quicksand SemiBold 16/24

specs:
  minWidth: 120px (Medium), 100% (Full)
  minHeight: 52px
  touchTarget: 44x44px

a11y:
  - Ensure 4.5:1 contrast ratio
  - Focus state required for keyboard navigation
  - aria-disabled for disabled state
```

---

## Quick Reference Table

| Category | Max Points | Critical Threshold |
|----------|------------|-------------------|
| **Implementation** | **100** | **70** |
| - Variant Structure | 25 | 18 |
| - Token System | 25 | 18 |
| - Visual Consistency | 20 | 14 |
| - Accessibility States | 20 | 15 |
| - Code Quality | 10 | 7 |
| **LLM Accessibility** | **100** | **70** |
| - Description | 20 | 14 |
| - Searchability | 15 | 10 |
| - Dev Metadata | 25 | 18 |
| - Usage Guidelines | 20 | 14 |
| - Technical Specs | 20 | 14 |
