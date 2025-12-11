# /tech-spec Command

Transform a PRD into a comprehensive Technical Specification.

## Usage

```
/tech-spec [feature-name]
```

## What It Does

1. **Reads PRD** - Finds latest `docs/prd/YYYY-MM-DD-[feature-name].md`
2. **Transforms Content** - Converts requirements into technical design
3. **Saves Document** - Location: `docs/tech-spec/YYYY-MM-DD-[feature-name].md`

---

## PRD to Tech Spec Transformation

| PRD Section | Tech Spec Output |
|-------------|------------------|
| User Roles | RBAC Data Models, Permission Matrix |
| Features | API Endpoints, Service Layer Design |
| Data Requirements | Database Schema, Migrations |
| Workflows | State Machines, Event Flows |
| UI Requirements | Component Specifications |
| Integrations | API Contracts, Sequence Diagrams |

---

## 7-Shot Prompt Structure

### 1. ROLE

```
You are a Senior Tech Lead / Software Architect with 10+ years of experience.

Your expertise:
• Backend system design (Node.js, Python, Go)
• Frontend architecture (React, Vue, Angular)
• Database design (PostgreSQL, MongoDB, Redis)
• API design (REST, GraphQL)
• Security & Authentication patterns
• Performance optimization
• Design patterns and best practices

You write for: Backend Developers, Frontend Developers, DevOps Engineers.
The code you write is production-ready, NOT pseudo-code.
```

### 2. TASK

```
Take the [SECTION_NAME] from the PRD and transform it into a detailed technical specification.

The specification must include:
• TypeScript Interfaces for all Data Models
• SQL Schema with constraints and indexes
• Complete API Endpoints with request/response schemas
• Service layer code examples
• Security patterns (auth/authz)
• Testing requirements

A developer should be able to take this document and start development immediately.
```

### 3. CONTEXT

```
Tech Stack:
• Language: [TypeScript / Python / Go]
• Backend Framework: [Express / NestJS / FastAPI / Gin]
• Database: [PostgreSQL / MongoDB / MySQL]
• Cache: [Redis / Memcached]
• Auth: [JWT / OAuth2 / Session]
• Frontend: [React / Vue / Angular]

Project Conventions:
• Naming: [camelCase / snake_case / PascalCase]
• File structure: [feature-based / layer-based]
• Error handling: [pattern]
• Logging: [logger]

Existing Components:
• [List of existing services/modules]
• [Patterns already in use]

PRD Reference:
• Section: [Section number]
• Link: [Path to PRD]
```

### 4. REASONING

```
Approach the specification in these steps:

Step 1 - Data First:
   Start by defining the Data Models.
   They are the foundation for everything else - API, Services, UI.

Step 2 - Schema Design:
   Translate Models to Database Schema.
   Consider: indexes, constraints, relationships.

Step 3 - API Design:
   Define endpoints following REST conventions.
   Consider: versioning, pagination, filtering.

Step 4 - Security Layer:
   Add authentication to every endpoint.
   Add authorization (permissions) to every operation.

Step 5 - Implementation Patterns:
   Provide code examples for each major pattern.
   Code must be runnable, not pseudo-code.

Step 6 - Testing Strategy:
   Define what needs to be tested.
   Provide detailed test cases.
```

### 5. OUTPUT FORMAT

````markdown
# Technical Specification
## [Module/Feature Name]

| Field | Value |
|-------|-------|
| PRD Reference | [Section X.X] |
| Version | 1.0 |
| Status | Draft |
| Author | [Name] |

---

## 1. Overview

### 1.1 Scope
[What this specification covers]

### 1.2 Dependencies
| Dependency | Type | Reason |
|------------|------|--------|
| [Service X] | Internal | [why] |
| [Library Y] | External | [why] |

### 1.3 Out of Scope
- [What is NOT covered]

---

## 2. Data Models

### 2.1 TypeScript Interfaces

```typescript
/**
 * [Entity description]
 * @see PRD Section X.X
 */
interface EntityName {
  /** Primary identifier (UUID v4) */
  id: string;

  /** [Field description] - max X characters */
  fieldName: string;

  /** Foreign key to RelatedEntity */
  relatedId: string;

  /** Current status */
  status: EntityStatus;

  /** ISO 8601 timestamp */
  createdAt: string;

  /** ISO 8601 timestamp */
  updatedAt: string;
}

/** Possible statuses for Entity */
enum EntityStatus {
  DRAFT = 'draft',
  ACTIVE = 'active',
  ARCHIVED = 'archived'
}

/** DTO for creating Entity */
interface CreateEntityDTO {
  fieldName: string;
  relatedId: string;
}

/** DTO for updating Entity */
interface UpdateEntityDTO {
  fieldName?: string;
  status?: EntityStatus;
}
```

