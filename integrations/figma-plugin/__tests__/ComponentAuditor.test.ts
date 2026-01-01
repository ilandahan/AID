/**
 * @file __tests__/ComponentAuditor.test.ts
 * @description Comprehensive tests for ComponentAuditor modules
 *
 * Tests cover:
 * - Configuration constants
 * - Utility functions (isInteractiveComponent, levenshteinDistance, extractNameValues)
 * - Naming checks (checkNameFormat, checkCommonTypos, checkLayerNames)
 * - Scoring functions (calculateScore, identifyBlockers, generateSuggestions)
 * - ComponentAuditor class facade
 */

import {
  // Configuration
  SCORING_CONFIG,
  INTERACTIVE_PATTERNS,
  CORRECT_TERMS,
  GENERIC_LAYER_NAMES,
  // Utilities
  isInteractiveComponent,
  levenshteinDistance,
  extractNameValues,
  // Scoring
  calculateScore,
  identifyBlockers,
  generateSuggestions,
  calculateDeepInspectionPenalty,
  // Naming checks
  checkNameFormat,
  checkCommonTypos,
  checkLayerNames,
} from '../services/ComponentAuditor';

import type { AuditIssue, CategoryScore } from '../types';

// ============================================================================
// Test Helpers
// ============================================================================

/**
 * Create a mock AuditIssue
 */
function mockAuditIssue(overrides: Partial<AuditIssue> = {}): AuditIssue {
  return {
    severity: 'warning',
    category: 'naming',
    message: 'Test issue',
    location: 'TestComponent',
    suggestion: 'Fix the issue',
    autoFixable: false,
    ...overrides,
  };
}

/**
 * Create a mock CategoryScore
 */
function mockCategoryScore(overrides: Partial<CategoryScore> = {}): CategoryScore {
  return {
    score: 80,
    weight: 0.25,
    passed: 4,
    failed: 1,
    warnings: 1,
    checks: [],
    ...overrides,
  };
}

/**
 * Create a mock Figma node
 */
function mockFigmaNode(overrides: Record<string, unknown> = {}): SceneNode {
  return {
    id: 'node-123',
    name: 'Button / Primary',
    type: 'COMPONENT',
    visible: true,
    ...overrides,
  } as unknown as SceneNode;
}

/**
 * Create a mock node with children
 */
function mockNodeWithChildren(
  name: string,
  childNames: string[]
): SceneNode & { children: SceneNode[] } {
  return {
    id: 'parent-123',
    name,
    type: 'FRAME',
    visible: true,
    children: childNames.map((childName, i) => ({
      id: `child-${i}`,
      name: childName,
      type: childName.includes('Text') ? 'TEXT' : 'FRAME',
      visible: true,
    })),
  } as unknown as SceneNode & { children: SceneNode[] };
}

// ============================================================================
// Configuration Tests
// ============================================================================

