/**
 * @file services/ScoringEngine/config.ts
 * @description Default configuration for scoring engine
 */

import type { ScoringConfig } from './types';

/**
 * Default scoring configuration
 *
 * Weights must sum to 1.0 (100%)
 * - consistency: 25% - Naming and visual consistency
 * - metadata: 30% - Documentation completeness
 * - accessibility: 25% - A11y compliance (critical)
 * - structure: 20% - Component structure
 *
 * Export threshold: 90/100 minimum score required
 */
export const DEFAULT_CONFIG: ScoringConfig = {
  weights: {
    consistency: 0.25,    // 25%
    metadata: 0.30,       // 30%
    accessibility: 0.25,  // 25%
    structure: 0.20       // 20%
  },
  minimums: {
    consistency: 70,
    metadata: 60,
    accessibility: 80,
    structure: 70
  },
  exportThreshold: 90
};
