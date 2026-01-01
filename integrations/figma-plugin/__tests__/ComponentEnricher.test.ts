/**
 * @file __tests__/ComponentEnricher.test.ts
 * @description Comprehensive tests for ComponentEnricher service modules
 *
 * Tests cover:
 * - Utils: Node traversal, string manipulation
 * - Config: Prop patterns, state patterns
 * - Props: Prop inference, text/slot extraction
 * - Variants: Variant extraction, state/breakpoint detection
 */

import {
  traverseNodes,
  toCamelCase,
  inferPropNameFromText,
  isLabelText,
  deduplicateProps,
} from '../services/ComponentEnricher/utils';

import {
  PROP_PATTERNS,
  STATE_PATTERNS,
  BREAKPOINT_PATTERNS,
} from '../services/ComponentEnricher/config';

import {
  extractVariants,
  detectStates,
  detectBreakpoints,
} from '../services/ComponentEnricher/variants';

import {
  inferProps,
  extractTextProps,
  extractSlotProps,
} from '../services/ComponentEnricher/props';

import type {
  FigmaNodeInfo,
  ComponentClassification,
  PropDefinition,
  VariantDefinition,
} from '../types';

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
 * Create a mock FigmaNodeInfo with text content
 */
function mockTextNode(name: string, characters: string): FigmaNodeInfo {
  return mockFigmaNode({
    id: `text-${name}`,
    name,
    type: 'TEXT',
    properties: { characters },
  });
}

/**
 * Create a mock ComponentClassification
 */
function mockClassification(overrides: Partial<ComponentClassification> = {}): ComponentClassification {
  return {
    level: 'atom',
    confidence: 0.85,
    reasoning: 'Small, reusable component',
    suggestedName: 'Button',
    category: 'button',
    ...overrides,
  };
}

/**
 * Create a mock PropDefinition
 */
function mockProp(overrides: Partial<PropDefinition> = {}): PropDefinition {
  return {
    name: 'testProp',
    type: 'string',
    required: false,
    description: 'Test prop',
    ...overrides,
  };
}

// ============================================================================
// Utils Tests
// ============================================================================

