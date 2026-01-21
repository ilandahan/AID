# Role-Based Phase Terminology

> This document defines how phases are named and described for each persona in the AID methodology.

## Overview

Different roles think in different terms. This mapping ensures each persona sees phase names and descriptions that match their mental model and industry terminology.

---

## Roles

| ID | Name | Short | Focus |
|----|------|-------|-------|
| `pm` | Product Manager | PM | User value, requirements, business outcomes |
| `lead` | Tech Lead | Lead | Architecture, technical decisions, team guidance |
| `developer` | Developer | Dev | Implementation, code quality, TDD |
| `qa` | QA Engineer | QA | Testing, validation, quality assurance |

---

## Phase Terminology by Role

### Product Manager (PM)

| Phase | Name | Description | Skills |
|-------|------|-------------|--------|
| 0 | Market & Competitive Research | Research competitors, market trends, and validate the problem space with stakeholders | pre-prd-research, aid-discovery, nano-banana-visual |
| 1 | Product Requirements (PRD) | Define what we're building, user stories, acceptance criteria, and scope boundaries | aid-prd |
| 2 | Solution Review | Review technical approach, ensure it aligns with product vision and user needs | aid-tech-spec, system-architect |
| 3 | Roadmap & Prioritization | Prioritize features, define milestones, coordinate with stakeholders on timeline | - |
| 4 | Feature Validation & UAT | Validate implemented features against requirements, conduct user acceptance testing | aid-development, atomic-design, atomic-page-builder |
| 5 | Launch & Go-to-Market | Prepare release communications, coordinate launch, gather initial user feedback | aid-qa-ship |

---

### Tech Lead

| Phase | Name | Description | Skills |
|-------|------|-------------|--------|
| 0 | Technology & Architecture Research | Evaluate technologies, assess technical feasibility, research architectural patterns | pre-prd-research, aid-discovery, nano-banana-visual |
| 1 | Technical Requirements Report | Translate business needs into technical requirements, identify constraints and risks | aid-prd |
| 2 | System Architecture Design | Design system architecture, define APIs, data models, and integration patterns | aid-tech-spec, system-architect |
| 3 | Sprint Planning & Task Breakdown | Break down work into epics/stories/tasks, estimate effort, assign to team members | - |
| 4 | Code Review & Architecture Oversight | Review code quality, ensure architectural compliance, mentor developers | aid-development, code-review, test-driven |
| 5 | Release Engineering & Deployment | Oversee deployment process, ensure operational readiness, manage release risks | aid-qa-ship, code-review |

---

### Developer

| Phase | Name | Description | Skills |
|-------|------|-------------|--------|
| 0 | Technical Spike & Research | Prototype solutions, research libraries/frameworks, validate technical approaches | pre-prd-research, aid-discovery |
| 1 | Feature Specification | Understand requirements deeply, clarify edge cases, document technical assumptions | aid-prd |
| 2 | Technical Design | Design component structure, plan implementation approach, identify dependencies | aid-tech-spec, system-architect |
| 3 | Task Breakdown & Estimation | Break features into coding tasks, estimate complexity, identify blockers | - |
| 4 | Implementation & Coding | Write production code with TDD, implement features, write unit/integration tests | aid-development, atomic-design, atomic-page-builder, test-driven, code-review |
| 5 | Bug Fixes & Polish | Fix bugs from QA, optimize performance, clean up code, update documentation | aid-qa-ship, test-driven, code-review |

---

### QA Engineer

| Phase | Name | Description | Skills |
|-------|------|-------------|--------|
| 0 | Test Strategy Research | Research testing approaches, evaluate tools, understand system testability | pre-prd-research, aid-discovery |
| 1 | Test Requirements & Coverage Plan | Derive test requirements from PRD, plan coverage, identify risk areas | aid-prd |
| 2 | Test Architecture & Framework | Design test framework, set up automation infrastructure, define test patterns | aid-tech-spec, test-driven |
| 3 | Test Plan & Case Design | Write detailed test cases, design test data, plan regression suite | test-driven |
| 4 | Test Execution & Automation | Execute tests, automate test cases, report bugs, verify fixes | aid-development, test-driven |
| 5 | Release Certification & Sign-off | Final regression, performance testing, sign off on release quality | aid-qa-ship, test-driven |

---

## Common Skills (Always Loaded)

These skills are loaded regardless of role or phase:

- `phase-enforcement` - Ensures work stays within allowed phase
- `context-tracking` - Maintains task/step state across sessions  
- `learning-mode` - Decision transparency and feedback collection

---

## Role Skill Mapping

Each role has a dedicated skill file:

| Role | Skill File |
|------|------------|
| pm | role-product-manager |
| lead | role-tech-lead |
| developer | role-developer |
| qa | role-qa-engineer |

---

## Usage

This terminology is used by:
1. `/aid-start` command - To display role-appropriate phase names
2. Role SKILL.md files - For phase-specific guidance
3. `phase-enforcement` - To validate work against phase permissions

See `.claude/references/role-phase-terminology.json` for the machine-readable version.