### 2.2 Entity Relationship Diagram

```
┌──────────────┐       ┌──────────────┐
│   Entity A   │──1:N──│   Entity B   │
├──────────────┤       ├──────────────┤
│ id (PK)      │       │ id (PK)      │
│ name         │       │ entityA_id   │──FK
│ created_at   │       │ value        │
└──────────────┘       └──────────────┘
```

---

## 3. Database Schema

### 3.1 Tables

```sql
-- =============================================
-- Table: entities
-- Description: [What this table stores]
-- PRD Reference: Section X.X
-- =============================================

CREATE TABLE entities (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Core Fields
    field_name VARCHAR(100) NOT NULL,
    description TEXT,

    -- Foreign Keys
    related_id UUID NOT NULL REFERENCES related_table(id)
        ON DELETE CASCADE,
    created_by UUID NOT NULL REFERENCES users(id),

    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'draft'
        CHECK (status IN ('draft', 'active', 'archived')),

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT uq_entity_field UNIQUE (field_name, related_id)
);

-- Indexes
CREATE INDEX idx_entities_related ON entities(related_id);
CREATE INDEX idx_entities_status ON entities(status)
    WHERE status != 'archived';
CREATE INDEX idx_entities_created ON entities(created_at DESC);

-- Updated timestamp trigger
CREATE TRIGGER trg_entities_updated
    BEFORE UPDATE ON entities
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();
```

### 3.2 Seed Data

```sql
-- Required initial data
INSERT INTO entities (id, field_name, status) VALUES
    ('uuid-1', 'Default Value 1', 'active'),
    ('uuid-2', 'Default Value 2', 'active');
```

---

## 4. API Endpoints

### 4.1 Summary

| Method | Path | Description | Auth | Permission |
|--------|------|-------------|------|------------|
| GET | `/api/v1/entities` | List entities | JWT | `entity:read` |
| GET | `/api/v1/entities/:id` | Get entity | JWT | `entity:read` |
| POST | `/api/v1/entities` | Create entity | JWT | `entity:create` |
| PUT | `/api/v1/entities/:id` | Update entity | JWT | `entity:update` |
| DELETE | `/api/v1/entities/:id` | Delete entity | JWT | `entity:delete` |

### 4.2 GET /api/v1/entities

**Description:** List entities with pagination and filtering.

**Query Parameters:**
| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| page | int | No | 1 | Page number (1-based) |
| limit | int | No | 20 | Items per page (max 100) |
| status | string | No | - | Filter by status |
| search | string | No | - | Search in field_name |
| sort | string | No | createdAt | Sort field |
| order | string | No | desc | Sort order (asc/desc) |

**Success Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "fieldName": "value",
      "status": "active",
      "createdAt": "2024-01-01T00:00:00Z"
    }
  ],
  "meta": {
    "total": 100,
    "page": 1,
    "limit": 20,
    "totalPages": 5,
    "hasNext": true,
    "hasPrev": false
  }
}
```

**Error Responses:**
```json
// 401 Unauthorized
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Authentication required"
  }
}

// 403 Forbidden
{
  "success": false,
  "error": {
    "code": "FORBIDDEN",
    "message": "Insufficient permissions",
    "required": ["entity:read"]
  }
}
```

### 4.3 POST /api/v1/entities

**Description:** Create a new entity.

**Request Body:**
```json
{
  "fieldName": "string (required, 1-100 chars)",
  "description": "string (optional, max 500 chars)",
  "relatedId": "uuid (required, must exist)"
}
```

**Validation Rules:**
| Field | Rules |
|-------|-------|
| fieldName | Required, 1-100 chars, alphanumeric + spaces |
| description | Optional, max 500 chars |
| relatedId | Required, valid UUID, must exist in DB |

**Success Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "new-uuid",
    "fieldName": "value",
    "status": "draft",
    "createdAt": "2024-01-01T00:00:00Z"
  }
}
```

**Error Response (400):**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": [
      {
        "field": "fieldName",
        "message": "Field is required",
        "code": "REQUIRED"
      }
    ]
  }
}
```

---

## 5. Service Layer

### 5.1 Entity Service

```typescript
// services/entityService.ts

