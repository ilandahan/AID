---
name: atomic-design
description: "Expert-level Atomic Design System development from Figma style guides. Use this skill when building a design system from Figma designs, creating reusable component libraries with atoms, molecules, organisms, templates, and pages, extracting design tokens from Figma via MCP, developing responsive React/Vue/HTML component systems, or ensuring design consistency across an application. Integrates with Figma MCP for design token extraction and automated component generation."
---

# Atomic Design System Development

Build production-ready, fully typed design systems from Figma style guides using Atomic Design methodology. All visual properties (typography, spacing, colors, responsiveness) are encapsulated in components—only content/labels remain as props.

## Core Workflow

### Phase 1: Design Token Extraction from Figma

**Using Official Figma Dev Mode MCP:**

1. Open Figma Desktop → Enable Dev Mode (Shift+D) → Enable MCP server
2. Navigate to style guide page in Figma
3. Select token frames (Colors, Typography, Spacing sections)
4. Ask Claude Code to extract:

```
"Extract design tokens from my current Figma selection"
"Get all color styles and generate CSS custom properties"
"Extract typography tokens from the selected text styles"
```

**Two approaches:**
- **Selection-based**: Select in Figma → Ask Claude to extract
- **Link-based**: Copy Figma link → Paste with request

See `references/figma-mcp-integration.md` for detailed workflow.

### Phase 2: Token System Architecture

Create hierarchical token structure:

```typescript
// tokens/primitives.ts - Raw values
export const primitives = {
  colors: {
    blue: { 50: '#eff6ff', 500: '#3b82f6', 900: '#1e3a8a' },
    // ... extracted from Figma
  },
  spacing: { 0: '0', 1: '4px', 2: '8px', 3: '12px', 4: '16px', /* ... */ },
  fontSizes: { xs: '12px', sm: '14px', base: '16px', lg: '18px', /* ... */ },
}

// tokens/semantic.ts - Purpose-driven aliases
export const semantic = {
  colors: {
    primary: primitives.colors.blue[500],
    primaryHover: primitives.colors.blue[600],
    textPrimary: primitives.colors.gray[900],
    textSecondary: primitives.colors.gray[600],
    surface: primitives.colors.white,
    border: primitives.colors.gray[200],
  },
  spacing: {
    componentPadding: primitives.spacing[4],
    sectionGap: primitives.spacing[8],
  }
}
```

### Phase 3: Atomic Component Hierarchy

Build components in strict order—each level composes the previous:

```
ATOMS → MOLECULES → ORGANISMS → TEMPLATES → PAGES
```

**See:** `references/atomic-hierarchy.md` for complete component breakdown and examples.

### Phase 4: Component Development Standards

**Every component MUST include:**

1. **All visual styles encapsulated** - typography, colors, spacing, borders
2. **Responsive behavior built-in** - breakpoint-based adjustments
3. **Only content as props** - labels, text, icons, handlers
4. **Full TypeScript types** - strict prop interfaces
5. **Accessibility** - ARIA attributes, keyboard navigation

**Component prop pattern:**
```typescript
// ✅ CORRECT - Only content/behavior as props
interface ButtonProps {
  label: string;
  onClick: () => void;
  icon?: ReactNode;
  disabled?: boolean;
  variant?: 'primary' | 'secondary' | 'ghost'; // Predefined visual variants
}

// ❌ WRONG - Visual properties as props
interface ButtonProps {
  label: string;
  fontSize?: string;      // NO - encapsulate in component
  padding?: string;       // NO - encapsulate in component
  backgroundColor?: string; // NO - use variants
}
```

### Phase 5: Responsive Design Integration

**Breakpoint system (from Figma):**
```typescript
const breakpoints = {
  xs: '320px',   // Small mobile (iPhone SE)
  sm: '480px',   // Mobile landscape
  md: '768px',   // Tablet portrait (iPad)
  lg: '1024px',  // Tablet landscape / Small laptop
  xl: '1280px',  // Desktop
  '2xl': '1440px', // Large desktop
  '3xl': '1920px', // Full HD / Wide screens
}
```

