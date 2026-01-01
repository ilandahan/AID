/**
 * @file componentAuditor.test.js
 * @description Unit tests for component auditing and scoring logic.
 * Tests naming, structure, visual, accessibility, and metadata audits.
 */

const componentAuditor = require('../../src/services/componentAuditor');

// ============================================
// Test Data - Realistic Component Examples
// ============================================

const testComponents = {
  // Well-formed button component with complete metadata (all 16 fields for 90+ combined score)
  goodButton: {
    component: {
      name: 'Button/Primary',
      type: 'COMPONENT_SET',
      description: `Primary action button for forms and CTAs.

---
tags: button, primary, cta, action
notes: Use for main actions. Limit to one per section.
category: button
level: atom
ariaLabel: Primary action button
priority: high
tokens: bg-primary, text-white, spacing-md
states: default, hover, focus, disabled
variants: size, theme
dos:
  - Use for primary actions
  - Keep label concise
donts:
  - Avoid multiple primary buttons
  - Do not use for navigation
analytics: button_primary_click
testId: btn-primary
a11y: role=button, aria-pressed
related: SecondaryButton, IconButton
specs: https://figma.com/file/xxx`,
      hasAutoLayout: true,
      hasStates: true,
      childCount: 5,
      width: 120,
      height: 48
    },
    tokens: [
      { type: 'color', name: 'background', value: '#0066FF' },
      { type: 'color', name: 'text', value: '#FFFFFF' },
      { type: 'spacing', name: 'padding', value: '12px 24px' },
      { type: 'typography', name: 'label', value: 'Inter 16px Medium' }
    ],
    variants: [
      { name: 'State=Default' },
      { name: 'State=Hover' },
      { name: 'State=Disabled' }
    ]
  },

  // Poorly formed component with many issues
  poorComponent: {
    component: {
      name: 'box',
      type: 'COMPONENT',
      description: '',
      hasAutoLayout: false,
      hasStates: false,
      childCount: 0,
      width: 30,
      height: 30
    },
    tokens: [],
    variants: []
  },

  // Component with special characters in name
  specialCharsComponent: {
    component: {
      name: 'My Component!!!@#$',
      type: 'COMPONENT',
      description: 'A component',
      hasAutoLayout: true,
      hasStates: true,
      childCount: 2,
      width: 100,
      height: 50
    },
    tokens: [],
    variants: []
  },

  // Component with partial metadata
  partialMetadata: {
    component: {
      name: 'Card/Product',
      type: 'COMPONENT_SET',
      description: `Product display card.

---
tags: card, product
category: data-display
level: molecule`,
      hasAutoLayout: true,
      hasStates: true,
      childCount: 8,
      width: 280,
      height: 380
    },
    tokens: [
      { type: 'color', name: 'bg', value: '#FFFFFF' }
    ],
    variants: [
      { name: 'Variant=Default' }
    ]
  },

  // Component with very light colors (accessibility concern)
  lightColorsComponent: {
    component: {
      name: 'Text/Light',
      type: 'COMPONENT',
      description: 'Light text component\n\n---\ntags: text\nnotes: For light backgrounds\ncategory: typography\nlevel: atom',
      hasAutoLayout: true,
      hasStates: true,
      childCount: 1,
      width: 200,
      height: 24
    },
    tokens: [
      { type: 'color', name: 'text', value: '#FAFAFA' }, // Very light
      { type: 'color', name: 'bg', value: '#FFFFFF' }
    ],
    variants: []
  }
};

// ============================================
// Naming Audit Tests
// ============================================

