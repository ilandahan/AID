# AI Full Stack Development Phases

Complete guide to the 8-phase development methodology.

## Overview

```
Phase 1: Discovery     →  Gather raw requirements, market research
Phase 2: PRD          →  Transform into Product Requirements Document
Phase 3: Tech Spec    →  Architecture, APIs, database schema
Phase 4: Jira         →  Project breakdown with time estimates
Phase 5: Development  →  TDD implementation with atomic design
Phase 6: Testing      →  Comprehensive test coverage
Phase 7: Review       →  Code review and quality gates
Phase 8: Deployment   →  CI/CD and production release
```

---

## Phase 1: Discovery

**Goal:** Gather all raw requirements, stakeholder input, and market context.

### Inputs
- Stakeholder interviews
- Market research
- Competitor analysis
- User feedback
- Technical constraints

### Activities
1. Collect raw content from all sources
2. Organize into themes
3. Identify gaps and ambiguities
4. Validate with stakeholders

### Outputs
- Raw content document
- Stakeholder requirements list
- Competitive analysis summary
- Technical constraints document

### Prompt Template
```
/discovery [project-name]

Analyze the following raw content and:
1. Extract key requirements
2. Identify user personas
3. Map feature priorities
4. Note technical constraints
5. Flag ambiguities for clarification
```

---

## Phase 2: PRD Creation

**Goal:** Transform raw content into structured Product Requirements Document.

### Inputs
- Phase 1 outputs
- Business objectives
- Success metrics

### Activities
1. Define product vision
2. Identify user personas
3. Map user journeys
4. Prioritize features (MoSCoW)
5. Define success metrics

### Outputs
- Complete PRD document
- User persona profiles
- Feature prioritization matrix
- Success metrics dashboard spec

### PRD Structure
```markdown
1. Executive Summary
2. Problem Statement
3. Goals & Success Metrics
4. User Personas
5. User Stories
6. Feature Requirements (MoSCoW)
7. Non-Functional Requirements
8. Out of Scope
9. Timeline & Milestones
10. Risks & Mitigations
```

### Prompt Template
```
/prd [project-name]

Transform the discovery content into a PRD:
- Extract clear problem statement
- Define measurable success metrics
- Create detailed user personas
- Write user stories in standard format
- Prioritize using MoSCoW method
```

---

## Phase 3: Technical Specification

**Goal:** Convert PRD into detailed technical architecture.

### Inputs
- PRD document
- Technical constraints
- Infrastructure requirements

### Activities
1. Design system architecture
2. Define API contracts
3. Create database schema
4. Plan integrations
5. Document security requirements

### Outputs
- Architecture diagram
- API specifications (OpenAPI)
- Database schema (TypeScript interfaces)
- Integration map
- Security checklist

### Tech Spec Structure
```markdown
1. Overview
2. Architecture Diagram
3. Component Breakdown
4. API Contracts
5. Data Models
6. Database Schema
7. Integration Points
8. Security Considerations
9. Performance Requirements
10. Deployment Architecture
```

### Prompt Template
```
/tech-spec [feature-name]

Create technical specification:
- Define TypeScript interfaces for all entities
- Design REST API endpoints with request/response types
- Create PostgreSQL schema with migrations
- Document integration points
- Specify authentication/authorization
```

---

## Phase 4: Jira Breakdown

**Goal:** Create actionable project structure with time estimates.

### Inputs
- Tech spec
- Team capacity
- Sprint duration

### Activities
1. Create Epic hierarchy
2. Break into Stories
3. Define Tasks and Sub-tasks
4. Estimate story points
5. Plan sprint allocation

### Outputs
- Epic structure in Jira
- Stories with acceptance criteria
- Tasks with time estimates
- Sprint plan

### Hierarchy
```
Epic (1-2 weeks)
└── Story (1-3 days)
    └── Task (2-8 hours)
        └── Sub-task (1-4 hours)
```

