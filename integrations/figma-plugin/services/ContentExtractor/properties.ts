/**
 * @file services/ContentExtractor/properties.ts
 * @description Property and text extraction from Figma nodes
 */

import type { ExtractedText, ExtractedVariant, ComponentPropertyDefinition } from './types';

/**
 * Extract property definitions from component
 */
export function extractPropertyDefinitions(
  node: ComponentSetNode | ComponentNode
): ComponentPropertyDefinition[] {
  const properties: ComponentPropertyDefinition[] = [];

  // Only COMPONENT_SET or non-variant COMPONENT can access componentPropertyDefinitions
  // Variant components (children of COMPONENT_SET) will throw an error
  const isVariantComponent = node.type === 'COMPONENT' &&
    (node as ComponentNode).parent?.type === 'COMPONENT_SET';

  if (!isVariantComponent && 'componentPropertyDefinitions' in node && node.componentPropertyDefinitions) {
    for (const [name, def] of Object.entries(node.componentPropertyDefinitions)) {
      const prop: ComponentPropertyDefinition = {
        name: name.replace(/#\d+:\d+$/, ''), // Remove Figma ID suffix
        type: def.type as 'TEXT' | 'BOOLEAN' | 'VARIANT' | 'INSTANCE_SWAP',
      };

      if (def.type === 'TEXT') {
        prop.defaultValue = def.defaultValue as string;
      } else if (def.type === 'BOOLEAN') {
        prop.defaultValue = def.defaultValue as boolean;
      } else if (def.type === 'VARIANT') {
        prop.variantOptions = def.variantOptions;
        prop.defaultValue = def.defaultValue as string;
      }

      properties.push(prop);
    }
  }

  return properties;
}

/**
 * Extract variant information from a component
 */
export function extractVariant(component: ComponentNode): ExtractedVariant {
  const properties: Record<string, string> = {};

  // Parse variant name to get properties
  // Format: "Property1=Value1, Property2=Value2"
  const parts = component.name.split(',').map(p => p.trim());
  for (const part of parts) {
    const [key, value] = part.split('=').map(s => s.trim());
    if (key && value) {
      properties[key] = value;
    }
  }

  const texts = extractTextsFromNode(component);

  return {
    name: component.name,
    properties,
    texts
  };
}

/**
 * Extract all text content from a node (recursive)
 */
export function extractTextsFromNode(node: SceneNode): ExtractedText[] {
  const texts: ExtractedText[] = [];

  if (node.type === 'TEXT') {
    texts.push(extractTextNode(node));
  }

  if ('children' in node) {
    for (const child of node.children) {
      texts.push(...extractTextsFromNode(child));
    }
  }

  return texts;
}

/**
 * Extract text content from a text node
 */
export function extractTextNode(textNode: TextNode): ExtractedText {
  // Try to find associated property name
  let propertyName: string | undefined;

  // Check if this text is linked to a component property
  if ('componentPropertyReferences' in textNode) {
    const refs = textNode.componentPropertyReferences;
    if (refs && 'characters' in refs) {
      const charsRef = refs.characters as string;
      propertyName = charsRef ? charsRef.replace(/#\d+:\d+$/, '') : undefined;
    }
  }

  // Get font info
  let fontFamily: string | undefined;
  let fontSize: number | undefined;
  let fontWeight: number | undefined;

  if (typeof textNode.fontName !== 'symbol') {
    fontFamily = textNode.fontName.family;
  }
  if (typeof textNode.fontSize !== 'symbol') {
    fontSize = textNode.fontSize;
  }
  if (typeof textNode.fontWeight !== 'symbol') {
    fontWeight = textNode.fontWeight as number;
  }

  return {
    layerName: textNode.name,
    propertyName,
    value: textNode.characters,
    fontFamily,
    fontSize,
    fontWeight
  };
}
