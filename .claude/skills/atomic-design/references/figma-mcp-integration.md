# Figma MCP Integration Guide

Integration with Figma's official Dev Mode MCP Server for extracting design tokens and component specs.

## Prerequisites

- Figma Desktop app (latest version)
- Dev Mode enabled in Figma file
- Claude Code with Figma MCP connected

## Official Figma Dev Mode MCP

The official Figma MCP runs locally from Figma Desktop at:
- Local: `http://127.0.0.1:3845/mcp`
- Remote: `https://mcp.figma.com/mcp`

### How to Enable

1. Open Figma Desktop app (latest version)
2. Open a Figma Design file
3. Toggle to **Dev Mode** (Shift+D)
4. In the inspect panel, click **Enable desktop MCP server**
5. Server runs at `http://127.0.0.1:3845/mcp`

## Two Ways to Work

### Method 1: Selection-Based (Recommended for Design Systems)

1. Select a frame/component in Figma
2. Ask Claude Code:
```
"Extract design tokens from my current Figma selection"
"Get the button component specs from the selected frame"
```

### Method 2: Link-Based

1. Copy Figma link (Right-click â†’ Copy link)
2. Paste in Claude Code:
```
"Extract the color tokens from this style guide: [figma-link]"
"Convert this component to React: [figma-link]"
```

## Extracting Design Tokens Workflow

### Step 1: Navigate in Figma to Style Guide

Open your style guide file and go to the tokens/foundations page.

### Step 2: Select Token Groups

Select the relevant frames:
- Colors section â†’ Extract color tokens
- Typography section â†’ Extract text styles
- Spacing section â†’ Extract spacing scale

### Step 3: Request Extraction

```
"From my current Figma selection, extract all color tokens 
and generate CSS custom properties"
```

### Step 4: Typical Token Structure in Figma

```
Figma Style Guide Structure:
â”œâ”€â”€ ðŸŽ¨ Colors
â”‚   â”œâ”€â”€ Primitives (raw color values)
â”‚   â””â”€â”€ Semantic (purpose-driven aliases)
â”œâ”€â”€ ðŸ“ Typography
â”‚   â”œâ”€â”€ Font families
â”‚   â”œâ”€â”€ Type scale
â”‚   â””â”€â”€ Text styles
â”œâ”€â”€ ðŸ“ Spacing
â”‚   â”œâ”€â”€ Base unit
â”‚   â””â”€â”€ Scale
â”œâ”€â”€ ðŸ”² Effects
â”‚   â”œâ”€â”€ Shadows
â”‚   â””â”€â”€ Blurs
â”œâ”€â”€ ðŸ“ Borders
â”‚   â”œâ”€â”€ Radii
â”‚   â””â”€â”€ Widths
â””â”€â”€ ðŸ“± Breakpoints
    â””â”€â”€ Device widths
```

## Token Transformation Patterns

### From Figma Colors to Code

**Transform to token structure:**
```typescript
// From Figma: "Blue/500" -> #3b82f6
// To tokens:
const colors = {
  primitives: {
    blue: {
      50: '#eff6ff',
      100: '#dbeafe',
      200: '#bfdbfe',
      300: '#93c5fd',
      400: '#60a5fa',
      500: '#3b82f6',  // Primary
      600: '#2563eb',
      700: '#1d4ed8',
      800: '#1e40af',
      900: '#1e3a8a',
    },
    // ... other color palettes
  },
  semantic: {
    // Map to purposes
    primary: 'var(--color-blue-500)',
    primaryHover: 'var(--color-blue-600)',
    primaryActive: 'var(--color-blue-700)',
    
    background: {
      default: 'var(--color-white)',
      subtle: 'var(--color-gray-50)',
      muted: 'var(--color-gray-100)',
    },
    
    text: {
      primary: 'var(--color-gray-900)',
      secondary: 'var(--color-gray-600)',
      muted: 'var(--color-gray-400)',
      inverse: 'var(--color-white)',
    },
    
    border: {
      default: 'var(--color-gray-200)',
      strong: 'var(--color-gray-300)',
    },
    
    status: {
      success: 'var(--color-green-500)',
      warning: 'var(--color-yellow-500)',
      error: 'var(--color-red-500)',
      info: 'var(--color-blue-500)',
    },
  },
};
```

### Step 3: Extract Typography Tokens

**MCP Command:**
```
figma.get_styles(file_key, style_type="TEXT")
```

