/**
 * @file plugin/state.ts
 * @description Plugin state management - handles current component state and settings
 */

import type { PluginSettings } from '../types';
import type { PluginCurrentState } from './types';
import type { MCPClient } from '../services/MCPClient';

// ============================================
// Plugin State
// ============================================

/**
 * MCP client instance (singleton)
 */
export let mcpClient: MCPClient | null = null;

/**
 * Set the MCP client instance
 */
export function setMCPClient(client: MCPClient | null): void {
  mcpClient = client;
}

/**
 * Get the current MCP client instance
 */
export function getMCPClient(): MCPClient | null {
  return mcpClient;
}

/**
 * Current component state maintained by the plugin
 */
export const currentState: PluginCurrentState = {
  selectedNode: null,
  audit: null,
  metadata: null,
  generated: null,
  report: null,
  tokens: [],
};

/**
 * Reset the current state for a new selection
 */
export function resetStateForNewSelection(): void {
  currentState.audit = null;
  currentState.metadata = null;
  currentState.generated = null;
  currentState.report = null;
}

/**
 * Default plugin settings
 */
export const defaultSettings: PluginSettings = {
  mcpEndpoint: 'https://figma-plugin-server-983606191500.us-central1.run.app/mcp',
  autoClassify: true,
  defaultPriority: 5,
  tokenNamingConvention: 'kebab-case',
  outputFormat: 'react',
  includeStorybook: true,
  includeTests: false,
};

/**
 * Current plugin settings (can be modified at runtime)
 */
export let settings = { ...defaultSettings };

/**
 * Update plugin settings
 */
export function updateSettings(newSettings: Partial<PluginSettings>): void {
  settings = { ...settings, ...newSettings };
}

/**
 * Get current settings
 */
export function getSettings(): PluginSettings {
  return { ...settings };
}
