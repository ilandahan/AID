# Component Templates

Production-ready templates for common design system components.

## ⚠️ CRITICAL: These Are Templates, Not Final Values

```
┌─────────────────────────────────────────────────────────────────────┐
│  🚨 BEFORE USING THESE TEMPLATES:                                    │
│                                                                      │
│  1. Extract specs from Figma using MCP                              │
│  2. Replace ALL placeholder values with EXACT Figma values          │
│  3. Add @figma JSDoc tag with actual Figma link                     │
│  4. Document extraction date                                         │
│                                                                      │
│  These templates show STRUCTURE and PATTERNS.                       │
│  The actual VALUES must come from YOUR Figma design system.         │
└─────────────────────────────────────────────────────────────────────┘
```

**Related documents:**
- `figma-design-fidelity.md` - Complete extraction workflow
- `design-deviation-rules.md` - Zero deviation policy
- `figma-mcp-integration.md` - MCP commands for extraction

## Complete Atom: Button

```typescript
/**
 * Button Atom
 *
 * @figma [REPLACE: https://figma.com/file/xxx/Design-System?node-id=button]
 * @extracted [REPLACE: YYYY-MM-DD]
 * @designer [REPLACE: Designer Name]
 *
 * ⚠️ Replace ALL values below with EXACT values from Figma extraction
 */

// atoms/Button/Button.tsx
import { forwardRef, ButtonHTMLAttributes, ReactNode } from 'react';
import clsx from 'clsx';
import styles from './Button.module.css';

type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger';
type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps extends Omit<ButtonHTMLAttributes<HTMLButtonElement>, 'children'> {
  /** Button text content */
  label: string;
  /** Visual variant */
  variant?: ButtonVariant;
  /** Size preset */
  size?: ButtonSize;
  /** Icon element to display */
  icon?: ReactNode;
  /** Icon position relative to label */
  iconPosition?: 'left' | 'right';
  /** Show loading spinner */
  loading?: boolean;
  /** Full width button */
  fullWidth?: boolean;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      label,
      variant = 'primary',
      size = 'md',
      icon,
      iconPosition = 'left',
      loading = false,
      fullWidth = false,
      disabled,
      className,
      ...props
    },
    ref
  ) => {
    const isDisabled = disabled || loading;

    return (
      <button
        ref={ref}
        disabled={isDisabled}
        className={clsx(
          styles.button,
          styles[variant],
          styles[size],
          fullWidth && styles.fullWidth,
          loading && styles.loading,
          className
        )}
        aria-busy={loading}
        aria-disabled={isDisabled}
        {...props}
      >
        {loading ? (
          <span className={styles.spinner} aria-hidden="true" />
        ) : (
          <>
            {icon && iconPosition === 'left' && (
              <span className={styles.iconLeft} aria-hidden="true">
                {icon}
              </span>
            )}
            <span className={styles.label}>{label}</span>
            {icon && iconPosition === 'right' && (
              <span className={styles.iconRight} aria-hidden="true">
                {icon}
              </span>
            )}
          </>
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';
export default Button;
```

