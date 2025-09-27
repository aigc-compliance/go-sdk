// Package aigcompliance provides the official Go SDK for AIGC Compliance API
//
// The AIGC Compliance API provides AI content detection and watermarking
// with EU GDPR and China Cybersecurity Law compliance.
//
// Example usage:
//
//	import "github.com/aigc-compliance/go-sdk"
//
//	client := aigcompliance.NewClient("your_api_key")
//	result, err := client.Comply(imageData, &aigcompliance.ComplianceOptions{
//		Region: "EU",
//		WatermarkText: "AI Generated Content",
//	})
//	if err != nil {
//		log.Fatal(err)
//	}
//	fmt.Printf("AI Generated: %v\n", result.IsAIGenerated)
package aigcompliance

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"net/url"
	"strconv"
	"strings"
	"time"
)

const (
	// DefaultBaseURL is the default API base URL
	DefaultBaseURL = "https://api.aigc-compliance.com"
	// DefaultTimeout is the default request timeout
	DefaultTimeout = 30 * time.Second
	// DefaultMaxRetries is the default maximum number of retries
	DefaultMaxRetries = 3
	// SDKVersion is the current SDK version
	SDKVersion = "1.0.0"
)

// Client represents the AIGC Compliance API client
type Client struct {
	apiKey     string
	baseURL    string
	httpClient *http.Client
	maxRetries int
	userAgent  string
}

// ClientOption represents a client configuration option
type ClientOption func(*Client)

// WithBaseURL sets a custom base URL
func WithBaseURL(baseURL string) ClientOption {
	return func(c *Client) {
		c.baseURL = strings.TrimRight(baseURL, "/")
	}
}

// WithTimeout sets a custom request timeout
func WithTimeout(timeout time.Duration) ClientOption {
	return func(c *Client) {
		c.httpClient.Timeout = timeout
	}
}

// WithMaxRetries sets the maximum number of retries
func WithMaxRetries(maxRetries int) ClientOption {
	return func(c *Client) {
		c.maxRetries = maxRetries
	}
}

// WithUserAgent sets a custom user agent
func WithUserAgent(userAgent string) ClientOption {
	return func(c *Client) {
		c.userAgent = userAgent
	}
}

// WithHTTPClient sets a custom HTTP client
func WithHTTPClient(httpClient *http.Client) ClientOption {
	return func(c *Client) {
		c.httpClient = httpClient
	}
}

// NewClient creates a new AIGC Compliance client
//
// Example:
//
//	client := aigcompliance.NewClient("your_api_key")
//
//	// With options
//	client := aigcompliance.NewClient("your_api_key",
//		aigcompliance.WithTimeout(60*time.Second),
//		aigcompliance.WithMaxRetries(5),
//	)
func NewClient(apiKey string, options ...ClientOption) *Client {
	if apiKey == "" {
		panic("API key is required")
	}

	client := &Client{
		apiKey:  apiKey,
		baseURL: DefaultBaseURL,
		httpClient: &http.Client{
			Timeout: DefaultTimeout,
		},
		maxRetries: DefaultMaxRetries,
		userAgent:  fmt.Sprintf("aigc-compliance-go/%s", SDKVersion),
	}

	// Apply options
	for _, option := range options {
		option(client)
	}

	return client
}

// ComplianceOptions represents options for the comply endpoint
type ComplianceOptions struct {
	Region         string                 `json:"region,omitempty"`
	WatermarkText  string                 `json:"watermark_text,omitempty"`
	WatermarkLogo  *bool                  `json:"watermark_logo,omitempty"`
	MetadataLevel  string                 `json:"metadata_level,omitempty"`
	CustomMetadata map[string]interface{} `json:"custom_metadata,omitempty"`
}

// TagOptions represents options for the tag endpoint
type TagOptions struct {
	Region        string `json:"region,omitempty"`
	WatermarkText string `json:"watermark_text,omitempty"`
	WatermarkLogo *bool  `json:"watermark_logo,omitempty"`
	MetadataLevel string `json:"metadata_level,omitempty"`
}

// BatchOptions represents options for batch processing
type BatchOptions struct {
	Region        string `json:"region,omitempty"`
	WatermarkLogo *bool  `json:"watermark_logo,omitempty"`
	MetadataLevel string `json:"metadata_level,omitempty"`
}

