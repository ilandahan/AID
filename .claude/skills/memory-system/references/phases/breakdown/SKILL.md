# Breakdown Phase Skill

> **Source**: `.claude/commands/jira-breakdown.md`
>
> This file is a reference. The main prompt is in the `.claude/commands/` directory.
> Use the `/jira-breakdown` command for work breakdown generation.

## Quick Reference

**Phase**: 3 - Breakdown
**Command**: `/jira-breakdown [feature-name]`
**Output**: Epics, Stories, Tasks, Subtasks with estimates

### Entry Criteria
- Tech Spec phase completed and approved
- Architecture decisions documented
- API contracts defined
- Data models specified

### Exit Criteria
- All work items created in breakdown
- Estimates assigned (Story Points + Hours)
- Dependencies documented
- Sprint plan created
- Team review completed

### Jira Hierarchy

| Level | Size | Contains |
|-------|------|----------|
| Epic | 2-6 weeks | 3-10 Stories |
| Story | 1-5 days | 2-5 Tasks |
| Task | 2-8 hours | 2-6 Subtasks |
| Subtask | 30min-2h | — |

### Key Deliverables
1. Epic Overview (with priorities)
2. Stories with User Story format + Acceptance Criteria
3. Tasks with technical descriptions + estimates
4. Subtasks as atomic work units
5. Dependencies Map
6. Sprint Plan
7. Risk Assessment

## Cumulative Learnings

See `cumulative.md` for project-specific learnings captured by the memory system.
