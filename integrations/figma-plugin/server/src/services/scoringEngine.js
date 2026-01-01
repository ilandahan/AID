/**
 * @file scoringEngine.js
 * @description Generates quality reports and calculates weighted scores for components.
 *              Combines audit results with metadata analysis for comprehensive reporting.
 * @related
 *   - ../index.js - Main server, calls generateReport()
 *   - ./componentAuditor.js - Provides audit results and CATEGORY_WEIGHTS
 *   - ./metadataGenerator.js - Provides generated metadata for reports
 * @created 2025-12-23
 */

const { CATEGORY_WEIGHTS } = require('./componentAuditor');

/**
 * Generate a comprehensive quality report
 * @param {Object} auditResult - Result from componentAuditor.runAudit()
 * @param {Object} metadataAnalysis - Result from analyzeMetadataGaps() (optional, now included in auditResult)
 * @param {Object} generatedMetadata - Optional generated metadata from Claude
 * @param {Object} componentData - Original component data for context
 * @returns {Object} Complete quality report
 *
 * Note: auditResult now includes combinedScore, metadataCompletenessScore, and gaps
 * from the unified scoring in componentAuditor.runAudit()
 */
function generateReport(auditResult, metadataAnalysis, generatedMetadata = null, componentData = null) {
  const { score, categories, issues, combinedScore: auditCombinedScore, metadataCompletenessScore, gaps: auditGaps } = auditResult;

  // Debug logging
  console.log('[SCORING] auditResult.score:', score);
  console.log('[SCORING] auditResult.metadataCompletenessScore:', metadataCompletenessScore);
  console.log('[SCORING] metadataAnalysis:', metadataAnalysis ? JSON.stringify(metadataAnalysis).substring(0, 100) : 'null');
  console.log('[SCORING] metadataAnalysis?.completenessScore:', metadataAnalysis?.completenessScore);

  // Use metadata analysis from passed parameter first (more reliable), then auditResult
  // Note: auditResult.metadataCompletenessScore may be 0 if existingDescription wasn't passed to runAudit
  const completenessScore = metadataAnalysis?.completenessScore !== undefined
    ? metadataAnalysis.completenessScore
    : (metadataCompletenessScore || 0);

  console.log('[SCORING] Using completenessScore:', completenessScore);

  const gaps = auditGaps || metadataAnalysis?.gaps || { required: [], recommended: [], complete: [] };

  // Always recalculate combined score using the correct completenessScore
  // (auditCombinedScore may be based on stale metadataCompletenessScore)
  const combinedScore = Math.round((score * 0.7) + (completenessScore * 0.3));
  console.log('[SCORING] Combined score:', score, '* 0.7 +', completenessScore, '* 0.3 =', combinedScore);

  // Group issues by severity
  const issuesBySeverity = {
    error: issues.filter(i => i.severity === 'error'),
    warning: issues.filter(i => i.severity === 'warning'),
    info: issues.filter(i => i.severity === 'info')
  };

  // Group issues by category
  const issuesByCategory = {
    naming: issues.filter(i => i.category === 'naming'),
    structure: issues.filter(i => i.category === 'structure'),
    visual: issues.filter(i => i.category === 'visual'),
    accessibility: issues.filter(i => i.category === 'accessibility'),
    metadata: issues.filter(i => i.category === 'metadata')
  };

  // Generate improvement suggestions
  const improvements = generateImprovements(issues, gaps);

  // Determine export readiness (same logic as componentAuditor)
  const exportReady = combinedScore >= 90 && issuesBySeverity.error.length === 0;

  // Build strengths and weaknesses for Style Guide Implementation
  const styleGuideEval = buildStyleGuideEvaluation(categories, issues, issuesByCategory, componentData);

  // Build metadata accessibility evaluation
  const metadataEval = buildMetadataEvaluation(completenessScore, gaps, componentData);

  // Generate formatted markdown report
  const formattedReport = generateFormattedReport({
    componentName: componentData?.component?.name || 'Component',
    styleGuideScore: score,
    metadataScore: completenessScore,
    combinedScore,
    styleGuideEval,
    metadataEval,
    improvements,
    exportReady
  });

  return {
    overallScore: combinedScore,
    auditScore: score,
    metadataScore: completenessScore,
    exportReady,
    categories: {
      ...categories,
      metadataCompleteness: completenessScore  // Separate from category metadata score
    },
    issues: {
      total: issues.length,
      bySeverity: issuesBySeverity,
      byCategory: issuesByCategory,
      list: issues
    },
    gaps: {
      required: gaps.required,
      recommended: gaps.recommended,
      complete: gaps.complete
    },
    improvements,
    styleGuideEvaluation: styleGuideEval,
    metadataEvaluation: metadataEval,
    generatedMetadata: generatedMetadata ? {
      available: true,
      description: generatedMetadata.description,
      formattedDescription: generatedMetadata.formattedDescription
    } : {
      available: false
    },
    formattedReport,
    summary: generateSummary(combinedScore, issues, gaps, exportReady),
    timestamp: new Date().toISOString()
  };
}

