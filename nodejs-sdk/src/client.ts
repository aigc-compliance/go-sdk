/**
 * AIGC Compliance Node.js Client
 * 
 * Official Node.js client for AIGC Compliance API.
 * Provides comprehensive AI content detection and watermarking capabilities.
 */

import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import FormData from 'form-data';
import {
  ClientConfig,
  ComplianceResponse,
  BatchResponse,
  AnalyticsResponse,
  ComplyOptions,

  BatchOptions,
  AnalyticsOptions,
  WebhookOptions,
  WebhookRegistration,
  QuotaInfo,
  HealthResponse,
  BatchItem,
  RateLimitInfo,
  ComplianceAPIError,
  ComplianceAuthenticationError,
  ComplianceRateLimitError,
  ComplianceQuotaExceededError,
  ComplianceValidationError,
  ComplianceServerError,
  ComplianceNetworkError,
  ErrorResponse,
} from './types';

export class ComplianceClient {
  private static readonly DEFAULT_BASE_URL = 'https://api.aigc-compliance.com';
  private static readonly DEFAULT_TIMEOUT = 30000;
  private static readonly DEFAULT_MAX_RETRIES = 3;

  private readonly apiKey: string;
  private readonly baseURL: string;
  private readonly timeout: number;
  private readonly maxRetries: number;
  private readonly httpClient: AxiosInstance;

  /**
   * Initialize AIGC Compliance client
   * 
   * @param config - Client configuration
   * 
   * @example
   * ```typescript
   * import { ComplianceClient } from '@aigc-compliance/sdk';
   * 
   * const client = new ComplianceClient({
   *   apiKey: 'your_api_key_here',
   * });
   * ```
   */
  constructor(config: ClientConfig) {
    if (!config.apiKey) {
      throw new ComplianceAuthenticationError('API key is required');
    }

    this.apiKey = config.apiKey;
    this.baseURL = config.baseURL?.replace(/\/$/, '') || ComplianceClient.DEFAULT_BASE_URL;
    this.timeout = config.timeout || ComplianceClient.DEFAULT_TIMEOUT;
    this.maxRetries = config.maxRetries || ComplianceClient.DEFAULT_MAX_RETRIES;

    this.httpClient = axios.create({
      baseURL: this.baseURL,
      timeout: this.timeout,
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'User-Agent': config.userAgent || '@aigc-compliance/sdk-1.0.0',
      },
    });

