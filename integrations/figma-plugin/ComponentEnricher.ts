/**
 * @file ComponentEnricher.ts
 * @description Component enricher service for the Figma plugin.
 * @created 2024-12
 * @refactored 2024-12 - Extracted modules to ./services/ComponentEnricher/
 *
 * This file re-exports the modular ComponentEnricher for backward compatibility.
 * The actual implementation is in ./services/ComponentEnricher/
 */

// Re-export everything from the modular implementation
export {
  // Main class and singleton
  ComponentEnricher,
  componentEnricher,

  // Types
  type InferredProp,
  type FigmaNodeInfo,
  type ComponentClassification,
  type EnrichedComponentData,
  type PropDefinition,
  type VariantDefinition,
  type DesignToken,
  type AtomicLevel,

  // Configuration
  PROP_PATTERNS,
  STATE_PATTERNS,
  BREAKPOINT_PATTERNS,

  // Utility functions
  traverseNodes,
  toCamelCase,
  inferPropNameFromText,
  isLabelText,
  deduplicateProps,

  // Prop extraction
  inferProps,
  extractTextProps,
  extractSlotProps,

  // Variant extraction
  extractVariants,
  detectStates,
  detectBreakpoints,

  // Accessibility
  extractAccessibility,
  extractDependencies,
  generateDescription,
} from './services/ComponentEnricher';

// Default export for backward compatibility
export { ComponentEnricher as default } from './services/ComponentEnricher';