```css
/**
 * Button Styles
 *
 * Source: Figma Design System
 * Frame: Components/Button
 * Extracted: [REPLACE: YYYY-MM-DD]
 *
 * ⚠️ ALL values must be EXACT from Figma - DO NOT MODIFY
 * Replace placeholder values with your Figma values
 */

/* atoms/Button/Button.module.css */
.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
  border: none;
  border-radius: var(--radius-md);
  font-family: var(--font-body);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--transition-fast);
  text-decoration: none;
  white-space: nowrap;
}

.button:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Variants */
.primary {
  background: var(--color-primary);
  color: var(--color-text-inverse);
}
.primary:hover:not(:disabled) {
  background: var(--color-primary-hover);
}
.primary:active:not(:disabled) {
  background: var(--color-primary-active);
}

.secondary {
  background: transparent;
  color: var(--color-primary);
  border: 1px solid var(--color-primary);
}
.secondary:hover:not(:disabled) {
  background: var(--color-primary-subtle);
}

.ghost {
  background: transparent;
  color: var(--color-text-primary);
}
.ghost:hover:not(:disabled) {
  background: var(--color-background-muted);
}

.danger {
  background: var(--color-error);
  color: var(--color-text-inverse);
}
.danger:hover:not(:disabled) {
  background: var(--color-error-hover);
}

/* Sizes - Mobile first */
/* ⚠️ ALL values from Figma - check each size variant in Figma */
.sm {
  min-height: 36px;                          /* From Figma: Button/Small */
  padding: var(--spacing-2) var(--spacing-3); /* From Figma */
  font-size: var(--font-size-sm);             /* From Figma */
}

.md {
  min-height: 44px;                          /* From Figma: Button/Medium */
  padding: var(--spacing-2) var(--spacing-4); /* From Figma */
  font-size: var(--font-size-sm);             /* From Figma */
}

.lg {
  min-height: 52px;                          /* From Figma: Button/Large */
  padding: var(--spacing-3) var(--spacing-5); /* From Figma */
  font-size: var(--font-size-base);           /* From Figma */
}

/* Responsive: Check Figma Desktop frame for these values */
@media (min-width: 768px) {
  .sm {
    min-height: 32px;  /* From Figma Desktop: Button/Small */
  }
  .md {
    min-height: 40px;  /* From Figma Desktop: Button/Medium */
    font-size: var(--font-size-base);
  }
  .lg {
    min-height: 48px;  /* From Figma Desktop: Button/Large */
  }
}

/* Full width */
.fullWidth {
  width: 100%;
}

/* Loading */
.loading {
  position: relative;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Icons */
.iconLeft,
.iconRight {
  display: flex;
  width: 1em;
  height: 1em;
}
```

```typescript
// atoms/Button/index.ts
export { Button, type ButtonProps } from './Button';
export default Button;
```

---

## Complete Atom: Input

```typescript
/**
 * Input Atom
 *
 * @figma [REPLACE: https://figma.com/file/xxx/Design-System?node-id=input]
 * @extracted [REPLACE: YYYY-MM-DD]
 *
 * ⚠️ Replace ALL values below with EXACT values from Figma extraction
 */

// atoms/Input/Input.tsx
import { forwardRef, InputHTMLAttributes, ReactNode } from 'react';
import clsx from 'clsx';
import styles from './Input.module.css';

type InputSize = 'sm' | 'md' | 'lg';

interface InputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'size'> {
  /** Visual size */
  size?: InputSize;
  /** Error state */
  error?: boolean;
  /** Icon on the left */
  leftIcon?: ReactNode;
  /** Icon or element on the right */
  rightElement?: ReactNode;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      size = 'md',
      error = false,
      leftIcon,
      rightElement,
      className,
      disabled,
      ...props
    },
    ref
  ) => {
    return (
      <div
        className={clsx(
          styles.wrapper,
          styles[size],
          error && styles.error,
          disabled && styles.disabled,
          className
        )}
      >
        {leftIcon && (
          <span className={styles.leftIcon} aria-hidden="true">
            {leftIcon}
          </span>
        )}
        <input
          ref={ref}
          disabled={disabled}
          className={styles.input}
          aria-invalid={error}
          {...props}
        />
        {rightElement && (
          <span className={styles.rightElement}>{rightElement}</span>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
export default Input;
```

```css
/**
 * Input Styles
 *
 * Source: Figma Design System
 * Frame: Components/Input
 * Extracted: [REPLACE: YYYY-MM-DD]
 *
 * ⚠️ ALL values must be EXACT from Figma - DO NOT MODIFY
 */

/* atoms/Input/Input.module.css */
.wrapper {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.wrapper:focus-within {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-subtle);
}

.error {
  border-color: var(--color-error);
}
.error:focus-within {
  box-shadow: 0 0 0 3px var(--color-error-subtle);
}

.disabled {
  background: var(--color-background-muted);
  opacity: 0.7;
  cursor: not-allowed;
}

.input {
  flex: 1;
  width: 100%;
  background: transparent;
  border: none;
  font-family: var(--font-body);
  color: var(--color-text-primary);
}

.input:focus {
  outline: none;
}

.input::placeholder {
  color: var(--color-text-muted);
}

/* Sizes */
.sm {
  min-height: 36px;
  padding: 0 var(--spacing-3);
  font-size: var(--font-size-sm);
}

.md {
  min-height: 44px;
  padding: 0 var(--spacing-3);
  font-size: var(--font-size-base);
}

.lg {
  min-height: 52px;
  padding: 0 var(--spacing-4);
  font-size: var(--font-size-lg);
}

@media (min-width: 768px) {
  .sm { min-height: 32px; }
  .md { min-height: 40px; }
  .lg { min-height: 48px; }
}

.leftIcon,
.rightElement {
  display: flex;
  flex-shrink: 0;
  color: var(--color-text-secondary);
}

.leftIcon {
  margin-left: var(--spacing-1);
}

.rightElement {
  margin-right: var(--spacing-1);
}
```

