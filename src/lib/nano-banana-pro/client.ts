/**
 * Nano Banana Pro API Client
 * Supports Google AI Studio, Vertex AI, and AI/ML API providers
 */

import {
  NanoBananaProConfig,
  GenerationConfig,
  GenerationResponse,
  GeneratedImage,
  NanoBananaProError,
  GoogleGenerateRequest,
  GoogleGenerateResponse,
  AimlApiGenerateRequest,
  AimlApiGenerateResponse,
  SafetySetting,
  VertexAIConfig,
} from './types';

// ============================================
// Constants
// ============================================

const GOOGLE_API_BASE = 'https://generativelanguage.googleapis.com/v1beta';
const AIML_API_BASE = 'https://api.aimlapi.com/v1';

/**
 * Model IDs for image generation
 * - gemini-2.0-flash-exp: Supports native image generation (experimental)
 * - Supports text rendering and multimodal output
 */
const MODEL_IDS = {
  google: 'gemini-2.0-flash-exp',
  aimlapi: 'google/gemini-2.0-flash-exp',
  vertex: 'gemini-2.0-flash-exp',
} as const;

/**
 * Default generation settings optimized for UI/diagram generation
 */
const DEFAULT_GENERATION_CONFIG = {
  temperature: 0.7,        // Balanced creativity (recommended)
  candidateCount: 1,
} as const;

const DEFAULT_CONFIG: Partial<NanoBananaProConfig> = {
  timeout: 60000,
  retries: 3,
};

// ============================================
// Client Class
// ============================================

export class NanoBananaProClient {
  private config: NanoBananaProConfig;

