# Figma MCP Integration Guide

Integration with Figma's official Dev Mode MCP Server for extracting design tokens and component specs.

## ⚠️ CRITICAL: This Is Not Optional

```
┌─────────────────────────────────────────────────────────────────────┐
│  🚨 EXTRACTION FROM FIGMA IS MANDATORY BEFORE ANY CODING            │
│                                                                      │
│  This guide shows HOW to extract from Figma.                        │
│  The extraction itself is NOT optional - it's REQUIRED.             │
│                                                                      │
│  ❌ "אני אשתמש בערכים שנראים לי נכונים" = FORBIDDEN                  │
│  ✅ "אני חייב לחלץ את הערכים מ-Figma קודם" = CORRECT                 │
└─────────────────────────────────────────────────────────────────────┘
```

**Related documents:**
- `figma-design-fidelity.md` - Complete extraction workflow
- `design-deviation-rules.md` - Zero deviation policy

---

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

---

## Two Ways to Work

### Method 1: Selection-Based (Recommended for Design Systems)

1. Select a frame/component in Figma
2. Ask Claude Code:
```
"Extract design tokens from my current Figma selection"
"Get the button component specs from the selected frame"
```

### Method 2: Link-Based

1. Copy Figma link (Right-click → Copy link)
2. Paste in Claude Code:
```
"Extract the color tokens from this style guide: [figma-link]"
"Convert this component to React: [figma-link]"
```

---

## Extracting Design Tokens Workflow

### Step 1: Navigate in Figma to Style Guide

Open your style guide file and go to the tokens/foundations page.

### Step 2: Select Token Groups

Select the relevant frames:
- Colors section → Extract color tokens
- Typography section → Extract text styles
- Spacing section → Extract spacing scale

### Step 3: Request Extraction

```
"From my current Figma selection, extract all color tokens
and generate CSS custom properties"
```

### Step 4: Typical Token Structure in Figma

```
Figma Style Guide Structure:
├── 🎨 Colors
│   ├── Primitives (raw color values)
│   └── Semantic (purpose-driven aliases)
├── 📝 Typography
│   ├── Font families
│   ├── Type scale
│   └── Text styles
├── 📐 Spacing
│   ├── Base unit
│   └── Scale
├── 📲 Effects
│   ├── Shadows
│   └── Blurs
├── 🔲 Borders
│   ├── Radii
│   └── Widths
└── 📱 Breakpoints
    └── Device widths
```

---

## Token Transformation Patterns

### ⚠️ IMPORTANT: Extract EXACT Values

```
When extracting from Figma:

✅ CORRECT: Copy the exact value
   Figma shows: #3B82F6 → Code: #3B82F6
   Figma shows: 13px → Code: 13px
   Figma shows: 450 weight → Code: font-weight: 450

❌ WRONG: Round or "improve" values
   Figma shows: #3B82F6 → Code: #3F85F7 (changed!)
   Figma shows: 13px → Code: 12px (rounded!)
   Figma shows: 450 weight → Code: font-weight: 500 (standardized!)
```

### From Figma Colors to Code

**Transform to token structure (EXACT values only):**
```typescript
// From Figma: "Blue/500" -> #3b82f6
// To tokens (use EXACT Figma value):
const colors = {
  primitives: {
    blue: {
      50: '#eff6ff',   // EXACT from Figma
      100: '#dbeafe',  // EXACT from Figma
      200: '#bfdbfe',  // EXACT from Figma
      300: '#93c5fd',  // EXACT from Figma
      400: '#60a5fa',  // EXACT from Figma
      500: '#3b82f6',  // EXACT from Figma - Primary
      600: '#2563eb',  // EXACT from Figma
      700: '#1d4ed8',  // EXACT from Figma
      800: '#1e40af',  // EXACT from Figma
      900: '#1e3a8a',  // EXACT from Figma
    },
    // ... other color palettes
  },
  semantic: {
    // Map to purposes (aliases to primitives)
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

### Extract Typography Tokens

**MCP Command:**
```
figma.get_styles(file_key, style_type="TEXT")
```

**Transform to token structure (EXACT values only):**
```typescript
/**
 * Typography Tokens
 * Source: Figma Style Guide
 * Extracted: [DATE]
 *
 * ⚠️ ALL values are EXACT from Figma - DO NOT MODIFY
 */
