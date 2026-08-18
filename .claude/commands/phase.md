# /phase Command

Navigate to a specific phase in the AI Full Stack Development workflow.

## Usage

```
/phase <number>
```

## Phases

| Phase | Name | Description |
|-------|------|-------------|
| 1 | Discovery | Gather requirements, understand context |
| 2 | PRD Creation | Generate Product Requirements Document |
| 3 | Technical Spec | Create technical specification |
| 4 | Jira Breakdown | Generate project structure in Jira |
| 5 | Development | Implement features (TDD approach) |
| 6 | Testing & QA | Comprehensive testing |
| 7 | Code Review | Review and refine |
| 8 | Deployment | Deploy to production |

## Examples

```bash
# Start Discovery phase
/phase 1

# Jump to Development
/phase 5

# Begin Testing
/phase 6
```

## Phase Details

### Phase 1: Discovery
**Goal:** Understand requirements and context

**Activities:**
- Review existing documentation
- Identify stakeholders
- Define success criteria
- List assumptions and constraints

**Output:** Discovery summary document

---

### Phase 2: PRD Creation
**Goal:** Document product requirements

**Activities:**
- Define user stories
- Specify acceptance criteria
- Create wireframes/mockups
- Define MVP scope

**Output:** `docs/prd/PRD-<feature>.md`

**Command:** `/prd`

---

### Phase 3: Technical Specification
**Goal:** Design technical solution

**Activities:**
- Database schema design
- API endpoint definitions
- Component architecture
- TypeScript interfaces

**Output:** `docs/tech-specs/TECH-SPEC-<feature>.md`

**Command:** `/tech-spec`

**Skill:** `system-architect`

---

### Phase 4: Jira Breakdown
**Goal:** Create project structure

**Activities:**
- Create Epic
- Break into Stories
- Define Tasks and Subtasks
- Estimate effort

**Output:** Jira project with hierarchy

**Command:** `/jira-breakdown`

---

### Phase 5: Development
**Goal:** Implement features

**Activities:**
- TDD: Write tests first
- Implement components (atoms → pages)
- API development
- Database migrations

**Skills:**
- `atomic-design` - Component development
- `atomic-page-builder` - Page composition
- `test-driven` - TDD methodology

---

### Phase 6: Testing & QA
**Goal:** Ensure quality

**Activities:**
- Unit tests
- Integration tests
- E2E tests with Puppeteer
- Visual regression testing

**Command:** `/test-review`

**Skill:** `test-driven`

---

### Phase 7: Code Review
**Goal:** Review and refine

**Activities:**
- Code quality review
- Security review
- Performance review
- Documentation review

**Command:** `/code-review`

**Skill:** `code-review`

---

### Phase 8: Deployment
**Goal:** Deploy to production

**Activities:**
- Build production bundle
- Run deployment scripts
- Verify deployment
- Monitor for issues

## Workflow

```
Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6 → Phase 7 → Phase 8
   ↓         ↓         ↓         ↓         ↓         ↓         ↓         ↓
Discovery → PRD → Tech Spec → Jira → Development → Testing → Review → Deploy
```

## Tips

- Complete each phase before moving to the next
- Document decisions in `docs/decisions/`
- Use skills relevant to each phase
- Run `/test-review` and `/code-review` frequently in phases 5-7

---

## Prompt

```markdown
**Role**: You are a technical project manager guiding a development workflow through structured phases.

**Task**: Navigate to phase [PHASE_NUMBER] and provide guidance for completing it successfully.

**Context**:
- Current phase: [PHASE_NUMBER]
- Project: [PROJECT_NAME]
- Previous phases completed: [LIST]

**Reasoning**:
- Each phase builds on previous outputs
- Use relevant skills and commands for each phase
- Follow TDD in development phases
- Document all decisions

**Output Format**:
1. Phase overview (goal, activities, outputs)
2. Required skills/commands for this phase
3. Checklist of deliverables
4. Transition criteria to next phase

**Stopping Condition**:
- All phase activities explained
- Relevant commands and skills identified
- Clear success criteria defined

**Steps**:
1. Identify requested phase number
2. Load phase details from this command reference
3. Identify required skills (system-architect, atomic-design, test-driven, etc.)
4. Provide phase-specific guidance
5. List expected outputs
6. Define completion criteria

---
Phase: [PHASE_NUMBER]
Project: [PROJECT_NAME]
---
```
