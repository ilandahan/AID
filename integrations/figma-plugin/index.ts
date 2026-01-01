// ============================================
// Services Barrel Export
// ============================================

// Core Services
export { NodeAnalyzer, nodeAnalyzer } from './NodeAnalyzer';
export { QueueManager, queueManager } from './QueueManager';
export { MCPClient, createMCPClient } from './MCPClient';
export { ComponentEnricher, componentEnricher } from './ComponentEnricher';
export { AuthService, authService } from './AuthService';
export type { AuthConfig, AuthMethod, AuthResult, UserInfo, OAuthConfig } from './AuthService';

// Quality Pipeline Services (NEW)
export { ComponentAuditor, runAudit, analyzeMetadata, prepareForMCP } from './ComponentAuditor';
export { ScoringEngine, scoringEngine, calculateScore, isExportReady, generateReport } from './ScoringEngine';

// Content Export
export { ContentExtractor, extractContent, exportAsTypeScript, exportAsJSON } from './ContentExtractor';
export type { ExtractedComponent, ExtractedVariant, ExtractedText, ExportFormat, ComponentPropertyDefinition } from './ContentExtractor';
