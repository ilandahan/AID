/**
 * @file services/NodeAnalyzer/extraction.ts
 * @description Node info and property extraction from Figma nodes
 */

import type {
  FigmaNodeInfo,
  FigmaNodeProperties,
} from '../../types';

/**
 * Extract node properties from a Figma scene node
 */
export function extractProperties(node: SceneNode): FigmaNodeProperties {
  const props: FigmaNodeProperties = {};

  // Geometry
  if ('width' in node) props.width = node.width;
  if ('height' in node) props.height = node.height;
  if ('x' in node) props.x = node.x;
  if ('y' in node) props.y = node.y;

  // Auto Layout
  if ('layoutMode' in node && node.layoutMode !== 'NONE') {
    props.layoutMode = node.layoutMode;
    props.paddingLeft = node.paddingLeft;
    props.paddingRight = node.paddingRight;
    props.paddingTop = node.paddingTop;
    props.paddingBottom = node.paddingBottom;
    props.itemSpacing = node.itemSpacing;
    props.primaryAxisSizingMode = node.primaryAxisSizingMode;
    props.counterAxisSizingMode = node.counterAxisSizingMode;
  }

  // Appearance
  if ('fills' in node && node.fills !== figma.mixed) {
    props.fills = node.fills;
  }
  if ('strokes' in node) {
    props.strokes = node.strokes;
    props.strokeWeight = node.strokeWeight as number;
  }
  if ('cornerRadius' in node && node.cornerRadius !== figma.mixed) {
    props.cornerRadius = node.cornerRadius;
  }
  if ('effects' in node) {
    props.effects = node.effects;
  }
  if ('opacity' in node) {
    props.opacity = node.opacity;
  }

  // Typography
  if (node.type === 'TEXT') {
    props.characters = node.characters;
    if (node.fontSize !== figma.mixed) props.fontSize = node.fontSize;
    if (node.fontName !== figma.mixed) props.fontName = node.fontName;
    if (node.fontWeight !== figma.mixed) props.fontWeight = node.fontWeight;
    if (node.lineHeight !== figma.mixed) props.lineHeight = node.lineHeight;
    if (node.letterSpacing !== figma.mixed) props.letterSpacing = node.letterSpacing;
    props.textAlignHorizontal = node.textAlignHorizontal;
    props.textAlignVertical = node.textAlignVertical;
  }

  return props;
}

/**
 * Extract variant properties from a component set
 */
export function extractVariantProperties(node: ComponentSetNode): Record<string, string> {
  const variants: Record<string, string> = {};

  if ('variantGroupProperties' in node) {
    for (const [key, value] of Object.entries(node.variantGroupProperties)) {
      variants[key] = value.values.join(', ');
    }
  }

  return variants;
}

/**
 * Create FigmaNodeInfo extraction function with caching
 */
export function createNodeInfoExtractor(nodeCache: Map<string, FigmaNodeInfo>) {
  const extractNodeInfo = (node: SceneNode): FigmaNodeInfo => {
    const cached = nodeCache.get(node.id);
    if (cached) return cached;

    const info: FigmaNodeInfo = {
      id: node.id,
      name: node.name,
      type: node.type,
      properties: extractProperties(node),
      children: extractChildren(node),
    };

    // Component-specific properties
    if (node.type === 'COMPONENT_SET') {
      info.isComponentSet = true;
      info.variantProperties = extractVariantProperties(node);
    }

    if (node.type === 'INSTANCE') {
      info.isInstance = true;
      info.mainComponentId = node.mainComponent ? node.mainComponent.id : undefined;
    }

    nodeCache.set(node.id, info);
    return info;
  };

  const extractChildren = (node: SceneNode): FigmaNodeInfo[] | undefined => {
    if (!('children' in node)) return undefined;
    return node.children.map(child => extractNodeInfo(child));
  };

  return extractNodeInfo;
}
