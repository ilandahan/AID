/**
 * @file services/ComponentAuditor/config.ts
 * @description Configuration constants for component auditing
 */

// ============================================
// Interactive Component Detection
// ============================================

/**
 * Patterns that indicate a component is interactive and should have
 * Focus/Hover states. Used to avoid false positives on non-interactive
 * components like Badge, Avatar, Divider.
 */
export const INTERACTIVE_PATTERNS = [
  /button/i, /btn/i,
  /input/i, /field/i, /text-?area/i,
  /select/i, /dropdown/i, /picker/i, /combobox/i,
  /checkbox/i, /radio/i, /toggle/i, /switch/i,
  /tab/i, /menu/i, /nav/i, /navigation/i,
  /link/i, /anchor/i, /href/i,
  /slider/i, /range/i,
  /modal/i, /dialog/i, /drawer/i, /popover/i, /tooltip/i,
  /accordion/i, /collapse/i, /expand/i,
  /chip/i, /tag/i,  // Often clickable/removable
  /stepper/i, /pagination/i,
  /search/i, /form/i
];

// ============================================
// Scoring Configuration
// ============================================

export const SCORING_CONFIG = {
  weights: {
    consistency: 0.25,    // 25%
    metadata: 0.30,       // 30%
    accessibility: 0.25,  // 25%
    structure: 0.20       // 20%
  },

  minimums: {
    consistency: 70,
    metadata: 60,
    accessibility: 80,  // A11y is critical
    structure: 70
  },

  exportThreshold: 90,

  blockerIssues: [
    'missing_component_description',
    'missing_focus_states',
    'contrast_ratio_fail',
    'no_accessibility_metadata',
    'critical_naming_error'
  ]
};

// ============================================
// Dictionary for Typo Detection
// ============================================

/**
 * Dictionary of correct terms used in design systems.
 * Fuzzy matching will detect typos within edit distance 1-2 of these terms.
 */
export const CORRECT_TERMS = [
  // States
  'Default', 'Hover', 'Active', 'Focused', 'Focus', 'Disabled', 'Pressed', 'Selected', 'Loading',
  // Variants
  'Primary', 'Secondary', 'Tertiary', 'Success', 'Warning', 'Error', 'Info', 'Danger',
  // Sizes
  'Small', 'Medium', 'Large', 'Extra', 'Full', 'Compact',
  // Component types
  'Button', 'Label', 'Icon', 'Input', 'Text', 'Link', 'Card', 'Modal', 'Dialog',
  // Styles
  'Outline', 'Outlined', 'Filled', 'Ghost', 'Solid', 'Contained', 'Minimal'
];

/**
 * Generic layer names that should be renamed to semantic names
 */
export const GENERIC_LAYER_NAMES = ['Frame', 'Group', 'Rectangle', 'Text', 'Vector', 'Ellipse'];
