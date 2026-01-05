# Figma Design Fidelity - Zero Deviation

## Core Rule

Figma is the single source of truth. All design values come from Figma. No guessing, rounding, or improving.

```
If Figma says 12px -> Code says 12px
If Figma says #3B82F6 -> Code says #3B82F6
If Figma says 400 weight -> Code says 400 weight
```

## Work Order

1. STOP - Don't write style code
2. EXTRACT - Get values from Figma
3. DOCUMENT - Record extracted values
4. IMPLEMENT - Use exact values
5. VERIFY - Compare result to Figma

## What to Extract

| Category | Details |
|----------|---------|
| Dimensions | width, height |
| Padding | all sides |
| Margin/Gap | spacing |
| Colors | fill, stroke, background |
| Typography | font, size, weight, line-height |
| Effects | shadow, blur, opacity |
| Borders | radius, width |
| Layout | direction, alignment |

## MCP Commands

```typescript
const nodeSpec = await figma.get_node(file_key, node_id);

// Extract:
fill: nodeSpec.fills[0].color
width: nodeSpec.absoluteBoundingBox.width
paddingTop: nodeSpec.paddingTop
itemSpacing: nodeSpec.itemSpacing  // gap
fontFamily: nodeSpec.style.fontFamily
fontSize: nodeSpec.style.fontSize
cornerRadius: nodeSpec.cornerRadius
```

## Button Extraction Example

```
Figma: "Button/Primary/Default"

Extracted:
- height: 48px
- padding: 12px 24px
- background: #3B82F6
- borderRadius: 8px
- font: Inter 16px/500
- color: #FFFFFF

States:
- hover: bg #2563EB
- active: bg #1D4ED8
- disabled: bg #E5E7EB, color #9CA3AF
```

## Verification Checklist

```
Component: [Name]
Figma Frame: [Link]
Date: [YYYY-MM-DD]

Dimensions: [ ] width, [ ] height
Spacing: [ ] padding (4 sides), [ ] gap
Colors: [ ] background, [ ] text, [ ] border, [ ] states
Typography: [ ] font, [ ] size, [ ] weight, [ ] line-height
Effects: [ ] radius, [ ] shadow
Responsive: [ ] mobile, [ ] tablet, [ ] desktop
```

## Common Mistakes

### Rounding Values
```css
/* Figma: 13px */
padding: 12px;  /* WRONG */
padding: 13px;  /* CORRECT */
```

### Improving Colors
```css
/* Figma: #3B82F6 */
background: #3F85F7;  /* WRONG */
background: #3B82F6;  /* CORRECT */
```

### Adding Effects
```css
/* Figma: no shadow */
box-shadow: 0 2px 4px rgba(0,0,0,0.1);  /* WRONG */
box-shadow: none;  /* CORRECT */
```

### Responsive Assumptions
```css
/* Figma mobile: padding 16px */
@media (max-width: 768px) {
  padding: 12px;  /* WRONG - assumed */
  padding: 16px;  /* CORRECT - from Figma */
}
```

## Token Sync

When Figma updates:
1. Detect change
2. Update tokens/colors.json
3. Regenerate CSS
4. Verify components
5. Commit: "sync: Update [property] from Figma [value]"

## Visual Testing

1. Screenshot from Figma
2. Screenshot from browser
3. Diff comparison
4. Difference should be 0%

## When Figma Is Unclear

DO NOT: Make assumptions or fix yourself
DO: Ask designer and wait for confirmation

```
"In frame [X], padding is 13px. Intentional or should be 12px for 4px grid?"
```

## Quick Check

Before writing any style:
- [ ] Did I extract from Figma?
- [ ] Is value exact (no rounding)?
- [ ] Checked all states?
- [ ] Checked responsive?

Before delivery:
- [ ] Visual comparison 0% difference
- [ ] All breakpoints match Figma
- [ ] Tokens up-to-date
- [ ] Figma link documented
