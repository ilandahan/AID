/**
 * @file services/ScoringEngine/formatting.ts
 * @description Report formatting for display
 */

import type { ComponentQualityReport } from '../../types';
import type { ScoringConfig } from './types';

/**
 * Get visual icon based on score
 */
export function getScoreIcon(score: number): string {
  if (score >= 80) return '✅';
  if (score >= 60) return '⚠️';
  return '❌';
}

/**
 * Format report for display with ASCII art
 */
export function formatReportForDisplay(
  report: ComponentQualityReport,
  config: ScoringConfig
): string {
  const statusEmoji = report.exportReady ? '✅' : '⚠️';
  const statusText = report.exportReady ? 'READY FOR EXPORT' : 'NOT READY';

  let output = `
╔════════════════════════════════════════════════════════════╗
║  📊 COMPONENT QUALITY REPORT                               ║
╠════════════════════════════════════════════════════════════╣
║  Component: ${report.componentName.padEnd(43)}║
║  Type: ${report.componentType.padEnd(48)}║
║  Generated: ${new Date(report.generatedAt).toLocaleString().padEnd(43)}║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║     OVERALL SCORE: ${report.overallScore}/100  ${statusEmoji} ${statusText.padEnd(23)}║
║     ${'█'.repeat(Math.floor(report.overallScore / 5))}${'░'.repeat(20 - Math.floor(report.overallScore / 5))}                        ║
║                                                            ║
╠════════════════════════════════════════════════════════════╣
║  CATEGORY BREAKDOWN:                                       ║
║  ├── ${getScoreIcon(report.scores.consistency)} Consistency:    ${String(report.scores.consistency).padStart(3)}/100                      ║
║  ├── ${getScoreIcon(report.scores.metadata)} Metadata:       ${String(report.scores.metadata).padStart(3)}/100                      ║
║  ├── ${getScoreIcon(report.scores.accessibility)} Accessibility:  ${String(report.scores.accessibility).padStart(3)}/100                      ║
║  └── ${getScoreIcon(report.scores.structure)} Structure:      ${String(report.scores.structure).padStart(3)}/100                      ║
╠════════════════════════════════════════════════════════════╣`;

  if (report.blockers.length > 0) {
    output += `
║  🔴 BLOCKERS (${report.blockers.length}):                                          ║`;
    for (const blocker of report.blockers.slice(0, 5)) {
      output += `
║     • ${blocker.substring(0, 50).padEnd(50)}║`;
    }
  }

  if (report.requiredFixes.length > 0) {
    output += `
╠════════════════════════════════════════════════════════════╣
║  🟡 REQUIRED FIXES (${report.requiredFixes.length}):                                    ║`;
    for (const fix of report.requiredFixes.slice(0, 5)) {
      output += `
║     • ${fix.issue.substring(0, 50).padEnd(50)}║`;
    }
  }

  if (!report.exportReady) {
    const pointsNeeded = config.exportThreshold - report.overallScore;
    output += `
╠════════════════════════════════════════════════════════════╣
║  📈 ${pointsNeeded} points needed to reach export threshold (90)         ║`;
  }

  output += `
╚════════════════════════════════════════════════════════════╝`;

  return output;
}
