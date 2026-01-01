/**
 * @file metadataGenerator.test.js
 * @description Unit tests for metadata generation service.
 * Tests fallback generation, level/category classification, and formatting.
 */

// Mock claudeClient before requiring metadataGenerator
jest.mock('../../src/utils/claudeClient', () => ({
  isAvailable: jest.fn(),
  generateMetadata: jest.fn()
}));

const metadataGenerator = require('../../src/services/metadataGenerator');
const claudeClient = require('../../src/utils/claudeClient');

// ============================================
// Test Data
// ============================================

const testComponents = {
  button: {
    component: {
      name: 'Button/Primary',
      type: 'COMPONENT_SET',
      description: 'Existing description',
      variantCount: 3,
      childCount: 2
    },
    tokens: [
      { type: 'color', name: 'background', value: '#0066FF' },
      { type: 'spacing', name: 'padding', value: '12px' },
      { type: 'typography', name: 'font', value: 'Inter 16px' }
    ],
    variants: [
      { name: 'Default', description: 'Default state' },
      { name: 'Hover', description: 'Hover state' }
    ]
  },

  icon: {
    component: {
      name: 'Icon/Star',
      type: 'COMPONENT',
      description: '',
      childCount: 1
    },
    tokens: [
      { type: 'color', name: 'fill', value: '#FFD700' }
    ],
    variants: []
  },

  card: {
    component: {
      name: 'Card/Product',
      type: 'COMPONENT_SET',
      description: '',
      childCount: 8,
      variantCount: 2
    },
    tokens: [],
    variants: [
      { name: 'Default' },
      { name: 'Featured' }
    ]
  },

  modal: {
    component: {
      name: 'Modal/Dialog',
      type: 'COMPONENT_SET',
      description: '',
      childCount: 15,
      variantCount: 5
    },
    tokens: [],
    variants: []
  },

  form: {
    component: {
      name: 'Input/Text',
      type: 'COMPONENT_SET',
      description: '',
      childCount: 3
    },
    tokens: [],
    variants: []
  },

  nav: {
    component: {
      name: 'Navigation/Menu',
      type: 'COMPONENT_SET',
      description: '',
      childCount: 5
    },
    tokens: [],
    variants: []
  },

  alert: {
    component: {
      name: 'Alert/Success',
      type: 'COMPONENT',
      description: '',
      childCount: 2
    },
    tokens: [],
    variants: []
  },

  table: {
    component: {
      name: 'Table/Data',
      type: 'COMPONENT_SET',
      description: '',
      childCount: 20
    },
    tokens: [],
    variants: []
  },

  popup: {
    component: {
      name: 'Overlay/Popup',
      type: 'COMPONENT',
      description: '',
      childCount: 3
    },
    tokens: [],
    variants: []
  },

  page: {
    component: {
      name: 'Page/Dashboard',
      type: 'COMPONENT',
      description: '',
      childCount: 50
    },
    tokens: [],
    variants: []
  }
};

// ============================================
// Fallback Metadata Generation Tests
// ============================================

