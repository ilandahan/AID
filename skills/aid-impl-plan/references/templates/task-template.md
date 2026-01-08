# Task Template

## Task Hierarchy

```
EPIC-{N}: {Domain}
└── Story {N}.{S}: {Capability}
    └── Task E{N}-T{##}: {Specific Implementation}
```

**Critical Rule**: Tasks are TECHNICAL. A developer should be able to work from a task description without asking questions.

---

## Task Naming Convention

### Format
```
E{Epic#}-T{Sequential##}: {Action Verb} {Component/Feature}
```

**Examples:**
- E2-T01: Create User Registration Endpoint
- E2-T05: Implement JWT Token Generation
- E8-T14: Create Role Selection Component
- E1-T13: Configure API Rate Limiting

### Action Verbs by Task Type

| Type | Verbs |
|------|-------|
| Creation | Create, Build, Implement, Add |
| Modification | Update, Refactor, Enhance, Extend |
| Configuration | Configure, Set up, Initialize |
| Integration | Connect, Integrate, Wire up |
| Testing | Write tests for, Add test coverage |
| Documentation | Document, Add comments to |

---

## Task Description Template (Jira-Ready)

```markdown
## Task E{N}-T{##}: {Title}

**Type**: {Feature | Bug | Refactor | Configuration | Test | Documentation}

### Description
{2-3 sentences describing what needs to be built and why}

### Technical Details

**File(s) to create/modify:**
- `{path/to/file1.ts}` - {what to do}
- `{path/to/file2.ts}` - {what to do}

**Implementation Approach:**
{Step-by-step approach or pseudocode}

1. {Step 1}
2. {Step 2}
3. {Step 3}

**Code Pattern/Example:**
```{language}
// Example implementation or pattern to follow
{code snippet}
```

**API Contract (if applicable):**
```
{Method} {Endpoint}
Request: {schema or example}
Response: {schema or example}
Errors: {error codes and meanings}
```

**Database Changes (if applicable):**
- Table: `{table_name}`
- Fields: `{field1}`, `{field2}`
- Migration: {Yes/No}

### Dependencies
- **Blocked by**: {Task IDs that must complete first}
- **Related to**: {Task IDs that share code/context}

### Acceptance Criteria
{Specific, testable outcomes - NOT Gherkin, more technical}
- [ ] {Criterion 1 - e.g., "Endpoint returns 200 with valid input"}
- [ ] {Criterion 2 - e.g., "Password hashed with bcrypt cost 12"}
- [ ] {Criterion 3 - e.g., "Error 400 returned for missing email"}
- [ ] {Criterion 4 - e.g., "Unit tests cover happy path and 2 error cases"}

### Error Handling
| Error Case | Response | Action |
|------------|----------|--------|
| {Case 1} | {HTTP code} | {What happens} |
| {Case 2} | {HTTP code} | {What happens} |

### Testing Requirements
- [ ] Unit tests for {component/function}
- [ ] Integration test for {flow}
- [ ] Edge case: {specific edge case}

### Size Estimate
**{XS | S | M | L | XL}** (~{N} hours)

| Size | Hours | Complexity |
|------|-------|------------|
| XS | < 2 | Config, copy change |
| S | 2-4 | Single function/component |
| M | 4-8 | Feature with tests |
| L | 8-16 | Complex feature |
| XL | 16+ | Consider splitting |

### Tech Spec References
- Section: {Tech Spec section number}
- API: {OpenAPI path}
- Model: {Prisma model name}

### Notes for Developer
{Any gotchas, tips, or context that would help}
- {Note 1}
- {Note 2}
```

---

## Content Mapping Rules

### What Goes in Task (FROM TECH SPEC)

| Tech Spec Element | Task Field |
|-------------------|------------|
| API endpoint definition | API Contract |
| Request/response schemas | Code Pattern |
| Database schema | Database Changes |
| Security implementation | Technical Details |
| Error codes | Error Handling |

### What Goes in Task (FROM OPENAPI)

| OpenAPI Element | Task Field |
|-----------------|------------|
| Path + Method | API Contract |
| Request body schema | Code Pattern |
| Response schema | Acceptance Criteria |
| Error responses | Error Handling |
| Security schemes | Technical Details |

### What Goes in Task (FROM IMPLEMENTATION PLAN)

| Impl Plan Element | Task Field |
|-------------------|------------|
| File paths | Files to create/modify |
| Code examples | Code Pattern |
| Dependencies | Dependencies |
| Size estimate | Size Estimate |

---

## Task Types

### Feature Task
```markdown
**Type**: Feature

Create new functionality. Includes:
- New endpoint, component, or function
- User-facing capability
- Business logic implementation
```

### Configuration Task
```markdown
**Type**: Configuration

Setup or configuration. Includes:
- Environment variables
- Cloud resource provisioning
- Third-party service setup
- Security configuration (CORS, rate limits)
```

### Integration Task
```markdown
**Type**: Integration

Connect systems/components. Includes:
- API integrations
- WebSocket connections
- Database connections
- External service wiring
```

### Test Task
```markdown
**Type**: Test

Testing work. Includes:
- Unit test suites
- Integration tests
- E2E test scenarios
- Performance tests
```

---

## Task Granularity Guide

### Too Big (Split It)
- "Implement authentication" → Split into signup, login, logout, refresh
- "Build dashboard" → Split into layout, components, data fetching
- Takes more than 2 days → Definitely split

### Too Small (Combine It)
- "Add import statement" → Combine with related work
- "Fix typo" → Not worth a task unless critical
- Takes less than 30 minutes → Combine with related task

### Just Right
- "Create login endpoint with JWT" → Specific, 4-8 hours
- "Build role selection component" → Specific, testable
- "Configure Cloud SQL connection" → Clear scope

---

## Task Dependencies

### Dependency Types

```markdown
### Dependencies
- **Hard Block**: Cannot start until {TASK-ID} completes
- **Soft Block**: Could start, but {TASK-ID} provides context
- **Shared Code**: Modifies same files as {TASK-ID}
```

### Dependency Visualization

```
E1-T01: GCP Project Setup
    │
    ├──► E1-T02: Secret Manager Setup
    │        │
    │        └──► E2-T01: Auth Function Setup
    │
    └──► E1-T03: Cloud SQL Setup
             │
             └──► E2-T02: Prisma Schema
```

---

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Vague tasks | "Make it work" | Specific acceptance criteria |
| No file paths | Developer doesn't know where | Always list files |
| No code examples | Developer reinvents wheel | Provide patterns |
| Missing error handling | Only happy path | Include error table |
| No size estimate | Can't plan sprint | Always estimate |
| Copy-paste specs | Duplicated content | Reference, don't copy |
| Tech jargon without context | Confusing | Explain why, not just what |
