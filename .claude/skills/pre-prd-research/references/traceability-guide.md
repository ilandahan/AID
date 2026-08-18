# Traceability Guide Reference

Complete guide to maintaining research-to-requirements traceability throughout the AID methodology.

## Traceability Overview

### Why Traceability Matters

```
┌─────────────────────────────────────────────────────────────────┐
│                 TRACEABILITY BENEFITS                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ✓ ACCOUNTABILITY                                               │
│    Every requirement traces back to validated research           │
│    No "pet features" without evidence                           │
│                                                                  │
│  ✓ COMPLETENESS                                                 │
│    No research finding gets "lost" in translation               │
│    Systematic coverage of all discoveries                        │
│                                                                  │
│  ✓ CHANGE MANAGEMENT                                            │
│    Know impact when requirements change                          │
│    Understand why decisions were made                            │
│                                                                  │
│  ✓ VALIDATION                                                   │
│    QA can test against original user needs                       │
│    Verify we built what was actually needed                      │
│                                                                  │
│  ✓ COMMUNICATION                                                │
│    Stakeholders understand requirement origins                   │
│    Decisions are transparent and defensible                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## ID Format Specification

### Standard Format

```
[PROJECT]-[ACTIVITY]-[TYPE]-[NUMBER]

Examples:
AUTH-A-INT-001    = Auth project, Activity A (Understand), Interview finding #1
DASH-B-IDEA-023   = Dashboard project, Activity B (Explore), Idea #23
PAY-C-OPP-005     = Payment project, Activity C (Define), Opportunity #5
```

### Activity Codes

| Code | Activity | Phase | Description |
|------|----------|-------|-------------|
| A | Understand | Research | Primary research and analysis |
| B | Explore | Research | Ideation and brainstorming |
| C | Define | Research | Synthesis and prioritization |
| R | Requirement | PRD | Formal requirements |
| T | Technical | Tech Spec | Technical specifications |

### Type Codes by Activity

#### Activity A - Understand
| Code | Type | Description |
|------|------|-------------|
| INT | Interview | User/stakeholder interview findings |
| SURV | Survey | Survey results and insights |
| COMP | Competitive | Competitor analysis findings |
| JTBD | Jobs-to-be-Done | Job statements |
| DATA | Data | Analytics/metrics findings |
| OBS | Observation | User observation notes |

#### Activity B - Explore
| Code | Type | Description |
|------|------|-------------|
| IDEA | Idea | Generated ideas |
| ROOT | Root Cause | 5 Whys analysis findings |
| HMW | How Might We | Problem reframes |
| PROTO | Prototype | Prototype test results |

#### Activity C - Define
| Code | Type | Description |
|------|------|-------------|
| OPP | Opportunity | Validated opportunities |
| BLUE | Blue Ocean | Strategic analysis |
| VPC | Value Prop | Value proposition canvas |
| SCORE | Score | Opportunity scoring |
| REC | Recommendation | Strategic recommendations |

---

## Creating the Traceability Matrix

### Matrix Template

```markdown
# Traceability Matrix: [Project Name]

**Project ID**: [PROJECT]
**Created**: [Date]
**Last Updated**: [Date]

## Research Findings Register

| ID | Type | Finding Summary | Status | PRD Links | Notes |
|----|------|-----------------|--------|-----------|-------|
| [PROJECT]-A-INT-001 | Interview | [Summary] | INCLUDE | US-001 | |
| [PROJECT]-A-INT-002 | Interview | [Summary] | DEFER | - | Phase 2 |
| [PROJECT]-A-COMP-001 | Competitive | [Summary] | INCLUDE | US-003 | |
| [PROJECT]-B-IDEA-001 | Idea | [Summary] | EXCLUDE | - | Too complex |
| [PROJECT]-C-OPP-001 | Opportunity | [Summary] | INCLUDE | US-001, US-002 | Core feature |

## Status Definitions

| Status | Meaning | Action |
|--------|---------|--------|
| INCLUDE | Will be implemented in current phase | Link to PRD requirement |
| DEFER | Valid but postponed | Document in roadmap |
| EXCLUDE | Not pursuing | Document rationale |
| VALIDATE | Needs more research | Plan validation |

## Requirements Traceability

