/**
 * @file services/ContentExtractor/utils.ts
 * @description String utility functions for content extraction
 */

/**
 * Convert component name to a valid variable name
 */
export function toVariableName(name: string): string {
  return name
    .replace(/[\/\s-]+/g, '')
    .replace(/[^a-zA-Z0-9]/g, '');
}

/**
 * Convert string to camelCase
 */
export function toCamelCase(str: string): string {
  return str
    .replace(/[^a-zA-Z0-9]+(.)/g, (_, char) => char.toUpperCase())
    .replace(/^[A-Z]/, char => char.toLowerCase())
    .replace(/[^a-zA-Z0-9]/g, '');
}

/**
 * Escape string for use in code output
 */
export function escapeString(str: string): string {
  return str
    .replace(/\\/g, '\\\\')
    .replace(/"/g, '\\"')
    .replace(/\n/g, '\\n');
}
