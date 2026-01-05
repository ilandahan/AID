# Component Templates

Production-ready templates. Replace ALL placeholder values with EXACT Figma values.

## Button Atom

```typescript
// atoms/Button/Button.tsx
interface ButtonProps extends Omit<ButtonHTMLAttributes<HTMLButtonElement>, 'children'> {
  label: string;
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  icon?: ReactNode;
  iconPosition?: 'left' | 'right';
  loading?: boolean;
  fullWidth?: boolean;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ label, variant = 'primary', size = 'md', icon, iconPosition = 'left', loading = false, fullWidth = false, disabled, className, ...props }, ref) => (
    <button
      ref={ref}
      disabled={disabled || loading}
      className={clsx(styles.button, styles[variant], styles[size], fullWidth && styles.fullWidth)}
      aria-busy={loading}
      {...props}
    >
      {loading ? <span className={styles.spinner} /> : (
        <>
          {icon && iconPosition === 'left' && <span className={styles.iconLeft}>{icon}</span>}
          <span>{label}</span>
          {icon && iconPosition === 'right' && <span className={styles.iconRight}>{icon}</span>}
        </>
      )}
    </button>
  )
);
```

```css
/* Button.module.css - All values from Figma */
.button {
  display: inline-flex; align-items: center; justify-content: center;
  gap: var(--spacing-2); border: none; border-radius: var(--radius-md);
  font-family: var(--font-body); font-weight: var(--font-weight-medium);
  cursor: pointer; transition: all var(--transition-fast);
}
.button:focus-visible { outline: 2px solid var(--color-primary); outline-offset: 2px; }
.button:disabled { opacity: 0.5; cursor: not-allowed; }

/* Variants */
.primary { background: var(--color-primary); color: var(--color-text-inverse); }
.primary:hover:not(:disabled) { background: var(--color-primary-hover); }
.secondary { background: transparent; color: var(--color-primary); border: 1px solid var(--color-primary); }
.secondary:hover:not(:disabled) { background: var(--color-primary-subtle); }
.ghost { background: transparent; color: var(--color-text-primary); }
.ghost:hover:not(:disabled) { background: var(--color-background-muted); }
.danger { background: var(--color-error); color: var(--color-text-inverse); }

/* Sizes - from Figma */
.sm { min-height: 36px; padding: var(--spacing-2) var(--spacing-3); font-size: var(--font-size-sm); }
.md { min-height: 44px; padding: var(--spacing-2) var(--spacing-4); font-size: var(--font-size-sm); }
.lg { min-height: 52px; padding: var(--spacing-3) var(--spacing-5); font-size: var(--font-size-base); }

@media (min-width: 768px) {
  .sm { min-height: 32px; }
  .md { min-height: 40px; font-size: var(--font-size-base); }
  .lg { min-height: 48px; }
}

.fullWidth { width: 100%; }
.spinner { width: 16px; height: 16px; border: 2px solid currentColor; border-right-color: transparent; border-radius: 50%; animation: spin 0.6s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
```

## Input Atom

```typescript
// atoms/Input/Input.tsx
interface InputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'size'> {
  size?: 'sm' | 'md' | 'lg';
  error?: boolean;
  leftIcon?: ReactNode;
  rightElement?: ReactNode;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ size = 'md', error = false, leftIcon, rightElement, className, disabled, ...props }, ref) => (
    <div className={clsx(styles.wrapper, styles[size], error && styles.error, disabled && styles.disabled)}>
      {leftIcon && <span className={styles.leftIcon}>{leftIcon}</span>}
      <input ref={ref} disabled={disabled} className={styles.input} aria-invalid={error} {...props} />
      {rightElement && <span className={styles.rightElement}>{rightElement}</span>}
    </div>
  )
);
```

