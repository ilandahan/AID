/**
 * @file setup.ts
 * @description Jest setup file - declares Figma global types for testing
 */

// Declare Figma global types that exist in the Figma plugin environment
// but are not available in Node.js test environment
declare global {
  // Figma node types
  type SceneNode = any;
  type ComponentNode = any;
  type ComponentSetNode = any;
  type FrameNode = any;
  type TextNode = any;
  type InstanceNode = any;
  type BaseNode = any;
  type PageNode = any;

  // Figma appearance types
  type Paint = any;
  type Effect = any;
  type FontName = { family: string; style: string };
  type LineHeight = { value: number; unit: string };
  type LetterSpacing = { value: number; unit: string };

  // Figma constants
  type NodeType = string;
}

export {};