// AnalyticsOptions represents options for analytics queries
type AnalyticsOptions struct {
	Period    string `json:"period,omitempty"`
	StartDate string `json:"start_date,omitempty"`
	EndDate   string `json:"end_date,omitempty"`
}

// WebhookOptions represents options for webhook registration
type WebhookOptions struct {
	URL    string   `json:"url"`
	Events []string `json:"events"`
	Secret string   `json:"secret,omitempty"`
}

// BatchItem represents a single item in batch processing
type BatchItem struct {
	ID             string                 `json:"id"`
	ImageData      []byte                 `json:"-"`
	CustomMetadata map[string]interface{} `json:"custom_metadata,omitempty"`
}

// ComplianceMetadata represents basic compliance metadata
type ComplianceMetadata struct {
	AIGeneratedProbability float64 `json:"ai_generated_probability"`
	ContentType           string  `json:"content_type"`
	ProcessingTimestamp   string  `json:"processing_timestamp"`
	GDPRCompliant         bool    `json:"gdpr_compliant"`
}

// ChinaComplianceMetadata represents enhanced metadata for China
type ChinaComplianceMetadata struct {
	ComplianceMetadata
	CybersecurityLawCompliance bool                   `json:"cybersecurity_law_compliance"`
	WatermarkInfo             WatermarkInfo          `json:"watermark_info"`
	ContentLabeling           map[string]interface{} `json:"content_labeling"`
}

// WatermarkInfo represents watermark information
type WatermarkInfo struct {
	Text         string  `json:"text,omitempty"`
	LogoApplied  bool    `json:"logo_applied"`
	Position     string  `json:"position"`
	Transparency float64 `json:"transparency"`
}

// ComplianceResponse represents the response from the comply endpoint
type ComplianceResponse struct {
	IsAIGenerated      bool                   `json:"is_ai_generated"`
	Confidence         float64                `json:"confidence"`
	WatermarkApplied   bool                   `json:"watermark_applied"`
	ProcessingTimeMS   int                    `json:"processing_time_ms"`
	QuotaRemaining     int                    `json:"quota_remaining"`
	ComplianceMetadata map[string]interface{} `json:"compliance_metadata"`
	RateLimitInfo      *RateLimitInfo         `json:"-"`
}

// BatchResult represents a single result in batch processing
type BatchResult struct {
	ID                 string                 `json:"id"`
	IsAIGenerated      bool                   `json:"is_ai_generated"`
	Confidence         float64                `json:"confidence"`
	WatermarkApplied   bool                   `json:"watermark_applied"`
	ProcessingTimeMS   int                    `json:"processing_time_ms"`
	ComplianceMetadata map[string]interface{} `json:"compliance_metadata"`
	Error              string                 `json:"error,omitempty"`
}

// BatchResponse represents the response from batch processing
type BatchResponse struct {
	BatchID          string         `json:"batch_id"`
	TotalProcessed   int            `json:"total_processed"`
	Successful       int            `json:"successful"`
	Failed           int            `json:"failed"`
	ProcessingTimeMS int            `json:"processing_time_ms"`
	Results          []BatchResult  `json:"results"`
	RateLimitInfo    *RateLimitInfo `json:"-"`
}

// AnalyticsData represents analytics data for a period
type AnalyticsData struct {
	TotalRequests        int    `json:"total_requests"`
	AIGeneratedDetected  int    `json:"ai_generated_detected"`
	WatermarksApplied    int    `json:"watermarks_applied"`
	QuotaUsed           int    `json:"quota_used"`
	QuotaLimit          int    `json:"quota_limit"`
	PeriodStart         string `json:"period_start"`
	PeriodEnd           string `json:"period_end"`
}

// AnalyticsResponse represents the response from analytics endpoint
type AnalyticsResponse struct {
	CurrentPeriod  AnalyticsData `json:"current_period"`
	PreviousPeriod AnalyticsData `json:"previous_period"`
	GrowthRate     float64       `json:"growth_rate"`
}

// WebhookRegistration represents a webhook registration
type WebhookRegistration struct {
	WebhookID string   `json:"webhook_id"`
	URL       string   `json:"url"`
	Events    []string `json:"events"`
	Secret    string   `json:"secret,omitempty"`
	CreatedAt string   `json:"created_at"`
}

