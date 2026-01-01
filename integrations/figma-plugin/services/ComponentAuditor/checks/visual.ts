/**
 * @file services/ComponentAuditor/checks/visual.ts
 * @description Visual consistency checks (fonts, colors, border radius)
 */

import type { AuditIssue, CategoryScore, CheckResult } from '../../../types';
import { SCORING_CONFIG } from '../config';

/**
 * Run all visual checks on a node
 */
export function checkVisual(node: SceneNode, issues: AuditIssue[]): CategoryScore {
  const checks: CheckResult[] = [];
  let passed = 0;
  let failed = 0;
  let warnings = 0;

  // Check 1: Consistent font sizes
  const fontSizeCheck = checkFontSizeConsistency(node);
  checks.push(fontSizeCheck);
  if (fontSizeCheck.passed) passed++; else warnings++;
  if (!fontSizeCheck.passed) {
    issues.push({
      severity: 'warning',
      category: 'visual',
      message: fontSizeCheck.message,
      location: node.name,
      suggestion: 'Standardize font sizes to whole numbers (e.g., 14px instead of 13.7px)',
      autoFixable: true
    });
  }

  // Check 2: Consistent border radius
  const borderRadiusCheck = checkBorderRadiusConsistency(node);
  checks.push(borderRadiusCheck);
  if (borderRadiusCheck.passed) passed++; else warnings++;

  // Check 3: Uses design system colors (basic check)
  const colorCheck = checkColorUsage(node);
  checks.push(colorCheck);
  if (colorCheck.passed) passed++; else warnings++;

  const score = checks.length > 0 ? Math.round((passed / checks.length) * 100) : 100;

  return {
    score,
    weight: SCORING_CONFIG.weights.consistency,
    passed,
    failed,
    warnings,
    checks
  };
}

/**
 * Check for consistent font sizes (no fractional sizes like 13.7px)
 */
export function checkFontSizeConsistency(node: SceneNode): CheckResult {
  const fontSizes: number[] = [];

  const collectFontSizes = (n: SceneNode) => {
    if (n.type === 'TEXT') {
      const fontSize = n.fontSize;
      if (typeof fontSize === 'number') {
        fontSizes.push(fontSize);
      }
    }
    if ('children' in n) {
      for (const child of n.children) {
        collectFontSizes(child);
      }
    }
  };

  collectFontSizes(node);

  // Check for non-integer font sizes
  const nonInteger = fontSizes.filter(s => s !== Math.round(s));

  return {
    name: 'Font size consistency',
    passed: nonInteger.length === 0,
    message: nonInteger.length === 0
      ? 'All font sizes are whole numbers'
      : `Found non-standard font sizes: ${[...new Set(nonInteger)].join('px, ')}px`,
    severity: nonInteger.length > 0 ? 'warning' : undefined
  };
}

/**
 * Check for consistent border radius values
 */
export function checkBorderRadiusConsistency(node: SceneNode): CheckResult {
  const radii: number[] = [];

  const collectRadii = (n: SceneNode) => {
    if ('cornerRadius' in n && typeof n.cornerRadius === 'number') {
      radii.push(n.cornerRadius);
    }
    if ('children' in n) {
      for (const child of n.children) {
        collectRadii(child);
      }
    }
  };

  collectRadii(node);

  const uniqueRadii = [...new Set(radii)];

  // Allow up to 4 different radii (0, 8, 999 for pill shapes, etc.)
  const threshold = 4;

  return {
    name: 'Border radius consistency',
    passed: uniqueRadii.length <= threshold,
    message: uniqueRadii.length <= threshold
      ? `Consistent border radii: ${uniqueRadii.join('px, ')}px`
      : `Multiple border radii found: ${uniqueRadii.join('px, ')}px - consider standardizing`,
    severity: uniqueRadii.length > threshold ? 'info' : undefined
  };
}

/**
 * Check color usage (basic check - full validation requires design tokens)
 */
export function checkColorUsage(node: SceneNode): CheckResult {
  return {
    name: 'Color usage',
    passed: true,
    message: 'Color usage check - requires design system tokens for full validation'
  };
}
