/**
 * @file ScoringEngine.ts
 * @description Scoring engine that calculates weighted quality scores for Figma components.
 * @created 2024-12
 * @refactored 2024-12 - Extracted modules to ./services/ScoringEngine/
 *
 * This file re-exports the modular ScoringEngine for backward compatibility.
 * The actual implementation is in ./services/ScoringEngine/
 *
 * @scoring
 *   Weights (must sum to 1.0):
 *   - consistency: 25% - Naming and visual consistency
 *   - metadata: 30% - Documentation completeness
 *   - accessibility: 25% - A11y compliance (critical)
 *   - structure: 20% - Component structure
 *
 *   Export threshold: 90/100 minimum score required
 */

// Re-export everything from the modular implementation
export {
  // Main class and singleton
  ScoringEngine,
  scoringEngine,

  // Types
  type ScoringConfig,
  type ScoreResult,
  type ExportReadinessResult,
  type CategorizedActionItems,
  type AuditResult,
  type MetadataGapAnalysis,
  type ComponentQualityReport,
  type GeneratedMetadata,
  type ActionItem,

  // Configuration
  DEFAULT_CONFIG,

  // Scoring functions
  calculateOverallScore,
  checkExportReadiness,
  calculateScore,
  isExportReady,

  // Action items
  generateActionItems,

  // Report generation
  generateReport,
  generatePlaceholderMetadata,

  // Formatting
  formatReportForDisplay,
  getScoreIcon,
} from './services/ScoringEngine';

// Default export for backward compatibility
export { ScoringEngine as default } from './services/ScoringEngine';
