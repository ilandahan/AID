/**
 * Internationalization (i18n) Module
 * Handles translations for the Figma plugin UI
 */

export const i18n = {
  en: {
    // Status messages
    'status.loading': 'Waiting for analysis...',
    'status.analyzing': 'Analyzing component...',
    'status.complete': '✓ Analysis complete',
    'status.ready': 'Ready to export',
    'status.notReady': 'Score below threshold',
    'status.metadataApplied': '✓ Metadata applied to Figma',

    // Tabs
    'tab.review': 'Review',
    'tab.audit': 'Audit',
    'tab.metadata': 'Metadata',
    'tab.report': 'Dev Info',
    'tab.export': 'Export',

    // Review Tab
    'review.title': 'Design Review Before Export',
    'review.subtitle': 'AI.D - Atomic Design Extractor reviews your design system and recommends enhancements before a single line of code is written. We believe in keeping you in control — your designs, your decisions, nothing moves forward without your approval.',
    'review.scoreBreakdown': 'Score Breakdown',
    'review.auditWeight': 'Audit',
    'review.metadataWeight': 'Metadata Analysis',

    // Selection
    'selection.empty': 'Select a Component Set or a single Component in Figma to begin',

    // Sections
    'section.issues': 'Issues',
    'section.score': 'Quality Score',
    'section.fields': 'Fields',

    // Buttons
    'btn.runAudit': 'Run Audit',
    'btn.generateMeta': 'Generate Metadata',
    'btn.applyToFigma': 'Apply to Figma',
    'btn.export': 'Export to AI.D',
    'btn.runPipeline': 'Run Full Pipeline',
    'btn.copyMarkdown': 'Copy Markdown',
    'btn.copyTypeScript': 'Copy TypeScript',

    // Empty states
    'empty.noComponent': 'Select a Component Set in Figma to begin',
    'empty.noAudit': 'Run an audit to see issues',
    'empty.noMetadata': 'Generate metadata to see fields',
    'empty.noReport': 'Run full pipeline to generate report',

    // Severity
    'severity.critical': 'Critical',
    'severity.error': 'Error',
    'severity.warning': 'Warning',
    'severity.info': 'Info',

    // Categories
    'category.structure': 'Structure',
    'category.naming': 'Naming',
    'category.consistency': 'Consistency',
    'category.accessibility': 'Accessibility',

    // Pairing
    'pairing.title': 'Connect to AI.D Server',
    'pairing.prompt': 'Enter the 6-digit code shown in your AI.D terminal:',
    'pairing.placeholder': 'Enter code (e.g., 123 456)',
    'pairing.connect': 'Connect',
    'pairing.cancel': 'Cancel',
    'pairing.success': '✓ Connected to AI.D Server',
    'pairing.failed': 'Connection failed. Please check the code and try again.',
    'pairing.invalidFormat': 'Please enter a valid 6-digit code',

    // Connection status
    'connection.paired': '✓ Paired with AI.D',
    'connection.notPaired': 'Not connected',
    'connection.validating': 'Validating session...',
    'connection.reconnecting': '🔄 Reconnecting to AI.D...',
    'connection.lost': 'Connection lost. Attempting to reconnect...',
    'connection.expiring': '⚠️ Session expiring in {{minutes}} minutes. Re-pair to continue.',
    'connection.restored': 'Connection restored!',

    // MCP Status
    'mcp.connecting': 'Connecting to AI.D Server...',
    'mcp.pleaseWait': 'Please wait while we establish connection',
    'mcp.connected': 'Connected to AI.D',
    'mcp.ready': 'Ready to review your designs',
    'mcp.error': 'Connection Failed',
    'mcp.errorMessage': 'Could not connect to AI.D server. Please check if the server is running.',

    // AID Connection Screen
    'aid.title': 'Atomic Design Extractor',
    'aid.subtitle': 'analyze and export your Figma components to atomic design',
    'aid.notPaired': 'Not paired with AI.D Server',
    'aid.pairButton': 'Pair with AI.D',
    'aid.howToPair': 'How to pair:',
    'aid.step1': 'Start the AI.D tool',
    'aid.step2': 'Run',
    'aid.step3': 'Enter the code and click "Pair with AI.D"',

    // Pipeline phases
    'phase.audit': 'Audit',
    'phase.metadata': 'Metadata',
    'phase.analyze': 'Analyze',
    'phase.generate': 'Generate',
    'phase.report': 'Report',
    'phase.summary': 'Review Summary',
    'phase.combined': 'Combined Score',
    'phase.ready': 'Ready',

    // Pipeline UI
    'pipeline.title': 'Review Progress',
    'pipeline.audit': 'Quality Audit',
    'pipeline.metadata': 'Metadata Check',
    'pipeline.generate': 'Smart Suggestions',
    'pipeline.report': 'Final Report',
    'pipeline.status.idle': 'Waiting...',
    'pipeline.status.waiting': 'Queued...',
    'pipeline.status.running': 'Running...',
    'pipeline.status.running.audit': 'Checking design quality...',
    'pipeline.status.running.metadata': 'Analyzing metadata...',
    'pipeline.status.running.generate': 'Generating suggestions...',
    'pipeline.status.running.report': 'Creating report...',
    'pipeline.status.done.audit': 'Audit complete',
    'pipeline.status.done.metadata': 'Metadata analyzed',
    'pipeline.status.done.generate': 'Suggestions ready',
    'pipeline.status.done.report': 'Report generated',
    'pipeline.status.complete': 'Complete',
    'pipeline.status.error': 'Failed',

    // Actions
    'action.runPipeline': 'Run Full Review',
    'action.runAudit': 'Run Audit',
    'action.analyzeMetadata': 'Analyze',
    'action.generateAuto': 'Generate',
    'action.applyToFigma': 'Apply to Figma',
    'action.cancel': 'Cancel',
    'action.confirmApply': 'Confirm & Apply',
    'action.keepCurrent': 'Keep Current',
    'action.switchComponent': 'Switch',
    'action.exportToAID': 'Export to AID',

    // Modal dialogs
    'modal.switchComponent': 'Switch Component?',
    'modal.currentComponent': 'You have analysis data for:',
    'modal.discardWarning': 'Switching to a new component will discard this data.',
    'modal.approveMetadata': 'Approve Metadata',
    'modal.reviewBeforeApply': 'Review the generated metadata before applying to Figma:',

    // Issues
    'issues.title': 'Issues Found',
    'issues.none': 'No issues found - great job!',

    // Notifications
    'notify.auditComplete': 'Audit complete',
    'notify.analysisComplete': 'Analysis complete',
    'notify.generated': 'Metadata generated',
    'notify.reportReady': 'Report ready',
    'notify.pipelineComplete': 'Pipeline complete',
    'notify.connected': 'Connected to AI.D',
    'notify.error': 'Error',

    // Export levels
    'export.level.atom': 'Atom',
    'export.level.molecule': 'Molecule',
    'export.level.organism': 'Organism',

    // Export tab labels
    'export.destination': 'Destination:',
    'export.score': 'Score:',
    'export.filesCreated': 'Files to be created:',
    'export.autoDetected': '(auto-detected)',

    // Status
    'status.pointsNeeded': '{{points}} more points needed to export',
    'status.applyFailed': 'Failed to apply metadata',
    'status.issuesToFix': '{{count}} issues to address',

    // Metadata tab
    'metadata.runAnalysis': 'Run analysis to check metadata',
    'metadata.selectComponent': 'Select a component and click "Analyze" to view details',
    'metadata.completeness': 'Metadata Completeness',

    // Score labels
    'score.overall': 'Overall Score',
    'score.audit': 'Audit Score'
  }
};

/**
 * Translate a key to the current language
 * @param {string} key - Translation key
 * @param {Object} vars - Variables to interpolate
 * @returns {string} Translated text
 */
export function t(key, vars = {}) {
  let text = i18n.en[key] || key;
  for (const [k, v] of Object.entries(vars)) {
    text = text.replace(`{{${k}}}`, v);
  }
  return text;
}

/**
 * Initialize all i18n elements on load
 */
export function initializeTranslations() {
  document.querySelectorAll('[data-i18n]').forEach(el => {
    el.textContent = t(el.dataset.i18n);
  });
}
