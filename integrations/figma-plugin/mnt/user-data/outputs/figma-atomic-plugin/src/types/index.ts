// ============================================
// Atomic Design Types & Interfaces
// ============================================

/** Atomic Design hierarchy levels */
export type AtomicLevel = 'atom' | 'molecule' | 'organism' | 'template' | 'page';

/** Component category */
export type ComponentCategory = 
  | 'button' 
  | 'navigation' 
  | 'form' 
  | 'layout' 
  | 'feedback' 
  | 'data-display' 
  | 'overlay'
  | 'card'
  | 'input'
  | 'typography';

/** Issue severity levels */
export type IssueSeverity = 'error' | 'warning' | 'info';

/** Audit check categories */
export type AuditCategory = 'naming' | 'structure' | 'visual' | 'accessibility' | 'variants' | 'metadata';

// ============================================
// Quality Pipeline Types
// ============================================

/** Request payload for component audit */
export interface ComponentAuditRequest {
  component: {
    name: string;
    type: 'COMPONENT' | 'COMPONENT_SET' | 'INSTANCE';
    nodeId: string;
    properties: ComponentPropertyInfo[];
    variants: VariantInfo[];
    children: ChildNodeInfo[];
    // Additional fields for server-side audit
    hasAutoLayout?: boolean;
    hasStates?: boolean;
    width?: number;
    height?: number;
    childCount?: number;
  };
  existingDescription?: string;
  tokens?: DesignToken[];
  variants?: VariantInfo[];
  checks?: AuditCategory[];
  auditResult?: AuditResult;
  metadataAnalysis?: MetadataGapAnalysis;
  /** Generated metadata from Phase 3, used when generating report */
  generatedMetadata?: GeneratedMetadata;
}

export interface ComponentPropertyInfo {
  name: string;
  type: 'TEXT' | 'BOOLEAN' | 'VARIANT' | 'INSTANCE_SWAP';
  defaultValue?: string | boolean;
  variantOptions?: string[];
}

export interface VariantInfo {
  name: string;
  nodeId: string;
  properties: Record<string, string>;
  description?: string;
  hasDescription: boolean;
}

export interface ChildNodeInfo {
  name: string;
  type: string;
  nodeId: string;
  properties?: Record<string, unknown>;
}

// ============================================
// Phase 1: Audit Types
// ============================================

export interface AuditResult {
  score: number;

  categories: {
    naming: CategoryScore;
    structure: CategoryScore;
    visual: CategoryScore;
    accessibility: CategoryScore;
    variants: CategoryScore;
  };

  issues: AuditIssue[];
  suggestions: string[];
  blockers: string[];

  // Server-computed classification (single source of truth)
  level?: AtomicLevel;           // Atomic design level
  destinationPath?: string;      // Export destination path
}

export interface CategoryScore {
  score: number;
  weight: number;
  passed: number;
  failed: number;
  warnings: number;
  checks: CheckResult[];
}

export interface CheckResult {
  name: string;
  passed: boolean;
  message: string;
  severity?: IssueSeverity;
}

export interface AuditIssue {
  severity: IssueSeverity;
  category: AuditCategory;
  message: string;
  location: string;
  suggestion: string;
  autoFixable: boolean;
  nodeId?: string;  // Figma node ID for "Go to" navigation
}

// ============================================
// Phase 2: Metadata Analysis Types
// ============================================

export interface MetadataGapAnalysis {
  componentName: string;
  completenessScore: number;
  
  componentSetLevel: {
    present: string[];
    missing: string[];
    incomplete: string[];
  };
  
  variantLevel: {
    total: number;
    withDescription: number;
    missingDescription: VariantInfo[];
  };
  
  propertyLevel: {
    total: number;
    withDescription: number;
    missingDescription: string[];
  };
  
  accessibilityMetadata: {
    hasAriaLabel: boolean;
    hasA11yNotes: boolean;
    hasFocusStates: boolean;
    hasContrastInfo: boolean;
  };
}

// ============================================
// Phase 3: Generated Metadata Types
// ============================================

export interface GeneratedMetadata {
  // Component Set Description
  description: string;
  
  // Structured metadata
  tags: string[];
  notes: string;
  ariaLabel: string;
  category: ComponentCategory;
  level: AtomicLevel;
  priority: 'critical' | 'high' | 'medium' | 'low';
  
