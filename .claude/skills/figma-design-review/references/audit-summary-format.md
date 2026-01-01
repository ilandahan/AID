# Component Audit Summary Format

Reference template for Figma plugin component review output.

---

## Output Format Structure

The audit summary follows a **concise, actionable format** with two detail levels:

| Level | Purpose | When to Use |
|-------|---------|-------------|
| **Summary Report** | High-level scores + key findings | Default output after review |
| **Detailed Audit** | Full breakdown + all issues | On request or score < 70 |

---

## Summary Report Template

```markdown
## Component Evaluation: [Component Path / Name]

### 1️⃣ Style Guide Implementation: [XX]/100

**Strengths:**
- ✅ [Key strength 1]
- ✅ [Key strength 2]
- ✅ [Key strength 3]

**Weaknesses:**
- ⚠️ [Issue] → **Fix:** [How to fix]
- ⚠️ [Issue] → **Fix:** [How to fix]

---

### 2️⃣ LLM Metadata Accessibility: [XX]/100 [🌟 if ≥90]

**[Excellent/Good/Needs Work]! Includes:**
- ✅ [Present element 1]
- ✅ [Present element 2]

**Missing:**
- ❌ [Missing element] → **Add:** [What to add]

---

## 📊 Final Weighted Score

| Criterion | Score | Weight | Contribution |
|-----------|-------|--------|--------------|
| Style Guide Implementation | **XX** | 70% | XX.X |
| LLM Accessibility | **XX** | 30% | XX.X |
| **Total Weighted** | | | **XX.X/100** |

---

### 💡 Recommendations:

1. **[Action item]** → [Specific fix instruction]
2. **[Action item]** → [Specific fix instruction]
3. **[Action item]** → [Specific fix instruction]

**Overall:** [One-sentence assessment]
```

---

## Field Guidelines

### Strengths Section (Max 6 items)

List only **notable positives**. Use these categories:

| Category | Example |
|----------|---------|
| Variants | "Complete variant matrix (Size × State × Style = 18 variants)" |
| Tokens | "Consistent CSS Variables for all colors (`--color/azure/48`)" |
| Naming | "Clear naming convention (`Size=Full, State=Hover`)" |
| TypeScript | "Well-defined TypeScript interface with proper types" |
| Colors | "Semantic color system (Azure, Denim, Pale Sky)" |
| Typography | "Consistent typography (Quicksand SemiBold 16/24)" |
| Accessibility | "Focus state with visible 2px ring" |
| Code | "DRY code structure with shared utilities" |

### Weaknesses Section (Max 5 items, always include fix)

Every weakness **MUST include a fix**. Format:

```markdown
- ⚠️ [Problem description] → **Fix:** [Actionable solution]
```

#### Common Issues with Fixes

| Issue | Fix |
|-------|-----|
| `translate-x-[-50%]` artifact | Remove from production code - Figma centering artifact |
| Inconsistent font-weight (500 vs 600) | Standardize to 600 (SemiBold) across all variants |
| Code duplication | Extract shared styles to base classes/utilities |
| Missing Focus states | Add `:focus-visible` with visible ring (2px solid) |
| Missing Disabled variants | Add Disabled state for all sizes with opacity 0.5 |
| Hardcoded hex colors | Convert to CSS Variables: `var(--color/name)` |
| Inconsistent padding | Align to 8px scale (8, 16, 24, 32) |
| No TypeScript interface | Add typed props with union types for variants |
| Missing touch target | Ensure minimum 44x44px interactive area |
| Low contrast | Increase to meet WCAG 4.5:1 ratio |

### Metadata Section Phrases

| Score Range | Phrase |
|-------------|--------|
| 90-100 | "**Excellent!** Includes:" |
| 80-89 | "**Good!** Includes:" |
| 70-79 | "**Acceptable.** Includes:" |
| 60-69 | "**Needs Work.** Has:" |
| < 60 | "**Incomplete.** Only has:" |

### Missing Metadata with Fix Instructions

