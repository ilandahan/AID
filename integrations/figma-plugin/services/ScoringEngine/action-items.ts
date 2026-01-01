/**
 * @file services/ScoringEngine/action-items.ts
 * @description Action item generation from audit and metadata results
 */

import type { AuditResult, MetadataGapAnalysis, ActionItem } from '../../types';
import type { CategorizedActionItems } from './types';

/**
 * Generate action items prioritized by impact
 */
export function generateActionItems(
  audit: AuditResult,
  metadata: MetadataGapAnalysis
): CategorizedActionItems {
  const items: ActionItem[] = [];

  // From audit issues (with defensive check)
  const auditIssues = audit?.issues || [];
  for (const issue of auditIssues) {
    items.push({
      priority: issue.severity === 'error' ? 'critical' :
                issue.severity === 'warning' ? 'high' : 'medium',
      category: issue.category,
      issue: issue.message,
      howToFix: issue.suggestion,
      location: issue.location,
      autoFixAvailable: issue.autoFixable
    });
  }

  // From metadata gaps (with defensive check)
  const missingFields = metadata?.componentSetLevel?.missing || [];
  for (const missing of missingFields) {
    const priority = ['description', 'tags', 'notes'].includes(missing) ? 'critical' : 'high';
    items.push({
      priority,
      category: 'metadata',
      issue: `Missing ${missing}`,
      howToFix: `Add ${missing} to component description`,
      location: 'Component Set',
      autoFixAvailable: true
    });
  }

  // Variant descriptions (with defensive check)
  const variantsMissingDesc = metadata?.variantLevel?.missingDescription || [];
  if (variantsMissingDesc.length > 0) {
    items.push({
      priority: 'medium',
      category: 'metadata',
      issue: `${variantsMissingDesc.length} variants missing descriptions`,
      howToFix: 'Add description to each variant in Figma',
      location: 'Variants',
      autoFixAvailable: true
    });
  }

  // Accessibility metadata (with defensive checks)
  const a11yMeta = metadata?.accessibilityMetadata;
  if (a11yMeta && !a11yMeta.hasAriaLabel) {
    items.push({
      priority: 'high',
      category: 'accessibility',
      issue: 'Missing ariaLabel',
      howToFix: 'Add ariaLabel to component metadata',
      location: 'Component Set',
      autoFixAvailable: true
    });
  }

  if (a11yMeta && !a11yMeta.hasA11yNotes) {
    items.push({
      priority: 'medium',
      category: 'accessibility',
      issue: 'Missing accessibility notes',
      howToFix: 'Add a11y section with accessibility requirements',
      location: 'Component Set',
      autoFixAvailable: true
    });
  }

  // Sort and categorize
  return {
    critical: items.filter(i => i.priority === 'critical'),
    high: items.filter(i => i.priority === 'high'),
    medium: items.filter(i => i.priority === 'medium'),
    low: items.filter(i => i.priority === 'low')
  };
}
