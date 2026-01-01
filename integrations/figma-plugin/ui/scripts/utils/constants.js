/**
 * Shared Constants
 * Centralized configuration values used across the plugin UI
 */

/**
 * Minimum score required for export (must match MCPClient.ts threshold)
 */
export const MIN_EXPORT_SCORE = 90;

/**
 * Valid message types that can be received from the Figma plugin
 */
export const VALID_MESSAGE_TYPES = [
  'SELECTION_CHANGED',
  'AUDIT_COMPLETE',
  'METADATA_ANALYZED',
  'METADATA_GENERATED',
  'METADATA_APPLIED',
  'METADATA_APPLY_FAILED',
  'REPORT_READY',
  'PIPELINE_COMPLETE',
  'PIPELINE_STEP',
  'MCP_CONNECTED',
  'MCP_DISCONNECTED',
  'AID_CONNECTED',
  'AID_PAIRED',
  'AID_PAIR_FAILED',
  'EXPORT_SUCCESS',
  'CONTENT_EXPORTED',
  'ERROR'
];

/**
 * Atomic design level configurations
 */
export const LEVEL_CONFIG = {
  atom: { icon: '🔵', color: '#dbeafe', textColor: '#1e40af' },
  molecule: { icon: '🟢', color: '#dcfce7', textColor: '#166534' },
  organism: { icon: '🟣', color: '#f3e8ff', textColor: '#7c3aed' },
  template: { icon: '📄', color: '#f3e8ff', textColor: '#7c3aed' },
  page: { icon: '📑', color: '#ffe4e6', textColor: '#be123c' }
};
