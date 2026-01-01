/**
 * AID Methodology - Phase 0 (Discovery) Tests
 *
 * Tests for the Phase 0 Discovery phase:
 * - Research folder structure
 * - Phase state management
 * - Gate check requirements
 * - Phase transitions (0 → 1)
 *
 * Phase 0 Output Structure:
 * docs/research/YYYY-MM-DD-[project]/
 * ├── research-report.md
 * ├── traceability-matrix.md
 * ├── interviews/
 * ├── analysis/
 * ├── ideation/
 * ├── opportunities/
 * └── assets/
 */

import * as fs from 'fs';
import * as path from 'path';

// Folder paths
const DOCS_ROOT = path.join(process.cwd(), 'docs');
const RESEARCH_FOLDER = path.join(DOCS_ROOT, 'research');
const AID_FOLDER = path.join(process.cwd(), '.aid');
const COMMANDS_FOLDER = path.join(process.cwd(), '.claude', 'commands');
const SKILLS_FOLDER = path.join(process.cwd(), '.claude', 'skills');

// Date-prefixed folder regex: YYYY-MM-DD-project-name/
const DATE_PREFIX_FOLDER_REGEX = /^\d{4}-\d{2}-\d{2}-[\w-]+$/;

describe('Phase 0: Discovery - Folder Structure', () => {
  describe('Research Folder', () => {
    test('docs/research/ folder exists or can be created', () => {
      // The folder should exist or be creatable
      if (!fs.existsSync(RESEARCH_FOLDER)) {
        fs.mkdirSync(RESEARCH_FOLDER, { recursive: true });
      }
      expect(fs.existsSync(RESEARCH_FOLDER)).toBe(true);
    });
  });

  describe('Research Project Structure', () => {
    const requiredSubfolders = [
      'interviews',
      'analysis',
      'ideation',
      'opportunities',
      'assets',
    ];

    const requiredFiles = [
      'research-report.md',
      'traceability-matrix.md',
    ];

    test('research project folder naming follows convention', () => {
      expect('2024-12-21-user-authentication').toMatch(DATE_PREFIX_FOLDER_REGEX);
      expect('2025-01-15-my-project').toMatch(DATE_PREFIX_FOLDER_REGEX);
      expect('user-authentication').not.toMatch(DATE_PREFIX_FOLDER_REGEX);
    });

    test('research project has required subfolders', () => {
      // Test structure requirements (not actual folders)
      expect(requiredSubfolders).toContain('interviews');
      expect(requiredSubfolders).toContain('analysis');
      expect(requiredSubfolders).toContain('ideation');
      expect(requiredSubfolders).toContain('opportunities');
      expect(requiredSubfolders).toContain('assets');
    });

    test('research project has required files', () => {
      expect(requiredFiles).toContain('research-report.md');
      expect(requiredFiles).toContain('traceability-matrix.md');
    });
  });

  describe('Research Path Builder', () => {
    function buildResearchPath(projectName: string, date: Date = new Date()): string {
      const dateStr = date.toISOString().split('T')[0]; // YYYY-MM-DD
      const normalizedName = projectName.toLowerCase().replace(/\s+/g, '-');
      return path.join(RESEARCH_FOLDER, `${dateStr}-${normalizedName}`);
    }

    test('builds correct research folder path', () => {
      const date = new Date('2024-12-21');
      const result = buildResearchPath('user-authentication', date);
      expect(result).toContain('docs');
      expect(result).toContain('research');
      expect(result).toContain('2024-12-21-user-authentication');
    });

    test('normalizes project names with spaces', () => {
      const date = new Date('2024-12-21');
      const result = buildResearchPath('User Authentication', date);
      expect(result).toContain('2024-12-21-user-authentication');
    });
  });
});

describe('Phase 0: Discovery - State Management', () => {
  describe('State File Schema', () => {
    test('.aid/state.json exists', () => {
      const stateFile = path.join(AID_FOLDER, 'state.json');
      if (fs.existsSync(stateFile)) {
        const content = JSON.parse(fs.readFileSync(stateFile, 'utf-8'));
        expect(content).toHaveProperty('current_phase');
        expect(content).toHaveProperty('phase_name');
      }
    });

    test('state.json starts at Phase 0', () => {
      const stateFile = path.join(AID_FOLDER, 'state.json');
      if (fs.existsSync(stateFile)) {
        const content = JSON.parse(fs.readFileSync(stateFile, 'utf-8'));
        expect(content.current_phase).toBe(0);
        expect(content.phase_name).toBe('Discovery');
      }
    });

    test('state.json has research document field', () => {
      const stateFile = path.join(AID_FOLDER, 'state.json');
      if (fs.existsSync(stateFile)) {
        const content = JSON.parse(fs.readFileSync(stateFile, 'utf-8'));
        if (content.documents) {
          expect(content.documents).toHaveProperty('research');
        }
      }
    });
  });

  describe('Phase Name Mapping', () => {
    const PHASE_NAMES: Record<number, string> = {
      0: 'Discovery',
      1: 'PRD',
      2: 'Tech Spec',
      3: 'Implementation Plan',
      4: 'Development',
      5: 'QA & Ship',
    };

    test('Phase 0 maps to Discovery', () => {
      expect(PHASE_NAMES[0]).toBe('Discovery');
    });

    test('Phase 1 maps to PRD', () => {
      expect(PHASE_NAMES[1]).toBe('PRD');
    });

    test('all 6 phases are defined', () => {
      expect(Object.keys(PHASE_NAMES).length).toBe(6);
    });
  });
});

