# Epic Template

## Jira Epic Structure

```
EPIC-{N}: {Domain Name}
├── Story {N}.1: {Capability Group}
│   ├── Task: {Specific Implementation}
│   ├── Task: {Specific Implementation}
│   └── Task: {Specific Implementation}
├── Story {N}.2: {Capability Group}
│   ├── Task: ...
│   └── Task: ...
└── Story {N}.3: {Capability Group}
    └── Task: ...
```

---

## Epic Description Template

### Title Format
```
EPIC-{N}: {Domain Name} ({Primary Technology})
```

**Examples:**
- EPIC-1: Infrastructure & DevOps (GCP)
- EPIC-2: Authentication Service (Cloud Functions)
- EPIC-8: Frontend Application (Next.js)

---

### Description Format (Jira-Ready)

```markdown
## Summary
{2-3 sentences describing what this epic delivers and its scope}

## Business Value
{Why this epic matters to users/stakeholders/investors. Connect to PRD goals.}

## User Impact
{Which user personas benefit and how. Reference PRD user stories.}

## Dependencies
- **Blocked by**: {List prerequisite epics that must complete first}
- **Blocks**: {List dependent epics that cannot start until this completes}
- **Parallel with**: {Epics that can run concurrently}

## Success Criteria
{Measurable outcomes from PRD, written as checkboxes}
- [ ] {Outcome 1 - specific, testable}
- [ ] {Outcome 2 - specific, testable}
- [ ] {Outcome 3 - specific, testable}

## Technical Context
{Key architectural decisions from Tech Spec}
- **Primary Technology**: {Framework/service}
- **Database**: {Tables/schemas involved}
- **APIs**: {Endpoints this epic implements}
- **Security**: {Auth/encryption requirements}

## PRD References
- User Stories: {US-XX, US-YY, US-ZZ}
- Requirements Section: {Section number in PRD}

## Tech Spec References
- Architecture Section: {Section number}
- API Contract: {OpenAPI paths}
- Data Model: {Prisma models}

## Estimated Duration
{X-Y days} ({Z story points total})

## Stories in this Epic
{Auto-populated or manually listed}
1. Story {N}.1: {Name}
2. Story {N}.2: {Name}
3. Story {N}.3: {Name}
```

---

## Content Mapping Rules

### What Goes in Epic (FROM PRD)

| PRD Section | Epic Field |
|-------------|------------|
| Product Goals | Business Value |
| User Personas | User Impact |
| Success Metrics | Success Criteria |
| User Stories (grouped) | Stories list |
| Dependencies | Dependencies |

### What Goes in Epic (FROM TECH SPEC)

| Tech Spec Section | Epic Field |
|-------------------|------------|
| Architecture Overview | Technical Context |
| Technology Choices | Primary Technology |
| Security Requirements | Security notes |
| API Summary | APIs list |

---

## Epic Naming Conventions

### Domain Categories

| Domain | Prefix | Example |
|--------|--------|---------|
| Infrastructure | EPIC-1 | Infrastructure & DevOps |
| Authentication | EPIC-2 | Authentication Service |
| Core Domain 1 | EPIC-3 | {Primary business entity} |
| Core Domain 2 | EPIC-4 | {Secondary business entity} |
| Core Domain N | EPIC-N | {Business capability} |
| Frontend | EPIC-Last | Frontend Application |

### Ordering Principle

```
Infrastructure → Auth → Core Backend (by dependency) → Frontend
```

Always order epics by dependency chain, not alphabetically.

---

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| "EPIC-0: Setup" | Too vague | Split into specific infra tasks |
| "EPIC: Miscellaneous" | Catch-all bucket | Every task belongs to a domain |
| Spec fixes in Epic | Not developer work | Fix source docs directly |
| No dependencies | Unclear execution order | Always specify blocked-by |
| No success criteria | Can't verify completion | Must have testable outcomes |
