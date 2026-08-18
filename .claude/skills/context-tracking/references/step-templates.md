# Step Templates Reference

Predefined step templates for different task types and phases.

---

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  STEP TEMPLATE SELECTION                                        │
│                                                                 │
│  Phase 1-3: Document Creation                                   │
│  Phase 4:   Development (by task type)                          │
│  Phase 5:   QA & Ship                                           │
│                                                                 │
│  Task Types:                                                    │
│  - feature: New functionality                                   │
│  - bug: Bug fix                                                 │
│  - refactor: Code improvement                                   │
│  - qa: Quality assurance task                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Research & PRD

```json
{
  "template_name": "prd_creation",
  "phase": 1,
  "steps": [
    {
      "order": 1,
      "name": "Load context",
      "description": "Read existing context, understand current state"
    },
    {
      "order": 2,
      "name": "Gather requirements",
      "description": "Interview stakeholders, review related docs"
    },
    {
      "order": 3,
      "name": "Define user stories",
      "description": "Write user stories with acceptance criteria"
    },
    {
      "order": 4,
      "name": "Draft PRD",
      "description": "Create initial PRD document"
    },
    {
      "order": 5,
      "name": "Review and refine",
      "description": "Self-review, fill gaps, improve clarity"
    },
    {
      "order": 6,
      "name": "Save to docs/prd/",
      "description": "Save as YYYY-MM-DD-[feature].md"
    },
    {
      "order": 7,
      "name": "Update context",
      "description": "Update project.documents.prd path"
    }
  ]
}
```

---

## Phase 2: Tech Spec Creation

```json
{
  "template_name": "tech_spec_creation",
  "phase": 2,
  "steps": [
    {
      "order": 1,
      "name": "Load context",
      "description": "Read PRD, understand requirements"
    },
    {
      "order": 2,
      "name": "Security assessment",
      "description": "Data classification, threat model"
    },
    {
      "order": 3,
      "name": "Design architecture",
      "description": "System diagram, components, data flow"
    },
    {
      "order": 4,
      "name": "Define data models",
      "description": "TypeScript interfaces, database schema"
    },
    {
      "order": 5,
      "name": "Specify APIs",
      "description": "Endpoints, request/response, error codes"
    },
    {
      "order": 6,
      "name": "Document security controls",
      "description": "Auth, encryption, audit logging"
    },
    {
      "order": 7,
      "name": "Review and refine",
      "description": "Self-review, ensure completeness"
    },
    {
      "order": 8,
      "name": "Save to docs/tech-spec/",
      "description": "Save as YYYY-MM-DD-[feature].md"
    },
    {
      "order": 9,
      "name": "Update context",
      "description": "Update project.documents.tech_spec path"
    }
  ]
}
```

---

## Phase 3: Implementation Plan Creation

```json
{
  "template_name": "implementation_plan_creation",
  "phase": 3,
  "steps": [
    {
      "order": 1,
      "name": "Load context",
      "description": "Read Tech Spec, understand scope"
    },
    {
      "order": 2,
      "name": "Break down phases",
      "description": "Define implementation phases"
    },
    {
      "order": 3,
      "name": "Create task list",
      "description": "Detailed tasks with estimates"
    },
    {
      "order": 4,
      "name": "Identify dependencies",
      "description": "External services, libraries, APIs"
    },
    {
      "order": 5,
      "name": "Define test strategy",
      "description": "Unit, integration, E2E approach"
    },
    {
      "order": 6,
      "name": "Document risks",
      "description": "Risks with mitigations"
    },
    {
      "order": 7,
      "name": "Review and refine",
      "description": "Self-review, validate estimates"
    },
    {
      "order": 8,
      "name": "Save to docs/implementation-plan/",
      "description": "Save as YYYY-MM-DD-[feature].md"
    },
    {
      "order": 9,
      "name": "Update context",
      "description": "Update project.documents.implementation_plan path"
    }
  ]
}
```

---

## Phase 4: Feature Development

```json
{
  "template_name": "feature_development",
  "phase": 4,
  "task_type": "feature",
  "steps": [
    {
      "order": 1,
      "name": "Load task context",
      "description": "Read Jira, understand requirements"
    },
    {
      "order": 2,
      "name": "Read Tech Spec section",
      "description": "Find relevant section for this task"
    },
    {
      "order": 3,
      "name": "Write tests (TDD)",
      "description": "Write failing tests first"
    },
    {
      "order": 4,
      "name": "Implement component",
      "description": "Write code to make tests pass"
    },
    {
      "order": 5,
      "name": "Run tests / fix",
      "description": "Iterate until all tests pass"
    },
    {
      "order": 6,
      "name": "Apply styling",
      "description": "Add CSS/styles using design tokens"
    },
    {
      "order": 7,
      "name": "Self code review",
      "description": "Review own code for quality"
    },
    {
      "order": 8,
      "name": "Update Jira",
      "description": "Log progress, time, comments"
    },
    {
      "order": 9,
      "name": "Commit",
      "description": "Commit with proper message"
    }
  ]
}
```

---

## Phase 4: Bug Fix

```json
{
  "template_name": "bug_fix",
  "phase": 4,
  "task_type": "bug",
  "steps": [
    {
      "order": 1,
      "name": "Load task context",
      "description": "Read bug report, understand issue"
    },
    {
      "order": 2,
      "name": "Reproduce issue",
      "description": "Verify bug exists, understand trigger"
    },
    {
      "order": 3,
      "name": "Write failing test",
      "description": "Create test that demonstrates bug"
    },
    {
      "order": 4,
      "name": "Implement fix",
      "description": "Write code to fix the bug"
    },
    {
      "order": 5,
      "name": "Verify fix",
      "description": "Run test, verify fix doesn't break others"
    },
    {
      "order": 6,
      "name": "Update Jira",
      "description": "Document root cause and fix"
    },
    {
      "order": 7,
      "name": "Commit",
      "description": "Commit with issue reference"
    }
  ]
}
```

