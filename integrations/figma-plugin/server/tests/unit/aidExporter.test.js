/**
 * @file aidExporter.test.js
 * @description Unit tests for AID component exporter.
 * Tests validation, export structure, and file operations.
 */

// Mock fs module
jest.mock('fs', () => ({
  promises: {
    mkdir: jest.fn().mockResolvedValue(undefined),
    writeFile: jest.fn().mockResolvedValue(undefined),
    readFile: jest.fn(),
    readdir: jest.fn(),
    stat: jest.fn()
  }
}));

const aidExporter = require('../../src/services/aidExporter');
const fs = require('fs');

// Suppress console output
beforeAll(() => {
  jest.spyOn(console, 'log').mockImplementation(() => {});
  jest.spyOn(console, 'error').mockImplementation(() => {});
});

afterAll(() => {
  jest.restoreAllMocks();
});

// ============================================
// Test Data
// ============================================

const testPayloads = {
  valid: {
    component: {
      name: 'Button/Primary',
      type: 'COMPONENT_SET',
      nodeId: '1:234',
      fileKey: 'abc123'
    },
    metadata: {
      description: 'Primary button component',
      formattedDescription: 'Full formatted description',
      tags: 'button, primary',
      notes: 'Use for primary actions',
      ariaLabel: 'Primary button',
      category: 'button',
      level: 'atom',
      priority: 'high'
    },
    tokens: [
      { type: 'color', name: 'bg', value: '#0066FF' }
    ],
    content: { svg: '<svg>...</svg>' },
    certification: {
      score: 95,
      auditPassed: true,
      metadataComplete: true
    }
  },

  lowScore: {
    component: {
      name: 'Box',
      type: 'COMPONENT',
      nodeId: '2:345'
    },
    certification: {
      score: 75
    }
  },

  noComponent: {
    metadata: {},
    certification: { score: 95 }
  },

  noName: {
    component: {
      type: 'COMPONENT'
    },
    certification: { score: 95 }
  },

  blockingIssues: {
    component: {
      name: 'Test',
      type: 'COMPONENT'
    },
    certification: {
      score: 95,
      hasBlockingIssues: true
    }
  },

  minimal: {
    component: {
      name: 'Icon/Star',
      type: 'COMPONENT'
    },
    score: 92
  }
};

// ============================================
// validateExport Tests
// ============================================

describe('AIDExporter - validateExport', () => {
  test('validates complete payload', () => {
    const result = aidExporter.validateExport(testPayloads.valid);

    expect(result.valid).toBe(true);
    expect(result.issues).toHaveLength(0);
  });

  test('rejects payload without component', () => {
    const result = aidExporter.validateExport(testPayloads.noComponent);

    expect(result.valid).toBe(false);
    expect(result.issues).toContain('Missing component data');
  });

  test('rejects payload without component name', () => {
    const result = aidExporter.validateExport(testPayloads.noName);

    expect(result.valid).toBe(false);
    expect(result.issues.some(i => i.includes('name'))).toBe(true);
  });

  test('rejects score below 90', () => {
    const result = aidExporter.validateExport(testPayloads.lowScore);

    expect(result.valid).toBe(false);
    expect(result.issues.some(i => i.includes('90'))).toBe(true);
  });

  test('rejects payload with blocking issues', () => {
    const result = aidExporter.validateExport(testPayloads.blockingIssues);

    expect(result.valid).toBe(false);
    expect(result.issues.some(i => i.includes('blocking'))).toBe(true);
  });

  test('accepts score from root payload if certification missing', () => {
    const result = aidExporter.validateExport(testPayloads.minimal);

    expect(result.valid).toBe(true);
  });

  test('returns joined message for multiple issues', () => {
    const result = aidExporter.validateExport({
      component: {},
      certification: { score: 50 }
    });

    expect(result.valid).toBe(false);
    expect(result.message).toContain(';');
  });
});

// ============================================
// exportComponent Tests
// ============================================

