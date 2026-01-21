# Responsive Design Patterns

Mobile-first responsive patterns. Extract ALL responsive values from Figma frames.

## Critical: Extract from Figma Frames

Check Figma for ALL frame variations: Mobile (320-480px), Tablet (768-1024px), Desktop (1280px+).
Do NOT invent breakpoint behavior - use Figma frames.

## Breakpoint System

| Name | Size | Target |
|------|------|--------|
| xs | 320px | Small mobile |
| sm | 480px | Mobile landscape |
| md | 768px | Tablet portrait |
| lg | 1024px | Tablet landscape |
| xl | 1280px | Desktop |
| 2xl | 1440px | Large desktop |
| 3xl | 1920px | Wide screens |

```css
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

## Mobile-First Pattern

```css
/* Mobile base - from Figma Mobile */
.button { width: 100%; padding: var(--spacing-3) var(--spacing-4); font-size: var(--font-size-sm); }

/* Landscape - from Figma */
@media (min-width: 480px) { .button { width: auto; } }

/* Tablet - from Figma Tablet */
@media (min-width: 768px) { .button { padding: var(--spacing-3) var(--spacing-6); font-size: var(--font-size-base); } }
```

## Container

```css
.container {
  width: 100%; padding-inline: var(--spacing-4); margin-inline: auto;
}
@media (min-width: 480px) { .container { padding-inline: var(--spacing-5); } }
@media (min-width: 768px) { .container { padding-inline: var(--spacing-6); } }
@media (min-width: 1024px) { .container { max-width: 960px; padding-inline: var(--spacing-8); } }
@media (min-width: 1280px) { .container { max-width: 1200px; } }
@media (min-width: 1440px) { .container { max-width: 1320px; } }
```

## Typography Scale

```css
.h1 { font-size: var(--font-size-2xl); }
@media (min-width: 480px) { .h1 { font-size: var(--font-size-3xl); } }
@media (min-width: 1024px) { .h1 { font-size: var(--font-size-4xl); } }
```

## Card Grid

```css
.cardGrid {
  display: grid; gap: var(--spacing-4);
  grid-template-columns: 1fr;
}
@media (min-width: 480px) { .cardGrid { grid-template-columns: repeat(2, 1fr); } }
@media (min-width: 768px) { .cardGrid { gap: var(--spacing-5); } }
@media (min-width: 1024px) { .cardGrid { grid-template-columns: repeat(3, 1fr); gap: var(--spacing-6); } }
@media (min-width: 1440px) { .cardGrid { grid-template-columns: repeat(4, 1fr); } }
```

## Form Layout

```css
.form { display: flex; flex-direction: column; gap: var(--spacing-4); }
.formRow { display: flex; flex-direction: column; gap: var(--spacing-4); }
@media (min-width: 768px) {
  .formRow { flex-direction: row; gap: var(--spacing-5); }
  .formRow > * { flex: 1; }
}

.formActions { display: flex; flex-direction: column-reverse; gap: var(--spacing-3); }
@media (min-width: 480px) {
  .formActions { flex-direction: row; justify-content: flex-end; gap: var(--spacing-4); }
}
```

## Navigation

```css
.nav { display: none; }
.mobileMenuButton { display: flex; }

@media (min-width: 768px) {
  .nav { display: flex; align-items: center; gap: var(--spacing-6); }
  .mobileMenuButton { display: none; }
}

.mobileMenu {
  position: fixed; inset: 0;
  background: var(--color-surface);
  padding: var(--spacing-6); z-index: 50;
}
@media (min-width: 768px) { .mobileMenu { display: none; } }
```

## Modal

```css
.modal { position: fixed; inset: 0; display: flex; flex-direction: column; }
.modalContent { flex: 1; overflow-y: auto; padding: var(--spacing-4); }

@media (min-width: 480px) {
  .modal { inset: var(--spacing-4); border-radius: var(--radius-lg); }
}
@media (min-width: 768px) {
  .modal {
    inset: unset; top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    max-width: 500px; max-height: 90vh;
    border-radius: var(--radius-xl);
  }
  .modalContent { padding: var(--spacing-6); }
}
```

## Dashboard Layout

```css
.dashboardLayout { display: flex; flex-direction: column; min-height: 100vh; }
.sidebar { display: none; }
.mainContent { flex: 1; padding: var(--spacing-4); }

@media (min-width: 1024px) {
  .dashboardLayout { display: grid; grid-template-columns: 250px 1fr; }
  .sidebar { display: flex; flex-direction: column; border-right: 1px solid var(--color-border); padding: var(--spacing-4); }
  .mainContent { padding: var(--spacing-6); }
}
@media (min-width: 1440px) {
  .dashboardLayout { grid-template-columns: 280px 1fr; }
  .mainContent { padding: var(--spacing-8); }
}
```

## Touch Targets

```css
.interactiveElement { min-height: 44px; min-width: 44px; padding: var(--spacing-3); }
@media (min-width: 1024px) {
  .interactiveElement { min-height: 36px; min-width: 36px; padding: var(--spacing-2); }
}
```