/**
 * Build Style Guide Implementation evaluation (strengths & weaknesses)
 */
function buildStyleGuideEvaluation(categories, issues, issuesByCategory, componentData) {
  const strengths = [];
  const weaknesses = [];

  // Check naming
  if (categories.naming >= 90) {
    strengths.push('Clear naming convention following Category/Type/Name format');
  } else if (categories.naming >= 70) {
    strengths.push('Generally good naming structure');
  }
  if (issuesByCategory.naming.length > 0) {
    issuesByCategory.naming.forEach(issue => {
      weaknesses.push(issue.message);
    });
  }

  // Check structure
  if (categories.structure >= 90) {
    strengths.push('Excellent Auto Layout structure for responsive design');
  } else if (categories.structure >= 70) {
    strengths.push('Good component structure with Auto Layout');
  }
  if (issuesByCategory.structure.length > 0) {
    issuesByCategory.structure.forEach(issue => {
      weaknesses.push(issue.message);
    });
  }

  // Check visual consistency
  if (categories.visual >= 90) {
    strengths.push('Consistent use of design tokens for colors and typography');
  } else if (categories.visual >= 70) {
    strengths.push('Generally consistent visual styling');
  }
  if (issuesByCategory.visual.length > 0) {
    issuesByCategory.visual.forEach(issue => {
      weaknesses.push(issue.message);
    });
  }

  // Check accessibility
  if (categories.accessibility >= 90) {
    strengths.push('Comprehensive accessibility states (Focus, Disabled)');
  } else if (categories.accessibility >= 70) {
    strengths.push('Basic accessibility support');
  }
  if (issuesByCategory.accessibility.length > 0) {
    issuesByCategory.accessibility.forEach(issue => {
      weaknesses.push(issue.message);
    });
  }

  // Check variants if available
  const variantCount = componentData?.variants?.length || componentData?.component?.variantCount || 0;
  if (variantCount > 0) {
    strengths.push(`Well-structured variants (${variantCount} variations)`);
  }

  // Check tokens if available
  const tokenCount = componentData?.tokens?.length || 0;
  if (tokenCount >= 3) {
    strengths.push(`Design tokens extracted (${tokenCount} tokens)`);
  }

  return { strengths, weaknesses, score: Math.round(Object.values(categories).reduce((a, b) => a + b, 0) / Object.values(categories).length) || 0 };
}

/**
 * Build Metadata Accessibility evaluation (checklist)
 */
function buildMetadataEvaluation(completenessScore, gaps, componentData) {
  const present = [];
  const missing = [];

  // Required fields check
  const requiredFields = ['tags', 'notes', 'category', 'level'];
  const recommendedFields = ['ariaLabel', 'priority', 'tokens', 'states', 'variants', 'dos', 'donts'];
  const completeFields = ['analytics', 'testId', 'a11y', 'related', 'specs'];

  // Check what's present vs missing from gaps
  const allMissing = [...(gaps.required || []), ...(gaps.recommended || []), ...(gaps.complete || [])];
  const allFields = [...requiredFields, ...recommendedFields, ...completeFields];

  allFields.forEach(field => {
    if (allMissing.includes(field)) {
      missing.push(field);
    } else {
      present.push(field);
    }
  });

  // Check description
  if (componentData?.component?.description) {
    present.push('description');
  } else {
    missing.push('description');
  }

  return {
    score: completenessScore,
    present,
    missing,
    requiredComplete: requiredFields.filter(f => !gaps.required?.includes(f)),
    requiredMissing: gaps.required || [],
    recommendedComplete: recommendedFields.filter(f => !gaps.recommended?.includes(f)),
    recommendedMissing: gaps.recommended || []
  };
}

/**
 * Generate formatted markdown report
 */
function generateFormattedReport(data) {
  const { componentName, styleGuideScore, metadataScore, combinedScore, styleGuideEval, metadataEval, improvements, exportReady } = data;

  // Determine emoji for scores
  const getScoreEmoji = (score) => {
    if (score >= 90) return '🌟';
    if (score >= 70) return '✅';
    if (score >= 50) return '⚠️';
    return '❌';
  };

  let report = `---

## 🎯 Component Evaluation: ${componentName}

### 1️⃣ Style Guide Implementation: **${styleGuideScore}/100** ${getScoreEmoji(styleGuideScore)}

**Strengths:**
${styleGuideEval.strengths.map(s => `- ✅ ${s}`).join('\n') || '- No major strengths identified'}

**Weaknesses:**
${styleGuideEval.weaknesses.map(w => `- ⚠️ ${w}`).join('\n') || '- No weaknesses found'}

---

### 2️⃣ LLM Metadata Accessibility: **${metadataScore}/100** ${getScoreEmoji(metadataScore)}

**Present:**
${metadataEval.present.map(p => `- ✅ ${p}`).join('\n') || '- None'}

**Missing:**
${metadataEval.missing.map(m => `- ❌ ${m}`).join('\n') || '- None - Excellent documentation!'}

---

## 📊 Final Weighted Score

| Criterion | Score | Weight | Contribution |
|-----------|-------|--------|--------------|
| Style Guide Implementation | **${styleGuideScore}** | 70% | ${(styleGuideScore * 0.7).toFixed(1)} |
| LLM Metadata Accessibility | **${metadataScore}** | 30% | ${(metadataScore * 0.3).toFixed(1)} |
| **Total Weighted** | | | **${combinedScore}/100** |

**Export Status:** ${exportReady ? '✅ Ready for export' : '⚠️ Needs improvement before export'}

---

### 💡 Recommendations for Improvement:

${improvements.slice(0, 5).map((imp, i) => `${i + 1}. **${imp.action}** - ${imp.impact}`).join('\n') || 'No recommendations - component is ready!'}

---`;

  return report;
}