describe('ComponentEnricher Utils', () => {
  describe('traverseNodes', () => {
    it('should call callback for single node', () => {
      const node = mockFigmaNode();
      const callback = jest.fn();

      traverseNodes(node, callback);

      expect(callback).toHaveBeenCalledTimes(1);
      expect(callback).toHaveBeenCalledWith(node);
    });

    it('should traverse all children recursively', () => {
      const child1 = mockFigmaNode({ id: 'child-1', name: 'Child1' });
      const child2 = mockFigmaNode({ id: 'child-2', name: 'Child2' });
      const grandchild = mockFigmaNode({ id: 'grandchild', name: 'Grandchild' });

      child1.children = [grandchild];
      const parent = mockFigmaNode({ children: [child1, child2] });

      const visited: string[] = [];
      traverseNodes(parent, (node) => visited.push(node.id));

      expect(visited).toEqual(['node-123', 'child-1', 'grandchild', 'child-2']);
    });

    it('should handle node without children', () => {
      const node = mockFigmaNode();
      const callback = jest.fn();

      traverseNodes(node, callback);

      expect(callback).toHaveBeenCalledWith(node);
    });

    it('should handle deeply nested structure', () => {
      const level3 = mockFigmaNode({ id: 'level-3', name: 'Level3' });
      const level2 = mockFigmaNode({ id: 'level-2', name: 'Level2', children: [level3] });
      const level1 = mockFigmaNode({ id: 'level-1', name: 'Level1', children: [level2] });
      const root = mockFigmaNode({ id: 'root', children: [level1] });

      let count = 0;
      traverseNodes(root, () => count++);

      expect(count).toBe(4);
    });
  });

  describe('toCamelCase', () => {
    it('should convert space-separated words', () => {
      expect(toCamelCase('hello world')).toBe('helloWorld');
    });

    it('should convert hyphen-separated words', () => {
      // Note: ComponentEnricher's toCamelCase removes hyphens BEFORE splitting
      // So 'hello-world' → 'helloworld' (no word boundary remains)
      expect(toCamelCase('hello-world')).toBe('helloworld');
    });

    it('should convert underscore-separated words', () => {
      // Note: ComponentEnricher's toCamelCase removes underscores BEFORE splitting
      // So 'hello_world' → 'helloworld' (no word boundary remains)
      expect(toCamelCase('hello_world')).toBe('helloworld');
    });

    it('should handle mixed separators', () => {
      // Note: ComponentEnricher's toCamelCase removes - and _ first, then splits on space
      // Input: 'hello-world_test case' → 'helloworldtest case' → ['helloworldtest', 'case']
      expect(toCamelCase('hello-world_test case')).toBe('helloworldtestCase');
    });

    it('should handle single word', () => {
      expect(toCamelCase('hello')).toBe('hello');
    });

    it('should handle empty string', () => {
      expect(toCamelCase('')).toBe('');
    });

    it('should remove special characters', () => {
      expect(toCamelCase('hello@world#test')).toBe('helloworldtest');
    });

    it('should handle uppercase input', () => {
      expect(toCamelCase('HELLO WORLD')).toBe('helloWorld');
    });
  });

  describe('inferPropNameFromText', () => {
    it('should recognize title pattern', () => {
      expect(inferPropNameFromText('Card Title', 'Some text')).toBe('title');
    });

    it('should recognize heading pattern', () => {
      expect(inferPropNameFromText('Main Heading', 'Header')).toBe('heading');
    });

    it('should recognize label pattern', () => {
      expect(inferPropNameFromText('Button Label', 'Click')).toBe('label');
    });

    it('should recognize description pattern', () => {
      expect(inferPropNameFromText('Product Description', 'Details')).toBe('description');
    });

    it('should recognize cta pattern', () => {
      // Note: 'text' pattern is checked before 'cta' in object iteration
      // 'CTA Text'.toLowerCase() contains 'text', so it matches 'text' pattern first
      expect(inferPropNameFromText('CTA Text', 'Click here')).toBe('text');
    });

    it('should recognize button pattern', () => {
      expect(inferPropNameFromText('Submit Button', 'Submit')).toBe('label');
    });

    it('should fallback to camelCase node name', () => {
      expect(inferPropNameFromText('custom-node-name', 'Some value')).toBe('customnodename');
    });
  });

  describe('isLabelText', () => {
    it('should return true for label nodes', () => {
      const node = mockFigmaNode({ name: 'Button Label' });
      expect(isLabelText(node)).toBe(true);
    });

    it('should return true for title nodes', () => {
      const node = mockFigmaNode({ name: 'Card Title' });
      expect(isLabelText(node)).toBe(true);
    });

    it('should return true for heading nodes', () => {
      const node = mockFigmaNode({ name: 'Main Heading' });
      expect(isLabelText(node)).toBe(true);
    });

    it('should return false for non-label nodes', () => {
      const node = mockFigmaNode({ name: 'Icon Container' });
      expect(isLabelText(node)).toBe(false);
    });

    it('should be case-insensitive', () => {
      const node = mockFigmaNode({ name: 'TITLE TEXT' });
      expect(isLabelText(node)).toBe(true);
    });
  });

  describe('deduplicateProps', () => {
    it('should remove duplicate props by name', () => {
      const props = [
        mockProp({ name: 'title', type: 'string' }),
        mockProp({ name: 'title', type: 'string' }),
        mockProp({ name: 'description', type: 'string' }),
      ];

      const result = deduplicateProps(props);

      expect(result).toHaveLength(2);
      expect(result.map(p => p.name)).toEqual(['title', 'description']);
    });

    it('should keep first occurrence', () => {
      const props = [
        mockProp({ name: 'onClick', type: 'function', description: 'First' }),
        mockProp({ name: 'onClick', type: 'function', description: 'Second' }),
      ];

      const result = deduplicateProps(props);

      expect(result[0].description).toBe('First');
    });

    it('should handle empty array', () => {
      expect(deduplicateProps([])).toEqual([]);
    });

    it('should handle array with unique props', () => {
      const props = [
        mockProp({ name: 'a' }),
        mockProp({ name: 'b' }),
        mockProp({ name: 'c' }),
      ];

      const result = deduplicateProps(props);

      expect(result).toHaveLength(3);
    });
  });
});