| Missing Item | Add Instruction |
|--------------|-----------------|
| Description | Add 2-3 sentences: purpose, use case, context |
| Tags | Add 6+ keywords: type, purpose, location, action |
| testId | Add format: `component-name-variant` |
| ariaLabel | Add accessible label describing action |
| analytics | Add event name: `component_action_context` |
| Do's/Don'ts | Add 3+ each with specific guidance |
| Specs | Add minWidth, minHeight, touchTarget values |
| A11y guidelines | Add contrast ratio, focus requirements |

---

## Recommendations Section

### Priority Order

Always order recommendations by impact:

1. 🔴 **Critical** (Accessibility blockers, broken functionality)
2. 🟠 **High** (Missing states, major inconsistencies)
3. 🟡 **Medium** (Code quality, incomplete metadata)
4. 🟢 **Low** (Minor polish, nice-to-haves)

### Recommendation Format

```markdown
1. **[Action verb] [what]** → [Specific technical instruction]
```

#### Examples

```markdown
1. **Remove translate artifact** → Delete `translate-x-[-50%]` from all variant styles
2. **Add Focus states** → Implement `:focus-visible { outline: 2px solid var(--color/azure/48); outline-offset: 2px; }`
3. **Complete Disabled variants** → Add Disabled state for Compact size with `opacity: 0.5; cursor: not-allowed;`
4. **Consolidate duplicate code** → Extract shared `padding`, `border-radius` to base button class
5. **Add missing metadata** → Include testId, ariaLabel, and analytics event name
```

---

## Score Thresholds & Status

| Score | Grade | Status | Action |
|-------|-------|--------|--------|
| 90-100 | 🌟 Excellent | ✅ Ready | Export immediately |
| 80-89 | ✅ Good | ✅ Ready | Export with minor notes |
| 70-79 | ⚠️ Acceptable | ⚠️ Conditional | Fix before export |
| 60-69 | 🔶 Needs Work | ❌ Not Ready | Significant fixes needed |
| < 60 | ❌ Poor | ❌ Blocked | Major rework required |

---

## Audit Tab Format (Component-Grouped Issues)

The Audit Tab groups all issues **by component/sub-component**. Each component shows all its issues together with a navigation arrow.

### Structure

```
┌─────────────────────────────────────────────────────────────────┐
│  🔍 AUDIT RESULTS                                    [X issues] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 📦 Component Name                              → [arrow] │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │ ⚠️ Issue 1 description                                  │   │
│  │    Fix: How to fix this issue                           │   │
│  │                                                         │   │
│  │ ⚠️ Issue 2 description                                  │   │
│  │    Fix: How to fix this issue                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 📦 Another Component                           → [arrow] │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │ ⚠️ Issue description                                    │   │
│  │    Fix: How to fix                                      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Audit Tab Template

```markdown
## 🔍 Audit Results

### 📦 Button / Primary / Full  [→]
| Issue | Fix |
|-------|-----|
| ⚠️ Missing Focus state | Add `:focus-visible` with 2px outline ring |
| ⚠️ `translate-x-[-50%]` artifact | Remove - Figma centering artifact |

---

### 📦 Button / Primary / Compact  [→]
| Issue | Fix |
|-------|-----|
| ⚠️ Missing Disabled variant | Add with `opacity: 0.5; cursor: not-allowed` |
| ⚠️ Touch target < 44px | Increase min-height to 44px |

---

### 📦 Button / Secondary / All Sizes  [→]
| Issue | Fix |
|-------|-----|
| ⚠️ Inconsistent font-weight | Standardize to 600 across all variants |

---

### 📦 Component Metadata  [→]
| Issue | Fix |
|-------|-----|
| ❌ Missing analytics event | Add: `button_primary_click` |
```

### Navigation Arrow Behavior

The `[→]` arrow is **clickable** and performs:

```typescript
// On arrow click - navigate to component in Figma
interface AuditNavigationAction {
  type: 'navigate_to_component';

