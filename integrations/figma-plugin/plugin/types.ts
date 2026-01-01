/**
 * @file plugin/types.ts
 * @description Shared types for the Figma plugin modules
 */

import type {
  AuditResult,
  MetadataGapAnalysis,
  GeneratedMetadata,
  ComponentQualityReport,
  DesignToken,
} from '../types';

// ============================================
// Plugin State Types
// ============================================

/**
 * Current component state maintained by the plugin
 */
export interface PluginCurrentState {
  selectedNode: SceneNode | null;
  audit: AuditResult | null;
  metadata: MetadataGapAnalysis | null;
  generated: GeneratedMetadata | null;
  report: ComponentQualityReport | null;
  tokens: DesignToken[];
}

// ============================================
// UI Message Types
// ============================================

/**
 * Information about the currently selected component
 */
export interface SelectionInfo {
  name: string;
  type: string;
  nodeId: string;
  variantCount?: number;
  childCount?: number;
  hasDescription: boolean;
}

/**
 * Results from a complete pipeline run
 */
export interface PipelineResults {
  audit: AuditResult;
  metadata: MetadataGapAnalysis;
  generated: GeneratedMetadata;
  report: ComponentQualityReport;
  exportReady: boolean;
}

/**
 * Messages sent from plugin to UI
 */
export type PluginToUIMessage =
  | { type: 'SELECTION_CHANGED'; node: SelectionInfo | null }
  | { type: 'AUDIT_COMPLETE'; audit: AuditResult }
  | { type: 'METADATA_ANALYZED'; metadata: MetadataGapAnalysis }
  | { type: 'METADATA_GENERATED'; generated: GeneratedMetadata }
  | { type: 'METADATA_APPLIED'; validationPassed?: boolean; appliedLength?: number; expectedLength?: number }
  | { type: 'METADATA_APPLY_FAILED'; error: string }
  | { type: 'REPORT_READY'; report: ComponentQualityReport }
  | { type: 'MCP_CONNECTED' }
  | { type: 'MCP_DISCONNECTED' }
  | {
      type: 'EXPORT_SUCCESS';
      format: string;
      files?: string[];
      componentDir?: string;
      // Cloud export fields
      zipBase64?: string;
      downloadFilename?: string;
      downloadSize?: number;
      isCloudExport?: boolean;
      componentName?: string;
      relativePath?: string;
    }
  | { type: 'CONTENT_EXPORTED'; content: string; format: string; filename: string }
  | { type: 'ERROR'; message: string }
  | { type: 'PIPELINE_STEP'; step: string; status: string; detail?: string }
  | { type: 'PIPELINE_COMPLETE'; results: PipelineResults }
  // AID Pairing messages
  | { type: 'AID_PAIRED'; token: string }
  | { type: 'AID_PAIR_FAILED'; error: string }
  | { type: 'AID_TOKEN_VALID'; token: string }
  | { type: 'AID_TOKEN_INVALID' }
  | { type: 'AID_TOKEN_VALIDATING'; token: string }
  | { type: 'AID_SESSION_EXPIRING'; remainingSec: number; remainingHuman: string }
  | { type: 'AID_CONNECTION_LOST' }
  | { type: 'AID_CONNECTION_RECONNECTING'; token?: string };

/**
 * Messages received from UI
 */
export type UIToPluginMessage =
  | { type: 'INIT' }
  | { type: 'RUN_AUDIT' }
  | { type: 'ANALYZE_METADATA' }
  | { type: 'GENERATE_METADATA' }
  | { type: 'APPLY_METADATA_TO_FIGMA' }
  | { type: 'EXPORT_TO_AID'; level?: AtomicLevel; componentName?: string }
  | { type: 'EXPORT_CONTENT'; format: 'json' | 'typescript' | 'csv' }
  | { type: 'RUN_FULL_PIPELINE' }
  | { type: 'CONNECT_MCP'; endpoint: string }
  | { type: 'DISCONNECT_MCP' }
  | { type: 'AID_PAIR'; code: string }
  | { type: 'CHECK_AID_TOKEN' }
  | { type: 'AID_DISCONNECT' }
  | { type: 'SELECT_NODE'; nodeId: string };

// ============================================
// Export Types
// ============================================

/**
 * Atomic design levels for component classification
 * NOTE: Classification is done by SERVER (single source of truth)
 */
export type AtomicLevel = 'atom' | 'molecule' | 'organism' | 'template' | 'page';

/**
 * Export payload for AID system
 */
export interface AIDExportPayload {
  component: {
    name: string;
    type: string;
    description: string;
    level: AtomicLevel;
    destinationPath: string;
  };
  metadata: GeneratedMetadata;
  tokens: DesignToken[];
  content: Record<string, string>;
  qualityCertification: {
    score: number;
    auditedAt: Date;
    passedChecks: string[];
  };
  figma: {
    fileKey: string;
    nodeId: string;
    exportedAt: Date;
  };
  filesToCreate: {
    component: string;
    styles: string;
    test: string;
    index: string;
  };
}

// ============================================
// Pipeline Phase Types
// ============================================

export type PipelinePhase = 'audit' | 'metadata' | 'generate' | 'report';
export type PipelineStatus = 'waiting' | 'running' | 'done' | 'error';
