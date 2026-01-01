/**
 * @file componentAuditor.js
 * @description Runs quality audits on Figma components for atomic design compliance.
 *              Checks naming conventions, structure, visual tokens, accessibility, and metadata.
 * @related
 *   - ../index.js - Main server, calls runAudit() and analyzeMetadataGaps()
 *   - ./scoringEngine.js - Uses audit results for report generation
 *   - ../resources/SKILL.md - Metadata format specification
 * @created 2025-12-23
 */

/**
 * Scoring weights by category
 *
 * ALIGNMENT WITH CLIENT (ComponentAuditor.ts + ScoringEngine.ts):
 *
 * Client runLocalAudit() runs 5 categories:
 *   - naming (weight: 0.25 = consistency)
 *   - structure (weight: 0.20)
 *   - visual (weight: 0.25 = consistency)
 *   - accessibility (weight: 0.25)
 *   - variants (no explicit weight, uses default)
 *
 * Client ScoringEngine adds metadata (0.30) separately via MetadataGapAnalysis
 *
 * Server runs 5 categories (same as client runLocalAudit):
 *   - naming, structure, visual, accessibility, metadata
 *
 * For consistency, we use percentage-based weights (0-100 per category, then weighted average)
 */
const CATEGORY_WEIGHTS = {
  naming: 0.25,        // consistency weight from client
  structure: 0.20,     // structure weight from client
  visual: 0.25,        // consistency weight from client (same as naming)
  accessibility: 0.25, // accessibility weight from client
  metadata: 0.30       // metadata weight from ScoringEngine
};

// Sum of weights for normalization
const TOTAL_WEIGHT = Object.values(CATEGORY_WEIGHTS).reduce((a, b) => a + b, 0); // 1.25

/**
 * Classify component into atomic design level
 * This is the SINGLE SOURCE OF TRUTH for component classification
 * @param {Object} component - Component data
 * @returns {string} Level: 'atom', 'molecule', 'organism', or 'template'
 */
function classifyComponentLevel(component) {
  const name = (component?.name || '').toLowerCase();

  // Atoms: Basic building blocks
  if (/^(icon|button|input|label|badge|chip|avatar|divider|text|image|checkbox|radio|switch|spinner|progress)/i.test(name)) {
    return 'atom';
  }
  // Molecules: Simple combinations of atoms
  if (/^(card|form-field|list-item|menu-item|search|dropdown|select|tabs|tooltip|alert|toast|tag)/i.test(name)) {
    return 'molecule';
  }
  // Organisms: Complex UI sections
  if (/^(header|footer|sidebar|modal|dialog|form|table|nav|navigation|menu|accordion|carousel|gallery)/i.test(name)) {
    return 'organism';
  }
  // Templates: Page-level layouts
  if (/^(page|layout|template|view|screen|dashboard)/i.test(name)) {
    return 'template';
  }

  // Default to molecule if uncertain
  return 'molecule';
}

/**
 * Get destination path for export
 * @param {string} level - Atomic design level
 * @param {string} componentName - Name of the component
 * @returns {string} Destination path
 */
function getDestinationPath(level, componentName) {
  const folderMap = {
    'atom': 'atoms',
    'molecule': 'molecules',
    'organism': 'organisms',
    'template': 'templates'
  };
  const folder = folderMap[level] || 'molecules';

  // Clean component name
  let cleanName = componentName || 'Component';
  if (cleanName.includes('=') || cleanName.includes(',')) {
    cleanName = cleanName.split(/[=,]/)[0].trim();
  }
  cleanName = cleanName.replace(/[^a-zA-Z0-9]/g, '') || 'Component';

  return `src/components/${folder}/${cleanName}/`;
}

/**
 * Run a full audit on component data
 * @param {Object} componentData - Component data from plugin
 * @returns {Object} Audit result with scores and issues
 *
 * Returns:
 *   - score: Raw audit score (weighted average of 5 categories)
 *   - metadataCompletenessScore: Score from analyzeMetadataGaps (0-100)
 *   - combinedScore: Final score = (audit * 0.7) + (metadataCompleteness * 0.3)
 *   - categories: Individual category scores
 *   - issues: List of issues found
 *   - exportReady: true if combinedScore >= 90 and no errors
 */
