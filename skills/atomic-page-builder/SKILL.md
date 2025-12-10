---
name: atomic-page-builder
description: "Build complete pages, views, and features using ONLY existing atomic-design components. REQUIRES atomic-design skill. Use when composing pages from existing design system components, building new views/features that must maintain design consistency, creating layouts that combine organisms and templates, or when the user asks to 'build a page', 'create a view', or 'compose a feature' from existing components. Enforces design system usage."
---

# Atomic Page Builder

Build production-ready pages by composing ONLY from existing atomic-design components. This skill enforces design system consistency.

## Critical Dependency

**This skill REQUIRES the atomic-design skill.**

Before proceeding:
1. Verify atomic-design skill exists
2. Read atomic-design to understand available components
3. Check which atoms, molecules, organisms, and templates exist

If atomic-design is not available → STOP and inform the user.

## Core Principle: Compose, Never Create

```
❌ FORBIDDEN: Creating new atoms, molecules, or base styles
✅ REQUIRED: Compose pages using ONLY existing components
```

### Decision Tree

```
User Request → "Build me a dashboard page"
                    ↓
    1. Read atomic-design/SKILL.md
    2. Scan project for existing components:
       - /src/atoms/
       - /src/molecules/
       - /src/organisms/
       - /src/templates/
    3. Map request to available components
    4. Identify GAPS (missing components)
                    ↓
         ┌─────────┴─────────┐
         ↓                   ↓
    No Gaps              Gaps Found
         ↓                   ↓
    Compose page      STOP: Report to user
    from existing     "Missing components needed:
    components        - DataChart (organism)
                      Switch to atomic-design
                      to create these first."
```

## Workflow

### Phase 1: Component Inventory

Before writing ANY code, document available components:

```markdown
## Available Components Inventory

### Atoms
- Button (primary, secondary, ghost variants)
- Input (text, email, password)
- Typography (h1-h6, body, caption)
- Icon (from lucide-react)

### Molecules
- FormField (Label + Input + Error)
- SearchBar (Input + Button + Icon)
- Card (container with header, body, footer)

### Organisms
- Header (Logo + Nav + UserMenu)
- Sidebar (NavLinks + UserInfo)
- DataTable (headers, rows, pagination)

### Templates
- DashboardLayout (Header + Sidebar + MainContent)
- AuthLayout (centered card)
```

### Phase 2: Gap Analysis

Map user requirements to components:

| Requirement | Component | Status |
|------------|-----------|--------|
| User greeting | Typography (h1) | ✅ Exists |
| Stats cards | Card + Typography | ✅ Exists |
| Activity chart | ??? | ❌ MISSING |
| Recent orders table | DataTable | ✅ Exists |

**If gaps exist → Report and switch to atomic-design skill.**

### Phase 3: Page Composition

Only proceed if ALL components exist.

```typescript
// pages/Dashboard.tsx
import { DashboardLayout } from '@/templates/DashboardLayout';
import { Card } from '@/molecules/Card';
import { Typography } from '@/atoms/Typography';
import { DataTable } from '@/organisms/DataTable';

// ✅ CORRECT: Using only existing components
export const Dashboard = () => (
  <DashboardLayout>
    <Typography variant="h1">Welcome back</Typography>
    
    <div className="grid grid-cols-3 gap-6">
      <Card>
        <Typography variant="h3">Revenue</Typography>
        <Typography variant="display">$12,450</Typography>
      </Card>
    </div>
    
    <DataTable 
      columns={orderColumns}
      data={recentOrders}
    />
  </DashboardLayout>
);
```

### Forbidden Patterns

```typescript
// ❌ FORBIDDEN: Inline styles that bypass design system
<div style={{ padding: '24px', color: '#333' }}>

// ❌ FORBIDDEN: Hardcoded values instead of tokens
<div className="p-6 text-gray-700">

// ❌ FORBIDDEN: Creating new base components
const NewButton = styled.button`...`;

// ❌ FORBIDDEN: Mixing design systems
import { Button } from '@chakra-ui/react';
```

### Allowed Patterns

```typescript
// ✅ ALLOWED: Layout composition with existing components
<div className="grid grid-cols-2 gap-component">
  <ExistingCard />
  <ExistingCard />
</div>

// ✅ ALLOWED: Passing content props to existing components
<Button label="Submit" onClick={handleSubmit} />

// ✅ ALLOWED: Conditional rendering of existing components
{isLoading ? <Spinner /> : <DataTable data={data} />}
```

## Output Checklist

Before delivering any page:

- [ ] All components imported from design system
- [ ] Zero hardcoded colors, spacing, or typography
- [ ] Zero new component definitions
- [ ] Zero external UI library imports
- [ ] Layout uses only design system spacing tokens
- [ ] Page compiles without errors

## When to Switch Skills

| Situation | Action |
|-----------|--------|
| Missing atom/molecule/organism | → Switch to atomic-design |
| Need new design tokens | → Switch to atomic-design |
| Building component library | → Switch to atomic-design |
| Composing pages from existing | → Stay here ✓ |

---

## Prompt: Page Composition

```markdown
**Role**: You are a frontend developer specializing in component composition and page assembly. You strictly adhere to design system constraints and never create new base components.

**Task**: Build the requested page/view by composing ONLY from existing design system components. No new atoms, molecules, or organisms may be created.

**Context**:
- Design system location: /src/design-system/ (or /src/components/)
- Page request: [USER REQUEST]
- Available components: Must be inventoried before starting
- Framework: React with TypeScript
- Styling: Must use only design system tokens and layout utilities

**Reasoning**:
- NEVER create new base components—compose only
- NEVER use hardcoded colors, spacing, or typography
- NEVER import external UI libraries (Chakra, MUI, etc.)
- If a component is missing, STOP and report the gap
- Layout utilities (grid, flex, gap) are allowed
- Content and behavior props are the only customization

**Output Format**:
1. Component Inventory (what exists)
2. Gap Analysis (what's missing, if any)
3. Page Implementation (if no gaps):
   - TypeScript React component
   - Only imports from design system
   - Zero hardcoded values
4. Usage example

**Stopping Condition**:
- If ANY required component is missing → STOP immediately
- Report missing components
- Suggest switching to atomic-design skill to create them
- Do not proceed with partial implementation

**Steps**:
1. Read atomic-design/SKILL.md to understand the system
2. Scan project for existing components:
   - List all atoms in /src/atoms/ or /src/design-system/atoms/
   - List all molecules
   - List all organisms
   - List all templates
3. Parse user request into component requirements
4. Map each requirement to existing components
5. Identify gaps (requirements with no matching component)
6. If gaps exist → STOP, report gaps, suggest atomic-design skill
7. If no gaps → Compose page using only existing components
8. Verify: zero hardcoded values, zero new components
9. Deliver final page code

---
[PAGE REQUEST HERE]
---
```