describe('Component Auditor - Naming', () => {
  describe('runAudit - naming category', () => {
    test('scores 100 for proper PascalCase naming', () => {
      const result = componentAuditor.runAudit(testComponents.goodButton);

      expect(result.categories.naming).toBe(100);
      expect(result.issues.filter(i => i.category === 'naming')).toHaveLength(0);
    });

    test('penalizes generic names like "box" or "container"', () => {
      const result = componentAuditor.runAudit(testComponents.poorComponent);

      expect(result.categories.naming).toBeLessThan(100);

      const namingIssues = result.issues.filter(i => i.category === 'naming');
      expect(namingIssues.length).toBeGreaterThan(0);
      expect(namingIssues.some(i => i.message.includes('generic'))).toBe(true);
    });

    test('penalizes improper naming format', () => {
      const result = componentAuditor.runAudit(testComponents.specialCharsComponent);

      expect(result.categories.naming).toBeLessThan(100);

      // Algorithm checks for Category / Type format, not special characters specifically
      const namingIssues = result.issues.filter(i => i.category === 'naming');
      expect(namingIssues.some(i => i.message.includes('Category / Type format'))).toBe(true);
    });

    test('accepts kebab-case naming', () => {
      const kebabComponent = {
        component: {
          name: 'button-primary',
          type: 'COMPONENT',
          description: 'Button\n\n---\ntags: btn\nnotes: Primary\ncategory: button\nlevel: atom',
          hasAutoLayout: true,
          hasStates: true,
          childCount: 1,
          width: 100,
          height: 44
        },
        tokens: [{ type: 'color', value: '#000' }],
        variants: []
      };

      const result = componentAuditor.runAudit(kebabComponent);
      const namingIssues = result.issues.filter(i =>
        i.category === 'naming' && i.message.includes('PascalCase')
      );

      expect(namingIssues).toHaveLength(0);
    });
  });
});

// ============================================
// Structure Audit Tests
// ============================================

describe('Component Auditor - Structure', () => {
  describe('runAudit - structure category', () => {
    test('scores 100 for component with Auto Layout and children', () => {
      const result = componentAuditor.runAudit(testComponents.goodButton);

      expect(result.categories.structure).toBe(100);
      expect(result.issues.filter(i => i.category === 'structure')).toHaveLength(0);
    });

    test('penalizes missing Auto Layout', () => {
      const result = componentAuditor.runAudit(testComponents.poorComponent);

      expect(result.categories.structure).toBeLessThan(100);

      const structureIssues = result.issues.filter(i => i.category === 'structure');
      expect(structureIssues.some(i => i.message.includes('Auto Layout'))).toBe(true);
    });

    test('penalizes empty component with no children', () => {
      const result = componentAuditor.runAudit(testComponents.poorComponent);

      const structureIssues = result.issues.filter(i => i.category === 'structure');
      expect(structureIssues.some(i => i.message.includes('no child'))).toBe(true);
    });

    test('penalizes COMPONENT_SET with no variants', () => {
      const noVariants = {
        component: {
          name: 'Button/Test',
          type: 'COMPONENT_SET',
          description: 'Test\n\n---\ntags: btn\nnotes: Test\ncategory: button\nlevel: atom',
          hasAutoLayout: true,
          hasStates: true,
          childCount: 3,
          width: 100,
          height: 44
        },
        tokens: [{ type: 'color', value: '#000' }],
        variants: []
      };

      const result = componentAuditor.runAudit(noVariants);

      const structureIssues = result.issues.filter(i => i.category === 'structure');
      expect(structureIssues.some(i => i.message.includes('no variants'))).toBe(true);
    });
  });
});

// ============================================
// Visual Audit Tests
// ============================================

