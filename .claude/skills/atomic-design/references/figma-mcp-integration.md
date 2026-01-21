# Figma MCP Integration

Extraction from Figma is MANDATORY before any coding.

## Prerequisites

- Figma Desktop (latest)
- Dev Mode enabled
- Claude Code with Figma MCP

## Enable MCP

1. Open Figma Desktop
2. Open design file
3. Toggle Dev Mode (Shift+D)
4. Click "Enable desktop MCP server" in inspect panel
5. Server at http://127.0.0.1:3845/mcp

## Two Methods

### Selection-Based (Recommended)
1. Select frame/component in Figma
2. Ask Claude: "Extract design tokens from my current Figma selection"

### Link-Based
1. Copy Figma link (Right-click -> Copy link)
2. Ask Claude: "Extract tokens from: [figma-link]"

## Token Extraction Workflow

1. Navigate to Style Guide in Figma
2. Select token groups (Colors, Typography, Spacing)
3. Request: "Extract all color tokens and generate CSS variables"

## Figma Structure

```
Style Guide:
  Colors -> Primitives, Semantic
  Typography -> Fonts, Scale, Styles
  Spacing -> Base unit, Scale
  Effects -> Shadows, Blurs
  Borders -> Radii, Widths
  Breakpoints -> Device widths
```

## Critical: Use EXACT Values

```
Figma: #3B82F6 -> Code: #3B82F6 (not #3F85F7)
Figma: 13px -> Code: 13px (not 12px)
Figma: 450 weight -> Code: font-weight: 450 (not 500)
```

## Color Tokens

```typescript
const colors = {
  primitives: {
    blue: { 500: '#3b82f6', 600: '#2563eb' }
  },
  semantic: {
    primary: 'var(--color-blue-500)',
    primaryHover: 'var(--color-blue-600)',
    text: { primary: 'var(--color-gray-900)', secondary: 'var(--color-gray-600)' },
    border: { default: 'var(--color-gray-200)' }
  }
};
```

## Typography Tokens

```typescript
const typography = {
  fonts: {
    heading: '"Inter", sans-serif',
    body: '"Inter", sans-serif'
  },
  fontSizes: {
    sm: '0.875rem',
    base: '1rem',
    lg: '1.125rem'
  },
  fontWeights: { normal: 400, medium: 500, bold: 700 },
  lineHeights: { tight: 1.25, normal: 1.5 }
};
```

## Spacing Tokens

```typescript
const spacing = {
  1: '0.25rem',  // 4px
  2: '0.5rem',   // 8px
  3: '0.75rem',  // 12px
  4: '1rem',     // 16px
  6: '1.5rem',   // 24px
  8: '2rem'      // 32px
};
```

## Effects Tokens

```typescript
const effects = {
  shadows: {
    sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    md: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
  },
  borderRadius: {
    sm: '0.125rem',
    md: '0.375rem',
    lg: '0.5rem'
  },
  transitions: {
    fast: '150ms ease',
    base: '200ms ease'
  }
};
```

## Component Spec Extraction

```
figma.get_node(file_key, node_id)
```

Extract:
- Dimensions (width, height)
- Padding (auto-layout)
- Gap (auto-layout)
- Corner radius
- Fill/stroke colors
- Effects (shadows)
- Text properties

## Documentation Template

```typescript
/**
 * Button Component
 *
 * @figma https://figma.com/file/xxx?node-id=123
 * @extracted 2024-01-15
 *
 * Specs (DO NOT MODIFY):
 * - height: 48px (md)
 * - padding: 12px 24px
 * - background: #3B82F6
 * - border-radius: 8px
 * - font: Inter 16px/500
 *
 * States:
 * - hover: bg #2563EB
 * - disabled: bg #E5E7EB
 */
```

## Handling Updates

When Figma changes:
1. Extract NEW values
2. Compare with existing tokens
3. Update tokens/*.json
4. Regenerate CSS
5. Commit: "sync: Update tokens from Figma [date]"

## Output: CSS Variables

```css
:root {
  --color-primary: #3b82f6;
  --color-primary-hover: #2563eb;
  --font-heading: 'Inter', sans-serif;
  --font-size-base: 1rem;
  --spacing-4: 1rem;
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --radius-lg: 0.5rem;
}
```
