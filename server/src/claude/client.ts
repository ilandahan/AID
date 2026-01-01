/**
 * @file client.ts
 * @description Anthropic Claude API client wrapper.
 * Handles API calls for design review operations.
 *
 * @related
 *   - ./prompt-builder.ts - Builds prompts for API calls
 *   - ../tools/design-review.ts - Uses this client
 */

import Anthropic from '@anthropic-ai/sdk';

export interface ClaudeResponse {
  content: string;
  usage: {
    inputTokens: number;
    outputTokens: number;
  };
}

export interface ClaudeClientConfig {
  apiKey?: string;
  model?: string;
  maxTokens?: number;
}

const DEFAULT_MODEL = 'claude-sonnet-4-20250514';
const DEFAULT_MAX_TOKENS = 4096;

export class ClaudeClient {
  private client: Anthropic;
  private model: string;
  private maxTokens: number;

  constructor(config: ClaudeClientConfig = {}) {
    const apiKey = config.apiKey || process.env.ANTHROPIC_API_KEY;

    if (!apiKey) {
      throw new Error('ANTHROPIC_API_KEY is required');
    }

    this.client = new Anthropic({ apiKey });
    this.model = config.model || DEFAULT_MODEL;
    this.maxTokens = config.maxTokens || DEFAULT_MAX_TOKENS;
  }

  /**
   * Send a message to Claude and get a response
   */
  async chat(prompt: string): Promise<ClaudeResponse> {
    try {
      const message = await this.client.messages.create({
        model: this.model,
        max_tokens: this.maxTokens,
        messages: [
          {
            role: 'user',
            content: prompt
          }
        ]
      });

      // Extract text content from response
      const textContent = message.content.find(block => block.type === 'text');
      const content = textContent && 'text' in textContent ? textContent.text : '';

      return {
        content,
        usage: {
          inputTokens: message.usage.input_tokens,
          outputTokens: message.usage.output_tokens
        }
      };
    } catch (error) {
      console.error('Claude API error:', error);
      throw error;
    }
  }

  /**
   * Send a message and parse JSON response
   */
  async chatJSON<T>(prompt: string): Promise<T> {
    const response = await this.chat(prompt);

    try {
      // Try to extract JSON from the response
      let jsonStr = response.content.trim();

      // Remove markdown code blocks if present
      const jsonMatch = jsonStr.match(/```(?:json)?\s*([\s\S]*?)```/);
      if (jsonMatch) {
        jsonStr = jsonMatch[1].trim();
      }

      // Parse and return
      return JSON.parse(jsonStr) as T;
    } catch (error) {
      console.error('Failed to parse JSON response:', response.content);
      throw new Error(`Invalid JSON response from Claude: ${error}`);
    }
  }

  /**
   * Audit a component for quality issues
   */
  async auditComponent(prompt: string): Promise<AuditResult> {
    return this.chatJSON<AuditResult>(prompt);
  }

  /**
   * Analyze metadata completeness
   */
  async analyzeMetadata(prompt: string): Promise<MetadataAnalysis> {
    return this.chatJSON<MetadataAnalysis>(prompt);
  }

  /**
   * Generate metadata suggestions
   */
  async generateMetadata(prompt: string): Promise<GeneratedMetadata> {
    return this.chatJSON<GeneratedMetadata>(prompt);
  }

  /**
   * Generate formatted output (returns raw text, not JSON)
   */
  async generateFormatted(prompt: string): Promise<string> {
    const response = await this.chat(prompt);
    return response.content.trim();
  }

  /**
   * Generate complete quality report
   */
  async generateReport(prompt: string): Promise<QualityReport> {
    return this.chatJSON<QualityReport>(prompt);
  }
}

// Type definitions for Claude responses
export interface AuditResult {
  scores: {
    overall: number;
    naming: number;
    structure: number;
    visual: number;
    accessibility: number;
    metadata: number;
  };
  issues: AuditIssue[];
  exportReady: boolean;
  blockers: string[];
}

export interface AuditIssue {
  id: string;
  category: 'naming' | 'structure' | 'visual' | 'accessibility' | 'metadata';
  severity: 'error' | 'warning' | 'info';
  message: string;
  location: string;
  suggestion: string;
  autoFixable: boolean;
}

export interface MetadataAnalysis {
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
    missingDescription: Array<{ name: string; properties: Record<string, string> }>;
  };
  recommendations: string[];
}

export interface GeneratedMetadata {
  description: string;
  tags: string[];
  notes: string;
  ariaLabel?: string;
  category: string;
  level: string;
  priority: string;
  tokens: {
    colors: string[];
    spacing: string[];
    typography: string[];
  };
  states: Record<string, string>;
  variants: Record<string, string>;
  dos: string[];
  donts: string[];
  a11y: string[];
  formattedDescription: string;
}

export interface QualityReport {
  component: Record<string, unknown>;
  tokens: Array<Record<string, unknown>>;
  figmaMetadata: Record<string, unknown>;
  qualityReport: {
    overallScore: number;
    scores: Record<string, number>;
    exportReady: boolean;
    blockers: string[];
    issues: AuditIssue[];
    actionItems: Array<{
      priority: 'critical' | 'high' | 'medium' | 'low';
      issue: string;
      howToFix: string;
    }>;
  };
  generatedMetadata: GeneratedMetadata;
  formattedForFigma: string;
}

// Singleton instance
let clientInstance: ClaudeClient | null = null;

export function getClaudeClient(config?: ClaudeClientConfig): ClaudeClient {
  if (!clientInstance) {
    clientInstance = new ClaudeClient(config);
  }
  return clientInstance;
}

export function resetClaudeClient(): void {
  clientInstance = null;
}
