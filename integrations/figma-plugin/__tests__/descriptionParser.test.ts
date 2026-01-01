/**
 * @file descriptionParser.test.ts
 * @description Unit tests for descriptionParser module
 */

import { parseComponentDescription, formatComponentDescription, type ParsedDescription } from '../descriptionParser';

describe('Description Parser', () => {
  describe('parseComponentDescription', () => {
    it('should parse simple description without metadata', () => {
      const input = 'A simple button component';
      const result = parseComponentDescription(input);

      expect(result.description).toBe('A simple button component');
      expect(result.tags).toEqual([]);
      expect(result.notes).toBe('');
      expect(result.ariaLabel).toBeNull();
    });

    it('should parse description with YAML-style metadata', () => {
      const input = `Primary button for main actions.
---
tags: button, primary, interactive
notes: Use for primary CTA
ariaLabel: Submit form`;

      const result = parseComponentDescription(input);

      expect(result.description).toBe('Primary button for main actions.');
      expect(result.tags).toContain('button');
      expect(result.tags).toContain('primary');
      expect(result.tags).toContain('interactive');
      expect(result.notes).toBe('Use for primary CTA');
      expect(result.ariaLabel).toBe('Submit form');
    });

    it('should handle empty input', () => {
      const result = parseComponentDescription('');

      expect(result.description).toBe('');
      expect(result.tags).toEqual([]);
      expect(result.notes).toBe('');
    });

    it('should handle description with only separator (no trailing newline)', () => {
      // When --- has no newline after it, the regex doesn't match,
      // so the entire input is treated as description
      const input = `Some description
---`;

      const result = parseComponentDescription(input);

      // The --- is kept as part of description since there's no content after it
      expect(result.description).toBe('Some description\n---');
      expect(result.tags).toEqual([]);
    });

    it('should parse multiple tags correctly', () => {
      const input = `Test component
---
tags: one, two, three, four`;

      const result = parseComponentDescription(input);

      expect(result.tags).toHaveLength(4);
      expect(result.tags).toEqual(['one', 'two', 'three', 'four']);
    });

    it('should handle whitespace in tags', () => {
      const input = `Test
---
tags:   spaced  ,  out  ,  tags  `;

      const result = parseComponentDescription(input);

      expect(result.tags).toEqual(['spaced', 'out', 'tags']);
    });

    it('should parse custom fields', () => {
      const input = `Component description
---
category: button
level: atom
priority: high`;

      const result = parseComponentDescription(input);

      expect(result.customFields).toBeDefined();
      expect(result.customFields.category).toBe('button');
      expect(result.customFields.level).toBe('atom');
      expect(result.customFields.priority).toBe('high');
    });

    it('should handle multiline notes', () => {
      const input = `Description here
---
notes: First line of notes. Second sentence.`;

      const result = parseComponentDescription(input);

      expect(result.notes).toBe('First line of notes. Second sentence.');
    });

    it('should handle external references', () => {
      const input = `Component with externals
---
external: IconButton, BaseInput
tags: composite`;

      const result = parseComponentDescription(input);

      expect(result.external).toContain('IconButton');
      expect(result.external).toContain('BaseInput');
    });

    it('should preserve description with multiple paragraphs before separator', () => {
      const input = `First paragraph of description.

Second paragraph with more details.
---
tags: test`;

      const result = parseComponentDescription(input);

      expect(result.description).toContain('First paragraph');
      expect(result.description).toContain('Second paragraph');
    });
  });

  describe('edge cases', () => {
    it('should handle undefined input', () => {
      const result = parseComponentDescription(undefined as unknown as string);
      expect(result.description).toBe('');
    });

    it('should handle null input', () => {
      const result = parseComponentDescription(null as unknown as string);
      expect(result.description).toBe('');
    });

    it('should handle input with only whitespace', () => {
      const result = parseComponentDescription('   \n\n   ');
      expect(result.description.trim()).toBe('');
    });

    it('should handle malformed YAML-like content', () => {
      const input = `Description
---
this is not valid yaml
tags without colon`;

      // Should not throw
      expect(() => parseComponentDescription(input)).not.toThrow();
      const result = parseComponentDescription(input);
      expect(result.description).toBe('Description');
    });

    it('should handle separator in the middle of content', () => {
      const input = `Description with --- in it
---
tags: test`;

      const result = parseComponentDescription(input);
      // Should split on the first proper separator
      expect(result.description).toBe('Description with --- in it');
      expect(result.tags).toContain('test');
    });
  });

  describe('formatComponentDescription', () => {
    it('should format description with metadata back to string', () => {
      const data: Partial<ParsedDescription> = {
        description: 'Test component',
        tags: ['button', 'primary'],
        notes: 'Usage notes here',
      };

      const result = formatComponentDescription(data);

      expect(result).toContain('Test component');
      expect(result).toContain('---');
      expect(result).toContain('tags: button, primary');
      expect(result).toContain('notes: Usage notes here');
    });

    it('should format description without metadata', () => {
      const data: Partial<ParsedDescription> = {
        description: 'Simple description',
      };

      const result = formatComponentDescription(data);

      expect(result).toBe('Simple description');
      expect(result).not.toContain('---');
    });

    it('should include ariaLabel when present', () => {
      const data: Partial<ParsedDescription> = {
        description: 'Button',
        ariaLabel: 'Submit form',
      };

      const result = formatComponentDescription(data);

      expect(result).toContain('ariaLabel: Submit form');
    });

    it('should include external dependencies', () => {
      const data: Partial<ParsedDescription> = {
        description: 'Composite component',
        external: ['IconButton', 'Tooltip'],
      };

      const result = formatComponentDescription(data);

      expect(result).toContain('external: IconButton, Tooltip');
    });

    it('should include custom fields', () => {
      const data: Partial<ParsedDescription> = {
        description: 'Component',
        customFields: {
          category: 'button',
          level: 'atom',
        },
      };

      const result = formatComponentDescription(data);

      expect(result).toContain('category: button');
      expect(result).toContain('level: atom');
    });
  });
});
