/**
 * Issues Rendering Module
 * Renders audit issues grouped by component and severity
 */

import { state } from '../state.js';
import { t } from '../utils/i18n.js';
import { escapeHtml } from '../utils/sanitize.js';

/**
 * Render issues grouped by component, then by severity
 * Uses CSS classes from ui.html for styling (maintainable approach)
 * @param {Array} issues - Array of issue objects
 * @param {string} componentName - Name of the root component
 * @returns {string} HTML string
 */
export function renderIssuesBySeverity(issues, componentName) {
  if (!issues || issues.length === 0) {
    return `<div class="no-issues">${t('issues.none')}</div>`;
  }

  const severityOrder = ['error', 'warning', 'info'];
  const severityLabels = {
    error: { icon: '🔴', label: t('severity.error') },
    warning: { icon: '🟡', label: t('severity.warning') },
    info: { icon: '🔵', label: t('severity.info') }
  };

  // Use provided componentName or fall back to state
  const rootCompName = componentName || state.node?.name || '';

  // Step 1: Group issues by component/variant name first
  // Location format: "VariantName > path" - extract first part as component name
  const byComponent = {};
  issues.forEach(issue => {
    // Extract component name from location (first part before " > ")
    let compKey = rootCompName;
    if (issue.location) {
      const parts = issue.location.split(' > ');
      if (parts.length > 0 && parts[0].trim()) {
        compKey = parts[0].trim();
      }
    }
    if (!byComponent[compKey]) {
      byComponent[compKey] = { issues: [], nodeId: null };
    }
    byComponent[compKey].issues.push(issue);
    // Store the first nodeId found for "Go to" button on component header
    if (issue.nodeId && !byComponent[compKey].nodeId) {
      byComponent[compKey].nodeId = issue.nodeId;
    }
  });

  // Step 2: For each component, group by severity
  let html = '';
  Object.keys(byComponent).forEach(compKey => {
    const compData = byComponent[compKey];
    const compIssues = compData.issues;
    const compNodeId = compData.nodeId;

    // Group this component's issues by severity
    const bySeverity = {};
    severityOrder.forEach(s => bySeverity[s] = []);
    compIssues.forEach(issue => {
      const sev = issue.severity || 'info';
      if (bySeverity[sev]) bySeverity[sev].push(issue);
    });

    // Calculate total issues for this component
    const totalIssues = compIssues.length;

    // Render component header with "Go to" button (uses CSS classes)
    html += `
      <div class="component-group">
        <div class="component-header">
          <div style="display: flex; align-items: center; gap: 8px;">
            <span class="component-name">📦 ${escapeHtml(compKey)}</span>
            <span class="count">${totalIssues} issue${totalIssues !== 1 ? 's' : ''}</span>
          </div>
          ${compNodeId ? `
            <button class="goto-btn" data-node-id="${compNodeId}" title="${t('action.goToComponent') || 'Go to this component in Figma'}">
              <span>🎯</span>
              <span>Go to</span>
            </button>
          ` : ''}
        </div>
        <div class="component-issues">
    `;

    // Render severity groups within this component
    severityOrder.forEach(severity => {
      const items = bySeverity[severity];
      if (items.length === 0) return;

      const { icon, label } = severityLabels[severity];
      html += `
        <div class="severity-group">
          <div class="severity-header">
            <span>${icon}</span>
            <span>${label}</span>
            <span class="count">${items.length}</span>
          </div>
          ${items.map((issue) => renderIssueItem(issue, severity)).join('')}
        </div>
      `;
    });

    html += `
        </div>
      </div>
    `;
  });

  return html;
}

/**
 * Render a single issue item
 * Extracted for readability and reusability
 * @param {Object} issue - Issue object
 * @param {string} severity - Severity level (error/warning/info)
 * @returns {string} HTML string
 */
function renderIssueItem(issue, severity) {
  // Extract variant name (first part) and remaining path
  let variantName = '';
  let subPath = '';
  if (issue.location) {
    const parts = issue.location.split(' > ');
    if (parts.length > 0) {
      variantName = parts[0].trim();
    }
    if (parts.length > 1) {
      subPath = parts.slice(1).join(' > ');
    }
  }

  return `
    <div class="issue-item ${severity}">
      <div class="issue-content">
        ${variantName ? `
          <div class="issue-variant" style="font-size: 10px; color: var(--gray-500); margin-bottom: 2px; font-weight: 500;">
            🏷️ ${escapeHtml(variantName)}
          </div>
        ` : ''}
        <div class="issue-message">${escapeHtml(issue.message)}</div>
        ${subPath ? `
          <div class="issue-location">
            <span>📍</span>
            <span>${escapeHtml(subPath)}</span>
          </div>
        ` : ''}
      </div>
      ${issue.nodeId ? `
        <button class="goto-btn small" data-node-id="${issue.nodeId}" title="${t('action.goToElement') || 'Go to this element in Figma'}">
          <span>🎯</span>
        </button>
      ` : ''}
    </div>
  `;
}