describe('ComponentAuditor Configuration', () => {
  describe('SCORING_CONFIG', () => {
    it('should define weight properties that sum to 1.0', () => {
      const weights = SCORING_CONFIG.weights;
      const totalWeight = Object.values(weights).reduce((sum, w) => sum + w, 0);
      expect(totalWeight).toBe(1.0);
    });

    it('should define minimum thresholds for all categories', () => {
      expect(SCORING_CONFIG.minimums.consistency).toBeDefined();
      expect(SCORING_CONFIG.minimums.metadata).toBeDefined();
      expect(SCORING_CONFIG.minimums.accessibility).toBeDefined();
      expect(SCORING_CONFIG.minimums.structure).toBeDefined();
    });

    it('should have export threshold of 90', () => {
      expect(SCORING_CONFIG.exportThreshold).toBe(90);
    });

    it('should define blocker issues', () => {
      expect(SCORING_CONFIG.blockerIssues).toContain('missing_component_description');
      expect(SCORING_CONFIG.blockerIssues).toContain('missing_focus_states');
      expect(SCORING_CONFIG.blockerIssues.length).toBeGreaterThan(0);
    });
  });

  describe('INTERACTIVE_PATTERNS', () => {
    it('should include common interactive element patterns', () => {
      const patternStrings = INTERACTIVE_PATTERNS.map(p => p.source);
      expect(patternStrings.some(p => p.includes('button'))).toBe(true);
      expect(patternStrings.some(p => p.includes('input'))).toBe(true);
      expect(patternStrings.some(p => p.includes('select'))).toBe(true);
    });

    it('should be case-insensitive', () => {
      // All patterns should have the 'i' flag
      INTERACTIVE_PATTERNS.forEach(pattern => {
        expect(pattern.flags).toContain('i');
      });
    });
  });

  describe('CORRECT_TERMS', () => {
    it('should include common design system terms', () => {
      expect(CORRECT_TERMS).toContain('Default');
      expect(CORRECT_TERMS).toContain('Hover');
      expect(CORRECT_TERMS).toContain('Primary');
      expect(CORRECT_TERMS).toContain('Button');
    });

    it('should include state terms', () => {
      const stateTerms = ['Default', 'Hover', 'Active', 'Focused', 'Disabled'];
      stateTerms.forEach(term => {
        expect(CORRECT_TERMS).toContain(term);
      });
    });

    it('should include variant terms', () => {
      const variantTerms = ['Primary', 'Secondary', 'Success', 'Warning', 'Error'];
      variantTerms.forEach(term => {
        expect(CORRECT_TERMS).toContain(term);
      });
    });

    it('should include size terms', () => {
      const sizeTerms = ['Small', 'Medium', 'Large'];
      sizeTerms.forEach(term => {
        expect(CORRECT_TERMS).toContain(term);
      });
    });
  });

  describe('GENERIC_LAYER_NAMES', () => {
    it('should include common Figma auto-generated names', () => {
      expect(GENERIC_LAYER_NAMES).toContain('Frame');
      expect(GENERIC_LAYER_NAMES).toContain('Group');
      expect(GENERIC_LAYER_NAMES).toContain('Rectangle');
      expect(GENERIC_LAYER_NAMES).toContain('Text');
      expect(GENERIC_LAYER_NAMES).toContain('Vector');
    });
  });
});

// ============================================================================
// Utility Functions Tests
// ============================================================================

describe('ComponentAuditor Utilities', () => {
  describe('isInteractiveComponent', () => {
    it('should return true for button components', () => {
      expect(isInteractiveComponent('Button')).toBe(true);
      expect(isInteractiveComponent('button-primary')).toBe(true);
      expect(isInteractiveComponent('SubmitBtn')).toBe(true);
    });

    it('should return true for input components', () => {
      expect(isInteractiveComponent('TextInput')).toBe(true);
      expect(isInteractiveComponent('input-field')).toBe(true);
      expect(isInteractiveComponent('TextField')).toBe(true);
    });

    it('should return true for select/dropdown components', () => {
      expect(isInteractiveComponent('Select')).toBe(true);
      expect(isInteractiveComponent('dropdown-menu')).toBe(true);
      expect(isInteractiveComponent('ComboBox')).toBe(true);
    });

    it('should return true for checkbox/radio/toggle components', () => {
      expect(isInteractiveComponent('Checkbox')).toBe(true);
      expect(isInteractiveComponent('RadioButton')).toBe(true);
      expect(isInteractiveComponent('Toggle')).toBe(true);
      expect(isInteractiveComponent('Switch')).toBe(true);
    });

    it('should return true for navigation components', () => {
      expect(isInteractiveComponent('Tab')).toBe(true);
      expect(isInteractiveComponent('MenuItem')).toBe(true);
      expect(isInteractiveComponent('Navigation')).toBe(true);
      expect(isInteractiveComponent('Link')).toBe(true);
    });

    it('should return false for non-interactive components', () => {
      expect(isInteractiveComponent('Badge')).toBe(false);
      expect(isInteractiveComponent('Avatar')).toBe(false);
      expect(isInteractiveComponent('Divider')).toBe(false);
      expect(isInteractiveComponent('Icon')).toBe(false);
      expect(isInteractiveComponent('Text')).toBe(false);
    });
  });

  describe('levenshteinDistance', () => {
    it('should return 0 for identical strings', () => {
      expect(levenshteinDistance('hello', 'hello')).toBe(0);
      expect(levenshteinDistance('Button', 'Button')).toBe(0);
      expect(levenshteinDistance('', '')).toBe(0);
    });

    it('should return correct distance for insertions', () => {
      expect(levenshteinDistance('cat', 'cats')).toBe(1);
      expect(levenshteinDistance('Button', 'Buttons')).toBe(1);
    });

    it('should return correct distance for deletions', () => {
      expect(levenshteinDistance('cats', 'cat')).toBe(1);
      expect(levenshteinDistance('hello', 'hell')).toBe(1);
    });

    it('should return correct distance for substitutions', () => {
      expect(levenshteinDistance('cat', 'bat')).toBe(1);
      expect(levenshteinDistance('kitten', 'sitten')).toBe(1);
    });

    it('should return correct distance for multiple edits', () => {
      expect(levenshteinDistance('kitten', 'sitting')).toBe(3);
      expect(levenshteinDistance('sunday', 'saturday')).toBe(3);
    });

    it('should detect common typos', () => {
      // Distance 1 = likely typo
      expect(levenshteinDistance('Primray', 'Primary')).toBe(2);
      expect(levenshteinDistance('Buton', 'Button')).toBe(1);
      expect(levenshteinDistance('Defualt', 'Default')).toBe(2);
    });

    it('should handle empty strings', () => {
      expect(levenshteinDistance('', 'hello')).toBe(5);
      expect(levenshteinDistance('hello', '')).toBe(5);
    });
  });

  describe('extractNameValues', () => {
    it('should extract values from Property=Value format', () => {
      const result = extractNameValues('State=Default, Size=Medium');
      expect(result).toContainEqual({ value: 'Default', field: 'State' });
      expect(result).toContainEqual({ value: 'Medium', field: 'Size' });
    });

    it('should extract values from path format', () => {
      const result = extractNameValues('Button / Primary / Large');
      expect(result).toContainEqual({ value: 'Button', field: 'name' });
      expect(result).toContainEqual({ value: 'Primary', field: 'name' });
      expect(result).toContainEqual({ value: 'Large', field: 'name' });
    });

    it('should extract single word values', () => {
      const result = extractNameValues('Button');
      expect(result).toContainEqual({ value: 'Button', field: 'name' });
    });

    it('should filter out short values (less than 3 chars)', () => {
      const result = extractNameValues('A=On, B=Off');
      // 'On' and 'Off' have length 2-3, check if they're included
      expect(result.some(r => r.value === 'On')).toBe(false); // 2 chars
      expect(result.some(r => r.value === 'Off')).toBe(true); // 3 chars
    });

    it('should handle mixed formats', () => {
      const result = extractNameValues('Button / Primary, State=Hover');
      expect(result.length).toBeGreaterThan(0);
    });
  });
});

