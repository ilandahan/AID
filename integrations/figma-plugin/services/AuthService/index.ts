/**
 * @file services/AuthService/index.ts
 * @description Authentication service for the Figma plugin supporting API Key, OAuth, and JWT flows.
 * @created 2024-12
 * @refactored 2024-12 - Modular structure for maintainability
 */

import type { MCPRequest } from '../../types';
import type { AuthConfig, OAuthConfig, AuthResult, UserInfo, AuthMethod } from './types';

// Import from modules
import { loadConfig, saveConfig, clearAllAuthData } from './storage';
import { authenticateWithApiKey } from './api-key';
import { startOAuthFlow, completeOAuthFlow, refreshAccessToken } from './oauth';
import { authenticateWithJWT } from './jwt';
import { getAuthHeaders, signMCPRequest, isTokenExpired } from './signing';

// Re-export types
export type { AuthMethod, AuthConfig, OAuthConfig, AuthResult, UserInfo } from './types';
export { STORAGE_KEYS } from './types';

/**
 * AuthService class - Facade for all authentication operations
 */
export class AuthService {
  private config: AuthConfig | null = null;
  private user: UserInfo | null = null;

  // ============================================
  // Initialization
  // ============================================

  /**
   * Load saved auth config from Figma's client storage
   */
  async initialize(): Promise<boolean> {
    const savedConfig = await loadConfig();

    if (savedConfig) {
      this.config = savedConfig;

      // Check if token is expired
      if (isTokenExpired(this.config)) {
        // Try to refresh
        if (this.config.refreshToken) {
          const refreshed = await refreshAccessToken(this.config);
          if (refreshed) {
            this.config = refreshed;
            return true;
          }
        }
        this.config = null;
        return false;
      }

      return true;
    }

    return false;
  }

  /**
   * Clear all saved auth data
   */
  async logout(): Promise<void> {
    this.config = null;
    this.user = null;
    await clearAllAuthData();
  }

  // ============================================
  // API Key Authentication
  // ============================================

  /**
   * Authenticate with API Key + Tenant ID
   */
  async authenticateWithApiKey(
    tenantId: string,
    apiKey: string,
    backendUrl: string
  ): Promise<AuthResult> {
    const { result, config, user } = await authenticateWithApiKey(tenantId, apiKey, backendUrl);

    if (config) this.config = config;
    if (user) this.user = user;

    return result;
  }

  // ============================================
  // OAuth Authentication
  // ============================================

  /**
   * Start OAuth flow - opens browser for user to authenticate
   */
  async startOAuthFlow(oauthConfig: OAuthConfig): Promise<string> {
    const { authUrl, config } = await startOAuthFlow(oauthConfig);
    this.config = config;
    return authUrl;
  }

  /**
   * Complete OAuth flow with authorization code
   */
  async completeOAuthFlow(
    code: string,
    state: string,
    backendUrl: string
  ): Promise<AuthResult> {
    const { result, config, user } = await completeOAuthFlow(
      code,
      state,
      backendUrl,
      this.config
    );

    if (config) this.config = config;
    if (user) this.user = user;

    return result;
  }

  // ============================================
  // JWT Validation
  // ============================================

  /**
   * Authenticate with a pre-existing JWT
   */
  async authenticateWithJWT(jwt: string, backendUrl: string): Promise<AuthResult> {
    const { result, config, user } = await authenticateWithJWT(jwt, backendUrl);

    if (config) this.config = config;
    if (user) this.user = user;

    return result;
  }

  // ============================================
  // Request Signing
  // ============================================

  /**
   * Get authentication headers for requests
   */
  getAuthHeaders(): Record<string, string> {
    if (!this.config) {
      throw new Error('Not authenticated');
    }
    return getAuthHeaders(this.config);
  }

  /**
   * Sign MCP request with authentication
   */
  signMCPRequest(request: MCPRequest): MCPRequest & { _auth: Record<string, string> } {
    if (!this.config) {
      throw new Error('Not authenticated');
    }
    return signMCPRequest(request, this.config);
  }

  // ============================================
  // State Checking
  // ============================================

  /**
   * Check if authenticated
   */
  isAuthenticated(): boolean {
    if (!this.config) return false;
    return !isTokenExpired(this.config);
  }

  /**
   * Get current user
   */
  getUser(): UserInfo | null {
    return this.user;
  }

  /**
   * Get tenant ID
   */
  getTenantId(): string | null {
    return this.config?.tenantId ?? null;
  }

  /**
   * Get current auth method
   */
  getAuthMethod(): AuthMethod | null {
    return this.config?.method ?? null;
  }
}

// Export singleton
export const authService = new AuthService();
