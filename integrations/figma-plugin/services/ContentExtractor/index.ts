/**
 * @file services/ContentExtractor/index.ts
 * @description Main ContentExtractor class facade and convenience functions
 */

import type { ExtractedComponent, ExportFormat } from './types';
import {
  extractFromSelection,
  extractFromComponentSet,
  extractFromComponent,
  extractFromInstance,
} from './extraction';
import {
  extractPropertyDefinitions,
  extractVariant,
  extractTextsFromNode,
  extractTextNode,
} from './properties';
import { toTypeScript, toJSON, toCSV, exportAllFormats } from './formatters';
import { toVariableName, toCamelCase, escapeString } from './utils';

// Re-export everything for external consumers
export * from './types';
export * from './utils';
export * from './properties';
export * from './extraction';
export * from './formatters';

/**
 * ContentExtractor - Extracts text content from Figma components
 *
 * This class provides static methods to extract content from Figma components
 * and export it in various formats (TypeScript, JSON, CSV).
 */
export class ContentExtractor {
  // Extraction methods
  static extractFromSelection = extractFromSelection;
  static extractFromComponentSet = extractFromComponentSet;
  static extractFromComponent = extractFromComponent;
  static extractFromInstance = extractFromInstance;

  // Property extraction
  static extractPropertyDefinitions = extractPropertyDefinitions;
  static extractVariant = extractVariant;
  static extractTextsFromNode = extractTextsFromNode;
  static extractTextNode = extractTextNode;

  // Formatters
  static toTypeScript = toTypeScript;
  static toJSON = toJSON;
  static toCSV = toCSV;
  static export = exportAllFormats;

  // Utilities
  static toVariableName = toVariableName;
  static toCamelCase = toCamelCase;
  static escapeString = escapeString;
}

/**
 * Quick function to extract and log content
 */
export function extractContent(): ExtractedComponent[] {
  const components = extractFromSelection();

  if (components.length > 0) {
    console.log('Extracted components:', components);
    figma.notify(`Extracted ${components.length} component(s)`);
  }

  return components;
}

/**
 * Quick function to export content as TypeScript
 */
export function exportAsTypeScript(): string {
  const components = extractFromSelection();
  return toTypeScript(components);
}

/**
 * Quick function to export content as JSON
 */
export function exportAsJSON(): string {
  const components = extractFromSelection();
  return toJSON(components);
}