// ============================================================================
// Naming Checks Tests
// ============================================================================

describe('ComponentAuditor Naming Checks', () => {
  describe('checkNameFormat', () => {
    it('should pass for Category / Type format', () => {
      const result = checkNameFormat('Button / Primary');
      expect(result.passed).toBe(true);
    });

    it('should pass for Category / Type / Name format', () => {
      const result = checkNameFormat('Button / Primary / Large');
      expect(result.passed).toBe(true);
    });

    it('should pass for variant Property=Value format', () => {
      const result = checkNameFormat('State=Default, Size=Medium');
      expect(result.passed).toBe(true);
      expect(result.message).toContain('Property=Value');
    });

    it('should pass for single-word names', () => {
      const result = checkNameFormat('Button');
      expect(result.passed).toBe(true);
    });

    it('should warn for improper format', () => {
      const result = checkNameFormat('Button Primary'); // No separator
      expect(result.passed).toBe(false);
      expect(result.severity).toBe('warning');
    });

    it('should fail for empty parts in path', () => {
      const result = checkNameFormat('Button / / Primary');
      expect(result.passed).toBe(false);
    });
  });

  describe('checkCommonTypos', () => {
    it('should pass for correct terms', () => {
      const result = checkCommonTypos('State=Default, Size=Medium');
      expect(result.passed).toBe(true);
    });

    it('should detect typos in property values', () => {
      const result = checkCommonTypos('State=Defualt'); // typo: Defualt → Default
      expect(result.passed).toBe(false);
      expect(result.message.toLowerCase()).toContain('typo');
    });

    it('should detect typos in component names', () => {
      const result = checkCommonTypos('Buton / Primary'); // typo: Buton → Button
      expect(result.passed).toBe(false);
      expect(result.message).toContain('typo');
    });

    it('should not flag valid variant terms', () => {
      const validTerms = ['Primary', 'Secondary', 'Success', 'Warning', 'Error'];
      validTerms.forEach(term => {
        const result = checkCommonTypos(term);
        expect(result.passed).toBe(true);
      });
    });

    it('should not flag custom valid terms', () => {
      // Custom terms that are not in dictionary should pass
      const result = checkCommonTypos('CustomComponent / SpecialVariant');
      expect(result.passed).toBe(true);
    });

    it('should include field info for property typos', () => {
      const result = checkCommonTypos('State=Hovr'); // typo: Hovr → Hover
      if (!result.passed) {
        expect(result.field).toBe('State');
      }
    });
  });

  describe('checkLayerNames', () => {
    it('should pass for semantic layer names', () => {
      const node = mockNodeWithChildren('Button', ['Label', 'Icon', 'Background']);
      const result = checkLayerNames(node);
      expect(result.passed).toBe(true);
    });

    it('should fail for generic layer names like Frame 1', () => {
      const node = mockNodeWithChildren('Button', ['Frame 1', 'Text 2', 'Label']);
      const result = checkLayerNames(node);
      expect(result.passed).toBe(false);
      expect(result.message).toContain('generic');
    });

    it('should detect Rectangle with numbers', () => {
      const node = mockNodeWithChildren('Card', ['Rectangle 1', 'Content']);
      const result = checkLayerNames(node);
      expect(result.passed).toBe(false);
    });

    it('should detect Vector without semantic names', () => {
      const node = mockNodeWithChildren('Icon', ['Vector', 'Vector 2']);
      const result = checkLayerNames(node);
      expect(result.passed).toBe(false);
    });

    it('should handle deeply nested children', () => {
      const node = {
        id: 'parent',
        name: 'Card',
        type: 'FRAME',
        children: [
          {
            id: 'child-1',
            name: 'Content',
            type: 'FRAME',
            children: [
              { id: 'grandchild', name: 'Frame 1', type: 'FRAME' },
            ],
          },
        ],
      } as unknown as SceneNode & { children: SceneNode[] };

      const result = checkLayerNames(node);
      expect(result.passed).toBe(false);
    });

    it('should handle empty children', () => {
      const node = mockNodeWithChildren('Button', []);
      const result = checkLayerNames(node);
      expect(result.passed).toBe(true);
    });
  });
});

