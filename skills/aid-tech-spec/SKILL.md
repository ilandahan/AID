---
name: aid-tech-spec
description: AID Phase 2 - Technical Specification. Use for system architecture, API contracts, data models, security architecture, transitioning from PRD to implementation.
---

# Tech Spec Phase Skill

Purpose: design the technical solution - a blueprint developers follow without ambiguity.

Entry: PRD approved, requirements clear, dependencies identified.
Exit: tech spec complete, architecture documented, API contracts defined, data models specified.

## Deliverables

1. Tech Spec Document - Implementation-ready design
2. Architecture Diagram - Components and interactions
3. API Contracts - Endpoints, schemas, errors
4. Data Models - Schemas, types, constraints
5. Agent Architecture - Section 9, scaled to the PRD §1.5 Solution Shape level, traced to §7A

## Common Pitfalls

| Pitfall | Fix |
|---|---|
| Over-engineering | Design for current needs |
| Missing error handling | Define errors upfront |
| Tight coupling | Design for testability |
| Ignoring non-functionals | Address performance, security |
| Unclear contracts | APIs unambiguous with examples |
| Agent where a workflow works | Lowest ladder level that works |
| Permissions only in the prompt | Policy as code, default deny |

## Phase Gate Checklist

- [ ] Tech spec complete
- [ ] Architecture diagram created
- [ ] All API contracts defined
- [ ] Data models specified
- [ ] Error handling strategy defined
- [ ] Security considerations addressed
- [ ] Performance requirements addressed
- [ ] Section 9 Agent Architecture filled at the §1.5 level, never "N/A"
- [ ] Every Section 9 item cites its §7A item (7A.1-7A.8)
- [ ] Level 5 only: one of the four multi-agent justifications stated
- [ ] Tech lead approved

## Tech Spec Template

Emit these 9 sections, in this order, with these exact headings:

````markdown
# [Feature] Technical Specification

## 1. Overview
### Problem Summary
### Proposed Solution
### Key Decisions
| Decision | Choice | Rationale |

## 2. Architecture
### System Diagram
[Mermaid or image]

### Component Breakdown
| Component | Responsibility | Dependencies |

### Data Flow

## 3. API Design
### POST /api/[resource]
**Request:**
```json
{ "field": "type" }
```

**Response (200):**
```json
{ "id": "string" }
```

**Errors:**
| Code | Error | Description |

## 4. Data Model
### Entity: [Name]
| Field | Type | Constraints | Description |

## 5. Security
### Authentication
### Authorization
### Data Protection

## 6. Error Handling
| Scenario | Response | Recovery |

## 7. Non-Functional Requirements
| Requirement | Target | Measurement |

## 8. Risks & Mitigations
| Risk | Impact | Mitigation |

## 9. Agent Architecture
[Single copy of this section's template, scaling by level and classic forms for levels 0-1:
`references/agent-architecture.md`. Never "N/A". Headings:]
### 9.1 Orchestration Pattern
### 9.2 Tool Contracts & Permission Policy
### 9.3 Guardrails
### 9.4 Trace Schema
### 9.5 Eval Harness
### 9.6 Model Choice & Fallbacks
### 9.7 Cost & Latency Budgets
### 9.8 Kill Switch
````

**Eval timing (A9):** 9.5 designs the harness from the PRD's 7A.6 and the Phase 1 seed cases (`docs/prd/SEED-EVALS-<feature>.md`). The tech spec never waits for the golden set: QA grows it and its held-out split in parallel with Phases 2-4, complete only for the Phase 5 release gate. The data scientist calibrates the judge in Phase 4, when a judge is introduced.

## Role Guidance

| Role | Focus |
|---|---|
| PM | Validate approach addresses requirements |
| Dev | Own spec, design for testability |
| QA | Review testability, integration points |
| Tech Lead | Review architecture, approve direction; own the §1.5 level, agent architecture, permission policy |

## Handoff to Implementation

- Approved tech spec
- API contracts
- Data models
- Architecture decisions with rationale
- Spike/POC results (if any)
- Agent Architecture (Section 9): permission policy, trace schema, eval harness, kill switch

Save to: `docs/tech-spec/YYYY-MM-DD-[feature].md`
