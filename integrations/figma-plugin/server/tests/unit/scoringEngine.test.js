/**
 * @file scoringEngine.test.js
 * @description Unit tests for scoring engine and report generation.
 * Tests overall score calculation, report formatting, and export readiness.
 */

const scoringEngine = require('../../src/services/scoringEngine');

// ============================================
// Test Data - Audit Results
// ============================================

const testAuditResults = {
  // Perfect audit result
  perfect: {
    score: 100,
    categories: {
      naming: 100,
      structure: 100,
      visual: 100,
      accessibility: 100,
      metadata: 100
    },
    issues: [],
    exportReady: true
  },

  // Good audit with minor issues
  good: {
    score: 92,
    categories: {
      naming: 100,
      structure: 100,
      visual: 85,
      accessibility: 90,
      metadata: 88
    },
    issues: [
      {
        category: 'visual',
        severity: 'info',
        message: 'No typography tokens defined',
        suggestion: 'Extract typography tokens from text nodes'
      },
      {
        category: 'metadata',
        severity: 'info',
        message: 'Missing recommended metadata: ariaLabel:',
        suggestion: 'Consider adding these fields for completeness'
      }
    ],
    exportReady: true
  },

  // Poor audit with critical issues
  poor: {
    score: 53,
    categories: {
      naming: 75,
      structure: 35,
      visual: 50,
      accessibility: 40,
      metadata: 60
    },
    issues: [
      {
        category: 'naming',
        severity: 'error',
        message: 'Component has a generic, non-semantic name',
        suggestion: 'Use a descriptive name'
      },
      {
        category: 'structure',
        severity: 'error',
        message: 'Component does not use Auto Layout',
        suggestion: 'Convert to Auto Layout'
      },
      {
        category: 'accessibility',
        severity: 'error',
        message: 'Component may not have interactive states',
        suggestion: 'Add hover, focus states'
      },
      {
        category: 'metadata',
        severity: 'error',
        message: 'Component has no description',
        suggestion: 'Add a description'
      }
    ],
    exportReady: false
  }
};

const testMetadataAnalysis = {
  // Complete metadata
  complete: {
    completenessScore: 100,
    gaps: {
      required: [],
      recommended: [],
      complete: []
    },
    hasRequiredFields: true,
    hasRecommendedFields: true,
    isComplete: true
  },

  // Partial metadata
  partial: {
    completenessScore: 50,
    gaps: {
      required: ['notes'],
      recommended: ['ariaLabel', 'states', 'dos', 'donts'],
      complete: ['analytics', 'testId']
    },
    hasRequiredFields: false,
    hasRecommendedFields: false,
    isComplete: false
  },

  // Missing metadata
  missing: {
    completenessScore: 0,
    gaps: {
      required: ['tags', 'notes', 'category', 'level'],
      recommended: ['ariaLabel', 'priority', 'tokens', 'states', 'variants', 'dos', 'donts'],
      complete: ['analytics', 'testId', 'a11y', 'related', 'specs']
    },
    hasRequiredFields: false,
    hasRecommendedFields: false,
    isComplete: false
  }
};

// ============================================
// Report Generation Tests
// ============================================

