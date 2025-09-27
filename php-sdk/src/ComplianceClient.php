<?php

declare(strict_types=1);

namespace AigcCompliance;

use GuzzleHttp\Client as HttpClient;
use GuzzleHttp\Exception\GuzzleException;
use GuzzleHttp\Exception\RequestException;
use Psr\Http\Message\ResponseInterface;
use AigcCompliance\Exceptions\ComplianceAPIException;
use AigcCompliance\Exceptions\ComplianceAuthenticationException;
use AigcCompliance\Exceptions\ComplianceRateLimitException;
use AigcCompliance\Exceptions\ComplianceQuotaExceededException;
use AigcCompliance\Exceptions\ComplianceValidationException;
use AigcCompliance\Exceptions\ComplianceServerException;
use AigcCompliance\Exceptions\ComplianceNetworkException;

/**
 * AIGC Compliance PHP Client
 * 
 * Official PHP client for AIGC Compliance API.
 * Provides comprehensive AI content detection and watermarking capabilities.
 * 
 * @package AigcCompliance
 * @author AIGC Compliance Team <support@aigc-compliance.com>
 * @version 1.0.0
 * 
 * @example
 * ```php
 * use AigcCompliance\ComplianceClient;
 * 
 * $client = new ComplianceClient('your_api_key');
 * $result = $client->comply('path/to/image.jpg');
 * echo "AI Generated: " . ($result['is_ai_generated'] ? 'Yes' : 'No');
 * ```
 */
class ComplianceClient
{
    private const DEFAULT_BASE_URL = 'https://api.aigc-compliance.com';
    private const DEFAULT_TIMEOUT = 30;
    private const DEFAULT_MAX_RETRIES = 3;
    private const USER_AGENT = 'AIGC-Compliance-PHP/1.0.0';

    private string $apiKey;
    private string $baseUrl;
    private int $timeout;
    private int $maxRetries;
    private HttpClient $httpClient;

    /**
     * Initialize AIGC Compliance client.
     *
     * @param string $apiKey Your AIGC Compliance API key
     * @param array $options Optional configuration options
     * @throws ComplianceValidationException If API key is invalid
     */
    public function __construct(string $apiKey, array $options = [])
    {
        if (empty($apiKey)) {
            throw new ComplianceValidationException('API key is required');
        }

        $this->apiKey = $apiKey;
        $this->baseUrl = $options['base_url'] ?? self::DEFAULT_BASE_URL;
        $this->timeout = $options['timeout'] ?? self::DEFAULT_TIMEOUT;
        $this->maxRetries = $options['max_retries'] ?? self::DEFAULT_MAX_RETRIES;

        $this->httpClient = new HttpClient([
            'base_uri' => $this->baseUrl,
            'timeout' => $this->timeout,
            'headers' => [
                'User-Agent' => self::USER_AGENT,
                'Authorization' => 'Bearer ' . $this->apiKey,
            ],
        ]);
    }

    /**
     * Process image for AI detection and compliance watermarking.
     *
     * @param string $filePath Path to the image file to process
     * @param string $region Region for processing ("EU" or "CN")
     * @param string|null $watermarkPosition Position for watermark ("top-left", "top-right", "bottom-left", "bottom-right")
     * @param string|null $logoFile Path to logo file to include
     * @param bool $includeBase64 Whether to include base64 encoded image in response
     * @param bool $saveToDisk Whether to save the processed image to disk
     * @return array Compliance analysis result
     * @throws ComplianceAPIException
     */
    public function comply(
        string $filePath,
        string $region = 'EU',
        ?string $watermarkPosition = 'bottom-right',
        ?string $logoFile = null,
        bool $includeBase64 = true,
        bool $saveToDisk = false
    ): array {
        // Validate region
        if (!in_array($region, ['EU', 'CN'])) {
            throw new ComplianceValidationException("Region must be either 'EU' or 'CN'");
        }

        if (!file_exists($filePath)) {
            throw new ComplianceValidationException("Image file not found: {$filePath}");
        }

        $multipart = [
            [
                'name' => 'file',
                'contents' => fopen($filePath, 'r'),
                'filename' => basename($filePath),
            ],
            [
                'name' => 'region',
                'contents' => $region,
            ],
            [
                'name' => 'watermark_position',
                'contents' => $watermarkPosition,
            ],
            [
                'name' => 'include_base64',
                'contents' => $includeBase64 ? 'true' : 'false',
            ],
            [
                'name' => 'save_to_disk',
                'contents' => $saveToDisk ? 'true' : 'false',
            ],
        ];

        // Add logo file if provided
        if ($logoFile !== null && file_exists($logoFile)) {
            $multipart[] = [
                'name' => 'logo_file',
                'contents' => fopen($logoFile, 'r'),
                'filename' => basename($logoFile),
            ];
        }

        return $this->makeRequest('POST', '/comply', [
            'multipart' => $multipart,
        ]);
    }