---

## Complete Molecule: FormField

```typescript
/**
 * FormField Molecule
 *
 * @figma [REPLACE: https://figma.com/file/xxx/Design-System?node-id=formfield]
 * @extracted [REPLACE: YYYY-MM-DD]
 *
 * Composes: Typography (label) + Input + Typography (error/hint)
 * ⚠️ Replace ALL spacing values with EXACT values from Figma
 */

// molecules/FormField/FormField.tsx
import { ReactNode, useId } from 'react';
import clsx from 'clsx';
import { Typography } from '@/atoms/Typography';
import { Input, InputProps } from '@/atoms/Input';
import styles from './FormField.module.css';

interface FormFieldProps extends Omit<InputProps, 'id' | 'aria-describedby'> {
  /** Field label */
  label: string;
  /** Error message */
  errorMessage?: string;
  /** Help text */
  hint?: string;
  /** Required field indicator */
  required?: boolean;
}

export const FormField = ({
  label,
  errorMessage,
  hint,
  required = false,
  className,
  ...inputProps
}: FormFieldProps) => {
  const id = useId();
  const errorId = `${id}-error`;
  const hintId = `${id}-hint`;
  
  const hasError = !!errorMessage;
  const describedBy = hasError ? errorId : hint ? hintId : undefined;

  return (
    <div className={clsx(styles.field, className)}>
      <label htmlFor={id} className={styles.label}>
        <Typography variant="label" color="primary">
          {label}
          {required && <span className={styles.required} aria-hidden="true">*</span>}
        </Typography>
      </label>

      <Input
        id={id}
        error={hasError}
        aria-describedby={describedBy}
        aria-required={required}
        {...inputProps}
      />

      {hasError && (
        <Typography
          id={errorId}
          variant="caption"
          color="error"
          className={styles.message}
          role="alert"
        >
          {errorMessage}
        </Typography>
      )}

      {hint && !hasError && (
        <Typography
          id={hintId}
          variant="caption"
          color="muted"
          className={styles.message}
        >
          {hint}
        </Typography>
      )}
    </div>
  );
};

export default FormField;
```

```css
/**
 * FormField Styles
 *
 * Source: Figma Design System
 * Frame: Components/FormField
 * Extracted: [REPLACE: YYYY-MM-DD]
 *
 * ⚠️ ALL gap/margin values from Figma - DO NOT MODIFY
 */

/* molecules/FormField/FormField.module.css */
.field {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-1);  /* From Figma: gap between label and input */
}

.label {
  display: flex;
  align-items: center;
  gap: var(--spacing-1);  /* From Figma: gap between label text and asterisk */
}

.required {
  color: var(--color-error);  /* From Figma: required indicator color */
}

.message {
  margin-top: var(--spacing-1);  /* From Figma: gap between input and message */
}
```

---

## Complete Organism: Header

