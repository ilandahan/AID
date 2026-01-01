/**
 * @file plugin/pipeline/index.ts
 * @description Pipeline module barrel export
 */

// Audit phase
export {
  runLocalAudit,
  runServerAudit,
  runDeepInspection,
  mergeAuditResults,
} from './audit-phase';

// Metadata phase
export { analyzeMetadata, generateMetadata, injectTokensIfNeeded } from './metadata-phase';

// Apply phase
export { applyMetadataToFigma, prepareFigmaDescription } from './apply-phase';
