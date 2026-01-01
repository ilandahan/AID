/**
 * @file __tests__/ContentExtractor.test.ts
 * @description Comprehensive tests for ContentExtractor service modules
 *
 * Tests cover:
 * - Utils: String manipulation functions
 * - Properties: Property and text extraction
 * - Extraction: Component extraction from Figma nodes
 * - Formatters: TypeScript, JSON, CSV export
 */

import {
  toVariableName,
  toCamelCase,
  escapeString,
} from '../services/ContentExtractor/utils';

import {
  toTypeScript,
  toJSON,
  toCSV,
  exportAllFormats,
} from '../services/ContentExtractor/formatters';

import type { ExtractedComponent, ExtractedText, ExtractedVariant } from '../services/ContentExtractor/types';

// ============================================================================
// Test Helpers
// ============================================================================

/**
 * Create a mock ExtractedText for testing
 */
function mockExtractedText(overrides: Partial<ExtractedText> = {}): ExtractedText {
  return {
    layerName: 'Label',
    value: 'Default Text',
    propertyName: undefined,
    fontFamily: 'Inter',
    fontSize: 14,
    fontWeight: 400,
    ...overrides,
  };
}

/**
 * Create a mock ExtractedVariant for testing
 */
function mockExtractedVariant(overrides: Partial<ExtractedVariant> = {}): ExtractedVariant {
  return {
    name: 'Default',
    properties: {},
    texts: [mockExtractedText()],
    ...overrides,
  };
}

/**
 * Create a mock ExtractedComponent for testing
 */
function mockExtractedComponent(overrides: Partial<ExtractedComponent> = {}): ExtractedComponent {
  return {
    name: 'Button',
    type: 'COMPONENT',
    description: 'A button component',
    properties: [],
    variants: [mockExtractedVariant()],
    defaultContent: { Label: 'Default Text' },
    ...overrides,
  };
}

// ============================================================================
// Utils Tests
// ============================================================================

describe('ContentExtractor Utils', () => {
  describe('toVariableName', () => {
    it('should remove slashes and convert to valid variable name', () => {
      expect(toVariableName('Button/Primary')).toBe('ButtonPrimary');
    });

    it('should remove spaces', () => {
      expect(toVariableName('My Component')).toBe('MyComponent');
    });

    it('should remove hyphens', () => {
      expect(toVariableName('my-component')).toBe('mycomponent');
    });

    it('should remove special characters', () => {
      expect(toVariableName('Button@Primary#1')).toBe('ButtonPrimary1');
    });

    it('should handle multiple consecutive special characters', () => {
      expect(toVariableName('Button///Primary---Secondary')).toBe('ButtonPrimarySecondary');
    });

    it('should handle empty string', () => {
      expect(toVariableName('')).toBe('');
    });

    it('should preserve numbers', () => {
      expect(toVariableName('Button123')).toBe('Button123');
    });

    it('should handle component names with emojis', () => {
      expect(toVariableName('Button 🎨 Primary')).toBe('ButtonPrimary');
    });
  });

  describe('toCamelCase', () => {
    it('should convert space-separated words to camelCase', () => {
      expect(toCamelCase('hello world')).toBe('helloWorld');
    });

    it('should convert hyphen-separated words to camelCase', () => {
      expect(toCamelCase('hello-world')).toBe('helloWorld');
    });

    it('should convert underscore-separated words to camelCase', () => {
      expect(toCamelCase('hello_world')).toBe('helloWorld');
    });

    it('should handle PascalCase input', () => {
      expect(toCamelCase('HelloWorld')).toBe('helloWorld');
    });

    it('should handle mixed separators', () => {
      expect(toCamelCase('hello-world_test case')).toBe('helloWorldTestCase');
    });

    it('should handle empty string', () => {
      expect(toCamelCase('')).toBe('');
    });

    it('should handle single word', () => {
      expect(toCamelCase('hello')).toBe('hello');
    });

    it('should remove special characters', () => {
      expect(toCamelCase('hello@world#test')).toBe('helloWorldTest');
    });
  });

  describe('escapeString', () => {
    it('should escape backslashes', () => {
      expect(escapeString('path\\to\\file')).toBe('path\\\\to\\\\file');
    });

    it('should escape double quotes', () => {
      expect(escapeString('say "hello"')).toBe('say \\"hello\\"');
    });

    it('should escape newlines', () => {
      expect(escapeString('line1\nline2')).toBe('line1\\nline2');
    });

    it('should handle multiple escape sequences', () => {
      expect(escapeString('path\\to\n"file"')).toBe('path\\\\to\\n\\"file\\"');
    });

    it('should handle empty string', () => {
      expect(escapeString('')).toBe('');
    });

    it('should handle string without special characters', () => {
      expect(escapeString('normal text')).toBe('normal text');
    });
  });
});

