/**
 * @file services/AuthService/api-key.ts
 * @description API Key authentication flow
 */

import type { AuthConfig, AuthResult, UserInfo } from './types';
import { saveConfig } from './storage';

/**
 * Authenticate with API Key + Tenant ID
 * This is the simplest method for B2B SaaS
 */
export async function authenticateWithApiKey(
  tenantId: string,
  apiKey: string,
  backendUrl: string
): Promise<{ result: AuthResult; config: AuthConfig | null; user: UserInfo | null }> {
  try {
    // Validate the API key against the backend
    const response = await fetch(`${backendUrl}/auth/validate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Tenant-ID': tenantId,
        'X-API-Key': apiKey,
      },
      body: JSON.stringify({ tenantId, apiKey }),
    });

    if (!response.ok) {
      const error = await response.json();
      return {
        result: {
          success: false,
          error: error.message || 'Invalid API key or tenant ID',
        },
        config: null,
        user: null,
      };
    }

    const data = await response.json();

    // Create the config
    const config: AuthConfig = {
      method: 'api_key',
      apiKey,
      tenantId,
    };

    await saveConfig(config);

    return {
      result: {
        success: true,
        user: data.user,
      },
      config,
      user: data.user,
    };
  } catch (error) {
    return {
      result: {
        success: false,
        error: error instanceof Error ? error.message : 'Authentication failed',
      },
      config: null,
      user: null,
    };
  }
}
