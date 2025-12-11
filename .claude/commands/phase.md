# /phase

Show current phase status and requirements.

## What It Does

1. Read `.aid/state.json`
2. Display current phase with visual indicator
3. Show completed vs locked phases
4. Show what's allowed/blocked

## Output Format

```
═══════════════════════════════════════════════════════
                    AID PHASE STATUS
═══════════════════════════════════════════════════════

Current Phase: [2] TECH SPEC
Started: 2025-12-10 11:30

═══════════════════════════════════════════════════════

✅ Phase 1: PRD
   └─ docs/prd/YYYY-MM-DD-[feature].md ✓
   └─ Approved: 2025-12-10 11:30 ✓

🔄 Phase 2: Tech Spec (IN PROGRESS)
   Required:
   └─ [ ] docs/tech-spec/YYYY-MM-DD-[feature].md
   └─ [ ] Human approval

⏳ Phase 3: Implementation Plan (LOCKED)
   Required:
   └─ [ ] docs/implementation-plan/YYYY-MM-DD-[feature].md
   └─ [ ] Human approval

⏳ Phase 4: Development (LOCKED)
⏳ Phase 5: QA & Ship (LOCKED)

═══════════════════════════════════════════════════════

ALLOWED in Phase 2:
  ✅ Architecture design
  ✅ Database schema
  ✅ API definitions
  ✅ Component planning

BLOCKED until Phase 4:
  ❌ Writing production code
  ❌ Creating components

═══════════════════════════════════════════════════════

Next: Complete Tech Spec, then /phase-approve

═══════════════════════════════════════════════════════
                    DOCUMENT PATHS
═══════════════════════════════════════════════════════

Phase 1 → docs/prd/YYYY-MM-DD-[feature].md
Phase 2 → docs/tech-spec/YYYY-MM-DD-[feature].md
Phase 3 → docs/implementation-plan/YYYY-MM-DD-[feature].md

All documents use date prefix for versioning.
Test-driven skill reads latest version from each folder.
═══════════════════════════════════════════════════════
```

## If No State File

```
⚠️ No .aid/state.json found

This project isn't initialized with AID.
Run /aid-init to start Phase 1 (PRD)
```
