# Atomic Design Hierarchy

## Critical: Extract from Figma First

Before creating any component: Extract specs from Figma, document Figma link, use EXACT values.

## Level 1: Atoms

Smallest, indivisible UI elements.

### Typography Atom
```typescript
type TypographyVariant = 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6' | 'body-lg' | 'body' | 'body-sm' | 'caption' | 'overline' | 'label';

interface TypographyProps {
  children: ReactNode;
  variant?: TypographyVariant;
  as?: keyof JSX.IntrinsicElements;
  color?: 'primary' | 'secondary' | 'muted' | 'inverse' | 'error' | 'success';
}
```

### Button Atom
```typescript
interface ButtonProps {
  label: string;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  icon?: ReactNode;
  iconPosition?: 'left' | 'right';
  fullWidth?: boolean;
}
```

### Input Atom
```typescript
interface InputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url';
  disabled?: boolean;
  error?: boolean;
  id?: string;
  name?: string;
  'aria-describedby'?: string;
}
```

### Other Atoms
- Icon: SVG wrapper (size, color)
- Badge: Status indicators (label, variant)
- Avatar: Image/initials (src, alt, size)
- Divider: Visual separator (orientation)
- Spinner: Loading indicator (size)
- Checkbox/Radio/Switch: Toggle controls

## Level 2: Molecules

Groups of atoms functioning together.

### FormField Molecule
```typescript
interface FormFieldProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  type?: 'text' | 'email' | 'password' | 'number';
  error?: string;
  hint?: string;
  required?: boolean;
  disabled?: boolean;
}
// Composes: Typography (label) + Input + Typography (error/hint)
```

### Card Molecule
```typescript
interface CardProps {
  title?: string;
  subtitle?: string;
  children: ReactNode;
  footer?: ReactNode;
  variant?: 'elevated' | 'outlined' | 'filled';
  onClick?: () => void;
  as?: 'article' | 'section' | 'div';
}
```

### Other Molecules
- SearchBar: Input + Button + Icon
- MenuItem: Icon + Label + Badge
- ListItem: Avatar + Content + Actions
- Breadcrumb: Icon + Links + Separator
- Pagination: Buttons + Page numbers
- Tabs: Tab buttons + active state
- Toast: Icon + Message + Close
- Modal Header: Title + Close button

## Level 3: Organisms

Complex UI sections composed of molecules and atoms.

### Header Organism
```typescript
interface HeaderProps {
  logo: ReactNode;
  navItems: { label: string; href: string; isActive?: boolean }[];
  onLogoClick?: () => void;
  actions?: ReactNode;
  userMenu?: {
    userName: string;
    userAvatar?: string;
    menuItems: { label: string; onClick: () => void }[];
  };
}
// Composes: Logo + NavItems + UserMenu + MobileMenu
```

### Form Organism
```typescript
interface FormProps {
  fields: FormField[];
  values: Record<string, string>;
  errors: Record<string, string>;
  onChange: (name: string, value: string) => void;
  onSubmit: () => void;
  submitLabel: string;
  loading?: boolean;
  secondaryAction?: { label: string; onClick: () => void };
}
// Composes: FormFields + Buttons
```

### Other Organisms
- DataTable: Headers + Rows + Pagination + Sorting
- Sidebar: Navigation + User section + Logo
- Footer: Links + Social + Copyright
- HeroSection: Heading + CTA + Image
- FeatureGrid: Cards grid + Section header
- PricingTable: Plan cards + Comparison

## Level 4: Templates

Page-level layouts without specific content.

```typescript
interface DashboardLayoutProps {
  header: ReactNode;
  sidebar: ReactNode;
  children: ReactNode;
  footer?: ReactNode;
}
```

## Level 5: Pages

Specific instances of templates with real content.

```typescript
// pages/Dashboard/Dashboard.tsx
export const DashboardPage = () => {
  const { user } = useAuth();
  return (
    <DashboardLayout
      header={<Header logo={<Logo />} navItems={NAV_ITEMS} />}
      sidebar={<Sidebar items={SIDEBAR_ITEMS} />}
    >
      <Typography variant="h1">Welcome, {user.firstName}</Typography>
      <StatsGrid stats={stats} />
    </DashboardLayout>
  );
};
```
