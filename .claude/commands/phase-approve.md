# /phase-approve

Human approval checkpoint for current phase.

## What It Does

1. Show summary of phase artifacts
2. Ask for explicit confirmation
3. Create approval file
4. Update state

## Flow

### Step 1: Summary

```
═══════════════════════════════════════════════════════
           PHASE 2 (Tech Spec) APPROVAL
═══════════════════════════════════════════════════════

Artifacts produced:
  📄 docs/tech-spec/YYYY-MM-DD-[feature].md
     - Architecture: Next.js + PostgreSQL
     - Data Models: 5 tables
     - API Endpoints: 12 endpoints
     - Components: 24 identified

This confirms:
  ✓ Technical approach is correct
  ✓ Architecture fits requirements
  ✓ Ready to break down into tasks

═══════════════════════════════════════════════════════

Type "approve" to confirm, or describe changes needed:
```

### Step 2: Handle Response

**If "approve":**
- Create approval artifact
- Update state

**If changes needed:**
- Acknowledge feedback
- Do NOT create approval
- List what to fix

### Step 3: Create Approval

Save to `.aid/approvals/tech-spec-approved.md`:

```markdown
# Phase 2 (Tech Spec) Approval

**Approved by:** Human
**Date:** 2025-12-10T14:30:00Z

## Approved Artifacts
- docs/tech-spec/YYYY-MM-DD-[feature].md

## Notes
[Any notes from human]
```

### Step 4: Confirm

```
═══════════════════════════════════════════════════════
✅ PHASE 2 APPROVED

Saved: .aid/approvals/tech-spec-approved.md

Run /phase-advance to move to Phase 3

═══════════════════════════════════════════════════════
                    DOCUMENT PATHS
═══════════════════════════════════════════════════════

Phase 1 (PRD)      → docs/prd/YYYY-MM-DD-[feature].md
Phase 2 (Tech Spec) → docs/tech-spec/YYYY-MM-DD-[feature].md
Phase 3 (Impl Plan) → docs/implementation-plan/YYYY-MM-DD-[feature].md
═══════════════════════════════════════════════════════
```
