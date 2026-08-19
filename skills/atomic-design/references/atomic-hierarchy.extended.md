# Atomic Design Hierarchy

Complete breakdown of component levels with implementation patterns.

## ⚠️ CRITICAL: Extract from Figma First

```
┌─────────────────────────────────────────────────────────────────────┐
│  🚨 BEFORE CREATING ANY COMPONENT:                                   │
│                                                                      │
│  1. Extract specs from Figma using MCP                              │
│  2. Document the Figma link in your component                       │
│  3. Use EXACT values - no rounding or "improving"                   │
│                                                                      │
│  The examples below show STRUCTURE, not actual values.              │
│  Your values MUST come from your Figma design system.               │
└─────────────────────────────────────────────────────────────────────┘
```

**Related documents:**
- `figma-design-fidelity.md` - Complete extraction workflow
- `design-deviation-rules.md` - Zero deviation policy
- `figma-mcp-integration.md` - MCP commands for extraction

## Level 1: Atoms

**Definition:** Smallest, indivisible UI elements. Cannot be broken down further.

### Typography Atoms

```typescript
/**
 * Typography Atom
 *
 * @figma https://figma.com/file/xxx/Design-System?node-id=typography
 * @extracted [DATE]
 *
 * ⚠️ All font sizes, weights, and line-heights from Figma - DO NOT MODIFY
 */

// atoms/Typography/Typography.tsx
import { ReactNode } from 'react';
import styles from './Typography.module.css';

type TypographyVariant = 
  | 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6'
  | 'body-lg' | 'body' | 'body-sm'
  | 'caption' | 'overline' | 'label';

interface TypographyProps {
  children: ReactNode;
  variant?: TypographyVariant;
  as?: keyof JSX.IntrinsicElements;
  color?: 'primary' | 'secondary' | 'muted' | 'inverse' | 'error' | 'success';
}

export const Typography = ({ 
  children, 
  variant = 'body', 
  as,
  color = 'primary' 
}: TypographyProps) => {
  const Component = as || getDefaultTag(variant);
  return (
    <Component className={`${styles[variant]} ${styles[`color-${color}`]}`}>
      {children}
    </Component>
  );
};

/* Typography.module.css - ALL styles encapsulated */
/* ⚠️ ALL values EXACT from Figma - verify before using */

.h1 {
  font-family: var(--font-heading);      /* From Figma */
  font-size: var(--font-size-4xl);       /* From Figma */
  font-weight: var(--font-weight-bold);  /* From Figma */
  line-height: var(--line-height-tight); /* From Figma */
  letter-spacing: var(--letter-spacing-tight); /* From Figma */
}

/* Responsive: Check Figma Mobile frame for these values */
@media (max-width: 768px) {
  .h1 { font-size: var(--font-size-2xl); } /* From Figma Mobile */
}
/* ... all variants defined - ALL from Figma */
```

### Button Atom

```typescript
/**
 * Button Atom
 *
 * @figma https://figma.com/file/xxx/Design-System?node-id=button
 * @extracted [DATE]
 *
 * ⚠️ All sizes, padding, colors from Figma - DO NOT MODIFY
 */

// atoms/Button/Button.tsx
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

export const Button = ({
  label,
  onClick,
  type = 'button',
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  icon,
  iconPosition = 'left',
  fullWidth = false,
}: ButtonProps) => {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={clsx(
        styles.button,
        styles[variant],
        styles[size],
        fullWidth && styles.fullWidth
      )}
      aria-busy={loading}
    >
      {loading ? <Spinner size="sm" /> : (
        <>
          {icon && iconPosition === 'left' && <span className={styles.icon}>{icon}</span>}
          <span>{label}</span>
          {icon && iconPosition === 'right' && <span className={styles.icon}>{icon}</span>}
        </>
      )}
    </button>
  );
};
```

### Input Atom

```typescript
/**
 * Input Atom
 *
 * @figma https://figma.com/file/xxx/Design-System?node-id=input
 * @extracted [DATE]
 *
 * ⚠️ All sizes, padding, border styles from Figma - DO NOT MODIFY
 */

// atoms/Input/Input.tsx
interface InputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url';
  disabled?: boolean;
  error?: boolean;
  id?: string;
  name?: string;
  autoComplete?: string;
  'aria-describedby'?: string;
}

export const Input = ({
  value,
  onChange,
  placeholder,
  type = 'text',
  disabled = false,
  error = false,
  ...props
}: InputProps) => {
  return (
    <input
      type={type}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      disabled={disabled}
      className={clsx(styles.input, error && styles.error)}
      aria-invalid={error}
      {...props}
    />
  );
};
```

### Other Atoms
- **Icon** - SVG wrapper with size/color variants
- **Badge** - Status indicators (label + variant)
- **Avatar** - Image/initials display (src + alt + size)
- **Divider** - Visual separator (orientation)
- **Spinner** - Loading indicator (size)
- **Checkbox** - Toggle (checked + onChange + label)
- **Radio** - Selection (checked + onChange + label)
- **Switch** - Toggle switch (checked + onChange)

