/**
 * @file ComponentAuditor.ts
 * @description Component auditor service that runs local quality checks on Figma components.
 *              Coordinates the 4-phase quality pipeline: Audit → Analyze → Generate → Report.
 * @created 2024-12
 * @refactored 2024-12 - Extracted modules to ./services/ComponentAuditor/
 *
 * This file re-exports the modular ComponentAuditor for backward compatibility.
 * The actual implementation is in ./services/ComponentAuditor/
 */

// Re-export everything from the modular implementation
export {
  // Main class
  ComponentAuditor,

  // Convenience functions
  runAudit,
  analyzeMetadata,

  // Check functions
  checkNaming,
  checkNameFormat,
  checkCommonTypos,
  checkLayerNames,
  checkVariantNaming,
  checkStructure,
  checkUnnecessaryWrappers,
  checkVariantStructureConsistency,
  checkVisual,
  checkFontSizeConsistency,
  checkBorderRadiusConsistency,
  checkColorUsage,
  checkAccessibility,
  checkFocusState,
  checkDisabledState,
  checkTouchTargetSize,
  checkVariants,
  checkExpectedStates,
  checkVariantCombinations,
  checkVariantDistinction,

  // Configuration
  SCORING_CONFIG,
  INTERACTIVE_PATTERNS,
  CORRECT_TERMS,
  GENERIC_LAYER_NAMES,

  // Utilities
  isInteractiveComponent,
  levenshteinDistance,
  extractNameValues,

  // Scoring
  calculateScore,
  identifyBlockers,
  generateSuggestions,
  calculateDeepInspectionPenalty,

  // Core functions
  runLocalAudit,
  deepInspectChildren,
  analyzeMetadataLocal,
  prepareForMCP,
} from './services/ComponentAuditor';

// Default export for backward compatibility
export { ComponentAuditor as default } from './services/ComponentAuditor';
