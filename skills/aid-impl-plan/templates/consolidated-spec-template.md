# Consolidated Specification: [Feature Name]

**Date:** YYYY-MM-DD
**Version:** 1.0
**Status:** [Draft | Approved]

---

## Document Information

| Field | Value |
|-------|-------|
| Feature | [Feature Name] |
| Project | [Project Name] |
| Author | [Name] |
| Approved By | [Name] |
| Approval Date | [Date] |

### Source Documents

| Document | Path | Date |
|----------|------|------|
| PRD | `docs/prd/YYYY-MM-DD-[feature].md` | [Date] |
| Tech Spec | `docs/tech-spec/YYYY-MM-DD-[feature].md` | [Date] |
| Research | `docs/research/[feature]-research.md` | [Date or N/A] |

---

## Contradiction Resolution Summary

### Resolution Statistics

| Category | Found | Resolved |
|----------|-------|----------|
| Critical | [N] | [N] |
| High | [N] | [N] |
| Low | [N] | [N] |
| **Total** | **[N]** | **[N]** |

### Resolved Contradictions

#### Contradiction #1: [Title]

- **Found In:** [PRD Section] vs [Tech Spec Section]
- **Description:** [What conflicts]
- **Resolution:** [How resolved]
- **Authority Used:** [Research/PRD/Tech Spec]
- **Rationale:** [Why this decision]

> [RESOLVED] - Original text preserved below for reference:
> - PRD stated: "[original text]"
> - Tech Spec stated: "[original text]"
> - **Final Decision:** "[resolved text]"

<!-- Repeat for each contradiction -->

---

## 1. Executive Summary

### 1.1 Problem Statement
<!-- From PRD -->
[Problem description]

### 1.2 Solution Overview
<!-- From Tech Spec -->
[Solution description]

### 1.3 Success Metrics
<!-- From PRD -->
- [ ] [Metric 1]: [Target]
- [ ] [Metric 2]: [Target]
- [ ] [Metric 3]: [Target]

---

## 2. User Stories & Requirements

### 2.1 User Personas
<!-- From PRD -->

#### Persona: [Name]
- **Role:** [Role]
- **Goals:** [Goals]
- **Pain Points:** [Pain points]

### 2.2 User Stories

#### US-001: [Story Title]

**As a** [persona]
**I want** [capability]
**So that** [benefit]

**Acceptance Criteria:**
- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

**Technical Notes:**
<!-- From Tech Spec -->
[Implementation details]