```css
/* Input.module.css */
.wrapper {
  display: flex; align-items: center; gap: var(--spacing-2);
  background: var(--color-surface); border: 1px solid var(--color-border);
  border-radius: var(--radius-md); transition: all var(--transition-fast);
}
.wrapper:focus-within { border-color: var(--color-primary); box-shadow: 0 0 0 3px var(--color-primary-subtle); }
.error { border-color: var(--color-error); }
.disabled { background: var(--color-background-muted); opacity: 0.7; }
.input { flex: 1; background: transparent; border: none; font-family: var(--font-body); color: var(--color-text-primary); }
.input:focus { outline: none; }
.input::placeholder { color: var(--color-text-muted); }

.sm { min-height: 36px; padding: 0 var(--spacing-3); font-size: var(--font-size-sm); }
.md { min-height: 44px; padding: 0 var(--spacing-3); font-size: var(--font-size-base); }
.lg { min-height: 52px; padding: 0 var(--spacing-4); font-size: var(--font-size-lg); }

@media (min-width: 768px) {
  .sm { min-height: 32px; }
  .md { min-height: 40px; }
  .lg { min-height: 48px; }
}
```

## FormField Molecule

```typescript
// molecules/FormField/FormField.tsx
interface FormFieldProps extends Omit<InputProps, 'id' | 'aria-describedby'> {
  label: string;
  errorMessage?: string;
  hint?: string;
  required?: boolean;
}

export const FormField = ({ label, errorMessage, hint, required = false, ...inputProps }: FormFieldProps) => {
  const id = useId();
  const errorId = `${id}-error`;
  const hintId = `${id}-hint`;
  const hasError = !!errorMessage;

  return (
    <div className={styles.field}>
      <label htmlFor={id} className={styles.label}>
        <Typography variant="label">{label}{required && <span className={styles.required}>*</span>}</Typography>
      </label>
      <Input id={id} error={hasError} aria-describedby={hasError ? errorId : hint ? hintId : undefined} {...inputProps} />
      {hasError && <Typography id={errorId} variant="caption" color="error">{errorMessage}</Typography>}
      {hint && !hasError && <Typography id={hintId} variant="caption" color="muted">{hint}</Typography>}
    </div>
  );
};
```

## Header Organism

```typescript
// organisms/Header/Header.tsx
interface HeaderProps {
  logo: ReactNode;
  navItems: { label: string; href: string; isActive?: boolean }[];
  onLogoClick?: () => void;
  actions?: ReactNode;
}

export const Header = ({ logo, navItems, onLogoClick, actions }: HeaderProps) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  return (
    <header className={styles.header}>
      <div className={styles.container}>
        <div className={styles.logo} onClick={onLogoClick}>{logo}</div>
        <nav className={styles.desktopNav}>
          <ul className={styles.navList}>
            {navItems.map(item => (
              <li key={item.href}>
                <a href={item.href} className={clsx(styles.navLink, item.isActive && styles.active)}>{item.label}</a>
              </li>
            ))}
          </ul>
        </nav>
        <div className={styles.actions}>{actions}</div>
        <Button label="Menu" variant="ghost" onClick={() => setMobileMenuOpen(true)} className={styles.mobileMenuButton} />
      </div>
    </header>
  );
};
```

## CSS Variables Template

```css
/* tokens/variables.css - ALL from Figma */
:root {
  /* Colors */
  --color-primary: #3b82f6;
  --color-primary-hover: #2563eb;
  --color-primary-subtle: #eff6ff;
  --color-surface: #ffffff;
  --color-background-muted: #f3f4f6;
  --color-text-primary: #111827;
  --color-text-secondary: #4b5563;
  --color-text-muted: #9ca3af;
  --color-text-inverse: #ffffff;
  --color-border: #e5e7eb;
  --color-error: #ef4444;
  --color-success: #22c55e;

  /* Typography */
  --font-body: 'Inter', sans-serif;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  --font-weight-medium: 500;

  /* Spacing */
  --spacing-1: 0.25rem;
  --spacing-2: 0.5rem;
  --spacing-3: 0.75rem;
  --spacing-4: 1rem;
  --spacing-5: 1.25rem;
  --spacing-6: 1.5rem;

  /* Effects */
  --radius-md: 0.375rem;
  --radius-lg: 0.5rem;
  --transition-fast: 150ms ease;
}
```