| Requirement ID | Title | Research Backing | Assumption? |
|----------------|-------|------------------|-------------|
| US-001 | [Title] | A-INT-001, C-OPP-001 | No |
| US-002 | [Title] | C-OPP-001 | No |
| US-003 | [Title] | - | Yes: ASSUME-001 |

## Coverage Summary

### Forward Trace (Research → Requirements)
| Research Type | Total | INCLUDE | DEFER | EXCLUDE | Coverage |
|---------------|-------|---------|-------|---------|----------|
| Interviews (A-INT) | | | | | |
| Competitive (A-COMP) | | | | | |
| Ideas (B-IDEA) | | | | | |
| Opportunities (C-OPP) | | | | | |

### Backward Trace (Requirements → Research)
| Requirement Type | Total | With Research | Assumptions |
|------------------|-------|---------------|-------------|
| User Stories | | | |
| Success Metrics | | | |
```

---

## Workflow Integration

### During Research Phase

```
┌─────────────────────────────────────────────────────────────────┐
│                RESEARCH PHASE WORKFLOW                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. CAPTURE                                                      │
│     ├── Record finding in research notes                        │
│     ├── Assign ID immediately: [PROJECT]-[A/B/C]-[TYPE]-XXX    │
│     └── Add to Findings Register with status PENDING            │
│                                                                  │
│  2. CATEGORIZE                                                   │
│     ├── Review finding for relevance                            │
│     ├── Update status: INCLUDE / DEFER / EXCLUDE / VALIDATE    │
│     └── Document rationale                                       │
│                                                                  │
│  3. SYNTHESIZE                                                   │
│     ├── Group related findings                                  │
│     ├── Create Opportunity IDs (C-OPP-XXX)                      │
│     └── Link opportunities to source findings                   │
│                                                                  │
│  4. PRIORITIZE                                                   │
│     ├── Score opportunities                                     │
│     ├── Finalize INCLUDE list                                   │
│     └── Prepare handoff to PRD phase                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### During PRD Phase

```
┌─────────────────────────────────────────────────────────────────┐
│                PRD PHASE WORKFLOW                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  FOR EACH REQUIREMENT:                                          │
│                                                                  │
│  ┌─────────────────┐                                            │
│  │ New requirement │                                            │
│  │   identified    │                                            │
│  └────────┬────────┘                                            │
│           │                                                      │
│           ▼                                                      │
│  ┌─────────────────┐     YES    ┌─────────────────┐             │
│  │ Research backing│──────────▶│ Add research IDs│             │
│  │    exists?      │           │ to requirement  │             │
│  └────────┬────────┘           └─────────────────┘             │
│           │ NO                                                   │
│           ▼                                                      │
│  ┌─────────────────┐     NO     ┌─────────────────┐             │
│  │ Critical for    │──────────▶│ Consider deferring│            │
│  │     MVP?        │           │ to Phase 2       │             │
│  └────────┬────────┘           └─────────────────┘             │
│           │ YES                                                  │
│           ▼                                                      │
│  ┌─────────────────────────┐                                    │
│  │ Add to Assumptions Log: │                                    │
│  │ • ASSUME-XXX ID         │                                    │
│  │ • Document assumption   │                                    │
│  │ • Assess risk           │                                    │
│  │ • Define validation     │                                    │
│  └─────────────────────────┘                                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Validation Checklist

### Before Phase Transition

```markdown
## Traceability Validation Checklist

### Forward Trace (Research → Requirements)
- [ ] All INCLUDE findings have linked requirements
- [ ] DEFER findings documented in roadmap
- [ ] EXCLUDE findings have documented rationale
- [ ] No orphan research (findings with no decision)

### Backward Trace (Requirements → Research)
- [ ] Every requirement has research ID(s) OR assumption flag
- [ ] All referenced research IDs exist in matrix
- [ ] Assumptions have risk assessment
- [ ] Assumptions have validation plan

### Matrix Integrity
- [ ] All IDs follow naming convention
- [ ] No duplicate IDs
- [ ] All statuses are valid
- [ ] Coverage summary is accurate
- [ ] Matrix is up to date

### Documentation Quality
- [ ] Finding summaries are clear
- [ ] Rationales are documented
- [ ] Links are bidirectional
- [ ] Dates are current
```

---

## Handling Common Scenarios

### Scenario 1: New Finding Mid-PRD

```markdown
**Problem**: User mentions new pain point during PRD review

