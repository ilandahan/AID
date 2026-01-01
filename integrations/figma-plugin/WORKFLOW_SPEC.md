# Figma Atomic Design Extractor - Workflow Specification

## 🎯 Vision

A Figma plugin that ensures design system quality BEFORE code generation.
Components must pass quality gates to be exported - "Quality First, Code Second".

---

## 📊 The 4-Phase Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌───────────┐ │
│  │   PHASE 1    │ →  │   PHASE 2    │ →  │   PHASE 3    │ →  │  PHASE 4  │ │
│  │   AUDIT      │    │   METADATA   │    │   REPORT     │    │  EXPORT   │ │
│  │              │    │              │    │              │    │           │ │
│  │ Style Guide  │    │ Gap Analysis │    │ Generate &   │    │ Extract   │ │
│  │ Review       │    │ & Completion │    │ Score        │    │ to Code   │ │
│  └──────────────┘    └──────────────┘    └──────────────┘    └───────────┘ │
│                                                                             │
│        ⬇️                   ⬇️                   ⬇️                ⬇️       │
│   Consistency          Metadata             Quality           Code        │
│   Score                Completeness         Report            Generation  │
│                                                                             │
│  ════════════════════════════════════════════════════════════════════════  │
│                                                                             │
│                    🚫 BLOCKED until Score ≥ 90                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Style Guide Audit (סקירת Style Guide)

### Purpose
Ensure component consistency across the design system before any export.

### Checks

#### 1.1 Naming Conventions
```yaml
checks:
  - component_name_format: "Category / Type / Name"
  - variant_property_names: PascalCase (Size, State, Style)
  - variant_values: PascalCase (Default, Hover, Primary)
  - layer_names: Semantic (Label, Icon, Container - not Text 1, Frame 2)
  - no_typos: Check common errors (Defult → Default, lable → label)
```

#### 1.2 Structure Consistency
```yaml
checks:
  - no_unnecessary_wrappers: Component Set not wrapped in Frame
  - consistent_hierarchy: Similar components have similar structure
  - auto_layout_usage: Components use Auto Layout properly
  - constraint_settings: Responsive constraints are set
```

#### 1.3 Visual Consistency
```yaml
checks:
  - font_weight_uniform: Same weight across similar variants
  - font_size_uniform: Consistent sizes (no 13.7px, 13.8px variations)
  - padding_uniform: Account for borders, keep internal spacing identical
  - border_radius_uniform: Same radius across variants
  - color_tokens: Using design system colors (not hardcoded)
  - spacing_tokens: Using design system spacing
```

#### 1.4 Variant Completeness
```yaml
checks:
  - all_states_present: Default, Hover, Focus, Disabled (where applicable)
  - all_combinations_exist: No missing variant combinations
  - state_visual_distinction: Each state is visually different
```

#### 1.5 Accessibility States (מצבי נגישות)
```yaml
required_states:
  interactive_components:
    - Default: Rest state
    - Hover: Mouse over (cursor: pointer indication)
    - Focus: Keyboard navigation (visible focus ring, 3:1 contrast)
    - Active: Being pressed/clicked
    - Disabled: Non-interactive (aria-disabled, reduced opacity)
    
  focus_requirements:
    - focus_ring_visible: true
    - focus_ring_contrast: "≥ 3:1"
    - focus_ring_style: "outline or box-shadow"
    - focus_ring_offset: "2-3px recommended"
    
  disabled_requirements:
    - visual_indication: "Reduced opacity or grayed out"
    - not_focusable: "tabindex=-1 or aria-disabled"
    - cursor: "not-allowed"
```

### Output: Consistency Score (0-100)

```typescript
interface AuditResult {
  score: number;  // 0-100
  
  categories: {
    naming: CategoryScore;
    structure: CategoryScore;
    visual: CategoryScore;
    variants: CategoryScore;
    accessibility: CategoryScore;
  };
  
  issues: AuditIssue[];
  suggestions: string[];
}

interface CategoryScore {
  score: number;
  weight: number;  // How much this category affects total
  passed: number;
  failed: number;
  warnings: number;
}

interface AuditIssue {
  severity: 'error' | 'warning' | 'info';
  category: string;
  message: string;
  location: string;  // Node path
  suggestion: string;
  autoFixable: boolean;
}
```

---

## Phase 2: Metadata Gap Analysis (זיהוי פערים במטא דאטה)

