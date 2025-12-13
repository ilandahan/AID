---
name: atomic-design
description: Expert-level Atomic Design System development from Figma style guides. Use this skill when building a design system from Figma designs, creating reusable component libraries with atoms, molecules, organisms, templates, and pages, extracting design tokens from Figma via MCP, developing responsive React/Vue/HTML component systems, or ensuring design consistency across an application.
---

# Atomic Design System

Build production-ready design systems using Atomic Design methodology.

## ⚠️ CRITICAL RULE: Figma Is The Source of Truth

```
┌─────────────────────────────────────────────────────────────────────┐
│  🚨 MANDATORY: ALWAYS EXTRACT AND IMPLEMENT FROM FIGMA EXACTLY      │
│                                                                      │
│  1. NEVER guess or assume design values                             │
│  2. ALWAYS use Figma MCP to extract EXACT specs before coding       │
│  3. Download code/CSS from Figma Dev Mode when available            │
│  4. If Figma shows different values than existing tokens → UPDATE   │
│  5. Implementation MUST match Figma pixel-perfect                   │
│                                                                      │
│  ❌ "אני חושב שזה ייראה יותר טוב ככה" = FORBIDDEN                    │
│  ✅ "Figma מראה X, אז הקוד יהיה X" = CORRECT                         │
└─────────────────────────────────────────────────────────────────────┘
```

### Figma-First Workflow (REQUIRED)

```
BEFORE writing ANY component or style code:

1. EXTRACT FROM FIGMA (MANDATORY - NO EXCEPTIONS)
   │
   ├─► Use Figma MCP: get_code_connect_map / get_node
   ├─► Copy specs: colors, spacing, typography, effects
   ├─► Download generated code if available
   ├─► Document ALL extracted values
   │
2. COMPARE WITH EXISTING
   │
   ├─► Check current tokens/*.json
   ├─► If Figma differs → UPDATE tokens (Figma wins ALWAYS)
   ├─► Document changes in commit message
   │
3. IMPLEMENT EXACTLY
   │
   └─► Match Figma specs 1:1 - NO interpretation
       NO rounding, NO "improvements", NO creative freedom
```

### Zero Deviation Policy

| Forbidden Action | Why It's Wrong | Correct Action |
|------------------|----------------|----------------|
| Round `13px` to `12px` | Unauthorized change | Use exact `13px` |
| Change `#3B82F6` to `#3F85F7` | Designer chose that color | Use exact `#3B82F6` |
| Add shadow not in Figma | Creative decision | No shadow if not designed |
| "Improve" spacing | Not your role | Exact spacing from Figma |
| Use different font | Breaking brand | Exact font from Figma |

**Read:** `references/design-deviation-rules.md` for complete deviation policy.

---

## When to Use This Skill

| Trigger | Action |
|---------|--------|
| "Create a Button component" | FIRST: Extract from Figma → THEN: Build |
| "Style this element" | FIRST: Check Figma specs → THEN: Apply |
| "Build a page/form/layout" | Switch to atomic-page-builder skill |
| "Extract tokens from Figma" | Use this skill |
| "What color should I use?" | Extract from Figma → Read `tokens/colors.json` |

---

## Decision Tree: What to Do

```
User Request
     │
     ├─► "Create new component"
     │        │
     │        ├─► STEP 1: Extract from Figma MCP (MANDATORY)
     │        │        └─► get_node / get_code_connect_map
     │        │        └─► Document ALL values extracted
     │        │
     │        ├─► STEP 2: Verify/Update tokens if needed
     │        │        └─► Figma values ALWAYS win
     │        │
     │        ├─► Is it an Atom? (Button, Input, Icon)
     │        │        └─► Build from Figma specs + tokens
     │        │
     │        ├─► Is it a Molecule? (FormField, Card)
     │        │        └─► Use existing Atoms → Compose per Figma
     │        │
     │        └─► Is it an Organism? (Header, Form)
     │                 └─► Use existing Molecules + Atoms → Match Figma layout
     │
     ├─► "Build a page"
     │        └─► Switch to atomic-page-builder skill
     │            (Extract page specs from Figma FIRST)
     │
     ├─► "Extract from Figma"
     │        └─► Read references/figma-mcp-integration.md
     │            Use Figma MCP to extract tokens
     │
     └─► "Style something"
              └─► Extract exact values from Figma
                  Update tokens if different
                  Apply semantic token names
```

---

## Figma MCP Commands (Use These FIRST)

```typescript
// ALWAYS START WITH THESE BEFORE CODING

// 1. Get component specs
figma.get_node(file_key, node_id)

// 2. Get code snippets (if available)
figma.get_code_connect_map(file_key, node_id)

// 3. Get styles from selection
figma.get_styles(file_key, style_type)

// 4. Get local variables (design tokens)
figma.get_local_variables(file_key)
```

### Example: Creating a Button

