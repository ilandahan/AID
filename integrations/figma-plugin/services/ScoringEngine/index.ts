/**
 * @file services/ScoringEngine/index.ts
 * @description Main ScoringEngine class facade and singleton
 */

import type {
  AuditResult,
  MetadataGapAnalysis,
  ComponentQualityReport,
  GeneratedMetadata,
} from '../../types';
import type { ScoringConfig, ScoreResult, ExportReadinessResult, CategorizedActionItems } from './types';
import { DEFAULT_CONFIG } from './config';
import { calculateOverallScore, checkExportReadiness } from './scoring';
import { generateActionItems } from './action-items';
import { generateReport as createReport, generatePlaceholderMetadata } from './report';
import { formatReportForDisplay, getScoreIcon } from './formatting';

// Re-export everything for external consumers
export * from './types';
export { DEFAULT_CONFIG } from './config';
export { calculateOverallScore, checkExportReadiness } from './scoring';
export { generateActionItems } from './action-items';
export { generatePlaceholderMetadata } from './report';
export { formatReportForDisplay, getScoreIcon } from './formatting';

/**
 * ScoringEngine - Calculates weighted quality scores for Figma components
 *
 * Combines audit results and metadata analysis into an overall quality report.
 * Uses configurable weights and thresholds for scoring.
 */
export class ScoringEngine {
  private config: ScoringConfig;

  constructor(config?: Partial<ScoringConfig>) {
    this.config = { ...DEFAULT_CONFIG, ...config };
  }

  /**
   * Calculate overall quality score from audit and metadata analysis
   */
  calculateOverallScore(
    audit: AuditResult,
    metadata: MetadataGapAnalysis
  ): ScoreResult {
    return calculateOverallScore(audit, metadata, this.config);
  }

  /**
   * Check if component is ready for export
   */
  isExportReady(
    audit: AuditResult,
    metadata: MetadataGapAnalysis
  ): ExportReadinessResult {
    return checkExportReadiness(audit, metadata, this.config);
  }

  /**
   * Generate action items prioritized by impact
   */
  generateActionItems(
    audit: AuditResult,
    metadata: MetadataGapAnalysis
  ): CategorizedActionItems {
    return generateActionItems(audit, metadata);
  }

  /**
   * Generate full quality report
   */
  generateReport(
    componentName: string,
    componentType: 'COMPONENT' | 'COMPONENT_SET' | 'INSTANCE',
    audit: AuditResult,
    metadata: MetadataGapAnalysis,
    suggestedMetadata?: GeneratedMetadata
  ): ComponentQualityReport {
    return createReport(componentName, componentType, audit, metadata, this.config, suggestedMetadata);
  }

  /**
   * Format report for display
   */
  formatReportForDisplay(report: ComponentQualityReport): string {
    return formatReportForDisplay(report, this.config);
  }

  /**
   * Get configuration
   */
  getConfig(): ScoringConfig {
    return { ...this.config };
  }

  /**
   * Update configuration
   */
  updateConfig(config: Partial<ScoringConfig>): void {
    this.config = { ...this.config, ...config };
  }
}

// Export singleton instance
export const scoringEngine = new ScoringEngine();

// Convenience functions using singleton
export function calculateScore(audit: AuditResult, metadata: MetadataGapAnalysis) {
  return scoringEngine.calculateOverallScore(audit, metadata);
}

export function isExportReady(audit: AuditResult, metadata: MetadataGapAnalysis) {
  return scoringEngine.isExportReady(audit, metadata);
}

export function generateReport(
  componentName: string,
  componentType: 'COMPONENT' | 'COMPONENT_SET' | 'INSTANCE',
  audit: AuditResult,
  metadata: MetadataGapAnalysis,
  suggestedMetadata?: GeneratedMetadata
) {
  return scoringEngine.generateReport(componentName, componentType, audit, metadata, suggestedMetadata);
}
