/**
 * @file plugin/mcp-connection.ts
 * @description MCP connection management with health monitoring
 */

import { createMCPClient } from '../services';
import { logger } from '../Logger';
import { sendToUI, sendError } from './ui-messaging';
import { mcpClient, setMCPClient, settings, updateSettings } from './state';

// Connection health check interval (30 seconds)
const HEALTH_CHECK_INTERVAL = 30000;
let healthCheckTimer: ReturnType<typeof setInterval> | null = null;

// ============================================
// Connection Health Monitoring
// ============================================

/**
 * Start periodic connection health checks
 */
function startHealthCheck(): void {
  // Clear any existing timer
  stopHealthCheck();

  healthCheckTimer = setInterval(async () => {
    if (mcpClient && mcpClient.isConnected()) {
      try {
        const isAlive = await mcpClient.ping();
        if (!isAlive) {
          logger.warn('[PLUGIN] Health check failed - connection lost');
          handleConnectionLost();
        }
      } catch (error) {
        logger.error('[PLUGIN] Health check error:', error);
        handleConnectionLost();
      }
    }
  }, HEALTH_CHECK_INTERVAL);

  logger.debug('[PLUGIN] Started connection health check');
}

/**
 * Stop connection health checks
 */
function stopHealthCheck(): void {
  if (healthCheckTimer) {
    clearInterval(healthCheckTimer);
    healthCheckTimer = null;
    logger.debug('[PLUGIN] Stopped connection health check');
  }
}

/**
 * Handle connection lost - update state and notify UI
 */
function handleConnectionLost(): void {
  logger.warn('[PLUGIN] Connection lost - notifying UI');
  stopHealthCheck();
  setMCPClient(null);
  sendToUI({ type: 'MCP_DISCONNECTED' });
  figma.notify('Connection lost. Please reconnect.', { error: true });
}

// ============================================
// MCP Connection Functions
// ============================================

/**
 * Connect to MCP server
 */
export async function connectMCP(endpoint: string): Promise<void> {
  try {
    const client = createMCPClient(endpoint);
    const connected = await client.connect();

    if (connected) {
      setMCPClient(client);
      updateSettings({ mcpEndpoint: endpoint });
      sendToUI({ type: 'MCP_CONNECTED' });
      figma.notify('Connected to MCP server');

      // Start health monitoring
      startHealthCheck();
    } else {
      throw new Error('Connection failed');
    }
  } catch (error) {
    sendError(
      `MCP connection failed: ${error instanceof Error ? error.message : 'Unknown error'}`
    );
    setMCPClient(null);
  }
}

/**
 * Disconnect from MCP server
 */
export async function disconnectMCP(): Promise<void> {
  stopHealthCheck();
  if (mcpClient) {
    await mcpClient.disconnect();
    setMCPClient(null);
    sendToUI({ type: 'MCP_DISCONNECTED' });
    figma.notify('Disconnected from MCP');
  }
}

/**
 * Check if MCP is connected
 */
export function isMCPConnected(): boolean {
  return mcpClient !== null && mcpClient.isConnected();
}

/**
 * Stop health check (exported for cleanup)
 */
export { stopHealthCheck };
