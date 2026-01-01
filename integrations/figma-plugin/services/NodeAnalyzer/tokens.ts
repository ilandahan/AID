/**
 * @file services/NodeAnalyzer/tokens.ts
 * @description Design token extraction from Figma nodes
 */

import type {
  FigmaNodeInfo,
  DesignToken,
} from '../../types';

import { generateSuggestedName } from './classification';

// Figma type declarations for environments where global types aren't available (e.g., Jest)
// These match the Figma Plugin API types
type RGB = { r: number; g: number; b: number };
type RGBA = { r: number; g: number; b: number; a: number };
type SolidPaint = { type: 'SOLID'; color: RGB; opacity?: number; visible?: boolean };
type Paint = { type: string; visible?: boolean };
type DropShadowEffect = {
  type: 'DROP_SHADOW';
  color: RGBA;
  offset: { x: number; y: number };
  radius: number;
  spread?: number;
  visible?: boolean;
};

/**
 * Convert RGB to hex
 */
export function rgbToHex(color: RGB): string {
  const r = Math.round(color.r * 255).toString(16).padStart(2, '0');
  const g = Math.round(color.g * 255).toString(16).padStart(2, '0');
  const b = Math.round(color.b * 255).toString(16).padStart(2, '0');
  return `#${r}${g}${b}`;
}

/**
 * Convert RGBA to string
 */
export function rgbaToString(color: RGBA): string {
  const r = Math.round(color.r * 255);
  const g = Math.round(color.g * 255);
  const b = Math.round(color.b * 255);
  const a = color.a.toFixed(2);
  return `rgba(${r}, ${g}, ${b}, ${a})`;
}

/**
 * Remove duplicate tokens
 */
export function deduplicateTokens(tokens: DesignToken[]): DesignToken[] {
  const seen = new Set<string>();
  return tokens.filter(token => {
    const key = `${token.category}:${token.value}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

/**
 * Extract color tokens from fills
 */
function extractColorTokensFromFills(
  fills: readonly Paint[],
  baseName: string,
  tokenType: 'bg' | 'border'
): DesignToken[] {
  const tokens: DesignToken[] = [];
  const solidFills = fills.filter(f => f.type === 'SOLID') as SolidPaint[];

  solidFills.forEach((fill, index) => {
    const colorValue = rgbToHex(fill.color);
    const suffix = index > 0 ? `-${index}` : '';
    tokens.push({
      name: `${baseName}-${tokenType}${suffix}`,
      value: colorValue,
      category: 'color',
      rawValue: fill.color,
      cssVariable: `--color-${baseName}-${tokenType}${suffix}`,
    });
  });

  return tokens;
}

/**
 * Extract spacing tokens
 */
function extractSpacingTokens(
  properties: FigmaNodeInfo['properties'],
  baseName: string
): DesignToken[] {
  const tokens: DesignToken[] = [];

  if (properties.paddingTop !== undefined) {
    const padding = {
      top: properties.paddingTop,
      right: properties.paddingRight,
      bottom: properties.paddingBottom,
      left: properties.paddingLeft,
    };

    tokens.push({
      name: `${baseName}-padding`,
      value: `${padding.top}px ${padding.right}px ${padding.bottom}px ${padding.left}px`,
      category: 'spacing',
      rawValue: padding,
      cssVariable: `--spacing-${baseName}-padding`,
    });
  }

  if (properties.itemSpacing !== undefined) {
    tokens.push({
      name: `${baseName}-gap`,
      value: `${properties.itemSpacing}px`,
      category: 'spacing',
      rawValue: properties.itemSpacing,
      cssVariable: `--spacing-${baseName}-gap`,
    });
  }

  return tokens;
}

/**
 * Extract typography tokens
 */
function extractTypographyTokens(
  properties: FigmaNodeInfo['properties'],
  baseName: string
): DesignToken[] {
  const tokens: DesignToken[] = [];

  if (properties.fontSize) {
    tokens.push({
      name: `${baseName}-font-size`,
      value: `${properties.fontSize}px`,
      category: 'typography',
      rawValue: properties.fontSize,
      cssVariable: `--font-size-${baseName}`,
    });
  }

  if (properties.fontName) {
    tokens.push({
      name: `${baseName}-font-family`,
      value: properties.fontName.family,
      category: 'typography',
      rawValue: properties.fontName,
      cssVariable: `--font-family-${baseName}`,
    });
  }

  return tokens;
}

/**
 * Extract shadow tokens
 */
function extractShadowTokens(
  effects: readonly Effect[],
  baseName: string
): DesignToken[] {
  const tokens: DesignToken[] = [];

  const shadows = effects.filter(e =>
    e.type === 'DROP_SHADOW' || e.type === 'INNER_SHADOW'
  ) as DropShadowEffect[];

  shadows.forEach((shadow, index) => {
    const shadowValue = `${shadow.offset.x}px ${shadow.offset.y}px ${shadow.radius}px ${rgbaToString(shadow.color)}`;
    const suffix = index > 0 ? `-${index}` : '';
    tokens.push({
      name: `${baseName}-shadow${suffix}`,
      value: shadowValue,
      category: 'shadow',
      rawValue: shadow,
      cssVariable: `--shadow-${baseName}${suffix}`,
    });
  });

  return tokens;
}

/**
 * Extract design tokens from a node
 */
export function extractTokens(nodeInfo: FigmaNodeInfo): DesignToken[] {
  const tokens: DesignToken[] = [];
  const { properties } = nodeInfo;
  const baseName = generateSuggestedName(nodeInfo.name, 'atom').toLowerCase();

  // Extract colors
  if (properties.fills) {
    tokens.push(...extractColorTokensFromFills(
      properties.fills as readonly Paint[],
      baseName,
      'bg'
    ));
  }

  if (properties.strokes) {
    tokens.push(...extractColorTokensFromFills(
      properties.strokes as readonly Paint[],
      baseName,
      'border'
    ));
  }

  // Extract spacing
  tokens.push(...extractSpacingTokens(properties, baseName));

  // Extract border radius
  if (properties.cornerRadius !== undefined && properties.cornerRadius > 0) {
    tokens.push({
      name: `${baseName}-radius`,
      value: `${properties.cornerRadius}px`,
      category: 'borderRadius',
      rawValue: properties.cornerRadius,
      cssVariable: `--radius-${baseName}`,
    });
  }

  // Extract typography
  tokens.push(...extractTypographyTokens(properties, baseName));

  // Extract shadows
  if (properties.effects) {
    tokens.push(...extractShadowTokens(properties.effects, baseName));
  }

  // Recursively extract from children
  if (nodeInfo.children) {
    for (const child of nodeInfo.children) {
      tokens.push(...extractTokens(child));
    }
  }

  return deduplicateTokens(tokens);
}