```typescript
/**
 * Header Organism
 *
 * @figma [REPLACE: https://figma.com/file/xxx/Design-System?node-id=header]
 * @extracted [REPLACE: YYYY-MM-DD]
 *
 * Composes: Logo + NavItems + Actions + MobileMenu
 * ⚠️ Check Figma for Desktop, Tablet, Mobile variations
 * ⚠️ Replace ALL height, padding, breakpoint values with EXACT Figma values
 */

// organisms/Header/Header.tsx
import { useState, ReactNode } from 'react';
import clsx from 'clsx';
import { Button } from '@/atoms/Button';
import { Typography } from '@/atoms/Typography';
import styles from './Header.module.css';

interface NavItem {
  label: string;
  href: string;
  isActive?: boolean;
}

interface HeaderProps {
  /** Logo element */
  logo: ReactNode;
  /** Navigation items */
  navItems: NavItem[];
  /** Logo click handler */
  onLogoClick?: () => void;
  /** Right-side action buttons */
  actions?: ReactNode;
}

export const Header = ({
  logo,
  navItems,
  onLogoClick,
  actions,
}: HeaderProps) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className={styles.header}>
      <div className={styles.container}>
        {/* Logo */}
        <div 
          className={styles.logo}
          onClick={onLogoClick}
          role={onLogoClick ? 'button' : undefined}
          tabIndex={onLogoClick ? 0 : undefined}
        >
          {logo}
        </div>

        {/* Desktop Navigation */}
        <nav className={styles.desktopNav} aria-label="Main navigation">
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

        {/* Actions */}
        <div className={styles.actions}>
          {actions}
        </div>

        {/* Mobile Menu Button */}
        <Button
          label="Menu"
          variant="ghost"
          size="sm"
          onClick={() => setMobileMenuOpen(true)}
          className={styles.mobileMenuButton}
          aria-expanded={mobileMenuOpen}
          aria-controls="mobile-menu"
        />
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div 
          id="mobile-menu"
          className={styles.mobileMenu}
          role="dialog"
          aria-modal="true"
          aria-label="Mobile navigation"
        >
          <div className={styles.mobileMenuHeader}>
            {logo}
            <Button
              label="Close"
              variant="ghost"
              size="sm"
              onClick={() => setMobileMenuOpen(false)}
            />
          </div>
          <nav>
            <ul className={styles.mobileNavList}>
              {navItems.map((item) => (
                <li key={item.href}>
                  <a
                    href={item.href}
                    className={clsx(styles.mobileNavLink, item.isActive && styles.active)}
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    {item.label}
                  </a>
                </li>
              ))}
            </ul>
          </nav>
          <div className={styles.mobileActions}>{actions}</div>
        </div>
      )}
    </header>
  );
};

export default Header;
```

```css
/**
 * Header Styles
 *
 * Source: Figma Design System
 * Frame: Components/Header
 * Extracted: [REPLACE: YYYY-MM-DD]
 *
 * ⚠️ ALL values from Figma - check Desktop, Tablet, Mobile frames
 */

/* organisms/Header/Header.module.css */
.header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--color-surface);        /* From Figma */
  border-bottom: 1px solid var(--color-border); /* From Figma */
}

.container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1280px;
  margin: 0 auto;
  padding: var(--spacing-3) var(--spacing-4);
}

@media (min-width: 768px) {
  .container {
    padding: var(--spacing-4) var(--spacing-6);
  }
}

.logo {
  cursor: pointer;
}

/* Desktop Nav - Hidden on mobile */
.desktopNav {
  display: none;
}

@media (min-width: 768px) {
  .desktopNav {
    display: flex;
    flex: 1;
    justify-content: center;
  }
}

.navList {
  display: flex;
  gap: var(--spacing-1);
  list-style: none;
  margin: 0;
  padding: 0;
}

.navLink {
  display: block;
  padding: var(--spacing-2) var(--spacing-3);
  color: var(--color-text-secondary);
  text-decoration: none;
  font-weight: var(--font-weight-medium);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.navLink:hover {
  color: var(--color-text-primary);
  background: var(--color-background-subtle);
}

.navLink.active {
  color: var(--color-primary);
  background: var(--color-primary-subtle);
}

.actions {
  display: none;
}

@media (min-width: 768px) {
  .actions {
    display: flex;
    gap: var(--spacing-3);
  }
}

/* Mobile Menu Button - Visible only on mobile */
.mobileMenuButton {
  display: flex;
}

@media (min-width: 768px) {
  .mobileMenuButton {
    display: none;
  }
}

/* Mobile Menu */
.mobileMenu {
  position: fixed;
  inset: 0;
  z-index: 200;
  background: var(--color-surface);
  display: flex;
  flex-direction: column;
  padding: var(--spacing-4);
}

.mobileMenuHeader {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-6);
}

.mobileNavList {
  list-style: none;
  margin: 0;
  padding: 0;
}

.mobileNavLink {
  display: block;
  padding: var(--spacing-4);
  color: var(--color-text-primary);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-medium);
  text-decoration: none;
  border-bottom: 1px solid var(--color-border);
}

.mobileNavLink.active {
  color: var(--color-primary);
}

.mobileActions {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}
```