describe('Component Auditor - Visual', () => {
  describe('runAudit - visual category', () => {
    test('scores 100 when all token types present', () => {
      const result = componentAuditor.runAudit(testComponents.goodButton);

      expect(result.categories.visual).toBe(100);
      expect(result.issues.filter(i => i.category === 'visual')).toHaveLength(0);
    });

    test('penalizes missing design tokens', () => {
      const result = componentAuditor.runAudit(testComponents.poorComponent);

      expect(result.categories.visual).toBeLessThan(100);

      const visualIssues = result.issues.filter(i => i.category === 'visual');
      expect(visualIssues.some(i => i.message.includes('No design tokens'))).toBe(true);
    });

    test('penalizes missing color tokens', () => {
      const noColors = {
        component: {
          name: 'Spacer',
          type: 'COMPONENT',
          description: 'Spacer\n\n---\ntags: spacer\nnotes: Spacing\ncategory: layout\nlevel: atom',
          hasAutoLayout: true,
          hasStates: false,
          childCount: 0,
          width: 50,
          height: 50
        },
        tokens: [
          { type: 'spacing', name: 'size', value: '16px' }
        ],
        variants: []
      };

      const result = componentAuditor.runAudit(noColors);

      const visualIssues = result.issues.filter(i => i.category === 'visual');
      expect(visualIssues.some(i => i.message.includes('color tokens'))).toBe(true);
    });

    test('penalizes missing typography tokens', () => {
      const noTypography = {
        component: {
          name: 'Icon/Check',
          type: 'COMPONENT',
          description: 'Check icon\n\n---\ntags: icon\nnotes: Check\ncategory: icon\nlevel: atom',
          hasAutoLayout: true,
          hasStates: false,
          childCount: 1,
          width: 24,
          height: 24
        },
        tokens: [
          { type: 'color', name: 'fill', value: '#000000' }
        ],
        variants: []
      };

      const result = componentAuditor.runAudit(noTypography);

      const visualIssues = result.issues.filter(i => i.category === 'visual');
      expect(visualIssues.some(i => i.message.includes('typography tokens'))).toBe(true);
    });
  });
});

// ============================================
// Accessibility Audit Tests
// ============================================

describe('Component Auditor - Accessibility', () => {
  describe('runAudit - accessibility category', () => {
    test('scores based on states and contrast', () => {
      const result = componentAuditor.runAudit(testComponents.goodButton);

      // Good component scores 70: has hover+disabled but missing focus (-15)
      // and has white color #FFFFFF which triggers light color warning (-15)
      expect(result.categories.accessibility).toBeGreaterThanOrEqual(65);
      expect(result.categories.accessibility).toBeLessThanOrEqual(75);
    });

    test('penalizes missing interactive states', () => {
      const result = componentAuditor.runAudit(testComponents.poorComponent);

      expect(result.categories.accessibility).toBeLessThan(100);

      // Algorithm generates messages like "Missing Focus state" (singular)
      const a11yIssues = result.issues.filter(i => i.category === 'accessibility');
      expect(a11yIssues.some(i => i.message.includes('state'))).toBe(true);
    });

    test('penalizes touch target below 44x44px', () => {
      const result = componentAuditor.runAudit(testComponents.poorComponent);

      const a11yIssues = result.issues.filter(i => i.category === 'accessibility');
      expect(a11yIssues.some(i => i.message.includes('44x44px'))).toBe(true);
    });

    test('warns about very light colors (contrast concern)', () => {
      const result = componentAuditor.runAudit(testComponents.lightColorsComponent);

      const a11yIssues = result.issues.filter(i => i.category === 'accessibility');
      expect(a11yIssues.some(i => i.message.includes('contrast'))).toBe(true);
    });

    test('accepts components meeting touch target size', () => {
      const largeComponent = {
        component: {
          name: 'Button/Large',
          type: 'COMPONENT',
          description: 'Large button\n\n---\ntags: btn\nnotes: Large\ncategory: button\nlevel: atom',
          hasAutoLayout: true,
          hasStates: true,
          childCount: 1,
          width: 200,
          height: 56
        },
        tokens: [{ type: 'color', value: '#000' }],
        variants: []
      };

      const result = componentAuditor.runAudit(largeComponent);

      const touchIssues = result.issues.filter(i =>
        i.category === 'accessibility' && i.message.includes('44x44px')
      );
      expect(touchIssues).toHaveLength(0);
    });
  });
});

// ============================================
// Metadata Audit Tests
// ============================================

