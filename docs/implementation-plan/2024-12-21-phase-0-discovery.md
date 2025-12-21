# Implementation Plan: Phase 0 - Discovery & Research

## Overview

**Goal:** Add Phase 0 (Discovery & Research) to the AID methodology, making `pre-prd-research` and `aid-discovery` skills accessible to users with proper commands, gate checks, and Nano Banana Pro integration.

**Current State:** 5-phase system (1-5: PRD, Tech Spec, Implementation Plan, Development, QA & Ship)

**Target State:** 6-phase system (0-5: Discovery, PRD, Tech Spec, Implementation Plan, Development, QA & Ship)

---

## Implementation Tasks

### Task 1: Create `/discovery` Slash Command
**File:** `.claude/commands/discovery.md`
**Acceptance Criteria:**
- Command invokes `pre-prd-research` and `aid-discovery` skills
- Guides user through research activities
- Creates output in `docs/research/YYYY-MM-DD-[project-name]/`
- Offers Nano Banana Pro for visual artifacts (if enabled)
- Shows clear next steps to Phase 1

**Implementation:**
```markdown
# /discovery

Start Phase 0: Discovery & Research

## Purpose
Validate problem space before writing PRD. Uses pre-prd-research and aid-discovery skills.

## Flow
1. Check if Nano Banana Pro is enabled (offer visual generation)
2. Guide through research activities:
   - Problem validation
   - Stakeholder identification
   - Competitive analysis
   - Root cause analysis
3. Create research artifacts in docs/research/
4. Generate traceability matrix
5. Prepare for Phase 1 transition
```

---

### Task 2: Update Phase-Enforcement Skill for Phase 0
**File:** `.claude/skills/phase-enforcement/SKILL.md`
**Acceptance Criteria:**
- Add Phase 0 to phase definitions
- Add Phase 0 detection patterns ("research", "discovery", "stakeholder", "competitive analysis")
- Add Phase 0 → 1 review checklist
- Update PHASE_ALLOWED mapping
- Update violation templates

**Changes Required:**

1. **Phase definitions table** - Add row for Phase 0:
   ```
   | 0 | Discovery | Research & Validation | docs/research/ |
   ```

2. **PHASE_ALLOWED mapping** - Add Phase 0:
   ```javascript
   const PHASE_ALLOWED = {
     0: ["research"],
     1: ["research", "requirements"],
     // ... rest unchanged
   };
   ```

3. **Detection patterns** - Add Phase 0:
   ```
   Phase 0 (research): "research", "discovery", "stakeholder", "competitive",
                       "market analysis", "problem validation", "root cause"
   ```

4. **Phase 0 → 1 Review Checklist:**
   ```
   1. Problem statement validated (SCQ format)
   2. Stakeholders identified and mapped
   3. Competitive landscape documented
   4. Root causes identified
   5. Success metrics defined
   6. Research findings have IDs (RES-XXX)
   7. Traceability matrix created
   8. Go/No-Go decision documented
   ```

---

### Task 3: Update `.aid/state.json` Schema
**File:** `.claude/commands/aid-init.md` (template section)
**File:** `templates/.aid/state.json`
**Acceptance Criteria:**
- Support `current_phase: 0`
- Add `phase_name: "Discovery"` mapping
- Update phase name mappings in all commands

**Changes Required:**

1. **Phase name mapping:**
   ```javascript
   const PHASE_NAMES = {
     0: "Discovery",
     1: "PRD",
     2: "Tech Spec",
     3: "Implementation Plan",
     4: "Development",
     5: "QA & Ship"
   };
   ```

2. **Default initial state:**
   ```json
   {
     "current_phase": 0,
     "phase_name": "Discovery"
   }
   ```

---

### Task 4: Update `/aid-start` Command
**File:** `.claude/commands/aid-start.md`
**Acceptance Criteria:**
- Include Phase 0 in phase selection menu
- Load `pre-prd-research` and `aid-discovery` skills for Phase 0
- Show Nano Banana Pro availability for Phase 0

**Changes Required:**