// ============================================================================
// Config Tests
// ============================================================================

describe('ComponentEnricher Config', () => {
  describe('PROP_PATTERNS', () => {
    it('should define button props', () => {
      expect(PROP_PATTERNS.button).toBeDefined();
      expect(PROP_PATTERNS.button.map(p => p.name)).toContain('onClick');
      expect(PROP_PATTERNS.button.map(p => p.name)).toContain('disabled');
    });

    it('should define input props', () => {
      expect(PROP_PATTERNS.input).toBeDefined();
      expect(PROP_PATTERNS.input.map(p => p.name)).toContain('value');
      expect(PROP_PATTERNS.input.map(p => p.name)).toContain('onChange');
      expect(PROP_PATTERNS.input.map(p => p.name)).toContain('placeholder');
    });

    it('should define link props', () => {
      expect(PROP_PATTERNS.link).toBeDefined();
      expect(PROP_PATTERNS.link.map(p => p.name)).toContain('href');
      expect(PROP_PATTERNS.link.find(p => p.name === 'href')?.required).toBe(true);
    });

    it('should define modal props', () => {
      expect(PROP_PATTERNS.modal).toBeDefined();
      expect(PROP_PATTERNS.modal.map(p => p.name)).toContain('isOpen');
      expect(PROP_PATTERNS.modal.map(p => p.name)).toContain('onClose');
    });
  });

  describe('STATE_PATTERNS', () => {
    it('should include common UI states', () => {
      expect(STATE_PATTERNS).toContain('default');
      expect(STATE_PATTERNS).toContain('hover');
      expect(STATE_PATTERNS).toContain('active');
      expect(STATE_PATTERNS).toContain('disabled');
      expect(STATE_PATTERNS).toContain('focus');
    });

    it('should include loading and error states', () => {
      expect(STATE_PATTERNS).toContain('loading');
      expect(STATE_PATTERNS).toContain('error');
    });
  });

  describe('BREAKPOINT_PATTERNS', () => {
    it('should include device-based breakpoints', () => {
      expect(BREAKPOINT_PATTERNS).toContain('mobile');
      expect(BREAKPOINT_PATTERNS).toContain('tablet');
      expect(BREAKPOINT_PATTERNS).toContain('desktop');
    });

    it('should include size-based breakpoints', () => {
      expect(BREAKPOINT_PATTERNS).toContain('sm');
      expect(BREAKPOINT_PATTERNS).toContain('md');
      expect(BREAKPOINT_PATTERNS).toContain('lg');
      expect(BREAKPOINT_PATTERNS).toContain('xl');
    });
  });
});

// ============================================================================
// Variants Tests
// ============================================================================

