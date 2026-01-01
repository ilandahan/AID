# Component Metadata Format for Figma

## Overview

This document defines the standard metadata format for Figma components. Use this format in the **Description** field of Component Sets to ensure consistent documentation across your design system.

---

## Full Metadata Template

```yaml
[Primary description - 2-3 sentences explaining what the component is and its main purpose]

---
# Core Identification
tags: [comma-separated keywords for search and categorization]
notes: [brief usage guidelines and important considerations]
ariaLabel: [accessibility label for screen readers]
category: [component category: button, navigation, form, layout, feedback, data-display, overlay]
level: [atomic design level: atom, molecule, organism, template, page]
priority: [importance level: critical, high, medium, low]

# Development
analytics: [analytics event name for tracking]
testId: [data-testid attribute value for testing]
storybook: [storybook path when available]

# Design Tokens
tokens:
  colors: [list of colors used with hex values]
  spacing: [padding, margin, gap values]
  radius: [border-radius values]
  typography: [font family, size, weight, line-height]
  shadows: [box-shadow values if applicable]
  borders: [border width, style, color if applicable]

# States
states:
  default: [description of default/rest state]
  hover: [description of hover state]
  active: [description of active/pressed state]
  focus: [description of focus state for keyboard navigation]
  disabled: [description of disabled state]
  loading: [description of loading state if applicable]
  error: [description of error state if applicable]
  success: [description of success state if applicable]

# Variants
variants:
  [VariantName1]: [description of when and how to use this variant]
  [VariantName2]: [description of when and how to use this variant]

# Usage Guidelines
dos:
  - [recommended usage pattern 1]
  - [recommended usage pattern 2]
  - [recommended usage pattern 3]

donts:
  - [anti-pattern or misuse to avoid 1]
  - [anti-pattern or misuse to avoid 2]
  - [anti-pattern or misuse to avoid 3]

# Accessibility
a11y:
  - [accessibility requirement 1]
  - [accessibility requirement 2]
  - [WCAG compliance notes]
  - [keyboard interaction requirements]
  - [screen reader considerations]

# Related Components
related:
  - [Related/Component/Name1]
  - [Related/Component/Name2]

# Technical Specifications
specs:
  minWidth: [minimum width value or 'auto']
  maxWidth: [maximum width value or 'none']
  minHeight: [minimum height value]
  touchTarget: [minimum touch target size, typically 44x44px for WCAG]
  contrast: [contrast ratio requirements]
  breakpoints: [responsive behavior notes if applicable]
```

---

## Example: Button Component

```yaml
Primary CTA button for lead capture on homepage hero section.
Triggers contact form modal and sends inquiry to sales team.
Used as the main conversion element above the fold.

---
# Core Identification
tags: button, cta, lead, homepage, hero, conversion, primary, action, submit
notes: Primary style for main actions. Secondary for supporting actions. Full width for mobile/hero. Medium for sidebars. Compact for inline/text links. Max 1 primary CTA per viewport.
ariaLabel: Send message to start a conversation with our team
category: button
level: atom
priority: critical

# Development
analytics: lead_button_click
testId: btn-lead-send
storybook: atoms-button--primary

# Design Tokens
tokens:
  colors: Azure Radiance (#0C8CE9), Denim (#0A6FBA), Pale Sky (#6C757D), White (#FFFFFF)
  spacing: padding-x: 32px, padding-y: 16px, compact-padding: 36px 18px
  radius: 6px
  typography: Quicksand SemiBold 16/24
  shadows: 0px 4px 6px -1px rgba(0,0,0,0.1) (hover only)

# States
states:
  default: Normal resting state, solid background color
  hover: Darker background with subtle shadow for interactive feedback
  focus: Focus ring for keyboard navigation (required for a11y)
  disabled: Grey background (#6C757D), non-interactive, cursor not-allowed

# Variants
variants:
  Primary: Solid filled button for main actions. Blue background, white text.
  Secondary: Outline button for supporting actions. White/transparent background, blue border and text.
  Size-Full: 100% width, for mobile viewports and hero sections.
  Size-Medium: Auto width based on content, for desktop forms and sidebars.
  Size-Compact: Minimal padding, text-link style for inline actions.

# Usage Guidelines
dos:
  - Use Primary for single main action per viewport
  - Use Secondary alongside Primary for alternative actions
  - Keep label text short (2-3 words max)
  - Use Full size on mobile breakpoints
  - Always provide meaningful label text

donts:
  - Don't use multiple Primary buttons in same section
  - Don't use Compact for important actions
  - Don't change button colors outside design system
  - Don't use disabled state without explaining why
  - Don't use icon-only buttons without ariaLabel

# Accessibility
a11y:
  - Ensure 4.5:1 contrast ratio for text
  - Focus ring must be visible (3:1 contrast minimum)
  - Minimum touch target 44x44px (WCAG 2.1 AAA)
  - Use aria-disabled instead of disabled attribute when possible
  - Provide aria-label for icon-only buttons
  - Support keyboard activation (Enter and Space)

# Related Components
related:
  - Button/Icon (for icon-only buttons)
  - Link/Text (for inline text links)
  - Form/Submit (for form submissions)
  - Button/Group (for button arrangements)

# Technical Specifications
specs:
  minWidth: 120px (Medium), 100% (Full), auto (Compact)
  minHeight: 52px (Full/Medium), 60px (Compact)
  touchTarget: 44x44px minimum (WCAG 2.1)
  contrast: 4.5:1 (text), 3:1 (UI components)
```

