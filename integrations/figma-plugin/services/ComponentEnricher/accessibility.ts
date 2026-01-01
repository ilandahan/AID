/**
 * @file services/ComponentEnricher/accessibility.ts
 * @description Accessibility extraction and dependency management
 */

import type { FigmaNodeInfo, ComponentClassification, EnrichedComponentData, AtomicLevel } from '../../types';
import { nodeAnalyzer } from '../../NodeAnalyzer';
import { traverseNodes } from './utils';

/**
 * ARIA role mapping from component categories
 */
const ROLE_MAP: Record<string, string> = {
  button: 'button',
  link: 'link',
  input: 'textbox',
  checkbox: 'checkbox',
  radio: 'radio',
  select: 'combobox',
  modal: 'dialog',
  navigation: 'navigation',
  header: 'banner',
  footer: 'contentinfo',
  sidebar: 'complementary',
  form: 'form',
  table: 'table',
  list: 'list',
  card: 'article',
};

/**
 * Keyboard interaction patterns by category
 */
const KEYBOARD_MAP: Record<string, string[]> = {
  button: ['Enter', 'Space'],
  link: ['Enter'],
  input: ['Tab'],
  checkbox: ['Space'],
  radio: ['Arrow keys', 'Space'],
  select: ['Arrow keys', 'Enter', 'Escape'],
  modal: ['Escape', 'Tab trap'],
  tabs: ['Arrow keys', 'Tab'],
};

/**
 * Extract accessibility information from node
 */
export function extractAccessibility(
  nodeInfo: FigmaNodeInfo,
  classification: ComponentClassification
): EnrichedComponentData['accessibility'] {
  const accessibility: EnrichedComponentData['accessibility'] = {};

  // Infer ARIA role from category
  accessibility.role = ROLE_MAP[classification.category];

  // Find text for aria-label
  let labelText: string | undefined;
  traverseNodes(nodeInfo, (node) => {
    if (!labelText && node.properties.characters) {
      const nameLower = node.name.toLowerCase();
      if (nameLower.includes('label') || nameLower.includes('title')) {
        labelText = node.properties.characters;
      }
    }
  });

  if (labelText) {
    accessibility.ariaLabel = labelText;
  }

  // Add keyboard interactions based on category
  accessibility.keyboardInteraction = KEYBOARD_MAP[classification.category];

  return accessibility;
}

/**
 * Extract component dependencies (internal and external)
 */
export function extractDependencies(nodeInfo: FigmaNodeInfo): {
  internal: string[];
  external: string[];
} {
  const internal: string[] = [];
  const external: string[] = [];

  const deps = nodeAnalyzer.findDependencies(nodeInfo);

  for (const dep of deps) {
    if (dep.isExternal) {
      external.push(dep.nodeName);
    } else {
      internal.push(dep.nodeId);
    }
  }

  return { internal, external };
}

/**
 * Generate component description based on classification
 */
export function generateDescription(
  nodeInfo: FigmaNodeInfo,
  classification: ComponentClassification
): string {
  const levelDescriptions: Record<AtomicLevel, string> = {
    atom: 'Basic UI element that cannot be broken down further',
    molecule: 'Group of atoms working together as a unit',
    organism: 'Complex component made of molecules and atoms',
    template: 'Page-level layout that arranges organisms',
    page: 'Specific instance of a template with real content',
  };

  return `${classification.suggestedName} - ${levelDescriptions[classification.level]}. Category: ${classification.category}.`;
}