---

## Level 2: Molecules

**Definition:** Groups of atoms functioning together as a unit.

### FormField Molecule

```typescript
/**
 * FormField Molecule
 *
 * @figma https://figma.com/file/xxx/Design-System?node-id=formfield
 * @extracted [DATE]
 *
 * Composes: Typography (label) + Input + Typography (error/hint)
 * ⚠️ Layout spacing from Figma - DO NOT MODIFY
 */

// molecules/FormField/FormField.tsx
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

export const FormField = ({
  label,
  value,
  onChange,
  placeholder,
  type = 'text',
  error,
  hint,
  required = false,
  disabled = false,
}: FormFieldProps) => {
  const id = useId();
  const errorId = `${id}-error`;
  const hintId = `${id}-hint`;

  return (
    <div className={styles.field}>
      <Typography 
        as="label" 
        variant="label" 
        htmlFor={id}
        className={styles.label}
      >
        {label}
        {required && <span className={styles.required}>*</span>}
      </Typography>
      
      <Input
        id={id}
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        disabled={disabled}
        error={!!error}
        aria-describedby={error ? errorId : hint ? hintId : undefined}
      />
      
      {error && (
        <Typography id={errorId} variant="caption" color="error">
          {error}
        </Typography>
      )}
      {hint && !error && (
        <Typography id={hintId} variant="caption" color="muted">
          {hint}
        </Typography>
      )}
    </div>
  );
};
```

### Card Molecule

```typescript
/**
 * Card Molecule
 *
 * @figma https://figma.com/file/xxx/Design-System?node-id=card
 * @extracted [DATE]
 *
 * ⚠️ All padding, shadows, border-radius from Figma - DO NOT MODIFY
 */

// molecules/Card/Card.tsx
interface CardProps {
  title?: string;
  subtitle?: string;
  children: ReactNode;
  footer?: ReactNode;
  variant?: 'elevated' | 'outlined' | 'filled';
  onClick?: () => void;
  as?: 'article' | 'section' | 'div';
}

export const Card = ({
  title,
  subtitle,
  children,
  footer,
  variant = 'elevated',
  onClick,
  as: Component = 'div',
}: CardProps) => {
  const isInteractive = !!onClick;
  
  return (
    <Component
      className={clsx(styles.card, styles[variant], isInteractive && styles.interactive)}
      onClick={onClick}
      role={isInteractive ? 'button' : undefined}
      tabIndex={isInteractive ? 0 : undefined}
    >
      {(title || subtitle) && (
        <div className={styles.header}>
          {title && <Typography variant="h4">{title}</Typography>}
          {subtitle && <Typography variant="body-sm" color="secondary">{subtitle}</Typography>}
        </div>
      )}
      <div className={styles.content}>{children}</div>
      {footer && <div className={styles.footer}>{footer}</div>}
    </Component>
  );
};
```

### Other Molecules
- **SearchBar** - Input + Button + Icon
- **MenuItem** - Icon + Label + Badge (optional)
- **ListItem** - Avatar + Content + Actions
- **Breadcrumb** - Icon + Links + Separator
- **Pagination** - Buttons + Page numbers
- **Tabs** - Tab buttons + active state
- **Toast** - Icon + Message + Close button
- **Modal Header** - Title + Close button

---

## Level 3: Organisms

**Definition:** Complex UI sections composed of molecules and atoms.

### Header Organism

```typescript
/**
 * Header Organism
 *
 * @figma https://figma.com/file/xxx/Design-System?node-id=header
 * @extracted [DATE]
 *
 * Composes: Logo + NavItems + UserMenu + MobileMenu
 * ⚠️ All heights, spacing, responsive behavior from Figma - DO NOT MODIFY
 */

// organisms/Header/Header.tsx
interface NavItem {
  label: string;
  href: string;
  isActive?: boolean;
}

interface HeaderProps {
  logo: ReactNode;
  navItems: NavItem[];
  onLogoClick?: () => void;
  actions?: ReactNode;
  userMenu?: {
    userName: string;
    userAvatar?: string;
    menuItems: { label: string; onClick: () => void }[];
  };
}

export const Header = ({
  logo,
  navItems,
  onLogoClick,
  actions,
  userMenu,
}: HeaderProps) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className={styles.header}>
      <div className={styles.container}>
        <div className={styles.logoSection} onClick={onLogoClick}>
          {logo}
        </div>
        
        <nav className={styles.nav} aria-label="Main navigation">
          <ul className={styles.navList}>
            {navItems.map((item) => (
              <li key={item.href}>
                <a 
                  href={item.href}
                  className={clsx(styles.navLink, item.isActive && styles.active)}
                  aria-current={item.isActive ? 'page' : undefined}
                >
                  {item.label}
                </a>
              </li>
            ))}
          </ul>
        </nav>

        <div className={styles.actions}>
          {actions}
          {userMenu && (
            <UserMenu 
              userName={userMenu.userName}
              userAvatar={userMenu.userAvatar}
              menuItems={userMenu.menuItems}
            />
          )}
        </div>

        <Button
          label="Menu"
          variant="ghost"
          icon={<MenuIcon />}
          onClick={() => setMobileMenuOpen(true)}
          className={styles.mobileMenuButton}
        />
      </div>
      
      <MobileMenu 
        isOpen={mobileMenuOpen}
        onClose={() => setMobileMenuOpen(false)}
        navItems={navItems}
      />
    </header>
  );
};
```

