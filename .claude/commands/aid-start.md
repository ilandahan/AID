# /aid start

Start a new work session with the AID Memory System.

## Purpose

Begin a tracked work session. Selects role FIRST, then shows phase options with role-specific terminology.

## Terminology Reference

Load role-specific phase names and descriptions from:
`.claude/references/role-phase-terminology.json`

## Flow

### Step 1: Start Required Services (Optional)

- Check if Figma MCP server is running: `curl -s http://localhost:3001/health`
- If not running and needed, start it:
  ```bash
  cd server && npm run dev &
  ```
- Report server status to user

### Step 2: Check Existing Session

Load `~/.aid/state.json`
- If active session exists, ask to continue or start new

```
Welcome back!

Last session:
- Role: [Previous Role]
- Phase: [Previous Phase Name]

Continue this session? (y/n)
```

### Step 3: Select Role (FIRST)

Display the role options as plain text (do NOT use AskUserQuestion tool - it has a 4-option limit):

```
What is your role today?

1. **Product Manager**
   Focuses on user value, requirements, and business outcomes

2. **Tech Lead**
   Focuses on architecture, technical decisions, and team guidance

3. **Developer**
   Focuses on implementation, code quality, and TDD

4. **QA Engineer**
   Focuses on testing, validation, and quality assurance

5. **Other** (describe your role)

Enter role number (1-5):
```

Wait for user to type their selection before proceeding to phase selection.

### Step 4: Select Phase (SECOND - with Role-Specific Terminology)

After role is selected, display phases as plain text with **bold phase names** (do NOT use AskUserQuestion tool).

#### If Role = Product Manager:

```
What phase are you working on? (Product Manager)

0. **Market & Competitive Research**
   Research competitors, market trends, and validate the problem space with stakeholders

1. **Product Requirements (PRD)**
   Define what we're building, user stories, acceptance criteria, and scope boundaries

2. **Solution Review**
   Review technical approach, ensure it aligns with product vision and user needs

3. **Roadmap & Prioritization**
   Prioritize features, define milestones, coordinate with stakeholders on timeline

4. **Feature Validation & UAT**
   Validate implemented features against requirements, conduct user acceptance testing

5. **Launch & Go-to-Market**
   Prepare release communications, coordinate launch, gather initial user feedback

6. **Other** (describe your work)

Enter phase number (0-6):
```

#### If Role = Tech Lead:

```
What phase are you working on? (Tech Lead)

0. **Technology & Architecture Research**
   Evaluate technologies, assess technical feasibility, research architectural patterns

1. **Technical Requirements Report**
   Translate business needs into technical requirements, identify constraints and risks

2. **System Architecture Design**
   Design system architecture, define APIs, data models, and integration patterns

3. **Sprint Planning & Task Breakdown**
   Break down work into epics/stories/tasks, estimate effort, assign to team members

4. **Code Review & Architecture Oversight**
   Review code quality, ensure architectural compliance, mentor developers

5. **Release Engineering & Deployment**
   Oversee deployment process, ensure operational readiness, manage release risks

6. **Other** (describe your work)

Enter phase number (0-6):
```

#### If Role = Developer:

```
What phase are you working on? (Developer)

0. **Technical Spike & Research**
   Prototype solutions, research libraries/frameworks, validate technical approaches

1. **Feature Specification**
   Understand requirements deeply, clarify edge cases, document technical assumptions

2. **Technical Design**
   Design component structure, plan implementation approach, identify dependencies

3. **Task Breakdown & Estimation**
   Break features into coding tasks, estimate complexity, identify blockers

4. **Implementation & Coding**
   Write production code with TDD, implement features, write unit/integration tests

5. **Bug Fixes & Polish**
   Fix bugs from QA, optimize performance, clean up code, update documentation

6. **Other** (describe your work)

Enter phase number (0-6):
```

#### If Role = QA Engineer:

