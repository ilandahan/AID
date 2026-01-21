# Figma MCP Integration

Connect Claude Code to Figma for design token extraction and component specs.

## Prerequisites

- Figma Desktop app (latest version)
- Dev Mode enabled in Figma file
- No additional installation required

## Setup

The Figma MCP runs locally from Figma Desktop (no `.mcp.json` configuration needed):

1. Open Figma Desktop app
2. Open a Figma Design file
3. Toggle to **Dev Mode** (Shift+D)
4. In the inspect panel, click **Enable desktop MCP server**
5. Server runs at `http://127.0.0.1:3845/mcp`

> **Note:** Unlike other MCP servers, Figma MCP runs directly from the Figma Desktop app.
> You don't need to add it to `.mcp.json` - it's automatically available when enabled in Figma.

## Connection

| Endpoint | URL |
|----------|-----|
| Local | `http://127.0.0.1:3845/mcp` |
| Remote | `https://mcp.figma.com/mcp` |

## Two Ways to Work

### Method 1: Selection-Based (Recommended)

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

## Available Operations

| Operation | Description |
|-----------|-------------|
| Get styles | Extract color, text, effect styles |
| Get node | Get specific node details |
| Get components | List component definitions |
| Get variables | Extract design variables |

## Token Extraction Workflow

### Step 1: Extract Colors

Select Colors frame in Figma:
```
"Extract all color tokens as CSS custom properties"
```

Output:
```css
:root {
  --color-primary: #3b82f6;
  --color-primary-hover: #2563eb;
  --color-text-primary: #111827;
  --color-text-secondary: #6b7280;
  --color-surface: #ffffff;
  --color-border: #e5e7eb;
}
```

### Step 2: Extract Typography

Select Typography frame:
```
"Extract text styles and generate TypeScript types"
```

Output:
```typescript
const typography = {
  h1: { fontSize: '2.25rem', fontWeight: 700, lineHeight: 1.25 },
  h2: { fontSize: '1.875rem', fontWeight: 700, lineHeight: 1.3 },
  body: { fontSize: '1rem', fontWeight: 400, lineHeight: 1.5 },
  caption: { fontSize: '0.75rem', fontWeight: 400, lineHeight: 1.5 },
};
```

### Step 3: Extract Spacing

Select Spacing frame:
```
"Extract spacing scale values"
```

Output:
```typescript
const spacing = {
  0: '0',
  1: '0.25rem',  // 4px
  2: '0.5rem',   // 8px
  3: '0.75rem',  // 12px
  4: '1rem',     // 16px
  5: '1.25rem',  // 20px
  6: '1.5rem',   // 24px
  8: '2rem',     // 32px
};
```

## Component Extraction

### Get Component Specs

Select a component in Figma:
```
"Get the button component specs including all variants"
```

### Generate React Component

```
"Create a React component from this Figma button design"
```

## Typical Style Guide Structure

```
Figma Style Guide:
├── 🎨 Colors
│   ├── Primitives (raw color values)
│   └── Semantic (purpose-driven aliases)
├── 📝 Typography
│   ├── Font families
│   ├── Type scale
│   └── Text styles
├── 📏 Spacing
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

## Token Naming Transformation

Transform Figma names to code-friendly names:

```
"Colors/Blue/500" → "--color-blue-500"
"Typography/Heading/H1" → "--font-h1"
"Spacing/Large" → "--spacing-lg"
```

## Output Formats

### CSS Custom Properties
```css
:root {
  --color-primary: #3b82f6;
  --font-size-base: 1rem;
  --spacing-4: 1rem;
}
```

### Tailwind Config
```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: { DEFAULT: '#3b82f6', hover: '#2563eb' }
      }
    }
  }
};
```

### TypeScript Theme Object
```typescript
export const theme = {
  colors: { /* ... */ },
  typography: { /* ... */ },
  spacing: { /* ... */ },
} as const;
```

## Troubleshooting

### MCP Server Not Available
- Ensure Figma Desktop is open
- Toggle Dev Mode on (Shift+D)
- Click "Enable desktop MCP server" in inspect panel

### Selection Not Detected
- Make sure a frame/component is selected
- Try reselecting the element
- Check Dev Mode is active

### Styles Not Extracting
- Ensure styles are properly defined in Figma
- Check styles aren't nested too deeply
- Try selecting parent frame instead
