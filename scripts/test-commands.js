#!/usr/bin/env node
/**
 * AID Commands Validation Script
 * Tests that all slash commands are properly configured and functional
 */

const fs = require('fs');
const path = require('path');

const COMMANDS_DIR = path.join(__dirname, '..', '.claude', 'commands');
const STATE_FILE = path.join(__dirname, '..', '.aid', 'state.json');
const CONTEXT_FILE = path.join(__dirname, '..', '.aid', 'context.json');

// Expected commands and their requirements
const EXPECTED_COMMANDS = {
  // Phase Management
  'phase-advance': {
    required: true,
    description: 'Advance to next phase',
    mustContain: ['current_phase', 'phase_approved', '.aid/state.json'],
  },
  'phase-approve': {
    required: true,
    description: 'Approve current phase',
    mustContain: ['phase_approved', 'checklist', 'approve'],
  },
  'gate-check': {
    required: true,
    description: 'Check if phase ready to advance',
    mustContain: ['deliverables', 'READY', 'NOT READY'],
  },
  'phase': {
    required: true,
    description: 'Navigate to specific phase',
    mustContain: ['Phase', 'PRD', 'Tech Spec', 'Development'],
  },

  // AID Session Management
  'aid-start': {
    required: true,
    description: 'Start AID session',
    mustContain: ['role', 'phase', 'session', '.mcp.json'],
  },
  'aid-end': {
    required: true,
    description: 'End AID session',
    mustContain: ['session', 'feedback'],
  },
  'aid-init': {
    required: true,
    description: 'Initialize AID project',
    mustContain: ['.aid', 'state.json'],
  },
  'aid-status': {
    required: true,
    description: 'Show AID status',
    mustContain: ['phase', 'session', 'state'],
  },

  // Development Commands
  'prd': {
    required: true,
    description: 'Create PRD document',
    mustContain: ['PRD', 'requirements'],
  },
  'tech-spec': {
    required: true,
    description: 'Create technical specification',
    mustContain: ['technical', 'specification', 'architecture'],
  },
  'architecture': {
    required: true,
    description: 'System architecture design',
    mustContain: ['architecture', 'system'],
  },
  'design-system': {
    required: true,
    description: 'Build design system from Figma',
    mustContain: ['design', 'Figma', 'component'],
  },
  'build-page': {
    required: true,
    description: 'Compose pages from components',
    mustContain: ['page', 'component', 'atomic'],
  },
  'code-review': {
    required: true,
    description: 'Review code quality',
    mustContain: ['review', 'code', 'quality'],
  },
  'write-tests': {
    required: true,
    description: 'TDD test writing',
    mustContain: ['test', 'TDD'],
  },
  'test-review': {
    required: true,
    description: 'Review test quality',
    mustContain: ['test', 'review'],
  },
  'jira-breakdown': {
    required: true,
    description: 'Break spec into Jira issues',
    mustContain: ['Jira', 'Epic', 'Story'],
  },

  // Utility Commands
  'link-project': {
    required: true,
    description: 'Link external project to AID',
    mustContain: ['symlink', 'project', 'AID'],
  },
  'start-project': {
    required: false,
    description: 'Initialize new project',
    mustContain: ['project', 'init'],
  },

  // Memory System
  'aid-improve': {
    required: false,
    description: 'Run learning cycle',
    mustContain: ['learning', 'improve'],
  },
  'aid-memory': {
    required: false,
    description: 'Manage memory entries',
    mustContain: ['memory'],
  },
  'aid-reset': {
    required: false,
    description: 'Reset memory system',
    mustContain: ['reset'],
  },
};

// Test results
const results = {
  passed: [],
  failed: [],
  warnings: [],
};

function log(type, message) {
  const icons = {
    pass: '\x1b[32m✓\x1b[0m',
    fail: '\x1b[31m✗\x1b[0m',
    warn: '\x1b[33m⚠\x1b[0m',
    info: '\x1b[34mℹ\x1b[0m',
  };
  console.log(`  ${icons[type]} ${message}`);
}