function runAudit(componentData) {
  const { component, checks } = componentData;

  console.log('[AUDIT] componentData keys:', Object.keys(componentData || {}));
  console.log('[AUDIT] componentData.tokens:', componentData.tokens?.length || 'undefined');
  console.log('[AUDIT] component?.tokens:', component?.tokens?.length || 'undefined');

  // Tokens and variants can be at top level or inside component
  const tokens = componentData.tokens || component?.tokens || [];
  const variants = componentData.variants || component?.variants || [];

  console.log('[AUDIT] resolved tokens count:', tokens?.length || 0);
  console.log('[AUDIT] resolved variants count:', variants?.length || 0);

  const categories = {};
  const issues = [];

  // Run requested checks (default to all)
  const checksToRun = checks || ['naming', 'structure', 'visual', 'accessibility', 'metadata'];

  if (checksToRun.includes('naming')) {
    categories.naming = auditNaming(component, issues);
  }

  if (checksToRun.includes('structure')) {
    categories.structure = auditStructure(component, variants, issues);
  }

  if (checksToRun.includes('visual')) {
    categories.visual = auditVisual(tokens, issues);
  }

  if (checksToRun.includes('accessibility')) {
    categories.accessibility = auditAccessibility(component, tokens, issues, variants);
  }

  if (checksToRun.includes('metadata')) {
    categories.metadata = auditMetadata(component, issues);
  }

  // Calculate audit score (weighted average of categories)
  const auditScore = calculateOverallScore(categories);

  // Calculate metadata completeness score (same as analyzeMetadataGaps)
  // Pass the full componentData to preserve existingDescription
  const metadataAnalysis = analyzeMetadataGaps(componentData);
  const metadataCompletenessScore = metadataAnalysis.completenessScore;

  // Calculate combined score: audit (70%) + metadata completeness (30%)
  const combinedScore = Math.round((auditScore * 0.7) + (metadataCompletenessScore * 0.3));

  // Check for blocking errors
  const hasErrors = issues.some(i => i.severity === 'error');

  // Classify component level (SINGLE SOURCE OF TRUTH)
  const level = classifyComponentLevel(component);
  const destinationPath = getDestinationPath(level, component?.name);

  return {
    score: auditScore,                          // Raw audit score (backward compat)
    metadataCompletenessScore,                  // Metadata gaps score
    combinedScore,                              // Final unified score
    categories,
    issues,
    gaps: metadataAnalysis.gaps,                // Include gap details
    exportReady: combinedScore >= 90 && !hasErrors,
    level,                                      // Atomic design level (atom/molecule/organism/template)
    destinationPath                             // Export destination path
  };
}

/**
 * Audit component naming
 * Returns score 0-100 (percentage)
 *
 * ALIGNED WITH CLIENT: ComponentAuditor.ts checkNaming()
 * - Checks for "Category / Type" format (slashes)
 * - Checks for common typos
 * - Less strict than before - allows spaces in names
 */
