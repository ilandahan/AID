/**
 * @file services/ComponentAuditor/index.ts
 * @description Component auditor service barrel export.
 *              Coordinates the 4-phase quality pipeline: Audit → Analyze → Generate → Report.
 * @created 2024-12
 * @refactored 2024-12 - Extracted modules to ./ComponentAuditor/
 */

// Re-export all check functions
export * from './checks';

// Re-export configuration
export { SCORING_CONFIG, INTERACTIVE_PATTERNS, CORRECT_TERMS, GENERIC_LAYER_NAMES } from './config';

// Re-export utilities
export { isInteractiveComponent, levenshteinDistance, extractNameValues } from './utils';

// Re-export scoring functions
export { calculateScore, identifyBlockers, generateSuggestions, calculateDeepInspectionPenalty } from './scoring';

// Re-export main audit functions
export { runLocalAudit, deepInspectChildren } from './local-audit';

// Re-export metadata analysis
export { analyzeMetadataLocal } from './metadata-analysis';

// Re-export MCP preparation
export { prepareForMCP } from './mcp-preparation';

// ============================================
// ComponentAuditor Class (facade for compatibility)
// ============================================

import type { AuditResult, MetadataGapAnalysis, ComponentAuditRequest } from '../../types';
import { runLocalAudit as _runLocalAudit } from './local-audit';
import { analyzeMetadataLocal as _analyzeMetadataLocal } from './metadata-analysis';
import { prepareForMCP as _prepareForMCP } from './mcp-preparation';

/**
 * ComponentAuditor class - facade for backward compatibility.
 * All methods are static and delegate to modular functions.
 */
export class ComponentAuditor {
  /**
   * Run local audit checks that don't require Claude
   */
  static runLocalAudit(node: SceneNode): AuditResult {
    return _runLocalAudit(node);
  }

  /**
   * Analyze metadata completeness locally
   */
  static analyzeMetadataLocal(node: SceneNode, description?: string): MetadataGapAnalysis {
    return _analyzeMetadataLocal(node, description);
  }

  /**
   * Prepare component data for sending to Claude via MCP
   */
  static prepareForMCP(node: SceneNode): ComponentAuditRequest {
    return _prepareForMCP(node);
  }
}

// ============================================
// Convenience exports for direct function usage
// ============================================

/**
 * Run audit on a node
 */
export function runAudit(node: SceneNode): AuditResult {
  return _runLocalAudit(node);
}

/**
 * Analyze metadata for a node
 */
export function analyzeMetadata(node: SceneNode, description?: string): MetadataGapAnalysis {
  return _analyzeMetadataLocal(node, description);
}

// Default export for the class
export default ComponentAuditor;