// ============================================================================
// Scoring Functions Tests
// ============================================================================

describe('ComponentAuditor Scoring', () => {
  describe('calculateScore', () => {
    it('should calculate weighted average of category scores', () => {
      const categories = {
        naming: mockCategoryScore({ score: 100, weight: 0.20 }),
        structure: mockCategoryScore({ score: 80, weight: 0.20 }),
        visual: mockCategoryScore({ score: 90, weight: 0.20 }),
        accessibility: mockCategoryScore({ score: 70, weight: 0.20 }),
        variants: mockCategoryScore({ score: 85, weight: 0.20 }),
      };

      const score = calculateScore(categories);

      // Expected: (100*0.20 + 80*0.20 + 90*0.20 + 70*0.20 + 85*0.20) / 1.0 = 85
      expect(score).toBeGreaterThanOrEqual(80);
      expect(score).toBeLessThanOrEqual(90);
    });

    it('should return 0 for empty categories', () => {
      // Test edge case with empty object (bypass strict typing)
      const score = calculateScore({} as any);
      expect(score).toBe(0);
    });

    it('should handle single category', () => {
      // Test edge case with single category (bypass strict typing)
      const categories = {
        naming: mockCategoryScore({ score: 75, weight: 1.0 }),
      };

      const score = calculateScore(categories as any);
      expect(score).toBe(75);
    });

    it('should round to nearest integer', () => {
      const categories = {
        naming: mockCategoryScore({ score: 77, weight: 0.2 }),
        structure: mockCategoryScore({ score: 82, weight: 0.2 }),
        visual: mockCategoryScore({ score: 80, weight: 0.2 }),
        accessibility: mockCategoryScore({ score: 78, weight: 0.2 }),
        variants: mockCategoryScore({ score: 83, weight: 0.2 }),
      };

      const score = calculateScore(categories);
      expect(Number.isInteger(score)).toBe(true);
    });
  });

  describe('identifyBlockers', () => {
    it('should extract error severity issues', () => {
      const issues: AuditIssue[] = [
        mockAuditIssue({ severity: 'error', message: 'Critical error' }),
        mockAuditIssue({ severity: 'warning', message: 'Warning' }),
        mockAuditIssue({ severity: 'error', message: 'Another error' }),
        mockAuditIssue({ severity: 'info', message: 'Info' }),
      ];

      const blockers = identifyBlockers(issues);

      expect(blockers).toHaveLength(2);
      expect(blockers).toContain('Critical error');
      expect(blockers).toContain('Another error');
    });

    it('should return empty array when no errors', () => {
      const issues: AuditIssue[] = [
        mockAuditIssue({ severity: 'warning' }),
        mockAuditIssue({ severity: 'info' }),
      ];

      const blockers = identifyBlockers(issues);
      expect(blockers).toHaveLength(0);
    });

    it('should handle empty issues array', () => {
      const blockers = identifyBlockers([]);
      expect(blockers).toHaveLength(0);
    });
  });

  describe('generateSuggestions', () => {
    it('should extract suggestions from issues', () => {
      const issues: AuditIssue[] = [
        mockAuditIssue({ suggestion: 'Fix naming' }),
        mockAuditIssue({ suggestion: 'Add description' }),
        mockAuditIssue({ suggestion: undefined }),
      ];

      const suggestions = generateSuggestions(issues);

      expect(suggestions).toContain('Fix naming');
      expect(suggestions).toContain('Add description');
      expect(suggestions).toHaveLength(2);
    });

    it('should limit to top 5 suggestions', () => {
      const issues: AuditIssue[] = Array(10).fill(null).map((_, i) =>
        mockAuditIssue({ suggestion: `Suggestion ${i + 1}` })
      );

      const suggestions = generateSuggestions(issues);
      expect(suggestions).toHaveLength(5);
    });

    it('should filter out undefined suggestions', () => {
      const issues: AuditIssue[] = [
        mockAuditIssue({ suggestion: undefined }),
        mockAuditIssue({ suggestion: 'Valid suggestion' }),
      ];

      const suggestions = generateSuggestions(issues);
      expect(suggestions).toHaveLength(1);
    });
  });

  describe('calculateDeepInspectionPenalty', () => {
    it('should calculate penalty for deep issues', () => {
      const issues: AuditIssue[] = [
        mockAuditIssue({ location: 'Button > Label', severity: 'error' }),
        mockAuditIssue({ location: 'Button > Icon', severity: 'warning' }),
        mockAuditIssue({ location: 'Toplevel', severity: 'error' }), // Not deep
      ];

      const penalty = calculateDeepInspectionPenalty(issues);

      // 1 deep error (3 points) + 1 deep warning (1 point) = 4
      expect(penalty).toBe(4);
    });

    it('should return 0 for no deep issues', () => {
      const issues: AuditIssue[] = [
        mockAuditIssue({ location: 'Button', severity: 'error' }),
        mockAuditIssue({ location: 'Card', severity: 'warning' }),
      ];

      const penalty = calculateDeepInspectionPenalty(issues);
      expect(penalty).toBe(0);
    });

    it('should weight errors more than warnings', () => {
      const errorIssues: AuditIssue[] = [
        mockAuditIssue({ location: 'A > B', severity: 'error' }),
      ];
      const warningIssues: AuditIssue[] = [
        mockAuditIssue({ location: 'A > B', severity: 'warning' }),
      ];

      const errorPenalty = calculateDeepInspectionPenalty(errorIssues);
      const warningPenalty = calculateDeepInspectionPenalty(warningIssues);

      expect(errorPenalty).toBe(3);
      expect(warningPenalty).toBe(1);
      expect(errorPenalty).toBeGreaterThan(warningPenalty);
    });
  });
});

