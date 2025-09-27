package com.aigccompliance;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.ObjectMapper;
import okhttp3.*;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.TimeUnit;

/**
 * AIGC Compliance Java Client
 * 
 * Official Java client for AIGC Compliance API.
 * Provides comprehensive AI content detection and watermarking capabilities.
 * 
 * @author AIGC Compliance Team
 * @version 1.0.0
 * 
 * @example
 * <pre>
 * ComplianceClient client = new ComplianceClient("your_api_key");
 * 
 * // Process image file
 * ComplianceResponse result = client.comply(new File("image.jpg"), 
 *     ComplianceOptions.builder().region("eu").build());
 * 
 * System.out.println("AI Generated: " + result.isAiGenerated());
 * </pre>
 */
public class ComplianceClient {
    
    private static final String DEFAULT_BASE_URL = "https://api.aigc-compliance.com";
    private static final int DEFAULT_TIMEOUT = 30;
    private static final int DEFAULT_MAX_RETRIES = 3;
    
    private final String apiKey;
    private final String baseUrl;
    private final int timeout;
    private final int maxRetries;
    private final OkHttpClient httpClient;
    private final ObjectMapper objectMapper;
    
    /**
     * Initialize AIGC Compliance client
     * 
     * @param apiKey Your AIGC Compliance API key
     * @throws ComplianceAuthenticationException If API key is invalid
     */
    public ComplianceClient(@NotNull String apiKey) {
        this(apiKey, new ClientOptions());
    }
    
    /**
     * Initialize AIGC Compliance client with options
     * 
     * @param apiKey Your AIGC Compliance API key
     * @param options Client configuration options
     * @throws ComplianceAuthenticationException If API key is invalid
     */
    public ComplianceClient(@NotNull String apiKey, @NotNull ClientOptions options) {
        if (apiKey == null || apiKey.trim().isEmpty()) {
            throw new ComplianceAuthenticationException("API key is required");
        }
        
        this.apiKey = apiKey;
        this.baseUrl = options.getBaseUrl() != null ? options.getBaseUrl() : DEFAULT_BASE_URL;
        this.timeout = options.getTimeout() != null ? options.getTimeout() : DEFAULT_TIMEOUT;
        this.maxRetries = options.getMaxRetries() != null ? options.getMaxRetries() : DEFAULT_MAX_RETRIES;
        this.objectMapper = new ObjectMapper();
        
        this.httpClient = new OkHttpClient.Builder()
            .connectTimeout(timeout, TimeUnit.SECONDS)
            .writeTimeout(timeout, TimeUnit.SECONDS)
            .readTimeout(timeout, TimeUnit.SECONDS)
            .addInterceptor(chain -> {
                Request original = chain.request();
                Request.Builder requestBuilder = original.newBuilder()
                    .header("Authorization", "Bearer " + apiKey)
                    .header("User-Agent", options.getUserAgent() != null ? 
                        options.getUserAgent() : "aigc-compliance-java/1.0.0");
                
                return chain.proceed(requestBuilder.build());
            })
            .build();
    }
    
    /**
     * Process image for AI content detection and compliance watermarking
     * 
     * @param filePath Path to the image file to process
     * @param region Region for processing ("EU" or "CN")
     * @param watermarkPosition Position for watermark ("top-left", "top-right", "bottom-left", "bottom-right")
     * @param logoFile Optional path to logo file to include
     * @param includeBase64 Whether to include base64 encoded image in response
     * @param saveToDisk Whether to save the processed image to disk
     * @return Map containing the compliance response
     * @throws ComplianceAPIException On API errors
     * @throws IOException On file reading errors
     */
    public Map<String, Object> comply(
            @NotNull String filePath, 
            @NotNull String region,
            @Nullable String watermarkPosition,
            @Nullable String logoFile,
            boolean includeBase64,
            boolean saveToDisk) throws IOException, ComplianceAPIException {
        
        // Validate region
        if (!region.equals("EU") && !region.equals("CN")) {
            throw new ComplianceValidationException("Region must be either 'EU' or 'CN'");
        }

        File file = new File(filePath);
        if (!file.exists()) {
            throw new ComplianceValidationException("Image file not found: " + filePath);
        }

        MultipartBody.Builder formBuilder = new MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart("file", file.getName(), 
                RequestBody.create(Files.readAllBytes(file.toPath()), MediaType.parse("image/jpeg")))
            .addFormDataPart("region", region)
            .addFormDataPart("watermark_position", watermarkPosition != null ? watermarkPosition : "bottom-right")
            .addFormDataPart("include_base64", String.valueOf(includeBase64))
            .addFormDataPart("save_to_disk", String.valueOf(saveToDisk));

        // Add logo file if provided
        if (logoFile != null) {
            File logo = new File(logoFile);
            if (logo.exists()) {
                formBuilder.addFormDataPart("logo_file", logo.getName(),
                    RequestBody.create(Files.readAllBytes(logo.toPath()), MediaType.parse("image/png")));
            }
        }

        Request request = new Request.Builder()
            .url(baseUrl + "/comply")
            .post(formBuilder.build())
            .build();

        try (Response response = executeWithRetry(request)) {
            return parseResponse(response, Map.class);
        } catch (IOException e) {
            throw new ComplianceNetworkException("Network request failed", e);
        }
    }

