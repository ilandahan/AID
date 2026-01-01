/**
 * @file services/MCPClient/connection.ts
 * @description Connection management for MCP Client
 */

import type { MCPResponse } from '../../types';
import type { MCPClientConfig, ConnectionState, PendingRequest, ConnectionListener } from './types';
import { sendRequest, sendNotification } from './request';

/**
 * Connect to the MCP server
 */
export async function connect(
  config: MCPClientConfig,
  state: ConnectionState,
  requestIdRef: { value: number },
  pendingRequests: Map<number, PendingRequest>,
  notifyChange: () => void
): Promise<boolean> {
  try {
    const response = await sendRequest(
      'initialize',
      {
        protocolVersion: '2024-11-05',
        capabilities: {
          tools: {},
          resources: {},
        },
        clientInfo: {
          name: 'figma-atomic-plugin',
          version: '1.0.0',
        },
      },
      config,
      requestIdRef,
      pendingRequests
    );

    if (response.result) {
      state.isConnected = true;
      state.lastPing = new Date();
      state.serverInfo = response.result as ConnectionState['serverInfo'];

      // Send initialized notification
      await sendNotification('notifications/initialized', {}, config);

      notifyChange();
      return true;
    }

    return false;
  } catch (error) {
    console.error('MCP connection failed:', error);
    state.isConnected = false;
    notifyChange();
    return false;
  }
}

/**
 * Disconnect from the MCP server
 */
export function disconnect(
  state: ConnectionState,
  pendingRequests: Map<number, PendingRequest>,
  notifyChange: () => void
): void {
  state.isConnected = false;
  pendingRequests.forEach(({ reject, timeout }) => {
    clearTimeout(timeout);
    reject(new Error('Connection closed'));
  });
  pendingRequests.clear();
  notifyChange();
}

/**
 * Ping the server to check connection
 */
export async function ping(
  config: MCPClientConfig,
  state: ConnectionState,
  requestIdRef: { value: number },
  pendingRequests: Map<number, PendingRequest>
): Promise<boolean> {
  try {
    const response = await sendRequest('ping', {}, config, requestIdRef, pendingRequests);
    if (response.result) {
      state.lastPing = new Date();
      return true;
    }
    return false;
  } catch {
    return false;
  }
}

/**
 * Notify all connection listeners of state change
 */
export function notifyConnectionChange(
  state: ConnectionState,
  listeners: ConnectionListener[]
): void {
  const stateCopy = { ...state };
  for (const listener of listeners) {
    try {
      listener(stateCopy);
    } catch (e) {
      console.error('Connection listener error:', e);
    }
  }
}

/**
 * Subscribe to connection state changes
 */
export function onConnectionChange(
  callback: ConnectionListener,
  listeners: ConnectionListener[]
): () => void {
  listeners.push(callback);
  return () => {
    const index = listeners.indexOf(callback);
    if (index > -1) listeners.splice(index, 1);
  };
}
