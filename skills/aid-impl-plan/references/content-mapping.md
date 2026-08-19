# Content Mapping: Source Documents → Jira Hierarchy

## The Golden Rule

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│   PRD (Phase 1)              →   EPIC & STORY    (WHY & WHAT)           │
│   Tech Spec (Phase 2)        →   TASK            (HOW)                  │
│   OpenAPI + Prisma           →   TASK details    (SPECIFICATIONS)       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Visual Content Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        SOURCE DOCUMENTS                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐                │
│  │     PRD      │   │  Tech Spec   │   │   OpenAPI    │                │
│  │  (Phase 1)   │   │  (Phase 2)   │   │   + Prisma   │                │
│  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘                │
│         │                  │                   │                         │
│         │                  │                   │                         │
│         ▼                  │                   │                         │
│  ┌──────────────┐          │                   │                         │
│  │    EPIC      │◄─────────┤                   │                         │
│  │              │          │                   │                         │
│  │ • Summary    │          │                   │                         │
│  │ • Biz Value  │          │                   │                         │
│  │ • User Impact│          │                   │                         │
│  │ • Success    │          │                   │                         │
│  │   Criteria   │          │                   │                         │
│  └──────┬───────┘          │                   │                         │
│         │                  │                   │                         │
│         ▼                  │                   │                         │
│  ┌──────────────┐          │                   │                         │
│  │    STORY     │◄─────────┤                   │                         │
│  │              │          │                   │                         │
│  │ • User Story │          │                   │                         │
│  │ • Acceptance │          │                   │                         │
│  │   Criteria   │          │                   │                         │
│  │ • API List   │◄─────────┘                   │                         │
│  │ • DoD        │                              │                         │
│  └──────┬───────┘                              │                         │
│         │                                      │                         │
│         ▼                                      │                         │
│  ┌──────────────┐                              │                         │
│  │    TASK      │◄─────────────────────────────┘                         │
│  │              │                                                        │
│  │ • Tech Impl  │  (FROM TECH SPEC)                                     │
│  │ • Code Pattern│ (FROM OPENAPI)                                       │
│  │ • API Contract│ (FROM OPENAPI)                                       │
│  │ • DB Changes │  (FROM PRISMA)                                        │
│  │ • Error Cases│  (FROM OPENAPI)                                       │
│  │ • File Paths │  (FROM IMPL PLAN)                                     │
│  └──────────────┘                                                        │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Detailed Mapping Tables

### PRD → Epic

| PRD Element | Epic Field | Notes |
|-------------|------------|-------|
| Product Goals | Business Value | Why this epic matters |
| Target Personas | User Impact | Who benefits |
| Success Metrics | Success Criteria | Measurable outcomes |
| Feature Scope | Summary | What's included |
| Out of Scope | (exclude) | What's NOT included |
| Timeline Goals | Estimated Duration | Sprint/week estimate |

**Example:**
```
PRD Section: "2.1 Product Goals"
→ Epic Field: "Business Value"
→ Content: "Reduce user onboarding time by 50% through streamlined registration"
```

### PRD → Story

| PRD Element | Story Field | Notes |
|-------------|-------------|-------|
| User Story | User Story | As a... I want... So that... |
| Acceptance Criteria | Acceptance Criteria | Convert to Gherkin |
| UI Requirements | Design References | Wireframes, mockups |
| User Flow | Context | How user gets here |
| Edge Cases | AC (error scenarios) | Given error... Then... |

**Example:**
```
PRD: "As a user, I want to register with email so I can access the platform"
→ Story: User Story field (verbatim)
→ Story: AC in Gherkin (Given no account, When submit form, Then account created)
```

### Tech Spec → Story (Partial)

| Tech Spec Element | Story Field | Notes |
|-------------------|-------------|-------|
| API Endpoints | API Endpoints table | List of routes |
| Security Requirements | Non-Functional Reqs | Auth, validation |
| Performance Targets | Non-Functional Reqs | Response times |

### Tech Spec → Task

| Tech Spec Element | Task Field | Notes |
|-------------------|------------|-------|
| Architecture Decisions | Technical Details | Why this approach |
| Component Design | Implementation Approach | Step-by-step |
| Error Handling | Error Handling table | All error cases |
| Security Implementation | Technical Details | How to secure |

### OpenAPI → Task

| OpenAPI Element | Task Field | Notes |
|-----------------|------------|-------|
| Path + Method | API Contract | POST /api/v1/users |
| Request Body Schema | Code Pattern | TypeScript interface |
| Response Schema | Acceptance Criteria | What to return |
| Error Responses | Error Handling table | 400, 401, 404, etc. |
| Security Schemes | Technical Details | Bearer token, API key |
| Parameters | API Contract | Path, query params |

