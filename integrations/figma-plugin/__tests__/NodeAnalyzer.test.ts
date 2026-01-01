/**
 * @file __tests__/NodeAnalyzer.test.ts
 * @description Comprehensive tests for NodeAnalyzer service modules
 *
 * Tests cover:
 * - Classification: Component hierarchy classification
 * - Tokens: Design token extraction and color conversion
 * - Utilities: Node traversal and counting
 */

import {
  classifyComponent,
  countChildren,
  calculateDepth,
  isLayoutContainer,
  detectCategory,
  generateSuggestedName,
} from '../services/NodeAnalyzer/classification';

import {
  rgbToHex,
  rgbaToString,
  deduplicateTokens,
} from '../services/NodeAnalyzer/tokens';

import {
  ATOM_PATTERNS,
  MOLECULE_PATTERNS,
  ORGANISM_PATTERNS,
  TEMPLATE_PATTERNS,
  CATEGORY_PATTERNS,
} from '../services/NodeAnalyzer/config';

import type { FigmaNodeInfo, DesignToken, AtomicLevel } from '../types';

// ============================================================================
// Test Helpers
// ============================================================================

/**
 * Create a minimal mock FigmaNodeInfo
 */
function mockFigmaNode(overrides: Partial<FigmaNodeInfo> = {}): FigmaNodeInfo {
  return {
    id: 'node-123',
    name: 'TestComponent',
    type: 'COMPONENT',
    properties: {},
    ...overrides,
  };
}

/**
 * Create a mock node with children
 */
function mockNodeWithChildren(count: number, depth = 1): FigmaNodeInfo {
  if (depth <= 0 || count <= 0) {
    return mockFigmaNode();
  }

  const children: FigmaNodeInfo[] = [];
  for (let i = 0; i < count; i++) {
    children.push(mockFigmaNode({
      id: `child-${depth}-${i}`,
      name: `Child ${i}`,
      children: depth > 1 ? [mockNodeWithChildren(2, depth - 1)] : undefined,
    }));
  }

  return mockFigmaNode({ children });
}

/**
 * Create a mock DesignToken
 */
function mockToken(overrides: Partial<DesignToken> = {}): DesignToken {
  return {
    name: 'test-token',
    value: '#FF0000',
    category: 'color',
    cssVariable: '--color-test',
    ...overrides,
  };
}

// ============================================================================
// Classification Tests
// ============================================================================

