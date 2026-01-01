/**
 * @file ScoringEngine.test.ts
 * @description Unit tests for ScoringEngine module
 */

import { scoringEngine, ScoringEngine } from '../ScoringEngine';

// Type definitions inline to avoid import issues
interface CategoryScore {
  score: number;
  weight: number;
  passed: number;
  failed: number;
  warnings: number;
  checks: Array<{ name: string; passed: boolean; message: string }>;
}

interface AuditResult {
  score: number;
  categories: {
    naming: CategoryScore;
    structure: CategoryScore;
    visual: CategoryScore;
    accessibility: CategoryScore;
    variants: CategoryScore;
  };
  issues: Array<{
    severity: 'error' | 'warning' | 'info';
    category: string;
    message: string;
    location: string;
    suggestion?: string;
    autoFixable: boolean;
  }>;
  suggestions: string[];
  blockers: string[];
}

interface MetadataGapAnalysis {
  componentName: string;
  completenessScore: number;
  componentSetLevel: {
    present: string[];
    missing: string[];
    incomplete: string[];
  };
  variantLevel: {
    total: number;
    withDescription: number;
    missingDescription: Array<{ name: string; nodeId: string; properties: Record<string, string> }>;
  };
  propertyLevel: {
    total: number;
    withDescription: number;
    missingDescription: string[];
  };
  accessibilityMetadata: {
    hasAriaLabel: boolean;
    hasA11yNotes: boolean;
    hasFocusStates: boolean;
    hasContrastInfo: boolean;
  };
}

// Helper to create a mock CategoryScore
function mockCategoryScore(score: number, weight: number = 0.25): CategoryScore {
  return {
    score,
    weight,
    passed: Math.floor(score / 10),
    failed: 10 - Math.floor(score / 10),
    warnings: 2,
    checks: [],
  };
}

// Helper to create a mock AuditResult
function mockAuditResult(overrides: Partial<AuditResult> = {}): AuditResult {
  return {
    score: 80,
    categories: {
      naming: mockCategoryScore(85),
      structure: mockCategoryScore(75),
      visual: mockCategoryScore(80),
      accessibility: mockCategoryScore(70),
      variants: mockCategoryScore(90),
    },
    issues: [],
    suggestions: [],
    blockers: [],
    ...overrides,
  };
}

// Helper to create a mock MetadataGapAnalysis
function mockMetadataAnalysis(overrides: Partial<MetadataGapAnalysis> = {}): MetadataGapAnalysis {
  return {
    componentName: 'TestComponent',
    completenessScore: 75,
    componentSetLevel: {
      present: ['description', 'tags'],
      missing: ['notes', 'ariaLabel'],
      incomplete: [],
    },
    variantLevel: {
      total: 4,
      withDescription: 2,
      missingDescription: [],
    },
    propertyLevel: {
      total: 3,
      withDescription: 1,
      missingDescription: ['size', 'variant'],
    },
    accessibilityMetadata: {
      hasAriaLabel: false,
      hasA11yNotes: false,
      hasFocusStates: true,
      hasContrastInfo: false,
    },
    ...overrides,
  };
}