**Every component handles its own responsiveness:**
```css
.button {
  /* Mobile first - base styles */
  padding: var(--spacing-2) var(--spacing-3);
  font-size: var(--font-size-sm);
  width: 100%;
  
  @media (min-width: 480px) {
    width: auto;
  }
  
  @media (min-width: 768px) {
    padding: var(--spacing-3) var(--spacing-4);
    font-size: var(--font-size-base);
  }
  
  @media (min-width: 1440px) {
    padding: var(--spacing-3) var(--spacing-5);
  }
}
```

## File Structure

```
design-system/
├── tokens/
│   ├── primitives.ts      # Raw Figma values
│   ├── semantic.ts        # Purpose-driven aliases
│   └── index.ts           # Unified export
├── atoms/
│   ├── Button/
│   │   ├── Button.tsx
│   │   ├── Button.module.css
│   │   └── index.ts
│   ├── Input/
│   ├── Typography/
│   ├── Icon/
│   └── index.ts
├── molecules/
│   ├── FormField/
│   ├── SearchBar/
│   ├── Card/
│   └── index.ts
├── organisms/
│   ├── Header/
│   ├── Form/
│   ├── DataTable/
│   └── index.ts
├── templates/
│   ├── DashboardLayout/
│   ├── AuthLayout/
│   └── index.ts
└── index.ts               # Public API
```

## Implementation Checklist

Before delivering any component:

- [ ] Visual tokens extracted from Figma
- [ ] Component uses only semantic tokens (no hardcoded values)
- [ ] Responsive styles at all breakpoints
- [ ] Props limited to content/behavior only
- [ ] TypeScript interfaces complete
- [ ] Accessibility attributes included
- [ ] Storybook story created (if applicable)

---

## Prompt: Design System Creation

```markdown
**Role**: You are an expert UI engineer specializing in design systems, component architecture, and Figma-to-code workflows. You have deep expertise in Atomic Design methodology, CSS architecture, TypeScript, and accessibility standards.

**Task**: Build a complete design system from the provided Figma style guide, creating a hierarchical component library following Atomic Design principles (atoms → molecules → organisms → templates → pages).

**Context**:
- Figma style guide: [Link or selection]
- Target framework: React with TypeScript
- Styling approach: CSS Modules with CSS custom properties
- Design tokens available in Figma: colors, typography, spacing, shadows, borders
- Must be responsive (mobile-first)
- Must meet WCAG 2.1 AA accessibility standards

**Reasoning**:
- Extract ALL visual properties into design tokens first
- Build atoms before molecules, molecules before organisms
- Encapsulate ALL styling in components—props should only be content/behavior
- Use semantic token names (--color-primary) not primitive values
- Every component must handle its own responsive behavior
- Never expose visual properties as component props

**Output Format**:
1. Design Tokens (tokens/primitives.ts, tokens/semantic.ts)
2. CSS Variables file (tokens/variables.css)
3. Component files per atomic level:
   - ComponentName.tsx (TypeScript + JSX)
   - ComponentName.module.css (all styles)
   - index.ts (exports)
4. Full TypeScript interfaces for all props
5. Usage examples for each component

**Stopping Condition**:
- All Figma tokens extracted and organized
- Complete atom set (Button, Input, Typography, Icon, Badge, etc.)
- At least 3 molecules composed from atoms
- At least 2 organisms composed from molecules
- All components have responsive styles
- All components have accessibility attributes
- No hardcoded colors, spacing, or typography values

**Steps**:
1. Connect to Figma via MCP or use provided link
2. Extract color tokens → create primitives and semantic colors
3. Extract typography tokens → font families, sizes, weights, line heights
4. Extract spacing scale → base unit and multipliers
5. Extract effects → shadows, borders, radii
6. Generate CSS custom properties file
7. Build atoms one by one (Button, Input, Typography first)
8. Compose molecules from atoms (FormField, SearchBar, Card)
9. Compose organisms from molecules (Header, Form, DataTable)
10. Create template layouts (DashboardLayout, AuthLayout)
11. Verify all components use only semantic tokens
12. Test responsive behavior at all breakpoints
13. Audit accessibility (ARIA, focus states, contrast)

---
[FIGMA LINK OR DESCRIPTION HERE]
---
```

## References

- `references/atomic-hierarchy.md` - Detailed atom/molecule/organism examples
- `references/figma-mcp-integration.md` - Figma MCP commands and token extraction
- `references/responsive-patterns.md` - Mobile-first responsive patterns
- `references/component-templates.md` - Copy-paste component templates
