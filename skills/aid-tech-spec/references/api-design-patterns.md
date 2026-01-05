# API Design Patterns

## RESTful API Conventions

### URL Structure
```
GET    /api/v1/resources          # List
GET    /api/v1/resources/:id      # Get one
POST   /api/v1/resources          # Create
PUT    /api/v1/resources/:id      # Replace
PATCH  /api/v1/resources/:id      # Update
DELETE /api/v1/resources/:id      # Delete
```

### Nested Resources
```
GET    /api/v1/users/:userId/orders           # User's orders
GET    /api/v1/users/:userId/orders/:orderId  # Specific order
POST   /api/v1/users/:userId/orders           # Create order for user
```

### Query Parameters
```
# Pagination
GET /api/v1/resources?page=2&limit=20

# Filtering
GET /api/v1/resources?status=active&type=premium

# Sorting
GET /api/v1/resources?sort=createdAt&order=desc

# Field selection
GET /api/v1/resources?fields=id,name,email

# Search
GET /api/v1/resources?q=search+term
```

## Response Formats

### Success Response
```json
{
  "data": {
    "id": "123",
    "type": "user",
    "attributes": {
      "name": "John Doe",
      "email": "john@example.com"
    }
  },
  "meta": {
    "requestId": "abc-123"
  }
}
```

### List Response
```json
{
  "data": [
    { "id": "1", "name": "Item 1" },
    { "id": "2", "name": "Item 2" }
  ],
  "meta": {
    "total": 100,
    "page": 1,
    "limit": 20,
    "totalPages": 5
  },
  "links": {
    "self": "/api/v1/resources?page=1",
    "next": "/api/v1/resources?page=2",
    "last": "/api/v1/resources?page=5"
  }
}
```

### Error Response
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  },
  "meta": {
    "requestId": "abc-123",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

## HTTP Status Codes

### Success
| Code | Meaning | Use Case |
|------|---------|----------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |

### Client Errors
| Code | Meaning | Use Case |
|------|---------|----------|
| 400 | Bad Request | Validation error |
| 401 | Unauthorized | Missing/invalid auth |
| 403 | Forbidden | No permission |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate, state conflict |
| 422 | Unprocessable | Semantic error |
| 429 | Too Many Requests | Rate limit exceeded |

### Server Errors
| Code | Meaning | Use Case |
|------|---------|----------|
| 500 | Internal Error | Unexpected error |
| 502 | Bad Gateway | Upstream failure |
| 503 | Service Unavailable | Maintenance/overload |
| 504 | Gateway Timeout | Upstream timeout |

## Error Codes Standard

```typescript
enum ErrorCode {
  // Validation
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  INVALID_FORMAT = 'INVALID_FORMAT',
  REQUIRED_FIELD = 'REQUIRED_FIELD',

  // Auth
  UNAUTHORIZED = 'UNAUTHORIZED',
  FORBIDDEN = 'FORBIDDEN',
  TOKEN_EXPIRED = 'TOKEN_EXPIRED',

  // Resource
  NOT_FOUND = 'NOT_FOUND',
  ALREADY_EXISTS = 'ALREADY_EXISTS',
  CONFLICT = 'CONFLICT',

  // System
  INTERNAL_ERROR = 'INTERNAL_ERROR',
  SERVICE_UNAVAILABLE = 'SERVICE_UNAVAILABLE',
  RATE_LIMIT_EXCEEDED = 'RATE_LIMIT_EXCEEDED'
}
```

## API Documentation Template

```markdown
## POST /api/v1/users

Create a new user.

### Authentication
Required: Bearer token with `users:create` scope

### Request Body
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| email | string | Yes | Valid email |
| name | string | Yes | 2-100 chars |
| role | string | No | Default: "user" |

### Example Request
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "role": "admin"
}
```

### Success Response (201)
```json
{
  "data": {
    "id": "user_123",
    "email": "user@example.com",
    "name": "John Doe",
    "role": "admin",
    "createdAt": "2024-01-15T10:30:00Z"
  }
}
```

### Error Responses

**400 Bad Request**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Email is required"
  }
}
```

**409 Conflict**
```json
{
  "error": {
    "code": "ALREADY_EXISTS",
    "message": "User with this email already exists"
  }
}
```
```

## Versioning Strategy

### URL Versioning (Recommended)
```
/api/v1/users
/api/v2/users
```

### Header Versioning
```
Accept: application/vnd.api+json; version=1
```

### Migration Strategy
1. Support old version for N months
2. Add deprecation header
3. Document migration path
4. Remove after sunset date