function auditNaming(component, issues) {
  let score = 100; // Start at 100%
  const name = component.name || '';

  // Check for proper naming format: "Category / Type" or "Category / Type / Name"
  // This matches the client's checkNameFormat()
  const parts = name.split('/').map(p => p.trim());
  const hasProperFormat = parts.length >= 2 && parts.every(p => p.length > 0);

  if (!hasProperFormat) {
    score -= 15;
    issues.push({
      category: 'naming',
      severity: 'warning',
      message: `Component name "${name}" should follow Category / Type format`,
      suggestion: 'Use format: Category / Type / Name (e.g., Button / Primary / Full)'
    });
  }

  // Check for common typos (matches client's checkCommonTypos)
  const typos = {
    'defult': 'Default', 'defulat': 'Default', 'defualt': 'Default',
    'hove': 'Hover', 'hovr': 'Hover',
    'diabled': 'Disabled', 'disbaled': 'Disabled',
    'lable': 'Label', 'buton': 'Button', 'buttn': 'Button',
    'primay': 'Primary', 'secndary': 'Secondary', 'secondry': 'Secondary',
    'focued': 'Focused', 'actve': 'Active'
  };

  const lowerName = name.toLowerCase();
  for (const [typo, correct] of Object.entries(typos)) {
    if (lowerName.includes(typo)) {
      score -= 20;
      issues.push({
        category: 'naming',
        severity: 'error',
        message: `Found typo: "${typo}" should be "${correct}"`,
        suggestion: `Fix typo in component name`
      });
      break; // Only report first typo
    }
  }

  // Check for generic/non-semantic names
  const genericNames = ['component', 'item', 'element', 'thing', 'box', 'untitled'];
  const baseName = name.split('/').pop().toLowerCase().trim();
  if (genericNames.includes(baseName)) {
    score -= 25;
    issues.push({
      category: 'naming',
      severity: 'error',
      message: 'Component has a generic, non-semantic name',
      suggestion: 'Use a descriptive name that indicates purpose'
    });
  }

  return Math.max(0, score);
}

/**
 * Audit component structure
 * Returns score 0-100 (percentage)
 */
function auditStructure(component, variants, issues) {
  let score = 100; // Start at 100%

  // Check variant count
  if (component.type === 'COMPONENT_SET') {
    if (!variants || variants.length === 0) {
      score -= 25;
      issues.push({
        category: 'structure',
        severity: 'warning',
        message: 'Component set has no variants',
        suggestion: 'Add at least one variant'
      });
    }
  }

  // Check for Auto Layout (indicated by having layout properties)
  if (!component.hasAutoLayout) {
    score -= 40;
    issues.push({
      category: 'structure',
      severity: 'error',
      message: 'Component does not use Auto Layout',
      suggestion: 'Convert to Auto Layout for responsive behavior'
    });
  }

  // Check for proper hierarchy (at least some structure)
  if (component.childCount !== undefined && component.childCount === 0) {
    score -= 25;
    issues.push({
      category: 'structure',
      severity: 'warning',
      message: 'Component has no child elements',
      suggestion: 'Add child elements to build component structure'
    });
  }

  return Math.max(0, score);
}

/**
 * Audit visual properties
 * Returns score 0-100 (percentage)
 *
 * ALIGNED WITH CLIENT: ComponentAuditor.ts checkVisual()
 * - Tokens use 'category' field (not 'type')
 * - Less strict penalties - having tokens is good
 */
function auditVisual(tokens, issues) {
  let score = 100; // Start at 100%

  if (!tokens || tokens.length === 0) {
    score -= 30;
    issues.push({
      category: 'visual',
      severity: 'warning',
      message: 'No design tokens detected',
      suggestion: 'Use design tokens for colors, spacing, and typography'
    });
    return Math.max(0, score);
  }

  // Log token categories for debugging
  const categories = tokens.map(t => t.category || t.type || 'unknown');
  console.log('[AUDIT VISUAL] Token categories:', [...new Set(categories)]);

  // Check for color tokens (tokens use 'category' field, not 'type')
  const colorTokens = tokens.filter(t => t.category === 'color' || t.type === 'color');
  console.log('[AUDIT VISUAL] Color tokens:', colorTokens.length);
  if (colorTokens.length === 0) {
    score -= 10;
    issues.push({
      category: 'visual',
      severity: 'info',
      message: 'No color tokens defined',
      suggestion: 'Extract color tokens from component fills and strokes'
    });
  }

  // Check for typography tokens
  const typographyTokens = tokens.filter(t =>
    t.category === 'typography' || t.type === 'typography' ||
    t.category === 'fontSize' || t.category === 'fontFamily'
  );
  console.log('[AUDIT VISUAL] Typography tokens:', typographyTokens.length);
  if (typographyTokens.length === 0) {
    score -= 10;
    issues.push({
      category: 'visual',
      severity: 'info',
      message: 'No typography tokens defined',
      suggestion: 'Extract typography tokens from text nodes'
    });
  }

  // Check for spacing/radius tokens
  const spacingTokens = tokens.filter(t =>
    t.category === 'spacing' || t.type === 'spacing' ||
    t.category === 'borderRadius' || t.category === 'padding'
  );
  console.log('[AUDIT VISUAL] Spacing tokens:', spacingTokens.length);
  if (spacingTokens.length === 0) {
    score -= 10;
    issues.push({
      category: 'visual',
      severity: 'info',
      message: 'No spacing tokens defined',
      suggestion: 'Extract spacing tokens from padding and gaps'
    });
  }

  console.log('[AUDIT VISUAL] Final score:', score);

  return Math.max(0, score);
}

