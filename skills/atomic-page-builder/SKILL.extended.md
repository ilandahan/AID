---
name: atomic-page-builder
description: Build complete pages, views, and features using ONLY existing atomic-design components. REQUIRES atomic-design skill. Use when composing pages from existing design system components, building new views/features that must maintain design consistency, creating layouts that combine organisms and templates, or when the user asks to 'build a page', 'create a view', or 'compose a feature' from existing components.
---

# Atomic Page Builder

Compose production-ready pages using ONLY existing atomic-design components.

## ⚠️ CRITICAL RULE: design spec Is The Source of Truth

```
┌─────────────────────────────────────────────────────────────────────────┐
│  🚨 MANDATORY: EXTRACT PAGE LAYOUT FROM design spec BEFORE BUILDING           │
│                                                                         │
│  1. NEVER guess page layout or spacing                                  │
│  2. ALWAYS use local design specifications to extract EXACT page specs first              │
│  3. Download code/CSS from local design exports when available                │
│  4. Page overrides in design spec = implement as page-specific styles         │
│  5. If design spec shows values different than tokens → UPDATE tokens         │
│                                                                         │
│  ❌ "אני חושב שהלייאאוט הזה ייראה יותר טוב ככה" = FORBIDDEN               │
│  ✅ "design spec מראה את הלייאאוט ככה, אז הקוד יהיה ככה" = CORRECT              │
└─────────────────────────────────────────────────────────────────────────┘
```

### design spec-First Workflow for Pages (REQUIRED)

```
BEFORE building ANY page:

1. EXTRACT PAGE SPECS FROM design spec (MANDATORY - NO EXCEPTIONS)
   │
Read the approved local design specification and token files.
   ├─► Extract: grid layout, gaps, padding, margins
   ├─► Identify which components are used
   ├─► Note any page-specific overrides
   ├─► Document ALL extracted values
   │
2. COMPARE WITH EXISTING TOKENS
   │
   ├─► Check spacing tokens match design spec
   ├─► Check breakpoint behavior matches
   ├─► If different → UPDATE tokens (design spec WINS always)
   │
3. IMPLEMENT EXACTLY AS DESIGNED
   │
   └─► Match design spec layout 1:1 - NO interpretation
       NO "improvements", NO creative decisions
```

---

## Critical Rules

```
❌ FORBIDDEN: Creating new atoms, molecules, organisms, or base styles
❌ FORBIDDEN: Guessing layout values without checking design spec
❌ FORBIDDEN: Ignoring page-specific overrides shown in design spec
❌ FORBIDDEN: "Improving" or "fixing" the designer's layout decisions
❌ FORBIDDEN: Rounding values (13px stays 13px, not 12px)

✅ REQUIRED: Extract page specs from design spec FIRST
✅ REQUIRED: Compose pages using ONLY existing components
✅ REQUIRED: Implement page-specific styles from design spec exactly
✅ REQUIRED: Document design spec link in page component
```

**Prerequisite:** atomic-design skill must exist. If not → STOP and inform user.

---

## Zero Deviation Policy for Pages

| Forbidden Action | Why It's Wrong | Correct Action |
|------------------|----------------|----------------|
| Change grid columns | Designer decided layout | Use exact grid from design spec |
| Adjust gap spacing | Not developer's choice | Extract exact gap from design spec |
| Move elements around | Layout is designed | Follow design spec exactly |
| Add margins/padding | Unauthorized change | Only what design spec shows |
| "Optimize" for mobile | Check design spec mobile frame | Use design spec mobile specs |

**Read:** `atomic-design/references/design-deviation-rules.md` for complete policy.

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
| **design spec fidelity guide** | `atomic-design/references/design-deviation-rules.md` |
| **Deviation rules** | `atomic-design/references/design-deviation-rules.md` |

**Do NOT duplicate tokens or create new ones here.**

---

## Decision Tree

```
User Request: "Build a [page/view/feature]"
     │
     ├─► Step 0: EXTRACT FROM design spec (MANDATORY)
     │        │
     │        └─► Use MCP to get page frame specs:
     │            • Layout (grid columns, flex direction)
     │            • Gaps between sections
     │            • Page padding/margins
     │            • Section-specific overrides
     │            • Responsive variations
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

### Phase 0: Extract from design spec (MANDATORY)

**Before ANY other step:**

Read the approved local design specification and token files. Document layout type, columns, rows, gaps, padding, section spacing and behavior at each breakpoint. Ask for missing values before composing the page.

**Document extracted specs:**
```
Page: Dashboard
design spec Link: ./design-spec.md
Extracted: 2024-01-15

├── Layout: CSS Grid
├── Columns: 12-column grid (from design spec)
├── Gap: 24px (--spacing-6) - EXACT from design spec
├── Padding: 32px (--spacing-8) - EXACT from design spec
├── Header height: 64px
├── Sidebar width: 280px
└── Responsive (from design spec frames):
    ├── Mobile (< 768px): Single column, no sidebar
    ├── Tablet (768-1023px): Sidebar as drawer
    └── Desktop (≥ 1024px): Full layout