  // Figma node ID for direct navigation
  nodeId: string;

  // Action to perform
  action: 'select' | 'zoom_to' | 'open_properties';

  // Default: open properties panel
  openPropertiesPanel: boolean;
}

// Example implementation
function onArrowClick(nodeId: string) {
  figma.viewport.scrollAndZoomIntoView([figma.getNodeById(nodeId)]);
  figma.currentPage.selection = [figma.getNodeById(nodeId)];
  // Trigger properties panel open
  figma.notify('Component selected - check Properties panel');
}
```

### Grouping Rules

| Rule | Description |
|------|-------------|
| **Group by component** | All issues for same component appear together |
| **Show full path** | `Button / Primary / Full` not just `Full` |
| **Combine variants** | If issue affects all sizes, show `All Sizes` |
| **Order by severity** | Critical issues first within each component |
| **Metadata separate** | Component metadata issues in own section |

### Issue Categories for Grouping

```
Component Issues:
├── Visual Issues (per variant)
│   ├── Layout artifacts
│   ├── Inconsistent styling
│   └── Missing states
├── Token Issues (per property)
│   ├── Hardcoded colors
│   ├── Missing variables
│   └── Inconsistent values
├── Accessibility Issues (per variant)
│   ├── Missing Focus
│   ├── Missing Disabled
│   └── Touch target
└── Metadata Issues (component-level)
    ├── Missing description
    ├── Missing testId
    └── Missing analytics
```

### Example: Grouped Audit Output

```markdown
## 🔍 Audit Results (7 issues across 4 components)

---

### 📦 Button / Lead / Send Message / Full  [→]

| # | Severity | Issue | Fix |
|---|----------|-------|-----|
| 1 | 🔴 Critical | Missing Focus state | Add `:focus-visible { outline: 2px solid var(--color/azure/48); }` |
| 2 | 🟡 Medium | `translate-x-[-50%]` artifact | Remove from styles - Figma centering leftover |

---

### 📦 Button / Lead / Send Message / Compact  [→]

| # | Severity | Issue | Fix |
|---|----------|-------|-----|
| 1 | 🔴 Critical | Missing Focus state | Add `:focus-visible` with visible ring |
| 2 | 🔴 Critical | Missing Disabled variant | Create variant with `opacity: 0.5` |
| 3 | 🟠 High | Touch target 36px | Increase to minimum 44px |

---

### 📦 Button / Lead / Send Message / All Variants  [→]

| # | Severity | Issue | Fix |
|---|----------|-------|-----|
| 1 | 🟡 Medium | Inconsistent font-weight (500 vs 600) | Standardize to 600 (SemiBold) |

---

### 📦 Component Metadata  [→]

| # | Severity | Issue | Fix |
|---|----------|-------|-----|
| 1 | 🟢 Low | Missing analytics event | Add: `lead_button_click` |

---

**Total: 7 issues** (3 Critical, 1 High, 2 Medium, 1 Low)
```

### Arrow Icon Options

Use one of these for the navigation arrow:

| Icon | Unicode | Usage |
|------|---------|-------|
| → | `\u2192` | Simple arrow |
| ➜ | `\u279C` | Heavy arrow |
| ▶ | `\u25B6` | Play/navigate |
| ⤴ | `\u2934` | Go to |
| 🔗 | `\u{1F517}` | Link icon |

**Recommended:** `→` for clean appearance

---

## Analysis Tab Format (Metadata & Naming)

The Analysis Tab focuses on **metadata completeness** and **naming conventions**. Shows exactly what the designer needs to enter.

### Structure

```
┌─────────────────────────────────────────────────────────────────┐
│  📋 ANALYSIS RESULTS                              [X to review] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 📦 Component Name                              → [arrow] │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │ 📛 NAMING                                               │   │
│  │    Current: "btn primary"                               │   │
│  │    Suggested: "Button / Primary / Default"              │   │
│  │                                                         │   │
│  │ 📝 MISSING METADATA                                     │   │
│  │    ┌────────────────────────────────────────────────┐  │   │
│  │    │ description: [Enter value here]                │  │   │
│  │    │ tags: [Enter value here]                       │  │   │
│  │    │ testId: [Enter value here]                     │  │   │
│  │    └────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Component Naming Convention (Figma Best Practice)

