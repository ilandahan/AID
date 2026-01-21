# Technical Specification Template

## Document Info
- **Feature:** [Feature Name]
- **Author:** [Name]
- **Date:** YYYY-MM-DD
- **Status:** Draft | In Review | Approved | Implemented
- **Reviewers:** [List]
- **PRD Reference:** docs/prd/YYYY-MM-DD-[feature].md

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

## 2. Security Assessment

### Data Classification

| Data Element | Classification | Handling Requirements |
|-------------|---------------|----------------------|
| [Element 1] | PUBLIC / INTERNAL / CONFIDENTIAL / RESTRICTED | [Requirements] |
| [Element 2] | [Classification] | [Requirements] |

```
Classification Levels:
- PUBLIC: No restrictions
- INTERNAL: Employees only
- CONFIDENTIAL: Need-to-know, encrypted at rest
- RESTRICTED: Highest sensitivity, field-level encryption, MFA required
```

### Threat Model

| Threat | Impact | Likelihood | Mitigation |
|--------|--------|------------|------------|
| Unauthorized access | High | Medium | OAuth2 + RBAC |
| Data breach | High | Low | Encryption, audit logs |
| Injection attacks | High | Medium | Input validation, parameterized queries |
| [Threat] | [Impact] | [Likelihood] | [Mitigation] |

### Compliance Requirements

| Requirement | Applicable | Implementation |
|-------------|-----------|----------------|
| ISO 27001 A.9 (Access Control) | Yes/No | [Details] |
| ISO 27001 A.10 (Cryptography) | Yes/No | [Details] |
| ISO 27001 A.12 (Operations) | Yes/No | [Details] |
| GDPR (if PII involved) | Yes/No | [Details] |
| [Other] | Yes/No | [Details] |

---

## 3. Proposed Solution

### High-Level Approach
[2-3 paragraphs explaining the solution at a conceptual level]

### Key Design Decisions

| Decision | Choice | Rationale | Security Impact |
|----------|--------|-----------|-----------------|
| [Decision 1] | [Choice] | [Why] | [Security notes] |
| [Decision 2] | [Choice] | [Why] | [Security notes] |

### Alternatives Considered

#### Alternative 1: [Name]
- **Pros:** [List]
- **Cons:** [List]
- **Security Concerns:** [List]
- **Rejected because:** [Reason]

---

## 4. Technical Design

### System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      SECURITY LAYERS                          │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐                                             │
│  │    WAF      │  ← DDoS protection, OWASP rules            │
│  └──────┬──────┘                                             │
│         ▼                                                     │
│  ┌─────────────┐                                             │
│  │ API Gateway │  ← Rate limiting, JWT validation           │
│  └──────┬──────┘                                             │
│         ▼                                                     │
│  ┌─────────────┐                                             │
│  │ Application │  ← Business logic, authorization           │
│  └──────┬──────┘                                             │
│         ▼                                                     │
│  ┌─────────────┐                                             │
│  │  Database   │  ← RLS, encryption at rest                 │
│  └─────────────┘                                             │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Component Breakdown

#### Component 1: [Name]
- **Responsibility:** [What it does]
- **Interface:** [How other components interact with it]
- **Dependencies:** [What it depends on]
- **Security Requirements:**
  - Authentication: [Required/Not required]
  - Authorization: [RBAC rules]
  - Data handling: [Encryption, classification]

#### Component 2: [Name]
[Same structure]

---

## 5. API Contracts

### Authentication Requirements

| Endpoint Pattern | Auth Type | Roles Allowed |
|-----------------|-----------|---------------|
| `/api/v1/public/*` | None | All |
| `/api/v1/user/*` | JWT | authenticated |
| `/api/v1/admin/*` | JWT + MFA | admin |

### Endpoint: POST /api/v1/[resource]

**Authentication:** JWT required
**Authorization:** `resource:create` permission

**Request:**
```typescript
interface CreateResourceRequest {
  name: string;
  type: 'type_a' | 'type_b';
  metadata?: Record<string, unknown>;
}
```

**Response (201 Created):**
```typescript
interface CreateResourceResponse {
  id: string;
  name: string;
  type: string;
  createdAt: string; // ISO 8601
  updatedAt: string;
}
```

**Error Responses:**

| Status | Code | Description | Audit Log |
|--------|------|-------------|-----------|
| 400 | VALIDATION_ERROR | Invalid request body | No |
| 401 | UNAUTHORIZED | Missing/invalid token | Yes |
| 403 | FORBIDDEN | Insufficient permissions | Yes |
| 409 | CONFLICT | Resource already exists | No |
| 429 | RATE_LIMITED | Too many requests | Yes |
| 500 | INTERNAL_ERROR | Server error | Yes |

### Rate Limiting

| Endpoint | Limit | Window | Scope |
|----------|-------|--------|-------|
| `/api/v1/*` | 100 | 1 min | Per user |
| `/api/v1/auth/login` | 5 | 15 min | Per IP |
| `/api/v1/admin/*` | 50 | 1 min | Per user |

---

## 6. Data Model

### TypeScript Interfaces