/**
 * Audit accessibility
 * Returns score 0-100 (percentage)
 */
function auditAccessibility(component, tokens, issues, variants) {
  let score = 100; // Start at 100%

  // Check for specific required states by examining variant names
  const variantNames = (variants || []).map(v =>
    (v.name || '').toLowerCase()
  ).join(' ');

  // Also check component properties for state definitions
  const propertyNames = (component.properties || []).map(p =>
    (p.name || p || '').toLowerCase()
  ).join(' ');

  const stateContext = variantNames + ' ' + propertyNames;

  console.log('[AUDIT A11Y] Variant names:', variantNames.substring(0, 200));
  console.log('[AUDIT A11Y] Property names:', propertyNames);

  // Check for required interactive states
  const hasHover = stateContext.includes('hover');
  const hasFocus = stateContext.includes('focus');
  const hasDisabled = stateContext.includes('disabled');

  console.log('[AUDIT A11Y] Has hover:', hasHover, 'focus:', hasFocus, 'disabled:', hasDisabled);

  if (!hasHover) {
    score -= 10;
    issues.push({
      category: 'accessibility',
      severity: 'warning',
      message: 'Missing Hover state',
      suggestion: 'Add a hover state variant for mouse interaction feedback'
    });
  }

  if (!hasFocus) {
    score -= 15;
    issues.push({
      category: 'accessibility',
      severity: 'error',
      message: 'Missing Focus state - required for keyboard navigation',
      suggestion: 'Add a focus state variant for keyboard accessibility'
    });
  }

  if (!hasDisabled) {
    score -= 10;
    issues.push({
      category: 'accessibility',
      severity: 'warning',
      message: 'Missing Disabled state',
      suggestion: 'Add a disabled state variant to indicate non-interactive state'
    });
  }

  // Check for minimum touch target size (if dimensions available)
  if (component.width && component.height) {
    const minTouchTarget = 44;
    if (component.width < minTouchTarget || component.height < minTouchTarget) {
      score -= 25;
      issues.push({
        category: 'accessibility',
        severity: 'warning',
        message: `Touch target size (${component.width}x${component.height}px) is below 44x44px minimum`,
        suggestion: 'Increase size or add padding for touch accessibility'
      });
    }
  }

  // Check color contrast (if color tokens available)
  if (tokens) {
    const colorTokens = tokens.filter(t => t.type === 'color');
    // Simple check: warn if very light colors used (might have contrast issues)
    const lightColors = colorTokens.filter(t => {
      if (!t.value) return false;
      const hex = t.value.replace('#', '');
      const r = parseInt(hex.substr(0, 2), 16);
      const g = parseInt(hex.substr(2, 2), 16);
      const b = parseInt(hex.substr(4, 2), 16);
      const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
      return luminance > 0.9;
    });

    if (lightColors.length > 0) {
      score -= 15;
      issues.push({
        category: 'accessibility',
        severity: 'info',
        message: 'Very light colors detected - verify contrast ratios',
        suggestion: 'Ensure 4.5:1 contrast ratio for text, 3:1 for UI elements'
      });
    }
  }

  return Math.max(0, score);
}

/**
 * Audit metadata completeness
 * Returns score 0-100 (percentage)
 */