// ============================================================================
// Formatters Tests
// ============================================================================

describe('ContentExtractor Formatters', () => {
  describe('toTypeScript', () => {
    it('should generate valid TypeScript interface and const', () => {
      const components = [mockExtractedComponent()];
      const output = toTypeScript(components);

      expect(output).toContain('// Auto-generated content from Figma');
      expect(output).toContain('export interface ButtonContent');
      expect(output).toContain('label: string;');
      expect(output).toContain('export const ButtonContent: ButtonContent');
      expect(output).toContain('label: "Default Text"');
    });

    it('should handle multiple components', () => {
      const components = [
        mockExtractedComponent({ name: 'Button', defaultContent: { Label: 'Click' } }),
        mockExtractedComponent({ name: 'Card', defaultContent: { Title: 'Card Title' } }),
      ];
      const output = toTypeScript(components);

      expect(output).toContain('export interface ButtonContent');
      expect(output).toContain('export interface CardContent');
      expect(output).toContain('export const ButtonContent');
      expect(output).toContain('export const CardContent');
    });

    it('should convert property names to camelCase', () => {
      const components = [
        mockExtractedComponent({
          defaultContent: {
            'Primary Label': 'Hello',
            'secondary-text': 'World',
          },
        }),
      ];
      const output = toTypeScript(components);

      expect(output).toContain('primaryLabel: string;');
      expect(output).toContain('secondaryText: string;');
    });

    it('should escape special characters in values', () => {
      const components = [
        mockExtractedComponent({
          defaultContent: { Label: 'Say "Hello"\nWorld' },
        }),
      ];
      const output = toTypeScript(components);

      expect(output).toContain('label: "Say \\"Hello\\"\\nWorld"');
    });

    it('should handle empty components array', () => {
      const output = toTypeScript([]);
      expect(output).toContain('// Auto-generated content from Figma');
      expect(output).not.toContain('export interface');
    });

    it('should include generation timestamp', () => {
      const output = toTypeScript([]);
      expect(output).toContain('// Generated at:');
    });
  });

  describe('toJSON', () => {
    it('should generate valid JSON with metadata', () => {
      const components = [mockExtractedComponent()];
      const output = toJSON(components);
      const parsed = JSON.parse(output);

      expect(parsed.Button).toBeDefined();
      expect(parsed.Button._meta).toBeDefined();
      expect(parsed.Button._meta.name).toBe('Button');
      expect(parsed.Button._meta.type).toBe('COMPONENT');
      expect(parsed.Button.content).toEqual({ Label: 'Default Text' });
    });

    it('should include description in metadata', () => {
      const components = [
        mockExtractedComponent({ description: 'A primary button' }),
      ];
      const output = toJSON(components);
      const parsed = JSON.parse(output);

      expect(parsed.Button._meta.description).toBe('A primary button');
    });

    it('should include property names in metadata', () => {
      const components = [
        mockExtractedComponent({
          properties: [
            { name: 'size', type: 'VARIANT', variantOptions: ['sm', 'md', 'lg'] },
            { name: 'disabled', type: 'BOOLEAN', defaultValue: false },
          ],
        }),
      ];
      const output = toJSON(components);
      const parsed = JSON.parse(output);

      expect(parsed.Button._meta.properties).toEqual(['size', 'disabled']);
    });

    it('should include variant count in metadata', () => {
      const components = [
        mockExtractedComponent({
          variants: [
            mockExtractedVariant({ name: 'Default' }),
            mockExtractedVariant({ name: 'Hover' }),
            mockExtractedVariant({ name: 'Pressed' }),
          ],
        }),
      ];
      const output = toJSON(components);
      const parsed = JSON.parse(output);

      expect(parsed.Button._meta.variantCount).toBe(3);
    });

    it('should handle multiple components', () => {
      const components = [
        mockExtractedComponent({ name: 'Button' }),
        mockExtractedComponent({ name: 'Card' }),
      ];
      const output = toJSON(components);
      const parsed = JSON.parse(output);

      expect(Object.keys(parsed)).toEqual(['Button', 'Card']);
    });

    it('should handle empty components array', () => {
      const output = toJSON([]);
      expect(JSON.parse(output)).toEqual({});
    });
  });

  describe('toCSV', () => {
    it('should generate valid CSV with headers', () => {
      const components = [mockExtractedComponent()];
      const output = toCSV(components);
      const rows = output.split('\n');

      expect(rows[0]).toBe('"Component","Property","Value"');
    });

    it('should include component data rows', () => {
      const components = [
        mockExtractedComponent({
          name: 'Button',
          defaultContent: { Label: 'Click Me' },
        }),
      ];
      const output = toCSV(components);
      const rows = output.split('\n');

      expect(rows[1]).toBe('"Button","Label","Click Me"');
    });

    it('should handle multiple properties', () => {
      const components = [
        mockExtractedComponent({
          name: 'Card',
          defaultContent: {
            Title: 'Card Title',
            Description: 'Card description text',
          },
        }),
      ];
      const output = toCSV(components);
      const rows = output.split('\n');

      expect(rows.length).toBe(3); // header + 2 data rows
      expect(rows[1]).toContain('Title');
      expect(rows[2]).toContain('Description');
    });

    it('should escape double quotes in values', () => {
      const components = [
        mockExtractedComponent({
          defaultContent: { Label: 'Say "Hello"' },
        }),
      ];
      const output = toCSV(components);

      expect(output).toContain('"Say ""Hello"""');
    });

    it('should handle multiple components', () => {
      const components = [
        mockExtractedComponent({ name: 'Button', defaultContent: { Label: 'Click' } }),
        mockExtractedComponent({ name: 'Card', defaultContent: { Title: 'Title' } }),
      ];
      const output = toCSV(components);
      const rows = output.split('\n');

      expect(rows.length).toBe(3); // header + 2 rows
      expect(rows[1]).toContain('Button');
      expect(rows[2]).toContain('Card');
    });

    it('should handle empty components array', () => {
      const output = toCSV([]);
      const rows = output.split('\n');

      expect(rows.length).toBe(1);
      expect(rows[0]).toBe('"Component","Property","Value"');
    });
  });

  describe('exportAllFormats', () => {
    it('should return all three formats', () => {
      const components = [mockExtractedComponent()];
      const result = exportAllFormats(components);

      expect(result.typescript).toBeDefined();
      expect(result.json).toBeDefined();
      expect(result.csv).toBeDefined();
    });

    it('should generate consistent content across formats', () => {
      const components = [
        mockExtractedComponent({
          name: 'TestComponent',
          defaultContent: { Title: 'Test' },
        }),
      ];
      const result = exportAllFormats(components);

      // TypeScript should have the component
      expect(result.typescript).toContain('TestComponent');

      // JSON should be parseable and have the component
      const json = JSON.parse(result.json);
      expect(json.TestComponent).toBeDefined();

      // CSV should have the component name
      expect(result.csv).toContain('TestComponent');
    });

    it('should handle empty components', () => {
      const result = exportAllFormats([]);

      expect(result.typescript).toContain('// Auto-generated');
      expect(JSON.parse(result.json)).toEqual({});
      expect(result.csv).toBe('"Component","Property","Value"');
    });
  });
});