```
What phase are you working on? (QA Engineer)

0. **Test Strategy Research**
   Research testing approaches, evaluate tools, understand system testability

1. **Test Requirements & Coverage Plan**
   Derive test requirements from PRD, plan coverage, identify risk areas

2. **Test Architecture & Framework**
   Design test framework, set up automation infrastructure, define test patterns

3. **Test Plan & Case Design**
   Write detailed test cases, design test data, plan regression suite

4. **Test Execution & Automation**
   Execute tests, automate test cases, report bugs, verify fixes

5. **Release Certification & Sign-off**
   Final regression, performance testing, sign off on release quality

6. **Other** (describe your work)

Enter phase number (0-6):
```

#### If Role = Other:

Use Developer terminology as default, but record the custom role description.

### Step 5: Handle "Other" Selections

**If "Other" role selected:**
- Ask: "Please describe your role for this session:"
- Record response in session state
- Use Developer phase terminology as default

**If "Other" phase selected:**
- Ask: "Please describe what you're working on:"
- Record response in session state
- Determine closest matching phase for skill loading

### Step 6: Load Skills

Based on the selected role and phase, load skills from `.claude/references/role-phase-terminology.json`:

1. **Role Skill**: Load from `roleSkillMapping[role]`
   - pm → `role-product-manager`
   - lead → `role-tech-lead`
   - developer → `role-developer`
   - qa → `role-qa-engineer`

2. **Phase Skills**: Load from `phases[role][phase].skills`
   - Example: Developer + Phase 4 → `["aid-development", "atomic-design", "atomic-page-builder", "test-driven", "code-review"]`

3. **Common Skills**: Always load:
   - `phase-enforcement`
   - `context-tracking`
   - `learning-mode`

Read and apply guidelines from:
- `.claude/skills/{role-skill}/SKILL.md`
- `.claude/skills/{each-phase-skill}/SKILL.md`

### Step 7: Update State

Save session to `~/.aid/state.json`:

```json
{
  "role": "developer",
  "role_display": "Developer",
  "phase": 4,
  "phase_display": "Implementation & Coding",
  "phase_description": "Write production code with TDD, implement features, write unit/integration tests",
  "session_start": "2024-01-15T09:00:00Z",
  "status": "active",
  "skills_loaded": [
    "role-developer",
    "aid-development",
    "atomic-design",
    "atomic-page-builder",
    "test-driven",
    "code-review",
    "phase-enforcement",
    "context-tracking",
    "learning-mode"
  ]
}
```

### Step 8: Greet User

```
✅ Session started

Role: Developer
Phase: Implementation & Coding
       Write production code with TDD, implement features, write unit/integration tests

Skills loaded:
  • role-developer
  • aid-development
  • atomic-design
  • test-driven
  • code-review
  • phase-enforcement
  • context-tracking

Ready to work! Use /aid end when completing this phase.
```

## Usage

```
/aid start
```

Or with parameters (using role-specific phase names or numbers):
```
/aid start developer 4
/aid start pm "Product Requirements"
```

## Quick Reference

| Role | Phase 0 | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Phase 5 |
|------|---------|---------|---------|---------|---------|---------|
| PM | Market Research | PRD | Solution Review | Roadmap | UAT | Launch |
| Lead | Tech Research | Tech Requirements | Architecture | Sprint Planning | Code Review | Deployment |
| Dev | Spike & Research | Feature Spec | Technical Design | Task Breakdown | Coding | Bug Fixes |
| QA | Test Strategy | Coverage Plan | Test Framework | Test Cases | Execution | Certification |

## Notes

- Role is selected FIRST, then phase (allows terminology to be customized)
- All 6 phases (0-5) are shown, plus "Other" option
- Phase names and descriptions are role-specific
- Skills are loaded based on role+phase combination
- Session state persists across conversations
- Use `/aid status` to check current state
- See `memory-system/docs/AGENT.md` for full behavior spec