function auditMetadata(component, issues) {
  let score = 100; // Start at 100%
  const description = component.description || '';

  // Check for description
  if (!description || description.trim().length === 0) {
    score -= 40;
    issues.push({
      category: 'metadata',
      severity: 'error',
      message: 'Component has no description',
      suggestion: 'Add a description following the SKILL.md format'
    });
    return Math.max(0, score);
  }

  // Check for metadata separator
  if (!description.includes('---')) {
    score -= 25;
    issues.push({
      category: 'metadata',
      severity: 'warning',
      message: 'Description does not follow SKILL.md format',
      suggestion: 'Add structured metadata after --- separator'
    });
  }

  // Check for required fields
  const requiredFields = ['tags:', 'notes:', 'category:', 'level:'];
  const missingFields = requiredFields.filter(field => !description.includes(field));

  if (missingFields.length > 0) {
    score -= missingFields.length * 5;
    issues.push({
      category: 'metadata',
      severity: 'warning',
      message: `Missing required metadata fields: ${missingFields.join(', ')}`,
      suggestion: 'Add missing fields to component description'
    });
  }

  // Check for recommended fields
  const recommendedFields = ['ariaLabel:', 'states:', 'dos:', 'donts:'];
  const missingRecommended = recommendedFields.filter(field => !description.includes(field));

  if (missingRecommended.length > 0) {
    score -= missingRecommended.length * 3;
    issues.push({
      category: 'metadata',
      severity: 'info',
      message: `Missing recommended metadata: ${missingRecommended.join(', ')}`,
      suggestion: 'Consider adding these fields for completeness'
    });
  }

  return Math.max(0, score);
}

/**
 * Calculate overall weighted score
 * Each category returns a score 0-100 (percentage)
 * We apply category weights and calculate weighted average
 *
 * Formula matches client-side ScoringEngine.ts:
 *   weighted = sum(categoryScore * categoryWeight) / sum(weights)
 */
function calculateOverallScore(categories) {
  let weightedSum = 0;
  let totalWeight = 0;

  for (const [category, score] of Object.entries(categories)) {
    const weight = CATEGORY_WEIGHTS[category] || 0;
    weightedSum += score * weight;
    totalWeight += weight;
  }

  // Calculate weighted average (0-100)
  return totalWeight > 0 ? Math.round(weightedSum / totalWeight) : 0;
}

/**
 * Analyze metadata gaps against SKILL.md format
 * @updated 2025-12-25 - Fixed to return componentSetLevel and variantLevel
 */
