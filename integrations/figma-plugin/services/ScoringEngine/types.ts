/**
 * @file services/ScoringEngine/types.ts
 * @description Type definitions for ScoringEngine
 */

/**
 * Configuration for the scoring engine
 */
export interface ScoringConfig {
  weights: {
    consistency: number;
    metadata: number;
    accessibility: number;
    structure: number;
  };
  minimums: {
    consistency: number;
    metadata: number;
    accessibility: number;
    structure: number;
  };
  exportThreshold: number;
}

/**
 * Result of score calculation
 */
export interface ScoreResult {
  overall: number;
  breakdown: Record<string, number>;
  meetsMinimums: boolean;
  failedMinimums: string[];
}

/**
 * Export readiness result
 */
export interface ExportReadinessResult {
  ready: boolean;
  score: number;
  blockers: string[];
  pointsNeeded: number;
}

/**
 * Categorized action items
 */
export interface CategorizedActionItems {
  critical: import('../../types').ActionItem[];
  high: import('../../types').ActionItem[];
  medium: import('../../types').ActionItem[];
  low: import('../../types').ActionItem[];
}

// Re-export types from main types file
export type {
  AuditResult,
  MetadataGapAnalysis,
  ComponentQualityReport,
  GeneratedMetadata,
  ActionItem,
  AuditCategory,
} from '../../types';