```

### Phase 1: Component Inventory

**After extracting design spec specs, list available components:**

```
ATOMS:      Button, Input, Typography, Icon, Avatar, Badge, Spinner
MOLECULES:  FormField, SearchBar, Card, NavItem, Toast
ORGANISMS:  Header, Sidebar, Footer, Form, DataTable, Modal
TEMPLATES:  DashboardLayout, AuthLayout, SettingsLayout
```

### Phase 2: Gap Analysis

| Requirement (from design spec) | Needed Component | Status |
|--------------------------|------------------|--------|
| Page header | Typography (h1) | ✅ |
| Stats display | Card + Typography | ✅ |
| Data chart | Chart (organism) | ❌ MISSING |
| User table | DataTable | ✅ |

**Gap Found?** → STOP. Report: "Missing: Chart organism. Switch to atomic-design to create."

### Phase 3: Page Composition

**Only if ALL components exist AND design spec specs extracted:**

```tsx
/**
 * Dashboard Page
 *
 * @design-source ./design-spec.md
 * @extracted 2024-01-15
 *
 * Layout specs from design spec - DO NOT MODIFY without designer approval.
 */

import { DashboardLayout } from '@/templates/DashboardLayout';
import { Card } from '@/molecules/Card';
import { Typography } from '@/atoms/Typography';
import { DataTable } from '@/organisms/DataTable';
import styles from './Dashboard.module.css';

export const Dashboard = () => (
  <DashboardLayout>
    <Typography variant="h1">Dashboard</Typography>

    {/* Grid layout matches design spec exactly */}
    <div className={styles.statsGrid}>
      <Card title="Revenue">$12,450</Card>
      <Card title="Users">1,234</Card>
    </div>

    <DataTable columns={columns} data={data} />
  </DashboardLayout>
);
```

```css
/**
 * Dashboard Page Styles
 *
 * Source: design spec Design System
 * Frame: Pages/Dashboard
 * Extracted: 2024-01-15
 *
 * ⚠️ ALL values from design spec - DO NOT MODIFY
 */

/* Values extracted from design spec - EXACT */
.statsGrid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);  /* design spec: 3-column layout */
  gap: var(--spacing-6);                   /* design spec: 24px gap - EXACT */
}

@media (max-width: 768px) {
  .statsGrid {
    grid-template-columns: 1fr;            /* design spec mobile: single column */
    gap: var(--spacing-4);                 /* design spec mobile: 16px gap - EXACT */
  }
}
```

---

## Handling Page-Specific Overrides from design spec

### When design spec Shows Different Values

```
Scenario: design spec shows hero section with padding: 64px
          But --spacing-section-gap is 48px

Decision Tree:
├─► Is this a new standard for all pages?
│        └─► YES → Update token in atomic-design skill
│                  Then use: padding: var(--spacing-section-gap)
│
└─► Is this a page-specific exception?
         └─► YES → Create page-specific style with design spec link comment:
```

```css
/* Dashboard.module.css */

/**
 * Page-specific override - matches design spec design for dashboard hero
 * design spec: ./design-spec.md
 * This is an intentional exception, NOT a mistake.
 */
.heroSection {
  padding: var(--spacing-16);  /* 64px - exception for dashboard */
}
```

### When Components Look Different in design spec Page vs Style Guide

```
Situation: Button in design spec page has different border-radius
          than Button in design spec style guide

Action:
1. STOP - this is a design inconsistency
2. Report to designer/team
3. Ask: "Should style guide be updated or is this an exception?"
4. Only proceed when clarified:
   ├─► Update style guide → Use atomic-design skill to update Button
   └─► Page exception → Create page-specific wrapper class with comment
```

### Question Template for Designer:
```
שמתי לב שבעמוד [page name] הקומפוננטה [component]
נראית שונה מה-Style Guide.
[property] בעמוד הוא [page value] אבל ב-Style Guide הוא [guide value].
האם זו חריגה מכוונת או שצריך לעדכן את ה-Style Guide?
```

---

## Rules: Allowed vs Forbidden

| Allowed | Forbidden |
|---------|-----------|
| Import from design system | Import from external UI libs (MUI, Chakra) |
| Layout utilities (grid, flex) from design spec | Guessing layout values |
| Content/behavior props | Visual props (color, fontSize) |
| CSS Modules with tokens | Hardcoded values (`#333`, `24px`) |
| Conditional rendering | Creating new base components |
| Page-specific layout (from design spec) | `styled-components` new definitions |
| Exact design spec values | Rounded or "improved" values |

### Code Examples

```tsx
// ✅ ALLOWED - Layout from design spec specs
<div className={styles.grid}>  {/* Grid values extracted from design spec */}
  <Card>{content}</Card>
</div>

// ❌ FORBIDDEN - Guessed values
<div style={{ padding: '24px', color: '#333' }}>

// ❌ FORBIDDEN - External UI library
import { Button } from '@chakra-ui/react';

// ❌ FORBIDDEN - Tailwind classes instead of design system
<div className="p-6 text-gray-700">

// ❌ FORBIDDEN - Creating new styled component
const NewCard = styled.div`...`;

// ❌ FORBIDDEN - "Improving" the design
gap: 20px;  // When design spec shows 24px - WRONG!
```

