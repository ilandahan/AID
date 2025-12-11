# /design-system Command

Build a complete design system from Figma using Atomic Design methodology.

## Usage

```
/design-system [figma-link]
```

## What It Does

1. **Extracts Design Tokens**
   - Colors (primitives + semantic)
   - Typography (fonts, sizes, weights)
   - Spacing scale
   - Effects (shadows, borders, radii)

2. **Generates Components**
   - Atoms → Molecules → Organisms → Templates
   - Full TypeScript interfaces
   - CSS Modules with tokens

3. **Uses Skill**
   - `atomic-design` skill for methodology

## Prerequisites

- Figma Desktop with Dev Mode enabled, OR
- Figma API key configured

## Examples

```bash
# From Figma selection (Dev Mode MCP)
/design-system

# From Figma link
/design-system https://figma.com/file/xxx

# Extract only tokens
/design-system --tokens-only

# Generate specific component level
/design-system --level atoms
```

## Output Structure

```
design-system/
├── tokens/
│   ├── primitives.ts
│   ├── semantic.ts
│   ├── variables.css
│   └── index.ts
├── atoms/
│   ├── Button/
│   ├── Input/
│   ├── Typography/
│   └── index.ts
├── molecules/
│   ├── FormField/
│   ├── Card/
│   └── index.ts
├── organisms/
│   ├── Header/
│   ├── Form/
│   └── index.ts
└── templates/
    ├── DashboardLayout/
    └── index.ts
```

## Workflow

1. Read `skills/atomic-design/SKILL.md`
2. Read `skills/atomic-design/references/figma-mcp-integration.md`
3. Connect to Figma (MCP or link)
4. Extract design tokens
5. Generate CSS variables
6. Build atoms first
7. Compose molecules from atoms
8. Compose organisms from molecules
9. Create layout templates

## Component Standards

Every component includes:
- All visual styles encapsulated
- Responsive behavior (breakpoints)
- Only content as props
- Full TypeScript types
- Accessibility attributes

## Breakpoints

| Name | Size | Device |
|------|------|--------|
| xs | 320px | Small mobile |
| sm | 480px | Mobile landscape |
| md | 768px | Tablet |
| lg | 1024px | Small laptop |
| xl | 1280px | Desktop |
| 2xl | 1440px | Large desktop |
| 3xl | 1920px | Wide screens |

## Tips

- Start with tokens extraction
- Build atoms before molecules
- Test responsive at all breakpoints
- Use semantic token names
- Never hardcode visual values

---

## Prompt

```markdown
**Role**: You are an expert UI engineer specializing in design systems, Atomic Design methodology, and Figma-to-code workflows.

**Task**: Build a complete design system from the provided Figma style guide using Atomic Design principles.

**Context**:
- Figma source: [FIGMA LINK OR SELECTION]
- Framework: React with TypeScript
- Styling: CSS Modules with CSS custom properties
- Read: `skills/atomic-design/SKILL.md`
- Read: `skills/atomic-design/references/figma-mcp-integration.md`

**Reasoning**:
- Extract ALL visual properties into design tokens first
- Build atoms before molecules, molecules before organisms
- Encapsulate ALL styling—props should only be content/behavior
- Use semantic token names (--color-primary not --color-blue-500)
- Every component handles its own responsive behavior

**Output Format**:
1. Design tokens (primitives + semantic)
2. CSS variables file
3. Components by level (atoms → molecules → organisms → templates)
4. TypeScript interfaces
5. Usage examples

**Stopping Condition**:
- All tokens extracted from Figma
- Complete atom set created
- At least 3 molecules composed
- At least 2 organisms composed
- All components responsive
- No hardcoded values

**Steps**:
1. Connect to Figma via MCP or link
2. Extract color tokens
3. Extract typography tokens
4. Extract spacing scale
5. Extract effects (shadows, borders)
6. Generate CSS custom properties
7. Build atoms (Button, Input, Typography, Icon)
8. Compose molecules (FormField, Card, SearchBar)
9. Compose organisms (Header, Form, DataTable)
10. Create templates (DashboardLayout, AuthLayout)
11. Verify responsive behavior
12. Audit accessibility

---
[FIGMA LINK OR DESCRIPTION]
---
```
