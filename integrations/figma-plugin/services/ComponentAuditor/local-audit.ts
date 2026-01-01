/**
 * @file services/ComponentAuditor/local-audit.ts
 * @description Local audit execution and deep inspection
 */

import type { AuditResult, AuditIssue } from '../../types';
import { checkNaming, checkStructure, checkVisual, checkAccessibility, checkVariants } from './checks';
import { calculateScore, identifyBlockers, generateSuggestions, calculateDeepInspectionPenalty } from './scoring';

/**
 * Run local audit checks that don't require Claude.
 * These are structural checks that can be done directly on Figma data.
 *
 * DEEP INSPECTION MODE:
 * When auditing a COMPONENT_SET, we audit EACH variant (child COMPONENT)
 * individually and aggregate all issues.
 */
export function runLocalAudit(node: SceneNode): AuditResult {
  const issues: AuditIssue[] = [];

  console.log(`[AUDIT] Starting deep inspection of: ${node.name} (${node.type})`);
  const startTime = Date.now();

  // Run all check categories on the main node
  const namingResult = checkNaming(node, issues);
  const structureResult = checkStructure(node, issues);
  const visualResult = checkVisual(node, issues);
  const accessibilityResult = checkAccessibility(node, issues);
  const variantsResult = checkVariants(node, issues);

  // DEEP INSPECTION: If this is a COMPONENT_SET, audit each variant individually
  if (node.type === 'COMPONENT_SET') {
    const variants = node.children.filter(c => c.type === 'COMPONENT') as ComponentNode[];
    console.log(`[AUDIT] Deep inspecting ${variants.length} variants...`);

    for (const variant of variants) {
      console.log(`[AUDIT]   → Inspecting variant: ${variant.name}`);

      const variantIssues: AuditIssue[] = [];

      // Run individual checks on each variant
      checkNaming(variant, variantIssues);
      checkVisual(variant, variantIssues);
      checkStructure(variant, variantIssues);

      // Add variant context and nodeId to each issue for navigation
      variantIssues.forEach(issue => {
        issue.location = `${variant.name} > ${issue.location || 'root'}`;
        issue.nodeId = variant.id;
        issues.push(issue);
      });
    }
  }

  // Also deep inspect nested components (for organisms)
  if ('children' in node && node.type !== 'COMPONENT_SET') {
    deepInspectChildren(node as FrameNode, issues);
  }

  const elapsed = Date.now() - startTime;
  console.log(`[AUDIT] Deep inspection complete: ${issues.length} issues found in ${elapsed}ms`);

  // Calculate overall score
  const categories = {
    naming: namingResult,
    structure: structureResult,
    visual: visualResult,
    accessibility: accessibilityResult,
    variants: variantsResult
  };

  // Adjust score based on deep inspection issues
  let score = calculateScore(categories);
  const penalty = calculateDeepInspectionPenalty(issues);
  score = Math.max(0, score - penalty);

  console.log(`[AUDIT] Final score: ${score} (penalty: ${penalty})`);

  const blockers = identifyBlockers(issues);

  return {
    score,
    categories,
    issues,
    suggestions: generateSuggestions(issues),
    blockers
  };
}

/**
 * Deep inspect nested children for complex components (molecules/organisms)
 */
export function deepInspectChildren(
  node: FrameNode,
  issues: AuditIssue[],
  depth: number = 0
): void {
  if (depth > 3) return; // Limit depth to prevent performance issues

  for (const child of node.children) {
    if (child.type === 'INSTANCE' || child.type === 'COMPONENT') {
      console.log(`[AUDIT]   → Inspecting nested: ${child.name} (depth=${depth})`);

      const nestedIssues: AuditIssue[] = [];
      checkNaming(child, nestedIssues);
      checkVisual(child, nestedIssues);

      nestedIssues.forEach(issue => {
        issue.location = `${node.name} > ${child.name} > ${issue.location || 'root'}`;
        issue.nodeId = child.id;
        issues.push(issue);
      });
    }

    if ('children' in child) {
      deepInspectChildren(child as FrameNode, issues, depth + 1);
    }
  }
}
