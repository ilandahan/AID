---
name: figma-design-review
description: AI-powered design review for Figma components with weighted dual-scoring system. Evaluates Style Guide Implementation (70%) and LLM Metadata Accessibility (30%) to produce actionable reports. For export, this skill hands off to atomic-design skill.
version: 2.1.0
---

# Figma Design Review Skill

Review and score Figma component designs using a **weighted dual-scoring system**.

## Purpose

This skill enables Claude to:
1. **Evaluate** components on two dimensions: Implementation Quality & LLM Accessibility
2. **Score** using weighted formula: (Implementation × 0.7) + (LLM Accessibility × 0.3)
3. **Identify** strengths and weaknesses with actionable recommendations
4. **Generate** professional reports in English
5. **Hand off to `atomic-design` skill** for export and code generation

## Two-Skill Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  FIGMA PLUGIN WORKFLOW                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────┐                               │
│  │  figma-design-review        │  ◄── THIS SKILL               │
│  │         (PHASE 1)           │                               │
│  ├─────────────────────────────┤                               │
│  │ • Score components (70/30)  │                               │
│  │ • Identify issues           │                               │
│  │ • Analyze metadata gaps     │                               │
│  │ • Recommend fixes           │                               │
│  │ • Determine export readiness│                               │
│  └──────────────┬──────────────┘                               │
│                 │ Score >= 70?                                 │
│                 ▼                                               │
│  ┌─────────────────────────────┐                               │
│  │     atomic-design           │  ◄── EXPORT SKILL             │
│  │         (PHASE 2)           │                               │
│  ├─────────────────────────────┤                               │
│  │ • Classify level (A/M/O)    │                               │
│  │ • Determine folder path     │                               │
│  │ • Generate component files  │                               │
│  │ • Extract tokens from Figma │                               │
│  │ • Apply Figma-first rules   │                               │
│  └─────────────────────────────┘                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

> **Why two skills?** The `atomic-design` skill is also used by `atomic-page-builder`.
> By delegating export to `atomic-design`, we ensure consistent classification and
> file structure across both the Figma plugin and the page builder.

## Scoring Philosophy

| Dimension | Weight | Focus |
|-----------|--------|-------|
| **Style Guide Implementation** | 70% | Code quality, consistency, accessibility states, visual correctness |
| **LLM Metadata Accessibility** | 30% | Documentation quality for AI code generation |

> **Why this weighting?** Implementation quality directly impacts user experience and production code. Metadata accessibility enables efficient AI-assisted development but is secondary to functional correctness.

---

## When to Use

| Trigger | Action |
|---------|--------|
| Designer selects component in Figma | Run full design review |
| "Review this component" | Generate scored report |
| "What's missing?" | Gap analysis with recommendations |
| "Is this ready for export?" | Export readiness check |
| Score < 80 | Provide improvement roadmap |

---

## Scoring System

### Dimension 1: Style Guide Implementation (70% weight)

**Maximum Score: 100 points**

#### 1.1 Variant Structure (25 points)
| Criterion                   | Points | Check |
|---------                     --|--------|-------|
| Complete variant matrix       | 10 | All Size × State × Style combinations exist |
| Consistent naming convention | 5 | `Size=X, State=Y, Style=Z` format |
| TypeScript interface defined | 5 | Props with proper types and defaults |
| Logical variant organization | 5 | Grouped by primary axis (size/style) |

#### 1.2 Token System (25 points)
| Criterion | Points | Check |
|-----------|--------|-------|
| CSS Variables for colors | 10 | `var(--color/name)` not hardcoded hex |
| CSS Variables for typography | 5 | `var(--font-family/...)` usage |
| CSS Variables for spacing | 5 | Consistent padding/margin tokens |
| Semantic token naming | 5 | Meaningful names (azure, primary) not (color1) |

#### 1.3 Visual Consistency (20 points)
| Criterion | Points | Check |
|-----------|--------|-------|
| Consistent font-weight across variants | 5 | No 500 vs 600 mismatches |
| Consistent border-radius | 5 | Same radius across all variants |
| Consistent padding/spacing | 5 | No arbitrary variations |
| No layout artifacts | 5 | No unwanted translate/transform |

#### 1.4 Accessibility States (20 points)
| Criterion | Points | Check |
|-----------|--------|-------|
| Focus state present | 8 | Visible focus ring for keyboard nav |
| Disabled state present | 6 | All sizes have disabled variant |
| Hover state present | 4 | Interactive feedback |
| Touch target ≥ 44px | 2 | WCAG compliance |

