/**
 * @file services/ComponentAuditor/mcp-preparation.ts
 * @description Prepare component data for sending to Claude via MCP
 */

import type {
  ComponentAuditRequest,
  ComponentPropertyInfo,
  VariantInfo,
  ChildNodeInfo
} from '../../types';

// Local type for Figma's component property definitions
type ComponentPropertyDefinition = {
  type: string;
  defaultValue?: unknown;
  variantOptions?: string[];
};

/**
 * Prepare component data for sending to Claude via MCP
 */
export function prepareForMCP(node: SceneNode): ComponentAuditRequest {
  const properties: ComponentPropertyInfo[] = [];
  const variants: VariantInfo[] = [];
  const children: ChildNodeInfo[] = [];

  // Extract properties - only for COMPONENT_SET or non-variant COMPONENT
  const canAccessPropertyDefs = node.type === 'COMPONENT_SET' ||
    (node.type === 'COMPONENT' && !(node as ComponentNode).parent?.type?.includes('COMPONENT_SET'));

  if (canAccessPropertyDefs && 'componentPropertyDefinitions' in node) {
    const defs = (node as ComponentSetNode).componentPropertyDefinitions;
    for (const [name, def] of Object.entries(defs) as [string, ComponentPropertyDefinition][]) {
      properties.push({
        name: name.replace(/#\d+:\d+$/, ''),
        type: def.type as 'TEXT' | 'BOOLEAN' | 'VARIANT' | 'INSTANCE_SWAP',
        defaultValue: def.defaultValue as string | boolean,
        variantOptions: def.type === 'VARIANT' ? def.variantOptions : undefined
      });
    }
  }

  // Extract variants
  if (node.type === 'COMPONENT_SET') {
    for (const child of node.children) {
      if (child.type === 'COMPONENT') {
        const variantProps: Record<string, string> = {};
        const parts = child.name.split(',').map(p => p.trim());
        for (const part of parts) {
          const [key, value] = part.split('=').map(s => s.trim());
          if (key && value) variantProps[key] = value;
        }

        variants.push({
          name: child.name,
          nodeId: child.id,
          properties: variantProps,
          description: (child as ComponentNode).description || undefined,
          hasDescription: Boolean((child as ComponentNode).description)
        });
      }
    }
  }

  // Extract children structure
  if ('children' in node) {
    const extractChildren = (nodes: readonly SceneNode[]): ChildNodeInfo[] => {
      return nodes.map(n => ({
        name: n.name,
        type: n.type,
        nodeId: n.id
      }));
    };
    children.push(...extractChildren(node.children));
  }

  // Get description
  let existingDescription: string | undefined;
  if ('description' in node) {
    existingDescription = (node as ComponentNode | ComponentSetNode).description;
  }

  // Extract additional fields needed by server audit
  let hasAutoLayout = 'layoutMode' in node && node.layoutMode !== 'NONE';
  if (!hasAutoLayout && node.type === 'COMPONENT_SET') {
    // Check if any variant child uses Auto Layout
    hasAutoLayout = node.children.some(child =>
      'layoutMode' in child && (child as FrameNode).layoutMode !== 'NONE'
    );
  }
  const width = 'width' in node ? (node.width as number) : undefined;
  const height = 'height' in node ? (node.height as number) : undefined;
  const childCount = 'children' in node ? node.children.length : 0;

  // Check for interactive states in variant names
  let hasStates = false;
  const variantNames: string[] = [];
  if (node.type === 'COMPONENT_SET') {
    node.children.forEach(c => variantNames.push(c.name.toLowerCase()));
    hasStates = variantNames.some(name =>
      name.includes('hover') || name.includes('focus') ||
      name.includes('disabled') || name.includes('active') ||
      name.includes('pressed')
    );
  }

  // Log extraction data
  logFigmaDataExtraction(node, properties, variants, variantNames, children, existingDescription, width, height, childCount, hasAutoLayout, hasStates);

  return {
    component: {
      name: node.name,
      type: node.type as 'COMPONENT' | 'COMPONENT_SET' | 'INSTANCE',
      nodeId: node.id,
      properties,
      variants,
      children,
      hasAutoLayout,
      hasStates,
      width,
      height,
      childCount
    },
    existingDescription,
    variants
  };
}

/**
 * Log Figma data extraction for debugging
 */
function logFigmaDataExtraction(
  node: SceneNode,
  properties: ComponentPropertyInfo[],
  variants: VariantInfo[],
  variantNames: string[],
  children: ChildNodeInfo[],
  existingDescription: string | undefined,
  width: number | undefined,
  height: number | undefined,
  childCount: number,
  hasAutoLayout: boolean,
  hasStates: boolean
): void {
  console.log('[FIGMA DATA] ========== COMPONENT EXTRACTION ==========');
  console.log('[FIGMA DATA] Node name:', node.name);
  console.log('[FIGMA DATA] Node type:', node.type);
  console.log('[FIGMA DATA] Node ID:', node.id);
  console.log('[FIGMA DATA] Width:', width);
  console.log('[FIGMA DATA] Height:', height);
  console.log('[FIGMA DATA] Child count:', childCount);
  console.log('[FIGMA DATA] Has Auto Layout (node):', 'layoutMode' in node ? node.layoutMode : 'N/A');
  console.log('[FIGMA DATA] Has Auto Layout (resolved):', hasAutoLayout);
  console.log('[FIGMA DATA] Has States:', hasStates);
  console.log('[FIGMA DATA] Existing Description:', existingDescription ? existingDescription.substring(0, 100) + '...' : 'NONE');
  console.log('[FIGMA DATA] Properties count:', properties.length);
  console.log('[FIGMA DATA] Properties:', JSON.stringify(properties.map(p => ({ name: p.name, type: p.type }))));
  console.log('[FIGMA DATA] Variants count:', variants.length);
  console.log('[FIGMA DATA] Variant names:', variantNames.slice(0, 5).join(', ') + (variantNames.length > 5 ? '...' : ''));
  console.log('[FIGMA DATA] Children (top level):', children.map(c => c.name).slice(0, 5).join(', '));
  console.log('[FIGMA DATA] ===========================================');
}