    /**
     * Process image for AI content detection and compliance watermarking (legacy method)
     * 
     * @param image Image file to process
     * @param options Processing options
     * @return ComplianceResponse with detection results
     * @throws ComplianceAPIException On API errors
     * @throws IOException On file reading errors
     */
    public ComplianceResponse complyLegacy(@NotNull File image, @Nullable ComplianceOptions options) 
            throws IOException, ComplianceAPIException {
        return comply(Files.readAllBytes(image.toPath()), options);
    }
    
    /**
     * Process image for AI content detection and compliance watermarking
     * 
     * @param imageData Image binary data
     * @param options Processing options
     * @return ComplianceResponse with detection results
     * @throws ComplianceAPIException On API errors
     */
    public ComplianceResponse comply(@NotNull byte[] imageData, @Nullable ComplianceOptions options) 
            throws ComplianceAPIException {
        
        if (options == null) {
            options = ComplianceOptions.builder().build();
        }
        
        MultipartBody.Builder formBuilder = new MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart("file", "image.jpg", 
                RequestBody.create(imageData, MediaType.parse("image/jpeg")))
            .addFormDataPart("region", options.getRegion())
            .addFormDataPart("watermark_logo", String.valueOf(options.isWatermarkLogo()))
            .addFormDataPart("metadata_level", options.getMetadataLevel());
        
        if (options.getWatermarkText() != null) {
            formBuilder.addFormDataPart("watermark_text", options.getWatermarkText());
        }
        
        if (options.getCustomMetadata() != null) {
            try {
                formBuilder.addFormDataPart("custom_metadata", 
                    objectMapper.writeValueAsString(options.getCustomMetadata()));
            } catch (Exception e) {
                throw new ComplianceValidationException("Invalid custom metadata: " + e.getMessage());
            }
        }
        
        Request request = new Request.Builder()
            .url(baseUrl + "/comply")
            .post(formBuilder.build())
            .build();
        
        try (Response response = executeWithRetry(request)) {
            ComplianceResponse result = parseResponse(response, ComplianceResponse.class);
            result.setRateLimitInfo(extractRateLimitInfo(response));
            return result;
        } catch (IOException e) {
            throw new ComplianceNetworkException("Network request failed", e);
        }
    }
    
    /**
     * Legacy endpoint: Process image from URL for AI detection
     * 
     * @param imageUrl URL of the image to process
     * @param region Compliance region ("EU" or "CN")
     * @param watermarkText Custom watermark text
     * @param watermarkLogo Whether to apply logo watermark
     * @param metadataLevel Level of compliance metadata
     * @return Map containing detection results
     * @throws ComplianceAPIException On API errors
     */
    public Map<String, Object> tag(
            @NotNull String imageUrl,
            @NotNull String region,
            @Nullable String watermarkText,
            boolean watermarkLogo,
            @NotNull String metadataLevel) throws ComplianceAPIException {
        
        // Validate region
        if (!region.equals("EU") && !region.equals("CN")) {
            throw new ComplianceValidationException("Region must be either 'EU' or 'CN'");
        }
        
        Map<String, Object> data = new HashMap<>();
        data.put("image_url", imageUrl);
        data.put("region", region);
        data.put("watermark_logo", watermarkLogo);
        data.put("metadata_level", metadataLevel);
        
        if (watermarkText != null) {
            data.put("watermark_text", watermarkText);
        }
        
        try {
            RequestBody body = RequestBody.create(
                objectMapper.writeValueAsString(data),
                MediaType.parse("application/json")
            );
            
            Request request = new Request.Builder()
                .url(baseUrl + "/v1/tag")
                .post(body)
                .build();
            
            try (Response response = executeWithRetry(request)) {
                return parseResponse(response, Map.class);
            }
        } catch (IOException e) {
            throw new ComplianceNetworkException("Network request failed", e);
        }
    }