Use hierarchical naming for optimal LLM context:

```
[Category] / [Type] / [Variant] / [State]
```

#### Naming Hierarchy Examples

| Level | Purpose | Examples |
|-------|---------|----------|
| **Category** | Component family | `Button`, `Input`, `Card`, `Modal` |
| **Type** | Specific purpose | `Primary`, `Secondary`, `Ghost`, `Outline` |
| **Variant** | Size or layout | `Full`, `Medium`, `Compact`, `Icon-Only` |
| **State** | Interaction state | `Default`, `Hover`, `Focus`, `Disabled` |

#### Naming Corrections Table

| Current (Wrong) | Suggested (Correct) | Why |
|-----------------|---------------------|-----|
| `btn primary` | `Button / Primary / Default` | Use PascalCase, full hierarchy |
| `Primary Button` | `Button / Primary / Default` | Category first, not type |
| `button-primary-hover` | `Button / Primary / Hover` | Use `/` separator, PascalCase |
| `PrimaryBtn` | `Button / Primary / Default` | Spell out fully, add hierarchy |
| `CTA` | `Button / CTA / Default` | Add category prefix |
| `Large Primary Button` | `Button / Primary / Large` | Restructure to hierarchy |
| `input field` | `Input / Text / Default` | PascalCase, add type |
| `Card` | `Card / Product / Default` | Add type and state |

### Analysis Tab Template

```markdown
## 📋 Analysis Results

---

### 📦 Button / Primary  [→]

#### 📛 Naming Issue
| Current | Suggested |
|---------|-----------|
| `btn primary` | `Button / Primary / Default` |

**Why:** Use hierarchical naming with `/` separators for better LLM context. Category comes first, followed by type, variant, and state.

#### 📝 Missing Metadata — Enter These Values:

| Field | Value to Enter |
|-------|----------------|
| **description** | `Primary action button for form submissions and main CTAs. Triggers primary user actions with high visual prominence.` |
| **tags** | `button, primary, cta, action, submit, form, interactive` |
| **testId** | `btn-primary-default` |
| **ariaLabel** | `[Action] button` (e.g., "Submit form button") |
| **analytics** | `button_primary_click` |

---

### 📦 Button / Secondary  [→]

#### 📛 Naming Issue
| Current | Suggested |
|---------|-----------|
| `secondary btn` | `Button / Secondary / Default` |

#### 📝 Missing Metadata — Enter These Values:

| Field | Value to Enter |
|-------|----------------|
| **description** | `Secondary action button for alternative actions. Used alongside Primary buttons for cancel, back, or secondary options.` |
| **tags** | `button, secondary, cancel, back, alternative, interactive` |
| **testId** | `btn-secondary-default` |

---

### 📦 Input / Email  [→]

#### ✅ Naming: Correct
Current name follows best practices.

#### 📝 Missing Metadata — Enter These Values:

| Field | Value to Enter |
|-------|----------------|
| **Do's** | `• Always include visible label`<br>`• Show validation on blur`<br>`• Use type="email" for mobile keyboard` |
| **Don'ts** | `• Don't use placeholder as label`<br>`• Don't validate on every keystroke`<br>`• Don't disable autocomplete` |

---