    // Add response interceptor for error handling
    this.httpClient.interceptors.response.use(
      (response) => response,
      (error) => this.handleHttpError(error)
    );
  }

  /**
   * Process image for AI content detection and compliance watermarking
   * 
   * @param image - Image buffer or file path
   * @param options - Processing options
   * @returns Promise with detection results and compliance metadata
   * 
   * @example
   * ```typescript
   * import fs from 'fs';
   * 
   * // From file
   * const image = fs.readFileSync('image.jpg');
   * const result = await client.comply(image, { 
   *   region: 'eu',
   *   watermarkText: 'AI Generated Content' 
   * });
   * 
   * console.log(`AI Generated: ${result.is_ai_generated}`);
   * console.log(`Confidence: ${result.confidence}`);
   * ```
   */
  /**
   * Process an image file for compliance with EU AI Act or China Cybersecurity Law.
   * Accepts multipart/form-data for direct file uploads.
   * 
   * @param file - Image file (PNG, JPG, JPEG, max 10MB) as Buffer or file path
   * @param options - Processing options as defined in documentation
   */
  async comply(file: Buffer | string, options: ComplyOptions): Promise<ComplianceResponse> {
    // Validate required region parameter
    if (!options.region) {
      throw new ComplianceValidationError('region parameter is required. Use "EU" or "CN"');
    }
    
    if (!['EU', 'CN'].includes(options.region)) {
      throw new ComplianceValidationError('Supported regions: EU, CN');
    }

    const fileBuffer = typeof file === 'string' 
      ? await import('fs').then(fs => fs.readFileSync(file))
      : file;

    const formData = new FormData();
    
    // Use 'file' as the field name per documentation
    formData.append('file', fileBuffer, 'image.jpg');
    
    // REQUIRED region parameter
    formData.append('region', options.region);
    
    // Optional parameters as documented
    if (options.watermark_text) {
      formData.append('watermark_text', options.watermark_text);
    }
    
    if (options.watermark_position) {
      formData.append('watermark_position', options.watermark_position);
    }
    
    if (options.logo_file) {
      const logoBuffer = typeof options.logo_file === 'string' 
        ? await import('fs').then(fs => fs.readFileSync(options.logo_file as string))
        : options.logo_file;
      formData.append('logo_file', logoBuffer, 'logo.png');
    }
    
    if (options.include_base64 !== undefined) {
      formData.append('include_base64', String(options.include_base64));
    }
    
    if (options.save_to_disk !== undefined) {
      formData.append('save_to_disk', String(options.save_to_disk));
    }

    if (options.custom_metadata) {
      formData.append('custom_metadata', JSON.stringify(options.custom_metadata));
    }

    const response = await this.makeRequest<ComplianceResponse>({
      method: 'POST',
      url: '/comply',
      data: formData,
      headers: formData.getHeaders(),
    });

    return {
      ...response.data,
      _rateLimitInfo: this.extractRateLimitInfo(response),
    };
  }

  /**
   * DEPRECATED: Legacy endpoint - Process an image via URL. Use `/comply` for new integrations.
   * 
   * @param imageUrl - URL of the image to process
   * @param options - Processing options (limited compared to comply endpoint)
   * @returns Promise with detection results
   * 
   * @example
   * ```typescript
   * const result = await client.tag('https://example.com/image.jpg', {
   *   compliance_regions: ['EU']
   * });
   * ```
   */
  async tag(imageUrl: string, options: { compliance_regions: string[] }): Promise<ComplianceResponse> {
    // Exact format from documentation
    const data = {
      image_url: imageUrl,
      compliance_regions: options.compliance_regions || ['EU']
    };

    const response = await this.makeRequest<ComplianceResponse>({
      method: 'POST',
      url: '/v1/tag',
      data,
    });

    return {
      ...response.data,
      _rateLimitInfo: this.extractRateLimitInfo(response),
    };
  }

  /**
   * Process multiple images in batch (Enterprise feature)
   * 
   * @param items - Array of batch items to process (max 100)
   * @param options - Batch processing options
   * @returns Promise with batch processing results
   * 
   * @example
   * ```typescript
   * const items = [
   *   { id: 'img1', image: image1Buffer, customMetadata: { source: 'upload' } },
   *   { id: 'img2', image: image2Buffer, customMetadata: { source: 'api' } },
   * ];
   * 
   * const result = await client.batchProcess(items, { region: 'eu' });
   * console.log(`Processed: ${result.successful}/${result.total_processed}`);
   * ```
   */
  async batchProcess(items: BatchItem[], options: BatchOptions = {}): Promise<BatchResponse> {
    if (items.length > 100) {
      throw new ComplianceValidationError('Maximum 100 items per batch');
    }

    const formData = new FormData();
    formData.append('region', options.region || 'eu');
    formData.append('watermark_logo', String(options.watermarkLogo !== false));
    formData.append('metadata_level', options.metadataLevel || 'basic');

    items.forEach((item, index) => {
      formData.append(`images_${index}`, item.image, `image_${index}.jpg`);
      if (item.custom_metadata) {
        formData.append(`custom_metadata_${index}`, JSON.stringify(item.custom_metadata));
      }
    });

    const response = await this.makeRequest<BatchResponse>({
      method: 'POST',
      url: '/v1/batch',
      data: formData,
      headers: formData.getHeaders(),
    });

    return {
      ...response.data,
      _rateLimitInfo: this.extractRateLimitInfo(response),
    };
  }

  /**
   * Get usage analytics (Enterprise feature)
   * 
   * @param options - Analytics query options
   * @returns Promise with usage statistics and insights
   * 
   * @example
   * ```typescript
   * // Get monthly analytics
   * const analytics = await client.getAnalytics({ period: 'month' });
   * 
   * // Get custom period
   * const customAnalytics = await client.getAnalytics({
   *   startDate: '2024-01-01',
   *   endDate: '2024-01-31'
   * });
   * ```
   */
  async getAnalytics(options: AnalyticsOptions = {}): Promise<AnalyticsResponse> {
    const params: Record<string, string> = {};
    
    if (options.period) params.period = options.period;
    if (options.startDate) params.start_date = options.startDate;
    if (options.endDate) params.end_date = options.endDate;

    const response = await this.makeRequest<AnalyticsResponse>({
      method: 'GET',
      url: '/v1/analytics',
      params,
    });

    return response.data;
  }

  /**
   * Register webhook endpoint (Enterprise feature)
   * 
   * @param options - Webhook registration options
   * @returns Promise with webhook registration details
   * 
   * @example
   * ```typescript
   * const webhook = await client.registerWebhook({
   *   url: 'https://your-app.com/webhooks/compliance',
   *   events: ['compliance.completed', 'batch.finished'],
   *   secret: 'your_webhook_secret'
   * });
   * ```
   */
  async registerWebhook(options: WebhookOptions): Promise<WebhookRegistration> {
    const data = {
      url: options.url,
      events: options.events,
      ...(options.secret && { secret: options.secret }),
    };

    const response = await this.makeRequest<WebhookRegistration>({
      method: 'POST',
      url: '/v1/webhooks',
      data,
    });

    return response.data;
  }

  /**
   * List registered webhooks (Enterprise feature)
   * 
   * @returns Promise with array of registered webhooks
   */
  async listWebhooks(): Promise<WebhookRegistration[]> {
    const response = await this.makeRequest<{ webhooks: WebhookRegistration[] }>({
      method: 'GET',
      url: '/v1/webhooks',
    });

    return response.data.webhooks;
  }

  /**
   * Delete webhook (Enterprise feature)
   * 
   * @param webhookId - ID of webhook to delete
   * @returns Promise with boolean indicating success
   */
  async deleteWebhook(webhookId: string): Promise<boolean> {
    try {
      await this.makeRequest({
        method: 'DELETE',
        url: `/v1/webhooks/${webhookId}`,
      });
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Get current quota information
   * 
   * @returns Promise with quota details
   */
  async getQuotaInfo(): Promise<QuotaInfo> {
    const response = await this.makeRequest<QuotaInfo>({
      method: 'GET',
      url: '/quota',
    });

    return response.data;
  }

  /**
   * Service health check and status information.
   * No authentication required.
   * 
   * @returns Promise with health status
   * 
   * @example
   * ```typescript
   * const health = await client.getHealth();
   * console.log(`API Status: ${health.status}`);
   * ```
   */
  async getHealth(): Promise<HealthResponse> {
    const response = await this.makeRequest<HealthResponse>({
      method: 'GET',
      url: '/health',
    });

    return response.data;
  }

  /**
   * Download processed files by filename. No authentication required.
   * 
   * @param filename - The filename to download
   * @returns Promise with file buffer
   * 
   * @example
   * ```typescript
   * const fileBuffer = await client.downloadFile('processed-image.jpg');
   * ```
   */
  async downloadFile(filename: string): Promise<Buffer> {
    const response = await this.makeRequest<Buffer>({
      method: 'GET',
      url: `/download/${filename}`,
      responseType: 'arraybuffer'
    });

    return response.data;
  }

  /**
   * Make HTTP request with error handling and retries
   */
  private async makeRequest<T = any>(config: any): Promise<AxiosResponse<T>> {
    let lastError: Error;
    
    for (let attempt = 0; attempt <= this.maxRetries; attempt++) {
      try {
        const response = await this.httpClient.request<T>(config);
        return response;
      } catch (error) {
        lastError = error as Error;
        
        // Don't retry on authentication errors or validation errors
        if (error instanceof ComplianceAuthenticationError || 
            error instanceof ComplianceValidationError) {
          throw error;
        }
        
        // Handle rate limiting with exponential backoff
        if (error instanceof ComplianceRateLimitError && attempt < this.maxRetries) {
          const delay = error.retryAfter ? error.retryAfter * 1000 : Math.pow(2, attempt) * 1000;
          await this.sleep(delay);
          continue;
        }
        
        // Retry network errors with exponential backoff
        if ((error instanceof ComplianceNetworkError || 
             error instanceof ComplianceServerError) && 
            attempt < this.maxRetries) {
          await this.sleep(Math.pow(2, attempt) * 1000);
          continue;
        }
        
        throw error;
      }
    }
    
    throw lastError!;
  }

  /**
   * Handle HTTP errors and convert to appropriate error types
   */
  private handleHttpError(error: AxiosError): never {
    const response = error.response;
    const responseData: ErrorResponse = (response?.data as ErrorResponse) || { message: error.message || 'Unknown error' };
    
    if (!response) {
      throw new ComplianceNetworkError(`Network request failed: ${error.message}`, error);
    }
    
    const { status } = response;
    const message = responseData.message || `HTTP ${status}`;
    
    switch (status) {
      case 401:
        throw new ComplianceAuthenticationError(message, responseData);
        
      case 402:
        throw new ComplianceQuotaExceededError(
          message,
          responseData.details?.quota_limit,
          responseData.details?.quota_used,
          responseData
        );
        
      case 422:
        throw new ComplianceValidationError(
          message,
          responseData.details?.field_errors,
          responseData
        );
        
      case 429:
        const retryAfter = response.headers['retry-after'] 
          ? parseInt(response.headers['retry-after'], 10)
          : undefined;
        throw new ComplianceRateLimitError(message, retryAfter, responseData);
        
      case 500:
      case 502:
      case 503:
      case 504:
        throw new ComplianceServerError(message, responseData);
        
      default:
        throw new ComplianceAPIError(message, status, responseData);
    }
  }

  /**
   * Extract rate limit information from response headers
   */
  private extractRateLimitInfo(response: AxiosResponse): RateLimitInfo {
    return {
      limit: parseInt(response.headers['x-ratelimit-limit'] || '0', 10),
      remaining: parseInt(response.headers['x-ratelimit-remaining'] || '0', 10),
      reset: new Date(parseInt(response.headers['x-ratelimit-reset'] || '0', 10) * 1000),
    };
  }

  /**
   * Sleep for specified milliseconds
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Export everything for convenience
export * from './types';
export default ComplianceClient;