# Responsive Design Patterns

Mobile-first responsive patterns for Atomic Design components.

## Breakpoint System

**Standard breakpoints (mobile-first):**

| Name | Size | Target Device |
|------|------|---------------|
| `xs` | 320px | Small mobile (iPhone SE) |
| `sm` | 480px | Mobile landscape |
| `md` | 768px | Tablet portrait (iPad) |
| `lg` | 1024px | Tablet landscape / Small laptop |
| `xl` | 1280px | Desktop |
| `2xl` | 1440px | Large desktop |
| `3xl` | 1920px | Full HD / Wide screens |

```css
/* CSS Custom Properties for breakpoints */
:root {
  --breakpoint-xs: 320px;
  --breakpoint-sm: 480px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 1024px;
  --breakpoint-xl: 1280px;
  --breakpoint-2xl: 1440px;
  --breakpoint-3xl: 1920px;
}
```

```typescript
// TypeScript breakpoints
const breakpoints = {
  xs: '320px',   // Small mobile (iPhone SE)
  sm: '480px',   // Mobile landscape
  md: '768px',   // Tablet portrait (iPad)
  lg: '1024px',  // Tablet landscape / Small laptop
  xl: '1280px',  // Desktop
  '2xl': '1440px', // Large desktop
  '3xl': '1920px', // Full HD / Wide screens
} as const;
```

## Core Principle: Mobile-First

**Always start with mobile styles, then enhance for larger screens.**

```css
/* CORRECT - Mobile first */
.button {
  width: 100%;
  padding: var(--spacing-3) var(--spacing-4);
  font-size: var(--font-size-sm);
}

@media (min-width: 480px) {
  .button {
    width: auto;
  }
}

@media (min-width: 768px) {
  .button {
    padding: var(--spacing-3) var(--spacing-6);
    font-size: var(--font-size-base);
  }
}

/* WRONG - Desktop first */
.button {
  width: auto;
  padding: var(--spacing-3) var(--spacing-6);
}

@media (max-width: 767px) {
  .button {
    width: 100%;
    padding: var(--spacing-3) var(--spacing-4);
  }
}
```

## Responsive Token Patterns

### Container Width

```css
.container {
  width: 100%;
  padding-inline: var(--spacing-4);
  margin-inline: auto;
}

@media (min-width: 480px) {
  .container {
    padding-inline: var(--spacing-5);
  }
}

@media (min-width: 768px) {
  .container {
    padding-inline: var(--spacing-6);
  }
}

@media (min-width: 1024px) {
  .container {
    max-width: 960px;
    padding-inline: var(--spacing-8);
  }
}

@media (min-width: 1280px) {
  .container {
    max-width: 1200px;
  }
}

@media (min-width: 1440px) {
  .container {
    max-width: 1320px;
  }
}

@media (min-width: 1920px) {
  .container {
    max-width: 1600px;
  }
}
```

### Typography Scale

```css
/* Heading scales down on mobile */
.h1 {
  font-size: var(--font-size-2xl);  /* 24px mobile */
  line-height: var(--line-height-tight);
}

@media (min-width: 480px) {
  .h1 {
    font-size: var(--font-size-3xl);  /* 30px */
  }
}

@media (min-width: 1024px) {
  .h1 {
    font-size: var(--font-size-4xl);  /* 36px */
  }
}

@media (min-width: 1440px) {
  .h1 {
    font-size: var(--font-size-5xl);  /* 48px */
  }
}

/* Body text slightly smaller on mobile */
.body {
  font-size: var(--font-size-sm);  /* 14px mobile */
}

@media (min-width: 768px) {
  .body {
    font-size: var(--font-size-base);  /* 16px */
  }
}
```

## Component Responsive Patterns

### Button

