/**
 * @file NodeAnalyzer.ts
 * @description Figma node analyzer that classifies components in the Atomic Design hierarchy.
 *              Extracts node properties, design tokens, and creates work plans for conversion.
 * @created 2024-12
 * @refactored 2024-12 - Extracted modules to ./services/NodeAnalyzer/
 *
 * This file re-exports the modular NodeAnalyzer for backward compatibility.
 * The actual implementation is in ./services/NodeAnalyzer/
 */

// Re-export everything from the modular implementation
export {
  // Main class and singleton
  NodeAnalyzer,
  nodeAnalyzer,

  // Configuration patterns
  ATOM_PATTERNS,
  MOLECULE_PATTERNS,
  ORGANISM_PATTERNS,
  TEMPLATE_PATTERNS,
  CATEGORY_PATTERNS,

  // Classification utilities
  classifyComponent,
  countChildren,
  calculateDepth,
  isLayoutContainer,
  detectCategory,
  generateSuggestedName,

  // Token utilities
  extractTokens,
  rgbToHex,
  rgbaToString,
  deduplicateTokens,

  // Work plan utilities
  findDependencies,
  createWorkPlan,
} from './services/NodeAnalyzer';

// Default export for backward compatibility
export { NodeAnalyzer as default } from './services/NodeAnalyzer';
