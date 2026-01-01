/**
 * @file services/MCPClient/request.ts
 * @description Request handling and retry logic for MCP Client
 */

import type { MCPRequest, MCPResponse } from '../../types';
import type { MCPClientConfig, PendingRequest } from './types';
import { authService } from '../../AuthService';

/**
 * Send a JSON-RPC request with retry logic
 */
export async function sendRequest(
  method: string,
  params: unknown,
  config: MCPClientConfig,
  requestIdRef: { value: number },
  pendingRequests: Map<number, PendingRequest>
): Promise<MCPResponse> {
  const id = ++requestIdRef.value;

  const request: MCPRequest = {
    jsonrpc: '2.0',
    id,
    method,
    params,
  };

  return executeWithRetry(async () => {
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        pendingRequests.delete(id);
        reject(new Error(`Request timeout: ${method}`));
      }, config.timeout || 30000);

      pendingRequests.set(id, { resolve, reject, timeout });

      sendToServer(request, config, pendingRequests).catch(error => {
        clearTimeout(timeout);
        pendingRequests.delete(id);
        reject(error);
      });
    });
  }, config);
}

/**
 * Send a notification (no response expected)
 */
export async function sendNotification(
  method: string,
  params: unknown,
  config: MCPClientConfig
): Promise<void> {
  const notification = {
    jsonrpc: '2.0' as const,
    method,
    params,
  };

  await sendToServer(notification, config);
}

/**
 * Execute request with exponential backoff retry logic
 */
async function executeWithRetry<T>(
  operation: () => Promise<T>,
  config: MCPClientConfig
): Promise<T> {
  let lastError: Error | undefined;
  const retryAttempts = config.retryAttempts || 3;
  const retryDelay = config.retryDelay || 1000;

  for (let attempt = 0; attempt < retryAttempts; attempt++) {
    try {
      return await operation();
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));

      // Don't retry on client errors
      if (isClientError(lastError)) {
        throw lastError;
      }

      // Wait before retry with exponential backoff
      if (attempt < retryAttempts - 1) {
        await delay(retryDelay * Math.pow(2, attempt));
      }
    }
  }

  throw lastError;
}

/**
 * Send data to MCP server via HTTP
 */
async function sendToServer(
  data: unknown,
  config: MCPClientConfig,
  pendingRequests?: Map<number, PendingRequest>
): Promise<void> {
  // Check authentication if required
  if (config.requireAuth !== false && !authService.isAuthenticated()) {
    throw new Error('Not authenticated. Please login first.');
  }

  // Get auth headers
  const authHeaders = authService.isAuthenticated()
    ? authService.getAuthHeaders()
    : {};

  const response = await fetch(config.endpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...authHeaders,
    },
    body: JSON.stringify(data),
  });

  if (response.status === 401) {
    throw new Error('Authentication failed. Please login again.');
  }

  if (response.status === 403) {
    throw new Error('Access denied. Check your permissions.');
  }

  if (!response.ok) {
    throw new Error(`HTTP error: ${response.status} ${response.statusText}`);
  }

  const result = await response.json() as MCPResponse;

  // Handle response for pending requests
  if (pendingRequests && 'id' in result && result.id !== null) {
    const pending = pendingRequests.get(result.id as number);
    if (pending) {
      clearTimeout(pending.timeout);
      pendingRequests.delete(result.id as number);
      pending.resolve(result);
    }
  }
}

/**
 * Check if error is a client error (shouldn't retry)
 */
function isClientError(error: Error): boolean {
  const message = error.message.toLowerCase();
  return (
    message.includes('invalid') ||
    message.includes('validation') ||
    message.includes('not found') ||
    message.includes('unauthorized') ||
    message.includes('forbidden')
  );
}

/**
 * Delay helper for retry backoff
 */
function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}