**Transform to token structure:**
```typescript
const typography = {
  fonts: {
    heading: '"Inter", -apple-system, BlinkMacSystemFont, sans-serif',
    body: '"Inter", -apple-system, BlinkMacSystemFont, sans-serif',
    mono: '"JetBrains Mono", "Fira Code", monospace',
  },
  
  fontSizes: {
    xs: '0.75rem',    // 12px
    sm: '0.875rem',   // 14px
    base: '1rem',     // 16px
    lg: '1.125rem',   // 18px
    xl: '1.25rem',    // 20px
    '2xl': '1.5rem',  // 24px
    '3xl': '1.875rem',// 30px
    '4xl': '2.25rem', // 36px
    '5xl': '3rem',    // 48px
  },
  
  fontWeights: {
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },
  
  lineHeights: {
    none: 1,
    tight: 1.25,
    snug: 1.375,
    normal: 1.5,
    relaxed: 1.625,
    loose: 2,
  },
  
  letterSpacing: {
    tighter: '-0.05em',
    tight: '-0.025em',
    normal: '0',
    wide: '0.025em',
    wider: '0.05em',
  },
  
  // Composed text styles (from Figma text styles)
  textStyles: {
    h1: {
      fontFamily: 'var(--font-heading)',
      fontSize: 'var(--font-size-4xl)',
      fontWeight: 'var(--font-weight-bold)',
      lineHeight: 'var(--line-height-tight)',
      letterSpacing: 'var(--letter-spacing-tight)',
    },
    h2: {
      fontFamily: 'var(--font-heading)',
      fontSize: 'var(--font-size-3xl)',
      fontWeight: 'var(--font-weight-bold)',
      lineHeight: 'var(--line-height-tight)',
    },
    // ... other text styles
    body: {
      fontFamily: 'var(--font-body)',
      fontSize: 'var(--font-size-base)',
      fontWeight: 'var(--font-weight-normal)',
      lineHeight: 'var(--line-height-normal)',
    },
    caption: {
      fontFamily: 'var(--font-body)',
      fontSize: 'var(--font-size-xs)',
      fontWeight: 'var(--font-weight-normal)',
      lineHeight: 'var(--line-height-normal)',
    },
  },
};
```

### Step 4: Extract Spacing Tokens

**From Figma auto-layout values:**
```typescript
const spacing = {
  // Base unit: 4px
  0: '0',
  px: '1px',
  0.5: '0.125rem',  // 2px
  1: '0.25rem',     // 4px
  1.5: '0.375rem',  // 6px
  2: '0.5rem',      // 8px
  2.5: '0.625rem',  // 10px
  3: '0.75rem',     // 12px
  4: '1rem',        // 16px
  5: '1.25rem',     // 20px
  6: '1.5rem',      // 24px
  8: '2rem',        // 32px
  10: '2.5rem',     // 40px
  12: '3rem',       // 48px
  16: '4rem',       // 64px
  20: '5rem',       // 80px
  24: '6rem',       // 96px
};

// Semantic spacing
const semanticSpacing = {
  component: {
    paddingXs: 'var(--spacing-2)',      // 8px - compact elements
    paddingSm: 'var(--spacing-3)',      // 12px - small buttons
    paddingMd: 'var(--spacing-4)',      // 16px - default buttons
    paddingLg: 'var(--spacing-5)',      // 20px - large buttons
  },
  layout: {
    gapSm: 'var(--spacing-2)',          // 8px
    gapMd: 'var(--spacing-4)',          // 16px
    gapLg: 'var(--spacing-6)',          // 24px
    gapXl: 'var(--spacing-8)',          // 32px
    sectionGap: 'var(--spacing-16)',    // 64px
  },
  container: {
    paddingMobile: 'var(--spacing-4)',  // 16px
    paddingTablet: 'var(--spacing-6)',  // 24px
    paddingDesktop: 'var(--spacing-8)', // 32px
  },
};
```

### Step 5: Extract Effects & Borders

```typescript
const effects = {
  shadows: {
    none: 'none',
    sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    base: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
    md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
    lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
    xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
    inner: 'inset 0 2px 4px 0 rgb(0 0 0 / 0.05)',
  },
  
  borderRadius: {
    none: '0',
    sm: '0.125rem',   // 2px
    base: '0.25rem',  // 4px
    md: '0.375rem',   // 6px
    lg: '0.5rem',     // 8px
    xl: '0.75rem',    // 12px
    '2xl': '1rem',    // 16px
    full: '9999px',
  },
  
  borderWidth: {
    0: '0',
    1: '1px',
    2: '2px',
    4: '4px',
  },
  
  transitions: {
    fast: '150ms ease',
    base: '200ms ease',
    slow: '300ms ease',
    slower: '500ms ease',
  },
};
```

### Step 6: Extract Breakpoints

```typescript
const breakpoints = {
  xs: '320px',   // Small mobile (iPhone SE)
  sm: '480px',   // Mobile landscape
  md: '768px',   // Tablet portrait (iPad)
  lg: '1024px',  // Tablet landscape / Small laptop
  xl: '1280px',  // Desktop
  '2xl': '1440px', // Large desktop
  '3xl': '1920px', // Full HD / Wide screens
};

// Media query helpers
const media = {
  xs: `@media (min-width: ${breakpoints.xs})`,
  sm: `@media (min-width: ${breakpoints.sm})`,
  md: `@media (min-width: ${breakpoints.md})`,
  lg: `@media (min-width: ${breakpoints.lg})`,
  xl: `@media (min-width: ${breakpoints.xl})`,
  '2xl': `@media (min-width: ${breakpoints['2xl']})`,
  '3xl': `@media (min-width: ${breakpoints['3xl']})`,
};
```