#### 1.5 Code Quality (10 points)
| Criterion | Points | Check |
|-----------|--------|-------|
| No code duplication | 5 | Shared logic extracted |
| Clean conditional structure | 3 | Readable variant logic |
| Proper default values | 2 | Sensible fallbacks |

---

### Dimension 2: LLM Metadata Accessibility (30% weight)

**Maximum Score: 100 points**

#### 2.1 Component Description (20 points)
| Criterion | Points | Check |
|-----------|--------|-------|
| Primary description (2-3 sentences) | 10 | Clear purpose and use case |
| Use case specified | 5 | Where/when to use |
| Conversion/analytics context | 5 | Business purpose if applicable |

#### 2.2 Searchability (15 points)
| Criterion | Points | Check |
|-----------|--------|-------|
| Tags present | 8 | Comma-separated keywords |
| Tags comprehensive | 7 | Covers: type, purpose, location, action |

#### 2.3 Development Metadata (25 points)
| Criterion | Points | Check |
|-----------|--------|-------|
| `testId` defined | 5 | For automated testing |
| `ariaLabel` defined | 5 | Accessibility label |
| `analytics` event name | 5 | For tracking |
| `category` specified | 5 | Component type |
| `level` specified | 5 | Atomic hierarchy |

#### 2.4 Usage Guidelines (20 points)
| Criterion | Points | Check |
|-----------|--------|-------|
| Do's list | 7 | Recommended practices |
| Don'ts list | 7 | Anti-patterns to avoid |
| Notes/guidelines | 6 | Usage context |

#### 2.5 Technical Specifications (20 points)
| Criterion | Points | Check |
|-----------|--------|-------|
| Design tokens documented | 8 | Colors, spacing, typography |
| Specs documented | 6 | minWidth, minHeight, touchTarget |
| A11y requirements | 6 | Contrast ratios, ARIA needs |

---

## Report Output Format

> **Important:** See `./references/audit-summary-format.md` for the complete output specification.
>
> **Key Rules:**
> - Every weakness **MUST include a fix** → `⚠️ [Issue] → **Fix:** [Solution]`
> - Every issue **MUST name the specific field/property** with the error (e.g., `Property: State` not just "typo found")
> - Strengths capped at 6 items (prioritize notable ones)
> - Weaknesses capped at 5 items (focus on impactful issues)
> - Recommendations ordered by priority (critical first)
> - English only for all output

### Report Structure

```markdown
## 🎯 Component Evaluation: [Component Name]

### 1️⃣ Style Guide Implementation: **[XX]/100**

**Strengths:**
- ✅ [Positive finding 1]
- ✅ [Positive finding 2]

**Weaknesses:**
- ⚠️ [Issue 1] - [explanation]
- ⚠️ [Issue 2] - [explanation]

---

### 2️⃣ LLM Metadata Accessibility: **[XX]/100**

**[Excellent!/Good/Needs Work] Includes:**
- ✅ [Present metadata 1]
- ✅ [Present metadata 2]

**Missing:**
- ❌ [Missing metadata 1]

---

## 📊 Final Weighted Score

| Criterion | Score | Weight | Contribution |
|-----------|-------|--------|--------------|
| Style Guide Implementation | **XX** | 70% | XX.X |
| LLM Accessibility | **XX** | 30% | XX.X |
| **Total Weighted** | | | **XX.X/100** |

---

### 💡 Recommendations for Improvement:

1. **[Recommendation 1]** - [explanation]
2. **[Recommendation 2]** - [explanation]

**Overall Assessment:** [Summary statement]
```

---

## Score Interpretation

| Weighted Score | Grade | Export Status | Action |
|----------------|-------|---------------|--------|
| 90-100 | 🌟 Excellent | Ready | Export immediately |
| 80-89 | ✅ Good | Ready with notes | Export, note improvements |
| 70-79 | ⚠️ Acceptable | Conditional | Fix critical issues first |
| 60-69 | 🔶 Needs Work | Not ready | Significant improvements needed |
| < 60 | ❌ Poor | Blocked | Major rework required |

---

## TypeScript Interface