// ============================================================================
// Integration Tests
// ============================================================================

describe('ComponentAuditor Integration', () => {
  describe('Typo detection workflow', () => {
    it('should detect and suggest corrections for common typos', () => {
      const testCases = [
        { input: 'Buton', expectedCorrection: 'Button' },
        { input: 'Primray', expectedCorrection: 'Primary' },
        { input: 'Seconadry', expectedCorrection: 'Secondary' },
      ];

      testCases.forEach(({ input }) => {
        const result = checkCommonTypos(input);
        // These should be detected as typos
        expect(result.passed).toBe(false);
      });
    });
  });

  describe('Interactive component detection', () => {
    it('should correctly identify components needing focus states', () => {
      const needsFocus = ['Button', 'TextInput', 'Checkbox', 'Link', 'Tab'];
      const noFocus = ['Badge', 'Avatar', 'Divider', 'Card', 'Text'];

      needsFocus.forEach(name => {
        expect(isInteractiveComponent(name)).toBe(true);
      });

      noFocus.forEach(name => {
        expect(isInteractiveComponent(name)).toBe(false);
      });
    });
  });

  describe('Score calculation with penalties', () => {
    it('should reduce score based on deep inspection issues', () => {
      const baseCategories = {
        naming: mockCategoryScore({ score: 90, weight: 0.20 }),
        structure: mockCategoryScore({ score: 90, weight: 0.20 }),
        visual: mockCategoryScore({ score: 90, weight: 0.20 }),
        accessibility: mockCategoryScore({ score: 90, weight: 0.20 }),
        variants: mockCategoryScore({ score: 90, weight: 0.20 }),
      };

      const baseScore = calculateScore(baseCategories);

      const deepIssues: AuditIssue[] = [
        mockAuditIssue({ location: 'Variant > Label', severity: 'error' }),
        mockAuditIssue({ location: 'Variant > Icon', severity: 'error' }),
      ];

      const penalty = calculateDeepInspectionPenalty(deepIssues);
      const adjustedScore = Math.max(0, baseScore - penalty);

      expect(adjustedScore).toBeLessThan(baseScore);
      expect(penalty).toBe(6); // 2 errors * 3 points
    });
  });

  describe('Name extraction and validation', () => {
    it('should extract and validate variant property names', () => {
      const variantName = 'State=Default, Size=Large, Type=Primary';
      const values = extractNameValues(variantName);

      // Check extraction
      expect(values).toContainEqual({ value: 'Default', field: 'State' });
      expect(values).toContainEqual({ value: 'Large', field: 'Size' });
      expect(values).toContainEqual({ value: 'Primary', field: 'Type' });

      // Validate each value against dictionary
      values.forEach(({ value }) => {
        const result = checkCommonTypos(value);
        expect(result.passed).toBe(true);
      });
    });
  });
});

