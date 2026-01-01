/**
 * @file services/ComponentAuditor/checks/accessibility.ts
 * @description Accessibility checks (focus states, touch targets, disabled states)
 */

import type { AuditIssue, CategoryScore, CheckResult } from '../../../types';
import { SCORING_CONFIG } from '../config';
import { isInteractiveComponent } from '../utils';

/**
 * Run all accessibility checks on a node
 */
export function checkAccessibility(node: SceneNode, issues: AuditIssue[]): CategoryScore {
  const checks: CheckResult[] = [];
  let passed = 0;
  let failed = 0;
  let warnings = 0;

  // Check 1: Has Focus state (for INTERACTIVE components only)
  if (node.type === 'COMPONENT_SET') {
    const isInteractive = isInteractiveComponent(node.name);
    const focusCheck = checkFocusState(node, isInteractive);
    checks.push(focusCheck);
    if (focusCheck.passed) passed++; else { failed++; }
    if (!focusCheck.passed && isInteractive) {
      issues.push({
        severity: 'error',
        category: 'accessibility',
        message: 'Missing Focus state - required for keyboard navigation',
        location: node.name,
        suggestion: 'Add Focus variant with visible focus ring (2-3px offset, 3:1 contrast)',
        autoFixable: false
      });
    }
  }

  // Check 2: Has Disabled state
  if (node.type === 'COMPONENT_SET') {
    const disabledCheck = checkDisabledState(node);
    checks.push(disabledCheck);
    if (disabledCheck.passed) passed++; else warnings++;
  }

  // Check 3: Touch target size
  const touchTargetCheck = checkTouchTargetSize(node);
  checks.push(touchTargetCheck);
  if (touchTargetCheck.passed) passed++; else warnings++;

  const score = checks.length > 0 ? Math.round((passed / checks.length) * 100) : 100;

  return {
    score,
    weight: SCORING_CONFIG.weights.accessibility,
    passed,
    failed,
    warnings,
    checks
  };
}

/**
 * Check for Focus state in component set
 */
export function checkFocusState(componentSet: ComponentSetNode, isInteractive: boolean): CheckResult {
  const variantNames = componentSet.children.map(c => c.name.toLowerCase());
  const hasFocus = variantNames.some(name =>
    name.includes('focus') || name.includes('focused')
  );

  // Non-interactive components (Badge, Avatar, Divider) don't need Focus state
  if (!isInteractive) {
    return {
      name: 'Focus state',
      passed: true,
      message: hasFocus
        ? 'Component has Focus state'
        : 'Non-interactive component - Focus state not required',
      severity: undefined
    };
  }

  return {
    name: 'Focus state',
    passed: hasFocus,
    message: hasFocus
      ? 'Component has Focus state'
      : 'Missing Focus state - required for keyboard accessibility',
    severity: hasFocus ? undefined : 'error'
  };
}

/**
 * Check for Disabled state in component set
 */
export function checkDisabledState(componentSet: ComponentSetNode): CheckResult {
  const variantNames = componentSet.children.map(c => c.name.toLowerCase());
  const hasDisabled = variantNames.some(name =>
    name.includes('disabled')
  );

  return {
    name: 'Disabled state',
    passed: hasDisabled,
    message: hasDisabled
      ? 'Component has Disabled state'
      : 'Consider adding Disabled state for interactive components',
    severity: hasDisabled ? undefined : 'info'
  };
}

/**
 * Check touch target meets minimum size (44x44px)
 */
export function checkTouchTargetSize(node: SceneNode): CheckResult {
  // For COMPONENT_SET, measure the first variant child, not the container
  let targetNode: SceneNode = node;

  if (node.type === 'COMPONENT_SET' && 'children' in node && node.children.length > 0) {
    const firstVariant = node.children.find((c: SceneNode) => c.type === 'COMPONENT');
    if (firstVariant) {
      targetNode = firstVariant;
    }
  }

  if (!('width' in targetNode) || !('height' in targetNode)) {
    return {
      name: 'Touch target size',
      passed: true,
      message: 'Cannot determine size'
    };
  }

  const minSize = 44; // iOS/Android recommended minimum
  const width = targetNode.width as number;
  const height = targetNode.height as number;
  const meetsMinimum = width >= minSize && height >= minSize;

  // Add context if measuring a variant
  const context = targetNode !== node ? ` (measured from variant: ${targetNode.name.substring(0, 30)}...)` : '';

  return {
    name: 'Touch target size',
    passed: meetsMinimum,
    message: meetsMinimum
      ? `Touch target meets minimum (${width}x${height}px ≥ 44x44px)${context}`
      : `Touch target too small (${width}x${height}px < 44x44px minimum)${context}`,
    severity: meetsMinimum ? undefined : 'warning'
  };
}