    /**
     * Legacy endpoint: Process image from URL for AI detection
     *
     * @param string $imageUrl URL of the image to process
     * @param string $region Compliance region ("EU" or "CN")
     * @param string|null $watermarkText Custom watermark text
     * @param bool $watermarkLogo Whether to apply logo watermark
     * @param string $metadataLevel Level of compliance metadata
     * @return array Detection results
     * @throws ComplianceAPIException
     */
    public function tag(
        string $imageUrl,
        string $region = 'EU',
        ?string $watermarkText = null,
        bool $watermarkLogo = true,
        string $metadataLevel = 'basic'
    ): array {
        // Validate region
        if (!in_array($region, ['EU', 'CN'])) {
            throw new ComplianceValidationException("Region must be either 'EU' or 'CN'");
        }

        $data = [
            'image_url' => $imageUrl,
            'region' => $region,
            'watermark_logo' => $watermarkLogo,
            'metadata_level' => $metadataLevel,
        ];

        if ($watermarkText !== null) {
            $data['watermark_text'] = $watermarkText;
        }

        return $this->makeRequest('POST', '/v1/tag', [
            'json' => $data,
        ]);
    }

    /**
     * Check API health status
     *
     * @return array Health status information
     * @throws ComplianceAPIException
     */
    public function health(): array
    {
        return $this->makeRequest('GET', '/health');
    }

    /**
     * Download a processed file
     *
     * @param string $filename Name of the file to download
     * @return string File content as binary string
     * @throws ComplianceAPIException
     */
    public function downloadFile(string $filename): string
    {
        $response = $this->makeRequest('GET', "/download/{$filename}", [], false);
        return (string) $response->getBody();
    }

    /**
     * Process multiple files in batch.
     *
     * @param array $files Array of file paths or contents
     * @param array $options Batch processing options
     * @return array Batch processing job information
     * @throws ComplianceAPIException
     */
    public function batchProcess(array $files, array $options = []): array
    {
        $multipart = [];
        
        foreach ($files as $index => $file) {
            $fileMultipart = $this->prepareMultipartData($file, "files[$index]");
            $multipart = array_merge($multipart, $fileMultipart);
        }
        
        foreach ($options as $key => $value) {
            $multipart[] = [
                'name' => $key,
                'contents' => is_array($value) ? json_encode($value) : (string) $value,
            ];
        }

        return $this->makeRequest('POST', '/v1/batch', [
            'multipart' => $multipart,
        ]);
    }

    /**
     * Get batch job status.
     *
     * @param string $jobId Batch job ID
     * @return array Job status information
     * @throws ComplianceAPIException
     */
    public function getBatchStatus(string $jobId): array
    {
        return $this->makeRequest('GET', "/v1/batch/$jobId");
    }

    /**
     * Get analytics and metrics.
     *
     * @param array $params Query parameters for analytics
     * @return array Analytics data
     * @throws ComplianceAPIException
     */
    public function getAnalytics(array $params = []): array
    {
        $query = http_build_query($params);
        $endpoint = '/v1/analytics' . ($query ? '?' . $query : '');
        
        return $this->makeRequest('GET', $endpoint);
    }

    /**
     * Register a webhook.
     *
     * @param string $url Webhook URL
     * @param array $events Events to subscribe to
     * @param array $options Additional webhook options
     * @return array Webhook registration result
     * @throws ComplianceAPIException
     */
    public function registerWebhook(string $url, array $events = [], array $options = []): array
    {
        $payload = array_merge([
            'url' => $url,
            'events' => $events,
        ], $options);

        return $this->makeRequest('POST', '/v1/webhooks', [
            'json' => $payload,
        ]);
    }

    /**
     * List registered webhooks.
     *
     * @return array List of webhooks
     * @throws ComplianceAPIException
     */
    public function listWebhooks(): array
    {
        return $this->makeRequest('GET', '/v1/webhooks');
    }

    /**
     * Delete a webhook.
     *
     * @param string $webhookId Webhook ID to delete
     * @return array Deletion result
     * @throws ComplianceAPIException
     */
    public function deleteWebhook(string $webhookId): array
    {
        return $this->makeRequest('DELETE', "/v1/webhooks/$webhookId");
    }

    /**
     * Get quota information.
     *
     * @return array Quota and usage information
     * @throws ComplianceAPIException
     */
    public function getQuota(): array
    {
        return $this->makeRequest('GET', '/quota');
    }