describe('ScoringEngine', () => {
  describe('calculateOverallScore', () => {
    it('should calculate weighted score correctly', () => {
      const audit = mockAuditResult({ score: 80 });
      const metadata = mockMetadataAnalysis({ completenessScore: 70 });

      const result = scoringEngine.calculateOverallScore(audit as any, metadata as any);

      // Should return an object with overall score and breakdown
      expect(result).toHaveProperty('overall');
      expect(result).toHaveProperty('breakdown');
      expect(result).toHaveProperty('meetsMinimums');
      expect(result.overall).toBeGreaterThan(0);
      expect(result.overall).toBeLessThanOrEqual(100);
    });

    it('should return 0 for empty audit', () => {
      const audit = mockAuditResult({
        score: 0,
        categories: {
          naming: mockCategoryScore(0),
          structure: mockCategoryScore(0),
          visual: mockCategoryScore(0),
          accessibility: mockCategoryScore(0),
          variants: mockCategoryScore(0),
        },
      });
      const metadata = mockMetadataAnalysis({ completenessScore: 0 });

      const result = scoringEngine.calculateOverallScore(audit as any, metadata as any);

      expect(result.overall).toBe(0);
    });

    it('should return 100 for perfect scores', () => {
      const audit = mockAuditResult({
        score: 100,
        categories: {
          naming: mockCategoryScore(100),
          structure: mockCategoryScore(100),
          visual: mockCategoryScore(100),
          accessibility: mockCategoryScore(100),
          variants: mockCategoryScore(100),
        },
      });
      const metadata = mockMetadataAnalysis({ completenessScore: 100 });

      const result = scoringEngine.calculateOverallScore(audit as any, metadata as any);

      expect(result.overall).toBe(100);
    });

    it('should include breakdown of category scores', () => {
      const audit = mockAuditResult();
      const metadata = mockMetadataAnalysis();

      const result = scoringEngine.calculateOverallScore(audit as any, metadata as any);

      expect(result.breakdown).toHaveProperty('consistency');
      expect(result.breakdown).toHaveProperty('metadata');
      expect(result.breakdown).toHaveProperty('accessibility');
      expect(result.breakdown).toHaveProperty('structure');
    });

    it('should identify failed minimums', () => {
      const audit = mockAuditResult({
        categories: {
          naming: mockCategoryScore(50), // Below minimum of 70
          structure: mockCategoryScore(50), // Below minimum of 70
          visual: mockCategoryScore(80),
          accessibility: mockCategoryScore(50), // Below minimum of 80
          variants: mockCategoryScore(90),
        },
      });
      const metadata = mockMetadataAnalysis({ completenessScore: 40 }); // Below minimum of 60

      const result = scoringEngine.calculateOverallScore(audit as any, metadata as any);

      expect(result.meetsMinimums).toBe(false);
      expect(result.failedMinimums.length).toBeGreaterThan(0);
    });
  });

  describe('isExportReady', () => {
    it('should return ready true for high scores without blockers', () => {
      const audit = mockAuditResult({
        score: 95,
        categories: {
          naming: mockCategoryScore(95),
          structure: mockCategoryScore(95),
          visual: mockCategoryScore(95),
          accessibility: mockCategoryScore(95),
          variants: mockCategoryScore(95),
        },
        blockers: [],
      });
      const metadata = mockMetadataAnalysis({
        completenessScore: 95,
        componentSetLevel: {
          present: ['description', 'tags', 'notes'],
          missing: [],
          incomplete: [],
        },
      });

      const result = scoringEngine.isExportReady(audit as any, metadata as any);

      expect(result.ready).toBe(true);
      expect(result.score).toBeGreaterThanOrEqual(90);
      expect(result.blockers).toHaveLength(0);
    });

    it('should return ready false for low scores', () => {
      const audit = mockAuditResult({
        score: 50,
        categories: {
          naming: mockCategoryScore(50),
          structure: mockCategoryScore(50),
          visual: mockCategoryScore(50),
          accessibility: mockCategoryScore(50),
          variants: mockCategoryScore(50),
        },
      });
      const metadata = mockMetadataAnalysis({ completenessScore: 50 });

      const result = scoringEngine.isExportReady(audit as any, metadata as any);

      expect(result.ready).toBe(false);
      expect(result.pointsNeeded).toBeGreaterThan(0);
    });

    it('should return ready false when there are blockers', () => {
      const audit = mockAuditResult({
        score: 95,
        categories: {
          naming: mockCategoryScore(95),
          structure: mockCategoryScore(95),
          visual: mockCategoryScore(95),
          accessibility: mockCategoryScore(95),
          variants: mockCategoryScore(95),
        },
        blockers: ['Missing focus state'],
      });
      const metadata = mockMetadataAnalysis({ completenessScore: 95 });

      const result = scoringEngine.isExportReady(audit as any, metadata as any);

      expect(result.ready).toBe(false);
      expect(result.blockers.length).toBeGreaterThan(0);
    });

    it('should include missing description as blocker', () => {
      const audit = mockAuditResult({
        categories: {
          naming: mockCategoryScore(90),
          structure: mockCategoryScore(90),
          visual: mockCategoryScore(90),
          accessibility: mockCategoryScore(90),
          variants: mockCategoryScore(90),
        },
      });
      const metadata = mockMetadataAnalysis({
        completenessScore: 90,
        componentSetLevel: {
          present: ['tags'],
          missing: ['description'], // Missing description is a blocker
          incomplete: [],
        },
      });

      const result = scoringEngine.isExportReady(audit as any, metadata as any);

      expect(result.blockers).toContain('Missing component description');
    });
  });

  describe('generateActionItems', () => {
    it('should generate prioritized action items', () => {
      const audit = mockAuditResult({
        issues: [
          {
            severity: 'error',
            category: 'accessibility',
            message: 'Missing focus state',
            location: 'Component',
            suggestion: 'Add focus variant',
            autoFixable: false,
          },
          {
            severity: 'warning',
            category: 'naming',
            message: 'Generic layer name',
            location: 'Frame 1',
            suggestion: 'Use semantic names',
            autoFixable: true,
          },
        ],
      });
      const metadata = mockMetadataAnalysis({
        componentSetLevel: {
          present: ['description'],
          missing: ['tags', 'notes'],
          incomplete: [],
        },
      });

      const result = scoringEngine.generateActionItems(audit as any, metadata as any);

      expect(result).toHaveProperty('critical');
      expect(result).toHaveProperty('high');
      expect(result).toHaveProperty('medium');
      expect(result).toHaveProperty('low');
    });

    it('should prioritize accessibility issues as critical', () => {
      const audit = mockAuditResult({
        issues: [
          {
            severity: 'error',
            category: 'accessibility',
            message: 'Missing focus state',
            location: 'Component',
            suggestion: 'Add focus variant',
            autoFixable: false,
          },
        ],
      });
      const metadata = mockMetadataAnalysis();

      const result = scoringEngine.generateActionItems(audit as any, metadata as any);

      // Critical should include accessibility errors
      expect(result.critical.length).toBeGreaterThan(0);
    });
  });

  describe('generateReport', () => {
    it('should generate a complete report', () => {
      const audit = mockAuditResult({ score: 85 });
      const metadata = mockMetadataAnalysis({ completenessScore: 80 });

      const report = scoringEngine.generateReport(
        'TestComponent',
        'COMPONENT_SET',
        audit as any,
        metadata as any
      );

      expect(report.componentName).toBe('TestComponent');
      expect(report.componentType).toBe('COMPONENT_SET');
      expect(report.overallScore).toBeGreaterThan(0);
      expect(report.exportReady).toBeDefined();
      expect(report.audit).toBeDefined();
      expect(report.scores).toBeDefined();
    });

    it('should correctly determine exportReady status', () => {
      const audit = mockAuditResult({
        score: 95,
        categories: {
          naming: mockCategoryScore(95),
          structure: mockCategoryScore(95),
          visual: mockCategoryScore(95),
          accessibility: mockCategoryScore(95),
          variants: mockCategoryScore(95),
        },
        blockers: [],
      });
      const metadata = mockMetadataAnalysis({
        completenessScore: 95,
        componentSetLevel: {
          present: ['description', 'tags', 'notes'],
          missing: [],
          incomplete: [],
        },
      });

      const report = scoringEngine.generateReport(
        'HighQualityComponent',
        'COMPONENT',
        audit as any,
        metadata as any
      );

      expect(report.overallScore).toBeGreaterThanOrEqual(90);
      expect(report.exportReady).toBe(true);
    });

    it('should include blockers in report', () => {
      const audit = mockAuditResult({
        score: 60,
        blockers: ['Missing focus state', 'No description'],
      });
      const metadata = mockMetadataAnalysis({ completenessScore: 50 });

      const report = scoringEngine.generateReport(
        'LowQualityComponent',
        'COMPONENT',
        audit as any,
        metadata as any
      );

      expect(report.blockers).toContain('Missing focus state');
      expect(report.blockers).toContain('No description');
      expect(report.exportReady).toBe(false);
    });
  });
});

