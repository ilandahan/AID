# Code Documentation Standards

## MANDATORY: Every Code File Must Have Documentation

All code written by AID **MUST** include documentation at three levels:

---

## 1. File-Level Comment (TOP OF FILE)

Every file must start with a comment block explaining:
- **Purpose**: What this file does
- **Related files**: What other files it connects to
- **Author/Created**: When it was created (by AID)

### TypeScript/JavaScript Example
```typescript
/**
 * @file UserService.ts
 * @description Handles all user-related business logic including
 *              creation, authentication, and profile management.
 *
 * @related
 *   - ./UserRepository.ts - Data access layer
 *   - ./UserController.ts - HTTP endpoints that call this service
 *   - ../models/User.ts - User entity definition
 *   - ../validators/userValidators.ts - Input validation
 *
 * @created 2025-12-15 by AID
 */
```

### Python Example
```python
"""
File: user_service.py
Description: Handles all user-related business logic including
             creation, authentication, and profile management.

Related Files:
    - ./user_repository.py - Data access layer
    - ./user_controller.py - HTTP endpoints that call this service
    - ../models/user.py - User entity definition
    - ../validators/user_validators.py - Input validation

Created: 2025-12-15 by AID
"""
```

### React Component Example
```tsx
/**
 * @file Button.tsx
 * @description Primary button atom component. Part of the atomic design system.
 *              Supports multiple variants, sizes, and states.
 *
 * @related
 *   - ../tokens/colors.ts - Color definitions
 *   - ../tokens/spacing.ts - Spacing values
 *   - ./Button.test.tsx - Unit tests
 *   - ./Button.stories.tsx - Storybook documentation
 *
 * @created 2025-12-15 by AID
 */
```

---

## 2. Component/Class-Level Comment

Every component, class, or module must have a comment explaining:
- **What it does** (single sentence)
- **When to use it** (use cases)
- **Props/Parameters** (if applicable)

### React Component Example
```tsx
/**
 * Button - Primary interactive element for user actions.
 *
 * Use this component when:
 * - User needs to submit a form
 * - User needs to trigger an action
 * - User needs to navigate (use as link)
 *
 * @example
 * <Button variant="primary" onClick={handleClick}>
 *   Submit
 * </Button>
 *
 * @see ButtonProps for all available props
 */
export const Button: React.FC<ButtonProps> = ({ ... }) => {
```

### Class Example
```typescript
/**
 * UserService - Business logic layer for user operations.
 *
 * Responsibilities:
 * - User creation and validation
 * - Authentication and session management
 * - Profile updates and retrieval
 *
 * Dependencies:
 * - UserRepository for data persistence
 * - EmailService for notifications
 * - AuthProvider for token management
 */
export class UserService {
```

---

## 3. Function-Level Comment

Every function must have a comment explaining:
- **What it does** (one line)
- **Parameters** (with types and purpose)
- **Returns** (what and when)
- **Throws** (error conditions)
- **Related files** (if it calls/uses other files)

### Function Example
```typescript
/**
 * Creates a new user account with validation.
 *
 * @param data - User creation data
 * @param data.email - User's email address (must be unique)
 * @param data.name - User's display name
 * @param data.password - Plain text password (will be hashed)
 *
 * @returns The created user object with generated ID
 *
 * @throws {ValidationError} If email format is invalid
 * @throws {DuplicateError} If email already exists
 *
 * @related
 *   - ../validators/emailValidator.ts - Email validation logic
 *   - ../utils/passwordHash.ts - Password hashing
 *   - ./UserRepository.ts - Database persistence
 *
 * @example
 * const user = await userService.createUser({
 *   email: 'jane@example.com',
 *   name: 'Jane Doe',
 *   password: 'securePassword123'
 * });
 */
async createUser(data: CreateUserInput): Promise<User> {
```

### Simple Function Example
```typescript
/**
 * Validates email format using RFC 5322 standard.
 *
 * @param email - Email string to validate
 * @returns True if email format is valid
 *
 * @related ../constants/regex.ts - Email regex pattern
 */
function isValidEmail(email: string): boolean {
```