// ============================================================================
// Edge Cases Tests
// ============================================================================

describe('ComponentAuditor Edge Cases', () => {
  describe('levenshteinDistance edge cases', () => {
    it('should handle single character strings', () => {
      expect(levenshteinDistance('a', 'b')).toBe(1);
      expect(levenshteinDistance('a', 'a')).toBe(0);
    });

    it('should handle very long strings', () => {
      const long1 = 'a'.repeat(100);
      const long2 = 'a'.repeat(99) + 'b';
      expect(levenshteinDistance(long1, long2)).toBe(1);
    });

    it('should handle unicode characters', () => {
      expect(levenshteinDistance('café', 'cafe')).toBe(1);
    });
  });

  describe('extractNameValues edge cases', () => {
    it('should handle empty string', () => {
      const result = extractNameValues('');
      expect(result).toHaveLength(0);
    });

    it('should handle string with only separators', () => {
      const result = extractNameValues('/ / /');
      expect(result).toHaveLength(0);
    });

    it('should handle malformed property=value', () => {
      const result = extractNameValues('=Value');
      // Should handle gracefully
      expect(Array.isArray(result)).toBe(true);
    });
  });

  describe('checkLayerNames edge cases', () => {
    it('should handle case variations', () => {
      const node = mockNodeWithChildren('Button', ['frame 1', 'FRAME 2', 'Frame']);
      const result = checkLayerNames(node);
      // 'Frame' without number should pass, others should fail
      expect(result.passed).toBe(false);
    });
  });

  describe('Score calculation edge cases', () => {
    it('should handle all zero scores', () => {
      const categories = {
        naming: mockCategoryScore({ score: 0, weight: 0.2 }),
        structure: mockCategoryScore({ score: 0, weight: 0.2 }),
        visual: mockCategoryScore({ score: 0, weight: 0.2 }),
        accessibility: mockCategoryScore({ score: 0, weight: 0.2 }),
        variants: mockCategoryScore({ score: 0, weight: 0.2 }),
      };

      const score = calculateScore(categories);
      expect(score).toBe(0);
    });

    it('should handle all perfect scores', () => {
      const categories = {
        naming: mockCategoryScore({ score: 100, weight: 0.2 }),
        structure: mockCategoryScore({ score: 100, weight: 0.2 }),
        visual: mockCategoryScore({ score: 100, weight: 0.2 }),
        accessibility: mockCategoryScore({ score: 100, weight: 0.2 }),
        variants: mockCategoryScore({ score: 100, weight: 0.2 }),
      };

      const score = calculateScore(categories);
      expect(score).toBe(100);
    });
  });
});

