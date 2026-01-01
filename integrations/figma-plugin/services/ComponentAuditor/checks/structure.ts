/**
 * @file services/ComponentAuditor/checks/structure.ts
 * @description Structure checks for components (auto-layout, wrappers, consistency)
 */

import type { AuditIssue, CategoryScore, CheckResult } from '../../../types';
import { SCORING_CONFIG } from '../config';

/**
 * Run all structure checks on a node
 */
export function checkStructure(node: SceneNode, issues: AuditIssue[]): CategoryScore {
  const checks: CheckResult[] = [];
  let passed = 0;
  let failed = 0;
  let warnings = 0;

  // Check 1: Uses Auto Layout
  if ('layoutMode' in node) {
    const autoLayoutCheck: CheckResult = {
      name: 'Auto Layout',
      passed: node.layoutMode !== 'NONE',
      message: node.layoutMode !== 'NONE'
        ? 'Component uses Auto Layout'
        : 'Component should use Auto Layout for responsiveness',
      severity: node.layoutMode === 'NONE' ? 'warning' : undefined
    };
    checks.push(autoLayoutCheck);
    if (autoLayoutCheck.passed) passed++; else warnings++;
  }

  // Check 2: No unnecessary wrappers
  const wrapperCheck = checkUnnecessaryWrappers(node);
  checks.push(wrapperCheck);
  if (wrapperCheck.passed) passed++; else warnings++;

  // Check 3: Consistent variant structure (for component sets)
  if (node.type === 'COMPONENT_SET') {
    const structureCheck = checkVariantStructureConsistency(node);
    checks.push(structureCheck);
    if (structureCheck.passed) passed++; else warnings++;
  }

  const score = checks.length > 0 ? Math.round((passed / checks.length) * 100) : 100;

  return {
    score,
    weight: SCORING_CONFIG.weights.structure,
    passed,
    failed,
    warnings,
    checks
  };
}

/**
 * Check for unnecessary wrapper frames
 */
export function checkUnnecessaryWrappers(node: SceneNode): CheckResult {
  if (!('children' in node)) {
    return {
      name: 'No unnecessary wrappers',
      passed: true,
      message: 'No children to check for wrappers'
    };
  }

  const unnecessaryWrappers: string[] = [];

  const checkForWrappers = (children: readonly SceneNode[]) => {
    for (const child of children) {
      // A frame/group with exactly one child might be unnecessary
      if ((child.type === 'FRAME' || child.type === 'GROUP') &&
          'children' in child &&
          child.children.length === 1) {
        // Check if the wrapper has no styling
        const hasNoStyling = child.type === 'FRAME' &&
          (!('fills' in child) || (Array.isArray(child.fills) && child.fills.length === 0)) &&
          (!('strokes' in child) || (Array.isArray(child.strokes) && child.strokes.length === 0));

        if (hasNoStyling) {
          unnecessaryWrappers.push(child.name);
        }
      }
    }
  };

  checkForWrappers(node.children);

  if (unnecessaryWrappers.length > 0) {
    return {
      name: 'No unnecessary wrappers',
      passed: true, // Downgrade to info - don't fail for this
      message: `Potential unnecessary wrappers: ${unnecessaryWrappers.slice(0, 2).join(', ')}${unnecessaryWrappers.length > 2 ? '...' : ''}`,
      severity: 'info'
    };
  }

  return {
    name: 'No unnecessary wrappers',
    passed: true,
    message: 'No unnecessary wrapper frames detected'
  };
}

/**
 * Check that variants have consistent structure
 */
export function checkVariantStructureConsistency(componentSet: ComponentSetNode): CheckResult {
  const variants = componentSet.children.filter((c: SceneNode) => c.type === 'COMPONENT') as ComponentNode[];

  if (variants.length < 2) {
    return {
      name: 'Variant structure consistency',
      passed: true,
      message: 'Single variant - consistency check not applicable'
    };
  }

  // Compare layer count across variants
  const layerCounts = variants.map(v => ('children' in v ? v.children.length : 0));
  const allSame = layerCounts.every((c: number) => c === layerCounts[0]);

  // Different layer counts are often INTENTIONAL (hasIcon=true vs false)
  return {
    name: 'Variant structure consistency',
    passed: true, // Always pass - this is informational only
    message: allSame
      ? 'All variants have consistent structure'
      : 'Variants have different layer counts (this may be intentional for variants like hasIcon)',
    severity: allSame ? undefined : 'info'
  };
}