```css
.button {
  /* Mobile: Full width, stacked */
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--spacing-2);
  width: 100%;
  min-height: 44px; /* Touch target */
  padding: var(--spacing-3) var(--spacing-4);
  font-size: var(--font-size-sm);
}

@media (min-width: 480px) {
  .button {
    /* Mobile landscape: Auto width */
    width: auto;
  }
}

@media (min-width: 768px) {
  .button {
    /* Tablet+: Standard sizing */
    min-height: 40px;
    padding: var(--spacing-2) var(--spacing-4);
  }
}

@media (min-width: 1024px) {
  .button {
    /* Desktop: Standard sizing */
    padding: var(--spacing-2) var(--spacing-5);
    font-size: var(--font-size-base);
  }
}

/* Size variants also respond */
.button.lg {
  min-height: 52px;
  padding: var(--spacing-4) var(--spacing-5);
}

@media (min-width: 768px) {
  .button.lg {
    min-height: 48px;
    padding: var(--spacing-3) var(--spacing-6);
  }
}
```

### Card Grid

```css
.cardGrid {
  display: grid;
  gap: var(--spacing-4);
  
  /* Mobile: Single column */
  grid-template-columns: 1fr;
}

@media (min-width: 480px) {
  .cardGrid {
    /* Mobile landscape: 2 columns */
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 768px) {
  .cardGrid {
    /* Tablet: 2 columns with larger gap */
    gap: var(--spacing-5);
  }
}

@media (min-width: 1024px) {
  .cardGrid {
    /* Desktop: 3 columns */
    grid-template-columns: repeat(3, 1fr);
    gap: var(--spacing-6);
  }
}

@media (min-width: 1440px) {
  .cardGrid {
    /* Large desktop: 4 columns */
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (min-width: 1920px) {
  .cardGrid {
    /* Wide screens: 5 columns */
    grid-template-columns: repeat(5, 1fr);
    gap: var(--spacing-8);
  }
}
```

### Form Layout

```css
.form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.formRow {
  /* Mobile: Stack fields vertically */
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

@media (min-width: 768px) {
  .formRow {
    /* Tablet+: Side by side */
    flex-direction: row;
    gap: var(--spacing-5);
  }
  
  .formRow > * {
    flex: 1;
  }
}

.formActions {
  /* Mobile: Stack buttons, full width */
  display: flex;
  flex-direction: column-reverse;
  gap: var(--spacing-3);
}

@media (min-width: 480px) {
  .formActions {
    /* Mobile landscape+: Inline buttons */
    flex-direction: row;
    justify-content: flex-end;
    gap: var(--spacing-4);
  }
}
```

### Navigation

```css
.nav {
  /* Mobile: Hidden, show hamburger */
  display: none;
}

.mobileMenuButton {
  display: flex;
}

@media (min-width: 768px) {
  .nav {
    /* Tablet+: Show nav */
    display: flex;
    align-items: center;
    gap: var(--spacing-6);
  }
  
  .mobileMenuButton {
    display: none;
  }
}

/* Mobile menu overlay */
.mobileMenu {
  position: fixed;
  inset: 0;
  background: var(--color-surface);
  padding: var(--spacing-6);
  z-index: 50;
}

@media (min-width: 768px) {
  .mobileMenu {
    display: none;
  }
}
```

### Modal / Dialog

```css
.modal {
  /* Mobile: Full screen */
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
}

.modalContent {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-4);
}

@media (min-width: 480px) {
  .modal {
    /* Mobile landscape: Centered with some margin */
    inset: var(--spacing-4);
    border-radius: var(--radius-lg);
  }
}

@media (min-width: 768px) {
  .modal {
    /* Tablet+: Centered overlay */
    inset: unset;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    max-width: 500px;
    max-height: 90vh;
    border-radius: var(--radius-xl);
  }
  
  .modalContent {
    padding: var(--spacing-6);
  }
}

@media (min-width: 1024px) {
  .modal {
    max-width: 600px;
  }
}
```

### Table to Cards