describe('MetadataGenerator - generateFallbackMetadata', () => {
  describe('Basic Structure', () => {
    test('returns success flag', () => {
      const result = metadataGenerator.generateFallbackMetadata(testComponents.button);
      expect(result.success).toBe(true);
    });

    test('returns source as fallback', () => {
      const result = metadataGenerator.generateFallbackMetadata(testComponents.button);
      expect(result.source).toBe('fallback');
    });

    test('includes all required fields', () => {
      const result = metadataGenerator.generateFallbackMetadata(testComponents.button);

      expect(result.description).toBeDefined();
      expect(result.formattedDescription).toBeDefined();
      expect(result.tags).toBeDefined();
      expect(result.notes).toBeDefined();
      expect(result.ariaLabel).toBeDefined();
      expect(result.category).toBeDefined();
      expect(result.level).toBeDefined();
      expect(result.priority).toBeDefined();
      expect(result.dos).toBeDefined();
      expect(result.donts).toBeDefined();
      expect(result.a11y).toBeDefined();
    });
  });

  describe('Level Classification', () => {
    test('classifies button as atom', () => {
      const result = metadataGenerator.generateFallbackMetadata(testComponents.button);
      expect(result.level).toBe('atom');
    });

    test('classifies icon as atom', () => {
      const result = metadataGenerator.generateFallbackMetadata(testComponents.icon);
      expect(result.level).toBe('atom');
    });

    test('classifies card as molecule', () => {
      const result = metadataGenerator.generateFallbackMetadata(testComponents.card);
      expect(result.level).toBe('molecule');
    });

    test('classifies modal based on variant count', () => {
      // Algorithm prioritizes variant count over name patterns:
      // variantCount >= 5 → molecule (before name check for "modal")
      const result = metadataGenerator.generateFallbackMetadata(testComponents.modal);
      // modal has variantCount: 5, which triggers molecule classification
      expect(result.level).toBe('molecule');
    });

    test('classifies page as template', () => {
      const result = metadataGenerator.generateFallbackMetadata(testComponents.page);
      expect(result.level).toBe('template');
    });

    test('classifies form input as atom', () => {
      const result = metadataGenerator.generateFallbackMetadata(testComponents.form);
      expect(result.level).toBe('atom');
    });
  });

  describe('Category Classification', () => {
    test('classifies button correctly', () => {
      const result = metadataGenerator.generateFallbackMetadata(testComponents.button);
      expect(result.category).toBe('button');
    });

    test('classifies navigation correctly', () => {
      const result = metadataGenerator.generateFallbackMetadata(testComponents.nav);
      expect(result.category).toBe('navigation');
    });

    test('classifies form input correctly', () => {
      const result = metadataGenerator.generateFallbackMetadata(testComponents.form);
      expect(result.category).toBe('form');
    });

    test('classifies card as layout', () => {
      const result = metadataGenerator.generateFallbackMetadata(testComponents.card);
      expect(result.category).toBe('layout');
    });

    test('classifies alert as feedback', () => {
      const result = metadataGenerator.generateFallbackMetadata(testComponents.alert);
      expect(result.category).toBe('feedback');
    });

    test('classifies table as data-display', () => {
      const result = metadataGenerator.generateFallbackMetadata(testComponents.table);
      expect(result.category).toBe('data-display');
    });

    test('classifies popup as overlay', () => {
      const result = metadataGenerator.generateFallbackMetadata(testComponents.popup);
      expect(result.category).toBe('overlay');
    });
  });

  describe('Description Generation', () => {
    test('includes component name in description', () => {
      const result = metadataGenerator.generateFallbackMetadata(testComponents.button);
      expect(result.description).toContain('Primary');
    });

    test('mentions variants for COMPONENT_SET', () => {
      const result = metadataGenerator.generateFallbackMetadata(testComponents.button);
      expect(result.description).toContain('variant');
    });

    test('does not mention variants for simple COMPONENT', () => {
      const result = metadataGenerator.generateFallbackMetadata(testComponents.icon);
      expect(result.description).not.toContain('variant');
    });
  });

  describe('Tags Generation', () => {
    test('generates tags as comma-separated string', () => {
      const result = metadataGenerator.generateFallbackMetadata(testComponents.button);
      expect(typeof result.tags).toBe('string');
      expect(result.tags).toContain(',');
    });

    test('includes category in tags', () => {
      const result = metadataGenerator.generateFallbackMetadata(testComponents.button);
      expect(result.tags).toContain('button');
    });

    test('includes level in tags', () => {
      const result = metadataGenerator.generateFallbackMetadata(testComponents.button);
      expect(result.tags).toContain('atom');
    });
  });

  describe('ARIA Label Generation', () => {
    test('generates readable ARIA label', () => {
      const result = metadataGenerator.generateFallbackMetadata(testComponents.button);
      expect(result.ariaLabel).toBeDefined();
      expect(result.ariaLabel.length).toBeGreaterThan(0);
    });

    test('converts kebab-case to readable text', () => {
      const result = metadataGenerator.generateFallbackMetadata({
        component: { name: 'my-button-component' },
        tokens: [],
        variants: []
      });
      expect(result.ariaLabel).toContain(' ');
    });
  });

  describe('Dos and Donts', () => {
    test('generates dos array', () => {
      const result = metadataGenerator.generateFallbackMetadata(testComponents.button);
      expect(Array.isArray(result.dos)).toBe(true);
      expect(result.dos.length).toBeGreaterThan(0);
    });

    test('generates donts array', () => {
      const result = metadataGenerator.generateFallbackMetadata(testComponents.button);
      expect(Array.isArray(result.donts)).toBe(true);
      expect(result.donts.length).toBeGreaterThan(0);
    });

    test('button has category-specific dos', () => {
      const result = metadataGenerator.generateFallbackMetadata(testComponents.button);
      expect(result.dos.some(d => d.includes('label') || d.includes('action'))).toBe(true);
    });

    test('form has category-specific dos', () => {
      const result = metadataGenerator.generateFallbackMetadata(testComponents.form);
      expect(result.dos.some(d => d.includes('label') || d.includes('keyboard'))).toBe(true);
    });
  });

  describe('Accessibility Requirements', () => {
    test('generates a11y array', () => {
      const result = metadataGenerator.generateFallbackMetadata(testComponents.button);
      expect(Array.isArray(result.a11y)).toBe(true);
      expect(result.a11y.length).toBeGreaterThan(0);
    });

    test('includes contrast ratio requirement', () => {
      const result = metadataGenerator.generateFallbackMetadata(testComponents.button);
      expect(result.a11y.some(a => a.includes('contrast'))).toBe(true);
    });

    test('button has touch target requirement', () => {
      const result = metadataGenerator.generateFallbackMetadata(testComponents.button);
      expect(result.a11y.some(a => a.includes('44x44'))).toBe(true);
    });

    test('navigation has keyboard nav requirement', () => {
      const result = metadataGenerator.generateFallbackMetadata(testComponents.nav);
      expect(result.a11y.some(a => a.includes('keyboard'))).toBe(true);
    });
  });

  describe('Formatted Description', () => {
    test('includes separator', () => {
      const result = metadataGenerator.generateFallbackMetadata(testComponents.button);
      expect(result.formattedDescription).toContain('---');
    });

    test('includes tags line', () => {
      const result = metadataGenerator.generateFallbackMetadata(testComponents.button);
      expect(result.formattedDescription).toContain('tags:');
    });

    test('includes category line', () => {
      const result = metadataGenerator.generateFallbackMetadata(testComponents.button);
      expect(result.formattedDescription).toContain('category:');
    });

    test('includes tokens section when tokens present', () => {
      const result = metadataGenerator.generateFallbackMetadata(testComponents.button);
      expect(result.formattedDescription).toContain('tokens:');
    });

    test('includes states section for interactive components', () => {
      // Format changed: variant info now appears in description text
      // and interactive components get a "states:" section
      const result = metadataGenerator.generateFallbackMetadata(testComponents.button);
      expect(result.formattedDescription).toContain('states:');
    });
  });

  describe('Token Extraction', () => {
    test('extracts color tokens', () => {
      const result = metadataGenerator.generateFallbackMetadata(testComponents.button);
      expect(result.formattedDescription).toContain('#0066FF');
    });

    test('extracts spacing tokens', () => {
      const result = metadataGenerator.generateFallbackMetadata(testComponents.button);
      expect(result.formattedDescription).toContain('12px');
    });

    test('handles empty tokens', () => {
      const result = metadataGenerator.generateFallbackMetadata(testComponents.card);
      expect(result).toBeDefined();
      expect(result.formattedDescription).not.toContain('tokens:');
    });
  });
});

