/**
 * @file services/NodeAnalyzer/index.ts
 * @description Figma node analyzer that classifies components in the Atomic Design hierarchy.
 *              Extracts node properties, design tokens, and creates work plans for conversion.
 * @created 2024-12
 * @refactored 2024-12 - Modular structure for maintainability
 */

import type {
  FigmaNodeInfo,
  ComponentClassification,
  DependencyInfo,
  ComponentWorkPlan,
  DesignToken,
} from '../../types';

// Import from modules
import { createNodeInfoExtractor } from './extraction';
import { classifyComponent, countChildren, calculateDepth } from './classification';
import { extractTokens } from './tokens';
import { findDependencies, createWorkPlan } from './work-plan';

// Re-export configuration
export {
  ATOM_PATTERNS,
  MOLECULE_PATTERNS,
  ORGANISM_PATTERNS,
  TEMPLATE_PATTERNS,
  CATEGORY_PATTERNS,
} from './config';

// Re-export classification utilities
export {
  classifyComponent,
  countChildren,
  calculateDepth,
  isLayoutContainer,
  detectCategory,
  generateSuggestedName,
} from './classification';

// Re-export token utilities
export {
  extractTokens,
  rgbToHex,
  rgbaToString,
  deduplicateTokens,
} from './tokens';

// Re-export work plan utilities
export { findDependencies, createWorkPlan } from './work-plan';

/**
 * NodeAnalyzer class - Facade for all node analysis operations
 */
export class NodeAnalyzer {
  private nodeCache: Map<string, FigmaNodeInfo> = new Map();
  private extractNodeInfoFn: (node: SceneNode) => FigmaNodeInfo;

  constructor() {
    this.extractNodeInfoFn = createNodeInfoExtractor(this.nodeCache);
  }

  /**
   * Extract detailed info from a Figma node
   */
  extractNodeInfo(node: SceneNode): FigmaNodeInfo {
    return this.extractNodeInfoFn(node);
  }

  /**
   * Classify a component in the Atomic Design hierarchy
   */
  classifyComponent(nodeInfo: FigmaNodeInfo): ComponentClassification {
    return classifyComponent(nodeInfo);
  }

  /**
   * Find dependencies of a component
   */
  findDependencies(nodeInfo: FigmaNodeInfo): DependencyInfo[] {
    return findDependencies(nodeInfo, this.nodeCache);
  }

  /**
   * Extract design tokens from a node
   */
  extractTokens(nodeInfo: FigmaNodeInfo): DesignToken[] {
    return extractTokens(nodeInfo);
  }

  /**
   * Create a work plan for converting a component
   */
  createWorkPlan(nodeInfo: FigmaNodeInfo): ComponentWorkPlan {
    return createWorkPlan(nodeInfo, this.nodeCache);
  }

  /**
   * Clear the node cache
   */
  clearCache(): void {
    this.nodeCache.clear();
  }
}

// Export singleton instance
export const nodeAnalyzer = new NodeAnalyzer();