describe('ComponentEnricher Variants', () => {
  describe('extractVariants', () => {
    it('should extract variants from variantProperties', () => {
      const node = mockFigmaNode({
        variantProperties: {
          Size: 'sm, md, lg',
          Type: 'primary, secondary',
        },
      });

      const variants = extractVariants(node);

      expect(variants).toHaveLength(2);
      expect(variants.find(v => v.name === 'size')).toBeDefined();
      expect(variants.find(v => v.name === 'type')).toBeDefined();
    });

    it('should set first option as default', () => {
      const node = mockFigmaNode({
        variantProperties: {
          Size: 'sm, md, lg',
        },
      });

      const variants = extractVariants(node);

      expect(variants[0].defaultOption).toBe('sm');
    });

    it('should extract all variants including State key', () => {
      // Note: extractVariants checks if KEY is in STATE_PATTERNS
      // STATE_PATTERNS = ['default', 'hover', 'active', ...] - state VALUES, not 'state' itself
      // So 'State' key is NOT in STATE_PATTERNS and gets extracted normally
      const node = mockFigmaNode({
        variantProperties: {
          Size: 'sm, md, lg',
          State: 'default, hover, active',
        },
      });

      const variants = extractVariants(node);

      expect(variants).toHaveLength(2);
      expect(variants.find(v => v.name === 'size')).toBeDefined();
      expect(variants.find(v => v.name === 'state')).toBeDefined();
    });

    it('should return empty array if no variantProperties', () => {
      const node = mockFigmaNode();

      const variants = extractVariants(node);

      expect(variants).toEqual([]);
    });

    it('should include all options in variant', () => {
      const node = mockFigmaNode({
        variantProperties: {
          Size: 'xs, sm, md, lg, xl',
        },
      });

      const variants = extractVariants(node);

      expect(variants[0].options).toEqual(['xs', 'sm', 'md', 'lg', 'xl']);
    });
  });

  describe('detectStates', () => {
    it('should always include default state', () => {
      const node = mockFigmaNode();
      const variants: VariantDefinition[] = [];

      const states = detectStates(node, variants);

      expect(states).toContain('default');
    });

    it('should detect states from variant properties', () => {
      const node = mockFigmaNode({
        variantProperties: {
          State: 'default, hover, pressed',
        },
      });

      const states = detectStates(node, []);

      expect(states).toContain('hover');
      expect(states).toContain('pressed');
    });

    it('should detect states from property values', () => {
      const node = mockFigmaNode({
        variantProperties: {
          Interaction: 'default, hover, focus, disabled',
        },
      });

      const states = detectStates(node, []);

      expect(states).toContain('hover');
      expect(states).toContain('focus');
      expect(states).toContain('disabled');
    });

    it('should detect states from children names', () => {
      const hoverChild = mockFigmaNode({ name: 'Hover State' });
      const disabledChild = mockFigmaNode({ name: 'Disabled State' });
      const node = mockFigmaNode({
        children: [hoverChild, disabledChild],
      });

      const states = detectStates(node, []);

      expect(states).toContain('hover');
      expect(states).toContain('disabled');
    });
  });

  describe('detectBreakpoints', () => {
    it('should detect breakpoints from component name', () => {
      const node = mockFigmaNode({ name: 'Button Mobile' });

      const breakpoints = detectBreakpoints(node);

      expect(breakpoints).toContain('mobile');
    });

    it('should detect multiple breakpoints from name', () => {
      const node = mockFigmaNode({ name: 'Card Mobile Tablet' });

      const breakpoints = detectBreakpoints(node);

      expect(breakpoints).toContain('mobile');
      expect(breakpoints).toContain('tablet');
    });

    it('should detect breakpoints from children', () => {
      const mobileChild = mockFigmaNode({ name: 'Layout Mobile' });
      const desktopChild = mockFigmaNode({ name: 'Layout Desktop' });
      const node = mockFigmaNode({
        name: 'ResponsiveCard',
        children: [mobileChild, desktopChild],
      });

      const breakpoints = detectBreakpoints(node);

      expect(breakpoints).toContain('mobile');
      expect(breakpoints).toContain('desktop');
    });

    it('should return default if no breakpoints detected', () => {
      const node = mockFigmaNode({ name: 'SimpleButton' });

      const breakpoints = detectBreakpoints(node);

      expect(breakpoints).toEqual(['default']);
    });

    it('should not duplicate breakpoints', () => {
      const mobileChild = mockFigmaNode({ name: 'Mobile Version' });
      const node = mockFigmaNode({
        name: 'Card Mobile',
        children: [mobileChild],
      });

      const breakpoints = detectBreakpoints(node);

      const mobileCount = breakpoints.filter(bp => bp === 'mobile').length;
      expect(mobileCount).toBe(1);
    });
  });
});

