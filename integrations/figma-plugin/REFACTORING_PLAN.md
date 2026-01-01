# Figma Plugin TypeScript Refactoring Plan

## Executive Summary

This plan outlines the refactoring of **10 long TypeScript files** in the Figma plugin codebase to improve maintainability. Target: **300 lines max per file**.

### Files to Refactor (Sorted by Priority)

| Priority | File | Lines | Modules After Refactor |
|----------|------|-------|------------------------|
| 🔴 P1 | code.ts | 1,628 | 8 modules |
| 🔴 P2 | ComponentAuditor.ts | 1,301 | 7 modules |
| 🟡 P3 | MCPClient.ts | 767 | 4 modules |
| 🟡 P4 | NodeAnalyzer.ts | 616 | 3 modules |
| 🟡 P5 | AuthService.ts | 552 | 3 modules |
| 🟡 P6 | ComponentEnricher.ts | 539 | 3 modules |
| 🟡 P7 | QueueManager.ts | 517 | 2 modules |
| 🟢 P8 | crypto-utils.ts | 446 | 2 modules |
| 🟢 P9 | ScoringEngine.ts | 434 | 2 modules |
| 🟢 P10 | ContentExtractor.ts | 428 | 2 modules |

---

## Phase 1: code.ts (1,628 lines → 8 modules)

### Current Structure Analysis
```
code.ts
├── Plugin State (lines 43-77)
├── UI Communication (lines 78-120)
├── Selection Handling (lines 121-170)
├── Audit Phase (lines 171-275)
├── Metadata Analysis (lines 276-340)
├── Metadata Generation (lines 341-450)
├── Apply Metadata (lines 451-630)
├── Export Functions (lines 631-822)
├── MCP Connection (lines 823-860)
├── Pipeline Orchestration (lines 860-1035)
├── Cache Management (lines 1036-1090)
├── Node Navigation (lines 1091-1120)
├── Message Handling (lines 1121-1230)
└── Configuration/Auth (lines 1231-1628)
```

### Target Module Structure
```
src/
├── plugin/
│   ├── index.ts              # Main entry, plugin init, event setup (~100 lines)
│   ├── state.ts              # Plugin state management (~80 lines)
│   ├── ui-messaging.ts       # UI communication helpers (~60 lines)
│   ├── selection-handler.ts  # Selection change handling (~100 lines)
│   ├── pipeline/
│   │   ├── index.ts          # Pipeline orchestration (~200 lines)
│   │   ├── audit-phase.ts    # Audit phase logic (~150 lines)
│   │   ├── metadata-phase.ts # Analyze + Generate metadata (~200 lines)
│   │   └── apply-phase.ts    # Apply metadata to Figma (~180 lines)
│   ├── export/
│   │   ├── index.ts          # Export coordinator (~100 lines)
│   │   └── formatters.ts     # JSON/TS/CSV formatters (~150 lines)
│   ├── mcp-connection.ts     # MCP connect/disconnect (~80 lines)
│   └── config-manager.ts     # Settings, auth, endpoints (~200 lines)
```

### Step-by-Step Implementation

#### Step 1.1: Create directory structure
```bash
mkdir -p src/plugin/pipeline src/plugin/export
```

#### Step 1.2: Extract state.ts (~80 lines)
- Move `currentState` object
- Move `defaultSettings` object
- Move `settings` variable
- Export state getters/setters

#### Step 1.3: Extract ui-messaging.ts (~60 lines)
- Move `sendToUI()` function
- Move `sendError()` function
- Move message type definitions

#### Step 1.4: Extract selection-handler.ts (~100 lines)
- Move `handleSelectionChange()` function
- Move selection-related helpers

#### Step 1.5: Extract pipeline/audit-phase.ts (~150 lines)
- Move `runLocalAudit()` function
- Move `runServerAudit()` function

#### Step 1.6: Extract pipeline/metadata-phase.ts (~200 lines)
- Move `analyzeMetadata()` function
- Move `generateMetadata()` function
- Move `prepareFigmaDescription()` helper

#### Step 1.7: Extract pipeline/apply-phase.ts (~180 lines)
- Move `applyMetadataToFigma()` function
- Move validation helpers

#### Step 1.8: Extract pipeline/index.ts (~200 lines)
- Move `runFullPipeline()` function
- Move `sendPipelineStep()` helper
- Move pipeline state management

