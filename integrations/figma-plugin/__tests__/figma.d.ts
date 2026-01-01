/**
 * @file figma.d.ts
 * @description Type declarations for Figma global types in test environment
 * These types stub out the Figma plugin API types that aren't available in Node.js
 */

// Figma node types
declare type SceneNode = any;
declare type ComponentNode = any;
declare type ComponentSetNode = any;
declare type FrameNode = any;
declare type TextNode = any;
declare type InstanceNode = any;
declare type BaseNode = any;
declare type PageNode = any;

// Figma appearance types
declare type Paint = any;
declare type Effect = any;
declare type FontName = { family: string; style: string };
declare type LineHeight = { value: number; unit: string };
declare type LetterSpacing = { value: number; unit: string };

// Figma constants
declare type NodeType = string;