function analyzeMetadataGaps(componentData) {
  const description = componentData.existingDescription || componentData.component?.description || '';
  const componentName = componentData.component?.name || 'Untitled';

  // Fields to check - aligned with UI expectations
  const requiredFields = ['description', 'tags', 'notes', 'category', 'level'];
  const recommendedFields = ['ariaLabel', 'priority', 'tokens', 'states', 'variants', 'dos', 'donts'];
  const completeFields = ['analytics', 'testId', 'a11y', 'related', 'specs'];

  const present = [];
  const missing = [];
  const incomplete = [];

  const gaps = {
    required: [],
    recommended: [],
    complete: []
  };

  // Check if description exists
  if (description && description.length > 0) {
    present.push('description');

    // Check for structured metadata (YAML-like format after ---)
    if (description.includes('---')) {
      // Check required fields
      requiredFields.forEach(field => {
        if (field === 'description') return; // Already checked
        if (description.includes(`${field}:`)) {
          present.push(field);
        } else {
          missing.push(field);
          gaps.required.push(field);
        }
      });

      // Check recommended fields
      recommendedFields.forEach(field => {
        if (description.includes(`${field}:`)) {
          present.push(field);
        } else {
          gaps.recommended.push(field);
        }
      });

      // Check complete fields
      completeFields.forEach(field => {
        if (description.includes(`${field}:`)) {
          present.push(field);
        } else {
          gaps.complete.push(field);
        }
      });
    } else {
      // Has description but no structured metadata
      incomplete.push('description (missing structured metadata)');
      missing.push('tags', 'notes', 'category', 'level');
      gaps.required = ['tags', 'notes', 'category', 'level'];
      gaps.recommended = [...recommendedFields];
      gaps.complete = [...completeFields];
    }
  } else {
    // No description at all
    missing.push('description', 'tags', 'notes', 'category', 'level');
    gaps.required = ['description', 'tags', 'notes', 'category', 'level'];
    gaps.recommended = [...recommendedFields];
    gaps.complete = [...completeFields];
  }

  // Check variants (from componentData)
  let totalVariants = 0;
  let variantsWithDesc = 0;
  const variantsMissingDesc = [];

  const variants = componentData.variants || componentData.component?.variants || [];
  if (variants.length > 0) {
    variants.forEach(v => {
      totalVariants++;
      if (v.description || v.hasDescription) {
        variantsWithDesc++;
      } else {
        variantsMissingDesc.push({
          name: v.name,
          nodeId: v.nodeId,
          properties: v.properties || {},
          hasDescription: false
        });
      }
    });
  }

  // Check properties (VARIANT type only - Size, Style, State, etc.)
  let totalProperties = 0;
  let propertiesWithDesc = 0;
  const propertiesMissingDesc = [];

  const properties = componentData.component?.properties || [];
  if (properties.length > 0) {
    properties.forEach(p => {
      // Only count VARIANT type properties (not TEXT, BOOLEAN, etc.)
      if (p.type === 'VARIANT') {
        totalProperties++;
        const propName = p.name || '';
        // Check if property name is mentioned in description with a colon (structured metadata)
        if (description && description.includes(`${propName}:`)) {
          propertiesWithDesc++;
        } else {
          propertiesMissingDesc.push(propName);
        }
      }
    });
  }

  console.log('[METADATA] Properties analysis:', { totalProperties, propertiesWithDesc, propertiesMissingDesc });

  // Calculate completeness score - now includes accessibility metadata!
  const presentRequired = requiredFields.filter(f => present.includes(f)).length;
  const variantScore = totalVariants > 0 ? (variantsWithDesc / totalVariants) * 100 : 100;
  const fieldScore = (presentRequired / requiredFields.length) * 100;

  // FIX: Include accessibility metadata in the score calculation
  // Check all 4 accessibility items
  const hasAriaLabel = present.includes('ariaLabel');
  const hasA11yNotes = present.includes('a11y');
  const hasFocusStates = description.includes('states:') && /focus\s*:/i.test(description);
  const hasContrastInfo = description.includes('specs:') && /contrast\s*:/i.test(description);
  const a11yCount = [hasAriaLabel, hasA11yNotes, hasFocusStates, hasContrastInfo].filter(Boolean).length;
  const accessibilityScore = (a11yCount / 4) * 100;

  // New formula: fields (50%) + variants (30%) + accessibility (20%)
  const completenessScore = Math.round((fieldScore * 0.5) + (variantScore * 0.3) + (accessibilityScore * 0.2));

  return {
    componentName,
    completenessScore,
    // Structure expected by UI (aligned with client ComponentAuditor.ts)
    componentSetLevel: {
      present,
      missing,
      incomplete
    },
    variantLevel: {
      total: totalVariants,
      withDescription: variantsWithDesc,
      missingDescription: variantsMissingDesc
    },
    propertyLevel: {
      total: totalProperties,
      withDescription: propertiesWithDesc,
      missingDescription: propertiesMissingDesc
    },
    accessibilityMetadata: {
      // Use the values already calculated for the score
      hasAriaLabel,
      hasA11yNotes,
      hasFocusStates,
      hasContrastInfo
    },
    // Keep original gaps structure for scoring engine
    gaps,
    hasRequiredFields: gaps.required.length === 0,
    hasRecommendedFields: gaps.recommended.length === 0,
    isComplete: gaps.required.length === 0 && gaps.recommended.length === 0 && gaps.complete.length === 0
  };
}

module.exports = {
  runAudit,
  analyzeMetadataGaps,
  classifyComponentLevel,    // Single source of truth for level classification
  getDestinationPath,        // Single source of truth for export path
  CATEGORY_WEIGHTS
};