```typescript
interface DesignReviewReport {
  // Component identification
  component: {
    id: string;
    name: string;
    displayName: string;
    figmaUrl?: string;
  };

  // Dual scoring system
  scores: {
    implementation: {
      total: number;          // 0-100
      variantStructure: number;
      tokenSystem: number;
      visualConsistency: number;
      accessibilityStates: number;
      codeQuality: number;
    };
    llmAccessibility: {
      total: number;          // 0-100
      description: number;
      searchability: number;
      devMetadata: number;
      usageGuidelines: number;
      technicalSpecs: number;
    };
    weighted: number;         // (impl × 0.7) + (llm × 0.3)
  };

  // Detailed findings
  findings: {
    strengths: Finding[];
    weaknesses: Finding[];
  };

  // Actionable recommendations
  recommendations: Recommendation[];

  // Export readiness
  exportStatus: {
    ready: boolean;
    grade: 'excellent' | 'good' | 'acceptable' | 'needs-work' | 'poor';
    blockers: string[];
  };

  // Metadata for report generation
  meta: {
    reviewedAt: string;
    language: 'en';
    skillVersion: string;
  };
}

interface Finding {
  category: 'variant' | 'token' | 'visual' | 'accessibility' | 'code' | 'metadata';
  type: 'strength' | 'weakness';
  message: string;
  severity?: 'critical' | 'major' | 'minor';
  location?: string;
}

interface Recommendation {
  priority: 1 | 2 | 3 | 4 | 5;
  title: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
  effort: 'high' | 'medium' | 'low';
}
```

---

## Prompt Template

When reviewing a component, use this analysis framework:

```
## Component Review Framework

### Step 1: Extract Component Data
- Name and structure from Figma
- Generated code from get_design_context
- Screenshot from get_screenshot
- Metadata from component description

### Step 2: Evaluate Implementation (70%)

**Variant Structure (25 pts)**
□ Count variants: expected vs actual
□ Naming consistency check
□ TypeScript interface quality
□ Organization logic

**Token System (25 pts)**
□ CSS Variables usage for colors
□ Typography tokens
□ Spacing tokens
□ Semantic naming

**Visual Consistency (20 pts)**
□ Font-weight consistency
□ Border-radius uniformity
□ Padding/spacing consistency
□ Layout artifact check (translate, position)

**Accessibility States (20 pts)**
□ Focus state: present? visible?
□ Disabled state: all sizes?
□ Hover state: feedback clear?
□ Touch target: ≥44px?

**Code Quality (10 pts)**
□ Duplication assessment
□ Conditional clarity
□ Default values

### Step 3: Evaluate LLM Accessibility (30%)

**Description (20 pts)**
□ Primary description present?
□ Use case clear?
□ Business context?

**Searchability (15 pts)**
□ Tags present?
□ Tag coverage?

**Dev Metadata (25 pts)**
□ testId? □ ariaLabel? □ analytics?
□ category? □ level?

**Usage Guidelines (20 pts)**
□ Do's? □ Don'ts? □ Notes?

**Technical Specs (20 pts)**
□ Tokens documented?
□ Specs (min/max sizes)?
□ A11y requirements?

### Step 4: Calculate Scores

implementation_score = (variant + token + visual + a11y + code)
llm_score = (desc + search + dev + usage + specs)
weighted_score = (implementation × 0.7) + (llm × 0.3)

### Step 5: Generate Report
- List strengths (✅)
- List weaknesses (⚠️)
- Provide recommendations by priority
- Determine export readiness
```

---

## References

### This Skill (Evaluation)

| Document | Purpose |
|----------|---------|
| `./references/audit-summary-format.md` | **Output format template** - How to structure review summaries |
| `./references/scoring-rubric.md` | Detailed scoring criteria |
| `./references/checklist.md` | Pre-export checklist |
| `./references/examples.md` | Example reports |
| `./references/common-issues.md` | Frequent problems, fixes, **and false positive prevention guide** |

### Export Skill (Code Generation)

| Document | Purpose |
|----------|---------|
| `../atomic-design/SKILL.md` | **EXPORT SKILL** - Classification + code generation |
| `../atomic-design/references/atomic-hierarchy.md` | Atom/Molecule/Organism definitions |
| `../atomic-design/references/component-templates.md` | File structure templates |
| `../atomic-design/references/figma-mcp-integration.md` | Token extraction from Figma |

### Shared

| Document | Purpose |
|----------|---------|
| `../atomic-page-builder/SKILL.md` | Page composition (uses same atomic-design skill)