### Purpose
Identify missing or incomplete metadata based on our defined format.

### Required Metadata (from SKILL.md)

#### 2.1 Component Set Level (Required)
```yaml
required:
  - description: "Primary description (2-3 sentences)"
  - tags: "Comma-separated keywords"
  - notes: "Usage guidelines"
  - category: "button|navigation|form|layout|feedback|data-display|overlay"
  - level: "atom|molecule|organism|template|page"

recommended:
  - ariaLabel: "Accessibility label"
  - priority: "critical|high|medium|low"
  - analytics: "Event name"
  - testId: "data-testid value"

optional:
  - tokens: "Design tokens used"
  - states: "State descriptions"
  - variants: "Variant descriptions"
  - dos: "Recommended practices"
  - donts: "Anti-patterns"
  - a11y: "Accessibility requirements"
  - related: "Related components"
  - specs: "Technical specifications"
```

#### 2.2 Variant Level (Required)
```yaml
required:
  - description: "Brief description of variant purpose"

format: "[What this variant is]. [When to use it]. [Key visual characteristics]."
example: "Full-width primary button for mobile viewports. Main CTA state. Solid blue background."
```

#### 2.3 Property Level (Recommended)
```yaml
properties:
  Style: "Visual style variant description"
  Size: "Size variant description"
  State: "Interactive state description"
  Label: "Text content description"
```

### Gap Analysis Output

```typescript
interface MetadataGapAnalysis {
  componentName: string;
  completenessScore: number;  // 0-100
  
  componentSetLevel: {
    present: string[];
    missing: string[];
    incomplete: string[];
  };
  
  variantLevel: {
    total: number;
    withDescription: number;
    missingDescription: VariantInfo[];
  };
  
  propertyLevel: {
    total: number;
    withDescription: number;
    missingDescription: string[];
  };
  
  generatedSuggestions: {
    description?: string;
    tags?: string;
    notes?: string;
    variantDescriptions?: Record<string, string>;
  };
}
```

---

## Phase 3: Report Generation (ג'נרוט דוחות)

### Purpose
Generate comprehensive quality report with auto-generated content suggestions.

### 3.1 Component Quality Report

```typescript
interface ComponentQualityReport {
  // Header
  componentName: string;
  componentType: 'COMPONENT' | 'COMPONENT_SET';
  generatedAt: Date;
  
  // Scores
  overallScore: number;  // 0-100
  scores: {
    consistency: number;      // From Phase 1
    metadataComplete: number; // From Phase 2
    accessibility: number;    // A11y specific
    structure: number;        // Component structure
  };
  
  // Status
  exportReady: boolean;  // true if overallScore >= 90
  blockers: string[];    // Issues preventing export
  
  // Details
  audit: AuditResult;
  metadata: MetadataGapAnalysis;
  
  // Auto-generated content
  suggestedMetadata: GeneratedMetadata;
  
  // Action items
  requiredFixes: ActionItem[];
  recommendedFixes: ActionItem[];
}

interface ActionItem {
  priority: 'critical' | 'high' | 'medium' | 'low';
  category: string;
  issue: string;
  howToFix: string;
  location: string;
  autoFixAvailable: boolean;
}
```

### 3.2 Auto-Generated Metadata

```typescript
interface GeneratedMetadata {
  // Component Set Description
  description: string;
  
  // Structured metadata
  tags: string[];
  notes: string;
  ariaLabel: string;
  category: string;
  level: AtomicLevel;
  
  // Tokens extracted
  tokens: {
    colors: string[];
    spacing: string[];
    typography: string[];
    radius: string[];
    shadows: string[];
  };
  
  // Variant descriptions
  variants: Record<string, string>;
  
  // Usage guidelines (AI-generated)
  dos: string[];
  donts: string[];
  
  // Accessibility
  a11y: string[];
  
  // Full formatted output
  formattedDescription: string;  // Ready to paste into Figma
}
```