---

## Phase 4: Refactoring

```json
{
  "template_name": "refactoring",
  "phase": 4,
  "task_type": "refactor",
  "steps": [
    {
      "order": 1,
      "name": "Load task context",
      "description": "Understand refactoring goal"
    },
    {
      "order": 2,
      "name": "Review existing tests",
      "description": "Ensure good test coverage exists"
    },
    {
      "order": 3,
      "name": "Run tests (baseline)",
      "description": "Verify all tests pass before changes"
    },
    {
      "order": 4,
      "name": "Apply refactoring",
      "description": "Make changes incrementally"
    },
    {
      "order": 5,
      "name": "Run tests (verify)",
      "description": "Verify no regressions"
    },
    {
      "order": 6,
      "name": "Update documentation",
      "description": "Update any affected docs"
    },
    {
      "order": 7,
      "name": "Self code review",
      "description": "Review refactored code"
    },
    {
      "order": 8,
      "name": "Commit",
      "description": "Commit with refactor description"
    }
  ]
}
```

---

## Phase 4: API Development

```json
{
  "template_name": "api_development",
  "phase": 4,
  "task_type": "feature",
  "variant": "api",
  "steps": [
    {
      "order": 1,
      "name": "Load task context",
      "description": "Read API spec from Tech Spec"
    },
    {
      "order": 2,
      "name": "Write API tests",
      "description": "Integration tests for endpoint"
    },
    {
      "order": 3,
      "name": "Implement handler",
      "description": "Create route handler"
    },
    {
      "order": 4,
      "name": "Implement service layer",
      "description": "Business logic"
    },
    {
      "order": 5,
      "name": "Implement data layer",
      "description": "Database queries"
    },
    {
      "order": 6,
      "name": "Add validation",
      "description": "Input validation, error handling"
    },
    {
      "order": 7,
      "name": "Run tests / fix",
      "description": "Iterate until all pass"
    },
    {
      "order": 8,
      "name": "Update OpenAPI spec",
      "description": "Document endpoint"
    },
    {
      "order": 9,
      "name": "Commit",
      "description": "Commit with API description"
    }
  ]
}
```

---

## Phase 5: QA Task

```json
{
  "template_name": "qa_task",
  "phase": 5,
  "task_type": "qa",
  "steps": [
    {
      "order": 1,
      "name": "Load task context",
      "description": "Understand QA scope"
    },
    {
      "order": 2,
      "name": "Run test suite",
      "description": "Execute all tests"
    },
    {
      "order": 3,
      "name": "Check coverage",
      "description": "Verify coverage meets threshold"
    },
    {
      "order": 4,
      "name": "Review checklist",
      "description": "Go through QA checklist"
    },
    {
      "order": 5,
      "name": "Document findings",
      "description": "Record any issues found"
    },
    {
      "order": 6,
      "name": "Fix issues",
      "description": "Address found issues"
    },
    {
      "order": 7,
      "name": "Final verification",
      "description": "Re-run tests, verify fixes"
    }
  ]
}
```

---

## Phase 5: Deployment

```json
{
  "template_name": "deployment",
  "phase": 5,
  "task_type": "deploy",
  "steps": [
    {
      "order": 1,
      "name": "Pre-deploy checklist",
      "description": "Verify all gates passed"
    },
    {
      "order": 2,
      "name": "Build production",
      "description": "Create production build"
    },
    {
      "order": 3,
      "name": "Deploy to staging",
      "description": "Deploy to staging environment"
    },
    {
      "order": 4,
      "name": "Staging verification",
      "description": "Test on staging"
    },
    {
      "order": 5,
      "name": "Deploy to production",
      "description": "Deploy to production"
    },
    {
      "order": 6,
      "name": "Production smoke test",
      "description": "Verify production works"
    },
    {
      "order": 7,
      "name": "Update documentation",
      "description": "Release notes, changelog"
    }
  ]
}
```

---

## Template Selection Logic

```javascript
function getStepsTemplate(taskType, phase, variant = null) {
  // Phase 1-3: Document creation
  if (phase <= 3) {
    const templates = {
      1: 'prd_creation',
      2: 'tech_spec_creation',
      3: 'implementation_plan_creation'
    };
    return loadTemplate(templates[phase]);
  }

  // Phase 4: Development by task type
  if (phase === 4) {
    const templates = {
      feature: variant === 'api' ? 'api_development' : 'feature_development',
      bug: 'bug_fix',
      refactor: 'refactoring',
      task: 'feature_development'
    };
    return loadTemplate(templates[taskType] || 'feature_development');
  }

  // Phase 5: QA or deployment
  if (phase === 5) {
    const templates = {
      qa: 'qa_task',
      deploy: 'deployment'
    };
    return loadTemplate(templates[taskType] || 'qa_task');
  }
}
```

---

## Custom Templates

Users can define custom templates in `.aid/step-templates.json`:

```json
{
  "custom_templates": [
    {
      "template_name": "documentation_update",
      "steps": [
        { "order": 1, "name": "Identify docs to update" },
        { "order": 2, "name": "Make changes" },
        { "order": 3, "name": "Review formatting" },
        { "order": 4, "name": "Commit" }
      ]
    }
  ]
}
```
