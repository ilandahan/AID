/**
 * @file services/AuthService/oauth.ts
 * @description OAuth authentication flow with PKCE
 */

import type { AuthConfig, OAuthConfig, AuthResult, UserInfo } from './types';
import {
  saveConfig,
  storeOAuthState,
  storeCodeVerifier,
  getOAuthState,
  getCodeVerifier,
  cleanupOAuthStorage,
} from './storage';
import { sha256Base64Url, secureRandom } from '../../crypto-utils';
import { authLogger } from '../../Logger';

/**
 * Generate PKCE challenge pair using proper SHA-256 hashing
 */
async function generatePKCE(): Promise<{ codeVerifier: string; codeChallenge: string }> {
  // Generate a cryptographically suitable code verifier (43-128 chars, URL-safe)
  const codeVerifier = secureRandom.randomUrlSafe(64);

  // Compute SHA-256 hash and encode as base64url (RFC 7636 S256 method)
  const codeChallenge = sha256Base64Url(codeVerifier);

  authLogger.debug('Generated PKCE pair', {
    verifierLength: codeVerifier.length,
    challengeLength: codeChallenge.length,
  });

  return { codeVerifier, codeChallenge };
}

/**
 * Start OAuth flow - opens browser for user to authenticate
 */
export async function startOAuthFlow(oauthConfig: OAuthConfig): Promise<{
  authUrl: string;
  config: AuthConfig;
}> {
  // Generate PKCE challenge for security
  const { codeVerifier, codeChallenge } = await generatePKCE();

  // Store code verifier for later
  await storeCodeVerifier(codeVerifier);

  // Generate state for CSRF protection
  const state = secureRandom.randomString(32);
  await storeOAuthState(state);

  // Build authorization URL
  const params = new URLSearchParams({
    client_id: oauthConfig.clientId,
    redirect_uri: oauthConfig.redirectUri,
    response_type: 'code',
    scope: oauthConfig.scope,
    state,
    code_challenge: codeChallenge,
    code_challenge_method: 'S256',
  });

  const authUrl = `${oauthConfig.authorizationEndpoint}?${params.toString()}`;

  // Create OAuth config
  const config: AuthConfig = {
    method: 'oauth',
    oauthProvider: 'custom',
    oauthConfig,
  };

  return { authUrl, config };
}

/**
 * Complete OAuth flow with authorization code
 */
export async function completeOAuthFlow(
  code: string,
  state: string,
  backendUrl: string,
  currentConfig: AuthConfig | null
): Promise<{ result: AuthResult; config: AuthConfig | null; user: UserInfo | null }> {
  try {
    // Verify state
    const savedState = await getOAuthState();
    if (state !== savedState) {
      return {
        result: { success: false, error: 'Invalid state parameter' },
        config: null,
        user: null,
      };
    }

    // Get code verifier
    const codeVerifier = await getCodeVerifier();
    if (!codeVerifier) {
      return {
        result: { success: false, error: 'Missing code verifier' },
        config: null,
        user: null,
      };
    }

    const oauthConfig = currentConfig?.oauthConfig;
    if (!oauthConfig) {
      return {
        result: { success: false, error: 'OAuth config not found' },
        config: null,
        user: null,
      };
    }

    // Exchange code for tokens
    const tokenResponse = await fetch(oauthConfig.tokenEndpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        grant_type: 'authorization_code',
        client_id: oauthConfig.clientId,
        code,
        redirect_uri: oauthConfig.redirectUri,
        code_verifier: codeVerifier,
      }),
    });

    if (!tokenResponse.ok) {
      const error = await tokenResponse.json();
      return {
        result: { success: false, error: error.error_description || 'Token exchange failed' },
        config: null,
        user: null,
      };
    }

    const tokens = await tokenResponse.json();

    // Validate token with backend and get user info
    const userResponse = await fetch(`${backendUrl}/auth/oauth/callback`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${tokens.access_token}`,
      },
      body: JSON.stringify({
        accessToken: tokens.access_token,
        idToken: tokens.id_token,
      }),
    });

    if (!userResponse.ok) {
      return {
        result: { success: false, error: 'Failed to validate token with backend' },
        config: null,
        user: null,
      };
    }

    const userData = await userResponse.json();

    // Update config with tokens
    const config: AuthConfig = {
      ...currentConfig!,
      accessToken: tokens.access_token,
      refreshToken: tokens.refresh_token,
      expiresAt: Date.now() + (tokens.expires_in * 1000),
      tenantId: userData.tenantId,
    };

    await saveConfig(config);

    // Clean up
    await cleanupOAuthStorage();

    return {
      result: { success: true, user: userData.user },
      config,
      user: userData.user,
    };
  } catch (error) {
    return {
      result: {
        success: false,
        error: error instanceof Error ? error.message : 'OAuth flow failed',
      },
      config: null,
      user: null,
    };
  }
}

/**
 * Refresh the access token
 */
export async function refreshAccessToken(config: AuthConfig): Promise<AuthConfig | null> {
  if (!config.refreshToken || !config.oauthConfig) {
    return null;
  }

  try {
    const response = await fetch(config.oauthConfig.tokenEndpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        grant_type: 'refresh_token',
        client_id: config.oauthConfig.clientId,
        refresh_token: config.refreshToken,
      }),
    });

    if (!response.ok) {
      return null;
    }

    const tokens = await response.json();

    const updatedConfig: AuthConfig = {
      ...config,
      accessToken: tokens.access_token,
      expiresAt: Date.now() + (tokens.expires_in * 1000),
    };

    if (tokens.refresh_token) {
      updatedConfig.refreshToken = tokens.refresh_token;
    }

    await saveConfig(updatedConfig);
    return updatedConfig;
  } catch {
    return null;
  }
}
