---
name: atomic-design
description: "Atomic Design System development. Use when building UI components, styling, or creating pages. Read token files only when needed."
---

# Atomic Design System

Build production-ready design systems using Atomic Design methodology.

## When to Load This Skill

| Trigger | Action |
|---------|--------|
| "Create a Button component" | Load this skill |
| "Style this element" | Load this skill |
| "Build a page/form/layout" | Load this skill |
| "Extract tokens from Figma" | Load this skill |
| "What color should I use?" | Read `tokens/colors.json` |

---

## Decision Tree: What to Do

```
User Request
     │
     ├─► "Create new component"
     │        │
     │        ├─► Is it an Atom? (Button, Input, Icon)
     │        │        └─► Read tokens/*.json → Build from scratch
     │        │
     │        ├─► Is it a Molecule? (FormField, Card)
     │        │        └─► Use existing Atoms → Compose
     │        │
     │        └─► Is it an Organism? (Header, Form)
     │                 └─► Use existing Molecules + Atoms → Compose
     │
     ├─► "Build a page"
     │        └─► Switch to atomic-page-builder skill
     │            (Only compose, never create new components)
     │
     ├─► "Extract from Figma"
     │        └─► Read references/figma-mcp-integration.md
     │            Use Figma MCP to extract tokens
     │
     └─► "Style something"
              └─► Read relevant tokens/*.json
                  Apply semantic token names
```

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
/* DO: Use semantic names */
color: var(--color-primary);
padding: var(--spacing-component-padding);

/* DON'T: Use primitives directly */
color: var(--blue-500);  /* Wrong */
padding: 16px;           /* Wrong */
```

---

## Atomic Hierarchy

```
┌─────────────────────────────────────────────────────┐
│  PAGES        Dashboard, Settings, UserProfile      │
│       ↑                                             │
│  TEMPLATES    DashboardLayout, AuthLayout           │
│       ↑                                             │
│  ORGANISMS    Header, Sidebar, Form, DataTable      │
│       ↑                                             │
│  MOLECULES    FormField, SearchBar, Card, NavItem   │
│       ↑                                             │
│  ATOMS        Button, Input, Typography, Icon       │
│       ↑                                             │
│  TOKENS       colors, typography, spacing           │
└─────────────────────────────────────────────────────┘
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

### 1. Props = Content Only
```typescript
// ✅ CORRECT
interface ButtonProps {
  children: ReactNode;      // Content
  onClick: () => void;      // Behavior
  variant?: 'primary' | 'secondary';  // Predefined visual
  disabled?: boolean;       // State
}

// ❌ WRONG - Visual properties exposed
interface ButtonProps {
  backgroundColor?: string; // NO
  fontSize?: string;        // NO
  padding?: string;         // NO
}
```

### 2. All Styles Encapsulated
```typescript
// Component handles ALL its visual styles internally
// Read tokens/components.json for button specs
.button {
  background: var(--color-primary);
  padding: var(--spacing-button-padding-y) var(--spacing-button-padding-x);
  font-size: var(--font-size-button);
  border-radius: var(--radius-md);
}
```

### 3. Responsive Built-In
```css
/* Mobile-first: Start small, add breakpoints up */
.card {
  padding: var(--spacing-4);        /* Mobile */
}

@media (min-width: 768px) {
  .card { padding: var(--spacing-6); }  /* Tablet+ */
}

@media (min-width: 1024px) {
  .card { padding: var(--spacing-8); }  /* Desktop+ */
}
```

### 4. Accessibility Required
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
| `style={{ color: '#3B82F6' }}` | Hardcoded color | Use `var(--color-primary)` |
| `className="p-4 text-sm"` | Tailwind in design system | Use CSS Modules + tokens |
| `<Button fontSize="14px">` | Visual prop exposed | Remove prop, encapsulate |
| Creating Atom inside Organism | Wrong hierarchy | Create Atom separately first |
| Importing external UI lib | Inconsistent design | Use only internal components |

---

## Workflow: Create New Component

### Step 1: Classify Level
```
Is this component breakable into smaller parts?
├─► No  → It's an ATOM
└─► Yes → What does it compose?
         ├─► Only Atoms → MOLECULE
         └─► Molecules + Atoms → ORGANISM
```

### Step 2: Read Required Tokens
```
For Button (Atom):
1. Read tokens/components.json → button section
2. Read tokens/colors.json → semantic colors
3. Read tokens/spacing.json → padding values
4. Read tokens/typography.json → font specs
```

### Step 3: Create Files
```
src/design-system/atoms/Button/
├── Button.tsx           # Component + Props
├── Button.module.css    # All styles (tokens only)
├── Button.test.tsx      # Tests
└── index.ts             # Export
```

### Step 4: Implement Pattern
```tsx
// Button.tsx
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

## Workflow: Extract from Figma

### Prerequisites
- Figma Desktop with Dev Mode enabled (Shift+D)
- MCP server running at `http://127.0.0.1:3845/mcp`

### Process
```
1. Open Figma → Navigate to style guide
2. Select token frames (Colors, Typography, Spacing)
3. Ask Claude:
   "Extract design tokens from my current Figma selection"
4. Claude generates tokens/*.json files
5. Update CSS variables from JSON
```

**Detailed guide:** `references/figma-mcp-integration.md`

---

## Quick Reference

### Common Components by Level

**Atoms:**
`Button`, `Input`, `Textarea`, `Select`, `Checkbox`, `Radio`, `Switch`, `Icon`, `Avatar`, `Badge`, `Spinner`, `Typography`

**Molecules:**
`FormField`, `SearchBar`, `Card`, `NavItem`, `MenuItem`, `Toast`, `Tooltip`, `Dropdown`, `Tabs`, `Breadcrumb`

**Organisms:**
`Header`, `Sidebar`, `Footer`, `Form`, `DataTable`, `Modal`, `Drawer`, `Pagination`, `Calendar`

**Templates:**
`DashboardLayout`, `AuthLayout`, `SettingsLayout`, `MarketingLayout`

---

## Checklist Before Delivery

- [ ] Correct atomic level (atom/molecule/organism)
- [ ] Uses ONLY semantic tokens (no hardcoded values)
- [ ] Props are content/behavior only (no visual props)
- [ ] Responsive at all breakpoints
- [ ] TypeScript interfaces complete
- [ ] Accessibility attributes (ARIA, keyboard)
- [ ] CSS Module file with token-based styles

---

## References (Read When Needed)

| File | When to Read |
|------|--------------|
| `tokens/colors.json` | Need color values |
| `tokens/typography.json` | Need font specs |
| `tokens/spacing.json` | Need spacing/shadows |
| `tokens/components.json` | Building Button/Input/Card |
| `tokens/breakpoints.json` | Adding responsive styles |
| `references/atomic-hierarchy.md` | Full component examples |
| `references/component-templates.md` | Copy-paste templates |
| `references/figma-mcp-integration.md` | Extracting from Figma |
| `references/responsive-patterns.md` | Responsive patterns |