import { db } from '../db';
import {
  Entity,
  CreateEntityDTO,
  UpdateEntityDTO,
  EntityFilters,
  PaginatedResult
} from '../types';
import {
  NotFoundError,
  ValidationError,
  ForbiddenError
} from '../errors';
import { logger } from '../logger';

export class EntityService {

  /**
   * Create a new entity
   *
   * @param data - Entity creation data
   * @param userId - ID of the creating user
   * @returns Created entity
   * @throws ValidationError if data is invalid
   * @throws NotFoundError if relatedId doesn't exist
   */
  async create(
    data: CreateEntityDTO,
    userId: string
  ): Promise<Entity> {
    // Validate related entity exists
    const related = await db('related_table')
      .where('id', data.relatedId)
      .first();

    if (!related) {
      throw new NotFoundError(
        `Related entity ${data.relatedId} not found`
      );
    }

    // Create entity
    const [entity] = await db('entities')
      .insert({
        field_name: data.fieldName,
        description: data.description,
        related_id: data.relatedId,
        created_by: userId,
        status: 'draft'
      })
      .returning('*');

    logger.info('Entity created', {
      entityId: entity.id,
      userId
    });

    return this.mapToEntity(entity);
  }

  /**
   * Get paginated list of entities with filters
   */
  async findAll(
    filters: EntityFilters,
    user: AuthUser
  ): Promise<PaginatedResult<Entity>> {
    let query = db('entities').select('*');

    // Role-based filtering
    if (user.role === 'viewer') {
      query = query.where('status', 'active');
    }

    // Apply filters
    if (filters.status) {
      query = query.where('status', filters.status);
    }

    if (filters.search) {
      query = query.where(
        'field_name',
        'ilike',
        `%${filters.search}%`
      );
    }

    // Get total count
    const [{ count }] = await query.clone().count();
    const total = parseInt(count as string);

    // Apply pagination
    const data = await query
      .offset((filters.page - 1) * filters.limit)
      .limit(filters.limit)
      .orderBy(filters.sort, filters.order);

    return {
      data: data.map(this.mapToEntity),
      meta: {
        total,
        page: filters.page,
        limit: filters.limit,
        totalPages: Math.ceil(total / filters.limit),
        hasNext: filters.page * filters.limit < total,
        hasPrev: filters.page > 1
      }
    };
  }

  private mapToEntity(row: any): Entity {
    return {
      id: row.id,
      fieldName: row.field_name,
      description: row.description,
      relatedId: row.related_id,
      status: row.status,
      createdBy: row.created_by,
      createdAt: row.created_at.toISOString(),
      updatedAt: row.updated_at.toISOString()
    };
  }
}
```

### 5.2 Validation Schema

```typescript
// validators/entityValidator.ts

import Joi from 'joi';

export const createEntitySchema = Joi.object({
  fieldName: Joi.string()
    .min(1)
    .max(100)
    .pattern(/^[a-zA-Z0-9\s]+$/)
    .required()
    .messages({
      'string.empty': 'Field name is required',
      'string.max': 'Field name cannot exceed 100 characters',
      'string.pattern.base': 'Field name can only contain letters, numbers, and spaces'
    }),

  description: Joi.string()
    .max(500)
    .optional()
    .allow(''),

  relatedId: Joi.string()
    .uuid({ version: 'uuidv4' })
    .required()
    .messages({
      'string.guid': 'Related ID must be a valid UUID'
    })
});
```

---

## 6. Security

### 6.1 Authentication Middleware

```typescript
// middleware/authenticate.ts

export const authenticate = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  const authHeader = req.headers.authorization;

  if (!authHeader?.startsWith('Bearer ')) {
    return res.status(401).json({
      success: false,
      error: {
        code: 'UNAUTHORIZED',
        message: 'Bearer token required'
      }
    });
  }

  const token = authHeader.split(' ')[1];

  try {
    const decoded = await verifyJWT(token);
    req.user = await getUserWithPermissions(decoded.sub);
    next();
  } catch (error) {
    return res.status(401).json({
      success: false,
      error: {
        code: 'INVALID_TOKEN',
        message: 'Token is invalid or expired'
      }
    });
  }
};
```

### 6.2 Authorization Middleware

```typescript
// middleware/authorize.ts