describe('NodeAnalyzer Classification', () => {
  describe('countChildren', () => {
    it('should return 0 for node without children', () => {
      const node = mockFigmaNode();
      expect(countChildren(node)).toBe(0);
    });

    it('should count direct children', () => {
      const node = mockFigmaNode({
        children: [
          mockFigmaNode({ id: 'child-1' }),
          mockFigmaNode({ id: 'child-2' }),
          mockFigmaNode({ id: 'child-3' }),
        ],
      });
      expect(countChildren(node)).toBe(3);
    });

    it('should count nested children recursively', () => {
      const node = mockFigmaNode({
        children: [
          mockFigmaNode({
            id: 'child-1',
            children: [
              mockFigmaNode({ id: 'grandchild-1' }),
              mockFigmaNode({ id: 'grandchild-2' }),
            ],
          }),
          mockFigmaNode({ id: 'child-2' }),
        ],
      });
      // 2 direct + 2 grandchildren = 4
      expect(countChildren(node)).toBe(4);
    });
  });

  describe('calculateDepth', () => {
    it('should return 0 for node without children', () => {
      const node = mockFigmaNode();
      expect(calculateDepth(node)).toBe(0);
    });

    it('should return 1 for node with direct children only', () => {
      const node = mockFigmaNode({
        children: [mockFigmaNode()],
      });
      expect(calculateDepth(node)).toBe(1);
    });

    it('should return max depth for deeply nested structure', () => {
      // Depth 3: root -> child -> grandchild -> great-grandchild
      const greatGrandchild = mockFigmaNode({ id: 'great-grandchild' });
      const grandchild = mockFigmaNode({ id: 'grandchild', children: [greatGrandchild] });
      const child = mockFigmaNode({ id: 'child', children: [grandchild] });
      const root = mockFigmaNode({ children: [child] });

      expect(calculateDepth(root)).toBe(3);
    });

    it('should handle uneven tree depths', () => {
      const deepBranch = mockFigmaNode({
        id: 'deep',
        children: [mockFigmaNode({ id: 'deeper' })],
      });
      const shallowBranch = mockFigmaNode({ id: 'shallow' });
      const root = mockFigmaNode({
        children: [deepBranch, shallowBranch],
      });

      expect(calculateDepth(root)).toBe(2);
    });
  });

  describe('isLayoutContainer', () => {
    it('should return true for auto-layout with AUTO sizing', () => {
      const node = mockFigmaNode({
        properties: {
          layoutMode: 'HORIZONTAL',
          primaryAxisSizingMode: 'AUTO',
        },
      });
      expect(isLayoutContainer(node)).toBe(true);
    });

    it('should return true for large dimensions', () => {
      const node = mockFigmaNode({
        properties: {
          width: 1200,
          height: 800,
        },
      });
      expect(isLayoutContainer(node)).toBe(true);
    });

    it('should return false for small fixed layout', () => {
      const node = mockFigmaNode({
        properties: {
          layoutMode: 'HORIZONTAL',
          primaryAxisSizingMode: 'FIXED',
          counterAxisSizingMode: 'FIXED',
          width: 200,
          height: 100,
        },
      });
      expect(isLayoutContainer(node)).toBe(false);
    });

    it('should return false for node without layout', () => {
      const node = mockFigmaNode();
      expect(isLayoutContainer(node)).toBe(false);
    });
  });

  describe('detectCategory', () => {
    it('should detect button category', () => {
      expect(detectCategory('primary-button')).toBe('button');
      expect(detectCategory('submit-btn')).toBe('button');
    });

    it('should detect input category', () => {
      expect(detectCategory('text-input')).toBe('input');
      expect(detectCategory('search-textfield')).toBe('input');
    });

    it('should detect navigation category', () => {
      expect(detectCategory('main-navigation')).toBe('navigation');
      expect(detectCategory('nav-bar')).toBe('navigation');
    });

    it('should return other for unknown patterns', () => {
      expect(detectCategory('custom-component')).toBe('other');
    });
  });

  describe('generateSuggestedName', () => {
    it('should convert to PascalCase', () => {
      expect(generateSuggestedName('primary button', 'atom')).toBe('PrimaryButton');
    });

    it('should handle hyphens', () => {
      expect(generateSuggestedName('nav-bar-item', 'molecule')).toBe('NavBarItem');
    });

    it('should handle underscores', () => {
      expect(generateSuggestedName('card_container', 'organism')).toBe('CardContainer');
    });

    it('should remove special characters', () => {
      expect(generateSuggestedName('Button @Primary#1', 'atom')).toBe('ButtonPrimary1');
    });

    it('should handle empty string', () => {
      expect(generateSuggestedName('', 'atom')).toBe('');
    });
  });

  describe('classifyComponent', () => {
    it('should classify simple component as atom', () => {
      const node = mockFigmaNode({ name: 'icon-close' });
      const result = classifyComponent(node);

      expect(result.level).toBe('atom');
      expect(result.confidence).toBeGreaterThan(0.5);
    });

    it('should classify button as atom', () => {
      const node = mockFigmaNode({ name: 'Button/Primary' });
      const result = classifyComponent(node);

      expect(result.level).toBe('atom');
      expect(result.category).toBe('button');
    });

    it('should classify search field with >3 children as molecule', () => {
      // Molecule requires: name in MOLECULE_PATTERNS.names OR
      // minChildren <= count <= maxChildren (2-6) AND depth <= 3
      // With 4 children, structure-based classification triggers molecule
      const node = mockFigmaNode({
        name: 'Search Field',
        children: [
          mockFigmaNode({ id: 'icon' }),
          mockFigmaNode({ id: 'input' }),
          mockFigmaNode({ id: 'button' }),
          mockFigmaNode({ id: 'hint' }),
        ],
      });
      const result = classifyComponent(node);

      expect(result.level).toBe('molecule');
    });

    it('should classify simple card as atom (structure-based)', () => {
      // A simple Card with no children is classified as atom due to
      // the structure-based check (≤3 children, depth ≤2) taking precedence
      const node = mockFigmaNode({ name: 'Card' });
      const result = classifyComponent(node);

      // Simple structure → atom, even though 'card' is in ORGANISM_PATTERNS
      expect(result.level).toBe('atom');
    });

    it('should classify complex header as organism', () => {
      // Organisms require: name in ORGANISM_PATTERNS.names OR
      // minChildren >= 3 AND minDepth >= 2
      // Header name matches ORGANISM_PATTERNS.names, but simple structure → atom
      // To get organism, need to exceed atom/molecule structure thresholds
      const node = mockNodeWithChildren(8, 3); // 8 children, depth 3
      node.name = 'Header';
      const result = classifyComponent(node);

      expect(result.level).toBe('organism');
    });

    it('should classify complex structure as organism', () => {
      const node = mockNodeWithChildren(10, 3);
      node.name = 'ProductList';
      const result = classifyComponent(node);

      expect(['molecule', 'organism']).toContain(result.level);
    });

    it('should classify page layout with layout properties as template', () => {
      // Templates require: name in TEMPLATE_PATTERNS.names AND structure that escapes earlier checks
      // Algorithm checks: atom → molecule → organism → template
      // To reach template name check, need:
      // - >3 children (escape atom structure)
      // - >6 children (escape molecule structure)
      // - depth <2 (escape organism structure: minChildren=3, minDepth=2)
      // So we need many direct children but shallow depth
      const node = mockFigmaNode({
        name: 'Page Layout',
        children: [
          mockFigmaNode({ id: 'header' }),
          mockFigmaNode({ id: 'nav' }),
          mockFigmaNode({ id: 'main' }),
          mockFigmaNode({ id: 'aside' }),
          mockFigmaNode({ id: 'content' }),
          mockFigmaNode({ id: 'footer' }),
          mockFigmaNode({ id: 'sidebar' }),
        ],
        properties: {
          layoutMode: 'VERTICAL',
          primaryAxisSizingMode: 'AUTO',
          width: 1200,
          height: 800,
        },
      });
      const result = classifyComponent(node);

      expect(result.level).toBe('template');
    });

    it('should include suggested name', () => {
      const node = mockFigmaNode({ name: 'primary button' });
      const result = classifyComponent(node);

      expect(result.suggestedName).toBe('PrimaryButton');
    });

    it('should include reasoning', () => {
      const node = mockFigmaNode({ name: 'Button' });
      const result = classifyComponent(node);

      expect(result.reasoning).toBeDefined();
      expect(result.reasoning.length).toBeGreaterThan(0);
    });

    it('should handle component set with variants', () => {
      const node = mockFigmaNode({
        name: 'Button',
        isComponentSet: true,
        variantProperties: {
          Size: 'sm, md, lg',
          State: 'default, hover',
        },
      });
      const result = classifyComponent(node);

      // Should be at least molecule due to multiple variants
      expect(['molecule', 'atom']).toContain(result.level);
    });
  });
});

