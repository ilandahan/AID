/**
 * @file services/AuthService/signing.ts
 * @description Request signing and auth headers
 */

import type { MCPRequest } from '../../types';
import type { AuthConfig } from './types';
import { secureRandom } from '../../crypto-utils';

/**
 * Get authentication headers for requests
 */
export function getAuthHeaders(config: AuthConfig): Record<string, string> {
  const headers: Record<string, string> = {};

  switch (config.method) {
    case 'api_key':
      headers['X-Tenant-ID'] = config.tenantId!;
      headers['X-API-Key'] = config.apiKey!;
      break;

    case 'oauth':
    case 'jwt':
      headers['Authorization'] = `Bearer ${config.accessToken}`;
      if (config.tenantId) {
        headers['X-Tenant-ID'] = config.tenantId;
      }
      break;
  }

  // Add request signature for extra security
  const timestamp = Date.now().toString();
  const nonce = secureRandom.randomString(16);
  headers['X-Timestamp'] = timestamp;
  headers['X-Nonce'] = nonce;

  return headers;
}

/**
 * Sign MCP request with authentication
 */
export function signMCPRequest(
  request: MCPRequest,
  config: AuthConfig
): MCPRequest & { _auth: Record<string, string> } {
  return {
    ...request,
    _auth: getAuthHeaders(config),
  };
}

/**
 * Check if token is expired
 */
export function isTokenExpired(config: AuthConfig): boolean {
  if (!config.expiresAt) return false;
  return Date.now() > config.expiresAt;
}