function testCommandFile(name, config) {
  const filePath = path.join(COMMANDS_DIR, `${name}.md`);

  // Check file exists
  if (!fs.existsSync(filePath)) {
    if (config.required) {
      results.failed.push(`${name}: File not found (REQUIRED)`);
      log('fail', `${name}.md - File not found (REQUIRED)`);
    } else {
      results.warnings.push(`${name}: File not found (optional)`);
      log('warn', `${name}.md - File not found (optional)`);
    }
    return false;
  }

  // Read file content
  const content = fs.readFileSync(filePath, 'utf8');

  // Check file is not empty
  if (content.trim().length < 50) {
    results.failed.push(`${name}: File is too short/empty`);
    log('fail', `${name}.md - File is too short`);
    return false;
  }

  // Check has title (starts with #)
  if (!content.startsWith('#')) {
    results.warnings.push(`${name}: Missing title header`);
    log('warn', `${name}.md - Missing # title header`);
  }

  // Check required content
  const missingContent = [];
  for (const keyword of config.mustContain) {
    if (!content.toLowerCase().includes(keyword.toLowerCase())) {
      missingContent.push(keyword);
    }
  }

  if (missingContent.length > 0) {
    results.warnings.push(`${name}: Missing expected content: ${missingContent.join(', ')}`);
    log('warn', `${name}.md - Missing: ${missingContent.join(', ')}`);
  }

  // Check has Usage section
  if (!content.includes('## Usage') && !content.includes('## usage')) {
    results.warnings.push(`${name}: Missing Usage section`);
  }

  results.passed.push(name);
  log('pass', `${name}.md - Valid`);
  return true;
}

function testStateFiles() {
  console.log('\n📁 Testing State Files...\n');

  // Test state.json
  if (fs.existsSync(STATE_FILE)) {
    try {
      const state = JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));

      // Check required fields
      const requiredFields = ['current_phase', 'phase_name', 'phase_approved', 'feedback_provided', 'current_session'];
      const missingFields = requiredFields.filter(f => !(f in state));

      if (missingFields.length > 0) {
        results.failed.push(`state.json: Missing fields: ${missingFields.join(', ')}`);
        log('fail', `state.json - Missing: ${missingFields.join(', ')}`);
      } else {
        results.passed.push('state.json');
        log('pass', `state.json - Valid (Phase ${state.current_phase}: ${state.phase_name})`);
      }
    } catch (e) {
      results.failed.push(`state.json: Invalid JSON - ${e.message}`);
      log('fail', `state.json - Invalid JSON`);
    }
  } else {
    results.warnings.push('state.json: Not found (run /aid-init)');
    log('warn', 'state.json - Not found (run /aid-init)');
  }

  // Test context.json
  if (fs.existsSync(CONTEXT_FILE)) {
    try {
      const context = JSON.parse(fs.readFileSync(CONTEXT_FILE, 'utf8'));
      results.passed.push('context.json');
      log('pass', 'context.json - Valid');
    } catch (e) {
      results.failed.push(`context.json: Invalid JSON - ${e.message}`);
      log('fail', 'context.json - Invalid JSON');
    }
  } else {
    results.warnings.push('context.json: Not found');
    log('warn', 'context.json - Not found');
  }
}