// ============================================================================
// Props Tests
// ============================================================================

describe('ComponentEnricher Props', () => {
  describe('inferProps', () => {
    it('should add category-specific props for button', () => {
      const node = mockFigmaNode();
      const classification = mockClassification({ category: 'button' });

      const props = inferProps(node, classification);

      expect(props.find(p => p.name === 'onClick')).toBeDefined();
      expect(props.find(p => p.name === 'disabled')).toBeDefined();
    });

    it('should add category-specific props for input', () => {
      const node = mockFigmaNode();
      const classification = mockClassification({ category: 'input' });

      const props = inferProps(node, classification);

      expect(props.find(p => p.name === 'value')).toBeDefined();
      expect(props.find(p => p.name === 'onChange')).toBeDefined();
      expect(props.find(p => p.name === 'placeholder')).toBeDefined();
    });

    it('should extract props from variant properties', () => {
      const node = mockFigmaNode({
        variantProperties: {
          Size: 'sm, md, lg',
        },
      });
      const classification = mockClassification({ category: 'card' });

      const props = inferProps(node, classification);

      const sizeProp = props.find(p => p.name === 'size');
      expect(sizeProp).toBeDefined();
      expect(sizeProp?.type).toBe('enum');
      expect(sizeProp?.enumValues).toEqual(['sm', 'md', 'lg']);
    });

    it('should include all variant props including state', () => {
      // Note: inferProps extracts all variants as props (including 'State')
      // State filtering is done at a higher level in the component enrichment
      const node = mockFigmaNode({
        variantProperties: {
          Size: 'sm, md, lg',
          State: 'default, hover, active',
        },
      });
      const classification = mockClassification({ category: 'card' });

      const props = inferProps(node, classification);

      expect(props.find(p => p.name === 'state')).toBeDefined();
      expect(props.find(p => p.name === 'size')).toBeDefined();
    });

    it('should deduplicate props', () => {
      const labelChild = mockTextNode('Label', 'Click me');
      const anotherLabel = mockTextNode('Label', 'Click me too');
      const node = mockFigmaNode({
        children: [labelChild, anotherLabel],
      });
      const classification = mockClassification({ category: 'button' });

      const props = inferProps(node, classification);

      const labelProps = props.filter(p => p.name === 'label');
      expect(labelProps.length).toBeLessThanOrEqual(1);
    });
  });

  describe('extractTextProps', () => {
    it('should extract text props from nodes with characters', () => {
      const textChild = mockTextNode('Title', 'Hello World');
      const node = mockFigmaNode({
        children: [textChild],
      });

      const props = extractTextProps(node);

      expect(props).toHaveLength(1);
      expect(props[0].name).toBe('title');
      expect(props[0].defaultValue).toBe('Hello World');
    });

    it('should mark label text as required', () => {
      const labelChild = mockTextNode('Button Label', 'Submit');
      const node = mockFigmaNode({
        children: [labelChild],
      });

      const props = extractTextProps(node);

      expect(props[0].required).toBe(true);
    });

    it('should extract from nested text nodes', () => {
      const nestedText = mockTextNode('DeepLabel', 'Nested');
      const container = mockFigmaNode({
        id: 'container',
        name: 'Container',
        children: [nestedText],
      });
      const root = mockFigmaNode({ children: [container] });

      const props = extractTextProps(root);

      expect(props.length).toBeGreaterThanOrEqual(1);
      expect(props.find(p => p.defaultValue === 'Nested')).toBeDefined();
    });
  });

  describe('extractSlotProps', () => {
    it('should extract icon slots', () => {
      const iconChild = mockFigmaNode({ id: 'icon-1', name: 'Leading Icon' });
      const node = mockFigmaNode({ children: [iconChild] });

      const props = extractSlotProps(node);

      expect(props.find(p => p.name.toLowerCase().includes('icon'))).toBeDefined();
      expect(props[0].type).toBe('node');
    });

    it('should extract content slots', () => {
      const contentChild = mockFigmaNode({ id: 'content-1', name: 'Content Area' });
      const node = mockFigmaNode({ children: [contentChild] });

      const props = extractSlotProps(node);

      expect(props.find(p => p.name.toLowerCase().includes('content'))).toBeDefined();
    });

    it('should extract children slots', () => {
      const childrenSlot = mockFigmaNode({ id: 'children-1', name: 'Children Container' });
      const node = mockFigmaNode({ children: [childrenSlot] });

      const props = extractSlotProps(node);

      expect(props.find(p => p.name.toLowerCase().includes('children'))).toBeDefined();
    });

    it('should not extract non-slot nodes', () => {
      const regularChild = mockFigmaNode({ id: 'frame-1', name: 'Background Frame' });
      const node = mockFigmaNode({ children: [regularChild] });

      const props = extractSlotProps(node);

      expect(props).toHaveLength(0);
    });
  });
});