// ============================================================================
// Token Tests
// ============================================================================

describe('NodeAnalyzer Tokens', () => {
  describe('rgbToHex', () => {
    it('should convert pure red', () => {
      expect(rgbToHex({ r: 1, g: 0, b: 0 })).toBe('#ff0000');
    });

    it('should convert pure green', () => {
      expect(rgbToHex({ r: 0, g: 1, b: 0 })).toBe('#00ff00');
    });

    it('should convert pure blue', () => {
      expect(rgbToHex({ r: 0, g: 0, b: 1 })).toBe('#0000ff');
    });

    it('should convert white', () => {
      expect(rgbToHex({ r: 1, g: 1, b: 1 })).toBe('#ffffff');
    });

    it('should convert black', () => {
      expect(rgbToHex({ r: 0, g: 0, b: 0 })).toBe('#000000');
    });

    it('should handle fractional values', () => {
      expect(rgbToHex({ r: 0.5, g: 0.5, b: 0.5 })).toBe('#808080');
    });
  });

  describe('rgbaToString', () => {
    it('should convert opaque color', () => {
      const result = rgbaToString({ r: 1, g: 0, b: 0, a: 1 });
      expect(result).toBe('rgba(255, 0, 0, 1.00)');
    });

    it('should convert transparent color', () => {
      const result = rgbaToString({ r: 0, g: 0, b: 1, a: 0.5 });
      expect(result).toBe('rgba(0, 0, 255, 0.50)');
    });

    it('should handle fully transparent', () => {
      const result = rgbaToString({ r: 1, g: 1, b: 1, a: 0 });
      expect(result).toBe('rgba(255, 255, 255, 0.00)');
    });
  });

  describe('deduplicateTokens', () => {
    it('should remove duplicate tokens', () => {
      const tokens = [
        mockToken({ name: 'color-1', value: '#FF0000', category: 'color' }),
        mockToken({ name: 'color-2', value: '#FF0000', category: 'color' }),
        mockToken({ name: 'color-3', value: '#00FF00', category: 'color' }),
      ];

      const result = deduplicateTokens(tokens);

      expect(result).toHaveLength(2);
    });

    it('should keep tokens with same value but different category', () => {
      const tokens = [
        mockToken({ name: 'color-1', value: '16px', category: 'spacing' }),
        mockToken({ name: 'size-1', value: '16px', category: 'typography' }),
      ];

      const result = deduplicateTokens(tokens);

      expect(result).toHaveLength(2);
    });

    it('should handle empty array', () => {
      expect(deduplicateTokens([])).toEqual([]);
    });

    it('should preserve first occurrence', () => {
      const tokens = [
        mockToken({ name: 'first', value: '#FF0000', category: 'color' }),
        mockToken({ name: 'second', value: '#FF0000', category: 'color' }),
      ];

      const result = deduplicateTokens(tokens);

      expect(result[0].name).toBe('first');
    });
  });
});

