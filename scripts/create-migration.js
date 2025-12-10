#!/usr/bin/env node

/**
 * AID Database Migration Creator
 * 
 * Usage:
 *   npm run db:migrate:create -- --name add_users_table
 *   npm run db:migrate:create -- --name "add user preferences"
 */

const { execSync } = require('child_process');
const path = require('path');

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

function getMigrationName() {
  const args = process.argv.slice(2);
  const nameIndex = args.findIndex(arg => arg === '--name' || arg === '-n');
  
  if (nameIndex === -1 || !args[nameIndex + 1]) {
    return null;
  }
  
  return args[nameIndex + 1];
}

function formatMigrationName(name) {
  // Convert to snake_case and remove special characters
  return name
    .toLowerCase()
    .replace(/\s+/g, '_')
    .replace(/[^a-z0-9_]/g, '')
    .replace(/_+/g, '_')
    .replace(/^_|_$/g, '');
}

function createMigration(name) {
  const formattedName = formatMigrationName(name);
  
  log(`\n📝 Creating migration: ${formattedName}`, 'blue');
  log('================================', 'dim');
  
  try {
    // First, check if there are schema changes
    log('\n1. Checking for schema changes...', 'dim');
    
    // Create the migration
    execSync(`npx prisma migrate dev --name ${formattedName}`, {
      stdio: 'inherit',
      env: { ...process.env },
    });
    
    log('\n✅ Migration created successfully!', 'green');
    log('\nNext steps:', 'yellow');
    log('  1. Review the generated migration in prisma/migrations/', 'dim');
    log('  2. Test the migration locally', 'dim');
    log('  3. Commit the migration files', 'dim');
    
  } catch (error) {
    log('\n❌ Failed to create migration', 'red');
    log('\nCommon issues:', 'yellow');
    log('  - No changes detected in schema.prisma', 'dim');
    log('  - Database connection issues', 'dim');
    log('  - Conflicting migrations', 'dim');
    process.exit(1);
  }
}

function showUsage() {
  log('\n🗄️  AID Migration Creator', 'blue');
  log('========================', 'dim');
  log('\nUsage:', 'yellow');
  log('  npm run db:migrate:create -- --name <migration_name>', 'dim');
  log('\nExamples:', 'yellow');
  log('  npm run db:migrate:create -- --name add_users_table', 'dim');
  log('  npm run db:migrate:create -- --name "add user preferences"', 'dim');
  log('\nNaming conventions:', 'yellow');
  log('  - Use descriptive names: add_users_table, remove_legacy_field', 'dim');
  log('  - Avoid generic names: update, fix, change', 'dim');
}

// Main execution
function main() {
  const name = getMigrationName();
  
  if (!name) {
    showUsage();
    process.exit(1);
  }
  
  createMigration(name);
}

main();
