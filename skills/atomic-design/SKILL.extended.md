---
name: atomic-design
description: Expert-level Atomic Design System development from design spec style guides. Use this skill when building a design system from design spec designs, creating reusable component libraries with atoms, molecules, organisms, templates, and pages, extracting design tokens from approved local design specifications, developing responsive React/Vue/HTML component systems, or ensuring design consistency across an application.
---

# Atomic Design System

Build production-ready design systems using Atomic Design methodology.

## ⚠️ CRITICAL RULE: design spec Is The Source of Truth

```
┌─────────────────────────────────────────────────────────────────────┐
│  🚨 MANDATORY: ALWAYS EXTRACT AND IMPLEMENT FROM design spec EXACTLY      │
│                                                                      │
│  1. NEVER guess or assume design values                             │
│  2. ALWAYS use local design specifications to extract EXACT specs before coding       │
│  3. Download code/CSS from local design exports when available            │
│  4. If design spec shows different values than existing tokens → UPDATE   │
│  5. Implementation MUST match design spec pixel-perfect                   │
│                                                                      │
│  ❌ "אני חושב שזה ייראה יותר טוב ככה" = FORBIDDEN                    │
│  ✅ "design spec מראה X, אז הקוד יהיה X" = CORRECT                         │
└─────────────────────────────────────────────────────────────────────┘
```

### design spec-First Workflow (REQUIRED)

```
BEFORE writing ANY component or style code:

1. EXTRACT FROM design spec (MANDATORY - NO EXCEPTIONS)
   │
Read the approved local design specification and token files.
   ├─► Copy specs: colors, spacing, typography, effects
   ├─► Download generated code if available
   ├─► Document ALL extracted values
   │
2. COMPARE WITH EXISTING
   │
   ├─► Check current tokens/*.json
   ├─► If design spec differs → UPDATE tokens (design spec wins ALWAYS)
   ├─► Document changes in commit message
   │
3. IMPLEMENT EXACTLY
   │
   └─► Match design spec specs 1:1 - NO interpretation
       NO rounding, NO "improvements", NO creative freedom
```

### Zero Deviation Policy

| Forbidden Action | Why It's Wrong | Correct Action |
|------------------|----------------|----------------|
| Round `13px` to `12px` | Unauthorized change | Use exact `13px` |
| Change `#3B82F6` to `#3F85F7` | Designer chose that color | Use exact `#3B82F6` |
| Add shadow not in design spec | Creative decision | No shadow if not designed |
| "Improve" spacing | Not your role | Exact spacing from design spec |
| Use different font | Breaking brand | Exact font from design spec |

**Read:** `references/design-deviation-rules.md` for complete deviation policy.

---

## When to Use This Skill

| Trigger | Action |
|---------|--------|
| "Create a Button component" | FIRST: Extract from design spec → THEN: Build |
| "Style this element" | FIRST: Check design spec specs → THEN: Apply |
| "Build a page/form/layout" | Switch to atomic-page-builder skill |
| "Extract tokens from design spec" | Use this skill |
| "What color should I use?" | Extract from design spec → Read `tokens/colors.json` |

---

## Decision Tree: What to Do

```
User Request
     │
     ├─► "Create new component"
     │        │
     │        ├─► STEP 1: Extract from local design specifications (MANDATORY)
     │        │        └─► read source files and token definitions
     │        │        └─► Document ALL values extracted
     │        │
     │        ├─► STEP 2: Verify/Update tokens if needed
     │        │        └─► design spec values ALWAYS win
     │        │
     │        ├─► Is it an Atom? (Button, Input, Icon)
     │        │        └─► Build from design spec specs + tokens
     │        │
     │        ├─► Is it a Molecule? (FormField, Card)
     │        │        └─► Use existing Atoms → Compose per design spec
     │        │
     │        └─► Is it an Organism? (Header, Form)
     │                 └─► Use existing Molecules + Atoms → Match design spec layout
     │
     ├─► "Build a page"
     │        └─► Switch to atomic-page-builder skill
     │            (Extract page specs from design spec FIRST)
     │
     ├─► "Extract from design spec"
     │        └─► Read references/design-deviation-rules.md
     │            Use local design specifications to extract tokens
     │
     └─► "Style something"
              └─► Extract exact values from design spec
                  Update tokens if different
                  Apply semantic token names
```

---

## Design input

Read the approved local specification, token files and exported assets. Document their paths and exact values. Ask for missing measurements before coding.

## Design Tokens (Read On-Demand)