---

## Example: Navigation Link Item

```yaml
Navigation link item for header and footer menus.
Interactive text link with optional dropdown indicator for expandable sections.
Supports multiple contexts: main header navigation, footer links, and external/special links.

---
# Core Identification
tags: navigation, nav, link, menu, header, footer, item, anchor, dropdown, submenu, text-link
notes: Header variant for main nav with optional chevron dropdown. Footer for standard footer links. FooterSpecial for external links (GitHub, social, docs). Always use text prop for dynamic content. showIcon only affects Header variant.
ariaLabel: Navigation menu link
category: navigation
level: atom
priority: high

# Development
analytics: nav_link_click
testId: nav-link-item
storybook: atoms-navigation--link-item

# Design Tokens
tokens:
  colors: Azure Radiance (#0C8CE9), Black (#000000), Outer Space (#343B42), Athens Gray (#F8F9FA)
  spacing: padding-x: 16px, padding-y: 8px, icon-gap: 4px
  radius: 6px
  typography: Quicksand Medium 14/24.5 (Header), Quicksand Medium 16/24 (Footer)

# States
states:
  default: Normal state, no background, standard text color
  hover: Light gray background (#F8F9FA), text underline, blue text for Header variant

# Variants
variants:
  Header: Main navigation item with optional dropdown chevron. Font 14px. Shows icon when hasSubmenu.
  Footer: Standard footer link. Font 16px. Dark gray text (#343B42).
  FooterSpecial: External link style. Font 16px. Black text, blue on hover. No padding/background.

# Usage Guidelines
dos:
  - Use Header for main navigation items
  - Use Footer for sitemap-style footer links
  - Use FooterSpecial for external resources (GitHub, Twitter, Docs)
  - Keep text short (1-3 words)
  - Use showIcon=true only for items with dropdown menus
  - Ensure consistent text property across all instances

donts:
  - Don't use Header variant in footer
  - Don't use showIcon on Footer variants
  - Don't hardcode text - always use text prop
  - Don't mix font sizes within same navigation area
  - Don't use FooterSpecial for internal navigation

# Accessibility
a11y:
  - Minimum touch target 44x44px
  - Use aria-expanded="true/false" for dropdown items
  - Use aria-current="page" for active page link
  - Ensure 4.5:1 contrast ratio for text
  - Focus ring required for keyboard navigation
  - Screen reader should announce as "link" or "button" based on behavior

# Related Components
related:
  - Navigation/Dropdown (for submenu container)
  - Navigation/Bar (parent component)
  - Button/Text (similar text-link style)
  - Icons/Chevron (dropdown indicator)

# Technical Specifications
specs:
  minWidth: auto (content-based)
  minHeight: 40px (Header/Footer), 24px (FooterSpecial)
  touchTarget: 44x44px minimum (WCAG 2.1)
  contrast: 4.5:1 text, 3:1 UI elements
  iconSize: 16x16px
```

---

## Variant-Level Descriptions

For individual variants within a Component Set, use shorter descriptions:

### Format:
```
[Brief description of this specific variant's purpose and appearance. When to use it.]
```

### Examples:

**Button - Size=Full, State=Default, Style=Primary:**
```
Full-width primary button for mobile viewports and hero sections. Main CTA state. Solid blue background with white text.
```

**Button - Size=Full, State=Hover, Style=Primary:**
```
Hover state with darker background (#0A6FBA) and shadow for interactive feedback. Indicates clickable element on mouse over.
```

**Button - Size=Full, State=Disabled, Style=Primary:**
```
Disabled state with grey background (#6C757D). Use when action is unavailable. Requires aria-disabled attribute.
```

---

## Property-Level Descriptions

When Figma supports Property descriptions, use this format:

| Property | Description |
|----------|-------------|
| **Style** | Visual style variant. Primary for main CTAs, Secondary for supporting actions. |
| **Size** | Button dimensions. Full (100% width), Medium (auto width), Compact (minimal padding). |
| **State** | Interactive state. Default (rest), Hover (mouse over), Focus (keyboard), Disabled (inactive). |
| **Label** | Button text content. Keep short and action-oriented (e.g., "Send Message", "Learn More"). |

---

## Quick Reference: Required vs Optional Fields

### Required (Minimum)
```yaml
[Primary description]

---
tags: [keywords]
notes: [usage guidelines]
category: [component type]
level: [atomic level]
```

### Recommended (Standard)
```yaml
+ ariaLabel
+ priority
+ tokens (colors, spacing, typography)
+ states
+ variants
+ dos/donts
```

### Complete (Comprehensive)
```yaml
+ analytics
+ testId
+ storybook
+ a11y
+ related
+ specs
```

---

## Parsing Notes

The metadata format uses YAML-like syntax for easy parsing:

1. **Separator**: `---` separates description from metadata
2. **Sections**: `# Comment` lines are section headers (ignored in parsing)
3. **Key-Value**: `key: value` format for simple fields
4. **Lists**: Lines starting with `-` are list items
5. **Nested**: Indentation indicates nesting (e.g., under `tokens:`)

### Parser Implementation

See `/src/utils/descriptionParser.ts` for the TypeScript implementation that parses this format from Figma component descriptions.
