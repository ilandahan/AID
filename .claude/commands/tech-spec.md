# /tech-spec Command

Generate a Technical Specification document from a PRD.

## Usage

```
/tech-spec [feature-name]
```

## What It Does

1. **Reads PRD**
   - Parses `docs/prd/PRD-<feature-name>.md`
   - Extracts requirements

2. **Generates Technical Spec**
   - Database schema (PostgreSQL)
   - TypeScript interfaces
   - API endpoints
   - Component architecture
   - Security considerations

3. **Saves Document**
   - Location: `docs/tech-specs/TECH-SPEC-<feature-name>.md`

## Technical Spec Structure

```markdown
# Technical Specification: [Feature Name]

## Overview
Technical approach summary

## Architecture
System architecture decisions

## Database Schema
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

## TypeScript Interfaces
```typescript
interface User {
  id: string;
  email: string;
  createdAt: Date;
}
```

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/users | Create user |
| GET | /api/users/:id | Get user |

## Component Architecture
- Atoms: Button, Input, Avatar
- Molecules: UserCard, LoginForm
- Organisms: UserProfile, AuthSection
- Templates: AuthLayout
- Pages: LoginPage, RegisterPage

## Security Considerations
- Authentication method
- Authorization rules
- Data validation

## Performance Considerations
- Caching strategy
- Database indexes
- Lazy loading

## Testing Strategy
- Unit tests
- Integration tests
- E2E tests

## Migration Plan
Database migration steps
```

## Skill Used

This command uses the **system-architect** skill:
- SaaS architecture patterns
- Multi-tenancy considerations
- Scalability patterns
- Security best practices

## Examples

```bash
# Generate tech spec from existing PRD
/tech-spec user-authentication

# Interactive mode
/tech-spec
```

## After Tech Spec Creation

1. Review architecture decisions
2. Validate with team
3. Move to Phase 4: Jira Breakdown
   ```
   /jira-breakdown
   ```

## Tips

- Reference the PRD for requirements
- Use TypeScript interfaces from the start
- Plan database indexes early
- Consider API versioning
- Document security from day one