const typography = {
  fonts: {
    heading: '"Inter", -apple-system, BlinkMacSystemFont, sans-serif',  // EXACT from Figma
    body: '"Inter", -apple-system, BlinkMacSystemFont, sans-serif',     // EXACT from Figma
    mono: '"JetBrains Mono", "Fira Code", monospace',                   // EXACT from Figma
  },

  fontSizes: {
    xs: '0.75rem',    // 12px - EXACT from Figma
    sm: '0.875rem',   // 14px - EXACT from Figma
    base: '1rem',     // 16px - EXACT from Figma
    lg: '1.125rem',   // 18px - EXACT from Figma
    xl: '1.25rem',    // 20px - EXACT from Figma
    '2xl': '1.5rem',  // 24px - EXACT from Figma
    '3xl': '1.875rem',// 30px - EXACT from Figma
    '4xl': '2.25rem', // 36px - EXACT from Figma
    '5xl': '3rem',    // 48px - EXACT from Figma
  },

  fontWeights: {
    normal: 400,   // EXACT from Figma
    medium: 500,   // EXACT from Figma
    semibold: 600, // EXACT from Figma
    bold: 700,     // EXACT from Figma
  },

  lineHeights: {
    none: 1,       // EXACT from Figma
    tight: 1.25,   // EXACT from Figma
    snug: 1.375,   // EXACT from Figma
    normal: 1.5,   // EXACT from Figma
    relaxed: 1.625,// EXACT from Figma
    loose: 2,      // EXACT from Figma
  },

  letterSpacing: {
    tighter: '-0.05em', // EXACT from Figma
    tight: '-0.025em',  // EXACT from Figma
    normal: '0',        // EXACT from Figma
    wide: '0.025em',    // EXACT from Figma
    wider: '0.05em',    // EXACT from Figma
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
    // ... other text styles - ALL from Figma
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

### Extract Spacing Tokens

**From Figma auto-layout values (EXACT):**
```typescript
/**
 * Spacing Tokens
 * Source: Figma Style Guide
 * Extracted: [DATE]
 *
 * ⚠️ ALL values are EXACT from Figma - DO NOT MODIFY
 */
const spacing = {
  // Base unit: 4px (from Figma)
  0: '0',
  px: '1px',
  0.5: '0.125rem',  // 2px - EXACT from Figma
  1: '0.25rem',     // 4px - EXACT from Figma
  1.5: '0.375rem',  // 6px - EXACT from Figma
  2: '0.5rem',      // 8px - EXACT from Figma
  2.5: '0.625rem',  // 10px - EXACT from Figma
  3: '0.75rem',     // 12px - EXACT from Figma
  4: '1rem',        // 16px - EXACT from Figma
  5: '1.25rem',     // 20px - EXACT from Figma
  6: '1.5rem',      // 24px - EXACT from Figma
  8: '2rem',        // 32px - EXACT from Figma
  10: '2.5rem',     // 40px - EXACT from Figma
  12: '3rem',       // 48px - EXACT from Figma
  16: '4rem',       // 64px - EXACT from Figma
  20: '5rem',       // 80px - EXACT from Figma
  24: '6rem',       // 96px - EXACT from Figma
};

// Semantic spacing (aliases)
const semanticSpacing = {
  component: {
    paddingXs: 'var(--spacing-2)',      // 8px - from Figma compact elements
    paddingSm: 'var(--spacing-3)',      // 12px - from Figma small buttons
    paddingMd: 'var(--spacing-4)',      // 16px - from Figma default buttons
    paddingLg: 'var(--spacing-5)',      // 20px - from Figma large buttons
  },
  layout: {
    gapSm: 'var(--spacing-2)',          // 8px - from Figma
    gapMd: 'var(--spacing-4)',          // 16px - from Figma
    gapLg: 'var(--spacing-6)',          // 24px - from Figma
    gapXl: 'var(--spacing-8)',          // 32px - from Figma
    sectionGap: 'var(--spacing-16)',    // 64px - from Figma
  },
  container: {
    paddingMobile: 'var(--spacing-4)',  // 16px - from Figma Mobile frame
    paddingTablet: 'var(--spacing-6)',  // 24px - from Figma Tablet frame
    paddingDesktop: 'var(--spacing-8)', // 32px - from Figma Desktop frame
  },
};
```

### Extract Effects & Borders

```typescript
/**
 * Effects Tokens
 * Source: Figma Style Guide
 * Extracted: [DATE]
 *
 * ⚠️ ALL values are EXACT from Figma - DO NOT MODIFY
 */
const effects = {
  shadows: {
    none: 'none',
    sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',                                      // EXACT from Figma
    base: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',    // EXACT from Figma
    md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',   // EXACT from Figma
    lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)', // EXACT from Figma
    xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',// EXACT from Figma
    inner: 'inset 0 2px 4px 0 rgb(0 0 0 / 0.05)',                              // EXACT from Figma
  },

  borderRadius: {
    none: '0',
    sm: '0.125rem',   // 2px - EXACT from Figma
    base: '0.25rem',  // 4px - EXACT from Figma
    md: '0.375rem',   // 6px - EXACT from Figma
    lg: '0.5rem',     // 8px - EXACT from Figma
    xl: '0.75rem',    // 12px - EXACT from Figma
    '2xl': '1rem',    // 16px - EXACT from Figma
    full: '9999px',
  },

  borderWidth: {
    0: '0',
    1: '1px',  // EXACT from Figma
    2: '2px',  // EXACT from Figma
    4: '4px',  // EXACT from Figma
  },

  transitions: {
    fast: '150ms ease',   // EXACT from Figma
    base: '200ms ease',   // EXACT from Figma
    slow: '300ms ease',   // EXACT from Figma
    slower: '500ms ease', // EXACT from Figma
  },
};
```

### Extract Breakpoints

```typescript
/**
 * Breakpoints
 * Source: Figma Style Guide / Frame sizes
 * Extracted: [DATE]
 *
 * ⚠️ Check Figma for which breakpoints have dedicated frames
 */
const breakpoints = {
  xs: '320px',   // Small mobile (iPhone SE) - check Figma
  sm: '480px',   // Mobile landscape - check Figma
  md: '768px',   // Tablet portrait (iPad) - check Figma
  lg: '1024px',  // Tablet landscape / Small laptop - check Figma
  xl: '1280px',  // Desktop - check Figma
  '2xl': '1440px', // Large desktop - check Figma
  '3xl': '1920px', // Full HD / Wide screens - check Figma
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

---

## Component Spec Extraction

### Reading Component Details from Figma

**MCP Command:**
```
figma.get_node(file_key, node_id)
```

**Extract from component (ALL values EXACT):**
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
├── State=Default, Size=Small, Type=Primary
├── State=Hover, Size=Small, Type=Primary
├── State=Default, Size=Medium, Type=Primary
├── State=Default, Size=Small, Type=Secondary
└── ...

↓ Maps to ↓

ButtonProps:
- variant: 'primary' | 'secondary' | 'ghost'
- size: 'sm' | 'md' | 'lg'
- state handled by CSS :hover, :active, :disabled
```

### Documentation Template for Extracted Component

```typescript
/**
 * Button Component
 *
 * @figma https://figma.com/file/xxx/Design-System?node-id=123
 * @extracted 2024-01-15
 * @designer [Designer Name]
 *
 * Extracted Specs (DO NOT MODIFY without Figma update):
 * ├── Dimensions
 * │   ├── height: 48px (md size)
 * │   └── min-width: auto (hug contents)
 * │
 * ├── Padding
 * │   ├── vertical: 12px
 * │   └── horizontal: 24px
 * │
 * ├── Visual
 * │   ├── background: #3B82F6 (--color-primary)
 * │   ├── border-radius: 8px (--radius-lg)
 * │   └── shadow: none
 * │
 * ├── Typography
 * │   ├── font: Inter
 * │   ├── size: 16px
 * │   ├── weight: 500
 * │   └── color: #FFFFFF
 * │
 * └── States
 *     ├── hover: bg #2563EB
 *     ├── active: bg #1D4ED8
 *     └── disabled: bg #E5E7EB, color #9CA3AF
 */
```

---

## Output Formats

### CSS Custom Properties

```css
/**
 * Design Tokens - CSS Variables
 * Source: Figma Style Guide
 * Extracted: [DATE]
 *
 * ⚠️ ALL values EXACT from Figma - DO NOT MODIFY manually
 * To update: Extract new values from Figma first
 */

:root {
  /* Colors - Primitives (EXACT from Figma) */
  --color-blue-500: #3b82f6;
  --color-blue-600: #2563eb;

  /* Colors - Semantic (aliases) */
  --color-primary: var(--color-blue-500);
  --color-primary-hover: var(--color-blue-600);

  /* Typography (EXACT from Figma) */
  --font-heading: 'Inter', sans-serif;
  --font-size-base: 1rem;

  /* Spacing (EXACT from Figma) */
  --spacing-4: 1rem;

  /* Effects (EXACT from Figma) */
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --radius-lg: 0.5rem;
}
```

### TypeScript Theme Object

```typescript
/**
 * Theme Configuration
 * Source: Figma Style Guide
 * Extracted: [DATE]
 *
 * ⚠️ ALL values EXACT from Figma
 */

export const theme = {
  colors: { /* ... */ },
  typography: { /* ... */ },
  spacing: { /* ... */ },
  effects: { /* ... */ },
  breakpoints: { /* ... */ },
} as const;

export type Theme = typeof theme;
```

---

## Workflow for New Projects

### Starting a New Project with Figma MCP

```markdown
1. **Setup Figma**
   - Open style guide in Figma Desktop
   - Enable Dev Mode (Shift+D)
   - Enable MCP server in inspect panel

2. **Extract Tokens (MANDATORY)**
   - Select Colors frame → "Extract color tokens as CSS variables"
   - Select Typography frame → "Extract text styles"
   - Select Spacing frame → "Extract spacing scale"
   - ⚠️ Use EXACT values - no rounding or "improving"

3. **Generate Token Files**
   Ask Claude: "Generate a tokens.css file from the extracted values"

4. **Create Components**
   - Select Button component → "Create React Button atom using my tokens"
   - ⚠️ All values must come from Figma extraction
   - Continue for each component type
```

### Token Naming Convention

Transform Figma names to code-friendly names:

```typescript
// "Colors/Blue/500" → "--color-blue-500"
// "Typography/Heading/H1" → "--font-h1"
// "Spacing/Large" → "--spacing-lg"

function normalizeTokenName(figmaName: string): string {
  return figmaName
    .toLowerCase()
    .replace(/\//g, '-')
    .replace(/\s+/g, '-');
}
```

---

## Handling Figma Updates

### When Style Guide Changes in Figma

```
1. Detect change (via Figma MCP or manual check)
2. Extract NEW values from Figma (EXACT)
3. Compare with existing tokens
4. Update tokens/*.json with new EXACT values
5. Regenerate CSS variables
6. Run visual regression tests
7. Commit: "sync: Update tokens from Figma [date]"
```

### When Component Changes in Figma

```
1. Extract NEW component specs via MCP
2. Compare with current implementation
3. Update component CSS with EXACT new values
4. Update component props if variants changed
5. Verify visual match with Figma
6. Commit: "sync: Update [Component] from Figma [date]"
```

---

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

---

## Summary

| Action | Approach |
|--------|----------|
| Extract colors | Select Colors frame → Ask Claude → Use EXACT values |
| Extract typography | Select Typography frame → Ask Claude → Use EXACT values |
| Extract component | Select component → Ask Claude → Use EXACT values |
| Generate tokens file | Request specific format (CSS/Tailwind/SCSS) |
| Create components | Select design → "Create React/Vue component" → EXACT specs |

### ⚠️ Remember

```
┌─────────────────────────────────────────────────────────────────┐
│  EVERY value in your code must come from Figma extraction.      │
│  NO guessing. NO rounding. NO "improving".                      │
│  If Figma shows 13px → Code is 13px (not 12px).                │
│  If Figma shows #3B82F6 → Code is #3B82F6 (not #3F85F7).       │
└─────────────────────────────────────────────────────────────────┘
```
