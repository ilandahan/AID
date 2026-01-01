/**
 * @file services/ComponentEnricher/props.ts
 * @description Prop inference and extraction from Figma nodes
 */

import type { FigmaNodeInfo, ComponentClassification, PropDefinition } from '../../types';
import { PROP_PATTERNS, STATE_PATTERNS } from './config';
import { traverseNodes, toCamelCase, inferPropNameFromText, isLabelText, deduplicateProps } from './utils';

/**
 * Infer props from node structure
 */
export function inferProps(
  nodeInfo: FigmaNodeInfo,
  classification: ComponentClassification
): PropDefinition[] {
  const props: PropDefinition[] = [];

  // Add category-specific props
  const categoryProps = PROP_PATTERNS[classification.category];
  if (categoryProps) {
    for (const prop of categoryProps) {
      props.push({
        name: prop.name!,
        type: prop.type || 'string',
        required: prop.required || false,
        defaultValue: prop.defaultValue,
        enumValues: prop.enumValues,
        description: prop.description || '',
      });
    }
  }

  // Extract text content props
  const textProps = extractTextProps(nodeInfo);
  props.push(...textProps);

  // Extract slot props (areas where content can be inserted)
  const slotProps = extractSlotProps(nodeInfo);
  props.push(...slotProps);

  // Extract from variant properties
  if (nodeInfo.variantProperties) {
    for (const [key, values] of Object.entries(nodeInfo.variantProperties)) {
      // Skip state variants, they become CSS states
      if (STATE_PATTERNS.includes(key.toLowerCase())) continue;

      const enumValues = values.split(', ');
      props.push({
        name: toCamelCase(key),
        type: 'enum',
        required: false,
        enumValues,
        defaultValue: enumValues[0],
        description: `${key} variant`,
        mappedFrom: key,
      });
    }
  }

  return deduplicateProps(props);
}

/**
 * Extract text content props from node tree
 */
export function extractTextProps(nodeInfo: FigmaNodeInfo): PropDefinition[] {
  const props: PropDefinition[] = [];

  traverseNodes(nodeInfo, (node) => {
    if (node.properties.characters !== undefined) {
      const propName = inferPropNameFromText(node.name, node.properties.characters);

      // Check if this is a label-like text
      const isLabel = isLabelText(node);

      props.push({
        name: propName,
        type: 'string',
        required: isLabel,
        defaultValue: node.properties.characters,
        description: `Text content for ${node.name}`,
        mappedFrom: node.id,
      });
    }
  });

  return props;
}

/**
 * Extract slot props for content areas
 */
export function extractSlotProps(nodeInfo: FigmaNodeInfo): PropDefinition[] {
  const props: PropDefinition[] = [];

  traverseNodes(nodeInfo, (node) => {
    // Look for common slot patterns
    const nameLower = node.name.toLowerCase();

    if (nameLower.includes('icon') || nameLower.includes('slot') ||
        nameLower.includes('content') || nameLower.includes('children')) {
      props.push({
        name: toCamelCase(node.name.replace(/\s+/g, '')),
        type: 'node',
        required: false,
        description: `Content slot for ${node.name}`,
        mappedFrom: node.id,
      });
    }
  });

  return props;
}
