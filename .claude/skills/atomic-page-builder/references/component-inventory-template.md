# Component Inventory Template

## How to Use This Template

Before building any page:
1. Copy this template
2. Fill in available components
3. Map page requirements to components
4. Identify gaps

## Current Design System Inventory

### Atoms
```markdown
| Component | Variants | Props | Status |
|-----------|----------|-------|--------|
| Button | primary, secondary, ghost, danger | size, disabled, loading | ✅ Ready |
| Input | text, password, email, search | size, error, disabled | ✅ Ready |
| Badge | success, warning, error, info, neutral | size | ✅ Ready |
| Icon | [list icons] | size, color | ✅ Ready |
| Avatar | image, initials | size | ✅ Ready |
| Checkbox | default | checked, disabled, indeterminate | ✅ Ready |
| Radio | default | checked, disabled | ✅ Ready |
| Toggle | default | on, disabled | ✅ Ready |
| Spinner | default | size | ✅ Ready |
| Tooltip | default | position | ✅ Ready |
```

### Molecules
```markdown
| Component | Composition | Props | Status |
|-----------|-------------|-------|--------|
| Card | Container + padding | variant, clickable | ✅ Ready |
| FormField | Label + Input + Error | name, label, error | ✅ Ready |
| SearchBar | Input + Icon + Button | onSearch, placeholder | ✅ Ready |
| Dropdown | Button + Menu | options, onChange | ✅ Ready |
| Tabs | TabList + TabPanels | tabs, activeTab | ✅ Ready |
| Breadcrumb | Links + Separators | items | ✅ Ready |
| Pagination | Buttons + Info | page, total, onChange | ✅ Ready |
| Alert | Icon + Text + Actions | type, message, onClose | ✅ Ready |
```

### Organisms
```markdown
| Component | Composition | Props | Status |
|-----------|-------------|-------|--------|
| Header | Logo + Nav + Actions | user, onLogout | ✅ Ready |
| Sidebar | Logo + NavItems + Footer | items, collapsed | ✅ Ready |
| DataTable | Header + Rows + Pagination | columns, data, sorting | ✅ Ready |
| Modal | Overlay + Container + Content | isOpen, onClose, size | ✅ Ready |
| Form | FormFields + Actions | onSubmit, schema | ✅ Ready |
| Card Grid | Grid + Cards | items, columns | ✅ Ready |
| Empty State | Icon + Text + Action | message, action | ✅ Ready |
```

### Templates
```markdown
| Template | Composition | Use Case |
|----------|-------------|----------|
| DashboardLayout | Sidebar + Header + Main | Admin pages |
| AuthLayout | Centered card | Login, Register |
| SettingsLayout | Sidebar nav + Content | Settings pages |
| ListPageLayout | Header + Filters + Table | List/index pages |
| DetailPageLayout | Header + Tabs + Content | Detail/show pages |
```

## Gap Analysis Template

### Page: [Page Name]

#### Required Components
```markdown
| Need | Have | Gap? | Action |
|------|------|------|--------|
| Stats Card | Card | Variant missing | Create variant |
| User Menu | Dropdown | ✅ Exists | - |
| Activity Feed | - | ❌ Missing | Build in atomic-design |
| Chart | - | ❌ Missing | Build in atomic-design |
```

#### Required Tokens
```markdown
| Need | Have | Gap? | Action |
|------|------|------|--------|
| spacing-6 (24px) | ✅ Yes | - | - |
| color-chart-1 | ❌ No | Missing | Add to tokens |
```

## Component Mapping Example

```markdown
## Page: User Dashboard

### Section: Stats Row
- StatsCard x 4 (molecule - exists as Card variant)
  - Icon (atom)
  - Text (atom)
  - Badge (atom)

### Section: Activity Feed
- ActivityList (organism - ❌ MISSING)
  - ActivityItem (molecule - ❌ MISSING)
    - Avatar (atom)
    - Text (atom)
    - Timestamp (atom)

### Section: Quick Actions
- ButtonGroup (molecule - exists)
  - Button (atom)
  - Button (atom)
  - Button (atom)

## Gaps Found
1. ActivityList organism - needs creation
2. ActivityItem molecule - needs creation

## Decision
[ ] All components exist → Proceed with page
[x] Missing components → Switch to atomic-design skill first
```

## Quick Inventory Commands

```bash
# List all components
ls src/components/atoms/
ls src/components/molecules/
ls src/components/organisms/
ls src/components/templates/

# Search for component usage
grep -r "import.*Button" src/pages/
```