```typescript
// Data classification decorator
type Classification = 'public' | 'internal' | 'confidential' | 'restricted';

interface Resource {
  id: string;                    // Classification: internal
  name: string;                  // Classification: internal
  type: 'type_a' | 'type_b';     // Classification: internal
  metadata: Record<string, unknown>; // Classification: confidential

  // Audit fields
  createdAt: Date;
  updatedAt: Date;
  createdBy: string;             // User ID
  updatedBy: string;             // User ID
}
```

### Database Schema

```sql
-- Enable row-level security
ALTER TABLE resources ENABLE ROW LEVEL SECURITY;

CREATE TABLE resources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,

    -- Encrypted column for sensitive data
    metadata BYTEA, -- Encrypted JSONB (AES-256)

    -- Tenant isolation (ISO 27001 A.9)
    tenant_id UUID NOT NULL REFERENCES tenants(id),

    -- Audit trail (ISO 27001 A.12)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID NOT NULL REFERENCES users(id),
    updated_by UUID NOT NULL REFERENCES users(id),

    -- Soft delete for audit compliance
    deleted_at TIMESTAMPTZ,
    deleted_by UUID REFERENCES users(id),

    CONSTRAINT valid_type CHECK (type IN ('type_a', 'type_b'))
);

-- Row-level security policy (ISO 27001 A.9.4)
CREATE POLICY tenant_isolation ON resources
    FOR ALL
    USING (tenant_id = current_setting('app.tenant_id')::uuid);

-- Indexes
CREATE INDEX idx_resources_tenant ON resources(tenant_id);
CREATE INDEX idx_resources_type ON resources(type) WHERE deleted_at IS NULL;
CREATE INDEX idx_resources_created_at ON resources(created_at);

-- Audit trigger
CREATE TRIGGER resources_audit
    AFTER INSERT OR UPDATE OR DELETE ON resources
    FOR EACH ROW EXECUTE FUNCTION audit_log();
```

### Encryption Requirements

| Column | Encryption | Key Management |
|--------|-----------|----------------|
| `metadata` | AES-256-GCM | AWS KMS |
| `email` (if exists) | AES-256-GCM | AWS KMS |
| `*` (at rest) | AES-256 | RDS encryption |

### Migration Strategy
1. Deploy new schema (backwards compatible)
2. Deploy application code
3. Run data migration (if needed)
4. Validate data integrity
5. Clean up old columns (if any)

---

## 7. Security Controls

### Authentication Flow

```
┌────────┐     ┌──────────┐     ┌─────────┐     ┌─────────┐
│ Client │────▶│ Auth0/   │────▶│   API   │────▶│   App   │
│        │     │ Cognito  │     │ Gateway │     │         │
└────────┘     └──────────┘     └─────────┘     └─────────┘
     │              │                │               │
     │  1. Login    │                │               │
     │─────────────▶│                │               │
     │              │                │               │
     │  2. JWT      │                │               │
     │◀─────────────│                │               │
     │              │                │               │
     │  3. Request with JWT          │               │
     │──────────────────────────────▶│               │
     │                               │  4. Validate  │
     │                               │──────────────▶│
     │                               │               │
     │                               │  5. Response  │
     │◀──────────────────────────────────────────────│
```

### Authorization (RBAC)

| Role | Permissions | Resources |
|------|-------------|-----------|
| `viewer` | `read` | Own tenant data |
| `editor` | `read`, `write` | Own tenant data |
| `admin` | `read`, `write`, `delete` | Own tenant data |
| `super_admin` | `*` | All data (requires MFA) |

### Resource-Level Authorization

```typescript
// Every endpoint must check:
async function authorize(user: User, action: Action, resource: Resource): Promise<boolean> {
  // 1. Check user has required role
  if (!user.roles.includes(getRequiredRole(action))) {
    auditLog('FORBIDDEN', { user, action, resource });
    return false;
  }

  // 2. Check tenant isolation
  if (resource.tenantId !== user.tenantId) {
    auditLog('TENANT_VIOLATION', { user, action, resource });
    return false;
  }

  // 3. Check resource-specific rules
  return checkResourceRules(user, action, resource);
}
```

### Audit Logging

| Event | Data Captured | Retention |
|-------|--------------|-----------|
| Authentication | User ID, IP, success/fail, timestamp | 2 years |
| Authorization failure | User ID, resource, action, reason | 2 years |
| Data access | User ID, resource type, query | 1 year |
| Data modification | User ID, resource, before/after | 7 years |
| Admin actions | User ID, action, target, timestamp | 7 years |

---

## 8. ISO 27001 Compliance

### Applicable Controls

| Control | Requirement | Implementation | Status |
|---------|------------|----------------|--------|
| **A.8.2** Information Classification | Classify all data | Classification tags on entities | [ ] |
| **A.9.1** Access Control Policy | Define access rules | RBAC implementation | [ ] |
| **A.9.2** User Access Management | Provision/deprovision | Automated via IAM | [ ] |
| **A.9.4** System Access Control | Restrict access | JWT + RLS | [ ] |
| **A.10.1** Cryptographic Controls | Encrypt sensitive data | AES-256 + TLS 1.3 | [ ] |
| **A.12.4** Logging and Monitoring | Audit all access | Centralized logging | [ ] |
| **A.14.2** Secure Development | Secure SDLC | SAST/DAST in CI/CD | [ ] |
| **A.18.1** Compliance | Meet legal requirements | Audit trails | [ ] |