### 3.3 Report Formats

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   📊 Component Quality Report                               │
│   ══════════════════════════                               │
│                                                             │
│   Component: Card / Feature                                 │
│   Type: COMPONENT_SET                                       │
│   Variants: 18                                              │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐  │
│   │  OVERALL SCORE: 72/100  ⚠️ NOT READY FOR EXPORT    │  │
│   └─────────────────────────────────────────────────────┘  │
│                                                             │
│   Category Scores:                                          │
│   ├── Consistency:    85/100 ✅                            │
│   ├── Metadata:       45/100 ❌                            │
│   ├── Accessibility:  70/100 ⚠️                            │
│   └── Structure:      90/100 ✅                            │
│                                                             │
│   ════════════════════════════════════════════════════     │
│                                                             │
│   🔴 BLOCKERS (Must fix):                                   │
│   1. Missing component description                          │
│   2. 6 variants missing Focus state                         │
│   3. No accessibility metadata                              │
│                                                             │
│   🟡 WARNINGS (Should fix):                                 │
│   1. Font size inconsistency (13.6px, 13.7px, 13.8px)      │
│   2. 12 variants missing descriptions                       │
│                                                             │
│   ════════════════════════════════════════════════════     │
│                                                             │
│   📝 SUGGESTED METADATA (copy to Figma):                   │
│   ───────────────────────────────────────                  │
│                                                             │
│   [Full formatted description ready to paste]               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 4: Export (חילוץ לקוד)

### Gate Requirement
```
Export ONLY enabled when: overallScore >= 90
```

### Export Options

```typescript
interface ExportOptions {
  // Content Export
  content: {
    format: 'typescript' | 'json' | 'csv';
    includeMetadata: boolean;
    includeTokens: boolean;
  };
  
  // Code Generation (via MCP)
  code: {
    framework: 'react' | 'vue' | 'html';
    styling: 'tailwind' | 'css' | 'styled-components';
    includeStorybook: boolean;
    includeTests: boolean;
  };
  
  // Documentation
  docs: {
    generateReadme: boolean;
    generateChangelog: boolean;
  };
}
```

### Export Payload

```typescript
interface ExportPayload {
  // Component data
  component: {
    name: string;
    type: string;
    description: string;
    metadata: GeneratedMetadata;
  };
  
  // Quality certification
  qualityCertification: {
    score: number;
    auditedAt: Date;
    passedChecks: string[];
  };
  
  // Design tokens
  tokens: DesignToken[];
  
  // Content
  content: Record<string, string>;
  
  // Variants
  variants: VariantExport[];
  
  // Figma metadata
  figma: {
    fileKey: string;
    nodeId: string;
    exportedAt: Date;
  };
}
```

---

## 🔌 Plugin UI Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  🧬 Atomic Design Extractor                              [─][□][×]│   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────┬─────────┬─────────┬─────────┐                             │
│  │ 1.Audit │2.Metadata│3.Report │4.Export │                             │
│  └─────────┴─────────┴─────────┴─────────┘                             │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                                                                 │   │
│  │   📋 Selected: Card / Feature (18 variants)                    │   │
│  │                                                                 │   │
│  │   ┌───────────────────────────────────────┐                    │   │
│  │   │  QUALITY SCORE                        │                    │   │
│  │   │                                       │                    │   │
│  │   │         72/100                        │                    │   │
│  │   │     ████████░░░░░░░                   │                    │   │
│  │   │                                       │                    │   │
│  │   │  ⚠️ 18 points needed for export      │                    │   │
│  │   └───────────────────────────────────────┘                    │   │
│  │                                                                 │   │
│  │   Category Breakdown:                                          │   │
│  │   ├── ✅ Consistency:    85                                    │   │
│  │   ├── ❌ Metadata:       45                                    │   │
│  │   ├── ⚠️ Accessibility:  70                                    │   │
│  │   └── ✅ Structure:      90                                    │   │
│  │                                                                 │   │
│  │   ──────────────────────────────────────────                   │   │
│  │                                                                 │   │
│  │   🔴 Critical Issues (3):                                      │   │
│  │   ┌─────────────────────────────────────────────────────────┐  │   │
│  │   │ 1. Missing component description         [Auto-Generate]│  │   │
│  │   │ 2. 6 Focus states missing                [Show Details] │  │   │
│  │   │ 3. No a11y metadata                      [Auto-Generate]│  │   │
│  │   └─────────────────────────────────────────────────────────┘  │   │
│  │                                                                 │   │
│  │   🟡 Warnings (2):                                             │   │
│  │   ┌─────────────────────────────────────────────────────────┐  │   │
│  │   │ 1. Font size inconsistency               [Show Details] │  │   │
│  │   │ 2. 12 variant descriptions missing       [Auto-Generate]│  │   │
│  │   └─────────────────────────────────────────────────────────┘  │   │
│  │                                                                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────────────┐   │
│  │ 🔄 Re-Analyze  │  │ 📝 View Report │  │ 🚫 Export (Score < 90) │   │
│  └────────────────┘  └────────────────┘  └────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📐 Scoring Algorithm

