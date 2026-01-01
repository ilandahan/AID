/**
 * @file MCPClient.ts
 * @description MCP (Model Context Protocol) client for communication with the AID backend server.
 *              Handles JSON-RPC requests, retry logic, and the 4-phase quality pipeline API.
 * @created 2024-12
 * @refactored 2024-12 - Extracted modules to ./services/MCPClient/
 *
 * This file re-exports the modular MCPClient for backward compatibility.
 * The actual implementation is in ./services/MCPClient/
 */

// Re-export everything from the modular implementation
export {
  MCPClient,
  createMCPClient,
  type MCPClientConfig,
  type ConnectionState,
} from './services/MCPClient';

// Default export for backward compatibility
export { MCPClient as default } from './services/MCPClient';