function testMCPConfig() {
  console.log('\n🔌 Testing MCP Configuration...\n');

  const mcpFile = path.join(__dirname, '..', '.mcp.json');
  const mcpExample = path.join(__dirname, '..', '.mcp.json.example');

  // Test .mcp.json.example (should always exist in repo)
  if (fs.existsSync(mcpExample)) {
    try {
      const config = JSON.parse(fs.readFileSync(mcpExample, 'utf8'));
      if (config.mcpServers) {
        const servers = Object.keys(config.mcpServers);
        results.passed.push('.mcp.json.example');
        log('pass', `.mcp.json.example - Valid (${servers.length} servers: ${servers.join(', ')})`);
      } else {
        results.failed.push('.mcp.json.example: Missing mcpServers');
        log('fail', '.mcp.json.example - Missing mcpServers key');
      }
    } catch (e) {
      results.failed.push(`.mcp.json.example: Invalid JSON`);
      log('fail', '.mcp.json.example - Invalid JSON');
    }
  } else {
    results.failed.push('.mcp.json.example: Not found');
    log('fail', '.mcp.json.example - Not found');
  }

  // Test .mcp.json (user config, may not exist)
  if (fs.existsSync(mcpFile)) {
    try {
      const config = JSON.parse(fs.readFileSync(mcpFile, 'utf8'));
      const servers = Object.keys(config.mcpServers || {});

      // Check for placeholder tokens
      const content = fs.readFileSync(mcpFile, 'utf8');
      if (content.includes('YOUR_') || content.includes('your@email')) {
        results.warnings.push('.mcp.json: Contains placeholder tokens');
        log('warn', '.mcp.json - Contains placeholder tokens (edit before use)');
      } else {
        results.passed.push('.mcp.json');
        log('pass', `.mcp.json - Configured (${servers.length} servers)`);
      }
    } catch (e) {
      results.failed.push('.mcp.json: Invalid JSON');
      log('fail', '.mcp.json - Invalid JSON');
    }
  } else {
    log('info', '.mcp.json - Not found (will be created on install)');
  }
}

function testSkills() {
  console.log('\n🎯 Testing Skills...\n');

  const skillsDir = path.join(__dirname, '..', '.claude', 'skills');
  const expectedSkills = [
    'atomic-design',
    'atomic-page-builder',
    'code-review',
    'context-tracking',
    'learning-mode',
    'phase-enforcement',
    'system-architect',
    'test-driven',
  ];

  if (!fs.existsSync(skillsDir)) {
    results.warnings.push('Skills directory not found');
    log('warn', '.claude/skills/ - Directory not found (run install script)');
    return;
  }

  for (const skill of expectedSkills) {
    const skillPath = path.join(skillsDir, skill);
    if (fs.existsSync(skillPath)) {
      // Check for SKILL.md
      const skillFile = path.join(skillPath, 'SKILL.md');
      if (fs.existsSync(skillFile)) {
        results.passed.push(`skill:${skill}`);
        log('pass', `${skill}/ - Valid`);
      } else {
        results.warnings.push(`skill:${skill} - Missing SKILL.md`);
        log('warn', `${skill}/ - Missing SKILL.md`);
      }
    } else {
      results.warnings.push(`skill:${skill} - Not found`);
      log('warn', `${skill}/ - Not found`);
    }
  }
}

function printSummary() {
  console.log('\n' + '='.repeat(50));
  console.log('📊 TEST SUMMARY');
  console.log('='.repeat(50));

  console.log(`\n  \x1b[32m✓ Passed: ${results.passed.length}\x1b[0m`);
  console.log(`  \x1b[31m✗ Failed: ${results.failed.length}\x1b[0m`);
  console.log(`  \x1b[33m⚠ Warnings: ${results.warnings.length}\x1b[0m`);

  if (results.failed.length > 0) {
    console.log('\n\x1b[31mFailed Tests:\x1b[0m');
    results.failed.forEach(f => console.log(`  - ${f}`));
  }

  if (results.warnings.length > 0 && process.argv.includes('--verbose')) {
    console.log('\n\x1b[33mWarnings:\x1b[0m');
    results.warnings.forEach(w => console.log(`  - ${w}`));
  }

  console.log('\n' + '='.repeat(50));

  if (results.failed.length === 0) {
    console.log('\x1b[32m✓ All critical tests passed!\x1b[0m\n');
    process.exit(0);
  } else {
    console.log('\x1b[31m✗ Some tests failed. Please fix before proceeding.\x1b[0m\n');
    process.exit(1);
  }
}

// Main
console.log('\n' + '='.repeat(50));
console.log('🧪 AID COMMANDS VALIDATION');
console.log('='.repeat(50));

console.log('\n📝 Testing Command Files...\n');

for (const [name, config] of Object.entries(EXPECTED_COMMANDS)) {
  testCommandFile(name, config);
}

testStateFiles();
testMCPConfig();
testSkills();
printSummary();
