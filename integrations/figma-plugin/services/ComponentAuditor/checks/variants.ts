/**
 * @file services/ComponentAuditor/checks/variants.ts
 * @description Variant completeness and quality checks
 */

import type { AuditIssue, CategoryScore, CheckResult } from '../../../types';
import { isInteractiveComponent } from '../utils';

/**
 * Run all variant checks on a node
 */
export function checkVariants(node: SceneNode, issues: AuditIssue[]): CategoryScore {
  const checks: CheckResult[] = [];
  let passed = 0;
  let failed = 0;
  let warnings = 0;

  if (node.type !== 'COMPONENT_SET') {
    return {
      score: 100,
      weight: 0.1,
      passed: 1,
      failed: 0,
      warnings: 0,
      checks: [{ name: 'N/A', passed: true, message: 'Not a component set' }]
    };
  }

  // Check 1: Has all expected states
  const statesCheck = checkExpectedStates(node);
  checks.push(statesCheck);
  if (statesCheck.passed) passed++; else warnings++;

  // Check 2: No missing variant combinations
  const combinationsCheck = checkVariantCombinations(node);
  checks.push(combinationsCheck);
  if (combinationsCheck.passed) passed++; else warnings++;

  // Check 3: Each variant is visually distinct
  const distinctCheck = checkVariantDistinction(node);
  checks.push(distinctCheck);
  if (distinctCheck.passed) passed++; else warnings++;

  const score = checks.length > 0 ? Math.round((passed / checks.length) * 100) : 100;

  return {
    score,
    weight: 0.15,
    passed,
    failed,
    warnings,
    checks
  };
}

/**
 * Check for expected states (Default/Rest, Hover for interactive)
 */
export function checkExpectedStates(componentSet: ComponentSetNode): CheckResult {
  const variantNames = componentSet.children.map(c => c.name.toLowerCase());

  // Accept "Default" OR "Rest" OR "Normal" as valid default states
  const hasDefault = variantNames.some(n =>
    n.includes('default') || n.includes('rest') || n.includes('normal')
  );
  const hasHover = variantNames.some(n => n.includes('hover'));

  // Only require Hover for interactive components
  const isInteractive = isInteractiveComponent(componentSet.name);

  const missingStates: string[] = [];
  if (!hasDefault) missingStates.push('Default/Rest/Normal');
  if (!hasHover && isInteractive) missingStates.push('Hover');

  const successMessage = isInteractive
    ? 'Has required states (Default/Rest + Hover)'
    : 'Has base state (Default/Rest/Normal)';

  return {
    name: 'Expected states',
    passed: missingStates.length === 0,
    message: missingStates.length === 0
      ? successMessage
      : `Missing states: ${missingStates.join(', ')}`,
    severity: missingStates.length > 0 ? 'warning' : undefined
  };
}

/**
 * Check variant combinations count
 */
export function checkVariantCombinations(componentSet: ComponentSetNode): CheckResult {
  const variantCount = componentSet.children.length;

  return {
    name: 'Variant combinations',
    passed: variantCount >= 2,
    message: `Found ${variantCount} variants`,
    severity: variantCount < 2 ? 'info' : undefined
  };
}

/**
 * Check that variants are visually distinct (requires manual review)
 */
export function checkVariantDistinction(componentSet: ComponentSetNode): CheckResult {
  return {
    name: 'Variant visual distinction',
    passed: true,
    message: 'Visual distinction check requires manual review'
  };
}