### Form Organism

```typescript
/**
 * Form Organism
 *
 * @figma https://figma.com/file/xxx/Design-System?node-id=form
 * @extracted [DATE]
 *
 * Composes: FormFields + Buttons
 * ⚠️ All field gaps, button alignment from Figma - DO NOT MODIFY
 */

// organisms/Form/Form.tsx
interface FormField {
  name: string;
  label: string;
  type: 'text' | 'email' | 'password' | 'textarea' | 'select';
  placeholder?: string;
  required?: boolean;
  options?: { value: string; label: string }[]; // For select
}

interface FormProps {
  fields: FormField[];
  values: Record<string, string>;
  errors: Record<string, string>;
  onChange: (name: string, value: string) => void;
  onSubmit: () => void;
  submitLabel: string;
  loading?: boolean;
  secondaryAction?: {
    label: string;
    onClick: () => void;
  };
}

export const Form = ({
  fields,
  values,
  errors,
  onChange,
  onSubmit,
  submitLabel,
  loading = false,
  secondaryAction,
}: FormProps) => {
  return (
    <form onSubmit={(e) => { e.preventDefault(); onSubmit(); }} className={styles.form}>
      {fields.map((field) => (
        <FormField
          key={field.name}
          label={field.label}
          type={field.type}
          value={values[field.name] || ''}
          onChange={(value) => onChange(field.name, value)}
          placeholder={field.placeholder}
          error={errors[field.name]}
          required={field.required}
        />
      ))}
      
      <div className={styles.actions}>
        {secondaryAction && (
          <Button
            label={secondaryAction.label}
            variant="ghost"
            onClick={secondaryAction.onClick}
          />
        )}
        <Button
          label={submitLabel}
          type="submit"
          variant="primary"
          loading={loading}
        />
      </div>
    </form>
  );
};
```

### Other Organisms
- **DataTable** - Headers + Rows + Pagination + Sorting
- **Sidebar** - Navigation + User section + Logo
- **Footer** - Links + Social + Copyright
- **HeroSection** - Heading + CTA + Image/Video
- **FeatureGrid** - Cards grid + Section header
- **PricingTable** - Plan cards + Comparison
- **CommentSection** - Comments list + Reply form

---

## Level 4: Templates

**Definition:** Page-level layouts that arrange organisms without specific content.

```typescript
/**
 * DashboardLayout Template
 *
 * @figma https://figma.com/file/xxx/Design-System?node-id=dashboard-layout
 * @extracted [DATE]
 *
 * ⚠️ All grid columns, sidebar width, main area padding from Figma
 * Check Figma for Desktop, Tablet, Mobile frame variations
 */

// templates/DashboardLayout/DashboardLayout.tsx
interface DashboardLayoutProps {
  header: ReactNode;
  sidebar: ReactNode;
  children: ReactNode;
  footer?: ReactNode;
}

export const DashboardLayout = ({
  header,
  sidebar,
  children,
  footer,
}: DashboardLayoutProps) => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  return (
    <div className={styles.layout}>
      <div className={styles.headerArea}>{header}</div>
      <div className={clsx(styles.sidebarArea, sidebarCollapsed && styles.collapsed)}>
        {sidebar}
      </div>
      <main className={styles.mainArea}>{children}</main>
      {footer && <div className={styles.footerArea}>{footer}</div>}
    </div>
  );
};
```

---

## Level 5: Pages

**Definition:** Specific instances of templates with real content.

```typescript
/**
 * Dashboard Page
 *
 * @figma https://figma.com/file/xxx/App?node-id=dashboard-page
 * @extracted [DATE]
 *
 * Uses: DashboardLayout template + real content
 * ⚠️ All layout, spacing, responsive behavior from Figma page frames
 */

// pages/Dashboard/Dashboard.tsx
export const DashboardPage = () => {
  const { user } = useAuth();
  const { data: stats } = useDashboardStats();

  return (
    <DashboardLayout
      header={
        <Header
          logo={<Logo />}
          navItems={NAV_ITEMS}
          userMenu={{
            userName: user.name,
            userAvatar: user.avatar,
            menuItems: USER_MENU_ITEMS,
          }}
        />
      }
      sidebar={
        <Sidebar
          items={SIDEBAR_ITEMS}
          activeItem="dashboard"
        />
      }
    >
      <Typography variant="h1">Welcome back, {user.firstName}</Typography>
      <StatsGrid stats={stats} />
      <RecentActivityTable />
    </DashboardLayout>
  );
};
```