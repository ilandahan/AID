# PRD Template Extended Reference

Complete PRD template with all sections, examples, and guidance.

## Full PRD Template

```markdown
# [Feature/Product Name] PRD

**Document Version**: 1.0
**Created**: [Date]
**Last Updated**: [Date]
**Author**: [Name]
**Status**: Draft | In Review | Approved

---

## Document References

| Document | Link |
|----------|------|
| Research Report | [Link to docs/research/YYYY-MM-DD-[project]/research-report.md] |
| Traceability Matrix | [Link to docs/research/YYYY-MM-DD-[project]/traceability-matrix.md] |
| Discovery Phase | [Link if applicable] |
| Related PRDs | [Links to related PRDs] |

---

## 1. Executive Summary

### 1.1 Purpose
[One paragraph explaining what this document covers and why it exists]

### 1.2 Problem Statement
**Research Backing**: [PROJECT]-A-INT-XXX, [PROJECT]-A-JTBD-XXX

[Concise description of the problem being solved. Should be user-focused.]

**User Pain Points** (from research):
1. [Pain point 1] - Source: [PROJECT]-A-INT-XXX
2. [Pain point 2] - Source: [PROJECT]-A-INT-XXX
3. [Pain point 3] - Source: [PROJECT]-A-JTBD-XXX

### 1.3 Solution Overview
[Brief description of the proposed solution - high level, not technical]

### 1.4 Success Metrics
**Research Backing**: [PROJECT]-C-OPP-XXX

| Metric | Current State | Target | Timeline |
|--------|--------------|--------|----------|
| [Metric 1] | [Baseline] | [Goal] | [When] |
| [Metric 2] | [Baseline] | [Goal] | [When] |
| [Metric 3] | [Baseline] | [Goal] | [When] |

---

## 2. Background & Context

### 2.1 Current State
[Description of how things work today]

### 2.2 User Research Summary
**Sources**: [PROJECT]-A-INT-XXX through XXX

**Key Findings**:
1. [Finding 1]
2. [Finding 2]
3. [Finding 3]

**User Quotes**:
> "[Direct quote from research]" - [Persona type]
> "[Direct quote from research]" - [Persona type]

### 2.3 Competitive Landscape
**Sources**: [PROJECT]-A-COMP-XXX

| Competitor | Strengths | Weaknesses | Our Differentiation |
|------------|-----------|------------|---------------------|
| [Competitor 1] | | | |
| [Competitor 2] | | | |

### 2.4 Business Context
- Strategic alignment: [How this fits company strategy]
- Market opportunity: [Size/impact]
- Timing considerations: [Why now]

---

## 3. User Personas

### 3.1 Primary Persona: [Name]
**Research Backing**: [PROJECT]-A-INT-XXX

| Attribute | Description |
|-----------|-------------|
| Role | [Job title/role] |
| Demographics | [Relevant demographics] |
| Goals | [What they want to achieve] |
| Frustrations | [Current pain points] |
| Tech Savviness | [Low/Medium/High] |
| Usage Frequency | [How often they'd use this] |

**Jobs to be Done**:
- When [situation], I want to [motivation], so I can [outcome]

### 3.2 Secondary Persona: [Name]
**Research Backing**: [PROJECT]-A-INT-XXX

[Same structure as primary]

### 3.3 Anti-Persona: [Who This Is NOT For]
[Description of users explicitly NOT targeted]

---

## 4. User Stories

### 4.1 Epic: [Epic Name]
**Research Backing**: [PROJECT]-C-OPP-XXX

#### US-001: [Title]
**Research Backing**: [PROJECT]-A-INT-XXX, [PROJECT]-B-IDEA-XXX

**As a** [persona]
**I want** [capability]
**So that** [benefit]

**Acceptance Criteria:**
- [ ] Given [context], when [action], then [outcome]
- [ ] Given [context], when [action], then [outcome]
- [ ] Given [error condition], when [action], then [error handling]

**Priority**: Must Have
**Complexity**: M

---

#### US-002: [Title]
**Research Backing**: [PROJECT]-A-XXX OR ASSUMPTION - [rationale]

**As a** [persona]
**I want** [capability]
**So that** [benefit]

**Acceptance Criteria:**
- [ ] Given [context], when [action], then [outcome]

**Priority**: Should Have
**Complexity**: S

---

### 4.2 Epic: [Epic Name]
[Continue with more user stories...]

---

## 5. Scope Definition

### 5.1 In Scope (Phase 1)
| Feature | Description | Research Backing | Priority |
|---------|-------------|------------------|----------|
| [Feature 1] | [Brief description] | [PROJECT]-XXX | Must Have |
| [Feature 2] | [Brief description] | [PROJECT]-XXX | Must Have |
| [Feature 3] | [Brief description] | [PROJECT]-XXX | Should Have |

### 5.2 Out of Scope (Phase 1)
| Feature | Research Backing | Rationale | Future Phase |
|---------|------------------|-----------|--------------|
| [Feature A] | [PROJECT]-XXX | [Why deferred] | Phase 2 |
| [Feature B] | [PROJECT]-XXX | [Why excluded] | TBD |
| [Feature C] | N/A | Stakeholder decision | Phase 2 |

### 5.3 Scope Risks
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Scope creep from [area] | Medium | High | Strict change control |
| [Risk 2] | | | |

---

## 6. Functional Requirements

### 6.1 [Feature Area 1]

#### FR-001: [Requirement Title]
**Research Backing**: [PROJECT]-XXX

**Description**: [Detailed requirement description]

**Business Rules**:
1. [Rule 1]
2. [Rule 2]

**Data Requirements**:
- Input: [Data inputs needed]
- Output: [Data outputs produced]
- Validation: [Validation rules]

**User Interface**:
- [UI requirement 1]
- [UI requirement 2]

#### FR-002: [Requirement Title]
[Continue pattern...]

---

## 7. Non-Functional Requirements

### 7.1 Performance
| Requirement | Target | Measurement |
|-------------|--------|-------------|
| Page load time | < 2 seconds | P95 latency |
| API response time | < 500ms | P95 latency |
| Concurrent users | 1000+ | Load testing |

### 7.2 Security
- [ ] Authentication: [Requirements]
- [ ] Authorization: [Requirements]
- [ ] Data encryption: [Requirements]
- [ ] Compliance: [GDPR, SOC2, etc.]

### 7.3 Accessibility
- [ ] WCAG 2.1 AA compliance
- [ ] Keyboard navigation
- [ ] Screen reader support

### 7.4 Scalability
- [Scalability requirements]

### 7.5 Reliability
- Uptime target: [99.9%]
- Recovery time objective: [RTO]
- Recovery point objective: [RPO]

---

## 8. Dependencies

### 8.1 Internal Dependencies
| Dependency | Owner | Status | Impact if Delayed |
|------------|-------|--------|-------------------|
| [API from Team X] | [Owner] | In Progress | Blocks checkout |
| [Design system] | [Owner] | Complete | - |

### 8.2 External Dependencies
| Dependency | Vendor | Status | Contingency |
|------------|--------|--------|-------------|
| [Payment provider] | [Vendor] | Contracted | [Backup option] |
| [Third-party API] | [Vendor] | Evaluating | [Alternative] |

### 8.3 Technical Dependencies
- [Infrastructure requirement]
- [Platform requirement]

---

## 9. Assumptions Log

| ID | Assumption | Risk if Wrong | Validation Plan | Status |
|----|------------|---------------|-----------------|--------|
| ASSUME-001 | [Assumption] | [Impact] | [How to validate] | Open |
| ASSUME-002 | [Assumption] | [Impact] | [How to validate] | Validated |
| ASSUME-003 | [Assumption] | [Impact] | [How to validate] | Invalid |

---

## 10. Constraints

### 10.1 Business Constraints
- Budget: [Budget limitations]
- Timeline: [Hard deadlines]
- Resources: [Team limitations]

### 10.2 Technical Constraints
- Must use existing [technology/platform]
- Must integrate with [system]
- Cannot change [component]

### 10.3 Regulatory Constraints
- [Compliance requirement 1]
- [Compliance requirement 2]

---

## 11. Risks & Mitigations

| ID | Risk | Likelihood | Impact | Mitigation | Owner |
|----|------|------------|--------|------------|-------|
| RISK-001 | [Risk description] | High/Med/Low | High/Med/Low | [Mitigation plan] | [Name] |
| RISK-002 | [Risk description] | | | | |

---

## 12. Open Questions

| ID | Question | Owner | Due Date | Resolution |
|----|----------|-------|----------|------------|
| Q-001 | [Question] | [Name] | [Date] | [Pending/Resolved: answer] |
| Q-002 | [Question] | [Name] | [Date] | |

---

## 13. Traceability Summary

### 13.1 Research → Requirements Coverage

| Research Type | Total Findings | Used in PRD | Deferred | Excluded |
|---------------|----------------|-------------|----------|----------|
| Interviews (A-INT) | X | X | X | X |
| Competitive (A-COMP) | X | X | X | X |
| JTBD (A-JTBD) | X | X | X | X |
| Ideas (B-IDEA) | X | X | X | X |
| Root Causes (B-ROOT) | X | X | X | X |
| Opportunities (C-OPP) | X | X | X | X |

### 13.2 Requirements → Research Coverage

| Requirement Type | Total | With Research Backing | Assumptions |
|------------------|-------|----------------------|-------------|
| User Stories | X | X | X |
| Acceptance Criteria | X | X | X |
| Functional Requirements | X | X | X |
| Success Metrics | X | X | X |

### 13.3 Traceability Gaps
- [Any findings not yet addressed]
- [Any requirements without backing]

---

## 14. Appendices

### Appendix A: Glossary
| Term | Definition |
|------|------------|
| [Term 1] | [Definition] |
| [Term 2] | [Definition] |

### Appendix B: Related Documents
- [Link to designs]
- [Link to technical spec]
- [Link to research data]

### Appendix C: Revision History
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | [Date] | [Name] | Initial version |
| 1.1 | [Date] | [Name] | [Changes] |

---

## Approval Sign-off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Product Manager | | | |
| Tech Lead | | | |
| Design Lead | | | |
| QA Lead | | | |
| Stakeholder | | | |
```