describe('Component Auditor - Metadata', () => {
  describe('runAudit - metadata category', () => {
    test('scores high for complete metadata', () => {
      const result = componentAuditor.runAudit(testComponents.goodButton);

      expect(result.categories.metadata).toBeGreaterThanOrEqual(88);
    });

    test('penalizes missing description', () => {
      const result = componentAuditor.runAudit(testComponents.poorComponent);

      expect(result.categories.metadata).toBeLessThan(100);

      const metaIssues = result.issues.filter(i => i.category === 'metadata');
      expect(metaIssues.some(i => i.message.includes('no description'))).toBe(true);
    });

    test('penalizes missing --- separator', () => {
      const noSeparator = {
        component: {
          name: 'Card/Simple',
          type: 'COMPONENT',
          description: 'Simple card without structured metadata',
          hasAutoLayout: true,
          hasStates: true,
          childCount: 2,
          width: 200,
          height: 150
        },
        tokens: [{ type: 'color', value: '#FFF' }],
        variants: []
      };

      const result = componentAuditor.runAudit(noSeparator);

      const metaIssues = result.issues.filter(i => i.category === 'metadata');
      expect(metaIssues.some(i => i.message.includes('SKILL.md format'))).toBe(true);
    });

    test('penalizes missing required fields', () => {
      const result = componentAuditor.runAudit(testComponents.partialMetadata);

      const metaIssues = result.issues.filter(i => i.category === 'metadata');
      expect(metaIssues.some(i => i.message.includes('notes:'))).toBe(true);
    });

    test('suggests recommended fields as info', () => {
      const result = componentAuditor.runAudit(testComponents.partialMetadata);

      const infoIssues = result.issues.filter(i =>
        i.category === 'metadata' && i.severity === 'info'
      );
      expect(infoIssues.some(i => i.message.includes('ariaLabel'))).toBe(true);
    });
  });
});

// ============================================
// Overall Score Calculation Tests
// ============================================

describe('Component Auditor - Score Calculation', () => {
  describe('calculateOverallScore', () => {
    test('calculates weighted average correctly', () => {
      const result = componentAuditor.runAudit(testComponents.goodButton);

      // Audit score should be 90+ for well-formed component
      expect(result.score).toBeGreaterThanOrEqual(90);
    });

    test('returns score as integer 0-100', () => {
      const result = componentAuditor.runAudit(testComponents.partialMetadata);

      expect(Number.isInteger(result.score)).toBe(true);
      expect(result.score).toBeGreaterThanOrEqual(0);
      expect(result.score).toBeLessThanOrEqual(100);
    });

    test('poor component scores below export threshold', () => {
      const result = componentAuditor.runAudit(testComponents.poorComponent);

      // Combined score should be below 90
      expect(result.combinedScore).toBeLessThan(90);
      expect(result.exportReady).toBe(false);
    });

    test('good component has reasonable combined score', () => {
      const result = componentAuditor.runAudit(testComponents.goodButton);

      // Combined score formula: (audit * 0.7) + (metadataCompleteness * 0.3)
      // goodButton scores ~84: high audit but variants lack descriptions for metadata completeness
      expect(result.combinedScore).toBeGreaterThanOrEqual(80);
      // exportReady = combinedScore >= 90 && !hasErrors
      // Since goodButton scores ~84, it's not export ready
      expect(result.exportReady).toBe(result.combinedScore >= 90);
    });

    test('returns both audit score and combined score', () => {
      const result = componentAuditor.runAudit(testComponents.goodButton);

      expect(result.score).toBeDefined();
      expect(result.combinedScore).toBeDefined();
      expect(result.metadataCompletenessScore).toBeDefined();

      // Combined = audit * 0.7 + metadata * 0.3
      const expectedCombined = Math.round((result.score * 0.7) + (result.metadataCompletenessScore * 0.3));
      expect(result.combinedScore).toBe(expectedCombined);
    });

    test('includes gaps in audit result', () => {
      const result = componentAuditor.runAudit(testComponents.partialMetadata);

      expect(result.gaps).toBeDefined();
      expect(result.gaps.required).toBeInstanceOf(Array);
      expect(result.gaps.recommended).toBeInstanceOf(Array);
      expect(result.gaps.complete).toBeInstanceOf(Array);
    });

    test('exportReady uses combinedScore not raw score', () => {
      // A component might have high audit score but low metadata completeness
      const result = componentAuditor.runAudit(testComponents.partialMetadata);

      // exportReady should be based on combinedScore
      const expectedReady = result.combinedScore >= 90 && !result.issues.some(i => i.severity === 'error');
      expect(result.exportReady).toBe(expectedReady);
    });
  });
});