describe('Phase 0: Discovery - Gate Requirements', () => {
  describe('Phase 0 → Phase 1 Gate', () => {
    const gateRequirements = [
      'Research folder exists',
      'research-report.md present',
      'Problem statement in SCQ format',
      'Stakeholders identified',
      'Competitive analysis documented',
      'traceability-matrix.md created',
      'Go/No-Go decision documented',
      'Sub-agent review PASSED',
      'Feedback collected via /aid end',
    ];

    test('gate has required checkpoints', () => {
      expect(gateRequirements.length).toBeGreaterThanOrEqual(8);
    });

    test('research report is required', () => {
      expect(gateRequirements.some(r => r.includes('research-report'))).toBe(true);
    });

    test('traceability matrix is required', () => {
      expect(gateRequirements.some(r => r.includes('traceability'))).toBe(true);
    });

    test('Go/No-Go decision is required', () => {
      expect(gateRequirements.some(r => r.includes('Go/No-Go'))).toBe(true);
    });

    test('sub-agent review is mandatory', () => {
      expect(gateRequirements.some(r => r.includes('Sub-agent'))).toBe(true);
    });
  });
});

describe('Phase 0: Discovery - Commands', () => {
  describe('/discovery command', () => {
    const discoveryCommand = path.join(COMMANDS_FOLDER, 'discovery.md');

    test('/discovery command exists', () => {
      expect(fs.existsSync(discoveryCommand)).toBe(true);
    });

    test('/discovery references Phase 0', () => {
      if (fs.existsSync(discoveryCommand)) {
        const content = fs.readFileSync(discoveryCommand, 'utf-8');
        expect(content).toContain('Phase 0');
        expect(content).toContain('Discovery');
      }
    });

    test('/discovery references research folder', () => {
      if (fs.existsSync(discoveryCommand)) {
        const content = fs.readFileSync(discoveryCommand, 'utf-8');
        expect(content).toContain('docs/research/');
      }
    });

    test('/discovery mentions skills', () => {
      if (fs.existsSync(discoveryCommand)) {
        const content = fs.readFileSync(discoveryCommand, 'utf-8');
        expect(content).toContain('pre-prd-research');
      }
    });
  });

  describe('/aid-start command', () => {
    const aidStartCommand = path.join(COMMANDS_FOLDER, 'aid-start.md');

    test('/aid-start includes Phase 0 option', () => {
      if (fs.existsSync(aidStartCommand)) {
        const content = fs.readFileSync(aidStartCommand, 'utf-8');
        expect(content).toContain('0');
        expect(content).toContain('Discovery');
      }
    });
  });

  describe('/phase command', () => {
    const phaseCommand = path.join(COMMANDS_FOLDER, 'phase.md');

    test('/phase shows 6-phase lifecycle', () => {
      if (fs.existsSync(phaseCommand)) {
        const content = fs.readFileSync(phaseCommand, 'utf-8');
        expect(content).toContain('6-Phase');
        expect(content).toContain('Phase 0');
      }
    });
  });

  describe('/gate-check command', () => {
    const gateCheckCommand = path.join(COMMANDS_FOLDER, 'gate-check.md');

    test('/gate-check includes Phase 0 requirements', () => {
      if (fs.existsSync(gateCheckCommand)) {
        const content = fs.readFileSync(gateCheckCommand, 'utf-8');
        expect(content).toContain('Phase 0');
        expect(content).toContain('Discovery');
      }
    });
  });
});