| Need | Read File | Key Values |
|------|-----------|------------|
| Colors, backgrounds | `tokens/colors.json` | `semantic.primary`, `semantic.error` |
| Font sizes, weights | `tokens/typography.json` | `semantic.heading-1`, `semantic.body` |
| Padding, margins | `tokens/spacing.json` | `semantic.component-padding` |
| Button/Input specs | `tokens/components.json` | `button.variants`, `input.states` |
| Breakpoints | `tokens/breakpoints.json` | `md: 768px`, `lg: 1024px` |

### Token Usage Pattern
```css
/* DO: Use semantic names (extracted from design spec) */
color: var(--color-primary);
padding: var(--spacing-component-padding);

/* DON'T: Use primitives directly */
color: var(--blue-500);  /* Wrong */
padding: 16px;           /* Wrong - use token */
```

---

## Atomic Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│  PAGES        Dashboard, Settings, UserProfile                  │
│       ↑                                                         │
│  TEMPLATES    DashboardLayout, AuthLayout                       │
│       ↑                                                         │
│  ORGANISMS    Header, Sidebar, Form, DataTable                  │
│       ↑                                                         │
│  MOLECULES    FormField, SearchBar, Card, NavItem               │
│       ↑                                                         │
│  ATOMS        Button, Input, Typography, Icon                   │
│       ↑                                                         │
│  TOKENS       colors, typography, spacing (FROM design spec)          │
└─────────────────────────────────────────────────────────────────┘
```

| Level | Rule | Example |
|-------|------|---------|
| **Atom** | Uses ONLY tokens, no other components | `Button` uses color/spacing tokens |
| **Molecule** | Combines 2+ Atoms | `FormField` = Label + Input + ErrorText |
| **Organism** | Combines Molecules + Atoms | `Header` = Logo + NavItems + UserMenu |
| **Template** | Layout structure, no content | `DashboardLayout` = Header + Sidebar + Main |
| **Page** | Template + real content | `Dashboard` = DashboardLayout + widgets |

---

## Core Rules

### 1. design spec Specs Are Mandatory
```css
/* ✅ CORRECT - Values from design spec extraction */
.button {
  padding: 12px 24px;      /* Extracted from design spec - EXACT */
  border-radius: 8px;       /* Extracted from design spec - EXACT */
  background: #3B82F6;      /* Extracted from design spec - EXACT */
}

/* ❌ WRONG - Guessed or "improved" values */
.button {
  padding: 10px 20px;       /* Guessed */
  border-radius: 4px;       /* "Rounded" from 5px */
  background: blue;         /* Vague */
}
```

### 2. Props = Content Only
```typescript
// ✅ CORRECT
interface ButtonProps {
  children: ReactNode;      // Content
  onClick: () => void;      // Behavior
  variant?: 'primary' | 'secondary';  // Predefined visual (from design spec)
  disabled?: boolean;       // State
}

// ❌ WRONG - Visual properties exposed
interface ButtonProps {
  backgroundColor?: string; // NO - breaks design system
  fontSize?: string;        // NO - breaks design system
  padding?: string;         // NO - breaks design system
}
```

### 3. All Styles Encapsulated
```css
/* Component handles ALL its visual styles internally */
/* Read tokens/components.json for specs (extracted from design spec) */
.button {
  background: var(--color-primary);
  padding: var(--spacing-button-padding-y) var(--spacing-button-padding-x);
  font-size: var(--font-size-button);
  border-radius: var(--radius-md);
}
```

### 4. Responsive Built-In
```css
/* Mobile-first: Start small, add breakpoints up */
/* ALL breakpoint values from design spec frames */
.card {
  padding: var(--spacing-4);        /* Mobile - from design spec Mobile frame */
}

@media (min-width: 768px) {
  .card { padding: var(--spacing-6); }  /* Tablet - from design spec Tablet frame */
}

@media (min-width: 1024px) {
  .card { padding: var(--spacing-8); }  /* Desktop - from desktop design frame */
}
```

### 5. Accessibility Required
```tsx
<button
  aria-label={iconOnly ? label : undefined}
  aria-busy={loading}
  aria-disabled={disabled}
  disabled={disabled}
>
  {label}