  // Analytics & Testing
  analytics: string;
  testId: string;
  
  // Tokens extracted
  tokens: {
    colors: string[];
    spacing: string[];
    typography: string[];
    radius: string[];
    shadows: string[];
    borders: string[];
  };
  
  // States
  states: {
    default: string;
    hover: string;
    focus: string;
    active: string;
    disabled: string;
    loading?: string;
    error?: string;
    success?: string;
  };
  
  // Variant descriptions
  variants: Record<string, string>;
  
  // Usage guidelines
  dos: string[];
  donts: string[];
  
  // Accessibility
  a11y: string[];
  
  // Related components
  related: string[];
  
  // Technical specs
  specs: {
    minWidth?: string;
    minHeight?: string;
    touchTarget?: string;
    contrast?: string;
  };
  
  // Full formatted output (ready to paste into Figma)
  formattedDescription: string;
  
  // Variant-level descriptions
  variantDescriptions: Record<string, string>;
}

// ============================================
// Phase 4: Quality Report Types
// ============================================

export interface ComponentQualityReport {
  // Header
  componentName: string;
  componentType: 'COMPONENT' | 'COMPONENT_SET' | 'INSTANCE';
  generatedAt: Date;
  
  // Scores
  overallScore: number;
  scores: {
    consistency: number;
    metadata: number;
    accessibility: number;
    structure: number;
  };
  
  // Status
  exportReady: boolean;
  blockers: string[];
  
  // Details
  audit: AuditResult;
  metadata: MetadataGapAnalysis;
  
  // Auto-generated content
  suggestedMetadata: GeneratedMetadata;
  
  // Action items
  requiredFixes: ActionItem[];
  recommendedFixes: ActionItem[];
}

export interface ActionItem {
  priority: 'critical' | 'high' | 'medium' | 'low';
  category: AuditCategory;
  issue: string;
  howToFix: string;
  location: string;
  autoFixAvailable: boolean;
}

// ============================================
// Export Payload Types
// ============================================

export interface ExportPayload {
  component: {
    name: string;
    type: string;
    description: string;
  };
  
  metadata: GeneratedMetadata;
  
  tokens: DesignToken[];
  
  content: Record<string, string>;
  
  qualityCertification: {
    score: number;
    auditedAt: Date;
    passedChecks: string[];
  };
  
  figma: {
    fileKey: string;
    nodeId: string;
    exportedAt: Date;
  };
}

// ============================================
// Component conversion status (legacy)
// ============================================

/** Component conversion status */
export type ConversionStatus = 
  | 'pending' 
  | 'analyzing' 
  | 'planned' 
  | 'approved' 
  | 'enriching' 
  | 'converting' 
  | 'sending' 
  | 'completed' 
  | 'failed';

/** Design token categories */
export type TokenCategory = 
  | 'color' 
  | 'typography' 
  | 'spacing' 
  | 'borderRadius' 
  | 'shadow' 
  | 'animation'
  | 'size';

// ============================================
// Figma Node Analysis
// ============================================

export interface FigmaNodeInfo {
  id: string;
  name: string;
  type: NodeType;
  children?: FigmaNodeInfo[];
  properties: FigmaNodeProperties;
  variantProperties?: Record<string, string>;
  isComponentSet?: boolean;
  isInstance?: boolean;
  mainComponentId?: string;
}

export interface FigmaNodeProperties {
  // Layout
  width?: number;
  height?: number;
  x?: number;
  y?: number;
  
  // Auto Layout
  layoutMode?: 'NONE' | 'HORIZONTAL' | 'VERTICAL';
  primaryAxisSizingMode?: 'FIXED' | 'AUTO';
  counterAxisSizingMode?: 'FIXED' | 'AUTO';
  paddingLeft?: number;
  paddingRight?: number;
  paddingTop?: number;
  paddingBottom?: number;
  itemSpacing?: number;
  
  // Appearance
  fills?: readonly Paint[];
  strokes?: readonly Paint[];
  strokeWeight?: number;
  cornerRadius?: number;
  effects?: readonly Effect[];
  opacity?: number;
  