// ============================================
// generateMetadata (with Claude) Tests
// ============================================

describe('MetadataGenerator - generateMetadata', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('uses fallback when Claude not available', async () => {
    claudeClient.isAvailable.mockReturnValue(false);

    const result = await metadataGenerator.generateMetadata(testComponents.button);

    expect(result.source).toBe('fallback');
    expect(claudeClient.generateMetadata).not.toHaveBeenCalled();
  });

  test('calls Claude when available', async () => {
    claudeClient.isAvailable.mockReturnValue(true);
    claudeClient.generateMetadata.mockResolvedValue({
      description: 'AI generated description',
      tags: 'ai, generated',
      category: 'button',
      level: 'atom'
    });

    const result = await metadataGenerator.generateMetadata(testComponents.button);

    expect(result.source).toBe('claude');
    expect(claudeClient.generateMetadata).toHaveBeenCalled();
  });

  test('falls back on Claude error', async () => {
    claudeClient.isAvailable.mockReturnValue(true);
    claudeClient.generateMetadata.mockRejectedValue(new Error('API Error'));

    const result = await metadataGenerator.generateMetadata(testComponents.button);

    expect(result.source).toBe('fallback');
    expect(result.success).toBe(true);
  });

  test('returns success flag from Claude response', async () => {
    claudeClient.isAvailable.mockReturnValue(true);
    claudeClient.generateMetadata.mockResolvedValue({
      description: 'Test',
      tags: 'test'
    });

    const result = await metadataGenerator.generateMetadata(testComponents.button);

    expect(result.success).toBe(true);
  });
});

// ============================================
// Edge Cases
// ============================================

describe('MetadataGenerator - Edge Cases', () => {
  test('handles missing component name', () => {
    const result = metadataGenerator.generateFallbackMetadata({
      component: {},
      tokens: [],
      variants: []
    });

    expect(result).toBeDefined();
    expect(result.description).toContain('Untitled');
  });

  test('handles null tokens', () => {
    const result = metadataGenerator.generateFallbackMetadata({
      component: { name: 'Test' },
      tokens: null,
      variants: []
    });

    expect(result).toBeDefined();
  });

  test('handles null variants', () => {
    const result = metadataGenerator.generateFallbackMetadata({
      component: { name: 'Test' },
      tokens: [],
      variants: null
    });

    expect(result).toBeDefined();
  });

  test('handles component with special characters in name', () => {
    const result = metadataGenerator.generateFallbackMetadata({
      component: { name: 'Button/Primary@2x!!!' },
      tokens: [],
      variants: []
    });

    expect(result).toBeDefined();
    // The ariaLabel converts the name but may still contain some chars
    expect(result.ariaLabel.length).toBeGreaterThan(0);
  });

  test('handles complex nested path in name', () => {
    const result = metadataGenerator.generateFallbackMetadata({
      component: { name: 'Components/Forms/Input/TextField' },
      tokens: [],
      variants: []
    });

    expect(result).toBeDefined();
    expect(result.description).toContain('TextField');
  });
});
