/**
 * @file services/AuthService/storage.ts
 * @description Storage operations and config persistence
 */

import type { AuthConfig } from './types';
import { STORAGE_KEYS } from './types';

/**
 * Load saved auth config from Figma's client storage
 */
export async function loadConfig(): Promise<AuthConfig | null> {
  try {
    const savedConfig = await figma.clientStorage.getAsync(STORAGE_KEYS.AUTH_CONFIG);
    if (savedConfig) {
      return JSON.parse(savedConfig);
    }
    return null;
  } catch (error) {
    console.error('Failed to load auth config:', error);
    return null;
  }
}

/**
 * Save auth config to Figma's client storage
 */
export async function saveConfig(config: AuthConfig): Promise<void> {
  await figma.clientStorage.setAsync(
    STORAGE_KEYS.AUTH_CONFIG,
    JSON.stringify(config)
  );
}

/**
 * Clear all saved auth data
 */
export async function clearAllAuthData(): Promise<void> {
  await figma.clientStorage.deleteAsync(STORAGE_KEYS.AUTH_CONFIG);
  await figma.clientStorage.deleteAsync(STORAGE_KEYS.TENANT_ID);
  await figma.clientStorage.deleteAsync(STORAGE_KEYS.API_KEY);
  await figma.clientStorage.deleteAsync(STORAGE_KEYS.ACCESS_TOKEN);
  await figma.clientStorage.deleteAsync(STORAGE_KEYS.REFRESH_TOKEN);
}

/**
 * Store OAuth state for CSRF protection
 */
export async function storeOAuthState(state: string): Promise<void> {
  await figma.clientStorage.setAsync(STORAGE_KEYS.OAUTH_STATE, state);
}

/**
 * Get stored OAuth state
 */
export async function getOAuthState(): Promise<string | undefined> {
  return figma.clientStorage.getAsync(STORAGE_KEYS.OAUTH_STATE);
}

/**
 * Store PKCE code verifier
 */
export async function storeCodeVerifier(codeVerifier: string): Promise<void> {
  await figma.clientStorage.setAsync(STORAGE_KEYS.OAUTH_CODE_VERIFIER, codeVerifier);
}

/**
 * Get stored PKCE code verifier
 */
export async function getCodeVerifier(): Promise<string | undefined> {
  return figma.clientStorage.getAsync(STORAGE_KEYS.OAUTH_CODE_VERIFIER);
}

/**
 * Clean up OAuth temporary storage
 */
export async function cleanupOAuthStorage(): Promise<void> {
  await figma.clientStorage.deleteAsync(STORAGE_KEYS.OAUTH_STATE);
  await figma.clientStorage.deleteAsync(STORAGE_KEYS.OAUTH_CODE_VERIFIER);
}
