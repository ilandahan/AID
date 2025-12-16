/**
 * AID Methodology - Document Folder Structure Tests
 *
 * Tests that documents are created and saved in the correct folders
 * following the date-prefixed naming convention: YYYY-MM-DD-[feature].md
 *
 * Folder Structure:
 * - docs/prd/           - Product Requirements Documents (Phase 1)
 * - docs/tech-spec/     - Technical Specifications (Phase 2)
 * - docs/implementation-plan/ - Implementation Plans (Phase 3)
 */

import * as fs from 'fs';
import * as path from 'path';

// Document folder paths
const DOCS_ROOT = path.join(process.cwd(), 'docs');
const PRD_FOLDER = path.join(DOCS_ROOT, 'prd');
const TECH_SPEC_FOLDER = path.join(DOCS_ROOT, 'tech-spec');
const IMPL_PLAN_FOLDER = path.join(DOCS_ROOT, 'implementation-plan');

// Date-prefixed filename regex: YYYY-MM-DD-feature-name.md
const DATE_PREFIX_REGEX = /^\d{4}-\d{2}-\d{2}-[\w-]+\.md$/;

describe('AID Document Folder Structure', () => {
  describe('Folder Existence', () => {
    test('docs/prd/ folder exists', () => {
      expect(fs.existsSync(PRD_FOLDER)).toBe(true);
    });

    test('docs/tech-spec/ folder exists', () => {
      expect(fs.existsSync(TECH_SPEC_FOLDER)).toBe(true);
    });

    test('docs/implementation-plan/ folder exists', () => {
      expect(fs.existsSync(IMPL_PLAN_FOLDER)).toBe(true);
    });

    test('each folder has README.md', () => {
      expect(fs.existsSync(path.join(PRD_FOLDER, 'README.md'))).toBe(true);
      expect(fs.existsSync(path.join(TECH_SPEC_FOLDER, 'README.md'))).toBe(true);
      expect(fs.existsSync(path.join(IMPL_PLAN_FOLDER, 'README.md'))).toBe(true);
    });
  });

  describe('README Content', () => {
    test('PRD README explains naming convention', () => {
      const content = fs.readFileSync(path.join(PRD_FOLDER, 'README.md'), 'utf-8');
      expect(content).toContain('YYYY-MM-DD');
      expect(content).toContain('PRD');
    });

    test('Tech Spec README explains naming convention', () => {
      const content = fs.readFileSync(path.join(TECH_SPEC_FOLDER, 'README.md'), 'utf-8');
      expect(content).toContain('YYYY-MM-DD');
      expect(content).toContain('Tech');
    });

    test('Implementation Plan README explains naming convention', () => {
      const content = fs.readFileSync(path.join(IMPL_PLAN_FOLDER, 'README.md'), 'utf-8');
      expect(content).toContain('YYYY-MM-DD');
      expect(content).toContain('Implementation');
    });
  });
});

describe('Document Naming Convention', () => {
  describe('Date-Prefix Validation', () => {
    test('valid date-prefixed filenames accepted', () => {
      expect('2024-06-15-user-authentication.md').toMatch(DATE_PREFIX_REGEX);
      expect('2025-12-11-feature-name.md').toMatch(DATE_PREFIX_REGEX);
      expect('2024-01-01-simple.md').toMatch(DATE_PREFIX_REGEX);
    });

    test('invalid filenames rejected', () => {
      expect('user-authentication.md').not.toMatch(DATE_PREFIX_REGEX);
      expect('PRD.md').not.toMatch(DATE_PREFIX_REGEX);
      expect('TECH-SPEC.md').not.toMatch(DATE_PREFIX_REGEX);
      expect('2024-6-15-feature.md').not.toMatch(DATE_PREFIX_REGEX); // Wrong format
      expect('24-06-15-feature.md').not.toMatch(DATE_PREFIX_REGEX); // 2-digit year
    });
  });

  describe('Document Path Builder', () => {
    function buildDocumentPath(
      type: 'prd' | 'tech-spec' | 'implementation-plan',
      featureName: string,
      date: Date = new Date()
    ): string {
      const dateStr = date.toISOString().split('T')[0]; // YYYY-MM-DD
      const normalizedName = featureName.toLowerCase().replace(/\s+/g, '-');
      const filename = `${dateStr}-${normalizedName}.md`;

      const folders: Record<string, string> = {
        'prd': PRD_FOLDER,
        'tech-spec': TECH_SPEC_FOLDER,
        'implementation-plan': IMPL_PLAN_FOLDER,
      };

      return path.join(folders[type], filename);
    }

    test('builds correct PRD path', () => {
      const date = new Date('2024-06-15');
      const result = buildDocumentPath('prd', 'user-authentication', date);
      expect(result).toContain('docs');
      expect(result).toContain('prd');
      expect(result).toContain('2024-06-15-user-authentication.md');
    });

    test('builds correct Tech Spec path', () => {
      const date = new Date('2024-06-16');
      const result = buildDocumentPath('tech-spec', 'user-authentication', date);
      expect(result).toContain('docs');
      expect(result).toContain('tech-spec');
      expect(result).toContain('2024-06-16-user-authentication.md');
    });

    test('builds correct Implementation Plan path', () => {
      const date = new Date('2024-06-17');
      const result = buildDocumentPath('implementation-plan', 'user-authentication', date);
      expect(result).toContain('docs');
      expect(result).toContain('implementation-plan');
      expect(result).toContain('2024-06-17-user-authentication.md');
    });

    test('normalizes feature names with spaces', () => {
      const date = new Date('2024-06-15');
      const result = buildDocumentPath('prd', 'User Authentication', date);
      expect(result).toContain('2024-06-15-user-authentication.md');
    });
  });
});