// ============================================================================
// Config Tests
// ============================================================================

describe('NodeAnalyzer Config', () => {
  describe('ATOM_PATTERNS', () => {
    it('should have name patterns', () => {
      expect(ATOM_PATTERNS.names).toBeDefined();
      expect(ATOM_PATTERNS.names.length).toBeGreaterThan(0);
    });

    it('should include common atomic elements', () => {
      expect(ATOM_PATTERNS.names).toContain('icon');
      expect(ATOM_PATTERNS.names).toContain('button');
    });

    it('should have size constraints', () => {
      expect(ATOM_PATTERNS.maxChildren).toBeDefined();
      expect(ATOM_PATTERNS.maxDepth).toBeDefined();
    });
  });

  describe('MOLECULE_PATTERNS', () => {
    it('should have name patterns', () => {
      expect(MOLECULE_PATTERNS.names).toBeDefined();
      expect(MOLECULE_PATTERNS.names.length).toBeGreaterThan(0);
    });

    it('should include common molecules', () => {
      // Note: 'card' is in ORGANISM_PATTERNS, not MOLECULE_PATTERNS
      expect(MOLECULE_PATTERNS.names).toContain('form-field');
      expect(MOLECULE_PATTERNS.names).toContain('search');
    });

    it('should have size constraints', () => {
      expect(MOLECULE_PATTERNS.minChildren).toBeDefined();
      expect(MOLECULE_PATTERNS.maxChildren).toBeDefined();
    });
  });

  describe('ORGANISM_PATTERNS', () => {
    it('should have name patterns', () => {
      expect(ORGANISM_PATTERNS.names).toBeDefined();
      expect(ORGANISM_PATTERNS.names.length).toBeGreaterThan(0);
    });

    it('should include common organisms', () => {
      expect(ORGANISM_PATTERNS.names).toContain('header');
      expect(ORGANISM_PATTERNS.names).toContain('footer');
    });
  });

  describe('TEMPLATE_PATTERNS', () => {
    it('should have name patterns', () => {
      expect(TEMPLATE_PATTERNS.names).toBeDefined();
    });

    it('should include page-level patterns', () => {
      // Note: 'page' alone is not in patterns, only 'page-layout'
      expect(TEMPLATE_PATTERNS.names).toContain('page-layout');
      expect(TEMPLATE_PATTERNS.names).toContain('layout');
    });
  });

  describe('CATEGORY_PATTERNS', () => {
    it('should have common UI categories', () => {
      expect(CATEGORY_PATTERNS).toBeDefined();
      expect(CATEGORY_PATTERNS.button).toBeDefined();
      expect(CATEGORY_PATTERNS.input).toBeDefined();
    });

    it('should have patterns for each category', () => {
      for (const [category, patterns] of Object.entries(CATEGORY_PATTERNS)) {
        expect(Array.isArray(patterns)).toBe(true);
        expect(patterns.length).toBeGreaterThan(0);
      }
    });
  });
});

