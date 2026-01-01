/**
 * @file services/ComponentAuditor/scoring.ts
 * @description Score calculation and suggestion generation
 */

import type { AuditResult, AuditIssue, CategoryScore } from '../../types';

/**
 * Calculate weighted score from category scores
 */
export function calculateScore(categories: AuditResult['categories']): number {
  let weightedSum = 0;
  let totalWeight = 0;

  for (const [key, category] of Object.entries(categories) as [string, CategoryScore][]) {
    weightedSum += category.score * category.weight;
    totalWeight += category.weight;
  }

  return totalWeight > 0 ? Math.round(weightedSum / totalWeight) : 0;
}

/**
 * Identify blocking issues (errors that prevent export)
 */
export function identifyBlockers(issues: AuditIssue[]): string[] {
  return issues
    .filter(i => i.severity === 'error')
    .map(i => i.message);
}

/**
 * Generate actionable suggestions from issues
 */
export function generateSuggestions(issues: AuditIssue[]): string[] {
  return issues
    .filter(i => i.suggestion)
    .map(i => i.suggestion as string)
    .slice(0, 5); // Top 5 suggestions
}

/**
 * Calculate penalty for deep inspection issues
 */
export function calculateDeepInspectionPenalty(issues: AuditIssue[]): number {
  const deepIssues = issues.filter(i => i.location?.includes(' > '));
  const errorPenalty = deepIssues.filter(i => i.severity === 'error').length * 3;
  const warningPenalty = deepIssues.filter(i => i.severity === 'warning').length * 1;
  return errorPenalty + warningPenalty;
}