```typescript
interface ScoringConfig {
  weights: {
    consistency: 0.25,    // 25%
    metadata: 0.30,       // 30%
    accessibility: 0.25,  // 25%
    structure: 0.20       // 20%
  };
  
  // Minimum scores per category to pass
  minimums: {
    consistency: 70,
    metadata: 60,
    accessibility: 80,  // A11y is critical
    structure: 70
  };
  
  // Export threshold
  exportThreshold: 90;
  
  // Blocker rules
  blockers: [
    'missing_component_description',
    'missing_focus_states',
    'contrast_ratio_fail',
    'no_accessibility_metadata'
  ];
}

function calculateScore(audit: AuditResult, metadata: MetadataGapAnalysis): number {
  const config = getScoringConfig();
  
  let weightedScore = 0;
  let totalWeight = 0;
  
  for (const [category, weight] of Object.entries(config.weights)) {
    const categoryScore = getCategoryScore(category, audit, metadata);
    weightedScore += categoryScore * weight;
    totalWeight += weight;
  }
  
  const baseScore = weightedScore / totalWeight;
  
  // Apply blocker penalties
  const blockerPenalty = countBlockers(audit, metadata) * 10;
  
  return Math.max(0, Math.round(baseScore - blockerPenalty));
}
```

---

## 🗂️ File Structure

```
figma-atomic-plugin/
├── src/
│   ├── code.ts                    # Main plugin entry
│   │
│   ├── services/
│   │   ├── ComponentAuditor.ts    # Phase 1: Audit
│   │   ├── MetadataAnalyzer.ts    # Phase 2: Gap analysis
│   │   ├── ReportGenerator.ts     # Phase 3: Reports
│   │   ├── ContentExtractor.ts    # Phase 4: Export
│   │   ├── MetadataGenerator.ts   # Auto-generate metadata
│   │   ├── AccessibilityChecker.ts # A11y specific checks
│   │   └── ScoringEngine.ts       # Calculate scores
│   │
│   ├── checks/
│   │   ├── naming.ts              # Naming convention checks
│   │   ├── structure.ts           # Structure checks
│   │   ├── visual.ts              # Visual consistency checks
│   │   ├── variants.ts            # Variant completeness checks
│   │   └── accessibility.ts       # A11y state checks
│   │
│   ├── generators/
│   │   ├── descriptionGenerator.ts
│   │   ├── tagsGenerator.ts
│   │   ├── a11yGenerator.ts
│   │   └── variantDescGenerator.ts
│   │
│   ├── types/
│   │   └── index.ts
│   │
│   └── ui/
│       ├── components/
│       │   ├── ScoreCard.tsx
│       │   ├── IssueList.tsx
│       │   ├── CategoryBreakdown.tsx
│       │   └── ActionButtons.tsx
│       └── tabs/
│           ├── AuditTab.tsx
│           ├── MetadataTab.tsx
│           ├── ReportTab.tsx
│           └── ExportTab.tsx
│
├── skills/
│   └── component-metadata/
│       └── SKILL.md               # Our metadata format
│
└── docs/
    ├── COMPONENT_METADATA_FORMAT.md
    └── WORKFLOW_SPEC.md           # This file
```

---

## 🎯 Implementation Priority

### MVP (Phase 1)
1. ✅ Component Auditor - Basic checks
2. ✅ Metadata Analyzer - Gap detection
3. ✅ Score calculation
4. ✅ Basic UI with score display

### V1.0
1. Auto-generate metadata suggestions
2. Report generation (copy-paste ready)
3. Export with quality gate

### V1.1
1. Accessibility deep checks
2. Auto-fix capabilities
3. Batch processing

### V2.0
1. MCP integration for code generation
2. Storybook generation
3. Design system documentation

---

## ✅ Success Criteria

A component is **Export Ready** when:

1. **Overall Score ≥ 90**
2. **No Blockers**:
   - Has component description
   - All interactive states present (including Focus)
   - Accessibility metadata exists
   - Contrast ratios pass
3. **Category Minimums Met**:
   - Consistency ≥ 70
   - Metadata ≥ 60
   - Accessibility ≥ 80
   - Structure ≥ 70
