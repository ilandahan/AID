/**
 * @file testAuth.js
 * @description Shared authentication helpers for integration tests.
 * Provides functions to generate valid JWT tokens for testing.
 */

const request = require('supertest');

const BASE_URL = 'http://localhost:3001';

/**
 * Generate a valid JWT token for testing.
 * Uses the pairing flow to get a real token.
 * @returns {Promise<string>} JWT token
 */
async function getTestToken() {
  // Generate pairing code
  const pairingRes = await request(BASE_URL)
    .post('/auth/generate-pairing')
    .send({ tenantId: 'test-tenant', projectPath: '/test/path' });

  const code = pairingRes.body.code.replace(' ', '');

  // Exchange for JWT
  const pairRes = await request(BASE_URL)
    .post('/auth/pair')
    .send({ code });

  return pairRes.body.token;
}

/**
 * Create an authenticated request helper.
 * @param {string} token - JWT token
 * @returns {Function} Request function with auth header
 */
function authRequest(token) {
  return {
    post: (path) => request(BASE_URL)
      .post(path)
      .set('Authorization', `Bearer ${token}`),
    get: (path) => request(BASE_URL)
      .get(path)
      .set('Authorization', `Bearer ${token}`)
  };
}

module.exports = {
  BASE_URL,
  getTestToken,
  authRequest
};