// QuotaInfo represents quota information
type QuotaInfo struct {
	QuotaLimit            int    `json:"quota_limit"`
	QuotaUsed            int    `json:"quota_used"`
	QuotaRemaining       int    `json:"quota_remaining"`
	Plan                 string `json:"plan"`
	BillingPeriodStart   string `json:"billing_period_start"`
	BillingPeriodEnd     string `json:"billing_period_end"`
}

// RateLimitInfo represents rate limit information
type RateLimitInfo struct {
	Limit     int       `json:"limit"`
	Remaining int       `json:"remaining"`
	Reset     time.Time `json:"reset"`
}

// Comply processes image for AI content detection and compliance watermarking
//
// Example:
//
//	imageData, err := os.ReadFile("image.jpg")
//	if err != nil {
//		log.Fatal(err)
//	}
//
//	result, err := client.Comply(imageData, &aigcompliance.ComplianceOptions{
//		Region: "eu",
//		WatermarkText: "AI Generated Content",
//	})
//	if err != nil {
//		log.Fatal(err)
//	}
//
//	fmt.Printf("AI Generated: %v (confidence: %.2f)\n", 
//		result.IsAIGenerated, result.Confidence)
func (c *Client) Comply(imageData []byte, options *ComplianceOptions) (*ComplianceResponse, error) {
	return c.ComplyWithContext(context.Background(), imageData, options)
}

// ComplyWithContext processes image with context for cancellation
func (c *Client) ComplyWithContext(ctx context.Context, imageData []byte, options *ComplianceOptions) (*ComplianceResponse, error) {
	if options == nil {
		options = &ComplianceOptions{}
	}

	// Validate and set defaults
	if options.Region == "" {
		options.Region = "EU"
	}
	if options.Region != "EU" && options.Region != "CN" {
		return nil, fmt.Errorf("region must be either 'EU' or 'CN'")
	}
	if options.WatermarkLogo == nil {
		watermarkLogo := true
		options.WatermarkLogo = &watermarkLogo
	}
	if options.MetadataLevel == "" {
		options.MetadataLevel = "basic"
	}

	var body bytes.Buffer
	writer := multipart.NewWriter(&body)

	// Add image
	imageWriter, err := writer.CreateFormFile("file", "image.jpg")
	if err != nil {
		return nil, fmt.Errorf("failed to create form file: %w", err)
	}
	if _, err := imageWriter.Write(imageData); err != nil {
		return nil, fmt.Errorf("failed to write image data: %w", err)
	}

	// Add form fields
	writer.WriteField("region", options.Region)
	writer.WriteField("watermark_logo", strconv.FormatBool(*options.WatermarkLogo))
	writer.WriteField("metadata_level", options.MetadataLevel)

	if options.WatermarkText != "" {
		writer.WriteField("watermark_text", options.WatermarkText)
	}

	if options.CustomMetadata != nil {
		metadataJSON, err := json.Marshal(options.CustomMetadata)
		if err != nil {
			return nil, fmt.Errorf("failed to marshal custom metadata: %w", err)
		}
		writer.WriteField("custom_metadata", string(metadataJSON))
	}

	writer.Close()

	req, err := http.NewRequestWithContext(ctx, "POST", c.baseURL+"/comply", &body)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Content-Type", writer.FormDataContentType())
	req.Header.Set("Authorization", "Bearer "+c.apiKey)
	req.Header.Set("User-Agent", c.userAgent)

	resp, err := c.executeWithRetry(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result ComplianceResponse
	if err := c.parseResponse(resp, &result); err != nil {
		return nil, err
	}

	result.RateLimitInfo = c.extractRateLimitInfo(resp)
	return &result, nil
}

// Tag processes image from URL (Legacy endpoint)
//
// Example:
//
//	result, err := client.Tag("https://example.com/image.jpg", &aigcompliance.TagOptions{
//		Region: "cn",
//		WatermarkText: "AI生成内容",
//	})
func (c *Client) Tag(imageURL string, options *TagOptions) (*ComplianceResponse, error) {
	return c.TagWithContext(context.Background(), imageURL, options)
}

// TagWithContext processes image from URL with context
func (c *Client) TagWithContext(ctx context.Context, imageURL string, options *TagOptions) (*ComplianceResponse, error) {
	if options == nil {
		options = &TagOptions{}
	}

	// Validate and set defaults
	if options.Region == "" {
		options.Region = "EU"
	}
	if options.Region != "EU" && options.Region != "CN" {
		return nil, fmt.Errorf("region must be either 'EU' or 'CN'")
	}
	if options.WatermarkLogo == nil {
		watermarkLogo := true
		options.WatermarkLogo = &watermarkLogo
	}
	if options.MetadataLevel == "" {
		options.MetadataLevel = "basic"
	}

	data := map[string]interface{}{
		"image_url":       imageURL,
		"region":         options.Region,
		"watermark_logo": *options.WatermarkLogo,
		"metadata_level": options.MetadataLevel,
	}

	if options.WatermarkText != "" {
		data["watermark_text"] = options.WatermarkText
	}

	jsonData, err := json.Marshal(data)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request data: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, "POST", c.baseURL+"/v1/tag", bytes.NewReader(jsonData))
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+c.apiKey)
	req.Header.Set("User-Agent", c.userAgent)

	resp, err := c.executeWithRetry(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result ComplianceResponse
	if err := c.parseResponse(resp, &result); err != nil {
		return nil, err
	}

	result.RateLimitInfo = c.extractRateLimitInfo(resp)
	return &result, nil
}