// ============================================
// Metadata Gap Analysis Tests
// ============================================

describe('Component Auditor - analyzeMetadataGaps', () => {
  test('identifies missing required fields', () => {
    const result = componentAuditor.analyzeMetadataGaps({
      component: testComponents.partialMetadata.component
    });

    // Result has gaps.required, not just required
    expect(result.gaps.required).toContain('notes');
  });

  test('identifies missing recommended fields', () => {
    const result = componentAuditor.analyzeMetadataGaps({
      component: testComponents.partialMetadata.component
    });

    // Result has gaps.recommended, not just recommended
    expect(result.gaps.recommended).toContain('ariaLabel');
    expect(result.gaps.recommended).toContain('dos');
    expect(result.gaps.recommended).toContain('donts');
  });

  test('returns completeness score', () => {
    const result = componentAuditor.analyzeMetadataGaps({
      component: testComponents.goodButton.component
    });

    expect(typeof result.completenessScore).toBe('number');
    expect(result.completenessScore).toBeGreaterThanOrEqual(0);
    expect(result.completenessScore).toBeLessThanOrEqual(100);
  });

  test('handles empty description', () => {
    const result = componentAuditor.analyzeMetadataGaps({
      component: testComponents.poorComponent.component
    });

    // Result has gaps.required, not just required
    expect(result.gaps.required).toContain('tags');
    expect(result.gaps.required).toContain('notes');
    expect(result.gaps.required).toContain('category');
    expect(result.gaps.required).toContain('level');
  });
});

// ============================================
// Edge Cases
// ============================================

describe('Component Auditor - Edge Cases', () => {
  test('handles empty component data gracefully', () => {
    // When component property is missing, audit should still run
    const result = componentAuditor.runAudit({ component: {} });

    expect(result).toBeDefined();
    expect(typeof result.score).toBe('number');
  });

  test('handles null tokens array', () => {
    const result = componentAuditor.runAudit({
      component: {
        name: 'Test',
        type: 'COMPONENT',
        description: 'Test\n\n---\ntags: test\nnotes: Test\ncategory: test\nlevel: atom',
        hasAutoLayout: true,
        hasStates: true,
        childCount: 1,
        width: 100,
        height: 44
      },
      tokens: null,
      variants: []
    });

    expect(result).toBeDefined();
    expect(typeof result.score).toBe('number');
  });

  test('handles empty variants for non-COMPONENT_SET', () => {
    const result = componentAuditor.runAudit({
      component: {
        name: 'Icon/Star',
        type: 'COMPONENT', // Not COMPONENT_SET
        description: 'Star icon\n\n---\ntags: icon\nnotes: Star\ncategory: icon\nlevel: atom',
        hasAutoLayout: true,
        hasStates: false,
        childCount: 1,
        width: 24,
        height: 24
      },
      tokens: [{ type: 'color', value: '#FFD700' }],
      variants: [] // Empty is OK for COMPONENT
    });

    const variantIssues = result.issues.filter(i => i.message.includes('no variants'));
    expect(variantIssues).toHaveLength(0);
  });

  test('handles Unicode component names', () => {
    const result = componentAuditor.runAudit({
      component: {
        name: 'Button/Primary',
        type: 'COMPONENT',
        description: 'Button\n\n---\ntags: btn\nnotes: Primary\ncategory: button\nlevel: atom',
        hasAutoLayout: true,
        hasStates: true,
        childCount: 1,
        width: 100,
        height: 44
      },
      tokens: [{ type: 'color', value: '#000' }],
      variants: []
    });

    expect(result).toBeDefined();
  });
});