### Implementation Checklist

- [ ] All data elements classified
- [ ] RBAC roles and permissions defined
- [ ] Encryption implemented for CONFIDENTIAL+ data
- [ ] Audit logging enabled for all security events
- [ ] Row-level security enabled on all tenant data
- [ ] Secrets stored in AWS Secrets Manager
- [ ] Security scanning in CI/CD pipeline

---

## 9. Dependencies

### External Services

| Service | Purpose | SLA | Security | Fallback |
|---------|---------|-----|----------|----------|
| Auth0 | Authentication | 99.9% | SOC2, ISO27001 | Cached tokens |
| AWS KMS | Key management | 99.99% | FIPS 140-2 | None (critical) |
| [Service] | [Purpose] | [SLA] | [Certifications] | [Fallback] |

### Libraries

| Library | Version | Purpose | Security Notes |
|---------|---------|---------|----------------|
| jose | ^5.0.0 | JWT handling | Well-maintained |
| bcrypt | ^5.0.0 | Password hashing | Use cost factor 12+ |
| [Library] | [Version] | [Purpose] | [Notes] |

---

## 10. Risks & Mitigations

### Security Risks

| Risk | Impact | Probability | Mitigation | Owner |
|------|--------|-------------|------------|-------|
| Token theft | High | Medium | Short expiry, refresh rotation | Security |
| SQL injection | High | Low | Parameterized queries, ORM | Backend |
| Data breach | High | Low | Encryption, audit logs | Security |
| Insider threat | High | Low | Least privilege, audit trails | Security |

### Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Database migration failure | High | Low | Test in staging, rollback plan |
| Performance degradation | Medium | Medium | Load testing, caching |
| Third-party service outage | Medium | Low | Fallback behaviors |

---

## 11. Testing Strategy

### Security Testing
- [ ] SAST scan (SonarQube/Semgrep)
- [ ] Dependency vulnerability scan (Snyk)
- [ ] DAST scan (OWASP ZAP)
- [ ] Penetration testing (manual)
- [ ] Authentication bypass testing
- [ ] Authorization testing (horizontal/vertical)
- [ ] Injection testing

### Unit Tests
- [ ] [Component 1] - [Test scenarios]
- [ ] [Component 2] - [Test scenarios]

### Integration Tests
- [ ] API endpoint tests with authentication
- [ ] Authorization tests (RBAC)
- [ ] Database integration with RLS

### End-to-End Tests
- [ ] Full user flow: [Description]
- [ ] Error scenarios: [Description]

---

## 12. Rollout Plan

### Phase 1: Internal Testing
- **Duration:** [X days]
- **Scope:** Internal users only
- **Security:** Full audit logging enabled
- **Success criteria:** [Metrics]

### Phase 2: Beta
- **Duration:** [X days]
- **Scope:** [X% of users]
- **Security:** Monitor for anomalies
- **Success criteria:** [Metrics]

### Phase 3: General Availability
- **Duration:** [X days]
- **Scope:** All users
- **Security:** 24/7 monitoring
- **Success criteria:** [Metrics]

### Rollback Plan
1. Disable feature flag
2. Revert API deployment
3. Revert database changes (if needed)
4. Notify security team
5. Incident analysis

### Rollback Triggers
- Error rate > 1%
- Security incident detected
- Data integrity issues
- Performance degradation > 50%

---

## 13. Monitoring & Alerting

### Security Metrics

| Metric | Threshold | Severity | Action |
|--------|-----------|----------|--------|
| Failed auth attempts | > 10/min per IP | Warning | Auto-block IP |
| Failed auth attempts | > 100/min total | Critical | Page on-call |
| Authorization failures | > 5/min per user | Warning | Review access |
| Unusual data access | > 2 std dev | Warning | Investigate |

### Performance Metrics

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| p50 latency | < 100ms | > 200ms |
| p99 latency | < 500ms | > 1000ms |
| Error rate | < 0.1% | > 1% |
| Availability | 99.9% | < 99.5% |

### Alerts

| Alert | Condition | Severity | Action |
|-------|-----------|----------|--------|
| High error rate | > 1% errors | Critical | Page on-call |
| High latency | p99 > 2s | Warning | Slack notification |
| Security anomaly | Unusual pattern | Critical | Security team |
| Auth failures spike | > 5x baseline | Critical | Page security |

---

## Appendix

### Glossary
- **RLS:** Row-Level Security
- **RBAC:** Role-Based Access Control
- **MFA:** Multi-Factor Authentication
- **PII:** Personally Identifiable Information

### References
- [ISO 27001:2022 Controls](https://www.iso.org/standard/27001)
- [OWASP Top 10](https://owasp.org/Top10/)
- [Link to PRD]
- [Link to design files]