**Solution**:
1. Assign new research ID: [PROJECT]-A-INT-NEW-XXX
2. Add to matrix with status VALIDATE
3. Decide: INCLUDE (critical) or DEFER (nice-to-have)
4. If INCLUDE: Link to requirement, note late addition
5. Update coverage summary
```

### Scenario 2: Requirement Without Research

```markdown
**Problem**: PM wants feature not in research

**Solution**:
1. Challenge: Is this truly needed for MVP?
2. If YES: Add to Assumptions Log
   - ASSUME-XXX
   - Document the assumption clearly
   - Assess risk if wrong (Low/Medium/High)
   - Define validation plan (how to verify)
3. If NO: Defer to Phase 2
4. Never leave requirements unlinked
```

### Scenario 3: Conflicting Research

```markdown
**Problem**: Interview A says X, Interview B says not-X

**Solution**:
1. Document both findings with IDs
2. Note the conflict in both entries
3. Create validation opportunity: [PROJECT]-A-DATA-XXX
4. If resolution needed now:
   - More interviews? Survey?
   - Weight by user segment importance
   - Document decision rationale
5. Link to both findings in PRD with note
```

### Scenario 4: Research Finding Becomes Irrelevant

```markdown
**Problem**: Market changed, research no longer applies

**Solution**:
1. Update finding status to EXCLUDE
2. Document rationale: "Market shift - [date]"
3. Review all linked requirements
4. Remove or update linked requirements
5. Consider: New research needed?
6. Update coverage summary
```

---

## Tools and Automation

### Spreadsheet Setup

If using spreadsheets for matrix:

```
Sheet 1: Findings Register
- Columns: ID, Type, Summary, Source, Date, Status, PRD Links, Notes
- Filters: By Activity, By Status, By Type

Sheet 2: Requirements Register
- Columns: ID, Title, Description, Research IDs, Assumption?, Priority
- Validation: Research IDs exist in Sheet 1

Sheet 3: Coverage Dashboard
- Pivot tables: Findings by status, Requirements by backing
- Charts: Coverage percentages
- Alerts: Orphan findings, unlinked requirements

Sheet 4: Assumptions Log
- Columns: ID, Assumption, Risk, Impact, Validation Plan, Status
```

### ID Validation Script

```javascript
// Example validation (conceptual)
function validateTraceability(matrix, prd) {
  const issues = [];

  // Check all INCLUDE findings have PRD links
  matrix.findings
    .filter(f => f.status === 'INCLUDE')
    .forEach(f => {
      if (!f.prdLinks || f.prdLinks.length === 0) {
        issues.push(`Orphan finding: ${f.id}`);
      }
    });

  // Check all requirements have research or assumption
  prd.requirements.forEach(r => {
    if (!r.researchIds && !r.assumptionId) {
      issues.push(`Unlinked requirement: ${r.id}`);
    }
  });

  // Check all referenced IDs exist
  prd.requirements.forEach(r => {
    (r.researchIds || []).forEach(id => {
      if (!matrix.findings.find(f => f.id === id)) {
        issues.push(`Broken link: ${r.id} -> ${id}`);
      }
    });
  });

  return issues;
}
```

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────┐
│                TRACEABILITY QUICK REFERENCE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ID FORMAT:   [PROJECT]-[ACTIVITY]-[TYPE]-[NUMBER]              │
│                                                                  │
│  ACTIVITIES:  A = Understand  |  B = Explore  |  C = Define     │
│                                                                  │
│  TYPES:                                                          │
│    A: INT, SURV, COMP, JTBD, DATA, OBS                          │
│    B: IDEA, ROOT, HMW, PROTO                                    │
│    C: OPP, BLUE, VPC, SCORE, REC                                │
│                                                                  │
│  STATUSES:    INCLUDE | DEFER | EXCLUDE | VALIDATE              │
│                                                                  │
│  RULES:                                                          │
│    • Every finding gets an ID                                   │
│    • Every requirement needs research OR assumption             │
│    • Every INCLUDE finding needs PRD link                       │
│    • No broken links allowed                                    │
│                                                                  │
│  VALIDATION:                                                     │
│    ✓ Forward trace: Research → Requirements                     │
│    ✓ Backward trace: Requirements → Research                    │
│    ✓ No orphans (INCLUDE without links)                         │
│    ✓ No ghosts (links to non-existent IDs)                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```
