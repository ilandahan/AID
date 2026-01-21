# Data Modeling Guide

## Entity Definition Template

```markdown
## Entity: [EntityName]

### Description
[What this entity represents]

### Fields
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto | Unique identifier |
| createdAt | DateTime | NOT NULL, auto | Creation timestamp |
| updatedAt | DateTime | NOT NULL, auto | Last update timestamp |
| [field] | [type] | [constraints] | [description] |

### Indexes
| Name | Fields | Type | Purpose |
|------|--------|------|---------|
| idx_[name] | [fields] | B-tree/Hash | [why] |

### Relationships
| Entity | Type | FK | Description |
|--------|------|----|----|
| [Entity] | 1:N | [fk_field] | [description] |
```

## Common Data Types

### IDs
```typescript
// Use UUIDs for distributed systems
id: UUID  // "550e8400-e29b-41d4-a716-446655440000"

// Use auto-increment for simple cases
id: SERIAL  // 1, 2, 3...

// Use prefixed IDs for readability
id: string  // "user_abc123", "order_xyz789"
```

### Timestamps
```typescript
// Always include
createdAt: DateTime  // When created
updatedAt: DateTime  // Last modified

// Optional
deletedAt: DateTime  // Soft delete
expiresAt: DateTime  // TTL
```

### Status/State
```typescript
// Enum for finite states
status: enum('draft', 'published', 'archived')

// String for extensible states
status: string  // With validation
```

### Money
```typescript
// Store as smallest unit (cents)
amountCents: integer  // 1999 = $19.99
currency: string      // "USD", "EUR"

// Never use float for money
```

## Relationship Patterns

### One-to-Many
```sql
-- Parent
CREATE TABLE users (
  id UUID PRIMARY KEY,
  name VARCHAR(100)
);

-- Child with foreign key
CREATE TABLE orders (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id),
  total_cents INTEGER
);
```

### Many-to-Many
```sql
-- Junction table
CREATE TABLE user_roles (
  user_id UUID REFERENCES users(id),
  role_id UUID REFERENCES roles(id),
  assigned_at TIMESTAMP DEFAULT NOW(),
  PRIMARY KEY (user_id, role_id)
);
```

### Self-Referential
```sql
-- Hierarchy (e.g., categories, org chart)
CREATE TABLE categories (
  id UUID PRIMARY KEY,
  name VARCHAR(100),
  parent_id UUID REFERENCES categories(id)
);
```

## Indexing Strategy

### When to Index
- Primary keys (automatic)
- Foreign keys (for JOINs)
- Fields used in WHERE clauses
- Fields used in ORDER BY
- Fields with high selectivity

### When NOT to Index
- Low cardinality fields (boolean)
- Frequently updated fields
- Small tables
- Fields rarely queried

### Index Types
```sql
-- B-tree (default, most cases)
CREATE INDEX idx_users_email ON users(email);

-- Hash (equality only)
CREATE INDEX idx_users_id USING HASH ON users(id);

-- Composite (multi-column)
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- Partial (filtered)
CREATE INDEX idx_active_users ON users(email) WHERE status = 'active';

-- Unique
CREATE UNIQUE INDEX idx_users_email_unique ON users(email);
```

## Normalization Guidelines

### First Normal Form (1NF)
- No repeating groups
- Each field contains atomic values

```sql
-- Bad
CREATE TABLE orders (
  id UUID,
  items TEXT  -- "item1,item2,item3"
);

-- Good
CREATE TABLE orders (id UUID);
CREATE TABLE order_items (
  order_id UUID,
  item_id UUID
);
```

### Second Normal Form (2NF)
- 1NF + no partial dependencies

### Third Normal Form (3NF)
- 2NF + no transitive dependencies

### When to Denormalize
- Read-heavy workloads
- Complex aggregations
- Caching/materialized views
- Always document trade-off

## Schema Migration Template

```sql
-- Migration: [YYYYMMDDHHMMSS]_[description].sql

-- Up
BEGIN;

ALTER TABLE users ADD COLUMN phone VARCHAR(20);
CREATE INDEX idx_users_phone ON users(phone);

COMMIT;

-- Down
BEGIN;

DROP INDEX idx_users_phone;
ALTER TABLE users DROP COLUMN phone;

COMMIT;
```

## Data Validation Rules

```typescript
interface ValidationRules {
  // String
  email: { format: 'email', maxLength: 255 };
  name: { minLength: 2, maxLength: 100 };
  slug: { pattern: /^[a-z0-9-]+$/ };

  // Number
  age: { min: 0, max: 150 };
  price: { min: 0, precision: 2 };

  // Enum
  status: { enum: ['draft', 'published', 'archived'] };

  // Date
  birthDate: { before: 'now', after: '1900-01-01' };
}
```