describe('AIDExporter - exportComponent', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    fs.promises.mkdir.mockResolvedValue(undefined);
    fs.promises.writeFile.mockResolvedValue(undefined);
    fs.promises.readFile.mockRejectedValue({ code: 'ENOENT' });
  });

  test('returns success for valid payload', async () => {
    const result = await aidExporter.exportComponent(testPayloads.valid);

    expect(result.success).toBe(true);
    expect(result.componentId).toBeDefined();
    expect(result.level).toBe('atom');
  });

  test('generates correct component ID', async () => {
    const result = await aidExporter.exportComponent(testPayloads.valid);

    expect(result.componentId).toBe('primary-1-234');
  });

  test('returns validation error for invalid payload', async () => {
    const result = await aidExporter.exportComponent(testPayloads.lowScore);

    expect(result.success).toBe(false);
    expect(result.error).toBe('validation_failed');
    expect(result.issues.length).toBeGreaterThan(0);
  });

  test('creates output directory', async () => {
    await aidExporter.exportComponent(testPayloads.valid);

    expect(fs.promises.mkdir).toHaveBeenCalled();
  });

  test('writes component JSON file', async () => {
    await aidExporter.exportComponent(testPayloads.valid);

    expect(fs.promises.writeFile).toHaveBeenCalled();
    const writeCall = fs.promises.writeFile.mock.calls[0];
    expect(writeCall[0]).toContain('primary-1-234.json');
  });

  test('writes index file', async () => {
    await aidExporter.exportComponent(testPayloads.valid);

    // Should write at least component file and index (React generation adds more)
    expect(fs.promises.writeFile.mock.calls.length).toBeGreaterThanOrEqual(2);
    // Find the index write among all calls
    const indexCall = fs.promises.writeFile.mock.calls.find(call =>
      call[0].includes('_index.json')
    );
    expect(indexCall).toBeDefined();
  });

  test('handles mkdir error gracefully', async () => {
    fs.promises.mkdir.mockRejectedValue(new Error('Permission denied'));

    const result = await aidExporter.exportComponent(testPayloads.valid);

    expect(result.success).toBe(false);
    expect(result.error).toBe('export_failed');
  });

  test('handles write error gracefully', async () => {
    fs.promises.writeFile.mockRejectedValue(new Error('Disk full'));

    const result = await aidExporter.exportComponent(testPayloads.valid);

    expect(result.success).toBe(false);
    expect(result.error).toBe('export_failed');
  });

  test('returns relative file path', async () => {
    const result = await aidExporter.exportComponent(testPayloads.valid);

    expect(result.filePath).not.toContain('C:');
    expect(result.filePath).toContain('components');
  });

  test('includes success message', async () => {
    const result = await aidExporter.exportComponent(testPayloads.valid);

    expect(result.message).toContain('Button/Primary');
    expect(result.message).toContain('Successfully');
  });
});

// ============================================
// Export Data Structure Tests
// ============================================

describe('AIDExporter - Export Data Structure', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    fs.promises.mkdir.mockResolvedValue(undefined);
    fs.promises.writeFile.mockResolvedValue(undefined);
    fs.promises.readFile.mockRejectedValue({ code: 'ENOENT' });
  });

  test('includes schema version', async () => {
    await aidExporter.exportComponent(testPayloads.valid);

    const writeCall = fs.promises.writeFile.mock.calls[0];
    const data = JSON.parse(writeCall[1]);

    expect(data.$schema).toBe('aid-component-v1');
    expect(data.version).toBe('1.0');
  });

  test('includes component info', async () => {
    await aidExporter.exportComponent(testPayloads.valid);

    const writeCall = fs.promises.writeFile.mock.calls[0];
    const data = JSON.parse(writeCall[1]);

    expect(data.name).toBe('Button/Primary');
    expect(data.type).toBe('COMPONENT_SET');
    expect(data.nodeId).toBe('1:234');
  });

  test('includes metadata', async () => {
    await aidExporter.exportComponent(testPayloads.valid);

    const writeCall = fs.promises.writeFile.mock.calls[0];
    const data = JSON.parse(writeCall[1]);

    expect(data.metadata.description).toBe('Primary button component');
    expect(data.metadata.category).toBe('button');
    expect(data.metadata.level).toBe('atom');
  });

  test('includes tokens', async () => {
    await aidExporter.exportComponent(testPayloads.valid);

    const writeCall = fs.promises.writeFile.mock.calls[0];
    const data = JSON.parse(writeCall[1]);

    expect(data.tokens).toHaveLength(1);
    expect(data.tokens[0].value).toBe('#0066FF');
  });

  test('includes certification', async () => {
    await aidExporter.exportComponent(testPayloads.valid);

    const writeCall = fs.promises.writeFile.mock.calls[0];
    const data = JSON.parse(writeCall[1]);

    expect(data.certification.score).toBe(95);
    expect(data.certification.auditPassed).toBe(true);
    expect(data.certification.exportedAt).toBeDefined();
  });

  test('includes figma metadata', async () => {
    await aidExporter.exportComponent(testPayloads.valid);

    const writeCall = fs.promises.writeFile.mock.calls[0];
    const data = JSON.parse(writeCall[1]);

    expect(data.figma.fileKey).toBe('abc123');
    expect(data.figma.nodeId).toBe('1:234');
    expect(data.figma.exportedFrom).toBe('aid-figma-plugin');
  });
});

