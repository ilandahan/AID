/**
 * @file services/ComponentAuditor/utils.ts
 * @description Utility functions for component auditing
 */

import { INTERACTIVE_PATTERNS } from './config';

/**
 * Check if component name suggests it's interactive
 * (needs Focus, Hover, Disabled states)
 */
export function isInteractiveComponent(name: string): boolean {
  return INTERACTIVE_PATTERNS.some(pattern => pattern.test(name));
}

/**
 * Calculate Levenshtein distance between two strings.
 * This measures how many single-character edits (insertions, deletions, substitutions)
 * are needed to transform one string into another.
 *
 * Used for fuzzy typo detection: distance 1-2 suggests a typo
 */
export function levenshteinDistance(a: string, b: string): number {
  const matrix: number[][] = [];

  // Initialize first column (deletions)
  for (let i = 0; i <= a.length; i++) {
    matrix[i] = [i];
  }

  // Initialize first row (insertions)
  for (let j = 0; j <= b.length; j++) {
    matrix[0][j] = j;
  }

  // Fill in the rest of the matrix
  for (let i = 1; i <= a.length; i++) {
    for (let j = 1; j <= b.length; j++) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      matrix[i][j] = Math.min(
        matrix[i - 1][j] + 1,      // deletion
        matrix[i][j - 1] + 1,      // insertion
        matrix[i - 1][j - 1] + cost // substitution
      );
    }
  }

  return matrix[a.length][b.length];
}

/**
 * Extract values from a component name for typo checking
 */
export function extractNameValues(text: string): { value: string; field: string }[] {
  const results: { value: string; field: string }[] = [];

  for (const prop of text.split(',')) {
    const trimmed = prop.trim();
    const eqIndex = trimmed.indexOf('=');

    if (eqIndex > 0) {
      // Property=Value format
      const field = trimmed.substring(0, eqIndex).trim();
      const value = trimmed.substring(eqIndex + 1).trim();
      if (value.length >= 3) {
        results.push({ value, field });
      }
    } else if (trimmed.includes('/')) {
      // Path format: Category / Type / Name
      trimmed.split('/').forEach(part => {
        const clean = part.trim();
        if (clean.length >= 3) {
          results.push({ value: clean, field: 'name' });
        }
      });
    } else if (trimmed.length >= 3) {
      results.push({ value: trimmed, field: 'name' });
    }
  }

  return results;
}