</button>
```

---

## Anti-Patterns (Don't Do This)

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| Coding without design spec extraction | Values will be wrong | ALWAYS extract first |
| `style={{ color: '#3B82F6' }}` | Hardcoded color | Use `var(--color-primary)` |
| Guessing spacing values | Won't match design | Extract from design spec |
| Rounding `13px` to `12px` | Unauthorized change | Use exact design spec value |
| "Improving" colors | Not developer's role | Use exact design spec value |
| `className="p-4 text-sm"` | Tailwind in design system | Use CSS Modules + tokens |
| `<Button fontSize="14px">` | Visual prop exposed | Remove prop, encapsulate |
| Creating Atom inside Organism | Wrong hierarchy | Create Atom separately first |
| Ignoring design spec changes | Design drift | Always sync with design spec |

---

## Workflow: Create New Component

### Step 0: EXTRACT FROM design spec (MANDATORY)
```
1. Open the approved local design specification
2. Select the component
3. Use MCP to extract:
   - Dimensions, padding, margins
   - Colors (fill, stroke)
   - Typography (font, size, weight)
   - Effects (shadow, blur)
   - Border radius
4. Document ALL extracted values
5. Compare with existing tokens
6. Update tokens if design spec differs (design spec WINS)
```

### Step 1: Classify Level
```
Is this component breakable into smaller parts?
├─► No  → It's an ATOM
└─► Yes → What does it compose?
         ├─► Only Atoms → MOLECULE
         └─► Molecules + Atoms → ORGANISM
```

### Step 2: Read/Update Required Tokens
```
For Button (Atom):
1. FIRST: Extract from approved local design specifications
2. Compare with tokens/components.json → Update if different
3. Read tokens/colors.json → Update if different
4. Read tokens/spacing.json → Update if different
5. Read tokens/typography.json → Update if different
```

### Step 3: Create Files
```
src/design-system/atoms/Button/
├── Button.tsx           # Component + Props
├── Button.module.css    # All styles (tokens only, from design spec)
├── Button.test.tsx      # Tests
└── index.ts             # Export
```

### Step 4: Implement Pattern
```tsx
/**
 * Button Component
 *
 * @design-source ./design-spec.md
 * @extracted 2024-01-15
 *
 * All values from design spec - DO NOT MODIFY without designer approval.
 */

import styles from './Button.module.css';
import clsx from 'clsx';

interface ButtonProps {
  children: ReactNode;
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  onClick?: () => void;
}

export const Button = ({
  children,
  variant = 'primary',
  size = 'md',
  disabled,
  onClick
}: ButtonProps) => (
  <button
    className={clsx(styles.button, styles[variant], styles[size])}
    disabled={disabled}
    onClick={onClick}
  >
    {children}
  </button>
);
```

---

## Handling Design Discrepancies

### When Something Looks "Wrong" in design spec

```
DO NOT: "Fix" it yourself
DO NOT: Round values to "nicer" numbers
DO NOT: Make creative decisions

DO: Document the issue
DO: Ask the designer
DO: Wait for confirmation before proceeding
DO: Implement exactly what designer confirms
```

### Question Template for Designer:
```
שמתי לב שב-[frame name] הערך של [property] הוא [value].
זה נראה שונה מ-[expectation].
האם זה מכוון או טעות?
```

---

## Checklist Before Delivery

- [ ] ⚠️ Specs extracted from design spec (not guessed)
- [ ] ⚠️ Tokens updated if design spec values differ
- [ ] ⚠️ NO values rounded or "improved"
- [ ] ⚠️ Visual comparison shows 0% difference from design spec
- [ ] Correct atomic level (atom/molecule/organism)
- [ ] Uses ONLY semantic tokens (no hardcoded values)
- [ ] Props are content/behavior only (no visual props)
- [ ] Responsive at all breakpoints (per design spec frames)
- [ ] TypeScript interfaces complete
- [ ] Accessibility attributes (ARIA, keyboard)
- [ ] CSS Module file with token-based styles
- [ ] design spec link documented in component

---

## References (Read When Needed)

| File | When to Read |
|------|--------------|
| `tokens/colors.json` | Need color values |
| `tokens/typography.json` | Need font specs |
| `tokens/spacing.json` | Need spacing/shadows |
| `tokens/components.json` | Building Button/Input/Card |
| `tokens/breakpoints.json` | Adding responsive styles |
| `references/design-deviation-rules.md` | **Complete design spec extraction guide** |
| `references/design-deviation-rules.md` | **Zero deviation policy** |
| `references/atomic-hierarchy.md` | Full component examples |
| `references/component-templates.md` | Copy-paste templates |
| `references/design-deviation-rules.md` | Extracting from design spec |
| `references/responsive-patterns.md` | Responsive patterns |