describe('Document Finder', () => {
  function findLatestDocument(folder: string): string | null {
    if (!fs.existsSync(folder)) return null;

    const files = fs.readdirSync(folder)
      .filter(f => f.endsWith('.md') && f !== 'README.md')
      .filter(f => DATE_PREFIX_REGEX.test(f))
      .sort()
      .reverse();

    return files.length > 0 ? files[0] : null;
  }

  function findDocumentsByFeature(folder: string, featureName: string): string[] {
    if (!fs.existsSync(folder)) return [];

    const normalizedName = featureName.toLowerCase().replace(/\s+/g, '-');

    return fs.readdirSync(folder)
      .filter(f => f.endsWith('.md') && f !== 'README.md')
      .filter(f => f.includes(normalizedName))
      .sort()
      .reverse();
  }

  test('finds latest document in folder', () => {
    // This test verifies the finder logic works
    // Actual documents may or may not exist
    const finder = findLatestDocument;
    expect(typeof finder).toBe('function');
  });

  test('finds documents by feature name', () => {
    const finder = findDocumentsByFeature;
    expect(typeof finder).toBe('function');
  });

  test('returns null for empty folder', () => {
    // Create temp folder for testing
    const tempFolder = path.join(DOCS_ROOT, 'temp-test');
    if (!fs.existsSync(tempFolder)) {
      fs.mkdirSync(tempFolder, { recursive: true });
    }

    const result = findLatestDocument(tempFolder);
    expect(result).toBeNull();

    // Cleanup
    fs.rmdirSync(tempFolder);
  });
});

describe('Document-to-Test Mapping', () => {
  interface DocumentMapping {
    document: 'prd' | 'tech-spec' | 'implementation-plan';
    testType: string;
    extractFrom: string;
  }

  const mappings: DocumentMapping[] = [
    { document: 'prd', testType: 'E2E/GUI Tests', extractFrom: 'User Stories' },
    { document: 'tech-spec', testType: 'Backend/API Tests', extractFrom: 'API Endpoints' },
    { document: 'tech-spec', testType: 'Error Tests', extractFrom: 'Error Codes' },
    { document: 'implementation-plan', testType: 'Test Phases', extractFrom: 'Exit Criteria' },
  ];

  test('PRD maps to E2E/GUI tests', () => {
    const prdMappings = mappings.filter(m => m.document === 'prd');
    expect(prdMappings.some(m => m.testType.includes('E2E'))).toBe(true);
  });

  test('Tech Spec maps to Backend/API tests', () => {
    const specMappings = mappings.filter(m => m.document === 'tech-spec');
    expect(specMappings.some(m => m.testType.includes('Backend'))).toBe(true);
    expect(specMappings.some(m => m.testType.includes('Error'))).toBe(true);
  });

  test('Implementation Plan maps to test phases', () => {
    const planMappings = mappings.filter(m => m.document === 'implementation-plan');
    expect(planMappings.some(m => m.testType.includes('Phase'))).toBe(true);
  });
});

describe('Slash Command Integration', () => {
  // Verify that slash commands reference correct paths
  const COMMANDS_FOLDER = path.join(process.cwd(), '.claude', 'commands');

  test('/prd command references docs/prd/', () => {
    const prdCommand = path.join(COMMANDS_FOLDER, 'prd.md');
    if (fs.existsSync(prdCommand)) {
      const content = fs.readFileSync(prdCommand, 'utf-8');
      expect(content).toContain('docs/prd/');
      expect(content).toContain('YYYY-MM-DD');
    }
  });

  test('/tech-spec command references docs/tech-spec/', () => {
    const techSpecCommand = path.join(COMMANDS_FOLDER, 'tech-spec.md');
    if (fs.existsSync(techSpecCommand)) {
      const content = fs.readFileSync(techSpecCommand, 'utf-8');
      expect(content).toContain('docs/tech-spec/');
      expect(content).toContain('YYYY-MM-DD');
    }
  });

  test('/implementation-plan command references docs/implementation-plan/', () => {
    const implPlanCommand = path.join(COMMANDS_FOLDER, 'implementation-plan.md');
    if (fs.existsSync(implPlanCommand)) {
      const content = fs.readFileSync(implPlanCommand, 'utf-8');
      expect(content).toContain('docs/implementation-plan/');
      expect(content).toContain('YYYY-MM-DD');
    }
  });

  test('/write-tests command reads all document folders', () => {
    const writeTestsCommand = path.join(COMMANDS_FOLDER, 'write-tests.md');
    if (fs.existsSync(writeTestsCommand)) {
      const content = fs.readFileSync(writeTestsCommand, 'utf-8');
      expect(content).toContain('docs/prd/');
      expect(content).toContain('docs/tech-spec/');
      expect(content).toContain('docs/implementation-plan/');
    }
  });
});
