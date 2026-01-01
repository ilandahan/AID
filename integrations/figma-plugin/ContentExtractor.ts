/**
 * @file ContentExtractor.ts
 * @description Extracts text content from Figma components.
 * @created 2024-12
 * @refactored 2024-12 - Extracted modules to ./services/ContentExtractor/
 *
 * This file re-exports the modular ContentExtractor for backward compatibility.
 * The actual implementation is in ./services/ContentExtractor/
 *
 * This service traverses selected components and extracts:
 * - Text content from text layers
 * - Property values (text properties, boolean properties, etc.)
 * - Variant information
 * - Component metadata
 *
 * Output format is structured JSON ready for use in code.
 */

// Re-export everything from the modular implementation
export {
  // Main class
  ContentExtractor,

  // Types
  type ExtractedText,
  type ExtractedVariant,
  type ExtractedComponent,
  type ComponentPropertyDefinition,
  type ExportFormat,

  // Extraction functions
  extractFromSelection,
  extractFromComponentSet,
  extractFromComponent,
  extractFromInstance,

  // Property extraction
  extractPropertyDefinitions,
  extractVariant,
  extractTextsFromNode,
  extractTextNode,

  // Formatters
  toTypeScript,
  toJSON,
  toCSV,
  exportAllFormats,

  // Utilities
  toVariableName,
  toCamelCase,
  escapeString,

  // Convenience functions
  extractContent,
  exportAsTypeScript,
  exportAsJSON,
} from './services/ContentExtractor';

// Default export for backward compatibility
export { ContentExtractor as default } from './services/ContentExtractor';
