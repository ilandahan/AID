# Best Practices Guide

This document outlines the best practices adopted in the AID (AI Development Methodology) project. Following these guidelines ensures code quality, maintainability, and consistency across the codebase.

---

## Table of Contents

1. [Code Organization](#code-organization)
2. [TypeScript Guidelines](#typescript-guidelines)
3. [React Component Patterns](#react-component-patterns)
4. [Testing Standards](#testing-standards)
5. [Accessibility (A11y)](#accessibility-a11y)
6. [Performance](#performance)
7. [Security](#security)
8. [Documentation](#documentation)
9. [Git Workflow](#git-workflow)
10. [Error Handling](#error-handling)

---

## Code Organization

### Directory Structure

```
src/
├── app/                    # Next.js App Router pages
├── components/             # Reusable UI components
│   ├── atoms/              # Basic building blocks (Button, Input, Typography)
│   ├── molecules/          # Combinations of atoms (FormField, Card)
│   ├── organisms/          # Complex components (Header, Footer, Forms)
│   ├── templates/          # Page layouts
│   └── pages/              # Complete page compositions
├── lib/                    # Utility functions and helpers
├── hooks/                  # Custom React hooks
├── services/               # API and external service integrations
├── types/                  # TypeScript type definitions
├── styles/                 # Global styles and theme
└── __tests__/              # Test files (mirror src structure)
```

### File Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Components | PascalCase | `Button.tsx`, `UserCard.tsx` |
| Hooks | camelCase with `use` prefix | `useAuth.ts`, `useForm.ts` |
| Utilities | camelCase | `formatDate.ts`, `validators.ts` |
| Types | PascalCase | `UserTypes.ts`, `ApiResponses.ts` |
| Tests | Same as source + `.test` | `Button.test.tsx` |
| Styles | Same as component + `.module.css` | `Button.module.css` |

### Component File Structure

Each component should be organized in its own folder:

```
Button/
├── Button.tsx              # Main component
├── Button.module.css       # Component styles
├── Button.test.tsx         # Unit tests
├── Button.stories.tsx      # Storybook stories (optional)
└── index.ts                # Public exports
```

---

## TypeScript Guidelines

### Strict Mode

Always enable strict mode in `tsconfig.json`:

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true
  }
}
```

### Type Definitions

#### Prefer Interfaces for Objects

```typescript
// ✅ Good - Use interface for object shapes
interface UserProps {
  name: string;
  email: string;
  role?: 'admin' | 'user';
}

// ✅ Good - Use type for unions and complex types
type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger';
type ApiResponse<T> = { data: T; error: null } | { data: null; error: string };
```

#### Export Types Explicitly

```typescript
// ✅ Good - Export for reuse
export interface ButtonProps {
  label: string;
  variant?: ButtonVariant;
}

// Component uses exported types
export const Button = (props: ButtonProps) => { ... };
```

#### Avoid `any` Type

```typescript
// ❌ Bad
function process(data: any) { ... }

// ✅ Good - Use generics or specific types
function process<T>(data: T) { ... }
function process(data: unknown) { ... }
```

### Utility Types

Leverage TypeScript utility types:

```typescript
// Pick specific properties
type UserSummary = Pick<User, 'id' | 'name'>;

// Make all properties optional
type PartialUser = Partial<User>;

// Make all properties required
type RequiredUser = Required<User>;

// Omit specific properties
type UserWithoutPassword = Omit<User, 'password'>;
```

---

## React Component Patterns

### Functional Components with TypeScript

```typescript
import { FC, ReactNode } from 'react';

interface CardProps {
  title: string;
  children: ReactNode;
  className?: string;
}

export const Card: FC<CardProps> = ({ title, children, className }) => {
  return (
    <div className={className}>
      <h2>{title}</h2>
      {children}
    </div>
  );
};

Card.displayName = 'Card';
```

### forwardRef for DOM Access

```typescript
import { forwardRef, ButtonHTMLAttributes } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary';
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'primary', children, ...props }, ref) => {
    return (
      <button ref={ref} {...props}>
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';
```

### Custom Hooks

```typescript
// ✅ Good - Encapsulate logic in custom hooks
function useToggle(initial = false) {
  const [value, setValue] = useState(initial);

  const toggle = useCallback(() => setValue(v => !v), []);
  const setTrue = useCallback(() => setValue(true), []);
  const setFalse = useCallback(() => setValue(false), []);

  return { value, toggle, setTrue, setFalse };
}
```

### Compound Components Pattern

```typescript
// For complex components with related sub-components
const Tabs = ({ children }: TabsProps) => { ... };
Tabs.List = TabsList;
Tabs.Tab = Tab;
Tabs.Panel = TabPanel;

// Usage
<Tabs>
  <Tabs.List>
    <Tabs.Tab>Tab 1</Tabs.Tab>
  </Tabs.List>
  <Tabs.Panel>Content 1</Tabs.Panel>
</Tabs>
```

---

## Testing Standards

### Test File Organization

Place tests alongside source files or in `__tests__` directory:

```
src/
├── components/
│   └── Button/
│       ├── Button.tsx
│       └── Button.test.tsx    # Co-located test
└── __tests__/
    └── integration/           # Integration tests
```

### Testing Principles

#### 1. Test Behavior, Not Implementation

```typescript
// ❌ Bad - Testing implementation details
expect(component.state.isOpen).toBe(true);

// ✅ Good - Testing behavior
expect(screen.getByRole('dialog')).toBeInTheDocument();
```

#### 2. Use Testing Library Queries

```typescript
// Priority order (best to worst)
screen.getByRole('button', { name: 'Submit' });  // Most accessible
screen.getByLabelText('Email');                   // Form inputs
screen.getByPlaceholderText('Search...');         // Fallback
screen.getByText('Hello World');                  // Text content
screen.getByTestId('custom-element');             // Last resort
```

#### 3. Test User Interactions

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

test('submits form on button click', async () => {
  const user = userEvent.setup();
  const onSubmit = jest.fn();

  render(<Form onSubmit={onSubmit} />);

  await user.type(screen.getByLabelText('Email'), 'test@example.com');
  await user.click(screen.getByRole('button', { name: 'Submit' }));

  expect(onSubmit).toHaveBeenCalledWith({ email: 'test@example.com' });
});
```

### Test Categories

#### Unit Tests

Test individual components in isolation:

```typescript
describe('Button', () => {
  it('renders with label', () => {
    render(<Button label="Click me" />);
    expect(screen.getByRole('button', { name: 'Click me' })).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const handleClick = jest.fn();
    render(<Button label="Click" onClick={handleClick} />);
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

#### Integration Tests

Test component interactions:

```typescript
describe('LoginForm', () => {
  it('displays error on invalid credentials', async () => {
    const user = userEvent.setup();
    render(<LoginForm />);

    await user.type(screen.getByLabelText('Email'), 'bad@email.com');
    await user.type(screen.getByLabelText('Password'), 'wrong');
    await user.click(screen.getByRole('button', { name: 'Sign in' }));

    expect(await screen.findByText('Invalid credentials')).toBeInTheDocument();
  });
});
```

### Coverage Thresholds

Maintain minimum coverage of 70%:

```javascript
// jest.config.js
coverageThreshold: {
  global: {
    branches: 70,
    functions: 70,
    lines: 70,
    statements: 70,
  },
},
```

---

## Accessibility (A11y)

### ARIA Attributes

```typescript
// ✅ Good - Proper ARIA usage
<button
  aria-label="Close dialog"
  aria-pressed={isPressed}
  aria-disabled={isLoading}
>
  <CloseIcon aria-hidden="true" />
</button>

// ✅ Good - Loading states
<button aria-busy={isLoading} disabled={isLoading}>
  {isLoading ? 'Loading...' : 'Submit'}
</button>
```

### Semantic HTML

```typescript
// ✅ Good - Use semantic elements
<nav aria-label="Main navigation">
  <ul>
    <li><a href="/">Home</a></li>
  </ul>
</nav>

<main>
  <article>
    <header><h1>Title</h1></header>
    <section>Content</section>
  </article>
</main>
```

### Keyboard Navigation

```typescript
// ✅ Good - Handle keyboard events
const handleKeyDown = (e: KeyboardEvent) => {
  switch (e.key) {
    case 'Enter':
    case ' ':
      e.preventDefault();
      onSelect();
      break;
    case 'Escape':
      onClose();
      break;
  }
};
```

### Focus Management

```typescript
// ✅ Good - Manage focus for dialogs
useEffect(() => {
  if (isOpen) {
    const previousFocus = document.activeElement;
    dialogRef.current?.focus();

    return () => {
      (previousFocus as HTMLElement)?.focus();
    };
  }
}, [isOpen]);
```

---

## Performance

### React Optimization

#### Memoization

```typescript
// Memoize expensive computations
const sortedItems = useMemo(() =>
  items.sort((a, b) => a.name.localeCompare(b.name)),
  [items]
);

// Memoize callbacks
const handleClick = useCallback(() => {
  onSelect(item.id);
}, [item.id, onSelect]);

// Memoize components
const ExpensiveComponent = memo(({ data }) => {
  // Expensive render
});
```

#### Code Splitting

```typescript
// Dynamic imports for large components
const HeavyEditor = dynamic(() => import('./HeavyEditor'), {
  loading: () => <Skeleton />,
  ssr: false,
});
```

### Image Optimization

```typescript
import Image from 'next/image';

// ✅ Good - Use Next.js Image component
<Image
  src="/hero.jpg"
  alt="Hero image"
  width={1200}
  height={600}
  priority // For above-the-fold images
  placeholder="blur"
/>
```

### Bundle Size

- Use tree-shakable imports: `import { Button } from '@/components'`
- Analyze bundle: `npm run build && npx @next/bundle-analyzer`
- Lazy load non-critical components

---

## Security

### Input Validation

```typescript
// ✅ Good - Validate and sanitize inputs
import { z } from 'zod';

const UserSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8).max(100),
  name: z.string().min(1).max(50),
});

function validateUser(data: unknown) {
  return UserSchema.parse(data);
}
```

### XSS Prevention

```typescript
// ✅ Good - React auto-escapes by default
<div>{userInput}</div>

// ⚠️ Dangerous - Only use when necessary and sanitized
<div dangerouslySetInnerHTML={{ __html: sanitizedHtml }} />
```

### Authentication

```typescript
// ✅ Good - Secure token handling
// - Store JWT in httpOnly cookies (not localStorage)
// - Use short expiration times
// - Implement refresh token rotation
// - Validate tokens on every request
```

### Environment Variables

```typescript
// ✅ Good - Never expose secrets to client
// Server-only
const API_SECRET = process.env.API_SECRET;

// Client-safe (prefixed with NEXT_PUBLIC_)
const PUBLIC_URL = process.env.NEXT_PUBLIC_APP_URL;
```

---

## Documentation

### Component Documentation

```typescript
/**
 * A customizable button component following atomic design principles.
 *
 * @example
 * ```tsx
 * <Button
 *   label="Submit"
 *   variant="primary"
 *   onClick={handleSubmit}
 * />
 * ```
 */
export interface ButtonProps {
  /** Button text content */
  label: string;
  /** Visual variant */
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  /** Size preset */
  size?: 'sm' | 'md' | 'lg';
  /** Show loading spinner */
  loading?: boolean;
}
```

### README Structure

Every significant module should have:

1. **Overview** - What it does
2. **Installation** - How to set it up
3. **Usage** - Code examples
4. **API** - Props/methods reference
5. **Contributing** - How to contribute

---

## Git Workflow

### Commit Messages

Follow conventional commits:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructure
- `test`: Adding tests
- `chore`: Maintenance

Examples:
```
feat(auth): add login form validation
fix(button): resolve disabled state styling
docs(readme): update installation instructions
test(typography): add unit tests for variants
```

### Branch Naming

```
feature/user-authentication
bugfix/button-disabled-state
hotfix/security-patch
docs/api-documentation
```

### Pull Request Checklist

- [ ] Tests pass
- [ ] No linting errors
- [ ] Documentation updated
- [ ] Reviewed for security
- [ ] Accessible (a11y)
- [ ] Mobile responsive

---

## Error Handling

### Error Boundaries

```typescript
import { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
}

class ErrorBoundary extends Component<Props, State> {
  state = { hasError: false };

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught:', error, errorInfo);
    // Log to error reporting service
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || <div>Something went wrong</div>;
    }
    return this.props.children;
  }
}
```

### API Error Handling

```typescript
// ✅ Good - Typed error handling
interface ApiError {
  code: string;
  message: string;
  details?: Record<string, string[]>;
}

async function fetchUser(id: string): Promise<User> {
  const response = await fetch(`/api/users/${id}`);

  if (!response.ok) {
    const error: ApiError = await response.json();
    throw new Error(error.message);
  }

  return response.json();
}

// Usage with error handling
try {
  const user = await fetchUser(id);
} catch (error) {
  if (error instanceof Error) {
    showNotification({ type: 'error', message: error.message });
  }
}
```

### Form Validation Errors

```typescript
// ✅ Good - Clear error messages
const validateForm = (data: FormData): Record<string, string> => {
  const errors: Record<string, string> = {};

  if (!data.email) {
    errors.email = 'Email is required';
  } else if (!isValidEmail(data.email)) {
    errors.email = 'Please enter a valid email address';
  }

  if (!data.password) {
    errors.password = 'Password is required';
  } else if (data.password.length < 8) {
    errors.password = 'Password must be at least 8 characters';
  }

  return errors;
};
```

---

## Quick Reference

### Do's ✅

- Use TypeScript strict mode
- Write tests before implementation (TDD)
- Use semantic HTML elements
- Handle loading and error states
- Document public APIs
- Use conventional commits
- Review for accessibility

### Don'ts ❌

- Use `any` type
- Skip error handling
- Ignore TypeScript errors
- Write tests after the fact
- Use `innerHTML` without sanitization
- Commit secrets or credentials
- Ignore accessibility warnings

---

## Resources

- [React Documentation](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Testing Library](https://testing-library.com)
- [Web Content Accessibility Guidelines (WCAG)](https://www.w3.org/WAI/WCAG21/quickref/)
- [Next.js Documentation](https://nextjs.org/docs)

---

*This document is maintained as part of the AID methodology. For updates, see the project repository.*
