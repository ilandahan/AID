# Design Deviation Rules - Zero Tolerance

## Core Rule

Developer is not a designer. Role is to translate design to code - not improve it.

```
"I think it looks better this way" = FORBIDDEN
"Figma shows X, code will be X" = CORRECT
```

## Forbidden Deviations

### Aesthetic
| Forbidden | Example | Why |
|-----------|---------|-----|
| Change colors | #3B82F6 -> #3F85F7 | Designer chose specific color |
| Round values | 13px -> 12px | "Convenient" not relevant |
| Add effects | Add shadow not in design | Design decision |
| Change fonts | Inter -> System fonts | Breaks brand |
| Change spacing | 24px -> 20px | Breaks visual rhythm |

### Technical
| Forbidden | Correct |
|-----------|---------|
| Optimize values | Ask designer for unit preference |
| Standardize font-weight 450 to 500 | Check if font supports 450 |
| Fix inconsistencies | Report to designer, don't fix |

### Responsive
| Forbidden | Correct |
|-----------|---------|
| Invent breakpoints | Check Figma breakpoints |
| Logical adjustments | Extract from Figma Mobile frame |
| Change layout | Implement as shown in Figma |

## When Something Looks Wrong

1. STOP - Don't change anything
2. DOCUMENT - Screenshot the issue
3. ASK - Ask designer: "In [frame] the padding is 13px. Intentional or should be 12px?"
4. WAIT - Wait for response
5. IMPLEMENT - Follow designer guidance
6. DOCUMENT - Record decision

## Allowed Exceptions

### 1. Platform Bug
```css
/* Safari requires prefix */
backdrop-filter: blur(10px);
-webkit-backdrop-filter: blur(10px); /* Allowed - technical fix */
```

### 2. Accessibility Issue (Report First)
```css
/* Figma: 3.5:1 contrast, WCAG requires 4.5:1 */
/* REPORT TO DESIGNER - don't fix yourself */
/* Awaiting update: Jira DESIGN-123 */
```

### 3. Missing State
```css
/* Focus state not in Figma - request from designer */
/* TODO: Jira DESIGN-124 - using browser default */
```

## Documentation Requirements

### Component Header
```tsx
/**
 * @figma https://figma.com/file/xxx?node-id=123
 * @extracted 2024-01-15
 * @designer Sarah Cohen
 *
 * Specs: height 48px, padding 12px 24px, radius 8px
 * All values from Figma - DO NOT MODIFY without approval.
 */
```

### CSS Comments
```css
.button {
  padding: 12px 24px;  /* Figma: paddingTop/Bottom: 12, Left/Right: 24 */
  background: var(--color-primary);  /* Figma: fill #3B82F6 */
  border-radius: 8px;  /* Figma: cornerRadius: 8 */
}
```

## Code Review Checklist

```
Figma Link: [ ] Exists and correct
Values: [ ] All CSS has Figma source
Tokens: [ ] Uses tokens, matches Figma
Visual: [ ] Screenshot shows match
No unauthorized: [ ] No improved colors, rounded values, added effects
```

### Red Flags to Block PR
- Hardcoded color instead of token
- Rounded value different from Figma
- Missing Figma reference
- "Looks better this way" in commit

## The Rules

1. Don't change - implement exactly from Figma
2. Don't improve - improvements are deviations
3. Don't guess - if unclear, ask
4. Don't round - 13px is 13px, not 12px
5. Don't add - if not in Figma, not in code
6. Document - every value needs Figma source
7. Verify - visual check before delivery

## Quick Reference

| Situation | Action |
|-----------|--------|
| Value looks wrong | Ask designer |
| Think it looks better | Not relevant - use Figma |
| Designer made mistake | Report - don't fix |
| Missing state | Request from designer |
| Unsure which value | Ask designer |
| Want to change | Request Figma update first |
