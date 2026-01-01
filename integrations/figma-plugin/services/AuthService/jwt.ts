/**
 * @file services/AuthService/jwt.ts
 * @description JWT authentication flow
 */

import type { AuthConfig, AuthResult, UserInfo } from './types';
import { saveConfig } from './storage';

/**
 * Authenticate with a pre-existing JWT
 * Useful when user logged in elsewhere and has a token
 */
export async function authenticateWithJWT(
  jwt: string,
  backendUrl: string
): Promise<{ result: AuthResult; config: AuthConfig | null; user: UserInfo | null }> {
  try {
    // Validate JWT with backend
    const response = await fetch(`${backendUrl}/auth/jwt/validate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${jwt}`,
      },
    });

    if (!response.ok) {
      return {
        result: { success: false, error: 'Invalid JWT' },
        config: null,
        user: null,
      };
    }

    const data = await response.json();

    const config: AuthConfig = {
      method: 'jwt',
      accessToken: jwt,
      tenantId: data.tenantId,
      expiresAt: data.exp * 1000, // JWT exp is in seconds
    };

    // Try to persist config to storage, but don't fail if storage errors
    // (e.g., Figma's IndexedDB can sometimes be unavailable)
    try {
      await saveConfig(config);
    } catch (storageError) {
      console.warn('[AuthService] Could not save auth config to storage (session-only mode):', storageError);
    }

    // Always return config for in-memory authentication even if storage failed
    return {
      result: { success: true, user: data.user },
      config,
      user: data.user,
    };
  } catch (error) {
    return {
      result: {
        success: false,
        error: error instanceof Error ? error.message : 'JWT validation failed',
      },
      config: null,
      user: null,
    };
  }
}