---

## CSS Variables Template

```css
/**
 * Design Tokens - CSS Variables
 *
 * Source: Figma Style Guide
 * Extracted: [REPLACE: YYYY-MM-DD]
 *
 * ⚠️ CRITICAL: ALL values MUST be extracted from Figma
 * DO NOT use these placeholder values - replace with your Figma values
 *
 * To extract:
 * 1. Open Figma Style Guide
 * 2. Use MCP: figma.get_local_variables(file_key)
 * 3. Replace all values below with EXACT Figma values
 */

/* tokens/variables.css */
:root {
  /* ==================== COLORS ==================== */
  /* Primitives */
  --color-white: #ffffff;
  --color-black: #000000;
  
  --color-gray-50: #f9fafb;
  --color-gray-100: #f3f4f6;
  --color-gray-200: #e5e7eb;
  --color-gray-300: #d1d5db;
  --color-gray-400: #9ca3af;
  --color-gray-500: #6b7280;
  --color-gray-600: #4b5563;
  --color-gray-700: #374151;
  --color-gray-800: #1f2937;
  --color-gray-900: #111827;
  
  --color-blue-50: #eff6ff;
  --color-blue-100: #dbeafe;
  --color-blue-500: #3b82f6;
  --color-blue-600: #2563eb;
  --color-blue-700: #1d4ed8;
  
  --color-red-50: #fef2f2;
  --color-red-500: #ef4444;
  --color-red-600: #dc2626;
  
  --color-green-50: #f0fdf4;
  --color-green-500: #22c55e;
  --color-green-600: #16a34a;
  
  /* Semantic */
  --color-primary: var(--color-blue-500);
  --color-primary-hover: var(--color-blue-600);
  --color-primary-active: var(--color-blue-700);
  --color-primary-subtle: var(--color-blue-50);
  
  --color-surface: var(--color-white);
  --color-background-subtle: var(--color-gray-50);
  --color-background-muted: var(--color-gray-100);
  
  --color-text-primary: var(--color-gray-900);
  --color-text-secondary: var(--color-gray-600);
  --color-text-muted: var(--color-gray-400);
  --color-text-inverse: var(--color-white);
  
  --color-border: var(--color-gray-200);
  --color-border-strong: var(--color-gray-300);
  
  --color-error: var(--color-red-500);
  --color-error-hover: var(--color-red-600);
  --color-error-subtle: var(--color-red-50);
  
  --color-success: var(--color-green-500);
  --color-success-subtle: var(--color-green-50);
  
  /* ==================== TYPOGRAPHY ==================== */
  --font-body: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-heading: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
  
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.25rem;
  --font-size-2xl: 1.5rem;
  --font-size-3xl: 1.875rem;
  --font-size-4xl: 2.25rem;
  
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
  
  --line-height-none: 1;
  --line-height-tight: 1.25;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.625;
  
  /* ==================== SPACING ==================== */
  --spacing-0: 0;
  --spacing-1: 0.25rem;
  --spacing-2: 0.5rem;
  --spacing-3: 0.75rem;
  --spacing-4: 1rem;
  --spacing-5: 1.25rem;
  --spacing-6: 1.5rem;
  --spacing-8: 2rem;
  --spacing-10: 2.5rem;
  --spacing-12: 3rem;
  --spacing-16: 4rem;
  
  /* ==================== BREAKPOINTS ==================== */
  --breakpoint-xs: 320px;   /* Small mobile (iPhone SE) */
  --breakpoint-sm: 480px;   /* Mobile landscape */
  --breakpoint-md: 768px;   /* Tablet portrait (iPad) */
  --breakpoint-lg: 1024px;  /* Tablet landscape / Small laptop */
  --breakpoint-xl: 1280px;  /* Desktop */
  --breakpoint-2xl: 1440px; /* Large desktop */
  --breakpoint-3xl: 1920px; /* Full HD / Wide screens */
  
  /* ==================== EFFECTS ==================== */
  --radius-sm: 0.125rem;
  --radius-md: 0.375rem;
  --radius-lg: 0.5rem;
  --radius-xl: 0.75rem;
  --radius-full: 9999px;
  
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
  
  --transition-fast: 150ms ease;
  --transition-base: 200ms ease;
  --transition-slow: 300ms ease;
}
```