1. **Phase selection menu:**
   ```
   Select phase:
   [0] Discovery - Research & problem validation
   [1] PRD - Product requirements
   [2] Tech Spec - Technical specification
   [3] Implementation Plan - Task breakdown
   [4] Development - Code & tests
   [5] QA & Ship - Release
   ```

2. **Skills to load for Phase 0:**
   ```
   - pre-prd-research
   - aid-discovery
   - nano-banana-visual (if enabled)
   ```

---

### Task 5: Update `/phase` Command
**File:** `.claude/commands/phase.md`
**Acceptance Criteria:**
- Show Phase 0 in phase diagram
- Show Phase 0 requirements and deliverables
- Align with 6-phase system

**Changes Required:**

1. **Phase diagram:**
   ```
   Phase 0 ──► Gate ──► Phase 1 ──► Gate ──► Phase 2 ──► ...
   Discovery     ✓        PRD        ✓      Tech Spec
   ```

2. **Phase 0 section:**
   ```
   ## Phase 0: Discovery

   **Purpose:** Validate problem space before PRD

   **Deliverables:**
   - Research report (docs/research/)
   - Stakeholder map
   - Competitive analysis
   - Traceability matrix

   **Gate Requirements:**
   - Problem validated
   - Stakeholders identified
   - Go/No-Go decision documented
   ```

---

### Task 6: Update `/phase-advance` Command
**File:** `.claude/commands/phase-advance.md`
**Acceptance Criteria:**
- Handle Phase 0 → 1 transition
- Update phase name correctly
- Max phase remains 5

**Changes Required:**

1. **Phase name mapping update:**
   ```
   0 → "Discovery"
   1 → "PRD"
   ... (rest unchanged)
   ```

2. **Validation update:**
   ```
   - Min phase: 0
   - Max phase: 5
   ```

---

### Task 7: Update `/gate-check` Command
**File:** `.claude/commands/gate-check.md`
**Acceptance Criteria:**
- Add Phase 0 gate checks
- Check for research artifacts
- Check for traceability matrix

**Changes Required:**

1. **Phase 0 checks:**
   ```
   Phase 0 (Discovery) Gate Check:
   - [ ] docs/research/ directory exists
   - [ ] research-report.md present
   - [ ] traceability-matrix.md present
   - [ ] Problem statement in SCQ format
   - [ ] Stakeholders identified
   - [ ] Go/No-Go decision documented
   ```

---

### Task 8: Create Phase 0 Memory System Files
**Files:**
- `memory-system/skills/phases/discovery/SKILL.md`
- `memory-system/skills/phases/discovery/cumulative.md`

**Acceptance Criteria:**
- Follow existing phase skill format
- Include quick reference for Phase 0
- Support learning accumulation

---

### Task 9: Update Nano Banana Pro Integration
**File:** `.claude/skills/nano-banana-visual/SKILL.md`
**Acceptance Criteria:**
- Add Phase 0 visual types
- Document stakeholder map generation
- Document problem impact diagrams

**Changes Required:**

1. **Phase integration table:**
   ```
   | AID Phase | Trigger | Output |
   |-----------|---------|--------|
   | Discovery | "Create stakeholder map" | Stakeholder diagram |
   | Discovery | "Create problem diagram" | Problem impact visual |
   | Discovery | "Create competitive matrix" | Competitive landscape |
   ```

2. **Add prompt templates for Phase 0:**
   - Stakeholder map template
   - Problem impact diagram template
   - Competitive landscape template

---

### Task 10: Update CLAUDE.md
**File:** `CLAUDE.md`
**Acceptance Criteria:**
- Update phase permissions table
- Add Phase 0 to commands list
- Update phase diagram

**Changes Required:**

1. **Phase permissions:**
   ```
   | Phase | Allowed | Blocked |
   |-------|---------|---------|
   | 0 Discovery | Research, stakeholders, analysis | Requirements, code, architecture |
   | 1 PRD | + Requirements, scope, user stories | Code, architecture, Jira |
   ```

2. **Commands list:**
   ```
   | `/discovery` | Start Phase 0 research |
   ```

---

