/**
 * @file services/ComponentAuditor/checks/naming.ts
 * @description Naming convention checks for components
 */

import type { AuditIssue, CategoryScore, CheckResult } from '../../../types';
import { SCORING_CONFIG, CORRECT_TERMS, GENERIC_LAYER_NAMES } from '../config';
import { levenshteinDistance, extractNameValues } from '../utils';

// Figma type declarations for environments where global types aren't available (e.g., Jest)
type ChildrenMixin = { children: readonly SceneNode[] };
type ComponentPropertyDefinition = { type: string; defaultValue?: unknown; variantOptions?: string[] };

/**
 * Run all naming checks on a node
 */
export function checkNaming(node: SceneNode, issues: AuditIssue[]): CategoryScore {
  const checks: CheckResult[] = [];
  let passed = 0;
  let failed = 0;
  let warnings = 0;

  // Check 1: Component name format (Category / Type / Name)
  const nameFormatCheck = checkNameFormat(node.name);
  checks.push(nameFormatCheck);
  if (nameFormatCheck.passed) passed++; else failed++;
  if (!nameFormatCheck.passed) {
    issues.push({
      severity: 'warning',
      category: 'naming',
      message: nameFormatCheck.message,
      location: node.name,
      suggestion: 'Use format: Category / Type / Name (e.g., Button / Primary / Full)',
      autoFixable: false
    });
  }

  // Check 2: No typos in common words
  const typoCheck = checkCommonTypos(node.name);
  checks.push(typoCheck);
  if (typoCheck.passed) passed++; else { failed++; warnings++; }
  if (!typoCheck.passed) {
    issues.push({
      severity: 'error',
      category: 'naming',
      message: typoCheck.message,
      location: typoCheck.field ? `Property: ${typoCheck.field}` : node.name,
      suggestion: typoCheck.field
        ? `Rename property "${typoCheck.field}" to fix the typo`
        : 'Fix typo: ' + typoCheck.message,
      autoFixable: true
    });
  }

  // Check 3: Layer names are semantic
  if ('children' in node) {
    const layerNameCheck = checkLayerNames(node);
    checks.push(layerNameCheck);
    if (layerNameCheck.passed) passed++; else warnings++;
    if (!layerNameCheck.passed) {
      issues.push({
        severity: 'info',
        category: 'naming',
        message: layerNameCheck.message,
        location: 'Child layers',
        suggestion: 'Use semantic names: Title, Icon, Container instead of Text 1, Frame 2',
        autoFixable: false
      });
    }
  }

  // Check 4: Variant property names are PascalCase
  if (node.type === 'COMPONENT_SET') {
    const variantNamingCheck = checkVariantNaming(node);
    checks.push(variantNamingCheck);
    if (variantNamingCheck.passed) passed++; else warnings++;
  }

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
 * Check component name follows Category / Type format
 */
export function checkNameFormat(name: string): CheckResult {
  // Variant names use "Property=Value" format - these are VALID
  if (name.includes('=')) {
    return {
      name: 'Component name format',
      passed: true,
      message: 'Variant uses Property=Value format (correct)'
    };
  }

  // For component/component set names: Expected "Category / Type" or "Category / Type / Name"
  const parts = name.split('/').map(p => p.trim());
  const hasProperFormat = parts.length >= 2 && parts.every(p => p.length > 0);

  // Single-word names like "Button", "Icon", "Card" are valid
  const isSingleWord = parts.length === 1 && parts[0].length > 0 && !parts[0].includes(' ');

  if (isSingleWord) {
    return {
      name: 'Component name format',
      passed: true,
      message: `Single-word name "${name}" is valid (consider Category / Type for better organization)`,
      severity: undefined
    };
  }

  return {
    name: 'Component name format',
    passed: hasProperFormat,
    message: hasProperFormat
      ? 'Name follows Category / Type format'
      : `Name "${name}" should follow Category / Type format`,
    severity: hasProperFormat ? undefined : 'warning'
  };
}

/**
 * Check for common typos using fuzzy matching
 */
export function checkCommonTypos(name: string): CheckResult & { field?: string } {
  const values = extractNameValues(name);

  // Check each value against the dictionary using Levenshtein distance
  for (const { value, field } of values) {
    const lowerValue = value.toLowerCase();

    // First check if value is an exact match to ANY dictionary term
    const isExactMatchInDictionary = CORRECT_TERMS.some(
      term => term.toLowerCase() === lowerValue
    );
    if (isExactMatchInDictionary) {
      continue; // Valid term, skip typo checking
    }

    for (const correct of CORRECT_TERMS) {
      const lowerCorrect = correct.toLowerCase();

      // Only check similar length words
      const lengthDiff = Math.abs(value.length - correct.length);
      if (lengthDiff > 2) continue;

      // Calculate edit distance
      const distance = levenshteinDistance(lowerValue, lowerCorrect);

      // Distance 1-2 suggests a typo
      const threshold = value.length <= 4 ? 1 : 2;

      if (distance > 0 && distance <= threshold) {
        return {
          name: 'Typo check',
          passed: false,
          message: field !== 'name'
            ? `Typo in property "${field}": "${value}" → "${correct}"`
            : `Found typo: "${value}" should be "${correct}"`,
          severity: 'error',
          field: field !== 'name' ? field : undefined
        };
      }
    }
  }

  return {
    name: 'Typo check',
    passed: true,
    message: 'No typos detected'
  };
}

/**
 * Check that layer names are semantic (not generic like "Frame 1")
 */
export function checkLayerNames(node: SceneNode & ChildrenMixin): CheckResult {
  const problematicLayers: string[] = [];

  const checkChildren = (children: readonly SceneNode[]) => {
    for (const child of children) {
      // Check if name starts with generic type + number
      for (const generic of GENERIC_LAYER_NAMES) {
        if (child.name.match(new RegExp(`^${generic}\\s*\\d*$`, 'i'))) {
          problematicLayers.push(child.name);
          break;
        }
      }

      if ('children' in child) {
        checkChildren(child.children);
      }
    }
  };

  checkChildren(node.children);

  return {
    name: 'Semantic layer names',
    passed: problematicLayers.length === 0,
    message: problematicLayers.length === 0
      ? 'All layers have semantic names'
      : `Found generic layer names: ${problematicLayers.slice(0, 3).join(', ')}${problematicLayers.length > 3 ? '...' : ''}`,
    severity: problematicLayers.length > 0 ? 'info' : undefined
  };
}

/**
 * Check that variant property names use PascalCase
 */
export function checkVariantNaming(componentSet: ComponentSetNode): CheckResult {
  const propertyDefinitions = componentSet.componentPropertyDefinitions;
  const issues: string[] = [];

  for (const [propName, def] of Object.entries(propertyDefinitions) as [string, ComponentPropertyDefinition][]) {
    // Remove Figma's ID suffix
    const cleanName = propName.replace(/#\d+:\d+$/, '');

    // Check if PascalCase
    if (def.type === 'VARIANT') {
      if (!/^[A-Z][a-zA-Z0-9]*$/.test(cleanName)) {
        issues.push(cleanName);
      }
    }
  }

  return {
    name: 'Variant property naming',
    passed: issues.length === 0,
    message: issues.length === 0
      ? 'Variant properties use PascalCase'
      : `Properties should be PascalCase: ${issues.join(', ')}`,
    severity: issues.length > 0 ? 'warning' : undefined
  };
}