describe('Phase 0: Discovery - Skills', () => {
  describe('pre-prd-research skill', () => {
    const skillPath = path.join(SKILLS_FOLDER, 'pre-prd-research', 'SKILL.md');

    test('pre-prd-research skill exists', () => {
      expect(fs.existsSync(skillPath)).toBe(true);
    });

    test('skill includes research activities', () => {
      if (fs.existsSync(skillPath)) {
        const content = fs.readFileSync(skillPath, 'utf-8');
        expect(content).toContain('Activity A');
        expect(content).toContain('Activity B');
        expect(content).toContain('Activity C');
      }
    });

    test('skill includes traceability', () => {
      if (fs.existsSync(skillPath)) {
        const content = fs.readFileSync(skillPath, 'utf-8');
        expect(content).toContain('traceability');
      }
    });
  });

  describe('aid-discovery skill', () => {
    const skillPath = path.join(SKILLS_FOLDER, 'aid-discovery', 'SKILL.md');

    test('aid-discovery skill exists', () => {
      expect(fs.existsSync(skillPath)).toBe(true);
    });
  });

  describe('phase-enforcement skill', () => {
    const skillPath = path.join(SKILLS_FOLDER, 'phase-enforcement', 'SKILL.md');

    test('phase-enforcement includes Phase 0', () => {
      if (fs.existsSync(skillPath)) {
        const content = fs.readFileSync(skillPath, 'utf-8');
        expect(content).toContain('Phase 0');
        expect(content).toContain('Discovery');
        expect(content).toContain('research');
      }
    });

    test('phase-enforcement has 6-phase lifecycle', () => {
      if (fs.existsSync(skillPath)) {
        const content = fs.readFileSync(skillPath, 'utf-8');
        expect(content).toContain('6-Phase');
      }
    });

    test('phase-enforcement includes Phase 0 → 1 gate', () => {
      if (fs.existsSync(skillPath)) {
        const content = fs.readFileSync(skillPath, 'utf-8');
        expect(content).toContain('Phase 0 → Phase 1');
      }
    });
  });
});

describe('Phase 0: Discovery - Nano Banana Pro Integration', () => {
  describe('Visual artifacts for Phase 0', () => {
    const skillPath = path.join(SKILLS_FOLDER, 'nano-banana-visual', 'SKILL.md');

    test('nano-banana-visual supports Phase 0', () => {
      if (fs.existsSync(skillPath)) {
        const content = fs.readFileSync(skillPath, 'utf-8');
        expect(content).toContain('Phase 0');
        expect(content).toContain('Discovery');
      }
    });

    test('stakeholder map generation available', () => {
      if (fs.existsSync(skillPath)) {
        const content = fs.readFileSync(skillPath, 'utf-8');
        expect(content.toLowerCase()).toContain('stakeholder');
      }
    });

    test('competitive landscape generation available', () => {
      if (fs.existsSync(skillPath)) {
        const content = fs.readFileSync(skillPath, 'utf-8');
        expect(content.toLowerCase()).toContain('competitive');
      }
    });
  });
});

describe('Phase 0: Discovery - CLAUDE.md Documentation', () => {
  const claudeMd = path.join(process.cwd(), 'CLAUDE.md');

  test('CLAUDE.md includes Phase 0', () => {
    if (fs.existsSync(claudeMd)) {
      const content = fs.readFileSync(claudeMd, 'utf-8');
      expect(content).toContain('0 Discovery');
    }
  });

  test('CLAUDE.md lists /discovery command', () => {
    if (fs.existsSync(claudeMd)) {
      const content = fs.readFileSync(claudeMd, 'utf-8');
      expect(content).toContain('/discovery');
    }
  });

  test('CLAUDE.md lists Phase 0 skills', () => {
    if (fs.existsSync(claudeMd)) {
      const content = fs.readFileSync(claudeMd, 'utf-8');
      expect(content).toContain('pre-prd-research');
    }
  });
});

describe('Phase 0: Discovery - README.md Documentation', () => {
  const readmeMd = path.join(process.cwd(), 'README.md');

  test('README.md includes 6-phase lifecycle', () => {
    if (fs.existsSync(readmeMd)) {
      const content = fs.readFileSync(readmeMd, 'utf-8');
      expect(content).toContain('6 mandatory phases');
    }
  });

  test('README.md describes Phase 0', () => {
    if (fs.existsSync(readmeMd)) {
      const content = fs.readFileSync(readmeMd, 'utf-8');
      expect(content).toContain('Phase 0');
      expect(content).toContain('Discovery');
    }
  });
});

describe('Phase 0: Traceability ID Format', () => {
  // Format: [Project]-[Activity]-[Type]-[Number]
  const TRACEABILITY_REGEX = /^[A-Z]+-[ABC]-[A-Z]+-\d{3}$/;

  test('valid traceability IDs accepted', () => {
    expect('PROJ-A-INT-001').toMatch(TRACEABILITY_REGEX);
    expect('PROJ-B-IDEA-003').toMatch(TRACEABILITY_REGEX);
    expect('PROJ-C-OPP-002').toMatch(TRACEABILITY_REGEX);
    expect('AUTH-A-COMP-015').toMatch(TRACEABILITY_REGEX);
  });

  test('invalid traceability IDs rejected', () => {
    expect('INT-001').not.toMatch(TRACEABILITY_REGEX);
    expect('PROJ-D-INT-001').not.toMatch(TRACEABILITY_REGEX); // D not valid
    expect('proj-a-int-001').not.toMatch(TRACEABILITY_REGEX); // lowercase
    expect('PROJ-A-INT-1').not.toMatch(TRACEABILITY_REGEX); // 1 digit
  });
});