**Example:**
```yaml
# OpenAPI
/api/v1/users:
  post:
    requestBody:
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/CreateUserRequest'
    responses:
      '201':
        description: User created
      '400':
        description: Validation error

# → Task: API Contract
POST /api/v1/users
Request: { name: string, email: string, password: string }
Response: { id: string, name: string, email: string }
Errors: 400 (validation), 409 (email exists)
```

### Prisma Schema → Task

| Prisma Element | Task Field | Notes |
|----------------|------------|-------|
| Model Definition | Database Changes | Table structure |
| Field Types | Code Pattern | TypeScript types |
| Relations | Dependencies | Related tasks |
| Validations | Acceptance Criteria | Constraints to enforce |

**Example:**
```prisma
model User {
  id        String   @id @default(uuid())
  email     String   @unique
  password  String
  createdAt DateTime @default(now())
}

# → Task: Database Changes
Table: users
Fields: id (UUID, PK), email (unique), password, createdAt
Migration: Yes - create users table
```

---

## Hierarchy Enforcement Rules

### CRITICAL: Never Skip Levels

```
WRONG:                          RIGHT:
Epic → Task (flat)              Epic → Story → Task (proper)

EPIC-1                          EPIC-1
├── Task 1                      └── Story 1.1
├── Task 2                          ├── Task 1.1.1
├── Task 3                          ├── Task 1.1.2
└── Task 4                          └── Task 1.1.3
                                └── Story 1.2
                                    ├── Task 1.2.1
                                    └── Task 1.2.2
```

### Why Stories Matter

| Without Stories | With Stories |
|-----------------|--------------|
| Flat list of tasks | Grouped by user capability |
| No business context | Clear "why" for each group |
| Hard to prioritize | Can prioritize stories |
| No acceptance testing | Story = testable increment |
| Overwhelms developers | Manageable chunks |

### Story Grouping Principle

**Group tasks by USER CAPABILITY, not technical layer:**

```
WRONG (technical grouping):     RIGHT (capability grouping):

Story: Database Tasks           Story: User Registration
├── Create users table          ├── Create signup endpoint
├── Create projects table       ├── Create users table
└── Create sessions table       ├── Create signup form
                                └── Write registration tests

Story: API Tasks                Story: User Login
├── Create signup endpoint      ├── Create login endpoint
├── Create login endpoint       ├── Implement JWT generation
└── Create project endpoint     ├── Create login form
                                └── Write login tests
```

---

## Content Mapping Checklist

### Before Populating Jira

- [ ] **PRD Mapped to Epics**
  - [ ] Each product goal → Epic business value
  - [ ] Each persona → Epic user impact
  - [ ] Each success metric → Epic success criteria

- [ ] **PRD Mapped to Stories**
  - [ ] Each user story → Story (verbatim)
  - [ ] Each AC → Gherkin format
  - [ ] Each UI requirement → Design reference

- [ ] **Tech Spec Mapped to Tasks**
  - [ ] Each component → Task(s)
  - [ ] Each API endpoint → Task with contract
  - [ ] Each security requirement → Task with details

- [ ] **OpenAPI Mapped to Tasks**
  - [ ] Each path → Task API contract
  - [ ] Each schema → Task code pattern
  - [ ] Each error → Task error handling

- [ ] **No Orphan Content**
  - [ ] Every PRD section traced
  - [ ] Every Tech Spec section traced
  - [ ] Every OpenAPI path traced
  - [ ] Every Prisma model traced

---

## Traceability Matrix Template

| PRD Ref | Tech Spec Ref | OpenAPI | Prisma | Epic | Story | Task |
|---------|---------------|---------|--------|------|-------|------|
| US-01 | 4.1 | POST /auth/signup | User | E2 | S2.1 | T2.1.1-3 |
| US-02 | 4.2 | POST /auth/login | User | E2 | S2.2 | T2.2.1-2 |
| US-03 | 5.1 | GET /projects | Project | E3 | S3.1 | T3.1.1-4 |

Use this matrix to verify 100% coverage before populating Jira.

---

## Common Mapping Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Copying PRD text to Task | Too high-level | PRD → Epic/Story, Tech Spec → Task |
| Tech Spec text in Epic | Too technical | Tech Spec → Task, PRD → Epic |
| No code examples in Task | Developer guesses | Add OpenAPI/Prisma content |
| Missing error handling | Only happy path | Add error table from OpenAPI |
| No file paths | Where to code? | Add from Tech Spec or infer |
| Vague acceptance criteria | Can't test | Use Gherkin (Given/When/Then) |