---

## Section-by-Section Guidance

### Executive Summary
- Write last, summarize first
- Keep to one page
- Include key numbers
- Make it scannable

### User Stories
- Link every story to research
- Use INVEST criteria
- Include error cases
- Size appropriately (S/M/L)

### Scope Definition
- Be explicit about exclusions
- Document rationale for decisions
- Link to research for both in/out

### Assumptions Log
- Never hide assumptions
- Rate risk impact
- Plan validation before build
- Track status

### Traceability Summary
- Update after each change
- Identify gaps
- Ensure bidirectional links
- No orphan items

---

## Quality Checklist

Before PRD approval:

```
Executive Summary
☐ Problem statement is clear and user-focused
☐ Success metrics are measurable
☐ Solution overview is implementation-agnostic

Research Integration
☐ All key findings referenced
☐ Research IDs linked correctly
☐ Quotes attributed to personas

User Stories
☐ Follow "As a... I want... So that..." format
☐ Each has testable acceptance criteria
☐ Research backing or assumption flag present
☐ Priority and complexity assigned

Scope
☐ In-scope items clearly listed
☐ Out-of-scope items explicitly stated
☐ Rationale provided for exclusions

Dependencies & Risks
☐ All dependencies identified with owners
☐ Risks assessed with mitigations
☐ Open questions tracked

Traceability
☐ Forward trace complete (research → requirements)
☐ Backward trace complete (requirements → research)
☐ No broken links
☐ Coverage summary accurate

Sign-off
☐ All required approvals obtained
☐ Version history updated
☐ Distributed to stakeholders
```
