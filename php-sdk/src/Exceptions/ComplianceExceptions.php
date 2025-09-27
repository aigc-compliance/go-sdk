<?php

declare(strict_types=1);

namespace AigcCompliance\Exceptions;

use Exception;

/**
 * Base exception for all AIGC Compliance API errors
 */
class ComplianceAPIException extends Exception
{
    protected ?int $statusCode;
    protected array $responseData;

    public function __construct(string $message, ?int $statusCode = null, array $responseData = [], ?Exception $previous = null)
    {
        parent::__construct($message, $statusCode ?? 0, $previous);
        $this->statusCode = $statusCode;
        $this->responseData = $responseData;
    }

    public function getStatusCode(): ?int
    {
        return $this->statusCode;
    }

    public function getResponseData(): array
    {
        return $this->responseData;
    }
}

/**
 * Raised when API key is invalid or missing
 */
class ComplianceAuthenticationException extends ComplianceAPIException
{
    public function __construct(string $message = 'Invalid or missing API key', array $responseData = [])
    {
        parent::__construct($message, 401, $responseData);
    }
}

/**
 * Raised when rate limit is exceeded
 */
class ComplianceRateLimitException extends ComplianceAPIException
{
    private ?int $retryAfter;

    public function __construct(string $message = 'Rate limit exceeded', ?int $retryAfter = null, array $responseData = [])
    {
        parent::__construct($message, 429, $responseData);
        $this->retryAfter = $retryAfter;
    }

    public function getRetryAfter(): ?int
    {
        return $this->retryAfter;
    }
}

/**
 * Raised when API quota is exceeded
 */
class ComplianceQuotaExceededException extends ComplianceAPIException
{
    private ?int $quotaLimit;
    private ?int $quotaUsed;

    public function __construct(
        string $message = 'API quota exceeded',
        ?int $quotaLimit = null,
        ?int $quotaUsed = null,
        array $responseData = []
    ) {
        parent::__construct($message, 402, $responseData);
        $this->quotaLimit = $quotaLimit;
        $this->quotaUsed = $quotaUsed;
    }

    public function getQuotaLimit(): ?int
    {
        return $this->quotaLimit;
    }

    public function getQuotaUsed(): ?int
    {
        return $this->quotaUsed;
    }
}

/**
 * Raised when request validation fails
 */
class ComplianceValidationException extends ComplianceAPIException
{
    private array $fieldErrors;

    public function __construct(
        string $message = 'Request validation failed',
        array $fieldErrors = [],
        array $responseData = []
    ) {
        parent::__construct($message, 422, $responseData);
        $this->fieldErrors = $fieldErrors;
    }

    public function getFieldErrors(): array
    {
        return $this->fieldErrors;
    }
}

/**
 * Raised when server encounters an internal error
 */
class ComplianceServerException extends ComplianceAPIException
{
    public function __construct(string $message = 'Internal server error', array $responseData = [])
    {
        parent::__construct($message, 500, $responseData);
    }
}

/**
 * Raised when network request fails
 */
class ComplianceNetworkException extends ComplianceAPIException
{
    public function __construct(string $message = 'Network request failed', int $code = 0, ?Exception $previous = null)
    {
        parent::__construct($message, null, [], $previous);
    }
}