/**
 * Generate improvement suggestions based on issues and gaps
 */
function generateImprovements(issues, gaps) {
  const improvements = [];

  // Priority 1: Fix errors
  const errors = issues.filter(i => i.severity === 'error');
  errors.forEach(error => {
    improvements.push({
      priority: 'high',
      category: error.category,
      action: error.suggestion,
      impact: 'Required for export'
    });
  });

  // Priority 2: Add required metadata
  gaps.required.forEach(field => {
    improvements.push({
      priority: 'high',
      category: 'metadata',
      action: `Add required field: ${field}`,
      impact: 'Required for SKILL.md compliance'
    });
  });

  // Priority 3: Fix warnings
  const warnings = issues.filter(i => i.severity === 'warning');
  warnings.forEach(warning => {
    improvements.push({
      priority: 'medium',
      category: warning.category,
      action: warning.suggestion,
      impact: 'Improves quality score'
    });
  });

  // Priority 4: Add recommended metadata
  gaps.recommended.forEach(field => {
    improvements.push({
      priority: 'low',
      category: 'metadata',
      action: `Add recommended field: ${field}`,
      impact: 'Improves documentation'
    });
  });

  return improvements;
}

/**
 * Generate a human-readable summary
 */
function generateSummary(score, issues, gaps, exportReady) {
  const errorCount = issues.filter(i => i.severity === 'error').length;
  const warningCount = issues.filter(i => i.severity === 'warning').length;

  let status;
  if (exportReady) {
    status = 'Ready for export';
  } else if (score >= 80) {
    status = 'Almost ready - minor improvements needed';
  } else if (score >= 60) {
    status = 'Needs improvement';
  } else {
    status = 'Significant work required';
  }

  const parts = [
    `Score: ${score}/100 - ${status}`,
    errorCount > 0 ? `${errorCount} error(s) to fix` : null,
    warningCount > 0 ? `${warningCount} warning(s) to address` : null,
    gaps.required.length > 0 ? `Missing required metadata: ${gaps.required.join(', ')}` : null
  ].filter(Boolean);

  return parts.join('. ');
}

/**
 * Calculate score for a single category
 */
function calculateCategoryScore(categoryName, issues) {
  const maxScore = CATEGORY_WEIGHTS[categoryName] || 20;
  const categoryIssues = issues.filter(i => i.category === categoryName);

  let deductions = 0;
  categoryIssues.forEach(issue => {
    switch (issue.severity) {
      case 'error':
        deductions += 5;
        break;
      case 'warning':
        deductions += 3;
        break;
      case 'info':
        deductions += 1;
        break;
    }
  });

  return Math.max(0, maxScore - deductions);
}

/**
 * Determine the atomic design level of a component
 */
function classifyAtomicLevel(component, variants) {
  const name = (component.name || '').toLowerCase();
  const variantCount = variants?.length || component.variantCount || 0;
  const childCount = component.childCount || 0;

  // Heuristics for classification
  if (variantCount === 0 && childCount <= 3) {
    return 'atom';
  }

  if (variantCount <= 4 && childCount <= 10) {
    return 'molecule';
  }

  if (variantCount > 4 || childCount > 10) {
    return 'organism';
  }

  // Name-based hints
  const atomPatterns = /^(icon|button|input|label|badge|chip|avatar|divider)/i;
  const moleculePatterns = /^(card|form-field|list-item|menu-item|search|dropdown)/i;
  const organismPatterns = /^(header|footer|sidebar|modal|dialog|form|table|nav)/i;
  const templatePatterns = /^(page|layout|template|view)/i;

  if (templatePatterns.test(name)) return 'template';
  if (organismPatterns.test(name)) return 'organism';
  if (moleculePatterns.test(name)) return 'molecule';
  if (atomPatterns.test(name)) return 'atom';

  return 'molecule'; // Default
}

/**
 * Check if component meets export threshold
 */
function meetsExportThreshold(score, issues) {
  const errorCount = issues.filter(i => i.severity === 'error').length;
  return score >= 90 && errorCount === 0;
}

module.exports = {
  generateReport,
  calculateCategoryScore,
  classifyAtomicLevel,
  meetsExportThreshold
};