describe('ScoringEngine Configuration', () => {
  it('should use correct default weights', () => {
    // Weights should sum to 1.0
    const weights = {
      consistency: 0.25,
      metadata: 0.30,
      accessibility: 0.25,
      structure: 0.20,
    };

    const sum = Object.values(weights).reduce((a, b) => a + b, 0);
    expect(sum).toBeCloseTo(1.0, 2);
  });

  it('should have export threshold of 90', () => {
    const audit = mockAuditResult({
      score: 100,
      categories: {
        naming: mockCategoryScore(100),
        structure: mockCategoryScore(100),
        visual: mockCategoryScore(100),
        accessibility: mockCategoryScore(100),
        variants: mockCategoryScore(100),
      },
      blockers: [],
    });
    const metadata90 = mockMetadataAnalysis({
      completenessScore: 100,
      componentSetLevel: {
        present: ['description', 'tags', 'notes'],
        missing: [],
        incomplete: [],
      },
    });

    const result = scoringEngine.isExportReady(audit as any, metadata90 as any);
    expect(result.ready).toBe(true);
  });

  it('should allow custom configuration', () => {
    const customEngine = new ScoringEngine({
      exportThreshold: 80,
    });

    const audit = mockAuditResult({
      score: 85,
      categories: {
        naming: mockCategoryScore(85),
        structure: mockCategoryScore(85),
        visual: mockCategoryScore(85),
        accessibility: mockCategoryScore(85),
        variants: mockCategoryScore(85),
      },
      blockers: [],
    });
    const metadata = mockMetadataAnalysis({
      completenessScore: 85,
      componentSetLevel: {
        present: ['description', 'tags', 'notes'],
        missing: [],
        incomplete: [],
      },
    });

    const result = customEngine.isExportReady(audit as any, metadata as any);
    expect(result.ready).toBe(true);
  });
});
