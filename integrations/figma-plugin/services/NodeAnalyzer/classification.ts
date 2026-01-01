/**
 * @file services/NodeAnalyzer/classification.ts
 * @description Component classification in Atomic Design hierarchy
 */

import type {
  FigmaNodeInfo,
  FigmaNodeProperties,
  ComponentClassification,
  AtomicLevel,
} from '../../types';

import {
  ATOM_PATTERNS,
  MOLECULE_PATTERNS,
  ORGANISM_PATTERNS,
  TEMPLATE_PATTERNS,
  CATEGORY_PATTERNS,
} from './config';

/**
 * Count total children recursively
 */
export function countChildren(nodeInfo: FigmaNodeInfo): number {
  if (!nodeInfo.children) return 0;
  return nodeInfo.children.reduce((acc, child) => {
    return acc + 1 + countChildren(child);
  }, 0);
}

/**
 * Calculate maximum depth of tree
 */
export function calculateDepth(nodeInfo: FigmaNodeInfo, currentDepth = 0): number {
  if (!nodeInfo.children || nodeInfo.children.length === 0) {
    return currentDepth;
  }
  return Math.max(
    ...nodeInfo.children.map(child => calculateDepth(child, currentDepth + 1))
  );
}

/**
 * Check if node is a layout container
 */
export function isLayoutContainer(nodeInfo: FigmaNodeInfo): boolean {
  const { properties } = nodeInfo;

  // Has auto-layout with fill container
  if (properties.layoutMode &&
      (properties.primaryAxisSizingMode === 'AUTO' ||
       properties.counterAxisSizingMode === 'AUTO')) {
    return true;
  }

  // Large dimensions suggest page-level layout
  if (properties.width && properties.width > 800 &&
      properties.height && properties.height > 600) {
    return true;
  }

  return false;
}

/**
 * Detect component category from name
 */
export function detectCategory(name: string): string {
  for (const [category, patterns] of Object.entries(CATEGORY_PATTERNS)) {
    if (patterns.some(p => name.includes(p))) {
      return category;
    }
  }

  return 'other';
}

/**
 * Generate a code-friendly component name
 */
export function generateSuggestedName(originalName: string, level: AtomicLevel): string {
  // Clean the name
  let name = originalName
    .replace(/[^a-zA-Z0-9\s-_]/g, '')
    .replace(/[\s-_]+/g, ' ')
    .trim();

  // Convert to PascalCase
  name = name
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join('');

  return name;
}

/**
 * Classify a component in the Atomic Design hierarchy
 *
 * Priority order:
 * 1. Variant complexity (many variants = higher complexity regardless of name)
 * 2. Name-based patterns
 * 3. Child count/depth fallback
 */
export function classifyComponent(nodeInfo: FigmaNodeInfo): ComponentClassification {
  const nameLower = nodeInfo.name.toLowerCase().replace(/[_\s]/g, '-');
  const childCount = countChildren(nodeInfo);
  const depth = calculateDepth(nodeInfo);
  const hasLayout = !!nodeInfo.properties.layoutMode;
  const category = detectCategory(nameLower);

  // Calculate level and confidence
  let level: AtomicLevel = 'atom';
  let confidence = 0.5;
  let reasoning = '';

  // Get variant count for ComponentSets
  const variantCount = nodeInfo.isComponentSet
    ? (nodeInfo.children?.length || Object.keys(nodeInfo.variantProperties || {}).length || 0)
    : 0;

  // FIRST: Check variant complexity - ComponentSets with many variants are complex
  // regardless of their name (e.g., "Button" with 16 variants is not an atom)
  if (variantCount >= 10) {
    level = 'organism';
    confidence = 0.9;
    reasoning = `High variant complexity: ${variantCount} variants`;
  } else if (variantCount >= 5) {
    level = 'molecule';
    confidence = 0.85;
    reasoning = `Moderate variant complexity: ${variantCount} variants`;
  } else if (variantCount >= 3) {
    // Components with 3-4 variants are at least molecules
    level = 'molecule';
    confidence = 0.75;
    reasoning = `Has ${variantCount} variants`;
  }

  // SECOND: Name-based classification (only if not already classified by variants)
  else if (ATOM_PATTERNS.names.some(p => nameLower.includes(p))) {
    level = 'atom';
    confidence = 0.9;
    reasoning = `Name matches atom pattern and has ${childCount} children`;
  } else if (childCount <= ATOM_PATTERNS.maxChildren && depth <= ATOM_PATTERNS.maxDepth) {
    level = 'atom';
    confidence = 0.7;
    reasoning = `Simple structure: ${childCount} children, depth ${depth}`;
  }

  // Check for MOLECULE patterns
  else if (MOLECULE_PATTERNS.names.some(p => nameLower.includes(p))) {
    level = 'molecule';
    confidence = 0.9;
    reasoning = `Name matches molecule pattern`;
  } else if (childCount >= MOLECULE_PATTERNS.minChildren &&
             childCount <= MOLECULE_PATTERNS.maxChildren &&
             depth <= MOLECULE_PATTERNS.maxDepth) {
    level = 'molecule';
    confidence = 0.7;
    reasoning = `Moderate complexity: ${childCount} children, depth ${depth}`;
  }

  // Check for ORGANISM patterns
  else if (ORGANISM_PATTERNS.names.some(p => nameLower.includes(p))) {
    level = 'organism';
    confidence = 0.9;
    reasoning = `Name matches organism pattern`;
  } else if (childCount >= ORGANISM_PATTERNS.minChildren &&
             depth >= ORGANISM_PATTERNS.minDepth) {
    level = 'organism';
    confidence = 0.75;
    reasoning = `Complex structure: ${childCount} children, depth ${depth}`;
  }

  // Check for TEMPLATE patterns
  else if (TEMPLATE_PATTERNS.names.some(p => nameLower.includes(p))) {
    level = 'template';
    confidence = 0.9;
    reasoning = `Name matches template pattern`;
  } else if (hasLayout && isLayoutContainer(nodeInfo)) {
    level = 'template';
    confidence = 0.6;
    reasoning = `Appears to be a layout container`;
  }

  return {
    level,
    confidence,
    reasoning,
    suggestedName: generateSuggestedName(nodeInfo.name, level),
    category,
  };
}
