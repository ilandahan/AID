/**
 * Metadata Rendering Module
 * Handles metadata analysis display
 */

import { state, $ } from '../state.js';
import { t } from '../utils/i18n.js';
import { escapeHtml } from '../utils/sanitize.js';
import { updateExport } from './export.js';

/**
 * Update metadata display with analysis results
 * @param {Object} meta - Metadata analysis object
 */
export function updateMetadata(meta) {
  console.log('═══════════════════════════════════════════════════════════════════');
  console.log('[UI] 📋 METADATA ANALYSIS RECEIVED');
  console.log('═══════════════════════════════════════════════════════════════════');
  console.log('[UI] Component Name:', meta?.componentName || 'Unknown');
  console.log('[UI] Completeness Score:', meta?.completenessScore || 0, '%');

  // Log missing fields in detail
  if (meta?.componentSetLevel?.missing?.length) {
    console.log('[UI] ❌ Missing Required Fields:', meta.componentSetLevel.missing.join(', '));
  }
  if (meta?.componentSetLevel?.incomplete?.length) {
    console.log('[UI] ⚠️ Incomplete Fields:', meta.componentSetLevel.incomplete.join(', '));
  }
  if (meta?.componentSetLevel?.present?.length) {
    console.log('[UI] ✅ Present Fields:', meta.componentSetLevel.present.join(', '));
  }
  if (meta?.variantLevel?.missingDescription?.length) {
    const variantNames = meta.variantLevel.missingDescription.map(v => v.name || 'Unknown');
    console.log('[UI] ❌ Variants Missing Descriptions:', variantNames.join(', '));
  }
  if (meta?.propertyLevel?.missingDescription?.length) {
    console.log('[UI] ❌ Properties Missing Descriptions:', meta.propertyLevel.missingDescription.join(', '));
  }

  // Accessibility metadata
  const a11y = meta?.accessibilityMetadata || {};
  console.log('[UI] Accessibility:', {
    hasAriaLabel: a11y.hasAriaLabel || false,
    hasA11yNotes: a11y.hasA11yNotes || false,
    hasFocusStates: a11y.hasFocusStates || false,
    hasContrastInfo: a11y.hasContrastInfo || false
  });
  console.log('───────────────────────────────────────────────────────────────────');

  state.metadata = meta;

  // Update metadata score display
  const score = meta?.completenessScore || 0;
  const metadataScoreEl = $('metadataScore');
  const metadataBarEl = $('metadataBar');
  const metadataStatusEl = $('metadataStatus');

  if (metadataScoreEl) {
    metadataScoreEl.textContent = score;
  }
  if (metadataBarEl) {
    metadataBarEl.style.width = score + '%';
    metadataBarEl.className = 'score-bar-fill ' + (score >= 80 ? 'high' : score >= 60 ? 'medium' : 'low');
  }
  if (metadataStatusEl) {
    if (score >= 80) {
      metadataStatusEl.textContent = '✓ Metadata complete';
      metadataStatusEl.className = 'score-status ready';
    } else {
      const missing = (meta?.componentSetLevel?.missing?.length || 0) +
                     (meta?.variantLevel?.missingDescription?.length || 0) +
                     (meta?.propertyLevel?.missingDescription?.length || 0);
      metadataStatusEl.textContent = `⚠️ ${missing} fields need attention`;
      metadataStatusEl.className = 'score-status not-ready';
    }
  }

  // Render detailed metadata view
  const detailsEl = $('metadataDetails');
  if (!detailsEl || !meta) return;

  detailsEl.innerHTML = renderMetadataDetails(meta);

  // Add toggle handlers for collapsible sections
  detailsEl.querySelectorAll('.metadata-section-header').forEach(header => {
    header.addEventListener('click', () => {
      header.parentElement.classList.toggle('collapsed');
    });
  });

  updateExport();
}

/**
 * Render detailed metadata view
 * @param {Object} meta - Metadata object
 * @param {Object|null} generated - Optional generated metadata
 * @returns {string} HTML string
 */
