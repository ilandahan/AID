/**
 * Report Rendering Module
 * Handles developer handoff and report generation
 */

import { state, $ } from '../state.js';
import { updateExport } from './export.js';
import { copyToClipboard } from '../utils/clipboard.js';
import { escapeHtml } from '../utils/sanitize.js';

/**
 * Update report display
 * @param {Object} report - Report object
 */
export function updateReport(report) {
  // Update Developer Handoff view
  renderDevHandoff();
  updateExport();
}

/**
 * Render developer handoff section
 */
export function renderDevHandoff() {
  console.log('[UI] 🔧 renderDevHandoff() called');
  const gen = state.generated;
  const component = state.componentInfo;
  const meta = state.metadata;

  // Debug: Log what data we have
  console.log('[UI] 🔧 state.generated exists:', !!gen);
  if (gen?.tokens) {
    console.log('[UI] 🔧 gen.tokens type:', Array.isArray(gen.tokens) ? 'array' : typeof gen.tokens);
    console.log('[UI] 🔧 gen.tokens:', JSON.stringify(gen.tokens).substring(0, 200));
  } else {
    console.log('[UI] 🔧 gen.tokens is:', gen?.tokens);
  }

  // Show/hide empty state
  const hasData = gen || component || meta;
  const devEmptyEl = $('devHandoffEmpty');
  const devContentEl = $('devHandoffContent');
  const devButtonsEl = $('devHandoffButtons');
  if (devEmptyEl) devEmptyEl.style.display = hasData ? 'none' : 'flex';
  if (devContentEl) devContentEl.style.display = hasData ? 'block' : 'none';
  if (devButtonsEl) devButtonsEl.style.display = hasData ? 'flex' : 'none';

  if (!hasData) return;

  // Component name and level
  const componentName = component?.name || gen?.componentName || meta?.componentName || 'Component';
  const level = gen?.level || 'atom';
  const levelIcons = { atom: '⚛️', molecule: '🧬', organism: '🦠', template: '📄', page: '📑' };

  // Update the unified component info panel for Dev Info tab
  const devCompNameEl = $('devComponentInfoName');
  const devCompMetaEl = $('devComponentInfoMeta');
  if (devCompNameEl) devCompNameEl.textContent = '📦 ' + componentName;
  if (devCompMetaEl) {
    // Show level with icon in the meta line
    const levelIcon = levelIcons[level] || '⚛️';
    const levelText = level.charAt(0).toUpperCase() + level.slice(1);
    const variantCount = gen?.variantCount || state.node?.variantCount || 0;
    const variantText = variantCount > 0 ? `${variantCount} variant${variantCount !== 1 ? 's' : ''} • ` : '';
    devCompMetaEl.textContent = `${variantText}${levelIcon} ${levelText}`;
  }

  // Component Stats Section
  const statsItems = [];
  const nodeInfo = state.node || {};
  const componentInfo = state.componentInfo || {};

  // Component type
  const nodeType = nodeInfo.type || componentInfo.type || 'Unknown';
  const isComponentSet = nodeType === 'COMPONENT_SET';
  statsItems.push({ label: 'Type', value: isComponentSet ? 'Component Set' : nodeType });

  // Variant count
  const variantCount = gen?.variantCount || componentInfo.variantCount ||
    (isComponentSet && state.node?.children?.length) || 0;
  if (variantCount > 0) {
    statsItems.push({ label: 'Variants', value: String(variantCount) });
  }

  // Properties count
  const propCount = gen?.propertyDescriptions ? Object.keys(gen.propertyDescriptions).length :
    (componentInfo.properties?.length || 0);
  statsItems.push({ label: 'Properties', value: String(propCount) });

  // Child count
  const childCount = nodeInfo.childCount || componentInfo.childCount || 0;
  if (childCount > 0) {
    statsItems.push({ label: 'Children', value: String(childCount) });
  }

  // Dimensions
  const width = nodeInfo.width || componentInfo.width;
  const height = nodeInfo.height || componentInfo.height;
  if (width && height) {
    statsItems.push({ label: 'Size', value: `${Math.round(width)} × ${Math.round(height)}` });
  }

  // Has auto-layout
  if (nodeInfo.hasAutoLayout || componentInfo.hasAutoLayout) {
    statsItems.push({ label: 'Layout', value: 'Auto Layout ✓' });
  }

  // Has interactive states
  if (nodeInfo.hasStates || componentInfo.hasStates) {
    statsItems.push({ label: 'Interactive', value: 'Has States ✓' });
  }

  const statsHtml = statsItems.length > 0 ? statsItems.map(item => `
    <div class="dev-prop-row">
      <span class="dev-prop-name">${escapeHtml(item.label)}</span>
      <span style="color: var(--gray-600);">${escapeHtml(item.value)}</span>
    </div>
  `).join('') : '<div style="color: var(--gray-500); font-style: italic;">No stats available</div>';
  const devStatsEl = $('devStatsContent');
  if (devStatsEl) devStatsEl.innerHTML = statsHtml;

  // Props Section - Use propertyDescriptions from generated metadata
  const propDescriptions = gen?.propertyDescriptions || {};
  const propEntries = Object.entries(propDescriptions);
  const propsHtml = propEntries.length > 0 ? propEntries.map(([propName, propDesc]) => {
    return `<div class="dev-prop-row">
      <span class="dev-prop-name">${escapeHtml(propName)}</span>
      <span style="color: var(--gray-600); font-size: 11px;">${escapeHtml(propDesc)}</span>
    </div>`;
  }).join('') : '<div style="color: var(--gray-500); font-style: italic;">No props detected</div>';
  const devPropsEl = $('devPropsContent');
  if (devPropsEl) devPropsEl.innerHTML = propsHtml;

  // States Section - Use variantDescriptions from generated metadata
  const variantDescs = gen?.variantDescriptions || {};
  const variantEntries = Object.entries(variantDescs);
  const statesHtml = variantEntries.length > 0 ? variantEntries.map(([variantName, variantDesc]) => {
    if (!variantDesc) return '';
    return `<div class="dev-prop-row">
      <span class="dev-prop-name">${escapeHtml(variantName)}</span>
      <span style="color: var(--gray-600); font-size: 11px;">${escapeHtml(variantDesc)}</span>
    </div>`;
  }).filter(Boolean).join('') : '<div style="color: var(--gray-500); font-style: italic;">No variants/states documented</div>';
  const devStatesEl = $('devStatesContent');
  if (devStatesEl) devStatesEl.innerHTML = statesHtml;

  // Accessibility Section
  const a11yItems = [];
  if (gen?.ariaLabel) a11yItems.push({ label: 'ARIA Label', value: gen.ariaLabel });
  if (gen?.a11y && Array.isArray(gen.a11y)) {
    gen.a11y.forEach((item, i) => a11yItems.push({ label: `Guideline ${i+1}`, value: item }));
  }
  if (gen?.specs?.contrast) a11yItems.push({ label: 'Contrast', value: gen.specs.contrast });
  if (gen?.specs?.touchTarget) a11yItems.push({ label: 'Touch Target', value: gen.specs.touchTarget });

  const a11yHtml = a11yItems.length > 0 ? a11yItems.map(item => `
    <div class="dev-prop-row">
      <span class="dev-prop-name">${escapeHtml(item.label)}</span>
      <span style="color: var(--gray-600);">${escapeHtml(item.value)}</span>
    </div>
  `).join('') : '<div style="color: var(--gray-500); font-style: italic;">No accessibility data</div>';
  const devA11yEl = $('devA11yContent');
  if (devA11yEl) devA11yEl.innerHTML = a11yHtml;

  // Tokens Section - Handle both object format (from server) and array format (raw from plugin)
  let tokens = gen?.tokens || {};
  const tokenItems = [];

  // CLIENT-SIDE FALLBACK: If tokens is an array (raw from plugin), convert it to object format
  if (Array.isArray(tokens)) {
    console.log('[UI] 🔄 Converting raw tokens array to object format:', tokens.length, 'tokens');
    const converted = {};
    const getCategory = (t) => t.category || t.type;

    const colors = tokens.filter(t => getCategory(t) === 'color');
    if (colors.length > 0) converted.colors = colors.map(t => t.value).join(', ');

    const spacing = tokens.filter(t => getCategory(t) === 'spacing');
    if (spacing.length > 0) converted.spacing = spacing.map(t => `${t.name}: ${t.value}`).join(', ');

    const typography = tokens.filter(t => getCategory(t) === 'typography');
    if (typography.length > 0) converted.typography = typography.map(t => t.value).join(', ');

    const radius = tokens.filter(t => getCategory(t) === 'borderRadius');
    if (radius.length > 0) converted.radius = radius.map(t => t.value).join(', ');

    const shadows = tokens.filter(t => getCategory(t) === 'shadow');
    if (shadows.length > 0) converted.shadows = shadows.map(t => t.value).join(', ');

    tokens = converted;
    console.log('[UI] ✅ Converted tokens:', tokens);
  }

  // Debug: Log what tokens we have
  console.log('[UI] 🎨 Tokens for display:', tokens);

  // Helper to get token value (handles string or array format)
  const getTokenValue = (val) => {
    if (!val) return null;
    if (Array.isArray(val)) return val.join(', ');
    if (typeof val === 'string') return val;
    return null;
  };

  const colorsVal = getTokenValue(tokens.colors);
  const spacingVal = getTokenValue(tokens.spacing);
  const typographyVal = getTokenValue(tokens.typography);
  const radiusVal = getTokenValue(tokens.radius);
  const shadowsVal = getTokenValue(tokens.shadows);

  if (colorsVal) tokenItems.push({ label: 'Colors', value: colorsVal });
  if (spacingVal) tokenItems.push({ label: 'Spacing', value: spacingVal });
  if (typographyVal) tokenItems.push({ label: 'Typography', value: typographyVal });
  if (radiusVal) tokenItems.push({ label: 'Radius', value: radiusVal });
  if (shadowsVal) tokenItems.push({ label: 'Shadows', value: shadowsVal });

  console.log('[UI] 🎨 Token items built:', tokenItems.length, 'items');
  console.log('[UI] 🎨 Token items:', JSON.stringify(tokenItems));

  const tokensHtml = tokenItems.length > 0 ? tokenItems.map(item => `
    <div class="dev-prop-row">
      <span class="dev-prop-name">${escapeHtml(item.label)}</span>
      <span style="color: var(--gray-600); font-size: 10px;">${escapeHtml(item.value)}</span>
    </div>
  `).join('') : '<div style="color: var(--gray-500); font-style: italic;">No tokens extracted</div>';

  console.log('[UI] 🎨 tokensHtml length:', tokensHtml.length, 'chars');

  const devTokensEl = $('devTokensContent');
  console.log('[UI] 🎨 devTokensContent element found:', !!devTokensEl);
  if (devTokensEl) devTokensEl.innerHTML = tokensHtml;

  // Testing Section
  const componentName2 = gen?.componentName || meta?.componentName || state.node?.name || 'Component';
  const testHtml = `
    <div class="dev-prop-row">
      <span class="dev-prop-name">Test ID</span>
      <span style="color: var(--gray-600);">${gen?.testId || `data-testid="${componentName2.toLowerCase().replace(/\s+/g, '-')}"`}</span>
    </div>
    <div class="dev-prop-row">
      <span class="dev-prop-name">Analytics</span>
      <span style="color: var(--gray-600);">${gen?.analytics || `track('${componentName2.toLowerCase()}_click')`}</span>
    </div>
  `;
  const devTestEl = $('devTestContent');
  if (devTestEl) devTestEl.innerHTML = testHtml;

  // Add toggle handlers for collapsible sections
  document.querySelectorAll('#report-tab .dev-handoff-header').forEach(header => {
    header.onclick = () => header.parentElement.classList.toggle('collapsed');
  });
}