    /**
     * Check API health status
     * 
     * @return Health status information
     * @throws ComplianceAPIException On API errors
     */
    public Map<String, Object> health() throws ComplianceAPIException {
        Request request = new Request.Builder()
            .url(baseUrl + "/health")
            .get()
            .build();
        
        try (Response response = executeWithRetry(request)) {
            return parseResponse(response, Map.class);
        } catch (IOException e) {
            throw new ComplianceNetworkException("Health check failed", e);
        }
    }

    /**
     * Download a processed file
     * 
     * @param filename Name of the file to download
     * @return File content as byte array
     * @throws ComplianceAPIException On API errors
     */
    public byte[] downloadFile(@NotNull String filename) throws ComplianceAPIException {
        Request request = new Request.Builder()
            .url(baseUrl + "/download/" + filename)
            .get()
            .build();
        
        try (Response response = executeWithRetry(request)) {
            if (response.body() == null) {
                throw new ComplianceAPIException("Empty response body", response.code());
            }
            return response.body().bytes();
        } catch (IOException e) {
            throw new ComplianceNetworkException("File download failed", e);
        }
    }

    /**
     * Process multiple images in batch (Enterprise feature)
     * 
     * @param items List of batch items to process (max 100)
     * @param options Batch processing options
     * @return BatchResponse with results for all processed items
     * @throws ComplianceAPIException On API errors
     */
    public BatchResponse batchProcess(@NotNull List<BatchItem> items, @Nullable BatchOptions options)
            throws ComplianceAPIException {
        
        if (items.size() > 100) {
            throw new ComplianceValidationException("Maximum 100 items per batch");
        }
        
        if (options == null) {
            options = BatchOptions.builder().build();
        }
        
        MultipartBody.Builder formBuilder = new MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart("region", options.getRegion())
            .addFormDataPart("watermark_logo", String.valueOf(options.isWatermarkLogo()))
            .addFormDataPart("metadata_level", options.getMetadataLevel());
        
        for (int i = 0; i < items.size(); i++) {
            BatchItem item = items.get(i);
            formBuilder.addFormDataPart("images_" + i, "image_" + i + ".jpg",
                RequestBody.create(item.getImageData(), MediaType.parse("image/jpeg")));
            
            if (item.getCustomMetadata() != null) {
                try {
                    formBuilder.addFormDataPart("custom_metadata_" + i,
                        objectMapper.writeValueAsString(item.getCustomMetadata()));
                } catch (Exception e) {
                    throw new ComplianceValidationException("Invalid custom metadata for item " + i);
                }
            }
        }
        
        Request request = new Request.Builder()
            .url(baseUrl + "/v1/batch")
            .post(formBuilder.build())
            .build();
        
        try (Response response = executeWithRetry(request)) {
            BatchResponse result = parseResponse(response, BatchResponse.class);
            result.setRateLimitInfo(extractRateLimitInfo(response));
            return result;
        } catch (IOException e) {
            throw new ComplianceNetworkException("Network request failed", e);
        }
    }
    
    /**
     * Get usage analytics (Enterprise feature)
     * 
     * @param options Analytics query options
     * @return AnalyticsResponse with usage statistics
     * @throws ComplianceAPIException On API errors
     */
    public AnalyticsResponse getAnalytics(@Nullable AnalyticsOptions options) 
            throws ComplianceAPIException {
        
        HttpUrl.Builder urlBuilder = HttpUrl.parse(baseUrl + "/v1/analytics").newBuilder();
        
        if (options != null) {
            if (options.getPeriod() != null) {
                urlBuilder.addQueryParameter("period", options.getPeriod());
            }
            if (options.getStartDate() != null) {
                urlBuilder.addQueryParameter("start_date", options.getStartDate());
            }
            if (options.getEndDate() != null) {
                urlBuilder.addQueryParameter("end_date", options.getEndDate());
            }
        }
        
        Request request = new Request.Builder()
            .url(urlBuilder.build())
            .get()
            .build();
        
        try (Response response = executeWithRetry(request)) {
            return parseResponse(response, AnalyticsResponse.class);
        } catch (IOException e) {
            throw new ComplianceNetworkException("Network request failed", e);
        }
    }
    
    /**
     * Register webhook endpoint (Enterprise feature)
     * 
     * @param options Webhook registration options
     * @return WebhookRegistration with registration details
     * @throws ComplianceAPIException On API errors
     */
    public WebhookRegistration registerWebhook(@NotNull WebhookOptions options) 
            throws ComplianceAPIException {
        
        Map<String, Object> data = new HashMap<>();
        data.put("url", options.getUrl());
        data.put("events", options.getEvents());
        
        if (options.getSecret() != null) {
            data.put("secret", options.getSecret());
        }
        
        try {
            RequestBody body = RequestBody.create(
                objectMapper.writeValueAsString(data),
                MediaType.parse("application/json")
            );
            
            Request request = new Request.Builder()
                .url(baseUrl + "/v1/webhooks")
                .post(body)
                .build();
            
            try (Response response = executeWithRetry(request)) {
                return parseResponse(response, WebhookRegistration.class);
            }
        } catch (IOException e) {
            throw new ComplianceNetworkException("Network request failed", e);
        }
    }
    