export const authorize = (...permissions: string[]) => {
  return (req: Request, res: Response, next: NextFunction) => {
    const userPermissions = req.user.permissions;

    const hasPermission = permissions.every(
      p => userPermissions.includes(p)
    );

    if (!hasPermission) {
      return res.status(403).json({
        success: false,
        error: {
          code: 'FORBIDDEN',
          message: 'Insufficient permissions',
          required: permissions,
          current: userPermissions
        }
      });
    }

    next();
  };
};
```

### 6.3 Route Configuration

```typescript
// routes/entityRoutes.ts

router.get(
  '/entities',
  authenticate,
  authorize('entity:read'),
  entityController.list
);

router.post(
  '/entities',
  authenticate,
  authorize('entity:create'),
  validate(createEntitySchema),
  entityController.create
);
```

---

## 7. Testing Requirements

### 7.1 Unit Test Example

```typescript
// __tests__/entityService.test.ts

describe('EntityService', () => {
  describe('create', () => {
    it('should create entity with valid data', async () => {
      // Arrange
      const data = {
        fieldName: 'Test',
        relatedId: 'valid-uuid'
      };
      mockDb.related.mockResolvedValue({ id: 'valid-uuid' });
      mockDb.insert.mockResolvedValue([mockEntity]);

      // Act
      const result = await service.create(data, 'user-id');

      // Assert
      expect(result.fieldName).toBe('Test');
      expect(result.status).toBe('draft');
    });

    it('should throw NotFoundError for invalid relatedId', async () => {
      // Arrange
      mockDb.related.mockResolvedValue(null);

      // Act & Assert
      await expect(service.create(data, 'user-id'))
        .rejects
        .toThrow(NotFoundError);
    });
  });
});
```

### 7.2 Test Matrix

| Scenario | Input | Expected | Priority |
|----------|-------|----------|----------|
| Create valid entity | Valid DTO | 201, entity | High |
| Create missing field | No fieldName | 400, validation | High |
| Create invalid related | Bad UUID | 404, not found | High |
| List as admin | Admin token | All entities | High |
| List as viewer | Viewer token | Active only | High |
| Update without permission | Read-only user | 403 | Medium |
| Delete referenced entity | Has relations | 400 or cascade | Medium |

---

## 8. Acceptance Criteria

- [ ] All endpoints return correct status codes
- [ ] Validation errors include field-level details
- [ ] Role-based filtering works correctly
- [ ] Pagination works with all filter combinations
- [ ] Unit test coverage > 80%
- [ ] Integration tests pass
- [ ] No N+1 query issues
- [ ] Response times < 200ms (p95)
- [ ] All sensitive data excluded from logs
````

### 6. STOPPING CONDITION

```
The specification is complete when:

✅ Data Models are defined:
   ├── TypeScript interfaces with JSDoc
   ├── DTOs for create/update
   └── Enums for restricted values

✅ Database Schema includes:
   ├── CREATE TABLE with all fields
   ├── PRIMARY KEY and FOREIGN KEYS
   ├── CHECK constraints
   ├── UNIQUE constraints
   ├── Indexes for filtered/sorted fields
   ├── Trigger for updated_at
   └── Seed data (if required)

✅ API Endpoints documented with:
   ├── Method + Path
   ├── Query/Body parameters
   ├── Validation rules
   ├── Success response schema
   ├── Error response schemas
   ├── Auth requirement
   └── Permission requirement

✅ Code examples include:
   ├── At least one Service layer function
   ├── Validation schema
   ├── Auth middleware
   └── Route configuration

✅ Code is runnable (NOT pseudo-code)

✅ Testing requirements defined:
   ├── Unit test examples
   └── Test matrix