**Priority:** [Must Have | Should Have | Could Have | Won't Have]
**Story Points:** [N]

<!-- Repeat for each user story -->

---

## 3. Functional Requirements

### 3.1 [Feature Area 1]

#### FR-001: [Requirement Title]

**Description:** [Detailed description]

**Business Rule:**
<!-- From PRD -->
[Business logic]

**Technical Implementation:**
<!-- From Tech Spec -->
[How to implement]

**Validation Rules:**
- [Rule 1]
- [Rule 2]

**Error Handling:**
- [Error scenario 1]: [Response]
- [Error scenario 2]: [Response]

<!-- Repeat for each requirement -->

---

## 4. Non-Functional Requirements

### 4.1 Performance

| Metric | Requirement | Source |
|--------|-------------|--------|
| Response Time | [< X ms] | [PRD/Tech Spec] |
| Throughput | [X req/sec] | [PRD/Tech Spec] |
| Concurrent Users | [X users] | [PRD/Tech Spec] |

### 4.2 Security

| Requirement | Implementation | Source |
|-------------|----------------|--------|
| Authentication | [Method] | [Tech Spec] |
| Authorization | [Model] | [Tech Spec] |
| Data Encryption | [Standard] | [Tech Spec] |
| Compliance | [Standards] | [PRD] |

### 4.3 Scalability

[Scalability requirements and approach]

### 4.4 Availability

| Metric | Target |
|--------|--------|
| Uptime | [X%] |
| RTO | [X hours] |
| RPO | [X hours] |

---

## 5. System Architecture

### 5.1 Architecture Overview
<!-- From Tech Spec -->

```mermaid
[Architecture diagram]
```

### 5.2 Component Descriptions

#### Component: [Name]
- **Purpose:** [Why it exists]
- **Responsibilities:** [What it does]
- **Interfaces:** [How it connects]
- **Technology:** [Stack/framework]

<!-- Repeat for each component -->

### 5.3 Data Flow

```mermaid
[Data flow diagram]
```

---

## 6. Data Models

### 6.1 Entity Relationship Diagram

```mermaid
[ERD diagram]
```

### 6.2 Data Entities

#### Entity: [Name]

```typescript
interface [EntityName] {
  id: string;
  // ... all fields
  createdAt: Date;
  updatedAt: Date;
}
```

**Field Descriptions:**

| Field | Type | Required | Description | Business Rule |
|-------|------|----------|-------------|---------------|
| id | string | Yes | Unique identifier | UUID v4 |
| [field] | [type] | [Yes/No] | [Description] | [Rule] |

<!-- Repeat for each entity -->

---

## 7. API Contracts

### 7.1 API Overview

| Endpoint | Method | Purpose | Auth Required |
|----------|--------|---------|---------------|
| `/api/v1/[resource]` | GET | [Purpose] | [Yes/No] |
| `/api/v1/[resource]` | POST | [Purpose] | [Yes/No] |

### 7.2 Endpoint Details

#### `POST /api/v1/[resource]`

**Purpose:** [What it does]
**Business Context:** [Why from PRD]

**Request:**
```json
{
  "field1": "value",
  "field2": "value"
}
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "field1": "value",
  "createdAt": "ISO8601"
}
```

**Error Responses:**

| Code | Condition | Response |
|------|-----------|----------|
| 400 | Invalid input | `{"error": "message"}` |
| 401 | Unauthorized | `{"error": "message"}` |
| 404 | Not found | `{"error": "message"}` |

<!-- Repeat for each endpoint -->

---

## 8. User Interface Specifications

### 8.1 Page/Screen: [Name]

**Purpose:** [What it does]
**User Story Reference:** US-[XXX]

**Layout:**
[Description or wireframe reference]

**Components:**
- [Component 1]: [Purpose]
- [Component 2]: [Purpose]

**Interactions:**
- [Action]: [Result]
- [Action]: [Result]

**Validation:**
- [Field]: [Rules]
- [Field]: [Rules]

**States:**
- Loading: [Behavior]
- Error: [Behavior]
- Empty: [Behavior]
- Success: [Behavior]

<!-- Repeat for each page/screen -->

---

## 9. Integration Points

### 9.1 External Services

| Service | Purpose | Integration Method |
|---------|---------|-------------------|
| [Service 1] | [Purpose] | [REST/GraphQL/etc] |

### 9.2 Integration Details

#### Integration: [Service Name]

**Purpose:** [Why we integrate]
**Endpoint:** [URL]
**Authentication:** [Method]
**Rate Limits:** [Limits]

**Request/Response Examples:**
[Examples]

**Error Handling:**
[How to handle failures]

**Fallback Strategy:**
[What to do if service unavailable]

---

## 10. Security Considerations

### 10.1 Data Classification

| Data Type | Classification | Handling |
|-----------|---------------|----------|
| [Type] | PUBLIC/INTERNAL/CONFIDENTIAL | [Rules] |

### 10.2 Authentication Flow

[Detailed authentication flow]

### 10.3 Authorization Model

[RBAC/ABAC details]

### 10.4 Security Controls

| Control | Implementation | Verification |
|---------|----------------|--------------|
| Input Validation | [How] | [Test] |
| Output Encoding | [How] | [Test] |
| CSRF Protection | [How] | [Test] |
| Rate Limiting | [How] | [Test] |

---

## 11. Testing Strategy

### 11.1 Test Coverage Targets

| Type | Target | Rationale |
|------|--------|-----------|
| Unit Tests | [X%] | [Why] |
| Integration Tests | [X%] | [Why] |
| E2E Tests | [Scenarios] | [Why] |

### 11.2 Test Scenarios by User Story

#### US-001: [Story Title]

**Unit Tests:**
- [ ] [Test scenario 1]
- [ ] [Test scenario 2]

**Integration Tests:**
- [ ] [Test scenario 1]

**E2E Tests:**
- [ ] [Test scenario 1]

### 11.3 Test Data Requirements

[Test data strategy]

---

## 12. Deployment & Operations

### 12.1 Deployment Architecture

[Deployment diagram and description]

### 12.2 Environment Configuration

| Environment | Purpose | Configuration |
|-------------|---------|---------------|
| Development | [Purpose] | [Config] |
| Staging | [Purpose] | [Config] |
| Production | [Purpose] | [Config] |

### 12.3 Monitoring & Alerts

| Metric | Threshold | Alert |
|--------|-----------|-------|
| [Metric] | [Value] | [Action] |

### 12.4 Rollback Plan

[How to rollback if issues]

---

## 13. Out of Scope

<!-- From PRD -->
The following are explicitly **NOT** included in this implementation:

- [ ] [Item 1] - [Reason]
- [ ] [Item 2] - [Reason]
- [ ] [Item 3] - [Reason]

---

## 14. Open Questions & Decisions Needed

| # | Question | Status | Decision | Owner |
|---|----------|--------|----------|-------|
| 1 | [Question] | [Open/Resolved] | [Decision] | [Name] |

---

## 15. Appendices

### Appendix A: Glossary

| Term | Definition |
|------|------------|
| [Term] | [Definition] |

### Appendix B: References

- PRD: [link]
- Tech Spec: [link]
- Research: [link]
- Design Files: [link]

### Appendix C: Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | YYYY-MM-DD | [Name] | Initial consolidated version |

---

## Approval

- [ ] **Technical Review:** [Name] - [Date]
- [ ] **Business Review:** [Name] - [Date]
- [ ] **Final Approval:** [Name] - [Date]

**Approval Notes:**
[Any conditions or notes from approval]