  constructor(config: NanoBananaProConfig) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.validateConfig();
  }

  private validateConfig(): void {
    if (!['google', 'aimlapi', 'vertex'].includes(this.config.provider)) {
      throw new NanoBananaProError(
        'Invalid provider. Use "google", "aimlapi", or "vertex"',
        'INVALID_PROVIDER'
      );
    }

    if (this.config.provider === 'vertex') {
      if (!this.config.vertex?.projectId || !this.config.vertex?.location) {
        throw new NanoBananaProError(
          'Vertex AI requires projectId and location',
          'MISSING_VERTEX_CONFIG'
        );
      }
    } else if (!this.config.apiKey) {
      throw new NanoBananaProError(
        'API key is required for google/aimlapi providers',
        'MISSING_API_KEY'
      );
    }
  }

  // ============================================
  // Main Generation Methods
  // ============================================

  /**
   * Generate images from a text prompt
   */
  async generateFromText(
    prompt: string,
    options?: GenerationConfig
  ): Promise<GenerationResponse> {
    if (this.config.provider === 'vertex') {
      return this.generateWithVertex(prompt, options);
    }
    if (this.config.provider === 'google') {
      return this.generateWithGoogle(prompt, options);
    }
    return this.generateWithAimlApi(prompt, options);
  }

  /**
   * Generate images from a reference image with editing instructions
   */
  async editImage(
    imageBase64: string,
    instruction: string,
    options?: GenerationConfig
  ): Promise<GenerationResponse> {
    if (this.config.provider === 'aimlapi') {
      throw new NanoBananaProError(
        'Image editing is only supported with Google/Vertex providers',
        'UNSUPPORTED_OPERATION'
      );
    }
    if (this.config.provider === 'vertex') {
      return this.editWithVertex(imageBase64, instruction, options);
    }
    return this.editWithGoogle(imageBase64, instruction, options);
  }

  /**
   * Transform a wireframe sketch into a high-fidelity UI design
   */
  async wireframeToUI(
    sketchBase64: string,
    description: string,
    options?: GenerationConfig
  ): Promise<GenerationResponse> {
    const prompt = this.buildWireframePrompt(description);
    return this.editImage(sketchBase64, prompt, options);
  }

  // ============================================
  // Google API Implementation
  // ============================================

  private async generateWithGoogle(
    prompt: string,
    options?: GenerationConfig
  ): Promise<GenerationResponse> {
    const startTime = Date.now();
    const url = `${this.getBaseUrl()}/models/${MODEL_IDS.google}:generateContent`;

    const request: GoogleGenerateRequest = {
      contents: [
        {
          role: 'user',
          parts: [{ text: prompt }],
        },
      ],
      generationConfig: {
        responseModalities: ['IMAGE'],
        candidateCount: options?.numImages || DEFAULT_GENERATION_CONFIG.candidateCount,
        temperature: options?.temperature ?? DEFAULT_GENERATION_CONFIG.temperature,
      },
      // System instruction for technical diagrams and professional visuals
      systemInstruction: {
        parts: [{
          text: `You are an expert technical illustrator and information designer specializing in:
1. Research presentation slides - clean, data-driven visuals with charts and insights
2. Data schemas and flowcharts - clear ERDs, DFDs, and process flows with proper notation
3. System architecture diagrams - professional cloud/microservices diagrams with standard icons

Generate clean, professional diagrams with:

TEXT RENDERING REQUIREMENTS (CRITICAL):
- ALL text MUST be LARGE and clearly readable (minimum 16pt equivalent)
- Use BOLD, simple sans-serif fonts (Arial, Helvetica style)
- HIGH CONTRAST: Black text (#000000) on white/light backgrounds
- NO small text - if text won't fit, use abbreviations or split into multiple lines
- Leave generous padding around all text labels
- Never overlap text with other elements
- Titles should be at least 24pt equivalent

DIAGRAM REQUIREMENTS:
- Standard technical notation (boxes, arrows, connectors)
- Consistent color coding by category
- Clear visual hierarchy and logical flow
- White or light backgrounds for readability
- Professional presentation quality
- Adequate spacing between all elements`
        }]
      },
    };

    const response = await this.fetchWithRetry<GoogleGenerateResponse>(
      url,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-goog-api-key': this.config.apiKey!,
        },
        body: JSON.stringify(request),
      }
    );

    return this.parseGoogleResponse(response, startTime);
  }

  private async editWithGoogle(
    imageBase64: string,
    instruction: string,
    options?: GenerationConfig
  ): Promise<GenerationResponse> {
    const startTime = Date.now();
    const url = `${this.getBaseUrl()}/models/${MODEL_IDS.google}:generateContent`;

    const request: GoogleGenerateRequest = {
      contents: [
        {
          role: 'user',
          parts: [
            {
              inlineData: {
                mimeType: 'image/png',
                data: imageBase64,
              },
            },
            { text: instruction },
          ],
        },
      ],
      generationConfig: {
        responseModalities: ['IMAGE'],
        candidateCount: options?.numImages || 1,
        temperature: options?.temperature,
      },
    };

    const response = await this.fetchWithRetry<GoogleGenerateResponse>(
      url,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-goog-api-key': this.config.apiKey,
        },
        body: JSON.stringify(request),
      }
    );

    return this.parseGoogleResponse(response, startTime);
  }

  private parseGoogleResponse(
    response: GoogleGenerateResponse,
    startTime: number,
    provider: 'google' | 'vertex' = 'google'
  ): GenerationResponse {
    const images: GeneratedImage[] = [];

    for (const candidate of response.candidates || []) {
      for (const part of candidate.content?.parts || []) {
        if (part.inlineData) {
          images.push({
            base64: part.inlineData.data,
            mimeType: part.inlineData.mimeType,
          });
        }
      }
    }

    if (images.length === 0) {
      throw new NanoBananaProError(
        'No images generated in response',
        'NO_IMAGES_GENERATED'
      );
    }

    return {
      images,
      meta: {
        model: MODEL_IDS[provider],
        processingTime: Date.now() - startTime,
      },
    };
  }

  // ============================================
  // AI/ML API Implementation
  // ============================================

  private async generateWithAimlApi(
    prompt: string,
    options?: GenerationConfig
  ): Promise<GenerationResponse> {
    const startTime = Date.now();
    const url = `${this.getBaseUrl()}/images/generations`;

    const request: AimlApiGenerateRequest = {
      model: MODEL_IDS.aimlapi,
      prompt,
      aspect_ratio: options?.aspectRatio,
      resolution: options?.resolution,
      num_images: options?.numImages,
    };

    const response = await this.fetchWithRetry<AimlApiGenerateResponse>(
      url,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${this.config.apiKey}`,
        },
        body: JSON.stringify(request),
      }
    );

    return this.parseAimlApiResponse(response, startTime);
  }

  private parseAimlApiResponse(
    response: AimlApiGenerateResponse,
    startTime: number
  ): GenerationResponse {
    const images: GeneratedImage[] = (response.data || []).map((item) => ({
      url: item.url,
      base64: item.b64_json || undefined,
      mimeType: 'image/png',
    }));

    if (images.length === 0) {
      throw new NanoBananaProError(
        'No images generated in response',
        'NO_IMAGES_GENERATED'
      );
    }

    return {
      images,
      meta: {
        model: MODEL_IDS.aimlapi,
        processingTime: Date.now() - startTime,
        creditsUsed: response.meta?.usage?.credits_used,
      },
    };
  }

  // ============================================
  // Vertex AI Implementation
  // ============================================

  private getVertexBaseUrl(): string {
    const { projectId, location } = this.config.vertex!;
    return `https://${location}-aiplatform.googleapis.com/v1/projects/${projectId}/locations/${location}/publishers/google/models`;
  }

  private async getVertexAccessToken(): Promise<string> {
    // If access token is provided directly, use it
    if (this.config.vertex?.accessToken) {
      return this.config.vertex.accessToken;
    }

    // Try to get token from gcloud CLI (Application Default Credentials)
    try {
      const { execSync } = await import('child_process');
      const token = execSync('gcloud auth print-access-token', {
        encoding: 'utf-8',
      }).trim();
      return token;
    } catch {
      throw new NanoBananaProError(
        'Failed to get access token. Run "gcloud auth login" or provide accessToken in config',
        'AUTH_ERROR'
      );
    }
  }

  private async generateWithVertex(
    prompt: string,
    options?: GenerationConfig
  ): Promise<GenerationResponse> {
    const startTime = Date.now();
    const accessToken = await this.getVertexAccessToken();
    const url = `${this.getVertexBaseUrl()}/${MODEL_IDS.vertex}:generateContent`;

    const request: GoogleGenerateRequest = {
      contents: [
        {
          role: 'user',
          parts: [{ text: prompt }],
        },
      ],
      generationConfig: {
        responseModalities: ['IMAGE'],
        candidateCount: options?.numImages || DEFAULT_GENERATION_CONFIG.candidateCount,
        temperature: options?.temperature ?? DEFAULT_GENERATION_CONFIG.temperature,
      },
      // System instruction for technical diagrams and professional visuals
      systemInstruction: {
        parts: [{
          text: `You are an expert technical illustrator and information designer specializing in:
1. Research presentation slides - clean, data-driven visuals with charts and insights
2. Data schemas and flowcharts - clear ERDs, DFDs, and process flows with proper notation
3. System architecture diagrams - professional cloud/microservices diagrams with standard icons

Generate clean, professional diagrams with:

TEXT RENDERING REQUIREMENTS (CRITICAL):
- ALL text MUST be LARGE and clearly readable (minimum 16pt equivalent)
- Use BOLD, simple sans-serif fonts (Arial, Helvetica style)
- HIGH CONTRAST: Black text (#000000) on white/light backgrounds
- NO small text - if text won't fit, use abbreviations or split into multiple lines
- Leave generous padding around all text labels
- Never overlap text with other elements
- Titles should be at least 24pt equivalent

DIAGRAM REQUIREMENTS:
- Standard technical notation (boxes, arrows, connectors)
- Consistent color coding by category
- Clear visual hierarchy and logical flow
- White or light backgrounds for readability
- Professional presentation quality
- Adequate spacing between all elements`
        }]
      },
    };

    const response = await this.fetchWithRetry<GoogleGenerateResponse>(
      url,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify(request),
      }
    );

    return this.parseGoogleResponse(response, startTime, 'vertex');
  }

  private async editWithVertex(
    imageBase64: string,
    instruction: string,
    options?: GenerationConfig
  ): Promise<GenerationResponse> {
    const startTime = Date.now();
    const accessToken = await this.getVertexAccessToken();
    const url = `${this.getVertexBaseUrl()}/${MODEL_IDS.vertex}:generateContent`;

    const request: GoogleGenerateRequest = {
      contents: [
        {
          role: 'user',
          parts: [
            {
              inlineData: {
                mimeType: 'image/png',
                data: imageBase64,
              },
            },
            { text: instruction },
          ],
        },
      ],
      generationConfig: {
        responseModalities: ['IMAGE'],
        candidateCount: options?.numImages || 1,
        temperature: options?.temperature,
      },
    };

    const response = await this.fetchWithRetry<GoogleGenerateResponse>(
      url,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify(request),
      }
    );

    return this.parseGoogleResponse(response, startTime, 'vertex');
  }

  // ============================================
  // Utility Methods
  // ============================================

  private getBaseUrl(): string {
    if (this.config.baseUrl) {
      return this.config.baseUrl;
    }
    if (this.config.provider === 'vertex') {
      return this.getVertexBaseUrl();
    }
    return this.config.provider === 'google' ? GOOGLE_API_BASE : AIML_API_BASE;
  }

  private async fetchWithRetry<T>(
    url: string,
    options: RequestInit,
    attempt = 1
  ): Promise<T> {
    const maxRetries = this.config.retries || 3;

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(
        () => controller.abort(),
        this.config.timeout
      );

      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new NanoBananaProError(
          errorData.error?.message || `HTTP ${response.status}`,
          errorData.error?.code || 'HTTP_ERROR',
          response.status,
          errorData
        );
      }

      return response.json();
    } catch (error) {
      if (error instanceof NanoBananaProError) {
        // Don't retry client errors (4xx)
        if (error.statusCode && error.statusCode >= 400 && error.statusCode < 500) {
          throw error;
        }
      }

      if (attempt < maxRetries) {
        // Exponential backoff
        const delay = Math.min(1000 * Math.pow(2, attempt - 1), 10000);
        await new Promise((resolve) => setTimeout(resolve, delay));
        return this.fetchWithRetry<T>(url, options, attempt + 1);
      }

      if (error instanceof NanoBananaProError) {
        throw error;
      }

      throw new NanoBananaProError(
        error instanceof Error ? error.message : 'Unknown error',
        'FETCH_ERROR'
      );
    }
  }

  private buildWireframePrompt(description: string): string {
    return `Transform this wireframe into a polished, high-fidelity UI mockup.

${description}

Requirements:
- Modern iOS 18 / Material Design 3 aesthetic
- Rounded corners (12px), subtle shadows
- Clear text rendering with proper hierarchy
- Consistent 8px grid spacing
- Professional color palette
- Production-ready quality`;
  }

  // ============================================
  // Safety Settings
  // ============================================

  /**
   * Generate with custom safety settings (Google API only)
   */
  async generateWithSafety(
    prompt: string,
    safetySettings: SafetySetting[],
    options?: GenerationConfig
  ): Promise<GenerationResponse> {
    if (this.config.provider !== 'google') {
      throw new NanoBananaProError(
        'Custom safety settings only supported with Google provider',
        'UNSUPPORTED_OPERATION'
      );
    }

    const startTime = Date.now();
    const url = `${this.getBaseUrl()}/models/${MODEL_IDS.google}:generateContent`;

    const request: GoogleGenerateRequest = {
      contents: [
        {
          role: 'user',
          parts: [{ text: prompt }],
        },
      ],
      generationConfig: {
        responseModalities: ['IMAGE'],
        candidateCount: options?.numImages || 1,
        temperature: options?.temperature,
      },
      safetySettings,
    };

    const response = await this.fetchWithRetry<GoogleGenerateResponse>(
      url,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-goog-api-key': this.config.apiKey,
        },
        body: JSON.stringify(request),
      }
    );

    return this.parseGoogleResponse(response, startTime);
  }
}
