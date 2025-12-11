---
name: atomic-page-builder
description: "Build pages using ONLY existing design system components. Use when composing pages, views, or features from existing atoms/molecules/organisms."
---

# Atomic Page Builder

Compose production-ready pages using ONLY existing atomic-design components.

## Critical Rule

```
❌ FORBIDDEN: Creating new atoms, molecules, organisms, or base styles
✅ REQUIRED: Compose pages using ONLY existing components
```

**Prerequisite:** atomic-design skill must exist. If not → STOP and inform user.

---

## Shared Resources (from atomic-design)

This skill uses resources from the `atomic-design` skill:

| Need | Read From |
|------|-----------|
| Color values | `atomic-design/tokens/colors.json` |
| Spacing/shadows | `atomic-design/tokens/spacing.json` |
| Typography specs | `atomic-design/tokens/typography.json` |
| Component specs | `atomic-design/tokens/components.json` |
| Breakpoints | `atomic-design/tokens/breakpoints.json` |
| Component patterns | `atomic-design/references/` |

**Do NOT duplicate tokens or create new ones here.**

---

## Decision Tree

```
User Request: "Build a [page/view/feature]"
     │
     ├─► Step 1: INVENTORY
     │        │
     │        └─► Scan project for existing components:
     │            • src/design-system/atoms/
     │            • src/design-system/molecules/
     │            • src/design-system/organisms/
     │            • src/design-system/templates/
     │
     ├─► Step 2: GAP ANALYSIS
     │        │
     │        └─► Map requirements to components
     │            Create table: Requirement → Component → ✅/❌
     │
     └─► Step 3: BUILD OR STOP
              │
              ├─► All components exist?
              │        └─► YES → Compose page (Phase 3)
              │
              └─► Missing components?
                       └─► STOP → Report gaps → Switch to atomic-design
```

---

## Workflow Phases

### Phase 1: Component Inventory

**Before ANY code, list available components:**

```
ATOMS:      Button, Input, Typography, Icon, Avatar, Badge, Spinner
MOLECULES:  FormField, SearchBar, Card, NavItem, Toast
ORGANISMS:  Header, Sidebar, Footer, Form, DataTable, Modal
TEMPLATES:  DashboardLayout, AuthLayout, SettingsLayout
```

### Phase 2: Gap Analysis

| Requirement | Needed Component | Status |
|------------|------------------|--------|
| Page header | Typography (h1) | ✅ |
| Stats display | Card + Typography | ✅ |
| Data chart | Chart (organism) | ❌ MISSING |
| User table | DataTable | ✅ |

**Gap Found?** → STOP. Report: "Missing: Chart organism. Switch to atomic-design to create."

### Phase 3: Page Composition

**Only if ALL components exist:**

```tsx
// pages/Dashboard.tsx
import { DashboardLayout } from '@/templates/DashboardLayout';
import { Card } from '@/molecules/Card';
import { Typography } from '@/atoms/Typography';
import { DataTable } from '@/organisms/DataTable';

export const Dashboard = () => (
  <DashboardLayout>
    <Typography variant="h1">Dashboard</Typography>

    <div className={styles.statsGrid}>
      <Card title="Revenue">$12,450</Card>
      <Card title="Users">1,234</Card>
    </div>

    <DataTable columns={columns} data={data} />
  </DashboardLayout>
);
```

---

## Rules: Allowed vs Forbidden

| Allowed | Forbidden |
|---------|-----------|
| Import from design system | Import from external UI libs (MUI, Chakra) |
| Layout utilities (grid, flex) | Inline styles (`style={{ }}`) |
| Content/behavior props | Visual props (color, fontSize) |
| CSS Modules with tokens | Hardcoded values (`#333`, `24px`) |
| Conditional rendering | Creating new base components |
| Composition patterns | `styled-components` new definitions |

### Code Examples

```tsx
// ✅ ALLOWED
<div className={styles.grid}>
  <Card>{content}</Card>
</div>

// ❌ FORBIDDEN
<div style={{ padding: '24px', color: '#333' }}>
<div className="p-6 text-gray-700">
const NewCard = styled.div`...`;
import { Button } from '@chakra-ui/react';
```

---

## Layout Patterns

### Grid Layouts
```tsx
// Use CSS Module with token-based spacing
.statsGrid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-section-gap);
}

.twoColumn {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-component-gap);
}
```

### Responsive Composition
```tsx
.pageContent {
  padding: var(--spacing-page-margin);
}

@media (min-width: 768px) {
  .pageContent {
    padding: var(--spacing-page-margin-lg);
  }
}
```

---

## Output Checklist

Before delivering:

- [ ] All imports from design system only
- [ ] Zero hardcoded colors/spacing/typography
- [ ] Zero new component definitions
- [ ] Zero external UI library imports
- [ ] Layout uses CSS Modules + tokens
- [ ] Responsive at all breakpoints
- [ ] TypeScript types complete

---

## Skill Switching Guide

| Situation | Action |
|-----------|--------|
| Missing atom/molecule/organism | → Switch to **atomic-design** |
| Need new design tokens | → Switch to **atomic-design** |
| Need to modify existing component | → Switch to **atomic-design** |
| Composing from existing components | → **Stay here** ✓ |

---

## Common Page Types

| Page Type | Typical Components |
|-----------|-------------------|
| Dashboard | DashboardLayout + Card + DataTable + Typography |
| Settings | SettingsLayout + Form + FormField + Button |
| Auth (Login/Register) | AuthLayout + Card + Form + Input + Button |
| List/Table | PageLayout + DataTable + Pagination + SearchBar |
| Detail/Profile | PageLayout + Card + Avatar + Typography + Tabs |
| Form Page | PageLayout + Form + FormField + Button + Toast |

---

## Quick Reference

### Import Pattern
```tsx
// Always import from design system paths
import { Button } from '@/design-system/atoms/Button';
import { Card } from '@/design-system/molecules/Card';
import { Header } from '@/design-system/organisms/Header';
import { DashboardLayout } from '@/design-system/templates/DashboardLayout';
```

### Styling Pattern
```tsx
// Page-specific layout in CSS Module
import styles from './Dashboard.module.css';

// Use ONLY token-based values
.container {
  padding: var(--spacing-page-margin);
  gap: var(--spacing-section-gap);
}
```