#### Step 1.9: Extract export/formatters.ts (~150 lines)
- Move `exportContent()` function
- Move JSON/TS/CSV formatting logic

#### Step 1.10: Extract export/index.ts (~100 lines)
- Move `classifyComponentLevel()` function
- Move `getDestinationPath()` function
- Move `exportToAID()` function

#### Step 1.11: Extract mcp-connection.ts (~80 lines)
- Move `connectMCP()` function
- Move `disconnectMCP()` function

#### Step 1.12: Extract config-manager.ts (~200 lines)
- Move `getAIDEndpoint()` function
- Move `setAIDEndpoint()` function
- Move `loadCustomEndpoint()` function
- Move `pairWithAID()` function
- Move `validateTokenWithRetry()` function
- Move all auth-related functions

#### Step 1.13: Create index.ts (~100 lines)
- Plugin initialization
- Event listener setup
- Import and wire all modules

---

## Phase 2: ComponentAuditor.ts (1,301 lines → 7 modules)

### Current Structure Analysis
```
ComponentAuditor.ts
├── Interactive Component Patterns (lines 30-61)
├── Scoring Configuration (lines 63-91)
├── Phase 1: Local Audit (lines 99-218)
├── Naming Checks (lines 220-525)
├── Structure Checks (lines 526-650)
├── Visual Checks (lines 650-770)
├── Accessibility Checks (lines 771-903)
├── Variant Checks (lines 904-1003)
├── Build Payload (lines 1004-1033)
├── Send to Server (lines 1033-1160)
└── Generate Report (lines 1160-1301)
```

### Target Module Structure
```
src/auditor/
├── index.ts                # ComponentAuditor class facade (~100 lines)
├── config.ts               # Scoring config, patterns (~80 lines)
├── checks/
│   ├── index.ts            # Check aggregator (~50 lines)
│   ├── naming-checks.ts    # Naming validation (~200 lines)
│   ├── structure-checks.ts # Structure validation (~150 lines)
│   ├── visual-checks.ts    # Visual validation (~150 lines)
│   ├── a11y-checks.ts      # Accessibility checks (~200 lines)
│   └── variant-checks.ts   # Variant validation (~150 lines)
├── payload-builder.ts      # Build audit payload (~100 lines)
├── server-integration.ts   # Server communication (~150 lines)
└── report-generator.ts     # Generate quality report (~150 lines)
```

### Step-by-Step Implementation

#### Step 2.1: Extract config.ts (~80 lines)
- Move `INTERACTIVE_PATTERNS` array
- Move `SCORING_CONFIG` object
- Move `isInteractiveComponent()` function

#### Step 2.2: Extract checks/naming-checks.ts (~200 lines)
- Move `checkNaming()` method
- Move `checkNameFormat()` helper
- Move `checkCommonTypos()` helper
- Move all naming-related validation

#### Step 2.3: Extract checks/structure-checks.ts (~150 lines)
- Move `checkStructure()` method
- Move `checkUnnecessaryWrappers()` helper
- Move structure validation logic

#### Step 2.4: Extract checks/visual-checks.ts (~150 lines)
- Move `checkVisual()` method
- Move color, spacing, typography checks

#### Step 2.5: Extract checks/a11y-checks.ts (~200 lines)
- Move `checkAccessibility()` method
- Move contrast checks
- Move ARIA validation

#### Step 2.6: Extract checks/variant-checks.ts (~150 lines)
- Move `checkVariants()` method
- Move variant validation logic

#### Step 2.7: Extract checks/index.ts (~50 lines)
- Aggregate all check modules
- Export unified check runner

#### Step 2.8: Extract payload-builder.ts (~100 lines)
- Move payload building logic
- Move data transformation helpers

#### Step 2.9: Extract server-integration.ts (~150 lines)
- Move MCP communication logic
- Move server audit calls

#### Step 2.10: Extract report-generator.ts (~150 lines)
- Move report generation logic
- Move score calculation

#### Step 2.11: Create index.ts (~100 lines)
- ComponentAuditor class facade
- Import and delegate to modules

---

## Phase 3: MCPClient.ts (767 lines → 4 modules)