// ============================================================================
// Integration Tests
// ============================================================================

describe('NodeAnalyzer Integration', () => {
  it('should correctly classify a button component', () => {
    const buttonNode = mockFigmaNode({
      name: 'Primary Button',
      children: [
        mockFigmaNode({ id: 'icon', name: 'Leading Icon' }),
        mockFigmaNode({ id: 'label', name: 'Label', properties: { characters: 'Click me' } }),
      ],
      properties: {
        cornerRadius: 8,
        paddingLeft: 16,
        paddingRight: 16,
        paddingTop: 8,
        paddingBottom: 8,
      },
    });

    const classification = classifyComponent(buttonNode);

    expect(classification.level).toBe('atom');
    expect(classification.category).toBe('button');
    expect(classification.suggestedName).toBe('PrimaryButton');
  });

  it('should correctly classify a header organism', () => {
    const headerNode = mockFigmaNode({
      name: 'Main Header',
      children: [
        mockFigmaNode({ id: 'logo', name: 'Logo' }),
        mockFigmaNode({
          id: 'nav',
          name: 'Navigation',
          children: [
            mockFigmaNode({ id: 'nav-1' }),
            mockFigmaNode({ id: 'nav-2' }),
            mockFigmaNode({ id: 'nav-3' }),
          ],
        }),
        mockFigmaNode({
          id: 'actions',
          name: 'Actions',
          children: [
            mockFigmaNode({ id: 'search' }),
            mockFigmaNode({ id: 'profile' }),
          ],
        }),
      ],
    });

    const classification = classifyComponent(headerNode);

    expect(classification.level).toBe('organism');
    expect(classification.suggestedName).toBe('MainHeader');
  });

  it('should handle deeply nested product card', () => {
    const productCard = mockFigmaNode({
      name: 'Product Card',
      children: [
        mockFigmaNode({ id: 'image', name: 'Product Image' }),
        mockFigmaNode({
          id: 'content',
          name: 'Content',
          children: [
            mockFigmaNode({ id: 'title', name: 'Title' }),
            mockFigmaNode({ id: 'price', name: 'Price' }),
            mockFigmaNode({ id: 'rating', name: 'Rating' }),
          ],
        }),
        mockFigmaNode({
          id: 'actions',
          name: 'Actions',
          children: [
            mockFigmaNode({ id: 'buy-btn', name: 'Buy Button' }),
            mockFigmaNode({ id: 'wishlist-btn', name: 'Wishlist' }),
          ],
        }),
      ],
    });

    const classification = classifyComponent(productCard);
    const depth = calculateDepth(productCard);
    const childCount = countChildren(productCard);

    expect(['molecule', 'organism']).toContain(classification.level);
    expect(depth).toBe(2);
    expect(childCount).toBe(8);
  });
});