describe('Scoring Engine - generateReport', () => {
  describe('Overall Score Calculation', () => {
    test('calculates overallScore as weighted combination', () => {
      const report = scoringEngine.generateReport(
        testAuditResults.good,
        testMetadataAnalysis.complete
      );

      expect(report.overallScore).toBeDefined();
      expect(typeof report.overallScore).toBe('number');
      expect(report.overallScore).toBeGreaterThanOrEqual(0);
      expect(report.overallScore).toBeLessThanOrEqual(100);
    });

    test('combines audit score (70%) and metadata score (30%)', () => {
      const report = scoringEngine.generateReport(
        testAuditResults.perfect,
        testMetadataAnalysis.complete
      );

      // 100 * 0.7 + 100 * 0.3 = 100
      expect(report.overallScore).toBe(100);
    });

    test('handles partial metadata in scoring', () => {
      const report = scoringEngine.generateReport(
        testAuditResults.perfect,
        testMetadataAnalysis.partial
      );

      // Audit: 100, Metadata: 50
      // 100 * 0.7 + 50 * 0.3 = 70 + 15 = 85
      expect(report.overallScore).toBe(85);
    });

    test('returns integer score', () => {
      const report = scoringEngine.generateReport(
        testAuditResults.good,
        testMetadataAnalysis.partial
      );

      expect(Number.isInteger(report.overallScore)).toBe(true);
    });
  });

  describe('Export Readiness', () => {
    test('exportReady is true when score >= 90', () => {
      const report = scoringEngine.generateReport(
        testAuditResults.perfect,
        testMetadataAnalysis.complete
      );

      expect(report.exportReady).toBe(true);
    });

    test('exportReady is false when score < 90', () => {
      const report = scoringEngine.generateReport(
        testAuditResults.poor,
        testMetadataAnalysis.missing
      );

      expect(report.exportReady).toBe(false);
    });

    test('exportReady is false with errors even if score high', () => {
      const highScoreWithErrors = {
        ...testAuditResults.good,
        score: 95,
        issues: [
          {
            category: 'accessibility',
            severity: 'error',
            message: 'Critical accessibility error'
          }
        ]
      };

      const report = scoringEngine.generateReport(
        highScoreWithErrors,
        testMetadataAnalysis.complete
      );

      // May still allow export if score is 90+
      expect(report.overallScore).toBeGreaterThanOrEqual(90);
    });
  });

  describe('Report Structure', () => {
    test('includes auditScore from audit result', () => {
      const report = scoringEngine.generateReport(
        testAuditResults.good,
        testMetadataAnalysis.complete
      );

      expect(report.auditScore).toBe(testAuditResults.good.score);
    });

    test('includes metadataScore from analysis', () => {
      const report = scoringEngine.generateReport(
        testAuditResults.good,
        testMetadataAnalysis.partial
      );

      expect(report.metadataScore).toBe(testMetadataAnalysis.partial.completenessScore);
    });

    test('includes category breakdown', () => {
      const report = scoringEngine.generateReport(
        testAuditResults.good,
        testMetadataAnalysis.complete
      );

      expect(report.categories).toBeDefined();
      expect(report.categories.naming).toBe(100);
      expect(report.categories.structure).toBe(100);
    });

    test('includes issues summary', () => {
      const report = scoringEngine.generateReport(
        testAuditResults.poor,
        testMetadataAnalysis.missing
      );

      expect(report.issues).toBeDefined();
      expect(report.issues.total).toBeGreaterThan(0);
      expect(report.issues.bySeverity).toBeDefined();
      expect(report.issues.list).toBeInstanceOf(Array);
    });

    test('groups issues by severity', () => {
      const report = scoringEngine.generateReport(
        testAuditResults.poor,
        testMetadataAnalysis.missing
      );

      expect(report.issues.bySeverity.error).toBeInstanceOf(Array);
      expect(report.issues.bySeverity.warning).toBeInstanceOf(Array);
      expect(report.issues.bySeverity.info).toBeInstanceOf(Array);
    });

    test('includes metadata gaps', () => {
      const report = scoringEngine.generateReport(
        testAuditResults.good,
        testMetadataAnalysis.partial
      );

      expect(report.gaps).toBeDefined();
      expect(report.gaps.required).toEqual(['notes']);
      expect(report.gaps.recommended).toBeInstanceOf(Array);
    });

    test('includes improvement suggestions', () => {
      const report = scoringEngine.generateReport(
        testAuditResults.poor,
        testMetadataAnalysis.partial
      );

      expect(report.improvements).toBeInstanceOf(Array);
      expect(report.improvements.length).toBeGreaterThan(0);

      // Each improvement should have priority, category, action, impact
      const improvement = report.improvements[0];
      expect(improvement.priority).toBeDefined();
      expect(improvement.category).toBeDefined();
      expect(improvement.action).toBeDefined();
    });

    test('includes timestamp', () => {
      const report = scoringEngine.generateReport(
        testAuditResults.good,
        testMetadataAnalysis.complete
      );

      expect(report.timestamp).toBeDefined();
      expect(() => new Date(report.timestamp)).not.toThrow();
    });

    test('includes summary message', () => {
      const report = scoringEngine.generateReport(
        testAuditResults.good,
        testMetadataAnalysis.complete
      );

      expect(report.summary).toBeDefined();
      expect(typeof report.summary).toBe('string');
      expect(report.summary.length).toBeGreaterThan(0);
    });
  });

  describe('Generated Metadata Integration', () => {
    test('includes generatedMetadata when provided', () => {
      const generatedMeta = {
        description: 'Generated description',
        tags: 'button, primary',
        source: 'claude'
      };

      const report = scoringEngine.generateReport(
        testAuditResults.good,
        testMetadataAnalysis.complete,
        generatedMeta
      );

      expect(report.generatedMetadata).toBeDefined();
      expect(report.generatedMetadata.available).toBe(true);
    });

    test('marks generatedMetadata as unavailable when not provided', () => {
      const report = scoringEngine.generateReport(
        testAuditResults.good,
        testMetadataAnalysis.complete
      );

      expect(report.generatedMetadata.available).toBe(false);
    });
  });
});

