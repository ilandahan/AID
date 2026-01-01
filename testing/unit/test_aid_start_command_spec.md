# Test Specification: /aid-start Command Flow

> This document defines the expected behavior of the updated `/aid-start` command with role-based phase terminology.

## Test Cases

### TC-001: Role Selection (Step 1)

**Given**: User runs `/aid-start`
**When**: The command begins
**Then**: 
- [ ] Display role selection FIRST (before phase)
- [ ] Show exactly 5 options:
  1. Product Manager
  2. Tech Lead
  3. Developer
  4. QA Engineer
  5. Other (describe your role)
- [ ] Wait for user selection before proceeding

### TC-002: Phase Selection with PM Terminology

**Given**: User selected "Product Manager" as role
**When**: Phase selection is shown
**Then**:
- [ ] Show 7 options with PM-specific terminology:
  0. Market & Competitive Research
  1. Product Requirements (PRD)
  2. Solution Review
  3. Roadmap & Prioritization
  4. Feature Validation & UAT
  5. Launch & Go-to-Market
  6. Other (describe your work)
- [ ] Each option shows PM-specific description

### TC-003: Phase Selection with Tech Lead Terminology

**Given**: User selected "Tech Lead" as role
**When**: Phase selection is shown
**Then**:
- [ ] Show 7 options with Tech Lead-specific terminology:
  0. Technology & Architecture Research
  1. Technical Requirements Report
  2. System Architecture Design
  3. Sprint Planning & Task Breakdown
  4. Code Review & Architecture Oversight
  5. Release Engineering & Deployment
  6. Other (describe your work)

### TC-004: Phase Selection with Developer Terminology

**Given**: User selected "Developer" as role
**When**: Phase selection is shown
**Then**:
- [ ] Show 7 options with Developer-specific terminology:
  0. Technical Spike & Research
  1. Feature Specification
  2. Technical Design
  3. Task Breakdown & Estimation
  4. Implementation & Coding
  5. Bug Fixes & Polish
  6. Other (describe your work)

### TC-005: Phase Selection with QA Terminology

**Given**: User selected "QA Engineer" as role
**When**: Phase selection is shown
**Then**:
- [ ] Show 7 options with QA-specific terminology:
  0. Test Strategy Research
  1. Test Requirements & Coverage Plan
  2. Test Architecture & Framework
  3. Test Plan & Case Design
  4. Test Execution & Automation
  5. Release Certification & Sign-off
  6. Other (describe your work)

### TC-006: "Other" Role Handling

**Given**: User selected "Other" for role
**When**: Prompted for custom role
**Then**:
- [ ] Ask user to describe their role
- [ ] Use Developer terminology as default for phases
- [ ] Record custom role in session state

### TC-007: "Other" Phase Handling

**Given**: User selected any role, then "Other" for phase
**When**: Prompted for custom phase
**Then**:
- [ ] Ask user to describe their current work
- [ ] Record custom phase description in session state
- [ ] Load appropriate skills based on closest matching phase

### TC-008: Skills Loading

**Given**: User selects role and phase
**When**: Session starts
**Then**:
- [ ] Load role-specific skill from `roleSkillMapping`
- [ ] Load phase-specific skills from `phases[role][phase].skills`
- [ ] Load common skills: phase-enforcement, context-tracking, learning-mode
- [ ] Display loaded skills to user

### TC-009: State Persistence

**Given**: User completes role and phase selection
**When**: Session is created
**Then**:
- [ ] Save to `~/.aid/state.json`:
  ```json
  {
    "role": "developer",
    "role_display": "Developer",
    "phase": 4,
    "phase_display": "Implementation & Coding",
    "session_start": "ISO-8601 timestamp",
    "status": "active"
  }
  ```
- [ ] Note: phase_display uses role-specific terminology

### TC-010: All 6 Phases Available

**Given**: User runs `/aid-start`
**When**: Phase selection is shown
**Then**:
- [ ] ALL 6 phases (0-5) are displayed
- [ ] Plus "Other" option (option 6)
- [ ] Total of 7 options visible

### TC-011: Phase Descriptions Shown

**Given**: User sees phase selection
**When**: Looking at options
**Then**:
- [ ] Each phase shows its role-specific description
- [ ] Descriptions help user understand what work belongs in each phase

### TC-012: Terminology JSON Reference

**Given**: Command is executing
**When**: Building role/phase options
**Then**:
- [ ] Command references `.claude/references/role-phase-terminology.json`
- [ ] Terminology is loaded dynamically, not hardcoded

---

## Acceptance Criteria

For the `/aid-start` update to be complete:

1. ✅ Role selection happens FIRST
2. ✅ Phase selection happens SECOND (after role chosen)
3. ✅ Phase names are role-specific
4. ✅ Phase descriptions are role-specific
5. ✅ All 6 phases (0-5) are shown
6. ✅ "Other" option exists for both role and phase
7. ✅ Correct skills are loaded per role+phase combination
8. ✅ Session state includes role-specific display names

---

## Manual Test Procedure

1. Run `/aid-start`
2. Verify role options shown (5 options)
3. Select "Product Manager"
4. Verify PM-specific phase names shown (7 options)
5. Select phase 0
6. Verify "Market & Competitive Research" displayed
7. Verify correct skills loaded

Repeat for each role to confirm terminology mapping.