// ============================================
// Level Classification Tests
// ============================================

describe('AIDExporter - Level Classification', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    fs.promises.mkdir.mockResolvedValue(undefined);
    fs.promises.writeFile.mockResolvedValue(undefined);
    fs.promises.readFile.mockRejectedValue({ code: 'ENOENT' });
  });

  test('uses metadata level if provided', async () => {
    const result = await aidExporter.exportComponent(testPayloads.valid);
    expect(result.level).toBe('atom');
  });

  test('classifies button as atoms', async () => {
    const payload = {
      component: { name: 'Button/Secondary' },
      certification: { score: 95 }
    };

    const result = await aidExporter.exportComponent(payload);
    expect(result.level).toBe('atoms');
  });

  test('classifies card as molecules', async () => {
    const payload = {
      component: { name: 'Card/Product' },
      certification: { score: 95 }
    };

    const result = await aidExporter.exportComponent(payload);
    expect(result.level).toBe('molecules');
  });

  test('classifies modal as organisms', async () => {
    const payload = {
      component: { name: 'Modal/Confirm' },
      certification: { score: 95 }
    };

    const result = await aidExporter.exportComponent(payload);
    expect(result.level).toBe('organisms');
  });

  test('classifies page as templates', async () => {
    const payload = {
      component: { name: 'Page/Dashboard' },
      certification: { score: 95 }
    };

    const result = await aidExporter.exportComponent(payload);
    expect(result.level).toBe('templates');
  });

  test('defaults to molecules for unknown types', async () => {
    const payload = {
      component: { name: 'CustomThing' },
      certification: { score: 95 }
    };

    const result = await aidExporter.exportComponent(payload);
    expect(result.level).toBe('molecules');
  });
});

// ============================================
// Component ID Generation Tests
// ============================================

describe('AIDExporter - Component ID Generation', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    fs.promises.mkdir.mockResolvedValue(undefined);
    fs.promises.writeFile.mockResolvedValue(undefined);
    fs.promises.readFile.mockRejectedValue({ code: 'ENOENT' });
  });

  test('generates lowercase ID', async () => {
    const result = await aidExporter.exportComponent({
      component: { name: 'Button/PRIMARY' },
      certification: { score: 95 }
    });

    expect(result.componentId).toBe('primary');
  });

  test('replaces special characters with hyphens', async () => {
    const result = await aidExporter.exportComponent({
      component: { name: 'Button/My Fancy Component!!!' },
      certification: { score: 95 }
    });

    expect(result.componentId).toBe('my-fancy-component');
  });

  test('includes node ID suffix if provided', async () => {
    const result = await aidExporter.exportComponent({
      component: { name: 'Button/Test', nodeId: '1:234' },
      certification: { score: 95 }
    });

    expect(result.componentId).toBe('test-1-234');
  });

  test('rejects component without name', async () => {
    const result = await aidExporter.exportComponent({
      component: {},
      certification: { score: 95 }
    });

    // Validation fails because name is required
    expect(result.success).toBe(false);
    expect(result.issues.some(i => i.includes('name'))).toBe(true);
  });
});

// ============================================
// Index Update Tests
// ============================================

