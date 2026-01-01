/**
 * @file plugin/index.ts
 * @description Main barrel export for plugin modules
 */

// Types
export * from './types';

// State management
export {
  currentState,
  mcpClient,
  setMCPClient,
  getMCPClient,
  settings,
  updateSettings,
  getSettings,
  resetStateForNewSelection,
} from './state';

// UI messaging
export {
  sendToUI,
  sendError,
  sendPipelineStep,
  handleSelectionChange,
  selectNodeById,
} from './ui-messaging';

// MCP connection
export { connectMCP, disconnectMCP, isMCPConnected, stopHealthCheck } from './mcp-connection';

// Pipeline phases
export {
  runLocalAudit,
  runServerAudit,
  runDeepInspection,
  mergeAuditResults,
  analyzeMetadata,
  generateMetadata,
  applyMetadataToFigma,
  prepareFigmaDescription,
  injectTokensIfNeeded,
} from './pipeline';

// Export functionality
export {
  classifyComponentLevel,
  getDestinationPath,
  exportToAID,
  exportContent,
  extractContentData,
} from './export';

// AID pairing
export {
  getAIDEndpoint,
  setAIDEndpoint,
  loadCustomEndpoint,
  pairWithAID,
  checkAIDToken,
  disconnectFromAID,
  startHeartbeat,
  stopHeartbeat,
} from './aid-pairing';
