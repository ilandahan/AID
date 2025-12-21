# /build-page Command

Compose pages using ONLY existing design system components.

## Usage

```
/build-page <page-name>
```

## What It Does

1. **Inventories Components**
   - Scans existing atoms, molecules, organisms
   - Lists available templates
   - Identifies what can be composed

2. **Analyzes Gaps**
   - Maps requirements to components
   - Reports missing components
   - Suggests atomic-design skill if gaps exist

3. **Composes Page**
   - Uses only existing components
   - No new base components created
   - Enforces design consistency

4. **Uses Skill**
   - `atomic-page-builder` skill for methodology

## Examples

```bash
# Build a dashboard page
/build-page dashboard

# Build a settings page
/build-page settings

# Build a user profile page
/build-page user-profile

# Build with specific template
/build-page checkout --template AuthLayout
```

## Critical Rules

```
❌ FORBIDDEN:
- Creating new atoms/molecules/organisms
- Inline styles bypassing design system
- Hardcoded colors, spacing, typography
- Importing external UI libraries

✅ ALLOWED:
- Composing from existing components
- Layout utilities (grid, flex, gap)
- Passing content/behavior props
- Conditional rendering
```

## Workflow

1. Read `skills/atomic-page-builder/SKILL.md`
2. Scan project for existing components
3. Create component inventory
4. Map page requirements to components
5. Identify gaps (if any)
6. If gaps → STOP, report, suggest /design-system
7. If no gaps → Compose page
8. Verify no hardcoded values

## Output Format

```typescript
// pages/Dashboard.tsx
import { DashboardLayout } from '@/templates/DashboardLayout';
import { Card } from '@/molecules/Card';
import { Typography } from '@/atoms/Typography';
import { DataTable } from '@/organisms/DataTable';

export const DashboardPage = () => (
  <DashboardLayout>
    <Typography variant="h1">Welcome back</Typography>
    
    <div className="grid grid-cols-3 gap-6">
      <Card title="Revenue">
        <Typography variant="display">$12,450</Typography>
      </Card>
    </div>
    
    <DataTable columns={columns} data={data} />
  </DashboardLayout>
);
```

## Gap Report Format

```markdown
## Component Gap Analysis

### Required Components
| Requirement | Component | Status |
|------------|-----------|--------|
| User greeting | Typography | ✅ Exists |
| Stats cards | Card | ✅ Exists |
| Activity chart | Chart | ❌ MISSING |

### Action Required
Missing components detected. Please run:
/design-system --component Chart

Then return to:
/build-page dashboard
```

## Tips

- Always inventory before building
- Report gaps immediately
- Never create new base components
- Use only design system tokens
- Test at all breakpoints

---

## Prompt

```markdown
**Role**: You are a frontend developer specializing in component composition. You strictly adhere to design system constraints and never create new base components.

**Task**: Build the requested page by composing ONLY from existing design system components.

**Context**:
- Page: [PAGE_NAME]
- Design system: /src/design-system/ or /src/components/
- Read: `skills/atomic-page-builder/SKILL.md`

**Reasoning**:
- NEVER create new base components—compose only
- NEVER use hardcoded colors, spacing, typography
- NEVER import external UI libraries
- If a component is missing → STOP and report
- Layout utilities (grid, flex) are allowed

**Output Format**:
1. Component inventory (what exists)
2. Gap analysis (what's missing)
3. Page implementation (if no gaps)
4. Usage example

**Stopping Condition**:
- If ANY required component is missing → STOP
- Report missing components
- Suggest /design-system to create them
- Do NOT proceed with partial implementation

**Steps**:
1. Read `skills/atomic-page-builder/SKILL.md`
2. Scan for existing components (atoms, molecules, organisms, templates)
3. Create component inventory
4. Parse page requirements
5. Map requirements to components
6. Identify gaps
7. If gaps → STOP, report, suggest /design-system
8. If no gaps → Compose page
9. Verify zero hardcoded values
10. Deliver page code

---
Page: [PAGE_NAME]
---
```
