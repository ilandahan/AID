/**
 * @file services/ContentExtractor/extraction.ts
 * @description Component extraction from Figma selection
 */

import type { ExtractedComponent } from './types';
import { extractPropertyDefinitions, extractVariant, extractTextsFromNode } from './properties';

/**
 * Extract content from selected nodes
 */
export function extractFromSelection(): ExtractedComponent[] {
  const selection = figma.currentPage.selection;

  if (selection.length === 0) {
    figma.notify('Please select a component or component set');
    return [];
  }

  const extracted: ExtractedComponent[] = [];

  for (const node of selection) {
    if (node.type === 'COMPONENT_SET') {
      extracted.push(extractFromComponentSet(node));
    } else if (node.type === 'COMPONENT') {
      extracted.push(extractFromComponent(node));
    } else if (node.type === 'INSTANCE') {
      extracted.push(extractFromInstance(node));
    }
  }

  return extracted;
}

/**
 * Extract from Component Set (multiple variants)
 */
export function extractFromComponentSet(componentSet: ComponentSetNode): ExtractedComponent {
  const properties = extractPropertyDefinitions(componentSet);
  const variants: ReturnType<typeof extractVariant>[] = [];
  const defaultContent: Record<string, string> = {};

  // Extract from each variant
  for (const child of componentSet.children) {
    if (child.type === 'COMPONENT') {
      const variant = extractVariant(child);
      variants.push(variant);

      // Collect default content from first variant
      if (variants.length === 1) {
        for (const text of variant.texts) {
          const key = text.propertyName || text.layerName;
          defaultContent[key] = text.value;
        }
      }
    }
  }

  return {
    name: componentSet.name,
    type: 'COMPONENT_SET',
    description: componentSet.description || undefined,
    properties,
    variants,
    defaultContent
  };
}

/**
 * Extract from single Component
 */
export function extractFromComponent(component: ComponentNode): ExtractedComponent {
  const properties = extractPropertyDefinitions(component);
  const variant = extractVariant(component);
  const defaultContent: Record<string, string> = {};

  for (const text of variant.texts) {
    const key = text.propertyName || text.layerName;
    defaultContent[key] = text.value;
  }

  return {
    name: component.name,
    type: 'COMPONENT',
    description: component.description || undefined,
    properties,
    variants: [variant],
    defaultContent
  };
}

/**
 * Extract from Instance
 */
export function extractFromInstance(instance: InstanceNode): ExtractedComponent {
  const texts = extractTextsFromNode(instance);
  const defaultContent: Record<string, string> = {};

  for (const text of texts) {
    const key = text.propertyName || text.layerName;
    defaultContent[key] = text.value;
  }

  return {
    name: instance.name,
    type: 'INSTANCE',
    description: undefined,
    properties: [],
    variants: [{
      name: instance.name,
      properties: {},
      texts
    }],
    defaultContent
  };
}