// ============================================================================
// Types Tests (compile-time verification)
// ============================================================================

describe('ContentExtractor Types', () => {
  it('should accept valid ExtractedText', () => {
    const text: ExtractedText = {
      layerName: 'Label',
      value: 'Hello',
    };
    expect(text.layerName).toBe('Label');
  });

  it('should accept ExtractedText with all optional properties', () => {
    const text: ExtractedText = {
      layerName: 'Title',
      value: 'Hello World',
      propertyName: 'title',
      fontFamily: 'Inter',
      fontSize: 24,
      fontWeight: 700,
    };
    expect(text.fontWeight).toBe(700);
  });

  it('should accept valid ExtractedVariant', () => {
    const variant: ExtractedVariant = {
      name: 'Primary',
      properties: { size: 'large' },
      texts: [],
    };
    expect(variant.properties.size).toBe('large');
  });

  it('should accept valid ExtractedComponent', () => {
    const component: ExtractedComponent = {
      name: 'Button',
      type: 'COMPONENT',
      properties: [],
      variants: [],
      defaultContent: {},
    };
    expect(component.type).toBe('COMPONENT');
  });

  it('should accept all component types', () => {
    const types: ExtractedComponent['type'][] = ['COMPONENT', 'COMPONENT_SET', 'INSTANCE'];
    expect(types.length).toBe(3);
  });
});