```

### 7. PROMPT STEPS

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: PRD ANALYSIS                                        │
├─────────────────────────────────────────────────────────────┤
│ □ Read the relevant PRD section                             │
│ □ Identify all entities (nouns = tables)                    │
│ □ Identify all actions (verbs = API endpoints)              │
│ □ Note all constraints:                                     │
│   • Character limits                                        │
│   • Required fields                                         │
│   • Allowed values                                          │
│ □ Identify security requirements:                           │
│   • Who can do what                                         │
│   • Role-based filtering                                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ STEP 2: DATA MODELING                                       │
├─────────────────────────────────────────────────────────────┤
│ □ Create TypeScript interface for each entity               │
│ □ Add JSDoc comment to each field                           │
│ □ Define enums for restricted values (status, type, etc.)   │
│ □ Create DTOs:                                              │
│   • CreateDTO (what's needed for creation)                  │
│   • UpdateDTO (what can be updated)                         │
│ □ Document relationships:                                   │
│   • 1:1, 1:N, N:M                                           │
│   • Draw ERD                                                │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ STEP 3: DATABASE DESIGN                                     │
├─────────────────────────────────────────────────────────────┤
│ □ Translate interfaces to SQL tables                        │
│ □ Define primary keys (UUID recommended)                    │
│ □ Define foreign keys with ON DELETE behavior:              │
│   • CASCADE = deleting parent deletes children              │
│   • RESTRICT = prevent delete if children exist             │
│   • SET NULL = children.fk = NULL                           │
│ □ Add constraints:                                          │
│   • NOT NULL for required fields                            │
│   • CHECK for restricted values                             │
│   • UNIQUE for unique fields                                │
│ □ Create indexes for fields that are:                       │
│   • Filtered (WHERE)                                        │
│   • Sorted (ORDER BY)                                       │
│   • Foreign keys                                            │
│ □ Add timestamps (created_at, updated_at)                   │
│ □ Write seed data if required                               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ STEP 4: API DESIGN                                          │
├─────────────────────────────────────────────────────────────┤
│ □ Map each action to HTTP method + path:                    │
│   • GET /resources = list                                   │
│   • GET /resources/:id = get single                         │
│   • POST /resources = create                                │
│   • PUT /resources/:id = update                             │
│   • DELETE /resources/:id = delete                          │
│ □ Define query parameters for each GET:                     │
│   • Pagination (page, limit)                                │
│   • Filtering (status, search)                              │
│   • Sorting (sort, order)                                   │
│ □ Define request body schema for each POST/PUT              │
│ □ Define response schema:                                   │
│   • Success response                                        │
│   • Error responses (400, 401, 403, 404, 500)               │
│ □ Add auth requirement to each endpoint                     │
│ □ Add permission requirement to each endpoint               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ STEP 5: SERVICE LAYER                                       │
├─────────────────────────────────────────────────────────────┤
│ □ Write service class with main methods:                    │
│   • create()                                                │
│   • findAll() with filtering                                │
│   • findById()                                              │
│   • update()                                                │
│   • delete()                                                │
│ □ Add input validation                                      │
│ □ Add error handling:                                       │
│   • ValidationError                                         │
│   • NotFoundError                                           │
│   • ForbiddenError                                          │
│ □ Add logging                                               │
│ □ Add role-based filtering if required                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ STEP 6: SECURITY                                            │
├─────────────────────────────────────────────────────────────┤
│ □ Write authentication middleware                           │
│ □ Write authorization middleware                            │
│ □ Write route configuration with middleware chain           │
│ □ Verify every endpoint is protected                        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ STEP 7: TESTING                                             │
├─────────────────────────────────────────────────────────────┤
│ □ Write at least one unit test example                      │
│ □ Create test matrix with all scenarios:                    │
│   • Success cases                                           │
│   • Validation errors                                       │
│   • Not found errors                                        │
│   • Permission errors                                       │
│ □ Define acceptance criteria                                │
└─────────────────────────────────────────────────────────────┘
```

---

## Quality Checklist

Before finalizing the Tech Spec:

- [ ] All data models have TypeScript interfaces
- [ ] SQL schema is complete and valid
- [ ] API endpoints follow REST conventions
- [ ] Authentication/Authorization covered
- [ ] Error responses defined with codes
- [ ] Code examples are runnable
- [ ] Test cases specified
- [ ] Security considerations addressed
- [ ] Performance requirements noted

---

## Phase Integration

This command is used in **Phase 2: Tech Spec**

After Tech Spec creation:
1. Review architecture decisions
2. Validate with team
3. Get approval with `/phase-approve`
4. Move to Phase 3: Implementation Plan with `/phase-advance`

## Test-Driven Integration

The Tech Spec is used by `/write-tests` command to:
- Generate API contract tests from endpoint schemas
- Create database integration tests
- Define error scenario tests

```
Tech Spec API Design → Backend Tests (API contracts)
Tech Spec Data Model → Integration Tests (DB operations)
Tech Spec Error Handling → Error scenario tests
```

---

## Examples

```bash
# Generate tech spec from existing PRD
/tech-spec user-authentication
# Reads: docs/prd/2024-06-15-user-authentication.md
# Creates: docs/tech-spec/2024-06-16-user-authentication.md

# Interactive mode
/tech-spec
```
