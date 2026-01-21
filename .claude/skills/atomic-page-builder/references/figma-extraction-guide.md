# Figma Extraction Guide for Page Building

## Before You Start

### Required Information
```markdown
1. Figma file URL
2. Page/frame node-id
3. Access to Figma MCP tool
4. Existing design system inventory
```

## Step-by-Step Extraction

### Step 1: Get Page Structure
```typescript
// Use Figma MCP to get page node
const pageData = await figma.getNode({
  fileKey: 'abc123',
  nodeId: '123:456'  // Page frame ID
});
```

### Step 2: Extract Layout Values
```markdown
## Layout Extraction Checklist

### Container
- [ ] Width: [px or %]
- [ ] Max-width: [px]
- [ ] Padding: [top right bottom left]
- [ ] Margin: [auto or specific]

### Grid
- [ ] Columns: [number]
- [ ] Gap: [px]
- [ ] Row gap: [if different]

### Sections
- [ ] Section padding: [px]
- [ ] Section gap: [px]
- [ ] Background: [token or value]
```

### Step 3: Map to Tokens

```markdown
| Figma Value | Token | Notes |
|-------------|-------|-------|
| 24px | var(--spacing-6) | Standard gap |
| 16px | var(--spacing-4) | Compact gap |
| 48px | var(--spacing-12) | Section padding |
| #F5F5F5 | var(--color-bg-secondary) | Section bg |
```

**If value doesn't match a token:**
1. STOP
2. Update tokens in atomic-design
3. Then continue

### Step 4: Identify Components Used

```markdown
## Component Inventory

### Organisms
- [ ] Header (node: 123:789)
- [ ] DataTable (node: 123:790)
- [ ] Modal (node: 123:791)

### Molecules
- [ ] Card (node: 123:792)
- [ ] SearchBar (node: 123:793)

### Atoms
- [ ] Button variants: primary, secondary
- [ ] Input: text, search
- [ ] Badge: success, warning

## Missing Components
- [ ] [Component name] - needs creation
```

### Step 5: Extract Responsive Behavior

```markdown
## Breakpoints from Figma

### Desktop (1440px)
- Grid: 12 columns
- Sidebar: 280px
- Gap: 24px

### Tablet (768px)
- Grid: 8 columns
- Sidebar: hidden (hamburger)
- Gap: 16px

### Mobile (375px)
- Grid: 4 columns
- Sidebar: overlay
- Gap: 12px
```

## Extraction Templates

### Page Spec Document
```markdown
# Page: [Page Name]

## Figma Reference
- File: [URL]
- Frame: [node-id]
- Last extracted: [date]

## Layout Specs
| Property | Desktop | Tablet | Mobile |
|----------|---------|--------|--------|
| Max-width | 1200px | 100% | 100% |
| Padding | 48px | 32px | 16px |
| Grid cols | 12 | 8 | 4 |
| Gap | 24px | 16px | 12px |

## Sections
1. **Header** - Sticky, 64px height
2. **Hero** - Full width, 400px height
3. **Content** - Grid layout, cards
4. **Footer** - Full width, 200px

## Components Used
- Header (organism)
- Card (molecule) x 6
- Button (atom) x 3

## Tokens Required
- spacing: 4, 6, 8, 12
- colors: bg-primary, bg-secondary
- typography: heading-xl, body-md
```

## Common Extraction Pitfalls

| Mistake | Correct Approach |
|---------|------------------|
| Rounding 23px to 24px | Use exact Figma value, update tokens |
| Assuming breakpoints | Extract from Figma frames |
| Ignoring auto-layout | Map to flexbox/grid exactly |
| Missing hover states | Check all component states |
| Skipping spacing | Extract ALL gaps and padding |

## Validation Checklist

Before implementation:
- [ ] All layout values extracted
- [ ] All values mapped to tokens
- [ ] All components identified
- [ ] All breakpoints documented
- [ ] Missing components flagged
- [ ] Figma link documented
- [ ] Extraction date recorded