```
❌ WRONG: Start coding with assumptions
const Button = () => <button className="...">  // Guessing styles

✅ CORRECT: Extract first, then implement
1. figma.get_node("file_key", "button_node_id")
2. Extract: padding: 12px 24px, radius: 8px, bg: #3B82F6
3. Compare with tokens/components.json
4. Update tokens if different
5. Implement EXACTLY as Figma shows - NO changes
```

**Read:** `references/figma-design-fidelity.md` for complete extraction workflow.

---

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
/* DO: Use semantic names (extracted from Figma) */
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
│  TOKENS       colors, typography, spacing (FROM FIGMA)          │
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

### 1. Figma Specs Are Mandatory
```css
/* ✅ CORRECT - Values from Figma extraction */
.button {
  padding: 12px 24px;      /* Extracted from Figma - EXACT */
  border-radius: 8px;       /* Extracted from Figma - EXACT */
  background: #3B82F6;      /* Extracted from Figma - EXACT */
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
  variant?: 'primary' | 'secondary';  // Predefined visual (from Figma)
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
/* Read tokens/components.json for specs (extracted from Figma) */
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
/* ALL breakpoint values from Figma frames */
.card {
  padding: var(--spacing-4);        /* Mobile - from Figma Mobile frame */
}

@media (min-width: 768px) {
  .card { padding: var(--spacing-6); }  /* Tablet - from Figma Tablet frame */
}

@media (min-width: 1024px) {
  .card { padding: var(--spacing-8); }  /* Desktop - from Figma Desktop frame */
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
| Coding without Figma extraction | Values will be wrong | ALWAYS extract first |
| `style={{ color: '#3B82F6' }}` | Hardcoded color | Use `var(--color-primary)` |
| Guessing spacing values | Won't match design | Extract from Figma |
| Rounding `13px` to `12px` | Unauthorized change | Use exact Figma value |
| "Improving" colors | Not developer's role | Use exact Figma value |
| `className="p-4 text-sm"` | Tailwind in design system | Use CSS Modules + tokens |
| `<Button fontSize="14px">` | Visual prop exposed | Remove prop, encapsulate |
| Creating Atom inside Organism | Wrong hierarchy | Create Atom separately first |
| Ignoring Figma changes | Design drift | Always sync with Figma |

---

## Workflow: Create New Component

### Step 0: EXTRACT FROM FIGMA (MANDATORY)
```
1. Open Figma Dev Mode (Shift+D)
2. Select the component
3. Use MCP to extract:
   - Dimensions, padding, margins
   - Colors (fill, stroke)
   - Typography (font, size, weight)
   - Effects (shadow, blur)
   - Border radius
4. Document ALL extracted values
5. Compare with existing tokens
6. Update tokens if Figma differs (Figma WINS)
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
1. FIRST: Extract from Figma via MCP
2. Compare with tokens/components.json → Update if different
3. Read tokens/colors.json → Update if different
4. Read tokens/spacing.json → Update if different
5. Read tokens/typography.json → Update if different
```

### Step 3: Create Files
```
src/design-system/atoms/Button/
├── Button.tsx           # Component + Props
├── Button.module.css    # All styles (tokens only, from Figma)
├── Button.test.tsx      # Tests
└── index.ts             # Export
```

### Step 4: Implement Pattern
```tsx
/**
 * Button Component
 *
 * @figma https://figma.com/file/xxx/Design-System?node-id=123
 * @extracted 2024-01-15
 *
 * All values from Figma - DO NOT MODIFY without designer approval.
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

### When Something Looks "Wrong" in Figma

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

- [ ] ⚠️ Specs extracted from Figma (not guessed)
- [ ] ⚠️ Tokens updated if Figma values differ
- [ ] ⚠️ NO values rounded or "improved"
- [ ] ⚠️ Visual comparison shows 0% difference from Figma
- [ ] Correct atomic level (atom/molecule/organism)
- [ ] Uses ONLY semantic tokens (no hardcoded values)
- [ ] Props are content/behavior only (no visual props)
- [ ] Responsive at all breakpoints (per Figma frames)
- [ ] TypeScript interfaces complete
- [ ] Accessibility attributes (ARIA, keyboard)
- [ ] CSS Module file with token-based styles
- [ ] Figma link documented in component

---

## References (Read When Needed)

| File | When to Read |
|------|--------------|
| `tokens/colors.json` | Need color values |
| `tokens/typography.json` | Need font specs |
| `tokens/spacing.json` | Need spacing/shadows |
| `tokens/components.json` | Building Button/Input/Card |
| `tokens/breakpoints.json` | Adding responsive styles |
| `references/figma-design-fidelity.md` | **Complete Figma extraction guide** |
| `references/design-deviation-rules.md` | **Zero deviation policy** |
| `references/atomic-hierarchy.md` | Full component examples |
| `references/component-templates.md` | Copy-paste templates |
| `references/figma-mcp-integration.md` | Extracting from Figma |
| `references/responsive-patterns.md` | Responsive patterns |