  // Typography (for text nodes)
  fontSize?: number;
  fontName?: FontName;
  fontWeight?: number;
  lineHeight?: LineHeight;
  letterSpacing?: LetterSpacing;
  textAlignHorizontal?: string;
  textAlignVertical?: string;
  textDecoration?: string;
  
  // Content
  characters?: string;
}

// ============================================
// Component Classification
// ============================================

export interface ComponentClassification {
  level: AtomicLevel;
  confidence: number; // 0-1
  reasoning: string;
  suggestedName: string;
  category: string; // e.g., 'button', 'input', 'card', 'header'
}

export interface DependencyInfo {
  nodeId: string;
  nodeName: string;
  level: AtomicLevel;
  isExternal: boolean; // From another file/library
}

// ============================================
// Work Plan
// ============================================

export interface WorkPlanStep {
  id: string;
  order: number;
  action: 'extract_tokens' | 'analyze_variants' | 'map_props' | 'generate_code' | 'create_stories';
  description: string;
  estimatedTokens: number;
  status: 'pending' | 'in_progress' | 'completed' | 'skipped';
  result?: unknown;
}

export interface ComponentWorkPlan {
  componentId: string;
  componentName: string;
  classification: ComponentClassification;
  dependencies: DependencyInfo[];
  steps: WorkPlanStep[];
  totalEstimatedTokens: number;
  createdAt: Date;
  approvedAt?: Date;
  approvedBy?: string;
}

// ============================================
// Queue System
// ============================================

export interface QueueItem {
  id: string;
  nodeId: string;
  nodeName: string;
  priority: number; // Lower = higher priority
  status: ConversionStatus;
  workPlan?: ComponentWorkPlan;
  enrichedData?: EnrichedComponentData;
  designTokens?: DesignToken[];
  error?: string;
  addedAt: Date;
  startedAt?: Date;
  completedAt?: Date;
}

export interface ConversionQueue {
  items: QueueItem[];
  currentIndex: number;
  isProcessing: boolean;
  isPaused: boolean;
}

// ============================================
// Design Tokens
// ============================================

export interface DesignToken {
  name: string;
  value: string | number;
  category: TokenCategory;
  rawValue?: unknown; // Original Figma value
  cssVariable?: string;
  tailwindClass?: string;
  semanticName?: string;
}

export interface TokenSet {
  colors: DesignToken[];
  typography: DesignToken[];
  spacing: DesignToken[];
  borderRadius: DesignToken[];
  shadows: DesignToken[];
  animations: DesignToken[];
}

// ============================================
// Enriched Component Data
// ============================================

export interface PropDefinition {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'enum' | 'node' | 'function';
  required: boolean;
  defaultValue?: unknown;
  enumValues?: string[];
  description: string;
  mappedFrom?: string; // Figma property it maps from
}

export interface VariantDefinition {
  name: string;
  options: string[];
  defaultOption: string;
  description: string;
}

export interface EnrichedComponentData {
  componentId: string;
  componentName: string;
  displayName: string;
  description: string;
  
  // Atomic classification
  level: AtomicLevel;
  category: string;
  
  // Props & Variants
  props: PropDefinition[];
  variants: VariantDefinition[];
  
  // Design tokens used
  tokens: DesignToken[];
  
  // States
  states: string[]; // e.g., ['default', 'hover', 'active', 'disabled', 'focused']
  
  // Responsive
  breakpoints: string[];
  
  // Dependencies
  dependencies: {
    internal: string[]; // Component IDs within the same system
    external: string[]; // External library components
  };
  
  // Accessibility
  accessibility: {
    role?: string;
    ariaLabel?: string;
    keyboardInteraction?: string[];
  };
  
  // Metadata from Figma description field
  tags?: string[];
  notes?: string;
  customFields?: Record<string, string>;
  
  // Meta
  figmaUrl?: string;
  createdAt: Date;
  version: string;
}

// ============================================
// MCP Communication
// ============================================

export interface MCPRequest {
  jsonrpc: '2.0';
  id: string | number;
  method: string;
  params?: unknown;
}

export interface MCPResponse {
  jsonrpc: '2.0';
  id: string | number;
  result?: unknown;
  error?: MCPError;
}

export interface MCPError {
  code: number;
  message: string;
  data?: unknown;
}

export interface MCPToolCall {
  name: string;
  arguments: Record<string, unknown>;
}

