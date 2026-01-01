/**
 * Component Utilities
 * Helper functions for component classification and analysis
 */

import { t } from './i18n.js';
import { escapeHtml } from './sanitize.js';

/**
 * Count generated fields in a generated metadata object
 * Only counts fields that are NOT already present in Figma (from metadata analysis)
 * @param {Object} gen - Generated metadata object
 * @param {Object} meta - Metadata analysis results (optional - if not provided, counts all)
 * @returns {number} Count of truly generated (new) fields
 */
export function countGeneratedFields(gen, meta = null) {
  if (!gen) return 0;

  // If no metadata provided, we can't distinguish - count all (legacy behavior)
  if (!meta) {
    let count = 0;
    if (gen.description) count++;
    if (gen.tags?.length) count++;
    if (gen.notes) count++;
    if (gen.category) count++;
    if (gen.level) count++;
    if (gen.ariaLabel) count++;
    if (gen.a11y?.length) count++;
    if (Object.keys(gen.variantDescriptions || gen.variants || {}).length) count++;
    return count;
  }

  // With metadata, only count fields that are NOT already in Figma
  const present = meta.componentSetLevel?.present || [];
  const a11yMeta = meta.accessibilityMetadata || {};

  let count = 0;

  // Basic fields - only count if NOT already present in Figma
  if (gen.description && !present.includes('description')) count++;
  if (gen.tags?.length && !present.includes('tags')) count++;
  if (gen.notes && !present.includes('notes')) count++;
  if (gen.category && !present.includes('category')) count++;
  if (gen.level && !present.includes('level')) count++;

  // A11y fields - only count if NOT already in Figma
  if (gen.ariaLabel && !a11yMeta.hasAriaLabel) count++;
  if (gen.a11y?.length && !a11yMeta.hasA11yNotes) count++;

  // Property descriptions - these are always new (not in Figma's built-in metadata)
  const propDescCount = Object.keys(gen.propertyDescriptions || {}).length;
  count += propDescCount;

  return count;
}

/**
 * Get display properties for a component level
 * UI-only function - just maps server's level to visual representation
 * Classification logic is on the SERVER (single source of truth)
 * @param {string} level - Atomic design level from server (atom, molecule, organism, template)
 * @returns {Object} Display properties with icon, color, textColor
 */
export function getLevelDisplay(level) {
  const displayMap = {
    'atom': { icon: '🔵', color: '#dbeafe', textColor: '#1e40af' },
    'molecule': { icon: '🟢', color: '#dcfce7', textColor: '#166534' },
    'organism': { icon: '🟣', color: '#f3e8ff', textColor: '#7c3aed' },
    'template': { icon: '🟠', color: '#ffedd5', textColor: '#c2410c' }
  };
  return displayMap[level] || displayMap['molecule']; // Default to molecule if unknown
}

/**
 * Update export files list UI with predicted files (before export)
 * @param {string} componentName - Name of the component
 */
export function updateExportFiles(componentName) {
  let cleanName = componentName || 'Component';
  // If it looks like variant properties (contains = or ,), try to extract base name
  if (cleanName.includes('=') || cleanName.includes(',')) {
    cleanName = cleanName.split(/[=,]/)[0].trim();
  }
  cleanName = cleanName.replace(/[^a-zA-Z0-9]/g, '') || 'Component';
  const safeCleanName = escapeHtml(cleanName);
  const filesEl = document.getElementById('exportFilesList');
  if (filesEl) {
    // Predicted list of files (actual list comes from server after export)
    filesEl.innerHTML = `
      <div>├── ${safeCleanName}.tsx</div>
      <div>├── ${safeCleanName}.module.css</div>
      <div>├── ${safeCleanName}.types.ts</div>
      <div>├── ${safeCleanName}.test.tsx</div>
      <div>├── ${safeCleanName}.stories.tsx</div>
      <div>└── index.ts</div>
    `;
  }
}

/**
 * Display actual generated files from server response (after export)
 * @param {Array<string>} files - Array of filenames from server
 * @param {string} componentDir - Directory where files were created
 */
export function displayActualFiles(files, componentDir) {
  const filesEl = document.getElementById('exportFilesList');
  if (!filesEl || !files || !files.length) return;

  // Build the file tree display
  const fileItems = files.map((file, index) => {
    const safeFile = escapeHtml(file);
    const prefix = index === files.length - 1 ? '└──' : '├──';
    return `<div>${prefix} ${safeFile}</div>`;
  }).join('');

  filesEl.innerHTML = fileItems;

  // Update the label to show "Files created:" instead of "Files to be created:"
  const labelEl = filesEl.previousElementSibling;
  if (labelEl && labelEl.hasAttribute('data-i18n')) {
    labelEl.textContent = t('export.filesCreated') || 'Files created:';
  }
}
