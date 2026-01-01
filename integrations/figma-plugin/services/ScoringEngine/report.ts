/**
 * @file services/ScoringEngine/report.ts
 * @description Report generation functions
 */

import type {
  AuditResult,
  MetadataGapAnalysis,
  ComponentQualityReport,
  GeneratedMetadata,
} from '../../types';
import type { ScoringConfig } from './types';
import { calculateOverallScore, checkExportReadiness } from './scoring';
import { generateActionItems } from './action-items';

/**
 * Generate full quality report
 */
export function generateReport(
  componentName: string,
  componentType: 'COMPONENT' | 'COMPONENT_SET' | 'INSTANCE',
  audit: AuditResult,
  metadata: MetadataGapAnalysis,
  config: ScoringConfig,
  suggestedMetadata?: GeneratedMetadata
): ComponentQualityReport {
  const { overall, breakdown } = calculateOverallScore(audit, metadata, config);
  const exportStatus = checkExportReadiness(audit, metadata, config);
  const actionItems = generateActionItems(audit, metadata);

  return {
    componentName,
    componentType,
    generatedAt: new Date(),

    overallScore: overall,
    scores: {
      consistency: breakdown.consistency,
      metadata: breakdown.metadata,
      accessibility: breakdown.accessibility,
      structure: breakdown.structure
    },

    exportReady: exportStatus.ready,
    blockers: exportStatus.blockers,

    audit,
    metadata,

    suggestedMetadata: suggestedMetadata || generatePlaceholderMetadata(componentName),

    requiredFixes: [...actionItems.critical, ...actionItems.high],
    recommendedFixes: [...actionItems.medium, ...actionItems.low]
  };
}

/**
 * Generate placeholder metadata for a component
 */
export function generatePlaceholderMetadata(_componentName: string): GeneratedMetadata {
  return {
    description: '',
    tags: [],
    notes: '',
    ariaLabel: '',
    category: 'button',
    level: 'atom',
    priority: 'medium',
    analytics: '',
    testId: '',
    tokens: {
      colors: [],
      spacing: [],
      typography: [],
      radius: [],
      shadows: [],
      borders: []
    },
    states: {
      default: '',
      hover: '',
      focus: '',
      active: '',
      disabled: ''
    },
    variants: {},
    dos: [],
    donts: [],
    a11y: [],
    related: [],
    specs: {},
    formattedDescription: '',
    variantDescriptions: {}
  };
}