### Task 11: Update README.md
**File:** `README.md`
**Acceptance Criteria:**
- Update phase diagram to show 6 phases
- Add Phase 0 description
- Add `/discovery` command to table

---

### Task 12: Create Tests for Phase 0
**File:** `testing/e2e/test_phase_0.py`
**Acceptance Criteria:**
- Test Phase 0 initialization
- Test `/discovery` command execution
- Test Phase 0 → 1 gate check
- Test Phase 0 → 1 transition
- Test Nano Banana Pro integration (when enabled)

**Test Cases:**

```python
class TestPhase0Discovery:

    def test_aid_init_starts_at_phase_0(self):
        """After /aid-init, current_phase should be 0"""

    def test_discovery_command_creates_research_folder(self):
        """Running /discovery creates docs/research/ structure"""

    def test_phase_0_gate_check_validates_research(self):
        """/gate-check for Phase 0 checks research artifacts"""

    def test_phase_0_to_1_requires_approval(self):
        """Cannot advance to Phase 1 without approval"""

    def test_phase_0_blocks_code_work(self):
        """Phase 0 should block coding requests"""

    def test_phase_0_allows_research_work(self):
        """Phase 0 should allow research activities"""

    def test_nano_banana_available_in_phase_0(self):
        """Nano Banana Pro works for stakeholder maps"""
```

---

## File Change Summary

| File | Action | Priority |
|------|--------|----------|
| `.claude/commands/discovery.md` | CREATE | High |
| `.claude/skills/phase-enforcement/SKILL.md` | MODIFY | High |
| `.claude/commands/aid-init.md` | MODIFY | High |
| `.claude/commands/aid-start.md` | MODIFY | High |
| `.claude/commands/phase.md` | MODIFY | High |
| `.claude/commands/phase-advance.md` | MODIFY | Medium |
| `.claude/commands/gate-check.md` | MODIFY | Medium |
| `memory-system/skills/phases/discovery/SKILL.md` | CREATE | Medium |
| `memory-system/skills/phases/discovery/cumulative.md` | CREATE | Medium |
| `.claude/skills/nano-banana-visual/SKILL.md` | MODIFY | Medium |
| `CLAUDE.md` | MODIFY | Medium |
| `README.md` | MODIFY | Low |
| `testing/e2e/test_phase_0.py` | CREATE | High |
| `templates/.aid/state.json` | MODIFY | Medium |

---

## Implementation Order

1. **Task 2** - Update phase-enforcement (foundation)
2. **Task 3** - Update state.json schema
3. **Task 1** - Create /discovery command
4. **Task 4** - Update /aid-start
5. **Task 5** - Update /phase
6. **Task 6** - Update /phase-advance
7. **Task 7** - Update /gate-check
8. **Task 8** - Create memory system files
9. **Task 9** - Update Nano Banana Pro
10. **Task 10** - Update CLAUDE.md
11. **Task 11** - Update README.md
12. **Task 12** - Create tests

---

## Rollback Plan

If issues occur:
1. Revert all file changes via git
2. Phase system returns to 5-phase (1-5)
3. No data loss - research folder remains

---

## Success Criteria

1. User can run `/discovery` to start Phase 0
2. `/aid-start` shows Phase 0 option
3. `/phase` shows 6-phase diagram
4. Phase 0 → 1 transition requires gate approval
5. Nano Banana Pro can generate stakeholder maps in Phase 0
6. All existing tests still pass
7. New Phase 0 tests pass

---

## Estimated Effort

| Task | Complexity | Files |
|------|------------|-------|
| Task 1 | Medium | 1 |
| Task 2 | High | 1 |
| Task 3 | Low | 2 |
| Task 4 | Medium | 1 |
| Task 5 | Medium | 1 |
| Task 6 | Low | 1 |
| Task 7 | Medium | 1 |
| Task 8 | Low | 2 |
| Task 9 | Medium | 1 |
| Task 10 | Low | 1 |
| Task 11 | Low | 1 |
| Task 12 | High | 1 |

---

*This implementation plan was created following AID Phase 3 methodology.*

*Licensed under AID Community License v1.0*