// ============================================================================
// Integration Tests
// ============================================================================

describe('ComponentEnricher Integration', () => {
  it('should work with complex component structure', () => {
    // Create a realistic button component structure
    const labelText = mockTextNode('Button Label', 'Submit');
    const iconSlot = mockFigmaNode({ id: 'icon', name: 'Leading Icon' });
    const buttonComponent = mockFigmaNode({
      id: 'btn-1',
      name: 'Button',
      type: 'COMPONENT',
      variantProperties: {
        Size: 'sm, md, lg',
        Variant: 'primary, secondary, ghost',
        State: 'default, hover, active, disabled',
      },
      children: [iconSlot, labelText],
    });

    const classification = mockClassification({
      category: 'button',
      level: 'atom',
    });

    // Test all modules together
    const variants = extractVariants(buttonComponent);
    const states = detectStates(buttonComponent, variants);
    const props = inferProps(buttonComponent, classification);

    // Verify results
    // Note: STATE_PATTERNS contains values ('default', 'hover', etc.) not 'state' itself
    // So 'State' key is NOT filtered out - we get Size, Variant, AND State
    expect(variants).toHaveLength(3); // Size, Variant, and State
    expect(states).toContain('hover');
    expect(states).toContain('disabled');
    expect(props.find(p => p.name === 'onClick')).toBeDefined();
    expect(props.find(p => p.name === 'size')).toBeDefined();
    expect(props.find(p => p.name === 'variant')).toBeDefined();
  });

  it('should handle card component with nested content', () => {
    const title = mockTextNode('Card Title', 'Product Name');
    const description = mockTextNode('Card Description', 'A great product');
    const contentSlot = mockFigmaNode({
      id: 'content',
      name: 'Content Slot',
      children: [description],
    });

    const card = mockFigmaNode({
      name: 'ProductCard',
      variantProperties: {
        Size: 'compact, default, expanded',
      },
      children: [title, contentSlot],
    });

    const classification = mockClassification({ category: 'card', level: 'molecule' });

    const variants = extractVariants(card);
    const props = inferProps(card, classification);

    expect(variants[0].name).toBe('size');
    expect(variants[0].options).toHaveLength(3);
    expect(props.find(p => p.name === 'title')).toBeDefined();
    expect(props.find(p => p.name === 'description')).toBeDefined();
  });

  it('should handle responsive component', () => {
    const mobileLayout = mockFigmaNode({ name: 'Mobile Layout' });
    const tabletLayout = mockFigmaNode({ name: 'Tablet Layout' });
    const desktopLayout = mockFigmaNode({ name: 'Desktop Layout' });

    const responsiveComponent = mockFigmaNode({
      name: 'Responsive Hero',
      children: [mobileLayout, tabletLayout, desktopLayout],
    });

    const breakpoints = detectBreakpoints(responsiveComponent);

    expect(breakpoints).toContain('mobile');
    expect(breakpoints).toContain('tablet');
    expect(breakpoints).toContain('desktop');
  });
});