## Component Spec Extraction

### Reading Component Details from Figma

**MCP Command:**
```
figma.get_node(file_key, node_id)
```

**Extract from component:**
- Dimensions (width, height)
- Padding (from auto-layout)
- Gap (from auto-layout)
- Corner radius
- Fill colors
- Stroke colors and width
- Effects (shadows, blurs)
- Text properties

### Component Variant Mapping

Map Figma variants to code variants:

```
Figma Component: "Button"
â”œâ”€â”€ State=Default, Size=Small, Type=Primary
â”œâ”€â”€ State=Hover, Size=Small, Type=Primary
â”œâ”€â”€ State=Default, Size=Medium, Type=Primary
â”œâ”€â”€ State=Default, Size=Small, Type=Secondary
â””â”€â”€ ...

â†“ Maps to â†“

ButtonProps:
- variant: 'primary' | 'secondary' | 'ghost'
- size: 'sm' | 'md' | 'lg'
- state handled by CSS :hover, :active, :disabled
```

## Output Formats

### CSS Custom Properties

```css
:root {
  /* Colors - Primitives */
  --color-blue-500: #3b82f6;
  --color-blue-600: #2563eb;
  
  /* Colors - Semantic */
  --color-primary: var(--color-blue-500);
  --color-primary-hover: var(--color-blue-600);
  
  /* Typography */
  --font-heading: 'Inter', sans-serif;
  --font-size-base: 1rem;
  
  /* Spacing */
  --spacing-4: 1rem;
  
  /* Effects */
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --radius-lg: 0.5rem;
}
```

### Tailwind Config

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#3b82f6',
          hover: '#2563eb',
        },
      },
      fontFamily: {
        heading: ['Inter', 'sans-serif'],
      },
      spacing: {
        // Custom spacing if needed
      },
    },
  },
};
```

### TypeScript Theme Object

```typescript
export const theme = {
  colors: { /* ... */ },
  typography: { /* ... */ },
  spacing: { /* ... */ },
  effects: { /* ... */ },
  breakpoints: { /* ... */ },
} as const;

export type Theme = typeof theme;
```

## Project Configuration (Optional)

For teams managing multiple projects, create a config file to standardize output:

```typescript
// design-system.config.ts
export interface DesignSystemConfig {
  // Project info
  projectName: string;
  
  // Output configuration  
  output: {
    format: 'css' | 'tailwind' | 'styled-components' | 'scss';
    path: string;
    prefix?: string;  // e.g., 'ds-' for --ds-color-primary
  };
  
  // Token naming convention mapping (Figma name â†’ output name)
  tokenMapping?: {
    colors?: Record<string, string>;
    typography?: Record<string, string>;
    spacing?: Record<string, string>;
  };
}

// Example
const config: DesignSystemConfig = {
  projectName: 'my-app',
  output: {
    format: 'css',
    path: './src/design-system/tokens',
    prefix: '',
  },
};

export default config;
```

## Workflow for New Projects

### Starting a New Project with Figma MCP

```markdown
1. **Setup Figma**
   - Open style guide in Figma Desktop
   - Enable Dev Mode (Shift+D)
   - Enable MCP server in inspect panel

2. **Extract Tokens**
   - Select Colors frame â†’ "Extract color tokens as CSS variables"
   - Select Typography frame â†’ "Extract text styles"
   - Select Spacing frame â†’ "Extract spacing scale"

3. **Generate Token Files**
   Ask Claude: "Generate a tokens.css file from the extracted values"

4. **Create Components**
   - Select Button component â†’ "Create React Button atom using my tokens"
   - Continue for each component type
```

### Token Naming Convention

Transform Figma names to code-friendly names:

```typescript
// "Colors/Blue/500" â†’ "--color-blue-500"
// "Typography/Heading/H1" â†’ "--font-h1"
// "Spacing/Large" â†’ "--spacing-lg"

function normalizeTokenName(figmaName: string): string {
  return figmaName
    .toLowerCase()
    .replace(/\//g, '-')
    .replace(/\s+/g, '-');
}
```

## Tips for Efficient Extraction

### Batch Selection
Select multiple related frames at once:
```
"Extract all tokens from my current selection and organize by type"
```

### Component Variants
When selecting a component with variants:
```
"Extract this button component with all its variants (primary, secondary, sizes)"
```

### Full Style Guide
For comprehensive extraction:
```
"Walk through this entire style guide page and extract all design tokens,
then generate a complete tokens.css file"
```

## Summary

| Action | Approach |
|--------|----------|
| Extract colors | Select Colors frame â†’ Ask Claude |
| Extract typography | Select Typography frame â†’ Ask Claude |
| Extract component | Select component â†’ Ask Claude |
| Generate tokens file | Request specific format (CSS/Tailwind/SCSS) |
| Create components | Select design â†’ "Create React/Vue component" |