```css
/* Mobile: Show as cards */
.table {
  display: block;
}

.tableHeader {
  display: none;
}

.tableRow {
  display: flex;
  flex-direction: column;
  padding: var(--spacing-4);
  border-bottom: 1px solid var(--color-border);
}

.tableCell {
  display: flex;
  justify-content: space-between;
  padding: var(--spacing-2) 0;
}

.tableCell::before {
  content: attr(data-label);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
}

@media (min-width: 768px) {
  /* Tablet+: Show as table */
  .table {
    display: table;
    width: 100%;
  }
  
  .tableHeader {
    display: table-header-group;
  }
  
  .tableRow {
    display: table-row;
  }
  
  .tableCell {
    display: table-cell;
    padding: var(--spacing-3) var(--spacing-4);
  }
  
  .tableCell::before {
    display: none;
  }
}
```

## Layout Templates

### Dashboard Layout

```css
.dashboardLayout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.sidebar {
  /* Mobile: Hidden or bottom nav */
  display: none;
}

.mainContent {
  flex: 1;
  padding: var(--spacing-4);
}

@media (min-width: 1024px) {
  .dashboardLayout {
    display: grid;
    grid-template-columns: 250px 1fr;
    grid-template-rows: auto 1fr;
  }
  
  .header {
    grid-column: 1 / -1;
  }
  
  .sidebar {
    display: flex;
    flex-direction: column;
    border-right: 1px solid var(--color-border);
    padding: var(--spacing-4);
  }
  
  .mainContent {
    padding: var(--spacing-6);
  }
}

@media (min-width: 1440px) {
  .dashboardLayout {
    grid-template-columns: 280px 1fr;
  }
  
  .mainContent {
    padding: var(--spacing-8);
  }
}

@media (min-width: 1920px) {
  .dashboardLayout {
    grid-template-columns: 320px 1fr;
  }
  
  .mainContent {
    padding: var(--spacing-10);
    max-width: 1600px;
  }
}
```

### Auth Layout

```css
.authLayout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  padding: var(--spacing-4);
}

.authForm {
  width: 100%;
  margin-top: auto;
  margin-bottom: auto;
}

@media (min-width: 480px) {
  .authLayout {
    align-items: center;
    justify-content: center;
  }
  
  .authForm {
    max-width: 400px;
    padding: var(--spacing-6);
    background: var(--color-surface);
    border-radius: var(--radius-xl);
    box-shadow: var(--shadow-lg);
  }
}

@media (min-width: 768px) {
  .authForm {
    padding: var(--spacing-8);
  }
}
```

## Touch Target Guidelines

**Minimum touch targets:**
- Mobile: 44px x 44px
- Desktop: Can be smaller (36px minimum recommended)

```css
.interactiveElement {
  min-height: 44px;
  min-width: 44px;
  
  /* Or use padding to achieve size */
  padding: var(--spacing-3);
}

@media (min-width: 1024px) {
  .interactiveElement {
    min-height: 36px;
    min-width: 36px;
    padding: var(--spacing-2);
  }
}
```

## Spacing Adjustments

```css
:root {
  /* Base spacing tokens - Mobile */
  --section-gap: var(--spacing-8);
  --component-gap: var(--spacing-4);
  --content-padding: var(--spacing-4);
}

@media (min-width: 768px) {
  :root {
    --section-gap: var(--spacing-12);
    --component-gap: var(--spacing-5);
    --content-padding: var(--spacing-6);
  }
}

@media (min-width: 1024px) {
  :root {
    --section-gap: var(--spacing-16);
    --component-gap: var(--spacing-6);
    --content-padding: var(--spacing-8);
  }
}

@media (min-width: 1440px) {
  :root {
    --section-gap: var(--spacing-20);
    --component-gap: var(--spacing-8);
    --content-padding: var(--spacing-10);
  }
}

@media (min-width: 1920px) {
  :root {
    --section-gap: var(--spacing-24);
    --component-gap: var(--spacing-10);
    --content-padding: var(--spacing-12);
  }
}
```
