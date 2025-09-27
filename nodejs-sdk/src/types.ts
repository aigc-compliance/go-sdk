/**
 * Type definitions for AIGC Compliance Node.js SDK
 */

// Core types
export type Plan = 'free' | 'starter' | 'pro' | 'enterprise';
export type Region = 'eu' | 'cn';
export type MetadataLevel = 'basic' | 'detailed';

// Compliance metadata structures
export interface ComplianceMetadata {
  ai_generated_probability: number;
  content_type: string;
  processing_timestamp: string;
  gdpr_compliant: boolean;
}

export interface ChinaComplianceMetadata extends ComplianceMetadata {
  cybersecurity_law_compliance: boolean;
  watermark_info: WatermarkInfo;
  content_labeling: ContentLabeling;
}

export interface WatermarkInfo {
  text?: string;
  logo_applied: boolean;
  position: string;
  transparency: number;
}

export interface ContentLabeling {
  category: string;
  compliance_level: string;
  regulatory_notes: string;
}

// API Response types - EXACT match with documentation
export interface ComplianceResponse {
  status: 'success';
  region_applied: 'EU' | 'CN';
  timestamp: string;
  file_hash: string;
  original_filename: string;
  compliance_metadata: ComplianceMetadata | ChinaComplianceMetadata;
  download_url: string;
  download_expires_at: string;
  processed_image_base64?: string; // Only if include_base64=true
  processing_time_ms: number;
  credits_used: number;
  credits_remaining: number;
  _rateLimitInfo?: RateLimitInfo;
}

export interface BatchItem {
  id: string;
  image: Buffer;
  custom_metadata?: Record<string, any>;
}

export interface BatchResult {
  id: string;
  is_ai_generated: boolean;
  confidence: number;
  watermark_applied: boolean;
  processing_time_ms: number;
  compliance_metadata: ComplianceMetadata | ChinaComplianceMetadata;
  error?: string;
}

export interface BatchResponse {
  batch_id: string;
  total_processed: number;
  successful: number;
  failed: number;
  processing_time_ms: number;
  results: BatchResult[];
  _rateLimitInfo?: RateLimitInfo;
}

export interface AnalyticsData {
  total_requests: number;
  ai_generated_detected: number;
  watermarks_applied: number;
  quota_used: number;
  quota_limit: number;
  period_start: string;
  period_end: string;
}

export interface AnalyticsResponse {
  current_period: AnalyticsData;
  previous_period: AnalyticsData;
  growth_rate: number;
}

export interface WebhookEventData {
  event_id: string;
  timestamp: string;
  data: Record<string, any>;
}

export interface WebhookEvent {
  event: 'compliance.completed' | 'batch.finished' | 'quota.exceeded';
  data: WebhookEventData;
}

export interface WebhookRegistration {
  webhook_id: string;
  url: string;
  events: string[];
  secret?: string;
  created_at: string;
}

export interface RateLimitInfo {
  limit: number;
  remaining: number;
  reset: Date;
}

export interface QuotaInfo {
  credits_remaining: number;
  credits_used: number;
  quota_limit: number;
  reset_date: string;
}

// Health Check Response - exact match with documentation
export interface HealthResponse {
  status: 'healthy' | 'unhealthy';
  timestamp: string;
  version: string;
  services: {
    image_processor: 'operational' | 'degraded' | 'down';
    c2pa_handler: 'operational' | 'degraded' | 'down';
    metadata_injector: 'operational' | 'degraded' | 'down';
    redis: 'connected' | 'disconnected';
  };
}

// Client configuration
export interface ClientConfig {
  apiKey: string;
  baseURL?: string;
  timeout?: number;
  maxRetries?: number;
  userAgent?: string;
}

// Request options
export interface ComplyOptions {
  region: 'EU' | 'CN'; // REQUIRED per documentation
  watermark_text?: string;
  watermark_position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left';
  logo_file?: Buffer | string; // Logo file for watermark
  include_base64?: boolean; // Include base64 in response
  save_to_disk?: boolean; // Save processed file to disk
  custom_metadata?: Record<string, any>;
}

export interface TagOptions {
  region?: Region;
  watermarkText?: string;
  watermarkLogo?: boolean;
  metadataLevel?: MetadataLevel;
}

export interface BatchOptions {
  region?: Region;
  watermarkLogo?: boolean;
  metadataLevel?: MetadataLevel;
}

export interface AnalyticsOptions {
  period?: 'day' | 'week' | 'month';
  startDate?: string;
  endDate?: string;
}

export interface WebhookOptions {
  url: string;
  events: string[];
  secret?: string;
}

// Error types
export interface ErrorResponse {
  message: string;
  code?: string;
  details?: Record<string, any>;
}

export class ComplianceAPIError extends Error {
  public readonly statusCode?: number;
  public readonly responseData?: ErrorResponse;

  constructor(message: string, statusCode?: number, responseData?: ErrorResponse) {
    super(message);
    this.name = 'ComplianceAPIError';
    this.statusCode = statusCode;
    this.responseData = responseData;
  }
}

export class ComplianceAuthenticationError extends ComplianceAPIError {
  constructor(message = 'Invalid or missing API key', responseData?: ErrorResponse) {
    super(message, 401, responseData);
    this.name = 'ComplianceAuthenticationError';
  }
}

export class ComplianceRateLimitError extends ComplianceAPIError {
  public readonly retryAfter?: number;

  constructor(message = 'Rate limit exceeded', retryAfter?: number, responseData?: ErrorResponse) {
    super(message, 429, responseData);
    this.name = 'ComplianceRateLimitError';
    this.retryAfter = retryAfter;
  }
}

export class ComplianceQuotaExceededError extends ComplianceAPIError {
  public readonly quotaLimit?: number;
  public readonly quotaUsed?: number;

  constructor(
    message = 'API quota exceeded',
    quotaLimit?: number,
    quotaUsed?: number,
    responseData?: ErrorResponse
  ) {
    super(message, 402, responseData);
    this.name = 'ComplianceQuotaExceededError';
    this.quotaLimit = quotaLimit;
    this.quotaUsed = quotaUsed;
  }
}

export class ComplianceValidationError extends ComplianceAPIError {
  public readonly fieldErrors?: Record<string, string>;

  constructor(
    message = 'Request validation failed',
    fieldErrors?: Record<string, string>,
    responseData?: ErrorResponse
  ) {
    super(message, 422, responseData);
    this.name = 'ComplianceValidationError';
    this.fieldErrors = fieldErrors;
  }
}

export class ComplianceServerError extends ComplianceAPIError {
  constructor(message = 'Internal server error', responseData?: ErrorResponse) {
    super(message, 500, responseData);
    this.name = 'ComplianceServerError';
  }
}

export class ComplianceNetworkError extends ComplianceAPIError {
  public readonly originalError?: Error;

  constructor(message = 'Network request failed', originalError?: Error) {
    super(message);
    this.name = 'ComplianceNetworkError';
    this.originalError = originalError;
  }
}