// Health checks API health status
func (c *Client) Health() (map[string]interface{}, error) {
	return c.HealthWithContext(context.Background())
}

// HealthWithContext checks API health status with context
func (c *Client) HealthWithContext(ctx context.Context) (map[string]interface{}, error) {
	req, err := http.NewRequestWithContext(ctx, "GET", c.baseURL+"/health", nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Authorization", "Bearer "+c.apiKey)
	req.Header.Set("User-Agent", c.userAgent)

	resp, err := c.executeWithRetry(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result map[string]interface{}
	if err := c.parseResponse(resp, &result); err != nil {
		return nil, err
	}

	return result, nil
}

// DownloadFile downloads a processed file by filename
func (c *Client) DownloadFile(filename string) ([]byte, error) {
	return c.DownloadFileWithContext(context.Background(), filename)
}

// DownloadFileWithContext downloads a processed file with context
func (c *Client) DownloadFileWithContext(ctx context.Context, filename string) ([]byte, error) {
	req, err := http.NewRequestWithContext(ctx, "GET", c.baseURL+"/download/"+filename, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Authorization", "Bearer "+c.apiKey)
	req.Header.Set("User-Agent", c.userAgent)

	resp, err := c.executeWithRetry(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, c.handleHTTPError(resp)
	}

	data, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response body: %w", err)
	}

	return data, nil
}

// BatchProcess processes multiple images in batch (Enterprise feature)
//
// Example:
//
//	items := []aigcompliance.BatchItem{
//		{
//			ID: "img1",
//			ImageData: image1Data,
//			CustomMetadata: map[string]interface{}{"source": "upload"},
//		},
//		{
//			ID: "img2", 
//			ImageData: image2Data,
//		},
//	}
//
//	result, err := client.BatchProcess(items, &aigcompliance.BatchOptions{
//		Region: "eu",
//	})
func (c *Client) BatchProcess(items []BatchItem, options *BatchOptions) (*BatchResponse, error) {
	return c.BatchProcessWithContext(context.Background(), items, options)
}

// BatchProcessWithContext processes multiple images with context
func (c *Client) BatchProcessWithContext(ctx context.Context, items []BatchItem, options *BatchOptions) (*BatchResponse, error) {
	if len(items) > 100 {
		return nil, &ValidationError{Message: "Maximum 100 items per batch"}
	}

	if options == nil {
		options = &BatchOptions{}
	}

	// Set defaults
	if options.Region == "" {
		options.Region = "eu"
	}
	if options.WatermarkLogo == nil {
		watermarkLogo := true
		options.WatermarkLogo = &watermarkLogo
	}
	if options.MetadataLevel == "" {
		options.MetadataLevel = "basic"
	}

	var body bytes.Buffer
	writer := multipart.NewWriter(&body)

	// Add form fields
	writer.WriteField("region", options.Region)
	writer.WriteField("watermark_logo", strconv.FormatBool(*options.WatermarkLogo))
	writer.WriteField("metadata_level", options.MetadataLevel)

	// Add images
	for i, item := range items {
		imageWriter, err := writer.CreateFormFile(fmt.Sprintf("images_%d", i), fmt.Sprintf("image_%d.jpg", i))
		if err != nil {
			return nil, fmt.Errorf("failed to create form file for item %d: %w", i, err)
		}
		if _, err := imageWriter.Write(item.ImageData); err != nil {
			return nil, fmt.Errorf("failed to write image data for item %d: %w", i, err)
		}

		if item.CustomMetadata != nil {
			metadataJSON, err := json.Marshal(item.CustomMetadata)
			if err != nil {
				return nil, fmt.Errorf("failed to marshal custom metadata for item %d: %w", i, err)
			}
			writer.WriteField(fmt.Sprintf("custom_metadata_%d", i), string(metadataJSON))
		}
	}

	writer.Close()

	req, err := http.NewRequestWithContext(ctx, "POST", c.baseURL+"/v1/batch", &body)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Content-Type", writer.FormDataContentType())
	req.Header.Set("Authorization", "Bearer "+c.apiKey)
	req.Header.Set("User-Agent", c.userAgent)

	resp, err := c.executeWithRetry(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result BatchResponse
	if err := c.parseResponse(resp, &result); err != nil {
		return nil, err
	}

	result.RateLimitInfo = c.extractRateLimitInfo(resp)
	return &result, nil
}

// GetAnalytics gets usage analytics (Enterprise feature)
//
// Example:
//
//	// Monthly analytics
//	analytics, err := client.GetAnalytics(&aigcompliance.AnalyticsOptions{
//		Period: "month",
//	})
//
//	// Custom period
//	analytics, err := client.GetAnalytics(&aigcompliance.AnalyticsOptions{
//		StartDate: "2024-01-01",
//		EndDate:   "2024-01-31",
//	})
func (c *Client) GetAnalytics(options *AnalyticsOptions) (*AnalyticsResponse, error) {
	return c.GetAnalyticsWithContext(context.Background(), options)
}

// GetAnalyticsWithContext gets analytics with context
func (c *Client) GetAnalyticsWithContext(ctx context.Context, options *AnalyticsOptions) (*AnalyticsResponse, error) {
	u, err := url.Parse(c.baseURL + "/v1/analytics")
	if err != nil {
		return nil, fmt.Errorf("failed to parse URL: %w", err)
	}

	if options != nil {
		q := u.Query()
		if options.Period != "" {
			q.Set("period", options.Period)
		}
		if options.StartDate != "" {
			q.Set("start_date", options.StartDate)
		}
		if options.EndDate != "" {
			q.Set("end_date", options.EndDate)
		}
		u.RawQuery = q.Encode()
	}

	req, err := http.NewRequestWithContext(ctx, "GET", u.String(), nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Authorization", "Bearer "+c.apiKey)
	req.Header.Set("User-Agent", c.userAgent)

	resp, err := c.executeWithRetry(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result AnalyticsResponse
	if err := c.parseResponse(resp, &result); err != nil {
		return nil, err
	}

	return &result, nil
}

// RegisterWebhook registers webhook endpoint (Enterprise feature)
//
// Example:
//
//	webhook, err := client.RegisterWebhook(&aigcompliance.WebhookOptions{
//		URL: "https://your-app.com/webhooks/compliance",
//		Events: []string{"compliance.completed", "batch.finished"},
//		Secret: "your_webhook_secret",
//	})
func (c *Client) RegisterWebhook(options *WebhookOptions) (*WebhookRegistration, error) {
	return c.RegisterWebhookWithContext(context.Background(), options)
}

// RegisterWebhookWithContext registers webhook with context
func (c *Client) RegisterWebhookWithContext(ctx context.Context, options *WebhookOptions) (*WebhookRegistration, error) {
	jsonData, err := json.Marshal(options)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal webhook options: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, "POST", c.baseURL+"/v1/webhooks", bytes.NewReader(jsonData))
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+c.apiKey)
	req.Header.Set("User-Agent", c.userAgent)

	resp, err := c.executeWithRetry(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result WebhookRegistration
	if err := c.parseResponse(resp, &result); err != nil {
		return nil, err
	}

	return &result, nil
}

// GetQuotaInfo gets current quota information
//
// Example:
//
//	quota, err := client.GetQuotaInfo()
//	if err != nil {
//		log.Fatal(err)
//	}
//
//	fmt.Printf("Quota: %d/%d remaining\n", quota.QuotaRemaining, quota.QuotaLimit)
func (c *Client) GetQuotaInfo() (*QuotaInfo, error) {
	return c.GetQuotaInfoWithContext(context.Background())
}

// GetQuotaInfoWithContext gets quota info with context
func (c *Client) GetQuotaInfoWithContext(ctx context.Context) (*QuotaInfo, error) {
	req, err := http.NewRequestWithContext(ctx, "GET", c.baseURL+"/quota", nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Authorization", "Bearer "+c.apiKey)
	req.Header.Set("User-Agent", c.userAgent)

	resp, err := c.executeWithRetry(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result QuotaInfo
	if err := c.parseResponse(resp, &result); err != nil {
		return nil, err
	}

	return &result, nil
}

// executeWithRetry executes HTTP request with retry logic
func (c *Client) executeWithRetry(req *http.Request) (*http.Response, error) {
	var lastErr error

	for attempt := 0; attempt <= c.maxRetries; attempt++ {
		resp, err := c.httpClient.Do(req)
		if err != nil {
			lastErr = err
			if attempt < c.maxRetries {
				time.Sleep(time.Duration(1<<attempt) * time.Second)
				continue
			}
			return nil, &NetworkError{Message: "Network request failed", Err: err}
		}

		// Handle rate limiting with exponential backoff
		if resp.StatusCode == 429 {
			if attempt < c.maxRetries {
				retryAfter := resp.Header.Get("Retry-After")
				var delay time.Duration
				if retryAfter != "" {
					if seconds, err := strconv.Atoi(retryAfter); err == nil {
						delay = time.Duration(seconds) * time.Second
					}
				}
				if delay == 0 {
					delay = time.Duration(1<<attempt) * time.Second
				}

				resp.Body.Close()
				time.Sleep(delay)
				continue
			}
		}

		// Handle HTTP errors
		if resp.StatusCode >= 400 {
			return nil, c.handleHTTPError(resp)
		}

		return resp, nil
	}

	return nil, &NetworkError{Message: "Maximum retries exceeded", Err: lastErr}
}

// parseResponse parses JSON response
func (c *Client) parseResponse(resp *http.Response, result interface{}) error {
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return fmt.Errorf("failed to read response body: %w", err)
	}

	if err := json.Unmarshal(body, result); err != nil {
		return fmt.Errorf("failed to parse response JSON: %w", err)
	}

	return nil
}

// handleHTTPError handles HTTP error responses
func (c *Client) handleHTTPError(resp *http.Response) error {
	body, _ := io.ReadAll(resp.Body)
	resp.Body.Close()

	var errorData map[string]interface{}
	json.Unmarshal(body, &errorData)

	message := "HTTP " + strconv.Itoa(resp.StatusCode)
	if msg, ok := errorData["message"].(string); ok {
		message = msg
	}

	switch resp.StatusCode {
	case 401:
		return &AuthenticationError{Message: message, ResponseData: errorData}
	case 402:
		return &QuotaExceededError{
			Message:      message,
			ResponseData: errorData,
		}
	case 422:
		return &ValidationError{
			Message:      message,
			ResponseData: errorData,
		}
	case 429:
		retryAfter := 0
		if retryAfterStr := resp.Header.Get("Retry-After"); retryAfterStr != "" {
			retryAfter, _ = strconv.Atoi(retryAfterStr)
		}
		return &RateLimitError{
			Message:      message,
			RetryAfter:   retryAfter,
			ResponseData: errorData,
		}
	case 500, 502, 503, 504:
		return &ServerError{Message: message, ResponseData: errorData}
	default:
		return &APIError{
			Message:      message,
			StatusCode:   resp.StatusCode,
			ResponseData: errorData,
		}
	}
}

// extractRateLimitInfo extracts rate limit information from response headers
func (c *Client) extractRateLimitInfo(resp *http.Response) *RateLimitInfo {
	limit, _ := strconv.Atoi(resp.Header.Get("X-RateLimit-Limit"))
	remaining, _ := strconv.Atoi(resp.Header.Get("X-RateLimit-Remaining"))
	resetUnix, _ := strconv.ParseInt(resp.Header.Get("X-RateLimit-Reset"), 10, 64)

	return &RateLimitInfo{
		Limit:     limit,
		Remaining: remaining,
		Reset:     time.Unix(resetUnix, 0),
	}
}