export interface ComponentPayload {
  component: EnrichedComponentData;
  tokens: DesignToken[];
  figmaMetadata: {
    fileKey: string;
    nodeId: string;
    exportedAt: Date;
    pluginVersion: string;
  };
}

// ============================================
// Plugin State
// ============================================

export interface PluginState {
  isConnected: boolean;
  mcpEndpoint: string;
  queue: ConversionQueue;
  selectedNodes: FigmaNodeInfo[];
  currentWorkPlan?: ComponentWorkPlan;
  settings: PluginSettings;
  history: ConversionHistoryItem[];
}

export interface PluginSettings {
  mcpEndpoint: string;
  autoClassify: boolean;
  defaultPriority: number;
  tokenNamingConvention: 'kebab-case' | 'camelCase' | 'snake_case';
  outputFormat: 'react' | 'vue' | 'html';
  includeStorybook: boolean;
  includeTests: boolean;
}

export interface ConversionHistoryItem {
  id: string;
  componentName: string;
  status: 'success' | 'failed';
  timestamp: Date;
  errorMessage?: string;
}

// ============================================
// UI Messages
// ============================================

export type PluginMessage = 
  | { type: 'SELECTION_CHANGED'; nodes: FigmaNodeInfo[] }
  | { type: 'ANALYSIS_COMPLETE'; classifications: ComponentClassification[] }
  | { type: 'WORK_PLAN_CREATED'; plan: ComponentWorkPlan }
  | { type: 'QUEUE_UPDATED'; queue: ConversionQueue }
  | { type: 'STATUS_CHANGED'; itemId: string; status: ConversionStatus }
  | { type: 'MCP_CONNECTED'; endpoint: string }
  | { type: 'MCP_DISCONNECTED'; reason?: string }
  | { type: 'MCP_RESPONSE'; response: MCPResponse }
  | { type: 'ERROR'; message: string; details?: unknown }
  | { type: 'TOKENS_EXTRACTED'; tokens: DesignToken[] }
  | { type: 'COMPONENT_SENT'; componentId: string; success: boolean }
  | { type: 'AUTH_SUCCESS'; user: { id: string; email: string; name: string; tenantId: string; roles: string[] } }
  | { type: 'AUTH_LOGOUT' }
  | { type: 'AUTH_RESTORED'; user: { id: string; email: string; name: string; tenantId: string; roles: string[] } | null }
  | { type: 'CONTENT_EXTRACTED'; content: string; format: string; filename: string; components: ContentExtractedSummary[] }
  | { type: 'CONTENT_PREVIEW'; components: ContentPreviewComponent[] };

export interface ContentExtractedSummary {
  name: string;
  type: string;
  propertyCount: number;
  variantCount: number;
  contentKeys: string[];
}

export interface ContentPreviewComponent {
  name: string;
  type: string;
  description?: string;
  properties: any[];
  variantCount: number;
  defaultContent: Record<string, string>;
}

export type UIMessage =
  | { type: 'INIT' }
  | { type: 'ANALYZE_SELECTION' }
  | { type: 'ADD_TO_QUEUE'; nodeIds: string[] }
  | { type: 'APPROVE_PLAN'; planId: string }
  | { type: 'REJECT_PLAN'; planId: string; reason: string }
  | { type: 'PROCESS_QUEUE' }
  | { type: 'PAUSE_QUEUE' }
  | { type: 'RESUME_QUEUE' }
  | { type: 'REMOVE_FROM_QUEUE'; itemId: string }
  | { type: 'REORDER_QUEUE'; itemId: string; newIndex: number }
  | { type: 'CONNECT_MCP'; endpoint: string }
  | { type: 'DISCONNECT_MCP' }
  | { type: 'UPDATE_SETTINGS'; settings: Partial<PluginSettings> }
  | { type: 'EXPORT_TOKENS'; format: 'css' | 'json' | 'tailwind' }
  | { type: 'EDIT_METADATA'; itemId: string; metadata: Partial<EnrichedComponentData> }
  | { type: 'LOGIN'; tenantId: string; apiKey: string; backendUrl: string }
  | { type: 'LOGOUT' }
  | { type: 'EXTRACT_CONTENT'; format: 'typescript' | 'json' | 'csv' }
  | { type: 'EXTRACT_CONTENT_PREVIEW' };