### Prompt Template
```
/jira-breakdown

Based on the tech spec, create:
- Epics for major features
- Stories for user-facing functionality
- Tasks for technical implementation
- Sub-tasks for atomic work items
- Time estimates using story points
```

---

## Phase 5: Development

**Goal:** Implement features using TDD and atomic design.

### Inputs
- Jira tickets
- Design system
- API specs

### Activities
1. Write tests first (TDD)
2. Implement to pass tests
3. Build components atomically
4. Integrate with APIs
5. Document as you go

### Outputs
- Working code with tests
- Design system components
- API implementations
- Documentation

### TDD Workflow
```
1. Write failing test
2. Implement minimal code to pass
3. Refactor if needed
4. Repeat
```

### Prompt Template
```
/develop [ticket-id]

Implement the feature:
1. Write tests first based on acceptance criteria
2. Implement using atomic design patterns
3. Ensure all tests pass
4. Document the implementation
```

---

## Phase 6: Testing

**Goal:** Achieve comprehensive test coverage with minimal mocking.

### Inputs
- Implementation code
- Test plan
- Acceptance criteria

### Activities
1. Run unit tests
2. Execute integration tests
3. Perform E2E testing
4. Validate edge cases
5. Check coverage metrics

### Outputs
- Test reports
- Coverage metrics
- Bug reports
- Performance benchmarks

### Coverage Targets
```
Unit tests:     80%+ line coverage
Integration:    All critical paths
E2E:           Primary user flows
Performance:   Latency benchmarks met
```

### Prompt Template
```
/test-review

Review test quality:
- Check for anti-patterns
- Verify realistic test data
- Ensure minimal mocking (<20%)
- Validate edge case coverage
- Generate coverage report
```

---

## Phase 7: Code Review

**Goal:** Ensure production-ready code quality.

### Inputs
- Pull request
- Test results
- Documentation

### Activities
1. Review code changes
2. Check against standards
3. Validate tests
4. Verify documentation
5. Approve or request changes

### Outputs
- Review comments
- Approval status
- Improvement suggestions
- Final verdict

### Review Checklist
```
□ No shortcuts or workarounds
□ No hardcoded values
□ Proper error handling
□ Tests are comprehensive
□ Documentation is complete
□ Follows architecture patterns
```

### Prompt Template
```
/code-review

Review the changes:
- Check for code quality issues
- Validate against architecture patterns
- Verify test coverage
- Assess production readiness
- Provide verdict: Ready ✓ / Needs Work ⚠️
```

---

## Phase 8: Deployment

**Goal:** Safely release to production.

### Inputs
- Approved code
- CI/CD pipeline
- Release plan

### Activities
1. Run CI pipeline
2. Deploy to staging
3. Execute smoke tests
4. Deploy to production
5. Monitor and validate

### Outputs
- Deployed application
- Deployment logs
- Monitoring dashboards
- Rollback plan

### Deployment Checklist
```
□ All tests passing in CI
□ Staging deployment successful
□ Smoke tests pass
□ Monitoring configured
□ Alerts set up
□ Rollback tested
□ Documentation updated
```

### Prompt Template
```
/deploy [environment]

Prepare deployment:
- Verify CI status
- Check staging results
- Prepare release notes
- Confirm rollback plan
- Execute deployment
```

---

## Phase Transitions

| From | To | Trigger |
|------|-----|---------|
| Discovery | PRD | Raw content complete |
| PRD | Tech Spec | PRD approved |
| Tech Spec | Jira | Tech spec approved |
| Jira | Development | Sprint planned |
| Development | Testing | Implementation complete |
| Testing | Review | Tests passing |
| Review | Deployment | Review approved |
| Deployment | Done | Production stable |

## Quick Commands

```bash
# Start new project
/start-project [name]

# Move to next phase
/next-phase

# Check current phase status
/phase-status

# Generate phase output
/phase-output [phase-number]
```