// ============================================================================
// Integration Tests
// ============================================================================

describe('ContentExtractor Integration', () => {
  it('should handle complex component with multiple variants', () => {
    const component = mockExtractedComponent({
      name: 'Complex/Button',
      type: 'COMPONENT_SET',
      description: 'A complex button with multiple states',
      properties: [
        { name: 'size', type: 'VARIANT', variantOptions: ['sm', 'md', 'lg'] },
        { name: 'state', type: 'VARIANT', variantOptions: ['default', 'hover', 'pressed'] },
      ],
      variants: [
        mockExtractedVariant({
          name: 'size=sm, state=default',
          properties: { size: 'sm', state: 'default' },
          texts: [
            mockExtractedText({ layerName: 'Label', value: 'Small Button' }),
          ],
        }),
        mockExtractedVariant({
          name: 'size=md, state=default',
          properties: { size: 'md', state: 'default' },
          texts: [
            mockExtractedText({ layerName: 'Label', value: 'Medium Button' }),
          ],
        }),
      ],
      defaultContent: { Label: 'Small Button' },
    });

    const ts = toTypeScript([component]);
    const json = toJSON([component]);
    const csv = toCSV([component]);

    // Verify TypeScript output
    expect(ts).toContain('ComplexButton');
    // Component name slashes should be removed (note: comments still have //)
    expect(ts).not.toContain('Complex/Button');

    // Verify JSON metadata
    const parsed = JSON.parse(json);
    expect(parsed.ComplexButton._meta.variantCount).toBe(2);
    expect(parsed.ComplexButton._meta.properties).toEqual(['size', 'state']);

    // Verify CSV (uses raw component name, not transformed)
    expect(csv).toContain('Complex/Button');
  });

  it('should handle Unicode content correctly', () => {
    const component = mockExtractedComponent({
      name: 'InternationalButton',
      defaultContent: {
        LabelEN: 'Hello',
        LabelES: 'Hola',
        LabelJA: 'こんにちは',
        LabelAR: 'مرحبا',
      },
    });

    const ts = toTypeScript([component]);
    const json = toJSON([component]);

    expect(ts).toContain('こんにちは');
    expect(json).toContain('مرحبا');
  });

  it('should handle deeply nested property names', () => {
    const component = mockExtractedComponent({
      defaultContent: {
        'Header / Title / Primary Text': 'Main Title',
        'Body > Content > Paragraph': 'Body text',
      },
    });

    const ts = toTypeScript([component]);

    // Should convert to valid camelCase identifiers
    expect(ts).toMatch(/[a-zA-Z]+: string;/);
  });
});
