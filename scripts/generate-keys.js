#!/usr/bin/env node

/**
 * AID Security Keys Generator
 * 
 * Generates secure random keys for:
 * - NEXTAUTH_SECRET
 * - API_SECRET_KEY
 * - ENCRYPTION_KEY
 * 
 * Usage:
 *   npm run generate:keys           - Generate and display keys
 *   npm run generate:keys -- --env  - Output in .env format
 */

const crypto = require('crypto');

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
  dim: '\x1b[2m',
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

/**
 * Generate a secure random key
 * @param {number} length - Length in bytes
 * @param {string} encoding - Output encoding ('base64' or 'hex')
 */
function generateKey(length = 32, encoding = 'base64') {
  return crypto.randomBytes(length).toString(encoding);
}

/**
 * Generate all required keys
 */
function generateAllKeys() {
  return {
    NEXTAUTH_SECRET: generateKey(32, 'base64'),
    API_SECRET_KEY: generateKey(32, 'hex'),
    ENCRYPTION_KEY: generateKey(32, 'base64'),
    SESSION_SECRET: generateKey(32, 'base64'),
    CSRF_SECRET: generateKey(16, 'hex'),
  };
}

/**
 * Display keys in human-readable format
 */
function displayKeys(keys) {
  log('\n🔐 Generated Security Keys', 'blue');
  log('===========================', 'dim');
  log('\nCopy these to your .env.local file:\n', 'yellow');
  
  Object.entries(keys).forEach(([name, value]) => {
    log(`${name}:`, 'cyan');
    log(`  ${value}`, 'green');
    console.log();
  });
  
  log('⚠️  Security Notes:', 'yellow');
  log('  - Never commit these keys to version control', 'dim');
  log('  - Use different keys for each environment', 'dim');
  log('  - Rotate keys periodically in production', 'dim');
  log('  - Store production keys in a secure vault', 'dim');
}

/**
 * Display keys in .env format
 */
function displayEnvFormat(keys) {
  log('# Generated Security Keys', 'dim');
  log(`# Generated at: ${new Date().toISOString()}`, 'dim');
  log('# Add these to your .env.local file\n', 'dim');
  
  Object.entries(keys).forEach(([name, value]) => {
    console.log(`${name}=${value}`);
  });
}

/**
 * Validate key strength
 */
function validateKeyStrength(key, minLength = 32) {
  const buffer = Buffer.from(key, 'base64');
  return buffer.length >= minLength;
}

// Main execution
function main() {
  const args = process.argv.slice(2);
  const envFormat = args.includes('--env') || args.includes('-e');
  
  const keys = generateAllKeys();
  
  // Validate generated keys
  const allValid = Object.values(keys).every(key => 
    key.length >= 20 // Minimum length check
  );
  
  if (!allValid) {
    log('❌ Key generation failed - keys too short', 'red');
    process.exit(1);
  }
  
  if (envFormat) {
    displayEnvFormat(keys);
  } else {
    displayKeys(keys);
  }
}

main();
