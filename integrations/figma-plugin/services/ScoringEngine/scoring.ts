/**
 * @file services/ScoringEngine/scoring.ts
 * @description Core scoring calculation functions
 */

import type { AuditResult, MetadataGapAnalysis } from '../../types';
import type { ScoringConfig, ScoreResult, ExportReadinessResult } from './types';

/**
 * Calculate overall quality score from audit and metadata analysis
 */
export function calculateOverallScore(
  audit: AuditResult,
  metadata: MetadataGapAnalysis,
  config: ScoringConfig
): ScoreResult {
  // Calculate category scores
  const consistency = audit.categories.naming.score;
  const structure = audit.categories.structure.score;
  const accessibility = audit.categories.accessibility.score;
  const metadataScore = metadata.completenessScore;

  // Weighted average
  const weighted =
    (consistency * config.weights.consistency) +
    (metadataScore * config.weights.metadata) +
    (accessibility * config.weights.accessibility) +
    (structure * config.weights.structure);

  const overall = Math.round(weighted);

  // Check minimums
  const failedMinimums: string[] = [];
  if (consistency < config.minimums.consistency) {
    failedMinimums.push(`Consistency: ${consistency} < ${config.minimums.consistency}`);
  }
  if (metadataScore < config.minimums.metadata) {
    failedMinimums.push(`Metadata: ${metadataScore} < ${config.minimums.metadata}`);
  }
  if (accessibility < config.minimums.accessibility) {
    failedMinimums.push(`Accessibility: ${accessibility} < ${config.minimums.accessibility}`);
  }
  if (structure < config.minimums.structure) {
    failedMinimums.push(`Structure: ${structure} < ${config.minimums.structure}`);
  }

  return {
    overall,
    breakdown: {
      consistency,
      metadata: metadataScore,
      accessibility,
      structure
    },
    meetsMinimums: failedMinimums.length === 0,
    failedMinimums
  };
}

/**
 * Check if component is ready for export
 */
export function checkExportReadiness(
  audit: AuditResult,
  metadata: MetadataGapAnalysis,
  config: ScoringConfig
): ExportReadinessResult {
  const { overall, meetsMinimums, failedMinimums } = calculateOverallScore(audit, metadata, config);

  const blockers: string[] = [
    ...audit.blockers,
    ...failedMinimums
  ];

  // Check for critical issues
  if (audit.categories.accessibility.score < config.minimums.accessibility) {
    blockers.push('Accessibility score below minimum');
  }

  if (metadata.componentSetLevel.missing.includes('description')) {
    blockers.push('Missing component description');
  }

  const ready = overall >= config.exportThreshold && blockers.length === 0;
  const pointsNeeded = ready ? 0 : config.exportThreshold - overall;

  return {
    ready,
    score: overall,
    blockers: [...new Set(blockers)], // Remove duplicates
    pointsNeeded: Math.max(0, pointsNeeded)
  };
}
