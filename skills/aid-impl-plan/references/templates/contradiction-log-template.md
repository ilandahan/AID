# Contradiction Log Template

## Purpose

This log documents ALL contradictions found between PRD, Tech Spec, and Research Report.
It provides an audit trail for resolution decisions and ensures source documents are fixed.

---

## Process

```
1. COMPARE documents section-by-section
2. LOG every contradiction found
3. RESOLVE using authority hierarchy
4. FIX source documents
5. THEN consolidate (safe)
```

---

## Authority Hierarchy

```
Research Report (data-driven findings)
       │
       ▼ overrides
     PRD (business requirements)
       │
       ▼ overrides
   Tech Spec (technical implementation)
```

**Exception:** Tech Spec overrides PRD on technical feasibility and security details.

---

## Contradiction Log Format

```markdown
# Contradiction Log

**Project:** [Project Name]
**Date:** YYYY-MM-DD
**Documents Compared:**
- PRD: [path]
- Tech Spec: [path]
- Research Report: [path or N/A]

---

## Summary

| ID | Topic | PRD Section | Tech Spec Section | Resolution | Status |
|----|-------|-------------|-------------------|------------|--------|
| C-01 | Token Expiry | 8.1 | 4.2 | Use Tech Spec | ✅ Fixed |
| C-02 | API Versioning | 5.3 | 3.1 | Use PRD | ✅ Fixed |
| C-03 | Password Rules | 8.1 | 4.3 | Merge both | ✅ Fixed |

**Total Contradictions:** X
**Resolved:** X
**Pending:** 0

---

## Detailed Contradictions

### C-01: Token Expiry

**Severity:** High (Security Impact)

**PRD Section 8.1 Says:**
> "[Exact quote from PRD]"

**Tech Spec Section 4.2 Says:**
> "[Exact quote from Tech Spec]"

**Type:** Technical Conflict

**Resolution:** Use Tech Spec

**Authority Applied:** Tech Spec (security details override PRD)

**Rationale:**
1. [Reason 1]
2. [Reason 2]
3. [Reason 3]

**Action Taken:**
- [ ] Updated PRD Section 8.1 to match Tech Spec
- [ ] Verified consistency

**Resolved By:** [Name/Role]
**Resolved Date:** YYYY-MM-DD

---

### C-02: [Topic]

**Severity:** [High/Medium/Low]

**PRD Section X.X Says:**
> "[Exact quote]"

**Tech Spec Section Y.Y Says:**
> "[Exact quote]"

**Type:** [Scope/Technical/Requirement/Terminology]

**Resolution:** [Use PRD / Use Tech Spec / Merge / New Decision]

**Authority Applied:** [Which document and why]

**Rationale:**
1. [Reason]

**Action Taken:**
- [ ] [What was updated]

**Resolved By:** [Name]
**Resolved Date:** YYYY-MM-DD

---
```

---

## Contradiction Types

| Type | Description | Example |
|------|-------------|---------|
| **Scope** | What's included/excluded differs | PRD: "Mobile app", Tech Spec: "Web only" |
| **Technical** | Implementation details conflict | PRD: "HS256", Tech Spec: "RS256" |
| **Requirement** | Feature behavior differs | PRD: "Email required", Tech Spec: "Email optional" |
| **Terminology** | Same concept, different names | PRD: "User", Tech Spec: "Account" |
| **Numeric** | Numbers don't match | PRD: "1 hour", Tech Spec: "15 minutes" |
| **Missing** | One doc has it, other doesn't | PRD: "Password reset", Tech Spec: (missing) |

---

## Severity Levels

| Level | Criteria | Action |
|-------|----------|--------|
| **Critical** | Blocks development, security risk | Fix immediately, escalate if needed |
| **High** | Affects user experience, multiple features | Fix before consolidation |
| **Medium** | Affects one feature, workaround exists | Fix during consolidation |
| **Low** | Cosmetic, terminology only | Fix during consolidation |

---

## Section Mapping Template

Before comparing, map related sections:

```markdown
## Section Mapping

| PRD Section | Tech Spec Section | Topic |
|-------------|-------------------|-------|
| 1. Problem Statement | 1.1 Overview | Project context |
| 2. User Personas | - | Users (PRD only) |
| 3. Requirements | 2. Architecture | System design |
| 4. User Stories | 3. API Design | Functionality |
| 5. API Requirements | 3. API Design | API contracts |
| 6. Data Model | 2.3 Data Model | Database |
| 7. UI/UX | 5. Frontend | User interface |
| 8. Security | 4. Security | Auth, encryption |
| 9. Success Metrics | - | KPIs (PRD only) |
| - | 6. Infrastructure | Deployment (Tech Spec only) |
```

---

## Comparison Checklist

For each mapped section pair:

- [ ] Read PRD section completely
- [ ] Read Tech Spec section completely
- [ ] Compare every:
  - [ ] Feature/capability mentioned
  - [ ] Numeric value (timeouts, limits, sizes)
  - [ ] Terminology/naming
  - [ ] Behavior description
  - [ ] Error handling
  - [ ] Edge cases
- [ ] Log ANY discrepancy (even minor)
- [ ] Determine resolution
- [ ] Update source document
- [ ] Mark as resolved

---

## Post-Resolution Verification

After all contradictions resolved:

- [ ] Re-read PRD - still coherent?
- [ ] Re-read Tech Spec - still coherent?
- [ ] Cross-check: PRD security = Tech Spec security?
- [ ] Cross-check: PRD API = Tech Spec API?
- [ ] Cross-check: PRD data model = Tech Spec data model?
- [ ] No new contradictions introduced by fixes?

**Only proceed to consolidation when all checks pass.**
