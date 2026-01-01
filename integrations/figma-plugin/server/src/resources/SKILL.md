# Figma Component Metadata Skill

## Purpose

This skill provides the standard format for documenting Figma components with comprehensive metadata. Use this when creating or reviewing component descriptions in Figma to ensure consistent, thorough documentation across a design system.

## When to Use

- Creating new components in Figma
- Documenting existing components
- Reviewing component documentation completeness
- Generating component descriptions for design systems
- Preparing components for code generation

## Metadata Format

### Structure

```yaml
[Primary description - 2-3 sentences]

---
tags: [search keywords]
notes: [usage guidelines]
ariaLabel: [accessibility label]
category: [button|navigation|form|layout|feedback|data-display|overlay]
level: [atom|molecule|organism|template|page]
priority: [critical|high|medium|low]

analytics: [event name]
testId: [test attribute]

tokens:
  colors: [hex values]
  spacing: [padding, margin, gap]
  radius: [border-radius]
  typography: [font specs]
  shadows: [shadow values]

states:
  default: [description]
  hover: [description]
  focus: [description]
  disabled: [description]

variants:
  [Name]: [description]

dos:
  - [recommended practice]

donts:
  - [anti-pattern to avoid]

a11y:
  - [accessibility requirement]

related:
  - [Related/Component]

specs:
  minWidth: [value]
  minHeight: [value]
  touchTarget: [44x44px minimum]
  contrast: [ratio requirements]
```

### Required Fields (Minimum)

```yaml
[Primary description]

---
tags: [keywords]
notes: [usage]
category: [type]
level: [atomic level]
```

### Recommended Fields (Standard)

Add to minimum:
- `ariaLabel`
- `priority`
- `tokens` (colors, spacing, typography)
- `states`
- `variants`
- `dos/donts`

### Complete Fields (Comprehensive)

Add to recommended:
- `analytics`
- `testId`
- `a11y`
- `related`
- `specs`

## Examples

### Button Component

```yaml
Primary CTA button for lead capture on homepage hero section.
Triggers contact form modal and sends inquiry to sales team.

---
tags: button, cta, lead, homepage, hero, conversion, primary, action
notes: Primary for main actions. Secondary for supporting. Full width for mobile. Max 1 primary CTA per viewport.
ariaLabel: Send message to start a conversation
category: button
level: atom
priority: critical

analytics: lead_button_click
testId: btn-lead-send

tokens:
  colors: Azure Radiance (#0C8CE9), Denim (#0A6FBA), Pale Sky (#6C757D), White (#FFFFFF)
  spacing: padding: 16px 32px
  radius: 6px
  typography: Quicksand SemiBold 16/24
  shadows: 0px 4px 6px -1px rgba(0,0,0,0.1) (hover)

states:
  default: Solid background, normal state
  hover: Darker background with shadow
  focus: Focus ring for keyboard nav
  disabled: Grey background, non-interactive

variants:
  Primary: Solid blue background, white text. Main actions.
  Secondary: Outline style, blue border/text. Supporting actions.
  Full: 100% width for mobile/hero.
  Medium: Auto width for desktop.
  Compact: Minimal padding, text-link style.

dos:
  - Use Primary for single main action per viewport
  - Keep label text short (2-3 words)
  - Use Full size on mobile

donts:
  - Don't use multiple Primary buttons in same section
  - Don't use Compact for important actions
  - Don't use disabled without explanation

a11y:
  - 4.5:1 contrast ratio for text
  - 44x44px minimum touch target
  - Visible focus ring required
  - Support Enter and Space keys

related:
  - Button/Icon
  - Link/Text
  - Form/Submit

specs:
  minWidth: 120px (Medium), 100% (Full)
  minHeight: 52px
  touchTarget: 44x44px
  contrast: 4.5:1
```

## Best Practices

1. **Be Specific**: Include actual values (hex colors, px sizes)
2. **Be Consistent**: Use same format across all components
3. **Be Complete**: Fill all relevant fields
4. **Be Practical**: Focus on actionable guidance in dos/donts
5. **Be Accessible**: Always include a11y requirements
6. **Be Searchable**: Use relevant tags for discovery

## Parsing

The format uses YAML-like syntax:
- `---` separates description from metadata
- `key: value` for simple fields
- `-` prefix for list items
- Indentation for nesting
