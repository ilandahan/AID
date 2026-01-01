/**
 * @file services/ComponentEnricher/variants.ts
 * @description Variant, state, and breakpoint extraction
 */

import type { FigmaNodeInfo, VariantDefinition } from '../../types';
import { STATE_PATTERNS, BREAKPOINT_PATTERNS } from './config';
import { toCamelCase } from './utils';

/**
 * Extract variants from component set
 */
export function extractVariants(nodeInfo: FigmaNodeInfo): VariantDefinition[] {
  const variants: VariantDefinition[] = [];

  if (!nodeInfo.variantProperties) return variants;

  for (const [key, values] of Object.entries(nodeInfo.variantProperties)) {
    // Skip state-like variants
    if (STATE_PATTERNS.includes(key.toLowerCase())) continue;

    const options = values.split(', ');
    variants.push({
      name: toCamelCase(key),
      options,
      defaultOption: options[0],
      description: `${key} variant with ${options.length} options`,
    });
  }

  return variants;
}

/**
 * Detect component states from variants and children
 */
export function detectStates(
  nodeInfo: FigmaNodeInfo,
  _variants: VariantDefinition[]
): string[] {
  const states = new Set<string>(['default']);

  // Check variant properties for state-like values
  if (nodeInfo.variantProperties) {
    for (const [key, values] of Object.entries(nodeInfo.variantProperties)) {
      const keyLower = key.toLowerCase();

      // If the key is "state" or similar
      if (keyLower === 'state' || keyLower === 'status') {
        for (const value of values.split(', ')) {
          states.add(value.toLowerCase());
        }
      }

      // Check if any values are state-like
      for (const value of values.split(', ')) {
        if (STATE_PATTERNS.includes(value.toLowerCase())) {
          states.add(value.toLowerCase());
        }
      }
    }
  }

  // Check children for state-named nodes
  if (nodeInfo.children) {
    for (const child of nodeInfo.children) {
      const nameLower = child.name.toLowerCase();
      for (const state of STATE_PATTERNS) {
        if (nameLower.includes(state)) {
          states.add(state);
        }
      }
    }
  }

  return Array.from(states);
}

/**
 * Detect responsive breakpoints from component structure
 */
export function detectBreakpoints(nodeInfo: FigmaNodeInfo): string[] {
  const breakpoints: string[] = [];

  // Check component name for breakpoint hints
  const nameLower = nodeInfo.name.toLowerCase();
  for (const bp of BREAKPOINT_PATTERNS) {
    if (nameLower.includes(bp)) {
      breakpoints.push(bp);
    }
  }

  // Check children for breakpoint-specific variants
  if (nodeInfo.children) {
    for (const child of nodeInfo.children) {
      const childNameLower = child.name.toLowerCase();
      for (const bp of BREAKPOINT_PATTERNS) {
        if (childNameLower.includes(bp) && !breakpoints.includes(bp)) {
          breakpoints.push(bp);
        }
      }
    }
  }

  // If no breakpoints detected, use defaults
  if (breakpoints.length === 0) {
    return ['default'];
  }

  return breakpoints;
}
