# Pre-Export Checklist

Use this checklist before exporting any component to code.

---

## Quick Check (Must Pass All)

### 🔴 Blockers (Cannot Export)

- [ ] **Weighted Score ≥ 70** - Minimum viable quality
- [ ] **Focus state exists** - Keyboard accessibility required
- [ ] **Disabled state exists** - For interactive components
- [ ] **No layout artifacts** - No unexpected translate/transform
- [ ] **Primary description present** - LLM needs context

### 🟡 Warnings (Can Export with Notes)

- [ ] All variant combinations complete
- [ ] All colors use CSS Variables
- [ ] TypeScript interface defined
- [ ] Tags present for searchability
- [ ] Do's and Don'ts documented

### 🟢 Best Practice (Recommended)

- [ ] Analytics event name defined
- [ ] testId defined for testing
- [ ] ariaLabel specified
- [ ] Related components linked
- [ ] A11y requirements documented

---

## Detailed Checklist by Category

### Implementation Quality

#### Variant Structure
```
□ All Size variants present (Full, Medium, Compact, etc.)
□ All State variants present (Default, Hover, Focus, Disabled)
□ All Style variants present (Primary, Secondary, etc.)
□ Naming follows: Size=X, State=Y, Style=Z
□ TypeScript props interface defined
□ Default values specified
```

#### Token System
```
□ Background colors use var(--color/...)
□ Text colors use var(--color/...)
□ Border colors use var(--color/...)
□ Font family uses var(--font-family/...)
□ Spacing uses consistent tokens
□ Fallback values provided: var(--token, fallback)
```

#### Visual Consistency
```
□ Font-weight same across variants (unless intentional)
□ Border-radius uniform
□ Padding consistent per size
□ No translate-x or translate-y artifacts
□ No unexpected absolute positioning
□ Shadow consistent for same states
```

#### Accessibility
```
□ Focus state with visible ring (outline)
□ Focus visible on keyboard navigation
□ Disabled state with proper styling
□ Disabled includes aria-disabled
□ Touch target ≥ 44x44px
□ Color contrast ≥ 4.5:1 (text)
□ Color contrast ≥ 3:1 (UI components)
```

#### Code Quality
```
□ No copy-paste duplication
□ Shared styles extracted
□ Conditional logic is clear
□ Component is self-contained
□ No hardcoded dimensions (use tokens)
```

---

### LLM Metadata

#### Description
```
□ Primary description (2-3 sentences)
□ Purpose explained
□ Use case specified
□ Context provided (where it appears)
```

#### Searchability
```
□ Tags present
□ Tags include: component type (button, input, etc.)
□ Tags include: purpose (cta, navigation, etc.)
□ Tags include: location (hero, sidebar, etc.)
□ Tags include: action (submit, cancel, etc.)
```

#### Development Metadata
```
□ testId defined (e.g., btn-lead-send)
□ ariaLabel defined
□ analytics event name defined
□ category specified (button, form, etc.)
□ level specified (atom, molecule, etc.)
□ priority specified (critical, high, etc.)
```

#### Usage Guidelines
```
□ At least 3 Do's listed
□ Do's are specific and actionable
□ At least 3 Don'ts listed
□ Don'ts prevent common mistakes
□ Notes explain usage context
```

#### Technical Specs
```
□ Color tokens documented with hex values
□ Spacing tokens documented
□ Typography documented
□ minWidth / maxWidth if applicable
□ minHeight / maxHeight if applicable
□ Touch target size documented
□ Contrast requirements documented
□ ARIA requirements documented
```

---

## Export Decision Matrix

| Implementation Score | LLM Score | Weighted | Decision |
|---------------------|-----------|----------|----------|
| ≥80 | ≥80 | ≥80 | ✅ Export Ready |
| ≥80 | <80 | ≥70 | ⚠️ Export with metadata TODO |
| <80 | ≥80 | ≥70 | ⚠️ Export with impl TODO |
| ≥70 | ≥70 | ≥70 | ⚠️ Export with notes |
| <70 | any | <70 | ❌ Do not export |
| any | <70 | <70 | ❌ Do not export |

---

## Common Blockers and Fixes

### Missing Focus State

**Problem:** No visible focus indicator for keyboard users

**Fix:**
```css
/* Add to component */
&:focus-visible {
  outline: 2px solid var(--color/azure/48);
  outline-offset: 2px;
}
```

---

### Layout Artifacts (translate)

**Problem:** `translate-x-[-50%]` appearing in generated code

**Fix in Figma:**
1. Select the variant with the artifact
2. Check if it's using absolute positioning
3. Reset to Auto Layout
4. Remove manual X/Y offsets

---

### Missing Disabled State

**Problem:** No disabled variant for some sizes

**Fix in Figma:**
1. Duplicate the Default variant
2. Rename to `State=Disabled`
3. Apply disabled styling:
   - Background: Grey/46 (#6C757D)
   - Text: Same or lighter
   - Remove shadow/elevation

---

### Hardcoded Colors

**Problem:** Colors as hex values instead of tokens

**Fix in Figma:**
1. Create color styles if not existing
2. Apply color styles to all fills/strokes
3. Verify variable naming: `color/family/shade`

---

### Missing Description

**Problem:** Component has no description for LLM

**Fix in Figma:**
1. Select component set
2. Open Design panel → Description
3. Add 2-3 sentence description:
   ```
   [What it is]. [What it does]. [Where it's used].
   ```

---

## Checklist Template (Copy & Paste)

```markdown
## Component: [Name]
Date: [YYYY-MM-DD]
Reviewer: [Name]

### Blockers
- [ ] Score ≥ 70
- [ ] Focus state
- [ ] Disabled state
- [ ] No artifacts
- [ ] Description

### Implementation
- [ ] Variants complete
- [ ] Tokens used
- [ ] Consistent styling
- [ ] Accessible
- [ ] Clean code

### Metadata
- [ ] Tags
- [ ] testId
- [ ] ariaLabel
- [ ] Do's/Don'ts
- [ ] Specs

### Decision
- [ ] ✅ Ready
- [ ] ⚠️ Ready with notes
- [ ] ❌ Not ready

Notes:
_____________________
```
