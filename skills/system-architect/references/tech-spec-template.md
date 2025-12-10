# Technical Specification Template

## Document Info
- **Feature:** [Feature Name]
- **Author:** [Name]
- **Date:** [YYYY-MM-DD]
- **Status:** Draft | In Review | Approved | Implemented
- **Reviewers:** [List]

---

## 1. Problem Statement

### User Problem
[What user pain point are we solving?]

### Business Context
[Why is this important now? What's the business driver?]

### Success Metrics
- [ ] Metric 1: [Target value]
- [ ] Metric 2: [Target value]

---

## 2. Proposed Solution

### High-Level Approach
[2-3 paragraphs explaining the solution at a conceptual level]

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| [Decision 1] | [Choice] | [Why] |
| [Decision 2] | [Choice] | [Why] |

### Alternatives Considered

#### Alternative 1: [Name]
- **Pros:** [List]
- **Cons:** [List]
- **Rejected because:** [Reason]

---

## 3. Technical Design

### System Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│   API       │────▶│  Database   │
└─────────────┘     └─────────────┘     └─────────────┘
```

### Component Breakdown

#### Component 1: [Name]
- **Responsibility:** [What it does]
- **Interface:** [How other components interact with it]
- **Dependencies:** [What it depends on]

#### Component 2: [Name]
[Same structure]

---

## 4. API Contracts

### Endpoint: POST /api/v1/[resource]

**Request:**
```typescript
interface CreateResourceRequest {
  name: string;
  type: 'type_a' | 'type_b';
  metadata?: Record<string, unknown>;
}
```

**Response (200 OK):**
```typescript
interface CreateResourceResponse {
  id: string;
  name: string;
  type: string;
  createdAt: string;
  updatedAt: string;
}
```

**Error Responses:**
| Status | Code | Description |
|--------|------|-------------|
| 400 | VALIDATION_ERROR | Invalid request body |
| 409 | CONFLICT | Resource already exists |
| 500 | INTERNAL_ERROR | Server error |

---

## 5. Data Model

### New Tables

```sql
CREATE TABLE resources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT valid_type CHECK (type IN ('type_a', 'type_b'))
);

CREATE INDEX idx_resources_type ON resources(type);
CREATE INDEX idx_resources_created_at ON resources(created_at);
```

### Schema Changes
- [ ] New table: `resources`
- [ ] New index: `idx_resources_type`

### Migration Strategy
1. Deploy new schema (backwards compatible)
2. Deploy application code
3. Run data migration (if needed)
4. Clean up old columns (if any)

---

## 6. Dependencies

### External Services
| Service | Purpose | SLA | Fallback |
|---------|---------|-----|----------|
| [Service] | [Purpose] | [SLA] | [Fallback behavior] |

### Libraries
| Library | Version | Purpose |
|---------|---------|---------|
| [Library] | [Version] | [Purpose] |

---

## 7. Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| [Risk 1] | High/Medium/Low | High/Medium/Low | [Mitigation strategy] |
| [Risk 2] | High/Medium/Low | High/Medium/Low | [Mitigation strategy] |

---

## 8. Testing Strategy

### Unit Tests
- [ ] [Component 1] - [Test scenarios]
- [ ] [Component 2] - [Test scenarios]

### Integration Tests
- [ ] API endpoint tests with real database
- [ ] External service integration tests

### End-to-End Tests
- [ ] Full user flow: [Description]

---

## 9. Rollout Plan

### Phase 1: Internal Testing
- **Duration:** [X days]
- **Scope:** Internal users only
- **Success criteria:** [Metrics]

### Phase 2: Beta
- **Duration:** [X days]
- **Scope:** [X% of users]
- **Success criteria:** [Metrics]

### Phase 3: General Availability
- **Duration:** [X days]
- **Scope:** All users
- **Success criteria:** [Metrics]

### Rollback Plan
1. [Step 1]
2. [Step 2]
3. [Step 3]

---

## 10. Security Considerations

- [ ] Authentication required for all endpoints
- [ ] Authorization checks implemented
- [ ] Input validation on all user inputs
- [ ] Sensitive data encrypted at rest
- [ ] Audit logging implemented

---

## 11. Monitoring & Alerting

### Metrics to Track
- [ ] Request latency (p50, p95, p99)
- [ ] Error rate
- [ ] Throughput (requests/second)
- [ ] [Custom metric]

### Alerts
| Alert | Condition | Severity | Action |
|-------|-----------|----------|--------|
| High error rate | > 1% errors | Critical | Page on-call |
| High latency | p99 > 2s | Warning | Slack notification |

---

## Appendix

### Glossary
- **Term 1:** Definition
- **Term 2:** Definition

### References
- [Link to related docs]
- [Link to design files]