/**
 * Generate markdown for developer handoff
 * @returns {string} Markdown content
 */
export function generateDevMarkdown() {
  const gen = state.generated;
  const meta = state.metadata;
  const componentName = gen?.componentName || meta?.componentName || state.node?.name || 'Component';
  const level = gen?.level || 'atom';

  let md = `# ${componentName}\n\n`;
  md += `**Atomic Level:** ${level.charAt(0).toUpperCase() + level.slice(1)}\n\n`;

  // Props - use propertyDescriptions from generated metadata
  const propDescriptions = gen?.propertyDescriptions || {};
  const propEntries = Object.entries(propDescriptions);
  if (propEntries.length > 0) {
    md += `## Props\n\n`;
    md += `| Prop | Description |\n|------|-------------|\n`;
    propEntries.forEach(([propName, propDesc]) => {
      md += `| ${propName} | ${propDesc} |\n`;
    });
    md += '\n';
  }

  // States/Variants - use variantDescriptions
  const variantDescs = gen?.variantDescriptions || {};
  const variantEntries = Object.entries(variantDescs);
  if (variantEntries.length > 0) {
    md += `## Variants/States\n\n`;
    md += `| Variant | Description |\n|---------|-------------|\n`;
    variantEntries.forEach(([variantName, variantDesc]) => {
      if (variantDesc) md += `| ${variantName} | ${variantDesc} |\n`;
    });
    md += '\n';
  }

  // Accessibility
  if (gen?.ariaLabel || gen?.a11y?.length) {
    md += `## Accessibility\n\n`;
    if (gen.ariaLabel) md += `- **ARIA Label:** ${gen.ariaLabel}\n`;
    if (gen.a11y) gen.a11y.forEach(item => md += `- ${item}\n`);
    md += '\n';
  }

  // Testing
  md += `## Testing\n\n`;
  md += `- **Test ID:** ${gen?.testId || `data-testid="${componentName.toLowerCase().replace(/\\s+/g, '-')}"`}\n`;
  md += `- **Analytics:** ${gen?.analytics || `track('${componentName.toLowerCase()}_click')`}\n`;

  return md;
}

