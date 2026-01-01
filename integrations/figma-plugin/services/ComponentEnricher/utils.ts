/**
 * @file services/ComponentEnricher/utils.ts
 * @description Utility functions for node traversal and string manipulation
 */

import type { FigmaNodeInfo, PropDefinition } from '../../types';

/**
 * Traverse all nodes recursively and execute callback
 */
export function traverseNodes(
  nodeInfo: FigmaNodeInfo,
  callback: (node: FigmaNodeInfo) => void
): void {
  callback(nodeInfo);

  if (nodeInfo.children) {
    for (const child of nodeInfo.children) {
      traverseNodes(child, callback);
    }
  }
}

/**
 * Convert string to camelCase
 */
export function toCamelCase(str: string): string {
  return str
    .replace(/[^a-zA-Z0-9\s]/g, '')
    .split(/[\s-_]+/)
    .map((word, index) =>
      index === 0
        ? word.toLowerCase()
        : word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
    )
    .join('');
}

/**
 * Infer prop name from text node name and content
 */
export function inferPropNameFromText(nodeName: string, _textContent: string): string {
  const nameLower = nodeName.toLowerCase();

  // Common text element names
  const namePatterns: Record<string, string> = {
    title: 'title',
    heading: 'heading',
    label: 'label',
    description: 'description',
    subtitle: 'subtitle',
    caption: 'caption',
    text: 'text',
    content: 'content',
    cta: 'ctaText',
    button: 'label',
  };

  for (const [pattern, propName] of Object.entries(namePatterns)) {
    if (nameLower.includes(pattern)) {
      return propName;
    }
  }

  // Use cleaned node name
  return toCamelCase(nodeName);
}

/**
 * Check if text node is a label
 */
export function isLabelText(node: FigmaNodeInfo): boolean {
  const nameLower = node.name.toLowerCase();
  return nameLower.includes('label') ||
         nameLower.includes('title') ||
         nameLower.includes('heading');
}

/**
 * Remove duplicate props by name
 */
export function deduplicateProps(props: PropDefinition[]): PropDefinition[] {
  const seen = new Map<string, PropDefinition>();

  for (const prop of props) {
    if (!seen.has(prop.name)) {
      seen.set(prop.name, prop);
    }
  }

  return Array.from(seen.values());
}