**Total: 3 components reviewed** (2 naming issues, 8 missing metadata fields)
```

### Metadata Templates by Component Type

When metadata is missing, provide **ready-to-copy values**:

#### Button Metadata Template

```yaml
description: |
  [Purpose] button for [use case].
  [What it triggers/does].
  [Where it's typically used].

tags: button, [type], [purpose], [location], action, interactive, [additional]

testId: btn-[type]-[variant]-[state]
# Example: btn-primary-full-default

ariaLabel: [Action verb] [context]
# Example: "Submit contact form"

analytics: button_[type]_[action]
# Example: button_primary_click

category: button
level: atom
priority: [critical|high|medium|low]

dos:
  - Use for primary/single main action per viewport
  - Keep label text concise (2-3 words)
  - Ensure sufficient color contrast (4.5:1)

donts:
  - Don't use multiple [type] buttons in same section
  - Don't change colors outside design system
  - Don't remove focus states

specs:
  minWidth: [value]px
  minHeight: [value]px
  touchTarget: 44px
  contrast: 4.5:1
```

#### Input Metadata Template

```yaml
description: |
  [Type] input field for [data type].
  [Validation behavior].
  [Where it's typically used].

tags: input, [type], form, field, [validation], interactive

testId: input-[type]-[variant]
# Example: input-email-default

ariaLabel: Enter [field name]
# Example: "Enter email address"

analytics: form_[type]_[action]
# Example: form_email_focus

category: input
level: atom

dos:
  - Always include visible label
  - Show validation state on blur
  - Provide helper text for requirements

donts:
  - Don't use placeholder as only label
  - Don't show errors before interaction
  - Don't disable browser autocomplete without reason
```

#### Card Metadata Template

```yaml
description: |
  [Type] card for displaying [content type].
  [Interactive elements if any].
  [Where it's typically used].

tags: card, [type], [content], display, container

testId: card-[type]-[variant]
# Example: card-product-default

ariaLabel: [Content] card
# Example: "Product information card"

category: card
level: molecule

dos:
  - Maintain consistent aspect ratio in grids
  - Use lazy loading for images
  - Keep content hierarchy clear

donts:
  - Don't overflow text without truncation
  - Don't mix card sizes in same row
  - Don't hide critical info on hover only
```

### Naming Validation Rules

```typescript
interface NamingValidation {
  // Check naming follows hierarchy
  isValid: boolean;

  // Current component name
  current: string;

  // Suggested correction
  suggested: string;

  // Specific issues found
  issues: NamingIssue[];
}

interface NamingIssue {
  type: 'missing_category' | 'wrong_separator' | 'wrong_case' |
        'missing_type' | 'missing_state' | 'abbreviation';
  message: string;
  fix: string;
}

// Validation rules
const namingRules = {
  // Must use "/" as separator
  separator: '/',

  // Must use PascalCase
  casing: 'PascalCase',

  // Required levels (minimum)
  requiredLevels: ['Category', 'Type'],

  // Optional levels
  optionalLevels: ['Variant', 'State'],

  // No abbreviations
  noAbbreviations: ['btn', 'txt', 'img', 'bkg', 'clr'],

  // Expand abbreviations to
  expansions: {
    'btn': 'Button',
    'txt': 'Text',
    'img': 'Image',
    'bkg': 'Background',
    'clr': 'Color',
    'cta': 'CTA'  // CTA is acceptable
  }
};
```

### Example: Complete Analysis Output

```markdown
## 📋 Analysis Results (5 components, 12 issues)

---

### 📦 btn primary full  [→]

#### 📛 Naming Issues (3 found)

| Issue | Current | Fix |
|-------|---------|-----|
| Wrong separator | `btn primary full` | Use `/` → `Button / Primary / Full` |
| Abbreviation | `btn` | Expand → `Button` |
| Wrong case | `primary full` | PascalCase → `Primary / Full` |

**Corrected Name:** `Button / Primary / Full / Default`

#### 📝 Missing Metadata — Enter These Values:

| Field | Ready-to-Copy Value |
|-------|---------------------|
| **description** | `Primary action button at full width for main CTAs and form submissions. Used in hero sections and modal footers for maximum visual impact.` |
| **tags** | `button, primary, cta, full-width, action, submit, form, hero, modal` |
| **testId** | `btn-primary-full-default` |
| **ariaLabel** | `[Action] button` — Replace [Action] with specific action (e.g., "Submit form") |
| **analytics** | `button_primary_full_click` |
| **Do's** | `• Use as single primary action per viewport`<br>`• Place in prominent position (right side, bottom of form)`<br>`• Use for conversion-critical actions` |
| **Don'ts** | `• Don't use multiple full-width primary buttons on same page`<br>`• Don't use for secondary or cancel actions`<br>`• Don't reduce width on mobile` |

---

### 📦 Input / Email  [→]

#### ✅ Naming: Correct

#### 📝 Missing Metadata — Enter These Values:

| Field | Ready-to-Copy Value |
|-------|---------------------|
| **description** | `Email input field with format validation. Shows error state for invalid email format on blur. Used in contact forms, signup flows, and newsletter subscriptions.` |
| **analytics** | `form_email_interaction` |

---

### 📦 Card  [→]

#### 📛 Naming Issue (1 found)

| Issue | Current | Fix |
|-------|---------|-----|
| Missing type | `Card` | Add type → `Card / Product / Default` |

**Corrected Name:** `Card / Product / Default`

#### ✅ Metadata: Complete

---

**Summary:**
- 🔤 **Naming issues:** 4 across 2 components
- 📝 **Missing metadata:** 8 fields across 3 components
- ✅ **Complete:** 1 component fully configured
```

---

## Detailed Audit Format

Use **only when requested** or when score < 70. Adds:

### Variant Breakdown Table

```markdown
### Variant Analysis

| Size | Default | Hover | Focus | Disabled |
|------|---------|-------|-------|----------|
| Full | ✅ | ✅ | ❌ | ✅ |
| Medium | ✅ | ✅ | ❌ | ✅ |
| Compact | ✅ | ✅ | ❌ | ❌ |
```

### Token Audit Table

```markdown
### Token Usage

| Property | Value | Status |
|----------|-------|--------|
| Background | `var(--color/azure/48)` | ✅ Token |
| Text | `#FFFFFF` | ❌ Hardcoded |
| Border | `var(--color/denim)` | ✅ Token |
```

### Metadata Checklist

```markdown
### Metadata Completeness

| Field | Status | Value/Issue |
|-------|--------|-------------|
| Description | ✅ | "Primary CTA for lead capture..." |
| Tags | ✅ | button, cta, lead, homepage, hero |
| testId | ✅ | btn-lead-send |
| ariaLabel | ✅ | "Send message to start conversation" |
| analytics | ❌ | Missing - Add: `lead_button_click` |
| Do's | ✅ | 4 guidelines |
| Don'ts | ✅ | 3 guidelines |
| Specs | ⚠️ | Partial - Missing touchTarget |
```

---

## Example: Complete Summary Report

```markdown
## Component Evaluation: Button / Lead / Send Message

### 1️⃣ Style Guide Implementation: 78/100

**Strengths:**
- ✅ Excellent variant structure (Size × State × Style = 18 variants)
- ✅ Consistent CSS Variables for tokens (`--color/azure/48`, `--font-family/font-1`)
- ✅ Clear naming convention (`Size=Full, State=Hover, Style=Primary`)
- ✅ Well-defined TypeScript interface
- ✅ Semantic color system (Azure, Denim, Pale Sky)
- ✅ Consistent typography (Quicksand SemiBold 16/24)

**Weaknesses:**
- ⚠️ `translate-x-[-50%]` on some variants → **Fix:** Remove - Figma artifact, not needed in production
- ⚠️ Inconsistent font-weight (500 vs 600) → **Fix:** Standardize to 600 across all variants
- ⚠️ Significant code duplication → **Fix:** Extract shared padding/radius to base class
- ⚠️ Missing Focus states → **Fix:** Add `:focus-visible` with 2px outline ring
- ⚠️ Missing Disabled for Compact size → **Fix:** Add Disabled variant with opacity 0.5

---

### 2️⃣ LLM Metadata Accessibility: 95/100 🌟

**Excellent! Includes:**
- ✅ Detailed component description with use case
- ✅ Comprehensive tags (button, cta, lead, homepage, hero, conversion)
- ✅ Defined ariaLabel
- ✅ testId for automated testing
- ✅ analytics event name
- ✅ category and level (atom)
- ✅ priority (critical)
- ✅ Detailed Do's and Don'ts
- ✅ Documented design tokens
- ✅ Linked related components
- ✅ Precise specs (minWidth, minHeight, touchTarget, contrast)
- ✅ Detailed A11y guidelines
- ✅ Individual variant descriptions

This is one of the most comprehensive component documentations in the design system.

---

## 📊 Final Weighted Score

| Criterion | Score | Weight | Contribution |
|-----------|-------|--------|--------------|
| Style Guide Implementation | **78** | 70% | 54.6 |
| LLM Accessibility | **95** | 30% | 28.5 |
| **Total Weighted** | | | **83.1/100** |

---

### 💡 Recommendations:

1. **Remove translate artifact** → Delete `translate-x-[-50%]` from production styles
2. **Add Focus states** → Essential for keyboard accessibility compliance
3. **Complete Compact/Disabled variants** → Ensures design system completeness
4. **Consolidate duplicate code** → Reduces maintenance burden and file size

**Overall:** Excellent work! The metadata documentation is exceptional and will greatly help any LLM understand context and generate correct code.
```

---

## Export to AID Design System

> **⚠️ IMPORTANT:** Export is handled by the **`atomic-design` skill**, not this skill.
>
> This skill (`figma-design-review`) evaluates and scores components.
> The `atomic-design` skill classifies and generates code files.
>
> This ensures consistency with the `atomic-page-builder` skill which also uses `atomic-design`.

### Two-Skill Export Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     EXPORT WORKFLOW                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  STEP 1: EVALUATE (figma-design-review skill)                  │
│  ├── Score component (70/30 weighted)                          │
│  ├── Identify issues                                           │
│  ├── Check export readiness (score >= 70)                      │
│  └── If ready → proceed to Step 2                              │
│                                                                 │
│  STEP 2: EXPORT (atomic-design skill)                          │
│  ├── Classify level (Atom/Molecule/Organism)                   │
│  ├── Determine folder path                                     │
│  ├── Extract tokens from Figma (Figma-first rule)              │
│  ├── Generate component files                                  │
│  └── Place in src/design-system/[level]s/                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Single Export Button (NOT two separate buttons)

The plugin should have **ONE export button** that:
1. **Checks export readiness** using figma-design-review scoring
2. **Delegates to atomic-design skill** for classification and code generation
3. Uses atomic-design's file structure and Figma-first extraction rules
4. Shows a clear success message with destination path

### Export Button UI

```
┌─────────────────────────────────────────────────────────────────┐
│  Ready to Export                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Component: [Name]                                               │
│  Level: [🔵 Atom | 🟢 Molecule | 🟣 Organism] (auto-detected)   │
│  Score: [XX]/100 [✅ | ⚠️ | ❌]                                 │
│                                                                  │
│           ┌─────────────────────────────────────┐               │
│           │  📤 Export to AID Design System    │               │
│           └─────────────────────────────────────┘               │
│                                                                  │
│  Destination: src/design-system/[level]s/[Name]/                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Auto-Classification Logic (via atomic-design skill)

The classification logic follows the **atomic-design skill** rules (see `../atomic-design/SKILL.md`):

```typescript
/**
 * Classification is handled by the atomic-design skill.
 * This ensures consistency with atomic-page-builder.
 *
 * Rules from atomic-design skill:
 * - Atom: Uses ONLY tokens, no other components (Button, Icon, Input)
 * - Molecule: Combines 2+ Atoms (FormField, SearchBar, MenuItem)
 * - Organism: Combines Molecules + Atoms (Card, Modal, Header)
 */
function classifyComponent(component: FigmaComponent): 'atom' | 'molecule' | 'organism' {
  const children = getChildComponents(component);

  // Atom: No child components - uses only design tokens
  // Examples: Button, Icon, Input, Badge, Typography
  if (children.length === 0) {
    return 'atom';
  }

  // Check child levels recursively
  const childLevels = children.map(classifyComponent);

  // Molecule: Contains only atoms
  // Examples: FormField (Label + Input + Error), SearchBar (Input + Button)
  if (childLevels.every(level => level === 'atom')) {
    return 'molecule';
  }

  // Organism: Contains molecules (may also contain atoms)
  // Examples: Card (Image + Title + Description + Button), Modal, Header
  return 'organism';
}
```

### Export Destination by Level

| Level | Icon | Folder | Examples |
|-------|------|--------|----------|
| Atom | 🔵 | `src/design-system/atoms/` | Button, Input, Icon, Badge |
| Molecule | 🟢 | `src/design-system/molecules/` | FormField, SearchBar, MenuItem |
| Organism | 🟣 | `src/design-system/organisms/` | Card, Modal, Header, Footer |

### Files Generated on Export

```
src/design-system/[level]s/[ComponentName]/
├── [ComponentName].tsx          # React component with typed props
├── [ComponentName].module.css   # Styles using CSS Variables
├── [ComponentName].test.tsx     # Tests using testId from metadata
└── index.ts                     # Named export
```

### Export Success Message

```
✅ Exported [Component Name] as [LEVEL] to AID Design System

Files created in: src/design-system/[level]s/[Name]/
├── [Name].tsx          (Component + Props)
├── [Name].module.css   (Styles with tokens)
├── [Name].test.tsx     (Tests with testId)
└── index.ts            (Export)

Next steps:
• Run tests: npm test [Name]
• View in Storybook: npm run storybook
```

### Export Blocked Message (Score < 70)

```
❌ Cannot Export - Score Below Minimum

Current Score: [XX]/100 (minimum required: 70)

Blockers to fix:
• [Blocker 1] → [Fix]
• [Blocker 2] → [Fix]

Use the Audit tab to fix issues, then try again.
```

---

## Implementation Notes

### For Figma Plugin

1. **Generate Summary by default** - Use concise format
2. **Detailed Audit on request** - Add tables when asked
3. **Always include fixes** - Never list problem without solution
4. **Cap strengths at 6** - Prioritize most notable
5. **Cap weaknesses at 5** - Focus on impactful issues
6. **Order recommendations by priority** - Critical first

### For Audit Tab

1. **Group by component** - All issues for same component together
2. **Show component path** - Full hierarchy (`Button / Primary / Full`)
3. **Include navigation arrow** - `[→]` clickable to jump to component
4. **Arrow action** - Select component + scroll into view + open properties
5. **Severity badges** - 🔴 Critical, 🟠 High, 🟡 Medium, 🟢 Low
6. **Combine when possible** - `All Variants` for issues affecting everything
7. **Metadata section** - Separate section for component-level metadata issues

### For Analysis Tab

1. **Show naming corrections** - Current vs Suggested with hierarchy
2. **Provide ready-to-copy values** - Exact metadata to enter
3. **Use Figma naming convention** - `Category / Type / Variant / State`
4. **Expand abbreviations** - `btn` → `Button`, `txt` → `Text`
5. **Include navigation arrow** - `[→]` to jump to component
6. **Template by component type** - Button, Input, Card templates
7. **Mark complete items** - ✅ when naming or metadata is correct

### Arrow Click Handler

```typescript
// Required: Store nodeId with each audit item
interface AuditItem {
  nodeId: string;           // Figma node ID
  componentPath: string;    // "Button / Primary / Full"
  issues: Issue[];
}

// On arrow click
async function navigateToComponent(nodeId: string) {
  const node = await figma.getNodeByIdAsync(nodeId);
  if (node) {
    figma.viewport.scrollAndZoomIntoView([node]);
    figma.currentPage.selection = [node as SceneNode];
  }
}
```

### Language

- **English only** for all output
- Use technical terminology consistently
- Keep sentences concise and actionable