describe('AIDExporter - Index Updates', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    fs.promises.mkdir.mockResolvedValue(undefined);
    fs.promises.writeFile.mockResolvedValue(undefined);
  });

  test('creates new index if none exists', async () => {
    fs.promises.readFile.mockRejectedValue({ code: 'ENOENT' });

    await aidExporter.exportComponent(testPayloads.valid);

    const indexCall = fs.promises.writeFile.mock.calls[1];
    const indexData = JSON.parse(indexCall[1]);

    expect(indexData.components).toHaveLength(1);
    expect(indexData.components[0].id).toBe('primary-1-234');
  });

  test('updates existing index', async () => {
    fs.promises.readFile.mockResolvedValue(JSON.stringify({
      components: [
        { id: 'existing-component', name: 'Existing', updatedAt: '2025-01-01' }
      ]
    }));

    await aidExporter.exportComponent(testPayloads.valid);

    const indexCall = fs.promises.writeFile.mock.calls[1];
    const indexData = JSON.parse(indexCall[1]);

    expect(indexData.components).toHaveLength(2);
  });

  test('replaces existing entry with same ID', async () => {
    fs.promises.readFile.mockResolvedValue(JSON.stringify({
      components: [
        { id: 'primary-1-234', name: 'Old Name', updatedAt: '2025-01-01' }
      ]
    }));

    await aidExporter.exportComponent(testPayloads.valid);

    const indexCall = fs.promises.writeFile.mock.calls[1];
    const indexData = JSON.parse(indexCall[1]);

    expect(indexData.components).toHaveLength(1);
    expect(indexData.components[0].name).toBe('Button/Primary');
  });

  test('sorts components by name', async () => {
    fs.promises.readFile.mockResolvedValue(JSON.stringify({
      components: [
        { id: 'z-component', name: 'Zebra', updatedAt: '2025-01-01' }
      ]
    }));

    await aidExporter.exportComponent({
      component: { name: 'Apple/Component', nodeId: '1:1' },
      certification: { score: 95 }
    });

    const indexCall = fs.promises.writeFile.mock.calls[1];
    const indexData = JSON.parse(indexCall[1]);

    expect(indexData.components[0].name).toBe('Apple/Component');
    expect(indexData.components[1].name).toBe('Zebra');
  });
});

// ============================================
// listExportedComponents Tests
// ============================================

describe('AIDExporter - listExportedComponents', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('returns empty array when no components', async () => {
    fs.promises.readdir.mockRejectedValue(new Error('ENOENT'));

    const result = await aidExporter.listExportedComponents();

    expect(result).toEqual([]);
  });

  test('returns components from all levels', async () => {
    fs.promises.readdir.mockResolvedValue(['atoms', 'molecules']);
    fs.promises.stat.mockResolvedValue({ isDirectory: () => true });
    fs.promises.readFile.mockImplementation((path) => {
      if (path.includes('atoms')) {
        return Promise.resolve(JSON.stringify({
          components: [{ id: 'button', name: 'Button' }]
        }));
      }
      if (path.includes('molecules')) {
        return Promise.resolve(JSON.stringify({
          components: [{ id: 'card', name: 'Card' }]
        }));
      }
      return Promise.reject(new Error('Not found'));
    });

    const result = await aidExporter.listExportedComponents();

    expect(result).toHaveLength(2);
    expect(result.some(c => c.id === 'button')).toBe(true);
    expect(result.some(c => c.id === 'card')).toBe(true);
  });

  test('filters by level when specified', async () => {
    fs.promises.stat.mockResolvedValue({ isDirectory: () => true });
    fs.promises.readFile.mockResolvedValue(JSON.stringify({
      components: [{ id: 'button', name: 'Button' }]
    }));

    const result = await aidExporter.listExportedComponents('atoms');

    expect(result).toHaveLength(1);
    expect(result[0].level).toBe('atoms');
  });

  test('includes level in returned components', async () => {
    fs.promises.readdir.mockResolvedValue(['atoms']);
    fs.promises.stat.mockResolvedValue({ isDirectory: () => true });
    fs.promises.readFile.mockResolvedValue(JSON.stringify({
      components: [{ id: 'button', name: 'Button' }]
    }));

    const result = await aidExporter.listExportedComponents();

    expect(result[0].level).toBe('atoms');
  });
});