### Target Module Structure
```
src/mcp/
├── index.ts              # MCPClient class (~150 lines)
├── connection.ts         # Connection management (~150 lines)
├── request-handler.ts    # Request/response handling (~200 lines)
├── pipeline-api.ts       # Pipeline-specific API calls (~200 lines)
└── types.ts              # MCP-specific types (~50 lines)
```

### Steps
- Step 3.1: Extract connection.ts (connect/disconnect/ping)
- Step 3.2: Extract request-handler.ts (sendRequest, retry logic)
- Step 3.3: Extract pipeline-api.ts (audit, analyze, generate, export APIs)
- Step 3.4: Create index.ts (MCPClient facade)

---

## Phase 4: NodeAnalyzer.ts (616 lines → 3 modules)

### Target Module Structure
```
src/analyzer/
├── index.ts              # NodeAnalyzer class (~100 lines)
├── node-info.ts          # Node information extraction (~250 lines)
├── token-extractor.ts    # Design token extraction (~250 lines)
└── types.ts              # Analyzer types (~50 lines)
```

---

## Phase 5: AuthService.ts (552 lines → 3 modules)

### Target Module Structure
```
src/auth/
├── index.ts              # AuthService class (~100 lines)
├── token-manager.ts      # Token storage/validation (~200 lines)
├── pairing.ts            # Device pairing flow (~200 lines)
└── types.ts              # Auth types (~50 lines)
```

---

## Phase 6: ComponentEnricher.ts (539 lines → 3 modules)

### Target Module Structure
```
src/enricher/
├── index.ts              # ComponentEnricher class (~100 lines)
├── metadata-merger.ts    # Merge existing + generated (~200 lines)
├── description-builder.ts # Build formatted descriptions (~200 lines)
└── types.ts              # Enricher types (~50 lines)
```

---

## Phase 7: QueueManager.ts (517 lines → 2 modules)

### Target Module Structure
```
src/queue/
├── index.ts              # QueueManager class (~250 lines)
├── batch-processor.ts    # Batch processing logic (~250 lines)
└── types.ts              # Queue types (~50 lines)
```

---

## Phase 8: crypto-utils.ts (446 lines → 2 modules)

### Target Module Structure
```
src/crypto/
├── index.ts              # Crypto utilities (~200 lines)
├── encryption.ts         # Encryption/decryption (~200 lines)
└── types.ts              # Crypto types (~50 lines)
```

---

## Phase 9: ScoringEngine.ts (434 lines → 2 modules)

### Target Module Structure
```
src/scoring/
├── index.ts              # ScoringEngine class (~150 lines)
├── calculators.ts        # Score calculation logic (~250 lines)
└── types.ts              # Scoring types (~50 lines)
```

---

## Phase 10: ContentExtractor.ts (428 lines → 2 modules)

### Target Module Structure
```
src/content/
├── index.ts              # ContentExtractor class (~150 lines)
├── extractors.ts         # Content extraction logic (~250 lines)
└── types.ts              # Content types (~50 lines)
```

---

## Implementation Guidelines

### Preserve Functionality
1. **No breaking changes** - All public APIs remain identical
2. **Same exports** - Use barrel exports (index.ts) to maintain import paths
3. **GUI unchanged** - No changes to UI code or messages

### TypeScript Best Practices
1. **Single Responsibility** - Each module handles one concern
2. **Explicit Types** - Export interfaces, not inline types
3. **Dependency Injection** - Pass dependencies, don't import globals
4. **Pure Functions** - Prefer pure functions over class methods

### Testing Strategy
1. After each phase, run existing tests
2. Build plugin and verify in Figma
3. Test each pipeline step manually
4. Verify MCP connection works

### Build Verification
```bash
npm run build
# Should complete without errors
# Bundle size should be similar (±5%)
```

---

## Timeline Estimate

| Phase | Effort | Risk |
|-------|--------|------|
| Phase 1 (code.ts) | 4-6 hours | High |
| Phase 2 (ComponentAuditor) | 3-4 hours | Medium |
| Phase 3 (MCPClient) | 2-3 hours | Medium |
| Phases 4-10 | 1-2 hours each | Low |

**Total Estimate: 15-25 hours**

---

## Rollback Plan

If refactoring causes issues:
1. Git revert to pre-refactor commit
2. Restore original single-file structure
3. Document what went wrong for future attempt