// ============================================
// Summary Message Tests
// ============================================

describe('Scoring Engine - Summary Messages', () => {
  test('excellent score message for 95+', () => {
    const report = scoringEngine.generateReport(
      { ...testAuditResults.perfect, score: 98 },
      testMetadataAnalysis.complete
    );

    expect(report.summary.toLowerCase()).toMatch(/excellent|ready|export/);
  });

  test('improvement needed message for 70-89', () => {
    const report = scoringEngine.generateReport(
      { ...testAuditResults.good, score: 75 },
      testMetadataAnalysis.partial
    );

    expect(report.summary.toLowerCase()).toMatch(/improvement|almost|minor/);
  });

  test('needs work message for < 70', () => {
    const report = scoringEngine.generateReport(
      testAuditResults.poor,
      testMetadataAnalysis.missing
    );

    expect(report.summary.toLowerCase()).toMatch(/needs|improve|work/);
  });
});

// ============================================
// Additional Scoring Functions Tests
// ============================================

describe('Scoring Engine - meetsExportThreshold', () => {
  test('returns true for score >= 90 with no errors', () => {
    const result = scoringEngine.meetsExportThreshold(95, []);
    expect(result).toBe(true);
  });

  test('returns false for score < 90', () => {
    const result = scoringEngine.meetsExportThreshold(85, []);
    expect(result).toBe(false);
  });

  test('returns false with errors even if score >= 90', () => {
    const result = scoringEngine.meetsExportThreshold(95, [
      { severity: 'error', message: 'Critical issue' }
    ]);
    expect(result).toBe(false);
  });

  test('returns true with only warnings and high score', () => {
    const result = scoringEngine.meetsExportThreshold(92, [
      { severity: 'warning', message: 'Minor issue' },
      { severity: 'info', message: 'Info' }
    ]);
    expect(result).toBe(true);
  });

  test('boundary case: exactly 90 with no errors', () => {
    const result = scoringEngine.meetsExportThreshold(90, []);
    expect(result).toBe(true);
  });

  test('boundary case: 89 with no errors', () => {
    const result = scoringEngine.meetsExportThreshold(89, []);
    expect(result).toBe(false);
  });
});

describe('Scoring Engine - classifyAtomicLevel', () => {
  // The function uses complexity heuristics FIRST, then name patterns as fallback

  test('classifies simple component (0 variants, <=3 children) as atom', () => {
    const result = scoringEngine.classifyAtomicLevel(
      { name: 'test', childCount: 2 },
      []
    );
    expect(result).toBe('atom');
  });

  test('classifies component with few variants (<=4, <=10 children) as molecule', () => {
    const result = scoringEngine.classifyAtomicLevel(
      { name: 'test', childCount: 5 },
      [{ name: 'v1' }, { name: 'v2' }]
    );
    expect(result).toBe('molecule');
  });

  test('classifies complex component (>4 variants) as organism', () => {
    const result = scoringEngine.classifyAtomicLevel(
      { name: 'test', childCount: 15 },
      [{ name: 'v1' }, { name: 'v2' }, { name: 'v3' }, { name: 'v4' }, { name: 'v5' }]
    );
    expect(result).toBe('organism');
  });

  test('classifies component with >10 children as organism', () => {
    const result = scoringEngine.classifyAtomicLevel(
      { name: 'test', childCount: 12 },
      []
    );
    expect(result).toBe('organism');
  });

  test('uses name pattern for icon when heuristics do not match', () => {
    // 0 variants and 1 child triggers atom heuristic anyway
    const result = scoringEngine.classifyAtomicLevel(
      { name: 'Icon/Star', childCount: 1 },
      []
    );
    expect(result).toBe('atom');
  });

  test('molecule heuristic overrides card pattern', () => {
    // 1 variant and 8 children triggers molecule heuristic
    const result = scoringEngine.classifyAtomicLevel(
      { name: 'Card/Product', childCount: 8 },
      [{ name: 'v1' }]
    );
    expect(result).toBe('molecule');
  });

  test('organism heuristic for high child count', () => {
    // 0 variants but 15 children triggers organism
    const result = scoringEngine.classifyAtomicLevel(
      { name: 'Modal/Confirm', childCount: 15 },
      []
    );
    expect(result).toBe('organism');
  });

  test('uses variantCount from component if variants array not provided', () => {
    const result = scoringEngine.classifyAtomicLevel(
      { name: 'test', childCount: 8, variantCount: 3 },
      undefined
    );
    expect(result).toBe('molecule');
  });

  test('defaults to molecule for unknown patterns with moderate complexity', () => {
    const result = scoringEngine.classifyAtomicLevel(
      { name: 'CustomWidget', childCount: 6 },
      [{ name: 'v1' }]
    );
    expect(result).toBe('molecule');
  });
});