    /**
     * Prepare multipart data for file upload.
     *
     * @param string|resource $content File content
     * @param string $fieldName Field name for the file
     * @return array Multipart data array
     */
    private function prepareMultipartData($content, string $fieldName): array
    {
        if (is_string($content) && file_exists($content)) {
            // It's a file path
            return [[
                'name' => $fieldName,
                'contents' => fopen($content, 'r'),
                'filename' => basename($content),
            ]];
        } elseif (is_resource($content)) {
            // It's a stream resource
            return [[
                'name' => $fieldName,
                'contents' => $content,
                'filename' => 'upload',
            ]];
        } else {
            // It's file contents as string
            return [[
                'name' => $fieldName,
                'contents' => $content,
                'filename' => 'upload',
            ]];
        }
    }

    /**
     * Make HTTP request to the API.
     *
     * @param string $method HTTP method
     * @param string $endpoint API endpoint
     * @param array $options Request options
     * @return array Response data
     * @throws ComplianceAPIException
     */
    private function makeRequest(string $method, string $endpoint, array $options = [], bool $parseJson = true)
    {
        $attempt = 0;
        
        while ($attempt < $this->maxRetries) {
            try {
                $response = $this->httpClient->request($method, $endpoint, $options);
                if ($parseJson) {
                    return $this->handleResponse($response);
                } else {
                    return $response;
                }
            } catch (RequestException $e) {
                $attempt++;
                
                if ($attempt >= $this->maxRetries || !$this->isRetryableError($e)) {
                    $this->handleHttpException($e);
                }
                
                // Exponential backoff
                sleep(pow(2, $attempt - 1));
            } catch (GuzzleException $e) {
                throw new ComplianceNetworkException(
                    'Network error: ' . $e->getMessage(),
                    $e->getCode(),
                    $e
                );
            }
        }
        
        throw new ComplianceNetworkException('Max retries exceeded');
    }

    /**
     * Handle HTTP response.
     *
     * @param ResponseInterface $response
     * @return array
     * @throws ComplianceAPIException
     */
    private function handleResponse(ResponseInterface $response): array
    {
        $statusCode = $response->getStatusCode();
        $body = $response->getBody()->getContents();
        
        if ($statusCode >= 200 && $statusCode < 300) {
            $data = json_decode($body, true);
            
            if (json_last_error() !== JSON_ERROR_NONE) {
                throw new ComplianceServerException('Invalid JSON response: ' . json_last_error_msg());
            }
            
            return $data;
        }
        
        $this->handleErrorResponse($statusCode, $body);
    }

    /**
     * Handle HTTP exceptions.
     *
     * @param RequestException $exception
     * @throws ComplianceAPIException
     */
    private function handleHttpException(RequestException $exception): void
    {
        if ($exception->hasResponse()) {
            $response = $exception->getResponse();
            $statusCode = $response->getStatusCode();
            $body = $response->getBody()->getContents();
            
            $this->handleErrorResponse($statusCode, $body);
        } else {
            throw new ComplianceNetworkException(
                'Network error: ' . $exception->getMessage(),
                $exception->getCode(),
                $exception
            );
        }
    }

    /**
     * Handle error responses based on status code.
     *
     * @param int $statusCode
     * @param string $body
     * @throws ComplianceAPIException
     */
    private function handleErrorResponse(int $statusCode, string $body): void
    {
        $errorData = json_decode($body, true) ?: ['error' => $body];
        $message = $errorData['error'] ?? $errorData['message'] ?? 'Unknown error';
        
        switch ($statusCode) {
            case 400:
                throw new ComplianceValidationException($message, $statusCode);
            case 401:
                throw new ComplianceAuthenticationException($message, $statusCode);
            case 403:
                throw new ComplianceQuotaExceededException($message, $statusCode);
            case 429:
                throw new ComplianceRateLimitException($message, $statusCode);
            case 500:
            case 502:
            case 503:
            case 504:
                throw new ComplianceServerException($message, $statusCode);
            default:
                throw new ComplianceAPIException($message, $statusCode);
        }
    }

    /**
     * Check if an error is retryable.
     *
     * @param RequestException $exception
     * @return bool
     */
    private function isRetryableError(RequestException $exception): bool
    {
        if (!$exception->hasResponse()) {
            return true; // Network errors are retryable
        }
        
        $statusCode = $exception->getResponse()->getStatusCode();
        
        // Retry on server errors and rate limits
        return in_array($statusCode, [429, 500, 502, 503, 504]);
    }

    /**
     * Get client version.
     *
     * @return string
     */
    public function getVersion(): string
    {
        return '1.0.0';
    }

    /**
     * Get current configuration.
     *
     * @return array
     */
    public function getConfig(): array
    {
        return [
            'base_url' => $this->baseUrl,
            'timeout' => $this->timeout,
            'max_retries' => $this->maxRetries,
            'version' => $this->getVersion(),
        ];
    }
}