---

## Layout Patterns (Extract from design spec First)

### Grid Layouts
```css
/**
 * Grid Layout - values from design spec
 * design spec frame: [link]
 */

/* Extract from design spec:
   - Number of columns
   - Gap value
   - Responsive breakpoints
*/

.statsGrid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);   /* From design spec - EXACT */
  gap: var(--spacing-section-gap);          /* Token (verify matches design spec) */
}

.twoColumn {
  display: grid;
  grid-template-columns: 1fr 1fr;           /* From design spec - EXACT */
  gap: var(--spacing-component-gap);        /* Token (verify matches design spec) */
}
```

### Responsive Composition
```css
/**
 * Responsive styles - ALL values from design spec frames
 * Mobile: design spec frame [link]
 * Tablet: design spec frame [link]
 * Desktop: design spec frame [link]
 */

/* design spec shows:
   - Mobile: 16px padding
   - Tablet: 24px padding
   - Desktop: 32px padding
*/

.pageContent {
  padding: var(--spacing-4);   /* 16px - Mobile from design spec - EXACT */
}

@media (min-width: 768px) {
  .pageContent {
    padding: var(--spacing-6);  /* 24px - Tablet from design spec - EXACT */
  }
}

@media (min-width: 1024px) {
  .pageContent {
    padding: var(--spacing-8);  /* 32px - Desktop from design spec - EXACT */
  }
}
```

---

## Output Checklist

Before delivering:

- [ ] ⚠️ Page specs extracted from design spec (not guessed)
- [ ] ⚠️ Layout values match design spec exactly (no rounding)
- [ ] ⚠️ Responsive breakpoints match design spec behavior
- [ ] ⚠️ Visual comparison shows 0% difference from design spec
- [ ] ⚠️ design spec link documented in component and CSS
- [ ] All imports from design system only
- [ ] Zero hardcoded colors/spacing/typography
- [ ] Zero new component definitions
- [ ] Zero external UI library imports
- [ ] Layout uses CSS Modules + tokens
- [ ] TypeScript types complete
- [ ] Page-specific overrides documented with design spec links

---

## Skill Switching Guide

| Situation | Action |
|-----------|--------|
| Missing atom/molecule/organism | → Switch to **atomic-design** |
| Need new design tokens | → Switch to **atomic-design** |
| Need to modify existing component | → Switch to **atomic-design** |
| design spec shows token value changed | → Switch to **atomic-design** (update tokens first) |
| Composing from existing components | → **Stay here** ✓ |
| Page-specific layout from design spec | → **Stay here** ✓ |

---

## Common Page Types

| Page Type | Typical Components | Key design spec Specs to Extract |
|-----------|-------------------|---------------------------|
| Dashboard | DashboardLayout + Card + DataTable + Typography | Grid columns, card gaps, section spacing |
| Settings | SettingsLayout + Form + FormField + Button | Form width, field spacing, section dividers |
| Auth (Login/Register) | AuthLayout + Card + Form + Input + Button | Card width, form padding, centered layout |
| List/Table | PageLayout + DataTable + Pagination + SearchBar | Table width, row height, pagination position |
| Detail/Profile | PageLayout + Card + Avatar + Typography + Tabs | Content width, tab spacing, header layout |
| Form Page | PageLayout + Form + FormField + Button + Toast | Form max-width, field gaps, button alignment |

---

## Quick Reference

### design spec Extraction Checklist (Do First!)

```
□ Page container padding (all sides)
□ Section gaps/margins
□ Grid: columns, gap, alignment
□ Flex: direction, gap, alignment
□ Component placement
□ Responsive breakpoints (check ALL design spec frames)
□ Page-specific overrides
□ design spec links for documentation
```

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

// Use ONLY token-based values (verified against design spec)
.container {
  padding: var(--spacing-page-margin);   /* Verify: matches design spec */
  gap: var(--spacing-section-gap);       /* Verify: matches design spec */
}
```

### Page-Specific Override Pattern
```css
/**
 * Page-specific override
 * design spec: [paste frame link]
 * Reason: [why this differs from standard]
 * Approved by: [designer name/date]
 */
.specialSection {
  padding: var(--spacing-12);  /* Exception: 48px instead of standard 32px */
}
```

---

## References

| File | When to Read |
|------|--------------|
| `atomic-design/references/design-deviation-rules.md` | **Before ANY page work** |
| `atomic-design/references/design-deviation-rules.md` | **When tempted to change something** |
| `atomic-design/references/design-deviation-rules.md` | Extracting specs from design spec |
| `atomic-design/tokens/*.json` | Checking token values |
| `atomic-design/references/responsive-patterns.md` | Responsive implementation |
