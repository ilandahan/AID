/**
 * Nano Banana Pro API Types
 * Google's Gemini 3 Pro Image Generation Model
 */

// ============================================
// Configuration Types
// ============================================

export type ApiProvider = 'google' | 'aimlapi' | 'vertex';

export interface NanoBananaProConfig {
  /** API key for authentication (for google/aimlapi providers) */
  apiKey?: string;
  /** Which API provider to use */
  provider: ApiProvider;
  /** Base URL override (optional) */
  baseUrl?: string;
  /** Default timeout in ms (default: 60000) */
  timeout?: number;
  /** Default retry attempts (default: 3) */
  retries?: number;
  /** Vertex AI specific config */
  vertex?: VertexAIConfig;
}

export interface VertexAIConfig {
  /** Google Cloud Project ID */
  projectId: string;
  /** Google Cloud Location (e.g., 'us-central1') */
  location: string;
  /** Path to service account JSON file (optional if using ADC) */
  serviceAccountPath?: string;
  /** Access token (if already obtained) */
  accessToken?: string;
}

// ============================================
// Request Types
// ============================================

export type AspectRatio =
  | '1:1'
  | '16:9'
  | '9:16'
  | '4:3'
  | '3:4'
  | '3:2'
  | '2:3'
  | '5:4'
  | '4:5'
  | '21:9';

export type Resolution = '1K' | '2K' | '4K';

export type ImageQuality = 'standard' | 'high' | 'highest';

export interface GenerationConfig {
  /** Aspect ratio of generated image */
  aspectRatio?: AspectRatio;
  /** Resolution of generated image */
  resolution?: Resolution;
  /** Number of images to generate (1-4) */
  numImages?: number;
  /** Quality setting */
  quality?: ImageQuality;
  /** Temperature for generation (0.0-1.0) */
  temperature?: number;
  /** Response format */
  responseFormat?: 'url' | 'base64';
}

export interface SafetySetting {
  category:
    | 'HARM_CATEGORY_DANGEROUS_CONTENT'
    | 'HARM_CATEGORY_HATE_SPEECH'
    | 'HARM_CATEGORY_SEXUALLY_EXPLICIT'
    | 'HARM_CATEGORY_HARASSMENT';
  threshold:
    | 'BLOCK_NONE'
    | 'BLOCK_LOW_AND_ABOVE'
    | 'BLOCK_MEDIUM_AND_ABOVE'
    | 'BLOCK_HIGH_AND_ABOVE';
}

// Google API Request
export interface GoogleGenerateRequest {
  contents: Array<{
    role: 'user' | 'model';
    parts: Array<{
      text?: string;
      inlineData?: {
        mimeType: string;
        data: string;
      };
    }>;
  }>;
  generationConfig?: {
    responseMimeType?: string;
    responseModalities?: ('IMAGE' | 'TEXT')[];
    candidateCount?: number;
    temperature?: number;
  };
  safetySettings?: SafetySetting[];
  systemInstruction?: {
    parts: Array<{ text: string }>;
  };
}

// AI/ML API Request
export interface AimlApiGenerateRequest {
  model: 'google/nano-banana-pro' | 'google/gemini-3-pro-image-preview';
  prompt: string;
  aspect_ratio?: AspectRatio;
  resolution?: Resolution;
  num_images?: number;
}

// ============================================
// Response Types
// ============================================

export interface GeneratedImage {
  /** URL to the generated image (if url format) */
  url?: string;
  /** Base64 encoded image data (if base64 format) */
  base64?: string;
  /** MIME type of the image */
  mimeType: string;
  /** Width in pixels */
  width?: number;
  /** Height in pixels */
  height?: number;
}

export interface GenerationResponse {
  /** Array of generated images */
  images: GeneratedImage[];
  /** Generation metadata */
  meta: {
    /** Model used for generation */
    model: string;
    /** Time taken in milliseconds */
    processingTime?: number;
    /** Credits used (if applicable) */
    creditsUsed?: number;
    /** Request ID for tracking */
    requestId?: string;
  };
}

// Google API Response
export interface GoogleGenerateResponse {
  candidates: Array<{
    content: {
      parts: Array<{
        text?: string;
        inlineData?: {
          mimeType: string;
          data: string;
        };
      }>;
      role: string;
    };
    finishReason: string;
    safetyRatings?: Array<{
      category: string;
      probability: string;
    }>;
  }>;
  usageMetadata?: {
    promptTokenCount: number;
    candidatesTokenCount: number;
    totalTokenCount: number;
  };
}

// AI/ML API Response
export interface AimlApiGenerateResponse {
  data: Array<{
    url: string;
    b64_json: string | null;
  }>;
  meta: {
    usage: {
      credits_used: number;
    };
  };
}

// ============================================
// Error Types
// ============================================

export class NanoBananaProError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode?: number,
    public details?: unknown
  ) {
    super(message);
    this.name = 'NanoBananaProError';
  }
}

export interface ApiErrorResponse {
  error: {
    code: string;
    message: string;
    status?: number;
    details?: unknown;
  };
}

// ============================================
// Wireframe & Design Specific Types
// ============================================

export type DesignSystem =
  | 'ios18'
  | 'material3'
  | 'fluent'
  | 'ant-design'
  | 'chakra'
  | 'custom';

export type DeviceFrame =
  | 'iphone-16'
  | 'iphone-16-pro'
  | 'iphone-15'
  | 'pixel-9'
  | 'samsung-s24'
  | 'ipad-pro'
  | 'macbook-pro'
  | 'desktop-1920'
  | 'desktop-1440'
  | 'none';

export type WireframeStyle =
  | 'low-fidelity'
  | 'mid-fidelity'
  | 'high-fidelity'
  | 'sketch'
  | 'polished';

export interface WireframeOptions {
  /** Design system to apply */
  designSystem?: DesignSystem;
  /** Device frame to use */
  deviceFrame?: DeviceFrame;
  /** Fidelity level */
  style?: WireframeStyle;
  /** Color scheme */
  colorScheme?: 'light' | 'dark' | 'auto';
  /** Primary color (hex) */
  primaryColor?: string;
  /** Include placeholder images */
  includePlaceholders?: boolean;
  /** Generate component annotations */
  includeAnnotations?: boolean;
}

export interface UIComponentSpec {
  /** Component type */
  type: 'button' | 'input' | 'card' | 'navigation' | 'header' | 'footer' | 'list' | 'modal' | 'form' | 'custom';
  /** Component description */
  description: string;
  /** Position hint */
  position?: 'top' | 'center' | 'bottom' | 'left' | 'right';
  /** Size hint */
  size?: 'small' | 'medium' | 'large' | 'full-width';
}

export interface ScreenSpec {
  /** Screen name/title */
  name: string;
  /** Screen description */
  description: string;
  /** Components in the screen */
  components?: UIComponentSpec[];
  /** User flow context */
  flowContext?: string;
}
