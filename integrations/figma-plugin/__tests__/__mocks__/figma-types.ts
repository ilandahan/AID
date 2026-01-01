/**
 * @file figma-types.ts
 * @description Mock Figma types for Jest testing environment
 * These types stub out the Figma plugin API types that aren't available in Node.js
 */

// Stub Figma global types
export type SceneNode = any;
export type ComponentNode = any;
export type ComponentSetNode = any;
export type FrameNode = any;
export type TextNode = any;
export type InstanceNode = any;

// Figma appearance types
export type Paint = any;
export type Effect = any;
export type FontName = { family: string; style: string };
export type LineHeight = { value: number; unit: string };
export type LetterSpacing = { value: number; unit: string };
export type NodeType = string;
