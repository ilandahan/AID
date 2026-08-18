# API Design Template

Production-quality reference for designing, documenting, and reviewing REST APIs in a SaaS context. This template is injected into the API Designer agent context during Phase 2 (Tech Spec).

**Companion references**: `api-design-patterns.md` (quick lookup), `data-modeling-guide.md` (entity schemas), `architecture-diagrams.md` (sequence/flow diagrams).

---

## Table of Contents

1. [Endpoint Specification Format](#1-endpoint-specification-format)
2. [REST API Design Conventions](#2-rest-api-design-conventions)
3. [API Versioning Strategies](#3-api-versioning-strategies)
4. [Error Response Contract](#4-error-response-contract)
5. [Integration Patterns](#5-integration-patterns)
6. [Pagination Patterns](#6-pagination-patterns)
7. [Authentication per Endpoint](#7-authentication-per-endpoint)
8. [Rate Limiting Strategy](#8-rate-limiting-strategy)
9. [OpenAPI / Swagger Reference](#9-openapi--swagger-reference)

---

## 1. Endpoint Specification Format

Every endpoint in the tech spec MUST follow this format. No exceptions. An endpoint documented without request/response schemas and error cases is incomplete.

### Template

````markdown
### `METHOD /api/v1/resource-path`

**Description**: One-sentence summary of what this endpoint does and WHY it exists.

**Authentication**: `required` | `optional` | `public`
**Authorized Roles**: `admin`, `member` | `any authenticated user`
**Rate Limit**: `100 req/min per user` | `10 req/min per API key`
**Idempotency**: `required (via Idempotency-Key header)` | `naturally idempotent` | `not idempotent`

#### Request

**Headers**:
| Header | Required | Description |
|--------|----------|-------------|
| `Authorization` | Yes | `Bearer <jwt_token>` |
| `Content-Type` | Yes | `application/json` |
| `Idempotency-Key` | Conditional | Required for POST/PATCH. UUID v4. |
| `X-Request-ID` | No | Client-generated trace ID for debugging. |

**Path Parameters**:
| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `projectId` | `string (UUID)` | Target project identifier | `proj_a1b2c3d4` |

**Query Parameters**:
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `status` | `string` | No | `all` | Filter by status. Enum: `active`, `archived`, `all` |
| `cursor` | `string` | No | -- | Pagination cursor from previous response |
| `limit` | `integer` | No | `20` | Items per page. Min: 1, Max: 100 |

**Request Body** (JSON):
```json
{
  "name": "Q4 Campaign",
  "description": "End-of-year marketing push",
  "startDate": "2026-10-01T00:00:00Z",
  "tags": ["marketing", "q4"],
  "config": {
    "notifyOnComplete": true,
    "maxRetries": 3
  }
}
```

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `name` | `string` | Yes | 1-200 chars | Human-readable name |
| `description` | `string` | No | Max 2000 chars | Optional description |
| `startDate` | `string (ISO 8601)` | Yes | Must be in the future | Campaign start timestamp |
| `tags` | `string[]` | No | Max 20 items, each 1-50 chars | Categorization tags |
| `config` | `object` | No | -- | Optional configuration |
| `config.notifyOnComplete` | `boolean` | No | Default: `false` | Send webhook on completion |
| `config.maxRetries` | `integer` | No | Default: `3`, Range: 0-10 | Retry limit for failed steps |

#### Response

**`201 Created`** -- Resource successfully created:
```json
{
  "data": {
    "id": "cmp_x7k9m2n4",
    "name": "Q4 Campaign",
    "description": "End-of-year marketing push",
    "status": "draft",
    "startDate": "2026-10-01T00:00:00Z",
    "tags": ["marketing", "q4"],
    "config": {
      "notifyOnComplete": true,
      "maxRetries": 3
    },
    "createdAt": "2026-03-23T14:30:00Z",
    "updatedAt": "2026-03-23T14:30:00Z",
    "createdBy": "usr_abc123"
  },
  "meta": {
    "requestId": "req_f8e7d6c5"
  }
}
```

**`400 Bad Request`** -- Malformed request syntax or missing required fields:
```json
{
  "error": "Validation failed",
  "code": "VALIDATION_ERROR",
  "details": [
    { "field": "name", "message": "Name is required", "rule": "required" },
    { "field": "startDate", "message": "Start date must be in the future", "rule": "future_date" }
  ],
  "meta": { "requestId": "req_f8e7d6c5" }
}
```

**`401 Unauthorized`** -- Missing or invalid authentication token:
```json
{
  "error": "Authentication required",
  "code": "UNAUTHORIZED",
  "meta": { "requestId": "req_f8e7d6c5" }
}
```

**`403 Forbidden`** -- Authenticated but insufficient permissions:
```json
{
  "error": "You do not have permission to create campaigns in this project",
  "code": "FORBIDDEN",
  "meta": { "requestId": "req_f8e7d6c5" }
}
```

**`409 Conflict`** -- Resource state conflict (e.g., duplicate name):
```json
{
  "error": "A campaign with this name already exists in the project",
  "code": "ALREADY_EXISTS",
  "details": { "existingId": "cmp_z1y2x3w4" },
  "meta": { "requestId": "req_f8e7d6c5" }
}
```

**`422 Unprocessable Entity`** -- Semantically invalid (syntactically correct but business rule violation):
```json
{
  "error": "Cannot create campaign: project has reached its plan limit of 10 active campaigns",
  "code": "PLAN_LIMIT_EXCEEDED",
  "details": { "limit": 10, "current": 10, "plan": "starter" },
  "meta": { "requestId": "req_f8e7d6c5" }
}
```

**`429 Too Many Requests`** -- Rate limit exceeded:
```json
{
  "error": "Rate limit exceeded. Retry after 30 seconds.",
  "code": "RATE_LIMIT_EXCEEDED",
  "meta": {
    "requestId": "req_f8e7d6c5",
    "retryAfter": 30
  }
}
```

**`500 Internal Server Error`** -- Unexpected server failure:
```json
{
  "error": "An unexpected error occurred. Please try again or contact support.",
  "code": "INTERNAL_ERROR",
  "meta": { "requestId": "req_f8e7d6c5" }
}
```

#### Notes
- The `Idempotency-Key` header ensures that retried POST requests do not create duplicate resources. The server stores the key for 24 hours.
- The `requestId` in every response enables cross-referencing with server logs for debugging.
````

### Checklist: Is This Endpoint Spec Complete?

- [ ] Method and path defined
- [ ] Description includes WHY the endpoint exists
- [ ] Auth requirements specified (role-level, not just "required")
- [ ] Rate limit stated
- [ ] All path, query, and body parameters documented with types, constraints, and examples
- [ ] Every response status code has a body example
- [ ] Error responses use the standard error contract
- [ ] Idempotency requirements addressed for mutating endpoints

---

## 2. REST API Design Conventions

### Resource Naming

| Rule | Good | Bad | Why |
|------|------|-----|-----|
| Plural nouns for collections | `/api/v1/projects` | `/api/v1/project` | Collections represent multiple items |
| Singular for singletons | `/api/v1/users/me` | `/api/v1/users/current-user` | Only one "me" per auth context |
| Kebab-case for multi-word | `/api/v1/project-members` | `/api/v1/projectMembers` | URLs are case-insensitive by convention |
| Nouns, not verbs | `/api/v1/reports` | `/api/v1/generate-report` | HTTP method is the verb |
| No trailing slashes | `/api/v1/projects` | `/api/v1/projects/` | Canonical URL consistency |

### Standard CRUD Mapping

```
GET    /api/v1/projects                    # List projects (paginated)
POST   /api/v1/projects                    # Create a project
GET    /api/v1/projects/:projectId         # Get a single project
PATCH  /api/v1/projects/:projectId         # Partial update
PUT    /api/v1/projects/:projectId         # Full replacement (rare in practice)
DELETE /api/v1/projects/:projectId         # Delete (or soft-delete)
```

### Nested Resources

Use nesting to express ownership. Limit to two levels of nesting maximum.

```
# Good: two levels
GET  /api/v1/projects/:projectId/members
POST /api/v1/projects/:projectId/members

# Acceptable: access nested resource directly when it has a global ID
GET  /api/v1/members/:memberId

# Bad: three or more levels (use query params instead)
GET  /api/v1/organizations/:orgId/projects/:projectId/members/:memberId/tasks
# Better:
GET  /api/v1/tasks?memberId=:memberId&projectId=:projectId
```

### Action Endpoints (Non-CRUD Operations)

Some operations do not map cleanly to CRUD. Use a sub-resource verb for these:

```
POST /api/v1/projects/:projectId/archive        # Archive a project
POST /api/v1/projects/:projectId/duplicate       # Clone a project
POST /api/v1/invitations/:invitationId/accept    # Accept an invitation
POST /api/v1/reports/:reportId/export            # Trigger an export
```

### Filtering, Sorting, and Search

```
# Filtering -- field=value pairs
GET /api/v1/projects?status=active&ownerId=usr_abc123

# Multiple values for the same field -- comma-separated
GET /api/v1/projects?status=active,archived

# Date range -- use suffixes
GET /api/v1/projects?createdAfter=2026-01-01T00:00:00Z&createdBefore=2026-04-01T00:00:00Z

# Sorting -- sort=field:direction (default asc)
GET /api/v1/projects?sort=createdAt:desc
GET /api/v1/projects?sort=name:asc,createdAt:desc    # Multi-field sort

# Full-text search
GET /api/v1/projects?q=marketing+campaign

# Field selection (sparse fieldsets)
GET /api/v1/projects?fields=id,name,status
```

### Bulk Operations

For operations that affect multiple resources in one call:

```
# Bulk create
POST /api/v1/projects/:projectId/members/bulk
{
  "operations": [
    { "action": "add", "userId": "usr_abc", "role": "editor" },
    { "action": "add", "userId": "usr_def", "role": "viewer" }
  ]
}

# Bulk update
PATCH /api/v1/projects/bulk
{
  "ids": ["proj_a1", "proj_b2", "proj_c3"],
  "update": { "status": "archived" }
}

# Bulk delete
POST /api/v1/projects/bulk-delete
{
  "ids": ["proj_a1", "proj_b2"]
}
```

**Response for bulk operations** -- always report per-item status:
```json
{
  "data": {
    "succeeded": [
      { "id": "proj_a1", "status": "archived" },
      { "id": "proj_b2", "status": "archived" }
    ],
    "failed": [
      { "id": "proj_c3", "error": { "code": "NOT_FOUND", "message": "Project not found" } }
    ]
  },
  "meta": {
    "total": 3,
    "succeeded": 2,
    "failed": 1,
    "requestId": "req_f8e7d6c5"
  }
}
```

### Idempotency Keys

All non-idempotent mutations (POST, PATCH with side effects) SHOULD accept an `Idempotency-Key` header:

| Method | Naturally Idempotent? | Idempotency-Key Required? |
|--------|----------------------|--------------------------|
| GET | Yes | No |
| PUT | Yes (full replace) | No |
| DELETE | Yes | No |
| POST | No | Yes (for creates) |
| PATCH | Depends on operation | Recommended |

```
POST /api/v1/projects
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000

# If the client retries with the same key within 24h, the server
# returns the original response (201) without creating a duplicate.
```

Server behavior:
1. On first request: execute, store `(key, response, status)` for 24 hours.
2. On duplicate key within window: return stored response, skip execution.
3. On duplicate key with different body: return `422 Unprocessable Entity` with code `IDEMPOTENCY_KEY_REUSE`.

---

## 3. API Versioning Strategies

### Strategy Comparison

| Strategy | Format | Pros | Cons | Best For |
|----------|--------|------|------|----------|
| **URL path** (recommended) | `/api/v1/resources` | Explicit, cacheable, easy routing, visible in logs | URL changes on version bump, no partial versioning | Public APIs, multi-tenant SaaS |
| **Header** | `Accept: application/vnd.myapi.v2+json` | Clean URLs, can version per resource | Hidden from logs/caches, harder to test in browser | Internal APIs, API-first teams |
| **Query param** | `/api/resources?version=2` | Easy to add, visible | Pollutes query namespace, caching complications | Quick prototypes, gradual migration |

### Recommended: URL Path Versioning

```
/api/v1/projects      # Version 1 -- current stable
/api/v2/projects      # Version 2 -- next generation
```

Rules:
- The version number is a **major** version only. Minor/patch changes are backward-compatible and do not create a new version.
- Bump the version when you make a **breaking change**: removing a field, renaming a field, changing a field type, changing required/optional status, changing URL structure, changing authentication mechanism.
- Do NOT bump the version for: adding new optional fields, adding new endpoints, adding new query parameters, changing internal implementation.

### Deprecation Policy Template

```markdown
## Deprecation Policy: API v{N}

### Timeline
| Milestone | Date | Action |
|-----------|------|--------|
| Deprecation announced | YYYY-MM-DD | Deprecation header added to all v{N} responses |
| Migration guide published | YYYY-MM-DD | Documentation available at /docs/migration/v{N}-to-v{N+1} |
| Warning period begins | YYYY-MM-DD | Deprecation warning emails sent to API key owners weekly |
| Read-only mode | YYYY-MM-DD | Mutating endpoints return 410 Gone |
| Full sunset | YYYY-MM-DD | All v{N} endpoints return 410 Gone |

### Response Headers During Deprecation
Deprecation: Sun, 01 Jun 2027 00:00:00 GMT
Sunset: Mon, 01 Sep 2027 00:00:00 GMT
Link: </docs/migration/v1-to-v2>; rel="deprecation"

### Migration Guide Structure
1. Breaking changes inventory (field-by-field comparison)
2. Endpoint mapping (old path to new path)
3. Code examples (before/after)
4. SDK upgrade instructions
5. FAQ
```

### What Constitutes a Breaking Change

| Change | Breaking? | Requires New Version? |
|--------|-----------|----------------------|
| Remove a response field | Yes | Yes |
| Rename a response field | Yes | Yes |
| Change field type (string to integer) | Yes | Yes |
| Make optional field required | Yes | Yes |
| Change error code format | Yes | Yes |
| Add new optional response field | No | No |
| Add new optional request parameter | No | No |
| Add new endpoint | No | No |
| Fix a bug in validation | Depends | Document, usually no |
| Change rate limits | Possibly | Document, notify |

---

## 4. Error Response Contract

### Standard Error Shape

Every error response from every endpoint MUST conform to this shape:

```typescript
interface ErrorResponse {
  /** Human-readable error message. Safe to display to end users. */
  error: string;

  /** Machine-readable error code. UPPER_SNAKE_CASE.
   *  Used by client code for programmatic error handling. */
  code: string;

  /** Optional structured details.
   *  For validation errors: array of field-level issues.
   *  For business errors: relevant context (limits, IDs, etc.) */
  details?: ValidationDetail[] | Record<string, unknown>;

  /** Request metadata for debugging and support. */
  meta: {
    /** Server-generated unique request ID. Always present. */
    requestId: string;
    /** ISO 8601 timestamp of the error. */
    timestamp?: string;
    /** Seconds until the client may retry (for 429 responses). */
    retryAfter?: number;
  };
}

interface ValidationDetail {
  /** Dot-notation path to the invalid field. e.g., "config.maxRetries" */
  field: string;
  /** Human-readable description of the validation failure. */
  message: string;
  /** Machine-readable rule name. e.g., "required", "min_length", "enum" */
  rule: string;
}
```

### Error Code Naming Conventions

Error codes use `UPPER_SNAKE_CASE` and follow this structure: `{DOMAIN}_{SPECIFIC_ERROR}`

| Category | Code | HTTP Status | When to Use |
|----------|------|-------------|-------------|
| **Authentication** | `UNAUTHORIZED` | 401 | No token, expired token, malformed token |
| | `TOKEN_EXPIRED` | 401 | Token was valid but has expired (client can refresh) |
| | `INVALID_TOKEN` | 401 | Token is malformed or tampered |
| **Authorization** | `FORBIDDEN` | 403 | Authenticated but lacking required role/permission |
| | `INSUFFICIENT_SCOPE` | 403 | OAuth token lacks required scope |
| **Validation** | `VALIDATION_ERROR` | 400 | One or more fields fail validation (always include `details` array) |
| | `INVALID_FORMAT` | 400 | Request body is not valid JSON or violates content-type |
| | `MISSING_PARAMETER` | 400 | Required query/path parameter not provided |
| **Resource** | `NOT_FOUND` | 404 | Resource does not exist or caller cannot see it (avoids leaking existence) |
| | `ALREADY_EXISTS` | 409 | Unique constraint violation (duplicate email, name, etc.) |
| | `CONFLICT` | 409 | State conflict (e.g., trying to archive an already-archived project) |
| | `GONE` | 410 | Resource was deleted or endpoint deprecated |
| **Business Logic** | `PLAN_LIMIT_EXCEEDED` | 422 | Account has hit a plan/tier limit |
| | `INVALID_STATE_TRANSITION` | 422 | Operation not allowed in current resource state |
| | `PRECONDITION_FAILED` | 422 | A business prerequisite is not met |
| **Rate Limiting** | `RATE_LIMIT_EXCEEDED` | 429 | Too many requests; include `retryAfter` |
| **Idempotency** | `IDEMPOTENCY_KEY_REUSE` | 422 | Same idempotency key used with different payload |
| **Server** | `INTERNAL_ERROR` | 500 | Unexpected failure (log details server-side, never expose internals) |
| | `SERVICE_UNAVAILABLE` | 503 | Planned maintenance or temporary overload |
| | `UPSTREAM_ERROR` | 502 | A downstream dependency failed |

### When to Use 400 vs 422 vs 409

This is a common source of confusion. Use this decision tree:

```
Is the request syntactically malformed (bad JSON, missing required field, wrong type)?
  YES -> 400 Bad Request (code: VALIDATION_ERROR)

Is the request valid syntax but violates a business rule?
  (e.g., "cannot create more than 10 projects on starter plan")
  YES -> 422 Unprocessable Entity (code: domain-specific like PLAN_LIMIT_EXCEEDED)

Does the request conflict with the current state of a resource?
  (e.g., "a project with this name already exists", "resource is locked")
  YES -> 409 Conflict (code: ALREADY_EXISTS or CONFLICT)
```

### Error Response Rules

1. **Always include `requestId`** -- enables support to find the exact request in logs.
2. **Never expose stack traces, SQL queries, or internal paths** in production error responses.
3. **Use the same error shape for all endpoints** -- clients should parse errors with a single handler.
4. **Validation errors MUST include a `details` array** with per-field breakdown.
5. **404 for both "does not exist" AND "exists but you cannot see it"** -- prevents information leakage about resource existence.
6. **Error messages should be end-user safe** -- assume they may be displayed in a UI toast.

---

## 5. Integration Patterns

### 5.1 Webhooks

Webhooks push event data to registered callback URLs when something happens in the system.

#### Webhook Registration Endpoint

```
POST /api/v1/webhooks
{
  "url": "https://customer.example.com/hooks/aid",
  "events": ["project.created", "project.archived", "campaign.completed"],
  "secret": "whsec_a1b2c3d4e5f6..."
}
```

#### Webhook Payload Format

```json
{
  "id": "evt_m8n7o6p5",
  "type": "project.created",
  "apiVersion": "v1",
  "createdAt": "2026-03-23T14:30:00Z",
  "data": {
    "id": "proj_a1b2c3d4",
    "name": "Q4 Campaign",
    "status": "draft",
    "createdBy": "usr_abc123"
  }
}
```

#### Webhook Event Naming

```
{resource}.{action}

Examples:
project.created       project.updated       project.archived
project.deleted       member.added          member.removed
campaign.started      campaign.completed    campaign.failed
invoice.paid          invoice.overdue
```

#### Signature Verification

Every webhook request includes a signature header so the receiver can verify authenticity:

```
X-Webhook-Signature: sha256=a1b2c3d4e5f6...
X-Webhook-Timestamp: 1711200600
X-Webhook-ID: evt_m8n7o6p5
```

Verification algorithm (receiver side):
```
expected = HMAC-SHA256(
  key: webhook_secret,
  message: "{webhook_id}.{timestamp}.{raw_body}"
)
if (expected !== received_signature) reject
if (abs(now - timestamp) > 300) reject    # 5-min replay window
```

#### Retry Policy

| Attempt | Delay | Max Total Time |
|---------|-------|----------------|
| 1st retry | 30 seconds | -- |
| 2nd retry | 2 minutes | -- |
| 3rd retry | 15 minutes | -- |
| 4th retry | 1 hour | -- |
| 5th retry | 4 hours | -- |
| 6th retry (final) | 12 hours | ~17 hours from first attempt |

Behavior:
- Success = HTTP 2xx response within 10 seconds.
- Failure = HTTP 4xx/5xx, timeout, or connection refused.
- After all retries exhausted: mark webhook as `failing`, send notification to account owner.
- Auto-disable after 7 consecutive days of failures.

### 5.2 Server-Sent Events (SSE)

Use SSE for real-time, server-to-client streaming (e.g., live progress updates, activity feeds).

```
GET /api/v1/projects/:projectId/events
Accept: text/event-stream
Authorization: Bearer <token>
```

Response stream:
```
event: campaign.progress
data: {"campaignId": "cmp_x7k9m2n4", "percent": 45, "step": "analyzing"}
id: evt_001

event: campaign.completed
data: {"campaignId": "cmp_x7k9m2n4", "percent": 100, "result": "success"}
id: evt_003

: heartbeat
```

SSE design rules:
- Include `id` field for automatic reconnection (`Last-Event-ID` header).
- Send heartbeat comments (`: heartbeat`) every 30 seconds to keep connection alive.
- Set `Cache-Control: no-cache` and `Connection: keep-alive`.
- Implement server-side timeout (e.g., 5 minutes) and require client reconnection.

### 5.3 Polling (When Webhooks Are Not Available)

For long-running operations, return a job resource and let clients poll:

```
POST /api/v1/exports
{ "projectId": "proj_a1b2c3d4", "format": "csv" }

# Response (202 Accepted)
{
  "data": {
    "jobId": "job_q1w2e3r4",
    "status": "processing",
    "progress": 0,
    "estimatedCompletionAt": "2026-03-23T14:35:00Z"
  }
}

# Poll: GET /api/v1/exports/job_q1w2e3r4

# On completion:
{
  "data": {
    "jobId": "job_q1w2e3r4",
    "status": "completed",
    "progress": 100,
    "result": {
      "downloadUrl": "https://storage.example.com/exports/job_q1w2e3r4.csv",
      "expiresAt": "2026-03-24T14:35:00Z",
      "sizeBytes": 1048576
    }
  }
}
```

Polling design rules:
- Return `202 Accepted` (not 200) from the initial POST to signal async processing.
- Include `Retry-After` header with recommended poll interval (e.g., `Retry-After: 5`).
- Include `progress` (0-100) when possible so clients can display a progress bar.
- Set expiration on results (download URLs expire; job metadata persists for 7 days).

### 5.4 Batch Endpoints

For clients that need to execute multiple API calls in a single HTTP round-trip:

```
POST /api/v1/batch
{
  "requests": [
    { "id": "req_1", "method": "GET", "path": "/api/v1/projects/proj_a1" },
    { "id": "req_2", "method": "GET", "path": "/api/v1/projects/proj_b2" },
    { "id": "req_3", "method": "PATCH", "path": "/api/v1/projects/proj_c3", "body": { "name": "Updated" } }
  ]
}

# Response
{
  "responses": [
    { "id": "req_1", "status": 200, "body": { "data": { "id": "proj_a1" } } },
    { "id": "req_2", "status": 404, "body": { "error": "Not found", "code": "NOT_FOUND" } },
    { "id": "req_3", "status": 200, "body": { "data": { "id": "proj_c3" } } }
  ],
  "meta": { "requestId": "req_batch_f8e7" }
}
```

Batch rules:
- Maximum 25 sub-requests per batch.
- Each sub-request is independent (no ordering guarantees, no transactions).
- The batch endpoint itself always returns `200` -- check individual sub-request statuses.
- Batch requests count as N requests against rate limits (not 1).

---

## 6. Pagination Patterns

### 6.1 Cursor-Based Pagination (Recommended Default)

Best for: large datasets, real-time data, infinite scroll UIs.

```
GET /api/v1/projects?limit=20
GET /api/v1/projects?limit=20&cursor=eyJpZCI6InByb2pfYTFiMmMzIn0=
```

Response envelope:
```json
{
  "data": [
    { "id": "proj_a1", "name": "Alpha", "createdAt": "2026-03-20T10:00:00Z" },
    { "id": "proj_b2", "name": "Beta", "createdAt": "2026-03-21T11:00:00Z" }
  ],
  "pagination": {
    "hasMore": true,
    "nextCursor": "eyJpZCI6InByb2pfYjIifQ==",
    "limit": 20
  },
  "meta": { "requestId": "req_f8e7d6c5" }
}
```

Implementation notes:
- Cursor is a Base64-encoded opaque token (encodes the last item sort key).
- Clients MUST NOT decode or construct cursors -- treat as opaque.
- Stable under concurrent inserts/deletes (unlike offset-based).
- Cannot jump to arbitrary pages (no "go to page 5").

### 6.2 Offset-Based Pagination

Best for: admin dashboards, small datasets (<10K rows), UIs that need "page 3 of 12".

```
GET /api/v1/audit-logs?page=3&limit=20
```

Response envelope:
```json
{
  "data": [],
  "pagination": {
    "page": 3,
    "limit": 20,
    "total": 234,
    "totalPages": 12
  },
  "meta": { "requestId": "req_f8e7d6c5" }
}
```

Caveats:
- Performance degrades on large tables (`OFFSET 10000` is slow).
- Results shift when items are inserted/deleted during pagination.
- Counting `total` may be expensive -- consider making it optional: `?includeTotal=true`.

### 6.3 Keyset Pagination

Best for: time-series data, logs, event streams -- anything sorted by a monotonic key.

```
GET /api/v1/events?after=evt_m8n7o6p5&limit=50
GET /api/v1/events?before=evt_a1b2c3d4&limit=50
```

Response:
```json
{
  "data": [],
  "pagination": {
    "hasMore": true,
    "oldest": "evt_x1y2z3",
    "newest": "evt_m8n7o6p5"
  }
}
```

### When to Use Which

| Scenario | Pattern | Why |
|----------|---------|-----|
| Public API, general listing | Cursor | Stable, performant, forward-compatible |
| Admin panel with page numbers | Offset | UX requires page navigation |
| Time-series / event log | Keyset | Natural ordering, fast range queries |
| Search results | Cursor or Offset | Depends on search engine capability |
| Real-time feed / infinite scroll | Cursor | No missed items, no duplicates |

### Universal Pagination Rules

1. **Default `limit`**: 20 items.
2. **Max `limit`**: 100 items. Return 400 if client requests more.
3. **Always include `hasMore`** (or `totalPages`) so the client knows when to stop.
4. **Empty result set** returns `200` with `"data": []` -- NOT `404`.
5. **Consistent field names** across all paginated endpoints (use `pagination`, not `paging` or `meta.pagination`).

---

## 7. Authentication per Endpoint

### Auth Methods

| Method | Use Case | Format | Typical Lifetime |
|--------|----------|--------|-----------------|
| **JWT (access token)** | User-facing API calls from web/mobile apps | `Authorization: Bearer eyJhbGc...` | 15-60 minutes |
| **Refresh token** | Obtaining new access tokens | HTTP-only cookie or POST body | 7-30 days |
| **API key** | Server-to-server, CI/CD, developer tooling | `Authorization: Bearer ak_live_...` or `X-API-Key: ak_live_...` | Until revoked |
| **OAuth 2.0 token** | Third-party integrations | `Authorization: Bearer <oauth_token>` | Defined by grant |

### Endpoint Auth Matrix Template

Document this table for every resource group in the tech spec:

| Endpoint | Auth Required | Allowed Roles | API Key Allowed | Notes |
|----------|--------------|---------------|-----------------|-------|
| `GET /api/v1/health` | No | Public | N/A | Health check for load balancers |
| `POST /api/v1/auth/login` | No | Public | No | Returns JWT pair |
| `POST /api/v1/auth/refresh` | Refresh token | Any | No | Issues new access token |
| `GET /api/v1/projects` | Yes | `admin`, `member` | Yes | Filtered by caller access |
| `POST /api/v1/projects` | Yes | `admin` | Yes | Creates new project |
| `GET /api/v1/projects/:id` | Yes | `admin`, `member`, `viewer` | Yes | Must be project member |
| `DELETE /api/v1/projects/:id` | Yes | `admin` | Yes | Soft-deletes project |
| `GET /api/v1/admin/users` | Yes | `super_admin` | No | Internal admin only |
| `POST /api/v1/webhooks` | Yes | `admin` | Yes | Register webhook |

### Public Endpoints (No Auth)

These endpoints MUST be explicitly listed and justified:

| Endpoint | Justification |
|----------|---------------|
| `GET /api/v1/health` | Infrastructure health check. Must work without auth for LB probes. |
| `GET /api/v1/status` | Public status page data. |
| `POST /api/v1/auth/login` | Entry point for authentication flow. |
| `POST /api/v1/auth/signup` | New user registration. |
| `POST /api/v1/auth/forgot-password` | Password reset initiation. |
| `GET /api/v1/docs/*` | API documentation. |

### API Key Prefixes

Use environment-prefixed keys so developers can visually distinguish production from test:

```
ak_live_a1b2c3d4e5f6...    # Production API key
ak_test_x7y8z9w0v1u2...    # Test/sandbox API key
```

Rules:
- API keys are passed via `Authorization: Bearer ak_live_...` header (not query params -- they appear in logs).
- Each key has a set of scopes (e.g., `projects:read`, `projects:write`, `admin:*`).
- Keys can be rotated without downtime (support two active keys during rotation).

---

## 8. Rate Limiting Strategy

### Rate Limit Tiers

| Tier | Applies To | Limit | Window | Scope |
|------|-----------|-------|--------|-------|
| **Per-user default** | Authenticated requests | 1000 req/min | Sliding window | Per user ID |
| **Per-API-key default** | API key requests | 500 req/min | Sliding window | Per API key |
| **Per-endpoint override** | Expensive operations (exports, bulk, search) | 10-50 req/min | Sliding window | Per user + endpoint |
| **Anonymous** | Unauthenticated endpoints (login, signup) | 20 req/min | Fixed window | Per IP |
| **Global** | Entire API | 10,000 req/min | Fixed window | Per tenant/org |

### Sliding Window vs Fixed Window

| Algorithm | Behavior | Pros | Cons |
|-----------|----------|------|------|
| **Fixed window** | Counter resets at fixed intervals (e.g., every minute at :00) | Simple to implement | Burst at window edges (up to 2x limit) |
| **Sliding window** | Rolling time window from each request | Smoother distribution | Slightly more complex, needs timestamp storage |
| **Token bucket** | Refills tokens at constant rate, allows burst up to bucket size | Allows controlled bursts | More complex state |

**Recommendation**: Sliding window for per-user/per-key limits. Fixed window for anonymous/global limits.

### Rate Limit Response Headers

Every response (not just 429) SHOULD include rate limit headers so clients can self-throttle:

```http
X-RateLimit-Limit: 1000          # Max requests in the window
X-RateLimit-Remaining: 742       # Requests remaining in the current window
X-RateLimit-Reset: 1711200660    # Unix timestamp when the window resets
```

On `429 Too Many Requests`:
```http
HTTP/1.1 429 Too Many Requests
Retry-After: 30
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1711200660
Content-Type: application/json

{
  "error": "Rate limit exceeded. Try again in 30 seconds.",
  "code": "RATE_LIMIT_EXCEEDED",
  "meta": {
    "requestId": "req_f8e7d6c5",
    "retryAfter": 30
  }
}
```

### Per-Endpoint Overrides

Some endpoints are more expensive or abuse-sensitive. Override the default limit:

| Endpoint | Limit | Reason |
|----------|-------|--------|
| `POST /api/v1/auth/login` | 10 req/min per IP | Brute-force protection |
| `POST /api/v1/auth/forgot-password` | 3 req/hour per email | Abuse prevention |
| `POST /api/v1/exports` | 5 req/hour per user | CPU-intensive operation |
| `POST /api/v1/batch` | 20 req/min per user | Each batch counts as N sub-requests |
| `GET /api/v1/search` | 60 req/min per user | DB-intensive full-text search |

### Rate Limit Design Rules

1. **Identify the actor**: Use user ID for authenticated requests, IP for anonymous, API key for server-to-server.
2. **Always return `Retry-After`** with 429 responses -- clients need it for exponential backoff.
3. **Include rate limit headers on all responses** -- do not make the client guess.
4. **Log rate-limited requests** with actor identity for abuse detection.
5. **Support rate limit elevation** for enterprise customers (configurable per API key or tenant).
6. **Do not rate-limit health check endpoints** (`/api/v1/health`).

---

## 9. OpenAPI / Swagger Reference

The API Designer agent SHOULD produce an OpenAPI 3.1 specification alongside the tech spec. Below is the minimal structure with all required sections.

### Minimal OpenAPI 3.1 Template

```yaml
openapi: "3.1.0"
info:
  title: "[Product Name] API"
  version: "1.0.0"
  description: |
    API for [Product Name]. Provides endpoints for managing [core resources].
  contact:
    name: "API Support"
    email: "api-support@example.com"
    url: "https://docs.example.com"
  license:
    name: "Proprietary"

servers:
  - url: "https://api.example.com/api/v1"
    description: "Production"
  - url: "https://api.staging.example.com/api/v1"
    description: "Staging"
  - url: "http://localhost:3000/api/v1"
    description: "Local development"

tags:
  - name: "Projects"
    description: "Manage projects"
  - name: "Members"
    description: "Project membership management"
  - name: "Auth"
    description: "Authentication and token management"

paths:
  /projects:
    get:
      operationId: "listProjects"
      tags: ["Projects"]
      summary: "List projects"
      description: "Returns a paginated list of projects the caller has access to."
      security:
        - BearerAuth: []
        - ApiKeyAuth: []
      parameters:
        - $ref: "#/components/parameters/CursorParam"
        - $ref: "#/components/parameters/LimitParam"
        - name: "status"
          in: "query"
          required: false
          schema:
            type: "string"
            enum: ["active", "archived", "all"]
            default: "all"
          description: "Filter by project status"
      responses:
        "200":
          description: "Paginated list of projects"
          headers:
            X-RateLimit-Limit:
              $ref: "#/components/headers/X-RateLimit-Limit"
            X-RateLimit-Remaining:
              $ref: "#/components/headers/X-RateLimit-Remaining"
            X-RateLimit-Reset:
              $ref: "#/components/headers/X-RateLimit-Reset"
          content:
            application/json:
              schema:
                type: "object"
                required: ["data", "pagination", "meta"]
                properties:
                  data:
                    type: "array"
                    items:
                      $ref: "#/components/schemas/Project"
                  pagination:
                    $ref: "#/components/schemas/CursorPagination"
                  meta:
                    $ref: "#/components/schemas/ResponseMeta"
        "401":
          $ref: "#/components/responses/Unauthorized"
        "429":
          $ref: "#/components/responses/RateLimited"
        "500":
          $ref: "#/components/responses/InternalError"

    post:
      operationId: "createProject"
      tags: ["Projects"]
      summary: "Create a project"
      description: "Creates a new project. Requires admin role."
      security:
        - BearerAuth: []
        - ApiKeyAuth: []
      parameters:
        - $ref: "#/components/parameters/IdempotencyKey"
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/CreateProjectRequest"
            example:
              name: "Q4 Campaign"
              description: "End-of-year marketing push"
              tags: ["marketing", "q4"]
      responses:
        "201":
          description: "Project created"
          content:
            application/json:
              schema:
                type: "object"
                properties:
                  data:
                    $ref: "#/components/schemas/Project"
                  meta:
                    $ref: "#/components/schemas/ResponseMeta"
        "400":
          $ref: "#/components/responses/ValidationError"
        "401":
          $ref: "#/components/responses/Unauthorized"
        "403":
          $ref: "#/components/responses/Forbidden"
        "409":
          $ref: "#/components/responses/Conflict"
        "422":
          $ref: "#/components/responses/UnprocessableEntity"
        "429":
          $ref: "#/components/responses/RateLimited"
        "500":
          $ref: "#/components/responses/InternalError"

components:
  securitySchemes:
    BearerAuth:
      type: "http"
      scheme: "bearer"
      bearerFormat: "JWT"
      description: "JWT access token obtained from /auth/login"
    ApiKeyAuth:
      type: "apiKey"
      in: "header"
      name: "Authorization"
      description: "API key with Bearer prefix: Bearer ak_live_..."

  parameters:
    CursorParam:
      name: "cursor"
      in: "query"
      required: false
      schema:
        type: "string"
      description: "Opaque pagination cursor from previous response"
    LimitParam:
      name: "limit"
      in: "query"
      required: false
      schema:
        type: "integer"
        minimum: 1
        maximum: 100
        default: 20
      description: "Number of items per page"
    IdempotencyKey:
      name: "Idempotency-Key"
      in: "header"
      required: false
      schema:
        type: "string"
        format: "uuid"
      description: "UUID v4 for idempotent request deduplication (24h window)"

  headers:
    X-RateLimit-Limit:
      description: "Maximum requests allowed in the current window"
      schema:
        type: "integer"
    X-RateLimit-Remaining:
      description: "Requests remaining in the current window"
      schema:
        type: "integer"
    X-RateLimit-Reset:
      description: "Unix timestamp when the rate limit window resets"
      schema:
        type: "integer"

  schemas:
    Project:
      type: "object"
      required: ["id", "name", "status", "createdAt", "updatedAt"]
      properties:
        id:
          type: "string"
          example: "proj_a1b2c3d4"
          description: "Unique project identifier"
        name:
          type: "string"
          minLength: 1
          maxLength: 200
          example: "Q4 Campaign"
        description:
          type: "string"
          maxLength: 2000
          example: "End-of-year marketing push"
        status:
          type: "string"
          enum: ["draft", "active", "archived"]
          example: "active"
        tags:
          type: "array"
          items:
            type: "string"
            minLength: 1
            maxLength: 50
          maxItems: 20
          example: ["marketing", "q4"]
        createdAt:
          type: "string"
          format: "date-time"
        updatedAt:
          type: "string"
          format: "date-time"
        createdBy:
          type: "string"
          example: "usr_abc123"

    CreateProjectRequest:
      type: "object"
      required: ["name"]
      properties:
        name:
          type: "string"
          minLength: 1
          maxLength: 200
        description:
          type: "string"
          maxLength: 2000
        tags:
          type: "array"
          items:
            type: "string"
          maxItems: 20

    CursorPagination:
      type: "object"
      required: ["hasMore", "limit"]
      properties:
        hasMore:
          type: "boolean"
          description: "Whether more results exist beyond this page"
        nextCursor:
          type: "string"
          description: "Cursor to fetch the next page. Absent if hasMore is false."
        limit:
          type: "integer"

    ResponseMeta:
      type: "object"
      required: ["requestId"]
      properties:
        requestId:
          type: "string"
          example: "req_f8e7d6c5"

    ErrorResponse:
      type: "object"
      required: ["error", "code", "meta"]
      properties:
        error:
          type: "string"
          description: "Human-readable error message"
        code:
          type: "string"
          description: "Machine-readable error code (UPPER_SNAKE_CASE)"
        details:
          description: "Structured error details (validation array or context object)"
          oneOf:
            - type: "array"
              items:
                $ref: "#/components/schemas/ValidationDetail"
            - type: "object"
        meta:
          $ref: "#/components/schemas/ResponseMeta"

    ValidationDetail:
      type: "object"
      required: ["field", "message", "rule"]
      properties:
        field:
          type: "string"
          description: "Dot-notation path to the field"
          example: "config.maxRetries"
        message:
          type: "string"
          description: "Human-readable validation message"
          example: "Must be between 0 and 10"
        rule:
          type: "string"
          description: "Machine-readable rule name"
          example: "range"

  responses:
    ValidationError:
      description: "Request validation failed"
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/ErrorResponse"
          example:
            error: "Validation failed"
            code: "VALIDATION_ERROR"
            details:
              - field: "name"
                message: "Name is required"
                rule: "required"
            meta:
              requestId: "req_f8e7d6c5"
    Unauthorized:
      description: "Missing or invalid authentication"
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/ErrorResponse"
          example:
            error: "Authentication required"
            code: "UNAUTHORIZED"
            meta:
              requestId: "req_f8e7d6c5"
    Forbidden:
      description: "Insufficient permissions"
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/ErrorResponse"
          example:
            error: "You do not have permission to perform this action"
            code: "FORBIDDEN"
            meta:
              requestId: "req_f8e7d6c5"
    Conflict:
      description: "Resource state conflict"
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/ErrorResponse"
          example:
            error: "A resource with this identifier already exists"
            code: "ALREADY_EXISTS"
            meta:
              requestId: "req_f8e7d6c5"
    UnprocessableEntity:
      description: "Business rule violation"
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/ErrorResponse"
          example:
            error: "Operation cannot be completed due to business constraints"
            code: "PRECONDITION_FAILED"
            meta:
              requestId: "req_f8e7d6c5"
    RateLimited:
      description: "Rate limit exceeded"
      headers:
        Retry-After:
          description: "Seconds to wait before retrying"
          schema:
            type: "integer"
        X-RateLimit-Limit:
          $ref: "#/components/headers/X-RateLimit-Limit"
        X-RateLimit-Remaining:
          $ref: "#/components/headers/X-RateLimit-Remaining"
        X-RateLimit-Reset:
          $ref: "#/components/headers/X-RateLimit-Reset"
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/ErrorResponse"
          example:
            error: "Rate limit exceeded. Try again in 30 seconds."
            code: "RATE_LIMIT_EXCEEDED"
            meta:
              requestId: "req_f8e7d6c5"
              retryAfter: 30
    InternalError:
      description: "Unexpected server error"
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/ErrorResponse"
          example:
            error: "An unexpected error occurred. Please try again or contact support."
            code: "INTERNAL_ERROR"
            meta:
              requestId: "req_f8e7d6c5"
```

### OpenAPI Generation Checklist

When producing the OpenAPI spec for a tech spec, verify:

- [ ] `info` section: title, version, description, contact
- [ ] `servers`: at least production, staging, and local dev
- [ ] `tags`: one per resource group, with description
- [ ] Every path has `operationId` (used for SDK generation)
- [ ] Every path has appropriate `security` declaration
- [ ] All parameters use `$ref` to shared components where possible
- [ ] All request bodies have `schema` with constraints (`minLength`, `maxLength`, `minimum`, `maximum`, `enum`)
- [ ] All request bodies have `example` values
- [ ] Every endpoint documents at least: 200/201 success, 400, 401, 429, 500
- [ ] Mutating endpoints additionally document: 403, 409, 422
- [ ] Rate limit headers defined on success responses
- [ ] Error responses all use the shared `ErrorResponse` schema
- [ ] Pagination uses shared cursor/offset components

---

## Quick Reference: Complete Endpoint Checklist

Use this checklist when reviewing any endpoint in a tech spec:

| # | Check | Done? |
|---|-------|-------|
| 1 | Method + path follows REST naming conventions | |
| 2 | Description explains WHY, not just WHAT | |
| 3 | Auth requirements specified (method + roles) | |
| 4 | Rate limit defined | |
| 5 | Idempotency addressed for POST/PATCH | |
| 6 | All parameters documented (path, query, body) with types and constraints | |
| 7 | Request body has JSON schema with validation rules | |
| 8 | Request body has realistic example | |
| 9 | 200/201 response has full schema and example | |
| 10 | 400 response with validation detail array | |
| 11 | 401 response documented | |
| 12 | 403 response documented (for auth-required endpoints) | |
| 13 | 404 response documented (for endpoints with path params) | |
| 14 | 409 response documented (for creates and state-changing operations) | |
| 15 | 422 response documented (for business rule violations) | |
| 16 | 429 response documented with Retry-After | |
| 17 | 500 response documented | |
| 18 | Error responses use the standard error contract | |
| 19 | Response includes requestId in meta | |
| 20 | Pagination documented (for list endpoints) | |
