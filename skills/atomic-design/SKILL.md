---
name: atomic-design
description: Build an Atomic Design system from design spec style guides - extract tokens, create atoms/molecules/organisms/templates/pages as reusable component libraries. Use when building or extending a design system or component library.
---

# Atomic Design System

## When to Use

| Trigger | Action |
|---|---|
| Create a component | Extract from design spec -> Build |
| Style element | Check design spec specs -> Apply |
| Extract tokens | Use this skill |
| Build page/form/layout | Switch to atomic-page-builder |

## Critical Rule: design spec Is Source of Truth

Extract and implement from design spec exactly. Never guess design values.

1. READ THE APPROVED DESIGN SPEC (mandatory). Use local specification files, exported assets, screenshots and token definitions supplied by the user. Copy exact values and document their source. Ask for missing measurements instead of inventing them.
2. COMPARE WITH EXISTING - check current tokens/*.json. If design spec differs -> UPDATE tokens (design spec wins always).
3. IMPLEMENT EXACTLY - match design spec specs 1:1. No rounding, no improvements, no creative freedom.

### Zero Deviation Policy

| Forbidden | Correct |
|---|---|
| Round 13px to 12px | Use exact 13px |
| Change #3B82F6 to #3F85F7 | Use exact #3B82F6 |
| Add shadow not in design spec | No shadow if not designed |
| Improve spacing | Exact spacing from design spec |

## Design input

Read approved local specification files, token definitions and exported assets. Document their source paths and exact values. Ask for missing values before coding.

## Design Tokens

| Need | File | Key Values |
|---|---|---|
| Colors | tokens/colors.json | semantic.primary, semantic.error |
| Typography | tokens/typography.json | semantic.heading-1, semantic.body |
| Spacing | tokens/spacing.json | semantic.component-padding |
| Components | tokens/components.json | button.variants, input.states |
| Breakpoints | tokens/breakpoints.json | md: 768px, lg: 1024px |

Use semantic token names, never primitives:

```css
color: var(--color-primary);              /* DO */
padding: var(--spacing-component-padding);/* DO */
color: var(--blue-500);  /* Wrong - primitive */
padding: 16px;           /* Wrong - hardcoded */
```

## Atomic Hierarchy

```
PAGES      -> Dashboard, Settings, UserProfile
TEMPLATES  -> DashboardLayout, AuthLayout
ORGANISMS  -> Header, Sidebar, Form, DataTable
MOLECULES  -> FormField, SearchBar, Card, NavItem
ATOMS      -> Button, Input, Typography, Icon
TOKENS     -> colors, typography, spacing (FROM design spec)
```

| Level | Rule | Example |
|---|---|---|
| Atom | Uses ONLY tokens | Button uses color/spacing tokens |
| Molecule | Combines 2+ Atoms | FormField = Label + Input + ErrorText |
| Organism | Combines Molecules + Atoms | Header = Logo + NavItems + UserMenu |
| Template | Layout structure, no content | DashboardLayout |
| Page | Template + real content | Dashboard |

## Core Rules

### 1. Props = Content/Behavior Only

```typescript
// Correct
interface ButtonProps {
  children: ReactNode;
  onClick: () => void;
  variant?: 'primary' | 'secondary';
  disabled?: boolean;
}
// Wrong - visual props exposed
interface ButtonProps {
  backgroundColor?: string;  // NO
  fontSize?: string;         // NO
}
```

### 2. All Styles Encapsulated

```css
.button {
  background: var(--color-primary);
  padding: var(--spacing-button-padding-y) var(--spacing-button-padding-x);
  font-size: var(--font-size-button);
}
```

### 3. Responsive Built-In

```css
.card { padding: var(--spacing-4); }  /* Mobile */
@media (min-width: 768px) { .card { padding: var(--spacing-6); } }  /* Tablet */
@media (min-width: 1024px) { .card { padding: var(--spacing-8); } } /* Desktop */
```

### 4. Accessibility Required

```tsx
<button
  aria-label={iconOnly ? label : undefined}
  aria-busy={loading}
  aria-disabled={disabled}
>
```

## Workflow: Create New Component

### Step 0: Extract from design spec (mandatory)

1. Open the approved local design specification or export
2. Identify the component and its documented states
3. Extract: dimensions, padding, colors, typography, effects, border radius
4. Document ALL extracted values
5. Compare with existing tokens
6. Update tokens if design spec differs

### Step 1: Classify Level

```
Is component breakable into smaller parts?
  No  -> ATOM
  Yes -> What does it compose?
    Only Atoms      -> MOLECULE
    Molecules+Atoms -> ORGANISM
```

### Step 2: Create Files

```
src/design-system/atoms/Button/
  Button.tsx          # Component + Props
  Button.module.css   # All styles (tokens only)
  Button.test.tsx     # Tests
  index.ts            # Export
```

### Step 3: Implement Pattern

Head every component file with the design spec provenance comment:

```tsx
/**
 * @design-source ./design-spec.md
 * @extracted 2024-01-15
 * All values from design spec - DO NOT MODIFY without designer approval.
 */
```

Props: content/behavior only, e.g. `variant?: 'primary' | 'secondary' | 'ghost' | 'danger'`, `size?: 'sm' | 'md' | 'lg'`, `disabled?`, `onClick?`, `children`. Styles come from `./Button.module.css` via `clsx(styles.button, styles[variant], styles[size])`. Full template: references/component-templates.md

## Checklist Before Delivery

- [ ] Specs extracted from design spec (not guessed)
- [ ] Tokens updated if design spec values differ
- [ ] NO values rounded or improved
- [ ] Visual comparison shows 0% difference from design spec
- [ ] Correct atomic level
- [ ] Uses ONLY semantic tokens
- [ ] Props are content/behavior only
- [ ] Responsive at all breakpoints
- [ ] TypeScript interfaces complete
- [ ] Accessibility attributes
- [ ] design spec link documented

## References

| File | When to Read |
|---|---|
| tokens/*.json | Need specific token values |
| references/design-deviation-rules.md | design spec extraction guide |
| references/design-deviation-rules.md | Zero deviation policy |
| references/atomic-hierarchy.md | Component examples |
| references/component-templates.md | Copy-paste templates |
| references/responsive-patterns.md | Responsive patterns |
