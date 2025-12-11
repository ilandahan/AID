#!/usr/bin/env node

/**
 * AID Database Migration Runner
 * 
 * Usage:
 *   npm run db:migrate           - Run pending migrations
 *   npm run db:migrate -- --up   - Run pending migrations (explicit)
 *   npm run db:migrate -- --down - Rollback last migration
 *   npm run db:migrate -- --status - Show migration status
 */

const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

// Configuration
const MIGRATIONS_DIR = path.join(__dirname, '..', 'prisma', 'migrations');
const DATABASE_URL = process.env.DATABASE_URL;

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  blue: '\x1b[34m',
  dim: '\x1b[2m',
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function checkEnvironment() {
  if (!DATABASE_URL) {
    log('❌ DATABASE_URL environment variable is not set', 'red');
    log('   Please set it in your .env file', 'dim');
    process.exit(1);
  }
  
  log('✓ Environment configured', 'green');
}

function runMigrations() {
  log('\n🔄 Running database migrations...', 'blue');
  
  try {
    execSync('npx prisma migrate deploy', {
      stdio: 'inherit',
      env: { ...process.env },
    });
    log('\n✅ Migrations completed successfully', 'green');
  } catch (error) {
    log('\n❌ Migration failed', 'red');
    process.exit(1);
  }
}

function rollbackMigration() {
  log('\n⚠️  Rolling back last migration...', 'yellow');
  log('   Note: Prisma doesn\'t support automatic rollback.', 'dim');
  log('   You may need to manually revert using:', 'dim');
  log('   npx prisma migrate resolve --rolled-back <migration_name>', 'dim');
  
  // For manual rollback, show recent migrations
  showStatus();
}

function showStatus() {
  log('\n📋 Migration Status:', 'blue');
  
  try {
    execSync('npx prisma migrate status', {
      stdio: 'inherit',
      env: { ...process.env },
    });
  } catch (error) {
    // Status command may exit with non-zero if there are pending migrations
    // This is expected behavior
  }
}

function generateClient() {
  log('\n🔨 Generating Prisma client...', 'blue');
  
  try {
    execSync('npx prisma generate', {
      stdio: 'inherit',
      env: { ...process.env },
    });
    log('✅ Prisma client generated', 'green');
  } catch (error) {
    log('❌ Failed to generate Prisma client', 'red');
    process.exit(1);
  }
}

// Main execution
function main() {
  const args = process.argv.slice(2);
  const command = args[0] || '--up';
  
  log('🗄️  AID Database Migration Tool', 'blue');
  log('================================', 'dim');
  
  checkEnvironment();
  
  switch (command) {
    case '--up':
    case 'up':
      runMigrations();
      generateClient();
      break;
      
    case '--down':
    case 'down':
      rollbackMigration();
      break;
      
    case '--status':
    case 'status':
      showStatus();
      break;
      
    case '--generate':
    case 'generate':
      generateClient();
      break;
      
    default:
      log(`Unknown command: ${command}`, 'red');
      log('\nUsage:', 'yellow');
      log('  --up      Run pending migrations (default)', 'dim');
      log('  --down    Rollback guidance', 'dim');
      log('  --status  Show migration status', 'dim');
      log('  --generate  Generate Prisma client', 'dim');
      process.exit(1);
  }
}

main();