---

## Cross-File References

When a function or component interacts with another file, **ALWAYS** document the relationship:

### Pattern: @related Tag
```typescript
/**
 * @related
 *   - ./OtherFile.ts - Why it's related
 *   - ../services/ServiceName.ts - What we use from it
 */
```

### Pattern: Inline Reference
```typescript
// Uses validation from ../validators/emailValidator.ts
const isValid = validateEmail(email);

// Calls UserRepository.create() from ./UserRepository.ts
const user = await this.repository.create(userData);
```

---

## Code Review Checklist

When reviewing code, verify:

- [ ] **File comment** exists at top of every file
- [ ] **Component/Class comment** explains purpose and usage
- [ ] **Function comments** describe what, params, returns, throws
- [ ] **@related tags** document cross-file dependencies
- [ ] **Inline comments** explain non-obvious logic

---

## Examples by File Type

### Service File
```typescript
/**
 * @file AuthService.ts
 * @description Authentication and authorization service.
 *              Handles login, logout, token refresh, and permission checks.
 *
 * @related
 *   - ./UserService.ts - User lookup during auth
 *   - ./TokenService.ts - JWT token generation
 *   - ../repositories/SessionRepository.ts - Session persistence
 *   - ../middleware/authMiddleware.ts - Uses this service for route protection
 *
 * @created 2025-12-15 by AID
 */

import { UserService } from './UserService'; // User lookup
import { TokenService } from './TokenService'; // JWT operations
import { SessionRepository } from '../repositories/SessionRepository'; // Session storage

/**
 * AuthService - Handles all authentication operations.
 *
 * Use this service when:
 * - Authenticating users (login)
 * - Validating sessions/tokens
 * - Checking permissions
 */
export class AuthService {
  /**
   * Authenticates user with email and password.
   *
   * @param email - User's email address
   * @param password - Plain text password
   *
   * @returns Session object with access and refresh tokens
   *
   * @throws {AuthError} If credentials are invalid
   * @throws {AccountLocked} If too many failed attempts
   *
   * @related
   *   - ./UserService.ts - findByEmail() for user lookup
   *   - ./TokenService.ts - generateTokenPair() for JWT creation
   *   - ../utils/passwordHash.ts - comparePassword() for verification
   */
  async login(email: string, password: string): Promise<Session> {
    // Implementation...
  }
}
```

### React Component File
```tsx
/**
 * @file FormField.tsx
 * @description Form field molecule combining Label, Input, and ErrorMessage atoms.
 *              Provides consistent form field styling and validation display.
 *
 * @related
 *   - ../atoms/Label.tsx - Label atom
 *   - ../atoms/Input.tsx - Input atom
 *   - ../atoms/ErrorMessage.tsx - Error display atom
 *   - ../hooks/useFormField.ts - Form state management hook
 *   - ../tokens/spacing.ts - Spacing between elements
 *
 * @created 2025-12-15 by AID
 */

import { Label } from '../atoms/Label'; // Text label
import { Input } from '../atoms/Input'; // Input element
import { ErrorMessage } from '../atoms/ErrorMessage'; // Validation errors

/**
 * FormField - Molecule for form inputs with label and validation.
 *
 * Use this component when:
 * - Building forms with consistent styling
 * - Need label + input + error message together
 * - Want automatic validation display
 *
 * @example
 * <FormField
 *   label="Email"
 *   name="email"
 *   type="email"
 *   error={errors.email}
 * />
 */
export const FormField: React.FC<FormFieldProps> = ({
  label,
  name,
  type = 'text',
  error,
  ...inputProps
}) => {
  // Implementation...
};
```

---

## Quick Reference

| Level | Required Elements |
|-------|-------------------|
| **File** | @file, @description, @related, @created |
| **Component/Class** | Purpose, when to use, dependencies |
| **Function** | What, @param, @returns, @throws, @related |

**Remember**: If code references another file, document the relationship!