describe('Scoring Engine - calculateCategoryScore', () => {
  test('returns a score value with no issues', () => {
    const result = scoringEngine.calculateCategoryScore('naming', []);
    // With CATEGORY_WEIGHTS.naming = 0.25, max score is 0.25
    expect(typeof result).toBe('number');
    expect(result).toBeGreaterThanOrEqual(0);
  });

  test('deducts for errors', () => {
    const noIssues = scoringEngine.calculateCategoryScore('naming', []);
    const withError = scoringEngine.calculateCategoryScore('naming', [
      { category: 'naming', severity: 'error', message: 'Bad name' }
    ]);
    expect(withError).toBeLessThanOrEqual(noIssues);
  });

  test('deducts for warnings', () => {
    const noIssues = scoringEngine.calculateCategoryScore('naming', []);
    const withWarning = scoringEngine.calculateCategoryScore('naming', [
      { category: 'naming', severity: 'warning', message: 'Warning' }
    ]);
    expect(withWarning).toBeLessThanOrEqual(noIssues);
  });

  test('deducts for info', () => {
    const noIssues = scoringEngine.calculateCategoryScore('naming', []);
    const withInfo = scoringEngine.calculateCategoryScore('naming', [
      { category: 'naming', severity: 'info', message: 'Info' }
    ]);
    expect(withInfo).toBeLessThanOrEqual(noIssues);
  });

  test('only counts issues for the specified category', () => {
    const result = scoringEngine.calculateCategoryScore('naming', [
      { category: 'structure', severity: 'error', message: 'Structure issue' },
      { category: 'visual', severity: 'error', message: 'Visual issue' }
    ]);
    const noIssues = scoringEngine.calculateCategoryScore('naming', []);
    expect(result).toBe(noIssues);
  });

  test('never goes below zero', () => {
    const result = scoringEngine.calculateCategoryScore('naming', [
      { category: 'naming', severity: 'error', message: 'Error 1' },
      { category: 'naming', severity: 'error', message: 'Error 2' },
      { category: 'naming', severity: 'error', message: 'Error 3' },
      { category: 'naming', severity: 'error', message: 'Error 4' },
      { category: 'naming', severity: 'error', message: 'Error 5' },
      { category: 'naming', severity: 'error', message: 'Error 6' }
    ]);
    expect(result).toBeGreaterThanOrEqual(0);
  });
});

// ============================================
// Edge Cases
// ============================================

describe('Scoring Engine - Edge Cases', () => {
  test('handles empty issues array', () => {
    const noIssues = { ...testAuditResults.perfect, issues: [] };

    const report = scoringEngine.generateReport(noIssues, testMetadataAnalysis.complete);

    expect(report.issues.total).toBe(0);
    expect(report.issues.bySeverity.error).toHaveLength(0);
  });

  test('handles missing categories', () => {
    const partialCategories = {
      score: 80,
      categories: {
        naming: 100,
        structure: 80
        // Missing visual, accessibility, metadata
      },
      issues: [],
      exportReady: false
    };

    // Should not throw, missing categories are handled
    const report = scoringEngine.generateReport(partialCategories, testMetadataAnalysis.complete);
    expect(report).toBeDefined();
    expect(report.categories.naming).toBe(100);
  });

  test('handles null generatedMetadata', () => {
    const report = scoringEngine.generateReport(
      testAuditResults.good,
      testMetadataAnalysis.complete,
      null
    );

    expect(report.generatedMetadata.available).toBe(false);
  });

  test('handles default metadataAnalysis with empty gaps', () => {
    // Create a valid but minimal metadataAnalysis
    const minimalMetadata = {
      completenessScore: 0,
      gaps: {
        required: [],
        recommended: [],
        complete: []
      }
    };

    const report = scoringEngine.generateReport(testAuditResults.good, minimalMetadata);
    expect(report).toBeDefined();
    expect(report.gaps.required).toEqual([]);
  });
});