    /**
     * Get current quota information
     * 
     * @return QuotaInfo with quota details
     * @throws ComplianceAPIException On API errors
     */
    public QuotaInfo getQuotaInfo() throws ComplianceAPIException {
        Request request = new Request.Builder()
            .url(baseUrl + "/quota")
            .get()
            .build();
        
        try (Response response = executeWithRetry(request)) {
            return parseResponse(response, QuotaInfo.class);
        } catch (IOException e) {
            throw new ComplianceNetworkException("Network request failed", e);
        }
    }
    
    /**
     * Execute HTTP request with retry logic
     */
    private Response executeWithRetry(Request request) throws IOException, ComplianceAPIException {
        IOException lastException = null;
        
        for (int attempt = 0; attempt <= maxRetries; attempt++) {
            try {
                Response response = httpClient.newCall(request).execute();
                
                // Handle rate limiting with exponential backoff
                if (response.code() == 429) {
                    if (attempt < maxRetries) {
                        String retryAfter = response.header("Retry-After");
                        int delay = retryAfter != null ? Integer.parseInt(retryAfter) : (int) Math.pow(2, attempt);
                        
                        try {
                            Thread.sleep(delay * 1000);
                        } catch (InterruptedException e) {
                            Thread.currentThread().interrupt();
                            throw new ComplianceNetworkException("Request interrupted", e);
                        }
                        
                        response.close();
                        continue;
                    }
                }
                
                // Handle HTTP errors
                if (response.code() >= 400) {
                    handleHttpError(response);
                }
                
                return response;
                
            } catch (IOException e) {
                lastException = e;
                if (attempt < maxRetries) {
                    try {
                        Thread.sleep((long) Math.pow(2, attempt) * 1000);
                    } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                        throw new ComplianceNetworkException("Request interrupted", ie);
                    }
                    continue;
                }
            }
        }
        
        throw new ComplianceNetworkException("Maximum retries exceeded", lastException);
    }
    
    /**
     * Handle HTTP errors and convert to appropriate exceptions
     */
    private void handleHttpError(Response response) throws ComplianceAPIException {
        try {
            String responseBody = response.body() != null ? response.body().string() : "";
            Map<String, Object> errorData = null;
            
            try {
                errorData = objectMapper.readValue(responseBody, Map.class);
            } catch (Exception e) {
                errorData = Collections.singletonMap("message", responseBody);
            }
            
            String message = (String) errorData.getOrDefault("message", "HTTP " + response.code());
            
            switch (response.code()) {
                case 401:
                    throw new ComplianceAuthenticationException(message, errorData);
                case 402:
                    throw new ComplianceQuotaExceededException(message, errorData);
                case 422:
                    throw new ComplianceValidationException(message, errorData);
                case 429:
                    String retryAfter = response.header("Retry-After");
                    throw new ComplianceRateLimitException(message, 
                        retryAfter != null ? Integer.parseInt(retryAfter) : null, errorData);
                case 500:
                case 502:
                case 503:
                case 504:
                    throw new ComplianceServerException(message, errorData);
                default:
                    throw new ComplianceAPIException(message, response.code(), errorData);
            }
        } catch (IOException e) {
            throw new ComplianceNetworkException("Failed to read error response", e);
        } finally {
            response.close();
        }
    }
    
    /**
     * Parse JSON response
     */
    private <T> T parseResponse(Response response, Class<T> clazz) throws ComplianceAPIException {
        try {
            String responseBody = response.body() != null ? response.body().string() : "{}";
            return objectMapper.readValue(responseBody, clazz);
        } catch (IOException e) {
            throw new ComplianceAPIException("Failed to parse response", response.code());
        }
    }
    
    /**
     * Extract rate limit information from response headers
     */
    private RateLimitInfo extractRateLimitInfo(Response response) {
        return RateLimitInfo.builder()
            .limit(Integer.parseInt(response.header("X-RateLimit-Limit", "0")))
            .remaining(Integer.parseInt(response.header("X-RateLimit-Remaining", "0")))
            .reset(Instant.ofEpochSecond(Long.parseLong(response.header("X-RateLimit-Reset", "0"))))
            .build();
    }
}