export function renderMetadataDetails(meta, generated = null) {
  const componentName = escapeHtml(meta.componentName || 'Component');
  const csl = meta.componentSetLevel || { present: [], missing: [], incomplete: [] };
  const vl = meta.variantLevel || { total: 0, withDescription: 0, missingDescription: [] };
  const pl = meta.propertyLevel || { total: 0, withDescription: 0, missingDescription: [] };
  const a11y = meta.accessibilityMetadata || {};
  const gen = generated || state.generated;

  // Helper to get generated value for a field
  function getGeneratedValue(key) {
    if (!gen) return null;
    switch(key) {
      case 'description': return gen.description;
      case 'tags': return Array.isArray(gen.tags) ? gen.tags.join(', ') : gen.tags;
      case 'notes': return gen.notes;
      case 'category': return gen.category;
      case 'level': return gen.level;
      default: return null;
    }
  }

  // Required fields definition with labels
  const requiredFields = [
    { key: 'description', label: 'Description', icon: '📝' },
    { key: 'tags', label: 'Tags', icon: '🏷️' },
    { key: 'notes', label: 'Notes', icon: '📋' },
    { key: 'category', label: 'Category', icon: '📁' },
    { key: 'level', label: 'Atomic Level', icon: '⚛️' }
  ];

  // Build Required Fields section
  const requiredFieldsHtml = requiredFields.map(field => {
    const isPresent = csl.present.includes(field.key);
    const isIncomplete = csl.incomplete.includes(field.key);
    const isMissing = csl.missing.includes(field.key);
    const generatedValue = getGeneratedValue(field.key);
    const hasGenerated = !isPresent && generatedValue;

    let statusClass = 'missing';
    let statusIcon = '✗';
    if (isPresent) { statusClass = 'present'; statusIcon = '✓'; }
    else if (hasGenerated) { statusClass = 'present'; statusIcon = '✨'; }
    else if (isIncomplete) { statusClass = 'incomplete'; statusIcon = '!'; }

    // Determine display value
    let valueHtml = '';
    if (isPresent) {
      valueHtml = '<span>Configured</span>';
    } else if (hasGenerated) {
      const displayVal = String(generatedValue).length > 80
        ? String(generatedValue).substring(0, 80) + '...'
        : generatedValue;
      valueHtml = `
        <span class="generated-badge">✨ Generated</span>
        <span class="generated-value">${escapeHtml(displayVal)}</span>
      `;
    } else {
      valueHtml = `<span class="empty">${isMissing ? 'Not set' : 'Incomplete'}</span>`;
    }

    return `
      <div class="metadata-field">
        <div class="metadata-field-icon ${statusClass}">${statusIcon}</div>
        <div class="metadata-field-content">
          <div class="metadata-field-name">${field.icon} ${field.label}</div>
          <div class="metadata-field-value ${hasGenerated ? 'generated' : (isPresent ? '' : 'empty')}">
            ${valueHtml}
          </div>
        </div>
      </div>
    `;
  }).join('');

  // FIX: Only count fields that are in our displayed requiredFields list
  const requiredFieldKeys = requiredFields.map(f => f.key);
  const requiredComplete = csl.present.filter(key => requiredFieldKeys.includes(key)).length;
  const requiredTotal = requiredFields.length;
  const requiredStatus = requiredComplete === requiredTotal ? 'complete' :
                        (requiredComplete > 0 ? 'incomplete' : 'missing');

  // Build Variants section - show generated descriptions for missing variants
  const variantDescriptions = gen?.variantDescriptions || gen?.variants || {};
  const variantsHtml = vl.total > 0 ? `
    <div class="variant-list">
      ${(vl.missingDescription || []).map(v => {
        const variantName = escapeHtml(v.name || 'Unknown');
        const generatedDesc = variantDescriptions[v.name || 'Unknown'];
        if (generatedDesc) {
          const shortDesc = String(generatedDesc).length > 60
            ? String(generatedDesc).substring(0, 60) + '...'
            : generatedDesc;
          return `
            <div class="variant-item">
              <span class="variant-name">${variantName}</span>
              <span class="variant-status generated">✨ Generated</span>
            </div>
            <div style="padding: 4px 8px 8px 12px; font-size: 11px; color: #78350f; background: linear-gradient(135deg, #fffbeb, #fef3c7); margin: -8px 0 4px 0; border-radius: 0 0 4px 4px; border-left: 3px solid #f59e0b;">
              ${escapeHtml(shortDesc)}
            </div>
          `;
        }
        return `
          <div class="variant-item">
            <span class="variant-name">${variantName}</span>
            <span class="variant-status no-desc">Missing description</span>
          </div>
        `;
      }).join('')}
      ${vl.withDescription > 0 ? `
        <div class="variant-item" style="color: var(--success);">
          <span class="variant-name">✓ ${vl.withDescription} variant(s) with descriptions</span>
        </div>
      ` : ''}
    </div>
  ` : (state.node?.type === 'COMPONENT'
      ? '<div class="metadata-field-value empty" style="font-style: italic; color: #6b7280;">💡 Select a Component Set to see variant descriptions</div>'
      : '<div class="metadata-field-value empty">No variants found</div>');

  const variantStatus = vl.total === 0 ? 'complete' :
                       (vl.withDescription === vl.total ? 'complete' :
                       (vl.withDescription > 0 ? 'incomplete' : 'missing'));

  // Build Properties section - show generated descriptions for missing properties
  const propertyDescriptions = gen?.propertyDescriptions || {};
  const propertiesHtml = pl.total > 0 ? `
    <div class="variant-list">
      ${(pl.missingDescription || []).map(prop => {
        const generatedDesc = propertyDescriptions[prop];
        const safeProp = escapeHtml(prop);
        if (generatedDesc) {
          const shortDesc = String(generatedDesc).length > 60
            ? String(generatedDesc).substring(0, 60) + '...'
            : generatedDesc;
          return `
            <div class="variant-item">
              <span class="variant-name">${safeProp}</span>
              <span class="variant-status generated">✨ Generated</span>
            </div>
            <div style="padding: 4px 8px 8px 12px; font-size: 11px; color: #78350f; background: linear-gradient(135deg, #fffbeb, #fef3c7); margin: -8px 0 4px 0; border-radius: 0 0 4px 4px; border-left: 3px solid #f59e0b;">
              ${escapeHtml(shortDesc)}
            </div>
          `;
        }
        return `
          <div class="variant-item">
            <span class="variant-name">${safeProp}</span>
            <span class="variant-status no-desc">Missing description</span>
          </div>
        `;
      }).join('')}
      ${pl.withDescription > 0 ? `
        <div class="variant-item" style="color: var(--success);">
          <span class="variant-name">✓ ${pl.withDescription} property(ies) with descriptions</span>
        </div>
      ` : ''}
    </div>
  ` : (state.node?.type === 'COMPONENT'
      ? '<div class="metadata-field-value empty" style="font-style: italic; color: #6b7280;">💡 Select a Component Set to see property descriptions</div>'
      : '<div class="metadata-field-value empty">No properties found</div>');

  const propertyStatus = pl.total === 0 ? 'complete' :
                        (pl.withDescription === pl.total ? 'complete' :
                        (pl.withDescription > 0 ? 'incomplete' : 'missing'));

  // Build Accessibility section - with generated values
  const a11yFields = [
    { key: 'hasAriaLabel', label: 'ARIA Label', value: a11y.hasAriaLabel, genKey: 'ariaLabel' },
    { key: 'hasA11yNotes', label: 'A11y Notes', value: a11y.hasA11yNotes, genKey: 'a11y' },
    { key: 'hasFocusStates', label: 'Focus States', value: a11y.hasFocusStates, genKey: 'states' },
    { key: 'hasContrastInfo', label: 'Contrast Info', value: a11y.hasContrastInfo, genKey: 'specs' }
  ];

  // FIX: Pre-calculate which fields have generated values for counting
  const a11yFieldsWithGenerated = a11yFields.map(field => {
    let generatedValue = null;
    if (!field.value && gen && field.genKey) {
      if (field.genKey === 'ariaLabel') generatedValue = gen.ariaLabel;
      else if (field.genKey === 'a11y') generatedValue = Array.isArray(gen.a11y) ? gen.a11y.join('; ') : gen.a11y;
      else if (field.genKey === 'states') generatedValue = gen.states?.focus;
      else if (field.genKey === 'specs') generatedValue = gen.specs?.contrast;
    }
    return { ...field, generatedValue, hasGenerated: !field.value && !!generatedValue };
  });

  const a11yHtml = a11yFieldsWithGenerated.map(field => {
    const hasGenerated = field.hasGenerated;
    const generatedValue = field.generatedValue;

    let valueHtml = '';
    if (field.value) {
      valueHtml = '<span>Configured</span>';
    } else if (hasGenerated) {
      const shortVal = String(generatedValue).length > 50
        ? String(generatedValue).substring(0, 50) + '...'
        : generatedValue;
      valueHtml = `
        <span class="generated-badge">✨ Generated</span>
        <span class="generated-value">${escapeHtml(shortVal)}</span>
      `;
    } else {
      valueHtml = '<span class="empty">Not set</span>';
    }

    return `
      <div class="metadata-field">
        <div class="metadata-field-icon ${field.value ? 'present' : (hasGenerated ? 'present' : 'missing')}">${field.value ? '✓' : (hasGenerated ? '✨' : '✗')}</div>
        <div class="metadata-field-content">
          <div class="metadata-field-name">${field.label}</div>
          <div class="metadata-field-value ${hasGenerated ? 'generated' : (field.value ? '' : 'empty')}">
            ${valueHtml}
          </div>
        </div>
      </div>
    `;
  }).join('');

  // FIX: Count fields that have EITHER original value OR generated value
  const a11yCount = a11yFieldsWithGenerated.filter(f => f.value || f.hasGenerated).length;
  const a11yStatus = a11yCount === a11yFields.length ? 'complete' :
                    (a11yCount > 0 ? 'incomplete' : 'missing');

  return `
    <!-- Component Name Header -->
    <div style="font-size: 14px; font-weight: 600; margin-bottom: 12px; padding: 8px 12px; background: var(--gray-50); border-radius: 6px;">
      📦 ${componentName}
    </div>

    <!-- Required Fields Section -->
    <div class="metadata-section">
      <div class="metadata-section-header">
        <div>
          <span class="section-icon">📋</span>
          Required Fields
        </div>
        <div class="section-status ${requiredStatus}">
          ${requiredComplete}/${requiredTotal}
          <span class="chevron">▼</span>
        </div>
      </div>
      <div class="metadata-section-content">
        ${requiredFieldsHtml}
      </div>
    </div>

    <!-- Variants Section -->
    <div class="metadata-section ${vl.total === 0 ? 'collapsed' : ''}">
      <div class="metadata-section-header">
        <div>
          <span class="section-icon">🔀</span>
          Variant Descriptions
        </div>
        <div class="section-status ${variantStatus}">
          ${vl.withDescription}/${vl.total}
          <span class="chevron">▼</span>
        </div>
      </div>
      <div class="metadata-section-content">
        ${variantsHtml}
      </div>
    </div>

    <!-- Properties Section -->
    <div class="metadata-section ${pl.total === 0 ? 'collapsed' : ''}">
      <div class="metadata-section-header">
        <div>
          <span class="section-icon">⚙️</span>
          Property Descriptions
        </div>
        <div class="section-status ${propertyStatus}">
          ${pl.withDescription}/${pl.total}
          <span class="chevron">▼</span>
        </div>
      </div>
      <div class="metadata-section-content">
        ${propertiesHtml}
      </div>
    </div>

    <!-- Accessibility Section -->
    <div class="metadata-section">
      <div class="metadata-section-header">
        <div>
          <span class="section-icon">♿</span>
          Accessibility Metadata
        </div>
        <div class="section-status ${a11yStatus}">
          ${a11yCount}/${a11yFields.length}
          <span class="chevron">▼</span>
        </div>
      </div>
      <div class="metadata-section-content">
        ${a11yHtml}
      </div>
    </div>
  `;
}
