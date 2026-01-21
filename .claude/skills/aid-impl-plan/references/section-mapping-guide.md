# Section Mapping Guide for Consolidation

This guide helps Claude identify and map sections between PRD, Tech Spec, and Research documents.

## Standard Section Structure

### Research Report (Phase 0)

Typical sections to look for:

```
1. Executive Summary
2. Market Analysis
3. Competitive Analysis
4. User Research / Interviews
5. Technical Feasibility
6. Findings & Recommendations
7. Data & Evidence
8. Appendices
```

### PRD (Phase 1)

Typical sections to look for:

```
1. Overview / Executive Summary
2. Problem Statement
3. Goals & Objectives
4. User Personas
5. User Stories
6. Functional Requirements
7. Non-Functional Requirements
8. Acceptance Criteria
9. Success Metrics
10. Scope (In/Out)
11. Assumptions & Constraints
12. Dependencies
13. Timeline / Milestones
14. Risks
15. Appendices
```

### Tech Spec (Phase 2)

Typical sections to look for:

```
1. Overview / Summary
2. Architecture Overview
3. System Components
4. Data Models / Database Schema
5. API Contracts / Endpoints
6. Authentication & Authorization
7. Security Considerations
8. Error Handling
9. Performance Requirements
10. Scalability Considerations
11. Third-Party Integrations
12. Testing Strategy
13. Deployment Strategy
14. Monitoring & Logging
15. Migration Plan
16. Technical Risks
17. Appendices
```

---

## Section Relationship Mapping

### How Sections Relate Across Documents

| Research Section | PRD Section | Tech Spec Section | Relationship |
|-----------------|-------------|-------------------|--------------|
| Market Analysis | Problem Statement | - | Research validates problem |
| User Research | User Personas, User Stories | - | Research informs requirements |
| Competitive Analysis | Goals, Scope | Architecture | Competitors inform features |
| Technical Feasibility | Non-Functional Reqs | Architecture, Performance | Feasibility constrains design |
| - | User Stories | System Components | Stories drive components |
| - | Functional Requirements | API Contracts | Requirements define APIs |
| - | Non-Functional Requirements | Performance, Security | NFRs constrain tech choices |
| - | Acceptance Criteria | Testing Strategy | Criteria drive test cases |
| - | Dependencies | Third-Party Integrations | PRD deps become tech integrations |

---

## Dependency Detection Rules

### Within a Document

Look for these dependency indicators:

1. **Explicit references:**
   - "As described in Section X..."
   - "See [Section Name] for details"
   - "Building on the [previous section]..."

2. **Implicit dependencies:**
   - Data model sections depend on user story sections
   - API sections depend on data model sections
   - Security sections depend on architecture sections

3. **Terminology dependencies:**
   - If Section B uses terms defined in Section A, B depends on A

### Across Documents

1. **PRD → Tech Spec dependencies:**
   - Every Tech Spec section should trace to a PRD requirement
   - Look for: "This implements PRD requirement X"

2. **Research → PRD dependencies:**
   - PRD decisions should reference research findings
   - Look for: "Based on research finding X"

3. **Research → Tech Spec dependencies:**
   - Technical decisions may reference feasibility studies
   - Look for: "Per technical feasibility analysis"

---

## Processing Order Algorithm

### Step 1: Build Dependency Graph

```
For each section S in all documents:
  1. Identify explicit dependencies (references to other sections)
  2. Identify implicit dependencies (uses terms from other sections)
  3. Create edge: S depends on D for each dependency D
```

### Step 2: Topological Sort

```
1. Start with sections that have NO dependencies (roots)
2. Process roots first
3. Then process sections whose dependencies are all processed
4. Continue until all sections processed
```

### Step 3: Handle Cycles

If circular dependencies exist:
1. Flag for user attention
2. Process the cycle as a single unit
3. Ask user which section takes priority

---

## Consolidation Order Template

```yaml
consolidation_order:
  # Round 1: Foundation (no dependencies)
  round_1:
    - section: "Research: Executive Summary"
      depends_on: []
    - section: "PRD: Problem Statement"
      depends_on: []

  # Round 2: Core Requirements
  round_2:
    - section: "PRD: User Personas"
      depends_on: ["PRD: Problem Statement", "Research: User Research"]
    - section: "PRD: User Stories"
      depends_on: ["PRD: User Personas"]

  # Round 3: Technical Foundation
  round_3:
    - section: "Tech Spec: Architecture"
      depends_on: ["PRD: Non-Functional Requirements", "Research: Technical Feasibility"]
    - section: "Tech Spec: Data Models"
      depends_on: ["PRD: User Stories", "Tech Spec: Architecture"]

  # Round 4: Implementation Details
  round_4:
    - section: "Tech Spec: API Contracts"
      depends_on: ["Tech Spec: Data Models", "PRD: Acceptance Criteria"]
    - section: "Tech Spec: Security"
      depends_on: ["Tech Spec: Architecture", "PRD: Non-Functional Requirements"]

  # Round 5: Testing & Deployment
  round_5:
    - section: "Tech Spec: Testing Strategy"
      depends_on: ["PRD: Acceptance Criteria", "Tech Spec: API Contracts"]
    - section: "Tech Spec: Deployment Strategy"
      depends_on: ["Tech Spec: Architecture", "Tech Spec: Security"]
```

---

## Contradiction Detection Points

### High-Risk Contradiction Areas

These section pairs often contain contradictions:

| PRD Section | Tech Spec Section | Common Contradiction |
|-------------|-------------------|---------------------|
| Performance Requirements | Performance Implementation | Different metrics/targets |
| User Stories | API Contracts | Missing endpoints for stories |
| Security Requirements | Security Implementation | Missing security controls |
| Acceptance Criteria | Testing Strategy | Untested criteria |
| Scope (In) | System Components | Missing components |
| Scope (Out) | System Components | Extra components built |
| Timeline | Deployment Strategy | Unrealistic deployment |

### Contradiction Check Template

For each section pair:

```markdown
## Checking: [PRD Section] vs [Tech Spec Section]

### Alignment Check:
- [ ] All PRD items have Tech Spec coverage
- [ ] No Tech Spec items without PRD justification
- [ ] Metrics/targets match
- [ ] Terminology consistent

### Contradictions Found:
1. [Description]
   - PRD says: "[quote]"
   - Tech Spec says: "[quote]"
   - Severity: [Critical/High/Low]

### Resolution:
- Using: [Research/PRD/Tech Spec]
- Rationale: [Why]
```

---

## Section Content Verification

### Before Consolidation Completion

Verify each source section is represented:

```markdown
## Information Verification Checklist

### Research Report
- [ ] Executive Summary → Consolidated Section [X]
- [ ] Market Analysis → Consolidated Section [X]
- [ ] User Research → Consolidated Section [X]
...

### PRD
- [ ] Problem Statement → Consolidated Section [X]
- [ ] User Stories → Consolidated Section [X]
- [ ] Acceptance Criteria → Consolidated Section [X]
...

### Tech Spec
- [ ] Architecture → Consolidated Section [X]
- [ ] Data Models → Consolidated Section [X]
- [ ] API Contracts → Consolidated Section [X]
...

All sections accounted for: [Yes/No]
Information lost: [None/List]
```
