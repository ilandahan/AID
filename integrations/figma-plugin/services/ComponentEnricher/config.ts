/**
 * @file services/ComponentEnricher/config.ts
 * @description Configuration constants for prop patterns and state detection
 */

import type { PropDefinition } from '../../types';

/**
 * Common prop patterns for different component types
 * These are auto-injected based on component category
 */
export const PROP_PATTERNS: Record<string, Partial<PropDefinition>[]> = {
  button: [
    { name: 'onClick', type: 'function', required: false, description: 'Click handler' },
    { name: 'disabled', type: 'boolean', required: false, defaultValue: false, description: 'Disabled state' },
    { name: 'loading', type: 'boolean', required: false, defaultValue: false, description: 'Loading state' },
  ],
  input: [
    { name: 'value', type: 'string', required: false, description: 'Input value' },
    { name: 'onChange', type: 'function', required: false, description: 'Change handler' },
    { name: 'placeholder', type: 'string', required: false, description: 'Placeholder text' },
    { name: 'disabled', type: 'boolean', required: false, defaultValue: false, description: 'Disabled state' },
    { name: 'error', type: 'string', required: false, description: 'Error message' },
  ],
  link: [
    { name: 'href', type: 'string', required: true, description: 'Link URL' },
    { name: 'target', type: 'enum', required: false, enumValues: ['_self', '_blank'], description: 'Link target' },
  ],
  card: [
    { name: 'onClick', type: 'function', required: false, description: 'Click handler for interactive cards' },
  ],
  modal: [
    { name: 'isOpen', type: 'boolean', required: true, description: 'Modal visibility' },
    { name: 'onClose', type: 'function', required: true, description: 'Close handler' },
  ],
};

/**
 * State patterns to detect in component variants
 * These typically become CSS pseudo-states or conditional rendering
 */
export const STATE_PATTERNS = [
  'default',
  'hover',
  'active',
  'pressed',
  'focus',
  'focused',
  'disabled',
  'error',
  'loading',
  'selected',
];

/**
 * Breakpoint patterns for responsive design detection
 */
export const BREAKPOINT_PATTERNS = [
  'mobile',
  'tablet',
  'desktop',
  'sm',
  'md',
  'lg',
  'xl',
  '2xl',
];