/**
 * Generate TypeScript interface for developer handoff
 * @returns {string} TypeScript content
 */
export function generateDevTypeScript() {
  const gen = state.generated;
  const meta = state.metadata;
  const rawName = gen?.componentName || meta?.componentName || state.node?.name || 'Component';
  const componentName = rawName.replace(/[^a-zA-Z0-9]/g, '');

  // Use propertyDescriptions from generated metadata
  const propDescriptions = gen?.propertyDescriptions || {};
  const propEntries = Object.entries(propDescriptions);

  let ts = `// ${rawName} Component\n`;
  ts += `// Generated from Figma\n\n`;
  ts += `interface ${componentName}Props {\n`;

  if (propEntries.length > 0) {
    propEntries.forEach(([propName, propDesc]) => {
      const safePropName = propName.replace(/[^a-zA-Z0-9]/g, '');
      // Default to string type since we have descriptions, not types
      ts += `  /** ${propDesc} */\n`;
      ts += `  ${safePropName}?: string;\n`;
    });
  } else {
    ts += `  // No props detected\n`;
  }

  ts += `}\n\n`;
  ts += `// Test ID: ${gen?.testId || `${componentName.toLowerCase()}`}\n`;
  ts += `// Analytics: track('${componentName.toLowerCase()}_click')\n`;

  return ts;
}
